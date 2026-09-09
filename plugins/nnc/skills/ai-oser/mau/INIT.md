# INIT ĐỢT {{N}} — tờ cấu hình người chủ đọc TRƯỚC khi phát goal (5 phút)

**Init là gì:** tờ khai trước chuyến bay. GOAL là lệnh hành quân cho quản đốc; INIT này là của **bạn** —
vài lựa chọn cấu hình, mỗi cái có khuyến nghị sẵn, chọn xong dán một câu goal là buông tay.

## Chọn 1 — ghế nhận goal chạy model nào

| Phương án | Khi nào đáng |
|---|---|
| **A (khuyến nghị — ĐANG GHIM)** `{{MODEL_R0}}` | sóng có lô nặng, có quyết định kiến trúc |
| B — hạ một bậc | sóng chỉ toàn lô vá nhỏ |

**Vì sao ghế này xứng model đắt nhất:** nó **không code** — tiêu token vào đề bài và trọng tài, tức phần
*ít token nhất* nhưng **lái phần lớn chi phí phía dưới**. Quản đốc rẻ mà cắt lô sai một lần là cả chuỗi
ghế rẻ chạy lại từ đầu — lỗ kép.

## Chọn 2 — mức tư duy
Nếu phiên chạy **không người trực**: chốt mức TRƯỚC khi phát goal (giữa chừng không ai chỉnh được).
Mức cao nhất để dành cho bế tắc thật — thuốc đặc trị, không phải vitamin.

## Chọn 3 — chế độ duyệt quyền
Goal "chạy đến xong" mà phiên dừng hỏi y/n giữa lúc bạn đi vắng thì mọi thứ ở trên vô nghĩa.
- **Bypass permissions** hợp lệ khi: mọi sửa đổi nằm trong git · phiên không cầm key/secret nguy hiểm ·
  các chỗ dừng là **luật hành vi trong CLAUDE.md, không phải nút bấm**.
- Còn lại thì duyệt tay — nhưng khi đó phải có người ngồi.

## Chọn 4 — các ghế dưới: đã ghim, đừng chỉnh tay
Chỉ xem lại khi **số** nói khác: sau lô đầu chạy `do-quota.py`, vượt ngưỡng mới mở nắp máy.

## Xong → làm hai việc
1. Checklist môi trường (mục "Chuẩn bị máy" trong GOAL).
2. Dán lệnh kích hoạt ở cuối GOAL.

Từ lúc đó, chỗ của bạn là **đọc báo cáo cuối sóng**, không phải duyệt giữa đường. Quản đốc chỉ được gọi
bạn đúng hai lý do: **spec sai**, hoặc **van quota nổ**.
