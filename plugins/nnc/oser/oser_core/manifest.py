# -*- coding: utf-8 -*-
"""The project declaration: `.claude/oser/project.json` (PROJECT-OWNED; only `oser migrate` may rewrite it)."""
import os

from .util import git, load_catalog, load_json

SCHEMA_ID = "nnc-oser/project@4"
LEGACY_SCHEMAS = ("nnc-oser/project@2", "nnc-oser/project@3")
MANIFEST = ".claude/oser/project.json"
LOCK = ".claude/oser/lock.json"
LEDGER_DIR = ".claude/oser/ledger"

ADMISSION = ("not_admitted", "admitted")


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


def get(m, dotted, default=None):
    cur = m
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def legacy_keys(m):
    """Keys of the 2.0 organisational model still present (fixed model classes, capability catalog, …)."""
    found = []
    for k in load_catalog("legacy-v1.json")["v2_manifest_keys"]:
        if get(m, k) is not None:
            found.append(k)
    return found


def validate(m):
    errors = []
    if m.get("schema") in LEGACY_SCHEMAS:
        return ["schema %r is an older layout — run `oser migrate`" % m.get("schema")]
    if m.get("schema") != SCHEMA_ID:
        errors.append("schema must be %r (found %r)" % (SCHEMA_ID, m.get("schema")))
    for path in ("project.name", "phase.id", "phase.label", "mode", "authority.repo", "authority.ref",
                 "authority.entry", "workspace.state_file", "operating_model.root.model",
                 "operating_model.governor.required_family"):
        if get(m, path) in (None, ""):
            errors.append("missing required field %s" % path)
    for k in legacy_keys(m):
        errors.append("legacy 2.0 key %r present — fixed model/role configuration is retired (run `oser migrate`)" % k)
    modes = load_catalog("modes.json")["modes"]
    mode = m.get("mode")
    if mode and mode not in modes:
        errors.append("unknown mode %r (known: %s)" % (mode, ", ".join(sorted(modes))))
    elif mode == "build" and get(m, "build.admission") != "admitted":
        errors.append("mode 'build' requires build.admission = 'admitted' (BUILD ADMISSION REVIEW first)")
    elif mode == "operate":
        errors.append("mode 'operate' is contract-only in this OSER version")
    adm = get(m, "build.admission")
    if adm is not None and adm not in ADMISSION:
        errors.append("build.admission must be one of %s" % ", ".join(ADMISSION))
    if get(m, "build.effort_policy") is not None:
        errors.append("build.effort_policy is not allowed: effort is a per-packet scheduling dimension chosen from "
                      "the runtime set, never a fixed policy")
    fams = load_catalog("runtime.json")["model_families"]["values"]
    for path in ("operating_model.governor.required_family", "operating_model.root.expected_family"):
        v = get(m, path)
        if v is not None and v not in fams:
            errors.append("%s %r is not a model family (%s)" % (path, v, ", ".join(fams)))
    fb = get(m, "operating_model.governor.fallback", "none")
    if fb != "none" and not (isinstance(fb, list) and all(x in fams for x in fb)):
        errors.append("operating_model.governor.fallback must be 'none' or a list of model families")
    root_model = get(m, "operating_model.root.model")
    if root_model and root_model != "inherit" and not str(root_model).startswith("claude-"):
        errors.append("operating_model.root.model must be 'inherit' or an explicit claude-* id")
    return errors


def mode_spec(m):
    return load_catalog("modes.json")["modes"][m["mode"]]


def build_state(m):
    """'not_configured' | 'configured_not_admitted' | 'admitted' — BUILD configuration is not BUILD start."""
    if not m.get("build"):
        return "not_configured"
    return "admitted" if get(m, "build.admission") == "admitted" else "configured_not_admitted"


def governor_families(m):
    """Families allowed in the Governor slot: required_family + explicit fallback list (never implicit)."""
    fb = get(m, "operating_model.governor.fallback", "none")
    return [get(m, "operating_model.governor.required_family")] + (fb if isinstance(fb, list) else [])


def root_model(m):
    return get(m, "operating_model.root.model") or "inherit"


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
