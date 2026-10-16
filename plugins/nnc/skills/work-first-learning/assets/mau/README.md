# Dữ liệu mẫu — Lớp học NNC, Buổi 1

> **TOÀN BỘ DỮ LIỆU TRONG THƯ MỤC NÀY LÀ GIẢ.** Khách hàng, mặt hàng, mã hàng và giá đều bịa ra để tập; mọi tên đều kết thúc bằng "— mẫu". Đây **không phải** số liệu của NNC, của tập đoàn hay của bất kỳ khách hàng, nhà cung cấp nào. Không dùng các con số này để báo cáo hay ra quyết định.

Dùng khi học viên không có file việc thật phù hợp, hoặc lỡ mở file có dữ liệu nhạy cảm (giá vốn, công nợ, lương, danh sách khách hàng thật) — khi đó dừng lại và chuyển sang file mẫu.

## Các tệp

| Tệp | Là gì | Dùng ở đâu |
|---|---|---|
| `bang-tinh-mau.xlsx` | 40 dòng đơn hàng tuần 05–10/10/2026, sạch, nhất quán. Cột: Ngày · Kênh · Khách hàng · Mã hàng · Tên hàng · Số lượng · Đơn vị · Đơn giá · Thành tiền. Ba kênh OTC (nhà thuốc), HC (bệnh viện, phòng khám), SPM (tạp hoá, siêu thị). Đơn vị đều là hộp, giá tính bằng LAK | **Buổi 1 phần 2** — file dự phòng cho "Việc thật của tôi" khi học viên không có file |
| `bang-tinh-mau-tuan-sau.xlsx` | Tuần 12–17/10/2026, cùng cấu trúc nhưng **cài sẵn lỗi** (xem dưới) | **Buổi 1 phần 3, nhánh Đang lên** — "tuần sau file đổi, việc cũ còn chạy đúng không?" |
| `dap-an-mau.xlsx` | Đáp án cho giáo viên và người đứng lớp. Sheet *Tổng hợp theo kênh*: tổng Số lượng và Thành tiền từng kênh của `bang-tinh-mau.xlsx`. Sheet *Lỗi cài sẵn tuần sau*: danh sách lỗi kèm số dòng. Sheet *Tuần sau — kết quả mong đợi*: tổng đúng của tuần sau khi đã loại các dòng lỗi | Đối chiếu kết quả học viên; **kiểm Skill mẫu** |
| `../skill-mau/tong-hop-don-hang/SKILL.md` | Skill mẫu đã kiểm: tổng hợp bảng đơn hàng theo kênh ra file xlsx mới, **kiểm cột trước khi tính**, ghi vấn đề vào cột "Cần kiểm" thay vì đoán | **Buổi 1 phần 3, nhánh Vững** khi hết giờ; và để chạy thử trên file tuần sau |
| `_tao-du-lieu.py` | Script sinh lại ba file xlsx (seed cố định, chạy lại ra đúng nội dung cũ). Cần `openpyxl` | Người bảo trì; không đưa cho học viên |

## Đáp án tuần mẫu (`bang-tinh-mau.xlsx`)

| Kênh | Số dòng | Tổng Số lượng (hộp) | Tổng Thành tiền (LAK) |
|---|---:|---:|---:|
| OTC | 14 | 375 | 20.950.000 |
| HC | 13 | 530 | 44.200.000 |
| SPM | 13 | 504 | 36.720.000 |
| **Tổng cộng** | **40** | **1.409** | **101.870.000** |

## Lỗi cài sẵn trong `bang-tinh-mau-tuan-sau.xlsx`

Số dòng tính theo Excel (dòng 1 là tiêu đề; dữ liệu từ dòng 2 đến 42, tức 41 dòng).

| # | Loại lỗi | Dòng | Chi tiết | Cách xử lý đúng |
|---|---|---|---|---|
| 1 | Cột đổi tên | 1 (ô H1) | "Đơn giá" thành **"Giá bán"** | Nhận ra cột tương đương, nói rõ đã hiểu như vậy |
| 2 | Thiếu giá | 4 | HC · Bơm tiêm 5ml — mẫu | Ghi "Cần kiểm", không tự điền giá, không cộng vào tổng |
| 3 | Thiếu giá | 15 | OTC · Viên ngậm thảo dược — mẫu | Như trên |
| 4 | Thiếu giá | 21 | SPM · Khăn giấy — mẫu | Như trên |
| 5 | Dòng trùng | 12 | Trùng hoàn toàn với dòng 10 (Siêu thị M — mẫu · Kem đánh răng — mẫu · 13/10 · 60 hộp) | Chỉ tính một lần, đánh dấu dòng 12 "Cần kiểm", hỏi người phụ trách đơn |
| 6 | Đơn vị lệch | 31 | Paracetamol 500mg — mẫu, 20 **vỉ** (cả bảng là hộp) | Không cộng chung với hộp, không tự quy đổi; ghi "Cần kiểm" |

