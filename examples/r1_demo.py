#!/usr/bin/env python3
"""Offline disposable Mission walkthrough; never calls an inference model."""
import subprocess
import sys
import tempfile
from pathlib import Path

HOME = Path(__file__).resolve().parents[1] / "plugins/nnc/oser"
sys.path.insert(0, str(HOME))
from oser_mission.cli import initialize
from oser_mission.common import OserError
from oser_mission.health import Health, render
from oser_mission.state import Store


def main():
    with tempfile.TemporaryDirectory(prefix="nnc-oser-demo-") as tmp:
        root = Path(tmp)
        for folder in ("docs", "src", "evidence"):
            (root / folder).mkdir()
        (root / "docs/PRD.md").write_text("Normalize runs of whitespace to one space; remove leading/trailing whitespace. Preserve non-whitespace characters.\n", encoding="utf-8")
        (root / "src/app.py").write_text("def normalize(value):\n    return ' '.join(value.split())\n", encoding="utf-8")
        (root / "src/check.py").write_text("from app import normalize\ncases = [('', ''), ('  a   b ', 'a b'), ('a\\nb', 'a b'), ('A-1', 'A-1')]\nfor value, expected in cases:\n    actual = normalize(value)\n    assert actual == expected, (value, actual, expected)\nprint('PASS: 4 approved behavior examples')\n", encoding="utf-8")
        contract = {"id": "DEMO", "goal": "Verify the locked whitespace behavior", "owner": "demo-host",
                    "baseline": {"id": "DEMO-B1", "authority": [{"path": "docs/PRD.md"}]}, "sources": ["src"],
                    "acceptance": [{"id": "AC1", "description": "Approved behavior and test execution", "requires": ["test", "behavioral"]}],
                    "policy": {"bindings": [], "max_active_executions": 1}}
        initialize(root, contract)
        store = Store(root)

        def apply(operation, payload, event):
            state = store.read("DEMO")
            return store.apply("DEMO", operation, payload, state["revision"], event, "demo-host", 0)

        print("BEFORE\n" + render(store.view("DEMO"), Health(store).read()))
        result = subprocess.run([sys.executable, str(root / "src/check.py")], cwd=root, capture_output=True, text=True)
        (root / "evidence/check.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError("Demo behavioral check failed: " + result.stderr)
        apply("evidence.record", {"criterion": "AC1", "kind": "test", "outcome": "pass", "path": "evidence/check.log", "producer_ref": "demo:python-check"}, "demo:test")
        try:
            apply("mission.complete", {}, "demo:too-early")
        except OserError as exc:
            print("\nExpected early rejection:", exc.code)
        else:
            raise AssertionError("Incomplete acceptance was accepted")
        apply("evidence.record", {"criterion": "AC1", "kind": "behavioral", "outcome": "pass", "path": "evidence/check.log", "producer_ref": "demo:approved-behavior-cases"}, "demo:behavior")
        apply("checkpoint.record", {"summary": "Behavior examples verified", "next_action": "No remaining acceptance; close Mission"}, "demo:checkpoint")
        apply("mission.complete", {}, "demo:done")
        print("\nAFTER\n" + render(store.view("DEMO"), Health(store).read()))
        print("\nNo inference, paid quota, user settings or deployment was used. Demo directory is removed on exit.")


if __name__ == "__main__":
    main()
