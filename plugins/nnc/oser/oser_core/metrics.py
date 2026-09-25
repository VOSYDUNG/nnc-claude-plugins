# -*- coding: utf-8 -*-
"""Value metrics of the operating model, computed from the ledger joined with RAW transcript usage.

Scalar used for ratios: `work` tokens (runtime.json › units). Every metric also reports what it could not
see (`unknown`) instead of inventing numbers. The benchmark unit is the VERIFIED RESULT, not a call.
"""
import datetime
from collections import defaultdict

from . import ledger
from .transcripts import Index, add, family, project_transcript_dirs, zero


def _secs(a, b):
    try:
        t = lambda s: datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return max(0.0, (t(b) - t(a)).total_seconds())
    except (ValueError, AttributeError):
        return None


def attempt_usage(idx, att):
    x = att.get("execution") or {}
    u = idx.usage(x.get("sessionId"), x.get("agentId") or "", x.get("from"), x.get("to"))
    ev = [e for e in idx.by_exec.get((x.get("sessionId"), x.get("agentId") or ""), [])
          if not ((x.get("from") and e["ts"] < x["from"]) or (x.get("to") and e["ts"] > x["to"]))]
    u["wall_s"] = att.get("wall_s") if att.get("wall_s") is not None else (_secs(ev[0]["ts"], ev[-1]["ts"]) if ev else None)
    u["prompt_avg"] = (sum(e["v"]["input"] + e["v"]["cache_read"] + e["v"]["cache_creation"] for e in ev) / len(ev)) if ev else None
    u["seen"] = bool(ev)
    return u


def compute(root, manifest=None, wave=None):
    st = ledger.fold(ledger.read(root), manifest)
    idx = Index(project_transcript_dirs(root, all_machines=True))
    waves = {k: v for k, v in st["waves"].items() if wave is None or k == wave}
    packets = {k: v for k, v in st["packets"].items() if k in {p for w in waves.values() for p in w["packets"]}}
    unknown = []

    usage_att = {}
    for pid, p in packets.items():
        for a in p["attempts"]:
            usage_att[(pid, a["attempt"], a["role"])] = attempt_usage(idx, a)
            if not usage_att[(pid, a["attempt"], a["role"])]["seen"]:
                unknown.append("no transcript usage for %s attempt %s (%s)" % (pid, a["attempt"], a["execution"].get("sessionId")))

    def ptotal(pid):
        acc = zero()
        for a in packets[pid]["attempts"]:
            add(acc, usage_att[(pid, a["attempt"], a["role"])])
        return acc

    terminal = [pid for pid, p in packets.items() if p["states"][-1] in ("FABLE_ACCEPTED", "REJECTED")]
    accepted = [pid for pid in terminal if packets[pid]["states"][-1] == "FABLE_ACCEPTED"]

    def impl(pid):
        return [a for a in packets[pid]["attempts"] if a["role"] in ("implement", "solve_independent")]

    first_pass = [pid for pid in accepted if len(impl(pid)) == 1 and impl(pid)[0]["outcome"] == "pass"]

    # A · VERIFIED_RESULT_COST
    vrc = [ptotal(pid)["work"] for pid in accepted]
    # C · REWORK_AMPLIFICATION
    tot = sum(ptotal(pid)["work"] for pid in terminal)
    first = sum(usage_att[(pid, impl(pid)[0]["attempt"], impl(pid)[0]["role"])]["work"] for pid in terminal if impl(pid))

    # governor + root per wave
    gov, growth, isolation_below, isolation_up = {}, [], 0, 0
    for wid, w in waves.items():
        g = w["open"].get("governor") or {}
        gu = idx.usage(g.get("sessionId"), g.get("agentId") or "")
        gov[wid] = gu
        if w["states"][-1] == "ROOT_ACCEPTED":
            rs = w["open"].get("rootSessionId")
            a0 = idx.prompt_size_at(rs, w["open"].get("at", ""))
            a1 = idx.prompt_size_at(rs, w.get("accepted_at") or "")
            below = gu["work"] + gu["cache_read"] + sum(ptotal(pid)["work"] + ptotal(pid)["cache_read"] for pid in w["packets"])
            if a0 is not None and a1 is not None:
                growth.append(a1 - a0)
                isolation_below += below
                isolation_up += max(1, a1 - a0)
            elif w.get("result_chars"):
                isolation_below += below
                isolation_up += max(1, int(w["result_chars"] / 4))
                unknown.append("wave %s: Root transcript not found — isolation uses clean_result_chars/4" % wid)
            else:
                unknown.append("wave %s: Root context growth not observable" % wid)

    # F · DEFECT_CONTAINMENT
    before = sum(int(a.get("defects") or 0) for p in packets.values() for a in p["attempts"] if a["role"] in ("verify", "review"))
    before += sum(1 for d in st["defects"] if d.get("phase") == "before_integration" and (wave is None or d.get("waveId") == wave))
    after = sum(1 for d in st["defects"] if d.get("phase") == "after_acceptance" and (wave is None or d.get("waveId") == wave))

    # G · FABLE_LEVERAGE — measured family, not declared plan
    fable_work = 0
    for gu in gov.values():
        fable_work += sum(v for mdl, v in gu["models"].items() if family(mdl) == "fable")
    for u in usage_att.values():
        fable_work += sum(v for mdl, v in u["models"].items() if family(mdl) == "fable")

    # H · ESCALATION_EFFICIENCY
    esc = [pid for pid in terminal if any(a["outcome"] == "escalate" for a in packets[pid]["attempts"])]
    esc_ok = [pid for pid in esc if pid in accepted]

    ratio = lambda a, b: (a / b) if b else None
    m = {
        "waves_root_accepted": sum(1 for w in waves.values() if w["states"][-1] == "ROOT_ACCEPTED"),
        "packets_terminal": len(terminal), "packets_accepted": len(accepted),
        "VERIFIED_RESULT_COST": {"per_accepted_packet_work_mean": ratio(sum(vrc), len(vrc)),
                                 "per_root_accepted_wave_work_mean": ratio(
                                     sum(gov[w]["work"] + sum(ptotal(p)["work"] for p in waves[w]["packets"])
                                         for w in waves if waves[w]["states"][-1] == "ROOT_ACCEPTED"),
                                     sum(1 for w in waves.values() if w["states"][-1] == "ROOT_ACCEPTED"))},
        "FIRST_PASS_ACCEPT_RATE": ratio(len(first_pass), len(terminal)),
        "REWORK_AMPLIFICATION": ratio(tot, first),
        "ROOT_CONTEXT_GROWTH": {"per_accepted_wave_mean_tokens": ratio(sum(growth), len(growth)),
                                "waves_measured": len(growth), "root_handoffs": len(st["handoffs"])},
        "CONTEXT_ISOLATION_GAIN": ratio(isolation_below, isolation_up),
        "DEFECT_CONTAINMENT": {"before_integration": before, "after_acceptance": after, "rate": ratio(before, before + after)},
        "FABLE_LEVERAGE": {"accepted_packets_per_M_fable_work": ratio(len(accepted), fable_work / 1e6) if fable_work else None,
                           "fable_work": fable_work},
        "ESCALATION_EFFICIENCY": {"escalated": len(esc), "resolved": len(esc_ok), "rate": ratio(len(esc_ok), len(esc)),
                                  "work_mean": ratio(sum(ptotal(p)["work"] for p in esc), len(esc))},
        "DECISIONS": {z: sum(1 for d in st["decisions"] if d.get("zone") == z) for z in ("GREEN", "AMBER", "RED")},
        "FOUNDER_ESCALATIONS": sum(1 for d in st["decisions"] if d.get("escalated_to_founder")),
        "plans": plan_benchmark(packets, usage_att, accepted),
        "ledger_errors": st["errors"], "unknown": unknown,
    }
    return m


