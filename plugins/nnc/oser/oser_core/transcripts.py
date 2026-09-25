# -*- coding: utf-8 -*-
"""Read Claude Code transcripts: OBSERVED models for doctor, and the quota report (`oser quota`).

The quota report is the NNC-AI-OSer 1.0 `do-quota.py` moved here unchanged in method: weights follow
API list-price ratios (Opus/Fable 15/75 · Sonnet 3/15 · Haiku 0.8/4 $/MTok; cache read 0.1x input,
cache write 1.25x). On a subscription the absolute number is not money — comparisons on one ruler are.
"""
import datetime
import glob
import io
import json
import os
import subprocess
from collections import Counter, defaultdict

from .util import claude_home, transcript_slug

GIA = {"opus": (15.0, 75.0), "fable": (15.0, 75.0), "sonnet": (3.0, 15.0), "haiku": (0.8, 4.0)}


def bac(model):
    m = (model or "").lower()
    for k in GIA:
        if k in m:
            return k
    return "sonnet"


def diem(model, vao, ra, cr, cw):
    gv, gr = GIA[bac(model)]
    return (vao * gv + ra * gr + cr * gv * 0.1 + cw * gv * 1.25) / 1_000_000


def project_transcript_dirs(project_root, all_machines=False):
    base = os.path.join(claude_home(), "projects")
    own = os.path.join(base, transcript_slug(project_root))
    if not os.path.isdir(base):
        return []
    name = os.path.basename(os.path.abspath(project_root))
    siblings = [os.path.join(base, d) for d in os.listdir(base) if d.endswith("-" + transcript_slug(name))]
    if all_machines:
        return sorted(set(siblings + ([own] if os.path.isdir(own) else [])))
    if os.path.isdir(own):
        return [own]
    return siblings[:1] if len(siblings) == 1 else []


def _events(dirs):
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
                        if ev.get("type") == "assistant":
                            yield ev
            except OSError:
                continue


def observed_models(project_root):
    """What actually ran. ROOT = newest main-thread (non-sidechain) assistant turn."""
    dirs = project_transcript_dirs(project_root)
    root_last = None
    root, sub = Counter(), Counter()
    for ev in _events(dirs):
        model = (ev.get("message") or {}).get("model")
        if not model or model.startswith("<"):
            continue
        ts = ev.get("timestamp") or ""
        if ev.get("isSidechain"):
            sub[model] += 1
        else:
            root[model] += 1
            if root_last is None or ts > root_last[1]:
                root_last = (model, ts, (ev.get("sessionId") or "?")[:8])
    return {"dirs": dirs, "root_last": root_last, "root": dict(root), "sub": dict(sub),
            "all": sorted(set(root) | set(sub))}


# ---------------------------------------------------------------- quota report (`oser quota`)

class O:
    __slots__ = ("luot", "vao", "ra", "cr", "cw", "nghi", "d")

    def __init__(self):
        self.luot = self.vao = self.ra = self.cr = self.cw = self.nghi = 0
        self.d = 0.0

    def cong(self, model, u):
        self.luot += 1
        self.vao += u.get("input_tokens", 0)
        self.ra += u.get("output_tokens", 0)
        self.cr += u.get("cache_read_input_tokens", 0)
        self.cw += u.get("cache_creation_input_tokens", 0)
        self.nghi += (u.get("output_tokens_details") or {}).get("thinking_tokens", 0)
        self.d += diem(model, u.get("input_tokens", 0), u.get("output_tokens", 0),
                       u.get("cache_read_input_tokens", 0), u.get("cache_creation_input_tokens", 0))


def quet(dirs, tu=None, den=None):
    theo = {k: defaultdict(O) for k in ("model", "ngay", "effort", "vung", "nhanh", "phien")}
    hai_chieu = defaultdict(O)
    la = set()
    for d in _events(dirs):
        m = d.get("message") or {}
        u = m.get("usage") or {}
        if not u:
            continue
        model = m.get("model") or "?"
        ngay = (d.get("timestamp") or "")[:10]
        if tu and ngay and ngay < tu:
            continue
        if den and ngay and ngay > den:
            continue
        if bac(model) == "sonnet" and "sonnet" not in (model or "").lower():
            la.add(model)
        eff = d.get("effort") or "(khong ghi)"
        vung = "subagent" if d.get("isSidechain") else "phien-chinh"
        for khoa, gia_tri in (("model", model), ("ngay", ngay or "?"), ("effort", eff), ("vung", vung),
                              ("nhanh", d.get("gitBranch") or "(khong nhanh)"),
                              ("phien", (d.get("sessionId") or "?")[:8])):
            theo[khoa][gia_tri].cong(model, u)
        hai_chieu[(eff, bac(model))].cong(model, u)
    return theo, hai_chieu, la