Kết quả đúng của tuần sau khi loại 5 dòng cần kiểm (dòng 4, 12, 15, 21, 31):

| Kênh | Số dòng tính | Tổng Số lượng (hộp) | Tổng Thành tiền (LAK) | Dòng Cần kiểm |
|---|---:|---:|---:|---:|
| OTC | 12 | 225 | 19.850.000 | 2 |
| HC | 12 | 660 | 62.750.000 | 1 |
| SPM | 12 | 456 | 21.840.000 | 2 |
| **Tổng cộng** | **36** | **1.341** | **104.440.000** | **5** |

Nếu Claude (hoặc Skill mẫu) ra con số khác bảng trên, hoặc tự điền giá cho 3 dòng thiếu giá, thì đó chính là bài học: **kiểm tra trước khi tin**.

## Cách kiểm nhanh bằng tay

Mở file trong Excel, lọc cột Kênh lấy một kênh (ví dụ HC), chọn cột Thành tiền và nhìn tổng ở thanh trạng thái. So với bảng đáp án ở trên.

## Sinh lại dữ liệu

```
python plugins/nnc/skills/work-first-learning/assets/mau/_tao-du-lieu.py
python -m unittest tests.test_lop_hoc_sample_data -v
```

Đổi nội dung script thì phải cập nhật các bảng trong README này cho khớp (test sẽ báo nếu file và đáp án lệch nhau).

---

# Dữ liệu mẫu v0.6 — trò chơi và Tủ khả năng

> **VẪN LÀ DỮ LIỆU GIẢ.** "Công ty Mẫu", "Kho mẫu", "Phòng Kho vận — mẫu", mọi khách hàng, mặt hàng, mã hàng (`MAU-…`), giá, ngày và số máy lẻ đều bịa; tên khách và tên hàng đều kết thúc bằng "— mẫu". Không phải số liệu NNC, tập đoàn hay của ai. Dùng cho trò chơi (mục 4.1) và thẻ Tủ khả năng (mục 4.3) trong `docs/oser-r2/LOP-HOC-NANG-LUC-GIAO-VIEN.md`.

## Các tệp v0.6

| Tệp | Là gì | Trò / thẻ dùng |
|---|---|---|
| `gop/don-hang-tuan-40.xlsx` | 20 dòng đơn hàng 28/09–03/10/2026, sạch, cùng cột với `bang-tinh-mau.xlsx` | Thẻ **Gộp nhiều file** |
| `gop/don-hang-tuan-41.xlsx` | 20 dòng 05–10/10/2026, sạch | Thẻ **Gộp nhiều file**, **So sánh hai bảng** |
| `gop/don-hang-tuan-42.xlsx` | 20 dòng 12–17/10/2026, sạch; khác tuần 41 đúng ba điểm (xem dưới) | Thẻ **Gộp nhiều file**, **So sánh hai bảng** |
| `tim-loi/bang-tim-loi.xlsx` | 25 dòng đơn hàng 19–24/10/2026, **đúng 3 lỗi cài sẵn** | Trò **Tìm lỗi**; thẻ **Kiểm và đánh dấu lỗi** |
| `tim-loi/dap-an-tim-loi.md` | Đáp án Tìm lỗi cho giáo viên | Giáo viên |
| `ban-la-sep/ket-qua-claude-mau.xlsx` | Bảng tổng hợp theo kênh "như thể Claude làm" từ `bang-tinh-mau.xlsx`, có **1 tổng sai** và **thiếu 1 ghi chú** | Trò **Bạn là sếp** |
| `ban-la-sep/dap-an.md` | Đáp án Bạn là sếp cho giáo viên | Giáo viên |
| `phieu-nhan-hang-mau.png` | Ảnh phiếu nhận hàng giả 1000×700, "PHIẾU NHẬN HÀNG — MẪU", 6 dòng hàng | Thẻ **Đọc ảnh hoặc PDF** (ảnh → bảng) |
| `thong-bao-noi-bo-mau.md` | Thông báo nội bộ giả: lịch giao hàng và giờ làm kho dịp nghỉ lễ | Thẻ **Dịch Việt ↔ Lào**; thẻ **Viết thư** (thư nhắc lịch giao, soạn nháp) |
| `_tao-du-lieu-v06.py` | Script sinh lại mọi tệp v0.6 (seed cố định). Dùng lại danh mục của `_tao-du-lieu.py`, không sửa file đó. Cần `openpyxl`; `Pillow` để vẽ ảnh | Người bảo trì |

## Gộp nhiều file — đáp án

| Tệp | Số dòng | OTC (LAK) | HC (LAK) | SPM (LAK) | Tổng Số lượng (hộp) | Tổng Thành tiền (LAK) |
|---|---:|---:|---:|---:|---:|---:|
| Tuần 40 | 20 | 9.175.000 | 31.000.000 | 18.300.000 | 838 | 58.475.000 |
| Tuần 41 | 20 | 7.450.000 | 44.500.000 | 15.600.000 | 947 | 67.550.000 |
| Tuần 42 | 20 | 11.200.000 | 51.700.000 | 5.160.000 | 1.093 | 68.060.000 |
| **Gộp 3 tuần** | **60** | **27.825.000** | **127.200.000** | **39.060.000** | **2.878** | **194.085.000** |

