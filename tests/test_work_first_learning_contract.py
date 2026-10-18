"""Static contract checks for the optional work-first learning Skill (Lớp học NNC v0.8: always-open class, the teacher sets the stage).

These checks verify packaging and critical textual boundaries, not Claude behavior.
A real host/learner evaluation is still required.
"""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "nnc" / "skills" / "work-first-learning" / "SKILL.md"
REFS = SKILL.parent / "references"
SCENARIOS = REFS / "scenarios.md"
BUOI1 = REFS / "buoi-1.md"
CARDS = REFS / "the-dinh-nghia.md"
INTERACTIONS = REFS / "tuong-tac.md"
COMPETENCY = REFS / "nang-luc-giao-vien.md"
GAMES = REFS / "kho-tro-choi.md"
CAPABILITIES = REFS / "tu-kha-nang.md"
BADGES = REFS / "huy-hieu.md"
TEMPLATE = SKILL.parent / "templates" / "classroom-CLAUDE.md"
PILOT = ROOT / "docs" / "oser-r2" / "WORK-FIRST-LEARNING-PILOT.md"
CONTRACT = ROOT / "docs" / "oser-r2" / "LOP-HOC-V05-CONTRACT.md"
PLUGIN = ROOT / "plugins" / "nnc" / ".claude-plugin" / "plugin.json"
MARKET = ROOT / ".claude-plugin" / "marketplace.json"
DESIGN_V08 = ROOT / "docs" / "oser-r2" / "LOP-HOC-V08-THIET-KE.md"
TOOLBOX = REFS / "day-truc-quan.md"

LAO = re.compile(r"[຀-໿]")

CUES = (
    "Mở lớp", "Hạn mức · 5 giờ", "Hạn mức · tuần", "Hết hạn trả lời", "chọn giúp",
    "Học viên trở lại", "Xin phép", "Xin nghỉ", "Giơ tay", "Nhịp: chậm lại", "Nhịp: nhanh hơn",
)
# v0.6 cues a classroom may still send from an older podium: handled in the Skill's legacy line.
LEGACY_CUES = ("Mở buổi", "Bắt đầu phần", "Còn {n} phút", "Học viên vắng", "Kết thúc buổi")
EMOTIONS = ("hi", "no", "ai", "o", "bi", "lac", "giang", "nghe")
CARD_IDS = (
    "claude-code", "thu-muc", "phien", "model", "effort", "context",
    "usage-5h", "usage-tuan", "quyen", "skill",
)
GAME_KINDS = (
    "game:doan-xem", "game:hop-qua", "game:thu-thach-60s", "game:nguoi-voi-may",
    "game:tim-loi", "game:ban-la-sep", "game:dung-sai", "game:doi-vai",
)
BADGE_IDS = (
    "giao-viec-dau-tien", "mat-tinh", "thuoc-9-the", "tu-kiem-co-tam",
    "nguoi-day-lai", "dong-goi-skill-dau-tien", "ban-la-sep", "nhanh-tay",
)
SAMPLE_ASSETS = (
    "bang-tinh-mau.xlsx", "bang-tinh-mau-tuan-sau.xlsx", "gop/don-hang-tuan-40.xlsx",
    "gop/don-hang-tuan-41.xlsx", "gop/don-hang-tuan-42.xlsx", "phieu-nhan-hang-mau.png",
    "thong-bao-noi-bo-mau.md", "tim-loi/bang-tim-loi.xlsx", "ban-la-sep/ket-qua-claude-mau.xlsx",
)
STATE_FIELDS_V06 = ("one_touch", "activity", "challenge", "stars", "badges_new", "gift_box")
USAGE_SOURCES = (
    "https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work",
    "https://support.claude.com/en/articles/8325606-what-is-the-pro-plan",
    "https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan",
)


class _Balance(HTMLParser):
    """Tiny tag-balance check for the widget templates (container tags only)."""

    TAGS = {"div", "span", "table", "tr", "td", "ol", "li", "p", "b", "button", "svg", "script"}

    def __init__(self):
        super().__init__()
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag in self.TAGS:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.TAGS:
            if self.stack and self.stack[-1] == tag:
                self.stack.pop()
            else:
                self.errors.append(tag)


class WorkFirstLearningContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.scenarios = SCENARIOS.read_text(encoding="utf-8")
        cls.buoi1 = BUOI1.read_text(encoding="utf-8")
        cls.cards = CARDS.read_text(encoding="utf-8")
        cls.interactions = INTERACTIONS.read_text(encoding="utf-8")
        cls.competency = COMPETENCY.read_text(encoding="utf-8")
        cls.games = GAMES.read_text(encoding="utf-8")
        cls.capabilities = CAPABILITIES.read_text(encoding="utf-8")
        cls.badges = BADGES.read_text(encoding="utf-8")
        cls.template = TEMPLATE.read_text(encoding="utf-8")
        cls.pilot = PILOT.read_text(encoding="utf-8")
        cls.plugin = PLUGIN.read_text(encoding="utf-8")

    # --- packaging -------------------------------------------------------

    def test_plugin_baseline_unchanged(self):
        self.assertIn('"version": "5.1.0-alpha.2', self.plugin)
        self.assertIn("+lophoc.0.9.0", self.plugin)
        self.assertNotIn("5.1.0-alpha.3", self.plugin)

    def test_skill_frontmatter_and_links(self):
        self.assertTrue(self.skill.startswith("---\n"))
        frontmatter = self.skill.split("---", 2)[1]
        self.assertIn("name: work-first-learning", frontmatter)
        self.assertIn("version: 0.9.0", frontmatter)
        self.assertNotIn("version: 0.7.3", frontmatter)
        self.assertNotIn("version: 0.6.0", frontmatter)
        self.assertNotIn("version: 0.5.0", frontmatter)
        self.assertNotIn("version: 0.4.0", frontmatter)
        for ref in ("references/scenarios.md", "references/buoi-1.md",
                    "references/the-dinh-nghia.md", "references/tuong-tac.md",
                    "references/nang-luc-giao-vien.md", "references/kho-tro-choi.md",
                    "references/tu-kha-nang.md", "references/huy-hieu.md",
                    "references/vong-viec.md", "references/sach-tu-hoc.md",
                    "references/day-truc-quan.md"):
            self.assertIn(ref, self.skill)
            self.assertTrue((SKILL.parent / ref).is_file(), ref)
        self.assertIn("WORK-FIRST-LEARNING-PILOT.md", self.skill)
        self.assertTrue(PILOT.is_file())

    # --- kept from v0.4 --------------------------------------------------

    def test_recent_work_and_progressive_discovery(self):
        for phrase in (
            "Hôm nay, hôm qua", "job title", "one", "safe",
            "Stop questioning", "today", "yesterday",
        ):
            self.assertIn(phrase.lower(), self.skill.lower())

    def test_lead_engine(self):
        for phrase in (
            "Lead, don't just ask", "Restate", "Destination",
            "with its reason", "Ready path", "5 chặng",
            "at most **3 discovery questions**", "Decision Contract",
            "thử trước trên mẫu", "Never end a turn without a next step",
            "OSER checkpoint",
        ):
            self.assertIn(phrase, self.skill)
        self.assertIn("Led, not only asked", self.scenarios)

    def test_classroom_mode(self):
        for phrase in (
            "Lớp đang chờ giáo viên", "Bắt đầu việc mới", "Tiếp tục từ chỗ đã lưu",
            ".lop-hoc/state.json", '"schema": "lop-hoc/2"', "trainer.json",
            "calibration.json", "[Lớp học]", "Thưa cô, chỗ này chưa đúng",
            "Never edit this Skill yourself", "only names and modified dates",
            "never G-codes",
        ):
            self.assertIn(phrase, self.skill)
        self.assertNotIn('"schema": "lop-hoc/1"', self.skill)
        self.assertIn("work-first-learning", self.template)
        self.assertIn("Classroom:", self.scenarios)

    def test_drives_and_delegation(self):
        for phrase in (
            "mandatory once", "Never state current models, limits or recommendations from memory",
            "crop only the small region", "D1 Việc thật", "D2 Làm chủ Claude",
            "D3 Dám giao việc", "Kết nối", "Mục tiêu · Nguồn · Đầu ra · Cách kiểm",
            "Giao việc —", "Lượt của bạn", "result_parts", "Claude của tôi",
        ):
            self.assertIn(phrase, self.skill)

    def test_kernel_mission_and_privacy_boundaries(self):
        for phrase in (
            "does not replace or modify", "/nnc:mission-formation",
            "/nnc:adaptive-delivery", "without", "production",
            "Experience Observer", "off by default",
        ):
            self.assertIn(phrase.lower(), self.skill.lower())
        self.assertNotIn("run OSER init automatically", self.skill)
        self.assertIn("Do not automatically run OSER init", self.skill)

    def test_learning_observability_states(self):
        for state in (
            "GUIDED", "INDEPENDENT_NEW_INPUT", "REUSED_IN_WORK",
            "NO_OPPORTUNITY", "BLOCKED"
        ):
            self.assertIn(state, self.skill)
            self.assertIn(state, self.scenarios)

    def test_scenarios_and_host_not_claimed(self):
        for i in range(1, 57):
            self.assertIn("Case F{} ".format(i), self.scenarios)
        self.assertIn("NOT_TESTED", self.scenarios)
        self.assertIn("INSTALL_NOT_VERIFIED", self.pilot)
        self.assertIn("not proof of learner independence", self.pilot)
        self.assertIn("Claude Desktop", self.pilot)
        self.assertIn("Code → New session", self.pilot)
        self.assertIn("/work-first-learning", self.pilot)
        self.assertIn("/nnc:mission-formation", self.pilot)
        self.assertIn("OSER_SOURCE_UNVERIFIED", self.pilot)
        self.assertNotIn("claude --plugin-dir", self.pilot)

    # --- v0.5: teacher-led ----------------------------------------------

    def test_teacher_persona_emotions_and_honesty(self):
        for phrase in (
            "standing teacher", "thầy", "cô", "Nghiêm túc với nghề", "Sống kiến tạo",
            "Sống tích cực và hướng thiện", "never claim to be human", "never store it",
            "teacher.emotion",
        ):
            self.assertIn(phrase, self.skill)
        for code in EMOTIONS:
            self.assertIn("| `{}` |".format(code), self.skill)

    def test_every_contract_cue_is_handled(self):
        for cue in CUES + LEGACY_CUES:
            self.assertIn(cue, self.skill, cue)
        self.assertIn("[Giáo án]", self.skill)
        self.assertIn("Legacy cues", self.skill)
        if CONTRACT.is_file():  # cross-check against the shared contract when present
            contract = CONTRACT.read_text(encoding="utf-8")
            for raw in re.findall(r"`\[Giáo án\] ([^`]+)`", contract):
                key = raw.split(" · ")[0].split(" {")[0].strip()
                self.assertIn(key, self.skill, "contract cue not handled: " + key)
            for code in re.findall(r"`(\w+)` \(", contract.split("teacher.emotion", 1)[1].split("\n|", 1)[0]):
                self.assertIn(code, EMOTIONS)

    def test_native_ui_and_hidden_internals(self):
        for phrase in (
            "AskUserQuestion", "default option FIRST", "60 seconds", "task list",
            "Never show internal words", "runtime", "prompt", "hook", "mod",
            "never write `clock`", "help_needed",
        ):
            self.assertIn(phrase, self.skill)
        for phrase in ("[Giáo án]", "AskUserQuestion", "task list", "never claim to be human",
                       "lop-hoc/2", "Never ask the learner to type a slash command",
                       "Every visible line is in the learner's language"):
            self.assertIn(phrase, self.template)

    def test_nine_definitions_first_and_spaced_recall(self):
        for phrase in (
            "nine must-know definitions before any practice", "entry quiz",
            "Never keep the learner at the door more than one minute",
            "mastered after 3 correct recalls across at least 2 different days", "concepts",
            "Quick check first",
            "Do not claim when the five-hour window starts",
        ):
            self.assertIn(phrase, self.skill)

    def test_branches_are_never_labels(self):
        for phrase in ("`vung`", "`dang-len`", "`can-do`", "Branch names are **never shown**",
                       "branch point"):
            self.assertIn(phrase, self.skill)

    # --- v0.5: reference files ------------------------------------------

    def test_buoi1_script(self):
        for phrase in (
            "Part 0 — Vào lớp", "Part 1 — Làm quen nhanh", "Part 2 — Việc thật của tôi",
            "Part 3 — Thử thách theo nhịp của bạn", "Part 4 — Chốt vòng việc",
            "milestones, not minutes", "Exit milestone", "Usage-driven pace", '"header"', '"options"',
            "Branch point", "help_needed", "bai0_done", "việc kế tiếp",
            "Task list", "lop-hoc/2", "Người hỗ trợ", "quick check", "Đã chọn Auto",
        ):
            self.assertIn(phrase, self.buoi1, phrase)

    def test_definition_cards(self):
        for n in range(1, 11):
            self.assertIn("## Thẻ {} ".format(n), self.cards)
        for card_id in CARD_IDS:
            self.assertIn("`{}`".format(card_id), self.cards)
        self.assertEqual(self.cards.count("**Giải thích thêm:**"), 10)
        self.assertEqual(self.cards.count("**Nhớ lại:**"), 10)
        self.assertGreaterEqual(self.cards.count("✓"), 20)
        for url in USAGE_SOURCES:
            self.assertIn(url, self.cards)
        for phrase in ("resets every five hours", "giờ cố định mỗi tuần", "dùng chung", "Auto",
                       "Không có số tin nhắn cố định", "cảnh báo", "làm nốt bước đang dở",
                       "/status", "Settings > Usage", "Không được khẳng định",
                       "recalled_ok", "ít nhất 2 ngày khác nhau", "news"):
            self.assertIn(phrase, self.cards, phrase)

    def test_interaction_library(self):
        for phrase in (
            "Chào lớp (không điểm danh)", "năng lượng", "Nêu mục tiêu buổi", "Khởi động",
            "Giảng ngắn", "nghĩ to tiếng", "Thầy làm – cùng làm – em làm", "Gọi tên nhẹ nhàng",
            "Đố vui", "chọn giúp", "Khen cụ thể", "Sửa sai", "Động viên", "ngại giao việc",
            "an toàn dữ liệu", "Không ưng cách làm", "Câu đùa nhẹ", "Chuyển phần",
            "Chốt bước trước khi sang phần", "Nghỉ giữa giờ", "Giơ tay", "Xin phép", "Xin nghỉ",
            "chậm lại", "nhanh hơn", "Học viên im lặng", "trở lại", "Mời thử thách",
            "Tổng kết và nhớ lại", "học được từ học viên", "Việc kế tiếp", "quay lại",
            "người đứng lớp", "Trung thực",
        ):
            self.assertIn(phrase.lower(), self.interactions.lower(), phrase)
        self.assertGreaterEqual(self.interactions.count("- **Thầy"), 30)
        self.assertGreaterEqual(self.interactions.count("- **Cô"), 30)
        lao_lines = [l for l in self.interactions.splitlines()
                     if l.startswith("- **Lào:**") and LAO.search(l)]
        self.assertGreaterEqual(len(lao_lines), 8)
        for code in EMOTIONS:
            self.assertIn("`{}`".format(code), self.interactions)
        self.assertIn("không ghi gì", self.interactions)
        self.assertIn("không tự nhận là người", self.interactions)


    # --- v0.6: teacher competency ---------------------------------------

    def test_skill_competency_layer(self):
        for phrase in (
            "Teaching competency (v0.6)", "teaching loop", "Observe", "Choose the move", "Record",
            "high on sample data, none on real data", "2 Một chạm (start)",
            "Never the same interaction kind twice in a row", "every 3 minutes",
            "À, Claude làm được cái này", "4 minutes", "Fit test", "re-author", "Invariants",
            'never say "hạ bậc"', "autonomy_log", "games_proposed", "huy-hieu.json",
            "Thuc-hanh/", "Base directory for this skill", "Never copy answer keys",
            "Never put a timed challenge inside a question box", "observed behaviour",
            "within two minutes",
        ):
            self.assertIn(phrase, self.skill, phrase)
        for field in STATE_FIELDS_V06:
            self.assertIn("`{}".format(field), self.skill, field)
        for cue in ("[Giáo án] Đổi kiểu tương tác · {kind} · {n} phút",
                    "[Giáo án] Hết giờ thử thách · {title}", "Mở hộp quà"):
            self.assertIn(cue, self.skill, cue)
        for kind in ("giang", "demo", "one-touch", "quiz", "hands-on", "form") + GAME_KINDS:
            self.assertIn("`{}`".format(kind), self.skill, kind)

    def test_competency_manual(self):
        for level in ("0 · Xem", "1 · Bấm chọn", "2 · Một chạm", "3 · Điền mẫu",
                      "4 · Tự gõ", "5 · Tự làm việc mới"):
            self.assertIn(level, self.competency, level)
        for phrase in (
            "two correct in a row", "two stumbles in a row", "Nhịp: chậm lại",
            "does something above their level", "never announced", "hạ bậc",
            "cô làm thêm một chút", "autonomy_log", "dung-2-lan", "vap-2-lan", "het-han",
            "cham-lai", "tu-lam-vuot", "Signals → moves", "fit test", "Job context",
            "Time left", "Last kind", "re-author", "Invariants", "Nine definitions before practice",
            "Usage facts only from the official pages", "never claims to be human",
            "6 lines", "Đổi kiểu tương tác", "Hết giờ thử thách", "Mở hộp quà",
            "badges_new", "gift_box", "one_touch", "challenge", "thủ kho",
        ):
            self.assertIn(phrase, self.competency, phrase)

    def test_game_library(self):
        for kind in GAME_KINDS:
            self.assertIn("`{}`".format(kind), self.games, kind)
        for name in ("Đoán xem", "Hộp quà khả năng", "Thử thách 60 giây", "Người với máy",
                     "Tìm lỗi", "Bạn là sếp", "Đúng/sai chuỗi", "Đổi vai"):
            self.assertRegex(self.games, r"## \d\. " + re.escape(name) + r" — `game:", name)
        self.assertGreaterEqual(self.games.count('"options"'), 8)
        for field in ("**Thầy:**", "**Cô:**", "**Câu bài học:**", "**Thắng:**",
                      "**Đổi theo nghề:**", "**Sao/huy hiệu:**", "**Cảm xúc:**", "**Khi dùng:**"):
            self.assertGreaterEqual(self.games.count(field), 8, field)
        for phrase in ("Tự chế trò mới", "Danh sách kiểm 6 luật", "games_proposed",
                       "không bao giờ sửa file kho này", "Ví dụ 1 — Kho", "Ví dụ 2 — Bán hàng OTC",
                       "Ví dụ 3 — Kế toán", "không đặt trong hộp câu hỏi", "Tôi xong rồi",
                       "day-truc-quan.md", "Thuc-hanh/", "challenge"):
            self.assertIn(phrase, self.games, phrase)
        for n in range(1, 7):
            self.assertIn("- [ ] **{}.".format(n), self.games)

    def test_capability_cards(self):
        self.assertGreaterEqual(self.capabilities.count("**one_touch"), 9)
        self.assertGreaterEqual(self.capabilities.count('**Câu "À":**'), 9)
        self.assertGreaterEqual(self.capabilities.count("**An toàn:**"), 9)
        for asset in SAMPLE_ASSETS:
            self.assertIn(asset, self.capabilities, asset)
        for phrase in ("Base directory for this skill", "Thuc-hanh/", "Never copy answer keys",
                       "Never guess a path", "skill-mau/tong-hop-don-hang", "không gửi",
                       "cần người bản ngữ duyệt", "Sang file của học viên", "101.870.000"):
            self.assertIn(phrase, self.capabilities, phrase)
        # one-touch texts refer to the practice folder, never to the Skill's own folder
        texts = [l for l in self.capabilities.splitlines() if '"text":' in l]
        self.assertGreaterEqual(len(texts), 9)
        for line in texts:
            self.assertIn("Thuc-hanh/", line)
            self.assertNotIn("assets/", line)

    def test_badges(self):
        for badge in BADGE_IDS:
            self.assertIn("| `{}` |".format(badge), self.badges, badge)
        for phrase in ("hành vi", "Không bao giờ có huy hiệu hay sao cho số lần bấm",
                       "Không xếp hạng người với người", "Không trao khi", "badges_new",
                       "huy-hieu.json", "Sao trong buổi", "không bao giờ bị trừ"):
            self.assertIn(phrase, self.badges, phrase)

    def test_buoi1_competency(self):
        for phrase in ("Thuc-hanh/", "one_touch", "within the first two minutes",
                       "Move plan per part", "game:doan-xem", "game:dung-sai",
                       "game:ban-la-sep", "game:thu-thach-60s", "autonomy",
                       "Đổi kiểu tương tác", "Hết giờ thử thách", "Mở hộp quà",
                       "A taste of card 1, not practice"):
            self.assertIn(phrase, self.buoi1, phrase)
        # v0.7: no lesson lengths anywhere in the script
        for timing in ("| 0 | Vào lớp | 2 | 2 | 2 |", "15 phút (2 · 4 · 7 · 3)",
                       "45 phút (2 · 7 · 16 · nghỉ 3 · 14 · 3)", "Còn 2 phút phần"):
            self.assertNotIn(timing, self.buoi1, timing)
        plan = self.buoi1.split("Move plan per part", 1)[1]
        for part in ("0 Vào lớp", "1 Làm quen nhanh", "2 Việc thật", "3 `vung`", "3 `dang-len`",
                     "3 `can-do`", "4 Chốt vòng việc"):
            self.assertIn("| " + part + " |", plan, part)

    def test_interactions_v06(self):
        for code in range(1, 66):
            self.assertIn("### T{:02d} ".format(code), self.interactions, code)
        for phrase in ("Đưa lệnh một chạm", "Mở trò chơi", "Đóng trò", "Hết giờ thử thách",
                       "Trao huy hiệu", "Trao sao", "Mở hộp quà", "Đổi kiểu tương tác",
                       "Trao thêm quyền tự làm", "Làm thêm một chút", "từ chối trò chơi",
                       'Khoảnh khắc "À"', 'không bao giờ nói "lên bậc"'):
            self.assertIn(phrase, self.interactions, phrase)

    def test_template_and_scenarios_v06(self):
        for phrase in ("Teacher competency", "one_touch", "Thuc-hanh/",
                       "Đổi kiểu tương tác", "Hết giờ thử thách", "Mở hộp quà",
                       "autonomy_log", "never name a level",
                       "Base directory for this skill"):
            self.assertIn(phrase, self.template, phrase)
        for phrase in ("Teacher competency (v0.6)", "within the first two minutes", "6 rules",
                       "No badge without the behaviour", "refuses a game", "warehouse learner"):
            self.assertIn(phrase, self.scenarios, phrase)

    # --- v0.7: always-open class -----------------------------------------

    def test_always_open_class(self):
        for phrase in (
            "Always-open class (v0.7)", "vòng việc", "Milestones move parts",
            "Pace follows usage", "Hạn mức", "lean", "Tiếp tục", "Auto", "Bypass permissions",
            "sach-tu-hoc.md", "canonical source", "fallback", "vong-viec.json",
            "Xuất phiếu kết quả", "Soạn tin nhờ hỗ trợ", "kèm việc", "real-data mode",
            "việc kế tiếp", "There is no lesson time", "OSER checkpoint",
        ):
            self.assertIn(phrase, self.skill, phrase)
        self.assertNotIn("Mở buổi · {minutes} phút", self.skill)
        self.assertNotIn("Thời lượng* (30 phút default", self.skill)

    def test_loop_reference(self):
        loops = (REFS / "vong-viec.md").read_text(encoding="utf-8")
        for phrase in (
            '"schema": "lop-hoc/vong-viec-1"', "not** an OSER Mission", "never run `oser init`",
            "no Bypass permissions", "Real-data mode", "Outputs are new files",
            "Nothing real is copied into the classroom folder", "Phiếu kết quả",
            "never** G-codes", "Việc kế tiếp", "replaces homework", "Không cần nhắc",
            "Never create reminders", "REUSED_IN_WORK", "cho-xac-nhan", "chap-nhan",
            "never the receiver's name",
        ):
            self.assertIn(phrase, loops, phrase)
        book = (REFS / "sach-tu-hoc.md").read_text(encoding="utf-8")
        for phrase in ("CANONICAL SOURCE", "FALLBACK", "never as a script", "Chế độ quyền",
                       "Quy trình 7 bước", "Giao việc 4 ý", "chọn đúng việc cần xây", "Phụ lục 2. Đáp án"):
            self.assertIn(phrase, book, phrase)
        self.assertNotIn("hinh/hinh-", book)

    def test_scenarios_v07(self):
        for phrase in ("v0.7 cases — always-open class", "Parts move on milestones",
                       "Quick check skips what the learner knows", "A work box waits",
                       "Usage cue at 70 %", "kèm việc", "việc kế tiếp", "Tiếp tục",
                       "Phiếu kết quả", "Soạn tin nhờ hỗ trợ", "self-study book as the fallback"):
            self.assertIn(phrase, self.scenarios, phrase)
        for phrase in ("Always open.", "milestones you reach", "usage limits", "Auto",
                       "Xuất phiếu kết quả", "sach-tu-hoc.md"):
            self.assertIn(phrase, self.template, phrase)

    # --- v0.7.1: deployment risks and getting to know each other ----------

    def test_getting_to_know_each_other(self):
        for phrase in ("Getting to know each other (human standard)", "trainer.json` `learner`",
                       "no job title", "This is not discovery of the job", "When you meet again",
                       "Hạn mức · context", "Kiểm phần học", "Phieu-ket-qua.md"):
            self.assertIn(phrase, self.skill, phrase)
        for phrase in ("Introduce yourself", "Box A — getting to know the learner", "Kinh nghiệm",
                       "Mong muốn", "Điều ngại", "Loại việc", "Người hỗ trợ"):
            self.assertIn(phrase, self.buoi1, phrase)
        for phrase in ("Giáo viên tự giới thiệu", "Làm quen học viên", "Gặp lại"):
            self.assertIn(phrase, self.interactions, phrase)
        self.assertIn("Get to know each other first", self.template)

    def test_bilingual_class_v072(self):
        for phrase in ("`language`: `vi` · `lo`", "ມອບວຽກ —", "stay Vietnamese in both languages"):
            self.assertIn(phrase, self.skill, phrase)
        self.assertIn("Write `language` (`vi` or `lo`) into state right away", self.buoi1)
        for phrase in ("Case F46 — A Lao-speaking learner", "Case F47 — A machine installed before 0.7.2"):
            self.assertIn(phrase, self.scenarios, phrase)

    def test_samples_readable_without_python(self):
        for asset in SAMPLE_ASSETS:
            if asset.endswith(".xlsx"):
                twin = SKILL.parent / "assets" / "mau" / asset.replace(".xlsx", ".csv")
                self.assertTrue(twin.is_file(), twin)
        self.assertIn("no Python", self.capabilities)
        self.assertIn(".csv` twin", self.capabilities)



