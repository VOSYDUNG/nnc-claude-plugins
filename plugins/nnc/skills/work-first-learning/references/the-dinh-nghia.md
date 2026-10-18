# Thẻ định nghĩa — 9 thẻ phải nắm trước thực hành + thẻ 10 Skill

Dùng ở phần **Làm quen nhanh** của vòng việc đầu tiên (nhóm A: 1–3 · B: 4–6 · C: 7–9; **kiểm nhanh trước**, nhóm nào học viên đã biết thì chỉ nói một dòng), khi **gọi tên** định nghĩa trong việc thật, và trong các câu **nhớ lại** khi chốt vòng việc và khi học viên quay lại. Thẻ 10 chỉ mở cho học viên nhận thử thách ở phần 3, và là thẻ mới đầu tiên của lần quay lại sau đó. Nguồn chuẩn cho học viên tự đọc: sách tự học mục 2–5 ([sach-tu-hoc.md](sach-tu-hoc.md)).

Mỗi thẻ có: `id` (dùng trong sổ định nghĩa) · **Một câu** · **Ví dụ đời thường** · **Số liệu thật trên máy** · **Giải thích thêm** (cách nói thứ hai, khi học viên bấm *Giải thích thêm*) · **Gọi tên khi dùng** · **2 câu nhớ lại** (đáp án đúng ✓ và vì sao).

Quy tắc chung:
- Trình bày mỗi thẻ ≤ 3 dòng. Số liệu chỉ nói khi **đã thấy thật** trong buổi (thẻ usage trên bục giảng hoặc vòng tròn hạn mức cuối thanh dưới ô nhập do học viên đọc, Settings > Usage, kết quả `/status` ở bản dòng lệnh, tên model giáo viên đang chạy). Chưa thấy thì nhờ học viên đọc trên bục — đọc được chính là kỹ năng D2. **Không đoán, không nói theo trí nhớ.**
- Câu nhớ lại dùng **nút trên bục** (`choices`) hoặc **widget trả lời** (v0.8, SKILL §12); hộp câu hỏi gốc chỉ khi không có bục. **Phương án đầu tiên luôn là "Chưa chắc — cô nhắc lại"** (mặc định khi hết 60 giây). Chọn phương án này hoặc hết giờ **không** tính là nhớ đúng; giáo viên nhắc lại thẻ trong ≤ 30 giây.
- Các phương án sai là hiểu lầm thường gặp, không gài bẫy chữ.

---

## Thẻ 1 · Claude Code — `claude-code`
- **Một câu:** Claude làm việc trực tiếp với file trong thư mục của mình — đọc, tạo, sửa file — không chỉ trò chuyện.
- **Ví dụ đời thường:** như nhờ một đồng nghiệp ngồi cùng bàn mở file của mình ra làm luôn, thay vì chỉ góp ý qua điện thoại.
- **Số liệu thật:** sơ đồ *mình giao việc → Claude đọc, ghi file → mình kiểm*.
- **Giải thích thêm:** Claude trò chuyện giống hỏi ý kiến; Claude Code giống nhờ làm hộ ngay trên file. Vì làm thật trên file nên luôn có hai bước đi kèm: Claude **xin quyền** trước, và mình **kiểm** sau.
- **Gọi tên khi dùng:** lần đầu Claude đọc file thực hành — *"Đây là thẻ 1: Claude đang làm thẳng trên file."*
- **Nhớ lại:**
  1. *Claude Code khác Claude trò chuyện ở điểm chính nào?* — Chưa chắc · Chỉ trả lời hay hơn · **Làm việc thẳng với file trong thư mục ✓** · Tự gửi email cho khách. *Vì:* Claude Code đọc và ghi file thật, nên cần quyền và cần kiểm.
  2. *Claude Code tổng hợp xong một bảng. Ai kiểm trước khi dùng?* — Chưa chắc · Claude tự kiểm là đủ · **Mình kiểm với nguồn ✓** · Nhìn hợp lý là dùng được. *Vì:* nghe hợp lý chưa phải đúng; người dùng kết quả chịu trách nhiệm kiểm.

