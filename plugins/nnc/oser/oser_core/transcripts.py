# -*- coding: utf-8 -*-
"""Read Claude Code transcripts as RAW usage evidence.

Primary unit is raw tokens straight from the transcript (`runtime.json › units`). An API-price-weighted
figure exists only behind `--api-reference` and is never subscription cost.
"""
import datetime
import glob
import io
import json
import os
from collections import defaultdict

from .util import claude_home, load_catalog, model_generation, transcript_slug

FIELDS = ("input", "output", "thinking", "cache_read", "cache_creation")
_API = {"opus": (15.0, 75.0), "fable": (15.0, 75.0), "sonnet": (3.0, 15.0), "haiku": (0.8, 4.0)}


def zero():
    return {k: 0 for k in FIELDS + ("turns", "work")}


def add(acc, v):
    for k in FIELDS + ("turns", "work"):
        acc[k] += v.get(k, 0)
    return acc


def vec(usage):
    u = usage or {}
    v = {"input": u.get("input_tokens", 0) or 0, "output": u.get("output_tokens", 0) or 0,
         "thinking": (u.get("output_tokens_details") or {}).get("thinking_tokens", 0) or 0,
         "cache_read": u.get("cache_read_input_tokens", 0) or 0,
         "cache_creation": u.get("cache_creation_input_tokens", 0) or 0, "turns": 1}
    v["work"] = v["input"] + v["cache_creation"] + v["output"]
    return v


def family(model):
    g = model_generation(model or "")
    return g[0] if g else "other"


def project_transcript_dirs(project_root, all_machines=False):
    base = os.path.join(claude_home(), "projects")
    own = os.path.join(base, transcript_slug(project_root))
    if not os.path.isdir(base):
        return []
    name = transcript_slug(os.path.basename(os.path.abspath(project_root)))
    siblings = [os.path.join(base, d) for d in os.listdir(base) if d.endswith("-" + name)]
    if all_machines:
        return sorted(set(siblings + ([own] if os.path.isdir(own) else [])))
    if os.path.isdir(own):
        return [own]
    return siblings[:1] if len(siblings) == 1 else []


