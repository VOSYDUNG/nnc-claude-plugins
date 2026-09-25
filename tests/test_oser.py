# -*- coding: utf-8 -*-
"""End-to-end tests for NNC OSER. Run from the repo root:  python -m unittest discover -s tests -v

Every test builds disposable projects in a temp dir and points OSER at a temp ~/.claude, so nothing on the
machine (real transcripts, installed plugins, user settings) leaks in.
"""
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
OSER_HOME = os.path.join(os.path.dirname(HERE), "plugins", "nnc", "oser")
OSER = os.path.join(OSER_HOME, "oser.py")
FIX = os.path.join(HERE, "fixtures", "v1")
sys.path.insert(0, OSER_HOME)

from oser_core import doctor, engine  # noqa: E402
from oser_core.util import transcript_slug  # noqa: E402


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def r(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def g(cwd, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True,
                   capture_output=True)


def snapshot(root):
    out = {}
    for d, dirs, files in os.walk(root):
        if ".git" in dirs:
            dirs.remove(".git")
        for f in files:
            p = os.path.join(d, f)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, root).replace("\\", "/")] = hashlib.sha256(fh.read()).hexdigest()
    return out


def run_cli(*args, env=None):
    e = dict(os.environ)
    e.update(env or {})
    p = subprocess.run([sys.executable, OSER, *args], capture_output=True, text=True, encoding="utf-8", env=e)
    return p.returncode, p.stdout + p.stderr


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="oser-test-")
        self.home = os.path.join(self.tmp, "claude-home")
        os.makedirs(self.home)
        self._env = {k: os.environ.get(k) for k in ("NNC_OSER_CLAUDE_HOME", "NNC_OSER_AUTHORITY_PATH", "NNC_OSER_HOME")}
        os.environ["NNC_OSER_CLAUDE_HOME"] = self.home
        os.environ.pop("NNC_OSER_AUTHORITY_PATH", None)
        os.environ["NNC_OSER_HOME"] = OSER_HOME
        self.auth = os.path.join(self.tmp, "strategy")
        os.makedirs(self.auth)
        g(self.auth, "init", "-q", "-b", "main")
        w(os.path.join(self.auth, "docs", "HANDOFF.md"), "# handoff\n")
        g(self.auth, "add", "-A")
        g(self.auth, "commit", "-q", "-m", "handoff")
        self.base = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=self.auth, capture_output=True,
                                   text=True).stdout.strip()
        self.proj = os.path.join(self.tmp, "proj")
        os.makedirs(self.proj)
        g(self.proj, "init", "-q", "-b", "main")

    def tearDown(self):
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(self.tmp, ignore_errors=True)

    def P(self, *parts):
        return os.path.join(self.proj, *parts)

    def transcript(self, model, sidechain=False, ts="2026-09-25T05:00:00Z"):
        d = os.path.join(self.home, "projects", transcript_slug(self.proj))
        os.makedirs(d, exist_ok=True)
        with io.open(os.path.join(d, "s.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"type": "assistant", "isSidechain": sidechain, "timestamp": ts, "sessionId": "abcd1234",
                                "message": {"model": model, "usage": {"input_tokens": 10, "output_tokens": 5}}}) + "\n")

    def manifest(self, **over):
        m = {
            "schema": "nnc-oser/project@2",
            "project": {"name": "proj", "language": "vi"},
            "phase": {"id": "pre-build-setup", "label": "PRE-BUILD SETUP", "since": "2026-09-25", "summary": ["x"]},
            "mode": "setup",
            "authority": {"repo": "o/strategy", "ref": "main", "baseline": self.base, "entry": "docs/HANDOFF.md",
                          "local_path_hints": ["../strategy"]},
            "models": {"root": "inherit"},
            "capabilities": {"audit": {"enabled": False}},
            "workspace": {"state_file": "workspace/TRANG-THAI.md", "dir": "workspace", "current": ["TRANG-THAI.md"]},
            "control_plane": {"current": ["CLAUDE.md", "workspace/TRANG-THAI.md"], "inactivate": [".claude/CO-CAU-NHAN-SU.md"],
                              "historical": ["workspace/lich-su/"], "historical_banner": "LỊCH SỬ",
                              "stale_markers": [{"pattern": "BUILD LOT-0", "why": "old phase"}]},
            "compat": {"wrappers": {"cong-cu/do-quota.py": "quota", "cong-cu/doi-bac.py": "doi-bac"}},
            "migrate": {"moves": [{"from": "workspace/old-plan.md", "to": "workspace/lich-su/old-plan.md"}]},
        }
        m.update(over)
        w(self.P(".claude", "oser", "project.json"), json.dumps(m, ensure_ascii=False, indent=2) + "\n")
        return m

    def v1_project(self):
        w(self.P(".claude", "settings.json"), '{\n  "model": "claude-opus-5"\n}\n')
        w(self.P(".claude", "agents", "tho-dung.md"),
          "---\nname: tho-dung\nmodel: claude-sonnet-5\ndescription: Kỹ sư (Opus 5) dựng code\n---\nbody\n")
        w(self.P(".claude", "BAC-DANG-DUNG.md"),
          "# Bậc model đang dùng: **opus**\n\n> Sinh bởi `python cong-cu/doi-bac.py opus` lúc 09/09/2026.\n")
        w(self.P(".claude", "CO-CAU-NHAN-SU.md"), "# Cơ cấu bậc 1\n")
        os.makedirs(self.P("cong-cu"))
        shutil.copy(os.path.join(FIX, "doi-bac.py"), self.P("cong-cu", "doi-bac.py"))
        shutil.copy(os.path.join(FIX, "do-quota.py"), self.P("cong-cu", "do-quota.py"))
        w(self.P("CLAUDE.md"), "# Proj\n\nCURRENT PHASE: BUILD LOT-0\n\ncustom rule XYZ — project-owned\n")
        w(self.P("workspace", "TRANG-THAI.md"), "# Trạng thái\n\n**PRE-BUILD SETUP**\n")
        w(self.P("workspace", "old-plan.md"), "> LỊCH SỬ\nold plan\n")
        g(self.proj, "add", "-A")
        g(self.proj, "commit", "-q", "-m", "v1")


