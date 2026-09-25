# -*- coding: utf-8 -*-
"""install / update / migrate. Every command is a plan of actions; `dry_run` prints the plan only.

Ownership rules enforced here:
  * `.claude/oser/project.json` and every file outside a GENERATED marker are PROJECT-OWNED: `update` never
    rewrites them; `install` writes one-time scaffolds; only the explicit `migrate` upgrades the manifest schema.
  * GENERATED artifacts are rewritten only when their content changes, and never when the file on disk was
    hand-edited since the last update (reported instead) or is listed in `overrides`.
  * Legacy files (NNC-AI-OSer 1.x, NNC OSER 2.0) are removed only when provably recoverable: an unmodified
    fingerprinted copy, an unmodified generated file recorded in the lock, or a file git holds unmodified.
"""
import glob
import os

from . import render
from .manifest import LEGACY_SCHEMAS, LOCK, MANIFEST, SCHEMA_ID, load, mode_spec
from .util import (dump_json, git, load_catalog, load_json, now_iso, plugin_version, read_text, rel, sha, template,
                   write_text)

CONTROL_PLANE_DOC = ".claude/oser/CONTROL-PLANE.md"
SETTINGS = ".claude/settings.json"


class Blocked(Exception):
    """A step would destroy or overwrite project-owned content; nothing was written."""


class Plan:
    def __init__(self, root, dry_run):
        self.root, self.dry_run = root, dry_run
        self.actions, self.notes = [], []

    def p(self, relpath):
        return os.path.join(self.root, relpath)

    def write(self, relpath, text, why):
        cur = read_text(self.p(relpath))
        if cur == text.replace("\r\n", "\n"):
            return False
        self.actions.append(("write" if cur is not None else "create", relpath, why))
        if not self.dry_run:
            write_text(self.p(relpath), text)
        return True

    def move(self, src, dst, why):
        s, d = self.p(src), self.p(dst)
        if not os.path.exists(s):
            return False
        if os.path.exists(d):
            if read_text(s) == read_text(d):
                self.actions.append(("remove-duplicate", src, "identical copy already at " + dst))
                if not self.dry_run:
                    os.remove(s)
                return True
            raise Blocked("cannot move %s -> %s: destination exists with different content" % (src, dst))
        self.actions.append(("move", src + " -> " + dst, why))
        if not self.dry_run:
            os.makedirs(os.path.dirname(d), exist_ok=True)
            os.replace(s, d)
        return True

    def remove(self, relpath, why):
        if not os.path.exists(self.p(relpath)):
            return False
        self.actions.append(("remove", relpath, why))
        if not self.dry_run:
            os.remove(self.p(relpath))
            d = os.path.dirname(self.p(relpath))
            while d and os.path.isdir(d) and not os.listdir(d) and os.path.abspath(d) != os.path.abspath(self.root):
                os.rmdir(d)
                d = os.path.dirname(d)
        return True


def _load_lock(root):
    return load_json(os.path.join(root, LOCK)) or {}


def _require_manifest(root):
    m, errors = load(root)
    if m is None or errors:
        raise Blocked("manifest invalid: " + "; ".join(errors))
    return m


def git_preserved(root, relpath):
    """True when git tracks the file and the working copy equals HEAD (history can restore it exactly)."""
    if git(root, "ls-files", "--error-unmatch", relpath)[0] != 0:
        return False
    rc, out = git(root, "status", "--porcelain", "--", relpath)
    return rc == 0 and out == ""


# ------------------------------------------------------------------------------------------ legacy

def detect_legacy(root, m=None, lock=None):
    """Legacy organisational/control-plane artefacts. Each finding: key, path, state, action."""
    cat = load_catalog("legacy-v1.json")
    lock = lock if lock is not None else _load_lock(root)
    found = []
    wrappers = dict(((m or {}).get("compat") or {}).get("wrappers") or {})
    for key, t in cat["tools"].items():
        paths = [p for p, k in wrappers.items() if k == {"doi-bac": "doi-bac", "do-quota": "quota"}[key]] or [t["default_path"]]
        for p in paths:
            text = read_text(os.path.join(root, p))
            if text is None or "NNC-OSER:GENERATED" in text[:400]:
                continue
            state = "pristine" if sha(text) in t["sha256"] else ("modified" if t["signature"] in text else None)
            if state:
                found.append({"key": key, "path": p, "state": state, "action": t["replacement"]})
    for key, g in cat["generated"].items():
        text = read_text(os.path.join(root, g["path"]))
        if text is not None and g["signature"] in text:
            found.append({"key": key, "path": g["path"], "state": "generated", "action": "retire"})
    for key, a in (lock.get("artifacts") or {}).items():
        if a.get("kind") == "wrapper" and cat["v2_wrapper_templates"].get(a.get("template")) == "retire":
            text = read_text(os.path.join(root, a["path"]))
            if text is not None:
                found.append({"key": "v2-wrapper", "path": a["path"], "action": "retire",
                              "state": "generated" if sha(text) == a.get("sha256") else "modified"})
    roster = set(cat["v1_roster"])
    for f in sorted(glob.glob(os.path.join(root, ".claude", "agents", "*.md"))):
        if os.path.basename(f)[:-3] in roster:
            found.append({"key": "v1-seat", "path": rel(root, f), "state": "roster", "action": "retire"})
    team = cat["v1_team_doc"]
    if os.path.isfile(os.path.join(root, team)):
        found.append({"key": "v1-team-doc", "path": team, "state": "roster", "action": "retire"})
    inactive = os.path.join(root, cat["v2_inactive_dir"])
    for d, _, files in os.walk(inactive):
        for fn in sorted(files):
            found.append({"key": "v2-inactive", "path": rel(root, os.path.join(d, fn)), "state": "roster", "action": "retire"})
    return found


