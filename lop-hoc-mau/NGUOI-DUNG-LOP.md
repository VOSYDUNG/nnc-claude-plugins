# Checklist người đứng lớp

## Trước buổi học (mỗi máy, khoảng 10 phút)
- [ ] Claude Desktop đã cài, đăng nhập đúng tài khoản; tab **Code** mở được.
- [ ] Mở `/status` trong một phiên Code: phiên bản Claude Code từ **2.1.286** trở lên (cần cho giao diện lớp học).
- [ ] Thư mục **Lop-hoc-NNC** đã giải nén; mở thử một phiên **Local** trong thư mục này và **đồng ý** tin cậy, cài công cụ lớp học.
- [ ] Bục giảng hiện *"Lớp đang chờ giáo viên"*. Gõ `/` thấy **nnc:work-first-learning**.
- [ ] Chế độ quyền để mặc định (hỏi trước khi làm), không bật chế độ bỏ qua quyền.
- [ ] Nhắc học viên chuẩn bị **một việc gần đây có file** (bản sao, đã che thông tin). Không có cũng được: lớp có dữ liệu mẫu.

## Trong buổi học
- Mở lớp bằng lời của bạn trong 1–2 phút, rồi để giáo viên trong Claude dẫn.
- Đi quanh lớp. Máy nào bục giảng báo *"Đang cần người đứng lớp hỗ trợ"* hoặc *"Lớp tạm nghỉ"* thì đến hỗ trợ. **Không làm thay học viên.**
- Cuối buổi chốt bằng 1–2 câu chuyện đẹp trong lớp và nhắc bài về nhà.

## Sau buổi học
- Ghi mức của từng người: *có hướng dẫn* · *tự làm với đầu vào mới* · *đã dùng lại trong việc thật*. Mức cuối chỉ ghi khi bài về nhà được người nhận nghiệp vụ chấp nhận.
- Không chấm điểm bằng số lần bấm hay số câu lệnh.
- Huy hiệu của học viên nằm trong `.lop-hoc/huy-hieu.json` của thư mục lớp trên máy họ.

## Khi gặp sự cố
| Sự cố | Xử lý |
|---|---|
| Không thấy bục giảng | Đóng phiên, mở phiên mới trong thư mục lớp; kiểm tra đã đồng ý cài công cụ lớp học |
| Không được hỏi cài công cụ | Kiểm tra máy có mạng tới GitHub; mở lại phiên; xem mục **Plugins** có `nnc` và `lop-hoc` |
| Hết hạn mức 5 giờ | Làm cặp với bạn bên cạnh; xem giờ reset (đây cũng là một bài học) |
| Học viên định dùng dữ liệu thật nhạy cảm | Dừng lại, chuyển sang file mẫu |
