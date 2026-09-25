# -*- coding: utf-8 -*-
"""Pure rendering: manifest + OSER version -> generated artifacts. No I/O, fully deterministic."""
import re

from .manifest import INACTIVE_DIR, LOCK, MANIFEST, capability_state, get, mode_spec, model_mapping

BLOCK = "status"
BLOCK_TEMPLATE = "claude-status@2"
BEGIN_RE = re.compile(r"<!-- NNC-OSER:BEGIN block=%s\b[^>]*-->" % BLOCK)
END_MARK = "<!-- NNC-OSER:END block=%s -->" % BLOCK

ACTOR_LABEL = {"founder": "Founder", "strategy-session": "Strategy Session", "root-investigator": "ROOT (investigator)"}


def md_header(template, version, mode):
    return ("<!-- NNC-OSER:GENERATED template=%s oser=%s mode=%s source=%s — không sửa tay; "
            "sửa project.json rồi chạy: oser update -->\n" % (template, version, mode, MANIFEST))


def claude_block(m, version):
    spec = mode_spec(m)
    caps = capability_state(m)
    models = model_mapping(m)
    a = m["authority"]
    lines = [
        "<!-- NNC-OSER:BEGIN block=%s template=%s oser=%s mode=%s — GENERATED từ %s; sửa file đó rồi chạy: oser update -->"
        % (BLOCK, BLOCK_TEMPLATE, version, m["mode"], MANIFEST),
        "## Trạng thái điều khiển (NNC OSER)",
        "",
        "| | |",
        "|---|---|",
        "| **PHASE** | **%s**%s |" % (m["phase"]["label"], (" — từ %s" % m["phase"]["since"]) if m["phase"].get("since") else ""),
    ]
    for s in m["phase"].get("summary") or []:
        lines.append("| | %s |" % s)
    lines += [
        "| **MODE** | `%s` — %s |" % (m["mode"], " · ".join(ACTOR_LABEL.get(x, x) for x in spec.get("actors", []))
                                      or spec["summary"]),
        "| Subagent | **%s** |" % {"forbidden": "CẤM — không gọi agent, không build crew",
                                   "per-assignment": "chỉ theo assignment đã khai"}.get(spec["subagents"], spec["subagents"]),
        "| Audit (Fable) | **%s** |" % {"disabled": "TẮT", "gate-only": "chỉ tại audit gate tường minh"}.get(
            spec["audit"], spec["audit"]),
        "| **AUTHORITY** | `%s` @ `%s`%s → `%s` — đọc file đó trước; không chép canon vào repo này |"
        % (a["repo"], a["ref"], (" (baseline `%s`)" % a["baseline"]) if a.get("baseline") else "", a["entry"]),
        "| ROOT model | `%s` — %s |" % (
            models["root"],
            "theo model của phiên đang mở (client chọn); repo KHÔNG ghim" if models["root"] == "inherit"
            else "ghim tường minh trong .claude/settings.json"),
        "| Capability | %s |" % " · ".join("%s=%s" % (k, v) for k, v in sorted(caps.items())),
        "| Live state | `%s` |" % m["workspace"]["state_file"],
        "| Kiểm | `oser doctor` · bản đồ sở hữu: `.claude/oser/CONTROL-PLANE.md` |",
        END_MARK,
    ]
    return "\n".join(lines) + "\n"


def splice_block(text, block):
    """Replace the existing block, or insert it right after the first H1 (top of file if none)."""
    text = text or ""
    m = BEGIN_RE.search(text)
    if m:
        end = text.find(END_MARK, m.start())
        if end < 0:
            raise ValueError("CLAUDE.md has an OSER BEGIN marker without END marker")
        end += len(END_MARK)
        if text[end:end + 1] == "\n":
            end += 1
        return text[:m.start()] + block + text[end:]
    h1 = re.search(r"^# .*\n", text, re.M)
    if h1:
        return text[:h1.end()] + "\n" + block + "\n" + text[h1.end():].lstrip("\n")
    return block + "\n" + text


def extract_block(text):
    m = BEGIN_RE.search(text or "")
    if not m:
        return None
    end = text.find(END_MARK, m.start())
    return None if end < 0 else text[m.start():end + len(END_MARK)] + "\n"


