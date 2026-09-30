"""Strict values, bounded artifacts and canonical project locations (stdlib only)."""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath


class OserError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def require(condition, code, message):
    if not condition:
        raise OserError(code, message)


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), "INVALID_INPUT", label + " must be a nonblank string")
    require(len(value) <= 16384, "INVALID_INPUT", label + " is too long")
    return value


def number(value, label, minimum=0, maximum=None):
    require(type(value) in (int, float) and math.isfinite(value), "INVALID_INPUT", label + " must be finite")
    require(value >= minimum and (maximum is None or value <= maximum), "INVALID_INPUT", label + " is out of range")
    return value


def integer(value, label, minimum=0):
    require(type(value) is int and value >= minimum, "INVALID_INPUT", label + " must be an integer")
    return value


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def utcnow():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def epoch(value):
    text(value, "timestamp")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(dt.tzinfo is not None, "INVALID_TIME", "timestamp needs an explicit timezone")
        return dt.timestamp()
    except (ValueError, OverflowError) as exc:
        raise OserError("INVALID_TIME", "invalid timestamp") from exc


def project_root(path):
    """Linked Git worktrees share the main project's canonical state store.

    No fetch, credential lookup, shell, global config mutation, or inference.
    Non-Git projects use the supplied directory.
    """
    root = Path(path).resolve()
    require(root.is_dir(), "PROJECT_NOT_FOUND", "project must be an existing directory")
    try:
        result = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=str(root),
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                encoding="utf-8", timeout=5, check=False)
        if result.returncode == 0:
            common = Path(result.stdout.strip())
            common = (root / common).resolve() if not common.is_absolute() else common.resolve()
            if common.name == ".git" and common.is_dir():
                return common.parent
    except (OSError, subprocess.TimeoutExpired):
        pass
    return root


def safe_path(root, relative):
    text(relative, "relative path")
    normalized = relative.replace("\\", "/")
    parts = Path(normalized).parts
    require(not Path(normalized).is_absolute() and not PureWindowsPath(relative).is_absolute()
            and ".." not in parts and ".git" not in parts,
            "UNSAFE_PATH", "path must stay inside the project, outside .git")
    target = (Path(root) / normalized).resolve()
    try:
        target.relative_to(Path(root).resolve())
    except ValueError as exc:
        raise OserError("UNSAFE_PATH", "symlink/path escapes the project") from exc
    return target


def file_hash(path, max_bytes=16 * 1024 * 1024):
    path = Path(path)
    require(path.is_file(), "ARTIFACT_MISSING", "artifact is not a regular file: " + path.name)
    require(path.stat().st_size <= max_bytes, "ARTIFACT_TOO_LARGE", "artifact exceeds the bounded reader")
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def source_fingerprint(root, sources):
    """Hash explicitly declared source inputs. No broad scanning or hidden log reads.

    Directories are supported, but .git/.nnc-oser, symlinks and oversized trees
    cannot silently become accepted evidence. Changes invalidate prior evidence.
    """
    require(isinstance(sources, list) and bool(sources), "SOURCES_REQUIRED", "declare relevant source inputs")
    result = {}
    total = 0
    for relative in sources:
        path = safe_path(root, relative)
        require(path.exists(), "SOURCE_MISSING", "source input is missing: " + relative)
        paths = sorted(path.rglob("*")) if path.is_dir() else [path]
        for item in paths:
            rel = item.relative_to(Path(root)).as_posix()
            require(not item.is_symlink(), "UNSAFE_PATH", "source inputs must not contain symlinks")
            if any(part in (".git", ".nnc-oser", "__pycache__") for part in item.relative_to(root).parts):
                continue
            if item.is_file():
                total += item.stat().st_size
                require(len(result) < 10000 and total <= 64 * 1024 * 1024,
                        "SOURCE_SCAN_LIMIT", "narrow the declared source inputs")
                result[rel] = file_hash(item)
    require(bool(result), "SOURCES_REQUIRED", "source inputs contain no files")
    return digest(result)


def load_json_file(path):
    path = Path(path)
    require(path.stat().st_size <= 2 * 1024 * 1024, "INPUT_TOO_LARGE", "JSON input exceeds 2 MiB")
    with path.open(encoding="utf-8-sig") as stream:
        return json.load(stream, parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