class StageV08Tests(unittest.TestCase):
    """v0.8: the teacher sets the stage — visual toolbox, interaction order, density, one Write per turn, new cues."""

    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.toolbox = TOOLBOX.read_text(encoding="utf-8")
        cls.template = TEMPLATE.read_text(encoding="utf-8")
        cls.buoi1 = BUOI1.read_text(encoding="utf-8")
        cls.competency = COMPETENCY.read_text(encoding="utf-8")
        cls.interactions = INTERACTIONS.read_text(encoding="utf-8")
        cls.scenarios = SCENARIOS.read_text(encoding="utf-8")
        cls.plugin = PLUGIN.read_text(encoding="utf-8")
        cls.market = json.loads(MARKET.read_text(encoding="utf-8"))

    # --- versions --------------------------------------------------------

    def test_versions(self):
        self.assertIn("version: 0.9.0", self.skill.split("---", 2)[1])
        self.assertIn("What changed in v0.8", self.skill)
        nnc = json.loads(self.plugin)["version"]
        self.assertEqual(nnc, "5.1.0-alpha.2+lophoc.0.9.0")
        entry = {p["name"]: p for p in self.market["plugins"]}["nnc"]
        self.assertEqual(entry["version"], nnc)
        self.assertNotIn("alpha.3", nnc)
        self.assertIn("evaluation cases F1–F57", self.skill)

    # --- the visual toolbox ----------------------------------------------

    def test_toolbox_exists_is_linked_and_has_six_templates(self):
        self.assertTrue(TOOLBOX.is_file())
        self.assertIn("references/day-truc-quan.md", self.skill)
        for heading in ("## 2. Template A — bottom-bar mock-up", "## 3. Template B — concept slide",
                        "## 4. Template C — result explainer", "## 5. Template D — interactive check",
                        "## 6. Template E — 60-second game", "## 7. Template F — podium board"):
            self.assertIn(heading, self.toolbox, heading)
        self.assertIn("sendPrompt('[Lớp học] Trả lời", self.toolbox)
        for colour in ("#008816", "#006D11", "#0B3B16", "#FFEA00", "#C9A800", "#FFFDF0", "#1f2a1f",
                       "#3CC85A", "#4A90E2", "#F5A524"):
            self.assertIn(colour, self.toolbox, colour)
        for font in ("Leelawadee UI", "Phetsarath OT", "Noto Sans Lao"):
            self.assertIn(font, self.toolbox, font)
        for phrase in ("show_widget", "read_me", "Fallback", "One idea per visual", "picture before words",
                       "the learner does", "combine freely", "re-author for", "podium `board`", "≤ 16 KB",
                       "permission mode", "round usage circle", "Trên máy bạn", "Làm theo", "Cách tự kiểm"):
            self.assertIn(phrase.lower(), self.toolbox.lower(), phrase)

    def test_toolbox_svgs_and_widgets_are_valid(self):
        svgs = re.findall(r"```svg\n(.*?)```", self.toolbox, re.S)
        self.assertGreaterEqual(len(svgs), 1)
        for svg in svgs:
            ET.fromstring(svg)  # well-formed
            self.assertLess(len(svg.encode("utf-8")), 16 * 1024)
        # the bottom-bar mock-up has the four areas and the two sides of the bar
        mock = svgs[0]
        for area in ("hl-mode", "hl-model", "hl-effort", "hl-usage"):
            self.assertIn(area, mock, area)
        # the podium board example obeys the board limits and the sanitiser rules
        boards = []
        for block in re.findall(r"```json\n(.*?)```", self.toolbox, re.S):
            try:
                data = json.loads("{" + block + "}")
            except ValueError:
                continue
            if "board" in data:
                boards.append(data["board"])
        self.assertGreaterEqual(len(boards), 1)
        checked = 0
        for board in boards:
            self.assertLessEqual(len(board["title"]), 60)
            self.assertLessEqual(len(board["lines"]), 5)
            for line in board["lines"]:
                self.assertLessEqual(len(line), 90)
            if "…" in board["svg"]:
                continue  # an elided illustration of the whole stage
            ET.fromstring(board["svg"])
            self.assertLessEqual(len(board["svg"].encode("utf-8")), 16 * 1024)
            for banned in ("<script", "foreignObject", "href", "javascript:"):
                self.assertNotIn(banned, board["svg"])
            self.assertIsNone(re.search(r"\son[a-z]+\s*=", board["svg"]))
            checked += 1
        self.assertGreaterEqual(checked, 1)
        # html widgets: tags balanced; scripts are valid JavaScript (when node is available)
        htmls = re.findall(r"```html\n(.*?)```", self.toolbox, re.S)
        self.assertGreaterEqual(len(htmls), 5)
        for html in htmls:
            checker = _Balance()
            checker.feed(html)
            self.assertEqual(checker.stack, [], checker.stack)
            self.assertEqual(checker.errors, [])
            self.assertNotIn("<html", html)
            self.assertNotIn("<!DOCTYPE", html)
        node = shutil.which("node")
        scripts = [body for html in htmls for body in re.findall(r"<script>(.*?)</script>", html, re.S)]
        self.assertGreaterEqual(len(scripts), 2)
        if node:
            for body in scripts:
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "w.js"
                    path.write_text(body, encoding="utf-8")
                    result = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreaterEqual(self.toolbox.count("sendPrompt("), 2)

    # --- the Skill: interaction order, podium knowledge, density, rhythm ---

    def test_skill_interaction_order_and_stage(self):
        for phrase in (
            "Interaction modes — preferred order", "Podium `choices`", "Lesson widget with answer buttons",
            "One-touch", "Native `AskUserQuestion` box", "consent and safety", "the **delegation form**",
            "Never ask what the podium knows", "podium.point", "ask the learner to **do**",
            "Density from minute one", "at least one visual and at least one interaction that is not a native box",
            "first visual and the first interactive check come within your first two turns",
            "one full `Write` of `state.json` per turn", "Turn rhythm",
            "result explainer", "Scaffold ladder", "Three failed rungs on the same point",
            "Never repeat the same question the same way", "help_needed: true",
            "Hơi mệt", "more showing, fewer checks", "at most once per set of choices",
            "Làm theo", "/reload-plugins", "the only slash command the class ever asks for",
            "v0.8 stage fields", "podium.size", "podium.show", "podium.buttons", "timeout_s",
            "svg` ≤ 16 KB", "non-blocking", "Giơ tay · Xin phép · Xin nghỉ stay reachable",
        ):
            self.assertIn(phrase, self.skill, phrase)
        for field in ('"podium"', '"board"', '"choices"'):
            self.assertIn(field, self.skill, field)
        self.assertNotIn("Every choice is a native **AskUserQuestion** box", self.skill)

    def test_new_cues_exact(self):
        for cue in (
            "[Giáo án] Mở lớp · giáo viên {thay\\|co} · chế độ {label} · model {m} · effort {e} · hạn mức 5 giờ {p}% · tuần {q}%",
            "[Giáo án] Chế độ quyền · {label}",
            "[Giáo án] Hết hạn chọn · {id}",
            "[Giáo án] Hộp chờ lâu · {label}",
            "[Lớp học] Chọn · {id} · {label}",
            "[Lớp học] Trả lời · {id} · {value}",
        ):
            self.assertIn(cue, self.skill, cue)
        # the minute cue is gone from the cue table and from the script; only the legacy line mentions it
        self.assertNotIn("| `[Giáo án] Kiểm phần học", self.skill)
        self.assertIn("removed in v0.8", self.skill)
        self.assertNotIn("Kiểm phần học", self.buoi1)
        if DESIGN_V08.is_file():  # cross-check against the v0.8 design when present
            design = DESIGN_V08.read_text(encoding="utf-8")
            for prefix, raw in re.findall(r"`\[(Giáo án|Lớp học)\] ([^`]+)`", design):
                key = raw.split(" · ")[0].split(" {")[0].strip()
                self.assertIn("[{}] {}".format(prefix, key), self.skill, "cue not handled: " + key)

    def test_bypass_and_reload_rules(self):
        for phrase in ("Bypass at opening", "safety point", 'podium.point: "mode"', "the learner switches the mode themselves"):
            self.assertIn(phrase, self.skill, phrase)
        self.assertIn("no `[Giáo án] Mở lớp` cue has arrived", self.skill)
        self.assertIn("Never ask the learner to type a slash command, except that single `/reload-plugins` hint", self.skill)

    # --- references ------------------------------------------------------

    def test_buoi1_playbook_cards_and_no_read_back(self):
        for part in ("Part 0 — Vào lớp", "Part 1 — Làm quen nhanh", "Part 2 — Việc thật của tôi",
                     "Part 3 — Thử thách theo nhịp (by branch)", "Part 4 — Chốt vòng việc"):
            self.assertIn("| Card | " + part + " |", self.buoi1, part)
        for row in ("| Visual |", "| Interaction |", "| Game |", "| Badge |", "| Book |"):
            self.assertGreaterEqual(self.buoi1.count(row), 5, row)
        for phrase in ("Playbook cards (v0.8)", "Never ask what the podium knows", "profile widget",
                       "`podium.point`", "result explainer", "one full `Write`", "Chế độ quyền", "Hộp chờ lâu",
                       "Hết hạn chọn", "Đã chọn Auto"):
            self.assertIn(phrase, self.buoi1, phrase)
        # the opening no longer asks the learner which permission mode is on the bar
        self.assertNotIn('"header": "Chế độ"', self.buoi1)
        self.assertNotIn("Thanh dưới ô nhập đang ghi chế độ quyền nào?", self.buoi1)
        self.assertNotIn("Box B has 4 questions", self.buoi1)

    def test_competency_v08(self):
        text = self.competency.lower()
        for phrase in ("Scaffold ladder", "another everyday example", "three strikes", "help_needed: true",
                       "Never repeat the same question the same way", "Interaction modes — preferred order",
                       "Never ask what the podium knows", "read it back", "Density rule",
                       "The first visual and the first interactive check come within your first two teacher turns",
                       "more showing, fewer checks", "demonstrate on the machine"):
            self.assertIn(phrase.lower(), text, phrase)

    def test_interactions_v08(self):
        for title in ("T57 · Đổi cách nói", "T58 · Chế độ quyền", "T59 · Hết hạn chọn", "T60 · Hộp chờ lâu",
                      "T61 · Chỉ chỗ trên màn hình", "T62 · \"Làm theo\"", "T63 · Giải thích kết quả Claude",
                      "T64 · Thang đỡ bốn nấc", "T65 · Nhắc `/reload-plugins`"):
            self.assertIn("### " + title, self.interactions, title)
        k = self.interactions.split("## K. ", 1)[1].split("## Bảng nhanh", 1)[0]
        lao = [l for l in k.splitlines() if l.startswith("- **Lào:**") and LAO.search(l)]
        self.assertGreaterEqual(len(lao), 8)
        self.assertGreaterEqual(k.count("- **Thầy:**"), 9)
        self.assertGreaterEqual(k.count("- **Cô:**"), 9)
        for phrase in ("tối đa một lần trong một bộ lựa chọn", "Làm theo", "podium.point", "/reload-plugins"):
            self.assertIn(phrase, k, phrase)

    def test_classroom_template_v08(self):
        self.assertNotIn("Every choice is a native AskUserQuestion box", self.template)
        self.assertIn("AskUserQuestion", self.template)
        for phrase in ("Ask in this order", "Never ask what the podium knows", "Density from minute one",
                       "one full `Write`", "/reload-plugins", "result explainer", "three failed rungs",
                       "`[Lớp học] Chọn", "`[Lớp học] Trả lời", "Never ask the learner to type a slash command"):
            self.assertIn(phrase, self.template, phrase)
        guide = (ROOT / "lop-hoc-mau" / "HUONG-DAN.md").read_text(encoding="utf-8")
        self.assertIn("/reload-plugins", guide)

    def test_scenarios_f50_to_f56(self):
        for title in ("Case F50 — Bypass permissions at opening", "Case F51 — The learner cannot find the effort level",
                      "Case F52 — Podium choices time out", "Case F53 — A native box waits 90 seconds",
                      "Case F54 — The learner fails three rungs", "Case F55 — Result explainer after the receipt-to-table job",
                      "Case F56 — The first two turns carry a visual and an interactive check"):
            self.assertIn("## " + title, self.scenarios, title)
        self.assertIn("v0.8 cases — the teacher sets the stage (F50–F56)", self.scenarios)


