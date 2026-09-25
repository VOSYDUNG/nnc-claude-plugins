# -*- coding: utf-8 -*-
"""Work ledger — append-only JSONL of wave/packet/attempt events (PROJECT-OWNED data).

The ledger stores control-plane facts only: ids, states, execution identities, counts, refs. It never
stores prompts, customer data or worker reasoning — usage is joined from transcripts by execution id.

Lifecycle (catalog `operating-model.json`):
  packet  ASSIGNED → EXECUTED → MACHINE_VERIFIED → [INDEPENDENT_REVIEWED] → GOVERNOR_ACCEPTED   (REJECTED any time)
  wave    OPEN → PACKETS_ACCEPTED → GOVERNOR_CONSOLIDATED → ROOT_REVIEW → ROOT_ACCEPTED | ROOT_REJECTED
Worker done ≠ packet done; only ROOT_ACCEPTED advances a milestone.
"""
import io
import json
import os

from .manifest import LEDGER_DIR, governor_families
from .transcripts import family
from .util import load_catalog, now_iso

LEDGER_FILE = "ledger.jsonl"


def path(root):
    return os.path.join(root, LEDGER_DIR, LEDGER_FILE)


def _om():
    return load_catalog("operating-model.json")


def _need(ev, keys, errs):
    for k in keys:
        if ev.get(k) in (None, "", []):
            errs.append("%s: missing %s" % (ev.get("event"), k))


def _in(ev, key, allowed, errs, where=None):
    v = ev.get(key) if where is None else where.get(key)
    if v is not None and v not in allowed:
        errs.append("%s: %s=%r not in %s" % (ev.get("event"), key, v, "/".join(allowed)))


def _execution(ev, errs, field="execution"):
    x = ev.get(field) or {}
    if not x.get("sessionId"):
        errs.append("%s: %s.sessionId required (execution identity joins usage)" % (ev.get("event"), field))


