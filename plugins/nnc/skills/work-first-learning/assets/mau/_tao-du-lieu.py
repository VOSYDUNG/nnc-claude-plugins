# -*- coding: utf-8 -*-
"""Sinh dữ liệu MẪU (GIẢ) cho Lớp học NNC — Buổi 1.

Toàn bộ khách hàng, mặt hàng, mã hàng và giá trong các file sinh ra là BỊA,
mọi tên đều kết thúc bằng "— mẫu". Không dùng dữ liệu thật của NNC hay của ai.

Chạy lại bất cứ lúc nào; seed cố định nên nội dung luôn giống hệt:

    python plugins/nnc/skills/work-first-learning/assets/mau/_tao-du-lieu.py
    python .../_tao-du-lieu.py --out <thư mục khác>   # dùng cho test

Sinh ra:
    bang-tinh-mau.xlsx            ~40 dòng đơn hàng tuần 05–10/10/2026, sạch
    bang-tinh-mau-tuan-sau.xlsx   tuần 12–17/10/2026, có lỗi cài sẵn
    dap-an-mau.xlsx               đáp án tổng hợp + danh sách lỗi cài sẵn

Cần openpyxl (pip install openpyxl). Script không tự cài gì.
"""
import argparse
import datetime as dt
import os
import random
import sys

try:
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill
except ImportError:  # pragma: no cover
    sys.exit("Cần openpyxl để sinh file .xlsx: pip install openpyxl")

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20261005
FIXED_TIME = dt.datetime(2026, 10, 1, 8, 0, 0)

KENH = ["OTC", "HC", "SPM"]

KHACH = {
    "OTC": ["Nhà thuốc A — mẫu", "Nhà thuốc B — mẫu", "Nhà thuốc D — mẫu", "Nhà thuốc G — mẫu"],
    "HC": ["Phòng khám B — mẫu", "Phòng khám E — mẫu", "Bệnh viện H — mẫu"],
    "SPM": ["Tạp hoá C — mẫu", "Tạp hoá K — mẫu", "Siêu thị M — mẫu"],
}

# (mã hàng, tên hàng, đơn giá LAK / hộp) — giá tròn, bịa, chỉ để tập tính.
HANG = {
    "OTC": [
        ("MAU-OTC-01", "Vitamin C 500mg — mẫu", 45000),
        ("MAU-OTC-02", "Canxi D3 — mẫu", 120000),
        ("MAU-OTC-03", "Viên ngậm thảo dược — mẫu", 35000),
        ("MAU-OTC-04", "Paracetamol 500mg — mẫu", 25000),
        ("MAU-OTC-05", "Men tiêu hoá — mẫu", 60000),
    ],
    "HC": [
        ("MAU-HC-01", "Găng tay y tế — mẫu", 85000),
        ("MAU-HC-02", "Khẩu trang y tế — mẫu", 40000),
        ("MAU-HC-03", "Bơm tiêm 5ml — mẫu", 150000),
        ("MAU-HC-04", "Bông gạc vô trùng — mẫu", 55000),
        ("MAU-HC-05", "Dung dịch sát khuẩn — mẫu", 95000),
    ],
    "SPM": [
        ("MAU-SPM-01", "Nước rửa tay — mẫu", 30000),
        ("MAU-SPM-02", "Kem đánh răng — mẫu", 20000),
        ("MAU-SPM-03", "Dầu gội — mẫu", 50000),
        ("MAU-SPM-04", "Khăn giấy — mẫu", 15000),
        ("MAU-SPM-05", "Sữa bột — mẫu", 180000),
    ],
}

SO_LUONG = {
    "OTC": [5, 10, 15, 20, 25, 30, 40, 50],
    "HC": [10, 20, 30, 40, 50, 60, 80, 100],
    "SPM": [12, 24, 36, 48, 60, 72],
}

SO_DONG_MOI_KENH = {"OTC": 14, "HC": 13, "SPM": 13}  # = 40 dòng