## Thẻ 2 · Thư mục làm việc — `thu-muc`
- **Một câu:** Bàn làm việc của Claude: Claude chỉ thấy và làm với những gì nằm trong thư mục mình mở cho nó.
- **Ví dụ đời thường:** như bàn kiểm hàng: chỉ thùng nào đặt lên bàn mới được mở; hàng trong kho không ai đụng.
- **Số liệu thật:** đường dẫn thật của thư mục lớp học (giáo viên biết thư mục đang làm việc).
- **Giải thích thêm:** vì vậy mỗi việc nên có một thư mục riêng, chỉ chứa file được phép dùng, và luôn là **bản sao**. File gốc để nguyên chỗ cũ.
- **Gọi tên khi dùng:** khi tạo `Thuc-hanh/` và khi chép file vào.
- **Nhớ lại:**
  1. *Claude chỉ thấy file ở đâu?* — Chưa chắc · Mọi file trên máy · **Trong thư mục làm việc đã mở ✓** · Mọi file trên Drive công ty. *Vì:* thư mục làm việc là giới hạn Claude được mở ra.
  2. *Chị cần Claude làm với một file ở thư mục khác. Cách an toàn?* — Chưa chắc · **Chép một bản sao vào thư mục làm việc ✓** · Di chuyển luôn file gốc vào · Mở cho Claude cả ổ đĩa. *Vì:* bản sao giữ file gốc an toàn và giữ Claude trong đúng phạm vi.

## Thẻ 3 · Phiên — `phien`
- **Một câu:** Một cuộc làm việc với Claude, có trí nhớ riêng; việc mới thì mở phiên mới.
- **Ví dụ đời thường:** như một cuộc họp có biên bản riêng: họp việc khác thì mở biên bản mới, không ghi chồng lên.
- **Số liệu thật:** vị trí *tab Code → + New → This computer* (học viên đang ngồi trong một phiên như vậy; sách tự học Hình 1, Hình 7).
- **Giải thích thêm:** phiên dài, lẫn nhiều việc thì Claude dễ nhầm và mỗi lượt tốn hạn mức hơn. Chuyển sang việc khác hẳn, hoặc context đầy: ghi chú "lần sau tiếp từ đâu" rồi mở phiên mới.
- **Gọi tên khi dùng:** bước 1 của quy trình 7 bước; bước 7 (khi nào mở phiên mới).
- **Nhớ lại:**
  1. *Xong việc tổng hợp đơn hàng, giờ chị muốn soạn thư mời họp. Nên làm gì?* — Chưa chắc · **Mở phiên mới ✓** · Hỏi tiếp trong phiên cũ cho tiện · Tắt máy rồi mở lại. *Vì:* việc mới thì trí nhớ mới, gọn và ít nhầm.
  2. *Phiên giống cái gì nhất?* — Chưa chắc · **Một cuộc họp có biên bản riêng ✓** · Một tài khoản mới · Một file Excel. *Vì:* mỗi phiên có trí nhớ riêng cho một việc.

## Thẻ 4 · Model — `model`
- **Một câu:** Bộ não Claude đang dùng; bản mạnh hơn nghĩ sâu hơn nhưng thường tốn hạn mức hơn.
- **Ví dụ đời thường:** như chọn xe cho chuyến hàng: xe tải lớn chở được nhiều nhưng tốn dầu; giao vài thùng thì xe nhỏ là đủ.
- **Số liệu thật:** **tên model thật** đang chạy (giáo viên biết model của chính mình; bục giảng cũng hiện).
- **Giải thích thêm:** model là một trong các yếu tố làm thay đổi mức dùng hạn mức (theo trang hỗ trợ chính thức). Model nào hãng đang khuyên dùng cho việc nào thì **tra tài liệu chính thức lúc dạy và nói ngày tra**, không nói theo trí nhớ.
- **Gọi tên khi dùng:** bước 4 (nhìn bảng điều khiển).
- **Nhớ lại:**
  1. *Model mạnh hơn thường thế nào?* — Chưa chắc · Luôn nhanh hơn và tốn ít hơn · **Nghĩ sâu hơn nhưng tốn hạn mức hơn ✓** · Không khác gì. *Vì:* chọn model là đổi giữa độ sâu và hạn mức.
  2. *Chị đang dùng model nào?* — Chưa chắc · **Tên đang hiện trên bục giảng: ‹tên thật› ✓** · Claude không dùng model nào · Không xem được ở đâu. *Vì:* tên model luôn đọc được trên máy. (Giáo viên điền tên thật đã thấy; **không bịa tên model khác** làm phương án nhiễu.)

