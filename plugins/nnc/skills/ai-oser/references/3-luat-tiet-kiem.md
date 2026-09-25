# Bảy luật tiết kiệm token — kèm bằng chứng đo được

> Đo thời NNC-AI-OSer 1.0 (đội 9 ghế). Luật vẫn áp khi một mode có assignment chạy subagent; mode
> `setup` không chạy subagent nên luật 1, 3, 5, 6 chưa áp. Thước đo hiện hành: `oser quota`.

**Nguồn số:** một dự án phân phối đang chạy sản xuất, 21/8 → 9/9/2026, đo bằng `do-quota.py` (nay là `oser quota`) đọc
transcript thật. Tổng **34.626 lượt gọi · 10.999 điểm quota**.

## Bằng chứng nền

| Đo | Số |
|---|---|
| Chi phí mỗi lượt gọi | Haiku **0,010** · Sonnet **0,069** · Opus **0,464** · Fable **0,937** điểm |
| Chênh Opus / Sonnet | **6,7 lần** mỗi lượt |
| Trước khi ghim bậc (28/8) | **subagent chiếm 77%** quota vì chạy nhầm bậc · 0,408 điểm/lượt |
| Sau khi ghim bậc (9/9) | **subagent 55,8%** · **0,133 điểm/lượt — giảm 67%**, nhịp việc tăng ~6× |
| Cơ cấu phần subagent hiện tại | **Opus 78,6%** · Sonnet 21,4% · Haiku 0,1% |
| Nếu subagent chạy đúng bậc rẻ | 6.073 → **1.215 điểm (−80%)**, tổng giảm ~45% |

**Đọc số này thế nào:** ghim bậc đã bịt được nửa lỗ (77% → 56%). Nửa còn lại **không phải lỗi model** —
là **thói quen gọi**: ghế Tech Lead bị gọi như một người thợ. Đó là lý do luật 3 tồn tại.

## Bảy luật

**1. Model class khai trong `project.json`, không chỉnh tay mỗi phiên.** Cấu hình đi theo git; máy khác
`git pull` là nhận đúng mapping. Chỉnh tay là quên, quên là cháy. ROOT thì `inherit` — xem `1-model-policy.md`.

**2. Tầng trên tiêu token vào ĐỀ BÀI, không vào lao động.** Một đề bài lô chặt gồm: file sẽ đụng ·
given/when/then ba nhánh · checklist nghiệm thu · thứ KHÔNG được đụng. Đề bài chặt thì thợ rẻ làm
được. **Cấm ném việc mơ hồ xuống bậc dưới** — mơ hồ là việc của tầng trên gỡ trước.

**3. Gọi Tech Lead đúng bốn việc đã khai.** Đây là chỗ rò lớn nhất còn lại (78,6% chi phí subagent).
Trước khi gọi R1, hỏi: *đề bài này Sonnet làm được không?* Nếu được — viết đề bài chặt hơn, đừng nâng bậc.

**4. Mỗi sóng lớn = một phiên mới.** Phiên gần đầy context thì **mỗi tin nhắn đọc lại cả lịch sử** —
15 giờ dồn một phiên là trả tiền cho 15 giờ đó nhiều lần. `TRANG-THAI.md` là cầu: chốt sổ → đóng
phiên → phiên mới đọc TRANG-THAI là tiếp được.

**5. Subagent trả TÓM TẮT có trần.** ≤40 dòng + đường dẫn file. Ảnh, log, output dài để trên đĩa, trả
đường dẫn. Kết quả đo lặp lại trả PASS/FAIL + riêng chỗ fail, không trả toàn bộ transcript.

**6. R0 không tự đọc file dài.** Giao ghế dò đường. Cửa sổ context của subagent là **cửa sổ riêng,
chết cùng subagent** — chỉ câu trả lời quay về phiên chính. Đây là cách rẻ nhất để "biết mà không nhớ".

**7. Đo, đừng tin.** Đóng lô đầu của mỗi sóng là chạy `oser quota`, so mốc nền. Vượt ngưỡng thì dừng
tìm chỗ rò ngay, đừng đợi cuối sóng mới biết.

## Chỗ KHÔNG được tiết kiệm

Số đo chỉ ra chỗ cháy là **bậc model sai và thói quen gọi**, không phải khâu kiểm. Nên:
**không cắt hai ghế soi, không cắt ghế thử, không bỏ đo** để tiết kiệm. Cắt kiểm để tiết kiệm vài
trăm điểm rồi đổi lấy một lô hỏng phải làm lại là lỗ kép.

## Luật 6 — Workflow phải ghim bậc (đo 14/09/2026)

Ghế `.claude/agents/*.md` chỉ ghim model cho đường **`Agent`**. Đường **`Workflow`** (`agent()` trong script) **kế thừa model của phiên chính**.
Đo trên một dự án đang chạy sản xuất, một ngày: **1.242 / 1.484 lượt Opus** nằm trong ba lần Workflow — **34% quota ngày** — trong khi việc là việc thợ.
**Luật:** mọi `agent(prompt, {model: "claude-sonnet-5", ...})` — bắt buộc ghi `model`; dò đường `claude-haiku-4-5-20251001`. R0 không được để trống.
`do-quota.py` tách cột phiên `wf_*` để bắt lại (cột "vùng": subagent · phiên chính · **workflow**).

## Luật 7 — File trạng thái ≤ 15 KB

File R0 đọc đầu mỗi phiên là **thuế mỗi lượt**. Đo 14/09: `TRANG-THAI.md` 157 KB ≈ 60k token ⇒ R0 **1,46 điểm/lượt**, gấp 3 Opus subagent.
Giữ ≤ 15 KB: mục tiêu đang chạy + 3 mốc gần nhất + đang vướng + chờ Founder. Mốc cũ dời `workspace/lich-su/<khoảng ngày>.md`.
