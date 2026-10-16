# Tủ khả năng — thẻ "À, Claude làm được cái này" (v0.6)

Mỗi thẻ là một việc **chạy được ngay trên dữ liệu mẫu** của lớp, gói thành một lệnh **một chạm** (`state.one_touch`): học viên bấm nút ▶ trên bục, lệnh được điền vào ô nhập, học viên tự bấm **Enter**, Claude làm thật, và giáo viên nói một câu "À". Dùng trong trò **Đoán xem** và **Hộp quà khả năng** ([kho-tro-choi.md](kho-tro-choi.md)), khi một phần học còn thiếu khoảnh khắc "À" ([nang-luc-giao-vien.md](nang-luc-giao-vien.md) §3), hoặc khi cần đổi kiểu tương tác.

Toàn bộ dữ liệu trong `assets/mau/` là **GIẢ** (tên kết thúc bằng "— mẫu"); không phải số liệu của NNC hay của tập đoàn.

---

## 0. Chuẩn bị: chép file mẫu vào `Thuc-hanh/`

Học viên và lệnh một chạm **chỉ nói tới file trong `Thuc-hanh/`** — thư mục thực hành bên trong thư mục lớp học. Không bao giờ đưa đường dẫn của Skill vào lời nói hay vào `one_touch.text`.

**Tìm thư mục gốc của Skill (model instruction).** When the Skill tool loads this Skill, its output starts with a line like `Base directory for this skill: <path>`. Build every source path from it:

- sample file: `<base>/assets/mau/<relative path>` (e.g. `<base>/assets/mau/gop/don-hang-tuan-40.xlsx`)
- sample Skill: `<base>/assets/skill-mau/tong-hop-don-hang/`

No such header in this conversation (e.g. plain chat, Skill loaded another way) → find the file with a file search for its exact name under a `work-first-learning/assets/` folder. **Never guess a path.** Not found → say so in one line and use the CSV fallback in [buoi-1.md](buoi-1.md) §P2.1.

**Copy (model instruction).**
- Create `Thuc-hanh/` in the classroom folder (the working directory) if missing; mirror the sample's relative path inside it (`Thuc-hanh/gop/…`, `Thuc-hanh/tim-loi/…`, `Thuc-hanh/ban-la-sep/…`).
- Copy with the shell this host provides (`cp` in Bash, `Copy-Item` in PowerShell), paths quoted. Say one line before the permission box (T21): *"Claude sắp chép một file mẫu vào thư mục Thuc-hanh, không sửa gì khác — đây là thẻ Quyền."*
- File already in `Thuc-hanh/` → **reuse it**, do not overwrite (the learner may have changed it). Need a fresh copy → add a suffix (`-2`).
- **Never copy answer keys** (`dap-an-mau.xlsx`, `tim-loi/dap-an-tim-loi.md`, `ban-la-sep/dap-an.md`) into the classroom folder. Read them from `<base>` with the Read tool when you need them; never show them before the learner has answered.
- Copying sample files is teacher autonomy (sample data). It is also a good **first one-touch**: the learner presses Enter on a command like "Chép bảng đơn hàng mẫu của lớp vào thư mục Thuc-hanh rồi …"; you resolve the source path yourself.

**Các file mẫu và nơi dùng** (đường dẫn tính từ `<base>/assets/mau/`, chép sang cùng đường dẫn trong `Thuc-hanh/`):