def plan_benchmark(packets, usage_att, accepted):
    """Per declared (model, effort) — and per (taskClass, model, effort) — outcome of the work it produced."""
    rows = defaultdict(lambda: {"attempts": 0, "first_pass": 0, "first_attempts": 0, "rework": 0, "verify_defects": 0,
                                "work": 0, "thinking": 0, "prompt_sum": 0.0, "prompt_n": 0, "wall_s": 0.0,
                                "final_accepted": 0, "observed_model_mismatch": 0})
    for pid, p in packets.items():
        last_impl_key = None
        impls = [a for a in p["attempts"] if a["role"] in ("implement", "solve_independent")]
        for a in p["attempts"]:
            u = usage_att[(pid, a["attempt"], a["role"])]
            plan = a.get("plan") or {}
            for key in ((plan.get("model"), plan.get("effort")), (p["open"].get("taskClass"), plan.get("model"), plan.get("effort"))):
                r = rows[key]
                r["attempts"] += 1
                r["work"] += u["work"]
                r["thinking"] += u["thinking"]
                if u["prompt_avg"] is not None:
                    r["prompt_sum"] += u["prompt_avg"]; r["prompt_n"] += 1
                r["wall_s"] += u["wall_s"] or 0
                if u["models"] and plan.get("model") and plan["model"] not in u["models"]:
                    r["observed_model_mismatch"] += 1
                if a["role"] in ("implement", "solve_independent"):
                    if impls and a is impls[0]:
                        r["first_attempts"] += 1
                        if a["outcome"] == "pass" and len(impls) == 1 and pid in accepted:
                            r["first_pass"] += 1
                    if a["outcome"] in ("fail", "rework_required"):
                        r["rework"] += 1
            if a["role"] in ("implement", "solve_independent"):
                last_impl_key = (plan.get("model"), plan.get("effort"))
            elif a["role"] in ("verify", "review") and last_impl_key and a.get("defects"):
                rows[last_impl_key]["verify_defects"] += int(a["defects"])
        if pid in accepted and impls:
            fp = impls[-1].get("plan") or {}
            rows[(fp.get("model"), fp.get("effort"))]["final_accepted"] += 1
            rows[(p["open"].get("taskClass"), fp.get("model"), fp.get("effort"))]["final_accepted"] += 1
    out = []
    for key, r in rows.items():
        out.append(dict(r, key=list(key), first_pass_rate=(r["first_pass"] / r["first_attempts"]) if r["first_attempts"] else None,
                        prompt_avg=(r["prompt_sum"] / r["prompt_n"]) if r["prompt_n"] else None))
    return sorted(out, key=lambda r: (len(r["key"]), [str(x) for x in r["key"]]))


def resources(root):
    """Weekly all-models vs nested Fable raw usage + UI quota readings (caps themselves are UI-only)."""
    idx = Index(project_transcript_dirs(root, all_machines=True))
    from .transcripts import iso_week
    allw, fab = defaultdict(zero), defaultdict(zero)
    for evs in idx.by_exec.values():
        for e in evs:
            wk = iso_week(e["ts"])
            add(allw[wk], e["v"])
            if family(e["model"]) == "fable":
                add(fab[wk], e["v"])
    readings = ledger.fold(ledger.read(root))["readings"]
    return {"weekly_all_models_work": {k: v["work"] for k, v in sorted(allw.items())},
            "weekly_fable_work": {k: v["work"] for k, v in sorted(fab.items())},
            "ui_readings": readings,
            "caps": "UI-only (not derivable from transcripts); nested: Fable counts toward all-models"}
