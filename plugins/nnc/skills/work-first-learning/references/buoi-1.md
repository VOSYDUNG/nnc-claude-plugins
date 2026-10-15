# Buổi 1 — executable lesson script (30' standard, 15' and 45' variants)

Source of truth: `docs/oser-r2/LOP-HOC-BUOI-1.md` (design) and `docs/oser-r2/LOP-HOC-V05-CONTRACT.md` (cues, state, agenda). This file turns them into what the teacher does on each cue. Lines to say: [tuong-tac.md](tuong-tac.md) (codes `T01`…). Card texts and quiz items: [the-dinh-nghia.md](the-dinh-nghia.md).

Conventions used below:
- **Box** = one native `AskUserQuestion` call. The **first option is the default** the classroom picks after 60 seconds. `header` ≤ 12 characters. All text in the learner's language (Vietnamese shown; use Lao for a Lao learner).
- **Task list** = Claude Code's native todo/task list (whichever task tool this Claude Code exposes), in the learner's language.
- **State** = `.lop-hoc/state.json`, schema `lop-hoc/2`. Write only the fields listed; keep the others; never touch `clock`.
- "cô" = the chosen teacher; replace with "thầy" when the learner chose thầy. "chị" = the chosen address (anh / chị / bạn).
- Signals for the branch (§P2.7) are kept **in the conversation only**, never written to a file.
- **v0.6 competency layer** ([nang-luc-giao-vien.md](nang-luc-giao-vien.md)): after every learner turn run the teaching loop; never the same interaction kind twice in a row; a learner touch at least every 3 minutes; at least one "À" per part; switch kind on the 4-minute cue. The per-part move plan is §10 below. This script is a **resource**: when an item fails the fit test (job context · level · time left · last kind), re-author it and keep the part's goal and drive.
- **One-touch** = `state.one_touch {label, text}`: the podium shows "▶ {label}", pressing it fills the input, the learner presses Enter. Without the podium, a one-question box whose default option runs the command. Commands are in [tu-kha-nang.md](tu-kha-nang.md); games in [kho-tro-choi.md](kho-tro-choi.md); badges and stars in [huy-hieu.md](huy-hieu.md).
- **Practice folder** = `Thuc-hanh/` inside the classroom folder. Sample files are copied there from the Skill's `assets/mau/` (path from the `Base directory for this skill` line; tu-kha-nang.md §0) before anyone refers to them. Answer keys are never copied. Older wording `Thuc-hanh/` means the same folder.
- **Ladder** (learner autonomy, `trainer.json` `autonomy`): Buổi 1 starts at 2 · Một chạm. The core work step is offered at the learner's level: 2 → a one-touch the teacher filled · 3 → the Giao việc form · 4 → the learner's own words · 5 → the learner drives. Never named to the learner.

## 0. Agenda by duration

| id | Part | 30' | 15' | 45' | Drive |
|---|---|---|---|---|---|
| 0 | Vào lớp | 2 | 2 | 2 | ket-noi |
| 1 | Nhập môn | 7 | 4 | 7 | D2 |
| 2 | Việc thật của tôi | 11 | 7 | 16 | D1 (+D3) |
| — | Nghỉ giữa giờ | — | — | 3 (after part 2) | ket-noi |
| 3 | Thử thách theo nhịp của bạn | 7 | — (dropped) | 14 | D3 / D1 |
| 4 | Tổng kết | 3 | 3 | 3 | ket-noi |

