# Lớp học NNC — đóng gói, cài đặt, cập nhật và pilot (v0.7)

**Nơi chạy:** Claude Desktop trên Windows, tab **Code**, phiên **Local**. Giao diện lớp học (mod) cần Claude Code 2.1.286 trở lên.
**Bản phát hành pilot:** tag `lop-hoc-v0.7.2` trên nhánh `feat/learning-work-first-v0.1` (chưa merge `main`); nhánh phát hành **`lop-hoc-release`** trỏ cùng commit.
**Thành phần** (cùng một marketplace `nnc-claude-plugins`, nguồn đường dẫn tương đối):

| Plugin | Phiên bản | Chứa |
|---|---|---|
| `nnc` | `5.1.0-alpha.2+lophoc.0.7.2` | NNC OSER alpha.2 + Skill **`nnc:work-first-learning`** 0.7.2 (giáo viên, vòng việc, kho trò, thẻ định nghĩa, sách tự học, dữ liệu mẫu) |
| `lop-hoc` | `0.7.2` | Mod giao diện song ngữ Việt–Lào: lớp luôn mở, bục giảng, phần học theo mốc, tín hiệu hạn mức, một chạm, thử thách, sao, huy hiệu, phiếu kết quả |

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
       ├── extraKnownMarketplaces: nnc-claude-plugins ← git HTTPS github.com/VOSYDUNG/nnc-claude-plugins.git @ lop-hoc-release, autoUpdate
       ├── enabledPlugins: nnc@nnc-claude-plugins, lop-hoc@nnc-claude-plugins
       └── permissions.allow: Edit(./.lop-hoc/**), Edit(./Thuc-hanh/**), Edit(./Phieu-ket-qua.md)
~~~

Người mới mở thư mục trong **Claude Desktop → Code → New session → Local** (trên giao diện hiện nay: **+ New → This computer → Open folder…**), đồng ý tin cậy thư mục, chọn chế độ quyền **Auto** (không có thì Manual; không dùng Bypass permissions). Claude Code tải marketplace từ GitHub theo nhánh phát hành, **qua HTTPS** (dạng rút gọn `owner/repo` clone bằng SSH nên hỏng trên máy không có khóa SSH; đã kiểm bằng một lần cài mới). Hai plugin dùng đường dẫn tương đối nên được nạp theo marketplace, không cần lệnh cài.

**Dựng lại gói:** `python tools/build_lop_hoc_mau.py --zip <đường dẫn>.zip`. Dòng **Người hỗ trợ** trong `HUONG-DAN.md` của ZIP được điền từ `--support "…"` hoặc file `.lien-he-ho-tro.txt` (đã gitignore, chỉ trên máy người phát hành); repo luôn giữ dòng trống. Test kiểm tra `CLAUDE.md` của gói khớp template, gói trỏ nhánh `lop-hoc-release` và bật `autoUpdate`.

## 2. Kiểm tra một máy (G1)

1. Bục giảng hiện *"Lớp đang chờ giáo viên"*; chỉ có nút chọn thầy/cô và **Vào lớp** (v0.7 không chọn thời lượng).
2. Gõ `/`: có **`/nnc:work-first-learning`** và **`/nnc:mission-formation`**. Trong môi trường phát triển, Skill có thể hiện là `/work-first-learning`.
3. Thiếu thì ghi **INSTALL_NOT_VERIFIED**, mở phiên mới và xem mục Plugins hoặc thẻ Errors.
4. Nguồn hoặc phiên bản OSER không rõ (ví dụ máy đã cài `nnc` từ nguồn khác cùng tên marketplace) thì dừng ở **OSER_SOURCE_UNVERIFIED** và gửi ảnh chụp.
5. Không bật Experience Observer, không chạy OSER init, không cấp quyền rộng, không đưa dữ liệu riêng lên, không ghi vào hệ thống thật.

## 3. Phát hành bản mới

**Cách máy nhận bản mới (từ 0.7.2).** Gói trỏ nhánh `lop-hoc-release` và bật `autoUpdate`. Trong một phiên tương tác, sau tin nhắn đầu tiên Claude Code chờ ngẫu nhiên tối đa 10 phút rồi làm mới marketplace và cập nhật plugin đã cài khi `version` đổi; phiên đang chạy giữ bản cũ, phiên mở sau dùng bản mới. Không cần phát ZIP mới cho mỗi bản.

**Máy đã cài trước 0.7.2** (nguồn ghi trên máy là một tag cũ): phát ZIP mới một lần, học viên giải nén **đè lên** thư mục lớp cũ (giữ `.lop-hoc/`). Tài liệu chính thức nói marketplace khai báo trong settings mà đổi nguồn thì được tải lại từ nguồn mới; trường hợp chỉ đổi `ref` chưa có câu chữ riêng, nên kiểm trên máy thử (`claude plugin marketplace list --json` thấy `ref: lop-hoc-release`). Vẫn giữ tag cũ thì người phát hành chạy `claude plugin marketplace remove nnc-claude-plugins` trên máy đó rồi mở lại thư mục lớp (gỡ nguồn cũng gỡ plugin; mở lại thư mục sẽ cài lại; `.lop-hoc/` không mất).

**Các bước phát hành:**

1. Đổi `version` của `nnc` và/hoặc `lop-hoc` (cả `plugin.json` và `marketplace.json`). **Không đổi phiên bản thì máy đã cài giữ bản cũ.**
2. Chạy toàn bộ test: `python -m pytest tests`, rồi `claude plugin test plugins/lop-hoc` và `claude plugin validate plugins/lop-hoc` bằng bản `claude` đi kèm Desktop. Máy phát hành phải có `.noi-bo-tu-cam.txt` (gitignore) để test từ cấm thật sự chạy; thiếu file này thì **không đẩy** từ máy đó.
3. Commit, gắn tag `lop-hoc-vX.Y.Z`, đẩy nhánh làm việc và tag.
4. Đẩy nhánh phát hành tới đúng commit đó: `git push origin lop-hoc-vX.Y.Z^{commit}:refs/heads/lop-hoc-release`. Từ lúc này các máy tự cập nhật.
5. Chỉ khi gói đổi (HUONG-DAN, settings, CLAUDE.md): dựng ZIP với người hỗ trợ và phát lại.

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

**v0.7:** lớp luôn mở, vòng việc, nhịp theo hạn mức, kèm việc ở thư mục của học viên — hợp đồng §9.

Tài liệu thiết kế: [hợp đồng chung](LOP-HOC-V05-CONTRACT.md) · [bộ năng lực giáo viên](LOP-HOC-NANG-LUC-GIAO-VIEN.md) · [Buổi 1](LOP-HOC-BUOI-1.md). Tài liệu chính thức: https://code.claude.com/docs/en/plugins/mods/overview · https://code.claude.com/docs/en/plugins/marketplace-reference.