## Thẻ 5 · Effort — `effort`
- **Một câu:** Mức Claude nghĩ kỹ trước khi làm; việc đơn giản để mức vừa, việc khó mới tăng.
- **Ví dụ đời thường:** như kiểm hàng nhập: lô quen thì kiểm mẫu, lô mới hoặc giá trị cao thì kiểm từng thùng.
- **Số liệu thật:** **mức effort thật** trên bảng điều khiển / bục giảng.
- **Giải thích thêm:** nghĩ kỹ hơn thì thường chậm hơn và dùng hạn mức nhiều hơn — mức effort là một yếu tố ảnh hưởng mức dùng theo trang hỗ trợ chính thức. Tên các mức tuỳ phiên bản Claude Code: đọc trên máy, không đọc thuộc.
- **Gọi tên khi dùng:** bước 4; khi học viên tự đổi effort một lần.
- **Nhớ lại:**
  1. *Tổng hợp một bảng khoảng 40 dòng nên dùng effort nào?* — Chưa chắc · Luôn mức cao nhất cho chắc · **Mức vừa là đủ ✓** · Effort không liên quan. *Vì:* việc rõ ràng, nhỏ thì nghĩ vừa đủ, để dành hạn mức.
  2. *Tăng effort thì đổi gì?* — Chưa chắc · **Nghĩ kỹ hơn, thường chậm hơn và dùng hạn mức nhiều hơn ✓** · File lưu nhanh hơn · Không đổi gì. *Vì:* effort là độ kỹ, có giá của nó.

## Thẻ 6 · Context — `context`
- **Một câu:** Trí nhớ làm việc của phiên — tin nhắn, file đã đọc; đầy thì Claude phải tóm tắt bớt, nên mở phiên mới.
- **Ví dụ đời thường:** như mặt bàn: bày càng nhiều giấy tờ càng khó tìm; đầy bàn thì phải dọn bớt.
- **Số liệu thật:** **% context đã dùng** (học viên đọc trên bục giảng).
- **Giải thích thêm:** hội thoại càng dài thì mỗi lượt càng tốn hạn mức; trang hỗ trợ chính thức khuyên mở cuộc mới khi gần chạm hạn mức trong một cuộc dài. Vì vậy: việc mới → phiên mới, kèm ghi chú chỗ dừng.
- **Gọi tên khi dùng:** khi Claude đọc file lớn; bước 7.
- **Nhớ lại:**
  1. *Context gần đầy thì nên làm gì?* — Chưa chắc · Gửi thêm thật nhiều file · **Ghi chú chỗ dừng rồi mở phiên mới ✓** · Không sao, cứ tiếp. *Vì:* bàn đầy thì dọn, không chất thêm.
  2. *Context giống cái gì nhất?* — Chưa chắc · Ổ cứng của máy · Hạn mức tuần · **Mặt bàn làm việc của phiên ✓**. *Vì:* context là trí nhớ của một phiên, không phải nơi lưu file.