def upgrade_manifest(m):
    """2.0 → 3.0 manifest: drop fixed model classes / capability catalog / assignments; add operating model."""
    out = {}
    for k, v in m.items():
        if k in ("models", "capabilities", "assignments"):
            continue
        out[k] = v
        if k == "authority":
            out["operating_model"] = {
                "root": {"model": (m.get("models") or {}).get("root") or "inherit"},
                "governor": {"preferred_model": None, "session": "one-per-wave"},
                "workers": {"assignment": "per-packet"},
            }
            out["build"] = {"admission": "not_admitted"}
            out["resources"] = {"weekly_all_models": {"cap": "ui-only"},
                                "weekly_fable": {"cap": "ui-only", "nested_in": "weekly_all_models"}}
    out["schema"] = SCHEMA_ID
    cp = dict(out.get("control_plane") or {})
    cp.pop("inactivate", None)
    out["control_plane"] = cp
    w = dict((out.get("compat") or {}).get("wrappers") or {})
    for p in [p for p, k in w.items() if k == "doi-bac"]:
        w.pop(p)
    if "compat" in out:
        out["compat"] = dict(out["compat"], wrappers=w)
    return out


# ------------------------------------------------------------------------------------------ update

def _wrappers(m, lock):
    w = {p: k for p, k in (((m.get("compat") or {}).get("wrappers")) or {}).items() if k in render.WRAPPERS}
    for key, a in (lock.get("artifacts") or {}).items():
        if a.get("kind") == "wrapper" and key not in w and a.get("wrapper") in render.WRAPPERS:
            w[key] = a["wrapper"]
    return w