class ToolRouteTests(unittest.TestCase):
    """v0.7.3: lộ trình làm ra công cụ (sách tự học mục 11) được dạy trong lớp, có rào an toàn."""

    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.route = (SKILL.parent / "references" / "lo-trinh-cong-cu.md").read_text(encoding="utf-8")
        cls.buoi1 = (SKILL.parent / "references" / "buoi-1.md").read_text(encoding="utf-8")
        cls.scenarios = (SKILL.parent / "references" / "scenarios.md").read_text(encoding="utf-8")

    def test_route_is_linked_and_taught(self):
        self.assertIn("references/lo-trinh-cong-cu.md", self.skill)
        self.assertIn("The route to a tool is taught in class", self.skill)
        self.assertNotIn("never built here", self.buoi1)
        self.assertIn("lo-trinh-cong-cu.md", self.buoi1)

    def test_route_follows_book_section_11(self):
        for step in ("Khai thác việc thật", "Khóa bản mô tả", "Chọn cách đơn giản nhất đủ dùng",
                     "Làm và thử nhỏ", "Dùng thật và cải tiến", "mục 11", "Chưa chắc, thử nhỏ trước"):
            self.assertIn(step, self.route)

    def test_prototype_guardrails(self):
        for rule in ("Local only", "Sample or copied data only", "Nothing leaves the machine",
                     "No deploy", "never use credentials", "The learner leads", "/nnc:mission-formation",
                     "Never run OSER init yourself"):
            self.assertIn(rule, self.route)

    def test_scenario_f48(self):
        self.assertIn("Case F48 — Chặng 4", self.scenarios)
        self.assertIn("single-file HTML page", self.scenarios)


