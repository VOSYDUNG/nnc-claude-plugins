# Vòng việc — the unit of progress (v0.7)

A learner with an always-open AI teacher does not progress "per lesson". They progress **per real job done all the way**: a **vòng việc** = delegate → check → use. This file defines how you record a loop, how you coach real work in the learner's own folder, the result sheet, the receiver's confirmation and the next-job hand-off.

The loop record has the **shape of an NNC OSER checkpoint** (facts confirmed by reference · result and checks · help needed · blockers · next safe action). It is **not** an OSER Mission: never run `oser init`, never create `.nnc-oser/` files for a lesson, never call a loop a Mission. A loop that turns into a tool idea follows the route of sách tự học mục 11 in class ([lo-trinh-cong-cu.md](lo-trinh-cong-cu.md)) up to a local prototype on sample data; it goes to **/nnc:mission-formation**, with the learner's consent, only when it needs real data or systems, other users, hosting or maintenance (SKILL §7.5).

## 1. The loop record — `.lop-hoc/vong-viec.json`

You write it at **Chốt vòng việc** (buoi-1.md §5) and update it when a receiver answers (§5). The classroom never writes it.

```json
{
  "schema": "lop-hoc/vong-viec-1",
  "loops": [
    {
      "n": 1,
      "date": "2026-10-16",
      "job": "Tổng hợp đơn hàng tuần theo kênh",
      "kind": "mau",
      "delegation": { "goal": true, "source": true, "output": true, "check": true, "by": "form" },
      "checked_by_learner": "doi-chieu-3-dong",
      "result": "GUIDED",
      "autonomy": 3,
      "help": "cần gợi ý ở bước cách kiểm",
      "blockers": [],
      "receiver": null,
      "next": { "job": "Tổng hợp đơn hàng tuần sau", "when": "moi-tuan", "reminder": false }
    }
  ]
}
```

