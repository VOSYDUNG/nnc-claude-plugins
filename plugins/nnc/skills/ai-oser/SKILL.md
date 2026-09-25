---
name: ai-oser
description: NNC OSER — hệ điều hành agentic tái dùng cho một repo Claude Code. Cài (install), cập nhật (update), chuyển bố cục cũ (migrate), khám drift (doctor), ghi ledger wave/packet, và đo giá trị (metrics · quota) — Root điều khiển, Governor điều phối từng wave, execution plan theo từng work packet. Dùng khi người dùng nói "NNC OSER", "doctor", "control plane", "BUILD mode", "wave", "work packet", "ledger", "đo quota", "metrics", "giao việc cho agent", "Root rotation", hoặc khi CLAUDE.md/TRANG-THAI/agent của repo có dấu hiệu trỏ sai.
---

# NNC OSER 3 (`/nnc:ai-oser`)

**Plugin sở hữu framework; repo sở hữu cấu hình hiệu lực** (`.claude/oser/project.json`). OSER sinh các phần
có dấu `NNC-OSER:GENERATED` / `NNC-OSER:BEGIN…END` và ghi provenance ở `.claude/oser/lock.json`. Chi tiết:
`references/1-operating-model.md` · `2-routing.md` · `3-measurement.md`.

## Mô hình

Founder + Strategy → **Root** (trạng thái toàn cục, admit wave, tích hợp kết quả sạch) → **Governor** (một phiên
mới cho mỗi wave) → **phiên thực thi mới** → **verification độc lập** → kết quả wave sạch → Root.
Đơn vị lập lịch là **work packet**; mỗi lượt thử có execution plan riêng:
model × effort × context × session × song song × verification. **Không có model cố định theo vai.**
Effort là một chiều lập lịch: mọi mức runtime hỗ trợ (`low · medium · high · xhigh · max`) đều là candidate
đo được; không sàn, không mặc định.

| Mode | Trạng thái | Nghĩa |
|---|---|---|
| `setup` | active | Founder + Strategy + Root; `permissions.deny` Agent · Task · Workflow |
| `build` | admission-gated | cần `build.admission = admitted` (BUILD ADMISSION REVIEW) |
| `operate` | contract-only | — |

## CLI

Plugin đặt `bin/` lên PATH khi đã cài: `oser <lệnh>`; ngoài phiên: `python <thư-mục-skill>/../../oser/oser.py`.

| Lệnh | Việc |
|---|---|
| `oser doctor` | drift + va chạm mô hình cũ/mới (OSR-100) · BUILD admission (OSR-101) · ledger (OSR-102) |
| `oser install …` / `oser update` / `oser migrate` | cài · sinh lại GENERATED (idempotent) · chuyển bố cục 1.x/2.0 |
| `oser ledger add F.json` · `oser ledger check` | ghi/kiểm sự kiện wave/packet/attempt (schema + vòng đời) |
| `oser metrics` | verified-result cost · first-pass · rework · Root growth · isolation · defects · Fable leverage · escalation · plan benchmark |
| `oser root` · `oser quota` | chuỗi context của Root + handoff · usage thô theo model/effort/tuần (tất cả / Fable) |

## Khi dùng skill này

- Root không làm packet thường, không đọc log thô của worker; nhận kết quả sạch + đường dẫn bằng chứng.
- Machine-first: script/test/grep/emulator trước khi cấp worker LLM.
- Worker done ≠ packet done; chỉ `ROOT_ACCEPTED` đẩy milestone.
- Không sửa tay file GENERATED — sửa `project.json` rồi `oser update`; tự giữ thì khai `overrides`.
- **Founder giải xung đột sản phẩm; AI giải bất định kỹ thuật.** Không đưa lựa chọn kỹ thuật lên Founder: xem bằng
  chứng → so phương án → thử → chọn winner → ghi rationale (`decision` GREEN/AMBER) → đi tiếp. Chỉ RED
  (nghĩa nghiệp vụ · thẩm quyền · quyền · vòng đời · HIFI · metric · nguồn sự thật · phạm vi/chi phí lớn · go-live) lên Founder.
- Không chép canon của authority vào repo.
- Không nói cap thuê bao từ token: cap tuần (tổng và Fable lồng trong) là UI-only — ghi `quota_reading`.
