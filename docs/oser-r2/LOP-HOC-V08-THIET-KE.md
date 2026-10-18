# Lớp học NNC v0.8 — thiết kế: giáo viên tự chủ về thị giác và tương tác

Nguồn: buổi thử 18/10/2026 (23 phút, 14 hộp câu hỏi gốc, 36 lần ghi trạng thái hiện ra, **0 hình**, học viên kẹt 6 phút tìm Effort trong khi bục đã hiện "effort medium"). Checklist: L08–L23. Quyết định của người phụ trách: L08 chỉ nhắc `/reload-plugins`; bục giảng **không khóa cứng** — giáo viên dựng sân khấu mỗi lượt; tương tác phải có **từ phút đầu**, không chờ đến phần sau; phá thói quen "hỏi rồi chọn" của Claude Code.

This document is the contract between the podium mod (`plugins/lop-hoc`) and the teacher Skill (`plugins/nnc/skills/work-first-learning`). Both must implement exactly these names.

## 1. Visual direction

- Palette (from `art.ts`): green `#008816`, dark green `#006D11`, deep `#0B3B16`, yellow `#FFEA00`, dark yellow `#C9A800`, paper `#FFFDF0`, ink `#1f2a1f`; drive colours D1 `#3CC85A`, D2 `#4A90E2`, D3 `#F5A524`.
- One idea per visual. Big type (title ≥ 20 px in widgets), ≤ 5 short lines, a picture before words. Lao text uses `"Leelawadee UI","Phetsarath OT","Noto Sans Lao",sans-serif`.
- The teacher is the visual author. The podium is a **stage the teacher sets each turn** (size, board, choices, what to point at), not a fixed dashboard. Defaults are quiet: avatar, one teacher line, one primary action.
- Three surfaces, used together:
  1. **Podium** (band above the input): avatar + line + primary action; optional **board** (a small slide: title, ≤ 5 lines, optional SVG); optional **choices** (big buttons, non-blocking); **point** (highlight a real control on screen).
  2. **Lesson canvas in the chat** (the session's built-in visual tool `show_widget`, when present): slides, annotated screen mock-ups, result explainers, interactive checks and games whose buttons send the learner's answer back.
  3. **Artifact** (optional): a keepsake giáo án or a longer illustrated explanation the learner can reopen.
- The real Claude Desktop bottom bar (from the test screenshots): left = permission mode label (e.g. *Bypass permissions*, *Auto*); right = model name (e.g. *Opus 5.5*), effort (*Medium*), and the round usage circle. Folder and "This computer" sit in the session header. Mock-ups must follow this layout.

## 2. State contract additions (`.lop-hoc/state.json`, schema stays `lop-hoc/2`, all fields optional)

```json
"podium": {
  "size": "mini | normal | wide",
  "show": ["mode", "effort", "model", "context", "usage5", "usageWeek"],
  "point": "mode | effort | model | context | usage5 | usageWeek | null",
  "buttons": ["raise-hand", "ask-leave", "leave", "slower", "faster", "hint", "result-sheet", "delegate"]
},
"board": { "title": "…", "lines": ["…"], "svg": "<svg …>…</svg>" },
"choices": {
  "id": "short-id",
  "prompt": "…",
  "options": [{ "label": "…", "send": "…optional text…" }],
  "default": 0,
  "timeout_s": 60
}
```

- `podium.size`: `mini` = one line + primary action; `normal` (default); `wide` = room for the board.
- `podium.show`: which live facts appear on the podium (the mod already knows mode, model, effort, context, usage). Default: none shown.
- `podium.point`: the mod highlights that fact on the podium **and** draws a small picture of the Desktop bottom bar with that area highlighted and an arrow, with one line "ở thanh dưới ô nhập". `null` clears.
- `podium.buttons`: the teacher's chosen secondary buttons. **Giơ tay · Xin phép · Xin nghỉ are always reachable** (in a compact "⋯" group) whatever the teacher picks: the learner can always pause.
- `board`: title ≤ 60 chars, lines ≤ 5 × 90 chars, `svg` ≤ 16 KB; the mod sanitises SVG (no `<script>`, no `<foreignObject>`, no event attributes, no external `href`) and drops it when invalid.
- `choices`: 2–5 options, label ≤ 40 chars. Rendered as large podium buttons; **non-blocking** (the learner can still type). Click → the mod submits `[Lớp học] Chọn · <id> · <label>` (or the option's `send` text when given) as the learner's message and hides the choices locally until the state is rewritten. `timeout_s` (default none; quiz/game 60): when it passes with no click, the mod sends once `[Giáo án] Hết hạn chọn · <id>` and highlights the default; it never clicks for the learner.
- Unknown or invalid fields are ignored (defensive parsing, as today).

## 3. Cues (hidden `[Giáo án]` messages) — new or changed

| Cue | When | Teacher reaction |
|---|---|---|
| `[Giáo án] Mở lớp · giáo viên {thay\|co} · chế độ {label} · model {m} · effort {e} · hạn mức 5 giờ {p}% · tuần {q}%` | class opens (fields optional when unknown) | Never ask the learner for mode, model, effort or usage: you have them. If the mode is Bypass, start with the safety point (below). |
| `[Giáo án] Chế độ quyền · {label}` | the bottom bar's mode label changes (once per change) | Bypass → warm one-liner + `podium.point: "mode"` + a bar mock-up; Auto/Manual → praise in a few words, clear the point |
| `[Giáo án] Hết hạn chọn · {id}` | podium choices timed out | do not wait: change the approach (visual, demo, smaller step); for quiz/game choose the default for the learner kindly |
| `[Giáo án] Hộp chờ lâu · {label}` | a native question box (not quiz/game) stayed open 90 s; while open, the **podium itself** shows the hint "Chưa chắc thì chọn dòng đầu tiên — thầy/cô sẽ chỉ lại bằng hình"; the cue arrives after the box closes (the teacher's turn is blocked meanwhile) | explain visually (`point`, a board or a widget); do not reopen the same box; never answer a box for the learner |
| `[Lớp học] Chọn · {id} · {label}` | learner clicked a podium choice | treat as the learner's own answer |
| `[Lớp học] Trả lời · {id} · {value}` | learner answered inside a lesson widget | treat as the learner's own answer |
| ~~`Kiểm phần học · phần {n} · {m} phút`~~ | **removed** — parts move by milestones (v0.7) | — |

## 4. Mod behaviour (`plugins/lop-hoc`)

1. **Sync (L11):** besides tool-call and turn-end hooks, the clock tick re-reads `state.json` when its raw text changed (compare text; ~1.5 s), so the podium follows every write in time. Remove the per-part minute cue.
2. **Mode (L09):** read the bottom bar's mode labels through the `SessionMode` render component (pass-through `next(e)`, keep `e.modes`); include it in `Mở lớp`; send `Chế độ quyền · …` on change; Bypass → podium warning chip.
3. **Podium stage (L10, L12):** implement `podium.size/show/point/buttons`, `board` and `choices` as in §2; default quiet podium; primary action = one-touch when present.
4. **Tool rows (L18):** rows of tool calls whose input touches `.lop-hoc/` render as nothing (or one dim line "Thầy ghi sổ lớp"), on every surface that raises `ToolUse`/`ToolGroup`.
5. **Long box (L14):** any native question box that is not quiz/game, open 90 s → `Hộp chờ lâu` cue once.
6. **Question box look (L13):** when the surface supports re-rendering `AskUserQuestion`, add the class header (teacher name, part); otherwise leave it native — the Skill makes podium choices the default anyway.
7. All new strings in `i18n.ts` (vi, lo); tests for each behaviour; version `lop-hoc` **0.8.0**.

## 5. Teacher behaviour (Skill `work-first-learning` 0.8.0)

1. **Interaction modes, preferred order:** podium `choices` (non-blocking) → lesson widget with answer buttons → one-touch → native question box **only** for consent/safety, the delegation form, multi-field profile when no podium, or plain chat without the classroom UI.
2. **Never ask what the podium knows** (mode, model, effort, context, usage): show it with `podium.point` + a bar mock-up, ask the learner to *do* (click it), not to *read it back*.
3. **Density from minute one (L20):** every part — including Part 0 — has at least one visual and one interaction that is not a native box; the first visual and the first interactive check come within the first two teacher turns; a learner touch at least every 3 minutes as before.
4. **Visual teaching toolbox** (new reference `day-truc-quan.md`): ready templates the teacher adapts freely — bottom-bar mock-up with highlight, concept slide, result explainer (source beside result, rows to check highlighted), interactive check (buttons → `[Lớp học] Trả lời · …`), 60-second game, podium board SVG. The teacher owns the design: re-author, combine, invent.
5. **Turn rhythm (L18, L21, L22):** observe → choose a move → visual and/or touch → **one** full `Write` of `state.json` per turn → stars / badges / `book` when earned. A per-part playbook card (visual · interaction · game · badge · book sections) replaces hunting through many files.
6. **Scaffold ladder (L19):** not understood → (1) another everyday example → (2) a picture/slide/mock-up → (3) the teacher demonstrates on the machine (one-touch demo) → (4) the teacher does it, the learner watches and marks what they saw; never repeat the same question the same way; 3 failed rungs on the same point → `help_needed` + the support message; energy "Hơi mệt" → fewer checks, more showing.
7. **Results always explained (L17):** after Claude produces a result, show a result explainer (widget or board) before asking anything.
8. **Phrasing (L23):** vary lines; no repeated stock option ("Chưa chắc — thầy nhắc lại" at most once per box set); colour-framed "Làm theo" blocks in widgets for steps on screen.
9. **L08:** if a session in the classroom folder starts with the learner's own message and no `[Giáo án] Mở lớp` cue has arrived, the podium is not loaded: say in one line to type `/reload-plugins` (the only slash command the class ever asks for), then continue in chat.

## 6. Versions

`lop-hoc` 0.8.0 · `nnc` `5.1.0-alpha.2+lophoc.0.8.0` (never alpha.3) · Skill 0.8.0 · tag `lop-hoc-v0.8.0` → `lop-hoc-release`.
