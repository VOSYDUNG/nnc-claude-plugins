# GOAL ĐỢT {{N}} — {{TEN_DOT}} (người chủ kích hoạt {{NGAY}})

> Đọc `INIT-DOT-{{N}}.md` trước — tờ chọn cấu hình. Một phiên quản đốc mỗi lúc. **Commit + push sau MỖI lô.**

**Mục tiêu duy nhất:** {{MUC_TIEU_MOT_CAU}}

**Spec neo (nguồn sự thật, không viết lại):** {{DUONG_DAN_SPEC}}

## Chuẩn bị máy trước khi mở phiên — 10 phút

1. `git pull` mọi repo liên quan — cấu hình đội hình đi theo git, KHÔNG chỉnh tay
2. Soát ghim còn nguyên: `.claude/settings.json` + dòng `model:` trong các ghế
3. Chạy `{{LENH_KIEM}}` MỘT lần **trước khi mở phiên** — đỏ vì môi trường thì sửa môi trường trước,
   đừng để ghế R2 ngồi debug máy
4. {{CHUAN_BI_THEM}}

**Van đo giữa đường:** đóng lô đầu là chạy `python cong-cu/do-quota.py`, so mốc **{{MOC_QUOTA}}**.
Vượt ngưỡng = cơ cấu đang rò — DỪNG tìm chỗ rò rồi mới chạy tiếp.

## Thứ tự lô

| Lô | Việc | Nghiệm thu THẤY ĐƯỢC |
|---|---|---|
| {{N}}.1 | | |
| {{N}}.2 | | |

## Sự thật nền — không diễn giải lại
{{SU_THAT_NEN}}
<!-- những gì đã đo/đã chạy: phiên bản đang sống, dữ liệu đã có, thứ đã deploy, cái đã bị bác bỏ -->

## Không làm trong đợt này
{{NGOAI_PHAM_VI}}

## Rà mìn — để goal chạy ĐẾN XONG, không kẹt chờ người chủ
- Vá lỗi trong hành vi spec ≠ đổi phạm vi. Tự vá, tự duyệt.
- **Thang gỡ bế tắc TỰ TRỊ:** ghế R2 sai ×2 → gọi R1 → vẫn kẹt: R0 tự quyết (ghế cao nhất đang trực) →
  vẫn kẹt nữa: ghi TRANG-THAI rồi **nhảy sang lô kế tiếp không phụ thuộc**, gom báo MỘT LẦN cuối sóng.
  **Cấm dừng cả sóng để chờ** — chỉ hai thứ được phép dừng sóng: spec sai chặn mọi lô, hoặc van quota nổ.
- Điểm dừng còn lại là **vật lý, không phải xin phép** (hết môi trường, hết quota) — gặp thì chốt
  TRANG-THAI, báo một dòng, nghỉ. Không phải lỗi.

## Gate "xong đợt"
{{GATE}}
<!-- liệt kê đủ điều kiện, thiếu một là chưa xong -->

**Lệnh kích hoạt (người chủ dán nguyên văn):**
> Chạy đợt {{N}} theo GOAL-DOT-{{N}}.md: lô {{N}}.1 → {{N}}.x. Xong sóng chốt TRANG-THAI, báo cáo và push.
