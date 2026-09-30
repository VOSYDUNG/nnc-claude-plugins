"""Local observation only. Re-reading an old payload never refreshes its age."""
from __future__ import annotations

import json
from copy import deepcopy

from .capabilities import identity
from .common import canonical, digest, epoch, number, require, text, utcnow


class Health:
    def __init__(self, store):
        self.store = store

    def put(self, sample, now=None):
        require(isinstance(sample, dict), "INVALID_SAMPLE", "health sample must be an object")
        identity(sample)
        text(sample.get("bucket"), "bucket")
        text(sample.get("source_ref"), "source_ref")
        require(sample.get("kind") in ("quota", "context", "runtime"), "INVALID_SAMPLE", "unknown health kind")
        received_at = now or utcnow()
        number(sample.get("ttl_seconds"), "sample ttl_seconds", 1, 86400)
        observed = sample.get("observed_at")
        if observed is not None:
            require(epoch(observed) <= epoch(received_at), "INVALID_TIME", "sample is from the future")
        if sample.get("used_percent") is not None:
            number(sample["used_percent"], "used_percent", 0, 100)
        if sample.get("resets_at") is not None:
            number(sample["resets_at"], "resets_at")
        scope = dict(identity(sample), kind=sample["kind"], bucket=sample["bucket"])
        key = digest(scope)
        body = deepcopy(sample)
        body["fetched_at"] = received_at
        with self.store.transaction() as db:
            old_row = db.execute("SELECT body FROM health WHERE key=?", (key,)).fetchone()
            if old_row:
                old = json.loads(old_row[0])
                if old.get("observed_at") and observed and epoch(observed) < epoch(old["observed_at"]):
                    return {"changed": False, "reason": "OLDER_SAMPLE", "model_calls": 0}
                compare_old = {k: v for k, v in old.items() if k != "fetched_at"}
                compare_new = {k: v for k, v in body.items() if k != "fetched_at"}
                if compare_old == compare_new:
                    return {"changed": False, "reason": "UNCHANGED", "model_calls": 0}
            db.execute("INSERT OR REPLACE INTO health VALUES (?, ?)", (key, canonical(body)))
        return {"changed": True, "model_calls": 0}

    def read(self, now=None):
        clock = epoch(now or utcnow())
        with self.store.connection() as db:
            samples = [json.loads(row[0]) for row in db.execute("SELECT body FROM health ORDER BY key")]
        for sample in samples:
            observed = sample.get("observed_at")
            age = clock - epoch(observed) if observed else None
            state = "UNKNOWN"
            if age is not None:
                state = "FRESH" if 0 <= age <= sample["ttl_seconds"] else "STALE"
                if sample.get("resets_at") is not None and clock >= sample["resets_at"]:
                    state = "STALE"
            if sample["kind"] in ("context", "quota") and sample.get("used_percent") is None:
                state = "UNKNOWN"
            sample.update(freshness=state, age_seconds=age)
        return samples


def render(view, samples):
    """A text Mission surface, not an agent conversation dashboard."""
    lines = ["NNC OSER | " + view["id"] + " | " + view["goal"],
             "%s | verified %s/%s (%s%% acceptance, NOT time)" %
             (view["status"], view["accepted"], view["total"], view["verified_percent"]),
             "Frontier: " + (", ".join(view["frontier"]) or "all criteria have current evidence"),
             "Runtime: %s | authority: %s | automatic wake: %s" %
             (view["runtime_state"], view["authority_status"], view["automatic_wake"])]
    for criterion in view["criteria"]:
        mark = "[x]" if criterion["accepted"] else "[ ]"
        lines.append("%s %s %s | %s" % (mark, criterion["id"], criterion["description"],
                                              ", ".join(k + "=" + v for k, v in criterion["evidence"].items())))
    if not samples:
        lines.append("Health: UNKNOWN (no independent runtime samples)")
    for sample in samples:
        percent = sample.get("used_percent")
        value = "UNKNOWN" if percent is None else "%g%% used" % percent
        bar = ""
        if percent is not None:
            n = int(percent // 10)
            bar = " [" + "#" * n + "." * (10 - n) + "]"
        lines.append("%s %s/%s/%s %s: %s%s | %s | observed=%s" %
                     (sample["kind"], sample["host"], sample["provider"], sample["account"], sample["bucket"],
                      value, bar, sample["freshness"], sample.get("observed_at") or "UNKNOWN"))
    for blocker in view["blockers"]:
        lines.append("! %s %s: %s" % (blocker["kind"], blocker["id"], blocker["summary"]))
    if view["unreconciled"]:
        lines.append("! RECONCILIATION_REQUIRED: " + ", ".join(view["unreconciled"]))
    if view["policy_violations"]:
        lines.append("! OBSERVED_POLICY_MISMATCH: " + ", ".join(view["policy_violations"]))
    if view["checkpoint"]:
        lines.append("Next: " + view["checkpoint"]["next_action"])
    return "\n".join(lines)
