# Routing — execution plan theo packet

## Đơn vị lập lịch

**WORK PACKET**. Mỗi lượt thử (`attempt`) mang một execution plan:

```
Execution Plan = capability (việc cần làm) × model × effort × mode/session × context × verification (+ fallback/escalation)
```

Ledger bắt buộc `plan.capability · plan.model · plan.effort · plan.mode` ở mỗi lượt thử; họ model được suy từ
model id và đo lại từ transcript.

Model là **phân bổ tài nguyên tính toán**, không phải chức danh. Không có bảng "vai → model" trong plugin
hay trong dự án.

## Mục tiêu

**Kế hoạch VERIFIED tốn ít tài nguyên nhất mà vẫn giữ biên an toàn cần thiết** — tức cực tiểu
`ExpectedTotalResourceToVerifiedResult`: lượt đầu + review + retry + escalation + rework + tích hợp + replay
context + verification. Lượt đầu rẻ mà gây làm lại có thể đắt hơn. Một lượt 0,4 tài nguyên gây làm lại nhiều lần có thể tệ hơn một lượt 0,9 đạt ngay. Không đẩy một packet ra sát mép năng lực
đã quan sát của một kế hoạch khi kế hoạch khác giảm đáng kể rework/blast risk.

## Effort là một chiều lập lịch độc lập

- Tập hợp hợp lệ = đúng tập runtime hỗ trợ: `oser/catalog/runtime.json › efforts` (đo 25/09/2026:
  `low · medium · high · xhigh · max`). Ngoài tập đó ⇒ ledger từ chối.
- **Không** có sàn, trần, mặc định hay cấm theo mức. Không suy trước quan hệ mạnh/yếu giữa các tổ hợp
  (Opus Low vs Sonnet High, Sonnet XHigh vs Opus Medium…); không giả định High/XHigh luôn rẻ hơn về tổng.
- Mọi tổ hợp model × effort mà runtime hỗ trợ đều là **candidate để đo**. `project.json` không được khai
  `effort_policy` (manifest bị từ chối).
- Effort độc lập với cấp bậc: một packet có thể chạy effort cao hơn Root.

## Tín hiệu (bằng chứng, không phải ngưỡng cứng)

`complexity · ambiguity · blast_radius · reversibility · testability · context_load · independence ·
dependency_count · prior_rework · prior_first_pass · prior_verification_defects` — mức `low|medium|high|unknown`, ghi ở `packet_open.signals`; cộng lịch sử
đo được của lớp việc: **first-pass rate** và **rework** theo `(taskClass, model, effort)` và **chi phí
verification** (`oser metrics › PLAN BENCHMARK`). Không có ngưỡng số toàn cục khi chưa có bằng chứng.

Governor được chọn: cùng phiên · phiên mới · nhiều worker song song · model khác · effort khác · lời giải độc
lập · verifier độc lập · đưa lên Root.

## Benchmark

Đơn vị so sánh là **verified result**, không phải một lượt gọi. Với mỗi model × effort, ledger + transcript cho:
first-pass acceptance · rework · lỗi verifier tìm ra · tổng usage · thinking · context (prompt trung bình) ·
wall time · kết quả cuối được nhận. Dữ liệu chính là **các wave BUILD thật** — không dựng benchmark đồ chơi
làm bằng chứng cuối. Khởi đầu **bảo thủ**: mua biên an toàn trước, chỉ hạ kế hoạch khi có bằng chứng lặp lại.

## Tài nguyên

`WEEKLY_ALL_MODELS` với `WEEKLY_FABLE` **lồng bên trong** (Fable có sub-cap riêng nhưng cũng trừ vào tổng).
Fable không phải kho độc lập: dùng ở chỗ tạo đòn bẩy — chia wave, điều phối, lập luận độc lập, gom kết quả,
review giá trị cao, debug khó. Theo dõi cả phần Fable và tổng (`oser quota`, `oser metrics › resources`).
