#!/usr/bin/env python3
"""NNC OSER R1 entry point with warned, non-destructive v4 compatibility."""
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def legacy_requested(argv):
    if not argv:
        return False
    if argv[0] in ("legacy", "install", "update", "migrate", "ledger", "metrics", "root", "quota"):
        return True
    if argv[0] in ("status", "doctor"):
        root = Path.cwd()
        if "--project" in argv and argv.index("--project") + 1 < len(argv):
            root = Path(argv[argv.index("--project") + 1])
        return (root / ".claude/oser/project.json").is_file() and not (root / ".nnc-oser/state.sqlite3").exists()
    return False


if __name__ == "__main__":
    argv = sys.argv[1:]
    if legacy_requested(argv):
        print("LEGACY V4: historical compatibility only. Quantitative metrics are INVALIDATED; "
              "do not use them as a test baseline. No R1 state is modified.", file=sys.stderr)
        from legacy import main
        sys.exit(main(argv[1:] if argv[:1] == ["legacy"] else argv))
    from oser_mission.cli import main
    sys.exit(main(argv))