def validate_event(ev, manifest=None):
    om = _om()
    efforts = load_catalog("runtime.json")["efforts"]["values"]
    errs = []
    kind = ev.get("event")
    if kind == "wave_open":
        _need(ev, ["waveId", "rootSessionId", "scope"], errs)
        _execution(ev, errs, "governor")
        g = ev.get("governor") or {}
        for key in ("model", "effort"):
            if not g.get(key):
                errs.append("wave_open: governor.%s required" % key)
        if manifest and g.get("model"):
            allowed = governor_families(manifest)
            if family(g["model"]) not in allowed:
                errs.append("wave_open: governor model %s (family %s) not allowed by the profile (required_family=%s, "
                            "fallback=%s) — FAIL CLOSED" % (g["model"], family(g["model"]), allowed[0],
                                                           allowed[1:] or "none"))
        if g.get("effort") and g["effort"] not in efforts:
            errs.append("wave_open: governor.effort %r not a runtime effort" % g["effort"])
    elif kind == "packet_open":
        _need(ev, ["packetId", "waveId", "taskClass", "signals", "context", "verification_depth", "machine_first"], errs)
        _in(ev, "verification_depth", om["verification_depths"], errs)
        for s in om["routing_signals"]:
            lv = (ev.get("signals") or {}).get(s)
            if lv is None:
                errs.append("packet_open: signals.%s missing (use 'unknown' if not assessed)" % s)
            elif lv not in om["signal_levels"]:
                errs.append("packet_open: signals.%s=%r not in %s" % (s, lv, "/".join(om["signal_levels"])))
        ctx = ev.get("context") or {}
        for k in ("must_read", "may_read", "must_not_load", "output_budget"):
            if k not in ctx:
                errs.append("packet_open: context.%s missing" % k)
        mf = ev.get("machine_first") or {}
        if "considered" not in mf:
            errs.append("packet_open: machine_first.considered missing")
    elif kind == "attempt":
        _need(ev, ["packetId", "attempt", "role", "plan", "outcome"], errs)
        _execution(ev, errs)
        _in(ev, "role", om["attempt_roles"], errs)
        _in(ev, "outcome", om["attempt_outcomes"], errs)
        plan = ev.get("plan") or {}
        for k in ("capability", "model", "effort", "mode"):
            if not plan.get(k):
                errs.append("attempt: plan.%s required (model and effort are per attempt, never per role)" % k)
        if plan.get("effort") and plan["effort"] not in efforts:
            errs.append("attempt: plan.effort %r not a runtime effort" % plan["effort"])
        if plan.get("mode") and plan["mode"] not in om["attempt_modes"]:
            errs.append("attempt: plan.mode %r not in %s" % (plan["mode"], "/".join(om["attempt_modes"])))
    elif kind == "packet_state":
        _need(ev, ["packetId", "state"], errs)
        if ev.get("state") in om["legacy_state_names"]:
            errs.append("packet_state: legacy state name %s — run `oser migrate` (renames to %s)"
                        % (ev["state"], om["legacy_state_names"][ev["state"]]))
        _in(ev, "state", om["packet_states"], errs)
    elif kind == "wave_state":
        _need(ev, ["waveId", "state"], errs)
        if ev.get("state") in om["legacy_state_names"]:
            errs.append("wave_state: legacy state name %s — run `oser migrate` (renames to %s)"
                        % (ev["state"], om["legacy_state_names"][ev["state"]]))
        _in(ev, "state", om["wave_states"], errs)
    elif kind == "defect":
        _need(ev, ["waveId", "phase"], errs)
        _in(ev, "phase", ["before_integration", "after_acceptance"], errs)
    elif kind == "root_handoff":
        _need(ev, ["fromSessionId", "toSessionId", "reason", "stateRefs"], errs)
    elif kind == "decision":
        _need(ev, ["decisionId", "zone", "decidedBy", "subject"], errs)
        _in(ev, "zone", om["decision_zones"], errs)
        _in(ev, "decidedBy", ["root", "governor", "founder"], errs)
        zone = ev.get("zone")
        if zone in ("GREEN", "AMBER"):
            if not ev.get("rationale"):
                errs.append("decision: %s requires rationale (record rationale, continue)" % zone)
            if ev.get("escalated_to_founder"):
                errs.append("decision: engineering uncertainty (%s) must not be escalated to Founder — "
                            "inspect evidence, compare, test, choose a winner, record rationale, continue" % zone)
            if ev.get("decidedBy") == "founder":
                errs.append("decision: %s decisions belong to Root/Governor, not Founder (execution approval is "
                            "recorded as execution_approval_by, not as decision ownership)" % zone)
        if zone == "AMBER" and (not ev.get("alternatives") or not ev.get("winner")):
            errs.append("decision: AMBER requires alternatives[] and winner")
        if zone == "RED":
            if ev.get("red_basis") not in om["red_zone"]:
                errs.append("decision: RED requires red_basis in red_zone (%s)" % "; ".join(om["red_zone"]))
            if ev.get("decidedBy") == "governor":
                errs.append("decision: a governor cannot decide RED")
    elif kind == "quota_reading":
        _need(ev, ["source"], errs)
        for k in ("weekly_all_models_pct", "weekly_fable_pct"):
            if k in ev and not isinstance(ev[k], (int, float)):
                errs.append("quota_reading: %s must be a number" % k)
    else:
        errs.append("unknown event %r" % kind)
    return errs


def migrate_file(root):
    """Explicit rename of legacy lifecycle state names (3.x) — returns number of rewritten lines, 0 when clean."""
    p = path(root)
    if not os.path.isfile(p):
        return 0
    legacy = _om()["legacy_state_names"]
    out, n = [], 0
    with io.open(p, encoding="utf-8") as f:
        for line in f:
            try:
                ev = json.loads(line)
            except ValueError:
                out.append(line)
                continue
            if ev.get("state") in legacy:
                ev["state"] = legacy[ev["state"]]
                n += 1
                line = json.dumps(ev, ensure_ascii=False, sort_keys=True) + "\n"
            out.append(line)
    if n:
        with io.open(p, "w", encoding="utf-8", newline="\n") as f:
            f.writelines(out)
    return n


