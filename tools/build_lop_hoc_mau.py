"""Dựng thư mục lớp học mẫu `lop-hoc-mau/` từ nguồn duy nhất (template trong Skill).

Chạy: python tools/build_lop_hoc_mau.py [--ref lop-hoc-release] [--zip ĐƯỜNG_DẪN.zip] [--support "…"] [--nguon ĐƯỜNG_DẪN]
`CLAUDE.md` của lớp luôn sinh ra từ templates/classroom-CLAUDE.md; test kiểm tra hai bản khớp nhau.

Cập nhật (từ 0.7.2): gói trỏ vào nhánh phát hành `lop-hoc-release` (nhánh này được đẩy tới đúng commit
của mỗi tag lop-hoc-vX.Y.Z) và bật autoUpdate, nên máy đã cài nhận bản mới mà không cần gói mới.

Người hỗ trợ: tên người không nằm trong repo công khai. Khi đóng ZIP, dòng "Người hỗ trợ của bạn" trong
HUONG-DAN.md được điền từ --support, hoặc từ file .lien-he-ho-tro.txt (đã gitignore, chỉ trên máy người phát hành).

Danh mục liên kết tài liệu nội bộ (từ 0.9): khi đóng ZIP, nếu có file .nguon-tai-lieu.md (đã gitignore, ở gốc repo trên
máy người phát hành) hoặc --nguon ĐƯỜNG_DẪN, file được chép vào ZIP thành Lop-hoc-NNC/Tai-lieu/NGUON.md. Không bao giờ
ghi vào lop-hoc-mau/. Không có file thì ZIP không có NGUON.md và giáo viên bỏ qua nguồn này.
"""
from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "plugins" / "nnc" / "skills" / "work-first-learning" / "templates" / "classroom-CLAUDE.md"
OUT = ROOT / "lop-hoc-mau"
REPO = "VOSYDUNG/nnc-claude-plugins"
MARKETPLACE = "nnc-claude-plugins"
RELEASE_REF = "lop-hoc-release"
SUPPORT_FILE = ROOT / ".lien-he-ho-tro.txt"
SOURCES_FILE = ROOT / ".nguon-tai-lieu.md"
SOURCES_ARC = "Lop-hoc-NNC/Tai-lieu/NGUON.md"
SUPPORT_LINE = re.compile(r"^\*\*Người hỗ trợ của bạn:\*\*.*$", re.M)


def claude_md() -> str:
    return "# Lớp học NNC\n\n" + TEMPLATE.read_text(encoding="utf-8").split("\n", 1)[1].lstrip("\n")


def settings(ref: str = RELEASE_REF) -> dict:
    return {
        "extraKnownMarketplaces": {
            # Nguồn git qua HTTPS: dạng rút gọn owner/repo clone bằng SSH, máy học viên thường không có khóa SSH.
            # autoUpdate: marketplace bên thứ ba mặc định tắt; bật để máy đã cài tự nhận bản phát hành mới.
            MARKETPLACE: {"source": {"source": "git", "url": f"https://github.com/{REPO}.git", "ref": ref}, "autoUpdate": True}
        },
        "enabledPlugins": {f"nnc@{MARKETPLACE}": True, f"lop-hoc@{MARKETPLACE}": True},
        "permissions": {"allow": ["Edit(./.lop-hoc/**)", "Edit(./Thuc-hanh/**)", "Edit(./Phieu-ket-qua.md)"]},
    }


def build(ref: str) -> None:
    (OUT / ".claude").mkdir(parents=True, exist_ok=True)
    (OUT / "Thuc-hanh").mkdir(exist_ok=True)
    (OUT / "Tai-lieu").mkdir(exist_ok=True)
    (OUT / "CLAUDE.md").write_text(claude_md(), encoding="utf-8")
    (OUT / ".claude" / "settings.json").write_text(
        json.dumps(settings(ref), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def support_text(arg: str | None) -> str | None:
    if arg:
        return arg.strip()
    if SUPPORT_FILE.is_file():
        return SUPPORT_FILE.read_text(encoding="utf-8").strip() or None
    return None


def with_support(guide: str, who: str | None) -> str:
    if not who:
        return guide
    return SUPPORT_LINE.sub(lambda _: f"**Người hỗ trợ của bạn:** {who}", guide, count=1)


def sources_path(arg: str | None = None) -> Path | None:
    """File danh mục liên kết tài liệu: --nguon nếu có, không thì .nguon-tai-lieu.md ở gốc repo; không có file thì None."""
    p = Path(arg) if arg else SOURCES_FILE
    return p if p.is_file() else None


def make_zip(dest: Path, who: str | None = None, nguon: Path | None = None) -> bool:
    """Đóng ZIP; trả về True nếu đã chèn Tai-lieu/NGUON.md."""
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob("*")):
            if not p.is_file():
                continue
            arc = Path("Lop-hoc-NNC") / p.relative_to(OUT)
            if arc.as_posix() == SOURCES_ARC:
                continue  # NGUON.md chỉ đi vào ZIP từ file nguồn ở máy người phát hành
            if p.name == "HUONG-DAN.md" and p.parent == OUT:
                z.writestr(str(arc).replace("\\", "/"), with_support(p.read_text(encoding="utf-8"), who).encode("utf-8"))
            else:
                z.write(p, arc)
        if nguon is not None:
            z.writestr(SOURCES_ARC, nguon.read_text(encoding="utf-8"))
    return nguon is not None


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", "--tag", dest="ref", default=RELEASE_REF)
    ap.add_argument("--zip")
    ap.add_argument("--support", help="dòng Người hỗ trợ điền vào HUONG-DAN.md trong ZIP (không ghi vào repo)")
    ap.add_argument("--nguon", help="file danh mục liên kết tài liệu chép vào ZIP thành Tai-lieu/NGUON.md (mặc định .nguon-tai-lieu.md ở gốc repo; không ghi vào repo)")
    a = ap.parse_args()
    build(a.ref)
    if a.zip:
        who = support_text(a.support)
        src = sources_path(a.nguon)
        if a.nguon and src is None:
            raise SystemExit(f"--nguon: không thấy file {a.nguon}")
        included = make_zip(Path(a.zip), who, src)
        print("support line:", "filled" if who else "left blank")
        print("Tai-lieu/NGUON.md:", "included" if included else "not included (no source file)")
    print(f"lop-hoc-mau built for {REPO}@{a.ref}")
