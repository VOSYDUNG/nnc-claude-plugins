---
name: ai-oser
description: Khởi tạo và vận hành "xưởng AI" — đội agent nhiều bậc model có kỷ luật token — cho MỘT repo bất kỳ. Dùng khi người dùng muốn dựng đội agent cho dự án mới, chuẩn hoá cách giao việc cho agent, giảm quota hao phí, đo chi phí phiên, hoặc nói "init dự án", "dựng đội agent", "xưởng AI", "NNC-AI-OSer", "khởi tạo đội", "giao việc cho agent sao cho rẻ". Tự dò gói Claude đang dùng (có Fable hay cao nhất là Opus) để ghim model an toàn, không phát sinh phí ngoài gói.
---

# NNC-AI-OSer (`/nnc:ai-oser`) — dựng xưởng AI cho một repo

Skill này biến một repo thành **phân xưởng có tổ chức**: một quản đốc điều phối + các ghế thợ chạy
model rẻ hơn, mỗi ghế ghim sẵn bậc model, có luật giao việc và có thước đo chi phí.

**Vì sao cần:** đo trên dự án thật (NNC Kho, 34.143 lượt gọi, 10.893 điểm quota) — khi mọi ghế chạy
chung một model mạnh, **77% quota cháy ở subagent**. Ghim bậc cho từng ghế kéo xuống **56%**. Phần
còn lại là ghế Tech Lead bị gọi như thợ: **Opus tốn 0,464 điểm/lượt, Sonnet 0,069 — chênh 6,7 lần**.
Skill này gói cả cơ cấu lẫn cái phanh.

## Năm vai — nhớ VAI, không nhớ tên model

| Vai | Làm gì | Không làm gì |
|---|---|---|
| **R0 Quản đốc** (phiên chính) | nhận goal · cắt lô · viết đề bài · giữ cổng · báo cáo | không gõ code (sửa 1–2 dòng thì làm) |
| **R1 Tech Lead** (cửa sổ riêng) | đề bài kỹ thuật lô khó · dựng lô khó nhất · gỡ bế tắc · review kiến trúc cuối sóng | không đổi phạm vi lô, không làm việc thợ làm được |
| **R1b Nghiên cứu** | đo khả thi · khảo sát phương án kèm đánh đổi · kiểm kê nguồn dữ liệu thật — **dọn bàn cho R1** | không quyết kiến trúc, không sửa mã sản phẩm, không bịa số |
| **R2 Kỹ sư/QA/BA** (nhiều ghế) | gõ code · soi lỗi · chạy test · đọc tài liệu nghiệp vụ | không đổi đề bài — kẹt thì báo lên |
| **R3 Cơ khí** | tra cứu · chạy suite/seed · dò mã nguồn | không quyết gì |

Model nào ứng với vai nào **tuỳ gói, và gói đổi theo thời điểm** — nên skill cài sẵn **toggle**:
`python cong-cu/doi-bac.py fable|opus|sonnet` đổi cả xưởng trong một lệnh và ghi ra
`.claude/BAC-DANG-DUNG.md`. Chi tiết + số đo ở `references/1-bac-model.md`. Đây là chỗ tránh trừ tiền
ngoài gói: **ghim nhầm model gói không có là phát sinh phí không kiểm soát**.

## Quy trình INIT (chạy khi được gọi lần đầu trong một repo)

**Bước 1 — hỏi đúng 5 câu, không đoán:**
1. Repo này làm gì, ai là người dùng cuối? (một câu)
2. **Gói Claude đang dùng:** trong bảng chọn model của bạn, model cao nhất là gì — có **Fable** không?
3. Tài liệu nguồn (spec/PRD) nằm ở đâu — cùng repo hay repo khác? (đường dẫn tuyệt đối)
4. Bốn chỗ nào **agent không được tự quyết** ở dự án này? (mặc định gợi ý ở `mau/CO-CAU-NHAN-SU.md`)
5. Dự án có test suite / lệnh kiểm chưa? Lệnh gì?

**Bước 2 — chọn hồ sơ bậc model** theo câu 2 (`references/1-bac-model.md` có bảng ba hồ sơ):
`fable` (gói có Fable) · `opus` (không Fable, Opus cao nhất) · `sonnet` (gói 20$ / Opus eo hẹp).
Chép `references/doi-bac.py` vào `cong-cu/` rồi chạy `python cong-cu/doi-bac.py <hồ sơ>` — nó ghim
`.claude/settings.json` + mọi ghế + sinh `.claude/BAC-DANG-DUNG.md` trong một lệnh.
**Chỉ ghim model gói THẬT SỰ có** — và mọi tài liệu trỏ vào `BAC-DANG-DUNG.md`, đừng viết tên model
vào văn bản: gói bật/tắt theo thời điểm, đổi hồ sơ phải là một lệnh chứ không phải sửa 9 file.

