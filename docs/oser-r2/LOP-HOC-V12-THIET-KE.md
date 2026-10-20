# Lớp học NNC v0.12 — bọc kín khung thầy

Yêu cầu của người phụ trách: mọi thứ học viên **nhìn thấy** trong phiên lớp — kể cả dấu hiệu "thầy đang làm việc" (đọc file, chạy lệnh, suy nghĩ) — phải nằm trong khung thầy, không lộ phiên Claude Code mặc định.

## 0. Phát hiện "Tôi chấm lại 3 câu…"

Not an addressing setting and not a teacher message: it was the model's **thinking block** (internal reasoning), which Claude Desktop shows as a thinking summary. It speaks as "Tôi" and sits outside the teacher frame. Fix: the classroom `.claude/settings.json` sets `"showThinkingSummaries": false` (documented setting: "Request API-side thinking summaries and show them in the conversation… Set explicitly to override the default"); the mod also hides/relabels live thinking where the turn stream lets a hook do so.

## 1. Surfaces and their teacher frame (mod `lop-hoc` 0.12.0)

| Surface (render component) | v0.11 | v0.12 |
|---|---|---|
| Teacher text (`AssistantMessage`) | framed (avatar, part label, green border) | unchanged |
| Tool row (`ToolUse`) | teacher line added **above** the default row | **teacher activity row replaces it**: small avatar + *"Thầy đang đọc phiếu…"* (running) / *"Thầy vừa đọc phiếu"* (done) / *"Thầy gặp trục trặc, đang xử lý"* (error); the default row only behind a toggle *"Xem chi tiết"*; ledger rows stay one dim line |
| Tool group (`ToolGroup`) | default count line (*"Read a file, ran a command, edited 2 files"*) | **one teacher line** counting by kind in the learner's language (*"Thầy vừa: đọc 1 file · tạo 2 file · chạy 1 lệnh"*), toggle to expand into rows |
| Tool result (`ToolResult`) | default output block | **collapsed by default**: *"Kết quả · xem"*; errors *"Có lỗi — thầy đang xử lý · xem"* |
| Question box (`AskUserQuestion`) | header line only | **full frame**: border + avatar + header around the engine dialog |
| Slash command output (`CommandOutput`) | default (*"Reloaded: 31 plugins · 191 skills…"*) | `reload-plugins` → *"Đã nạp lại lớp học ✓"*; other commands → teacher-framed, original behind a toggle |
| Live thinking (turn stream) | shown as the model wrote it | hidden or *"Thầy đang suy nghĩ…"* where a hook can change it; otherwise rely on the setting in §0 |
| Spinner, prompt hint, learner messages, cue rows | wrapped / hidden | unchanged |

All new strings in vi and lo. Outside the classroom nothing changes.

## 2. Teacher voice (Skill 0.12.0)

- Self-reference is always **thầy/cô** (vi) or **ຄູ** (lo); never "tôi", "I", "Claude" as the speaker.
- Session-level text the host may show — task-list items, an end-of-turn recap the host asks for, closing lines — in the teacher's voice, learner's language, one short line; never internal words.
- At `Mở lớp`, if the session has a tool to set the session title, set it to *"Lớp học NNC · Thầy"* / *"· Cô"* once.
- Never show raw tool output to the learner; thinking stays internal and is never quoted.

## 3. Package and checker

- `tools/build_lop_hoc_mau.py` settings: add `"showThinkingSummaries": false` (class folder only).
- `tools/kiem-buoi-hoc.py` R12: voice and frame leaks in teacher text — self-reference "tôi"/"Tôi" (as the speaker), English sentences (≥ 5 consecutive Latin words without Vietnamese diacritics outside code/backticks), internal words; report snippets.

## 4. Outside the mod's reach (unchanged, noted)

Permission dialogs (teacher announces them in one line), the Desktop "Outputs" side panel listing `.lop-hoc` files (V1: move ledger writes to the podium), message action icons.

## 5. Versions

`lop-hoc` 0.12.0 · Skill 0.12.0 · `nnc` `5.1.0-alpha.2+lophoc.0.12.0` (never alpha.3) · tag `lop-hoc-v0.12.0` after review.
