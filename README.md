# NNC Claude Plugins

Bộ plugin dùng chung của **NNC Lao Group** cho [Claude Code](https://claude.com/claude-code). Công khai.

## Cài (một lần)

```
/plugin marketplace add https://github.com/VOSYDUNG/nnc-claude-plugins
/plugin install nnc@nnc-claude-plugins
```

Mở dự án bất kỳ, gõ `/nnc:ai-oser`, hoặc gọi thẳng CLI (plugin đặt `bin/` lên PATH của phiên):

```
oser doctor
```

## Trong gói có gì

| Thành phần | Gọi bằng | Làm gì |
|---|---|---|
| **NNC OSER** (skill) | `/nnc:ai-oser` | hướng dẫn agent vận hành: Root · Governor/wave · work packet · verification · đo |
| **NNC OSER** (CLI) | `oser install · update · migrate · doctor · status · ledger · metrics · root · quota` | cài / cập nhật / chuyển bố cục / khám drift / ghi ledger / đo giá trị |

**Plugin sở hữu framework; repo sở hữu cấu hình hiệu lực** (`.claude/oser/project.json`). Mọi file OSER
sinh ra đều có dấu `NNC-OSER:GENERATED` và provenance trong `.claude/oser/lock.json`.

Mô hình: Root điều khiển toàn cục → một Governor cho mỗi wave → phiên thực thi mới theo **work packet** →
verification độc lập. Model và effort chọn **theo từng lượt thử**, không theo vai; đơn vị so sánh là
**verified result**. Chi tiết: `plugins/nnc/skills/ai-oser/references/`.

Không cần gì ngoài Python 3.8+ (thư viện chuẩn) và git.

## Chuyển từ bố cục cũ (chỉ migration)

`oser migrate` đưa dự án 1.x hoặc 2.0 về 3.x: nâng `project.json` lên `nnc-oser/project@3`, gỡ cấu hình
model-theo-vai và các định nghĩa đội cũ **chỉ khi git đang giữ chúng nguyên vẹn** (không thì dừng, không ghi gì),
thay bản chép công cụ đo quota bằng wrapper gọi `oser`. Bản 1.x còn ở tag `v1.0.0`, bản 2.0 ở tag `v2.0.0`.

## Kiểm plugin

```
python -m unittest discover -s tests -v
```

## Cập nhật

```
/plugin marketplace update nnc-claude-plugins
/plugin update nnc
```

Rồi trong mỗi dự án: `oser update` (idempotent — chạy lần hai không đổi gì).

## Đẩy cho cả tổ chức

Quản trị viên xem `CHO-ADMIN-day-toan-to-chuc.md`.

## Giấy phép

MIT. Số liệu trong tài liệu là chỉ số vận hành nội bộ của công cụ AI, không chứa dữ liệu kinh doanh.
