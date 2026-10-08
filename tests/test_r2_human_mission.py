# -*- coding: utf-8 -*-
import json
import os
import shutil
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
OSER_HOME = os.path.join(os.path.dirname(HERE), "plugins", "nnc", "oser")
import sys
sys.path.insert(0, OSER_HOME)
HOOK = os.path.join(os.path.dirname(HERE), "plugins", "nnc", "hooks", "decision_guard.py")

from oser_core.util import sha as _legacy_sha  # noqa: F401
from oser_mission.common import OserError
from oser_mission.decision import ask_user_payload, render_decision, validate_decision, write_decision
from oser_mission.desk import desk_view, validate_desk
from oser_mission.formation import formation_view, validate_formation


class TestR2DecisionContract(unittest.TestCase):
    def card(self, level="D2"):
        option = {
            "id": "native",
            "label": "Dùng tính năng có sẵn",
            "consequence": "Ra thử nghiệm nhanh, ít phần phải tự vận hành.",
            "gain": "Thời gian tới giá trị ngắn.",
            "tradeoff": "Ít tùy biến hơn.",
            "risk": "Có thể thiếu một số hành vi đặc thù.",
            "reversibility": "easy",
            "data_impact": "Không mở thêm nguồn dữ liệu ngoài phạm vi đã duyệt.",
            "recurring_cost": "Theo gói nền tảng hiện hành.",
            "maintenance": "Thấp; chủ yếu cấu hình và nội dung.",
            "next_action": "Pilot một fanpage với bộ câu hỏi thật.",
            "recommended": True,
        }
        return {
            "id": "DEC-CHATBOT-001",
            "level": level,
            "topic": "Cách triển khai chatbot",
            "question": "Nên đi đường nào trước?",
            "options": [option, dict(option, id="custom", label="Tự xây bot", recommended=False,
                                     consequence="Linh hoạt hơn nhưng phải build và bảo trì.")],
            "uncertainty_option": {
                "id": "investigate",
                "label": "Tôi chưa chắc — điều tra/thử trước",
                "consequence": "Chưa khóa kiến trúc; giảm bất định trước.",
                "next_action": "Chạy một thử nghiệm giới hạn rồi quay lại quyết định.",
            },
        }

    def test_material_decision_requires_full_consequences_and_uncertainty_path(self):
        value = self.card()
        parsed = validate_decision(value)
        self.assertEqual(parsed["level"], "D2")
        self.assertIn("Tôi chưa chắc", render_decision(value))
        bad = self.card()
        del bad["options"][0]["risk"]
        with self.assertRaisesRegex(OserError, "option.risk"):
            validate_decision(bad)
        bad = self.card()
        bad.pop("uncertainty_option")
        with self.assertRaises(OserError) as ctx:
            validate_decision(bad)
        self.assertEqual(ctx.exception.code, "UNCERTAINTY_PATH_REQUIRED")

    def test_d3_cannot_turn_recommendation_into_approval(self):
        value = self.card("D3")
        value["approval_required"] = False
        with self.assertRaises(OserError) as ctx:
            validate_decision(value)
        self.assertEqual(ctx.exception.code, "APPROVAL_REQUIRED")

    def test_decision_ids_are_immutable_versions(self):
        root = tempfile.mkdtemp(prefix="oser-r2-decision-")
        try:
            os.mkdir(os.path.join(root, ".nnc-oser"))
            first = write_decision(root, self.card())
            self.assertTrue(first["changed"])
            again = write_decision(root, self.card())
            self.assertFalse(again["changed"])
            changed = self.card()
            changed["question"] = "Đổi câu hỏi?"
            with self.assertRaises(OserError) as ctx:
                write_decision(root, changed)
            self.assertEqual(ctx.exception.code, "DECISION_EXISTS")
        finally:
            shutil.rmtree(root, ignore_errors=True)


