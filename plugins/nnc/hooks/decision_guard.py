#!/usr/bin/env python3
"""Guard OSER material decision cards; unrelated AskUserQuestion stays native."""
from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "oser"))

from oser_mission.common import OserError  # noqa: E402
from oser_mission.decision import ask_user_payload, load_matching_decision  # noqa: E402


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))


def main():
    try:
        raw = sys.stdin.read(2 * 1024 * 1024 + 1)
        if len(raw) > 2 * 1024 * 1024:
            return 0
        event = json.loads(raw)
        if event.get("tool_name") != "AskUserQuestion":
            return 0
        tool_input = event.get("tool_input") or {}
        questions = tool_input.get("questions")
        if not isinstance(questions, list):
            return 0
        cwd = event.get("cwd")
        if not isinstance(cwd, str) or not cwd:
            return 0

        for question in questions:
            if not isinstance(question, dict) or not isinstance(question.get("question"), str):
                continue
            card = load_matching_decision(cwd, question["question"])
            if card is None or card["level"] not in ("D2", "D3"):
                continue
            expected = ask_user_payload(card)["questions"][0]
            incoming = dict(question)
            incoming.pop("header", None)
            comparable = dict(expected)
            comparable.pop("header", None)
            if incoming != comparable:
                deny("OSER material decision %s is missing its locked consequence-oriented option shape. "
                     "Rebuild AskUserQuestion from the saved Decision Card; do not ask the user to infer architecture risk."
                     % card["id"])
                return 0
        return 0
    except (OserError, OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        # Fail open for unrelated/corrupt local state. A generic Claude session
        # must not break because an optional OSER Decision Card is unavailable.
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