| File mẫu | Dùng ở | Đáp án (không chép) |
|---|---|---|
| `bang-tinh-mau.xlsx` | thẻ 1, 4, 6; phần 0 và phần 2 Buổi 1; Người với máy | `dap-an-mau.xlsx`, README |
| `bang-tinh-mau-tuan-sau.xlsx` | thẻ 8, 9 (và biến thể thẻ 3); Thử thách 60 giây; nhánh đang lên | `dap-an-mau.xlsx`, README |
| `gop/don-hang-tuan-40.xlsx` · `gop/don-hang-tuan-41.xlsx` · `gop/don-hang-tuan-42.xlsx` | thẻ 2 (cả ba), thẻ 3 (tuần 41 với 42); trò tự chế "Tổng kiểm soát" | README phần v0.6 |
| `phieu-nhan-hang-mau.png` | thẻ 7; trò tự chế "Soát phiếu" | README phần v0.6 (bảng mong đợi) |
| `thong-bao-noi-bo-mau.md` | thẻ 5, thẻ 6 | đọc file để kiểm |
| `tim-loi/bang-tim-loi.xlsx` | trò Tìm lỗi | `tim-loi/dap-an-tim-loi.md` |
| `ban-la-sep/ket-qua-claude-mau.xlsx` | trò Bạn là sếp (nguồn đối chiếu: `bang-tinh-mau.xlsx`) | `ban-la-sep/dap-an.md` |
| `../skill-mau/tong-hop-don-hang/` | thẻ 9; nhánh vững hết giờ | README (kết quả tuần sau) |

**Đọc file xlsx (model instruction).** Office machines often have **no Python**. Try in this order, without installing anything: (1) a short script with a library that is already installed; (2) on Windows with Excel installed, PowerShell opening the workbook **read-only** through Excel and printing the used range, then closing Excel; (3) the **`.csv` twin** that ships next to every sample (`bang-tinh-mau.csv`, `gop/don-hang-tuan-40.csv`, …, same rows, UTF-8): copy it into `Thuc-hanh/` beside the xlsx and read it with the Read tool. Say in one line which way you used (*"Máy này chưa đọc được Excel trực tiếp, cô dùng bản CSV cùng dữ liệu"*). Never invent the content. For the learner's own `.xlsx` with no reader available: ask them to **Save As CSV** a copy in Excel (a good real skill), never install software to teach.

**Kiểm con số trước khi nói.** Expected numbers below come from `assets/mau/README.md`. For a file whose numbers are not listed there, verify by reading the file yourself before you state anything; never state a number you have not seen.

---

## 1. Chọn thẻ theo việc của học viên

| Việc của học viên | Thẻ gần nhất |
|---|---|
| Bán hàng OTC / HC / SPM, sale admin | 1 Đọc và tóm tắt · 4 Vẽ biểu đồ · 6 Soạn thư nháp |
| Kho, giao nhận | 7 Đọc ảnh phiếu · 2 Gộp nhiều file · 8 Kiểm và đánh dấu lỗi |
| Kế toán, đối chiếu | 3 So sánh hai bảng · 2 Gộp nhiều file · 8 Kiểm và đánh dấu lỗi |
| Hành chính, nhân sự, truyền thông nội bộ | 5 Dịch Việt ↔ Lào · 6 Soạn thư nháp |
| Hiện trường (xây dựng, điện lạnh) | 7 Đọc ảnh phiếu · 6 Soạn thư nháp |
| Việc lặp lại đã làm đúng một lần | 9 Biến việc thành Skill |

Trong hộp quà: thẻ gần việc nhất đặt **đầu tiên**, ghi "(đề xuất)".

---

## 2. Các thẻ

### Thẻ 1 · Đọc và tóm tắt bảng tính — `doc-tom-tat-bang`
- **Chép:** `bang-tinh-mau.xlsx` → `Thuc-hanh/bang-tinh-mau.xlsx`
- **one_touch:** `{ "label": "Cho Claude đọc bảng đơn hàng", "text": "Đọc file Thuc-hanh/bang-tinh-mau.xlsx và cho tôi biết: có mấy kênh bán hàng, mỗi kênh bao nhiêu dòng và tổng thành tiền mỗi kênh." }`
- **Kết quả thấy được:** 40 dòng, 3 kênh — OTC 14 dòng · 20.950.000 LAK; HC 13 dòng · 44.200.000 LAK; SPM 13 dòng · 36.720.000 LAK; tổng 101.870.000 LAK.
- **Câu "À":** *"40 dòng, vài giây — và chị chưa phải mở Excel lần nào."*
- **An toàn:** chỉ đọc, không sửa file. Con số là của file mẫu, không phải doanh số NNC.
- **Sang file của học viên:** hộp an toàn dữ liệu trước (*"File này có tên khách hàng, giá vốn, công nợ hay lương không?"* — **Có hoặc không chắc — dùng mẫu** (mặc định) · **Đã che hết rồi**); học viên tự kéo **bản sao** vào `Thuc-hanh/`; lệnh giữ nguyên, chỉ đổi tên file.

