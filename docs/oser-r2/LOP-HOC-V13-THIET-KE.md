# Lớp học NNC v0.13 — một bục giảng, giáo án dựng sẵn, thầy dẫn từng bước

Đầu vào: buổi thử 0.12.1 với 2 người (lỗi L09–L20 trong checklist). Phương án đã duyệt: bốn trụ — A. bục giảng là phòng học duy nhất · B. Thiết lập · C. giáo án dựng sẵn và sư phạm · D. thầy tự dẫn từng bước. Chỉ một bục giảng (dải trên ô nhập); không mở khung riêng.

## 0. Findings this release answers

| Code | Learners saw | Root cause in 0.12.1 |
|---|---|---|
| L09 | had to scroll the podium; some questions outside it | one band, no height budget; choices below headline, board (up to 340 px), fact chips; native question box still used |
| L10 | language and address asked mid-lesson; no free-text name | the teacher asked and wrote state; the mod had no settings screen |
| L12, L19 | entered class and did not know what to do; did not know how to use the podium itself | nobody explains how the class works; first real task after 9 cards; no tour of the tools; setup steps checked as "clicked", not "understood" |
| L13 | the teacher waits for typing | the mod creates a turn only on clock cues; no "step done" signal; first silence step speaks more text |
| L15 | the first lesson is improvised at entry | the lesson plan is guidance for the teacher, not data the podium can show |
| L16 | thinking and tool rows scattered in the chat | only the transcript rows were framed; the podium did not show what the teacher is doing |
| L17 | marked screenshot unclear | the whole Claude window is shrunk to 420×340 |
| L18 | light theme: poor contrast | fixed dark colours against host-drawn buttons |
| L20 | teacher talk not engaging | no voice rules beyond brevity |
| L14 | — | about 12 rules contradict across SKILL, buoi-1, tuong-tac, nang-luc |

## 1. Built-in lesson plan (single source: `plugins/lop-hoc/hooks/giao-an.ts`)

The first work loop is **data shipped in the mod**: the podium shows step 0 the moment the learner presses **Vào lớp**, before the teacher's first word. The Skill's `references/giao-an-vong-1.md` carries the same ids and titles (a contract test compares them) plus what the teacher says and checks.

| id | Title (vi) | The learner does | Why (shown as "để …") | Understanding check |
|---|---|---|---|---|
| `0` | Tham quan lớp học | presses the parts of the podium and the Claude window one by one: ô nhập, chế độ quyền, nút Gợi ý, nút Xong | biết dùng chính công cụ | "Bí thì bấm nút nào?" |
| `1` | Học ở đây thế nào | reads the 3 boxes, presses *Hiểu rồi* | biết vai của mình | — |
| `2` | Việc đầu tiên | ▶ lets Claude read the sample order table | thấy Claude làm việc thật | "Claude vừa đếm được mấy kênh?" |
| `3` | Chế độ Auto | switches to Auto following the zoomed picture | Claude làm mà không hỏi từng việc nhỏ | "Auto giúp gì?" |
| `4` | Tự kiểm | compares 3 rows with the source table | biết kết quả nào tin được | "Khớp hay lệch?" |
| `5` | Giao việc 4 ý | fills the Giao việc form, presses Enter | tự giao việc cho Claude | teacher grades the 4 parts |
| `6` | Việc của tôi | picks one real job (a copy) or next week's sample | dùng được ngay hôm sau | self-check of the result |
| `7` | Chốt vòng việc | 2 recall answers, picks the next job | nhớ lâu, quay lại đúng chỗ | — |

Each step has, in vi and lo: `title`, `why`, three hint levels (`hints[0..2]`: remind the goal · show the place · teacher demonstrates), and an optional `check` question with 2–3 options and the index of the right one. Loops after the first use the same podium with the teacher's own steps (`state.step.title` overrides).

## 2. Mod (`lop-hoc` 0.13.0)

### 2.1 Settings screen (B)
- Shown instead of the old entry screen until the learner presses **Vào lớp**; reopened from **⋯ → Thiết lập** at any time.
- Rows: **Ngôn ngữ** (Tiếng Việt · ພາສາລາວ) · **Gọi tôi là** (Anh · Chị · Em · Bạn · free-text Input, ≤ 30 characters) · **Giáo viên** (Thầy · Cô) · primary **Vào lớp** (entry) or **Lưu** (reopened).
- **One language for the whole podium:** the language row comes first, each option written in its own language (Tiếng Việt · ພາສາລາວ); once chosen, every label switches and no bilingual line is shown anywhere.
- Saved in `$.store` (`language`, `address`, `teacher`) and applied at once to every label. The learner's choice wins over `state.language` / `state.address`.
- Cues: entry `[Giáo án] Mở lớp · giáo viên {thay|co} · ngôn ngữ {vi|lo} · gọi “{address}” · chế độ … · model … · hạn mức …`; reopened and saved `[Giáo án] Thiết lập · ngôn ngữ {vi|lo} · gọi “{address}” · giáo viên {thay|co}`.

