# Buổi 1 (30 phút) — Nhập môn Claude và làm việc thật với file

**Trạng thái:** thiết kế để duyệt, chưa build. Dựa trên [thiết kế v0.5](LOP-HOC-THIET-KE-V0.5.md): giáo viên thầy/cô, ba động lực, cảm xúc, nhịp 60 giây.
**Người đứng lớp:** một người đào tạo thật cùng giáo viên AI trong Claude; mỗi học viên một máy.

**Quyết định của người thiết kế (15/10/2026):**
- Buổi chuẩn **30 phút**.
- Phải **nhập môn** (Claude là gì, dùng thế nào, các định nghĩa phải nắm) **trước khi vào thực hành**, rồi **cuốn chiếu** các định nghĩa đó suốt các buổi sau.
- Giải nghĩa usage 5 giờ và usage tuần, **hiện trên màn hình**.
- **Phân loại người học**: ai nhanh thì vào nhánh Skill.
- Phần thực hành **ứng dụng ngay vào việc thật**. Yêu cầu "file, bảng tính" chỉ là gợi ý, không cứng nhắc.

## 0. Yêu cầu đào tạo và nơi đáp ứng

| # | Yêu cầu | Phần | Bằng chứng |
|---|---|---|---|
| R1 | Thao tác | 1, 2, 3 | Học viên tự làm các thao tác của quy trình 7 bước |
| R2 | Thực hành | 2, 3 (khoảng 17 trên 30 phút) | Một đầu ra từ việc thật, có tự kiểm |
| R3 | Khái niệm cơ bản | 1 (nhập môn), nhắc lại ở 2–4 và mọi buổi sau | Vé vào lớp (đạt ít nhất 2/3) + 2 câu nhớ lại cuối buổi |
| R4 | Quy trình cơ bản trên Code | 2 (đi trọn 7 bước) | Tự đi lại 7 bước |
| R5 | File, bảng tính (gợi ý) | 2: ưu tiên việc thật có file; không có thì dùng bảng tính mẫu | Một file đầu ra |
| R6 | Dùng được với file dữ liệu; cao hơn là xây Skill | 3 theo nhánh | Nhánh **Vững**: Skill nháp chạy được. Các nhánh khác: xử lý được đầu vào đổi |

## 1. Quy trình 7 bước trên Claude Code (R4)

1. **Mở đúng chỗ:** Desktop → Code → New session → Local.
2. **Chọn thư mục làm việc:** riêng cho việc này, chỉ chứa file được phép dùng.
3. **Đưa file vào:** chép bản sao vào thư mục, giữ bản gốc ở chỗ cũ.
4. **Nhìn bảng điều khiển:** model · effort · chế độ quyền · usage.
5. **Giao việc 4 ý:** mục tiêu · nguồn · đầu ra · cách kiểm.
6. **Theo dõi và duyệt:** đọc Claude đang làm gì; khi được hỏi quyền thì đọc rồi mới đồng ý.
7. **Kiểm, lưu, ghi chú:** đối chiếu với nguồn; đặt tên file rõ; ghi "lần sau tiếp từ đâu"; việc mới hoặc context đầy thì mở phiên mới.

## 2. Chín định nghĩa phải nắm trước khi vào thực hành (R3)

Mỗi định nghĩa là một **thẻ** trên bục giảng: một câu định nghĩa, một ví dụ đời thường, **số liệu thật trên máy** nếu có, và hai nút *Hiểu rồi · Giải thích thêm*.

