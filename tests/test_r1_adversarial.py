"""Adversarial regression beyond the happy-path Mission fixtures."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_mission_r1 import Fixture, at, catalog
from oser_mission.common import OserError, safe_path, source_fingerprint, utcnow
from oser_mission.health import Health
from oser_mission.mcp import invoke
from oser_mission.state import Store
from oser_mission.usage import Usage


class TestR1Adversarial(Fixture):
    def test_unknown_usage_does_not_poison_other_mission(self):
        second = copy.deepcopy(self.c)
        second["id"] = "M2"
        self.store.create(second, "create:M2")
        ledger = Usage(self.store)
        unknown = self.usage_record()
        unknown.pop("response_id")
        unknown.pop("request_id")
        ledger.put("M1", unknown)
        ledger.put("M2", self.usage_record())
        self.assertEqual(ledger.report("M1")["validity"], "UNKNOWN")
        self.assertEqual(ledger.report("M2")["validity"], "VALID")

    def test_added_request_metadata_does_not_double_count_response(self):
        row = self.usage_record()
        request = row.pop("request_id")
        ledger = Usage(self.store)
        ledger.put("M1", row)
        row["request_id"] = request
        self.assertTrue(ledger.put("M1", row)["duplicate"])
        self.assertEqual(ledger.report("M1")["unique_responses"], 1)

    def test_reported_running_is_not_observed_health(self):
        self.apply("checkpoint.record", {"summary": "I claim running", "next_action": "next", "runtime_state": "RUNNING"})
        view = self.store.view("M1")
        self.assertEqual(view["reported_runtime_state"], "RUNNING")
        self.assertEqual(view["runtime_state"], "UNKNOWN")

    def test_fresh_receipt_versus_stale_execution_observation(self):
        self.open_execution()
        self.receipt(status="RUNNING")
        self.assertEqual(self.store.view("M1")["runtime_state"], "RUNNING")
        with patch("oser_mission.state.utcnow", return_value=at(1000)):
            self.assertEqual(self.store.view("M1")["runtime_state"], "UNKNOWN")

    def test_future_receipt_is_rejected(self):
        self.open_execution()
        with self.assertRaises(OserError):
            self.apply("execution.receipt", {"ref": "E1", "native_ref": "native:E1", "source_ref": "fixture",
                         "observed_at": at(3600), "status": "COMPLETED"})

    def test_duplicate_receipt_does_not_reopen_reconciliation(self):
        self.open_execution()
        payload = {"ref": "E1", "native_ref": "native:E1", "source_ref": "fixture", "observed_at": utcnow(),
                   "status": "COMPLETED", "observed": {"model": "candidate-v2", "effort": "high"}}
        self.apply("execution.receipt", payload)
        (self.root / "proof/reconcile.txt").write_text("checked", encoding="utf-8")
        self.apply("execution.reconcile", {"ref": "E1", "evidence_ref": "proof/reconcile.txt"})
        self.apply("execution.receipt", payload)
        self.assertTrue(self.store.read("M1")["executions"]["E1"]["reconciled"])

    def test_contradictory_same_time_receipt_is_rejected(self):
        self.open_execution()
        payload = {"ref": "E1", "native_ref": "native:E1", "source_ref": "fixture", "observed_at": utcnow(),
                   "status": "RUNNING", "observed": {"model": "candidate-v2", "effort": "high"}}
        self.apply("execution.receipt", payload)
        payload["observed"]["effort"] = "max"
        with self.assertRaises(OserError) as caught:
            self.apply("execution.receipt", payload)
        self.assertEqual(caught.exception.code, "RECEIPT_CONFLICT")

    def test_transfer_cannot_reuse_prior_owners_checkpoint(self):
        self.apply("checkpoint.record", {"summary": "safe", "next_action": "continue"})
        self.apply("ownership.transfer", {"to": "owner-b", "reason": "first"})
        with self.assertRaises(OserError):
            self.apply("ownership.transfer", {"to": "owner-c", "reason": "second without checkpoint"})

    def test_missing_source_reopens_evidence_without_crashing_view(self):
        self.complete_evidence()
        self.apply("mission.complete", {})
        (self.root / "src/app.txt").unlink()
        view = self.store.view("M1")
        self.assertEqual(view["status"], "REOPENED")
        self.assertEqual(view["source_status"], "UNAVAILABLE")
        with self.assertRaises(OserError):
            self.apply("mission.complete", {})

    def test_blocker_reopens_completed_mission(self):
        self.complete_evidence()
        self.apply("mission.complete", {})
        self.apply("blocker.set", {"id": "regression", "summary": "new defect"})
        self.assertEqual(self.store.view("M1")["status"], "OPEN")

    def test_windows_drive_relative_path_is_not_portable_relative_path(self):
        with self.assertRaises(OserError):
            safe_path(self.root, "C:secret.txt")

    def test_source_walk_prunes_internal_state(self):
        # No source output depends on the changing sqlite journal contents.
        before = source_fingerprint(self.root, ["."])
        self.apply("checkpoint.record", {"summary": "new event", "next_action": "continue"})
        after = source_fingerprint(self.root, ["."])
        self.assertEqual(before, after)

    def test_enforced_count_rejects_extra_execution(self):
        self.open_execution("E1")
        for number in range(2, 5):
            self.open_execution("E" + str(number))
        with self.assertRaises(OserError) as caught:
            self.open_execution("E5")
        self.assertEqual(caught.exception.code, "CONCURRENCY_LIMIT")

    def test_changed_evidence_content_is_not_a_cryptographic_attestation(self):
        self.evidence("test")
        evidence = self.store.read("M1")["evidence"][-1]
        self.assertEqual(evidence["trust"], "RECORDED_ATTESTATION")
        self.assertNotIn("verified_by_model", evidence)


if __name__ == "__main__":
    unittest.main()
