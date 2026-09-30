"""Versioned host decoders. Provider/account are supplied by the trusted caller.

Pure decoders do not discover credentials, infer model quality, start agents,
change parent settings or assert a cached payload is fresh. Names here describe
host wire formats, not mandatory model families in the kernel.

Wire references (retrieved 2026-09-30):
https://developers.openai.com/codex/app-server
https://code.claude.com/docs/en/statusline
https://code.claude.com/docs/en/hooks
"""
from __future__ import annotations

from .common import epoch, require, text


def _base(host, provider, account, observed_at, source_ref):
    text(provider, "provider")
    text(account, "account")
    if observed_at is not None:
        epoch(observed_at)
    return {"host": host, "provider": provider, "account": account,
            "observed_at": observed_at, "source_ref": text(source_ref, "source_ref"), "ttl_seconds": 300}


def codex_catalog(payload, provider, account, observed_at, source_ref, evidence_state="DOCUMENTED"):
    result = payload.get("result", payload)
    require(isinstance(result, dict) and isinstance(result.get("data"), list), "ADAPTER_SCHEMA", "expected model/list result.data")
    base = _base("codex-app-server", provider, account, observed_at, source_ref)
    require(observed_at is not None, "SOURCE_TIME_REQUIRED", "catalog source observation time is required")
    models, aliases = [], {}
    default = None
    for row in result["data"]:
        if row.get("hidden"):
            continue
        mid = row.get("model") or row.get("id")
        efforts = [e["reasoningEffort"] for e in row.get("supportedReasoningEfforts", []) if isinstance(e, dict) and "reasoningEffort" in e]
        models.append({"id": mid, "available": True, "efforts": efforts,
                       "default_effort": row.get("defaultReasoningEffort"), "effort_scopes": ["turn"],
                       "scope_evidence": "DOCUMENTED", "context_window": row.get("contextWindow"),
                       "display_name": row.get("displayName"), "upgrade_hint": row.get("upgrade"),
                       "input_modalities": row.get("inputModalities"), "suitability": "NOT_EVALUATED"})
        if row.get("isDefault"):
            default = mid
        if row.get("id") and row["id"] != mid:
            aliases[row["id"]] = mid
    # isDefault is a provider recommendation, NOT a latest-version guarantee.
    return dict(base, schema="nnc-oser/capabilities@1", evidence_state=evidence_state,
                models=models, aliases=aliases, default_model=default,
                pagination_complete=result.get("nextCursor") is None, automatic_wake="UNKNOWN")


def codex_health(payload, provider, account, observed_at, source_ref):
    result = payload.get("result", payload.get("params", payload))
    require(isinstance(result, dict), "ADAPTER_SCHEMA", "expected rate limits object")
    buckets = result.get("rateLimitsByLimitId")
    if not isinstance(buckets, dict) or not buckets:
        single = result.get("rateLimits")
        buckets = {(single.get("limitId") or "unknown"): single} if isinstance(single, dict) else {}
    samples = []
    for name, bucket in buckets.items():
        if not isinstance(bucket, dict):
            continue
        for window in ("primary", "secondary"):
            value = bucket.get(window)
            if not isinstance(value, dict):
                continue
            sample = _base("codex-app-server", provider, account, observed_at, source_ref)
            sample.update(kind="quota", bucket=str(name) + "/" + window,
                          used_percent=value.get("usedPercent"), resets_at=value.get("resetsAt"),
                          window_minutes=value.get("windowDurationMins"))
            samples.append(sample)
    return samples


def claude_health(payload, provider, account, observed_at, source_ref):
    require(isinstance(payload, dict), "ADAPTER_SCHEMA", "expected statusLine object")
    samples = []
    for window, value in (payload.get("rate_limits") or {}).items():
        if not isinstance(value, dict):
            continue
        sample = _base("claude-code", provider, account, observed_at, source_ref)
        sample.update(kind="quota", bucket=window, used_percent=value.get("used_percentage"), resets_at=value.get("resets_at"))
        samples.append(sample)
    context = payload.get("context_window")
    if isinstance(context, dict):
        sample = _base("claude-code", provider, account, observed_at, source_ref)
        sample.update(kind="context", bucket="session/" + str(payload.get("session_id", "unknown")),
                      used_percent=context.get("used_percentage"),
                      model=(payload.get("model") or {}).get("id"),
                      effort=(payload.get("effort") or {}).get("level"))
        samples.append(sample)
    return samples


def claude_current_catalog(payload, provider, account, observed_at, source_ref):
    """Only the currently observed model. A status line is NOT a model catalog.

    'current' permits observing/retaining the exact current effort, never changing
    it per child. Unsupported scopes stay unavailable until genuinely probed.
    """
    mid = (payload.get("model") or {}).get("id")
    effort = (payload.get("effort") or {}).get("level")
    base = _base("claude-code", provider, account, observed_at, source_ref)
    require(observed_at is not None, "SOURCE_TIME_REQUIRED", "provide the source observation time")
    models = [{"id": mid, "available": True, "efforts": [effort] if effort else None,
               "default_effort": effort, "effort_scopes": ["current"], "scope_evidence": "OBSERVED",
               "context_window": (payload.get("context_window") or {}).get("context_window_size")}] if mid else []
    return dict(base, schema="nnc-oser/capabilities@1", evidence_state="OBSERVED" if mid else "UNKNOWN",
                models=models, aliases={}, default_model=mid, coverage="CURRENT_MODEL_ONLY", automatic_wake="UNKNOWN")


def claude_usage(row, provider, account):
    if row.get("type") != "assistant":
        return None
    message = row.get("message") or {}
    if str(message.get("model", "")).startswith("<") or not isinstance(message.get("usage"), dict):
        return None
    u = message["usage"]
    # Repeated apiBlockIndex snapshots deliberately share this same identity.
    return {"host": "claude-code", "provider": provider, "account": account,
            "session_ref": row.get("sessionId"), "request_id": row.get("requestId"), "response_id": message.get("id"),
            "mode": "snapshot", "usage": {"input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens"),
                                            "cache_read_tokens": u.get("cache_read_input_tokens"),
                                            "cache_write_tokens": u.get("cache_creation_input_tokens")}}


def claude_lifecycle(payload):
    """Return an observation, never a blocking SessionEnd response or a wake."""
    event = payload.get("hook_event_name")
    mapping = {"SessionStart": "RUNNING", "SessionEnd": "UNKNOWN", "Stop": "WAITING",
               "StopFailure": "INTERRUPTED", "SubagentStart": "RUNNING", "SubagentStop": "UNKNOWN"}
    return {"native_event": event, "session_ref": payload.get("session_id"),
            "native_agent_ref": payload.get("agent_id"), "status_hint": mapping.get(event, "UNKNOWN"),
            "completion_proven": False, "can_block_session_end": False,
            "recovery": "MANUAL_RESUME_REQUIRED" if event in ("SessionEnd", "StopFailure") else "NOT_REQUESTED"}
