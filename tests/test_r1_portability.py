"""Portable filesystem and initialization boundaries, no live host dependency."""
import subprocess
import unittest
from pathlib import Path

from test_mission_r1 import Fixture
from oser_mission.cli import initialize, migration_plan
from oser_mission.common import OserError, source_fingerprint


class TestPortability(Fixture):
    def test_resolved_and_original_temp_roots_have_identical_fingerprint(self):
        # On Windows the temporary path may have RUNNER~1 versus runneradmin.
        self.assertEqual(source_fingerprint(self.root, ["."]), source_fingerprint(self.root.resolve(), ["."]))

    def test_linked_worktree_cannot_bypass_active_legacy_manifest(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid", "commit", "--allow-empty", "-qm", "base"], cwd=self.root, check=True, capture_output=True)
        linked = self.root / "linked"
        subprocess.run(["git", "worktree", "add", "--detach", str(linked)], cwd=self.root, check=True, capture_output=True)
        legacy = self.root / ".claude/oser"
        legacy.mkdir(parents=True)
        (legacy / "project.json").write_text('{"schema":"nnc-oser/project@4"}', encoding="utf-8")
        self.assertTrue(migration_plan(linked)["legacy_found"])
        with self.assertRaises(OserError) as caught:
            initialize(linked, self.c)
        self.assertEqual(caught.exception.code, "LEGACY_CONFLICT")

    def test_directory_symlink_source_does_not_expand_a_foreign_tree(self):
        target = self.root / "proof"
        (target / "ignored.txt").write_text("outside source scope", encoding="utf-8")
        link = self.root / "src/link"
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError:
            self.skipTest("host does not grant symlink creation")
        with self.assertRaises(OserError):
            source_fingerprint(self.root, ["src"])


if __name__ == "__main__":
    unittest.main()