| # | Định nghĩa | Một câu | Hiện trên màn hình |
|---|---|---|---|
| 1 | Claude Code | Claude làm việc trực tiếp với file trong thư mục của bạn, không chỉ trò chuyện | Sơ đồ: bạn giao việc → Claude đọc, ghi file → bạn kiểm |
| 2 | Thư mục làm việc | Bàn làm việc của Claude: chỉ những gì bạn mở cho nó | Đường dẫn thư mục thật của buổi học |
| 3 | Phiên | Một cuộc làm việc; việc mới thì phiên mới | Vị trí nút New session (sơ đồ) |
| 4 | Model | Bộ não đang dùng; bản mạnh nghĩ sâu hơn nhưng tốn hạn mức hơn | **Tên model thật đang dùng** |
| 5 | Effort | Mức nghĩ kỹ; việc đơn giản để vừa | **Effort thật** |
| 6 | Context | Trí nhớ của phiên; đầy thì Claude tóm tắt hoặc nên mở phiên mới | **% context đã dùng** |
| 7 | Usage 5 giờ | Hạn mức theo phiên 5 giờ, reset mỗi 5 giờ; claude.ai, Code và Desktop dùng chung | **Dòng thời gian 5 giờ: đã dùng X%, reset lúc HH:MM** (mục 2.1) |
| 8 | Usage tuần | Hạn mức tuần, reset vào **giờ cố định mỗi tuần** của tài khoản | **Ngày và giờ reset tuần thật**, % đã dùng |
| 9 | Quyền | Claude hỏi trước khi sửa file hoặc chạy lệnh; bạn đọc rồi mới đồng ý | Hình hộp xin quyền (sơ đồ) + chế độ quyền đang bật |

Thẻ thứ 10, **Skill**, chỉ mở cho nhánh *Vững* ở phần 3, và là định nghĩa đầu tiên của Buổi 2.

### 2.1 Giải nghĩa usage trên màn hình

Bục giảng vẽ **dòng thời gian 5 giờ** từ số liệu thật của máy (phần trăm đã dùng, giờ reset):
- vạch "bây giờ";
- vạch "reset lúc 14:20";
- thanh phần trăm đã dùng;
- dòng chữ *"Còn 2 giờ 13 phút đến lượt reset"*.

Bên dưới là **lịch tuần** đánh dấu ngày và giờ reset tuần thật, cùng phần trăm đã dùng trong tuần.

Giáo viên giảng theo tài liệu chính thức (tra lúc dạy và ghi ngày tra):
- reset mỗi 5 giờ;
- tuần reset vào giờ cố định gắn với tài khoản;
- dùng chung giữa claude.ai, Code và Desktop;
- không phải một số tin nhắn cố định;
- gần chạm thì có cảnh báo;
- xem ở `/status` hoặc Settings > Usage.

Giáo viên **không khẳng định điểm bắt đầu của 5 giờ** khi tài liệu cho gói của học viên không ghi. Giáo viên chỉ vào **giờ reset thật** trên máy.

