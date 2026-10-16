"""Kiểm gói giao Lớp học NNC: marketplace, phiên bản, thư mục lớp mẫu và thông tin nội bộ."""
import importlib.util
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKET = ROOT / ".claude-plugin" / "marketplace.json"
NNC = ROOT / "plugins" / "nnc" / ".claude-plugin" / "plugin.json"
LOPHOC = ROOT / "plugins" / "lop-hoc" / ".claude-plugin" / "plugin.json"
MAU = ROOT / "lop-hoc-mau"


def _builder():
    spec = importlib.util.spec_from_file_location("build_lop_hoc_mau", ROOT / "tools" / "build_lop_hoc_mau.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class LopHocPackage(unittest.TestCase):
    def setUp(self):
        self.market = json.loads(MARKET.read_text(encoding="utf-8"))
        self.entries = {p["name"]: p for p in self.market["plugins"]}

    def test_one_marketplace_lists_both_plugins_by_relative_path(self):
        self.assertEqual(self.market["name"], "nnc-claude-plugins")
        self.assertEqual(self.entries["nnc"]["source"], "./plugins/nnc")
        self.assertEqual(self.entries["lop-hoc"]["source"], "./plugins/lop-hoc")
        self.assertFalse((ROOT / "mods").exists(), "the old dev marketplace folder must be gone")

    def test_versions_agree_between_manifest_and_marketplace(self):
        for name, path in (("nnc", NNC), ("lop-hoc", LOPHOC)):
            manifest = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["version"], self.entries[name]["version"], name)
        nnc = json.loads(NNC.read_text(encoding="utf-8"))["version"]
        self.assertTrue(nnc.startswith("5.1.0-alpha.2"), nnc)
        self.assertNotIn("alpha.3", nnc)

    def test_classroom_template_is_generated_from_the_skill_template(self):
        b = _builder()
        self.assertEqual((MAU / "CLAUDE.md").read_text(encoding="utf-8"), b.claude_md())
        self.assertIn("Lớp học NNC", (MAU / "CLAUDE.md").read_text(encoding="utf-8"))

    def test_classroom_settings_follow_the_release_branch(self):
        s = json.loads((MAU / ".claude" / "settings.json").read_text(encoding="utf-8"))
        src = s["extraKnownMarketplaces"]["nnc-claude-plugins"]["source"]
        # HTTPS, không SSH: máy học viên thường không có khóa SSH (đã kiểm bằng cài mới 15/10/2026).
        self.assertEqual(src["source"], "git")
        self.assertEqual(src["url"], "https://github.com/VOSYDUNG/nnc-claude-plugins.git")
        # Từ 0.7.2: trỏ vào nhánh phát hành (đẩy tới mỗi tag) và tự cập nhật, để máy đã cài nhận bản mới.
        self.assertEqual(src["ref"], "lop-hoc-release")
        self.assertTrue(s["extraKnownMarketplaces"]["nnc-claude-plugins"]["autoUpdate"])
        self.assertTrue(s["enabledPlugins"]["nnc@nnc-claude-plugins"])
        self.assertTrue(s["enabledPlugins"]["lop-hoc@nnc-claude-plugins"])
        self.assertIn("Edit(./.lop-hoc/**)", s["permissions"]["allow"])
        self.assertIn("Edit(./Phieu-ket-qua.md)", s["permissions"]["allow"])
        for f in ("HUONG-DAN.md", "NGUOI-DUNG-LOP.md", "Thuc-hanh/README.md"):
            self.assertTrue((MAU / f).is_file(), f)

    def test_support_contact_filled_only_in_the_zip(self):
        b = _builder()
        guide = (MAU / "HUONG-DAN.md").read_text(encoding="utf-8")
        self.assertIn("______", guide, "repo keeps the blank support line")
        filled = b.with_support(guide, "Người A hoặc người B")
        self.assertIn("**Người hỗ trợ của bạn:** Người A hoặc người B", filled)
        self.assertNotIn("______________________ (kênh liên hệ", filled)
        self.assertEqual(b.with_support(guide, None), guide)
        self.assertIn(".lien-he-ho-tro.txt", (ROOT / ".gitignore").read_text(encoding="utf-8"))

    def test_no_internal_names_or_links_in_tracked_files(self):
        try:
            files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
        except Exception as e:  # pragma: no cover
            self.skipTest(f"git unavailable: {e}")
        # Tên người và từ nội bộ không được nằm trong repo công khai. Danh sách đặt ở file
        # .noi-bo-tu-cam.txt (mỗi dòng một từ, đã gitignore, chỉ có trên máy người phát hành).
        terms = [r"docs\.google\.com", r"drive\.google\.com", r"WhatsApp"]
        local = ROOT / ".noi-bo-tu-cam.txt"
        if local.is_file():
            terms += [re.escape(t.strip()) for t in local.read_text(encoding="utf-8").splitlines() if t.strip()]
        pattern = re.compile("|".join(terms))
        hits = []
        for rel in files:
            p = ROOT / rel
            if p.suffix.lower() not in {".md", ".py", ".ts", ".tsx", ".json", ".txt"} or not p.is_file():
                continue
            if rel == "tests/test_lop_hoc_package.py":
                continue
            if pattern.search(p.read_text(encoding="utf-8", errors="ignore")):
                hits.append(rel)
        self.assertEqual(hits, [], f"internal info in public files: {hits}")


if __name__ == "__main__":
    unittest.main()
