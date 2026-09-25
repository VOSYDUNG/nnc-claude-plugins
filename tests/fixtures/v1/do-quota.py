# -*- coding: utf-8 -*-
"""
ĐO QUOTA THẬT từ transcript Claude Code — không đoán, không ước. BẢN 2 (9/9/2026).

Cách dùng:
    python cong-cu/do-quota.py                 # tự nhận repo đang mở (theo cwd)
    python cong-cu/do-quota.py --ngay 7        # chỉ 7 ngày gần nhất
    python cong-cu/do-quota.py --tu 2026-09-06 --den 2026-09-07
    python cong-cu/do-quota.py <thư-mục-project>

BẢN 2 thêm bốn thứ bản 1 bỏ phí (transcript vốn đã ghi sẵn):
    • theo NGÀY   — thấy từng đợt, không chỉ cộng dồn cả đời dự án
    • theo EFFORT — mức tư duy (`effort` trong transcript): chi phí và sản lượng từng mức
    • THINKING    — `output_tokens_details.thinking_tokens`: nghĩ tốn bao nhiêu trong tổng ra
    • theo NHÁNH  — `gitBranch`, quy chi phí về từng lô

VỀ CON SỐ: trọng số theo tỉ lệ bảng giá API (Opus/Fable 15/75 · Sonnet 3/15 · Haiku 0.8/4 $/MTok;
cache đọc 0.1× giá vào, cache ghi 1.25×). Trên gói thuê bao SỐ TUYỆT ĐỐI không phải tiền thật —
nhưng SO SÁNH cùng một thước thì đúng. Đó là mục đích.
"""
import io, json, os, sys, glob
from collections import defaultdict

GIA = {  # $/MTok (vào, ra) — trọng số tương đối
    "opus":   (15.0, 75.0),
    "fable":  (15.0, 75.0),
    "sonnet": (3.0, 15.0),
    "haiku":  (0.8, 4.0),
}

def bac(model):
    m = (model or "").lower()
    for k in GIA:
        if k in m:
            return k
    return "sonnet"

def diem(model, vao, ra, cr, cw):
    gv, gr = GIA[bac(model)]
    return (vao * gv + ra * gr + cr * gv * 0.1 + cw * gv * 1.25) / 1_000_000


class O:
    """Một ô đếm."""
    __slots__ = ("luot", "vao", "ra", "cr", "cw", "nghi", "d")
    def __init__(self):
        self.luot = self.vao = self.ra = self.cr = self.cw = self.nghi = 0
        self.d = 0.0
    def cong(self, model, u):
        self.luot += 1
        self.vao += u.get("input_tokens", 0)
        self.ra  += u.get("output_tokens", 0)
        self.cr  += u.get("cache_read_input_tokens", 0)
        self.cw  += u.get("cache_creation_input_tokens", 0)
        self.nghi += (u.get("output_tokens_details") or {}).get("thinking_tokens", 0)
        self.d += diem(model, u.get("input_tokens", 0), u.get("output_tokens", 0),
                       u.get("cache_read_input_tokens", 0), u.get("cache_creation_input_tokens", 0))


def quet(goc, tu=None, den=None):
    goc_list = goc if isinstance(goc, (list, tuple)) else [goc]
    theo = {k: defaultdict(O) for k in ("model", "ngay", "effort", "vung", "nhanh", "phien")}
    hai_chieu = defaultdict(O)          # (effort, bac) -> O  : tương quan mức nghĩ × bậc model
    la = set()
    for f in [x for g in goc_list for x in glob.glob(os.path.join(g, "**", "*.jsonl"), recursive=True)]:
        try:
            for line in io.open(f, encoding="utf-8", errors="replace"):
                line = line.strip()
                if not line or '"assistant"' not in line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get("type") != "assistant":
                    continue
                m = d.get("message") or {}
                u = m.get("usage") or {}
                if not u:
                    continue
                model = m.get("model") or "?"
                ngay = (d.get("timestamp") or "")[:10]
                if tu and ngay and ngay < tu:   continue
                if den and ngay and ngay > den: continue
                if bac(model) == "sonnet" and "sonnet" not in (model or "").lower():
                    la.add(model)
                eff = d.get("effort") or "(khong ghi)"
                vung = "subagent" if d.get("isSidechain") else "phien-chinh"
                nhanh = d.get("gitBranch") or "(khong nhanh)"
                phien = (d.get("sessionId") or "?")[:8]
                for khoa, gia_tri in (("model", model), ("ngay", ngay or "?"), ("effort", eff),
                                      ("vung", vung), ("nhanh", nhanh), ("phien", phien)):
                    theo[khoa][gia_tri].cong(model, u)
                hai_chieu[(eff, bac(model))].cong(model, u)
        except Exception as e:
            print("  (bo qua %s: %s)" % (os.path.basename(f), e))
    return theo, hai_chieu, la


