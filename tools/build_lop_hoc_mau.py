"""Dựng thư mục lớp học mẫu `lop-hoc-mau/` từ nguồn duy nhất (template trong Skill).

Chạy: python tools/build_lop_hoc_mau.py [--tag lop-hoc-v0.6.0] [--zip ĐƯỜNG_DẪN.zip]
`CLAUDE.md` của lớp luôn sinh ra từ templates/classroom-CLAUDE.md; test kiểm tra hai bản khớp nhau.
"""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "plugins" / "nnc" / "skills" / "work-first-learning" / "templates" / "classroom-CLAUDE.md"
OUT = ROOT / "lop-hoc-mau"
REPO = "VOSYDUNG/nnc-claude-plugins"
MARKETPLACE = "nnc-claude-plugins"
DEFAULT_TAG = "lop-hoc-v0.6.0"


def claude_md() -> str:
    return "# Lớp học NNC\n\n" + TEMPLATE.read_text(encoding="utf-8").split("\n", 1)[1].lstrip("\n")


def settings(tag: str) -> dict:
    return {
        "extraKnownMarketplaces": {
            MARKETPLACE: {"source": {"source": "github", "repo": REPO, "ref": tag}}
        },
        "enabledPlugins": {f"nnc@{MARKETPLACE}": True, f"lop-hoc@{MARKETPLACE}": True},
        "permissions": {"allow": ["Edit(./.lop-hoc/**)", "Edit(./Thuc-hanh/**)"]},
    }


def build(tag: str) -> None:
    (OUT / ".claude").mkdir(parents=True, exist_ok=True)
    (OUT / "Thuc-hanh").mkdir(exist_ok=True)
    (OUT / "CLAUDE.md").write_text(claude_md(), encoding="utf-8")
    (OUT / ".claude" / "settings.json").write_text(
        json.dumps(settings(tag), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_zip(dest: Path) -> None:
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob("*")):
            if p.is_file():
                z.write(p, Path("Lop-hoc-NNC") / p.relative_to(OUT))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default=DEFAULT_TAG)
    ap.add_argument("--zip")
    a = ap.parse_args()
    build(a.tag)
    if a.zip:
        make_zip(Path(a.zip))
    print(f"lop-hoc-mau built for {REPO}@{a.tag}")
