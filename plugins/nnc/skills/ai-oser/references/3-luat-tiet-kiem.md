# Bảy luật tiết kiệm token — kèm bằng chứng đo được

**Nguồn số:** dự án NNC Kho & Giao nhận, 21/8 → 9/9/2026, đo bằng `do-quota.py` đọc transcript thật.
Tổng **34.143 lượt gọi · 10.893 điểm quota**.

## Bằng chứng nền

| Đo | Số |
|---|---|
| Chi phí mỗi lượt gọi | Haiku **0,010** · Sonnet **0,069** · Opus **0,464** · Fable **0,937** điểm |
| Chênh Opus / Sonnet | **6,7 lần** mỗi lượt |
| Trước khi ghim bậc (GĐ4, 28/8) | 3.934 điểm — **subagent chiếm 77%** vì chạy nhầm bậc |
| Sau khi ghim bậc (9/9) | 10.893 điểm — **subagent 55,8%** |
| Cơ cấu phần subagent hiện tại | **Opus 78,6%** · Sonnet 21,4% · Haiku 0,1% |
| Nếu subagent chạy đúng bậc rẻ | 6.073 → **1.215 điểm (−80%)**, tổng giảm ~45% |

**Đọc số này thế nào:** ghim bậc đã bịt được nửa lỗ (77% → 56%). Nửa còn lại **không phải lỗi model** —
là **thói quen gọi**: ghế Tech Lead bị gọi như một người thợ. Đó là lý do luật 3 tồn tại.

## Bảy luật

**1. Ghim bậc trong file ghế, không chỉnh tay mỗi phiên.** Cấu hình đi theo git; máy khác `git pull`
là nhận đúng đội hình. Chỉnh tay là quên, quên là cháy.

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

**7. Đo, đừng tin.** Đóng lô đầu của mỗi sóng là chạy `do-quota.py`, so mốc nền. Vượt ngưỡng thì dừng
tìm chỗ rò ngay, đừng đợi cuối sóng mới biết.

## Chỗ KHÔNG được tiết kiệm

Số đo chỉ ra chỗ cháy là **bậc model sai và thói quen gọi**, không phải khâu kiểm. Nên:
**không cắt hai ghế soi, không cắt ghế thử, không bỏ đo** để tiết kiệm. Cắt kiểm để tiết kiệm vài
trăm điểm rồi đổi lấy một lô hỏng phải làm lại là lỗ kép.