COT = ["Ngày", "Kênh", "Khách hàng", "Mã hàng", "Tên hàng",
       "Số lượng", "Đơn vị", "Đơn giá", "Thành tiền"]

# Lỗi "đơn vị lệch" ở tuần sau: bán lẻ theo vỉ thay vì hộp.
VI_SO_LUONG = 20
VI_DON_GIA = 3000


def tao_tuan(rng, ngay_dau):
    """Trả về list dict đơn hàng của một tuần (Thứ Hai–Thứ Bảy), không trùng khoá."""
    ngay = [ngay_dau + dt.timedelta(days=i) for i in range(6)]
    rows, keys = [], set()
    for kenh in KENH:
        n = 0
        while n < SO_DONG_MOI_KENH[kenh]:
            ma, ten, gia = rng.choice(HANG[kenh])
            r = {
                "Ngày": rng.choice(ngay),
                "Kênh": kenh,
                "Khách hàng": rng.choice(KHACH[kenh]),
                "Mã hàng": ma,
                "Tên hàng": ten,
                "Số lượng": rng.choice(SO_LUONG[kenh]),
                "Đơn vị": "hộp",
                "Đơn giá": gia,
            }
            k = (r["Mã hàng"], r["Khách hàng"], r["Ngày"])
            if k in keys:  # tránh trùng ngẫu nhiên; trùng chỉ có khi cố ý cài
                continue
            keys.add(k)
            r["Thành tiền"] = r["Số lượng"] * r["Đơn giá"]
            rows.append(r)
            n += 1
    rows.sort(key=lambda r: (r["Ngày"], KENH.index(r["Kênh"]), r["Khách hàng"], r["Mã hàng"]))
    return rows


def cai_loi(rng, rows):
    """Cài đúng các lỗi đã hẹn vào bảng tuần sau. Trả về (rows, danh sách lỗi)."""
    rows = [dict(r) for r in rows]
    # 1 dòng đơn vị "vỉ": một dòng OTC đổi thành Paracetamol bán theo vỉ.
    ma, ten, _ = HANG["OTC"][3]
    da_co = {(r["Khách hàng"], r["Ngày"]) for r in rows if r["Mã hàng"] == ma}
    otc = [i for i, r in enumerate(rows)
           if r["Kênh"] == "OTC" and (r["Khách hàng"], r["Ngày"]) not in da_co]
    i_vi = rng.choice(otc)
    rows[i_vi].update({"Mã hàng": ma, "Tên hàng": ten, "Đơn vị": "vỉ",
                       "Số lượng": VI_SO_LUONG, "Đơn giá": VI_DON_GIA,
                       "Thành tiền": VI_SO_LUONG * VI_DON_GIA})
    # 3 dòng thiếu giá: mỗi kênh một dòng, khác dòng "vỉ".
    i_thieu = []
    for kenh in KENH:
        ung_vien = [i for i, r in enumerate(rows) if r["Kênh"] == kenh and i != i_vi]
        i_thieu.append(rng.choice(ung_vien))
    for i in i_thieu:
        rows[i]["Đơn giá"] = None
        rows[i]["Thành tiền"] = None
    # 1 dòng trùng: chép nguyên một dòng sạch, chèn cuối khối cùng ngày.
    sach = [i for i in range(len(rows)) if i != i_vi and i not in i_thieu]
    i_goc = rng.choice(sach)
    ban_sao = dict(rows[i_goc])
    j = i_goc + 1
    while j < len(rows) and rows[j]["Ngày"] == ban_sao["Ngày"]:
        j += 1
    if j == i_goc + 1:  # đừng để bản sao nằm ngay dưới bản gốc
        j = min(i_goc + 4, len(rows))
    rows.insert(j, ban_sao)
    ids = {id(r): n + 2 for n, r in enumerate(rows)}  # dòng Excel (dòng 1 là tiêu đề)

    def dong(i_cu):  # vị trí cũ -> dòng Excel sau khi chèn
        return i_cu + 2 + (1 if i_cu >= j else 0)

    loi = [("Cột đổi tên", 1, "H1",
            'Cột "Đơn giá" bị đổi tên thành "Giá bán"',
            "Nhận ra cột tương đương, nói rõ đã hiểu Giá bán = Đơn giá; không bỏ cột")]
    for i in sorted(i_thieu):
        loi.append(("Thiếu giá", dong(i), "H%d" % dong(i),
                    "%s · %s · trống Giá bán và Thành tiền" % (rows[dong(i) - 2]["Kênh"], rows[dong(i) - 2]["Tên hàng"]),
                    "Ghi vào cột Cần kiểm; không tự điền giá, không tính vào tổng"))
    loi.append(("Dòng trùng", ids[id(ban_sao)], "A%d:I%d" % (ids[id(ban_sao)], ids[id(ban_sao)]),
                "Trùng hoàn toàn với dòng %d (cùng Ngày, Khách hàng, Mã hàng, Số lượng)" % dong(i_goc),
                "Đánh dấu Cần kiểm, chỉ tính một lần, hỏi người phụ trách đơn"))
    loi.append(("Đơn vị lệch", dong(i_vi), "G%d" % dong(i_vi),
                'Đơn vị "vỉ" trong khi cả bảng là "hộp"',
                "Không cộng chung số lượng với hộp, không tự quy đổi; ghi Cần kiểm"))
    return rows, loi, {"thieu": [dong(i) for i in i_thieu], "trung": (dong(i_goc), ids[id(ban_sao)]),
                       "vi": dong(i_vi)}


