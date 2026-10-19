"""Kiểm gói giao Lớp học NNC: marketplace, phiên bản, thư mục lớp mẫu và thông tin nội bộ."""
import importlib.util
import json
import re
import subprocess
import tempfile
import unittest
import zipfile
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
        # Từ 0.12: tắt bản tóm tắt suy nghĩ của mô hình (nó nói "Tôi…" ngoài khung thầy).
        self.assertIs(s["showThinkingSummaries"], False)
        self.assertIs(_builder().settings()["showThinkingSummaries"], False)
        for f in ("HUONG-DAN.md", "NGUOI-DUNG-LOP.md", "Thuc-hanh/README.md"):
            self.assertTrue((MAU / f).is_file(), f)

    def test_nnc_version_carries_lophoc_0120_and_guide_has_reload_hint(self):
        nnc = json.loads(NNC.read_text(encoding="utf-8"))["version"]
        self.assertEqual(nnc, "5.1.0-alpha.2+lophoc.0.12.1")
        self.assertEqual(self.entries["nnc"]["version"], nnc)
        guide = (MAU / "HUONG-DAN.md").read_text(encoding="utf-8")
        self.assertIn("Chưa thấy bục giảng: gõ `/reload-plugins`", guide)
        claude_md = (MAU / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("/reload-plugins", claude_md)
        self.assertNotIn("Every choice is a native AskUserQuestion box", claude_md)

    def test_zip_ships_cai_dat_with_the_installer_runbook(self):
        b = _builder()
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "lop.zip"
            b.make_zip(dest, None, None)
            with zipfile.ZipFile(dest) as z:
                self.assertIn("Lop-hoc-NNC/CAI-DAT.md", z.namelist())
                zipped = z.read("Lop-hoc-NNC/CAI-DAT.md").decode("utf-8")
                zs = json.loads(z.read("Lop-hoc-NNC/.claude/settings.json").decode("utf-8"))
        text = (MAU / "CAI-DAT.md").read_text(encoding="utf-8")
        self.assertEqual(zipped, text)
        self.assertIs(zs["showThinkingSummaries"], False)
        self.assertIn("showThinkingSummaries", text, "installer step 5 must verify the key")
        self.assertTrue(text.startswith("# CÀI ĐẶT LỚP HỌC NNC"), "title must tell any Claude to read this first")
        for phrase in ("hãy cài đặt lớp học NNC cho tôi", "lop-hoc-release", "--scope project", "/reload-plugins",
                       "nnc@nnc-claude-plugins", "lop-hoc@nnc-claude-plugins", "2.1.286", "git ls-remote",
                       "known_marketplaces.json", "AskUserQuestion", "Lop-hoc-NNC-v*.zip", "claude.exe",
                       "Lớp đang chờ giáo viên", "Vào lớp", "Ctrl+Shift+M", "Never ask them to type a command"):
            self.assertIn(phrase, text, phrase)
        self.assertTrue("Expand-Archive" in text or "zipfile" in text)
        self.assertIn("NEVER delete or overwrite `.lop-hoc\\`", text)
        self.assertRegex(text, r"Never remove a marketplace or uninstall a plugin")
        self.assertRegex(text, r"Bypass permissions")
        # hand-over loop: five learner steps, in order
        order = [text.index(s) for s in ("### 6.1 ", "### 6.2 ", "### 6.3 ", "### 6.4 ", "### 6.5 ", "### 6.6 ")]
        self.assertEqual(order, sorted(order))
        for phrase in ("+ New", "This computer", "Open folder", "tin cậy thư mục", "Auto", "Manual", "thầy", "cô"):
            self.assertIn(phrase, text, phrase)
        self.assertRegex(text, r"[຀-໿]", "short Lao samples")
        guide = (MAU / "HUONG-DAN.md").read_text(encoding="utf-8")
        self.assertIn("hãy cài đặt lớp học NNC cho tôi", guide)
        self.assertIn("Kéo file ZIP", guide)

    def test_support_contact_filled_only_in_the_zip(self):
        b = _builder()
        guide = (MAU / "HUONG-DAN.md").read_text(encoding="utf-8")
        self.assertIn("______", guide, "repo keeps the blank support line")
        filled = b.with_support(guide, "Người A hoặc người B")
        self.assertIn("**Người hỗ trợ của bạn:** Người A hoặc người B", filled)
        self.assertNotIn("______________________ (kênh liên hệ", filled)
        self.assertEqual(b.with_support(guide, None), guide)
        self.assertIn(".lien-he-ho-tro.txt", (ROOT / ".gitignore").read_text(encoding="utf-8"))

    def test_tai_lieu_folder_is_public_and_has_no_nguon(self):
        readme = (MAU / "Tai-lieu" / "README.md").read_text(encoding="utf-8")
        self.assertIn("kho tra cứu", readme)
        self.assertIn("không cần mở", readme)
        self.assertFalse((MAU / "Tai-lieu" / "NGUON.md").exists(), "NGUON.md is injected only into the ZIP")
        self.assertIn(".nguon-tai-lieu.md", (ROOT / ".gitignore").read_text(encoding="utf-8"))
        self.assertIn("show, don't send searching", (MAU / "CLAUDE.md").read_text(encoding="utf-8").lower().replace("show don't", "show, don't"))

    def test_zip_includes_nguon_only_when_the_file_exists(self):
        b = _builder()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            nguon = tmp / "nguon.md"
            nguon.write_text("# Danh muc thu nghiem" + chr(10) + "- Tai lieu A: muc dich thu" + chr(10), encoding="utf-8")
            with_file = tmp / "co-nguon.zip"
            self.assertIs(b.make_zip(with_file, None, b.sources_path(str(nguon))), True)
            without = tmp / "khong-nguon.zip"
            self.assertIs(b.make_zip(without, None, b.sources_path(str(tmp / "khong-co.md"))), False)
            with zipfile.ZipFile(with_file) as z:
                names = z.namelist()
                self.assertIn("Lop-hoc-NNC/Tai-lieu/NGUON.md", names)
                self.assertIn("Lop-hoc-NNC/Tai-lieu/README.md", names)
                self.assertEqual(names.count("Lop-hoc-NNC/Tai-lieu/NGUON.md"), 1)
                self.assertIn("Tai lieu A", z.read("Lop-hoc-NNC/Tai-lieu/NGUON.md").decode("utf-8"))
            with zipfile.ZipFile(without) as z:
                self.assertNotIn("Lop-hoc-NNC/Tai-lieu/NGUON.md", z.namelist())
                self.assertIn("Lop-hoc-NNC/Tai-lieu/README.md", z.namelist())
        self.assertFalse((MAU / "Tai-lieu" / "NGUON.md").exists())

    def test_cli_nguon_flag_builds_zip_with_nguon(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            nguon = tmp / "nguon.md"
            nguon.write_text("# Thu nghiem" + chr(10), encoding="utf-8")
            dest = tmp / "lop.zip"
            out = subprocess.run(["python", str(ROOT / "tools" / "build_lop_hoc_mau.py"), "--zip", str(dest),
                                  "--nguon", str(nguon)], cwd=ROOT, capture_output=True, text=True,
                                 stdin=subprocess.DEVNULL, check=True).stdout
            self.assertIn("included", out)
            with zipfile.ZipFile(dest) as z:
                self.assertIn("Lop-hoc-NNC/Tai-lieu/NGUON.md", z.namelist())
        self.assertFalse((MAU / "Tai-lieu" / "NGUON.md").exists())

    def test_update_guidance_is_the_current_method(self):
        # L05 (0.12.1): gói không còn cách cập nhật cũ (giải nén đè, gỡ nguồn bằng tay); bản lớn = ZIP mới + câu cài đặt.
        for name in ("HUONG-DAN.md", "NGUOI-DUNG-LOP.md"):
            text = (MAU / name).read_text(encoding="utf-8")
            for old in ("0.7.2", "giải nén gói mới", "marketplace remove"):
                self.assertNotIn(old, text, f"{name}: {old}")
            update = text.split("## Cập nhật", 1)[1].split("\n## ", 1)[0]
            self.assertIn("hãy cài đặt lớp học NNC cho tôi", update, name)
            self.assertIn(".lop-hoc" if name == "NGUOI-DUNG-LOP.md" else "chỗ học", update, name)

    def test_package_is_lf_on_every_machine(self):
        # L07 (0.12.1): máy có core.autocrlf=true từng checkout gói ra CRLF và đóng ZIP CRLF.
        self.assertIn("lop-hoc-mau/** text eol=lf", (ROOT / ".gitattributes").read_text(encoding="utf-8"))
        for p in MAU.rglob("*"):
            if p.is_file() and p.suffix in (".md", ".json"):
                self.assertNotIn(b"\r\n", p.read_bytes(), p.relative_to(ROOT).as_posix())
        builder = (ROOT / "tools" / "build_lop_hoc_mau.py").read_text(encoding="utf-8")
        self.assertEqual(builder.count('encoding="utf-8", newline="\\n")'), 2,"the builder writes CLAUDE.md and settings.json with LF")

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