## Thẻ 7 · Usage 5 giờ — `usage-5h`
- **Một câu:** Hạn mức theo phiên, **reset mỗi 5 giờ**; claude.ai, Claude Code và Desktop dùng **chung** một hạn mức.
- **Ví dụ đời thường:** như suất ăn theo ca: dùng ở căng-tin nào cũng trừ vào cùng một suất; sang ca mới thì có suất mới.
- **Số liệu thật:** dòng thời gian 5 giờ trên bục giảng — vạch "bây giờ", vạch "reset lúc HH:MM", thanh % đã dùng, "còn … đến lượt reset". Giáo viên **chỉ vào giờ reset thật**, không tự tính.
- **Giải thích thêm:** không phải một số tin nhắn cố định — độ dài tin nhắn và file, độ dài cuộc trò chuyện, model, tính năng đều làm thay đổi mức dùng. Gần chạm sẽ có cảnh báo; chạm giới hạn khi Claude Code đang làm thì nó có thể làm nốt bước đang dở rồi dừng. Xem nhanh: vòng tròn hạn mức cuối thanh dưới ô nhập (Desktop); xem đủ: **Settings > Usage**; ở bản dòng lệnh: `/status`.
- **Không được nói:** "5 giờ tính từ tin nhắn đầu tiên" hay bất kỳ điểm bắt đầu nào — tài liệu cho gói cá nhân không ghi điều đó.
- **Gọi tên khi dùng:** bước 4; khi thấy cảnh báo gần chạm; khi hết usage (làm cặp với bạn bên cạnh và xem giờ reset — chính là bài học thẻ này).
- **Nhớ lại:**
  1. *Usage 5 giờ của mình reset lúc nào?* — Chưa chắc · Đúng 5 giờ sau tin nhắn đầu tiên · **Lúc ghi trên thẻ usage của bục giảng (hoặc Settings > Usage) ✓** · Nửa đêm mỗi ngày. *Vì:* tài liệu nói reset mỗi 5 giờ; giờ cụ thể thì đọc trên máy, không tự suy.
  2. *Sáng chị dùng claude.ai nhiều, chiều mở Claude Code. Hạn mức thế nào?* — Chưa chắc · Mỗi nơi một hạn mức riêng · Claude Code không tính · **Dùng chung một hạn mức ✓**. *Vì:* mọi nơi dùng Claude đều tính vào cùng giới hạn.

## Thẻ 8 · Usage tuần — `usage-tuan`
- **Một câu:** Hạn mức theo tuần, **reset vào một giờ cố định mỗi tuần gắn với tài khoản**, không phụ thuộc lúc mình bắt đầu dùng.
- **Ví dụ đời thường:** như kho chốt sổ tuần vào một giờ cố định: tuần đó nhập hàng lúc nào thì sổ vẫn chốt đúng giờ ấy.
- **Số liệu thật:** **ngày và giờ reset tuần thật** trên lịch tuần của bục giảng, % đã dùng trong tuần.
- **Giải thích thêm:** hết hạn mức tuần thì phải chờ tới giờ reset tuần, dù hạn mức 5 giờ đã reset (trừ khi tài khoản được bật dùng thêm ngoài gói — việc của người quản trị, không phải học viên). Trước một việc dài, nhìn **cả hai** con số. Giờ reset kế tiếp xem ở Settings > Usage.
- **Gọi tên khi dùng:** bước 4; khi hẹn việc kế tiếp; khi lớp báo hạn mức chạm ngưỡng.
- **Nhớ lại:**
  1. *Reset tuần của mình là lúc nào?* — Chưa chắc · 7 ngày sau lần mình dùng đầu tiên · Sáng thứ Hai, giống mọi người · **Giờ cố định của tài khoản — xem trên bục giảng / Settings > Usage ✓**. *Vì:* mỗi tài khoản được gán một giờ reset tuần cố định.
  2. *Hạn mức 5 giờ vừa reset nhưng hạn mức tuần đã hết. Làm tiếp được không?* — Chưa chắc · Được, vì 5 giờ đã reset · **Phải chờ tới giờ reset tuần ✓** · Chuyển sang claude.ai là được. *Vì:* hai giới hạn cùng áp dụng, và claude.ai dùng chung hạn mức.

## Thẻ 9 · Quyền — `quyen`
- **Một câu:** Claude hỏi trước khi sửa file hoặc chạy lệnh; mình **đọc rồi mới đồng ý**.
- **Ví dụ đời thường:** như phiếu xuất kho cần chữ ký: thủ kho đọc phiếu rồi mới ký, không ký phiếu trắng.
- **Số liệu thật:** hình hộp xin quyền (sơ đồ) + **chế độ quyền đang bật** trên bảng điều khiển.
- **Giải thích thêm:** hộp xin quyền nói Claude sắp làm gì. Đọc ba điều: làm gì, ở thư mục nào, có sửa hay xoá gì không. Không hiểu thì chưa đồng ý — hỏi cô. Chế độ quyền quyết định Claude được tự làm gì, phải hỏi gì: lớp học khuyên người mới chọn **Auto** (bộ kiểm riêng xem trước từng thao tác, thao tác rủi ro vẫn bị chặn hoặc phải hỏi); không có Auto thì **Manual** (hỏi mọi lần sửa); **không bao giờ Bypass permissions**. Desktop nhớ chế độ cho từng thư mục (sách tự học mục 5). Giáo viên không bao giờ bấm thay.
- **Gọi tên khi dùng:** mỗi lần hộp xin quyền hiện ra trong việc thật (*"chị vừa duyệt quyền — đúng thẻ số 9"*).
- **Nhớ lại:**
  1. *Claude hỏi quyền thì mình làm gì?* — Chưa chắc · Bấm đồng ý ngay cho nhanh · **Đọc nó sắp làm gì rồi mới đồng ý ✓** · Luôn từ chối cho an toàn. *Vì:* quyền là chữ ký của mình; ký khi đã đọc.
  2. *Hộp quyền ghi Claude sẽ xoá một file chị không nhận ra. Chị làm gì?* — Chưa chắc · **Chưa đồng ý, hỏi cô trước ✓** · Đồng ý vì Claude biết việc · Tắt máy ngay. *Vì:* không rõ thì dừng và hỏi — không đoán.

