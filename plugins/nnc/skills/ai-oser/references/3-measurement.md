# Measurement — ledger · metric · tài nguyên

## Nguồn dữ liệu

1. **Transcript thô** (`~/.claude/projects/<slug>/`): mỗi lượt assistant có `model`, `effort`, usage
   (`input · output · thinking · cache_read · cache_creation`), `sessionId`, `isSidechain`, `agentId` (subagent),
   `timestamp`, `gitBranch`. Danh tính một lượt chạy = `(sessionId, agentId)`.
2. **Ledger** (`.claude/oser/ledger/ledger.jsonl`, PROJECT-OWNED, chỉ ghi thêm qua `oser ledger add`): sự kiện
   `wave_open · packet_open · attempt · packet_state · wave_state · defect · root_handoff · quota_reading`.
   Không prompt, không dữ liệu khách, không lập luận của worker — chỉ id, trạng thái, danh tính lượt chạy, đếm, ref.

Usage được **nối** từ transcript theo danh tính lượt chạy (tuỳ chọn cửa sổ `from/to` khi nhiều lượt chung phiên).

## Đơn vị

`work = input + cache_creation + output` (thinking nằm trong output) — dùng cho mọi tỉ số; `cache_read` báo
riêng. `prompt_size = input + cache_read + cache_creation` của một lượt = context model nhận ở lượt đó (proxy
context Root). Trọng số giá API chỉ là **tham chiếu tuỳ chọn** (`oser quota --api-reference`, bảng có tên
phiên bản), không bao giờ là chi phí thuê bao hay kinh tế lập lịch.

## Metric (`oser metrics`)

| Metric | Định nghĩa |
|---|---|
| **VERIFIED_RESULT_COST** | work của mọi lượt (mọi vai) từ khi mở packet tới khi `FABLE_ACCEPTED`; mức wave = + governor |
| **FIRST_PASS_ACCEPT_RATE** | packet được nhận với đúng một lượt implement và lượt đó `pass` / packet đã kết |
| **REWORK_AMPLIFICATION** | work mọi lượt / work lượt implement đầu tiên |
| **ROOT_CONTEXT_GROWTH** | prompt_size Root lúc `ROOT_ACCEPTED` − lúc `wave_open`, trung bình theo wave; kèm số `root_handoff` |
| **CONTEXT_ISOLATION_GAIN** | (work + cache_read) dưới Root / tăng trưởng context Root (dự phòng: `clean_result_chars/4`) |
| **DEFECT_CONTAINMENT** | lỗi verifier + sự kiện `before_integration` / (trước + `after_acceptance`) |
| **FABLE_LEVERAGE** | packet được nhận / triệu work token của model họ Fable **đo được** (không theo plan khai) |
| **ESCALATION_EFFICIENCY** | packet có lượt `escalate`: tỉ lệ cuối cùng được nhận + work trung bình |
| **PLAN BENCHMARK** | theo `(model, effort)` và `(taskClass, model, effort)`: lượt · first-pass · rework · lỗi verifier · work · thinking · prompt TB · wall · kết quả cuối được nhận · lệch model khai/quan sát |

Cái không thấy được ghi vào `unknown` — không bịa.

## Tài nguyên thuê bao

`oser quota` cho usage thô theo model · effort · vùng (root/subagent) · tuần ISO, tách **tất cả model** và
**Fable (lồng bên trong)** + tỉ trọng Fable. Cap tuần (tổng và Fable) **chỉ có trên UI** — không suy từ token.
Ghi số đọc UI bằng `quota_reading` (`weekly_all_models_pct`, `weekly_fable_pct`, `source: "ui"`); khi đủ
cặp số đọc, quy đổi token ↔ % mới có bằng chứng.

## Bằng chứng đời trước (tham khảo)

Pilot 1.x (21/08→09/09/2026): lượt ở phiên chính đắt ~5,3× lượt subagent vì độ dài context; subagent chạy
nhầm cấp ăn 77 % quota trước khi phân cấp; Workflow `agent()` kế thừa model phiên chính nếu không ghi model
(một ngày: 34 % quota). Đó là lý do tồn tại của context isolation và của `plan.model` bắt buộc ở mỗi lượt.
