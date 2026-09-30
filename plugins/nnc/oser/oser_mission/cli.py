"""Thin local interface. No user settings edits, inference, auto-deploy or auto-wake."""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

from . import VERSION
from .adapters import claude_health, claude_lifecycle, claude_usage, codex_health
from .capabilities import admit
from .common import OserError, canonical, digest, epoch, file_hash, load_json_file, require, safe_path, utcnow
from .health import Health, render
from .probe import available_hosts, codex_probe
from .state import Store
from .usage import Usage


BRIEF = """# NNC OSER Mission contract
Read the active Mission with `oser status --json` or the OSER MCP tools.
Complete its approved baseline and acceptance. Proactively choose direct work,
tools, delegation or parallelism within the approved runtime/resource envelope.
Do not change authority or the acceptance denominator to make output look done.
Record evidence, checkpoints and native execution receipts through OSER tools.
Idle while registered work runs is valid. end_turn is not Mission completion.
Host permissions remain authoritative. OSER admission is not a sandbox or model.
Raw logs stay outside parent context; return evidence refs and useful changes.
"""


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))


def input_json(path):
    if path == "-":
        raw = sys.stdin.read(2 * 1024 * 1024 + 1)
        require(len(raw) <= 2 * 1024 * 1024, "INPUT_TOO_LARGE", "stdin JSON exceeds 2 MiB")
        return json.loads(raw)
    return load_json_file(path)


def summary(state):
    return {key: state[key] for key in ("id", "revision", "status", "owner")}


def migration_plan(root):
    """Read only: project-owned rules are never deleted by a guessed migration."""
    root = Path(root).resolve()
    manifest = root / ".claude/oser/project.json"
    if not manifest.is_file():
        return {"legacy_found": False, "writes": 0}
    old = load_json_file(manifest)
    files = ["CLAUDE.md", "AGENTS.md", ".claude/oser/CONTROL-PLANE.md", ".claude/oser/project.json", ".claude/oser/lock.json"]
    inventory = []
    for name in files:
        path = safe_path(root, name)
        if path.is_file():
            inventory.append({"path": name, "sha256": file_hash(path), "action": "REVIEW_ARCHIVE_BEFORE_INIT"})
    return {"legacy_found": True, "schema": old.get("schema"), "writes": 0,
            "inventory": inventory, "admission": "MANUAL_RECONCILIATION_REQUIRED",
            "note": "Preserve legacy ledger/transcripts. Reconcile active v4 role prompts and managed settings before moving the legacy manifest out of its active path. R1 init never deletes legacy/project-owned rules."}


def build_parser():
    ap = argparse.ArgumentParser(prog="oser", description="NNC OSER R1 — Mission, capability, evidence and Health")
    sub = ap.add_subparsers(dest="command")
    sub.add_parser("version")
    sub.add_parser("hosts")
    for name in ("init", "status", "doctor", "apply", "admit", "catalog", "health", "usage", "probe", "serve", "migration-plan", "statusline", "hook"):
        p = sub.add_parser(name)
        p.add_argument("--project", default=os.getcwd(), help="existing project/worktree (canonical state shared through Git common dir)")
        if name in ("status", "doctor", "apply", "admit", "catalog", "usage"):
            p.add_argument("--mission")
        if name == "init":
            p.add_argument("--contract", required=True, help="approved contract JSON file; '-' reads stdin")
            p.add_argument("--event-key")
        if name in ("status", "doctor"):
            p.add_argument("--json", action="store_true")
        if name == "apply":
            p.add_argument("--operation", required=True)
            p.add_argument("--payload", required=True, help="JSON file or '-' (MCP avoids shell serialization)")
            p.add_argument("--revision", required=True, type=int)
            p.add_argument("--event-key", required=True)
            p.add_argument("--actor", required=True)
            p.add_argument("--epoch", required=True, type=int)
        if name == "admit":
            p.add_argument("--request", required=True, help="JSON file or '-'")
        if name == "health":
            p.add_argument("--input", help="omit to read samples; JSON file or '-' to ingest")
            p.add_argument("--adapter", choices=("neutral", "claude-code", "codex-app-server"), default="neutral")
            p.add_argument("--provider")
            p.add_argument("--account")
            p.add_argument("--observed-at", help="source observation timestamp; missing means UNKNOWN, not now")
        if name == "usage":
            p.add_argument("--input", help="optional JSONL file; without it print report")
            p.add_argument("--adapter", choices=("neutral", "claude-code"), default="neutral")
            p.add_argument("--provider")
            p.add_argument("--account")
            p.add_argument("--since")
            p.add_argument("--until")
        if name == "probe":
            p.add_argument("--host", choices=("codex",), required=True)
            p.add_argument("--provider", required=True, help="approved provider binding, never inferred from a model self-report")
            p.add_argument("--account", required=True, help="local account reference, NOT a credential")
            p.add_argument("--timeout", type=int, default=15)
        if name in ("statusline", "hook"):
            p.add_argument("--provider", required=True)
            p.add_argument("--account", required=True)
    return ap