## Thẻ 10 · Skill — `skill` (chỉ mở ở phần thử thách; thẻ mới của lần quay lại đầu tiên)
- **Một câu:** Một gói hướng dẫn đã kiểm cho một việc lặp lại, để lần sau Claude làm đúng cách mà không phải dặn lại từ đầu.
- **Ví dụ đời thường:** như quy trình chuẩn dán cạnh máy: ai làm cũng theo cùng các bước và cùng cách kiểm.
- **Số liệu thật:** Skill nháp vừa tạo trong thư mục lớp (hoặc Skill mẫu của lớp).
- **Giải thích thêm:** chỉ đóng gói khi việc **lặp lại** (thường từ 3 lần) và cách làm **đã kiểm**. Một Skill tốt chứa đủ 4 ý: mục tiêu, nguồn, đầu ra, cách kiểm. Skill mới thường dùng được ở phiên mới.
- **Gọi tên khi dùng:** khi đóng gói ở phần 3; khi việc kế tiếp dùng Skill.
- **Nhớ lại:**
  1. *Khi nào nên đóng gói một việc thành Skill?* — Chưa chắc · Ngay lần đầu làm · **Khi việc lặp lại và cách làm đã kiểm ✓** · Khi muốn Claude tự quyết thay mình. *Vì:* Skill đóng gói cách làm đã đúng, không đóng gói thử nghiệm.
  2. *Skill giống cái gì nhất?* — Chưa chắc · Một model mạnh hơn · **Quy trình chuẩn dán cạnh máy ✓** · Một thư mục làm việc. *Vì:* Skill là cách làm được ghi lại để làm lại giống nhau.

---

## Sự thật về usage — chỉ theo trang hỗ trợ chính thức

Đã tra ngày **2026-10-15**. Khi dạy, nói "theo trang hỗ trợ của Anthropic, tra ngày …". Trang đổi thì tra lại và cập nhật ngày; điều gì trang không nói thì **không nói**.

