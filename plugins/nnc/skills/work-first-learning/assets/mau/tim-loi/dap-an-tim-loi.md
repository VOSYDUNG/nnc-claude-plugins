# Đáp án trò "Tìm lỗi" — dành cho giáo viên

> Dữ liệu GIẢ để học. File: `bang-tim-loi.xlsx` (25 dòng đơn hàng, tuần 19–24/10/2026). Số dòng tính theo Excel: dòng 1 là tiêu đề, dữ liệu từ dòng 2 đến 26.

Có **đúng 3 lỗi**, mỗi lỗi một kiểu khác nhau. Mọi dòng còn lại đều đúng: Thành tiền = Số lượng × Đơn giá, ngày trong tuần, kênh là OTC/HC/SPM, đơn vị là hộp, giá đúng bảng giá mẫu.

| # | Dòng | Ô | Loại lỗi | Vì sao sai |
|---|---:|---|---|---|
| 1 | 7 | B7 | Mã kênh gõ nhầm | Kênh = "OCT" (đúng là "OTC"; khách Nhà thuốc B — mẫu là nhà thuốc) |
| 2 | 15 | I15 | Thành tiền sai | Thành tiền ghi 785.000 nhưng 25 × 35.000 = 875.000 (đảo hai chữ số) |
| 3 | 21 | A21 | Ngày ngoài tuần | Ngày 24/11/2026 nằm ngoài tuần 19–24/10/2026 (có lẽ gõ nhầm tháng, đúng là 24/10/2026) |

**Cách thắng:** tìm đủ 3 lỗi và nói được vì sao trong 3 phút.

**Câu bài học:** Nhờ Claude kiểm từng loại lỗi một (công thức, ngày, mã kênh) rồi tự xem lại đúng các dòng nó chỉ ra — kiểm trước khi tin.
