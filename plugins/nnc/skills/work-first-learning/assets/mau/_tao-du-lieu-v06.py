# -*- coding: utf-8 -*-
"""Sinh dữ liệu MẪU (GIẢ) cho Lớp học NNC v0.6 — trò chơi và Tủ khả năng.

Toàn bộ khách hàng, mặt hàng, mã hàng, công ty và giá là BỊA; mọi tên khách
hàng và tên hàng đều kết thúc bằng "— mẫu". Không dùng dữ liệu thật của ai.

Chạy lại bất cứ lúc nào; seed cố định nên nội dung luôn giống hệt:

    python plugins/nnc/skills/work-first-learning/assets/mau/_tao-du-lieu-v06.py
    python .../_tao-du-lieu-v06.py --out <thư mục khác>   # dùng cho test

Sinh ra (trong thư mục --out, mặc định cạnh script):
    gop/don-hang-tuan-40.xlsx, -41.xlsx, -42.xlsx   thẻ "Gộp nhiều file", "So sánh hai bảng"
    tim-loi/bang-tim-loi.xlsx + dap-an-tim-loi.md    trò "Tìm lỗi" (đúng 3 lỗi cài sẵn)
    ban-la-sep/ket-qua-claude-mau.xlsx + dap-an.md   trò "Bạn là sếp" (1 tổng sai, 1 ghi chú thiếu)
    phieu-nhan-hang-mau.png                          thẻ "Đọc ảnh hoặc PDF" (cần Pillow)
    thong-bao-noi-bo-mau.md                          thẻ "Dịch Việt ↔ Lào"

Dùng lại danh mục khách, hàng, giá và cách ghi bảng của _tao-du-lieu.py (không
sửa file đó). "Bạn là sếp" đọc bang-tinh-mau.xlsx CẠNH SCRIPT để tính số đúng.

Cần openpyxl; Pillow để vẽ ảnh phiếu (thiếu Pillow thì bỏ qua ảnh và báo).
Script không tự cài gì.
"""
import argparse
import datetime as dt
import importlib.util
import os
import random
import sys

try:
    import openpyxl
    from openpyxl.styles import Font
except ImportError:  # pragma: no cover
    sys.exit("Cần openpyxl để sinh file .xlsx: pip install openpyxl")

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20261006


