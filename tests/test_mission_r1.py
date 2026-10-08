"""R1 conformance: synthetic/offline fixtures, NOT live-host certification.

No credentials, real quota, inference calls, production changes or user settings.
Run: python -m unittest discover -s tests -v
"""
import copy
import io
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

HOME = Path(__file__).resolve().parents[1] / "plugins/nnc/oser"
sys.path.insert(0, str(HOME))
from oser_mission.adapters import claude_current_catalog, claude_health, claude_lifecycle, claude_usage, codex_catalog, codex_health
from oser_mission.capabilities import admit
from oser_mission.cli import initialize, migration_plan
from oser_mission.common import OserError, canonical, digest, safe_path, utcnow
from oser_mission.health import Health, render
from oser_mission.mcp import invoke, serve
from oser_mission.probe import codex_probe
from oser_mission.state import Store
from oser_mission.usage import Usage


def at(seconds=0):
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat().replace("+00:00", "Z")


def binding(host="fixture-host", provider="fixture-provider", account="fixture-account"):
    return {"host": host, "provider": provider, "account": account,
            "allowed_efforts": ["low", "medium", "high", "xhigh"],
            "allowed_actions": ["inference"], "allow_uncontrolled_effort": False}


def catalog(host="fixture-host", provider="fixture-provider", account="fixture-account"):
    return {"schema": "nnc-oser/capabilities@1", "host": host, "provider": provider, "account": account,
            "observed_at": at(-1), "ttl_seconds": 3600, "evidence_state": "PROBED", "source_ref": "synthetic:catalog",
            "default_model": "candidate-v2", "aliases": {"latest": "candidate-v2"},
            "models": [{"id": model, "available": True, "efforts": ["low", "medium", "high", "xhigh", "max"],
                        "default_effort": "high", "effort_scopes": ["execution", "child"], "context_window": 32768}
                       for model in ("candidate-v1", "candidate-v2")]}


def contract():
    return {"id": "M1", "goal": "Deliver approved behavior", "owner": "owner-a",
            "baseline": {"id": "B1", "authority": [{"path": "docs/PRD.md"}]}, "sources": ["src"],
            "acceptance": [{"id": "A1", "description": "Matches tests AND approved behavior", "requires": ["test", "behavioral"]}],
            "policy": {"bindings": [binding()], "max_active_executions": 4}}


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="oser-r1-")
        self.root = Path(self.tmp.name)
        (self.root / "src").mkdir()
        (self.root / "docs").mkdir()
        (self.root / "proof").mkdir()
        (self.root / "src/app.txt").write_text("original\n", encoding="utf-8")
        (self.root / "docs/PRD.md").write_text("Locked behavior\n", encoding="utf-8")
        self.store = Store(self.root, create=True)
        self.c = contract()
        self.store.create(self.c, "create:M1")
        self.seq = 0

    def tearDown(self):
        self.tmp.cleanup()

    def apply(self, operation, payload, **overrides):
        state = self.store.read("M1")
        self.seq += 1
        args = {"mission": "M1", "operation": operation, "payload": payload,
                "expected_revision": state["revision"], "event_key": "event:" + str(self.seq),
                "actor": state["owner"]["ref"], "owner_epoch": state["owner"]["epoch"]}
        args.update(overrides)
        return self.store.apply(**args)

    def open_execution(self, ref="E1"):
        if self.store.read("M1")["catalog"] is None:
            self.apply("catalog.record", catalog())
        return self.apply("execution.open", {"ref": ref, "native_ref": "native:" + ref,
                                               "request": {"model": "latest", "effort": "high"}})

    def receipt(self, ref="E1", status="COMPLETED", observed=None, **overrides):
        return self.apply("execution.receipt", {"ref": ref, "native_ref": "native:" + ref,
                       "status": status, "observed_at": utcnow(), "source_ref": "fixture:terminal",
                       "observed": observed or {"model": "candidate-v2", "effort": "high"}}, **overrides)

    def evidence(self, kind="test", outcome="pass"):
        path = "proof/%s-%s.log" % (kind, self.seq)
        (self.root / path).write_text(outcome, encoding="utf-8")
        return self.apply("evidence.record", {"criterion": "A1", "kind": kind, "outcome": outcome,
                          "path": path, "producer_ref": "fixture-evaluator"})

    def complete_evidence(self):
        self.evidence("test")
        self.evidence("behavioral")

    def usage_record(self):
        return {"host": "fixture-host", "provider": "fixture-provider", "account": "fixture-account",
                "session_ref": "S1", "request_id": "Q1", "response_id": "R1", "mode": "snapshot",
                "usage": {"input_tokens": 7, "output_tokens": 3, "cache_read_tokens": 100, "cache_write_tokens": 10}}


