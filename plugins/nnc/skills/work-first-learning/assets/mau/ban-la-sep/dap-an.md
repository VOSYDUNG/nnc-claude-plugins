# Đáp án trò "Bạn là sếp" — dành cho giáo viên

> Dữ liệu GIẢ để học. `ket-qua-claude-mau.xlsx` là bản tổng hợp theo kênh "như thể Claude làm" từ `../bang-tinh-mau.xlsx` (tuần 05–10/10/2026). Học viên đóng vai sếp: **Đạt** hay **Trả lại vì…**

**Đáp án đúng: Trả lại**, vì hai lý do:

## 1. Một tổng bị sai

- Ô **D3** — kênh **HC**, cột *Tổng Thành tiền (LAK)*: file ghi **43.250.000**, đúng là **44.200.000**, lệch **-950.000 LAK** (thiếu 950.000).
- Nguyên nhân giả định: bỏ sót dòng 39 của `bang-tinh-mau.xlsx` (Phòng khám E — mẫu · Dung dịch sát khuẩn — mẫu · 10 hộp × 95.000), dù cột Số dòng vẫn ghi 13.
- Dấu hiệu tự phát hiện, không cần mở file nguồn: OTC + HC + SPM = 100.920.000, **không bằng** dòng Tổng cộng 101.870.000.
- Mọi ô số khác đều đúng: cả cột Số dòng, cả cột Tổng Số lượng, Tổng Thành tiền của OTC và SPM, và toàn bộ dòng Tổng cộng.

## 2. Thiếu một ghi chú

- Phần Ghi chú **không nói nguồn và kỳ dữ liệu**: lấy từ file nào, tuần nào. Thiếu dòng này thì người nhận không đối chiếu lại được. Ghi chú cần có, ví dụ: *Nguồn: bang-tinh-mau.xlsx, tuần 05–10/10/2026.*
- Ghi chú "đã cộng đủ các dòng" lại là khẳng định chưa được kiểm — đúng chỗ phải nghi.

## Bảng đúng để đối chiếu

| Kênh | Số dòng | Tổng Số lượng (hộp) | Tổng Thành tiền (LAK) |
|---|---:|---:|---:|
| OTC | 14 | 375 | 20.950.000 |
| HC | 13 | 530 | 44.200.000 |
| SPM | 13 | 504 | 36.720.000 |
| **Tổng cộng** | **40** | **1.409** | **101.870.000** |

**Câu trả lại mẫu:** "Trả lại vì tổng Thành tiền HC không khớp — ba kênh cộng lại không ra tổng cộng; và thiếu ghi chú nguồn, kỳ dữ liệu."

**Câu bài học:** Sếp giỏi không làm lại từ đầu — sếp kiểm vài chỗ then chốt (cộng ngang, đối chiếu tổng, đọc ghi chú) rồi mới ký Đạt.