class TestA_CleanInstall(Base):
    def test_install_setup_mode_is_clean(self):
        code, out = run_cli("install", "--project", self.proj, "--name", "demo", "--authority-repo", "o/strategy",
                            "--authority-entry", "docs/HANDOFF.md", "--authority-hint", "../strategy",
                            "--baseline", self.base, "--phase-id", "pre-build-setup", "--phase-label", "PRE-BUILD SETUP",
                            env={"NNC_OSER_CLAUDE_HOME": self.home})
        self.assertEqual(code, 0, out)
        rep = doctor.run(self.proj)
        bad = [f for f in rep.findings if f["severity"] != "info"]
        self.assertEqual(bad, [], bad)
        self.assertFalse(os.path.isdir(self.P(".claude", "agents")), "no agent may be activated by install")
        s = json.loads(r(self.P(".claude", "settings.json")))
        self.assertNotIn("model", s)
        self.assertEqual(s["permissions"]["deny"], ["Agent", "Task", "Workflow"])
        caps = json.loads(r(self.P(".claude", "oser", "project.json")))["capabilities"]
        self.assertFalse(caps["audit"]["enabled"])
        self.assertIn("audit=disabled", r(self.P("CLAUDE.md")))
        lock = json.loads(r(self.P(".claude", "oser", "lock.json")))
        self.assertEqual(lock["oser_version"], "2.0.0")
        self.assertEqual(lock["mode"], "setup")

    def test_install_refuses_existing_manifest(self):
        self.manifest()
        with self.assertRaises(engine.Blocked):
            engine.install(self.proj, "x", "o/s", "docs/HANDOFF.md")

    def test_contract_only_mode_rejected(self):
        self.manifest(mode="build")
        rep = doctor.run(self.proj)
        self.assertTrue(any("contract-only" in f["message"] for f in rep.findings))
        with self.assertRaises(engine.Blocked):
            engine.update(self.proj)