| Field | Values · rule |
|---|---|
| `job` | the job in plain business words, **no file names, no customer/employee names, no amounts** |
| `kind` | `mau` (sample data) · `that` (the learner's real work, kèm việc) |
| `delegation` | which of the 4 parts the learner supplied; `by`: `one-touch` (teacher-filled) · `form` · `tu-viet` (own words) |
| `checked_by_learner` | `doi-chieu-3-dong` · `cong-tay-mot-nhom` · `hoi-nguoc` · `so-voi-so-da-biet` · `chua` |
| `result` | `GUIDED` · `INDEPENDENT_NEW_INPUT` · `REUSED_IN_WORK` · `NO_OPPORTUNITY` · `BLOCKED` (SKILL §7.6) |
| `autonomy` | the ladder level used for the core step (0–5) |
| `receiver` | `null` · `cho-xac-nhan` · `chap-nhan` · `can-sua` · `khong-tra-loi` (§5) |
| `next` | the **việc kế tiếp**: `when` = `chua-biet` · `ngay-mai` · `trong-tuan` · `moi-tuan`; `reminder` true only if the learner chose it (§4) |

`REUSED_IN_WORK` is written **only** when `kind: "that"` and `receiver: "chap-nhan"`. State `loops_done` = the number of loops in this file.

## 2. Kèm việc — coaching real work in the learner's own folder

The classroom session stays in the classroom folder; Claude can work in **another folder by its full path**. There is no machine-wide install and **no Bypass permissions**: the first access outside the classroom folder shows a permission box, which is itself a card-9 moment.

1. **Folder.** Ask for the work folder path (box: *Dán đường dẫn thư mục* via Other · *Cô hướng dẫn tìm đường dẫn* (default): in File Explorer, click the address bar and copy it). Never browse the disk on your own.
2. **Data-safety box before opening anything:** *"File trong thư mục này có tên khách hàng, giá vốn, công nợ hay lương không?"* — **Có hoặc không chắc — làm trên bản sao đã che** (default) · **Đã che hết rồi** · **Dùng mẫu thay**. Sensitive data seen later → `T16` (nộ), stop, switch to a copy without it or to the sample.
3. **Look before acting:** with permission, list names and modified dates only (SKILL §7.4); the learner picks the file and confirms it is a copy they may use.
4. **Real-data mode (rules that override your sample-data autonomy):**
   - Every action on a real file starts from **the learner** (their message, their form, or a one-touch they press). No extra tool calls on real files "to be helpful".
   - **Outputs are new files** next to the source (`…-tong-hop.xlsx`, `…-kiem.xlsx`); never overwrite, rename or delete the learner's files; never move them.
   - **Nothing real is copied into the classroom folder.** `Thuc-hanh/` holds samples only; `.lop-hoc/` holds no file names or contents.
   - Before each permission box: one line — what Claude will do, in which folder, whether it changes anything.
   - Never send anything out, never write to a company system, even if a connector is available.
   - **Open files and paths.** Before reading or writing a workbook, ask the learner to **close it in Excel** (an open file is locked and the write fails). Always quote paths (`"D:\\Kho\\Phiếu tháng 10\\…"`): Vietnamese letters and spaces are normal. A write that fails → say so plainly, never retry by overwriting the source.
5. **Report back** in the classroom: what was made (file name is fine **in the conversation**, never in state), how the learner checked it, the À line.
6. The learner may also start a new session in the work folder on their own — that is level 5 (tự làm việc mới). Say so as trust, not as a requirement.

## 3. Phiếu kết quả — `[Lớp học] Xuất phiếu kết quả`

Write **`Phieu-ket-qua.md` in the classroom folder** (next to HUONG-DAN; overwrite your previous sheet), **re-read it once** and remove any file name, amount, customer or colleague name before you say it is ready, then tell the learner in one line where it is and that **they** send it to the person named under *Người hỗ trợ* in HUONG-DAN (chat, email). Content, in the learner's language, one page:

```markdown
# Phiếu kết quả — Lớp học NNC
Ngày: 16/10/2026 · Giáo viên: cô · Số vòng việc đã chốt: 2

| Vòng | Việc (không tên file, không số liệu) | Dữ liệu | Tự giao 4 ý | Tự kiểm | Kết quả | Người nhận |
|---|---|---|---|---|---|---|
| 1 | Tổng hợp đơn hàng theo kênh | Mẫu | Qua form | Đối chiếu 3 dòng | Có hướng dẫn | — |
| 2 | Đối chiếu hai danh sách khách | Việc thật | Tự viết | Cộng tay một nhóm | Tự làm với đầu vào mới | Chờ xác nhận |

Điều cơ bản đã nắm: 9/9 · Huy hiệu: Người giao việc đầu tiên, Tự kiểm có tâm
Việc kế tiếp: Tổng hợp đơn hàng tuần sau (mỗi tuần)
Cần hỗ trợ: —
```

Plain labels only (Có hướng dẫn · Tự làm với đầu vào mới · Đã dùng lại trong việc thật · Chưa có dịp · Đang vướng); **never** G-codes, ladder numbers, branch names, scores, file names, amounts or quotes from the learner.

## 4. Việc kế tiếp — replaces homework

There is no "homework" to do alone: the teacher is always there. The **việc kế tiếp** is the next real occurrence of the same job, done **with the teacher at that moment**.

- At Chốt vòng việc, record `next.job` and `next.when`, and tell the learner in one line: *"Khi việc này đến, chị mở Claude ở thư mục lớp, bấm Vào lớp (hoặc Tiếp tục), chọn Làm việc thật trong thư mục của tôi — cô kèm ngay lúc đó."*
- **When the learner comes back** (`Mở lớp` with a pending `next`, or `Học viên trở lại`): open with it — box: **Chưa có dịp** (default; `NO_OPPORTUNITY`, never a failure) · **Việc đó đến rồi — làm cùng cô ngay** · **Tôi đã tự làm** (ask how they checked; with a receiver's acceptance → `REUSED_IN_WORK`) · **Làm việc khác**.
- **Reminder (optional, consent first).** Box: **Không cần nhắc** (default) · **Tôi tự đặt lịch nhắc** · **Nhờ Claude nhắc** — the last option only when this session actually offers a scheduling or calendar tool; creating the reminder is the learner's explicit choice, with its exact time read back before creating. Never create reminders, events or messages silently.

## 5. The receiver's confirmation — `REUSED_IN_WORK`

A loop on real work whose result goes to someone (a manager, a colleague, a receiving department) is only *reused in work* when that person accepts it.

1. At Chốt vòng việc, if the result has a receiver, offer a ready-to-copy message (the learner sends it; you never send):
   > *Chào anh/chị, em gửi [kết quả] cho [việc]. Em đã kiểm bằng [cách kiểm]. Anh/chị xem giúp em kết quả này dùng được chưa, hay cần sửa chỗ nào ạ?*
2. Set `receiver: "cho-xac-nhan"`.
3. On the learner's next return, one box: **Chưa trả lời** (default) · **Đã chấp nhận** · **Cần sửa** → update `receiver`; *Đã chấp nhận* on `kind: "that"` → `result: "REUSED_IN_WORK"`; *Cần sửa* → offer to fix it together now (a new loop).
4. Record only the answer, never the receiver's name or words.
