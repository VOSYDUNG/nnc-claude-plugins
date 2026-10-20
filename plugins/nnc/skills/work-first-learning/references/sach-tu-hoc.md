<!-- Teacher note (model instruction, not for the learner):
This is the learner's self-study book "Tài liệu đào tạo Claude cơ bản" (v1.0), distributed to learners as a Word file with 11 screenshots (figure numbers below).
Use it as the CANONICAL SOURCE and the FALLBACK, never as a script:
- Teach by the goal of the current part; do not read this book aloud or copy it.
- Facts, steps, Desktop control names, and answer numbers here are the reference: when unsure, follow this book.
- Fallback: when Claude cannot do a step, the learner's screen differs, or the learner is lost, look up the exact section and figure yourself and SHOW that place on the learner's screen (redraw it from the caption, `podium.point`, the exact step); cite it in a small line under the visual ("Nguồn: Sách mục 4 · Hình 7"). Never send the learner to the book to find it (nghien-cuu-tai-lieu.md).
- The book's own numbering (mục 1–13, Phụ lục 1–4, Hình 1–11) is what the learner sees.
-->

# Tài liệu đào tạo Claude cơ bản

**Sách tự học cho NCIANS · Làm việc với file và bảng tính trên Claude Code**

| | |
|---|---|
| Đơn vị soạn thảo | Phòng Đào tạo & Phát triển |
| Phiên bản | 1.0 · 16/10/2026 · *bản trình duyệt* |
| Dùng cho | Học viên tự học · người đứng lớp tra cứu |
| Học cùng giáo viên AI | Lớp học NNC: cùng nội dung, có thầy hoặc cô dẫn từng bước ngay trong Claude |
| Thuật ngữ, viết tắt | **Phụ lục 1** cuối tài liệu |

---

## Tóm tắt (đọc trong 2 phút)

- **Tài liệu này là gì:** sách tự học Claude cơ bản, đủ các yêu cầu: thao tác, thực hành, khái niệm cơ bản, quy trình làm việc trên Claude Code (kể cả cách chọn đúng việc cần xây), làm với file và bảng tính; bước cao hơn là xây Skill.
- **Cách học:** đọc từng mục, làm theo ngay trên máy, tự kiểm bằng đáp án ở Phụ lục 2.
- **Học cùng giáo viên:** cùng nội dung này có trong **Lớp học NNC**, nơi một giáo viên AI dẫn bạn làm việc thật trên máy của bạn.
- **Cần chuẩn bị:** máy có Claude Desktop, tài khoản công ty, thư mục `Du-lieu-thuc-hanh` đi kèm tài liệu này.

## Mục tiêu

| Bạn đạt được gì | Đo bằng |
|---|---|
| Tự mở đúng phiên làm việc, chọn đúng chế độ quyền | Làm được, không cần ai hỗ trợ |
| Hiểu 9 khái niệm cơ bản | Đúng ít nhất 4/6 câu đầu của phần tự kiểm tra (mục 13) |
| Giao Claude một việc có file và tự kiểm kết quả | Có 1 file kết quả và 1 lần tự đối chiếu với nguồn |
| Áp dụng vào việc thật | Lần làm thật kế tiếp được người nhận kết quả chấp nhận |
| Biết khi nào dùng ngay, làm Skill, trợ lý hay ứng dụng | Trả lời đúng câu 7 và 8 (mục 13) |
| *Học nhanh:* đóng gói một việc thành Skill | Skill chạy đúng trên một file khác |

---

## 1. Claude Code là gì

- Claude **làm việc thẳng trên file** trong thư mục bạn chọn: đọc, tạo, sửa.
- Claude trò chuyện giống **hỏi ý kiến**. Claude Code giống **nhờ đồng nghiệp làm hộ ngay trên file**.
- Vì làm thật trên file nên luôn đi kèm hai việc: Claude **xin quyền** trước, bạn **kiểm** sau.
- Mở ở đâu: ứng dụng **Claude Desktop → tab Code**. Không cần biết lập trình.

| Nên dùng khi | Không dùng khi |
|---|---|
| Việc có file: bảng tính, văn bản, ảnh phiếu, PDF | Cần quyết định nghiệp vụ thay người |
| Tổng hợp, đối chiếu, tìm lỗi, soạn nháp | File còn dữ liệu nhạy cảm chưa che |
| Việc lặp lại nhiều lần | Gửi thư hay ghi vào hệ thống thật thay bạn |

**Hình 1.** ① Tab **Code** · ② Nút **+ New**: mở phiên làm việc mới.

## 2. Chín khái niệm cần nắm trước khi thực hành

Mọi thứ cần nhìn đều nằm ở **thanh ngay dưới ô nhập** (Hình 2).

**Hình 2.** Thanh dưới ô nhập: ① Nơi chạy (máy này) · ② Thư mục làm việc · ③ Chế độ quyền · ④ Model và effort · ⑤ Hạn mức.