### Thẻ 2 · Gộp nhiều file — `gop-nhieu-file`
- **Chép:** `gop/don-hang-tuan-40.xlsx`, `gop/don-hang-tuan-41.xlsx`, `gop/don-hang-tuan-42.xlsx` → `Thuc-hanh/gop/`
- **one_touch:** `{ "label": "Gộp đơn hàng 3 tuần", "text": "Gộp ba file đơn hàng trong Thuc-hanh/gop thành một bảng mới Thuc-hanh/gop/don-hang-3-tuan.xlsx, thêm cột Tuần, rồi báo số dòng của từng file và của bảng gộp." }`
- **Kết quả thấy được:** một file mới 60 dòng (20 + 20 + 20); tổng thành tiền 194.085.000 LAK = 58.475.000 (tuần 40) + 67.550.000 (tuần 41) + 68.060.000 (tuần 42). Ba file gốc không đổi.
- **Câu "À":** *"Ba file, một bảng, và có sẵn con số để chị đối chiếu."*
- **An toàn:** kết quả ghi ra file mới, không ghi đè file gốc. Cột khác tên giữa các tuần → Claude phải nói ra, không tự đoán.
- **Sang file của học viên:** như thẻ 1; chỉ gộp những file học viên đã chép vào `Thuc-hanh/`.

### Thẻ 3 · So sánh hai bảng — `so-sanh-hai-bang`
- **Chép:** `gop/don-hang-tuan-41.xlsx` và `gop/don-hang-tuan-42.xlsx` → `Thuc-hanh/gop/`
- **one_touch:** `{ "label": "So tuần 41 với tuần 42", "text": "So sánh Thuc-hanh/gop/don-hang-tuan-41.xlsx với Thuc-hanh/gop/don-hang-tuan-42.xlsx: tổng thành tiền mỗi kênh thay đổi thế nào, và những dòng nào gây ra thay đổi đó." }`
- **Kết quả thấy được:** đúng ba thay đổi — khách mới *Nhà thuốc P — mẫu* (OTC 7.450.000 → 11.200.000); khẩu trang của *Bệnh viện H — mẫu* từ 20 lên 200 hộp (HC 44.500.000 → 51.700.000); hai đơn SPM biến mất (SPM 15.600.000 → 5.160.000, −67%).
- **Câu "À":** *"Hai tuần, ba thay đổi, chỉ đúng tên khách và dòng — họp giao ban có ngay chuyện để hỏi."*
- **An toàn:** Claude chỉ nêu chỗ khác; **vì sao** khác (khách mới thật hay gõ nhầm 200?) là câu hỏi cho người phụ trách, không đoán. Biến thể đầu vào lỗi: `bang-tinh-mau.xlsx` với `bang-tinh-mau-tuan-sau.xlsx` (cột đổi tên, thiếu giá, trùng, lệch đơn vị — README v0.5).
- **Sang file của học viên:** hai bản sao của **cùng một loại báo cáo** ở hai kỳ; hỏi an toàn dữ liệu cho cả hai.

### Thẻ 4 · Vẽ biểu đồ — `ve-bieu-do`
- **Chép:** `bang-tinh-mau.xlsx` → `Thuc-hanh/` (thường đã có)
- **one_touch:** `{ "label": "Vẽ biểu đồ theo kênh", "text": "Vẽ biểu đồ cột tổng thành tiền theo kênh từ Thuc-hanh/bang-tinh-mau.xlsx, lưu thành file mới trong Thuc-hanh và cho tôi biết kênh nào cao nhất." }`
- **Kết quả thấy được:** một file biểu đồ mới (ảnh, hoặc file Excel có biểu đồ); HC cao nhất, rồi SPM, rồi OTC.
- **Câu "À":** *"Từ bảng số sang hình trong một câu lệnh — mang đi họp giao ban được ngay."*
- **An toàn:** máy không có công cụ vẽ → Claude nói thật và đưa bảng xếp hạng bằng chữ; không cài thêm phần mềm để dạy.
- **Sang file của học viên:** như thẻ 1; biểu đồ là của file đó, không trình như số liệu toàn công ty.