**Bước 3 — dựng khung** từ `mau/`, thay chỗ `{{...}}`:
```
.claude/settings.json      ghim model cho phiên chính (R0)
.claude/agents/*.md        các ghế, mỗi ghế một dòng model:
.claude/CO-CAU-NHAN-SU.md  luật đội: 4 chỗ dừng · luật nâng-hạ · vệ sinh context
CLAUDE.md                  vai + guardrail + đường dẫn tài liệu (ngắn, đọc mỗi phiên)
workspace/TRANG-THAI.md    bộ nhớ giữa các phiên (chỉ R0 ghi)
workspace/quyet-dinh.md    nhật ký quyết định đảo được
cong-cu/do-quota.py        thước đo chi phí
cong-cu/doi-bac.py         toggle đổi bậc cả xưởng một lệnh
.claude/BAC-DANG-DUNG.md   bậc đang dùng (sinh tự động — tài liệu trỏ vào đây)
```
Chỉ tạo ghế **thật sự cần** — dự án nhỏ có thể chỉ cần R0 + `tho-dung` + một ghế soi.

**Bước 4 — chốt số nền:** chạy `python cong-cu/do-quota.py`, ghi con số vào TRANG-THAI làm mốc so sánh.

**Bước 5 — bàn giao:** in ra cho người dùng ① bảng ghế + model đã ghim ② lệnh kích hoạt goal mẫu
③ mốc quota nền ④ bốn chỗ dừng của họ.

## Quy trình mỗi ĐỢT (sau khi đã init)

`INIT-<đợt>.md` (người chọn cấu hình) → `GOAL-<đợt>.md` (lệnh hành quân cho R0) → R0 cắt lô → mỗi lô:
đề bài → thợ dựng → **hai ghế soi** → vá → ghế thử → commit+push → cập nhật TRANG-THAI.
Mẫu ở `mau/INIT.md` và `mau/GOAL.md`.

**Van đo giữa đường:** đóng lô đầu tiên là chạy `do-quota.py` ngay, so với mốc nền. Vượt ngưỡng thì
**dừng tìm chỗ rò**, đừng đợi cuối sóng.

## Tám luật tiết kiệm token (đã đo, không phải cảm giác)

Chi tiết + số liệu ở `references/3-luat-tiet-kiem.md`. Tóm tắt:

1. **Ghim bậc trong file ghế**, không chỉnh tay mỗi phiên — cấu hình đi theo git.
2. **R0/R1 tiêu token vào ĐỀ BÀI, không vào lao động.** Đề bài mơ hồ ném xuống thợ rẻ là mua lại chính cái sai định tiết kiệm.
3. **Đừng để R0 tự nghiên cứu trong phiên chính** — giao ghế `nghien-cuu`: cùng việc đó rẻ hơn **15,4 lần** (1,088 → 0,070 điểm/lượt) và không nhiễm ngữ cảnh quản đốc.
4. **Gọi R1 đúng bốn việc đã khai.** Đây là chỗ rò lớn nhất còn lại: R1 chiếm **78,6% chi phí subagent** ở dự án mẫu.
5. **Mỗi sóng lớn = một phiên mới.** Context dài là trả tiền lại cho cả lịch sử ở MỖI lượt.
6. **Subagent trả tóm tắt có trần** (≤40 dòng + đường dẫn), không dán nguyên file/log.
7. **R0 không tự đọc file dài** — giao ghế dò đường; cửa sổ subagent chết cùng subagent.
8. **Đo, đừng tin.** Mỗi sóng chạy lại `do-quota.py`; số nói, không ai phải tin ai.

## Đọc thêm khi cần

- `references/1-bac-model.md` — hồ sơ bậc model theo gói (có Fable / không Fable), cách dò an toàn
- `references/2-khung-ghe.md` — mô tả 8 ghế, khi nào gọi, khi nào bỏ bớt
- `references/3-luat-tiet-kiem.md` — bằng chứng đo được + bảy luật đầy đủ
- `mau/` — bộ mẫu điền chỗ trống
