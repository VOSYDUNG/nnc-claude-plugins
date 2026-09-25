#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NNC OSER — installer · updater · migrator · doctor · work ledger · metrics for a project's control plane.

    oser install  --project DIR --name NAME --authority-repo OWNER/REPO --authority-entry PATH [...]
    oser update   [--project DIR] [--dry-run] [--force]
    oser migrate  [--project DIR] [--dry-run] [--force]      # NNC-AI-OSer 1.x / NNC OSER 2.0 layout -> 3.x
    oser doctor   [--project DIR] [--manifest FILE] [--json]
    oser status   [--project DIR]
    oser ledger   add FILE|- | check          [--project DIR]
    oser metrics  [--project DIR] [--wave ID] [--json]
    oser root     [--project DIR] [--session ID]
    oser quota    [--project DIR] [--ngay N | --tu D --den D] [--tat-ca] [--api-reference]
    oser version

Python 3.8+, standard library only.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from oser_core import doctor, engine, ledger, metrics  # noqa: E402
from oser_core.manifest import build_state, get, load, mode_spec, root_model  # noqa: E402
from oser_core.transcripts import Index, observed_models, project_transcript_dirs, quota_main  # noqa: E402
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
    print("active roles: %s · subagents: %s" % (", ".join(spec.get("active_roles", [])) or "-", spec["subagents"]))
    print("BUILD: %s" % build_state(m))
    obs = observed_models(root)
    print("Root: EXPECTED=%s OBSERVED=%s" % (root_model(m), obs["root_last"][0] if obs["root_last"] else "(no transcript)"))
    print("Governor: preferred=%s · one fresh session per wave" % (get(m, "operating_model.governor.preferred_model") or "(not declared)"))
    print("Workers/verifiers: execution plan per packet (model × effort × context × session × parallelism × verification)")
    return 0


def cmd_ledger(root, argv):
    m, _ = load(root)
    if not argv or argv[0] == "check":
        st = ledger.fold(ledger.read(root), m)
        for e in st["errors"]:
            print("  ERROR " + e)
        print("ledger: %d wave(s) · %d packet(s) · %d error(s)" % (len(st["waves"]), len(st["packets"]), len(st["errors"])))
        return 2 if st["errors"] else 0
    if argv[0] == "add" and len(argv) == 2:
        raw = sys.stdin.read() if argv[1] == "-" else open(argv[1], encoding="utf-8").read()
        evs = json.loads(raw)
        for ev in (evs if isinstance(evs, list) else [evs]):
            errs = ledger.append(root, ev, m)
            if errs:
                print("REJECTED %s: %s" % (ev.get("event"), "; ".join(errs)))
                return 2
            print("appended %s %s" % (ev.get("event"), ev.get("packetId") or ev.get("waveId") or ""))
        return 0
    print("usage: oser ledger add FILE|- | check")
    return 1


