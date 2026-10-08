#!/usr/bin/env python3
"""Claude Code hook adapter for local anonymous NNC OSER experience events."""
from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "oser"))

from oser_mission.decision import load_matching_decision  # noqa: E402
from oser_mission.experience import from_claude_hook  # noqa: E402


def main():
    try:
        raw = sys.stdin.read(2 * 1024 * 1024 + 1)
        if len(raw) > 2 * 1024 * 1024:
            return 0
        payload = json.loads(raw)
        cwd = payload.get("cwd")
        if isinstance(cwd, str) and cwd:
            from_claude_hook(cwd, payload, load_matching_decision)
    except Exception:
        # Telemetry must never break a user workflow.
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
