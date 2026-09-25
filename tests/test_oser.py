# -*- coding: utf-8 -*-
"""End-to-end tests for NNC OSER. Run from the repo root:  python -m unittest discover -s tests -v

Every test builds disposable projects in a temp dir and points OSER at a temp ~/.claude, so nothing on the
machine (real transcripts, installed plugins, user settings) leaks in. 1.x fixtures exist only to prove
migration.
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

from oser_core import doctor, engine, ledger, metrics  # noqa: E402
from oser_core.util import sha, transcript_slug  # noqa: E402


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

    def turn(self, session, model, ts, agent=None, **usage):
        d = os.path.join(self.home, "projects", transcript_slug(self.proj))
        f = os.path.join(d, session + ".jsonl") if not agent else os.path.join(d, session, "subagents", "agent-%s.jsonl" % agent)
        os.makedirs(os.path.dirname(f), exist_ok=True)
        u = {"input_tokens": usage.get("i", 10), "output_tokens": usage.get("o", 5),
             "cache_read_input_tokens": usage.get("cr", 0), "cache_creation_input_tokens": usage.get("cw", 0),
             "output_tokens_details": {"thinking_tokens": usage.get("t", 0)}}
        ev = {"type": "assistant", "isSidechain": bool(agent), "timestamp": ts, "sessionId": session, "effort": usage.get("effort", "high"),
              "message": {"model": model, "usage": u}}
        if agent:
            ev["agentId"] = agent
        with io.open(f, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(ev) + "\n")

    def transcript(self, model, sidechain=False, ts="2026-09-25T05:00:00Z"):
        self.turn("abcd1234-0000", model, ts, agent="sub1" if sidechain else None)

    def manifest(self, **over):
        m = {
            "schema": "nnc-oser/project@3",
            "project": {"name": "proj", "language": "vi"},
            "phase": {"id": "pre-build", "label": "PRE-BUILD SETUP", "since": "2026-09-25", "summary": ["x"]},
            "mode": "setup",
            "authority": {"repo": "o/strategy", "ref": "main", "baseline": self.base, "entry": "docs/HANDOFF.md",
                          "local_path_hints": ["../strategy"]},
            "operating_model": {"root": {"model": "inherit"}, "governor": {"preferred_model": "claude-fable-5-1"},
                                "workers": {"assignment": "per-packet"}},
            "build": {"admission": "not_admitted"},
            "workspace": {"state_file": "workspace/TRANG-THAI.md", "dir": "workspace", "current": ["TRANG-THAI.md"]},
            "control_plane": {"current": ["CLAUDE.md", "workspace/TRANG-THAI.md"],
                              "historical": ["workspace/lich-su/"], "historical_banner": "LỊCH SỬ",
                              "stale_markers": [{"pattern": "BUILD LOT-0", "why": "old phase"}]},
            "compat": {"wrappers": {"cong-cu/do-quota.py": "quota"}},
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

    def v2_project(self):
        """The layout NNC OSER 2.0 left behind: project@2 manifest, inactive roster, doi-bac wrapper."""
        m = self.manifest()
        m["schema"] = "nnc-oser/project@2"
        m.pop("operating_model")
        m.pop("build")
        m["models"] = {"root": "inherit", "classes": {"worker": "sonnet", "mechanical": "haiku"}}
        m["capabilities"] = {"audit": {"enabled": False}}
        m["compat"]["wrappers"]["cong-cu/doi-bac.py"] = "doi-bac"
        m["control_plane"]["inactivate"] = [".claude/CO-CAU-NHAN-SU.md"]
        w(self.P(".claude", "oser", "project.json"), json.dumps(m, ensure_ascii=False, indent=2) + "\n")
        w(self.P(".claude", "oser", "inactive", "agents", "tho-dung.md"), "---\nname: tho-dung\n---\n")
        w(self.P(".claude", "oser", "inactive", "README.md"), "<!-- NNC-OSER:GENERATED template=inactive-readme@2 -->\n")
        wrapper = "# NNC-OSER:GENERATED template=wrapper-doi-bac@2 oser=2.0.0\nprint('retired')\n"
        w(self.P("cong-cu", "doi-bac.py"), wrapper)
        w(self.P("CLAUDE.md"), "# Proj\n\ncustom rule XYZ — project-owned\n")
        w(self.P("workspace", "TRANG-THAI.md"), "# Trạng thái\n\n**PRE-BUILD SETUP**\n")
        w(self.P(".claude", "oser", "lock.json"), json.dumps({"oser_version": "2.0.0", "mode": "setup", "artifacts": {
            "cong-cu/doi-bac.py": {"kind": "wrapper", "path": "cong-cu/doi-bac.py", "template": "wrapper-doi-bac@2",
                                   "wrapper": "doi-bac", "sha256": sha(wrapper)}}}) + "\n")
        g(self.proj, "add", "-A")
        g(self.proj, "commit", "-q", "-m", "v2")


class TestA_CleanInstall(Base):
    def test_install_setup_mode_is_clean(self):
        code, out = run_cli("install", "--project", self.proj, "--name", "demo", "--authority-repo", "o/strategy",
                            "--authority-entry", "docs/HANDOFF.md", "--authority-hint", "../strategy",
                            "--baseline", self.base, "--phase-id", "pre-build", "--phase-label", "PRE-BUILD SETUP",
                            env={"NNC_OSER_CLAUDE_HOME": self.home})
        self.assertEqual(code, 0, out)
        rep = doctor.run(self.proj)
        bad = [f for f in rep.findings if f["severity"] != "info"]
        self.assertEqual(bad, [], bad)
        self.assertFalse(os.path.isdir(self.P(".claude", "agents")), "no agent may be activated by install")
        s = json.loads(r(self.P(".claude", "settings.json")))
        self.assertNotIn("model", s)
        self.assertEqual(s["permissions"]["deny"], ["Agent", "Task", "Workflow"])
        m = json.loads(r(self.P(".claude", "oser", "project.json")))
        self.assertEqual(m["build"]["admission"], "not_admitted")
        self.assertNotIn("models", m)
        self.assertIn("CHƯA ADMIT", r(self.P("CLAUDE.md")))
        lock = json.loads(r(self.P(".claude", "oser", "lock.json")))
        self.assertEqual(lock["mode"], "setup")

    def test_install_refuses_existing_manifest(self):
        self.manifest()
        with self.assertRaises(engine.Blocked):
            engine.install(self.proj, "x", "o/s", "docs/HANDOFF.md")

    def test_build_mode_requires_admission(self):
        self.manifest(mode="build")
        rep = doctor.run(self.proj)
        self.assertTrue(any("requires build.admission" in f["message"] for f in rep.findings))
        with self.assertRaises(engine.Blocked):
            engine.update(self.proj)

    def test_fixed_effort_policy_is_rejected(self):
        self.manifest(build={"admission": "not_admitted", "effort_policy": {"floor": "high"}})
        self.assertTrue(any("effort_policy is not allowed" in f["message"] for f in doctor.run(self.proj).findings))


class TestB_Migration(Base):
    def test_migrate_v1_retires_roster_and_records_provenance(self):
        self.v1_project()
        self.transcript("claude-opus-5-5")
        self.manifest()
        g(self.proj, "add", "-A")
        g(self.proj, "commit", "-q", "-m", "manifest")
        state_before = r(self.P("workspace", "TRANG-THAI.md"))
        engine.migrate(self.proj)
        claude = r(self.P("CLAUDE.md"))
        self.assertIn("custom rule XYZ — project-owned", claude)
        self.assertIn("NNC-OSER:BEGIN block=status", claude)
        self.assertEqual(r(self.P("workspace", "TRANG-THAI.md")), state_before)
        for gone in ((".claude", "agents", "tho-dung.md"), (".claude", "CO-CAU-NHAN-SU.md"), (".claude", "BAC-DANG-DUNG.md"),
                     ("cong-cu", "doi-bac.py"), (".claude", "oser", "inactive")):
            self.assertFalse(os.path.exists(self.P(*gone)), gone)
        self.assertTrue(os.path.exists(self.P("workspace", "lich-su", "old-plan.md")))
        self.assertIn("NNC-OSER:GENERATED", r(self.P("cong-cu", "do-quota.py")))
        self.assertNotIn("model", json.loads(r(self.P(".claude", "settings.json"))))
        lock = json.loads(r(self.P(".claude", "oser", "lock.json")))
        actions = {a["action"] for a in lock["migrations"][0]["actions"]}
        self.assertTrue({"retire", "wrap", "unpin-root-model", "move"} <= actions, actions)
        seat = [a for a in lock["migrations"][0]["actions"] if a["path"] == ".claude/agents/tho-dung.md"][0]
        self.assertTrue(seat["git_blob"], "retired roster must name the git blob that keeps it")

    def test_migrate_v2_to_v3(self):
        self.v2_project()
        engine.migrate(self.proj)
        m = json.loads(r(self.P(".claude", "oser", "project.json")))
        self.assertEqual(m["schema"], "nnc-oser/project@3")
        for k in ("models", "capabilities"):
            self.assertNotIn(k, m)
        self.assertNotIn("inactivate", m["control_plane"])
        self.assertEqual(m["compat"]["wrappers"], {"cong-cu/do-quota.py": "quota"})
        self.assertEqual(m["build"]["admission"], "not_admitted")
        self.assertFalse(os.path.exists(self.P(".claude", "oser", "inactive")))
        self.assertFalse(os.path.exists(self.P("cong-cu", "doi-bac.py")))
        self.assertIn("custom rule XYZ — project-owned", r(self.P("CLAUDE.md")))
        c = doctor.run(self.proj).counts()
        self.assertEqual(c["critical"], 0, [f for f in doctor.run(self.proj).findings if f["severity"] == "critical"])

    def test_uncommitted_roster_blocks_without_writing(self):
        self.v2_project()
        w(self.P(".claude", "oser", "inactive", "agents", "tho-dung.md"), "---\nname: tho-dung\nlocal edit\n---\n")
        before = snapshot(self.proj)
        with self.assertRaises(engine.Blocked):
            engine.migrate(self.proj)
        self.assertEqual(snapshot(self.proj), before)

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
    def test_doctor_catches_legacy_collision_then_clears(self):
        self.v1_project()
        self.transcript("claude-opus-5-5")
        self.transcript("claude-fable-5-1", sidechain=True)
        w(self.P("workspace", "stray.md"), "live?\n")
        with io.open(self.P("CLAUDE.md"), "a", encoding="utf-8") as f:
            f.write("authority on branch `codex/dead-branch`\nGọi `tho-dung` rồi `kiem-luat`. worker = sonnet\n"
                    "Ghế cũ ở `.claude/oser/inactive/`\n")
        self.manifest()
        g(self.proj, "add", "-A")
        g(self.proj, "commit", "-q", "-m", "drift")
        before = doctor.run(self.proj)
        ids = {f["id"] for f in before.findings if f["severity"] != "info"}
        for expected in ("OSR-002", "OSR-011", "OSR-020", "OSR-021", "OSR-030", "OSR-031", "OSR-040", "OSR-050", "OSR-060", "OSR-100"):
            self.assertIn(expected, ids, expected)
        self.assertTrue(any("1.x seats" in f["message"] for f in before.findings))
        self.assertTrue(any("fixed model" in f["message"] for f in before.findings))
        self.assertTrue(any("retired roster location" in f["message"] for f in before.findings))
        w(self.P("CLAUDE.md"), "# Proj\n\ncustom rule XYZ — project-owned\n")
        os.remove(self.P("workspace", "stray.md"))
        engine.migrate(self.proj)
        after = doctor.run(self.proj)
        c = after.counts()
        self.assertEqual((c["critical"], c["warning"]), (0, 0), [f for f in after.findings if f["severity"] != "info"])

    def test_v2_manifest_keys_are_a_collision(self):
        self.v2_project()
        ids = {f["id"] for f in doctor.run(self.proj).findings if f["severity"] == "critical"}
        self.assertTrue({"OSR-001", "OSR-100"} <= ids, ids)

    def test_firebase_forbidden_default_is_critical(self):
        self.manifest(checks={"firebase": {"data_project": "kho-data", "forbidden_defaults": ["driver"],
                                           "hosting_sites": {"kho": "driver"}, "protected_sites": ["hifi"]}})
        w(self.P(".firebaserc"), '{"projects": {"default": "driver"}}\n')
        w(self.P("firebase.json"), '{"firestore": {"rules": "r"}, "hosting": {"site": "kho"}}\n')
        crit = [f for f in doctor.run(self.proj).findings if f["id"] == "OSR-080" and f["severity"] == "critical"]
        self.assertEqual(len(crit), 1)
        w(self.P(".firebaserc"), '{"projects": {"kho-data": "kho-data", "review-host": "driver"}}\n')
        self.assertEqual([f["severity"] for f in doctor.run(self.proj).findings if f["id"] == "OSR-080"], ["info"])

    def test_installed_plugin_version_drift_warns(self):
        self.manifest()
        w(os.path.join(self.home, "plugins", "installed_plugins.json"), json.dumps({"version": 2, "plugins": {
            "nnc@nnc-claude-plugins": [{"scope": "user", "version": "2.0.0",
                                        "installPath": "C:\\x\\.claude\\plugins\\cache\\nnc-claude-plugins\\nnc\\2.0.0"}]}}))
        f = [x for x in doctor.run(self.proj).findings if x["id"] == "OSR-090"]
        self.assertEqual([x["severity"] for x in f], ["warning"], f)
        self.assertIn("2.0.0", f[0]["message"])

    def test_oversized_state_file_warns(self):
        self.manifest()
        w(self.P("workspace", "TRANG-THAI.md"), "**PRE-BUILD SETUP**\n" + "x" * (16 * 1024))
        self.assertTrue(any(f["id"] == "OSR-061" for f in doctor.run(self.proj).findings))


class TestD_Idempotence(Base):
    def test_second_migrate_and_update_change_nothing(self):
        self.v1_project()
        self.manifest()
        g(self.proj, "add", "-A")
        g(self.proj, "commit", "-q", "-m", "manifest")
        engine.migrate(self.proj)
        first = snapshot(self.proj)
        self.assertEqual(engine.migrate(self.proj).actions, [])
        self.assertEqual(engine.update(self.proj).actions, [])
        self.assertEqual(snapshot(self.proj), first)

    def test_v2_migration_is_idempotent(self):
        self.v2_project()
        engine.migrate(self.proj)
        first = snapshot(self.proj)
        self.assertEqual(engine.migrate(self.proj).actions, [])
        self.assertEqual(engine.update(self.proj).actions, [])
        self.assertEqual(snapshot(self.proj), first)

    def test_hand_edited_generated_file_is_not_overwritten(self):
        self.manifest()
        w(self.P("workspace", "TRANG-THAI.md"), "**PRE-BUILD SETUP**\n")
        engine.update(self.proj)
        cp = self.P(".claude", "oser", "CONTROL-PLANE.md")
        with io.open(cp, "a", encoding="utf-8") as f:
            f.write("hand edit\n")
        m = json.loads(r(self.P(".claude", "oser", "project.json")))
        m["phase"]["summary"] = ["changed"]
        w(self.P(".claude", "oser", "project.json"), json.dumps(m, ensure_ascii=False, indent=2) + "\n")
        plan = engine.update(self.proj)
        self.assertIn("hand edit", r(cp))
        self.assertTrue(any("SKIPPED hand-edited" in n for n in plan.notes))


class TestE_Wrappers(Base):
    def test_quota_wrapper_delegates_and_reports_raw_usage(self):
        self.v1_project()
        self.transcript("claude-opus-5-5")
        self.manifest()
        g(self.proj, "add", "-A")
        g(self.proj, "commit", "-q", "-m", "manifest")
        engine.migrate(self.proj)
        p = subprocess.run([sys.executable, self.P("cong-cu", "do-quota.py")], capture_output=True, text=True,
                           encoding="utf-8", env=dict(os.environ))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("claude-opus-5-5", p.stdout)
        self.assertIn("WEEKLY · FABLE", p.stdout)
        self.assertNotIn("API-PRICE", p.stdout, "API-price weights must be opt-in only")


class TestF_LedgerMetrics(Base):
    """A synthetic wave with hand-computed expectations for every metric."""

    def wave(self):
        self.manifest()
        R, G = "root-1", "gov-1"
        self.turn(R, "claude-opus-5-5", "2026-09-26T10:00:00Z", i=100, cr=9900)
        self.turn(R, "claude-opus-5-5", "2026-09-26T12:00:00Z", i=200, cr=11800)
        self.turn(G, "claude-fable-5-1", "2026-09-26T10:10:00Z", i=1000, o=500, cw=500)
        U = {"w1": ("claude-sonnet-5", 1000, 1000), "w2": ("claude-sonnet-5", 2000, 1000), "v1": ("claude-opus-5-5", 500, 500),
             "w3": ("claude-opus-5-5", 3000, 1000), "v2": ("claude-opus-5-5", 500, 500), "w4": ("claude-haiku-4-5-20251001", 300, 200),
             "w5": ("claude-sonnet-5", 1000, 500)}
        for a, (mdl, i, o) in U.items():
            self.turn(G, mdl, "2026-09-26T10:20:00Z", agent=a, i=i, o=o)
        ctx = {"must_read": ["docs/x.md"], "may_read": [], "must_not_load": ["workspace/lich-su/"], "output_budget": "40 lines"}
        sig = {s: "medium" for s in ("complexity", "ambiguity", "blast_radius", "reversibility", "testability",
                                     "context_load", "independence", "dependency_count", "prior_rework")}
        mf = {"considered": True, "tools": ["npm run kiem"]}

        def att(pid, n, role, model, effort, agent, outcome, defects=0):
            return {"event": "attempt", "packetId": pid, "attempt": n, "role": role, "outcome": outcome, "defects": defects,
                    "plan": {"model": model, "effort": effort, "mode": "fresh_session"},
                    "execution": {"sessionId": G, "agentId": agent}}

        evs = [{"event": "wave_open", "waveId": "W1", "rootSessionId": R, "scope": "fixture", "at": "2026-09-26T10:05:00Z",
                "governor": {"sessionId": G, "model": "claude-fable-5-1", "effort": "high"}}]
        for pid, cls, depth in (("P1", "ui-adapt", "machine"), ("P2", "data-migration", "independent_review"), ("P3", "ui-adapt", "machine")):
            evs.append({"event": "packet_open", "packetId": pid, "waveId": "W1", "taskClass": cls, "signals": sig,
                        "context": ctx, "verification_depth": depth, "machine_first": mf})
        evs += [att("P1", 1, "implement", "claude-sonnet-5", "high", "w1", "pass"),
                att("P2", 1, "implement", "claude-sonnet-5", "medium", "w2", "rework_required"),
                att("P2", 2, "review", "claude-opus-5-5", "high", "v1", "fail", defects=2),
                att("P2", 3, "implement", "claude-opus-5-5", "xhigh", "w3", "pass"),
                att("P2", 4, "review", "claude-opus-5-5", "high", "v2", "pass"),
                att("P3", 1, "implement", "claude-haiku-4-5-20251001", "low", "w4", "escalate"),
                att("P3", 2, "implement", "claude-sonnet-5", "high", "w5", "pass")]
        for pid, states in (("P1", ["EXECUTED", "MACHINE_VERIFIED", "FABLE_ACCEPTED"]),
                            ("P2", ["EXECUTED", "MACHINE_VERIFIED", "INDEPENDENT_REVIEWED", "FABLE_ACCEPTED"]),
                            ("P3", ["EXECUTED", "MACHINE_VERIFIED", "FABLE_ACCEPTED"])):
            evs += [{"event": "packet_state", "packetId": pid, "state": s} for s in states]
        evs += [{"event": "wave_state", "waveId": "W1", "state": s} for s in ("PACKETS_ACCEPTED", "FABLE_CONSOLIDATED", "ROOT_REVIEW")]
        evs += [{"event": "wave_state", "waveId": "W1", "state": "ROOT_ACCEPTED", "at": "2026-09-26T12:30:00Z", "clean_result_chars": 4000},
                {"event": "defect", "waveId": "W1", "phase": "after_acceptance", "severity": "minor"},
                {"event": "root_handoff", "fromSessionId": R, "toSessionId": "root-2", "reason": "context growth",
                 "stateRefs": ["workspace/TRANG-THAI.md"]}]
        for ev in evs:
            self.assertEqual(ledger.append(self.proj, ev), [], ev)

    def test_metrics_from_raw_usage(self):
        self.wave()
        m = metrics.compute(self.proj)
        self.assertEqual(m["packets_accepted"], 3)
        self.assertAlmostEqual(m["FIRST_PASS_ACCEPT_RATE"], 1 / 3)
        self.assertAlmostEqual(m["REWORK_AMPLIFICATION"], 13000 / 5500)
        self.assertAlmostEqual(m["VERIFIED_RESULT_COST"]["per_accepted_packet_work_mean"], 13000 / 3)
        self.assertEqual(m["VERIFIED_RESULT_COST"]["per_root_accepted_wave_work_mean"], 15000)
        self.assertEqual(m["ROOT_CONTEXT_GROWTH"]["per_accepted_wave_mean_tokens"], 2000)
        self.assertEqual(m["ROOT_CONTEXT_GROWTH"]["root_handoffs"], 1)
        self.assertAlmostEqual(m["CONTEXT_ISOLATION_GAIN"], 7.5)
        self.assertEqual(m["DEFECT_CONTAINMENT"], {"before_integration": 2, "after_acceptance": 1, "rate": 2 / 3})
        self.assertAlmostEqual(m["FABLE_LEVERAGE"]["accepted_packets_per_M_fable_work"], 1500.0)
        self.assertEqual((m["ESCALATION_EFFICIENCY"]["escalated"], m["ESCALATION_EFFICIENCY"]["resolved"]), (1, 1))
        plans = {tuple(p["key"]): p for p in m["plans"]}
        self.assertEqual(plans[("claude-sonnet-5", "high")]["final_accepted"], 2)
        self.assertEqual(plans[("claude-sonnet-5", "high")]["first_pass_rate"], 1.0)
        self.assertEqual(plans[("claude-sonnet-5", "medium")]["verify_defects"], 2)
        self.assertEqual(plans[("claude-sonnet-5", "medium")]["rework"], 1)
        self.assertEqual(plans[("claude-opus-5-5", "xhigh")]["final_accepted"], 1)
        self.assertIn(("data-migration", "claude-opus-5-5", "xhigh"), plans)
        self.assertEqual(m["unknown"], [])

    def test_lifecycle_is_enforced(self):
        self.wave()
        self.assertTrue(ledger.append(self.proj, {"event": "wave_state", "waveId": "W1", "state": "ROOT_REVIEW"}))
        self.manifest()
        evs = [{"event": "wave_open", "waveId": "W2", "rootSessionId": "r", "scope": "s",
                "governor": {"sessionId": "g", "model": "m", "effort": "high"}},
               {"event": "packet_open", "packetId": "Q1", "waveId": "W2", "taskClass": "c",
                "signals": {s: "unknown" for s in ("complexity", "ambiguity", "blast_radius", "reversibility", "testability",
                                                   "context_load", "independence", "dependency_count", "prior_rework")},
                "context": {"must_read": [], "may_read": [], "must_not_load": [], "output_budget": "x"},
                "verification_depth": "machine", "machine_first": {"considered": True}}]
        for ev in evs:
            self.assertEqual(ledger.append(self.proj, ev), [])
        self.assertTrue(ledger.append(self.proj, {"event": "packet_state", "packetId": "Q1", "state": "FABLE_ACCEPTED"}),
                        "FABLE_ACCEPTED without MACHINE_VERIFIED must be rejected")
        self.assertTrue(ledger.append(self.proj, {"event": "wave_state", "waveId": "W2", "state": "PACKETS_ACCEPTED"}),
                        "a wave cannot accept while a packet is open")
        bad = {"event": "attempt", "packetId": "Q1", "attempt": 1, "role": "implement", "outcome": "pass",
               "plan": {"model": "m", "effort": "ultra", "mode": "fresh_session"}, "execution": {"sessionId": "s"}}
        self.assertTrue(any("not a runtime effort" in e for e in ledger.append(self.proj, bad)))
        ok = dict(bad, plan={"model": "m", "effort": "low", "mode": "fresh_session"})
        self.assertEqual(ledger.append(self.proj, ok), [], "every runtime effort is a valid candidate")

    def test_cli_metrics_and_root(self):
        self.wave()
        code, out = run_cli("metrics", "--project", self.proj, env={"NNC_OSER_CLAUDE_HOME": self.home})
        self.assertEqual(code, 0, out)
        self.assertIn("REWORK_AMPLIFICATION", out)
        self.assertIn("PLAN BENCHMARK", out)
        code, out = run_cli("root", "--project", self.proj, env={"NNC_OSER_CLAUDE_HOME": self.home})
        self.assertIn("handoff", out)
        code, out = run_cli("ledger", "check", "--project", self.proj, env={"NNC_OSER_CLAUDE_HOME": self.home})
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
