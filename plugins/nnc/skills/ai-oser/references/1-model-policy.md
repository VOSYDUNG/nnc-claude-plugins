# Chính sách model — EXPECTED · CONFIGURED · OBSERVED

## Vì sao bỏ "hồ sơ theo tên model" (fable | opus | sonnet)

NNC-AI-OSer 1.0 ghim tên model vào `.claude/settings.json` (ROOT) và `model:` của 9 ghế, đổi bằng
`doi-bac.py`. Pilot nnc-kho đo được hai lỗi của cách đó:

| Đo (transcript thật) | Cấu hình khi đó | ROOT chạy thật |
|---|---|---|
| phiên 13/09/2026 | `settings.json` = `claude-opus-5` | `claude-fable-5-1` |
| phiên 25/09/2026 | `settings.json` = `claude-opus-5` | `claude-opus-5-5` |

1. **File không điều khiển ROOT ở Claude Desktop** — bảng chọn model của app thắng.
2. **Tên model mục theo thế hệ** — `claude-fable-5` / `claude-opus-5` còn nằm trong cấu hình khi máy
   đã chạy `-5-1` / `-5-5`.

## Chính sách 2.0

| Lớp | Mặc định | Luật |
|---|---|---|
| `root` | `inherit` | theo phiên đang mở. Chỉ ghim id tường minh khi client đó thật sự tôn trọng (ví dụ CLI `--model`) và doctor quan sát khớp |
| `frontier-audit` | `fable` | chỉ ở audit gate; phân giải thành thế hệ mới nhất ĐÃ QUAN SÁT lúc kích hoạt |
| `lead` | `opus` | alias họ model — không mục theo thế hệ |
| `worker` | `sonnet` | 〃 |
| `mechanical` | `haiku` | 〃 |

Dự án đổi mapping trong `project.json › models.classes`. Mapping chỉ có hiệu lực khi một capability
được **assignment** chạy — mode `setup` không chạy capability nào ngoài `investigate` (ROOT).

## Doctor đọc gì

- **EXPECTED** — `models.root` trong manifest.
- **CONFIGURED** — `model` trong `.claude/settings.json`, `settings.local.json`, `~/.claude/settings.json`.
- **OBSERVED** — lượt assistant mới nhất của main thread trong `~/.claude/projects/<slug>/`.

Cảnh báo khi: ghim ROOT mà policy là `inherit`; EXPECTED ≠ OBSERVED; id cứng cũ hơn thế hệ đã quan sát
cùng họ; mô tả ghế nói một họ model nhưng ghim họ khác.

**Chưa đo trong 2.0:** subagent có chạy đúng model class của assignment không. Transcript pilot cho thấy
ghim `model:` ở ghế từng có hiệu lực (Sonnet/Haiku xuất hiện ở sidechain), nhưng SETUP cấm subagent nên
chưa kiểm lại — việc của lần mở BUILD đầu tiên.

## Chi phí (đo 1.0, vẫn đúng làm thước)

Trọng số theo tỉ lệ bảng giá API: Opus/Fable 15/75 · Sonnet 3/15 · Haiku 0.8/4 $/MTok; cache đọc 0.1×,
cache ghi 1.25×. Trên gói thuê bao số tuyệt đối không phải tiền — so sánh cùng thước thì đúng.
Pilot 21/08→09/09: Haiku 0,010 · Sonnet 0,069 · Opus 0,465 điểm/lượt; lượt ở phiên chính đắt ~5,3× lượt
ở subagent vì độ dài ngữ cảnh. Chạy `oser quota --ngay 7` để có số của chính dự án.
