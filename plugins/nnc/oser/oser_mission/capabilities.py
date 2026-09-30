"""Admission, not an intelligence oracle. Native values stay native."""
from __future__ import annotations

from copy import deepcopy

from .common import OserError, canonical, digest, epoch, integer, number, require, text, utcnow


IDENTITY = ("host", "provider", "account")


def identity(value):
    require(isinstance(value, dict), "INVALID_IDENTITY", "identity must be an object")
    return {key: text(value.get(key), key) for key in IDENTITY}


def validate_catalog(value):
    require(isinstance(value, dict), "INVALID_CATALOG", "catalog must be an object")
    require(value.get("schema") == "nnc-oser/capabilities@1", "INVALID_CATALOG", "unsupported capability schema")
    identity(value)
    epoch(value.get("observed_at"))
    number(value.get("ttl_seconds"), "catalog ttl_seconds", 1, 86400)
    require(value.get("evidence_state") in ("DOCUMENTED", "PROBED", "OBSERVED", "UNAVAILABLE", "UNKNOWN"),
            "INVALID_CATALOG", "evidence_state is required")
    text(value.get("source_ref"), "source_ref")
    require(isinstance(value.get("models"), list), "INVALID_CATALOG", "models must be a list")
    ids = set()
    for item in value["models"]:
        require(isinstance(item, dict), "INVALID_CATALOG", "model entry must be an object")
        model_id = text(item.get("id"), "model.id")
        require(model_id not in ids, "INVALID_CATALOG", "duplicate model identity")
        ids.add(model_id)
        require(type(item.get("available")) is bool, "INVALID_CATALOG", "availability must be observed explicitly")
        efforts = item.get("efforts")
        require(efforts is None or (isinstance(efforts, list) and all(isinstance(x, str) and x for x in efforts)),
                "INVALID_CATALOG", "efforts must be a native string list or null")
        scopes = item.get("effort_scopes", [])
        require(isinstance(scopes, list) and all(isinstance(x, str) and x for x in scopes),
                "INVALID_CATALOG", "effort_scopes must be a list")
        if item.get("context_window") is not None:
            integer(item["context_window"], "context_window", 1)
    aliases = value.get("aliases", {})
    require(isinstance(aliases, dict) and all(isinstance(k, str) and v in ids for k, v in aliases.items()),
            "INVALID_CATALOG", "aliases must point into this snapshot")
    require(value.get("default_model") is None or value["default_model"] in ids,
            "INVALID_CATALOG", "default_model must be supplied by this catalog")
    return deepcopy(value)


def validate_policy(policy):
    require(isinstance(policy, dict), "INVALID_POLICY", "policy must be an object")
    require(isinstance(policy.get("bindings"), list), "INVALID_POLICY", "policy.bindings must be explicit (empty denies all)")
    seen = set()
    for binding in policy["bindings"]:
        key = canonical(identity(binding))
        require(key not in seen, "INVALID_POLICY", "duplicate account/host/provider binding")
        seen.add(key)
        for field in ("allowed_efforts", "allowed_actions"):
            require(isinstance(binding.get(field), list) and all(isinstance(x, str) and x for x in binding[field]),
                    "INVALID_POLICY", field + " must be an explicit native-value list")
        require(type(binding.get("allow_uncontrolled_effort", False)) is bool,
                "INVALID_POLICY", "allow_uncontrolled_effort must be boolean")
    integer(policy.get("max_active_executions", 1), "max_active_executions", 1)
    return deepcopy(policy)


def admit(catalog, policy, request, now=None):
    """Pure: no inference, no switch, no quota pooling, no fuzzy model ranking.

    All outcomes are reproducible against the snapshot. Passing admission is
    NOT proof that a native host applied it; callers must record a receipt.
    """
    try:
        validate_catalog(catalog)
        validate_policy(policy)
        require(isinstance(request, dict), "INVALID_REQUEST", "request must be an object")
        age = epoch(now or utcnow()) - epoch(catalog["observed_at"])
        require(0 <= age <= catalog["ttl_seconds"], "STALE_CATALOG", "refresh runtime capability evidence")
        require(catalog["evidence_state"] in ("PROBED", "OBSERVED"),
                "CAPABILITY_UNPROVEN", "configuration/documentation is not a runtime probe")
        binding = next((b for b in policy["bindings"] if identity(b) == identity(catalog)), None)
        require(binding is not None, "PROVIDER_NOT_AUTHORIZED", "host/provider/account binding is not approved")
        require(request.get("action", "inference") in binding["allowed_actions"],
                "ACTION_NOT_AUTHORIZED", "action is outside the approved resource envelope")
        for key in IDENTITY:
            require(key not in request or request[key] == catalog[key],
                    "IDENTITY_MISMATCH", "request identity differs from catalog")
        requested_model = request.get("model", "runtime_default")
        text(requested_model, "request.model")
        model_id = catalog.get("default_model") if requested_model == "runtime_default" else catalog.get("aliases", {}).get(requested_model, requested_model)
        model = next((m for m in catalog["models"] if m["id"] == model_id), None)
        require(model is not None, "MODEL_NOT_RESOLVED", "select a real candidate; never guess a latest model id")
        require(model["available"] and not model.get("retired", False), "MODEL_UNAVAILABLE", "model is not an available candidate")
        effort = request.get("effort", "runtime_default")
        effort = model.get("default_effort") if effort == "runtime_default" else effort
        if effort is None:
            require(binding.get("allow_uncontrolled_effort", False), "DEFAULT_EFFORT_UNKNOWN", "default must not silently bypass the envelope")
        else:
            text(effort, "effort")
            require(effort in (model.get("efforts") or []), "EFFORT_UNSUPPORTED", "effort is not runtime-supported")
            require(effort in binding["allowed_efforts"], "EFFORT_NOT_AUTHORIZED", "effort exceeds the approved native set")
            scope = request.get("effort_scope", "execution")
            require(scope in model.get("effort_scopes", []), "EFFORT_SCOPE_UNAVAILABLE", "no safe native override scope; do not mutate parent around parallel launches")
        if request.get("required_context_tokens") is not None:
            needed = integer(request["required_context_tokens"], "required_context_tokens", 1)
            require(model.get("context_window") is not None and needed <= model["context_window"],
                    "CONTEXT_CAPACITY_UNKNOWN_OR_INSUFFICIENT", "context requirement cannot be admitted")
        return {"status": "ADMITTED", "control": "ADMISSION_ONLY", "requested": deepcopy(request),
                "resolved": dict(identity(catalog), model=model_id, effort=effort,
                                 effort_scope=request.get("effort_scope", "execution")),
                "catalog_hash": digest(catalog), "catalog_observed_at": catalog["observed_at"],
                "observed": None, "native_execution": "NOT_STARTED", "model_selection": "agent_or_native",
                "latest_evidence": "RUNTIME_ALIAS" if requested_model in catalog.get("aliases", {}) else "NOT_ASSERTED"}
    except OserError as exc:
        return {"status": "DENIED", "code": exc.code, "reason": str(exc), "native_execution": "NOT_STARTED"}
