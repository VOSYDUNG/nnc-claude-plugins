"""Checks for the two screenshot scripts of the classroom Skill (Lop hoc NNC v0.10).

Static checks run everywhere. The runtime checks run on Windows only and never capture the
screen: they feed `danh-dau.ps1` a generated PNG and exercise `chup-man-hinh.ps1 -Clean`.
"""
from pathlib import Path
import os
import random
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "nnc" / "skills" / "work-first-learning" / "assets" / "scripts"
CHUP = SCRIPTS / "chup-man-hinh.ps1"
DANH = SCRIPTS / "danh-dau.ps1"

WINDOWS = sys.platform == "win32"
LAO_LABEL = "".join(chr(c) for c in (0x0E81, 0x0EBB, 0x0E94, 0x0E9A, 0x0EC8, 0x0EAD, 0x0E99, 0x0E99, 0x0EB5, 0x0EC9))


def _code(path):
    """Script text without comment-based help and # comments (so words in docs cannot satisfy a check)."""
    text = path.read_text(encoding="ascii")
    text = re.sub(r"<#.*?#>", "", text, flags=re.S)
    return "\n".join(re.sub(r"(^|\s)#(?!C9A800|FFEA00|1f2a1f|7A6700).*$", "", ln) for ln in text.splitlines())


def _param_block(path):
    text = path.read_text(encoding="ascii")
    text = re.sub(r"<#.*?#>", "", text, flags=re.S)
    return re.search(r"param\((.*?)\n\)", text, re.S).group(1)


def _png(path, width, height, seed=7):
    """A noisy RGB PNG written with the standard library only (no Pillow)."""
    rng = random.Random(seed)
    rows = []
    for y in range(height):
        row = bytearray(rng.getrandbits(8) for _ in range(width * 3))
        # a light band so there is something box-like to mark
        for x in range(width):
            if 100 <= x < 260 and 200 <= y < 232:
                row[x * 3:x * 3 + 3] = b"\xf0\xf0\xf0"
        rows.append(b"\x00" + bytes(row))
    raw = b"".join(rows)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))
    Path(path).write_bytes(png)


def _ps(script, *args, cwd):
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), *args]
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8",
                          errors="replace", stdin=subprocess.DEVNULL, timeout=180)


class CaptureScriptStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = CHUP.read_text(encoding="ascii")  # ASCII only: Windows PowerShell 5.1 reads BOM-less files as ANSI
        cls.code = _code(CHUP)
        cls.params = _param_block(CHUP)

    def test_parameters(self):
        self.assertRegex(self.params, r"\[string\]\$Out\s*=\s*'\.lop-hoc\\man-hinh\.png'")
        self.assertRegex(self.params, r"\[switch\]\$Clean")

    def test_process_is_dpi_aware(self):
        self.assertIn("SetProcessDpiAwarenessContext", self.code)
        self.assertIn("SetProcessDPIAware", self.code)
        self.assertIn("MakeDpiAware()", self.code)
        # made aware before the window rectangle is read
        self.assertLess(self.code.index("[NncShot.Win]::MakeDpiAware()"), self.code.index("FindWindows($pids)"))

    def test_only_the_claude_window_is_found(self):
        self.assertRegex(self.code, r"ProcessName -ieq 'Claude'")
        for api in ("EnumWindows", "IsWindowVisible", "IsIconic", "GetWindowThreadProcessId"):
            self.assertIn(api, self.code, api)
        self.assertIn("Cloaked", self.code)
        self.assertIn("b.Area.CompareTo(a.Area)", self.code, "largest area first")
        self.assertIn("ERR no-window", self.code)
        self.assertIn("ERR minimised", self.code)
        self.assertGreaterEqual(self.code.count("exit 1"), 4)

    def test_rect_prefers_dwm_frame_with_getwindowrect_fallback(self):
        self.assertIn("DwmGetWindowAttribute", self.code)
        self.assertRegex(self.code, r"DwmGetWindowAttribute\(h, 9, out r, 16\)")  # DWMWA_EXTENDED_FRAME_BOUNDS
        self.assertIn("GetWindowRect", self.code)
        self.assertLess(self.code.index("DwmGetWindowAttribute(h, 9"), self.code.index("return GetWindowRect(h, out r)"))

    def test_copies_only_the_window_rect_never_the_desktop(self):
        self.assertEqual(self.code.count("CopyFromScreen"), 1)
        m = re.search(r"CopyFromScreen\(([^)]*)\)", self.code)
        self.assertIn("$x0, $y0", m.group(1), "source corner is the window's own corner")
        self.assertNotRegex(self.code, r"CopyFromScreen\(\s*0\s*,\s*0")
        for bad in ("PrimaryScreen", "AllScreens", "Screen]::", "SystemInformation", "WorkingArea",
                    "Forms.Screen", "Add-Type -AssemblyName System.Windows.Forms", "keybd_event", "PrintScreen"):
            self.assertNotIn(bad, self.code, bad)
        # the bitmap is as big as the window rectangle, not as the screen
        self.assertRegex(self.code, r"New-Object System\.Drawing\.Bitmap\(\$w, \$h,")

    def test_covered_window_uses_printwindow_of_that_window_only(self):
        self.assertIn("PrintWindow", self.code)
        self.assertIn("TopmostAt", self.code)
        self.assertIn("ERR covered", self.code)

    def test_output_contract(self):
        self.assertRegex(self.code, r'Write-Output "OK \$\{w\}x\$\{h\} \$target"')
        self.assertIn("Format]::Png", self.code.replace("ImageFormat]::Png", "Format]::Png"))
        self.assertIn("ERR capture-failed", self.code)

    def test_clean_removes_only_the_two_files_and_exits(self):
        clean = self.code.split("if ($Clean) {", 1)[1].split("\n}\n", 1)[0]
        self.assertIn("man-hinh.png", clean)
        self.assertIn("chi-tay.jpg", clean)
        self.assertIn("exit 0", clean)
        self.assertNotIn("-Recurse", clean)
        self.assertLess(self.code.index("if ($Clean)"), self.code.index("Add-Type -TypeDefinition"),
                        "-Clean must not load capture code")


class MarkScriptStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = DANH.read_text(encoding="ascii")
        cls.code = _code(DANH)
        cls.params = _param_block(DANH)

    def test_parameters_and_defaults(self):
        self.assertRegex(self.params, r"\[string\]\$In\s*=\s*'\.lop-hoc\\man-hinh\.png'")
        self.assertRegex(self.params, r"\[string\]\$Out\s*=\s*'\.lop-hoc\\chi-tay\.jpg'")
        self.assertRegex(self.params, r"\[Parameter\(Mandatory = \$true\)\]\[string\]\$Box")
        self.assertRegex(self.params, r"\[string\]\$Label\s*=\s*''")
        self.assertRegex(self.params, r"\[int\]\$MaxWidth\s*=\s*960")
        self.assertRegex(self.params, r"\[int\]\$MaxBytes\s*=\s*92160")

    def test_drawing_spec(self):
        self.assertIn("#FFEA00", self.code)
        self.assertIn("#C9A800", self.code)
        self.assertRegex(self.code, r"\$pad = 6\b")
        self.assertRegex(self.code, r"Pen\(\$dark, \[single\]\(5 \* \$k\)\)")  # 5 px border
        self.assertIn("FromArgb(85", self.code)  # semi-transparent fill
        self.assertIn("FillPolygon", self.code)  # arrow
        self.assertIn("DrawString", self.code)  # label
        self.assertIn("RoundPath", self.code)  # rounded border and pill
        self.assertIn("$room", self.code)  # arrow comes from the side with more room

    def test_fonts_for_vietnamese_and_lao(self):
        self.assertIn("'Segoe UI'", self.code)
        self.assertIn("'Leelawadee UI'", self.code)
        self.assertIn("0x0E80", self.code)
        self.assertIn("0x0EFF", self.code)

    def test_crop_resize_and_jpeg_size_loop(self):
        # v0.13: vung cat sat hon (400x240) de vung can bam hien to tren buc; co ban do nho ca cua so.
        self.assertRegex(self.code, r"\$minW = \[Math\]::Min\(\[double\]\$MinCropW, \$W\)")
        self.assertRegex(self.code, r"\$minH = \[Math\]::Min\(\[double\]\$MinCropH, \$H\)")
        self.assertRegex(self.params, r"\[int\]\$MinCropW\s*=\s*400")
        self.assertRegex(self.params, r"\[int\]\$MinCropH\s*=\s*240")
        self.assertRegex(self.params, r"\[switch\]\$NoMap")
        self.assertIn("function Add-Map", self.code)
        self.assertIn("Add-Map $final", self.code)
        self.assertRegex(self.code, r"foreach \(\$q in 85, 80, 75, 70, 65, 60, 55, 50, 45, 40\)")
        self.assertIn("EncoderParameter([System.Drawing.Imaging.Encoder]::Quality", self.code)
        self.assertIn("$bytes.Length -le $MaxBytes", self.code)
        self.assertIn("HighQualityBicubic", self.code)
        self.assertIn("[Math]::Min($MaxWidth, $cropped.Width)", self.code)

    def test_output_contract_and_errors(self):
        self.assertRegex(self.code, r'Write-Output "OK \$\{fw\}x\$\{fh\} \$\(\$bytes\.Length\) \$outPath"')
        for err in ("ERR $msg", "bad-box", "no-input", "bad-input", "too-big"):
            self.assertIn(err, self.code, err)

    def test_works_on_a_copy_and_never_uses_the_desktop(self):
        self.assertIn("Format32bppArgb", self.code)
        self.assertNotIn("CopyFromScreen", self.code)
        self.assertNotIn("PrimaryScreen", self.code)
        self.assertNotIn("Forms.Screen", self.code)


