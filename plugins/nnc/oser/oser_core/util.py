# -*- coding: utf-8 -*-
"""Small, dependency-free helpers shared by every OSER command."""
import datetime
import hashlib
import io
import json
import os
import re
import subprocess

OSER_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../plugins/nnc/oser
PLUGIN_ROOT = os.path.dirname(OSER_HOME)                                    # .../plugins/nnc


def plugin_version():
    """Single source of truth for the OSER version: the plugin manifest."""
    with io.open(os.path.join(PLUGIN_ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8-sig") as f:
        return json.load(f)["version"]


def claude_home():
    """~/.claude, overridable for hermetic tests."""
    return os.environ.get("NNC_OSER_CLAUDE_HOME") or os.path.join(os.path.expanduser("~"), ".claude")


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def norm(text):
    return text.replace("\r\n", "\n")


def read_text(path):
    if not os.path.isfile(path):
        return None
    with io.open(path, encoding="utf-8-sig", errors="replace") as f:
        return norm(f.read())


def write_text(path, text):
    """Write LF text only when the normalised content differs. Returns True when the file changed."""
    text = norm(text)
    if read_text(path) == text:
        return False
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return True


def sha(text):
    return hashlib.sha256(norm(text).encode("utf-8")).hexdigest()


def load_json(path):
    t = read_text(path)
    return None if t is None else json.loads(t)


def dump_json(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def load_catalog(name):
    with io.open(os.path.join(OSER_HOME, "catalog", name), encoding="utf-8") as f:
        return json.load(f)


def template(name):
    with io.open(os.path.join(OSER_HOME, "templates", name), encoding="utf-8") as f:
        return norm(f.read())


def git(cwd, *args):
    try:
        r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
        return r.returncode, r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return 127, ""


def rel(root, path):
    return os.path.relpath(path, root).replace("\\", "/")


def transcript_slug(path):
    """Claude Code names a project's transcript folder by replacing every non-alphanumeric char with '-'."""
    return re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(path))


MODEL_RE = re.compile(r"\bclaude-(fable|opus|sonnet|haiku)-(\d+)(?:-(\d{1,2}))?(?:-\d{8})?\b")


def model_generation(model_id):
    """'claude-opus-5-5' -> ('opus', (5, 5)); 'claude-haiku-4-5-20251001' -> ('haiku', (4, 5)); else None."""
    m = MODEL_RE.search(model_id or "")
    if not m:
        return None
    return m.group(1), (int(m.group(2)), int(m.group(3) or 0))


def glob_to_regex(pattern):
    out, i = "", 0
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**", i):
            out += ".*"
            i += 2
        elif c == "*":
            out += "[^/]*"
            i += 1
        elif c == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(c)
            i += 1
    return re.compile("^" + out + "$")


def match_any(relpath, patterns):
    for p in patterns or []:
        if p.endswith("/") and (relpath + "/").startswith(p):
            return True
        if glob_to_regex(p).match(relpath):
            return True
    return False