| # | Khái niệm | Hiểu trong một câu | Giống như | Xem trên máy |
|---|---|---|---|---|
| 1 | Claude Code | Claude làm việc thẳng trên file của bạn | Đồng nghiệp ngồi cùng bàn mở file ra làm luôn | Tab Code (Hình 1) |
| 2 | Thư mục làm việc | Claude chỉ thấy file trong thư mục bạn mở cho nó | Bàn kiểm hàng: thùng nào đặt lên bàn mới được mở | Hình 2, mục ② |
| 3 | Phiên | Một cuộc làm việc có trí nhớ riêng; việc mới thì mở phiên mới | Cuộc họp có biên bản riêng | Nút + New (Hình 1) |
| 4 | Model | "Bộ não" Claude đang dùng; bản mạnh nghĩ sâu hơn nhưng tốn hạn mức hơn | Chọn xe: xe lớn chở nhiều nhưng tốn dầu | Bấm tên model (Hình 3) |
| 5 | Effort | Mức Claude nghĩ kỹ; việc đơn giản để mức vừa | Kiểm hàng: lô quen kiểm mẫu, lô mới kiểm từng thùng | Cùng chỗ với model → Effort (Hình 3) |
| 6 | Context | Trí nhớ làm việc của phiên; đầy thì nên mở phiên mới | Mặt bàn: bày càng nhiều càng khó tìm | Gõ `/context` (Hình 4) |
| 7 | Hạn mức 5 giờ | Hạn mức dùng, làm mới mỗi 5 giờ | Suất ăn theo ca | Vòng tròn cuối thanh (Hình 5) |
| 8 | Hạn mức tuần | Hạn mức tuần, làm mới vào giờ cố định của tài khoản | Kho chốt sổ tuần đúng một giờ | Vòng tròn cuối thanh (Hình 5) |
| 9 | Quyền | Claude hỏi trước khi sửa file hay chạy lệnh; đọc rồi mới đồng ý | Phiếu xuất kho cần chữ ký | Hộp xin quyền (Hình 11) |

Khái niệm thứ 10 là **Skill**, học ở mục 10.

**Hình 3.** Bấm tên model (Hình 2 mục ④): ① chọn model · ② mở Effort · ③ chọn mức. Mức **Medium** có nhãn *Recommended* (khuyên dùng). Mức **Max** ghi rõ tốn từ 3,5 lần hạn mức trở lên.

**Hình 4.** Gõ `/context`: thanh cho biết context của phiên đã dùng bao nhiêu phần trăm.

## 3. Hạn mức: những điều chắc chắn

Theo trang hỗ trợ chính thức của Anthropic, tra ngày 15/10/2026 (nguồn ở Phụ lục 3):

- Hạn mức theo phiên **làm mới mỗi 5 giờ**.
- Hạn mức tuần **làm mới vào một giờ cố định**, gắn với tài khoản.
- claude.ai, Claude Code và Claude Desktop **dùng chung** một hạn mức.
- **Không có số tin nhắn cố định.** Tin dài, file lớn, cuộc trò chuyện dài, model mạnh và effort cao đều tốn hạn mức hơn.
- Sắp hết thì có **cảnh báo**: phía trên ô nhập hiện dải *Approaching … usage limit* kèm giờ làm mới. Hết giữa chừng thì Claude Code có thể làm nốt bước đang dở rồi dừng.

**Xem hạn mức ở đâu:**
- **Xem nhanh:** bấm vòng tròn ở cuối thanh dưới ô nhập (Hình 5).
- **Xem đủ:** **Settings > Usage** (Hình 6). Có thể có thêm dòng hạn mức tuần riêng cho một model.

**Hình 5.** ③ Bấm vòng tròn để mở · ① Hạn mức phiên: % đã dùng, còn bao lâu làm mới · ② Hạn mức tuần: % đã dùng, giờ làm mới.

**Hình 6.** Settings: ① mục **Usage** · ② hạn mức phiên · ③ hạn mức tuần.

**Đừng nói những điều tài liệu chính thức không ghi:** "5 giờ tính từ tin nhắn đầu tiên", "mọi người làm mới cùng giờ", "được N tin nhắn".

**Cách tiết kiệm hạn mức:**
- Việc mới thì mở phiên mới.
- Việc đơn giản để effort mức vừa.
- Chỉ đưa vào những file cần dùng.

## 4. Chuẩn bị máy và mở phiên (làm một lần)

| Bước | Làm | Thấy gì là đúng |
|---|---|---|
| 1 | Cài Claude Desktop, đăng nhập tài khoản công ty | Ứng dụng mở được |
| 2 | Chọn tab **Code** (Hình 1). Nếu được hỏi cài Git cho Windows thì cài theo hướng dẫn trên màn hình | Tab Code mở được |
| 3 | Tạo một thư mục riêng cho việc, ví dụ `Tài liệu\Claude\Tong-hop-don-hang` | Thư mục chỉ chứa file được phép dùng |
| 4 | Bấm **+ New**. Ở thanh dưới ô nhập, chọn nơi chạy là **This computer** (Hình 7) | Thanh ghi *This computer* |
| 5 | Bấm mục thư mục → **Open folder…** → chọn thư mục ở bước 3 (Hình 8). Lần đầu mở một thư mục, Desktop có thể hỏi bạn có tin cậy thư mục không: đúng thư mục của bạn thì đồng ý | Thanh ghi đúng tên thư mục |
| 6 | Chọn chế độ quyền **Auto** (mục 5) | Thanh ghi *Auto* |
| 7 | Hỏi thử: *"Trong thư mục này có những file nào?"* | Claude kể đúng tên các file (Hình 9) |

