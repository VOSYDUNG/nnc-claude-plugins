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
Governor (1 phiên mới / wave) ── chia packet · đồ thị phụ thuộc · song song · execution plan từng lượt
        │   yêu cầu verification · retry · escalation · từ chối · gom bằng chứng → đóng phiên
        ▼
Phiên thực thi mới (worker)  ──►  Verifier độc lập  ──►  kết quả wave sạch  ──►  Root
```

- **Root** không làm packet thường, không đọc log thô của worker, không giữ lập luận của worker, không lập
  lịch từng thao tác, không thành "monolith gõ code" sống lâu. Độ phức tạp thô ở dưới; sự thật đã kiểm đi lên.
- **Governor** sở hữu đúng một wave có ranh giới; không làm Root; không mang context toàn dự án; đóng khi trả
  `wave_state ROOT_REVIEW` + kết quả sạch.
- **Worker** chạy một lượt thử trong context packet của nó. **Verifier** không bao giờ là tác giả của cái nó kiểm.
- Model ưu tiên cho Root/Governor là **khai báo của dự án** (`project.json › operating_model`), không phải
  mặc định của plugin. Worker/verifier **không có** model theo vai.

## Vòng đời

| Đối tượng | Trạng thái | Luật |
|---|---|---|
| Packet | `ASSIGNED → EXECUTED → MACHINE_VERIFIED → [INDEPENDENT_REVIEWED] → FABLE_ACCEPTED` · `REJECTED` bất cứ lúc | worker done ≠ packet done; độ sâu `independent_review`/`independent_solution` bắt buộc có `INDEPENDENT_REVIEWED` trước khi nhận |
| Wave | `OPEN → PACKETS_ACCEPTED → FABLE_CONSOLIDATED → ROOT_REVIEW → ROOT_ACCEPTED` · `ROOT_REJECTED` | chỉ `ROOT_ACCEPTED` đẩy milestone; không nhận khi còn packet chưa kết |

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

## RED — chỉ những thứ này lên Founder

Nghĩa nghiệp vụ · thẩm quyền actor · ngữ nghĩa capability/quyền · nghĩa vòng đời/hoàn thành · hành vi HIFI đã
khoá · nghĩa metric sản phẩm · ngữ nghĩa nguồn sự thật · quyết định chi phí/phạm vi/phát hành lớn không đảo
được. Lựa chọn kỹ thuật thường không lên Founder. Strategy Session cross-check Root ở các lần khoá lớn.

## Mode

`setup` (active: Founder + Strategy + Root, cấm subagent) · `build` (**admission-gated**: cần
`build.admission = admitted` — BUILD ADMISSION REVIEW) · `operate` (contract-only).