class BookMapTests(unittest.TestCase):
    """v0.7.3: động lực dẫn phải dẫn hết sách tự học (mục 1–13), có sổ theo dõi và điều kiện hoàn thành."""

    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.map = (SKILL.parent / "references" / "ban-do-sach.md").read_text(encoding="utf-8")
        cls.book = (SKILL.parent / "references" / "sach-tu-hoc.md").read_text(encoding="utf-8")
        cls.template = (SKILL.parent / "templates" / "classroom-CLAUDE.md").read_text(encoding="utf-8")

    def test_every_book_section_is_mapped(self):
        sections = re.findall(r"^## (\d+)\. ", self.book, re.M)
        self.assertEqual(sections, [str(i) for i in range(1, 14)])
        for n in sections:
            self.assertRegex(self.map, r"\| {} · ".format(n))

    def test_self_test_answers_match_book(self):
        self.assertIn("1b · 2b · 3b · 4c · 5b · 6b · 7a · 8b", self.book)
        self.assertIn("1b · 2b · 3b · 4c · 5b · 6b · 7a · 8b", self.map)

    def test_skill_requires_whole_book(self):
        self.assertIn("references/ban-do-sach.md", self.skill)
        self.assertIn("Lead the whole book", self.skill)
        self.assertIn("`book`", self.skill)
        self.assertIn("Lead the whole self-study book", self.template)
        for phrase in ("Round complete", "book_complete", "open", "taught", "done"):
            self.assertIn(phrase, self.map)