**Hình 7.** Chọn nơi chạy: ① **This computer**, nhóm *Local*, nghĩa là chạy trên chính máy bạn.

**Hình 8.** Chọn thư mục: ① **Open folder…** Danh sách *Recent* là các thư mục mở gần đây.

**Hình 9.** Claude đọc thư mục và kể tên các file. Claude mới xem tên, chưa mở nội dung.

## 5. Chế độ quyền: chọn chế độ nào

**Chế độ quyền** quyết định Claude được tự làm những gì và phải hỏi bạn những gì. Bấm tên chế độ ở thanh dưới ô nhập (Hình 2 mục ③), hoặc phím tắt **Ctrl+Shift+M**. Desktop nhớ chế độ đã chọn cho từng thư mục.

| Chế độ (dòng mô tả trên màn hình) | Claude tự làm | Vẫn hỏi bạn | Dùng khi |
|---|---|---|---|
| **Auto** · *Claude handles permission decisions* | Hầu hết việc. Một bộ kiểm riêng xem trước từng thao tác | Thao tác rủi ro: gửi dữ liệu ra ngoài, xoá hàng loạt, cài từ nguồn lạ… | **Mặc định cho người mới**, với việc thường ngày trên bản sao |
| **Manual** · *Always ask before making changes* | Chỉ đọc file | Mọi lần sửa file, chạy lệnh | Dữ liệu quan trọng; muốn xem từng bước; máy không có Auto |
| **Accept edits** · *Automatically accept all file edits* | Sửa file trong thư mục làm việc | Lệnh khác, file ngoài thư mục | Đã quen, việc sửa nhiều file |
| **Plan** · *Create a plan before making changes* | Chỉ đọc và lên kế hoạch, chưa sửa gì | Duyệt kế hoạch trước khi làm | Việc lớn, nhiều bước: xem kế hoạch trước |
| **Bypass permissions** · *Claude can modify or delete files without asking* | Mọi thứ, không kiểm | Gần như không hỏi | **Không dùng trên máy làm việc** |

**Hình 10.** Menu chế độ quyền. ① **Auto**: khuyên dùng cho người mới.

**Khuyến nghị:**
1. **Người mới: chọn Auto.** Claude làm trôi chảy, các thao tác rủi ro vẫn bị chặn hoặc phải hỏi.
2. **Không thấy Auto** trong danh sách (tài khoản hoặc công ty chưa bật): dùng **Manual**.
3. **Việc nhạy cảm** (file quan trọng, dữ liệu thật): chuyển sang **Manual** để duyệt từng bước.
4. **Không bật Bypass permissions.** Anthropic chỉ khuyên dùng chế độ này trong máy cách ly; nó không có lớp bảo vệ nào.
5. Auto **không thay bạn kiểm kết quả.** Bộ kiểm chỉ chặn thao tác rủi ro, không biết con số đúng hay sai.

Auto bị chặn 3 lần liên tiếp (hoặc 20 lần tổng cộng) thì tự chuyển về hỏi bạn từng bước.

## 6. Quy trình 7 bước làm việc trên Claude Code

| Bước | Làm gì | Dấu hiệu làm đúng | Lỗi hay gặp |
|---|---|---|---|
| 1. Mở đúng chỗ | Tab Code → **+ New** → **This computer** | Đang ở tab Code | Làm ở tab trò chuyện rồi hỏi sao Claude không thấy file |
| 2. Chọn thư mục | Một thư mục riêng, chỉ chứa file được phép dùng | Thanh dưới ô nhập ghi đúng thư mục | Mở cả ổ đĩa hoặc thư mục Tải về |
| 3. Đưa file vào | Chép **bản sao** vào thư mục, bản gốc để nguyên chỗ cũ | Bản gốc không bị đụng tới | Đưa file gốc vào cho Claude sửa |
| 4. Nhìn thanh dưới ô nhập | Chế độ quyền, model, effort, hạn mức (Hình 2) | Nói được còn bao nhiêu hạn mức | Bắt đầu việc dài khi hạn mức sắp hết |
| 5. Giao việc 4 ý | Mục tiêu · Nguồn · Đầu ra · Cách kiểm (mục 7) | Lời giao đủ 4 ý | *"Làm giúp tôi file này"* |
| 6. Theo dõi, duyệt | Đọc Claude đang làm gì. Gặp hộp xin quyền thì đọc rồi mới bấm (Hình 11) | Biết mỗi lần đồng ý là cho Claude làm gì | Bấm đồng ý liên tục mà không đọc |
| 7. Kiểm, lưu, ghi chú | Đối chiếu với nguồn · đặt tên file rõ · ghi "lần sau làm tiếp từ đâu" | Đã tự đối chiếu ít nhất một chỗ | Thấy hợp lý là dùng ngay |

Sang việc khác hẳn, hoặc context đã đầy, thì **mở phiên mới**.

**Hình 11.** Hộp xin quyền. Đọc đủ trước khi bấm: ① Claude xin làm gì · ② ở đâu (đường dẫn file) · ③ nội dung sẽ ghi · ④ **Deny** là từ chối; **Always allow** là cho phép và không hỏi lại với thao tác tương tự. Bấm mũi tên cạnh nút để xem lựa chọn khác.