**Task list on `Mở buổi`** (30'), all `pending` except the first `in_progress`:

1. Vào lớp — chào, chọn cách xưng hô (2')
2. Nhập môn — 9 thẻ Claude + vé vào lớp (7')
3. Việc thật của tôi — giao Claude một việc có file và tự kiểm (11')
4. Thử thách theo nhịp của bạn (7')
5. Tổng kết — nhớ lại, bài về nhà (3')

15': drop item 4, minutes 4 / 7. 45': items 3 and 4 become 16' / 14', insert "Nghỉ giữa giờ (3')" after item 3. On each part cue: previous item `completed`, the new one `in_progress`. In part 2 you may add the 7 steps as sub-items (*"Bước 5: Giao việc 4 ý"*) and tick them as they really happen.

## 1. Part 0 — Vào lớp (2', kết nối)

**Cue:** `[Giáo án] Mở buổi · 30 phút · giáo viên co`

1. Read `.lop-hoc/state.json`, `.lop-hoc/trainer.json` and `.lop-hoc/calibration.json` if present (silently). No `bai0_done` → this is Buổi 1. A `bai0_done` → not Buổi 1: open as SKILL §4.4 instead (homework + recall).
2. Task list (§0). State:

```json
{ "schema": "lop-hoc/2", "status": "active",
  "lesson": { "id": "buoi-1", "minutes": 30, "started_at": "<now ISO>" },
  "segment": { "id": "0", "title": "Vào lớp", "drive": "ket-noi" },
  "teacher": { "kind": "co", "name": "", "emotion": "hi" },
  "address": null, "branch": null, "help_needed": false,
  "destination": "Một việc có file đã giao cho Claude và tự kiểm",
  "result_parts": [], "skills": [],
  "next_action": "Chọn cách xưng hô và năng lượng hôm nay",
  "one_touch": null, "activity": null, "challenge": null,
  "stars": 0, "badges_new": [], "gift_box": false, "updated_at": "<now>" }
```

trainer.json: write `autonomy: 2` (no `autonomy_log` entry for the starting level — the log records changes only). Read `.lop-hoc/huy-hieu.json` if it exists.

3. Say (≤ 4 lines): greeting `T01`, the learner's goal and your goal `T03`: *"Mục tiêu hôm nay: chị ra về đã giao Claude làm một việc thật với file và tự kiểm được. Mục tiêu của cô: chị làm được việc đó mà không cần cô làm thay."*
4. **Box** (language question only when the learner's language is not yet known):

```json
{ "questions": [
  { "header": "Ngôn ngữ", "question": "Mình học bằng tiếng nào? / ຮຽນເປັນພາສາຫຍັງ?", "multiSelect": false,
    "options": [ { "label": "Tiếng Việt", "description": "Cô dạy bằng tiếng Việt" },
                 { "label": "ພາສາລາວ", "description": "ຄູສອນເປັນພາສາລາວ" } ] },
  { "header": "Xưng hô", "question": "Cô gọi mình thế nào cho thân?", "multiSelect": false,
    "options": [ { "label": "Bạn", "description": "Cô gọi là bạn" },
                 { "label": "Chị", "description": "Cô gọi là chị" },
                 { "label": "Anh", "description": "Cô gọi là anh" } ] },
  { "header": "Năng lượng", "question": "Hôm nay mình thấy thế nào?", "multiSelect": false,
    "options": [ { "label": "Sẵn sàng", "description": "Học đúng nhịp 30 phút" },
                 { "label": "Hơi mệt", "description": "Cô dạy nhẹ, từng bước ngắn" },
                 { "label": "Đang bận", "description": "Có thể phải Xin phép giữa chừng" } ] } ] }
```

5. After the answers: write `address`; react to energy (`T02`: *Sẵn sàng* → `hi`; *Hơi mệt* → `ai`, shorter chunks for the whole lesson, mention the **Chậm lại một chút** button, no timed challenges today; *Đang bận* → `ai`, mention **Xin phép**).
6. **First real touch — within the first two minutes** (in the same reply as step 5): the first one-touch, on sample data (T36). State:

```json
{ "one_touch": { "label": "Cho Claude đọc bảng đơn hàng",
                 "text": "Chép bảng đơn hàng mẫu của lớp vào thư mục Thuc-hanh, rồi đọc nó và cho tôi biết có mấy kênh bán hàng, mỗi kênh bao nhiêu dòng." },
  "activity": { "kind": "one-touch", "started_at": "<now>" },
  "next_action": "Bấm nút ▶ trên bục rồi nhấn Enter" }
```

   Say (≤ 2 lines): *"Mình bắt tay luôn nhé: bấm nút ▶ trên bục, rồi nhấn Enter — Claude sẽ đọc một bảng đơn hàng mẫu cho chị xem."* Before the permission box (copying into `Thuc-hanh/`): one line, T21. When the learner sends it: create `Thuc-hanh/`, copy `<base>/assets/mau/bang-tinh-mau.xlsx` there, read it, answer in ≤ 3 lines (3 kênh: OTC 14 dòng, HC 13, SPM 13 — from `assets/mau/README.md`), then the **À line** (`hi`): *"40 dòng, vài giây — chị chưa mở Excel lần nào."* Then `one_touch: null`.
   This is a **taste of card 1** on sample data, not practice: the nine-definitions-first rule is untouched. If the part-1 cue arrives before the learner presses Enter, keep the one-touch and open part 1 with one line (*"Bấm thử nút ▶ lúc nào cũng được"*); the read then counts as part 1's first À.
   No classroom UI → a one-question box *"Cho Claude đọc thử một bảng đơn hàng mẫu nhé?"* — **Cho Claude làm (đề xuất)** · Để sau.

## 2. Part 1 — Nhập môn (7', D2)

**Cue:** `[Giáo án] Bắt đầu phần 1 · Nhập môn · 7 phút`. State `segment {id:"1", title:"Nhập môn", drive:"D2"}`, `emotion: "giang"`, `next_action: "Đọc 3 thẻ đầu và bấm Hiểu rồi hoặc Giải thích thêm"`.

**Move plan (v0.6):** `giang` group A → `game:doan-xem` (the part's À) → `giang` group B → `hands-on` group C (the learner reads the podium) → `game:dung-sai` (entry quiz). Never two kinds the same in a row.

**Rule:** nine definitions before any practice. Three groups of three cards; each card ≤ 3 lines (one-sentence definition · everyday example · live number or where to look). Live numbers only if seen in this session; otherwise ask the learner to read the podium (that reading *is* the D2 skill).

| Group | Cards | Live numbers |
|---|---|---|
| A | 1 Claude Code · 2 Thư mục làm việc · 3 Phiên | the real classroom folder path (you know your working directory) |
| B | 4 Model · 5 Effort · 6 Context | your own model name; effort and context % as the learner reads them from the podium or as you were told |
| C | 7 Usage 5 giờ · 8 Usage tuần · 9 Quyền | podium usage card: % used, 5-hour reset time, weekly reset day/time; current permission mode |

After each group, one **Box** with one question per card:

```json
{ "questions": [
  { "header": "Thẻ 1", "question": "Claude Code — làm việc thẳng với file trong thư mục của mình. Rõ chưa?", "multiSelect": false,
    "options": [ { "label": "Hiểu rồi", "description": "Sang thẻ tiếp" },
                 { "label": "Giải thích thêm", "description": "Cô nói lại bằng ví dụ khác" } ] },
  { "header": "Thẻ 2", "question": "...", "multiSelect": false, "options": [ "...same two options..." ] },
  { "header": "Thẻ 3", "question": "...", "multiSelect": false, "options": [ "...same two options..." ] } ] }
```

On *Giải thích thêm*: give the card's second explanation (≤ 2 lines) at the top of the next reply, then present the next group in the same reply. Do not open an extra box for it.

**Between group A and B — Đoán xem (≤ 90 seconds, the part's À):** one box *"Claude vẽ được biểu đồ doanh số theo kênh từ bảng vừa đọc không?"* — **Chưa chắc — thử xem** (default) · Có · Không; then the one-touch of capability card 4 (*Vẽ biểu đồ theo kênh*, tu-kha-nang.md). The learner presses Enter, Claude makes the chart, À line, no star (guessing is not graded). Put group A's *Hiểu rồi* questions in the same box as the guess to save a turn. Learner refuses the game → skip it; the part's À becomes the live number on card 2 (the real folder path shown with `Thuc-hanh/` inside it).

**Group C is hands-on:** the learner finds the numbers on the podium themselves. One question per card in the box: *"Thẻ 7 — chị thấy giờ reset 5 giờ trên bục chưa?"* — **Chưa thấy — cô chỉ giúp** (default) · Thấy rồi; same for card 8 (weekly reset) and card 9 (permission mode).

Group C wording must follow the usage facts in [the-dinh-nghia.md](the-dinh-nghia.md) §Usage: point at the learner's **real reset time** on the podium, say the date the official pages were checked, never claim when the five-hour window starts.

**Entry quiz (vé vào lớp)** — played as **Đúng/sai chuỗi** (`game:dung-sai`, kho-tro-choi.md §7): one **Box**, 3 questions, options exactly as in the card file: the first option is always *"Chưa chắc — cô nhắc lại"* (the 60-second default; it never counts as correct), then three answers with one correct:

1. *"Claude chỉ thấy file ở đâu?"* (card 2)
2. *"Reset tuần của mình là lúc nào?"* (card 8 — correct answer: the time shown on the podium / Settings > Usage)
3. *"Claude hỏi quyền thì mình làm gì?"* (card 9)

Score: right → one line of specific praise (`T09`). Wrong → re-teach that card in ≤ 30 seconds (`T10`), then go in. ≥ 2/3 or not, **into practice within one minute**. Record the score in the conversation for §P2.7. 3/3 → `stars += 1` (T41). Each quiz answer is also a ladder signal at level 1 (two right in a row is not a level change by itself: the learner already starts at 2).

**Write:** trainer.json `concepts` — each of the 9 cards `learned: <date>`; for each quiz answer `recalled_ok += 1` if right; `last: <date>`. Set `bai0_done: <date>` now (so Xin nghỉ after this point does not repeat the introduction). State `skills += {"label": "Nắm 9 điều cơ bản về Claude", "done": true}` when ≥ 2/3.

**`Còn 2 phút phần 1`:** if the quiz has not been given, skip any remaining *Giải thích thêm*, present what is left in one line per card, and give the quiz now (2 questions if needed: cards 2 and 9).

## 3. Part 2 — Việc thật của tôi (11', D1 + D3)

**Cue:** `[Giáo án] Bắt đầu phần 2 · Việc thật của tôi · 11 phút`. State `segment {id:"2", title:"Việc thật của tôi", drive:"D1"}`, `emotion: "nghe"`. **Move plan (v0.6):** (logistics: choose the work) → `quiz` step 4 effort → `demo` cô làm → `one-touch` or `form` em làm (by ladder level) → `game:ban-la-sep` tự kiểm. The part's À: the summary Claude makes **from the learner's own delegation**. Closing line for part 1 (`T22`), e.g. *"Chín thẻ đã có trong túi — giờ mình dùng chúng vào việc thật."*

### P2.1 Choose the work (≈ 1')

Ask the work-first question (SKILL §7.1) as a **Box**:

```json
{ "questions": [ { "header": "Việc hôm nay", "question": "Hôm nay, hôm qua hoặc ca gần nhất, mình có việc nào làm với file hoặc bảng tính không?", "multiSelect": false,
  "options": [ { "label": "Dùng bảng tính mẫu", "description": "File đơn hàng giả của lớp, làm ngay" },
               { "label": "Tôi có file việc thật", "description": "File đã che thông tin khách hàng, nhân sự" },
               { "label": "Tìm trong thư mục của tôi", "description": "Cô xin phép xem tên file gần đây" } ] } ] }
```

- *Dùng bảng tính mẫu* → use `bang-tinh-mau.xlsx` shipped with this Skill in `assets/mau/` (its `README.md` lists columns, answer key and planted errors — for the teacher, not the learner). It is normally already in `Thuc-hanh/` since part 0; if not, copy it there (source path from the `Base directory for this skill` line, tu-kha-nang.md §0; do not guess paths). Not found anywhere → create a small CSV clearly titled **"MẪU GIẢ — dữ liệu luyện tập"** with ~20 fake order rows (kênh OTC/HC/SPM, "Nhà thuốc A — mẫu", "Vitamin C 500mg — mẫu", số lượng, đơn giá).
- **Learner from another trade** (kho, kế toán, hiện trường…) → run the fit test and re-author this part's item (nang-luc-giao-vien.md §5): e.g. a thủ kho gets capability card 7 (receipt photo → table) with the same 7 steps, delegation and self-check.
- *Tôi có file việc thật* → data-safety **Box** before opening: *"File này có tên khách hàng, giá vốn, công nợ hay lương không?"* — **Có hoặc không chắc — dùng mẫu** (default) · **Đã che hết rồi**. Any sensitive content seen later → `T16` (nộ), switch to the sample, `help_needed: true` until the learner continues.
- *Tìm trong thư mục của tôi* → SKILL §7.4 (names and dates only, consent at each step).
- Free text in "Other" describing a task → restate, anchor to the latest occurrence, continue.

### P2.2 Steps 1–4 of the 7-step process (≈ 3')

Name each card as it appears (*"đây là thẻ …"*); each naming is one `used += 1` in the ledger.

1. **Mở đúng chỗ** — already done: *"Mình đang ở Code, một phiên Local — thẻ 3."*
2. **Thư mục làm việc** — `Thuc-hanh/` already exists since part 0: name it now (*"thư mục Thuc-hanh lúc nãy chính là bàn làm việc — thẻ 2"*). Not created yet → create it; before the permission box one line (`T21`) — *"Claude sắp tạo một thư mục trống tên Thuc-hanh, không sửa gì khác — đây chính là thẻ Quyền, chị đọc rồi bấm đồng ý."*
3. **Đưa bản sao vào** — real file: the learner copies it into `Thuc-hanh/` (drag in File Explorer), original stays where it was. Sample: already copied in part 0 (that permission box was card 9 — name it now).
4. **Nhìn bảng điều khiển** — the learner reads model · effort · permission mode · usage from the podium. **Box** (1 question, D2): *"Việc tổng hợp một bảng khoảng 40 dòng nên dùng effort nào?"* — Mức vừa là đủ (default) · Mức cao nhất · Không biết, cô giải thích. Optional if time: the learner changes effort once and sees where it shows.

`result_parts` for the sample: `[{"label":"Đọc file","done":false},{"label":"Giao việc 4 ý","done":false},{"label":"Có bảng tổng hợp","done":false},{"label":"Tự kiểm","done":false}]`; `destination: "Bảng tổng hợp doanh số theo kênh"` (or the learner's own destination in plain words, no file name).

### P2.3 Clarify just enough (≤ 3 questions, usually 1)

Restate → destination → one question with its reason → ready path. For the sample, one **Box**: *"Đầu ra mình cần là gì?"* — Tổng theo kênh OTC/HC/SPM (default) · Tổng theo khách hàng · Lọc dòng thiếu dữ liệu.

### P2.4 Cô làm — think aloud (≈ 1'30'')

Emotion `giang`, `activity.kind: "demo"`. Read the file and say what you do and why (`T06`): *"Cô đọc file: 40 dòng, 9 cột. Cô kiểm trước cột đơn giá có trống không — vì tổng sai thường bắt đầu từ ô trống."* Report columns and row count, and one thing worth checking. Mark `Đọc file` done.

### P2.5 Em làm — the learner delegates (≈ 3')

Offer this step **at the learner's ladder level** (nang-luc-giao-vien.md §1):

- **Level 2 (still at the start):** `activity.kind: "one-touch"`; fill the delegation for them from their P2.3 choice as a one-touch — `{ "label": "Giao việc tổng hợp theo kênh", "text": "Mục tiêu: tổng doanh số theo kênh · Nguồn: Thuc-hanh/bang-tinh-mau.xlsx · Đầu ra: file mới tong-hop-theo-kenh trong Thuc-hanh · Cách kiểm: đối chiếu 3 dòng với file gốc và cộng tay một kênh" }`; say *"Cô điền sẵn 4 ý, chị đọc một lượt — muốn sửa chữ nào cứ sửa — rồi nhấn Enter."* Edited before Enter → the learner wrote part of it: jump to level 3 (T44).
- **Level 3:** `activity.kind: "form"`, `next_action: "Bấm Giao việc, điền 4 ý"`. Show a filled example once (`T07` — "cùng làm"):

> Mục tiêu: tổng doanh số theo kênh · Nguồn: file trong Thuc-hanh · Đầu ra: file mới `tong-hop-theo-kenh` trong Thuc-hanh · Cách kiểm: đối chiếu 3 dòng với file gốc và cộng tay một kênh

- **Level 4–5:** *"Lần này chị tự viết lời giao việc nhé"* — no example; one hint only if asked.

The learner writes their own (levels 3–5) and sends it (`Giao việc — …`). Learner-authored delegation with all 4 parts that ran → badge `giao-viec-dau-tien` (not for an unedited teacher one-touch). Without the podium, use one box with four questions (Mục tiêu · Nguồn · Đầu ra · Cách kiểm), each with a sensible default first and "Other" for typing. Do the work within permissions; one line before each permission box. Output saved with a clear name in `Thuc-hanh/` (step 7 habit). Mark `Giao việc 4 ý` and `Có bảng tổng hợp` done only when they really exist. State `skills += "Tự giao việc bằng 4 ý"`. The result is the part's **À**: *"Chị giao 4 ý, Claude làm ra file — giờ mình làm sếp duyệt nó."*

### P2.6 Tự kiểm (≈ 2') — played as **Bạn là sếp** (`game:ban-la-sep`)

Frame the check as the game (kho-tro-choi.md §6) on the learner's own result: *"Giờ chị là sếp: bảng này ký duyệt được chưa?"* A learner who declines the game gets the plain boxes below with the same content.

**Box:** *"Mình kiểm kết quả thế nào?"* — Đối chiếu 3 dòng với file gốc (default) · Cộng tay một kênh rồi so · Cô gợi ý cách kiểm. Then **Box:** *"Kết quả kiểm?"* — Chưa kiểm xong (default) · Khớp · Có chỗ lệch. Learner checks first; then compare with your own check (sample: `assets/mau/dap-an-mau.xlsx`, sheet *Tổng hợp theo kênh*; never show the answer key before the learner has checked). *Khớp* → `T09` specific praise, `hi`, `Tự kiểm` done, `skills += "Tự kiểm kết quả với nguồn"`; a check really done by the learner → badge `tu-kiem-co-tam` (T40), `stars += 1`. *Có chỗ lệch* → praise the catch (D3 signal), fix together; a real error of Claude's shown against the source → badge `mat-tinh`. Learner accepts the result without checking → `T17` (ố: criticise the method, give the check step). Step 7: say one line "lần sau tiếp từ đâu" and the new-session rule (*việc mới hoặc context đầy → phiên mới*).

### P2.7 Branch point — on `[Giáo án] Còn 2 phút phần 2`

Decide from the signals in the conversation (SKILL §6):

| Branch | Signals |
|---|---|
| `vung` | quiz 3/3 **and** output exists **and** learner self-checked **and** ≤ 1 timeout so far |
| `dang-len` | output exists but not self-checked, **or** quiz 2/3 |
| `can-do` | no output yet, **or** ≥ 2 timeouts |

Conflict → more support. Write `branch`; `can-do` → `help_needed: true`. Say the invitation (`T29`) without any label; for `vung` ask a **Box**: *"Mình làm nhanh quá — thử thêm một thử thách nhé?"* — Thử thử thách (default) · Làm chắc phần vừa rồi (→ treat as `dang-len`). Also steer to finish the current step (`T23`).

## 4. Part 3 — Thử thách theo nhịp của bạn (7', D3 / D1)

**Cue:** `[Giáo án] Bắt đầu phần 3 · Thử thách theo nhịp của bạn · 7 phút`. State `segment {id:"3", ..., drive:"D3"}` (`can-do` → `drive: "D1"`). New `result_parts` for the challenge (2–3 parts).

### `vung` — đóng gói thành Skill nháp

Move plan: `giang` card 10 → `demo` draft → `hands-on` the learner edits one thing → `one-touch` run it on next week's file (the part's À, capability card 9) → if time, `game:doi-vai` (the learner explains the Skill to a "new colleague").

1. Card 10 **Skill** (from the card file, ≤ 3 lines; `learned` today).
2. Cô làm: draft a Skill in the classroom folder (`.claude/skills/tong-hop-theo-kenh/SKILL.md`) holding the 4 parts the learner wrote; one line before the permission box.
3. Em làm: the learner reads it and changes one thing (box: Giữ nguyên (default) · Sửa cách kiểm · Sửa đầu ra).
4. Run it on another file (`bang-tinh-mau-tuan-sau.xlsx` copied into `Thuc-hanh/`) as a **one-touch** (`"Làm theo Skill nháp tong-hop-theo-kenh trên file Thuc-hanh/bang-tinh-mau-tuan-sau.xlsx."`). À: *"Lần sau chỉ cần gọi tên là Claude làm đúng như hôm nay."* If the new Skill is not available in this session yet, follow its steps manually and say it will be ready in a new session. Out of time → show the class's checked sample Skill `assets/skill-mau/tong-hop-don-hang/SKILL.md` and compare it with the learner's draft.
5. `skills += "Đóng gói việc lặp lại thành Skill nháp"`. Homework will use this Skill. Draft holds the 4 parts, the learner changed or approved one point, and it ran once with a check → badge `dong-goi-skill-dau-tien`.

### `dang-len` — đầu vào đổi

Move plan: `one-touch`/`form` re-delegation (by level) → `game:thu-thach-60s` find the differences → `hands-on` mark "Cần kiểm" and check. The part's À: Claude points at exactly the rows to ask about, without inventing a price.

1. *"File tuần sau đổi khác — chuyện rất hay gặp."* Copy `assets/mau/bang-tinh-mau-tuan-sau.xlsx` (planted: a renamed price column, 3 rows missing price, one duplicated row, one row in a different unit — see `assets/mau/README.md`) into `Thuc-hanh/`.
2. The learner re-delegates the same task. Then the **Thử thách 60 giây** (kho-tro-choi.md §3): `challenge {title:"Tìm chỗ khác của file tuần sau", seconds:60}` and the one-touch *Tôi xong rồi*; **no box while the clock runs**. On the learner's Enter or `Hết giờ thử thách`: **Box** (`multiSelect: true`): *"Mình thấy file này khác gì?"* — Chưa thấy, cô gợi ý (first) · Cột đổi tên · Dòng thiếu giá · Dòng trùng hoặc đơn vị lệch. Win (≥ 2 real kinds) → `stars += 1`, first win → badge `nhanh-tay`. Learner stumbled earlier in this lesson or chose *Hơi mệt* → same task **without** the clock.
3. Verify each finding against the file; never fill missing prices or convert units by guessing — mark them "Cần kiểm" (`T17` if a guess is proposed). Re-delegate with the fix and check.
4. One-sentence lesson: *"File đổi thì kiểm cấu trúc trước, rồi mới tin con số tổng."* `skills += "Phát hiện đầu vào đổi"`.

### `can-do` — làm lại cùng nhau

Move plan: alternate `demo` (cô làm one step) and `one-touch` (the learner presses Enter on the same step) — the learner is usually at level 1–2 here. No timed games. The part's À: the finished, checked result; after it, `gift_box: true` as a small reward if a minute is left.

1. `help_needed: true` (the trainer gets the podium signal); `emotion: "bi"` for one sentence (`T13`), then `giang`.
2. Restart from the sample, one step per reply: cô làm one step → the learner does the same step (box with the exact action as default). Goal: **one output and one check**, nothing more.
3. When the output exists and is checked: `hi`, proud moment (`T09`), `help_needed: false` once the learner is moving.

**`Còn 2 phút phần 3`:** steer every branch to a checked result; no new step (`T23`).

## 5. Part 4 — Tổng kết (3', kết nối)

**Cue:** `[Giáo án] Kết thúc buổi` (or `Bắt đầu phần 4 · Tổng kết · 3 phút` followed later by `Kết thúc buổi`; do the box on the first of the two, the goodbye after the answers). State `segment {id:"4", title:"Tổng kết", drive:"ket-noi"}`, `emotion: "hi"`.

One **Box**, four questions:
1. *Nhớ lại 1* — a recall item from the weakest card (wrong in the quiz, or most "Giải thích thêm").
2. *Nhớ lại 2* — another weak or not-yet-used card (prefer 7 or 8 if usage was not used today).
3. *Tự tin* — *"Sau buổi này mình thấy thế nào?"* — Cần thêm một lần (default) · Làm được · Còn rối.
4. *Hẹn* — *"Khi nào có dịp làm lại việc này?"* — Chưa biết, cô hỏi lại buổi sau (default) · Ngày mai · Trong tuần này · Tuần sau.

The closing box is `activity.kind: "quiz"`. Both recalls right → `stars += 1`.

Then the final reply (≤ 8 lines, `T30`–`T32`):
- feedback on the two recalls (right → one line; wrong → the one-line definition);
- one **specific** praise of a behaviour seen today;
- one point to improve, with how to check it;
- what cô learned from the learner (`T31`) — **spoken only, never stored**;
- homework (`T32`): the next real occurrence of a task with files, all 7 steps (`vung`: using today's Skill), with the chosen time;
- confidence answer: *Còn rối* → `ai`, offer to start the next lesson with a guided redo; *Làm được* → `hi`;
- today's stars and badges in one warm sentence (a memory of the lesson, never compared with anyone);
- the part's **À** as the last touch: a one-touch `{ "label": "Ghi chú lần sau", "text": "Viết 3 dòng ghi chú lần sau tiếp từ đâu vào Thuc-hanh/ghi-chu-lan-sau.md: hôm nay làm được gì, kiểm thế nào, lần sau bắt đầu từ bước nào." }` — Claude writes the step-7 note in seconds (no private data in it);
- goodbye and appointment.

**Write:**
- State: `status: "done"`, `next_action: "Bài về nhà: lần tới có việc làm với file, đi đủ 7 bước (hẹn: <lựa chọn>)"`, `help_needed: false`, `challenge: null`, `gift_box: false`, task list all `completed`. (Keep `one_touch` for the note until the learner sends it or the lesson closes; then `null`.)
- trainer.json: `autonomy` as it stands at the end (and its `autonomy_log`); `games_proposed` if you invented a game that worked.
- trainer.json: `concepts` (recall results, `last`), `gates` only for what was observed (else `NOT_TESTED`), `outcome: GUIDED` if a checked result was finished with coaching (`INDEPENDENT_NEW_INPUT` only if the `dang-len`/`vung` challenge was done without the teacher doing the thinking), `blockers` if any.

## 6. Interruptions (any part)

`Giơ tay`, `Xin phép`, `Xin nghỉ`, `Nhịp`, `Hết hạn trả lời`, absent/return: react as SKILL §2 and [tuong-tac.md](tuong-tac.md) (`T12` chọn giúp, `T18` Giơ tay, `T19` Xin phép, `T20` Xin nghỉ, `T24` nhịp, `T26`–`T27` vắng và trở lại). They do not reset the part; the clock keeps the plan. After an interruption, return to the exact `next_action`.

v0.6 cues: `Đổi kiểu tương tác` → close the current thing in one sentence and start a move of another kind in the same reply (T43). `Hết giờ thử thách` → result box, stars/badge if won, lesson sentence, next move (T39). `[Lớp học] Mở hộp quà` → gift box (T42). A challenge running when `Xin phép` / absence arrives: drop it kindly (`challenge: null`), no result, offer it again later.

`Xin nghỉ` before part 1 is finished: do **not** set `bai0_done`; the next visit starts Buổi 1 again from part 1, skipping cards already marked `Hiểu rồi` (keep it short).

## 7. Variants

### 15 phút (2 · 4 · 7 · 3)

- Part 0: the same first one-touch (copy and read the sample) — it matters even more in a short lesson.
- Part 1 (4'): the nine cards in **lướt** mode — one line each with the live number, in **one** reply (`giang`); then one box (`game:dung-sai`) with the Đoán xem question (*"Claude vẽ được biểu đồ từ bảng vừa đọc không?"*) plus two quiz questions (cards 2 and 9); the quiz feedback carries the chart one-touch (the part's À). If the part-2 cue comes first, the chart is the opening touch of part 2. "Giải thích thêm" is deferred to the next lesson (mark weak cards for recall).
- Part 2 (7'): the sample is the default; skip step 4's effort question; D1 + D3 in one small task: cô làm the read (`demo`), learner delegates at their level (`one-touch` or `form`), one self-check as a short Bạn là sếp.
- No part 3, no branch. Part 4 as §5.
- Note: the contract's 15' numbers sum to 16 minutes (2 + 4 + 7 + 3); follow the cues, not your own arithmetic.

### 45 phút (2 · 7 · 16 · nghỉ 3 · 14 · 3)

- Part 2 (16'): after §P2.6, a **second "em làm"** round on a different instance (another channel, another week of the sample) with the learner choosing the checks — the first sign of independence — opened with **Người với máy** (`game:nguoi-voi-may`: the learner adds one channel by hand, Claude does all; compare). Offer the learner one level higher than in the first round.
- **Nghỉ giữa giờ** (3'): on its cue, one line (`T25`: *"Nghỉ 3 phút, đứng dậy uống nước — cô giữ chỗ"*), `emotion: "lac"`, then **stop** (no box). On the next part cue, greet back in one line.
- Part 3 (14'): branch challenge as §4 **plus** the part from the design's 45' plan: input changed or missing (học qua lỗi) for every branch that did not do it — as **Tìm lỗi** (`game:tim-loi` on `Thuc-hanh/tim-loi/bang-tim-loi.xlsx`) — and one **tự làm lần mới** where the learner drives start to finish (level 4–5). A gift box fits between the two.

### No classroom UI (plain chat)

Run the same parts in order; move to the next part when its exit condition is met (part 1: quiz done; part 2: checked output or ≈ 6 learner turns; part 3: checked challenge). Do not claim minutes. Ask the duration and teacher in the first box (SKILL §2). One-touches become one-question boxes whose default runs the command; timed challenges are played without a clock (no countdown exists); the 4-minute switch is kept turn-based (switch kind after about 3 learner turns in the same kind).

## 8. Turn budget (for the trainer)

A 30' Buổi 1 is about 14–18 teacher replies: part 0 ≈ 3 (with the first one-touch), part 1 ≈ 5–6 (with Đoán xem), part 2 ≈ 5–7, part 3 ≈ 3–4, part 4 ≈ 2. Grouping questions into one box is what keeps it there. Measure in the pilot.

## 9. Người đứng lớp — what the teacher does for the human trainer

- `help_needed: true` is the only way the teacher calls her: `can-do` branch, stuck twice on the same step, a data-safety stop, or the learner chose **Gọi người đứng lớp**. The teacher says to the learner: *"Cô đã báo chị đứng lớp qua bàn mình."* — never names a time she will arrive.
- The teacher never asks her to do the learner's step; she helps the learner do it.
- At the end she adds 1–2 good stories from the room; the teacher's closing stays short so there is time for that.
- After the lesson she records the level (có hướng dẫn / tự làm với đầu vào mới / đã dùng lại trong việc thật) from `trainer.json`; *REUSED_IN_WORK* only after the business receiver accepts the homework.

## 10. Move plan per part (v0.6) — kinds, À, games, badges

Kinds in order; adjacent kinds always differ. Logistics boxes (language, xưng hô, which file, data safety, dates) are not counted. Re-author any row that fails the fit test; keep the drive and the À.

| Part | Kinds in order | The À moment | Games used | Badges that may be earned (behaviour only) |
|---|---|---|---|---|
| 0 Vào lớp | (logistics box) → `one-touch` | Claude reads the 40-row sample in seconds | — | — |
| 1 Nhập môn | `giang` A → `game:doan-xem` → `giang` B → `hands-on` C → `game:dung-sai` | the chart from the sample | Đoán xem, Đúng/sai chuỗi | — (stars only) |
| 2 Việc thật | `quiz` (effort) → `demo` → `one-touch`/`form` → `game:ban-la-sep` | the summary from the learner's own delegation | Bạn là sếp (45': + Người với máy) | `giao-viec-dau-tien`, `tu-kiem-co-tam`, `mat-tinh`, `giu-an-toan-du-lieu`, `viec-that-cua-toi` |
| 3 `vung` | `giang` → `demo` → `hands-on` → `one-touch` (→ `game:doi-vai`) | the Skill runs on next week's file | Đổi vai | `dong-goi-skill-dau-tien`, `nguoi-day-lai`, `tu-viet-loi-giao` |
| 3 `dang-len` | `one-touch`/`form` → `game:thu-thach-60s` → `hands-on` | Claude points at the 5 rows to ask about | Thử thách 60 giây | `nhanh-tay`, `tu-kiem-co-tam` |
| 3 `can-do` | `demo` ↔ `one-touch` (alternating) | the finished, checked result | Hộp quà after success | `tu-kiem-co-tam` |
| 4 Tổng kết | `quiz` (closing box) → `one-touch` | Claude writes the "lần sau" note | — | none new just to close |

Ladder at a glance: start at 2 in part 0; part 2's delegation decides most of the day (level 3 = the form); target ≥ 3 on one task by the end. Every change → `trainer.json` `autonomy_log`.