def bang(tieu_de, oo, cot1="", sap_theo_diem=True, tran=None, moi_luot=True):
    if not oo:
        return
    print("\n=== %s ===" % tieu_de)
    print("  %-24s %8s %12s %12s %10s %9s" % (cot1, "luot", "DIEM", "diem/luot", "token nghi", "% nghi"))
    muc = sorted(oo.items(), key=(lambda kv: -kv[1].d) if sap_theo_diem else (lambda kv: kv[0]))
    if tran:
        muc = muc[:tran]
    for ten, o in muc:
        pn = (100.0 * o.nghi / o.ra) if o.ra else 0.0
        print("  %-24s %8d %12.1f %12.4f %10s %8.1f%%"
              % (str(ten)[:24], o.luot, o.d, (o.d / o.luot if o.luot else 0), "{:,}".format(o.nghi), pn))


def main():
    args = [a for a in sys.argv[1:]]
    tu = den = None
    ngay_gan = None
    goc = None
    tat_ca = False
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--tu":    tu = args[i+1]; i += 2
        elif a == "--den": den = args[i+1]; i += 2
        elif a == "--ngay": ngay_gan = int(args[i+1]); i += 2
        elif a == "--tat-ca": tat_ca = True; i += 1
        else: goc = a; i += 1

    if not goc:
        def ma_hoa(d):
            return os.path.abspath(d).replace(":", "-").replace("\\", "-").replace("/", "-")
        gp = os.path.join(os.path.expanduser("~"), ".claude", "projects")
        goc = os.path.join(gp, ma_hoa(os.getcwd()))
        ten = os.path.basename(os.path.abspath(os.getcwd()))
        uv = [os.path.join(gp, d) for d in os.listdir(gp) if d.endswith("-" + ten)] if os.path.isdir(gp) else []
        if tat_ca and uv:
            goc = uv                      # GOP moi thu muc cua cung repo (nhieu may/nhieu duong dan)
        elif not os.path.isdir(goc) and len(uv) == 1:
            goc = uv[0]
        if not tat_ca and len(uv) > 1:
            print("  (!) Thay %d thu muc transcript cho repo nay: %s"
                  % (len(uv), ", ".join(os.path.basename(x) for x in uv)))
            print("      Dang do MOT thu muc. Them --tat-ca de gop het (khac may = khac thu muc)." )
    ds_goc = goc if isinstance(goc, list) else [goc]
    ds_goc = [g for g in ds_goc if os.path.isdir(g)]
    if not ds_goc:
        print("Khong thay thu muc transcript:", goc); return 1

    if ngay_gan:
        import datetime
        tu = (datetime.date.today() - datetime.timedelta(days=ngay_gan - 1)).isoformat()

    print("Nguon:", " + ".join(os.path.basename(g) for g in ds_goc),
          ("| tu %s" % tu if tu else ""), ("| den %s" % den if den else ""))
    theo, hai_chieu, la = quet(ds_goc, tu, den)

    tong = sum(o.d for o in theo["model"].values())
    tong_luot = sum(o.luot for o in theo["model"].values())
    tong_nghi = sum(o.nghi for o in theo["model"].values())
    tong_ra = sum(o.ra for o in theo["model"].values())
    if not tong_luot:
        print("Khong co du lieu trong khoang nay."); return 0

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
        re_hon = sum(o.d for k, o in theo["model"].items() if bac(k) in ("opus", "fable"))
        print("  WHAT-IF         : neu phan subagent chay bac Sonnet -> %.1f diem (~giam %.0f%%)"
              % (sub.d * 0.2, 80))
        del re_hon
    if la:
        print("  Model chua nhan ra bac (xep tam sonnet):", ", ".join(sorted(la)))
    # canh bao: ngay co commit git ma khong co transcript => phien do o MAY KHAC
    try:
        import subprocess
        r = subprocess.run(["git", "log", "--format=%ad", "--date=format:%Y-%m-%d", "--all"],
                           capture_output=True, text=True, timeout=20)
        ngay_git = set(x for x in r.stdout.split() if x[:2] == "20")
        ngay_do = set(theo["ngay"].keys())
        thieu = sorted(d for d in ngay_git - ngay_do if (not tu or d >= tu) and (not den or d <= den))
        if thieu:
            print("  (!) %d ngay CO COMMIT ma KHONG co transcript o day: %s"
                  % (len(thieu), ", ".join(thieu[-8:])))
            print("      => phien do chay o MAY KHAC. Chay --tat-ca, hoac chep thu muc transcript may kia sang.")
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