def update(root, dry_run=False, force=False, _skip_legacy_check=False, _extra_wrappers=None):
    m = _require_manifest(root)
    if not _skip_legacy_check:
        legacy = detect_legacy(root, m)
        if legacy:
            raise Blocked("legacy organisational/control-plane artefacts present (%s) — run: oser migrate"
                          % ", ".join(x["path"] for x in legacy))
    version = plugin_version()
    plan = Plan(root, dry_run)
    lock = _load_lock(root)
    old_art = lock.get("artifacts") or {}
    overrides = set(m.get("overrides") or [])
    new_art = {}
    stamp = now_iso()

    def emit(key, relpath, text, kind, tmpl, extra=None):
        prev = old_art.get(key) or {}
        disk = read_text(os.path.join(root, relpath)) if kind != "block" else render.extract_block(
            read_text(os.path.join(root, relpath)) or "")
        if relpath in overrides:
            plan.notes.append("override kept: " + relpath)
            new_art[key] = dict(prev, kind=kind, template=tmpl, overridden=True)
            return
        if disk is not None and prev.get("sha256") and sha(disk) != prev["sha256"] and sha(disk) != sha(text) and not force:
            plan.notes.append("SKIPPED hand-edited generated artifact %s (declare in overrides, or --force)" % relpath)
            new_art[key] = prev
            return
        changed = (disk is None) or sha(disk) != sha(text)
        if changed:
            if kind == "block":
                full = read_text(os.path.join(root, relpath))
                if full is None:
                    full = template("CLAUDE.md").replace("{{NAME}}", m["project"]["name"])
                plan.write(relpath, render.splice_block(full, text), "generated block " + tmpl)
            else:
                plan.write(relpath, text, "generated " + tmpl)
        entry = {"kind": kind, "path": relpath, "template": tmpl, "sha256": sha(text), "oser_version": version,
                 "mode": m["mode"], "generated_at": prev.get("generated_at") if not changed and prev else stamp}
        entry.update(extra or {})
        new_art[key] = entry

    emit("CLAUDE.md#status", "CLAUDE.md", render.claude_block(m, version), "block", render.BLOCK_TEMPLATE)
    wrappers = _wrappers(m, lock)
    wrappers.update(_extra_wrappers or {})
    for relpath, kind in sorted(wrappers.items()):
        emit(relpath, relpath, render.wrapper(kind, relpath, m, version), "wrapper",
             render.WRAPPERS[kind][0], {"wrapper": kind})
    generated_paths = sorted(set((k if a.get("kind") == "block" else a["path"]) for k, a in new_art.items()
                                 if a.get("path")) | {CONTROL_PLANE_DOC})
    emit(CONTROL_PLANE_DOC, CONTROL_PLANE_DOC, render.control_plane_doc(m, version, generated_paths), "file",
         "control-plane@3")

    managed = render.managed_settings(m)
    prev_deny = (old_art.get(SETTINGS + "#managed") or {}).get("deny", [])
    sp = os.path.join(root, SETTINGS)
    cur_settings = load_json(sp) if os.path.isfile(sp) else {}
    new_settings = render.apply_settings(cur_settings, managed, prev_deny)
    if new_settings != cur_settings and (new_settings or os.path.isfile(sp)):
        plan.write(SETTINGS, dump_json(new_settings), "managed keys: model=%s deny=%s"
                   % (managed["model"] or "(inherit)", managed["deny"]))
    prev_s = old_art.get(SETTINGS + "#managed") or {}
    same = prev_s.get("deny") == managed["deny"] and prev_s.get("model") == managed["model"]
    new_art[SETTINGS + "#managed"] = {"kind": "managed-keys", "path": SETTINGS, "template": "settings@3",
                                      "model": managed["model"], "deny": managed["deny"], "oser_version": version,
                                      "mode": m["mode"],
                                      "generated_at": prev_s.get("generated_at") if same and prev_s else stamp}

    new_lock = {
        "lock_schema": "nnc-oser/lock@1",
        "manifest_schema": SCHEMA_ID,
        "oser_version": version,
        "mode": m["mode"],
        "phase": m["phase"]["id"],
        "manifest_sha256": sha(read_text(os.path.join(root, MANIFEST))),
        "artifacts": dict(sorted(new_art.items())),
        "migrations": lock.get("migrations") or [],
        "retired": lock.get("retired") or [],
    }
    comparable = {k: v for k, v in lock.items() if k != "updated_at"}
    new_lock["updated_at"] = stamp if comparable != new_lock else lock.get("updated_at", stamp)
    plan.write(LOCK, dump_json(new_lock), "provenance")
    return plan


# ------------------------------------------------------------------------------------------ migrate