### 2.2 One podium in three tiers (A)
Top to bottom, every state:
1. **Tier 1 — now.** While the teacher works: the **speech bubble** (2.4) on the first row. Otherwise the step card: `Bước k/N · title` · `để why` · the step's action (one-touch ▶ or the teacher's choices) · **Xong** · **Chưa được** · **Gợi ý**. Choices and one-touch always render here, never lower.
2. **Tier 2 — one picture.** The teacher's `board` (lines, svg or shot). Height caps: svg 180, shot 260. When tier 1 has choices or a one-touch, the picture collapses to a **Xem hình** button (toggle).
3. **Tier 3 — map and quiet buttons.** The step rail (N dots: done · current · ahead) and **Giơ tay · Xin phép · ⋯**. `⋯` opens: Thiết lập · Xin nghỉ · Phiếu kết quả · Claude của tôi (usage panel) · Soạn tin nhờ hỗ trợ (only when help is needed, then also in tier 1).
- Removed from the main podium: fact chips row, destination row, result-parts row (result parts move under ⋯ → Tiến độ).
- Budget: the tree stays within `maxRows`; if it would not, the picture collapses first, then tier 3 shrinks to the rail and **⋯**.

### 2.3 Step buttons (D)
- **Xong** → `[Giáo án] Xong · bước {id} · {title}`. **Chưa được** → `[Giáo án] Chưa được · bước {id} · {title}`.
- **Gợi ý** cycles 1 → 2 → 3 per step (reset when the step changes):
  - nấc 1 is local: the podium shows `hints[0]` in tier 1 at once, no cue, no tokens;
  - nấc 2 and 3 send `[Giáo án] Gợi ý · bước {id} · nấc {2|3}` (the teacher shows the place, then demonstrates).
- The current step: `state.step.id` (teacher writes it); after **Vào lớp** with no state yet, step `0`.

### 2.4 Speech bubble (A)
From the turn stream: thinking → *Thầy đang nghĩ cách làm…*; text → *Thầy đang nói với bạn…*; tool by kind → *Thầy đang đọc file… · đang ghi file… · đang chạy một lệnh… · đang tra cứu… · đang làm việc…* (vi and lo; ຄູ in Lao). Cleared when the turn ends. It replaces the old "đang giảng — xem bên trên" headline.

### 2.5 Silence (D)
After the teacher's turn ends and the learner has not acted:
- 45 s: **podium nudge**, local, no cue: tier 1 shows a yellow line *"👉 Làm xong thì bấm Xong — chưa biết làm thì bấm Gợi ý"*.
- 2 min: `Học viên im lặng · nấc 1`; 3.5 min: `nấc 2`; 5 min: `nấc 3` (save the place and stop). Same gates as 0.12 (no cue while paused, working, typing).

### 2.6 Light and dark (A)
`$.config.list()` row `theme` is read at session start and every 30 s. A value containing `light` selects the light palette (board `#EAF4EC`, ink `#14301B`, dim `#3F6A4A`, accent `#006D11`, frame `#008816`); otherwise the dark palette of 0.12. Unreadable → dark.

### 2.7 Native question box
The teacher no longer uses it (Skill rule). The mod keeps the 0.12 frame for a box that still appears.

## 3. Teacher (Skill 0.13.0)

- **Opening:** the podium already holds language, address and teacher (cue `Mở lớp`). Never ask them. Introduce yourself in ≤ 3 lines calling the learner by the chosen address, then step 0.
- **Step loop:** write `step`, the picture (`board`), the action (`one_touch` or `choices`) in one `Write`; say ≤ 3 lines: what, why, which button. On `Xong`: if the step has a check, ask it as podium `choices`; right → one line of specific praise and the next step at once; wrong → explain another way (example → picture → demonstrate), check again. On `Chưa được` → go straight to nấc 2. On `Gợi ý · nấc 2` → show the place (zoomed screenshot or mock-up); `nấc 3` → do it with them (fill the one-touch, say each click).
- **Tour (step 0) and "how we learn" (step 1)** come first; concepts are named inside the steps that need them, not before.
- **No native question box**, no time talk, no roll call, no read-back of values: the learner clicks and the podium reports.
- **Voice:** call the learner by name or address, ask before telling, one example from NNC work (đơn hàng, phiếu nhập kho, bảng doanh số theo kênh OTC/HC/SPM), praise the exact act, one light touch of humour per loop, emotion on the podium; ≤ 3 short lines per message.
- **Screenshot:** `danh-dau.ps1` crops a region around the target, enlarges it (≤ 560 px wide), draws the ring, number and arrow, and adds a small map of the whole window with the region outlined.

## 4. Versions

`lop-hoc` 0.13.0 · Skill 0.13.0 · `nnc` `5.1.0-alpha.2+lophoc.0.13.0` (never alpha.3) · tag `lop-hoc-v0.13.0` after review.
