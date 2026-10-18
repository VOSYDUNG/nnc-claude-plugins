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
                for label, snip in scan_leaks(text):
                    leaks.append({"label": label, "snippet": snip, "turn": turns_done, "ts": ts})
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
                        cur_part = idm.group(1)
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
                    add("inter", "choices", ts, turns_done)
                for m in ONE_TOUCH_RE.finditer(text):
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
                if OUTCOME_RE.search(text):
                    loop_closed = True

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

    return {
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