def tong_theo_kenh(rows, bo_dong=()):
    out = {k: {"dong": 0, "sl": 0, "tien": 0} for k in KENH}
    for n, r in enumerate(rows, start=2):
        if n in bo_dong:
            continue
        t = out[r["Kênh"]]
        t["dong"] += 1
        t["sl"] += r["Số lượng"]
        t["tien"] += r["Thành tiền"]
    return out


HEAD_FONT = Font(bold=True, color="FFFFFF")
HEAD_FILL = PatternFill("solid", fgColor="123F1E")


def _wb():
    wb = openpyxl.Workbook()
    wb.properties.creator = "NNC lớp học — dữ liệu mẫu"
    wb.properties.created = FIXED_TIME
    wb.properties.modified = FIXED_TIME
    return wb


def _header(ws, cols, widths):
    ws.append(cols)
    for c, w in zip(ws[1], widths):
        c.font, c.fill = HEAD_FONT, HEAD_FILL
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[c.column_letter].width = w
    ws.freeze_panes = "A2"


def ghi_bang(path, rows, cot_gia="Đơn giá"):
    wb = _wb()
    ws = wb.active
    ws.title = "Đơn hàng"
    cols = [cot_gia if c == "Đơn giá" else c for c in COT]
    _header(ws, cols, [12, 8, 24, 13, 30, 10, 8, 12, 14])
    for r in rows:
        ws.append([r[c] for c in COT])
    for row in ws.iter_rows(min_row=2):
        row[0].number_format = "dd/mm/yyyy"
        for c in row[5], row[7], row[8]:
            c.number_format = "#,##0"
    wb.save(path)