class TestB_Migration(Base):
    def test_migrate_v1_preserves_project_owned_and_records_provenance(self):
        self.v1_project()
        self.transcript("claude-opus-5-5")
        self.manifest()
        agent_before = r(self.P(".claude", "agents", "tho-dung.md"))
        state_before = r(self.P("workspace", "TRANG-THAI.md"))
        engine.migrate(self.proj)
        claude = r(self.P("CLAUDE.md"))
        self.assertIn("custom rule XYZ — project-owned", claude)
        self.assertIn("NNC-OSER:BEGIN block=status", claude)
        self.assertEqual(r(self.P("workspace", "TRANG-THAI.md")), state_before)
        self.assertEqual(r(self.P(".claude", "oser", "inactive", "agents", "tho-dung.md")), agent_before)
        self.assertFalse(os.path.exists(self.P(".claude", "agents", "tho-dung.md")))
        self.assertTrue(os.path.exists(self.P(".claude", "oser", "inactive", "CO-CAU-NHAN-SU.md")))
        self.assertFalse(os.path.exists(self.P(".claude", "BAC-DANG-DUNG.md")))
        self.assertTrue(os.path.exists(self.P("workspace", "lich-su", "old-plan.md")))
        s = json.loads(r(self.P(".claude", "settings.json")))
        self.assertNotIn("model", s)
        for tool in ("do-quota.py", "doi-bac.py"):
            self.assertIn("NNC-OSER:GENERATED", r(self.P("cong-cu", tool)))
        lock = json.loads(r(self.P(".claude", "oser", "lock.json")))
        actions = {a["action"] for a in lock["migrations"][0]["actions"]}
        self.assertTrue({"retire", "wrap", "unpin-root-model", "inactivate", "move"} <= actions, actions)
        self.assertIn(".claude/BAC-DANG-DUNG.md", lock["retired"])

    def test_modified_legacy_tool_blocks_without_writing(self):
        self.v1_project()
        with io.open(self.P("cong-cu", "doi-bac.py"), "a", encoding="utf-8") as f:
            f.write("\n# local tweak\n")
        self.manifest()
        before = snapshot(self.proj)
        with self.assertRaises(engine.Blocked):
            engine.migrate(self.proj)
        self.assertEqual(snapshot(self.proj), before)

    def test_update_refuses_legacy_layout(self):
        self.v1_project()
        self.manifest()
        with self.assertRaises(engine.Blocked):
            engine.update(self.proj)


class TestC_DoctorBeforeAfter(Base):
    def test_doctor_catches_pilot_drift_classes_then_clears(self):
        self.v1_project()
        self.transcript("claude-opus-5-5")
        self.transcript("claude-fable-5-1", sidechain=True)
        w(self.P("workspace", "stray.md"), "live?\n")
        with io.open(self.P("CLAUDE.md"), "a", encoding="utf-8") as f:
            f.write("authority on branch `codex/dead-branch`\n")
        g(self.proj, "add", "-A")
        g(self.proj, "commit", "-q", "-m", "drift")
        self.manifest()
        before = doctor.run(self.proj)
        ids = {f["id"] for f in before.findings if f["severity"] != "info"}
        for expected in ("OSR-002", "OSR-011", "OSR-020", "OSR-021", "OSR-030", "OSR-031", "OSR-040", "OSR-050", "OSR-060"):
            self.assertIn(expected, ids, expected)
        self.assertIn("claude-opus-5-5", before.facts["root_model"]["observed"])
        # project-owned cleanup (what a human/ROOT does), then migrate
        w(self.P("CLAUDE.md"), "# Proj\n\ncustom rule XYZ — project-owned\n")
        os.remove(self.P("workspace", "stray.md"))
        engine.migrate(self.proj)
        after = doctor.run(self.proj)
        c = after.counts()
        self.assertEqual((c["critical"], c["warning"]), (0, 0), [f for f in after.findings if f["severity"] != "info"])

    def test_oversized_state_file_warns(self):
        self.manifest()
        w(self.P("workspace", "TRANG-THAI.md"), "**PRE-BUILD SETUP**\n" + "x" * (16 * 1024))
        self.assertTrue(any(f["id"] == "OSR-061" for f in doctor.run(self.proj).findings))

    def test_firebase_forbidden_default_is_critical(self):
        self.manifest(checks={"firebase": {"data_project": "kho-data", "forbidden_defaults": ["driver"],
                                           "hosting_sites": {"kho": "driver"}, "protected_sites": ["hifi"]}})
        w(self.P(".firebaserc"), '{"projects": {"default": "driver"}}\n')
        w(self.P("firebase.json"), '{"firestore": {"rules": "r"}, "hosting": {"site": "kho"}}\n')
        crit = [f for f in doctor.run(self.proj).findings if f["id"] == "OSR-080" and f["severity"] == "critical"]
        self.assertEqual(len(crit), 1)
        w(self.P(".firebaserc"), '{"projects": {"kho-data": "kho-data", "review-host": "driver"}}\n')
        sev = [f["severity"] for f in doctor.run(self.proj).findings if f["id"] == "OSR-080"]
        self.assertEqual(sev, ["info"])
        w(self.P("firebase.json"), '{"hosting": {"site": "hifi"}}\n')
        self.assertTrue(any(f["id"] == "OSR-080" and f["severity"] == "critical" for f in doctor.run(self.proj).findings))


