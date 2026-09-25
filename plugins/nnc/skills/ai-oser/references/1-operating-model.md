# Operating model — Root · Governor · packet

Catalog máy đọc: `oser/catalog/operating-model.json`. File này giải thích; catalog là chủ.

## Cấp bậc điều khiển (không phải cấp bậc model)

```
Founder + Strategy Session
        │   quyết WHAT/WHY · RED · deploy/billing
        ▼
Root  ── trạng thái toàn cục · con trỏ authority/kiến trúc · work graph · admit milestone/wave
        │   tích hợp KẾT QUẢ SẠCH · xung đột giữa wave · gói quyết định cho Founder · tự xoay context
        ▼
Governor (slot cố định · 1 phiên mới / wave) ── chia packet · đồ thị phụ thuộc · song song · execution plan từng lượt
        │   yêu cầu verification · retry · escalation · từ chối · gom bằng chứng → đóng phiên
        ▼
Phiên thực thi mới (worker)  ──►  Verifier độc lập  ──►  kết quả wave sạch  ──►  Root
```

- **Root** không làm packet thường, không đọc log thô của worker, không giữ lập luận của worker, không lập
  lịch từng thao tác, không thành "monolith gõ code" sống lâu. Độ phức tạp thô ở dưới; sự thật đã kiểm đi lên.
- **Governor** là một **slot cố định**: đúng một Governor cho mỗi wave, sở hữu wave đó; không làm Root, không mang
  context toàn dự án, không thành worker mặc định, không đẩy lựa chọn kỹ thuật lên Founder; đóng/xoay khi wave
  được nhận hoặc bị từ chối.
- **Worker** chạy một lượt thử trong context packet của nó. **Verifier** không bao giờ là tác giả của cái nó kiểm.
- **Họ model của slot Governor là cấu hình profile** (`operating_model.governor.required_family`, `fallback`):
  ví dụ `fable` ở gói có Fable, `opus` ở gói khác. `fallback: "none"` ⇒ lệch họ là **FAIL CLOSED**: ledger từ
  chối `wave_open` với governor khác họ, doctor OSR-104 báo critical khi họ **quan sát được** trong transcript khác
  profile. Plugin không chứa logic giá gói. Root: `expected_family` (khai) + model phiên (quan sát).
  Worker/verifier **không có** model theo vai.
- Root **có thể** tự điều tra kỹ thuật khi một vấn đề toàn cục/giữa wave cần; không phải builder mặc định.
  Nguyên tắc: **độ phức tạp thô đi xuống, sự thật đã kiểm đi lên.**

## Vòng đời

| Đối tượng | Trạng thái | Luật |
|---|---|---|
| Packet | `ASSIGNED → EXECUTED → MACHINE_VERIFIED → [INDEPENDENT_REVIEWED] → GOVERNOR_ACCEPTED` · `REJECTED` bất cứ lúc | worker done ≠ packet done; độ sâu `independent_review`/`independent_solution` bắt buộc có `INDEPENDENT_REVIEWED` trước khi nhận |
| Wave | `OPEN → PACKETS_ACCEPTED → GOVERNOR_CONSOLIDATED → ROOT_REVIEW → ROOT_ACCEPTED` · `ROOT_REJECTED` | chỉ `ROOT_ACCEPTED` đẩy milestone; không nhận khi còn packet chưa kết |

`oser ledger add` từ chối sự kiện sai thứ tự; `oser doctor` (OSR-102) báo ledger hỏng.

## Machine-first

Trước khi cấp một worker LLM, governor xét: script tất định · phân tích tĩnh · test runner · grep/index ·
emulator · công cụ chẩn đoán có sẵn. LLM diễn giải và quyết; máy đo và kiểm. Mỗi `packet_open` ghi
`machine_first.considered` (OSR-102 cảnh báo khi thiếu).

## Context economy

Mỗi packet khai `context`: **must_read** · **may_read** · **must_not_load** · **output_budget**. Không chuyển:
transcript Root, file authority không liên quan, cây mã không liên quan, workspace lịch sử, đầu ra của mọi
worker trước. Worker trả bằng chứng có trần: kết quả · commit/file · test · quyết định · rủi ro · việc còn mở ·
đường dẫn bằng chứng. Log thô nằm trên đĩa.

## Xoay Root (rotation)