## 7. Giao việc 4 ý

| Ý | Trả lời câu hỏi | Ví dụ |
|---|---|---|
| **Mục tiêu** | Làm để làm gì? | Tổng hợp đơn hàng tuần theo kênh để họp giao ban |
| **Nguồn** | Dựa vào file nào? | `bang-tinh-mau.xlsx` |
| **Đầu ra** | Kết quả là gì, lưu ở đâu? | File mới `tong-hop-tuan.xlsx`, mỗi kênh một dòng |
| **Cách kiểm** | Làm sao biết kết quả đúng? | Dòng thiếu giá hoặc trùng ghi vào cột "Cần kiểm", không tự điền; chỉ tôi cách tự cộng tay một kênh |

**Lời giao hoàn chỉnh (chép là dùng được):**
> Tổng hợp đơn hàng trong file bang-tinh-mau.xlsx theo kênh để họp giao ban. Kết quả lưu thành file mới tong-hop-tuan.xlsx: mỗi kênh một dòng gồm số dòng, tổng số lượng, tổng thành tiền. Dòng nào thiếu giá hoặc trùng thì ghi vào cột Cần kiểm, không tự điền. Cuối cùng chỉ tôi cách tự cộng tay một kênh để đối chiếu.

| Giao kém | Giao tốt |
|---|---|
| "Làm giúp file này" | Nói rõ làm để làm gì và kết quả lưu ở đâu |
| "Tính tổng đi" | Nói rõ tổng theo cột nào, nhóm theo gì |
| "Xong báo tôi" | Nói rõ cách kiểm và chỗ nào không được tự đoán |

**Claude dùng lời giao của bạn thế nào:** đọc lời giao → đọc nguồn → lên các bước → làm (xin quyền khi cần) → tự soát theo *Cách kiểm* → báo lại. Ý nào bạn bỏ trống, Claude phải tự đoán ý đó.

| Bạn ghi | Claude dùng để | Thiếu thì Claude sẽ |
|---|---|---|
| **Mục tiêu** | Chọn cách làm và mức chi tiết | Làm đúng chữ nhưng có thể sai ý |
| **Nguồn** | Biết phải đọc file nào | Hỏi lại, hoặc tự chọn một file khác |
| **Đầu ra** | Biết tạo gì, lưu ở đâu, đặt tên gì | Chỉ trả lời trong khung trò chuyện, không lưu file |
| **Cách kiểm** | Tự soát trước khi báo, đánh dấu chỗ nghi ngờ | Có thể tự điền chỗ trống mà không nói ra |

**Lời giao dùng ngay cho việc nhỏ văn phòng** (đổi tên file cho đúng việc của bạn):

| Việc | Lời giao |
|---|---|
| Biên bản họp | *"Từ ghi chú trong file ghi-chu-hop.docx, soạn biên bản họp gồm thành phần, nội dung, việc cần làm, người phụ trách, hạn. Lưu thành bien-ban-hop.docx. Chỗ nào chưa rõ người phụ trách hoặc hạn thì ghi Cần hỏi, không tự điền."* |
| Đối chiếu hai danh sách | *"So danh sách trong file A.xlsx với file B.xlsx. Ghi ra file mới những dòng có ở A mà không có ở B và ngược lại. Báo số dòng của từng file để tôi đối chiếu."* |
| Đổi tên ảnh phiếu | *"Đổi tên các ảnh trong thư mục Phieu theo dạng Ngày_SốPhiếu.jpg dựa vào nội dung ảnh. Trước khi đổi, liệt kê tên cũ và tên mới cho tôi duyệt. Ảnh nào đọc không rõ thì để nguyên."* |
| Tóm tắt văn bản | *"Tóm tắt quy định trong file quy-dinh.pdf thành một trang gồm 5 ý chính, mỗi ý ghi số trang nguồn. Lưu thành tom-tat.docx."* |

### Claude có làm được không? Hỏi vặn trước khi tin

Chưa biết Claude làm được việc đó không thì **đừng đoán**. Hỏi lần lượt:

1. *"Nhắc lại việc tôi giao bằng 4 ý. Chưa làm gì."* → biết Claude hiểu đúng chưa.
2. *"Bạn sẽ làm theo những bước nào? Trên máy này cần công cụ hay quyền gì?"*
3. *"Phần nào bạn không làm được hoặc không chắc?"*
4. *"Làm thử trên 3 dòng (hoặc 1 trang) trước, chỉ rõ lấy từ chỗ nào của nguồn."*
5. *"Kết quả này có thể sai ở đâu?"*

**Dấu hiệu Claude đã chạm giới hạn, nên dừng lại:**
- Cần cài thêm phần mềm, kết nối mới, hoặc quyền ngoài thư mục làm việc.
- Trả lời chung chung, không chỉ ra được dòng hay trang nguồn.
- Sửa 2 lần vẫn lặp lại cùng một lỗi.
- Soát 3 dòng thử đã có dòng sai.
- Việc cần thông tin chỉ có trong đầu người khác, hoặc trong hệ thống chưa kết nối với Claude.

Khi đó: ghi lại chỗ vướng, rồi chọn cách khác (mục 11) hoặc hỏi người hướng dẫn. **Claude nói "làm được" chưa phải bằng chứng. Kết quả đã soát mới là bằng chứng.**

