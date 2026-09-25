# -*- coding: utf-8 -*-
"""Pure rendering: manifest + OSER version -> generated artifacts. No I/O, fully deterministic."""
import re

from .manifest import LEDGER_DIR, LOCK, MANIFEST, build_state, get, mode_spec, root_model
from .util import load_catalog

BLOCK = "status"
BLOCK_TEMPLATE = "claude-status@3"
BEGIN_RE = re.compile(r"<!-- NNC-OSER:BEGIN block=%s\b[^>]*-->" % BLOCK)
END_MARK = "<!-- NNC-OSER:END block=%s -->" % BLOCK

ROLE_LABEL = {"founder": "Founder", "strategy-session": "Strategy Session", "root": "Root",
              "governor": "Governor (1 phiên/wave)", "worker": "Worker (theo packet)", "verifier": "Verifier độc lập"}
BUILD_LABEL = {"not_configured": "chưa cấu hình", "configured_not_admitted": "đã cấu hình · **CHƯA ADMIT — không chạy**",
               "admitted": "ADMITTED"}


def md_header(template, version, mode):
    return ("<!-- NNC-OSER:GENERATED template=%s oser=%s mode=%s source=%s — không sửa tay; "
            "sửa project.json rồi chạy: oser update -->\n" % (template, version, mode, MANIFEST))


def _governor(m):
    g = get(m, "operating_model.governor") or {}
    pref = g.get("preferred_model") or "chưa khai"
    return "%s — mỗi wave một phiên mới, đóng khi trả kết quả sạch" % pref


def claude_block(m, version):
    spec = mode_spec(m)
    a = m["authority"]
    rm = root_model(m)
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
        "| **MODE** | `%s` — %s |" % (m["mode"], " · ".join(ROLE_LABEL.get(x, x) for x in spec.get("active_roles", [])) or spec["summary"]),
        "| Subagent | **%s** |" % {"forbidden": "CẤM — không governor, không worker",
                                   "per-packet": "theo execution plan của từng packet"}.get(spec["subagents"], spec["subagents"]),
        "| **BUILD** | %s |" % BUILD_LABEL[build_state(m)],
        "| **AUTHORITY** | `%s` @ `%s`%s → `%s` — đọc file đó trước; không chép canon vào repo này |"
        % (a["repo"], a["ref"], (" (baseline `%s`)" % a["baseline"]) if a.get("baseline") else "", a["entry"]),
        "| Root | `%s` — %s |" % (rm, "model của phiên đang mở (client chọn); repo KHÔNG ghim" if rm == "inherit"
                               else "ghim tường minh trong .claude/settings.json"),
        "| Governor | %s |" % _governor(m),
        "| Worker/Verifier | model × effort × context × session × song song × verification **chọn theo từng packet**; không map model cố định theo vai |",
        "| Live state | `%s` · ledger `%s/` |" % (m["workspace"]["state_file"], LEDGER_DIR),
        "| Kiểm | `oser doctor` · `oser metrics` · bản đồ: `.claude/oser/CONTROL-PLANE.md` |",
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
    om = load_catalog("operating-model.json")
    cp = m.get("control_plane") or {}
    out = [md_header("control-plane@3", version, m["mode"]),
           "# Control plane — %s" % m["project"]["name"], "",
           "Một chủ cho mỗi mối quan tâm. Bảng này sinh từ `%s`; lịch sử nằm trong git." % MANIFEST, "",
           "## Mode `%s` (%s) · BUILD: %s" % (m["mode"], spec["status"], BUILD_LABEL[build_state(m)].replace("*", "")), "",
           spec["summary"], "",
           "## Mô hình vận hành", "",
           "Founder + Strategy → **Root** (điều khiển toàn cục, admit wave, tích hợp kết quả sạch) → **Governor** (một phiên",
           "mới cho mỗi wave: chia packet, chọn execution plan, yêu cầu verification, gom bằng chứng) → **phiên thực thi",
           "mới** → **verification độc lập** → kết quả wave sạch → Root. Chỉ `ROOT_ACCEPTED` đẩy milestone.", "",
           "| Vai | Sở hữu | Không được |", "|---|---|---|"]
    for name, r in om["roles"].items():
        out.append("| %s | %s | %s |" % (ROLE_LABEL.get(name, name), "; ".join(r.get("owns", [])), "; ".join(r.get("must_not", [])) or "—"))
    out += ["", "Đơn vị lập lịch: **work packet**. Mỗi lượt thử mang execution plan riêng: model × effort × context"
            " (must read / may read / must not load / output budget) × session (same/fresh/parallel/independent) ×"
            " verifier × escalation. Mục tiêu: kế hoạch **verified** tốn ít tài nguyên nhất mà vẫn giữ biên an toàn.", "",
            "Packet: %s. Wave: %s." % (" → ".join(om["packet_states"][:-1]) + " (| REJECTED)",
                                       " → ".join(om["wave_states"][:-1]) + " | ROOT_REJECTED"), "",
            "## Ai sở hữu file nào", "", "| Lớp | Đường dẫn | Luật |", "|---|---|---|"]
    rows = [("PROJECT-OWNED", MANIFEST, "khai báo hiệu lực của dự án; chỉ `oser migrate` được đổi schema"),
            ("PROJECT-OWNED", LEDGER_DIR + "/", "ledger wave/packet — chỉ ghi thêm, qua `oser ledger add`")]
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
                 "chỉ key `model` (bỏ khi Root=inherit) và giá trị `permissions.deny` của mode; key khác là PROJECT-OWNED"))
    rows.append(("PLUGIN-GENERATED", LOCK, "provenance: version · mode · template · sha256"))
    for p in m.get("overrides") or []:
        rows.append(("PROJECT-OVERRIDE", p, "dự án tự giữ; `oser update` bỏ qua"))
    for p in cp.get("historical") or []:
        rows.append(("HISTORICAL", p, "bằng chứng; không đọc để quyết việc hiện hành"))
    for cls, p, rule in rows:
        out.append("| %s | `%s` | %s |" % (cls, p, rule))
    out += ["", "## Lệnh", "", "```bash",
            "oser doctor            # drift: authority · phase · model EXPECTED/CONFIGURED/OBSERVED · ledger · legacy",
            "oser update            # sinh lại phần GENERATED từ project.json (idempotent)",
            "oser ledger add F.json # ghi một sự kiện wave/packet/attempt (kiểm schema + lifecycle)",
            "oser metrics           # verified-result cost · first-pass · rework · Root growth · isolation · defects · Fable leverage",
            "oser quota --ngay 7    # usage thô: model · effort · tuần (tất cả model / Fable)", "```", ""]
    return "\n".join(out)


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
    oser = find_oser()
    if not oser:
        print("NNC OSER not found. Install: /plugin install nnc@nnc-claude-plugins (or set NNC_OSER_HOME).")
        return 3
    return subprocess.call([sys.executable, oser, %(command)r, "--project", ROOT] + sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
'''

WRAPPERS = {"quota": ("wrapper-quota@3", "quota")}


def wrapper(kind, relpath, m, version):
    template, command = WRAPPERS[kind]
    depth = relpath.count("/")
    return WRAPPER % {"template": template, "version": version, "mode": m["mode"], "command": command,
                      "up": "/".join([".."] * depth) or "."}


def managed_settings(m):
    """Keys of .claude/settings.json that OSER owns for this mode: {'model': id|None, 'deny': [...]}."""
    rm = root_model(m)
    deny = list(mode_spec(m).get("settings", {}).get("permissions.deny", []))
    return {"model": None if rm == "inherit" else rm, "deny": deny}


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
