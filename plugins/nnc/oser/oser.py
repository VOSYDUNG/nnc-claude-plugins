#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NNC OSER — installer · updater · migrator · doctor for a project's Claude Code control plane.

    oser install  --project DIR --name NAME --authority-repo OWNER/REPO --authority-entry PATH [...]
    oser update   [--project DIR] [--dry-run] [--force]
    oser migrate  [--project DIR] [--dry-run] [--force]      # NNC-AI-OSer 1.0 layout -> 2.x
    oser doctor   [--project DIR] [--manifest FILE] [--json]
    oser status   [--project DIR]
    oser quota    [--project DIR] [--ngay N | --tu D --den D] [--tat-ca]
    oser version

Python 3.8+, standard library only. The project's `.claude/oser/project.json` is the declaration;
OSER renders the GENERATED parts from it and records provenance in `.claude/oser/lock.json`.
"""
import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from oser_core import doctor, engine  # noqa: E402
from oser_core.manifest import capability_state, load, mode_spec, model_mapping  # noqa: E402
from oser_core.transcripts import observed_models, quota_main  # noqa: E402
from oser_core.util import plugin_version  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _print_plan(plan, dry):
    for kind, path, why in plan.actions:
        print("  %s%-16s %s  — %s" % ("(dry) " if dry else "", kind, path, why))
    for n in plan.notes:
        print("  note: " + n)
    print("%d change(s)%s" % (len(plan.actions), " planned" if dry else ""))


def cmd_status(root):
    m, errors = load(root)
    if m is None or errors:
        print("no valid manifest:", "; ".join(errors))
        return 1
    spec = mode_spec(m)
    print("project %s · phase %s · mode %s (%s)" % (m["project"]["name"], m["phase"]["label"], m["mode"], spec["status"]))
    print("actors: %s · subagents: %s · audit: %s" % (", ".join(spec.get("actors", [])) or "-", spec["subagents"], spec["audit"]))
    for k, v in sorted(capability_state(m).items()):
        print("  capability %-12s %s" % (k, v))
    maps = model_mapping(m)
    obs = observed_models(root)
    print("ROOT model: EXPECTED=%s OBSERVED=%s" % (maps["root"], obs["root_last"][0] if obs["root_last"] else "(no transcript)"))
    for k, v in sorted(maps.items()):
        if k != "root":
            print("  model class %-15s -> %s" % (k, v))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="oser", description="NNC OSER control plane")
    sub = ap.add_subparsers(dest="cmd")
    for name in ("update", "migrate", "doctor", "status", "quota", "install"):
        p = sub.add_parser(name)
        p.add_argument("--project", default=os.getcwd())
        if name in ("update", "migrate", "install"):
            p.add_argument("--dry-run", action="store_true")
        if name in ("update", "migrate"):
            p.add_argument("--force", action="store_true", help="rewrite hand-edited generated artifacts")
        if name == "doctor":
            p.add_argument("--manifest", help="evaluate the tree against this manifest instead of the project's own")
            p.add_argument("--json", action="store_true")
        if name == "install":
            p.add_argument("--name", required=True)
            p.add_argument("--authority-repo", required=True)
            p.add_argument("--authority-entry", required=True)
            p.add_argument("--authority-ref", default="main")
            p.add_argument("--authority-hint", help="path of a local clone RELATIVE to the project")
            p.add_argument("--baseline")
            p.add_argument("--phase-id", default="setup")
            p.add_argument("--phase-label", default="SETUP")
            p.add_argument("--language", default="vi")
    sub.add_parser("version")
    args, rest = ap.parse_known_args(argv)
    if args.cmd == "version":
        print(plugin_version())
        return 0
    if args.cmd is None:
        ap.print_help()
        return 1
    root = os.path.abspath(args.project)
    if args.cmd == "quota":
        return quota_main(rest, root)
    if rest:
        ap.error("unrecognized arguments: %s" % " ".join(rest))
    try:
        if args.cmd == "update":
            _print_plan(engine.update(root, dry_run=args.dry_run, force=args.force), args.dry_run)
        elif args.cmd == "migrate":
            _print_plan(engine.migrate(root, dry_run=args.dry_run, force=args.force), args.dry_run)
        elif args.cmd == "install":
            _print_plan(engine.install(root, args.name, args.authority_repo, args.authority_entry, args.authority_ref,
                                       args.authority_hint, args.baseline, args.phase_id, args.phase_label,
                                       args.language, dry_run=args.dry_run), args.dry_run)
        elif args.cmd == "status":
            return cmd_status(root)
        elif args.cmd == "doctor":
            rep = doctor.run(root, args.manifest)
            if args.json:
                c = rep.counts()
                print(json.dumps({"facts": rep.facts, "findings": rep.findings, "counts": c}, ensure_ascii=False, indent=2))
                return 2 if c["critical"] else 1 if c["warning"] else 0
            return doctor.print_report(rep)
    except engine.Blocked as e:
        print("BLOCKED: %s" % e)
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