def initialize(project, contract, event_key=None):
    root = Path(project).resolve()
    plan = migration_plan(root)
    require(not plan["legacy_found"], "LEGACY_CONFLICT", "run oser migration-plan; archive/reconcile active v4 instructions explicitly")
    store = Store(root, create=True)
    state = store.create(contract, event_key or "init:" + digest(contract))
    # A discoverable frame, not a team roster or user-global settings change.
    frame = store.root / ".nnc-oser/BOOTSTRAP.md"
    if not frame.exists():
        frame.write_text(BRIEF, encoding="utf-8")
    return dict(summary(state), state_directory=str(store.path.parent),
                instruction_ref=".nnc-oser/BOOTSTRAP.md", instruction_load="ADVISORY",
                message="Reference BOOTSTRAP.md from your host's project instructions after review; no host settings were changed.")


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    if not args.command:
        ap.print_help()
        return 0
    try:
        if args.command == "version":
            print(VERSION)
            return 0
        if args.command == "hosts":
            emit(available_hosts())
            return 0
        if args.command == "migration-plan":
            emit(migration_plan(args.project))
            return 0
        if args.command == "init":
            emit(initialize(args.project, input_json(args.contract), args.event_key))
            return 0
        if args.command == "probe":
            emit(codex_probe(args.project, args.provider, args.account, args.timeout))
            return 0
        if args.command == "serve":
            from .mcp import serve
            serve(args.project, sys.stdin, sys.stdout)
            return 0
        store = Store(args.project)
        if args.command in ("statusline", "hook"):
            payload = input_json("-")
            samples = claude_health(payload, args.provider, args.account, None, "claude-code:statusline-callback")
            if args.command == "hook":
                hint = claude_lifecycle(payload)
                samples = [{"host": "claude-code", "provider": args.provider, "account": args.account,
                            "kind": "runtime", "bucket": "session/" + str(hint["session_ref"]),
                            "source_ref": "claude-code:hook", "observed_at": utcnow(), "ttl_seconds": 300,
                            "hint": hint}]
            for sample in samples:
                Health(store).put(sample)
            if args.command == "statusline":
                percentages = [str(s.get("used_percent")) + "% " + s["bucket"] for s in samples if s.get("used_percent") is not None]
                print("OSER | " + (" | ".join(percentages) if percentages else "quota/context UNKNOWN") + " | source age UNKNOWN")
            # Hooks never emit a block instruction, wake, or claim Mission DONE.
            return 0
        if args.command == "health":
            if args.input:
                value = input_json(args.input)
                if args.adapter == "neutral":
                    samples = value if isinstance(value, list) else [value]
                else:
                    fn = claude_health if args.adapter == "claude-code" else codex_health
                    samples = fn(value, args.provider, args.account, args.observed_at, "import:" + args.input)
                emit({"samples": [Health(store).put(s) for s in samples], "model_calls": 0})
            else:
                emit(Health(store).read())
            return 0
        mission = args.mission
        if not mission:
            missions = store.list()
            require(len(missions) == 1, "MISSION_REQUIRED", "select --mission when there is not exactly one Mission")
            mission = missions[0]["id"]
        if args.command == "apply":
            result = store.apply(mission, args.operation, input_json(args.payload), args.revision,
                                 args.event_key, args.actor, args.epoch)
            emit(summary(result))
        elif args.command in ("status", "doctor"):
            view = store.view(mission)
            health = Health(store).read()
            if args.command == "doctor":
                with store.connection() as db:
                    integrity = db.execute("PRAGMA quick_check").fetchone()[0]
                view["store_integrity"] = integrity
                view["legacy_conflict"] = migration_plan(store.root)["legacy_found"]
                view["live_conformance"] = "PENDING"
            if args.json:
                emit(dict(view, health=health))
            else:
                print(render(view, health))
            if args.command == "doctor" and (view["store_integrity"] != "ok" or view["legacy_conflict"] or view["authority_status"] == "DRIFT" or view["policy_violations"]):
                return 2
        elif args.command == "catalog":
            emit(store.read(mission)["catalog"] or {"evidence_state": "UNKNOWN", "models": []})
        elif args.command == "admit":
            state = store.read(mission)
            result = admit(state["catalog"], state["policy"], input_json(args.request))
            emit(result)
            return 0 if result["status"] == "ADMITTED" else 2
        elif args.command == "usage":
            ledger = Usage(store)
            if args.input:
                since = epoch(args.since) if args.since else None
                until = epoch(args.until) if args.until else None
                require(since is None or until is None or since <= until, "INVALID_TIME", "since must precede until")
                with Path(args.input).open(encoding="utf-8-sig") as stream:
                    for line in stream:
                        require(len(line) <= 2 * 1024 * 1024, "INPUT_TOO_LARGE", "JSONL record exceeds 2 MiB")
                        if not line.strip():
                            continue
                        row = json.loads(line)
                        if since is not None or until is not None:
                            at = epoch(row.get("timestamp"))
                            if (since is not None and at < since) or (until is not None and at >= until):
                                continue
                        record = claude_usage(row, args.provider, args.account) if args.adapter == "claude-code" else row
                        if record is not None:
                            ledger.put(mission, record)
            emit(ledger.report(mission))
        return 0
    except (OserError, OSError, ValueError, TypeError, KeyError, sqlite3.Error) as exc:
        error = {"error": getattr(exc, "code", "INPUT_OR_STORAGE_ERROR"), "message": str(exc)}
        if args.command in ("statusline", "hook"):
            print("OSER observer unavailable: " + error["error"], file=sys.stderr)
            return 0
        emit(error)
        return 2
