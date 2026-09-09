# NNC Claude Plugins

Bộ skill dùng chung của **NNC Lao Group** cho [Claude Code](https://claude.com/claude-code).
Công khai — ai thấy hữu ích thì dùng.

## Cài (một lần)

```
/plugin marketplace add https://github.com/VOSYDUNG/nnc-claude-plugins
/plugin install nnc@nnc-claude-plugins
```

Mở dự án bất kỳ, gõ `/nnc:ai-oser`.

## Trong gói có gì

| Skill | Gọi bằng | Làm gì |
|---|---|---|
| **NNC-AI-OSer** | `/nnc:ai-oser` | Dựng đội agent nhiều bậc cho một repo: 9 ghế, luật giao việc, thước đo quota, toggle đổi bậc theo gói (có Fable / không Fable / gói Pro) |

## Vì sao có bộ này

Đo trên **34.626 lượt gọi thật** của một dự án đang chạy sản xuất: khi mọi ghế agent chạy chung một
model mạnh, **77% quota cháy ở việc phụ** — dò file, chạy lệnh, tra cứu. Ghim bậc cho từng ghế cộng
kỷ luật giao việc kéo chi phí mỗi lượt gọi từ **0,408 xuống 0,133 điểm — giảm 67%**, trong khi nhịp
việc tăng gấp sáu.

Ba con số đáng nhớ, đều đo được:

- **Một lượt ở phiên chính đắt gấp 5,3 lần một lượt ở ghế thợ** — thứ đắt nhất không phải model, là
  độ dài ngữ cảnh.
- **Kéo mức tư duy lên gần như không đắt hơn** (−5% đến +4% mỗi lượt) trong khi tỉ lệ token "nghĩ"
  tăng rõ — nghĩ kỹ rẻ hơn làm lại.
- **Gói không có model cao nhất vẫn rẻ nhất** — hồ sơ `opus`/`sonnet` đo được rẻ hơn cấu hình cao cấp,
  vì nó bỏ luôn cái đệm dễ bị lạm dụng.

Không phải tin — sau khi cài, chạy `python cong-cu/do-quota.py` trong repo của bạn và tự xem.

## Cập nhật

```
/plugin marketplace update nnc-claude-plugins
/plugin update nnc
```

## Đẩy cho cả tổ chức

Quản trị viên xem `CHO-ADMIN-day-toan-to-chuc.md` — hai khoá trong managed settings là mọi thành viên
có sẵn, không ai phải gõ lệnh.

## Giấy phép

MIT. Số liệu trong tài liệu là chỉ số vận hành nội bộ của công cụ AI, không chứa dữ liệu kinh doanh.