def cmd_metrics(root, wave, as_json):
    m, _ = load(root)
    r = metrics.compute(root, m, wave)
    r["resources"] = metrics.resources(root)
    if as_json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0
    fmt = lambda v: "n/a" if v is None else ("%.3f" % v if isinstance(v, float) else str(v))
    print("waves ROOT_ACCEPTED=%d · packets terminal=%d accepted=%d" % (r["waves_root_accepted"], r["packets_terminal"], r["packets_accepted"]))
    print("A VERIFIED_RESULT_COST   work/accepted packet=%s · work/accepted wave=%s"
          % (fmt(r["VERIFIED_RESULT_COST"]["per_accepted_packet_work_mean"]), fmt(r["VERIFIED_RESULT_COST"]["per_root_accepted_wave_work_mean"])))
    print("B FIRST_PASS_ACCEPT_RATE %s" % fmt(r["FIRST_PASS_ACCEPT_RATE"]))
    print("C REWORK_AMPLIFICATION   %s" % fmt(r["REWORK_AMPLIFICATION"]))
    print("D ROOT_CONTEXT_GROWTH    %s tokens/wave (%d measured, %d handoff)" % (
        fmt(r["ROOT_CONTEXT_GROWTH"]["per_accepted_wave_mean_tokens"]), r["ROOT_CONTEXT_GROWTH"]["waves_measured"],
        r["ROOT_CONTEXT_GROWTH"]["root_handoffs"]))
    print("E CONTEXT_ISOLATION_GAIN %s× below-Root tokens per Root token" % fmt(r["CONTEXT_ISOLATION_GAIN"]))
    d = r["DEFECT_CONTAINMENT"]
    print("F DEFECT_CONTAINMENT     %s (before=%d after=%d)" % (fmt(d["rate"]), d["before_integration"], d["after_acceptance"]))
    print("G FABLE_LEVERAGE         %s accepted packets / M Fable work tokens" % fmt(r["FABLE_LEVERAGE"]["accepted_packets_per_M_fable_work"]))
    e = r["ESCALATION_EFFICIENCY"]
    print("H ESCALATION_EFFICIENCY  %s (%d/%d resolved, work mean %s)" % (fmt(e["rate"]), e["resolved"], e["escalated"], fmt(e["work_mean"])))
    print("\nPLAN BENCHMARK (declared model × effort; verified-result outcomes)")
    print("  %-44s %4s %6s %6s %6s %10s %9s %9s %6s" % ("plan", "att", "1stPass", "rework", "vDefect", "work", "thinking", "wall_s", "final"))
    for p in r["plans"]:
        print("  %-44s %4d %6s %6d %6d %10d %9d %9.0f %6d" % (
            " · ".join(str(x) for x in p["key"])[:44], p["attempts"], fmt(p["first_pass_rate"]), p["rework"],
            p["verify_defects"], p["work"], p["thinking"], p["wall_s"], p["final_accepted"]))
    for u in r["unknown"]:
        print("  UNKNOWN " + u)
    for e in r["ledger_errors"]:
        print("  LEDGER ERROR " + e)
    return 0


def cmd_root(root, session):
    idx = Index(project_transcript_dirs(root, all_machines=True))
    sessions = [session] if session else sorted({s for (s, a) in idx.by_exec if a == ""})
    for s in sessions:
        ser = idx.series(s)
        if not ser:
            continue
        print("root session %s · turns %d · prompt size first=%s last=%s max=%s (tokens)" % (
            s[:8], len(ser), "{:,}".format(ser[0][1]), "{:,}".format(ser[-1][1]), "{:,}".format(max(v for _, v in ser))))
    hand = ledger.fold(ledger.read(root))["handoffs"]
    for h in hand:
        print("handoff %s → %s at %s · %s" % (h["fromSessionId"][:8], h["toSessionId"][:8], h.get("at"), h["reason"]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="oser", description="NNC OSER control plane")
    sub = ap.add_subparsers(dest="cmd")
    for name in ("update", "migrate", "doctor", "status", "quota", "install", "ledger", "metrics", "root"):
        p = sub.add_parser(name)
        p.add_argument("--project", default=os.getcwd())
        if name in ("update", "migrate", "install"):
            p.add_argument("--dry-run", action="store_true")
        if name in ("update", "migrate"):
            p.add_argument("--force", action="store_true", help="rewrite hand-edited generated artifacts")
        if name == "doctor":
            p.add_argument("--manifest", help="evaluate the tree against this manifest instead of the project's own")
            p.add_argument("--json", action="store_true")
        if name == "metrics":
            p.add_argument("--wave")
            p.add_argument("--json", action="store_true")
        if name == "root":
            p.add_argument("--session")
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
    if args.cmd == "ledger":
        return cmd_ledger(root, rest)
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
        elif args.cmd == "metrics":
            return cmd_metrics(root, args.wave, args.json)
        elif args.cmd == "root":
            return cmd_root(root, args.session)
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
