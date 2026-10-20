#!/usr/bin/env python3
"""Lop hoc NNC - kiem buoi hoc (v0.9 part B).

Doc mot ban ghi buoi hoc (Claude Code JSONL) va viet bao cao Markdown tieng Viet
cham theo cac luat v0.8: tuong tac va hinh tu phut dau, it hop cau hoi goc,
moi luot thay chi ghi so lop mot lan, ghi `book` khi dong vong viec, khong ro ri.

Chi dung thu vien chuan. Xac dinh (khong goi mo hinh, khong dung mang).

Cach dung:
    python tools/kiem-buoi-hoc.py [SESSION.jsonl | THU_MUC_LOP | THU_MUC_PROJECTS] [--out BAO-CAO.md]

- Khong doi so: dung thu muc hien tai la thu muc lop.
- Thu muc lop: tim file *.jsonl moi nhat trong
  %USERPROFILE%\\.claude\\projects\\<slug>\\ voi slug = duong dan tuyet doi,
  moi ky tu khong phai chu/so doi thanh '-'.
- Thu muc da chua san *.jsonl (thu muc projects): lay file moi nhat trong do.

Ma thoat: 0 khi da viet bao cao (ke ca khi co dong hong); 2 khi khong tim thay buoi hoc.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

LONG_WAIT_S = 90  # nguong "Hop cho lau" cua v0.8
FIRST_TURNS = 2  # hinh dau va tuong tac dau phai den trong 2 luot thay dau

# ---------------------------------------------------------------------------
# Tim file buoi hoc
# ---------------------------------------------------------------------------


def session_slug(folder: str | os.PathLike) -> str:
    """Slug cua thu muc lop trong ~/.claude/projects: moi ky tu khong phai chu/so -> '-'."""
    return re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(str(folder)))


def projects_root() -> Path:
    home = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    return Path(home) / ".claude" / "projects"


def newest_jsonl(folder: Path) -> Path | None:
    files = [p for p in folder.glob("*.jsonl") if p.is_file()]
    if not files:
        return None
    return max(files, key=lambda p: (p.stat().st_mtime, p.name))


def projects_dir_for(folder: str | os.PathLike) -> Path:
    """Thu muc projects tuong ung voi thu muc lop (so khop khong phan biet hoa thuong neu can)."""
    root = projects_root()
    slug = session_slug(folder)
    exact = root / slug
    if exact.is_dir() or not root.is_dir():
        return exact
    low = slug.lower()
    for child in root.iterdir():
        if child.is_dir() and child.name.lower() == low:
            return child
    return exact


def resolve_session(target: str | None) -> tuple[Path | None, str]:
    """Tra ve (file jsonl, ghi chu). Khong tim thay thi (None, ly do)."""
    target = target or os.getcwd()
    p = Path(target)
    if p.is_file():
        return p, "file"
    if not p.exists():
        return None, f"Khong thay duong dan: {target}"
    if p.is_dir():
        direct = newest_jsonl(p)
        if direct is not None:
            return direct, "thu muc co san *.jsonl"
        pd = projects_dir_for(p)
        if pd.is_dir():
            found = newest_jsonl(pd)
            if found is not None:
                return found, f"thu muc lop -> {pd}"
        return None, f"Khong co file *.jsonl nao cho thu muc lop nay (da tim o {pd})"
    return None, f"Khong doc duoc: {target}"


# ---------------------------------------------------------------------------
# Doc JSONL
# ---------------------------------------------------------------------------


def parse_ts(value) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    s = value.strip()
    if s.endswith("Z") or s.endswith("z"):
        s = s[:-1] + "+00:00"
    try:
        d = datetime.fromisoformat(s)
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)


def load_rows(path: Path) -> tuple[list[dict], int]:
    rows: list[dict] = []
    bad = 0
    raw = Path(path).read_bytes().decode("utf-8-sig", errors="replace")
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except (ValueError, RecursionError):
            bad += 1
            continue
        if isinstance(obj, dict):
            rows.append(obj)
        else:
            bad += 1
    return rows, bad


# ---------------------------------------------------------------------------
# Phan loai tin nhan
# ---------------------------------------------------------------------------

NOISE_PREFIXES = (
    "<local-command",
    "<command-name>",
    "<command-message>",
    "<command-args>",
    "<system-reminder>",
    "<task-notification",
    "<bash-",
    "Base directory for this skill",
    "[Request interrupted",
    "Caveat:",
)
MARK_RE = re.compile(r"\[(Giáo án|Lớp học)\][^\n]*")
CHOOSE_RE = re.compile(r"\[Lớp học\]\s*(Chọn|Trả lời)\b")
CLOSE_RE = re.compile(r"Chốt vòng", re.I)


def blocks_of(message) -> list[dict]:
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return [b for b in content if isinstance(b, dict)]
    return []


def classify_text(text: str) -> tuple[str, str]:
    """-> (loai, nhan). loai: noise | cue | action | plain."""
    t = (text or "").strip()
    if not t:
        return "noise", ""
    if t.startswith(NOISE_PREFIXES):
        return "noise", ""
    m = MARK_RE.search(t)
    if m:
        kind = "cue" if m.group(1) == "Giáo án" else "action"
        return kind, m.group(0).strip()
    return "plain", t


def result_text(block: dict) -> str:
    c = block.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return " ".join(str(x.get("text", "")) for x in c if isinstance(x, dict))
    return ""


# ---------------------------------------------------------------------------
# Nhan dien ghi so lop
# ---------------------------------------------------------------------------

SEG_RE = re.compile(r'"segment"\s*:\s*\{(?P<body>[^{}]*)\}', re.S)
SEG_ID_RE = re.compile(r'"id"\s*:\s*"?([^",}\s]+)"?')
SEG_TITLE_RE = re.compile(r'"title"\s*:\s*"((?:[^"\\]|\\.)*)"')
BOARD_RE = re.compile(r'"board"\s*:\s*\{\s*[^\s}]')
POINT_RE = re.compile(r'"point"\s*:\s*"[^"]+"')
CHOICES_RE = re.compile(r'"choices"\s*:\s*[\{\[]\s*[^\s\]}]')
ONE_TOUCH_RE = re.compile(r'"one_touch"\s*:\s*\{(?P<body>.*?)\}', re.S)
ONE_TOUCH_TEXT_RE = re.compile(r'"text"\s*:\s*("(?:[^"\\]|\\.)*")', re.S)
BOOK_RE = re.compile(r'"book"\s*:\s*\{(?P<body>[^{}]*)\}', re.S)
BOOK_KEY_RE = re.compile(r'"[^"]+"\s*:')
BOOK_COMPLETE_RE = re.compile(r'"book_complete"\s*:\s*"[^"]+"')
OUTCOME_RE = re.compile(r'"outcome"\s*:\s*"([A-Za-z_]+)"')
PAUSED_RE = re.compile(r'"status"\s*:\s*"paused"')
DEFAULT_RE = re.compile(r'"default"\s*:\s*(?!null\b)[^\s,}\]]')

# v0.11: thang im lang (R9), do dai tin thay (R10), cuoi vong viec (R11)
SILENCE_CUE_RE = re.compile(r"Học viên im lặng\s*·\s*nấc\s*(\d)", re.I)
WAITING_RE = re.compile(r"đang đợi|đợi bạn", re.I)
MEDIAN_WORDS_MAX = 45
LONG_MSG_WORDS = 120
# Cau hoi mo o cuoi vong (heuristic): "lam gi tiep", "muon lam gi"...
OPEN_NEXT_RE = re.compile(
    r"làm gì (tiếp|nữa|bây giờ)|muốn làm gì|muốn (học|làm) (gì|tiếp)|bạn (làm|học) gì|"
    r"tiếp (theo )?(mình|ta) (làm|học) gì",
    re.I,
)
# De xuat cu the cho vong ke tiep (heuristic): thay tu de xuat va dat mac dinh.
PROPOSAL_RE = re.compile(
    r"vòng (tiếp|sau|kế)|đề xuất|mặc định|nếu bạn không (chọn|nói)|mình (sẽ )?(làm|học|đi|sang) tiếp|"
    r"mình sẽ (làm|học|sang|đi)|sang (vòng|mục|phần) ",
    re.I,
)


def count_words(text: str) -> int:
    return len(re.findall(r"\S+", text or ""))


def write_text(inp: dict) -> str:
    """Van ban moi duoc ghi (Write.content, Edit.new_string, MultiEdit.edits[].new_string)."""
    parts: list[str] = []
    for key in ("content", "new_string"):
        v = inp.get(key)
        if isinstance(v, str):
            parts.append(v)
    edits = inp.get("edits")
    if isinstance(edits, list):
        for e in edits:
            if isinstance(e, dict) and isinstance(e.get("new_string"), str):
                parts.append(e["new_string"])
    return "\n".join(parts)


def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


# ---------------------------------------------------------------------------
# Ro ri
# ---------------------------------------------------------------------------

LEAK_PATTERNS = [
    ("câu tiếng Anh có sẵn", re.compile(r"No response requested|Nothing is pending", re.I)),
    ("từ nội bộ state.json", re.compile(r"state\.json", re.I)),
    ("từ nội bộ trainer.json", re.compile(r"trainer\.json", re.I)),
    ("từ nội bộ .lop-hoc", re.compile(r"\.lop-hoc", re.I)),
    ("từ nội bộ hook", re.compile(r"\bhooks?\b", re.I)),
    ("từ nội bộ prompt", re.compile(r"\bprompts?\b", re.I)),
    ("lộ cue [Giáo án]", re.compile(r"\[Giáo án\]")),
]


def scan_leaks(text: str) -> list[tuple[str, str]]:
    out = []
    for label, rx in LEAK_PATTERNS:
        for m in rx.finditer(text or ""):
            start = max(0, m.start() - 25)
            snippet = re.sub(r"\s+", " ", text[start : start + 80]).strip()
            out.append((label, snippet))
    return out


# ---------------------------------------------------------------------------
# v0.12: R12 - giong thay va khung (tu xung "toi", cau tieng Anh, tu noi bo trong tin chu cua thay)
# ---------------------------------------------------------------------------

CODE_SPAN_RE = re.compile(r"```.*?```|`[^`\n]*`", re.S)
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)
FILE_NAME_RE = re.compile(
    r"[\w\-./\\]+\.(?:md|json|jsonl|txt|py|ps1|js|html?|css|csv|xlsx?|docx?|pptx?|pdf|png|jpe?g|zip|ya?ml)\b", re.I)
# Trich dan trong ngoac kep la loi nguoi khac (hoc vien, nhan nut), khong phai thay tu xung.
QUOTED_RE = re.compile(r'"[^"\n]*"|“[^”\n]*”|«[^»\n]*»')
SELF_REF_RE = re.compile(r"(?<!\w)[Tt]ôi(?!\w)")
LATIN_WORD_RE = re.compile(r"^[A-Za-z][A-Za-z'’\-]*$")
ENGLISH_RUN_MIN = 5
INTERNAL_WORDS_RE = re.compile(
    r"state\.json|\.lop-hoc|\bhooks?\b|\bprompts?\b|\bcues?\b|\bschema\b|\btokens?\b", re.I)


def _snip(text: str, start: int) -> str:
    return re.sub(r"\s+", " ", text[max(0, start - 20): start + 60]).strip()


def scan_voice(text: str) -> list[tuple[str, str]]:
    """-> [(loai, doan trich)]: tu xung "toi", cau tieng Anh (>= 5 tu Latin lien tiep khong dau), tu noi bo."""
    out: list[tuple[str, str]] = []
    text = text or ""
    # tu noi bo: xet ca trong dau backtick (hoc vien van thay)
    for m in INTERNAL_WORDS_RE.finditer(text):
        out.append(("từ nội bộ", _snip(text, m.start())))
    plain = FILE_NAME_RE.sub(" ", URL_RE.sub(" ", CODE_SPAN_RE.sub(" ", text)))
    plain = QUOTED_RE.sub(" ", plain)
    # Dong trich dan markdown ("> ...") la loi cua hoc vien (vi du loi giao viec 4 y viet theo giong hoc vien), bo qua.
    plain = "\n".join(line for line in plain.splitlines() if not line.lstrip().startswith(">"))
    for m in SELF_REF_RE.finditer(plain):
        out.append(('tự xưng "tôi"', _snip(plain, m.start())))
    # cau tieng Anh: chuoi tu Latin lien tiep khong dau tieng Viet, khong chu so
    run: list[str] = []

    def flush():
        if len(run) >= ENGLISH_RUN_MIN:
            lower = sum(1 for w in run if w[0].islower())
            if lower >= 3:  # bo qua danh sach ten rieng (Word, Excel, Zalo...)
                out.append(("câu tiếng Anh", " ".join(run)[:80]))
        run.clear()

    for tok in plain.split():
        core = tok.strip(".,;:!?()[]{}*_—–-·…\"'")
        if core and LATIN_WORD_RE.match(core) and (len(core) > 1 or core in ("a", "A", "I")):
            run.append(core)
        else:
            flush()
    flush()
    return out


# Hộp được miễn khỏi luật R4: đồng ý / an toàn và phiếu giao việc (xét tiêu đề + câu hỏi,
# không xét lựa chọn). Hộp kiểm bài (Đúng hay sai, Câu n, Thẻ n) không bao giờ được miễn.
EXEMPT_RE = re.compile(
    r"cho phép|xin phép|đồng ý|xác nhận|an toàn|bảo mật|giao việc|4 ý|biểu mẫu|phiếu giao",
    re.I,
)
QUIZ_HEADER_RE = re.compile(r"^\s*(câu|thẻ|quiz)\b", re.I)
QUIZ_QUESTION_RE = re.compile(r"^\s*(đúng hay sai|đúng\s*/\s*sai)", re.I)


def is_exempt_box(questions: list) -> bool:
    texts = []
    for q in questions:
        if not isinstance(q, dict):
            continue
        h = q.get("header") if isinstance(q.get("header"), str) else ""
        t = q.get("question") if isinstance(q.get("question"), str) else ""
        if QUIZ_HEADER_RE.search(h) or QUIZ_QUESTION_RE.search(t):
            return False
        texts.append(h + " " + t)
    return bool(EXEMPT_RE.search(" ".join(texts)))


# ---------------------------------------------------------------------------
# Phan tich
# ---------------------------------------------------------------------------


class Part:
    def __init__(self, pid: str, title: str = ""):
        self.id = pid
        self.title = title
        self.first_ts: datetime | None = None
        self.turns = 0
        self.visuals = 0
        self.inters = 0
        self.boxes = 0
        self.boxes_counted = 0
        self.writes = 0


def analyze(rows: list[dict], bad_lines: int = 0) -> dict:
    parts: dict[str, Part] = {}
    order: list[str] = []
    cur_part = "0"
    events: list[dict] = []  # {kind: visual|inter, sub, ts, turn, part}
    boxes: list[dict] = []
    pending: dict[str, dict] = {}
    leaks: list[dict] = []
    cues: list[str] = []
    actions: list[str] = []
    one_touch_offers: list[str] = []
    one_touch_sent = 0
    writes_total = 0
    writes_by_file: dict[str, int] = {}
    book_written = False
    book_complete = False
    loop_closed = False
    teacher_text_blocks = 0
    voice: list[dict] = []
    thinking_blocks = 0
    all_ts: list[datetime] = []
    first_cue_ts: datetime | None = None
    turns_done = 0
    in_turn = False
    turn_parts: set[str] = set()
    seen_uuid: set[str] = set()
    widgets = 0
    widget_buttons = 0
    artifacts = 0
    state_visual_writes = 0
    choices_writes = 0
    turn_info: dict[int, dict] = {}
    silence_cues: list[dict] = []
    loop_end_turns: set[int] = set()
    last_outcome = None

    def ti(n: int) -> dict:
        if n not in turn_info:
            turn_info[n] = {"texts": [], "visual": False, "choices": False, "choices_default": False,
                            "one_touch": False, "pause": False}
        return turn_info[n]

    def ensure(pid: str, title: str = "", ts: datetime | None = None) -> Part:
        if pid not in parts:
            parts[pid] = Part(pid, title)
            order.append(pid)
        p = parts[pid]
        if title and not p.title:
            p.title = title
        if ts and p.first_ts is None:
            p.first_ts = ts
        return p

    def add(kind: str, sub: str, ts, turn: int):
        events.append({"kind": kind, "sub": sub, "ts": ts, "turn": turn, "part": cur_part})
        if kind == "visual":
            ti(turn)["visual"] = True
        p = ensure(cur_part, ts=ts)
        if kind == "visual":
            p.visuals += 1
        else:
            p.inters += 1

    for row in rows:
        ts = parse_ts(row.get("timestamp"))
        if ts:
            all_ts.append(ts)
        rtype = row.get("type")
        if rtype not in ("user", "assistant"):
            continue
        if row.get("isSidechain") is True:
            continue
        uid = row.get("uuid")
        if isinstance(uid, str):
            if uid in seen_uuid:
                continue
            seen_uuid.add(uid)
        msg = row.get("message")
        blocks = blocks_of(msg)

        if rtype == "user":
            if row.get("isMeta") is True:
                continue
            for b in blocks:
                bt = b.get("type")
                if bt == "tool_result":
                    tid = b.get("tool_use_id")
                    box = pending.pop(tid, None) if isinstance(tid, str) else None
                    if box is not None:
                        txt = result_text(b)
                        box["interrupted"] = bool(b.get("is_error")) and "interrupted" in txt.lower()
                        if ts and box["ts"]:
                            box["wait"] = max(0.0, (ts - box["ts"]).total_seconds())
                    continue
                if bt != "text":
                    continue
                text = b.get("text") if isinstance(b.get("text"), str) else ""
                kind, label = classify_text(text)
                if kind == "noise":
                    continue
                in_turn = False  # moi tin nhan that mo ra mot luot thay moi
                if kind == "cue":
                    cues.append(label)
                    sm = SILENCE_CUE_RE.search(label)
                    if sm:
                        silence_cues.append({"nac": int(sm.group(1)), "turn": turns_done + 1, "ts": ts})
                    if first_cue_ts is None and ts:
                        first_cue_ts = ts
                    if CLOSE_RE.search(label):
                        loop_closed = True
                elif kind == "action":
                    actions.append(label)
                    if CLOSE_RE.search(label):
                        loop_closed = True
                    if CHOOSE_RE.search(label):
                        add("inter", "chon/tra-loi", ts, turns_done + 1)
                else:  # plain: hoc vien tu go, hoac nut mot cham
                    norm = norm_ws(text)
                    for offer in one_touch_offers:
                        key = norm_ws(offer)[:25]
                        if key and norm.startswith(key):
                            one_touch_sent += 1
                            add("inter", "mot-cham", ts, turns_done + 1)
                            break
            continue

        # assistant
        if not in_turn and blocks:
            turns_done += 1
            in_turn = True
            turn_parts = {cur_part}
            ensure(cur_part, ts=ts).turns += 1
        for b in blocks:
            bt = b.get("type")
            if bt == "text":
                text = b.get("text") if isinstance(b.get("text"), str) else ""
                if text.strip():
                    teacher_text_blocks += 1
                    ti(turns_done)["texts"].append(text.strip())
                for label, snip in scan_leaks(text):
                    leaks.append({"label": label, "snippet": snip, "turn": turns_done, "ts": ts})
                for label, snip in scan_voice(text):
                    voice.append({"label": label, "snippet": snip, "turn": turns_done, "ts": ts})
                continue
            if bt in ("thinking", "redacted_thinking"):
                thinking_blocks += 1  # chi de bao cao: Desktop co the hien khoi nay nhu ban tom tat suy nghi
                continue
            if bt != "tool_use":
                continue
            name = b.get("name") if isinstance(b.get("name"), str) else ""
            inp = b.get("input") if isinstance(b.get("input"), dict) else {}

            if name.endswith("show_widget"):
                widgets += 1
                add("visual", "widget", ts, turns_done)
                code = inp.get("widget_code")
                if isinstance(code, str) and "sendPrompt" in code:
                    widget_buttons += 1
                    add("inter", "widget-nut", ts, turns_done)
            elif name == "Artifact" or name.endswith("__Artifact"):
                action = inp.get("action")
                if (action in (None, "", "publish")) and not inp.get("asset"):
                    artifacts += 1
                    add("visual", "artifact", ts, turns_done)
            elif name == "AskUserQuestion":
                qs = inp.get("questions") if isinstance(inp.get("questions"), list) else []
                headers, strings = [], []
                for q in qs:
                    if not isinstance(q, dict):
                        continue
                    h = q.get("header")
                    if isinstance(h, str) and h.strip():
                        headers.append(h.strip())
                    for key in ("header", "question"):
                        if isinstance(q.get(key), str):
                            strings.append(q[key])
                    for o in q.get("options") or []:
                        if isinstance(o, dict):
                            for key in ("label", "description"):
                                if isinstance(o.get(key), str):
                                    strings.append(o[key])
                joined = " \n".join(strings)
                for label, snip in scan_leaks(joined):
                    leaks.append({"label": label, "snippet": snip, "turn": turns_done, "ts": ts, "where": "hộp câu hỏi"})
                exempt = is_exempt_box(qs)
                box = {
                    "ts": ts,
                    "turn": turns_done,
                    "part": cur_part,
                    "questions": len(qs),
                    "headers": headers,
                    "exempt": exempt,
                    "wait": None,
                    "interrupted": False,
                }
                boxes.append(box)
                p = ensure(cur_part, ts=ts)
                p.boxes += 1
                if not exempt:
                    p.boxes_counted += 1
                tid = b.get("id")
                if isinstance(tid, str):
                    pending[tid] = box
            elif name in ("Write", "Edit", "MultiEdit"):
                fpath = str(inp.get("file_path") or "").replace("\\", "/")
                if ".lop-hoc" not in fpath:
                    continue
                text = write_text(inp)
                writes_total += 1
                base = fpath.rsplit("/", 1)[-1] or fpath
                writes_by_file[base] = writes_by_file.get(base, 0) + 1
                # doi phan truoc, de moi thu trong lan ghi nay tinh vao phan moi
                for m in SEG_RE.finditer(text):
                    idm = SEG_ID_RE.search(m.group("body"))
                    if idm:
                        tm = SEG_TITLE_RE.search(m.group("body"))
                        title = ""
                        if tm:
                            try:
                                title = json.loads('"' + tm.group(1) + '"')
                            except ValueError:
                                title = tm.group(1)
                        new_id = idm.group(1)
                        if new_id != cur_part and (new_id == "4" or re.search(r"Chốt vòng việc", title, re.I)):
                            loop_end_turns.add(turns_done)
                        cur_part = new_id
                        np_ = ensure(cur_part, title, ts)
                        if in_turn and cur_part not in turn_parts:
                            turn_parts.add(cur_part)
                            np_.turns += 1
                p = ensure(cur_part, ts=ts)
                p.writes += 1
                has_board = bool(BOARD_RE.search(text))
                has_point = bool(POINT_RE.search(text))
                if has_board or has_point:
                    state_visual_writes += 1
                    add("visual", "+".join(x for x, f in (("board", has_board), ("point", has_point)) if f), ts, turns_done)
                if CHOICES_RE.search(text):
                    choices_writes += 1
                    ti(turns_done)["choices"] = True
                    if DEFAULT_RE.search(text):
                        ti(turns_done)["choices_default"] = True
                    add("inter", "choices", ts, turns_done)
                if PAUSED_RE.search(text):
                    ti(turns_done)["pause"] = True
                for m in ONE_TOUCH_RE.finditer(text):
                    ti(turns_done)["one_touch"] = True
                    tm = ONE_TOUCH_TEXT_RE.search(m.group("body"))
                    if tm:
                        try:
                            offer = json.loads(tm.group(1))
                        except ValueError:
                            offer = tm.group(1).strip('"')
                        if isinstance(offer, str) and offer.strip():
                            one_touch_offers.append(offer)
                for m in BOOK_RE.finditer(text):
                    if BOOK_KEY_RE.search(m.group("body")):
                        book_written = True
                if BOOK_COMPLETE_RE.search(text):
                    book_written = True
                    book_complete = True
                om = OUTCOME_RE.search(text)
                if om:
                    loop_closed = True
                    if om.group(1) != last_outcome:
                        last_outcome = om.group(1)
                        loop_end_turns.add(turns_done)

    # --- tong hop ---
    start = min(all_ts) if all_ts else None
    end = max(all_ts) if all_ts else None
    t0 = first_cue_ts or start
    visuals = [e for e in events if e["kind"] == "visual"]
    inters = [e for e in events if e["kind"] == "inter"]

    def first_of(lst):
        return min(lst, key=lambda e: (e["ts"] or datetime.max.replace(tzinfo=timezone.utc), e["turn"])) if lst else None

    fv, fi = first_of(visuals), first_of(inters)

    def minutes_from_t0(e):
        if e is None or e["ts"] is None or t0 is None:
            return None
        return max(0.0, (e["ts"] - t0).total_seconds())

    # phan duoc tinh: cac phan co luot thay, hoac duoc ghi bang segment, hoac co su kien
    reached = [parts[i] for i in order]
    if not reached:
        reached = []

    # v0.11: R9 - moi cue im lang phai duoc dap bang hanh dong trong luot thay ke tiep
    silence = []
    for c in silence_cues:
        info = turn_info.get(c["turn"])
        res = dict(c)
        if info is None:
            res.update(ok=False, why="thầy không đáp trong lượt kế tiếp")
        else:
            acts = [n for n, f in (("hình", info["visual"]), ("choices", info["choices"]),
                                   ("một chạm", info["one_touch"]),
                                   ("lưu chỗ/paused", info["pause"] and c["nac"] == 3)) if f]
            waiting = WAITING_RE.search(" ".join(info["texts"]))
            if waiting:
                res.update(ok=False, why="lời đáp có chữ \"đợi\"" + ("" if acts else " và không có hành động"))
            elif not acts:
                res.update(ok=False, why="chỉ có chữ, không có hành động")
            else:
                res.update(ok=True, why="hành động: " + ", ".join(acts))
        silence.append(res)

    # v0.11: R10 - do dai moi tin chu cua thay (moi khoi text la mot tin)
    msgs = []
    for n in sorted(turn_info):
        for t in turn_info[n]["texts"]:
            msgs.append({"turn": n, "words": count_words(t), "text": norm_ws(t), "visual": turn_info[n]["visual"]})
    words_sorted = sorted(m["words"] for m in msgs)
    if words_sorted:
        k = len(words_sorted)
        median_words = float(words_sorted[k // 2]) if k % 2 else (words_sorted[k // 2 - 1] + words_sorted[k // 2]) / 2
    else:
        median_words = None
    long_no_visual = [m for m in msgs if m["words"] > LONG_MSG_WORDS and not m["visual"]]
    longest3 = sorted(msgs, key=lambda m: (-m["words"], m["turn"]))[:3]

    # v0.11: R11 - cuoi vong viec khong duoc hoi mo "lam gi tiep" ma khong de xuat mac dinh
    loop_ends = []
    for n in sorted(loop_end_turns):
        info = turn_info.get(n) or {"texts": [], "choices_default": False}
        texts = info["texts"]
        last = texts[-1] if texts else ""
        open_q = bool(OPEN_NEXT_RE.search(last))
        proposal = bool(info["choices_default"] or PROPOSAL_RE.search(" ".join(texts)))
        loop_ends.append({"turn": n, "open_q": open_q, "proposal": proposal, "ok": (not open_q) or proposal,
                          "snippet": norm_ws(last)[-80:]})

    return {
        "silence": silence,
        "msgs": msgs,
        "median_words": median_words,
        "max_words": max(words_sorted) if words_sorted else None,
        "long_no_visual": long_no_visual,
        "longest3": longest3,
        "loop_ends": loop_ends,
        "bad_lines": bad_lines,
        "start": start,
        "end": end,
        "t0": t0,
        "length_s": (end - start).total_seconds() if start and end else None,
        "turns": turns_done,
        "teacher_text_blocks": teacher_text_blocks,
        "cues": cues,
        "actions": actions,
        "widgets": widgets,
        "widget_buttons": widget_buttons,
        "artifacts": artifacts,
        "state_visual_writes": state_visual_writes,
        "choices_writes": choices_writes,
        "one_touch_offers": len(one_touch_offers),
        "one_touch_sent": one_touch_sent,
        "visual_total": len(visuals),
        "inter_total": len(inters),
        "chosen_msgs": sum(1 for a in actions if CHOOSE_RE.search(a)),
        "boxes": boxes,
        "writes": writes_total,
        "writes_by_file": writes_by_file,
        "parts": reached,
        "book_written": book_written,
        "book_complete": book_complete,
        "loop_closed": loop_closed,
        "first_visual": fv,
        "first_inter": fi,
        "first_visual_s": minutes_from_t0(fv),
        "first_inter_s": minutes_from_t0(fi),
        "leaks": leaks,
        "voice": voice,
        "thinking_blocks": thinking_blocks,
        "events": events,
    }


# ---------------------------------------------------------------------------
# Phan quyet theo luat v0.8
# ---------------------------------------------------------------------------


def dec(x: float) -> str:
    return f"{x:.2f}".replace(".", ",")


SUB_VI = {
    "widget": "widget",
    "artifact": "artifact",
    "board": "board",
    "point": "point",
    "board+point": "board + point",
    "choices": "choices",
    "widget-nut": "widget có nút",
    "chon/tra-loi": "Chọn/Trả lời",
    "mot-cham": "một chạm",
}


def fmt_dur(s) -> str:
    if s is None:
        return "–"
    s = int(round(s))
    if s < 60:
        return f"{s} giây"
    m, r = divmod(s, 60)
    if m < 60:
        return f"{m} phút {r:02d} giây"
    h, m = divmod(m, 60)
    return f"{h} giờ {m:02d} phút"


def judge(a: dict) -> list[dict]:
    out: list[dict] = []

    def rule(rid, title, status, detail):
        out.append({"id": rid, "title": title, "status": status, "detail": detail})

    turns = a["turns"]
    if turns == 0:
        rule("R1", "Hình đầu tiên trong 2 lượt thầy đầu", "N/A", "không có lượt thầy nào trong bản ghi")
        rule("R2", "Tương tác không-hộp đầu tiên trong 2 lượt thầy đầu", "N/A", "không có lượt thầy nào")
    else:
        fv, fi = a["first_visual"], a["first_inter"]
        if fv is None:
            rule("R1", "Hình đầu tiên trong 2 lượt thầy đầu", "FAIL", f"không có hình nào trong cả buổi ({turns} lượt thầy, toàn chữ)")
        else:
            ok = fv["turn"] <= FIRST_TURNS
            rule("R1", "Hình đầu tiên trong 2 lượt thầy đầu", "PASS" if ok else "FAIL",
                 f"hình đầu ở lượt {fv['turn']} ({SUB_VI.get(fv['sub'], fv['sub'])}), sau {fmt_dur(a['first_visual_s'])} kể từ mở lớp; ngưỡng ≤ {FIRST_TURNS} lượt")
        if fi is None:
            rule("R2", "Tương tác không-hộp đầu tiên trong 2 lượt thầy đầu", "FAIL", f"không có tương tác không-hộp nào trong cả buổi ({turns} lượt thầy)")
        else:
            ok = fi["turn"] <= FIRST_TURNS
            rule("R2", "Tương tác không-hộp đầu tiên trong 2 lượt thầy đầu", "PASS" if ok else "FAIL",
                 f"tương tác đầu ở lượt {fi['turn']} ({SUB_VI.get(fi['sub'], fi['sub'])}), sau {fmt_dur(a['first_inter_s'])} kể từ mở lớp; ngưỡng ≤ {FIRST_TURNS} lượt")

    parts = [p for p in a["parts"] if p.turns or p.boxes or p.writes or p.visuals or p.inters]
    if not parts:
        rule("R3", "Mỗi phần đã tới có ≥ 1 hình và ≥ 1 tương tác không-hộp", "N/A", "chưa có phần nào")
    else:
        bad = [p for p in parts if p.visuals < 1 or p.inters < 1]
        if bad:
            lst = "; ".join(f"phần {p.id}: {p.visuals} hình, {p.inters} tương tác" for p in bad)
            rule("R3", "Mỗi phần đã tới có ≥ 1 hình và ≥ 1 tương tác không-hộp", "FAIL", f"{len(bad)}/{len(parts)} phần thiếu: {lst}")
        else:
            rule("R3", "Mỗi phần đã tới có ≥ 1 hình và ≥ 1 tương tác không-hộp", "PASS", f"{len(parts)}/{len(parts)} phần đủ")

    bad = [p for p in parts if p.boxes_counted > 1]
    total_boxes = len(a["boxes"])
    counted = sum(p.boxes_counted for p in parts)
    detail = f"{total_boxes} hộp gốc, {counted} hộp tính luật (bỏ hộp đồng ý/an toàn/phiếu giao việc; hộp hồ sơ nhiều ô vẫn tính)"
    if bad:
        detail += "; vượt ngưỡng ≤ 1 hộp/phần: " + "; ".join(f"phần {p.id}: {p.boxes_counted}" for p in bad)
        rule("R4", "Hộp câu hỏi gốc ≤ 1 mỗi phần (ngoài đồng ý/an toàn/phiếu giao việc)", "FAIL", detail)
    else:
        rule("R4", "Hộp câu hỏi gốc ≤ 1 mỗi phần (ngoài đồng ý/an toàn/phiếu giao việc)", "PASS", detail)

    if turns == 0:
        rule("R5", "Ghi sổ lớp ≤ 1 lần mỗi lượt thầy (trung bình)", "N/A", f"{a['writes']} lần ghi, không có lượt thầy")
    else:
        avg = a["writes"] / turns
        rule("R5", "Ghi sổ lớp ≤ 1 lần mỗi lượt thầy (trung bình)", "PASS" if avg <= 1.0 else "FAIL",
             f"{a['writes']} lần ghi / {turns} lượt thầy = {dec(avg)} lần mỗi lượt; ngưỡng ≤ 1,00")

    if not a["loop_closed"]:
        rule("R6", "Ghi `book` khi đã đóng vòng việc", "N/A", "buổi này chưa đóng vòng việc (chưa thấy outcome hay 'Chốt vòng')")
    elif a["book_written"]:
        rule("R6", "Ghi `book` khi đã đóng vòng việc", "PASS", "đã đóng vòng việc và `book` có nội dung")
    else:
        rule("R6", "Ghi `book` khi đã đóng vòng việc", "FAIL", "đã đóng vòng việc nhưng `book` trống hoặc chưa ghi lần nào")

    n_leak = len(a["leaks"])
    if n_leak:
        kinds = {}
        for lk in a["leaks"]:
            kinds[lk["label"]] = kinds.get(lk["label"], 0) + 1
        rule("R7", "Không rò rỉ (câu tiếng Anh có sẵn, từ nội bộ)", "FAIL",
             f"{n_leak} chỗ rò rỉ: " + ", ".join(f"{k} × {v}" for k, v in kinds.items()))
    else:
        rule("R7", "Không rò rỉ (câu tiếng Anh có sẵn, từ nội bộ)", "PASS", "0 chỗ rò rỉ")

    waits = [b for b in a["boxes"] if b["wait"] is not None and not b["interrupted"]]
    long_ = [b for b in waits if b["wait"] > LONG_WAIT_S]
    if not a["boxes"]:
        rule("R8", f"Không hộp gốc nào mở quá {LONG_WAIT_S} giây", "PASS", "không có hộp gốc")
    elif long_:
        worst = max(long_, key=lambda b: b["wait"])
        rule("R8", f"Không hộp gốc nào mở quá {LONG_WAIT_S} giây", "FAIL",
             f"{len(long_)}/{len(waits)} hộp mở quá {LONG_WAIT_S} giây; lâu nhất {fmt_dur(worst['wait'])} (hộp \"{' / '.join(worst['headers']) or '?'}\")")
    else:
        mx = max((b["wait"] for b in waits), default=None)
        rule("R8", f"Không hộp gốc nào mở quá {LONG_WAIT_S} giây", "PASS", f"{len(waits)} hộp có đo được, lâu nhất {fmt_dur(mx)}")

    # --- v0.11 ---
    t9 = "Mỗi cue im lặng được đáp bằng hành động, không bằng \"đợi\""
    sil = a["silence"]
    if not sil:
        rule("R9", t9, "N/A", "không có cue `Học viên im lặng · nấc N`")
    else:
        bad = [c for c in sil if not c["ok"]]
        if bad:
            rule("R9", t9, "FAIL",
                 f"{len(bad)}/{len(sil)} cue không được đáp đúng: " + "; ".join(f"nấc {c['nac']} (lượt {c['turn']}): {c['why']}" for c in bad))
        else:
            rule("R9", t9, "PASS",
                 f"{len(sil)}/{len(sil)} cue được đáp: " + "; ".join(f"nấc {c['nac']} → {c['why']}" for c in sil))

    t10 = f"Tin của thầy ngắn: trung vị ≤ {MEDIAN_WORDS_MAX} từ, không tin nào > {LONG_MSG_WORDS} từ nếu lượt đó không có hình"
    if not a["msgs"]:
        rule("R10", t10, "N/A", "thầy chưa có tin chữ nào")
    else:
        top = "; ".join(f"{m['words']} từ (lượt {m['turn']}): \"{m['text'][:80]}\"" for m in a["longest3"])
        base = f"{len(a['msgs'])} tin; trung vị {dec(a['median_words'])} từ, dài nhất {a['max_words']} từ; 3 tin dài nhất: {top}"
        probs = []
        if a["median_words"] > MEDIAN_WORDS_MAX:
            probs.append(f"trung vị {dec(a['median_words'])} > {MEDIAN_WORDS_MAX}")
        if a["long_no_visual"]:
            probs.append(f"{len(a['long_no_visual'])} tin > {LONG_MSG_WORDS} từ trong lượt không có hình")
        if probs:
            rule("R10", t10, "FAIL", "; ".join(probs) + " | " + base)
        else:
            rule("R10", t10, "PASS", base)

    t11 = "Cuối vòng việc, thầy không hỏi mở \"làm gì tiếp\" mà không đề xuất mặc định"
    le = a["loop_ends"]
    if not le:
        rule("R11", t11, "N/A", "chưa thấy ghi sổ đóng vòng (phần 4 / Chốt vòng việc / outcome)")
    else:
        bad = [x for x in le if not x["ok"]]
        if bad:
            rule("R11", t11, "FAIL",
                 f"{len(bad)}/{len(le)} lần cuối vòng kết bằng câu hỏi mở không có mặc định: " + "; ".join(f"lượt {x['turn']}: \"…{x['snippet']}\"" for x in bad))
        else:
            rule("R11", t11, "PASS",
                 f"{len(le)}/{len(le)} lần cuối vòng ổn: " + "; ".join(f"lượt {x['turn']} ({'có đề xuất/mặc định' if x['proposal'] else 'không hỏi mở'})" for x in le))

    t12 = 'Giọng thầy và khung: tin chữ của thầy không tự xưng "tôi", không có câu tiếng Anh, không có từ nội bộ'
    info12 = f"thông tin: {a['thinking_blocks']} khối suy nghĩ (thinking) trong bản ghi, chỉ để biết, không ảnh hưởng kết luận"
    if not a["msgs"]:
        rule("R12", t12, "N/A", "thầy chưa có tin chữ nào | " + info12)
    else:
        v = a["voice"]
        if v:
            by: dict[str, list[dict]] = {}
            for x in v:
                by.setdefault(x["label"], []).append(x)
            parts12 = []
            for label, xs in by.items():
                ex = "; ".join(f"lượt {x['turn']}: \"{x['snippet'][:80]}\"" for x in xs[:3])
                parts12.append(f"{len(xs)} chỗ {label} ({ex})")
            rule("R12", t12, "FAIL", " · ".join(parts12) + " | " + info12)
        else:
            rule("R12", t12, "PASS", f"{len(a['msgs'])} tin chữ sạch | " + info12)
    return out


# ---------------------------------------------------------------------------
# Bao cao
# ---------------------------------------------------------------------------


def esc(s) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def hhmm(ts) -> str:
    return ts.astimezone().strftime("%H:%M:%S") if ts else "–"


def build_report(a: dict, verdicts: list[dict], source: Path) -> str:
    L: list[str] = []
    npass = sum(1 for v in verdicts if v["status"] == "PASS")
    nfail = sum(1 for v in verdicts if v["status"] == "FAIL")
    nna = sum(1 for v in verdicts if v["status"] == "N/A")

    L.append("# Báo cáo chấm buổi học – Lớp học NNC")
    L.append("")
    L.append(f"- Bản ghi: `{source.name}`")
    L.append(f"- Từ {hhmm(a['start'])} đến {hhmm(a['end'])} · dài {fmt_dur(a['length_s'])}")
    L.append(f"- Kết quả chung: **{npass} PASS · {nfail} FAIL**" + (f" · {nna} không áp dụng" if nna else ""))
    if a["bad_lines"]:
        L.append(f"- Có {a['bad_lines']} dòng hỏng trong bản ghi, đã bỏ qua.")
    L.append("")
    L.append("**Lượt thầy** là một lần thầy/cô trả lời nối tiếp một tin nhắn thật: tin của học viên, cue `[Giáo án]` hay thao tác `[Lớp học]` (các dòng lệnh hệ thống, kết quả công cụ không mở lượt mới). Một lượt gồm mọi dòng trả lời của thầy cho tới tin nhắn thật kế tiếp.")
    L.append("")

    # --- bang so lieu ---
    boxes = a["boxes"]
    waits = [b for b in boxes if b["wait"] is not None and not b["interrupted"]]
    longest = max(waits, key=lambda b: b["wait"]) if waits else None
    nq = sum(b["questions"] for b in boxes)
    wbf = a["writes_by_file"]
    wbf_txt = ", ".join(f"{k}: {v}" for k, v in sorted(wbf.items())) or "–"
    seg_ids = [p.id for p in a["parts"]]
    L.append("## Số liệu")
    L.append("")
    L.append("| Chỉ số | Giá trị |")
    L.append("|---|---|")
    rows = [
        ("Độ dài buổi", fmt_dur(a["length_s"])),
        ("Lượt thầy", a["turns"]),
        ("Cue `[Giáo án]` nhận", len(a["cues"])),
        ("Thao tác học viên `[Lớp học]`", len(a["actions"])),
        ("Hình (tổng)", f"{a['visual_total']} (widget {a['widgets']} · artifact {a['artifacts']} · ghi bục có board/point {a['state_visual_writes']})"),
        ("Tương tác không-hộp (tổng)", f"{a['inter_total']} (ghi choices {a['choices_writes']} · widget có nút {a['widget_buttons']} · Chọn/Trả lời {a['chosen_msgs']} · một chạm đã gửi {a['one_touch_sent']}/{a['one_touch_offers']} lần đưa ra)"),
        ("Hộp câu hỏi gốc", f"{len(boxes)} hộp · {nq} câu hỏi · {sum(1 for b in boxes if b['exempt'])} hộp đồng ý/an toàn/phiếu giao việc"),
        ("Hộp mở lâu nhất", f"{fmt_dur(longest['wait'])} (hộp \"{' / '.join(longest['headers']) or '?'}\")" if longest else "–"),
        ("Ghi sổ lớp `.lop-hoc/` (Write/Edit)", f"{a['writes']} lần ({wbf_txt}) · {dec(a['writes'] / a['turns'])} lần mỗi lượt thầy" if a["turns"] else f"{a['writes']} lần ({wbf_txt})"),
        ("Phần đã tới", ", ".join(seg_ids) if seg_ids else "chưa ghi phần nào"),
        ("Vòng việc đã đóng", "có" if a["loop_closed"] else "chưa"),
        ("`book`", "đã ghi có nội dung" if a["book_written"] else "trống / chưa ghi"),
        ("Thời gian tới hình đầu tiên", (f"{fmt_dur(a['first_visual_s'])} (lượt {a['first_visual']['turn']})") if a["first_visual"] else "chưa có hình"),
        ("Thời gian tới tương tác không-hộp đầu tiên", (f"{fmt_dur(a['first_inter_s'])} (lượt {a['first_inter']['turn']})") if a["first_inter"] else "chưa có tương tác"),
        ("Chỗ rò rỉ", len(a["leaks"])),
        ("Cue im lặng (nấc 1/2/3)", (f"{len(a['silence'])} cue ({sum(1 for c in a['silence'] if c['nac'] == 1)}/{sum(1 for c in a['silence'] if c['nac'] == 2)}/{sum(1 for c in a['silence'] if c['nac'] == 3)}) · đáp đúng bằng hành động {sum(1 for c in a['silence'] if c['ok'])}/{len(a['silence'])}") if a["silence"] else "không có"),
        ("Độ dài tin thầy (từ)", (f"{len(a['msgs'])} tin · trung vị {dec(a['median_words'])} · dài nhất {a['max_words']} · > {LONG_MSG_WORDS} từ không có hình: {len(a['long_no_visual'])}") if a["msgs"] else "chưa có tin chữ"),
        ("Giọng thầy và khung (R12)", f"{len(a['voice'])} chỗ lệch · {a['thinking_blocks']} khối suy nghĩ trong bản ghi (chỉ thông tin)"),
        ("Lần cuối vòng việc (R11)", (f"{len(a['loop_ends'])} lần · kết bằng câu hỏi mở không mặc định: {sum(1 for x in a['loop_ends'] if not x['ok'])}") if a["loop_ends"] else "không có"),
    ]
    for k, v in rows:
        L.append(f"| {esc(k)} | {esc(v)} |")
    L.append("")
    L.append("Mốc thời gian tính từ cue `Mở lớp` (không có thì từ dòng đầu của bản ghi).")
    L.append("")

    # --- theo phan ---
    L.append("## Theo từng phần")
    L.append("")
    parts = [p for p in a["parts"] if p.turns or p.boxes or p.writes or p.visuals or p.inters]
    if not parts:
        L.append("Không có phần nào để thống kê.")
    else:
        L.append("| Phần | Tên | Lượt thầy* | Hình | Tương tác không-hộp | Hộp gốc (tính luật / tổng) | Ghi sổ | Từ lúc |")
        L.append("|---|---|---|---|---|---|---|---|")
        for p in parts:
            L.append(f"| {esc(p.id)} | {esc(p.title or '–')} | {p.turns} | {p.visuals} | {p.inters} | {p.boxes_counted} / {p.boxes} | {p.writes} | {hhmm(p.first_ts)} |")
    L.append("")
    L.append("\\* Một lượt thầy đi qua nhiều phần thì được tính ở mỗi phần nó chạm tới, nên tổng cột này có thể lớn hơn số lượt thầy.")
    L.append("")

    # --- phan quyet ---
    L.append("## Kết luận theo luật v0.8")
    L.append("")
    for v in verdicts:
        L.append(f"- **{v['status']}** · {v['id']} · {v['title']} – {v['detail']}")
    L.append("")
    L.append(f"Tổng: {npass} PASS · {nfail} FAIL" + (f" · {nna} không áp dụng" if nna else ""))
    L.append("")

    # --- top 5 cho lau ---
    L.append("## 5 hộp câu hỏi gốc chờ lâu nhất")
    L.append("")
    top = sorted(waits, key=lambda b: -b["wait"])[:5]
    if not top:
        L.append("Không có hộp nào đo được thời gian chờ.")
    else:
        L.append("| # | Chờ | Tiêu đề hộp | Số câu | Lúc mở | Lượt |")
        L.append("|---|---|---|---|---|---|")
        for i, b in enumerate(top, 1):
            L.append(f"| {i} | {fmt_dur(b['wait'])} | {esc(' / '.join(b['headers']) or '?')} | {b['questions']} | {hhmm(b['ts'])} | {b['turn']} |")
    n_int = sum(1 for b in boxes if b["interrupted"])
    n_open = sum(1 for b in boxes if b["wait"] is None and not b["interrupted"])
    if n_int or n_open:
        L.append("")
        L.append(f"Không tính: {n_int} hộp bị ngắt giữa chừng (phiên kết thúc trước khi có đáp án), {n_open} hộp không thấy kết quả.")
    L.append("")

    # --- ro ri ---
    L.append("## Rò rỉ")
    L.append("")
    if not a["leaks"]:
        L.append("Không thấy.")
    else:
        L.append("| Loại | Đoạn trích (≤ 80 ký tự) | Lượt | Lúc |")
        L.append("|---|---|---|---|")
        for lk in a["leaks"][:30]:
            where = " · trong hộp câu hỏi" if lk.get("where") else ""
            L.append(f"| {esc(lk['label'])}{where} | `{esc(lk['snippet'])}` | {lk['turn']} | {hhmm(lk['ts'])} |")
        if len(a["leaks"]) > 30:
            L.append("")
            L.append(f"… và {len(a['leaks']) - 30} chỗ nữa.")
    L.append("")

    L.append("## Cách tính")
    L.append("")
    L.append("- **Hình**: gọi công cụ vẽ trong chat (tên kết thúc `show_widget`), đăng Artifact, hoặc ghi sổ lớp có `board` / `podium.point`.")
    L.append("- **Tương tác không-hộp**: ghi `choices`, widget có nút gửi lại (`sendPrompt`), tin `[Lớp học] Chọn` / `Trả lời`, hoặc học viên gửi đúng lệnh một chạm đã đưa ra.")
    L.append("- **Hộp gốc**: lời gọi `AskUserQuestion`; thời gian chờ là từ lúc mở đến lúc có kết quả. Hộp có chữ đồng ý / cho phép / an toàn / giao việc / biểu mẫu ở tiêu đề hoặc câu hỏi không tính vào luật R4; hộp kiểm bài (Đúng hay sai, Câu n, Thẻ n) và hộp hồ sơ nhiều ô vẫn tính.")
    L.append("- **Ghi sổ lớp**: mọi Write/Edit có đường dẫn chứa `.lop-hoc`. **Phần** theo lần ghi `segment` gần nhất (trước đó mặc định là phần 0).")
    L.append("- **Đóng vòng việc**: thấy `outcome` được ghi (GUIDED, REUSED_IN_WORK…) hoặc tin có chữ \"Chốt vòng\".")
    L.append("- **R9 (cue im lặng)**: mỗi cue `Học viên im lặng · nấc N` phải có, trong lượt thầy kế tiếp, một hành động (hình, widget, ghi `choices`/`board`/`point`, một chạm; nấc 3 còn nhận ghi `status: paused`) và lời đáp không có chữ \"đang đợi\" / \"đợi bạn\". Không có cue thì N/A.")
    L.append(f"- **R10 (độ dài)**: mỗi khối chữ của thầy là một tin, đếm từ theo khoảng trắng; trung vị ≤ {MEDIAN_WORDS_MAX} từ; tin > {LONG_MSG_WORDS} từ chỉ được nằm trong lượt có hình.")
    L.append("- **R11 (cuối vòng)**: cuối vòng được nhận ra từ lần ghi sổ đổi sang phần \"4\" / \"Chốt vòng việc\" hoặc đặt `outcome`. Heuristic theo từ khóa: FAIL khi tin chữ cuối của lượt đó là câu hỏi mở (\"làm gì tiếp\", \"muốn làm gì\"…) và lượt đó không ghi `choices` có `default` cũng không có chữ đề xuất vòng kế (\"vòng tiếp\", \"đề xuất\", \"mặc định\"…).")
    L.append("- **R12 (giọng thầy)**: quét từng khối chữ của thầy. Tự xưng \"tôi\"/\"Tôi\" (bỏ đoạn trong ngoặc kép, code, tên file, đường dẫn); câu tiếng Anh = ≥ 5 từ Latin liền nhau không dấu tiếng Việt (bỏ code trong dấu backtick, URL, tên file, danh sách tên riêng viết hoa); từ nội bộ state.json, .lop-hoc, hook, prompt, cue, schema, token (kể cả trong backtick). Số khối `thinking` chỉ để biết, vì Desktop có thể hiện chúng như bản tóm tắt suy nghĩ; lớp mẫu đã tắt `showThinkingSummaries`.")
    L.append("")
    return "\n".join(L)


def summary_line(a: dict, verdicts: list[dict]) -> str:
    npass = sum(1 for v in verdicts if v["status"] == "PASS")
    nfail = sum(1 for v in verdicts if v["status"] == "FAIL")
    waits = [b["wait"] for b in a["boxes"] if b["wait"] is not None and not b["interrupted"]]
    mx = fmt_dur(max(waits)) if waits else "–"
    return (
        f"{a['turns']} lượt thầy · {a['visual_total']} hình · {a['inter_total']} tương tác không-hộp · "
        f"{len(a['boxes'])} hộp gốc (chờ lâu nhất {mx}) · {a['writes']} lần ghi sổ · "
        f"{len(a['leaks'])} rò rỉ · {npass} PASS / {nfail} FAIL"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def default_out(session: Path) -> Path:
    return Path.cwd() / f"bao-cao-buoi-hoc-{session.stem[:8]}.md"


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Chấm một buổi Lớp học NNC từ bản ghi Claude Code (JSONL).")
    ap.add_argument("target", nargs="?", help="file .jsonl, thư mục lớp, hoặc thư mục projects (mặc định: thư mục hiện tại)")
    ap.add_argument("--out", help="đường dẫn file báo cáo .md")
    args = ap.parse_args(argv)

    session, note = resolve_session(args.target)
    if session is None:
        print(f"Không tìm thấy buổi học: {note}", file=sys.stderr)
        return 2
    rows, bad = load_rows(session)
    a = analyze(rows, bad)
    verdicts = judge(a)
    report = build_report(a, verdicts, session)
    out = Path(args.out) if args.out else default_out(session)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(f"Báo cáo: {out}")
    print(summary_line(a, verdicts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
