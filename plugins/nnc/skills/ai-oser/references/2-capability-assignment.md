# Capability · Assignment · Ownership

## Capability (plugin catalog `oser/catalog/capabilities.json`)

| Capability | Chạy ở | Model class | Ghi chú |
|---|---|---|---|
| `investigate` | ROOT | `root` | đo môi trường thật, đọc mã + authority, trả bằng chứng — **active trong `setup`** |
| `strategy` | ngoài repo | — | người + phiên chiến lược sở hữu WHAT/WHY |
| `implement` · `review` · `test` | assignment | `worker` | chỉ chạy khi mode có assignment |
| `map-code` | assignment | `mechanical` | tra cứu cơ khí |
| `audit` | gate | `frontier-audit` | Fable; tắt mặc định, không bao giờ always-on |

## Assignment (dự án khai, chưa có mặc định)

`build`/`operate` là **contract-only** trong 2.0: manifest chọn các mode đó mà không có `assignments`
thì doctor báo critical và `oser update` từ chối. Hình dạng assignment (ai · capability · model class
· gate) sẽ chốt sau khi pilot đo BUILD thật — plugin không định sẵn roster.

Bộ 9 ghế của 1.0 (`truong-ky-thuat`, `tho-dung`, …) là **bằng chứng** cho thiết kế BUILD, không phải
mặc định: xem tag `v1.0.0`. Migrate chuyển các ghế đó nguyên byte sang `.claude/oser/inactive/agents/`.

## Lớp sở hữu

| Lớp | Ví dụ | `oser update` |
|---|---|---|
| PLUGIN-GENERATED | khối status trong CLAUDE.md · `CONTROL-PLANE.md` · wrapper tương thích · key quản lý trong settings.json · `lock.json` | sinh lại khi nội dung đổi; bỏ qua nếu bị sửa tay (báo) |
| PROJECT-OWNED | `project.json` · phần còn lại của CLAUDE.md · `TRANG-THAI.md` · công cụ riêng dự án | không bao giờ ghi |
| PROJECT-OVERRIDE | đường dẫn trong `overrides` | không ghi, doctor báo info |
| INACTIVE | `.claude/oser/inactive/` | không ghi (chỉ README) |
| HISTORICAL | khai trong `control_plane.historical` | không ghi; doctor kiểm banner |

Provenance của mỗi artifact trả lời: version OSER nào · mode nào · lúc nào (chỉ đổi khi nội dung đổi)
· template/schema nào · dự án có override không.
