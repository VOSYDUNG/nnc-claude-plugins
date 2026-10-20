# Chỉ trên màn hình thật — the marked real screenshot (v0.10)

Contract: `docs/oser-r2/LOP-HOC-V10-THIET-KE.md` §1, §3, §4. Model instructions are in English; everything the learner sees is in the learner's language (Vietnamese or Lao). Nothing here is quoted to the learner: no script names, no paths, no "capture", no "state".

## 1. The rule

**When the learner must find something on their own screen — the permission mode, model, effort, the usage circle, a button, a menu — the first choice is a real screenshot of their Claude window with the place marked in yellow. The bar mock-up ([day-truc-quan.md](day-truc-quan.md) A) and `podium.point` are the fallback**, used when consent is "no", the script cannot run or the capture fails (§5). A marked real picture beats a drawing: the learner sees *their* screen, not a model of it.

This is still *show, don't send searching* ([nghien-cuu-tai-lieu.md](nghien-cuu-tai-lieu.md)): the learner never hunts for the control; they see it marked and **click it**.

## 2. The flow

1. **Consent — once per session, as podium `choices`** (never a native box, never `timeout_s`: no click means no capture). Default first:
   - Vietnamese: *"Cho thầy chụp cửa sổ Claude trên máy chị để chỉ đúng chỗ? Ảnh chỉ nằm trong máy, xem xong thầy xoá."* — **Đồng ý** (default) · **Không, vẽ hình giúp mình**
   - Lao: *"ໃຫ້ຄູຖ່າຍຮູບໜ້າຕ່າງ Claude ໃນເຄື່ອງຂອງເອື້ອຍ ເພື່ອຊີ້ບອກຖືກບ່ອນບໍ? ຮູບຢູ່ໃນເຄື່ອງເທົ່ານັ້ນ ເບິ່ງແລ້ວຄູລຶບ."* — **ຕົກລົງ** · **ບໍ່, ແຕ້ມຮູບໃຫ້ແທນ**
   Write `trainer.json` `screen_consent`: today's date (`"2026-10-18"`) on yes, `"no"` on no. A value from an earlier session does not carry over: ask again once in a new session. After "no", never ask again in the same session and use the mock-up. The learner may revoke any time (*"Không chụp nữa"*): set `"no"`, run `-Clean`, go on with mock-ups.
2. **One line before the first run**, in the learner's language: what the script does (*"Thầy chụp riêng cửa sổ Claude, chỉ lưu trong máy"*). Desktop may ask the learner to allow the command the first time: that is expected, say it is safe in one phrase, never answer the box for them.
3. **Capture** (§3). The script prints `OK <w>x<h> <path>` or `ERR <code>`.
4. **Locate by reading the image.** Read `.lop-hoc/man-hinh.png` with your image-reading tool (vision) and find the target control's pixel box `x,y,w,h` in **the image's own pixels**. If the image is shown to you smaller than the printed size, scale the coordinates by `printed width ÷ shown width`. Box the control tightly (its label plus a little padding), not the whole bar.
5. **Mark** (§3). Read `.lop-hoc/chi-tay.jpg` once to check the yellow box really sits on the intended control and the label is legible. Wrong place → correct the box and mark again, **at most twice**; still wrong → §5 fallback.
6. **Show**: one full `Write` of state with `board: { "title": "…", "shot": ".lop-hoc/chi-tay.jpg", "lines": ["…"] }` (no `svg`: `shot` wins). `lines` say in one or two short lines what the marked place is and ask the learner to **click it now** (*"Chị bấm vào chỗ thầy khoanh vàng, rồi cho thầy biết có những mức nào"*), never to read the value back (SKILL §12.3). Keep `podium.point` set only if the mock-up is also on screen; with a real shot it is not needed.
7. **Clean**: once the learner did it, or at *Xin nghỉ* or the end of class, run `-Clean` (deletes `man-hinh.png` and `chi-tay.jpg`) and clear `board.shot` in the same turn's `Write`. Never leave a screenshot in the classroom folder overnight.

`board.shot` rules (mod contract): a path inside `.lop-hoc/`, ending `.jpg`, `.jpeg` or `.png`, file at most 96 KB (the marking script keeps it at or under 90 KB); anything else is ignored. The podium draws the image wide.

## 3. The two scripts — exact invocations

Use the Skill's **base directory** (the `Base directory for this skill` line the Skill tool gives you) as `<base>`. Run them from the classroom folder so `.lop-hoc\` is the classroom's own. Windows only (PowerShell 5.1, .NET built in, no modules).

Capture only the Claude window:

```
powershell -NoProfile -ExecutionPolicy Bypass -File "<base>\assets\scripts\chup-man-hinh.ps1"
```