@unittest.skipUnless(WINDOWS, "PowerShell 5.1 and System.Drawing are Windows only")
class ScriptsRunOnWindowsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="nnc-shot-"))
        (cls.tmp / ".lop-hoc").mkdir()
        _png(cls.tmp / ".lop-hoc" / "man-hinh.png", 1000, 600)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_marks_a_box_and_stays_within_the_size_budget(self):
        out = self.tmp / ".lop-hoc" / "chi-tay.jpg"
        out.unlink(missing_ok=True)
        r = _ps(DANH, "-Box", "100,200,160,32", "-Label", "Chế độ quyền: bấm vào đây", cwd=self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertRegex(r.stdout.strip(), r"^OK \d+x\d+ \d+ .*chi-tay\.jpg$")
        self.assertTrue(out.is_file())
        size = out.stat().st_size
        self.assertLessEqual(size, 92160)
        self.assertEqual(out.read_bytes()[:3], b"\xff\xd8\xff", "a JPEG")
        m = re.match(r"OK (\d+)x(\d+) (\d+) ", r.stdout.strip())
        self.assertLessEqual(int(m.group(1)), 960)
        self.assertEqual(int(m.group(3)), size)

    def test_lao_label_and_a_tight_budget(self):
        out = self.tmp / "tight.jpg"
        r = _ps(DANH, "-Box", "100,200,160,32", "-Label", LAO_LABEL, "-Out", str(out), "-MaxBytes", "40960", cwd=self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(out.is_file())
        self.assertLessEqual(out.stat().st_size, 40960)

    def test_the_input_picture_is_left_untouched(self):
        src = self.tmp / ".lop-hoc" / "man-hinh.png"
        before = src.read_bytes()
        r = _ps(DANH, "-Box", "10,10,50,20", "-Out", str(self.tmp / "other.jpg"), cwd=self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(src.read_bytes(), before)

    def test_bad_box_is_a_clear_error(self):
        r = _ps(DANH, "-Box", "5000,5000,10,10", "-Out", str(self.tmp / "no.jpg"), cwd=self.tmp)
        self.assertEqual(r.returncode, 1)
        self.assertTrue(r.stdout.startswith("ERR bad-box"), r.stdout)
        r = _ps(DANH, "-Box", "1,2,3", cwd=self.tmp)
        self.assertEqual(r.returncode, 1)
        self.assertTrue(r.stdout.startswith("ERR bad-box"), r.stdout)

    def test_clean_deletes_the_two_files_and_nothing_else(self):
        d = Path(tempfile.mkdtemp(prefix="nnc-clean-"))
        try:
            (d / ".lop-hoc").mkdir()
            for n in ("man-hinh.png", "chi-tay.jpg", "state.json"):
                (d / ".lop-hoc" / n).write_bytes(b"x")
            r = _ps(CHUP, "-Clean", cwd=d)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue(r.stdout.startswith("OK cleaned 2"), r.stdout)
            self.assertFalse((d / ".lop-hoc" / "man-hinh.png").exists())
            self.assertFalse((d / ".lop-hoc" / "chi-tay.jpg").exists())
            self.assertTrue((d / ".lop-hoc" / "state.json").exists())
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