## 8. Thực hành với file và bảng tính

**Dữ liệu thực hành:** thư mục `Du-lieu-thuc-hanh`, đi kèm tài liệu này.
- **Toàn bộ là dữ liệu giả.** Mọi tên đều có chữ "— mẫu".
- Chép **bản sao** vào thư mục làm việc trước khi làm.
- Đáp án ở **Phụ lục 2**. Làm xong rồi mới xem.

| Bài | File | Việc giao cho Claude | Bạn tự kiểm |
|---|---|---|---|
| **1. Đọc và tóm tắt bảng** | `bang-tinh-mau.xlsx` | *"Đọc file bang-tinh-mau.xlsx, cho tôi biết có mấy kênh bán hàng, mỗi kênh bao nhiêu dòng và tổng thành tiền mỗi kênh."* | Mở Excel, lọc cột Kênh lấy một kênh, xem tổng cột Thành tiền ở thanh trạng thái |
| **2. File tuần sau đổi khác** | `bang-tinh-mau-tuan-sau.xlsx` | *"Tổng hợp file này theo kênh ra file mới. Trước khi tính, kiểm cột đổi tên, dòng thiếu giá, dòng trùng, đơn vị khác. Dòng có vấn đề ghi vào cột Cần kiểm, không tự điền, không cộng vào tổng."* | Đếm số dòng Cần kiểm; so tổng với đáp án |
| **3. Gộp và so sánh** | 3 file trong thư mục `gop` | *"Gộp 3 file đơn hàng thành một bảng mới, thêm cột Tuần."* rồi *"So tuần 41 với tuần 42: khác nhau ở đâu, do những dòng nào?"* | Số dòng bảng gộp = tổng số dòng 3 file |
| **4. Việc thật của tôi** | File việc gần nhất của bạn, đã che thông tin | Tự viết lời giao 4 ý | Theo cách kiểm bạn đã ghi |

**Bạn sẽ thấy:**
- **Bài 1:** Claude trả lời ngay trong phiên bằng một bảng nhỏ: 3 kênh, số dòng và tổng thành tiền từng kênh.
- **Bài 2:** một file Excel mới trong thư mục. Bảng chi tiết có thêm cột **Cần kiểm**, ghi lý do ở đúng những dòng có vấn đề.
- **Bài 3:** một file gộp mới có thêm cột Tuần; khi so sánh, Claude liệt kê từng thay đổi kèm tên khách và dòng.


**Bài học của bài 2:** file đổi khác thì cách làm cũ có thể ra sai. Claude phải **nói ra chỗ khác, không đoán**. Ai cần xác nhận thì hỏi người giữ nguồn.

**Thử thêm: 9 việc Claude làm được với file**

| Việc | Ví dụ | Hợp với |
|---|---|---|
| Đọc và tóm tắt bảng tính | 40 đơn hàng chia theo kênh thế nào | Bán hàng, sale admin |
| Gộp nhiều file | Gộp đơn hàng 3 tuần thành một bảng | Kho, kế toán |
| So sánh hai bảng | Tuần này khác tuần trước ở đâu | Kế toán, đối chiếu |
| Vẽ biểu đồ | Doanh số theo kênh | Bán hàng |
| Dịch Việt ↔ Lào | Một thông báo nội bộ ngắn | Hành chính, nhân sự |
| Soạn thư nháp | Thư báo lịch giao hàng (không gửi) | Bán hàng, hành chính |
| Đọc ảnh hoặc PDF | Ảnh phiếu nhận hàng thành bảng | Kho, hiện trường |
| Kiểm và đánh dấu lỗi | Tìm dòng thiếu giá, dòng trùng | Kế toán, kho |
| Biến việc thành Skill | Lần sau chỉ cần gọi tên | Ai có việc lặp lại |

## 9. Tự kiểm kết quả

**Nguyên tắc:** kết quả nghe hợp lý chưa chắc đã đúng. Người dùng kết quả là người chịu trách nhiệm kiểm.

| Cách kiểm | Làm thế nào | Mất khoảng |
|---|---|---|
| Soát vài dòng | Chọn 3 dòng bất kỳ, so với file nguồn | 1 phút |
| Cộng tay một nhóm | Lọc một nhóm trong Excel, xem tổng ở thanh trạng thái | 1 phút |
| Hỏi ngược Claude | *"Con số này lấy từ những dòng nào?"* | 1 phút |
| So với số đã biết | So tổng với một con số chắc chắn đúng (báo cáo cũ, phiếu gốc) | 2 phút |

**Cộng tay một nhóm trong Excel:** chọn dòng tiêu đề → **Data > Filter** → ở cột Kênh chỉ chọn một kênh → bôi đen cột Thành tiền → xem số **Sum** ở góc dưới bên phải màn hình Excel.

## 10. Bước cao hơn: đóng gói việc thành Skill

- **Skill là gì:** gói hướng dẫn đã kiểm cho một việc lặp lại. Lần sau chỉ cần gọi tên là Claude làm đúng cách, kể cả bước kiểm.
- **Khi nào nên làm:** việc **lặp lại** (thường từ 3 lần trở lên) và cách làm **đã kiểm** là đúng.
- **Một Skill tốt có đủ:** mục tiêu · nguồn · đầu ra · cách kiểm · những điều không được làm.