RESEARCH = REFS / "nghien-cuu-tai-lieu.md"


class ResearchV09Tests(unittest.TestCase):
    """v0.9: documents are a research library; the teacher shows the exact place instead of sending the learner searching."""

    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.ref = RESEARCH.read_text(encoding="utf-8")
        cls.template = TEMPLATE.read_text(encoding="utf-8")
        cls.scenarios = SCENARIOS.read_text(encoding="utf-8")

    def test_reference_sections(self):
        self.assertTrue(RESEARCH.is_file())
        for heading in ("## 1. When to research", "## 2. Source order", "## 3. Budget",
                        "## 4. Show, don't send searching", "## 5. The citation line under a visual",
                        "## 6. Which fact wins", "## 7. Safety", "## 8. Record",
                        "## 9. Worked example"):
            self.assertIn(heading, self.ref, heading)
        self.assertRegex(self.ref, LAO, "Lao samples")

    def test_source_order(self):
        order = [self.ref.index(s) for s in ("| 1 | The self-study book", "| 2 | The class library folder",
                                              "| 3 | Company document links", "| 4 | Official product pages")]
        self.assertEqual(order, sorted(order))
        for phrase in ("sach-tu-hoc.md", "`Tai-lieu/`", "only through the document tool this session already has connected",
                       "never ask the learner to sign in", "skip it and tell the **trainer**", "the date you checked"):
            self.assertIn(phrase, self.ref, phrase)

    def test_budget_and_lean_mode(self):
        for phrase in ("At most 3 lookups per turn", "At most one visible line", "70 %", "sources 1 and 2 only",
                       "Thầy tra sách mục 5 · Hình 10"):
            self.assertIn(phrase, self.ref, phrase)

    def test_show_dont_send_patterns(self):
        for phrase in ("Show, don't send searching", "Redraw the figure from its caption", "bottom-bar mock-up",
                       "day-truc-quan.md", "podium.point", "Làm theo", "domain example drawn from the learner's job",
                       "chị mở sách mục 5 mà xem"):
            self.assertIn(phrase, self.ref, phrase)

    def test_citation_format_and_facts_precedence(self):
        self.assertIn("*Nguồn: Sách mục 5 · Hình 10*", self.ref)
        self.assertIn("ແຫຼ່ງ", self.ref)
        for phrase in ("title only", "never a link", "the **book** wins", "the **official page** wins", "news: true",
                       "Never state a fact from memory"):
            self.assertIn(phrase, self.ref, phrase)

    def test_safety_and_sources_used(self):
        for phrase in ("No private data", "Internal links are never shown to the learner", "Nothing is sent out",
                       "read only", "`sources_used`", '"source": "sach"', "`sach` · `tai-lieu` · `nguon` · `web`",
                       "Titles only"):
            self.assertIn(phrase, self.ref, phrase)
        for bad in ("docs." + "google", "drive." + "google", "http://", "https://"):
            self.assertNotIn(bad, self.ref, bad)

    def test_worked_example(self):
        part = self.ref.split("## 9. Worked example", 1)[1]
        for phrase in ("permission mode", "Hình 10", "mục 5", "podium.point: \"mode\"", "bottom-bar mock-up",
                       "*Nguồn: Sách mục 5 · Hình 10*", "Thấy rồi", "sources_used"):
            self.assertIn(phrase, part, phrase)

    def test_skill_links_rule_and_trainer_json(self):
        self.assertIn("references/nghien-cuu-tai-lieu.md", self.skill)
        self.assertIn("What changed in v0.9", self.skill)
        s12 = self.skill.split("## 12. The teacher sets the stage", 1)[1]
        for phrase in ("12.10", "Show, don't send searching", "Source order", "book", "Tai-lieu/NGUON.md",
                       "at most 3 lookups", "70 %"):
            self.assertIn(phrase, s12, phrase)
        self.assertIn("`sources_used: [{date, source:", self.skill)
        self.assertIn("titles only", self.skill)

    def test_nowhere_sends_the_learner_to_the_book(self):
        bad = re.compile(r"point to (its|the exact) section|point to the exact section and figure", re.I)
        for f in [SKILL, TEMPLATE, *sorted(REFS.glob("*.md"))]:
            text = f.read_text(encoding="utf-8")
            self.assertIsNone(bad.search(text), f.name)
        self.assertNotIn("so the learner can follow it alone", self.skill)
        self.assertIn("show that place", self.skill)
        self.assertIn("F57", self.scenarios)
        self.assertIn("Case F57 — The learner cannot find the permission mode", self.scenarios)

    def test_template_line(self):
        for phrase in ("Teaching sources, show don't send searching", "Tai-lieu/NGUON.md", "nghien-cuu-tai-lieu.md",
                       "never send the learner to the book", "At most 3 lookups per turn",
                       "never ask the learner to sign in", "internal links never shown to the learner"):
            self.assertIn(phrase, self.template, phrase)
        self.assertIn("(v0.9)", self.template)


if __name__ == "__main__":
    unittest.main()