Nguồn: [How do usage limits work](https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work) · [Pro plan](https://support.claude.com/en/articles/8325606-what-is-the-pro-plan) · [Claude Code với Pro/Max](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan).

### 2.2 Vé vào lớp

Sau 9 thẻ, giáo viên đố 3 câu dạng trắc nghiệm, mỗi câu có hạn 60 giây. Ví dụ:
- *"Claude chỉ thấy file ở đâu?"*
- *"Reset tuần của chị là lúc nào?"*
- *"Claude hỏi quyền thì chị làm gì?"*

Đúng ít nhất 2/3 thì vào thực hành. Sai câu nào thì giáo viên giảng lại đúng thẻ đó trong 30 giây rồi cho vào. **Không giữ học viên lại ngoài cửa quá 1 phút.**

## 3. Giáo án 30 phút

| Phút | Phần | Động lực | Giáo viên | Học viên (thao tác) | Cảm xúc |
|---|---|---|---|---|---|
| 0–2 | **0. Vào lớp** | Kết nối | Chào; học viên chọn thầy hoặc cô, cách xưng hô, năng lượng hôm nay; nói mục tiêu: *"ra về đã giao Claude làm một việc thật với file và tự kiểm được"* | Có mặt, chọn | Hỉ, ái |
| 2–9 | **1. Nhập môn** | D2 | 9 thẻ định nghĩa với số liệu thật; dòng thời gian usage; vé vào lớp | *Hiểu rồi / Giải thích thêm*; trả lời 3 câu | Tò mò, lạc |
| 9–20 | **2. Việc thật của tôi** | D1 + D3 | Hỏi việc gần nhất có file hoặc bảng tính (không có thì dùng bảng tính mẫu); dẫn đi 7 bước; **gọi tên định nghĩa ngay khi nó xuất hiện** (*"đây chính là thẻ Quyền"*); làm mẫu một phần, mời học viên giao phần còn lại bằng form 4 ý | Tạo thư mục, chép file, giao việc, duyệt quyền, mở đầu ra, **tự kiểm** | Hỉ; nộ nếu đụng dữ liệu nhạy cảm; ố nếu tin kết quả không kiểm |
| ~18 | **Điểm phân nhánh** | — | Giáo viên xếp nhánh theo dấu hiệu quan sát (mục 4) | — | — |
| 20–27 | **3. Theo nhánh** | D3 / D1 | **Vững:** đóng gói việc vừa làm thành Skill nháp và chạy thử trên một file khác. **Đang lên:** đầu vào đổi (một cột đổi tên, dòng thiếu), tự phát hiện và giao lại. **Cần đỡ:** giáo viên làm mẫu lại từ đầu với file mẫu, học viên làm theo; bục giảng báo để người đứng lớp đến hỗ trợ | Theo nhánh | Ai (đồng cảm), rồi tự hào |
| 27–30 | **4. Tổng kết** | Kết nối | 2 câu nhớ lại định nghĩa (cuốn chiếu); khen cụ thể; điều thầy/cô học được từ học viên; bài về nhà; chào | Chọn mức tự tin, chọn ngày làm bài về nhà | Tự hào, ái |

**Bài về nhà:** lần phát sinh thật kế tiếp của một việc có file, đi trọn 7 bước. Nhánh *Vững*: dùng Skill vừa tạo cho lần đó.

## 4. Phân loại người học (không dán nhãn lên màn hình)

Giáo viên xếp nhánh ở khoảng phút 18 bằng **dấu hiệu quan sát được**, không bằng cảm nhận:

| Nhánh (tên nội bộ) | Dấu hiệu | Học viên thấy |
|---|---|---|
| **Vững** | Vé vào lớp 3/3, đã có đầu ra và đã tự kiểm trước phút 18, không quá một lần hết hạn trả lời | *"Chị làm nhanh quá — thử một thử thách thêm nhé?"* (được quyền từ chối) |
| **Đang lên** | Có đầu ra nhưng chưa tự kiểm, hoặc vé vào lớp 2/3 | *"Mình thử một tình huống hay gặp: file tuần sau đổi khác."* |
| **Cần đỡ** | Chưa có đầu ra, hoặc từ 2 lần hết hạn trả lời trở lên | *"Mình làm lại cùng nhau từng bước nhé."* |

- Tên nhánh **không hiện** cho học viên. Học viên chỉ thấy lời mời phù hợp.
- Học viên tự xin đổi nhánh bất cứ lúc nào.
- Nhánh chỉ dùng để dạy cho vừa sức, không dùng để chấm người.

## 5. Cuốn chiếu định nghĩa xuyên các buổi

Mục tiêu: các định nghĩa **ăn sâu** nhờ được nhắc lại đúng lúc và cách quãng, không phải nhờ học thuộc một lần.

1. **Học:** thẻ định nghĩa ở phần nhập môn.
2. **Dùng:** khi định nghĩa xuất hiện trong việc thật, giáo viên gọi tên nó ngay (*"Chị vừa duyệt quyền — đúng thẻ số 9"*).
3. **Nhớ lại cuối buổi:** 2 câu, chọn từ những thẻ học viên còn yếu.
4. **Nhớ lại đầu buổi sau:** 2 câu, chọn từ những thẻ lâu chưa gặp hoặc đã sai. Sau đó dạy thêm 1–2 định nghĩa mới (Buổi 2: Skill).
5. **Thuộc:** một định nghĩa được coi là đã thuộc khi trả lời đúng 3 lần, trải qua ít nhất 2 buổi.

Giáo viên giữ một **sổ định nghĩa** cho từng học viên trong thư mục lớp, ở file dành cho người đào tạo: đã học, đã dùng, số lần nhớ lại đúng, ngày gặp gần nhất. Không chứa nội dung riêng.

Khi hãng đổi model hoặc thay đổi cách tính usage, định nghĩa liên quan được đánh dấu **"có tin mới"**, và giáo viên giảng lại thẻ đó ở đầu buổi sau.

## 6. Dữ liệu mẫu (dự phòng khi học viên không có file phù hợp)

| Tệp | Nội dung |
|---|---|
| `bang-tinh-mau.xlsx` | Khoảng 40 dòng đơn hàng **giả** gần việc NNC: kênh OTC/HC/SPM, khách "Nhà thuốc A — mẫu", hàng "Vitamin C 500mg — mẫu", số lượng, đơn giá |
| `bang-tinh-mau-tuan-sau.xlsx` | Cùng cấu trúc, cài sẵn: một cột đổi tên, 3 dòng thiếu giá, một mã trùng (dùng cho nhánh *Đang lên*) |
| `dap-an-mau.xlsx` | Tổng hợp đúng, để giáo viên và người đứng lớp đối chiếu |
| `skill-mau/SKILL.md` | Skill mẫu đã kiểm, dùng khi nhánh *Vững* hết giờ |

## 7. Hướng dẫn người đứng lớp

**Trước buổi:**
- Mỗi máy đã có Claude Desktop, đăng nhập đúng tài khoản, mở được tab Code.
- Thư mục lớp học đã cài sẵn; bục giảng hiện *"Lớp đang chờ giáo viên"*.
- Dặn học viên chuẩn bị **một việc gần đây có file** (đã che thông tin khách hàng và nhân sự). Không có cũng được.

**Trong buổi:**
- **Phút 0–2:** chị mở lớp bằng lời của mình.
- **Phút 2–20:** chị đi quanh lớp. Máy nào bục giảng báo *"cần hỗ trợ"* hoặc *"tạm nghỉ"* thì chị đến. **Không làm thay học viên.**
- **Phút 27–30:** chị chốt bằng 1–2 câu chuyện đẹp trong lớp và nhắc bài về nhà.

**Sau buổi:** ghi mức *có hướng dẫn / tự làm với đầu vào mới / đã dùng lại trong việc thật*. Mức cuối chỉ ghi khi bài về nhà được người nhận nghiệp vụ chấp nhận.

**Sự cố:**

| Sự cố | Xử lý |
|---|---|
| Không thấy bục giảng | Mở phiên mới trong thư mục lớp học |
| Hết usage 5 giờ | Làm cặp với bạn bên cạnh và xem giờ reset. Chính tình huống này cũng là bài học thẻ 7 |
| Đụng dữ liệu nhạy cảm | Dừng lại, chuyển sang file mẫu |

## 8. Cần build để chạy Buổi 1 (so với v0.4)

| Cần | Hiện có | Phải build |
|---|---|---|
| Thẻ định nghĩa trên bục giảng, có số liệu thật | Dòng "Claude của tôi" | 9 thẻ, nút *Hiểu rồi / Giải thích thêm*, dòng thời gian usage 5 giờ và lịch tuần (Svg) |
| Vé vào lớp, nhớ lại cuối và đầu buổi, sổ định nghĩa | Chưa | Có |
| Giáo án 30 phút theo giờ, tự chuyển phần, 60 giây, điểm danh, xin phép, xin nghỉ | Chưa | Có |
| Phân nhánh Vững / Đang lên / Cần đỡ, báo "cần hỗ trợ" cho người đứng lớp | Chưa | Có |
| Hai giáo viên thầy/cô, bảng cảm xúc | Nhân vật cũ | Có |
| Dữ liệu mẫu, đáp án, Skill mẫu | Chưa | Có |
