# NNC Claude Plugins

Bộ skill nội bộ của **NNC Lao Group**, phân phối qua marketplace của Claude Code.

## Cài (mỗi người làm một lần)

```
/plugin marketplace add <ĐƯỜNG-DẪN-GIT-CỦA-REPO-NÀY>
/plugin install nnc@nnc-claude-plugins
```

Xong. Mở dự án bất kỳ, gõ `/nnc:ai-oser` là dùng được.

## Trong gói có gì

| Skill | Gọi bằng | Làm gì |
|---|---|---|
| **NNC-AI-OSer** | `/nnc:ai-oser` | Dựng đội agent nhiều bậc cho một repo: 9 ghế, luật giao việc, thước đo quota, toggle đổi bậc theo gói (có Fable / không Fable / gói 20$) |

## Cập nhật

Repo này đổi thì chạy:
```
/plugin marketplace update nnc-claude-plugins
/plugin update nnc
```

## Vì sao có bộ này

Đo trên dự án thật (34.626 lượt gọi): khi mọi ghế agent chạy chung một model mạnh, **77% quota cháy ở
việc phụ**. Ghim bậc cho từng ghế + kỷ luật giao việc kéo chi phí mỗi lượt gọi từ **0,408 xuống 0,133**
— giảm 67%, trong khi nhịp việc tăng gấp sáu. Bộ skill này đóng gói đúng cơ cấu đó để dự án khác dùng lại.

Số tự kiểm được: sau khi cài, chạy `python cong-cu/do-quota.py` trong repo của bạn.