class TestMissionState(Fixture):
    def test_init_is_idempotent_and_does_not_write_host_settings(self):
        (self.root / "AGENTS.md").write_text("project-owned", encoding="utf-8")
        result = initialize(self.root, self.c, "create:M1")
        self.assertEqual(result["revision"], 0)
        self.assertEqual((self.root / "AGENTS.md").read_text(), "project-owned")
        self.assertFalse((self.root / ".claude/settings.json").exists())
        self.assertNotIn("Governor", (self.root / ".nnc-oser/BOOTSTRAP.md").read_text())

    def test_acceptance_denominator_cannot_be_edited_by_task_events(self):
        with self.assertRaises(OserError):
            self.apply("task.add", {"id": "tiny-task"})
        self.assertEqual(self.store.view("M1")["total"], 1)
        altered = copy.deepcopy(self.c)
        altered["goal"] = "silently changed"
        with self.assertRaises(OserError):
            self.store.create(altered, "create:M1-again")

    def test_bad_contract_does_not_create_a_mission(self):
        bad = copy.deepcopy(self.c)
        bad.update(id="bad", acceptance=[])
        with self.assertRaises(OserError):
            self.store.create(bad, "bad")
        self.assertEqual(len(self.store.list()), 1)

    def test_policy_boundaries_need_explicit_account_bindings(self):
        c = copy.deepcopy(self.c)
        c["id"] = "closed"
        c["policy"]["bindings"] = []
        result = self.store.create(c, "closed")
        self.assertEqual(admit(catalog(), result["policy"], {})["status"], "DENIED")

    def test_event_replay_is_idempotent_even_with_old_revision(self):
        p = {"summary": "checkpoint", "next_action": "continue"}
        a = self.apply("checkpoint.record", p, event_key="same")
        b = self.apply("checkpoint.record", p, event_key="same", expected_revision=0)
        self.assertEqual(a, b)
        self.assertEqual(self.store.read("M1")["revision"], 1)

    def test_idempotency_key_conflict_rejected(self):
        self.apply("checkpoint.record", {"summary": "one", "next_action": "next"}, event_key="same")
        with self.assertRaisesRegex(OserError, "different data"):
            self.apply("checkpoint.record", {"summary": "two", "next_action": "next"}, event_key="same")

    def test_revision_cas_and_failed_mutation_rollback(self):
        self.apply("checkpoint.record", {"summary": "one", "next_action": "next"})
        with self.assertRaises(OserError) as caught:
            self.apply("checkpoint.record", {"summary": "two", "next_action": "next"}, expected_revision=0)
        self.assertEqual(caught.exception.code, "REVISION_CONFLICT")
        with self.assertRaises(OserError):
            self.apply("execution.open", {"ref": "E1", "native_ref": "n"})
        self.assertEqual(self.store.read("M1")["revision"], 1)

    def test_concurrent_writers_have_one_cas_winner(self):
        gate = threading.Barrier(2)
        def write(index):
            gate.wait()
            try:
                Store(self.root).apply("M1", "checkpoint.record", {"summary": str(index), "next_action": "next"},
                                       0, "concurrent:" + str(index), "owner-a", 0)
                return "OK"
            except OserError as exc:
                return exc.code
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(write, [1, 2]))
        self.assertCountEqual(outcomes, ["OK", "REVISION_CONFLICT"])
        self.assertEqual(self.store.read("M1")["revision"], 1)

    def test_native_continuation_relation_is_not_a_closed_enum(self):
        self.open_execution()
        self.apply("execution.open", {"ref": "E2", "native_ref": "native:E2", "request": {},
                                      "relation": {"from": "E1", "native_relation": "future-host/resumed-fork"}})
        self.assertEqual(self.store.read("M1")["executions"]["E2"]["relation"]["native_relation"], "future-host/resumed-fork")

    def test_waiting_with_registered_child_is_legal(self):
        self.open_execution()
        state = self.apply("checkpoint.record", {"summary": "child runs", "next_action": "reconcile child",
                                                  "runtime_state": "WAITING", "waiting_for": ["E1"]})
        self.assertEqual(state["runtime_state"], "WAITING")
        self.assertIn("E1", state["checkpoints"][-1]["open_executions"])
        self.assertNotIn("STALLED", canonical(self.store.view("M1")))

    def test_waiting_requires_durable_dependency(self):
        with self.assertRaises(OserError):
            self.apply("checkpoint.record", {"summary": "waiting", "next_action": "next", "runtime_state": "WAITING"})

    def test_crash_reopen_and_late_receipt_after_transfer(self):
        self.open_execution()
        self.apply("checkpoint.record", {"summary": "work persists", "next_action": "reconcile E1"})
        self.apply("ownership.transfer", {"to": "owner-b", "reason": "replace interrupted owner"})
        self.store = Store(self.root)
        self.receipt(actor="native-observer", owner_epoch=0)
        self.assertIn("E1", self.store.view("M1")["unreconciled"])
        with self.assertRaises(OserError) as caught:
            self.apply("checkpoint.record", {"summary": "old", "next_action": "bad"}, actor="owner-a", owner_epoch=0)
        self.assertEqual(caught.exception.code, "OWNER_CONFLICT")

    def test_transfer_requires_checkpoint_and_increments_epoch(self):
        with self.assertRaises(OserError):
            self.apply("ownership.transfer", {"to": "owner-b", "reason": "test"})
        self.apply("checkpoint.record", {"summary": "safe", "next_action": "continue"})
        state = self.apply("ownership.transfer", {"to": "owner-b", "reason": "test"})
        self.assertEqual(state["owner"], {"ref": "owner-b", "epoch": 1})

    def test_native_receipt_does_not_mean_mission_complete(self):
        self.open_execution()
        self.receipt()
        self.assertEqual(self.store.read("M1")["status"], "OPEN")
        with self.assertRaises(OserError):
            self.apply("mission.complete", {})

    def test_receipt_identity_and_terminal_transition(self):
        self.open_execution()
        with self.assertRaises(OserError):
            self.apply("execution.receipt", {"ref": "E1", "native_ref": "wrong", "status": "COMPLETED"})
        self.receipt()
        with self.assertRaises(OserError):
            self.receipt(status="RUNNING")

    def test_observed_effort_mismatch_cannot_be_accepted(self):
        self.open_execution()
        self.receipt(observed={"model": "candidate-v2", "effort": "max"})
        self.complete_evidence()
        (self.root / "proof/reconcile.log").write_text("review", encoding="utf-8")
        self.apply("execution.reconcile", {"ref": "E1", "evidence_ref": "proof/reconcile.log"})
        with self.assertRaises(OserError):
            self.apply("mission.complete", {})
        self.assertEqual(self.store.view("M1")["policy_violations"], ["E1"])

    def test_unreconciled_result_blocks_completion(self):
        self.open_execution()
        self.receipt()
        self.complete_evidence()
        with self.assertRaises(OserError) as caught:
            self.apply("mission.complete", {})
        self.assertEqual(caught.exception.code, "UNRECONCILED_EXECUTION")
        (self.root / "proof/reconcile.log").write_text("receipt reviewed", encoding="utf-8")
        self.apply("execution.reconcile", {"ref": "E1", "evidence_ref": "proof/reconcile.log"})
        self.assertEqual(self.apply("mission.complete", {})["status"], "DONE")

    def test_test_pass_does_not_substitute_behavioral_evidence(self):
        self.evidence("test")
        self.assertEqual(self.store.view("M1")["verified_percent"], 0)
        self.evidence("behavioral", "fail")
        self.assertEqual(self.store.view("M1")["accepted"], 0)
        self.evidence("behavioral", "pass")
        self.assertEqual(self.store.view("M1")["accepted"], 1)

    def test_code_change_invalidates_evidence_and_reopens_done(self):
        self.complete_evidence()
        self.apply("mission.complete", {})
        (self.root / "src/app.txt").write_text("changed", encoding="utf-8")
        view = self.store.view("M1")
        self.assertEqual(view["status"], "REOPENED")
        self.assertEqual(view["criteria"][0]["evidence"]["test"], "STALE")

    def test_authority_and_artifact_drift(self):
        state = self.evidence("test")
        proof = state["evidence"][-1]["path"]
        (self.root / proof).write_text("altered", encoding="utf-8")
        self.assertEqual(self.store.view("M1")["criteria"][0]["evidence"]["test"], "STALE")
        (self.root / "docs/PRD.md").write_text("silently altered", encoding="utf-8")
        self.assertEqual(self.store.view("M1")["authority_status"], "DRIFT")

    def test_approval_tracking_never_grants_permission(self):
        self.apply("blocker.set", {"id": "approval", "summary": "review provider", "kind": "approval"})
        self.complete_evidence()
        with self.assertRaises(OserError):
            self.apply("mission.complete", {})
        self.apply("blocker.set", {"id": "approval", "summary": "resolved externally", "kind": "approval", "resolved": True})
        self.assertEqual(admit(catalog(provider="other"), self.store.read("M1")["policy"], {})["status"], "DENIED")

    def test_evidence_path_escape_and_symlink_are_rejected(self):
        for path in ("../outside", "/tmp/outside", "C:\\outside.txt", ".git/config"):
            with self.assertRaises(OserError):
                safe_path(self.root, path)
        outside = Path(self.tmp.name).parent / (self.root.name + "-outside")
        outside.write_text("outside", encoding="utf-8")
        try:
            link = self.root / "proof/link"
            try:
                link.symlink_to(outside)
            except OSError:
                return
            with self.assertRaises(OserError):
                safe_path(self.root, "proof/link")
        finally:
            outside.unlink()

    def test_legacy_migration_is_read_only_and_blocks_init(self):
        legacy = self.root / ".claude/oser"
        legacy.mkdir(parents=True)
        path = legacy / "project.json"
        path.write_text('{"schema":"nnc-oser/project@4"}', encoding="utf-8")
        before = path.read_bytes()
        self.assertEqual(migration_plan(self.root)["writes"], 0)
        with self.assertRaises(OserError):
            initialize(self.root, self.c)
        self.assertEqual(path.read_bytes(), before)

    def test_linked_worktree_uses_canonical_store(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid", "commit", "--allow-empty", "-qm", "base"], cwd=self.root, check=True, capture_output=True)
        worktree = self.root / "linked"
        subprocess.run(["git", "worktree", "add", "--detach", str(worktree)], cwd=self.root, check=True, capture_output=True)
        self.assertEqual(Store(worktree).path, self.store.path)


class TestCapabilityAdmission(Fixture):
    def test_runtime_default_and_xhigh_are_allowed_not_forced(self):
        policy = self.store.read("M1")["policy"]
        self.assertEqual(admit(catalog(), policy, {})["resolved"]["effort"], "high")
        self.assertEqual(admit(catalog(), policy, {"effort": "xhigh"})["status"], "ADMITTED")
        self.assertEqual(admit(catalog(), policy, {"effort": "low"})["status"], "ADMITTED")

    def test_default_cannot_bypass_effort_envelope(self):
        value = catalog()
        value["models"][1]["default_effort"] = "max"
        self.assertEqual(admit(value, self.c["policy"], {})["code"], "EFFORT_NOT_AUTHORIZED")
        value["models"][1]["default_effort"] = None
        self.assertEqual(admit(value, self.c["policy"], {})["code"], "DEFAULT_EFFORT_UNKNOWN")

    def test_unsupported_and_wrong_scope_are_not_silent(self):
        self.assertEqual(admit(catalog(), self.c["policy"], {"effort": "future"})["code"], "EFFORT_UNSUPPORTED")
        self.assertEqual(admit(catalog(), self.c["policy"], {"effort_scope": "global-parent"})["code"], "EFFORT_SCOPE_UNAVAILABLE")

    def test_documented_stale_future_unknown_catalogs_do_not_admit(self):
        for change in ({"evidence_state": "DOCUMENTED"}, {"observed_at": at(-7200)}, {"observed_at": at(3600)}):
            value = catalog()
            value.update(change)
            self.assertEqual(admit(value, self.c["policy"], {})["status"], "DENIED")
        self.assertEqual(admit(None, self.c["policy"], {})["status"], "DENIED")

    def test_latest_is_runtime_alias_not_name_guess(self):
        value = catalog()
        value["aliases"] = {}
        self.assertEqual(admit(value, self.c["policy"], {"model": "latest"})["code"], "MODEL_NOT_RESOLVED")
        self.assertEqual(admit(catalog(), self.c["policy"], {"model": "latest"})["resolved"]["model"], "candidate-v2")

    def test_catalog_refresh_does_not_mutate_existing_plan(self):
        self.open_execution()
        old = self.store.read("M1")["executions"]["E1"]["plan"]
        new = catalog()
        new["aliases"]["latest"] = "candidate-v1"
        self.apply("catalog.record", new)
        self.assertEqual(self.store.read("M1")["executions"]["E1"]["plan"], old)
        self.assertEqual(admit(new, self.c["policy"], {"model": "latest"})["resolved"]["model"], "candidate-v1")

    def test_other_provider_uses_same_kernel_but_needs_approval(self):
        new = catalog("other-host", "other-provider", "other-account")
        self.assertEqual(admit(new, self.c["policy"], {})["status"], "DENIED")
        policy = {"bindings": [binding("other-host", "other-provider", "other-account")], "max_active_executions": 2}
        self.assertEqual(admit(new, policy, {})["status"], "ADMITTED")

    def test_action_and_context_capacity_are_checked(self):
        self.assertEqual(admit(catalog(), self.c["policy"], {"action": "deploy"})["code"], "ACTION_NOT_AUTHORIZED")
        self.assertEqual(admit(catalog(), self.c["policy"], {"required_context_tokens": 999999})["code"], "CONTEXT_CAPACITY_UNKNOWN_OR_INSUFFICIENT")


class TestAccounting(Fixture):
    def test_A05_response_blocks_and_replay_count_once(self):
        usage = Usage(self.store)
        row = self.usage_record()
        usage.put("M1", row)
        row["apiBlockIndex"] = 1
        self.assertTrue(usage.put("M1", row)["duplicate"])
        self.assertTrue(Usage(Store(self.root)).put("M1", row)["duplicate"])
        report = usage.report("M1")
        self.assertEqual(report["unique_responses"], 1)
        self.assertEqual(report["total"]["input_tokens"], 7)
        self.assertIsNone(report["quota_percent"])

    def test_conflicting_snapshots_are_invalid_not_max_or_sum(self):
        usage = Usage(self.store)
        row = self.usage_record()
        usage.put("M1", row)
        row["usage"]["output_tokens"] += 1
        usage.put("M1", row)
        self.assertEqual(usage.report("M1")["validity"], "INVALID")
        self.assertIsNone(usage.report("M1")["total"])

    def test_missing_identity_is_unknown(self):
        row = self.usage_record()
        row.pop("response_id")
        row.pop("request_id")
        Usage(self.store).put("M1", row)
        self.assertEqual(Usage(self.store).report("M1")["validity"], "UNKNOWN")

    def test_rehome_does_not_duplicate_compute(self):
        other = copy.deepcopy(self.c)
        other["id"] = "M2"
        self.store.create(other, "create:M2")
        ledger = Usage(self.store)
        ledger.put("M1", self.usage_record())
        ledger.put("M2", self.usage_record())
        self.assertEqual(ledger.report("M1")["validity"], "INVALID")
        self.assertEqual(ledger.report("M2")["unique_responses"], 0)

    def test_usage_does_not_add_thinking_twice(self):
        row = self.usage_record()
        row["usage"]["thinking_tokens"] = 2
        ledger = Usage(self.store)
        ledger.put("M1", row)
        self.assertEqual(ledger.report("M1")["total"]["output_tokens"], 3)

    def test_unsupported_delta_not_treated_as_snapshot(self):
        row = self.usage_record()
        row["mode"] = "delta"
        ledger = Usage(self.store)
        ledger.put("M1", row)
        self.assertEqual(ledger.report("M1")["validity"], "INVALID")

    def test_adapter_preserves_response_identity_without_block_id(self):
        row = {"type": "assistant", "sessionId": "S", "requestId": "Q", "apiBlockIndex": 0,
               "message": {"id": "R", "model": "candidate", "usage": {"input_tokens": 1, "output_tokens": 2, "cache_read_input_tokens": 4, "cache_creation_input_tokens": 5}}}
        first = claude_usage(row, "fixture-provider", "account")
        row["apiBlockIndex"] = 1
        self.assertEqual(first, claude_usage(row, "fixture-provider", "account"))
        self.assertIsNone(claude_usage({"type": "user"}, "p", "a"))


class TestObserverAdapters(Fixture):
    def sample(self):
        return {"host": "fixture-host", "provider": "fixture-provider", "account": "A", "kind": "quota", "bucket": "window",
                "source_ref": "fixture:quota", "observed_at": at(-5), "ttl_seconds": 60, "used_percent": 20,
                "resets_at": datetime.now(timezone.utc).timestamp() + 3600}

    def test_A10_reading_old_payload_does_not_refresh_source_time(self):
        health = Health(self.store)
        s = self.sample()
        s["observed_at"] = at(-120)
        health.put(s)
        self.assertEqual(health.read()[0]["freshness"], "STALE")
        self.assertFalse(health.put(s)["changed"])
        self.assertEqual(health.read()[0]["freshness"], "STALE")

    def test_unknown_source_age_and_missing_fields_stay_unknown(self):
        s = self.sample()
        s["observed_at"] = None
        Health(self.store).put(s)
        self.assertEqual(Health(self.store).read()[0]["freshness"], "UNKNOWN")
        self.assertEqual(claude_health({}, "p", "a", None, "fixture"), [])

    def test_account_buckets_are_not_pooled(self):
        health = Health(self.store)
        a = self.sample()
        b = dict(a, account="B", used_percent=90)
        health.put(a)
        health.put(b)
        self.assertEqual(sorted(s["used_percent"] for s in health.read()), [20, 90])

    def test_invalid_percent_nan_and_future_timestamp_rejected(self):
        for change in ({"used_percent": 101}, {"used_percent": float("nan")}, {"observed_at": at(600)}):
            s = self.sample()
            s.update(change)
            with self.assertRaises(OserError):
                Health(self.store).put(s)

    def test_older_sample_cannot_replace_newer(self):
        health = Health(self.store)
        s = self.sample()
        health.put(s)
        old = dict(s, observed_at=at(-100), used_percent=5)
        self.assertEqual(health.put(old)["reason"], "OLDER_SAMPLE")
        self.assertEqual(health.read()[0]["used_percent"], 20)

    def test_reset_passed_does_not_invent_zero_usage(self):
        s = self.sample()
        s["resets_at"] = datetime.now(timezone.utc).timestamp() - 1
        health = Health(self.store)
        health.put(s)
        self.assertEqual(health.read()[0]["freshness"], "STALE")
        self.assertEqual(health.read()[0]["used_percent"], 20)

    def test_claude_statusline_is_not_full_model_catalog(self):
        payload = {"model": {"id": "observed-model"}, "effort": {"level": "high"}, "session_id": "S"}
        c = claude_current_catalog(payload, "p", "a", at(-1), "fixture")
        self.assertEqual(c["coverage"], "CURRENT_MODEL_ONLY")
        self.assertEqual(c["models"][0]["effort_scopes"], ["current"])
        self.assertEqual(c["aliases"], {})

    def test_codex_model_catalog_retains_native_effort_names(self):
        wire = {"data": [{"id": "id1", "model": "model1", "isDefault": True, "defaultReasoningEffort": "native-effort",
                         "supportedReasoningEfforts": [{"reasoningEffort": "native-effort"}]}], "nextCursor": None}
        c = codex_catalog(wire, "provider", "account", at(-1), "fixture")
        self.assertEqual(c["models"][0]["efforts"], ["native-effort"])
        self.assertEqual(c["evidence_state"], "DOCUMENTED")
        self.assertNotIn("latest", c["aliases"])

    def test_codex_multi_bucket_does_not_double_count_single_view(self):
        bucket = {"limitId": "one", "primary": {"usedPercent": 25, "resetsAt": 9999999999, "windowDurationMins": 300}}
        wire = {"rateLimits": bucket, "rateLimitsByLimitId": {"one": bucket, "two": dict(bucket, limitId="two")}}
        result = codex_health(wire, "p", "a", at(-1), "fixture")
        self.assertEqual(len(result), 2)
        self.assertEqual({s["bucket"] for s in result}, {"one/primary", "two/primary"})

    def test_session_end_hook_is_observation_not_a_guard(self):
        hint = claude_lifecycle({"hook_event_name": "SessionEnd", "session_id": "S"})
        self.assertFalse(hint["can_block_session_end"])
        self.assertFalse(hint["completion_proven"])
        self.assertEqual(hint["recovery"], "MANUAL_RESUME_REQUIRED")

    def test_A12_observer_and_view_do_not_start_subprocess_or_model(self):
        s = self.sample()
        with patch("subprocess.Popen", side_effect=AssertionError("observer started a process")):
            health = Health(self.store)
            self.assertEqual(health.put(s)["model_calls"], 0)
            text = render(self.store.view("M1"), health.read())
            self.assertIn("Frontier", text)
            self.assertIn("acceptance, NOT time", text)


class TestMcpAndCli(Fixture):
    def rpc(self, requests):
        source = io.StringIO("\n".join(json.dumps(r) for r in requests) + "\n")
        target = io.StringIO()
        serve(self.root, source, target)
        return [json.loads(line) for line in target.getvalue().splitlines()]

    def test_mcp_requires_handshake_and_has_no_sampling_or_shell(self):
        results = self.rpc([{"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                            {"jsonrpc": "2.0", "id": 2, "method": "initialize", "params": {"protocolVersion": "2025-11-25"}},
                            {"jsonrpc": "2.0", "method": "notifications/initialized"},
                            {"jsonrpc": "2.0", "id": 3, "method": "tools/list"}])
        self.assertIn("error", results[0])
        self.assertEqual(results[1]["result"]["capabilities"], {"tools": {}})
        self.assertEqual(len(results[2]["result"]["tools"]), 6)
        self.assertFalse(any("shell" == t["name"] for t in results[2]["result"]["tools"]))

    def test_mcp_structured_mutation_and_compact_response(self):
        result = invoke(self.root, "oser_mission_apply", {"mission": "M1", "operation": "checkpoint.record",
                         "payload": {"summary": "safe", "next_action": "next"}, "expected_revision": 0,
                         "event_key": "rpc", "actor": "owner-a", "owner_epoch": 0})
        self.assertEqual(result["revision"], 1)
        self.assertNotIn("executions", result)

    def test_mcp_cannot_choose_another_project_root(self):
        with self.assertRaises(OserError):
            invoke(self.root, "oser_mission_read", {"mission": "M1", "project": "/"})

    def test_cli_status_and_usage_without_global_configuration(self):
        command = [sys.executable, str(HOME / "oser.py"), "status", "--project", str(self.root), "--mission", "M1", "--json"]
        p = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)["total"], 1)
        p = subprocess.run([sys.executable, str(HOME / "oser.py"), "version"], capture_output=True, text=True)
        self.assertEqual(p.stdout.strip(), "5.1.0-alpha.1")

    def test_opt_in_probe_reads_catalog_not_model_turns(self):
        # sys.executable app-server runs this deterministic fake, on all OSes.
        script = '''import json,sys
for line in sys.stdin:
 r=json.loads(line)
 m=r['method']
 with open('probe-methods.txt','a') as f: f.write(m+'\\n')
 if 'id' not in r: continue
 if m=='initialize': value={}
 elif m=='model/list': value={'data':[{'id':'only','model':'only','isDefault':True,'defaultReasoningEffort':'low','supportedReasoningEfforts':[{'reasoningEffort':'low'}]}],'nextCursor':None}
 elif m=='account/rateLimits/read': value={'rateLimits':{'limitId':'fixture','primary':{'usedPercent':10,'resetsAt':9999999999}}}
 else: raise RuntimeError('unexpected method '+m)
 print(json.dumps({'id':r['id'],'result':value}),flush=True)
'''
        (self.root / "app-server").write_text(script, encoding="utf-8")
        result = codex_probe(self.root, "p", "a", timeout=5, executable=sys.executable)
        methods = (self.root / "probe-methods.txt").read_text().splitlines()
        self.assertEqual(methods, ["initialize", "initialized", "model/list", "account/rateLimits/read"])
        self.assertEqual(result["model_calls"], 0)
        self.assertEqual(result["catalog"]["evidence_state"], "PROBED")
        self.assertEqual(len(result["health"]), 1)


if __name__ == "__main__":
    unittest.main()
