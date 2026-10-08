"""Clean Desk manifest validation: authority, drafts, evidence and history stay distinct."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from .common import file_hash, require, safe_path, text

CLASSES = ("authority", "state", "drafts", "evidence", "history")


def _items(value, key):
    items = value.get(key, [])
    require(isinstance(items, list), "INVALID_DESK", key + " must be a list")
    return items


def validate_desk(project, value):
    require(isinstance(value, dict), "INVALID_DESK", "desk manifest must be an object")
    root = Path(project).resolve()
    result = {"schema": "nnc-oser/desk@1"}
    seen_paths = {}
    active_scopes = {}

    for key in CLASSES:
        out = []
        for raw in _items(value, key):
            require(isinstance(raw, dict), "INVALID_DESK", key + " entry must be an object")
            entry = deepcopy(raw)
            eid = text(entry.get("id"), key + ".id")
            path = text(entry.get("path"), key + ".path")
            require(path not in seen_paths, "DESK_CLASS_CONFLICT",
                    "%s appears in both %s and %s" % (path, seen_paths.get(path), key))
            seen_paths[path] = key
            file_path = safe_path(root, path)
            require(file_path.is_file(), "DESK_FILE_MISSING", "desk file missing: " + path)
            entry["sha256"] = file_hash(file_path)
            if key == "authority":
                scope = text(entry.get("scope"), "authority.scope")
                locked = entry.get("locked", True)
                require(type(locked) is bool, "INVALID_DESK", "authority.locked must be boolean")
                entry["locked"] = locked
                if locked:
                    require(scope not in active_scopes, "AUTHORITY_CONFLICT",
                            "two locked current authorities claim scope %s: %s and %s" %
                            (scope, active_scopes.get(scope), eid))
                    active_scopes[scope] = eid
            out.append(entry)
        result[key] = out

    require(bool(result["authority"]), "AUTHORITY_REQUIRED", "Clean Desk needs explicit current authority")
    return result


def desk_view(value):
    return {
        "authority": [{"id": x["id"], "scope": x["scope"], "path": x["path"], "locked": x["locked"]}
                      for x in value["authority"]],
        "state": [x["path"] for x in value["state"]],
        "drafts": [x["path"] for x in value["drafts"]],
        "evidence": [x["path"] for x in value["evidence"]],
        "history": [x["path"] for x in value["history"]],
        "load_policy": {
            "default": ["authority", "state"],
            "on_demand": ["drafts", "evidence"],
            "audit_only": ["history"],
        },
    }
