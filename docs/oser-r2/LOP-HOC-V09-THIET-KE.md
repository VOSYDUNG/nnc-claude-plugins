# Lớp học NNC v0.9 — kho tài liệu tra cứu linh động · chấm buổi học tự động

Quyết định của người phụ trách (sau 0.8.0): **không đóng gói hình của sách vào Skill.** Tài liệu đào tạo (sách tự học, chương trình, kịch bản, các bộ tài liệu sau này) là **kho tra cứu** mà giáo viên tìm và dùng linh động khi soạn bài; giáo viên **chỉ đúng chỗ bằng cách cho xem ngay**, không bắt học viên đi tìm. Kho lớn dần mà không cần phát hành lại.

Contract between the teacher Skill, the classroom package and the trainer tool. Builds on `LOP-HOC-V08-THIET-KE.md` (unchanged).

## 1. Teaching sources — where the teacher looks

| Order | Source | Where | Always available |
|---|---|---|---|
| 1 | Self-study book (canonical facts, steps, answers) | Skill reference `sach-tu-hoc.md` | yes |
| 2 | Class library folder | `Tai-lieu/` inside the classroom folder: any files the trainer drops there (docx, pdf, xlsx, png, md) | yes (may be empty) |
| 3 | Company document links | `Tai-lieu/NGUON.md`: titles, purpose, links (Drive). Read through the session's connected document tool **only if this session has one**; otherwise use the titles to ask the trainer, never the learner | no |
| 4 | Official product pages | Anthropic support / Claude Code docs (the book's appendix 3 list), fetched only for UI and usage facts that may have changed | needs network |

- `Tai-lieu/README.md` (public, from the repo) explains the folder to the trainer. `Tai-lieu/NGUON.md` holds internal links and is **never in the public repo**: it is injected when the ZIP is built, from the release machine's ignored file `.nguon-tai-lieu.md` (same pattern as `.lien-he-ho-tro.txt`). No file → the package has no `NGUON.md`, and the teacher skips source 3.
- The classroom permission allow-list stays as is; the teacher only **reads** `Tai-lieu/`.

## 2. Research protocol (teacher)

1. **When:** designing a visual or a lesson step; a learner question beyond the cards; a learner's domain needs an example; a UI or usage fact may have changed.
2. **Quiet and short:** at most 3 lookups per turn; one visible line at most (*"Thầy tra sách mục 5 · Hình 10"*); at ≥ 70 % of the 5-hour limit use sources 1–2 only.
3. **Show, don't send searching:** every finding becomes something the learner sees **now** — the exact place drawn (bar mock-up, `podium.point`, a slide that redraws the book figure from its caption), the exact step, the exact example. Never "mở sách mục 5 mà xem" as the answer; the book reference is a small citation line under the visual (*Nguồn: Sách mục 5 · Hình 10*).
4. **Facts:** the book wins for class facts; official pages win for current UI and usage, with the date checked; never state from memory.
5. **Safety:** no customer, cost, debt or salary data from any document into visuals, state or the result sheet; nothing sent out; internal links never shown to the learner.
6. **Record:** `trainer.json` `sources_used: [{ "date", "source": "sach|tai-lieu|nguon|web", "title" }]` — titles only.

## 3. Buổi học checker — `tools/kiem-buoi-hoc.py`

Reads a classroom session transcript (Claude Code JSONL; default: the newest file under `%USERPROFILE%\.claude\projects\<slug of the classroom folder>\`) and writes a Markdown report. Deterministic, no model calls, no network.

Measures: session length; teacher turns; cues received (`[Giáo án] …`) and learner actions (`[Lớp học] …`); **visuals** (lesson-canvas widget calls, artifact publishes, state writes carrying `board` or `podium.point`); **non-native interactions** (state writes carrying `choices`, `[Lớp học] Chọn`/`Trả lời` messages, one-touch submissions); **native boxes** (count, questions per box, longest wait open → answered); **state writes** (count of Write/Edit on `.lop-hoc/`); parts reached (from `segment` writes); `book` written or not; time to first visual and to first non-native interaction; leaks (English stock lines such as "No response requested", internal words `state.json`, `.lop-hoc`, `hook`, `prompt` in teacher text).

Verdict lines against the v0.8 rules: first visual and first interaction within the first two teacher turns; ≥ 1 visual and ≥ 1 non-native interaction per part reached; native boxes ≤ 1 per part outside consent/form; ≤ 1 state write per teacher turn on average; `book` written when a loop closed; no leaks. Output: `PASS`/`FAIL` per rule plus the numbers. Exit code 0 always (it is a report).

## 4. Versions

Skill 0.9.0 · `nnc` `5.1.0-alpha.2+lophoc.0.9.0` (never alpha.3) · `lop-hoc` mod unchanged unless needed · tag `lop-hoc-v0.9.0`.