Output `OK 1366x728 …\.lop-hoc\man-hinh.png`. Optional `-Out <path>`. It makes the process DPI-aware, finds the visible, not-minimised top-level window of the `Claude` process with the largest area and copies **only that rectangle**; it never captures the whole desktop. Errors: `ERR no-window` · `ERR minimised` · `ERR covered` · `ERR capture-failed` · `ERR save-failed` · `ERR not-windows`, exit code 1.

Mark the place (draws on a copy; the original is untouched):

```
powershell -NoProfile -ExecutionPolicy Bypass -File "<base>\assets\scripts\danh-dau.ps1" -Box 340,702,134,24 -Label "Chế độ quyền: bấm vào đây"
```

`-Box x,y,w,h` is required (pixels in the capture). `-Label` is optional, short (≤ 40 characters), in the learner's language; Lao labels use a Lao font automatically. Defaults: `-In .lop-hoc\man-hinh.png`, `-Out .lop-hoc\chi-tay.jpg`, `-MaxWidth 960`, `-MaxBytes 92160`. It draws a semi-transparent yellow fill and a 5 px `#C9A800` rounded border around the box, a thick arrow from the side with more room, and the label in a yellow pill near the arrow tail; crops a tight region around the box (v0.13: at least 400×240 when the image allows — `-MinCropW`, `-MinCropH` — so the control shows large on the podium), adds a **small map of the whole window** in the top-right corner with a red frame on the cropped region so the learner knows *where* it is (`-NoMap` to skip; the map is tiny and shows no readable content), downsizes to at most 960 px wide, and saves a JPEG lowering quality from 85 to 40 until it fits. Output `OK <w>x<h> <bytes> <path>`.

Clean up:

```
powershell -NoProfile -ExecutionPolicy Bypass -File "<base>\assets\scripts\chup-man-hinh.ps1" -Clean
```

Output `OK cleaned <n>`.

Targets worth marking in the Desktop bottom bar: the permission-mode label (left, under the input box), the model name and effort word (right), the round usage circle (far right). Mark **one** place per picture.

## 4. Privacy and safety

- Only the Claude window is captured, never other windows or the desktop; the file stays in the learner's own `.lop-hoc/`; it is never sent, uploaded, attached to the result sheet or copied into `trainer.json`, `state.json`, `vong-viec.json` or any other file.
- Consent once per session, revocable. No consent, no capture. Never capture while a permission box, a login or a password screen is on the learner's Claude window; wait.
- The window may show the learner's real work (sessions, file names, numbers). **Crop tightly to the control** (a small `-Box`; the script keeps only the context around it) and **never describe, read or comment on anything else in the picture**. If the first capture shows real data that would sit inside the crop, mark a different tight region or fall back to the mock-up.
- Delete after use (§2.7). The marked image is the only one that goes on the podium; `man-hinh.png` is never shown as is.
- Record in `trainer.json` only `screen_consent` (a date or `"no"`), never the picture, a path, or what was in it.

## 5. Fallbacks — no retry loop

| Situation | Do |
|---|---|
| Consent "no" (or revoked) | bar mock-up A + `podium.point` + a *Làm theo* block ([day-truc-quan.md](day-truc-quan.md) §2), as in v0.8; do not ask again this session |
| Not Windows, command blocked or refused, PowerShell missing | the same mock-up; say nothing technical |
| `ERR minimised` / `ERR covered` | one kind line (*"Chị mở cửa sổ Claude lên giúp thầy một chút"*) and **one** more try after the learner confirms; then the mock-up |
| `ERR no-window`, `ERR capture-failed`, `ERR save-failed`, or the marking is wrong twice | the mock-up in the same turn; **no retry loop**, never ask the learner to take a screenshot themselves |

A failed capture is never the learner's fault and never a lesson topic. The class never depends on the screenshot.

## 6. Worked example — the permission mode, first choice the real picture

The learner's mode is Bypass; the teacher has asked for consent and got **Đồng ý** (`screen_consent` written).

1. One line: *"Thầy chụp riêng cửa sổ Claude, chỉ lưu trong máy."* Run `chup-man-hinh.ps1` from the classroom folder → `OK 1366x728 …`.
2. Read `.lop-hoc/man-hinh.png`: the mode label *Bypass permissions* sits at about x 345, y 705, 125×20 px under the input box.
3. Run `danh-dau.ps1 -Box 340,702,134,24 -Label "Chế độ quyền"` → `OK 652x360 39472 …`; read `chi-tay.jpg`: the yellow box is on the mode label, the arrow and the pill are legible.
4. One `Write`: `board { "title": "Chế độ quyền ở đây", "shot": ".lop-hoc/chi-tay.jpg", "lines": ["Chữ ở góc trái, dưới ô nhập", "Chị bấm vào đó, chọn Auto"] }`, choices *Thầy chỉ thêm* · *Tôi đã đổi rồi*.
5. The `Chế độ quyền · Auto` cue arrives: praise in a few words, run `-Clean`, clear `board.shot`.

Citation line (*Nguồn: Sách mục 5 · Hình 10*) still goes under the picture when the step comes from the book.