### Thẻ 5 · Dịch Việt ↔ Lào — `dich-viet-lao`
- **Chép:** `thong-bao-noi-bo-mau.md` → `Thuc-hanh/`
- **one_touch (học viên Việt):** `{ "label": "Dịch thông báo sang tiếng Lào", "text": "Dịch thông báo trong Thuc-hanh/thong-bao-noi-bo-mau.md sang tiếng Lào, lưu thành file mới Thuc-hanh/thong-bao-noi-bo-mau-lo.md; giữ nguyên ngày, giờ và con số." }`
- **one_touch (học viên Lào):** cùng lệnh viết bằng tiếng Lào, dịch sang tiếng Việt, file `…-vi.md`.
- **Kết quả thấy được:** một file mới có bản dịch; ngày, giờ, con số giữ nguyên.
- **Câu "À":** *"Một thông báo, hai thứ tiếng, cả phòng cùng đọc được."*
- **An toàn:** bản dịch **cần người bản ngữ duyệt** trước khi dùng; Claude không gửi đi đâu.
- **Sang file của học viên:** chỉ văn bản nội bộ không có thông tin nhạy cảm; vẫn là bản sao trong `Thuc-hanh/`.

### Thẻ 6 · Soạn thư nháp (không gửi) — `soan-thu-nhap`
- **Chép:** `thong-bao-noi-bo-mau.md` → `Thuc-hanh/`
- **one_touch:** `{ "label": "Soạn nháp thư báo lịch giao", "text": "Dựa vào thông báo trong Thuc-hanh/thong-bao-noi-bo-mau.md, soạn nháp một thư ngắn, lịch sự báo khách nhà thuốc về lịch giao hàng dịp nghỉ lễ. Chỉ lưu nháp vào Thuc-hanh/thu-bao-lich-giao.md, không gửi." }`
- **Kết quả thấy được:** một file nháp đúng các mốc của thông báo: Thứ Sáu 20/11 kho làm đến 12:00 (đơn sau 10:00 giao ngày làm việc tiếp theo), nghỉ 21–22/11, làm lại 7:30 Thứ Hai 23/11, chốt đơn trước 16:00 Thứ Năm 19/11.
- **Câu "À":** *"Thư nháp có đúng mọi ngày giờ của thông báo — chị chỉ việc đọc, sửa giọng và tự gửi."*
- **An toàn:** **không bao giờ gửi**; Claude không có quyền gửi thư thay học viên. Số trong thư phải đối chiếu với bảng.
- **Sang file của học viên:** thư cho khách thật là việc của học viên; Claude chỉ soạn nháp từ dữ liệu đã được phép dùng.

### Thẻ 7 · Đọc ảnh hoặc PDF phiếu — `doc-anh-phieu`
- **Chép:** `phieu-nhan-hang-mau.png` → `Thuc-hanh/`
- **one_touch:** `{ "label": "Chép phiếu nhận hàng thành bảng", "text": "Đọc ảnh Thuc-hanh/phieu-nhan-hang-mau.png và chép các dòng hàng thành bảng mới Thuc-hanh/phieu-nhan-hang.xlsx gồm mã hàng, tên hàng, số lượng, đơn vị. Chỗ nào mờ hoặc không chắc thì ghi Cần kiểm, không đoán." }`
- **Kết quả thấy được:** bảng 6 dòng (phiếu PNH-MAU-001, 14/10/2026), từ *Vitamin C 500mg — mẫu 30 hộp* đến *Nước rửa tay — mẫu 36 hộp*; có một dòng tính bằng **thùng** (*Khăn giấy — mẫu 5 thùng*) — Claude phải giữ đúng đơn vị, không đổi sang hộp. Giáo viên tự xem ảnh để kiểm 3 dòng trước khi khen.
- **Câu "À":** *"Phiếu giấy thành bảng Excel mà không phải gõ lại — chị chỉ soát số lượng."*
- **An toàn:** chép từ ảnh luôn phải soát lại với phiếu gốc; PDF làm cùng cách. Ảnh phiếu thật có thể chứa tên khách, chữ ký → hỏi an toàn dữ liệu trước.
- **Sang file của học viên:** ảnh phiếu đã che thông tin khách, chép vào `Thuc-hanh/`.

