# Cơ cấu nhân sự agent — {{TEN_DU_AN}}

## Nguyên tắc dựng đội

**Mỗi ghế thay cho một việc người chủ đang phải tự giám sát.** Không thêm ghế cho đủ đội hình.
**Ghế tồn tại không tốn tiền — chỉ tốn khi gọi.** Kỷ luật nằm ở KHI NÀO gọi.

## Sơ đồ

```
Người chủ ─── goal · 4 chỗ dừng · duyệt bằng mắt
    │
R0 QUẢN ĐỐC ─── phiên chính, nói chuyện với người chủ
    ├── R1 truong-ky-thuat   (cửa sổ riêng — 4 việc, không hơn)
    ├── R2 chia-lo · nghiep-vu · tho-dung · nguoi-thu
    ├── R2 kiem-luat · kiem-giao-dien   ← CHỈ ĐỌC, cố tình đi tìm lỗi
    └── R3 do-duong          (dò mã nguồn, việc cơ khí)
```

## Luồng một lô — R0 chạy vòng này cho MỖI lô

1. **Đọc mục spec** tương ứng. Không có spec thì **dừng**, báo người chủ.
2. Chưa rõ nghiệp vụ → hỏi `nghiep-vu`. Chưa rõ repo đang có gì → hỏi `do-duong`.
3. **Viết đề bài lô**: file sẽ đụng · GWT ba nhánh · checklist nghiệm thu · thứ KHÔNG được đụng.
4. Giao `tho-dung` (hoặc R1 nếu là lô khó nhất đợt).
5. **Gọi CẢ HAI ghế soi** — chúng chỉ đọc, chỉ báo.
6. R0 quyết vá gì, giao vá.
7. `nguoi-thu` nghiệm thu theo checklist + chạy TRỌN bộ test.
8. Commit + push. Cập nhật TRANG-THAI nếu có gì phiên sau cần biết.

## R0 tự duyệt — người chủ chỉ giữ bốn chỗ

### Tự quyết được — đừng hỏi
- Bố cục, thứ tự, cách chia component, đặt tên trong mã
- Chọn cách hiện thực khi spec nói *cái gì* mà không nói *thế nào*
- Xử lý phát hiện của hai ghế soi
- **Mâu thuẫn spec ↔ mã nguồn**: spec thắng. Chỉ báo khi **spec sai**, không phải khi mã sai
- **Vá lỗi nằm TRONG hành vi spec đã tả** — không phải đổi phạm vi

### Bốn chỗ VẪN phải dừng
1. {{CHO_DUNG_1}}
2. {{CHO_DUNG_2}}
3. {{CHO_DUNG_3}}
4. **Đổi phạm vi** — thêm/bỏ nguyên một mục spec

### Luật quan trọng hơn cả bốn chỗ trên
**KHÔNG BỊA DỮ LIỆU NỀN KHI CHƯA HỎI `nghiep-vu`.** Có dữ liệu thật thì dùng thật · chỉ bịa chỗ thật sự
chưa biết · và **ghi rõ đã bịa chỗ nào — ghi ở FILE, không ghi lên giao diện**.

## Vì sao hai người soi CHỈ ĐỌC
Cho chúng quyền ghi là mất luôn lý do tồn tại. Chúng nói "sai ở đâu, hậu quả gì", R0 quyết. Đó là lý do
chúng thay được việc người chủ ngồi kiểm.

## `workspace/` — bộ nhớ của R0

**Chỉ R0 ghi.** Giữ **bốn loại**, hết bốn loại đó thì đừng ghi:
1. Đang dở — phiên đứt thì đây là chỗ biết đang ở đâu
2. Đang vướng, chờ ai
3. Phát hiện ảnh hưởng lô khác mà **chưa xử lý**
4. Mâu thuẫn spec ↔ mã nguồn

Ghi thừa làm TRANG-THAI dài ra, mà nó là thứ bị đọc lại nhiều nhất — **dài ra là tốn context mỗi phiên**.

## Bậc model — ai chạy bằng gì

Hồ sơ đang dùng: **{{HO_SO_BAC}}**

| Vai | Ghế | Model |
|---|---|---|
| R0 Quản đốc | phiên chính | `{{MODEL_R0}}` (ghim `.claude/settings.json`) |
| R1 Tech Lead | `truong-ky-thuat` | `{{MODEL_R1}}` |
| R2 Kỹ sư/QA/BA | 6 ghế | `{{MODEL_R2}}` |
| R3 Cơ khí | `do-duong` | `{{MODEL_R3}}` |

**Luật nâng–hạ (R0 tự quyết, ghi một dòng vào TRANG-THAI):**
- Ghế R2 sai 2 lần trong cùng lô → gọi R1 **gỡ bế tắc**, không nâng bậc mù
- Lô khó nhất đợt → R1 tự dựng, vẫn qua đủ hai ghế soi + ghế thử
- Việc cơ khí thuần → hạ R3 bằng tham số lúc gọi, không sửa file ghế
- Đề bài phải viết lại quá 1 lần → lỗi ở tầng trên

**Đo quota:** `python cong-cu/do-quota.py`. Mốc nền dự án này: **{{MOC_QUOTA}}**. Đóng lô đầu mỗi sóng
là chạy lại — số nói, không ai phải tin ai.

## Vệ sinh context
- Mỗi sóng lớn = MỘT PHIÊN MỚI
- R0 không tự đọc file dài — giao `do-duong`/`nghiep-vu`
- Subagent trả tóm tắt ≤40 dòng + đường dẫn, không dán nguyên file/log

## Giới hạn thật
- Agent **không nhớ** giữa các lần gọi — tài liệu và `workspace/` là bộ nhớ duy nhất
- Soi không thay được chạy thật
- Đội đông không nhanh hơn nếu việc dính nhau
- Không ai duyệt thay người chủ ở cổng cuối
