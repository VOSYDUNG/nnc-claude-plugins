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
| **NNC OSER** (skill) | `/nnc:ai-oser` | hướng dẫn agent dùng control plane: mode · capability · model class · ownership |
| **NNC OSER** (CLI) | `oser install · update · migrate · doctor · status · quota` | cài / cập nhật / chuyển đổi / khám drift cấu hình Claude Code của một repo |

**Plugin sở hữu framework; repo sở hữu cấu hình hiệu lực** (`.claude/oser/project.json`). Mọi file OSER
sinh ra đều có dấu `NNC-OSER:GENERATED` và provenance trong `.claude/oser/lock.json`.

Không cần gì ngoài Python 3.8+ (thư viện chuẩn) và git.

## Nâng từ 1.0 (NNC-AI-OSer — 9 ghế, `doi-bac.py fable|opus|sonnet`)

2.0 là bản **MAJOR**: hồ sơ theo tên model được thay bằng mode/capability/model class, và bố cục dự án
đổi. Đường chuyển có sẵn, không mất file của dự án:

1. viết `.claude/oser/project.json` từ `plugins/nnc/oser/templates/project.example.json`;
2. `oser doctor` (số trước) → dọn phần văn của dự án → `oser migrate` → `oser doctor` (số sau);
3. `cong-cu/doi-bac.py` và `cong-cu/do-quota.py` bản chép nguyên được thay bằng wrapper gọi `oser`.

Bản 1.0 còn nguyên ở tag `v1.0.0`.

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