class TestD_Idempotence(Base):
    def test_second_migrate_and_update_change_nothing(self):
        self.v1_project()
        self.manifest()
        engine.migrate(self.proj)
        first = snapshot(self.proj)
        p2 = engine.migrate(self.proj)
        p3 = engine.update(self.proj)
        self.assertEqual(p2.actions, [])
        self.assertEqual(p3.actions, [])
        self.assertEqual(snapshot(self.proj), first)

    def test_hand_edited_generated_file_is_not_overwritten(self):
        self.v1_project()
        self.manifest()
        engine.migrate(self.proj)
        cp = self.P(".claude", "oser", "CONTROL-PLANE.md")
        with io.open(cp, "a", encoding="utf-8") as f:
            f.write("hand edit\n")
        # change the manifest so update wants to re-render
        m = json.loads(r(self.P(".claude", "oser", "project.json")))
        m["phase"]["summary"] = ["changed"]
        w(self.P(".claude", "oser", "project.json"), json.dumps(m, ensure_ascii=False, indent=2) + "\n")
        plan = engine.update(self.proj)
        self.assertIn("hand edit", r(cp))
        self.assertTrue(any("SKIPPED hand-edited" in n for n in plan.notes))
        self.assertTrue(any(f["id"] == "OSR-070" for f in doctor.run(self.proj).findings))

    def test_override_is_respected(self):
        self.v1_project()
        self.manifest(overrides=["cong-cu/do-quota.py"])
        engine.migrate(self.proj)
        self.assertNotIn("NNC-OSER:GENERATED", r(self.P("cong-cu", "do-quota.py")))


class TestE_Wrappers(Base):
    def test_wrappers_delegate_to_canonical_oser(self):
        self.v1_project()
        self.transcript("claude-opus-5-5")
        self.manifest()
        engine.migrate(self.proj)
        env = dict(os.environ)
        p = subprocess.run([sys.executable, self.P("cong-cu", "doi-bac.py"), "opus"], capture_output=True, text=True,
                           encoding="utf-8", env=env)
        self.assertEqual(p.returncode, 2)
        self.assertIn("RETIRED", p.stdout)
        p = subprocess.run([sys.executable, self.P("cong-cu", "doi-bac.py")], capture_output=True, text=True,
                           encoding="utf-8", env=env)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("OBSERVED=claude-opus-5-5", p.stdout)
        p = subprocess.run([sys.executable, self.P("cong-cu", "do-quota.py")], capture_output=True, text=True,
                           encoding="utf-8", env=env)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("claude-opus-5-5", p.stdout)


if __name__ == "__main__":
    unittest.main()