| Điều giáo viên được nói | Nguồn |
|---|---|
| Hạn mức theo phiên **reset mỗi 5 giờ** ("resets every five hours") | [How do usage and length limits work](https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work) · [What is the Pro plan](https://support.claude.com/en/articles/8325606-what-is-the-pro-plan) |
| Hạn mức tuần **reset vào giờ cố định mỗi tuần được gán cho tài khoản** | [What is the Pro plan](https://support.claude.com/en/articles/8325606-what-is-the-pro-plan) |
| claude.ai, Claude Code và Desktop **dùng chung** một giới hạn | [How do usage and length limits work](https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work) · [Use Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan) |
| **Không có số tin nhắn cố định**; phụ thuộc độ dài tin nhắn và file đính kèm, độ dài cuộc trò chuyện, model, tính năng (và mức effort) | [What is the Pro plan](https://support.claude.com/en/articles/8325606-what-is-the-pro-plan) · [How do usage and length limits work](https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work) |
| Có **cảnh báo** khi gần chạm giới hạn | [Use Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan) |
| Chạm giới hạn giữa chừng: Claude Code **có thể làm nốt bước đang dở rồi dừng** | [Use Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan) |
| Xem bằng **`/status`** (Claude Code) hoặc **Settings > Usage** (giờ reset kế tiếp) | [Use Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan) · [What is the Pro plan](https://support.claude.com/en/articles/8325606-what-is-the-pro-plan) |

**Không được khẳng định** (các trang trên không ghi cho gói cá nhân): cửa sổ 5 giờ bắt đầu từ lúc nào; ngày/giờ reset tuần chung cho mọi người; một con số tin nhắn hay token cụ thể. Thay vào đó, chỉ vào **giờ reset thật** trên máy học viên.

---

## Cuốn chiếu định nghĩa và sổ định nghĩa

### Vòng đời một thẻ

1. **Học** — thẻ được trình bày (hoặc học viên chứng tỏ đã biết qua câu kiểm nhanh) ở phần Làm quen nhanh, hoặc là thẻ mới khi quay lại.
2. **Dùng** — giáo viên gọi tên thẻ ngay khi nó xuất hiện trong việc thật.
3. **Nhớ lại khi chốt vòng việc** — 2 câu, chọn từ thẻ yếu nhất.
4. **Nhớ lại khi học viên quay lại** (ngày khác) — 2 câu, chọn từ thẻ lâu chưa gặp, đã sai, hoặc có tin mới; sau đó dạy 1–2 thẻ mới khi đến lượt.
5. **Thuộc** — trả lời đúng **3 lần**, trải qua **ít nhất 2 ngày khác nhau** (lớp luôn mở nên không đếm theo buổi).

### Sổ định nghĩa — `.lop-hoc/trainer.json` → `concepts`

Chỉ người đào tạo xem. Không chứa nội dung riêng, không chứa câu trả lời nguyên văn.

```json
"concepts": {
  "quyen":    { "learned": "2026-10-16", "used": 2, "recalled_ok": 2, "last": "2026-10-16", "news": false },
  "usage-5h": { "learned": "2026-10-16", "used": 0, "recalled_ok": 0, "last": "2026-10-16", "news": false }
}
```

Id thẻ: `claude-code` · `thu-muc` · `phien` · `model` · `effort` · `context` · `usage-5h` · `usage-tuan` · `quyen` · `skill`.

### Quy tắc ghi

- `learned`: ngày thẻ được trình bày lần đầu; không đổi về sau.
- `used`: +1 mỗi lần giáo viên gọi tên thẻ trong việc thật (tối đa +3 mỗi ngày cho một thẻ, để con số phản ánh số lần gặp thật chứ không phải số lần nhắc).
- `recalled_ok`: +1 khi học viên **tự bấm** đúng đáp án trong vé vào lớp, nhớ lại khi chốt vòng việc hoặc khi quay lại. Không cộng khi hết giờ (lớp chọn giúp), khi chọn "Chưa chắc", hay khi trả lời sai. Sai thì **không trừ**, thẻ đó được ưu tiên nhớ lại lần sau.
- **Tối đa +2 `recalled_ok` cho một thẻ trong cùng một ngày** (so ngày ghi ở `last`). Nhờ vậy, đạt 3 lần đúng luôn cần ít nhất 2 ngày khác nhau — đúng điều kiện "thuộc" mà không cần thêm trường.
- `last`: ngày gặp gần nhất (học, dùng hoặc nhớ lại).
- `news`: `true` khi hãng đổi model hoặc đổi cách tính usage liên quan tới thẻ (biết qua hiệu chỉnh model hoặc khi tra tài liệu chính thức có thay đổi). Lần quay lại kế tiếp giảng lại thẻ đó ("Tin mới từ hãng", nói ngày tra), hỏi một câu nhớ lại, rồi đặt lại `false`.
- **Thuộc** = `recalled_ok ≥ 3` (với giới hạn +2/ngày ở trên). Thẻ đã thuộc không còn được chọn để nhớ lại, trừ khi `news: true`.

### Chọn câu nhớ lại

- **Khi chốt vòng việc (2 câu):** trong các thẻ đã học và chưa thuộc, ưu tiên: sai hôm nay → bấm *Giải thích thêm* hôm nay → `recalled_ok` thấp nhất → chưa được dùng hôm nay. Hai câu từ **hai thẻ khác nhau**; dùng câu nhớ lại chưa hỏi hôm nay.
- **Khi học viên quay lại (2 câu):** `news: true` trước → `last` cũ nhất → `recalled_ok` thấp nhất.
- Tín hiệu nhớ lại chỉ để dạy cho vừa sức; không dùng để chấm người.
