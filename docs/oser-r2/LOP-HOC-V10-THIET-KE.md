# Lớp học NNC v0.10 — thầy chỉ trên màn hình thật của học viên

Quyết định của người phụ trách: **ưu tiên chỉ từ ảnh chụp màn hình thật của học viên**; hình mô phỏng thanh dưới ô nhập chỉ là đường lui. Builds on v0.8 (stage, point) and v0.9 (research, show don't send searching).

## 1. Flow

1. **Consent** (once per session, podium `choices`, default first): *"Cho thầy chụp cửa sổ Claude trên máy bạn để chỉ đúng chỗ? Ảnh chỉ nằm trong máy, xem xong thầy xoá."* — **Đồng ý** · **Không, vẽ hình giúp mình** (→ bar mock-up / slide as in v0.8). Record `trainer.json` `screen_consent: "<date>" | "no"`. Never capture without it; never ask again the same session after "no".
2. **Capture** — the teacher runs the Skill's script `assets/scripts/chup-man-hinh.ps1` (Windows PowerShell 5.1, built-in .NET only): captures **only the Claude Desktop window** (no other window, no full desktop), DPI-aware, saves `.lop-hoc/man-hinh.png` in the classroom folder, prints the image size. The learner may see a permission box the first time: the teacher says in one line what it does before running it.
3. **Locate** — the teacher reads `.lop-hoc/man-hinh.png` (vision) and finds the target control's pixel box.
4. **Mark** — the teacher runs `assets/scripts/danh-dau.ps1 -Box x,y,w,h [-Label "…"]`: draws a thick yellow (`#FFEA00`, border `#C9A800`) rounded box and an arrow with the label on a copy, crops to the region around the target (context kept, ≥ 640 px wide when possible), downsizes to ≤ 960 px wide, saves `.lop-hoc/chi-tay.jpg` lowering JPEG quality until ≤ 90 KB, prints final bytes.
5. **Show** — state `board`: `{ "title": "…", "shot": ".lop-hoc/chi-tay.jpg", "lines": ["…"] }`. The podium draws the marked screenshot (wide). One line asks the learner to **click it** now.
6. **Clean** — after the learner did it (or at Xin nghỉ / class end), the teacher deletes `.lop-hoc/man-hinh.png` and `chi-tay.jpg` (the scripts offer `-Clean`), and clears `board.shot`.

## 2. Contract — `board.shot`

- Path must be inside `.lop-hoc/` of the classroom folder, end in `.jpg`/`.jpeg`/`.png`, file ≤ 96 KB. Anything else is ignored.
- The mod reads the bytes (`$.fs.read(path, { as: 'bytes' })`), base64-encodes and draws an `Svg` whose only content is one `<image href="data:image/jpeg;base64,…">` sized to the image, total source ≤ 131 072 characters (else not drawn). Re-read when the state or the file changes (generation by mtime/size if available, else by state rewrite).
- `shot` wins over `svg` when both are present; `lines` and `title` still show. Terminal surface: text fallback "Thầy đã đánh dấu trên ảnh màn hình — xem trong Claude Desktop".

## 3. Privacy and safety

Only the Claude window; local file only; never sent, uploaded, attached to the result sheet or written into trainer files; deleted after use; consent once per session, revocable ("Không chụp nữa" → teacher stops). If the window shows real data the learner is working on, the teacher crops tightly to the control and never describes the data.

## 4. Fallbacks

Not Windows, script blocked, capture fails, or consent "no" → v0.8 bar mock-up + `podium.point` (still "show, don't send searching").

## 5. Versions

`lop-hoc` 0.10.0 · Skill 0.10.0 · `nnc` `5.1.0-alpha.2+lophoc.0.10.0` (never alpha.3) · tag `lop-hoc-v0.10.0`.
