# NNC OSER — bản audit hiện hành

12/10/2026 · source repo `VOSYDUNG/nnc-claude-plugins` · baseline `94ddf8b` · patch local `5.1.0-alpha.3`.

**Kết quả:** làm rõ kernel / nghiệp vụ / host-native execution; sửa runtime Formation thiếu nguồn duyệt hướng. Đây là candidate local, chưa push, phát hành hay reload vào phiên plugin đã cài.

## Mục tiêu và phạm vi

Theo yêu cầu CEO: OSER phải nhất quán với tuyên bố chung, không mang cách tổ chức agent Anthropic sang OpenAI bằng suy đoán. [DECLARATION](DECLARATION.md) là điểm vào kiến trúc. [INTEGRATIONS](oser-r1/INTEGRATIONS.md) là ranh giới kỹ thuật và tài liệu hãng; [OPERATIONS](oser-r1/OPERATIONS.md) giữ giao kèo kernel đã có.

Repo local ban đầu sạch ở `9e9f5d8` (4.0); đã fetch và fast-forward lên `94ddf8b` trên origin/main trước audit. Bản 5.1 đã có Mission kernel; giữ phần đó, không dựng scheduler mới hoặc thay provider.

## Thay đổi có bằng chứng

| Vấn đề | Sửa | Giới hạn / acceptance |
|---|---|---|
| Skill có thể bị hiểu là một workflow gọi agent dùng chung | Skill/routing/integration phân biệt kernel durable với native host; không ép roster/wave/model hay AskUserQuestion trên Codex | Tài liệu hãng là nguồn kỹ thuật; khả năng có thật ở phiên là điều kiện thực thi |
| `MISSION_READY` có selected direction nhưng không giữ bằng chứng human đã duyệt hướng | Bắt buộc `direction_approval.approved_by`, `approved_at` có timezone, `decision_ref`; view đưa ra các trường đó | Attestation do caller cung cấp; không xác thực chữ ký, không cấp quyền deploy, không `init` Mission |
| Hướng dẫn toàn tổ chức Claude dễ bị áp qua Codex/R2 | Thêm scope Claude và legacy-v4, dẫn migration/integration hiện hành | Không chỉnh global settings hay tự migrate repo người dùng |
| Chưa có tuyên bố kernel và nghiệp vụ chung gọn | Thêm DECLARATION; README/skills dẫn tới contract đúng | Một report hiện hành; nghiệp vụ giữ nguồn riêng, kernel không sao chép ledger nghiệp vụ |

`MISSION_READY` caller cũ cần thêm evidence duyệt hướng; INTAKE/RESEARCH không cần approval mới. Dùng quyền/duyệt đã có trong session, không hỏi lại chỉ để điền form và không tự tạo approval.

## Đối chiếu hãng

- [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents): custom agents qua `.codex/agents/*.toml`; config theo host và slot thực tế.
- [Codex skills](https://learn.chatgpt.com/docs/build-skills): skill là hướng dẫn/tài nguyên, không là runtime agent scheduler.
- [Claude subagents](https://code.claude.com/docs/en/sub-agents): `.claude/agents/*.md` và cơ chế riêng của Claude Code.
- [Claude teams](https://code.claude.com/docs/en/agent-teams): tính năng experimental riêng, không thay native Codex API.

Các trang đã mở và đối chiếu trong audit. Không coi tương thích schema hoặc test stdlib là live conformance giữa hai host. Desktop, CLI, App Server và Responses/Agents API có bề mặt khác nhau.

## Kiểm chứng và trạng thái

- Baseline: 114 unittest pass. Patch worker: 115 pass. ROOT chạy độc lập full suite sau tích hợp và bump version: 115 pass, 34.685s; kiểm thêm timezone input khi rà patch. Log: `workspace/agents/kernel-audit/root-unittest.log`.
- Cả ba skill qua validator Codex. Field `version` ở hai skill R2 chuyển vào `metadata.version`, giữ giá trị cũ và hợp lệ với frontmatter Codex.
- Frontmatter/relative links đã kiểm tra; không còn link DECLARATION thiếu.
- Native Codex delegation đã sử dụng trong audit này theo tools của phiên; **chưa** chứng minh một Mission cùng acceptance chạy hoàn chỉnh trên cả Claude và Codex.
- Handoff: `workspace/agents/kernel-audit/runtime/handoff.md`, `workspace/agents/kernel-audit/native-docs/handoff.md`.

## Bước tiếp tục

Review patch local và dùng candidate trong phiên thử nghiệm mới khi người dùng muốn cập nhật plugin đã cài. Cần live conformance riêng cho runtime/adapter trước khi gọi production-ready. Câu hỏi nghiệp vụ tiền, ngưỡng và dự án nằm ở repo nghiệp vụ riêng; không sao chép dữ liệu cá nhân vào repo plugin.