def read(root):
    p = path(root)
    out = []
    if not os.path.isfile(p):
        return out
    with io.open(p, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append((n, json.loads(line)))
            except ValueError:
                out.append((n, {"event": "__invalid_json__"}))
    return out


def append(root, ev, manifest=None):
    ev = dict(ev)
    ev.setdefault("at", now_iso())
    errs = validate_event(ev, manifest)
    state = fold(read(root) + [(0, ev)])
    errs += state["errors_last"]
    if errs:
        return errs
    os.makedirs(os.path.dirname(path(root)), exist_ok=True)
    with io.open(path(root), "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(ev, ensure_ascii=False, sort_keys=True) + "\n")
    return []


def fold(records, manifest=None):
    """Replay events into waves/packets and check lifecycle order. Returns state + errors."""
    om = _om()
    P, W = om["packet_states"], om["wave_states"]
    waves, packets, defects, handoffs, readings, errors, decisions = {}, {}, [], [], [], [], []
    last_errs = []
    for n, ev in records:
        errs = []
        k = ev.get("event")
        if k == "__invalid_json__":
            errs.append("line %d: invalid JSON" % n)
        elif k == "wave_open":
            if ev.get("waveId") in waves:
                errs.append("wave %s opened twice" % ev.get("waveId"))
            else:
                waves[ev["waveId"]] = {"open": ev, "states": ["OPEN"], "packets": [], "result_chars": None,
                                       "accepted_at": None}
        elif k == "packet_open":
            w = waves.get(ev.get("waveId"))
            if w is None:
                errs.append("packet %s: unknown wave %s" % (ev.get("packetId"), ev.get("waveId")))
            elif ev.get("packetId") in packets:
                errs.append("packet %s opened twice" % ev.get("packetId"))
            elif w["states"][-1] != "OPEN":
                errs.append("packet %s: wave %s no longer OPEN" % (ev.get("packetId"), ev.get("waveId")))
            else:
                packets[ev["packetId"]] = {"open": ev, "states": ["ASSIGNED"], "attempts": []}
                w["packets"].append(ev["packetId"])
        elif k == "attempt":
            p = packets.get(ev.get("packetId"))
            if p is None:
                errs.append("attempt: unknown packet %s" % ev.get("packetId"))
            else:
                p["attempts"].append(ev)
        elif k == "packet_state":
            p = packets.get(ev.get("packetId"))
            s = ev.get("state")
            if p is None:
                errs.append("packet_state: unknown packet %s" % ev.get("packetId"))
            elif p["states"][-1] in ("GOVERNOR_ACCEPTED", "REJECTED"):
                errs.append("packet %s already terminal (%s)" % (ev["packetId"], p["states"][-1]))
            elif s != "REJECTED" and s in P and P.index(s) <= P.index(p["states"][-1]):
                errs.append("packet %s: %s cannot follow %s" % (ev["packetId"], s, p["states"][-1]))
            else:
                if s == "GOVERNOR_ACCEPTED":
                    if "MACHINE_VERIFIED" not in p["states"]:
                        errs.append("packet %s: GOVERNOR_ACCEPTED without MACHINE_VERIFIED" % ev["packetId"])
                    if p["open"].get("verification_depth") != "machine" and "INDEPENDENT_REVIEWED" not in p["states"]:
                        errs.append("packet %s: depth %s requires INDEPENDENT_REVIEWED before acceptance"
                                    % (ev["packetId"], p["open"].get("verification_depth")))
                if not errs:
                    p["states"].append(s)
                    p.setdefault("state_events", []).append(ev)
        elif k == "wave_state":
            w = waves.get(ev.get("waveId"))
            s = ev.get("state")
            if w is None:
                errs.append("wave_state: unknown wave %s" % ev.get("waveId"))
            elif w["states"][-1] in ("ROOT_ACCEPTED", "ROOT_REJECTED"):
                errs.append("wave %s already terminal" % ev["waveId"])
            elif s != "ROOT_REJECTED" and s in W and W.index(s) != W.index(w["states"][-1]) + 1:
                errs.append("wave %s: %s cannot follow %s" % (ev["waveId"], s, w["states"][-1]))
            else:
                if s in ("PACKETS_ACCEPTED", "ROOT_ACCEPTED"):
                    open_p = [pid for pid in w["packets"] if packets[pid]["states"][-1] not in ("GOVERNOR_ACCEPTED", "REJECTED")]
                    if open_p:
                        errs.append("wave %s: %s with packets not terminal: %s" % (ev["waveId"], s, ", ".join(open_p)))
                if not errs:
                    w["states"].append(s)
                    if s == "ROOT_ACCEPTED":
                        w["accepted_at"] = ev.get("at")
                        w["result_chars"] = ev.get("clean_result_chars")
        elif k == "defect":
            defects.append(ev)
        elif k == "root_handoff":
            handoffs.append(ev)
        elif k == "quota_reading":
            readings.append(ev)
        elif k == "decision":
            if ev.get("decidedBy") == "governor":
                w = waves.get(ev.get("waveId"))
                if w is None or w["states"][-1] in ("ROOT_ACCEPTED", "ROOT_REJECTED"):
                    errs.append("decision %s: governor decisions need an open wave (waveId)" % ev.get("decisionId"))
            if not errs:
                decisions.append(ev)
        errs += [] if k == "__invalid_json__" else validate_event(ev, manifest)
        if errs:
            errors += ["line %d: %s" % (n, e) for e in errs]
        last_errs = errs
    return {"waves": waves, "packets": packets, "defects": defects, "handoffs": handoffs, "readings": readings,
            "decisions": decisions,
            "errors": errors, "errors_last": last_errs}
