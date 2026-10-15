# Lớp học NNC — đóng gói, cài đặt và pilot (v0.6)

**Nơi chạy:** Claude Desktop trên Windows, tab **Code**, phiên **Local**. Giao diện lớp học (mod) cần Claude Code 2.1.286 trở lên.
**Bản phát hành pilot:** tag `lop-hoc-v0.6.0` trên nhánh `feat/learning-work-first-v0.1` (chưa merge `main`).
**Thành phần** (cùng một marketplace `nnc-claude-plugins`, nguồn đường dẫn tương đối):

| Plugin | Phiên bản | Chứa |
|---|---|---|
| `nnc` | `5.1.0-alpha.2+lophoc.0.6.0` | NNC OSER alpha.2 + Skill **`nnc:work-first-learning`** (giáo viên, giáo án, kho trò, thẻ định nghĩa, dữ liệu mẫu) |
| `lop-hoc` | `0.6.0` | Mod giao diện: bục giảng, nhịp buổi học, một chạm, thử thách, sao, huy hiệu |

**Trạng thái:** test tĩnh, test engine của mod và test dữ liệu mẫu đều qua; **chưa có học viên thật**. Test hay một lần cài thành công là **not proof of learner independence**.

## 1. Gói giao cho người mới

Thư mục `lop-hoc-mau/` trong repo, phát dưới dạng ZIP **Lop-hoc-NNC**:

~~~text
Lop-hoc-NNC/
├── CLAUDE.md            ← quy tắc lớp học (sinh từ templates/classroom-CLAUDE.md)
├── HUONG-DAN.md         ← 4 bước cho học viên
├── NGUOI-DUNG-LOP.md    ← checklist người đứng lớp
├── Thuc-hanh/           ← nơi giáo viên chép file mẫu
└── .claude/settings.json
       ├── extraKnownMarketplaces: nnc-claude-plugins ← git HTTPS github.com/VOSYDUNG/nnc-claude-plugins.git @ lop-hoc-v0.6.0
       ├── enabledPlugins: nnc@nnc-claude-plugins, lop-hoc@nnc-claude-plugins
       └── permissions.allow: Edit(./.lop-hoc/**), Edit(./Thuc-hanh/**)
~~~

Người mới mở thư mục trong **Claude Desktop → Code → New session → Local**, đồng ý tin cậy thư mục. Claude Code tải marketplace từ GitHub theo tag, **qua HTTPS** (dạng rút gọn `owner/repo` clone bằng SSH nên hỏng trên máy không có khóa SSH; đã kiểm bằng một lần cài mới). Hai plugin dùng đường dẫn tương đối nên được nạp theo marketplace, không cần lệnh cài.

**Dựng lại gói:** `python tools/build_lop_hoc_mau.py --tag <tag> --zip <đường dẫn>.zip`. Test kiểm tra `CLAUDE.md` của gói khớp template và tag khớp phiên bản `lop-hoc`.

## 2. Kiểm tra một máy (G1)

1. Bục giảng hiện *"Lớp đang chờ giáo viên"*.
2. Gõ `/`: có **`/nnc:work-first-learning`** và **`/nnc:mission-formation`**. Trong môi trường phát triển, Skill có thể hiện là `/work-first-learning`.
3. Thiếu thì ghi **INSTALL_NOT_VERIFIED**, mở phiên mới và xem mục Plugins hoặc thẻ Errors.
4. Nguồn hoặc phiên bản OSER không rõ (ví dụ máy đã cài `nnc` từ nguồn khác cùng tên marketplace) thì dừng ở **OSER_SOURCE_UNVERIFIED** và gửi ảnh chụp.
5. Không bật Experience Observer, không chạy OSER init, không cấp quyền rộng, không đưa dữ liệu riêng lên, không ghi vào hệ thống thật.

## 3. Phát hành bản mới

1. Đổi `version` của `nnc` và/hoặc `lop-hoc` (cả `plugin.json` và `marketplace.json`). Plugin GitHub được chép vào cache theo phiên bản, nên **không đổi phiên bản thì máy đã cài giữ bản cũ**.
2. Chạy toàn bộ test: `python -m unittest discover -s tests`, rồi `claude plugin test plugins/lop-hoc` và `claude plugin validate plugins/lop-hoc` bằng bản `claude` đi kèm Desktop.
3. Gắn tag mới, dựng lại `lop-hoc-mau` với tag đó, phát ZIP mới.

## 4. Riêng tư khi phát hành

Repo là **công khai**. File đưa lên repo không chứa tên người, yêu cầu nội bộ, đường dẫn tài liệu nội bộ hay dữ liệu thật; test `test_lop_hoc_package.py` kiểm tra điều này. Dữ liệu mẫu đều là dữ liệu giả, có nhãn "— mẫu".

## 5. Cổng kiểm chứng

| Cổng | Kiểm gì |
|---|---|
| G1 | Cài từ gói, bục giảng và Skill hiện đủ |
| G2 | Giáo viên mở từ việc gần nhất, thao tác thật trong 2 phút đầu |
| G3 | Học viên làm một việc và tự kiểm |
| G4 | Đầu vào đổi hoặc thiếu được kiểm, không đoán |
| G5 | Học viên tự làm một việc mới mà người đào tạo không làm thay |

Tài liệu thiết kế: [hợp đồng chung](LOP-HOC-V05-CONTRACT.md) · [bộ năng lực giáo viên](LOP-HOC-NANG-LUC-GIAO-VIEN.md) · [Buổi 1](LOP-HOC-BUOI-1.md). Tài liệu chính thức: https://code.claude.com/docs/en/plugins/mods/overview · https://code.claude.com/docs/en/plugins/marketplace-reference.