class TestR2Formation(unittest.TestCase):
    def card(self):
        return TestR2DecisionContract().card()

    def test_intake_can_start_from_vague_problem(self):
        value = {"id": "F-NONTECH-001", "stage": "INTAKE", "actor": "nontech-user",
                 "problem": "Muốn chatbot cho fanpage nhưng chưa biết bắt đầu từ đâu"}
        view = formation_view(validate_formation(value))
        self.assertFalse(view["mission_ready"])
        self.assertEqual(view["research_candidates"], 0)

    def test_research_stage_requires_current_reality_and_candidate_evidence(self):
        value = {
            "id": "F-NONTECH-001", "stage": "RESEARCH", "actor": "nontech-user",
            "problem": "Muốn chatbot cho fanpage",
            "current_reality": {"workflow": "Nhân viên trả lời comment/inbox thủ công",
                                "pain": "Lặp lại nhiều câu hỏi", "current_tools": ["Meta Business Suite"],
                                "constraints": ["Người dùng non-tech"]},
            "research": []
        }
        with self.assertRaises(OserError) as ctx:
            validate_formation(value)
        self.assertEqual(ctx.exception.code, "RESEARCH_REQUIRED")

    def test_mission_ready_is_draft_not_approval(self):
        value = {
            "id": "F-NONTECH-001", "stage": "MISSION_READY", "actor": "nontech-user",
            "problem": "Muốn chatbot cho fanpage",
            "current_reality": {"workflow": "Nhân viên trả lời comment/inbox thủ công",
                                "pain": "Lặp lại nhiều câu hỏi", "current_tools": ["Meta Business Suite"],
                                "constraints": ["Người dùng non-tech"]},
            "research": [{"candidate": "Meta automation", "class": "native",
                          "fit": "Có thể xử lý FAQ cơ bản", "source_ref": "official-meta-doc",
                          "unknowns": ["Có đủ cho free-text hay không"]}],
            "decision": self.card(),
            "selected_direction": "Pilot native/configuration trước",
            "unresolved": [],
            "mission_draft": {"goal": "Giảm phản hồi thủ công trên một fanpage",
                              "owner": "nontech-user",
                              "authority_refs": ["current-faq", "brand-policy"],
                              "acceptance_outcomes": ["FAQ chuẩn được trả lời đúng", "Không chắc thì chuyển người"]}
        }
        view = formation_view(validate_formation(value))
        self.assertTrue(view["mission_ready"])
        self.assertIn("not approval", view["note"])


class TestR2DecisionHook(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="oser-r2-hook-")
        os.mkdir(os.path.join(self.root, ".nnc-oser"))
        self.card = TestR2DecisionContract().card()
        write_decision(self.root, self.card)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def run_hook(self, question):
        payload = {"tool_name": "AskUserQuestion", "tool_input": {"questions": [question]},
                   "cwd": self.root}
        return subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                              text=True, capture_output=True, check=False)

    def test_matching_material_card_allows_exact_consequence_shape(self):
        question = ask_user_payload(self.card)["questions"][0]
        out = self.run_hook(question)
        self.assertEqual(out.returncode, 0)
        self.assertEqual(out.stdout.strip(), "")

    def test_matching_material_card_blocks_lossy_question(self):
        question = ask_user_payload(self.card)["questions"][0]
        question = json.loads(json.dumps(question))
        question["options"][0]["description"] = "Nhanh và tiện."
        out = self.run_hook(question)
        self.assertEqual(out.returncode, 0)
        decision = json.loads(out.stdout)
        self.assertEqual(decision["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_unrelated_native_question_is_not_intercepted(self):
        question = {"question": "Màu nào?", "header": "Màu",
                    "options": [{"label": "Xanh", "description": "Xanh"},
                                {"label": "Đỏ", "description": "Đỏ"}],
                    "multiSelect": False}
        out = self.run_hook(question)
        self.assertEqual(out.stdout.strip(), "")


class TestR2CleanDesk(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="oser-r2-desk-")
        for path, content in {
            "docs/prd.md": "current prd",
            "docs/architecture.md": "current architecture",
            "workspace/state.md": "state",
            "drafts/idea.md": "draft",
            "evidence/uat.md": "pass",
            "history/prd-v1.md": "old",
        }.items():
            full = os.path.join(self.root, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as stream:
                stream.write(content)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def manifest(self):
        return {
            "authority": [
                {"id": "prd-v2", "scope": "product.requirements", "path": "docs/prd.md"},
                {"id": "arch-v1", "scope": "technical.architecture", "path": "docs/architecture.md"},
            ],
            "state": [{"id": "state", "path": "workspace/state.md"}],
            "drafts": [{"id": "idea", "path": "drafts/idea.md"}],
            "evidence": [{"id": "uat", "path": "evidence/uat.md"}],
            "history": [{"id": "old-prd", "path": "history/prd-v1.md"}],
        }

    def test_clean_desk_loads_only_current_authority_and_state_by_default(self):
        parsed = validate_desk(self.root, self.manifest())
        view = desk_view(parsed)
        self.assertEqual(view["load_policy"]["default"], ["authority", "state"])
        self.assertEqual(view["load_policy"]["audit_only"], ["history"])
        self.assertEqual(len(parsed["authority"]), 2)

    def test_same_file_cannot_be_draft_and_authority(self):
        value = self.manifest()
        value["drafts"] = [{"id": "bad", "path": "docs/prd.md"}]
        with self.assertRaises(OserError) as ctx:
            validate_desk(self.root, value)
        self.assertEqual(ctx.exception.code, "DESK_CLASS_CONFLICT")

    def test_two_locked_authorities_cannot_claim_same_scope(self):
        value = self.manifest()
        value["authority"][1]["scope"] = "product.requirements"
        with self.assertRaises(OserError) as ctx:
            validate_desk(self.root, value)
        self.assertEqual(ctx.exception.code, "AUTHORITY_CONFLICT")


if __name__ == "__main__":
    unittest.main()
