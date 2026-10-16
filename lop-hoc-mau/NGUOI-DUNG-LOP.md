# Checklist người giám sát lớp

Lớp học **luôn mở**: giáo viên AI đứng lớp cho từng người, không có thời lượng buổi, không điểm danh. Người giám sát không dạy thay. Người giám sát chuẩn bị máy, kèm khi học viên cần, và đọc kết quả.

## Trước khi phát gói
- [ ] Dòng **Người hỗ trợ** ở đầu `HUONG-DAN.md` đã có tên và kênh liên hệ (người phát hành điền khi đóng gói; gói tự tải từ repo thì tự điền). Tin *Soạn tin nhờ hỗ trợ* và *Phiếu kết quả* của học viên gửi về đây.

## Cập nhật
- Gói từ 0.7.2 trở đi **tự cập nhật** theo nhánh phát hành; không cần phát gói mới cho mỗi bản.
- Máy đã cài bản trước 0.7.2: phát gói mới một lần, học viên giải nén đè lên thư mục cũ.
- Kiểm bản đang chạy trên một máy: mở `%USERPROFILE%\.claude\plugins\installed_plugins.json` bằng Notepad (chỉ xem, không sửa), tìm `lop-hoc@nnc-claude-plugins` → `version`.

## Trước khi học (mỗi máy, khoảng 10 phút)
- [ ] Claude Desktop đã cài, đăng nhập đúng tài khoản; tab **Code** mở được. Mỗi học viên một tài khoản còn hạn mức.
- [ ] Phiên bản Claude Code từ **2.1.286** trở lên (cần cho giao diện lớp học).
- [ ] Thư mục **Lop-hoc-NNC** đã giải nén; mở thử một phiên (**+ New → This computer → Open folder…**), **đồng ý** tin cậy và cài công cụ lớp học.
- [ ] Bục giảng hiện *"Lớp đang chờ giáo viên"*. Gõ `/` thấy **nnc:work-first-learning**.
- [ ] Chế độ quyền ở thanh dưới ô nhập: **Auto**. Không có Auto thì **Manual**. **Không bật Bypass permissions.**
- [ ] Nhắc học viên chuẩn bị **một việc gần đây có file** (bản sao, đã che thông tin). Không có cũng được: lớp có dữ liệu mẫu.

## Khi học viên học
- Học viên vào lớp theo nhịp riêng; nhiều người có thể bắt đầu cùng giờ nhưng không cùng nhịp.
- Máy nào bục giảng báo *"Đang cần người hỗ trợ"* thì học viên bấm **Soạn tin nhờ hỗ trợ** và gửi tin cho bạn. Ngồi cùng phòng thì đến máy đó luôn. **Không làm thay học viên.**
- Lớp nói gọn lại khi hạn mức của học viên gần hết; sắp chạm giới hạn thì giáo viên lưu chỗ để học tiếp sau giờ làm mới.

## Sau mỗi vòng việc
- Học viên bấm **Phiếu kết quả** và gửi bạn file `Phieu-ket-qua.md` (trong thư mục lớp). Phiếu không chứa tên file hay dữ liệu việc; thấy có thì nhắc học viên xoá trước khi gửi.
- Ghi mức của từng người: *có hướng dẫn* · *tự làm với đầu vào mới* · *đã dùng lại trong việc thật*. Mức cuối chỉ ghi khi người nhận kết quả chấp nhận (giáo viên hỏi lại khi học viên quay lại).
- Không chấm điểm bằng số lần bấm, số câu lệnh hay thời gian ngồi học.

## Khi gặp sự cố
| Sự cố | Xử lý |
|---|---|
| Không thấy bục giảng | Đóng phiên, mở phiên mới trong thư mục lớp; kiểm tra đã đồng ý cài công cụ lớp học |
| Không được hỏi cài công cụ | Kiểm tra máy có mạng tới GitHub; mở lại phiên; xem **+ → Plugins** có `nnc` và `lop-hoc` |
| Máy không đọc được file Excel mẫu (không có Python) | Bình thường: giáo viên dùng Excel trên máy hoặc bản CSV đi kèm dữ liệu mẫu |
| Hết hạn mức 5 giờ | Giáo viên đã lưu chỗ; học tiếp sau giờ làm mới (bấm **Tiếp tục**) |
| Claude không làm được một bước | Mở sách tự học đúng mục giáo viên chỉ, học viên làm theo sách |
| Học viên định dùng dữ liệu thật nhạy cảm | Dừng lại, làm trên bản sao đã che, hoặc chuyển sang file mẫu |
| Máy cũ vẫn chạy bản trước sau khi giải nén gói mới đè lên | Mở phiên mới trong thư mục lớp. Vẫn cũ: người phát hành gỡ nguồn cũ trên máy đó (`claude plugin marketplace remove nnc-claude-plugins`), rồi mở lại thư mục lớp và đồng ý cài công cụ (chỗ học trong `.lop-hoc` không mất) |
| Học viên người Lào | Giáo viên hỏi tiếng học ngay đầu lớp; chọn ພາສາລາວ thì bảng lớp chuyển tiếng Lào. Câu tiếng Lào đang chờ người bản ngữ duyệt: thấy câu khó hiểu thì ghi vào phiếu phản hồi |