| Bước | Làm |
|---|---|
| 1 | Làm đúng việc đó một lần, có tự kiểm |
| 2 | Nhờ Claude: *"Đóng gói cách mình vừa làm thành một Skill tên tong-hop-don-hang, gồm mục tiêu, nguồn, đầu ra, cách kiểm và những điều không được làm."* |
| 3 | Đọc lại Skill, sửa hoặc duyệt ít nhất một điểm |
| 4 | Mở **phiên mới**, gọi Skill trên **một file khác**, rồi kiểm kết quả |

**Mẫu để xem:** Skill `tong-hop-don-hang` trong `Du-lieu-thuc-hanh`.

**Bạn sẽ thấy:** gõ `/` trong ô nhập, danh sách lệnh có tên Skill vừa tạo. Chọn tên đó rồi nói file cần làm.

## 11. Khi muốn Claude làm ra công cụ: chọn đúng việc cần xây

Claude Code làm ra được nhiều thứ: một file kết quả, một Skill, một trợ lý, cả một trang web hay ứng dụng (thường gọi là *vibe code*). **Làm ra được không có nghĩa là nên làm.** Chọn sai thì tốn công, tốn hạn mức, và để lại thứ không ai duy trì.

Quy trình dưới đây chưng cất từ bộ công cụ NNC OSER. Áp dụng mỗi khi bạn định nhờ Claude "làm một cái gì đó" cho việc của mình.

**Quy tắc chung: khai thác trước, khóa mô tả, rồi mới chọn làm gì.**

| Bước | Làm gì | Xong khi |
|---|---|---|
| **1. Khai thác việc thật** | Kể **một lần làm gần nhất**: chuyện gì xảy ra, bạn làm từng bước thế nào, dùng file hay phiếu nào, kết quả đưa cho ai, vướng ở đâu, bao lâu lặp lại một lần. Claude hỏi **từng câu một** | Claude kể lại đúng việc của bạn |
| **2. Khóa bản mô tả** | Claude ghi thành **bản mô tả một trang**: mục tiêu, đầu vào, đầu ra, quy tắc, ai kiểm. Chỗ **mâu thuẫn hoặc còn thiếu** thì hỏi người giữ nguồn, không đoán | Bạn xác nhận *"đúng rồi"*. Từ đây mọi việc làm theo bản này |
| **3. Chọn cách đơn giản nhất đủ dùng** | So các cách ở bảng dưới. Claude nêu cho từng cách: được gì, mất gì, rủi ro, có quay lại được không, ai duy trì. Luôn có lựa chọn **"chưa chắc, thử nhỏ trước"** | Bạn chọn một cách, biết vì sao |
| **4. Làm và thử nhỏ** | Làm bản đầu trên **dữ liệu mẫu hoặc bản sao**. Thử với một ví dụ thật, tự kiểm | Kết quả đúng trên ví dụ thử |
| **5. Dùng thật và cải tiến** | Dùng ở lần làm thật kế tiếp; người nhận kết quả xác nhận. Việc thay đổi thì quay lại sửa bản mô tả ở bước 2 | Người nhận chấp nhận kết quả |

**Chọn cách nào (bước 3):** đi từ trên xuống, dừng ở cách đầu tiên đủ dùng.

| Cách | Hợp khi | Ví dụ |
|---|---|---|
| **Dùng công cụ sẵn có** (Excel, phần mềm đang dùng) | Công cụ hiện tại đã có tính năng, chỉ chưa biết dùng | Lọc và cộng theo kênh bằng Filter của Excel |
| **Nhờ Claude làm ngay** | Việc làm một lần, có file | Tổng hợp đơn hàng tuần này để họp |
| **Skill** | Việc lặp lại, quy tắc rõ, một người làm | Tuần nào cũng tổng hợp đơn hàng theo kênh |
| **Trợ lý AI** | Việc kéo dài nhiều lần, nhiều nguồn, có ngoại lệ phải theo dõi | Hằng ngày soát phiếu nhận hàng, phát hiện thiếu và soạn nhắc người phụ trách |
| **Ứng dụng hoặc web** | Nhiều người cùng nhập, duyệt, xem; mỗi người một quyền; dữ liệu dùng chung | Nhiều phòng cùng theo dõi một quy trình duyệt |

**Ghi nhớ:**
- Câu *"làm cho tôi một trang web"* khi chưa rõ việc thì quay lại **bước 1**.
- Trợ lý, ứng dụng hay web chạm tới **dữ liệu hoặc hệ thống thật**: báo quản lý và bộ phận công nghệ **trước khi làm**.
- Máy đã cài bộ công cụ NNC (có sẵn trong gói Lớp học NNC) thì gõ `/nnc:mission-formation` để Claude dẫn bạn đi bước 1 đến bước 3.

**Câu mở đầu mẫu (chép là dùng được):**
> Tôi muốn cải tiến việc [tên việc]. Hãy hỏi tôi từng câu một về lần gần nhất tôi làm việc này. Sau đó ghi lại thành bản mô tả một trang, chỉ ra chỗ mâu thuẫn hoặc còn thiếu. Chưa làm gì cho đến khi tôi xác nhận bản mô tả. Rồi đề xuất cách đơn giản nhất đủ dùng, nói rõ được và mất của từng cách.