def _nap_goc():
    spec = importlib.util.spec_from_file_location("_tao_du_lieu_goc", os.path.join(HERE, "_tao-du-lieu.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


G = _nap_goc()
KENH, KHACH, HANG, SO_LUONG, COT = G.KENH, G.KHACH, G.HANG, G.SO_LUONG, G.COT
HANG_THEO_MA = {ma: (ten, gia) for k in KENH for ma, ten, gia in HANG[k]}

# --- Gộp nhiều file / So sánh hai bảng ---------------------------------------
GOP_SO_DONG = {"OTC": 7, "HC": 7, "SPM": 6}  # = 20 dòng / tuần
TUAN_BAT_DAU = {40: dt.datetime(2026, 9, 28), 41: dt.datetime(2026, 10, 5), 42: dt.datetime(2026, 10, 12)}
KHACH_MOI = "Nhà thuốc P — mẫu"            # chỉ xuất hiện ở tuần 42
KHACH_MOI_DON = [("MAU-OTC-01", 30), ("MAU-OTC-02", 20)]
MA_TANG_VOT = "MAU-HC-02"                  # Khẩu trang y tế — mẫu
SL_TANG_VOT = (20, 200)                    # tuần 41 -> tuần 42
SO_DON_SPM_MAT = 2                         # 2 đơn SPM lớn nhất tuần 41 không lặp lại

# --- Tìm lỗi -------------------------------------------------------------------
TIM_LOI_SO_DONG = {"OTC": 9, "HC": 8, "SPM": 8}  # = 25 dòng
TIM_LOI_TUAN = dt.datetime(2026, 10, 19)          # Thứ Hai 19 – Thứ Bảy 24/10/2026

# --- Ảnh phiếu nhận hàng -----------------------------------------------------
PHIEU_NGAY = "14/10/2026"
PHIEU_SO = "PNH-MAU-001"
PHIEU_DONG = [
    ("MAU-OTC-01", "Vitamin C 500mg — mẫu", 30, "hộp"),
    ("MAU-OTC-02", "Canxi D3 — mẫu", 12, "hộp"),
    ("MAU-HC-01", "Găng tay y tế — mẫu", 50, "hộp"),
    ("MAU-HC-05", "Dung dịch sát khuẩn — mẫu", 24, "hộp"),
    ("MAU-SPM-04", "Khăn giấy — mẫu", 5, "thùng"),
    ("MAU-SPM-01", "Nước rửa tay — mẫu", 36, "hộp"),
]
PHIEU_KICH_THUOC = (1000, 700)

THONG_BAO = """# Thông báo nội bộ — MẪU

> Văn bản GIẢ, chỉ để tập dịch Việt ↔ Lào trong Lớp học NNC. Không phải thông báo thật; mọi tên, ngày, số máy lẻ đều bịa.

**V/v: Lịch giao hàng và giờ làm việc kho dịp nghỉ lễ — mẫu**

Kính gửi anh chị em các kênh OTC, HC và SPM,

Nhân dịp nghỉ lễ, Kho mẫu điều chỉnh lịch làm việc như sau:

- **Thứ Sáu 20/11/2026:** kho làm việc đến 12:00. Đơn nhận sau 10:00 sẽ giao vào ngày làm việc tiếp theo.
- **Thứ Bảy 21/11 và Chủ nhật 22/11/2026:** kho nghỉ, không giao hàng.
- **Thứ Hai 23/11/2026:** kho làm việc lại từ 7:30, ưu tiên giao các đơn còn tồn trước lễ.

Đề nghị các bộ phận bán hàng báo trước cho khách hàng và chốt đơn cần giao trước lễ chậm nhất 16:00 Thứ Năm 19/11/2026. Mọi thắc mắc xin liên hệ Phòng Kho vận — mẫu, số máy lẻ 000.

Chúc mọi người kỳ nghỉ vui vẻ, an toàn.

*Phòng Kho vận — mẫu*
"""


def fmt(n):
    """1234567 -> '1.234.567' (kiểu Việt Nam)."""
    return format(n, ",").replace(",", ".")


def _sap(rows):
    rows.sort(key=lambda r: (r["Ngày"], KENH.index(r["Kênh"]) if r["Kênh"] in KENH else 0,
                             r["Khách hàng"], r["Mã hàng"]))
    return rows


def _dong(ngay, kenh, khach, ma, sl):
    ten, gia = HANG_THEO_MA[ma]
    return {"Ngày": ngay, "Kênh": kenh, "Khách hàng": khach, "Mã hàng": ma, "Tên hàng": ten,
            "Số lượng": sl, "Đơn vị": "hộp", "Đơn giá": gia, "Thành tiền": sl * gia}


def tao_tuan(rng, ngay_dau, so_dong, bo_ma=()):
    """Đơn hàng một tuần, mỗi cặp (Khách hàng, Mã hàng) chỉ một dòng."""
    ngay = [ngay_dau + dt.timedelta(days=i) for i in range(6)]
    rows, keys = [], set()
    for kenh in KENH:
        hang = [h for h in HANG[kenh] if h[0] not in bo_ma]
        n = 0
        while n < so_dong[kenh]:
            ma = rng.choice(hang)[0]
            khach = rng.choice(KHACH[kenh])
            if (khach, ma) in keys:
                continue
            keys.add((khach, ma))
            rows.append(_dong(rng.choice(ngay), kenh, khach, ma, rng.choice(SO_LUONG[kenh])))
            n += 1
    return rows


# --- Gộp nhiều file ------------------------------------------------------------
def tao_gop(rng):
    t40 = _sap(tao_tuan(rng, TUAN_BAT_DAU[40], GOP_SO_DONG))
    # Tuần 41: HC có đúng một dòng Khẩu trang, số lượng cố định.
    so41 = dict(GOP_SO_DONG, HC=GOP_SO_DONG["HC"] - 1)
    t41 = tao_tuan(rng, TUAN_BAT_DAU[41], so41, bo_ma=(MA_TANG_VOT,))
    khach_kt = rng.choice(KHACH["HC"])
    t41.append(_dong(TUAN_BAT_DAU[41] + dt.timedelta(days=rng.randrange(6)), "HC", khach_kt,
                     MA_TANG_VOT, SL_TANG_VOT[0]))
    _sap(t41)
    # Tuần 42 = tuần 41 lùi 7 ngày, rồi đúng ba thay đổi có chủ đích.
    spm = sorted((r for r in t41 if r["Kênh"] == "SPM"), key=lambda r: (-r["Thành tiền"], r["Mã hàng"]))
    mat = {(r["Khách hàng"], r["Mã hàng"]) for r in spm[:SO_DON_SPM_MAT]}
    t42 = []
    for r in t41:
        if (r["Khách hàng"], r["Mã hàng"]) in mat:
            continue
        r2 = dict(r, **{"Ngày": r["Ngày"] + dt.timedelta(days=7)})
        if r2["Mã hàng"] == MA_TANG_VOT:
            r2 = _dong(r2["Ngày"], "HC", r2["Khách hàng"], MA_TANG_VOT, SL_TANG_VOT[1])
        t42.append(r2)
    for ma, sl in KHACH_MOI_DON:
        t42.append(_dong(TUAN_BAT_DAU[42] + dt.timedelta(days=rng.randrange(6)), "OTC", KHACH_MOI, ma, sl))
    _sap(t42)
    return {40: t40, 41: t41, 42: t42}, sorted(mat)


# --- Tìm lỗi -----------------------------------------------------------------
def _dao_so(v):
    """Đổi chỗ hai chữ số kề nhau khác nhau đầu tiên: 1350000 -> 1530000."""
    s = list(str(v))
    for i in range(len(s) - 1):
        if s[i] != s[i + 1] and s[i + 1] != "0":
            s[i], s[i + 1] = s[i + 1], s[i]
            return int("".join(s))
    return None


def tao_tim_loi(rng):
    rows = _sap(tao_tuan(rng, TIM_LOI_TUAN, TIM_LOI_SO_DONG))
    n = len(rows)
    ba = [range(0, n // 3), range(n // 3, 2 * n // 3), range(2 * n // 3, n)]
    loi = []
    # 1) Mã kênh gõ nhầm "OCT" — một dòng OTC ở phần đầu bảng.
    i = rng.choice([i for i in ba[0] if i >= 2 and rows[i]["Kênh"] == "OTC"])
    rows[i]["Kênh"] = "OCT"
    loi.append((i + 2, "Mã kênh gõ nhầm", 'Kênh = "OCT" (đúng là "OTC"; khách %s là nhà thuốc)'
                % rows[i]["Khách hàng"], "B%d" % (i + 2)))
    # 2) Thành tiền ≠ Số lượng × Đơn giá — đảo hai chữ số, ở giữa bảng.
    i = rng.choice([i for i in ba[1] if _dao_so(rows[i]["Thành tiền"])])
    dung = rows[i]["Thành tiền"]
    rows[i]["Thành tiền"] = _dao_so(dung)
    loi.append((i + 2, "Thành tiền sai", "Thành tiền ghi %s nhưng %d × %s = %s (đảo hai chữ số)"
                % (fmt(rows[i]["Thành tiền"]), rows[i]["Số lượng"], fmt(rows[i]["Đơn giá"]), fmt(dung)),
                "I%d" % (i + 2)))
    # 3) Ngày ngoài tuần — gõ nhầm tháng 10 thành 11, ở cuối bảng.
    i = rng.choice(list(ba[2]))
    goc = rows[i]["Ngày"]
    rows[i]["Ngày"] = goc.replace(month=11)
    loi.append((i + 2, "Ngày ngoài tuần", "Ngày %s nằm ngoài tuần 19–24/10/2026 (có lẽ gõ nhầm tháng, đúng là %s)"
                % (rows[i]["Ngày"].strftime("%d/%m/%Y"), goc.strftime("%d/%m/%Y")), "A%d" % (i + 2)))
    loi.sort()
    return rows, loi


def ghi_dap_an_tim_loi(path, rows, loi):
    out = ["# Đáp án trò \"Tìm lỗi\" — dành cho giáo viên",
           "",
           "> Dữ liệu GIẢ để học. File: `bang-tim-loi.xlsx` (%d dòng đơn hàng, tuần 19–24/10/2026). "
           "Số dòng tính theo Excel: dòng 1 là tiêu đề, dữ liệu từ dòng 2 đến %d." % (len(rows), len(rows) + 1),
           "",
           "Có **đúng 3 lỗi**, mỗi lỗi một kiểu khác nhau. Mọi dòng còn lại đều đúng: Thành tiền = Số lượng × Đơn giá, "
           "ngày trong tuần, kênh là OTC/HC/SPM, đơn vị là hộp, giá đúng bảng giá mẫu.",
           "",
           "| # | Dòng | Ô | Loại lỗi | Vì sao sai |",
           "|---|---:|---|---|---|"]
    for k, (dong, loai, mo_ta, o) in enumerate(loi, 1):
        out.append("| %d | %d | %s | %s | %s |" % (k, dong, o, loai, mo_ta))
    out += ["",
            "**Cách thắng:** tìm đủ 3 lỗi và nói được vì sao trong 3 phút.",
            "",
            "**Câu bài học:** Nhờ Claude kiểm từng loại lỗi một (công thức, ngày, mã kênh) rồi tự xem lại "
            "đúng các dòng nó chỉ ra — kiểm trước khi tin.",
            ""]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))


# --- Bạn là sếp ----------------------------------------------------------------
def doc_bang(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    head = list(rows[0])
    return [dict(zip(head, r)) for r in rows[1:] if any(v is not None for v in r)]


def tao_ban_la_sep(nguon):
    data = doc_bang(nguon)
    tong = {k: [0, 0, 0] for k in KENH}
    for r in data:
        t = tong[r["Kênh"]]
        t[0] += 1
        t[1] += r["Số lượng"]
        t[2] += r["Thành tiền"]
    hc = [(n, r) for n, r in enumerate(data, start=2) if r["Kênh"] == "HC"]
    bo_sot_dong, bo_sot = hc[-1]   # "Claude" bỏ sót dòng HC cuối cùng khi cộng Thành tiền
    sai = {"kenh": "HC", "cot": "Tổng Thành tiền (LAK)", "dung": tong["HC"][2],
           "hien": tong["HC"][2] - bo_sot["Thành tiền"], "lech": -bo_sot["Thành tiền"],
           "dong_nguon": bo_sot_dong, "dong_nguon_mo_ta": "%s · %s · %d hộp × %s"
           % (bo_sot["Khách hàng"], bo_sot["Tên hàng"], bo_sot["Số lượng"], fmt(bo_sot["Đơn giá"]))}
    tong_cong = [sum(tong[k][i] for k in KENH) for i in range(3)]
    return tong, tong_cong, sai


def ghi_ket_qua_claude(path, tong, tong_cong, sai):
    wb = G._wb()
    ws = wb.active
    ws.title = "Tổng hợp theo kênh"
    G._header(ws, ["Kênh", "Số dòng", "Tổng Số lượng (hộp)", "Tổng Thành tiền (LAK)"], [12, 10, 20, 24])
    for k in KENH:
        tien = sai["hien"] if k == sai["kenh"] else tong[k][2]
        ws.append([k, tong[k][0], tong[k][1], tien])
    ws.append(["Tổng cộng"] + tong_cong)
    for c in ws[5]:
        c.font = Font(bold=True)
    for row in ws.iter_rows(min_row=2, max_row=5):
        for c in row[1:]:
            c.number_format = "#,##0"
    ws.append([])
    ws.append(["Ghi chú"])
    ws["A7"].font = Font(bold=True)
    ws.append(["- Thành tiền tính bằng LAK, đã cộng đủ các dòng của từng kênh."])
    ws.append(["- Số lượng tính theo hộp; không có dòng nào cần kiểm."])
    ws.append([])
    ws.append(["Dữ liệu GIẢ để học (trò \"Bạn là sếp\") — không phải số liệu NNC."])
    wb.save(path)


def ghi_dap_an_sep(path, tong, tong_cong, sai):
    hien_sum = sum(tong[k][2] for k in KENH) + sai["lech"]
    out = ["# Đáp án trò \"Bạn là sếp\" — dành cho giáo viên",
           "",
           "> Dữ liệu GIẢ để học. `ket-qua-claude-mau.xlsx` là bản tổng hợp theo kênh \"như thể Claude làm\" "
           "từ `../bang-tinh-mau.xlsx` (tuần 05–10/10/2026). Học viên đóng vai sếp: **Đạt** hay **Trả lại vì…**",
           "",
           "**Đáp án đúng: Trả lại**, vì hai lý do:",
           "",
           "## 1. Một tổng bị sai",
           "",
           "- Ô **D3** — kênh **%s**, cột *%s*: file ghi **%s**, đúng là **%s**, lệch **%s LAK** (thiếu %s)."
           % (sai["kenh"], sai["cot"], fmt(sai["hien"]), fmt(sai["dung"]), fmt(sai["lech"]), fmt(-sai["lech"])),
           "- Nguyên nhân giả định: bỏ sót dòng %d của `bang-tinh-mau.xlsx` (%s), dù cột Số dòng vẫn ghi %d."
           % (sai["dong_nguon"], sai["dong_nguon_mo_ta"], tong[sai["kenh"]][0]),
           "- Dấu hiệu tự phát hiện, không cần mở file nguồn: OTC + HC + SPM = %s, **không bằng** dòng Tổng cộng %s."
           % (fmt(hien_sum), fmt(tong_cong[2])),
           "- Mọi ô số khác đều đúng: cả cột Số dòng, cả cột Tổng Số lượng, Tổng Thành tiền của OTC và SPM, "
           "và toàn bộ dòng Tổng cộng.",
           "",
           "## 2. Thiếu một ghi chú",
           "",
           "- Phần Ghi chú **không nói nguồn và kỳ dữ liệu**: lấy từ file nào, tuần nào. Thiếu dòng này thì người "
           "nhận không đối chiếu lại được. Ghi chú cần có, ví dụ: *Nguồn: bang-tinh-mau.xlsx, tuần 05–10/10/2026.*",
           "- Ghi chú \"đã cộng đủ các dòng\" lại là khẳng định chưa được kiểm — đúng chỗ phải nghi.",
           "",
           "## Bảng đúng để đối chiếu",
           "",
           "| Kênh | Số dòng | Tổng Số lượng (hộp) | Tổng Thành tiền (LAK) |",
           "|---|---:|---:|---:|"]
    for k in KENH:
        out.append("| %s | %d | %s | %s |" % (k, tong[k][0], fmt(tong[k][1]), fmt(tong[k][2])))
    out.append("| **Tổng cộng** | **%d** | **%s** | **%s** |" % (tong_cong[0], fmt(tong_cong[1]), fmt(tong_cong[2])))
    out += ["",
            "**Câu trả lại mẫu:** \"Trả lại vì tổng Thành tiền HC không khớp — ba kênh cộng lại không ra tổng "
            "cộng; và thiếu ghi chú nguồn, kỳ dữ liệu.\"",
            "",
            "**Câu bài học:** Sếp giỏi không làm lại từ đầu — sếp kiểm vài chỗ then chốt (cộng ngang, đối chiếu "
            "tổng, đọc ghi chú) rồi mới ký Đạt.",
            ""]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))


# --- Ảnh phiếu nhận hàng -------------------------------------------------------
def _font(ten, co):
    from PIL import ImageFont
    for p in (ten, ten.replace("arial", "segoeui").replace("segoeuibd", "segoeuib")):
        try:
            return ImageFont.truetype(os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", p), co)
        except OSError:
            continue
    for p in ("DejaVuSans-Bold.ttf" if "bd" in ten else "DejaVuSans.ttf",):
        try:
            return ImageFont.truetype(p, co)
        except OSError:
            pass
    return ImageFont.load_default(size=co)


def ve_phieu(path):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return False
    W, H = PHIEU_KICH_THUOC
    img = Image.new("RGB", (W, H), (226, 226, 222))
    d = ImageDraw.Draw(img)
    d.rectangle([24, 24, W - 16, H - 16], fill=(200, 200, 196))           # bóng giấy
    d.rectangle([16, 16, W - 24, H - 24], fill=(255, 255, 255), outline=(170, 170, 170))
    den = (20, 20, 20)
    f_bd, f_tt, f_th, f_nd, f_nho = (_font("arialbd.ttf", 22), _font("arialbd.ttf", 34),
                                     _font("arialbd.ttf", 20), _font("arial.ttf", 20), _font("arial.ttf", 16))
    d.text((48, 40), "Công ty Mẫu", font=f_bd, fill=den)
    d.text((48, 70), "Kho mẫu — Vientiane", font=f_nd, fill=den)
    d.text((700, 40), "Số phiếu: %s" % PHIEU_SO, font=f_nd, fill=den)
    d.text((700, 70), "Ngày: %s" % PHIEU_NGAY, font=f_nd, fill=den)
    tieu_de = "PHIẾU NHẬN HÀNG — MẪU"
    w = d.textlength(tieu_de, font=f_tt)
    d.text(((W - w) / 2, 112), tieu_de, font=f_tt, fill=den)
    d.text((48, 168), "Bên giao: Công ty Mẫu", font=f_nd, fill=den)
    d.text((500, 168), "Bên nhận: Nhà thuốc A — mẫu", font=f_nd, fill=den)
    # Bảng hàng
    cot = [48, 118, 268, 668, 798, 952]   # STT | Mã hàng | Tên hàng | Số lượng | Đơn vị
    ten_cot = ["STT", "Mã hàng", "Tên hàng", "Số lượng", "Đơn vị"]
    y0, h = 210, 40
    so_dong = len(PHIEU_DONG) + 1
    d.rectangle([cot[0], y0, cot[-1], y0 + h], fill=(234, 240, 234))
    for i in range(so_dong + 1):
        d.line([cot[0], y0 + i * h, cot[-1], y0 + i * h], fill=den, width=2 if i in (0, 1, so_dong) else 1)
    for x in cot:
        d.line([x, y0, x, y0 + so_dong * h], fill=den, width=2 if x in (cot[0], cot[-1]) else 1)
    for j, t in enumerate(ten_cot):
        d.text((cot[j] + 10, y0 + 9), t, font=f_th, fill=den)
    for i, (ma, ten, sl, dv) in enumerate(PHIEU_DONG, 1):
        y = y0 + i * h + 9
        d.text((cot[0] + 18, y), str(i), font=f_nd, fill=den)
        d.text((cot[1] + 10, y), ma, font=f_nd, fill=den)
        d.text((cot[2] + 10, y), ten, font=f_nd, fill=den)
        s = str(sl)
        d.text((cot[4] - 14 - d.textlength(s, font=f_nd), y), s, font=f_nd, fill=den)
        d.text((cot[4] + 10, y), dv, font=f_nd, fill=den)
    y = y0 + so_dong * h + 14
    d.text((48, y), "Tổng số mặt hàng: %d" % len(PHIEU_DONG), font=f_nd, fill=den)
    # Chữ ký
    for x, nhan in ((120, "Người giao — mẫu"), (620, "Người nhận — mẫu")):
        d.text((x, 560), nhan, font=f_bd, fill=den)
        d.text((x, 590), "(ký, ghi rõ họ tên)", font=f_nho, fill=(90, 90, 90))
        d.line([x, 640, x + 240, 640], fill=den, width=1)
    d.text((48, H - 52), "Ảnh MẪU — dữ liệu GIẢ để tập, không phải chứng từ thật.",
           font=f_nho, fill=(110, 110, 110))
    img.save(path, format="PNG", optimize=False)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=HERE, help="thư mục ghi file (mặc định: cạnh script)")
    out = ap.parse_args(argv).out
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):  # pragma: no cover
        pass
    for sub in ("gop", "tim-loi", "ban-la-sep"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    rng = random.Random(SEED)

    tuan, mat = tao_gop(rng)
    for so, rows in tuan.items():
        G.ghi_bang(os.path.join(out, "gop", "don-hang-tuan-%d.xlsx" % so), rows)

    tl_rows, tl_loi = tao_tim_loi(rng)
    G.ghi_bang(os.path.join(out, "tim-loi", "bang-tim-loi.xlsx"), tl_rows)
    ghi_dap_an_tim_loi(os.path.join(out, "tim-loi", "dap-an-tim-loi.md"), tl_rows, tl_loi)

    tong, tong_cong, sai = tao_ban_la_sep(os.path.join(HERE, "bang-tinh-mau.xlsx"))
    ghi_ket_qua_claude(os.path.join(out, "ban-la-sep", "ket-qua-claude-mau.xlsx"), tong, tong_cong, sai)
    ghi_dap_an_sep(os.path.join(out, "ban-la-sep", "dap-an.md"), tong, tong_cong, sai)

    with open(os.path.join(out, "thong-bao-noi-bo-mau.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(THONG_BAO)
    co_anh = ve_phieu(os.path.join(out, "phieu-nhan-hang-mau.png"))

    print("Đã ghi dữ liệu v0.6 vào", out)
    for so, rows in tuan.items():
        t = {k: [0, 0] for k in KENH}
        for r in rows:
            t[r["Kênh"]][0] += r["Số lượng"]
            t[r["Kênh"]][1] += r["Thành tiền"]
        print("Tuần %d: %d dòng  " % (so, len(rows))
              + "  ".join("%s SL %d / %s LAK" % (k, t[k][0], fmt(t[k][1])) for k in KENH))
    for so in (41, 42):
        for n, r in enumerate(tuan[so], start=2):
            if r["Khách hàng"] == KHACH_MOI or r["Mã hàng"] == MA_TANG_VOT or (r["Khách hàng"], r["Mã hàng"]) in mat:
                print("  tuần %d dòng %d: %s · %s · %s · %s · %d hộp · %s"
                      % (so, n, r["Ngày"].strftime("%d/%m"), r["Kênh"], r["Khách hàng"], r["Tên hàng"],
                         r["Số lượng"], fmt(r["Thành tiền"])))
    print("Tìm lỗi: %d dòng" % len(tl_rows))
    for item in tl_loi:
        print("  dòng %d %s: %s" % (item[0], item[1], item[2]))
    print("Bạn là sếp: %s %s ghi %s, đúng %s, lệch %s (bỏ sót dòng nguồn %d)"
          % (sai["kenh"], sai["cot"], fmt(sai["hien"]), fmt(sai["dung"]), fmt(sai["lech"]), sai["dong_nguon"]))
    print("Ảnh phiếu:", "đã vẽ PNG" if co_anh else "BỎ QUA — thiếu Pillow")


if __name__ == "__main__":
    main()