def ghi_dap_an(path, tong, loi, tong_sau, so_can_kiem):
    wb = _wb()
    ws = wb.active
    ws.title = "Tổng hợp theo kênh"
    _header(ws, ["Kênh", "Số dòng", "Tổng Số lượng", "Tổng Thành tiền (LAK)"], [12, 10, 16, 24])
    for k in KENH:
        ws.append([k, tong[k]["dong"], tong[k]["sl"], tong[k]["tien"]])
    ws.append(["Tổng cộng", sum(t["dong"] for t in tong.values()),
               sum(t["sl"] for t in tong.values()), sum(t["tien"] for t in tong.values())])
    ws["A5"].font = ws["B5"].font = ws["C5"].font = ws["D5"].font = Font(bold=True)
    ws.append([])
    ws.append(["Nguồn: bang-tinh-mau.xlsx. Toàn bộ là dữ liệu GIẢ để học, không phải số liệu NNC."])
    for row in ws.iter_rows(min_row=2, max_row=5):
        for c in row[1:]:
            c.number_format = "#,##0"

    ws2 = wb.create_sheet("Lỗi cài sẵn tuần sau")
    _header(ws2, ["Loại lỗi", "Dòng", "Ô", "Mô tả", "Cách xử lý đúng"], [14, 7, 9, 62, 66])
    for item in loi:
        ws2.append(list(item))
    ws2.append([])
    ws2.append(["Nguồn: bang-tinh-mau-tuan-sau.xlsx. Số dòng tính theo Excel (dòng 1 là tiêu đề)."])

    ws3 = wb.create_sheet("Tuần sau — kết quả mong đợi")
    _header(ws3, ["Kênh", "Số dòng tính", "Tổng Số lượng (hộp)", "Tổng Thành tiền (LAK)", "Số dòng Cần kiểm"],
            [12, 13, 20, 24, 17])
    for k in KENH:
        ws3.append([k, tong_sau[k]["dong"], tong_sau[k]["sl"], tong_sau[k]["tien"], so_can_kiem[k]])
    ws3.append(["Tổng cộng", sum(t["dong"] for t in tong_sau.values()),
                sum(t["sl"] for t in tong_sau.values()), sum(t["tien"] for t in tong_sau.values()),
                sum(so_can_kiem.values())])
    ws3.append([])
    ws3.append(["Chỉ tính các dòng không có lỗi; dòng trùng tính một lần (bản gốc). "
                "Đây là kết quả Skill mẫu tong-hop-don-hang phải ra."])
    for row in ws3.iter_rows(min_row=2, max_row=5):
        for c in row[1:4]:
            c.number_format = "#,##0"
    wb.save(path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=HERE, help="thư mục ghi file (mặc định: cạnh script)")
    out = ap.parse_args(argv).out
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):  # pragma: no cover
        pass
    os.makedirs(out, exist_ok=True)
    rng = random.Random(SEED)

    tuan1 = tao_tuan(rng, dt.datetime(2026, 10, 5))
    tuan2_sach = tao_tuan(rng, dt.datetime(2026, 10, 12))
    tuan2, loi, vi_tri = cai_loi(rng, tuan2_sach)

    ghi_bang(os.path.join(out, "bang-tinh-mau.xlsx"), tuan1)
    ghi_bang(os.path.join(out, "bang-tinh-mau-tuan-sau.xlsx"), tuan2, cot_gia="Giá bán")

    bo = set(vi_tri["thieu"]) | {vi_tri["trung"][1], vi_tri["vi"]}
    so_can_kiem = {k: 0 for k in KENH}
    for n in bo:
        so_can_kiem[tuan2[n - 2]["Kênh"]] += 1
    tong1 = tong_theo_kenh(tuan1)
    tong2 = tong_theo_kenh(tuan2, bo_dong=bo)
    ghi_dap_an(os.path.join(out, "dap-an-mau.xlsx"), tong1, loi, tong2, so_can_kiem)

    print("Đã ghi 3 file vào", out)
    print("Tuần 1: %d dòng" % len(tuan1))
    for k in KENH:
        print("  %-4s %2d dòng  SL %6d  Thành tiền %14s LAK"
              % (k, tong1[k]["dong"], tong1[k]["sl"], format(tong1[k]["tien"], ",")))
    print("  Tổng      SL %6d  Thành tiền %14s LAK"
          % (sum(t["sl"] for t in tong1.values()), format(sum(t["tien"] for t in tong1.values()), ",")))
    print("Tuần sau: %d dòng; lỗi cài sẵn:" % len(tuan2))
    for item in loi:
        print("  %-12s dòng %-3s %s" % (item[0], item[1], item[3]))


if __name__ == "__main__":
    main()