## So sánh hai bảng — tuần 42 khác tuần 41 ở đâu

Tuần 42 là tuần 41 dời sang 7 ngày sau, rồi **đúng ba thay đổi**; mọi cặp (Khách hàng, Mã hàng) khác giữ nguyên số lượng. Số dòng theo Excel (dòng 1 là tiêu đề).

| # | Thay đổi | Tuần 41 | Tuần 42 | Giải thích |
|---|---|---|---|---|
| 1 | Khách hàng mới | — | Dòng 5 và 18: **Nhà thuốc P — mẫu** (Vitamin C 500mg 30 hộp; Canxi D3 20 hộp) | OTC tăng 3.750.000 LAK, từ 7.450.000 lên 11.200.000 |
| 2 | Số lượng tăng vọt | Dòng 19: Bệnh viện H — mẫu · Khẩu trang y tế — mẫu · **20 hộp** | Dòng 19: cùng khách, cùng hàng · **200 hộp** (×10) | HC tăng 7.200.000 LAK, từ 44.500.000 lên 51.700.000 |
| 3 | Một kênh giảm | Dòng 17: Siêu thị M — mẫu · Sữa bột — mẫu · 48 hộp · 8.640.000; dòng 18: Tạp hoá C — mẫu · Dầu gội — mẫu · 36 hộp · 1.800.000 | Không còn hai đơn này | SPM giảm 10.440.000 LAK, từ 15.600.000 xuống 5.160.000 (−67%) |

## Tìm lỗi — lỗi cài sẵn trong `tim-loi/bang-tim-loi.xlsx`

25 dòng dữ liệu (dòng Excel 2–26). Đúng 3 lỗi, mỗi lỗi một kiểu; mọi dòng khác đều sạch.

| # | Dòng | Ô | Loại lỗi | Chi tiết |
|---|---:|---|---|---|
| 1 | 7 | B7 | Mã kênh gõ nhầm | Kênh "OCT" thay vì "OTC" (Nhà thuốc B — mẫu) |
| 2 | 15 | I15 | Thành tiền sai | Ghi 785.000 nhưng 25 × 35.000 = 875.000 (đảo hai chữ số) |
| 3 | 21 | A21 | Ngày ngoài tuần | 24/11/2026 thay vì 24/10/2026 (gõ nhầm tháng) |

## Bạn là sếp — chỗ sai trong `ban-la-sep/ket-qua-claude-mau.xlsx`

| Chỗ | Trong file | Đúng | Lệch |
|---|---|---|---|
| Ô D3 — HC, Tổng Thành tiền (LAK) | 43.250.000 | 44.200.000 | −950.000 LAK (bỏ sót dòng 39 của `bang-tinh-mau.xlsx`: Phòng khám E — mẫu · Dung dịch sát khuẩn — mẫu · 10 × 95.000) |
| Phần Ghi chú | Không có nguồn và kỳ dữ liệu | Cần ghi: *Nguồn: bang-tinh-mau.xlsx, tuần 05–10/10/2026* | — |

Mọi ô số khác đúng, kể cả dòng Tổng cộng (101.870.000) — nên OTC + HC + SPM = 100.920.000 không khớp tổng cộng: dấu hiệu sếp tự thấy mà không cần mở file nguồn. Đáp án đúng: **Trả lại vì…** tổng HC sai và thiếu ghi chú nguồn.

## Ảnh phiếu nhận hàng — bảng mong đợi khi đọc `phieu-nhan-hang-mau.png`

Công ty Mẫu → Nhà thuốc A — mẫu · Số phiếu PNH-MAU-001 · Ngày 14/10/2026 · ký: Người giao — mẫu, Người nhận — mẫu.

| STT | Mã hàng | Tên hàng | Số lượng | Đơn vị |
|---:|---|---|---:|---|
| 1 | MAU-OTC-01 | Vitamin C 500mg — mẫu | 30 | hộp |
| 2 | MAU-OTC-02 | Canxi D3 — mẫu | 12 | hộp |
| 3 | MAU-HC-01 | Găng tay y tế — mẫu | 50 | hộp |
| 4 | MAU-HC-05 | Dung dịch sát khuẩn — mẫu | 24 | hộp |
| 5 | MAU-SPM-04 | Khăn giấy — mẫu | 5 | thùng |
| 6 | MAU-SPM-01 | Nước rửa tay — mẫu | 36 | hộp |

## Sinh lại dữ liệu v0.6

```
python plugins/nnc/skills/work-first-learning/assets/mau/_tao-du-lieu-v06.py
python -m unittest tests.test_lop_hoc_v06_assets -v
```

Đổi script thì cập nhật các bảng v0.6 ở trên cho khớp (test sẽ báo nếu lệch).
