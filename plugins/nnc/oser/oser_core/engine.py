# -*- coding: utf-8 -*-
"""install / update / migrate. Every command is a plan of actions; `dry_run` prints the plan only.

Ownership rules enforced here:
  * `.claude/oser/project.json` and every file outside a GENERATED marker are PROJECT-OWNED: never rewritten
    (install writes one-time scaffolds only when the file does not exist).
  * GENERATED artifacts are rewritten only when their content changes, and never when the file on disk was
    hand-edited since the last update (reported instead) or is listed in `overrides`.
  * Legacy (NNC-AI-OSer 1.0) files are replaced only when their fingerprint proves they are unmodified copies.
"""
import glob
import os

from . import render
from .manifest import INACTIVE_DIR, LOCK, MANIFEST, SCHEMA_ID, load, mode_spec
from .util import dump_json, load_catalog, load_json, now_iso, read_text, rel, sha, template, write_text

CONTROL_PLANE_DOC = ".claude/oser/CONTROL-PLANE.md"
INACTIVE_README = INACTIVE_DIR + "/README.md"
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
        return True


def _load_lock(root):
    return load_json(os.path.join(root, LOCK)) or {}


def _require_manifest(root):
    m, errors = load(root)
    if m is None or errors:
        raise Blocked("manifest invalid: " + "; ".join(errors))
    return m


# ------------------------------------------------------------------------------------------ legacy

def detect_legacy(root, m=None):
    """Return a list of legacy (1.0) findings: dicts with key, path, state ('pristine'|'modified'|'generated')."""
    cat = load_catalog("legacy-v1.json")
    found = []
    wrappers = dict(((m or {}).get("compat") or {}).get("wrappers") or {})
    for key, t in cat["tools"].items():
        paths = [p for p, k in wrappers.items() if k == {"doi-bac": "doi-bac", "do-quota": "quota"}[key]] or [t["default_path"]]
        for p in paths:
            text = read_text(os.path.join(root, p))
            if text is None or "NNC-OSER:GENERATED" in text[:400]:
                continue
            if sha(text) in t["sha256"]:
                found.append({"key": key, "path": p, "state": "pristine", "replacement": t["replacement"]})
            elif t["signature"] in text:
                found.append({"key": key, "path": p, "state": "modified", "replacement": t["replacement"]})
    for key, g in cat["generated"].items():
        text = read_text(os.path.join(root, g["path"]))
        if text is not None and g["signature"] in text:
            found.append({"key": key, "path": g["path"], "state": "generated"})
    return found


# ------------------------------------------------------------------------------------------ update

def _wrappers(m, lock):
    w = dict(((m.get("compat") or {}).get("wrappers")) or {})
    for key, a in (lock.get("artifacts") or {}).items():
        if a.get("kind") == "wrapper" and key not in w:
            w[key] = a["wrapper"]
    return w


def update(root, dry_run=False, force=False, _skip_legacy_check=False, _extra_wrappers=None):
    m = _require_manifest(root)
    if not _skip_legacy_check:
        legacy = detect_legacy(root, m)
        if legacy:
            raise Blocked("legacy NNC-AI-OSer 1.0 artifacts present (%s) — run: oser migrate"
                          % ", ".join(x["path"] for x in legacy))
    from .util import plugin_version
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
    if os.path.isdir(os.path.join(root, INACTIVE_DIR)):
        emit(INACTIVE_README, INACTIVE_README, render.inactive_readme(m, version), "file", "inactive-readme@2")
    generated_paths = sorted(set((k if a.get("kind") == "block" else a["path"]) for k, a in new_art.items()
                                 if a.get("path")) | {CONTROL_PLANE_DOC})
    emit(CONTROL_PLANE_DOC, CONTROL_PLANE_DOC, render.control_plane_doc(m, version, generated_paths), "file",
         "control-plane@2")

    # settings.json — only the managed keys
    managed = render.managed_settings(m)
    prev_deny = (old_art.get(SETTINGS + "#managed") or {}).get("deny", [])
    sp = os.path.join(root, SETTINGS)
    cur_settings = load_json(sp) if os.path.isfile(sp) else {}
    new_settings = render.apply_settings(cur_settings, managed, prev_deny)
    if new_settings != cur_settings:
        if new_settings or os.path.isfile(sp):
            plan.write(SETTINGS, dump_json(new_settings), "managed keys: model=%s deny=%s"
                       % (managed["model"] or "(inherit)", managed["deny"]))
    prev_s = old_art.get(SETTINGS + "#managed") or {}
    same = prev_s.get("deny") == managed["deny"] and prev_s.get("model") == managed["model"]
    new_art[SETTINGS + "#managed"] = {"kind": "managed-keys", "path": SETTINGS, "template": "settings@2",
                                      "model": managed["model"], "deny": managed["deny"], "oser_version": version,
                                      "mode": m["mode"],
                                      "generated_at": prev_s.get("generated_at") if same and prev_s else stamp}

    manifest_text = read_text(os.path.join(root, MANIFEST))
    new_lock = {
        "lock_schema": "nnc-oser/lock@1",
        "manifest_schema": SCHEMA_ID,
        "oser_version": version,
        "mode": m["mode"],
        "phase": m["phase"]["id"],
        "manifest_sha256": sha(manifest_text),
        "artifacts": dict(sorted(new_art.items())),
        "migrations": lock.get("migrations") or [],
        "retired": lock.get("retired") or [],
    }
    comparable = {k: v for k, v in lock.items() if k != "updated_at"}
    if comparable != new_lock:
        new_lock["updated_at"] = stamp
    else:
        new_lock["updated_at"] = lock.get("updated_at", stamp)
    plan.write(LOCK, dump_json(new_lock), "provenance")
    return plan