Root sống lâu **về logic**, không nhất thiết một cuộc hội thoại vật lý. Khi context kém hiệu quả:
Root hiện tại ghi trạng thái sạch (file trạng thái sống của dự án + ledger) → sự kiện `root_handoff`
(`fromSessionId`, `toSessionId`, `reason`, `stateRefs`) → Root mới chỉ nạp: CLAUDE.md · trạng thái sống ·
entry kiến trúc · wave đang mở trong ledger. Chưa có ngưỡng token cứng — `oser root` cho chuỗi kích thước
prompt của từng phiên Root (đo được) và `oser metrics` cho ROOT_CONTEXT_GROWTH/wave; ngưỡng đặt khi có số.

## Verification

Độ sâu tăng theo blast radius · khả năng đảo ngược · khả năng test · rủi ro bảo mật/dữ liệu · lịch sử lỗi.
`machine` = kiểm máy (test/lint/emulator) đủ; `independent_review` = verifier khác phiên; `independent_solution`
= hai lời giải độc lập đối chiếu.

## Chủ quyền Founder / Engineering — ranh giới cứng

**Founder giải xung đột sản phẩm/nghiệp vụ. AI giải bất định kỹ thuật.** Bất đồng kỹ thuật giữa các agent
**không** phải escalation lên Founder.

- Engineering tự giải: mơ hồ kỹ thuật · phương án hiện thực · schema/query/index · ranh giới module ·
  transaction/batch/listener/cache · retry/backoff · cơ chế migration · chiến lược test · observability ·
  chọn model · chọn effort · context/session · song song · phân bổ worker · độ sâu verification · thứ tự kỹ thuật.
- **Root** quyết và khoá quyết định GREEN/AMBER; **Governor** quyết chi tiết thực thi bên trong wave đã admit.
- Quy trình bắt buộc: xem bằng chứng → so phương án → thử nếu được → chọn winner → ghi rationale → đi tiếp.
- Chỉ lên Founder khi lựa chọn chưa giải **đổi**: nghĩa nghiệp vụ · thẩm quyền actor · ngữ nghĩa
  capability/quyền · nghĩa vòng đời/hoàn thành · hành vi HIFI đã khoá · nghĩa metric sản phẩm · ngữ nghĩa nguồn
  sự thật · phạm vi/chi phí lớn không đảo được · cam kết release/go-live có đánh đổi nghiệp vụ thật.
- **Cloud/deploy HOW thuộc engineering**: topology trong kiến trúc đã khoá · thứ tự deploy · deploy đảo được · cấu hình
  môi trường · thao tác Firebase/cloud thường lệ · migration · rollback · quy trình cutover · giám sát · tối ưu chi phí
  trong ràng buộc đã duyệt. Founder chỉ giữ **hệ quả RED** (cam kết chi phí lớn không đảo được, đổi phạm vi lớn,
  đổi nghĩa sản phẩm, nghiệm thu go-live). **Phê duyệt thực thi ≠ quyền quyết định**: runtime có thể bắt người
  bấm duyệt trước một mutation bên ngoài — ghi `execution_approval_by`, quyết định vẫn là GREEN/AMBER.
- BUILD ADMISSION REVIEW chỉ được đưa lên: quyết định RED · đánh đổi nghiệp vụ lớn không đảo được · nghiệm thu
  go-live/release khi áp dụng. **Không** hỏi Founder chọn phương án kỹ thuật.

Máy kiểm: sự kiện `decision` (zone GREEN/AMBER/RED) — GREEN/AMBER bắt buộc rationale, AMBER bắt buộc
alternatives + winner, cả hai **không** được `escalated_to_founder`; RED bắt buộc `red_basis` thuộc danh sách
trên; governor không quyết RED và chỉ quyết trong wave đang mở. `oser doctor` OSR-103 bắt escalation sai vùng;
`oser metrics` đếm DECISIONS và FOUNDER_ESCALATIONS. Strategy Session cross-check Root ở các lần khoá lớn.

## OSER không bị khoá

OSER là hệ điều hành **có version và thích nghi**: được cấu hình, đồng bộ, đo, và tiến hoá từ bằng chứng BUILD.
Không có "OSER lock", "routing lock" hay "model/effort lock"; khoá thiết kế kỹ thuật cuối cùng trước BUILD là
kiến trúc production của dự án.

## Mode

`setup` (active: Founder + Strategy + Root, cấm subagent) · `build` (**admission-gated**: cần
`build.admission = admitted` — BUILD ADMISSION REVIEW) · `operate` (contract-only).