def control_plane_doc(m, version, generated_paths):
    spec = mode_spec(m)
    caps = capability_state(m)
    models = model_mapping(m)
    cp = m.get("control_plane") or {}
    out = [md_header("control-plane@2", version, m["mode"]),
           "# Control plane — %s" % m["project"]["name"], "",
           "Một chủ cho mỗi mối quan tâm. Bảng này sinh từ `%s`; lịch sử nằm trong git." % MANIFEST, "",
           "## Mode `%s` (%s)" % (m["mode"], spec["status"]), "", spec["summary"], "",
           "| Capability | Trạng thái | Model class | Model mapping |", "|---|---|---|---|"]
    from .util import load_catalog
    catalog = load_catalog("capabilities.json")["capabilities"]
    for name in sorted(caps):
        mc = catalog[name]["model_class"]
        out.append("| `%s` | %s | `%s` | `%s` |" % (name, caps[name], mc, models.get(mc, "?")))
    out += ["", "`configured` = đã khai, **không chạy**. Chỉ `active` mới được dùng trong mode này.", "",
            "## Ai sở hữu file nào", "", "| Lớp | Đường dẫn | Luật |", "|---|---|---|"]
    rows = [("PROJECT-OWNED", MANIFEST, "khai báo hiệu lực của dự án; OSER không bao giờ ghi đè")]
    for p in cp.get("current") or []:
        rows.append(("PROJECT-OWNED", p, "sự thật hiện hành do dự án viết"))
    for p in cp.get("project_tools") or []:
        rows.append(("PROJECT-OWNED", p, "công cụ riêng dự án, giữ tại chỗ"))
    for p in sorted(generated_paths):
        if "#" in p:
            rows.append(("PLUGIN-GENERATED", p, "chỉ phần giữa `NNC-OSER:BEGIN` … `END`; ngoài khối là PROJECT-OWNED"))
        else:
            rows.append(("PLUGIN-GENERATED", p, "sinh bởi `oser update`; sửa tay = drift"))
    rows.append(("PLUGIN-GENERATED", ".claude/settings.json#managed",
                 "chỉ key `model` (bỏ khi ROOT=inherit) và giá trị `permissions.deny` của mode; key khác là PROJECT-OWNED"))
    rows.append(("PLUGIN-GENERATED", LOCK, "provenance: version · mode · template · sha256"))
    for p in m.get("overrides") or []:
        rows.append(("PROJECT-OVERRIDE", p, "dự án tự giữ; `oser update` bỏ qua"))
    rows.append(("INACTIVE", INACTIVE_DIR + "/", "định nghĩa đã khai nhưng không chạy trong mode này"))
    for p in cp.get("historical") or []:
        rows.append(("HISTORICAL", p, "bằng chứng; không đọc để quyết việc hiện hành"))
    for cls, p, rule in rows:
        out.append("| %s | `%s` | %s |" % (cls, p, rule))
    out += ["", "## Lệnh", "", "```bash",
            "oser doctor   # drift: authority · phase · model EXPECTED/CONFIGURED/OBSERVED · provenance · target",
            "oser update   # sinh lại phần GENERATED từ project.json (idempotent)",
            "oser status   # mode · capability · model", "oser quota --ngay 7", "```", ""]
    return "\n".join(out)


def inactive_readme(m, version):
    return "\n".join([
        md_header("inactive-readme@2", version, m["mode"]),
        "# INACTIVE — không chạy trong mode `%s`" % m["mode"], "",
        "Thư mục này giữ nguyên byte các định nghĩa agent/đội thời trước (ví dụ ghế build crew) để làm",
        "**bằng chứng thiết kế** cho mode BUILD sau này. Claude Code **không** nạp agent từ đây.", "",
        "- Không gọi, không sửa để \"bật lại\" từng ghế.",
        "- Mở BUILD = dự án khai `mode` + `assignments` trong `%s` sau khi kiến trúc kỹ thuật chốt, rồi `oser update`." % MANIFEST,
        "- Con trỏ authority/model bên trong các file này là của thời đó — có thể đã chết.", ""])