# ------------------------------------------------------------------------------------------ migrate

def migrate(root, dry_run=False, force=False):
    m, errors = load(root)
    if m is None:
        raise Blocked("no %s — run `oser install` for a new project, or author the manifest first "
                      "(template: plugins/nnc/oser/templates/project.example.json)" % MANIFEST)
    if errors:
        raise Blocked("manifest invalid: " + "; ".join(errors))
    lock = _load_lock(root)
    plan = Plan(root, dry_run)
    overrides = set(m.get("overrides") or [])
    record = []
    extra_wrappers = {}

    for x in detect_legacy(root, m):
        if x["state"] == "generated":
            text = read_text(os.path.join(root, x["path"]))
            plan.remove(x["path"], "retired 1.0 generated file (superseded by CLAUDE.md OSER block)")
            record.append({"action": "retire", "path": x["path"], "sha256": sha(text)})
        elif x["state"] == "pristine":
            kind = {"wrapper-quota": "quota", "wrapper-doi-bac": "doi-bac"}[x["replacement"]]
            extra_wrappers[x["path"]] = kind
            record.append({"action": "wrap", "path": x["path"], "from_sha256": sha(read_text(os.path.join(root, x["path"]))),
                           "canonical": "oser " + render.WRAPPERS[kind][1]})
        elif x["path"] not in overrides:
            raise Blocked("%s is a MODIFIED copy of the 1.0 %s tool — project-owned content, not replaced. "
                          "Reconcile by hand or list it in overrides." % (x["path"], x["key"]))

    sp = os.path.join(root, SETTINGS)
    settings = load_json(sp) if os.path.isfile(sp) else {}
    if settings.get("model") and render.managed_settings(m)["model"] is None:
        record.append({"action": "unpin-root-model", "path": SETTINGS, "was": settings["model"],
                       "why": "models.root=inherit — client session model is authoritative"})

    if mode_spec(m)["subagents"] == "forbidden":
        for f in sorted(glob.glob(os.path.join(root, ".claude", "agents", "*.md"))):
            r = rel(root, f)
            dst = INACTIVE_DIR + "/agents/" + os.path.basename(f)
            if plan.move(r, dst, "mode %s forbids subagents — definition kept, not registered" % m["mode"]):
                record.append({"action": "inactivate", "path": r, "to": dst})
    for r in ((m.get("control_plane") or {}).get("inactivate") or []):
        dst = INACTIVE_DIR + "/" + os.path.basename(r)
        if plan.move(r, dst, "declared inactive in manifest"):
            record.append({"action": "inactivate", "path": r, "to": dst})
    for mv in ((m.get("migrate") or {}).get("moves") or []):
        if plan.move(mv["from"], mv["to"], mv.get("why", "declared move")):
            record.append({"action": "move", "path": mv["from"], "to": mv["to"]})

    if not dry_run and record:
        lock = _load_lock(root)
        from .util import plugin_version
        lock.setdefault("migrations", []).append({"from": "nnc-ai-oser-1.0", "oser_version": plugin_version(),
                                                  "at": now_iso(), "actions": record})
        lock["retired"] = sorted(set(lock.get("retired") or []) | {r["path"] for r in record if r["action"] == "retire"})
        write_text(os.path.join(root, LOCK), dump_json(lock))
    up = update(root, dry_run=dry_run, force=force, _skip_legacy_check=True, _extra_wrappers=extra_wrappers)
    plan.actions += up.actions
    plan.notes += up.notes
    return plan


# ------------------------------------------------------------------------------------------ install

def install(root, name, authority_repo, authority_entry, authority_ref="main", authority_hint=None,
            baseline=None, phase_id="setup", phase_label="SETUP", language="vi", dry_run=False):
    mp = os.path.join(root, MANIFEST)
    if os.path.exists(mp):
        raise Blocked("%s already exists — use `oser update` (or `oser migrate` for a 1.0 project)" % MANIFEST)
    if detect_legacy(root):
        raise Blocked("NNC-AI-OSer 1.0 artifacts found — author the manifest, then run `oser migrate`")
    plan = Plan(root, dry_run)
    manifest = {
        "schema": SCHEMA_ID,
        "project": {"name": name, "language": language},
        "phase": {"id": phase_id, "label": phase_label, "summary": []},
        "mode": "setup",
        "authority": {"repo": authority_repo, "ref": authority_ref, "entry": authority_entry,
                      "local_path_hints": [authority_hint] if authority_hint else []},
        "models": {"root": "inherit"},
        "capabilities": {"audit": {"enabled": False}},
        "workspace": {"state_file": "workspace/TRANG-THAI.md", "dir": "workspace", "current": ["TRANG-THAI.md"]},
        "control_plane": {"current": ["CLAUDE.md", "workspace/TRANG-THAI.md"], "historical": [],
                          "stale_markers": []},
    }
    if baseline:
        manifest["authority"]["baseline"] = baseline
    plan.write(MANIFEST, dump_json(manifest), "project declaration (PROJECT-OWNED scaffold)")
    state = os.path.join(root, "workspace", "TRANG-THAI.md")
    if not os.path.exists(state):
        plan.write("workspace/TRANG-THAI.md", template("TRANG-THAI.md").replace("{{NAME}}", name)
                   .replace("{{PHASE_LABEL}}", phase_label), "live state (PROJECT-OWNED scaffold)")
    if dry_run:
        return plan
    up = update(root)
    plan.actions += up.actions
    plan.notes += up.notes
    return plan
