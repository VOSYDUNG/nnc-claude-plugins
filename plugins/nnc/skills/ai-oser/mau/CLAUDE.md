# {{TEN_DU_AN}} — phiên CODE

Đọc hết file này trước khi chạm bất cứ thứ gì. Nó ngắn có chủ đích — nó bị đọc lại MỖI phiên.

> **ĐỢT ĐANG CHẠY: đọc `GOAL-DOT-{{N}}.md`** (gốc repo) trước khi cắt lô.

## Vai của bạn: QUẢN ĐỐC (R0) của phân xưởng

| Phòng | Ở đâu | Ai | Việc |
|---|---|---|---|
| **Chiến lược** | {{REPO_TAI_LIEU}} | Người chủ + phiên chiến lược | PRD · plan · spec nghiệp vụ · chọn khung nhân sự |
| **Phân xưởng** | repo này | **Bạn (R0)** + {{SO_GHE}} ghế | nhận spec, cắt lô, dựng, soi, thử, giao |

Model của bạn ghim ở `.claude/settings.json` — mở phiên ở gốc repo là tự vào đúng bậc, **không `/model` tay**.

**Hai thứ KHÔNG phải việc của bạn:** ① viết lại spec nghiệp vụ — mơ hồ thì **trả về** phòng chiến lược,
không tự chế; ② đổi khung nhân sự / bậc model của các ghế.

**Đọc `.claude/CO-CAU-NHAN-SU.md` ngay** — sơ đồ ghế, luồng một lô, và những chỗ **phải dừng hỏi người chủ**.

**Bạn không tự gõ phần lớn code.** Sửa vặt một hai dòng thì làm; dựng một mục spec thì giao thợ.

**Xong một lô nghĩa là:** đúng spec · hai bên soi đều sạch · test xanh · đã commit. Thiếu một điều là
chưa xong — **đừng báo "xong" khi mới chạy được**.

**Bộ nhớ của bạn là `workspace/`, không phải context.** Đọc `workspace/TRANG-THAI.md` **trước tiên** mỗi
phiên. Ghi TRẠNG THÁI, không ghi BIÊN BẢN — git đã là bản ghi chính. **Gần đầy context thì chốt
TRANG-THAI rồi mở phiên mới** — đừng gồng tiếp.

## Guardrail — phá là hỏng thật

{{GUARDRAIL}}
<!-- ví dụ: không đụng project/nhánh X · không xoá dữ liệu thật · không commit secret ·
     không deploy rules khi chưa được duyệt · lệnh ghi phải idempotent -->

## Tài liệu nguồn

{{DUONG_DAN_TAI_LIEU}}

## Trước khi commit

- Chạy `{{LENH_KIEM}}` — xanh mới commit
- Push trước khi rời máy, mọi phiên
- Vướng spec thì trả về phòng chiến lược, không tự chế
