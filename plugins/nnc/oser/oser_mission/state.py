"""Transactional Mission state, immutable acceptance and crash-safe replay.

The API enforces projection invariants, not an OS sandbox. Anyone with arbitrary
write access to this database has the local user's trust; host approvals and
sandboxing remain authoritative. No model inference or deployment lives here.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path

from .capabilities import admit, validate_catalog, validate_policy
from .common import canonical, digest, epoch, file_hash, integer, project_root, require, safe_path, source_fingerprint, text, utcnow

TERMINAL = ("COMPLETED", "FAILED", "CANCELLED")
RUNTIME_STATES = ("RUNNING", "WAITING", "INTERRUPTED", "UNKNOWN") + TERMINAL


class Store:
    def __init__(self, project, create=False):
        self.root = project_root(project)
        directory = self.root / ".nnc-oser"
        require(not directory.is_symlink(), "UNSAFE_PATH", "state directory must not be a symlink")
        self.path = directory / "state.sqlite3"
        require(not self.path.is_symlink(), "UNSAFE_PATH", "state database must not be a symlink")
        if create:
            directory.mkdir(exist_ok=True)
            with self.connection() as db:
                db.executescript("""
                CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS missions (id TEXT PRIMARY KEY, revision INTEGER NOT NULL, state TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS events (key TEXT PRIMARY KEY, fingerprint TEXT NOT NULL,
                  mission TEXT NOT NULL, operation TEXT NOT NULL, result TEXT NOT NULL, at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS health (key TEXT PRIMARY KEY, body TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS usage (key TEXT PRIMARY KEY, mission TEXT NOT NULL, body TEXT NOT NULL, validity TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS usage_unknown (key TEXT PRIMARY KEY, reason TEXT NOT NULL);
                """)
                db.execute("INSERT OR IGNORE INTO meta VALUES ('schema', 'nnc-oser/store@1')")
        require(self.path.exists(), "NOT_INITIALIZED", "run oser init with a Mission contract first")
        with self.connection() as db:
            version = db.execute("SELECT value FROM meta WHERE key='schema'").fetchone()
            require(version and version[0] == "nnc-oser/store@1", "STORE_VERSION", "unsupported state store")

    @contextmanager
    def connection(self):
        db = sqlite3.connect(str(self.path), timeout=5, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=5000")
        db.execute("PRAGMA foreign_keys=ON")
        try:
            yield db
        finally:
            db.close()

    @contextmanager
    def transaction(self):
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                yield db
                db.commit()
            except BaseException:
                db.rollback()
                raise

    def read(self, mission):
        with self.connection() as db:
            row = db.execute("SELECT state FROM missions WHERE id=?", (mission,)).fetchone()
        require(row is not None, "MISSION_NOT_FOUND", "unknown mission")
        return json.loads(row[0])

    def list(self):
        with self.connection() as db:
            return [json.loads(row[0]) for row in db.execute("SELECT state FROM missions ORDER BY id")]

    def create(self, contract, event_key):
        require(isinstance(contract, dict), "INVALID_CONTRACT", "contract must be an object")
        mid = text(contract.get("id"), "mission.id")
        goal = text(contract.get("goal"), "mission.goal")
        baseline = deepcopy(contract.get("baseline"))
        require(isinstance(baseline, dict), "INVALID_CONTRACT", "baseline is required")
        text(baseline.get("id"), "baseline.id")
        refs = baseline.get("authority")
        require(isinstance(refs, list) and bool(refs), "AUTHORITY_REQUIRED", "at least one locked authority reference is required")
        for ref in refs:
            require(isinstance(ref, dict), "INVALID_AUTHORITY", "authority must be an object")
            if "path" in ref:
                actual = file_hash(safe_path(self.root, ref["path"]))
                require(ref.get("sha256", actual) == actual, "AUTHORITY_DRIFT", "local authority does not match its lock")
                ref["sha256"] = actual
            else:
                text(ref.get("ref"), "authority.ref")
                text(ref.get("revision"), "authority.revision")
        sources = deepcopy(contract.get("sources"))
        source_fingerprint(self.root, sources)
        acceptance = contract.get("acceptance")
        require(isinstance(acceptance, list) and bool(acceptance), "ACCEPTANCE_REQUIRED", "acceptance must have a stable denominator")
        normalized = {}
        for item in acceptance:
            require(isinstance(item, dict), "INVALID_ACCEPTANCE", "criterion must be an object")
            cid = text(item.get("id"), "criterion.id")
            require(cid not in normalized, "INVALID_ACCEPTANCE", "duplicate criterion")
            text(item.get("description"), "criterion.description")
            kinds = item.get("requires")
            require(isinstance(kinds, list) and bool(kinds) and all(isinstance(k, str) and k for k in kinds),
                    "INVALID_ACCEPTANCE", "criterion.requires lists the evidence kinds needed, e.g. test and behavioral")
            normalized[cid] = {"description": item["description"], "requires": sorted(set(kinds))}
        state = {"schema": "nnc-oser/mission@1", "id": mid, "goal": goal, "baseline": baseline,
                 "sources": sources, "acceptance": normalized, "policy": validate_policy(contract.get("policy")),
                 "owner": {"ref": text(contract.get("owner"), "owner"), "epoch": 0}, "revision": 0,
                 "status": "OPEN", "runtime_state": "UNKNOWN", "catalog": None, "executions": {},
                 "evidence": [], "checkpoints": [], "blockers": {}, "created_at": utcnow()}
        fingerprint = digest({"operation": "mission.create", "contract": contract})
        text(event_key, "event_key")
        with self.transaction() as db:
            previous = self._replay(db, event_key, fingerprint)
            if previous is not None:
                return previous
            require(db.execute("SELECT 1 FROM missions WHERE id=?", (mid,)).fetchone() is None,
                    "MISSION_EXISTS", "create a new Mission/baseline; do not overwrite locked acceptance")
            db.execute("INSERT INTO missions VALUES (?, 0, ?)", (mid, canonical(state)))
            self._event(db, event_key, fingerprint, mid, "mission.create", state)
        return state

    @staticmethod
    def _replay(db, key, fingerprint):
        previous = db.execute("SELECT fingerprint,result FROM events WHERE key=?", (key,)).fetchone()
        if previous:
            require(previous["fingerprint"] == fingerprint, "IDEMPOTENCY_CONFLICT", "event key was reused for different data")
            return json.loads(previous["result"])
        return None

    @staticmethod
    def _event(db, key, fingerprint, mid, operation, result):
        db.execute("INSERT INTO events VALUES (?, ?, ?, ?, ?, ?)",
                   (key, fingerprint, mid, operation, canonical(result), utcnow()))

    def apply(self, mission, operation, payload, expected_revision, event_key, actor, owner_epoch):
        require(isinstance(payload, dict), "INVALID_INPUT", "payload must be an object")
        integer(expected_revision, "expected_revision")
        integer(owner_epoch, "owner_epoch")
        text(event_key, "event_key")
        text(actor, "actor")
        fingerprint = digest({"mission": mission, "operation": operation, "payload": payload,
                              "actor": actor, "owner_epoch": owner_epoch})
        with self.transaction() as db:
            replay = self._replay(db, event_key, fingerprint)
            if replay is not None:
                return replay
            row = db.execute("SELECT state,revision FROM missions WHERE id=?", (mission,)).fetchone()
            require(row is not None, "MISSION_NOT_FOUND", "unknown mission")
            require(row["revision"] == expected_revision, "REVISION_CONFLICT", "read current Mission before retrying")
            state = json.loads(row["state"])
            # A late native receipt may arrive after ownership transfer. It can
            # update execution facts, never acceptance, policy or ownership.
            if operation != "execution.receipt":
                require(state["owner"] == {"ref": actor, "epoch": owner_epoch},
                        "OWNER_CONFLICT", "stale owner or ownership epoch")
            self._reduce(state, operation, payload)
            state["revision"] += 1
            db.execute("UPDATE missions SET revision=?,state=? WHERE id=?", (state["revision"], canonical(state), mission))
            self._event(db, event_key, fingerprint, mission, operation, state)
            return state

    def _reduce(self, state, operation, p):
        if operation == "catalog.record":
            state["catalog"] = validate_catalog(p)
        elif operation == "execution.open":
            ref = text(p.get("ref"), "execution.ref")
            require(ref not in state["executions"], "EXECUTION_EXISTS", "use a new segment id for a continuation")
            active = sum(e["status"] not in TERMINAL for e in state["executions"].values())
            require(active < state["policy"].get("max_active_executions", 1), "CONCURRENCY_LIMIT", "active execution envelope exhausted")
            result = admit(state["catalog"], state["policy"], p.get("request", {}))
            require(result["status"] == "ADMITTED", result.get("code", "ADMISSION_DENIED"), result.get("reason", "admission failed"))
            relation = p.get("relation")
            if relation is not None:
                require(isinstance(relation, dict) and relation.get("from") in state["executions"], "UNKNOWN_RELATION", "continuation needs an existing predecessor")
                text(relation.get("native_relation"), "native_relation")
            state["executions"][ref] = {"ref": ref, "native_ref": text(p.get("native_ref"), "native_ref"),
                                          "plan": result, "relation": relation, "status": "UNKNOWN", "reconciled": False,
                                          "observed": None, "policy_violations": [], "opened_at": utcnow()}
            state["status"] = "OPEN"
        elif operation == "execution.receipt":
            ref = p.get("ref")
            require(ref in state["executions"], "EXECUTION_NOT_FOUND", "receipt does not match an execution")
            execution = state["executions"][ref]
            require(p.get("native_ref") == execution["native_ref"], "NATIVE_REF_MISMATCH", "receipt native identity mismatch")
            text(p.get("source_ref"), "receipt.source_ref")
            observed_at = text(p.get("observed_at"), "observed_at")
            epoch(observed_at)
            status = p.get("status")
            require(status in RUNTIME_STATES, "INVALID_STATUS", "normalize runtime status; preserve the native status separately")
            if execution.get("observed_at"):
                require(epoch(observed_at) >= epoch(execution["observed_at"]), "STALE_RECEIPT", "receipt predates the last observed execution event")
            require(execution["status"] not in TERMINAL or execution["status"] == status,
                    "TERMINAL_CONFLICT", "terminal segments are immutable; resume is a new segment")
            observed = p.get("observed", {})
            require(isinstance(observed, dict), "INVALID_RECEIPT", "observed must be an object")
            resolved = execution["plan"]["resolved"]
            violations = [key for key in ("host", "provider", "account", "model", "effort")
                          if key in observed and observed[key] != resolved.get(key)]
            execution.update(status=status, observed=observed, source_ref=p["source_ref"], observed_at=observed_at,
                             native_status=p.get("native_status"), reconciled=False)
            execution["policy_violations"] = sorted(set(execution["policy_violations"] + violations))
        elif operation == "execution.reconcile":
            ref = p.get("ref")
            require(ref in state["executions"], "EXECUTION_NOT_FOUND", "unknown execution")
            execution = state["executions"][ref]
            require(execution["status"] in TERMINAL, "NOT_TERMINAL", "reconcile only after a terminal receipt")
            text(p.get("evidence_ref"), "reconciliation evidence_ref")
            proof = safe_path(self.root, p["evidence_ref"])
            execution.update(reconciled=True, reconciliation={"path": p["evidence_ref"], "sha256": file_hash(proof)})
        elif operation == "checkpoint.record":
            text(p.get("summary"), "checkpoint.summary")
            text(p.get("next_action"), "checkpoint.next_action")
            mode = p.get("runtime_state", "UNKNOWN")
            require(mode in ("RUNNING", "WAITING", "INTERRUPTED", "UNKNOWN", "RECOVERING"), "INVALID_STATUS", "invalid checkpoint runtime state")
            if mode == "WAITING":
                require(bool(p.get("waiting_for")) or bool(p.get("external_wait_ref")), "WAIT_REASON_REQUIRED", "waiting is legal with a durable dependency")
                require(all(ref in state["executions"] for ref in p.get("waiting_for", [])), "UNKNOWN_DEPENDENCY", "waiting execution not registered")
            state["checkpoints"].append({"summary": p["summary"], "next_action": p["next_action"],
                                         "owner": deepcopy(state["owner"]), "at": utcnow(),
                                         "open_executions": [ref for ref, e in state["executions"].items() if not e["reconciled"]],
                                         "waiting_for": p.get("waiting_for", []), "external_wait_ref": p.get("external_wait_ref"),
                                         "source_hash": source_fingerprint(self.root, state["sources"])})
            state["runtime_state"] = mode
        elif operation == "ownership.transfer":
            require(bool(state["checkpoints"]), "CHECKPOINT_REQUIRED", "transfer requires durable continuation state")
            text(p.get("to"), "new owner")
            require(p["to"] != state["owner"]["ref"], "OWNER_CONFLICT", "new owner must differ")
            text(p.get("reason"), "transfer.reason")
            state["owner"] = {"ref": p["to"], "epoch": state["owner"]["epoch"] + 1}
            state["runtime_state"] = "RECOVERING"
        elif operation == "evidence.record":
            criterion = p.get("criterion")
            require(criterion in state["acceptance"], "UNKNOWN_CRITERION", "execution tasks cannot change acceptance")
            require(p.get("kind") in state["acceptance"][criterion]["requires"], "EVIDENCE_KIND", "evidence kind does not satisfy this criterion")
            require(p.get("outcome") in ("pass", "fail"), "EVIDENCE_OUTCOME", "explicit pass/fail required")
            text(p.get("producer_ref"), "producer_ref")
            path = safe_path(self.root, p.get("path"))
            state["evidence"].append({"criterion": criterion, "kind": p["kind"], "outcome": p["outcome"],
                                      "path": p["path"], "sha256": file_hash(path), "producer_ref": p["producer_ref"],
                                      "source_hash": source_fingerprint(self.root, state["sources"]), "baseline": state["baseline"]["id"],
                                      "at": utcnow(), "trust": "HOST_ATTESTATION", "note": p.get("note", "")})
            state["status"] = "OPEN"
        elif operation == "blocker.set":
            bid = text(p.get("id"), "blocker.id")
            text(p.get("summary"), "blocker.summary")
            require(type(p.get("resolved", False)) is bool, "INVALID_INPUT", "resolved must be boolean")
            state["blockers"][bid] = {"summary": p["summary"], "resolved": p.get("resolved", False),
                                       "kind": p.get("kind", "dependency"), "evidence_ref": p.get("evidence_ref")}
            # Tracking an approval never grants provider/deployment permissions.
        elif operation == "mission.complete":
            view = self.evaluate(state)
            require(view["accepted"] == view["total"] and view["authority_status"] != "DRIFT", "ACCEPTANCE_INCOMPLETE", "all current acceptance evidence must pass")
            require(not view["blockers"], "BLOCKED", "unresolved blockers remain")
            require(all(e["status"] in TERMINAL and e["reconciled"] and not e["policy_violations"] for e in state["executions"].values()),
                    "UNRECONCILED_EXECUTION", "execution result or policy mismatch remains unaccounted")
            state["status"] = "DONE"
        else:
            require(False, "UNKNOWN_OPERATION", "operation is not a Mission kernel operation")

    def evaluate(self, state):
        source_hash = source_fingerprint(self.root, state["sources"])
        authority_status = "LOCKED_LOCAL"
        for ref in state["baseline"]["authority"]:
            if "path" in ref:
                try:
                    actual = file_hash(safe_path(self.root, ref["path"]))
                except (ValueError, OSError):
                    actual = None
                if actual != ref["sha256"]:
                    authority_status = "DRIFT"
            elif authority_status != "DRIFT":
                authority_status = "REFERENCE_ONLY"
        criteria = []
        for cid, criterion in state["acceptance"].items():
            kinds = {}
            for kind in criterion["requires"]:
                candidates = [e for e in state["evidence"] if e["criterion"] == cid and e["kind"] == kind]
                status = "MISSING"
                if candidates:
                    evidence = candidates[-1]
                    try:
                        actual = file_hash(safe_path(self.root, evidence["path"]))
                    except (ValueError, OSError):
                        actual = None
                    current = (evidence["baseline"] == state["baseline"]["id"] and evidence["source_hash"] == source_hash
                               and actual == evidence["sha256"] and authority_status != "DRIFT")
                    status = ("PASS" if evidence["outcome"] == "pass" else "FAIL") if current else "STALE"
                kinds[kind] = status
            criteria.append({"id": cid, "description": criterion["description"], "evidence": kinds,
                             "accepted": all(value == "PASS" for value in kinds.values())})
        accepted = sum(c["accepted"] for c in criteria)
        pending = [ref for ref, e in state["executions"].items() if e["status"] in TERMINAL and not e["reconciled"]]
        violations = [ref for ref, e in state["executions"].items() if e["policy_violations"]]
        effective = "REOPENED" if state["status"] == "DONE" and (accepted != len(criteria) or authority_status == "DRIFT") else state["status"]
        return {"id": state["id"], "goal": state["goal"], "revision": state["revision"], "owner": state["owner"],
                "status": effective, "runtime_state": state["runtime_state"], "authority_status": authority_status,
                "accepted": accepted, "total": len(criteria), "verified_percent": round(100 * accepted / len(criteria)),
                "percentage_meaning": "current acceptance coverage, not remaining time", "criteria": criteria,
                "frontier": [c["id"] for c in criteria if not c["accepted"]], "source_hash": source_hash,
                "unreconciled": pending, "policy_violations": violations,
                "blockers": [dict(value, id=key) for key, value in state["blockers"].items() if not value["resolved"]],
                "checkpoint": state["checkpoints"][-1] if state["checkpoints"] else None,
                "recovery": "MANUAL_RESUME_REQUIRED", "automatic_wake": "UNAVAILABLE"}

    def view(self, mission):
        return self.evaluate(self.read(mission))
