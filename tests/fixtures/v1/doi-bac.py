# -*- coding: utf-8 -*-
"""
ĐỔI BẬC MODEL CỦA CẢ XƯỞNG — một lệnh, đổi hết, đảo lại được.

    python cong-cu/doi-bac.py            # xem đang ở hồ sơ nào
    python cong-cu/doi-bac.py fable      # gói CÓ Fable   (R0 Fable · R1 Opus · R2 Sonnet · R3 Haiku)
    python cong-cu/doi-bac.py opus       # gói KHÔNG Fable (R0 Opus  · R1 Sonnet · R2 Sonnet · R3 Haiku)
    python cong-cu/doi-bac.py sonnet     # gói eo hẹp Opus (R0 Sonnet· R1 Sonnet · R2 Sonnet · R3 Haiku)

VÌ SAO CÓ FILE NÀY: ghim tên model mà gói KHÔNG có là chỗ phát sinh phí không kiểm soát, và phiên có
thể rơi về đường tính tiền khác. Gói bật/tắt Fable theo thời điểm ⇒ phải đổi được trong một lệnh,
không phải sửa tay 9 file rồi quên một file.

Đổi ba chỗ cùng lúc: `.claude/settings.json` (ghế R0) · dòng `model:` trong mọi `.claude/agents/*.md`
· ghi lại hồ sơ đang dùng ra `.claude/BAC-DANG-DUNG.md` để tài liệu trỏ vào một chỗ duy nhất.
"""
import io, json, os, re, sys, glob, datetime

HAIKU = "claude-haiku-4-5-20251001"

HO_SO = {
    # ten     : (R0 phien chinh, R1 truong-ky-thuat, R1b nghien-cuu, R2 cac ghe, R3 do-duong)
    "fable":  ("claude-fable-5",  "claude-opus-5",   "claude-sonnet-5", "claude-sonnet-5", HAIKU),
    "opus":   ("claude-opus-5",   "claude-sonnet-5", "claude-sonnet-5", "claude-sonnet-5", HAIKU),
    "sonnet": ("claude-sonnet-5", "claude-sonnet-5", "claude-sonnet-5", "claude-sonnet-5", HAIKU),
}
MO_TA = {
    "fable": "Gói CÓ Fable — R0 Fable, còn đệm Tech Lead ở bậc Opus.",
    "opus":  "Gói KHÔNG có Fable (Opus là cao nhất) — R0 Opus, Tech Lead về Sonnet, nâng Opus theo LƯỢT GỌI khi thật khó.",
    "sonnet":"Gói eo hẹp Opus (ví dụ gói 20$ khi Opus gần hết) — cả xưởng chạy Sonnet, chỉ nâng theo lượt gọi.",
}
GHE_R1  = "truong-ky-thuat"
GHE_R1B = "nghien-cuu"
GHE_R3  = "do-duong"


def doc_hien_tai():
    try:
        m = json.load(io.open(".claude/settings.json", encoding="utf-8-sig")).get("model", "")
    except Exception:
        m = ""
    for ten, bo in HO_SO.items():
        if bo[0] == m:
            return ten, m
    return None, m


def dat(ten):
    r0, r1, r1b, r2, r3 = HO_SO[ten]
    # 1) settings.json — giữ nguyên các khoá khác
    p = ".claude/settings.json"
    try:
        cai = json.load(io.open(p, encoding="utf-8-sig"))
    except Exception:
        cai = {}
    cu_r0 = cai.get("model")
    cai["model"] = r0
    io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(cai, ensure_ascii=False, indent=2) + "\n")
    print("  settings.json : %s -> %s" % (cu_r0 or "(trong)", r0))

    # 2) frontmatter từng ghế
    for f in sorted(glob.glob(".claude/agents/*.md")):
        ten_ghe = os.path.basename(f)[:-3]
        moi = r1 if ten_ghe == GHE_R1 else r1b if ten_ghe == GHE_R1B else r3 if ten_ghe == GHE_R3 else r2
        s = io.open(f, encoding="utf-8-sig").read()
        cu = re.search(r"^model:\s*(\S+)\s*$", s, re.M)
        if not cu:
            print("  (!) %-18s KHONG co dong 'model:' — bo qua" % ten_ghe); continue
        if cu.group(1) == moi:
            print("  %-18s = %s" % (ten_ghe, moi)); continue
        s = s[:cu.start(1)] + moi + s[cu.end(1):]
        io.open(f, "w", encoding="utf-8", newline="\n").write(s)
        print("  %-18s %s -> %s" % (ten_ghe, cu.group(1), moi))

    # 3) ghi hồ sơ đang dùng — tài liệu trỏ vào ĐÚNG MỘT chỗ này
    io.open(".claude/BAC-DANG-DUNG.md", "w", encoding="utf-8", newline="\n").write(
        "# Bậc model đang dùng: **%s**\n\n"
        "> Sinh bởi `python cong-cu/doi-bac.py %s` lúc %s. **Đừng sửa tay file này** — chạy lại lệnh.\n\n"
        "%s\n\n"
        "| Vai | Ghế | Model |\n|---|---|---|\n"
        "| R0 Quản đốc | phiên chính (`.claude/settings.json`) | `%s` |\n"
        "| R1 Tech Lead | `truong-ky-thuat` | `%s` |\n"
        "| R1b Nghiên cứu | `nghien-cuu` | `%s` |\n"
        "| R2 Kỹ sư · QA · BA | các ghế còn lại | `%s` |\n"
        "| R3 Cơ khí | `do-duong` | `%s` |\n\n"
        "**Đổi hồ sơ:** `python cong-cu/doi-bac.py fable|opus|sonnet` — đổi cả settings lẫn 9 ghế trong một lệnh.\n"
        "**Luật cứng:** chỉ ghim model mà gói THẬT SỰ có. Ghim tên ngoài gói = phí không kiểm soát.\n"
        % (ten, ten, datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), MO_TA[ten], r0, r1, r1b, r2, r3))
    print("  .claude/BAC-DANG-DUNG.md : da ghi ho so '%s'" % ten)


def main():
    if not os.path.isdir(".claude"):
        print("Chay lenh nay o GOC REPO (cho co thu muc .claude)."); return 1
    if len(sys.argv) < 2:
        ten, m = doc_hien_tai()
        print("Ho so dang dung:", ten or "(khong khop ho so nao)", "| settings.model =", m or "(trong)")
        for f in sorted(glob.glob(".claude/agents/*.md")):
            mm = re.search(r"^model:\s*(\S+)\s*$", io.open(f, encoding="utf-8-sig").read(), re.M)
            print("  %-18s %s" % (os.path.basename(f)[:-3], mm.group(1) if mm else "(khong ghi)"))
        print("\nDoi: python cong-cu/doi-bac.py fable|opus|sonnet")
        return 0
    ten = sys.argv[1].strip().lower()
    if ten not in HO_SO:
        print("Ho so phai la mot trong:", " | ".join(HO_SO)); return 1
    print("Doi sang ho so '%s' — %s" % (ten, MO_TA[ten]))
    dat(ten)
    print("\nXONG. Nho: phien DANG MO khong tu doi — dong roi mo lai phien de an bac moi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
