"""One snapshot per native response, not per block, attempt or imported file.

Unknown identity, incomplete categories, conflicting snapshots and cross-Mission
attribution remain UNKNOWN/INVALID. No token -> quota, price or FLOP conversion.
"""
from __future__ import annotations

import json

from .capabilities import identity
from .common import OserError, canonical, digest, integer, require, text

CATEGORIES = ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens")


class Usage:
    def __init__(self, store):
        self.store = store

    def put(self, mission, record):
        self.store.read(mission)
        try:
            require(isinstance(record, dict), "INVALID_USAGE", "usage must be an object")
            scope = identity(record)
            scope["session_ref"] = text(record.get("session_ref"), "session_ref")
            request_id, response_id = record.get("request_id"), record.get("response_id")
            require(bool(request_id or response_id), "IDENTITY_UNKNOWN", "native response or request id is required")
            if request_id is not None:
                text(request_id, "request_id")
            if response_id is not None:
                text(response_id, "response_id")
            # Response ID is stable if a later content block adds request metadata.
            scope["native_id"] = "response:" + response_id if response_id else "request:" + request_id
            key = digest(scope)
        except OserError as exc:
            with self.store.transaction() as db:
                db.execute("INSERT OR IGNORE INTO usage_unknown VALUES (?, ?, ?)",
                           (digest({"mission": mission, "record": record}), mission, exc.code))
            return {"validity": "UNKNOWN", "reason": exc.code}
        validity = "VALID"
        counters = record.get("usage")
        if record.get("mode", "snapshot") != "snapshot":
            validity = "INVALID"
        if not isinstance(counters, dict) or not all(k in counters for k in CATEGORIES):
            validity = "INVALID" if validity == "INVALID" else "UNKNOWN"
        else:
            try:
                counters = {k: integer(counters[k], k) for k in CATEGORIES}
            except OserError:
                validity, counters = "INVALID", None
        body = {"identity": scope, "usage": counters, "mode": record.get("mode", "snapshot")}
        with self.store.transaction() as db:
            old = db.execute("SELECT mission,body,validity FROM usage WHERE key=?", (key,)).fetchone()
            if old:
                if old["mission"] != mission or old["body"] != canonical(body):
                    db.execute("UPDATE usage SET validity='INVALID' WHERE key=?", (key,))
                    return {"validity": "INVALID", "reason": "CONFLICTING_SNAPSHOT_OR_ATTRIBUTION"}
                return {"validity": old["validity"], "duplicate": True}
            db.execute("INSERT INTO usage VALUES (?, ?, ?, ?)", (key, mission, canonical(body), validity))
        return {"validity": validity, "duplicate": False}

    def report(self, mission):
        self.store.read(mission)
        with self.store.connection() as db:
            rows = list(db.execute("SELECT body,validity FROM usage WHERE mission=?", (mission,)))
            unknown = db.execute("SELECT COUNT(*) FROM usage_unknown WHERE mission=?", (mission,)).fetchone()[0]
        subtotal = {k: 0 for k in CATEGORIES}
        counts = {"VALID": 0, "INVALID": 0, "UNKNOWN": 0}
        for row in rows:
            counts[row["validity"]] += 1
            if row["validity"] == "VALID":
                usage = json.loads(row["body"])["usage"]
                for key in CATEGORIES:
                    subtotal[key] += usage[key]
        complete = bool(rows) and not (counts["INVALID"] or counts["UNKNOWN"] or unknown)
        return {"mission": mission, "validity": "VALID" if complete else "INVALID" if counts["INVALID"] else "UNKNOWN",
                "unique_responses": len(rows), "response_states": counts,
                "unattributed_unknown_records": unknown, "known_subtotal": subtotal,
                "total": subtotal if complete else None, "coverage": "IMPORTED_RECORDS_ONLY",
                "subscription_cost": None, "quota_percent": None}
