"""Tests for tools/kiem-buoi-hoc.py (Lop hoc NNC v0.9 part B).

Synthetic Claude Code transcripts (JSONL) are built in tmp dirs: a good v0.8
session and a bad one shaped like the 18/10 test. Stdlib + pytest only.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "kiem-buoi-hoc.py"

_spec = importlib.util.spec_from_file_location("kiem_buoi_hoc", TOOL)
kbh = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kbh)

CUE_TAIL = "\n\nThis is how Claude Code surfaces a prompt a plugin submits between turns — it starts this turn in the user's place. Address the message above."
STATE = "F:\\Lop\\Lop-hoc-NNC\\.lop-hoc\\state.json"
TRAINER = "F:\\Lop\\Lop-hoc-NNC\\.lop-hoc\\trainer.json"


class Session:
    """Builds a transcript the way Claude Code writes it."""

    def __init__(self):
        self.rows: list[dict] = []
        self.t = datetime(2026, 10, 18, 10, 0, 0, tzinfo=timezone.utc)
        self.n = 0
        self.tool_n = 0

    def tick(self, seconds: float):
        self.t += timedelta(seconds=seconds)

    def _row(self, rtype: str, content, **extra) -> dict:
        self.n += 1
        self.t += timedelta(seconds=1)
        row = {
            "type": rtype,
            "uuid": f"u-{self.n}",
            "isSidechain": False,
            "timestamp": self.t.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "message": {"role": rtype, "content": content},
        }
        row.update(extra)
        self.rows.append(row)
        return row

    # --- user side ---
    def user_text(self, text: str):
        self._row("user", text)

    def cue(self, label: str):
        self.user_text("The lop-hoc plugin sent a message:\n[Giáo án] " + label + CUE_TAIL)

    def learner(self, label: str):
        self.user_text("The lop-hoc plugin sent a message:\n[Lớp học] " + label)

    def result(self, tool_id: str, content="ok", is_error: bool = False):
        self._row("user", [{"type": "tool_result", "tool_use_id": tool_id, "content": content, "is_error": is_error}])

    # --- assistant side ---
    def say(self, text: str):
        self._row("assistant", [{"type": "text", "text": text}])

    def think(self, text: str = "Tôi chấm lại 3 câu."):
        self._row("assistant", [{"type": "thinking", "thinking": text, "signature": "sig"}])

    def tool(self, name: str, inp: dict, result: str = "ok", wait: float = 0.0) -> str:
        self.tool_n += 1
        tid = f"toolu_{self.tool_n}"
        self._row("assistant", [{"type": "tool_use", "id": tid, "name": name, "input": inp}])
        if wait:
            self.tick(wait)
        if result is not None:
            self.result(tid, result)
        return tid

    def widget(self, title: str, buttons: bool = True):
        code = "<div>slide</div>" + ("<button onclick=\"sendPrompt('[Lớp học] Trả lời · q · a')\">A</button>" if buttons else "")
        self.tool("mcp__visualize__show_widget", {"title": title, "widget_code": code}, "shown")

    def write_state(self, obj: dict, path: str = STATE):
        self.tool("Write", {"file_path": path, "content": json.dumps(obj, ensure_ascii=False, indent=2)}, "File created successfully")

    def edit(self, new_string: str, old_string: str = "x", path: str = STATE):
        self.tool("Edit", {"file_path": path, "old_string": old_string, "new_string": new_string, "replace_all": False}, "updated")

    def ask(self, headers: list[str], wait: float = 20.0, interrupted: bool = False):
        qs = [
            {"header": h, "question": f"Câu hỏi {h}?", "multiSelect": False,
             "options": [{"label": "A", "description": "a"}, {"label": "B", "description": "b"}]}
            for h in headers
        ]
        if interrupted:
            self.tool("AskUserQuestion", {"questions": qs}, "[Tool call interrupted: the session ended before this call's result was recorded]", wait)
            self.rows[-1]["message"]["content"][0]["is_error"] = True
        else:
            self.tool("AskUserQuestion", {"questions": qs}, 'Your questions have been answered: "x"="y"', wait)

    def dump(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in self.rows) + "\n", encoding="utf-8")
        return path


# ---------------------------------------------------------------------------
# Fixtures: a good v0.8 session and a bad one shaped like the real 18/10 test
# ---------------------------------------------------------------------------


def good_session() -> Session:
    s = Session()
    s.cue("Mở lớp · giáo viên thay · chế độ Auto · model Opus 5.5 · effort medium")
    s.say("Chào bạn, thầy vẽ cho bạn xem trước nhé.")
    s.widget("Thanh dưới ô nhập", buttons=True)
    s.write_state({
        "schema": "lop-hoc/2",
        "segment": {"id": "0", "title": "Vào lớp", "drive": "ket-noi"},
        "podium": {"size": "wide", "point": "effort"},
        "board": {"title": "Effort ở đâu?", "lines": ["Thanh dưới ô nhập", "Bên phải"]},
        "choices": {"id": "c1", "prompt": "Thấy chưa?", "options": [{"label": "Thấy rồi"}, {"label": "Chỉ giúp"}], "default": 1},
    })
    s.tick(20)
    s.learner("Chọn · c1 · Thấy rồi")
    s.say("Giỏi lắm. Giờ thầy cho một việc nhỏ.")
    s.write_state({
        "segment": {"id": "0", "title": "Vào lớp"},
        "choices": {"id": "c2", "prompt": "Việc nào?", "options": [{"label": "Bảng"}, {"label": "Thư"}]},
    })
    s.tick(25)
    s.learner("Trả lời · q1 · Bảng")
    s.say("Sang phần hai nhé.")
    s.widget("Phiếu và bảng", buttons=True)
    s.write_state({
        "segment": {"id": "1", "title": "Làm quen nhanh", "drive": "D2"},
        "board": {"title": "Nguồn và kết quả", "lines": ["Phiếu bên trái", "Bảng bên phải"]},
        "choices": {"id": "c3", "prompt": "Khớp không?", "options": [{"label": "Khớp"}, {"label": "Lệch"}]},
    })
    s.tick(30)
    s.learner("Chọn · c3 · Khớp")
    s.say("Trước khi cho Claude đọc thư mục, thầy xin bạn đồng ý.")
    s.ask(["Đồng ý"], wait=15)
    s.say("Cảm ơn bạn. Mình chốt vòng việc hôm nay.")
    s.write_state({
        "schema": "lop-hoc/2",
        "book": {"1": "done", "2": "taught"},
        "outcome": "GUIDED",
    }, path=TRAINER)
    return s


def bad_session() -> Session:
    """Shaped like the real 18/10 test: text-only, 14 native boxes, 36+ Edits, a 6-minute box wait."""
    s = Session()
    s.cue("Mở lớp · giáo viên thay")
    s.write_state({"schema": "lop-hoc/2", "segment": {"id": "0", "title": "Vào lớp"}, "board": None, "choices": None})
    s.write_state({"autonomy": 2, "book": {}, "outcome": None}, path=TRAINER)
    s.ask(["Ngôn ngữ", "Xưng hô", "Kinh nghiệm", "Mong muốn"], wait=33)
    s.edit('"address": "bạn"')
    s.edit('"language": "vi"')
    s.ask(["Chế độ", "Năng lượng", "Điều ngại"], wait=40, interrupted=True)
    s.say("No response requested.")
    s.cue("Học viên trở lại")
    s.say("Chào bạn quay lại.")
    s.ask(["Chế độ", "Năng lượng"], wait=20)
    s.ask(["Loại việc"], wait=15)
    s.edit('"next_action": "a"')
    s.edit('"next_action": "b"')
    s.user_text("Chép ảnh phiếu nhận hàng mẫu vào thư mục Thuc-hanh rồi đọc ảnh.")
    s.say("Xong rồi.")
    s.edit('"segment": { "id": "1", "title": "Làm quen nhanh", "drive": "D2" }')
    for i in range(5):
        s.edit(f'"next_action": "step {i}"')
    s.ask(["Bạn thấy"], wait=68)
    s.ask(["Đổi xong?"], wait=10)
    s.ask(["Câu 1", "Câu 2", "Câu 3"], wait=34)
    s.ask(["Thẻ 1"], wait=26)
    s.ask(["Câu A", "Câu B"], wait=79)
    s.ask(["Effort"], wait=360)
    s.ask(["Effort"], wait=12)
    for i in range(8):
        s.edit(f'"next_action": "mid {i}"')
    s.edit('"segment": { "id": "2", "title": "Việc thật của tôi", "drive": "D1" }')
    s.ask(["Tiếp theo"], wait=22)
    s.ask(["Kết quả"], wait=31)
    s.ask(["Tiếp theo"], wait=10)
    for i in range(14):
        s.edit(f'"next_action": "late {i}"')
    s.cue("Kiểm phần học · phần 0 · 17 phút")
    s.say("Bạn bấm nút trên bục rồi nhấn Enter nhé.")
    s.edit('"segment": { "id": "3", "title": "Thử thách", "drive": "D3" }')
    s.cue("Xin nghỉ")
    s.edit('"status": "paused"')
    s.edit('"outcome": "GUIDED"', path=TRAINER)
    s.say("Bạn nghỉ đi nhé.")
    return s


def statuses(a: dict) -> dict:
    return {v["id"]: v["status"] for v in kbh.judge(a)}


# ---------------------------------------------------------------------------
# Verdicts
# ---------------------------------------------------------------------------


def test_good_session_all_pass(tmp_path):
    path = good_session().dump(tmp_path / "good.jsonl")
    rows, bad = kbh.load_rows(path)
    assert bad == 0
    a = kbh.analyze(rows, bad)
    st = statuses(a)
    assert {k: v for k, v in st.items() if int(k[1:]) <= 8} == {f"R{i}": "PASS" for i in range(1, 9)}, kbh.judge(a)
    assert st["R9"] == "N/A" and st["R10"] == "PASS" and st["R11"] == "PASS", kbh.judge(a)
    assert a["first_visual"]["turn"] == 1
    assert a["first_inter"]["turn"] == 1
    assert a["book_written"] and a["loop_closed"]
    assert [p.id for p in a["parts"]] == ["0", "1"]
    # one state write per teacher turn on average
    assert a["writes"] <= a["turns"]
    assert a["leaks"] == []
    assert a["inter_total"] >= 4  # choices writes, widget buttons, Chọn/Trả lời messages


def test_bad_session_shaped_like_real_test(tmp_path):
    s = bad_session()
    path = s.dump(tmp_path / "bad.jsonl")
    rows, bad = kbh.load_rows(path)
    a = kbh.analyze(rows, bad)
    st = statuses(a)
    for rule in ("R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"):
        assert st[rule] == "FAIL", (rule, kbh.judge(a))
    assert len(a["boxes"]) == 14
    assert a["visual_total"] == 0
    assert a["inter_total"] == 0 or a["inter_total"] == a["one_touch_sent"]
    edits = sum(1 for r in rows if r["type"] == "assistant" and any(b.get("name") == "Edit" for b in r["message"]["content"] if isinstance(b, dict)))
    assert edits == 36
    assert a["writes"] == 38
    assert a["book_written"] is False and a["loop_closed"] is True
    waits = sorted((b["wait"] for b in a["boxes"] if b["wait"] is not None and not b["interrupted"]), reverse=True)
    assert 359 <= waits[0] <= 365  # the 6-minute box
    interrupted = [b for b in a["boxes"] if b["interrupted"]]
    assert len(interrupted) == 1
    assert [lk["snippet"] for lk in a["leaks"]] == ["No response requested."]
    assert all(len(lk["snippet"]) <= 80 for lk in a["leaks"])
    assert [p.id for p in a["parts"]] == ["0", "1", "2", "3"]


def test_bad_report_content(tmp_path):
    path = bad_session().dump(tmp_path / "bad.jsonl")
    rows, bad = kbh.load_rows(path)
    a = kbh.analyze(rows, bad)
    report = kbh.build_report(a, kbh.judge(a), path)
    assert report.startswith("# Báo cáo chấm buổi học")
    assert "## Số liệu" in report and "## Theo từng phần" in report
    assert "## Kết luận theo luật v0.8" in report
    assert "## 5 hộp câu hỏi gốc chờ lâu nhất" in report and "## Rò rỉ" in report
    for rid in ("R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"):
        assert re.search(rf"\*\*FAIL\*\* · {rid} ", report), rid
    assert "`No response requested.`" in report
    top = report.split("## 5 hộp câu hỏi gốc chờ lâu nhất")[1].split("## Rò rỉ")[0]
    rows_ = [ln for ln in top.splitlines() if ln.startswith("| ") and ln[2].isdigit()]
    assert 1 <= len(rows_) <= 5
    assert "Effort" in rows_[0] and "6 phút" in rows_[0]
    assert "3 PASS · 8 FAIL · 1 không áp dụng" in report


def test_good_report_has_pass_lines(tmp_path):
    path = good_session().dump(tmp_path / "good.jsonl")
    rows, bad = kbh.load_rows(path)
    a = kbh.analyze(rows, bad)
    report = kbh.build_report(a, kbh.judge(a), path)
    assert report.count("**PASS**") == 11
    assert report.count("**N/A**") == 1
    assert "**FAIL**" not in report
    assert "Không thấy." in report  # no leaks


# ---------------------------------------------------------------------------
# Rule details
# ---------------------------------------------------------------------------


def test_visual_in_third_turn_fails_r1(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.say("Một.")
    s.cue("Học viên trở lại")
    s.say("Hai.")
    s.cue("Kiểm")
    s.widget("Muộn", buttons=False)
    a = kbh.analyze(*kbh.load_rows(s.dump(tmp_path / "s.jsonl")))
    r1 = next(v for v in kbh.judge(a) if v["id"] == "R1")
    assert r1["status"] == "FAIL" and "lượt 3" in r1["detail"]


def test_exempt_consent_box_not_counted_but_profile_form_is(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.ask(["Đồng ý"], wait=5)  # consent -> exempt
    s.ask(["Ngôn ngữ", "Xưng hô", "Kinh nghiệm"], wait=5)  # profile form -> counted once
    a = kbh.analyze(*kbh.load_rows(s.dump(tmp_path / "s.jsonl")))
    assert [b["exempt"] for b in a["boxes"]] == [True, False]
    assert statuses(a)["R4"] == "PASS"
    s.ask(["Chế độ"], wait=5)
    a = kbh.analyze(*kbh.load_rows(s.dump(tmp_path / "s2.jsonl")))
    assert statuses(a)["R4"] == "FAIL"


def test_quiz_box_never_exempt_even_with_consent_words(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.tool("AskUserQuestion", {"questions": [{"header": "Câu 3", "question": 'Đúng hay sai: "Khi Claude xin quyền, mình đọc rồi mới đồng ý"', "options": []}]}, "ok")
    a = kbh.analyze(*kbh.load_rows(s.dump(tmp_path / "s.jsonl")))
    assert a["boxes"][0]["exempt"] is False


def test_book_rule_is_not_applicable_before_loop_closes(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.write_state({"book": {}, "outcome": None}, path=TRAINER)
    a = kbh.analyze(*kbh.load_rows(s.dump(tmp_path / "s.jsonl")))
    assert statuses(a)["R6"] == "N/A"


def test_board_null_does_not_count_as_visual(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.write_state({"board": None, "podium": {"point": None}, "choices": None})
    a = kbh.analyze(*kbh.load_rows(s.dump(tmp_path / "s.jsonl")))
    assert a["visual_total"] == 0 and a["inter_total"] == 0


def test_one_touch_submission_counts_as_interaction(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.say("Thầy để nút trên bục.")
    s.write_state({"one_touch": {"label": "Đọc bảng", "text": "Đọc file Thuc-hanh/bang-tinh-mau.xlsx và cho tôi biết có mấy kênh."}})
    s.user_text("Đọc file Thuc-hanh/bang-tinh-mau.xlsx và cho tôi biết có mấy kênh.")
    s.say("Đây là kết quả.")
    a = kbh.analyze(*kbh.load_rows(s.dump(tmp_path / "s.jsonl")))
    assert a["one_touch_offers"] == 1 and a["one_touch_sent"] == 1
    assert a["first_inter"]["sub"] == "mot-cham"


def test_artifact_and_widget_are_visuals_but_asset_upload_is_not(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.tool("Artifact", {"action": "publish", "file_path": "x.html"}, "published")
    s.tool("Artifact", {"asset": True, "file_path": "x.png", "url": "u"}, "uploaded")
    s.widget("A", buttons=False)
    a = kbh.analyze(*kbh.load_rows(s.dump(tmp_path / "s.jsonl")))
    assert a["artifacts"] == 1 and a["widgets"] == 1 and a["visual_total"] == 2
    assert a["widget_buttons"] == 0


def test_internal_words_leak_with_short_snippet(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.say("Thầy vừa ghi vào state.json và chạy một hook để lưu prompt của bạn, " + "x" * 200)
    a = kbh.analyze(*kbh.load_rows(s.dump(tmp_path / "s.jsonl")))
    labels = {lk["label"] for lk in a["leaks"]}
    assert {"từ nội bộ state.json", "từ nội bộ hook", "từ nội bộ prompt"} <= labels
    assert all(len(lk["snippet"]) <= 80 for lk in a["leaks"])
    assert statuses(a)["R7"] == "FAIL"


def test_sidechain_noise_and_duplicate_rows_ignored(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.say("Một.")
    dup = dict(s.rows[-1])  # same uuid replayed
    s.rows.append(dup)
    side = dict(s.rows[-1], uuid="side-1", isSidechain=True)
    s.rows.append(side)
    s.user_text("<local-command-caveat>x</local-command-caveat>")
    s.user_text("Base directory for this skill: C:\\x\n[Giáo án] Mở lớp trong tài liệu")
    s.say("Hai.")
    a = kbh.analyze(*kbh.load_rows(s.dump(tmp_path / "s.jsonl")))
    assert a["turns"] == 1  # noise rows never open a teacher turn
    assert len(a["cues"]) == 1


# ---------------------------------------------------------------------------
# Slug and session resolution
# ---------------------------------------------------------------------------


def test_slug_replaces_every_non_alphanumeric():
    assert kbh.session_slug("/") == "-" or sys.platform == "win32"
    p = Path("some") / "Thu-v0.7.3" / "Lop hoc"
    slug = kbh.session_slug(p)
    assert slug == re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(str(p)))
    assert re.fullmatch(r"[A-Za-z0-9-]+", slug)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows drive path")
def test_slug_matches_real_windows_example():
    got = kbh.session_slug(r"F:\NCC_LTD\Lop_NNC\Thu-v0.7.3\Lop-hoc-NNC")
    assert got == "F--NCC-LTD-Lop-NNC-Thu-v0-7-3-Lop-hoc-NNC"


def _fake_home(tmp_path, monkeypatch) -> Path:
    home = tmp_path / "home"
    (home / ".claude" / "projects").mkdir(parents=True)
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("HOME", str(home))
    return home


def test_class_folder_resolves_to_newest_jsonl(tmp_path, monkeypatch):
    home = _fake_home(tmp_path, monkeypatch)
    classroom = tmp_path / "Thu-v0.7.3" / "Lop-hoc-NNC"
    classroom.mkdir(parents=True)
    pdir = home / ".claude" / "projects" / kbh.session_slug(classroom)
    old = good_session().dump(pdir / "old.jsonl")
    new = bad_session().dump(pdir / "new.jsonl")
    os.utime(old, (1_700_000_000, 1_700_000_000))
    os.utime(new, (1_800_000_000, 1_800_000_000))
    (pdir / "notes.txt").write_text("not a session", encoding="utf-8")
    found, _ = kbh.resolve_session(str(classroom))
    assert found == new
    # an older one flips the pick
    os.utime(old, (1_900_000_000, 1_900_000_000))
    assert kbh.resolve_session(str(classroom))[0] == old


def test_projects_folder_and_file_and_cwd(tmp_path, monkeypatch):
    home = _fake_home(tmp_path, monkeypatch)
    pdir = home / ".claude" / "projects" / "F--Some-Slug"
    a = good_session().dump(pdir / "a.jsonl")
    b = bad_session().dump(pdir / "b.jsonl")
    os.utime(a, (1_700_000_000, 1_700_000_000))
    os.utime(b, (1_800_000_000, 1_800_000_000))
    assert kbh.resolve_session(str(pdir))[0] == b  # a projects folder
    assert kbh.resolve_session(str(a))[0] == a  # a file
    classroom = tmp_path / "Lop"
    classroom.mkdir()
    cpdir = home / ".claude" / "projects" / kbh.session_slug(classroom)
    c = good_session().dump(cpdir / "c.jsonl")
    monkeypatch.chdir(classroom)
    assert kbh.resolve_session(None)[0] == c  # no argument -> current folder


def test_missing_session_exit_code_2(tmp_path, monkeypatch, capsys):
    _fake_home(tmp_path, monkeypatch)
    empty = tmp_path / "Lop-trong"
    empty.mkdir()
    assert kbh.main([str(empty)]) == 2
    assert "Không tìm thấy" in capsys.readouterr().err
    assert kbh.main([str(tmp_path / "khong-co")]) == 2


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_out_option_writes_report_and_prints_path(tmp_path, capsys):
    path = good_session().dump(tmp_path / "good.jsonl")
    out = tmp_path / "nested" / "dir" / "bao-cao.md"
    assert kbh.main([str(path), "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert text.startswith("# Báo cáo chấm buổi học")
    stdout = capsys.readouterr().out
    assert str(out) in stdout
    assert "11 PASS / 0 FAIL" in stdout


def test_default_out_goes_to_cwd(tmp_path, monkeypatch, capsys):
    path = bad_session().dump(tmp_path / "src" / "abcdef123456.jsonl")
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    assert kbh.main([str(path)]) == 0
    assert (work / "bao-cao-buoi-hoc-abcdef12.md").is_file()
    assert "3 PASS / 8 FAIL" in capsys.readouterr().out


def test_subprocess_run_utf8_and_exit_zero(tmp_path):
    path = bad_session().dump(tmp_path / "bad.jsonl")
    out = tmp_path / "r.md"
    env = dict(os.environ, PYTHONIOENCODING="cp1252")  # the tool must not depend on console encoding
    proc = subprocess.run(
        [sys.executable, str(TOOL), str(path), "--out", str(out)],
        capture_output=True, env=env, stdin=subprocess.DEVNULL, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")
    assert out.is_file()
    assert "lượt thầy" in proc.stdout.decode("utf-8")


# ---------------------------------------------------------------------------
# Robustness
# ---------------------------------------------------------------------------


def test_malformed_lines_do_not_break_the_report(tmp_path, capsys):
    s = good_session()
    path = s.dump(tmp_path / "messy.jsonl")
    good = path.read_text(encoding="utf-8").splitlines()
    junk = [
        "{not json",
        "[1, 2, 3]",
        "null",
        '"just a string"',
        "",
        "   ",
        json.dumps({"type": "user"}),
        json.dumps({"type": "assistant", "message": None, "timestamp": "garbage"}),
        json.dumps({"type": "assistant", "message": {"content": None}}),
        json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Write"}]}}),
        json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Write", "input": {"file_path": 5, "content": 7}}]}}),
        json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "AskUserQuestion", "id": 3, "input": {"questions": "x"}}]}}),
        json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": ["a"], "content": {"x": 1}}]}}),
        json.dumps({"type": "user", "message": {"content": [{"type": "text", "text": 12}, "stray", None]}}),
        json.dumps({"type": "system", "timestamp": "2026-10-18T09:00:00Z"}),
        "\x00\x01 binary \xff",
    ]
    mixed = good[:5] + junk + good[5:]
    path.write_text("\n".join(mixed) + "\n", encoding="utf-8")
    out = tmp_path / "r.md"
    assert kbh.main([str(path), "--out", str(out)]) == 0
    report = out.read_text(encoding="utf-8")
    assert "dòng hỏng" in report
    # the good session still reads the same through the noise
    a = kbh.analyze(*kbh.load_rows(path))
    assert a["bad_lines"] >= 4
    assert statuses(a)["R1"] == "PASS"
    assert capsys.readouterr().out  # printed path and summary


def test_empty_and_header_only_files(tmp_path):
    empty = tmp_path / "empty.jsonl"
    empty.write_text("", encoding="utf-8")
    out = tmp_path / "e.md"
    assert kbh.main([str(empty), "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "Lượt thầy | 0" in text
    assert "N/A" in text
    assert "FAIL" not in text.split("## Kết luận theo luật v0.8")[1].split("## 5 hộp")[0].replace("0 FAIL", "")


def test_utf8_bom_and_crlf_are_accepted(tmp_path):
    path = good_session().dump(tmp_path / "bom.jsonl")
    raw = path.read_bytes().replace(b"\n", b"\r\n")
    path.write_bytes(b"\xef\xbb\xbf" + raw)
    rows, bad = kbh.load_rows(path)
    assert bad == 0 and rows
    assert statuses(kbh.analyze(rows, bad))["R1"] == "PASS"


# ---------------------------------------------------------------------------
# v0.11 rules: R9 silence cues, R10 message length, R11 loop end
# ---------------------------------------------------------------------------


def run(s: Session, tmp_path) -> dict:
    return kbh.analyze(*kbh.load_rows(s.dump(tmp_path / "s.jsonl")))


def verdict(a: dict, rid: str) -> dict:
    return next(v for v in kbh.judge(a) if v["id"] == rid)


def test_r9_not_applicable_without_silence_cue(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.say("Chào bạn.")
    assert verdict(run(s, tmp_path), "R9")["status"] == "N/A"


def test_r9_pass_each_nac_answered_by_action(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.say("Chào bạn.")
    s.cue("Học viên im lặng · nấc 1")
    s.say("Bạn đang ở bước nào?")
    s.write_state({"choices": {"id": "c1", "prompt": "Bước nào?", "options": [{"label": "A"}, {"label": "B"}]}})
    s.cue("Học viên im lặng · nấc 2")
    s.say("Thầy làm mẫu.")
    s.widget("Mẫu", buttons=False)
    s.cue("Học viên im lặng · nấc 3")
    s.say("Lớp vẫn mở, lúc nào quay lại mình học tiếp đúng chỗ này.")
    s.write_state({"status": "paused", "resume": "bước 2"})
    a = run(s, tmp_path)
    assert [c["nac"] for c in a["silence"]] == [1, 2, 3]
    v = verdict(a, "R9")
    assert v["status"] == "PASS", v
    assert "3/3" in v["detail"]


def test_r9_pause_write_only_counts_for_nac_3(tmp_path):
    s = Session()
    s.cue("Học viên im lặng · nấc 2")
    s.say("Thầy lưu chỗ nhé.")
    s.write_state({"status": "paused"})
    v = verdict(run(s, tmp_path), "R9")
    assert v["status"] == "FAIL" and "nấc 2" in v["detail"]


def test_r9_fail_text_only_waiting_or_no_reply(tmp_path):
    s = Session()
    s.cue("Học viên im lặng · nấc 1")
    s.say("Bạn thử bấm nút trên bục nhé.")  # text only, no action
    s.cue("Học viên im lặng · nấc 2")
    s.say("Thầy đang đợi bạn.")
    s.widget("Hình", buttons=False)  # action, but says "đợi"
    s.cue("Học viên im lặng · nấc 3")  # no teacher reply at all
    a = run(s, tmp_path)
    v = verdict(a, "R9")
    assert v["status"] == "FAIL"
    assert "3/3 cue không được đáp đúng" in v["detail"]
    assert "chỉ có chữ" in v["detail"] and "đợi" in v["detail"] and "không đáp" in v["detail"]
    st = statuses(a)
    assert st["R9"] == "FAIL"


def test_r9_one_touch_counts_as_action(tmp_path):
    s = Session()
    s.cue("Học viên im lặng · nấc 2")
    s.say("Thầy làm mẫu một chạm.")
    s.write_state({"podium": {"one_touch": {"label": "Mở thử", "text": "mở thử đi"}}})
    assert verdict(run(s, tmp_path), "R9")["status"] == "PASS"


def words(n: int, word: str = "chữ") -> str:
    return " ".join([word] * n)


def test_r10_pass_median_and_long_text_with_visual(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    for _ in range(4):
        s.say(words(20))
    s.say(words(150, "dài"))  # > 120 words but the same turn has a visual
    s.widget("Hình", buttons=False)
    a = run(s, tmp_path)
    v = verdict(a, "R10")
    assert v["status"] == "PASS", v
    assert a["median_words"] == 20 and a["max_words"] == 150
    assert "dài nhất 150 từ" in v["detail"] and "trung vị 20,00" in v["detail"]
    assert len(a["longest3"]) == 3
    assert all(len(m["text"][:80]) <= 80 for m in a["longest3"])


def test_r10_fail_long_text_without_visual(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    for _ in range(4):
        s.say(words(10))
    s.say(words(130))
    a = run(s, tmp_path)
    v = verdict(a, "R10")
    assert v["status"] == "FAIL" and "> 120 từ" in v["detail"]
    assert len(a["long_no_visual"]) == 1


def test_r10_fail_median_too_high(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    for _ in range(3):
        s.say(words(60))
    s.say(words(10))
    s.widget("Hình", buttons=False)
    a = run(s, tmp_path)
    v = verdict(a, "R10")
    assert v["status"] == "FAIL" and "trung vị" in v["detail"]
    assert a["median_words"] == 60 and a["long_no_visual"] == []


def test_r10_not_applicable_without_teacher_text(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.widget("Chỉ hình", buttons=False)
    assert verdict(run(s, tmp_path), "R10")["status"] == "N/A"


def trainer_outcome(s: Session):
    s.write_state({"book": {"1": "done"}, "outcome": "GUIDED"}, path=TRAINER)


def test_r11_not_applicable_without_loop_end(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.say("Bạn muốn làm gì tiếp?")
    assert verdict(run(s, tmp_path), "R11")["status"] == "N/A"


def test_r11_fail_open_question_at_loop_end(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    trainer_outcome(s)
    s.say("Xong vòng việc rồi. Bạn muốn làm gì tiếp?")
    v = verdict(run(s, tmp_path), "R11")
    assert v["status"] == "FAIL" and "câu hỏi mở" in v["detail"]


def test_r11_fail_when_segment_4_write_ends_with_open_question(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.write_state({"segment": {"id": "3", "title": "Thử thách"}})
    s.say("Mình chốt vòng.")
    s.write_state({"segment": {"id": "4", "title": "Chốt vòng việc"}})
    s.say("Giờ mình làm gì tiếp nhỉ?")
    a = run(s, tmp_path)
    assert len(a["loop_ends"]) == 1
    assert verdict(a, "R11")["status"] == "FAIL"


def test_r11_pass_choices_with_default(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.say("Bạn muốn làm gì tiếp?")
    trainer_outcome(s)
    s.write_state({"choices": {"id": "n1", "prompt": "Vòng tiếp?", "options": [{"label": "Tiếp"}, {"label": "Nghỉ"}], "default": 0}})
    v = verdict(run(s, tmp_path), "R11")
    assert v["status"] == "PASS", v


def test_r11_choices_without_default_do_not_rescue_open_question(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    trainer_outcome(s)
    s.write_state({"choices": {"id": "n1", "prompt": "?", "options": [{"label": "Tiếp"}, {"label": "Nghỉ"}], "default": None}})
    s.say("Muốn làm gì tiếp?")
    assert verdict(run(s, tmp_path), "R11")["status"] == "FAIL"


def test_r11_pass_text_proposes_concrete_next_loop(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    trainer_outcome(s)
    s.say("Thầy đề xuất vòng tiếp: đọc phiếu nhận hàng thứ hai, bạn muốn làm gì khác thì nói thầy.")
    assert verdict(run(s, tmp_path), "R11")["status"] == "PASS"


def test_report_has_v011_numbers_and_rule_lines(tmp_path):
    s = Session()
    s.cue("Học viên im lặng · nấc 1")
    s.say("Bạn đang ở bước nào?")
    s.widget("Hình", buttons=False)
    trainer_outcome(s)
    path = s.dump(tmp_path / "s.jsonl")
    a = kbh.analyze(*kbh.load_rows(path))
    report = kbh.build_report(a, kbh.judge(a), path)
    for label in ("Cue im lặng (nấc 1/2/3)", "Độ dài tin thầy (từ)", "Lần cuối vòng việc (R11)"):
        assert label in report
    for rid in ("R9", "R10", "R11"):
        assert re.search(rf"\*\*(PASS|FAIL|N/A)\*\* · {rid} ", report), rid
    assert "trung vị" in report


# ---------------------------------------------------------------------------
# v0.12 rule: R12 teacher voice and frame
# ---------------------------------------------------------------------------


def test_r12_not_applicable_without_teacher_text(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    assert verdict(run(s, tmp_path), "R12")["status"] == "N/A"


def test_r12_pass_clean_teacher_voice_with_code_names_and_quotes(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.say("Chào bạn, thầy là thầy của lớp. Thầy vừa chấm xong phiếu của bạn.")
    s.say("Bạn bấm nút \"Tìm trong thư mục của tôi\" rồi mở `npm install the best package ever` giúp thầy.")
    s.say("Mở file ke-hoach-bai-hoc-moi-nhat-hom-nay.md hoặc https://example.com/the/best/thing/ever/made nhé.")
    s.say("Hôm nay mình dùng Word, Excel, PowerPoint, Zalo, Teams cho việc này.")
    v = verdict(run(s, tmp_path), "R12")
    assert v["status"] == "PASS", v
    assert "0 khối suy nghĩ" in v["detail"]


def test_r12_fail_self_reference_toi_as_speaker(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.say("Tôi chấm lại 3 câu rồi, bạn đúng 7 trên 10.")
    v = verdict(run(s, tmp_path), "R12")
    assert v["status"] == "FAIL", v
    assert "tự xưng" in v["detail"] and "Tôi chấm lại 3 câu" in v["detail"]


def test_r12_fail_english_sentence(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.say("Thầy đọc xong. I rechecked all of the answers carefully và thấy đúng.")
    v = verdict(run(s, tmp_path), "R12")
    assert v["status"] == "FAIL", v
    assert "câu tiếng Anh" in v["detail"]


def test_r12_fail_internal_words(tmp_path):
    for word in ("state.json", ".lop-hoc", "hook", "prompt", "cue", "schema", "token"):
        s = Session()
        s.cue("Mở lớp")
        s.say(f"Thầy vừa cập nhật {word} cho bạn.")
        v = verdict(run(s, tmp_path), "R12")
        assert v["status"] == "FAIL", (word, v)
        assert "từ nội bộ" in v["detail"], word


def test_r12_counts_thinking_blocks_without_changing_verdict(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.think()
    s.say("Thầy chấm lại rồi: đúng 7 trên 10 câu.")
    s.think("Cần đọc phiếu trước.")
    a = run(s, tmp_path)
    assert a["thinking_blocks"] == 2
    v = verdict(a, "R12")
    assert v["status"] == "PASS", v
    assert "2 khối suy nghĩ" in v["detail"]
    path = s.dump(tmp_path / "t.jsonl")
    report = kbh.build_report(a, kbh.judge(a), path)
    assert "R12" in report and "Giọng thầy và khung (R12)" in report


def test_r12_ignores_thinking_text_and_user_text(tmp_path):
    s = Session()
    s.cue("Mở lớp")
    s.user_text("Tôi muốn học cách làm bảng, I want to learn how to make tables quickly please")
    s.think("Tôi chấm lại 3 câu.")
    s.say("Thầy đã nhận. Mình làm bảng ngay nhé.")
    assert verdict(run(s, tmp_path), "R12")["status"] == "PASS"


def test_r12_ignores_markdown_blockquote_learner_voice():
    import importlib.util, pathlib
    p = pathlib.Path(__file__).resolve().parents[1] / "tools" / "kiem-buoi-hoc.py"
    spec = importlib.util.spec_from_file_location("kbh_r12", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    text = "Thầy điền sẵn 4 ý:\n> **Cách kiểm:** liệt kê rõ những dòng để tôi đối chiếu\nBạn bấm ▶ rồi Enter nhé."
    assert not [x for x in m.scan_voice(text) if x[0].startswith("tự xưng")]
    assert [x for x in m.scan_voice("Tôi chấm lại 3 câu cho bạn.") if x[0].startswith("tự xưng")]