## 12. An toàn dữ liệu và quyền

1. Chỉ dùng file bạn **được phép** dùng, và luôn dùng **bản sao**.
2. **Che trước khi đưa vào:** tên khách hàng, giá vốn, công nợ, lương.
3. **Không** dán mật khẩu hay mã đăng nhập.
4. Claude chỉ **soạn nháp**. Người gửi đi là bạn. Không để Claude ghi vào hệ thống thật.
5. Gặp hộp xin quyền thì đọc đủ ba điều (Hình 11): **làm gì · ở thư mục nào · có sửa hoặc xoá gì không**. Không hiểu thì chưa đồng ý, hỏi người hướng dẫn.
6. Số liệu trong một file chỉ nói về file đó. Không trình bày như số liệu của toàn công ty.

## 13. Tự kiểm tra (đáp án ở Phụ lục 2)

1. Claude thấy được file ở đâu?
   a) Mọi file trên máy · b) Trong thư mục làm việc đã mở · c) Mọi file trên Drive công ty
2. Xong việc tổng hợp đơn hàng, giờ bạn muốn soạn thư mời họp. Nên làm gì?
   a) Hỏi tiếp trong phiên cũ · b) Mở phiên mới · c) Tắt máy rồi mở lại
3. Hạn mức 5 giờ của bạn làm mới lúc nào?
   a) Đúng 5 giờ sau tin nhắn đầu tiên · b) Lúc ghi ở Settings > Usage · c) Nửa đêm mỗi ngày
4. Sáng dùng claude.ai nhiều, chiều mở Claude Code. Hạn mức thế nào?
   a) Mỗi nơi một hạn mức · b) Claude Code không tính · c) Dùng chung một hạn mức
5. Hộp xin quyền báo Claude sẽ xoá một file bạn không nhận ra. Bạn làm gì?
   a) Đồng ý vì Claude biết việc · b) Chưa đồng ý, hỏi người hướng dẫn · c) Tắt máy ngay
6. Khi nào nên đóng gói một việc thành Skill?
   a) Ngay lần đầu làm · b) Khi việc lặp lại và cách làm đã kiểm · c) Khi muốn Claude tự quyết thay mình
7. Tuần nào bạn cũng tổng hợp đơn hàng theo kênh, cách làm đã kiểm đúng. Nên chọn cách nào?
   a) Đóng gói thành Skill · b) Làm một trang web · c) Mỗi tuần tự viết lại lời giao từ đầu
8. Đồng nghiệp nhờ: *"Làm cho tôi một web quản lý đơn"*, nhưng chưa rõ việc. Bước đầu tiên là gì?
   a) Chọn công nghệ để làm web · b) Khai thác lần làm gần nhất của việc đó · c) Tìm một mẫu web có sẵn

---

# PHỤ LỤC

## Phụ lục 1. Thuật ngữ và viết tắt

Cột tiếng Lào để chị điền khi dịch. Từ đánh dấu ★ nên giữ nguyên tiếng Anh, vì trên màn hình hiện đúng chữ đó.

| Tiếng Việt | ພາສາລາວ | Giải thích |
|---|---|---|
| Claude ★ | | Trợ lý AI của hãng Anthropic |
| Claude Desktop ★ | | Ứng dụng Claude cài trên máy tính |
| Claude Code ★ / tab Code ★ | | Cách dùng Claude để làm việc thẳng trên file |
| claude.ai ★ | | Claude trên trình duyệt web |
| + New ★ | | Nút mở phiên làm việc mới |
| This computer ★ (Local ★) | | Chạy trên chính máy mình |
| Open folder… ★ | | Chọn thư mục làm việc |
| Deny ★ · Always allow ★ | | Từ chối · cho phép và không hỏi lại thao tác tương tự |
| Session limit ★ · Weekly ★ | | Hạn mức phiên 5 giờ · hạn mức tuần |
| Recommended ★ · Default ★ | | Khuyên dùng · mặc định |
| Phiên | | Một cuộc làm việc có trí nhớ riêng |
| Thư mục làm việc | | Thư mục mở cho Claude; Claude chỉ thấy file trong đó |
| Bản sao · bản gốc | | Bản chép để làm · file gốc để nguyên |
| Model ★ | | "Bộ não" Claude đang dùng |
| Effort ★ | | Mức Claude nghĩ kỹ |
| Context ★ | | Trí nhớ làm việc của một phiên |
| Hạn mức (usage ★) | | Lượng dùng Claude được phép trong một khoảng thời gian |
| Làm mới (reset ★) | | Lúc hạn mức được cấp lại |
| `/context` ★ | | Lệnh gõ trong Claude Code để xem context đã dùng |
| Chế độ quyền: Auto ★ · Manual ★ · Accept edits ★ · Plan ★ · Bypass permissions ★ | | Tên các chế độ trên màn hình (mục 5) |
| Settings > Usage ★ | | Màn hình cài đặt, mục xem hạn mức |
| Quyền · hộp xin quyền | | Claude hỏi trước khi sửa file hay chạy lệnh |
| Chế độ quyền | | Cài đặt quyết định Claude được tự làm gì, phải hỏi gì |
| Giao việc 4 ý | | Mục tiêu · Nguồn · Đầu ra · Cách kiểm |
| Nguồn · Đầu ra | | File dựa vào · kết quả tạo ra |
| Tự kiểm · đối chiếu | | So kết quả với nguồn trước khi dùng |
| Cần kiểm | | Cột đánh dấu dòng có vấn đề, không tự sửa |
| Dữ liệu mẫu | | Dữ liệu giả để tập, tên có chữ "— mẫu" |
| Dữ liệu nhạy cảm | | Tên khách hàng, giá vốn, công nợ, lương |
| Skill ★ | | Gói hướng dẫn đã kiểm cho một việc lặp lại |
| Git cho Windows ★ | | Phần mềm Claude Code cần trên Windows |
| xlsx | | Đuôi file Excel |
| LAK | | Đồng kíp Lào |
| OTC · HC · SPM | | Kênh nhà thuốc · bệnh viện và phòng khám · tạp hoá và siêu thị |
| Vibe code ★ | | Nhờ AI làm ra công cụ (web, ứng dụng) bằng lời nói thường |
| Khai thác việc thật | | Kể lại lần làm gần nhất để Claude hiểu đúng việc |
| Bản mô tả (đã khóa) | | Bản một trang ghi mục tiêu, đầu vào, đầu ra, quy tắc, người kiểm; đã giải hết mâu thuẫn và được xác nhận |
| Trợ lý AI | | Claude được cấu hình cho một mảng việc, làm nhiều lần, có nguồn và quy tắc riêng |
| NNC OSER ★ | | Bộ công cụ NNC giúp đi từ ý tưởng đến công cụ đúng việc |
| Lớp học NNC | | Chương trình học trong Claude, có giáo viên AI |
| Giáo viên AI (thầy, cô) | | Nhân vật AI dẫn lớp, học viên tự chọn |
| Giáo trình · giáo án | | Nội dung nguồn của môn học · kế hoạch từng buổi |

