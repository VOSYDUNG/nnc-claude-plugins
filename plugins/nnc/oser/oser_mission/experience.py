"""Anonymous/local experience telemetry for NNC OSER R2.

No prompt text, answer text, filenames, personal names, cwd, credentials or
transcripts are recorded. The observer exists to measure workflow friction,
not user content or sentiment.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from .common import canonical, project_root, require, safe_path, text, utcnow


ALLOWED_EVENTS = {
    "session_started",
    "prompt_submitted",
    "decision_prompted",
    "decision_completed",
    "decision_guard_blocked",
    "runtime_interrupted",
    "context_compact_started",
    "context_compact_finished",
    "turn_stopped",
    "session_ended",
    "formation_checked",
    "mission_initialized",
}


def _opaque(value):
    if not isinstance(value, str) or not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _paths(project):
    root = project_root(project)
    directory = safe_path(root, ".nnc-oser")
    marker = safe_path(root, ".nnc-oser/experience.enabled")
    log = safe_path(root, ".nnc-oser/experience.jsonl")
    return root, directory, marker, log


def enable(project):
    _, directory, marker, _ = _paths(project)
    directory.mkdir(exist_ok=True)
    marker.write_text("nnc-oser/experience@1\n", encoding="utf-8")
    return {"enabled": True, "scope": "local-project", "content_capture": False,
            "note": "Only anonymous workflow events are recorded locally under .nnc-oser/."}


def disable(project):
    _, _, marker, _ = _paths(project)
    if marker.exists():
        marker.unlink()
    return {"enabled": False}


def enabled(project):
    _, _, marker, _ = _paths(project)
    return marker.is_file()


def append(project, event, fields=None):
    require(event in ALLOWED_EVENTS, "INVALID_EXPERIENCE_EVENT", "unsupported experience event")
    if not enabled(project):
        return {"recorded": False, "reason": "DISABLED"}
    _, directory, _, log = _paths(project)
    directory.mkdir(exist_ok=True)
    payload = {
        "schema": "nnc-oser/experience@1",
        "at": utcnow(),
        "event": event,
    }
    fields = fields or {}
    for key in ("decision_level", "decision_ref", "formation_stage", "route", "source"):
        value = fields.get(key)
        if isinstance(value, str) and value:
            payload[key] = value[:128]
    session_ref = _opaque(fields.get("session_id"))
    if session_ref:
        payload["session_ref"] = session_ref
    with log.open("a", encoding="utf-8") as stream:
        stream.write(canonical(payload) + "\n")
    return {"recorded": True, "event": event}


def _extract_answer(tool_response):
    """Return a scalar answer only when the hook payload exposes one cleanly."""
    if isinstance(tool_response, str):
        return tool_response
    if isinstance(tool_response, dict):
        for key in ("answer", "selected", "selection", "value"):
            value = tool_response.get(key)
            if isinstance(value, str):
                return value
        answers = tool_response.get("answers")
        if isinstance(answers, dict) and len(answers) == 1:
            value = next(iter(answers.values()))
            if isinstance(value, str):
                return value
    return None


def from_claude_hook(project, payload, decision_loader=None):
    """Convert a Claude hook payload into zero-content workflow events."""
    if not enabled(project) or not isinstance(payload, dict):
        return {"recorded": False, "reason": "DISABLED_OR_INVALID"}

    hook = payload.get("hook_event_name") or payload.get("event_name") or payload.get("event")
    session_id = payload.get("session_id")
    base = {"session_id": session_id, "source": "claude-code-hook"}

    mapping = {
        "SessionStart": "session_started",
        "UserPromptSubmit": "prompt_submitted",
        "Stop": "turn_stopped",
        "StopFailure": "runtime_interrupted",
        "PreCompact": "context_compact_started",
        "PostCompact": "context_compact_finished",
        "SessionEnd": "session_ended",
    }
    if hook in mapping:
        return append(project, mapping[hook], base)

    tool = payload.get("tool_name")
    if hook in ("PreToolUse", "PostToolUse") and tool == "AskUserQuestion":
        tool_input = payload.get("tool_input") or {}
        questions = tool_input.get("questions")
        if not isinstance(questions, list) or not questions:
            return {"recorded": False, "reason": "NO_QUESTION"}
        question = questions[0] if isinstance(questions[0], dict) else {}
        qtext = question.get("question")
        card = decision_loader(project, qtext) if decision_loader and isinstance(qtext, str) else None
        if card is None:
            return {"recorded": False, "reason": "NOT_OSER_DECISION"}
        fields = dict(base, decision_ref=card["id"], decision_level=card["level"])
        if hook == "PreToolUse":
            return append(project, "decision_prompted", fields)

        answer = _extract_answer(payload.get("tool_response"))
        route = None
        if answer:
            for option in card.get("options", []):
                if answer == option.get("label"):
                    route = option.get("id")
                    break
            u = card.get("uncertainty_option")
            if route is None and isinstance(u, dict) and answer == u.get("label"):
                route = u.get("id")
        if route:
            fields["route"] = route
        return append(project, "decision_completed", fields)

    return {"recorded": False, "reason": "UNTRACKED_EVENT"}


def report(project):
    _, _, _, log = _paths(project)
    if not log.is_file():
        return {"enabled": enabled(project), "events": 0, "counts": {},
                "self_service": {"material_decisions": 0, "guard_corrections": 0,
                                 "interruptions": 0, "uncertainty_routes": 0},
                "content_capture": False}

    rows = []
    with log.open(encoding="utf-8") as stream:
        for line in stream:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict) and row.get("event") in ALLOWED_EVENTS:
                rows.append(row)
    counts = Counter(row["event"] for row in rows)
    uncertainty = sum(1 for row in rows if row.get("event") == "decision_completed"
                      and row.get("route") in ("investigate", "investigate_first", "test_first"))
    sessions = {row.get("session_ref") for row in rows if row.get("session_ref")}
    return {
        "enabled": enabled(project),
        "events": len(rows),
        "sessions": len(sessions),
        "counts": dict(sorted(counts.items())),
        "self_service": {
            "material_decisions": counts.get("decision_completed", 0),
            "guard_corrections": counts.get("decision_guard_blocked", 0),
            "interruptions": counts.get("runtime_interrupted", 0),
            "uncertainty_routes": uncertainty,
        },
        "content_capture": False,
        "interpretation": "Behavioral telemetry only; it does not prove user sentiment or satisfaction.",
    }