def bang(tieu_de, oo, cot1="", sap_theo_diem=True, tran=None):
    if not oo:
        return
    print("\n=== %s ===" % tieu_de)
    print("  %-24s %8s %12s %12s %10s %9s" % (cot1, "luot", "DIEM", "diem/luot", "token nghi", "% nghi"))
    muc = sorted(oo.items(), key=(lambda kv: -kv[1].d) if sap_theo_diem else (lambda kv: kv[0]))
    for ten, o in muc[:tran] if tran else muc:
        pn = (100.0 * o.nghi / o.ra) if o.ra else 0.0
        print("  %-24s %8d %12.1f %12.4f %10s %8.1f%%"
              % (str(ten)[:24], o.luot, o.d, (o.d / o.luot if o.luot else 0), "{:,}".format(o.nghi), pn))


def quota_main(args, project_root):
    tu = den = None
    ngay_gan = None
    goc = None
    tat_ca = False
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--tu":
            tu = args[i + 1]; i += 2
        elif a == "--den":
            den = args[i + 1]; i += 2
        elif a == "--ngay":
            ngay_gan = int(args[i + 1]); i += 2
        elif a == "--tat-ca":
            tat_ca = True; i += 1
        else:
            goc = a; i += 1
    dirs = [goc] if goc else project_transcript_dirs(project_root, all_machines=tat_ca)
    dirs = [d for d in dirs if os.path.isdir(d)]
    if not dirs:
        print("Khong thay thu muc transcript cho", project_root)
        return 1
    if ngay_gan:
        tu = (datetime.date.today() - datetime.timedelta(days=ngay_gan - 1)).isoformat()
    print("Nguon:", " + ".join(os.path.basename(g) for g in dirs),
          ("| tu %s" % tu if tu else ""), ("| den %s" % den if den else ""))
    theo, hai_chieu, la = quet(dirs, tu, den)
    tong = sum(o.d for o in theo["model"].values())
    tong_luot = sum(o.luot for o in theo["model"].values())
    tong_nghi = sum(o.nghi for o in theo["model"].values())
    tong_ra = sum(o.ra for o in theo["model"].values())
    if not tong_luot:
        print("Khong co du lieu trong khoang nay.")
        return 0
    bang("THEO MODEL", theo["model"], "model")
    bang("THEO VUNG", theo["vung"], "vung")
    bang("THEO MUC TU DUY (effort)", theo["effort"], "effort")
    bang("THEO NGAY (moi nhat truoc)", theo["ngay"], "ngay", sap_theo_diem=False)
    bang("THEO NHANH GIT (top 12)", theo["nhanh"], "nhanh", tran=12)
    bang("THEO PHIEN (top 10)", theo["phien"], "sessionId", tran=10)
    print("\n=== TUONG QUAN: MUC TU DUY x BAC MODEL ===")
    print("  %-14s %-8s %8s %12s %12s %9s" % ("effort", "bac", "luot", "DIEM", "diem/luot", "% nghi"))
    for (eff, b), o in sorted(hai_chieu.items(), key=lambda kv: -kv[1].d):
        pn = (100.0 * o.nghi / o.ra) if o.ra else 0.0
        print("  %-14s %-8s %8d %12.1f %12.4f %8.1f%%"
              % (str(eff)[:14], b, o.luot, o.d, o.d / o.luot if o.luot else 0, pn))
    print("\n=== TONG ===")
    print("  luot goi        : %s" % "{:,}".format(tong_luot))
    print("  DIEM quota      : %.1f" % tong)
    print("  token nghi      : %s / %s token ra = %.1f%%"
          % ("{:,}".format(tong_nghi), "{:,}".format(tong_ra), 100.0 * tong_nghi / tong_ra if tong_ra else 0))
    sub = theo["vung"].get("subagent")
    if sub:
        print("  subagent chiem  : %.1f%% quota" % (100.0 * sub.d / tong))
    if la:
        print("  Model chua nhan ra bac (xep tam sonnet):", ", ".join(sorted(la)))
    try:
        r = subprocess.run(["git", "log", "--format=%ad", "--date=format:%Y-%m-%d", "--all"],
                           cwd=project_root, capture_output=True, text=True, timeout=20)
        ngay_git = set(x for x in r.stdout.split() if x[:2] == "20")
        thieu = sorted(d for d in ngay_git - set(theo["ngay"].keys())
                       if (not tu or d >= tu) and (not den or d <= den))
        if thieu:
            print("  (!) %d ngay CO COMMIT ma KHONG co transcript o day: %s" % (len(thieu), ", ".join(thieu[-8:])))
            print("      => phien do chay o MAY KHAC. Chay --tat-ca, hoac chep thu muc transcript may kia sang.")
    except (OSError, subprocess.SubprocessError):
        pass
    return 0