## Phụ lục 2. Đáp án

**Bài 1. Đọc và tóm tắt bảng** (`bang-tinh-mau.xlsx`):

| Kênh | Số dòng | Tổng thành tiền (LAK) |
|---|---:|---:|
| OTC | 14 | 20.950.000 |
| HC | 13 | 44.200.000 |
| SPM | 13 | 36.720.000 |
| **Cộng** | **40** | **101.870.000** |

**Bài 2. File tuần sau đổi khác** (`bang-tinh-mau-tuan-sau.xlsx`):
- Cột "Đơn giá" đổi tên thành **"Giá bán"**. Claude phải nói ra là đã hiểu như vậy.
- **5 dòng Cần kiểm**, tính theo số dòng Excel:
  - dòng 4, 15, 21 thiếu giá;
  - dòng 12 trùng với dòng 10;
  - dòng 31 tính bằng vỉ trong khi cả bảng tính bằng hộp.
- **36 dòng được tính:**

| Kênh | Tổng thành tiền (LAK) |
|---|---:|
| OTC | 19.850.000 |
| HC | 62.750.000 |
| SPM | 21.840.000 |
| **Cộng** | **104.440.000** |

**Bài 3. Gộp và so sánh:**
- **Gộp:** 60 dòng (20 + 20 + 20); tổng **194.085.000 LAK**.
- **Tuần 42 khác tuần 41 đúng 3 điểm:**
  - có khách mới *Nhà thuốc P — mẫu*;
  - khẩu trang của *Bệnh viện H — mẫu* tăng từ 20 lên 200 hộp;
  - hai đơn kênh SPM biến mất, kênh SPM giảm 67%.
- **Vì sao khác** là câu hỏi cho người phụ trách, Claude không được đoán.

**Mục 13. Tự kiểm tra:** 1b · 2b · 3b · 4c · 5b · 6b · 7a · 8b.

## Phụ lục 3. Nguồn chính thức (tra ngày 15/10/2026)

- How do usage and length limits work: https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work
- What is the Pro plan: https://support.claude.com/en/articles/8325606-what-is-the-pro-plan
- Use Claude Code with your Pro or Max plan: https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan
- Claude Code trên Desktop: https://code.claude.com/docs/en/desktop
- Chế độ quyền (tra ngày 16/10/2026): https://code.claude.com/docs/en/permission-modes

## Phụ lục 4. Đối chiếu yêu cầu đào tạo

| Yêu cầu | Đáp ứng ở |
|---|---|
| **1. Tập trung vào thao tác, thực hành, các khái niệm cơ bản** | **Thao tác:** mục 4, 5, 6 (Hình 1–11) · **Thực hành:** mục 8, 9; đáp án Phụ lục 2 · **Khái niệm cơ bản:** mục 2, 3, 5; Phụ lục 1; tự kiểm tra mục 13 |
| **2. Quy trình cơ bản khi làm trên Code** | Mục 6 (7 bước cho một việc) · mục 7 (giao việc 4 ý, hỏi vặn Claude) · mục 11 (chọn đúng việc cần xây) |
| **3. Thực hiện với file, bảng tính** | Mục 8 (4 bài với bảng tính) · mục 7 (lời giao mẫu cho file văn bản, PDF, ảnh) · mục 10 (đóng gói thành Skill) |