def migrate(root, dry_run=False, force=False):
    mp = os.path.join(root, MANIFEST)
    raw = load_json(mp)
    if raw is None:
        raise Blocked("no %s — run `oser install` for a new project, or author the manifest first "
                      "(template: plugins/nnc/oser/templates/project.example.json)" % MANIFEST)
    plan = Plan(root, dry_run)
    record = []
    source = "nnc-ai-oser-1.0"
    if raw.get("schema") in LEGACY_SCHEMAS:
        source = "nnc-oser-2.0"
        new = upgrade_manifest(raw)
        record.append({"action": "manifest-upgrade", "path": MANIFEST, "from_schema": raw["schema"],
                       "to_schema": SCHEMA_ID, "from_sha256": sha(read_text(mp))})
        m = new
    else:
        m = raw
    from .manifest import validate
    errors = validate(m)
    if errors:
        raise Blocked("manifest invalid: " + "; ".join(errors))
    lock = _load_lock(root)
    overrides = set(m.get("overrides") or [])
    extra_wrappers = {}

    findings = detect_legacy(root, m, lock)
    for x in findings:  # verify every removal is recoverable BEFORE touching anything
        if x["path"] in overrides:
            continue
        if x["state"] == "modified":
            raise Blocked("%s is a MODIFIED legacy file (%s) — project-owned content, not removed. "
                          "Reconcile by hand or list it in overrides." % (x["path"], x["key"]))
        if x["state"] == "roster" and not git_preserved(root, x["path"]):
            raise Blocked("%s (%s) is not committed unmodified in git — commit it first so history keeps it, "
                          "then re-run migrate" % (x["path"], x["key"]))
    if source == "nnc-oser-2.0":  # only after every removal is proven recoverable
        plan.write(MANIFEST, dump_json(m), "manifest %s → %s (fixed model classes / capability catalog removed)"
                   % (raw["schema"], SCHEMA_ID))
    for x in findings:
        if x["path"] in overrides:
            continue
        text = read_text(os.path.join(root, x["path"]))
        if x["action"] == "wrapper-quota":
            extra_wrappers[x["path"]] = "quota"
            record.append({"action": "wrap", "path": x["path"], "from_sha256": sha(text), "canonical": "oser quota"})
            continue
        why = {"v1-seat": "1.x seat — current model is Root/Governor/per-packet plans; git keeps it",
               "v1-team-doc": "1.x team doc — superseded by operating model; git keeps it",
               "v2-inactive": "2.0 inactive roster evidence — git keeps it",
               "v2-wrapper": "2.0 model-profile wrapper retired",
               "doi-bac": "1.x model-profile tool retired",
               "bac-dang-dung": "1.x generated model state retired"}.get(x["key"], "legacy retired")
        plan.remove(x["path"], why)
        blob = git(root, "rev-parse", "HEAD:" + x["path"])[1] if x["state"] == "roster" else None
        record.append({"action": "retire", "path": x["path"], "sha256": sha(text or ""), "git_blob": blob})

    sp = os.path.join(root, SETTINGS)
    settings = load_json(sp) if os.path.isfile(sp) else {}
    if settings.get("model") and render.managed_settings(m)["model"] is None:
        record.append({"action": "unpin-root-model", "path": SETTINGS, "was": settings["model"],
                       "why": "operating_model.root.model=inherit — client session model is authoritative"})
    for mv in ((m.get("migrate") or {}).get("moves") or []):
        if plan.move(mv["from"], mv["to"], mv.get("why", "declared move")):
            record.append({"action": "move", "path": mv["from"], "to": mv["to"]})

    if not dry_run and record:
        lock = _load_lock(root)
        lock.setdefault("migrations", []).append({"from": source, "oser_version": plugin_version(),
                                                  "at": now_iso(), "actions": record})
        retired = {r["path"] for r in record if r["action"] == "retire"}
        lock["retired"] = sorted(set(lock.get("retired") or []) | retired)
        lock["artifacts"] = {k: a for k, a in (lock.get("artifacts") or {}).items() if a.get("path") not in retired}
        write_text(os.path.join(root, LOCK), dump_json(lock))
    if dry_run and source == "nnc-oser-2.0":
        return plan
    up = update(root, dry_run=dry_run, force=force, _skip_legacy_check=True, _extra_wrappers=extra_wrappers)
    plan.actions += up.actions
    plan.notes += up.notes
    return plan


# ------------------------------------------------------------------------------------------ install

def install(root, name, authority_repo, authority_entry, authority_ref="main", authority_hint=None,
            baseline=None, phase_id="setup", phase_label="SETUP", language="vi", dry_run=False):
    mp = os.path.join(root, MANIFEST)
    if os.path.exists(mp):
        raise Blocked("%s already exists — use `oser update` (or `oser migrate` for an older layout)" % MANIFEST)
    if detect_legacy(root, None, {}):
        raise Blocked("legacy NNC-AI-OSer artefacts found — author the manifest, then run `oser migrate`")
    plan = Plan(root, dry_run)
    manifest = {
        "schema": SCHEMA_ID,
        "project": {"name": name, "language": language},
        "phase": {"id": phase_id, "label": phase_label, "summary": []},
        "mode": "setup",
        "authority": {"repo": authority_repo, "ref": authority_ref, "entry": authority_entry,
                      "local_path_hints": [authority_hint] if authority_hint else []},
        "operating_model": {"root": {"model": "inherit"},
                            "governor": {"preferred_model": None, "session": "one-per-wave"},
                            "workers": {"assignment": "per-packet"}},
        "build": {"admission": "not_admitted"},
        "resources": {"weekly_all_models": {"cap": "ui-only"},
                      "weekly_fable": {"cap": "ui-only", "nested_in": "weekly_all_models"}},
        "workspace": {"state_file": "workspace/TRANG-THAI.md", "dir": "workspace", "current": ["TRANG-THAI.md"]},
        "control_plane": {"current": ["CLAUDE.md", "workspace/TRANG-THAI.md"], "historical": [], "stale_markers": []},
    }
    if baseline:
        manifest["authority"]["baseline"] = baseline
    plan.write(MANIFEST, dump_json(manifest), "project declaration (PROJECT-OWNED scaffold)")
    if not os.path.exists(os.path.join(root, "workspace", "TRANG-THAI.md")):
        plan.write("workspace/TRANG-THAI.md", template("TRANG-THAI.md").replace("{{NAME}}", name)
                   .replace("{{PHASE_LABEL}}", phase_label), "live state (PROJECT-OWNED scaffold)")
    if dry_run:
        return plan
    up = update(root)
    plan.actions += up.actions
    plan.notes += up.notes
    return plan