### Thẻ 8 · Kiểm và đánh dấu lỗi — `kiem-danh-dau-loi`
- **Chép:** `bang-tinh-mau-tuan-sau.xlsx` → `Thuc-hanh/`. (Học viên sắp chơi **Tìm lỗi** thì **không** dùng `tim-loi/bang-tim-loi.xlsx` cho thẻ này — đừng lộ đáp án trò chơi.)
- **one_touch:** `{ "label": "Kiểm lỗi bảng tuần sau", "text": "Kiểm Thuc-hanh/bang-tinh-mau-tuan-sau.xlsx: tìm dòng thiếu giá, dòng trùng, đơn vị lệch và cột đổi tên. Ghi lý do vào cột Cần kiểm trong một file mới, không sửa file gốc." }`
- **Kết quả thấy được:** file mới có cột Cần kiểm ở 5 dòng (4, 12, 15, 21, 31) và một câu về cột "Giá bán".
- **Câu "À":** *"Claude soát 41 dòng và chỉ đúng chỗ cần hỏi — mình chỉ việc hỏi người có nguồn."*
- **An toàn:** đánh dấu, không sửa; không tự điền, không tự quy đổi.
- **Sang file của học viên:** như thẻ 1; danh sách lỗi là gợi ý để người phụ trách kiểm, không phải kết luận.

### Thẻ 9 · Biến việc thành Skill — `bien-viec-thanh-skill`
- **Chép:** thư mục `<base>/assets/skill-mau/tong-hop-don-hang/` → `Thuc-hanh/skill-mau/tong-hop-don-hang/` (để học viên đọc được); `bang-tinh-mau-tuan-sau.xlsx` → `Thuc-hanh/`
- **one_touch:** `{ "label": "Chạy Skill mẫu của lớp", "text": "Đọc Skill mẫu trong Thuc-hanh/skill-mau/tong-hop-don-hang rồi làm đúng các bước của nó trên file Thuc-hanh/bang-tinh-mau-tuan-sau.xlsx." }`
- **Kết quả thấy được:** một file tổng hợp mới: 36 dòng được tính, 5 dòng Cần kiểm; OTC 19.850.000 · HC 62.750.000 · SPM 21.840.000 · tổng 104.440.000 LAK; Claude nói rõ đã hiểu "Giá bán" là Đơn giá.
- **Câu "À":** *"Lần sau chỉ cần gọi tên là Claude làm đúng như hôm nay — kể cả bước kiểm."*
- **An toàn:** Skill mới thường dùng được ở **phiên mới**; trong phiên này Claude làm theo các bước của nó. Chỉ đóng gói việc đã làm đúng và có cách kiểm. Không cài Skill vào chỗ khác ngoài thư mục lớp.
- **Sang việc của học viên:** đóng gói Skill nháp từ chính 4 ý học viên đã viết (Buổi 1 phần 3, nhánh vững).

---

## 3. Sau mỗi thẻ

1. Học viên bấm Enter → Claude làm → giáo viên nói **câu "À"** (một câu, `hi`), rồi một câu hỏi kiểm nhanh về kết quả (bậc 2: "đúng" khi học viên trả lời đúng).
2. `one_touch: null` (hoặc lệnh một chạm kế tiếp); `gift_box: false` nếu thẻ đến từ hộp quà.
3. Không trao sao cho việc mở thẻ (khám phá, không phải thành tích). Sao và huy hiệu chỉ theo [huy-hieu.md](huy-hieu.md).
4. Mời chuyển sang file của học viên **chỉ khi** học viên tỏ ra muốn ("cái này tôi cần cho việc của tôi"): hộp an toàn dữ liệu, mặc định vẫn là mẫu.
