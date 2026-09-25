# -*- coding: utf-8 -*-
"""The project declaration: `.claude/oser/project.json` (PROJECT-OWNED, never rewritten by OSER)."""
import os

from .util import git, load_catalog, load_json

SCHEMA_ID = "nnc-oser/project@2"
MANIFEST = ".claude/oser/project.json"
LOCK = ".claude/oser/lock.json"
INACTIVE_DIR = ".claude/oser/inactive"


class ManifestError(Exception):
    pass


def manifest_path(root, override=None):
    return override or os.path.join(root, MANIFEST)


def load(root, override=None):
    """Return (manifest, errors). A manifest with errors is still returned when it parsed."""
    p = manifest_path(root, override)
    try:
        m = load_json(p)
    except ValueError as e:
        return None, ["%s is not valid JSON: %s" % (p, e)]
    if m is None:
        return None, ["%s not found" % p]
    return m, validate(m)


def validate(m):
    errors = []
    if m.get("schema") != SCHEMA_ID:
        errors.append("schema must be %r (found %r)" % (SCHEMA_ID, m.get("schema")))
    for path in ("project.name", "phase.id", "phase.label", "mode", "authority.repo", "authority.ref",
                 "authority.entry", "workspace.state_file"):
        if get(m, path) in (None, ""):
            errors.append("missing required field %s" % path)
    modes = load_catalog("modes.json")["modes"]
    mode = m.get("mode")
    if mode and mode not in modes:
        errors.append("unknown mode %r (known: %s)" % (mode, ", ".join(sorted(modes))))
    elif mode:
        spec = modes[mode]
        if spec["status"] != "active" and not m.get("assignments"):
            errors.append("mode %r is contract-only in this OSER version and requires 'assignments'" % mode)
    caps = load_catalog("capabilities.json")["capabilities"]
    for name in (m.get("capabilities") or {}):
        if name not in caps:
            errors.append("unknown capability %r" % name)
    root_model = get(m, "models.root") or "inherit"
    if root_model != "inherit" and not str(root_model).startswith("claude-"):
        errors.append("models.root must be 'inherit' or an explicit claude-* id")
    return errors


def get(m, dotted, default=None):
    cur = m
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def mode_spec(m):
    return load_catalog("modes.json")["modes"][m["mode"]]


def capability_state(m):
    """{capability: 'active'|'configured'|'disabled'} — configured ≠ running."""
    caps = load_catalog("capabilities.json")["capabilities"]
    spec = mode_spec(m)
    declared = m.get("capabilities") or {}
    out = {}
    for name, c in caps.items():
        enabled = declared.get(name, {}).get("enabled", c.get("default_enabled", True))
        if name in spec.get("active_capabilities", []):
            out[name] = "active"
        elif c["runs_as"] == "gate" and spec.get("audit") == "disabled":
            out[name] = "disabled"
        elif not enabled:
            out[name] = "disabled"
        elif c["runs_as"] == "external":
            out[name] = "external"
        else:
            out[name] = "configured"
    return out


def model_mapping(m):
    classes = load_catalog("capabilities.json")["model_classes"]
    declared = get(m, "models.classes") or {}
    out = {k: declared.get(k, v["default"]) for k, v in classes.items()}
    out["root"] = get(m, "models.root") or "inherit"
    return out


def resolve_authority(root, m):
    """Find a local clone of the authority repo without committing any absolute path."""
    cands = []
    env = os.environ.get("NNC_OSER_AUTHORITY_PATH")
    if env:
        cands.append(env)
    for hint in get(m, "authority.local_path_hints") or []:
        cands.append(os.path.normpath(os.path.join(root, hint)))
    for c in cands:
        if os.path.isdir(c) and git(c, "rev-parse", "--git-dir")[0] == 0:
            return c
    return None


def ref_exists(auth, ref):
    for r in ("refs/remotes/origin/" + ref, "refs/heads/" + ref):
        if git(auth, "rev-parse", "--verify", "--quiet", r)[0] == 0:
            return r
    return None