WRAPPER = r'''# -*- coding: utf-8 -*-
# NNC-OSER:GENERATED template=%(template)s oser=%(version)s mode=%(mode)s source=.claude/oser/project.json
# Compatibility wrapper. Canonical implementation: `oser %(command)s` in the nnc plugin
# (nnc-claude-plugins/plugins/nnc/oser/oser.py). Do not edit by hand — run `oser update`.
import glob, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, %(up)r))


def _ver(p):
    try:
        return tuple(int(x) for x in os.path.basename(os.path.dirname(os.path.dirname(p))).split("."))
    except ValueError:
        return (0,)


def find_oser():
    env = os.environ.get("NNC_OSER_HOME")
    if env and os.path.isfile(os.path.join(env, "oser.py")):
        return os.path.join(env, "oser.py")
    home = os.environ.get("NNC_OSER_CLAUDE_HOME") or os.path.join(os.path.expanduser("~"), ".claude")
    cached = sorted(glob.glob(os.path.join(home, "plugins", "cache", "*", "nnc", "*", "oser", "oser.py")), key=_ver)
    if cached:
        return cached[-1]
    for p in (os.path.join(home, "plugins", "marketplaces", "nnc-claude-plugins", "plugins", "nnc", "oser", "oser.py"),
              os.path.join(os.path.dirname(ROOT), "nnc-claude-plugins", "plugins", "nnc", "oser", "oser.py")):
        if os.path.isfile(p):
            return p
    return None


def main():
%(body)s


if __name__ == "__main__":
    sys.exit(main())
'''

BODY_QUOTA = '''    oser = find_oser()
    if not oser:
        print("NNC OSER not found. Install: /plugin install nnc@nnc-claude-plugins (or set NNC_OSER_HOME).")
        return 3
    return subprocess.call([sys.executable, oser, "quota", "--project", ROOT] + sys.argv[1:])'''

BODY_DOI_BAC = '''    if len(sys.argv) > 1:
        print("RETIRED (NNC OSER 2): model-name profiles (fable|opus|sonnet) no longer drive the team.")
        print("  Change mode / capability / model class in .claude/oser/project.json, then run: oser update")
        print("  ROOT model follows the active session; see: oser status")
        return 2
    oser = find_oser()
    if not oser:
        print("NNC OSER not found. Install: /plugin install nnc@nnc-claude-plugins (or set NNC_OSER_HOME).")
        return 3
    return subprocess.call([sys.executable, oser, "status", "--project", ROOT])'''

WRAPPERS = {
    "quota": ("wrapper-quota@2", "quota", BODY_QUOTA),
    "doi-bac": ("wrapper-doi-bac@2", "status", BODY_DOI_BAC),
}


def wrapper(kind, relpath, m, version):
    template, command, body = WRAPPERS[kind]
    depth = relpath.count("/")
    return WRAPPER % {"template": template, "version": version, "mode": m["mode"], "command": command,
                      "up": "/".join([".."] * depth) or ".", "body": body}


def managed_settings(m):
    """Keys of .claude/settings.json that OSER owns for this mode: {'model': id|None, 'deny': [...]}."""
    root = model_mapping(m)["root"]
    deny = list(mode_spec(m).get("settings", {}).get("permissions.deny", []))
    return {"model": None if root == "inherit" else root, "deny": deny}


def apply_settings(settings, managed, previously_managed_deny):
    """Merge managed keys into a settings dict without touching project-owned keys."""
    s = dict(settings or {})
    if managed["model"] is None:
        s.pop("model", None)
    else:
        s["model"] = managed["model"]
    perms = dict(s.get("permissions") or {})
    deny = [d for d in perms.get("deny", []) if d not in previously_managed_deny or d in managed["deny"]]
    for d in managed["deny"]:
        if d not in deny:
            deny.append(d)
    if deny:
        perms["deny"] = deny
    else:
        perms.pop("deny", None)
    if perms:
        s["permissions"] = perms
    else:
        s.pop("permissions", None)
    return s


def get_block_phase(block):
    m = re.search(r"\| \*\*PHASE\*\* \| \*\*(.+?)\*\*", block or "")
    return m.group(1) if m else None


__all__ = ["claude_block", "splice_block", "extract_block", "control_plane_doc", "inactive_readme", "wrapper",
           "managed_settings", "apply_settings", "get_block_phase", "get", "BEGIN_RE", "END_MARK"]