def events(dirs):
    """Every assistant turn with usage: dict(ts, session, agent, side, model, effort, branch, v)."""
    for d in dirs:
        for f in glob.glob(os.path.join(d, "**", "*.jsonl"), recursive=True):
            try:
                with io.open(f, encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        if '"assistant"' not in line:
                            continue
                        try:
                            ev = json.loads(line)
                        except ValueError:
                            continue
                        if ev.get("type") != "assistant":
                            continue
                        msg = ev.get("message") or {}
                        model = msg.get("model") or "?"
                        if model.startswith("<") or not msg.get("usage"):
                            continue
                        yield {"ts": ev.get("timestamp") or "", "session": ev.get("sessionId") or "?",
                               "agent": ev.get("agentId") or "", "side": bool(ev.get("isSidechain")),
                               "model": model, "effort": ev.get("effort") or "", "branch": ev.get("gitBranch") or "",
                               "v": vec(msg["usage"])}
            except OSError:
                continue


class Index:
    """Usage indexed by execution identity (sessionId, agentId); agentId '' = the session's main thread."""

    def __init__(self, dirs):
        self.dirs = dirs
        self.by_exec = defaultdict(list)
        for e in events(dirs):
            self.by_exec[(e["session"], e["agent"] if e["side"] else "")].append(e)
        for k in self.by_exec:
            self.by_exec[k].sort(key=lambda e: e["ts"])

    def usage(self, session, agent="", since=None, until=None):
        acc = zero()
        models, efforts = defaultdict(int), defaultdict(int)
        for e in self.by_exec.get((session, agent or ""), []):
            if (since and e["ts"] < since) or (until and e["ts"] > until):
                continue
            add(acc, e["v"])
            models[e["model"]] += e["v"]["work"]
            efforts[e["effort"]] += 1
        acc["models"] = dict(models)
        acc["efforts"] = dict(efforts)
        return acc

    def known(self, session, agent=""):
        return (session, agent or "") in self.by_exec

    def prompt_size_at(self, session, ts):
        """Context the Root received on its last main-thread turn at or before `ts` (prompt_size proxy)."""
        best = None
        for e in self.by_exec.get((session, ""), []):
            if e["ts"] <= ts:
                best = e
        if best is None:
            return None
        v = best["v"]
        return v["input"] + v["cache_read"] + v["cache_creation"]

    def series(self, session):
        return [(e["ts"], e["v"]["input"] + e["v"]["cache_read"] + e["v"]["cache_creation"])
                for e in self.by_exec.get((session, ""), [])]


def observed_models(project_root):
    """What actually ran. ROOT = newest main-thread turn."""
    dirs = project_transcript_dirs(project_root)
    root_last, root, sub = None, defaultdict(int), defaultdict(int)
    for e in events(dirs):
        if e["side"]:
            sub[e["model"]] += 1
        else:
            root[e["model"]] += 1
            if root_last is None or e["ts"] > root_last[1]:
                root_last = (e["model"], e["ts"], e["session"][:8])
    return {"dirs": dirs, "root_last": root_last, "root": dict(root), "sub": dict(sub),
            "all": sorted(set(root) | set(sub))}


def api_reference(model, v):
    gi, go = _API.get(family(model), _API["sonnet"])
    return (v["input"] * gi + v["output"] * go + v["cache_read"] * gi * 0.1 + v["cache_creation"] * gi * 1.25) / 1e6


def iso_week(ts):
    try:
        d = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return "?"
    y, w, _ = d.isocalendar()
    return "%d-W%02d" % (y, w)


def quota_main(args, project_root):
    """`oser quota` — raw usage: per model, per effort, per region (root/sub), per ISO week (all models vs Fable)."""
    since = until = None
    tat_ca = api = False
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--ngay":
            since = (datetime.date.today() - datetime.timedelta(days=int(args[i + 1]) - 1)).isoformat(); i += 2
        elif a == "--tu":
            since = args[i + 1]; i += 2
        elif a == "--den":
            until = args[i + 1] + "T99"; i += 2
        elif a == "--tat-ca":
            tat_ca = True; i += 1
        elif a == "--api-reference":
            api = True; i += 1
        else:
            i += 1
    dirs = project_transcript_dirs(project_root, all_machines=tat_ca)
    if not dirs:
        print("No transcript folder for", project_root)
        return 1
    by = {k: defaultdict(zero) for k in ("model", "effort", "region", "week_all", "week_fable")}
    ref = defaultdict(float)
    n = 0
    for e in events(dirs):
        if (since and e["ts"][:10] < since) or (until and e["ts"] > until):
            continue
        n += 1
        add(by["model"][e["model"]], e["v"])
        add(by["effort"][e["effort"] or "(none)"], e["v"])
        add(by["region"]["subagent" if e["side"] else "root"], e["v"])
        wk = iso_week(e["ts"])
        add(by["week_all"][wk], e["v"])
        if family(e["model"]) == "fable":
            add(by["week_fable"][wk], e["v"])
        if api:
            ref[e["model"]] += api_reference(e["model"], e["v"])
    print("Source:", " + ".join(os.path.basename(d) for d in dirs), "| turns", n,
          ("| since %s" % since) if since else "")
    print("Units: raw tokens from transcripts (%s)." % load_catalog("runtime.json")["units"]["work_tokens"])
    hdr = "  %-26s %7s %13s %11s %11s %13s %12s"
    row = "  %-26s %7d %13s %11s %11s %13s %12s"
    f = "{:,}".format
    for title, key in (("BY MODEL", "model"), ("BY EFFORT", "effort"), ("BY REGION", "region"),
                       ("WEEKLY · ALL MODELS", "week_all"), ("WEEKLY · FABLE (nested in all-models)", "week_fable")):
        print("\n=== %s ===" % title)
        print(hdr % ("", "turns", "work", "output", "thinking", "cache_read", "cache_write"))
        for k, v in sorted(by[key].items(), key=lambda kv: (-kv[1]["work"]) if key in ("model", "effort", "region") else kv[0]):
            print(row % (str(k)[:26], v["turns"], f(v["work"]), f(v["output"]), f(v["thinking"]), f(v["cache_read"]),
                         f(v["cache_creation"])))
    for wk, v in sorted(by["week_all"].items()):
        fv = by["week_fable"].get(wk, zero())
        if v["work"]:
            print("  %s Fable share of work tokens: %.1f%%" % (wk, 100.0 * fv["work"] / v["work"]))
    print("\nSubscription caps (weekly all-models / nested Fable) are UI-only: not derivable from tokens.")
    if api:
        print("\n=== API-PRICE REFERENCE (%s) — not subscription cost ===" % load_catalog("runtime.json")["api_reference"]["table"])
        for k, v in sorted(ref.items(), key=lambda kv: -kv[1]):
            print("  %-26s %10.2f" % (k[:26], v))
    return 0
