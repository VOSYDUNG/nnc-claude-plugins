---
name: tong-hop-don-hang
description: Tổng hợp một bảng tính đơn hàng (xlsx/csv) theo kênh bán OTC / HC / SPM ra một file xlsx mới. Kiểm cột và từng dòng TRƯỚC khi tính (cột đổi tên, thiếu giá, dòng trùng, đơn vị lệch), ghi vấn đề vào cột "Cần kiểm" thay vì đoán, rồi chỉ cho người dùng cách tự kiểm lại một kênh bằng tay. Dùng khi người dùng nói "tổng hợp đơn hàng", "cộng theo kênh", "tổng hợp file bán hàng tuần này", hoặc đưa một file đơn hàng và hỏi tổng. Đây là Skill MẪU của lớp học NNC, chạy trên dữ liệu giả.
version: 0.1.0
---

# Tổng hợp đơn hàng theo kênh (Skill mẫu — lớp học NNC)

**Purpose:** turn one order spreadsheet into a per-channel summary the user can trust, by checking the input before computing and never inventing values. Speak to the user in the language they use (Vietnamese or Lao); keep these instructions in English.

Sample input for practice: `assets/mau/bang-tinh-mau.xlsx` (clean) and `assets/mau/bang-tinh-mau-tuan-sau.xlsx` (planted defects). Expected results: `assets/mau/dap-an-mau.xlsx`.

## 1. Before reading

- Confirm the file path and which sheet holds the orders. One question at most if unclear.
- If the file looks like real company data (real customer names, cost prices, debts, salaries), say so in one sentence: the data stays on this machine, nothing is uploaded or pasted elsewhere. Numbers in the file describe that file only; do not present them as NNC or group-wide totals.
- Never modify the source file. Output always goes to a new file.

## 2. Check columns (before any arithmetic)

Required columns and accepted equivalents:

| Required | Accept as equivalent (tell the user you did) |
|---|---|
| Ngày | Ngày đặt, Ngày đơn |
| Kênh | Kênh bán |
| Khách hàng | Khách, Tên khách |
| Mã hàng | Mã SP, Mã sản phẩm |
| Số lượng | SL |
| Đơn vị | ĐVT |
| Đơn giá | Giá bán, Giá |
| Thành tiền | (optional — recomputed if missing) |

- An equivalent header is accepted but **stated** to the user, e.g. *"Cột 'Giá bán' em hiểu là Đơn giá."*
- A required column with no match: stop and ask. Do not guess which column it is.
- Extra columns are kept in the detail sheet, untouched.

## 3. Check every row

Write each problem into a new column **"Cần kiểm"** (short Vietnamese text, one or more reasons separated by "; "). A flagged row is **excluded from totals** and counted separately.

| Problem | Rule | "Cần kiểm" text |
|---|---|---|
| Missing price | Đơn giá empty or not a number | `Thiếu đơn giá` — never fill in a price from another row or week |
| Duplicate | Same Ngày + Khách hàng + Mã hàng + Số lượng as an earlier row | `Có thể trùng dòng N` on the later row; the first occurrence is counted |
| Unit mismatch | Đơn vị differs from the unit used by most rows | `Đơn vị "vỉ" khác "hộp"` — never convert units yourself |
| Wrong amount | Thành tiền present and ≠ Số lượng × Đơn giá | `Thành tiền lệch: file X, tính lại Y` |
| Unknown channel | Kênh not OTC / HC / SPM | `Kênh không rõ` |

Row numbers are Excel row numbers (header = row 1), so the user can find them.

## 4. Build the output

Create `tong-hop-<source-name>.xlsx` next to the source (ask before overwriting an existing file). Prefer a short Python script with openpyxl; if openpyxl is missing, ask before installing anything, or write CSV instead and say so.

- Sheet **"Tổng hợp theo kênh"**: Kênh · Số dòng tính · Tổng Số lượng · Tổng Thành tiền · Số dòng Cần kiểm, plus a Tổng cộng row. State the unit in the header (e.g. "Tổng Số lượng (hộp)").
- Sheet **"Chi tiết"**: all source rows in original order, plus the "Cần kiểm" column; flagged rows highlighted.
- Totals use only unflagged rows. Never put a guessed value in any cell.

## 5. Report to the user (Vietnamese, short)

1. One line: file read, number of rows, columns understood (mention any renamed column).
2. The per-channel table.
3. The "Cần kiểm" list: row number + reason, at most 10 lines, then "và N dòng khác trong sheet Chi tiết".
4. **How to verify, by hand, in under 2 minutes:** *"Mở file gốc trong Excel, lọc cột Kênh lấy một kênh (ví dụ HC), bỏ các dòng Cần kiểm, chọn cột Thành tiền và xem tổng ở thanh trạng thái phía dưới. Số đó phải bằng dòng HC trong bảng tổng hợp."*
5. One question for the flagged rows: who can confirm the missing prices / duplicates (e.g. người phụ trách đơn), and whether to rerun after they are fixed.

## 6. Do not

- Do not drop, merge or "fix" rows silently.
- Do not fill missing prices from a price list, another week or an average.
- Do not add quantities in different units.
- Do not claim the summary is correct before the user has checked one channel.

## Self-check with the sample files

Running this Skill on `bang-tinh-mau-tuan-sau.xlsx` must give exactly the sheet *"Tuần sau — kết quả mong đợi"* in `dap-an-mau.xlsx`: 36 counted rows, 5 rows in "Cần kiểm" (rows 4, 12, 15, 21, 31), and the "Giá bán" column reported as Đơn giá. On `bang-tinh-mau.xlsx` it must match sheet *"Tổng hợp theo kênh"* with zero flagged rows.
