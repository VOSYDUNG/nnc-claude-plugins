# Lớp học NNC v0.5 — Hợp đồng chung (Skill ↔ mod ↔ dữ liệu mẫu)

Nguồn sự thật cho mọi người cùng build v0.5. Đọc kèm: [LOP-HOC-THIET-KE-V0.5.md](LOP-HOC-THIET-KE-V0.5.md) (phương pháp, giáo viên, cảm xúc) và [LOP-HOC-BUOI-1.md](LOP-HOC-BUOI-1.md) (giáo án 30 phút). Sửa hợp đồng này phải báo người tích hợp.

## 1. Vai trò

| Thành phần | Sở hữu | Không được |
|---|---|---|
| **Mod `lop-hoc`** | Đồng hồ buổi học, giáo án theo giờ, tự chuyển phần, hạn 60 giây, điểm danh, tạm nghỉ, Xin phép/Xin nghỉ, hình giáo viên và cảm xúc, thẻ usage, giấu tín hiệu nội bộ | Tự quyết nội dung dạy; gọi model ngoài `$.prompt.submit` |
| **Skill `work-first-learning` (giáo viên)** | Nội dung giảng, câu hỏi, khen/sửa, phân nhánh, cảm xúc, ghi `.lop-hoc/state.json` | Tự đặt giờ; hiện từ kỹ thuật cho học viên |
| **Dữ liệu mẫu** | File bảng tính giả, đáp án, Skill mẫu | Dữ liệu thật |

**Dùng công cụ có sẵn của Anthropic, không vẽ lại:**
- **Câu hỏi, đố, thẻ định nghĩa, lựa chọn** → hộp câu hỏi gốc `AskUserQuestion` của Claude Code. Mod chỉ thêm một dòng tiêu đề lớp học phía trên, giữ nguyên hộp gốc.
- **Giáo án trong buổi** → danh sách việc gốc của Claude Code (task list) do giáo viên cập nhật.
- **Thông báo** → toast gốc. **Đang làm** → spinner gốc, đổi chữ.
- **Hộp xin quyền** → giữ nguyên.

Mod chỉ tự vẽ những gì Anthropic không có: bục giảng có giáo viên, thẻ usage theo thời gian, đồng hồ phần học.

## 2. Tín hiệu từ mod sang giáo viên (ẩn với học viên)

Mod gửi bằng `$.prompt.submit({ text, asUser: false })` khi Claude đang rảnh và ô nhập trống. Mỗi tín hiệu bắt đầu bằng `[Giáo án]`. Mod vẽ lại các tin này thành **một dòng chia phần** (hoặc ẩn hẳn), không hiện nguyên văn.

| Tín hiệu | Khi | Giáo viên làm |
|---|---|---|
| `[Giáo án] Mở buổi · {minutes} phút · giáo viên {thay|co}` | Học viên bấm vào lớp và chọn thời lượng, giáo viên | Chào theo nhân cách, nêu mục tiêu, ghi `state` |
| `[Giáo án] Bắt đầu phần {id} · {title} · {minutes} phút` | Đến giờ phần mới | Chốt một câu phần trước, mở phần mới |
| `[Giáo án] Còn {n} phút phần {id}` | 2 phút trước hết phần | Nhắc nhẹ, hướng về bước chốt |
| `[Giáo án] Hết hạn trả lời · chọn giúp {label}` | 60 giây không bấm | Chọn giúp, nói rõ, đi tiếp |
| `[Giáo án] Học viên vắng · tạm nghỉ` | Điểm danh hết hạn | Một câu "cô chờ", **dừng giảng** |
| `[Giáo án] Học viên trở lại` | Bấm Có mặt sau tạm nghỉ | Chào lại, nhắc đang ở đâu |
| `[Giáo án] Xin phép · {lý do}` | Bấm Xin phép | Đáp lại phù hợp, giữ nhịp |
| `[Giáo án] Xin nghỉ` | Bấm Xin nghỉ | Chào, lưu, hẹn bài về nhà, `status: paused` |
| `[Giáo án] Giơ tay` | Bấm Giơ tay | Mời học viên hỏi (ô "Kể cô nghe") |
| `[Giáo án] Nhịp: chậm lại` / `nhanh hơn` | Bấm nút nhịp | Điều chỉnh nhịp |
| `[Giáo án] Kết thúc buổi` | Hết giờ | Tổng kết, nhớ lại 2 định nghĩa, bài về nhà, chào |

Tin học viên tự gửi từ nút vẫn dùng tiền tố `[Lớp học] ` (như v0.4).

## 3. `.lop-hoc/state.json` — schema `lop-hoc/2`

Giáo viên ghi; mod đọc. Mod chỉ được ghi thêm khối `clock`.

```json
{
  "schema": "lop-hoc/2",
  "status": "active",
  "lesson": { "id": "buoi-1", "minutes": 30, "started_at": "2026-10-16T09:00:00+07:00" },
  "segment": { "id": "2", "title": "Việc thật của tôi", "drive": "D1" },
  "teacher": { "kind": "co", "name": "", "emotion": "hi" },
  "address": "chị",
  "branch": "dang-len",
  "next_action": "Bấm Giao việc, điền 4 ý",
  "destination": "Bảng tổng hợp theo kênh",
  "result_parts": [{ "label": "Đọc file", "done": true }, { "label": "Tổng hợp", "done": false }],
  "skills": [{ "label": "Biết thư mục làm việc", "done": true }],
  "help_needed": false,
  "updated_at": "2026-10-16T09:12:00+07:00",
  "clock": { "segment_started_at": "2026-10-16T09:09:00+07:00", "paused": false, "absent_strikes": 0 }
}
```

| Trường | Giá trị |
|---|---|
| `segment.id` | `"0"` Vào lớp · `"1"` Nhập môn · `"2"` Việc thật · `"3"` Theo nhánh · `"4"` Tổng kết |
| `drive` | `D1` · `D2` · `D3` · `ket-noi` |
| `teacher.kind` | `thay` · `co` |
| `teacher.emotion` | `hi` (vui) · `no` (nghiêm) · `ai` (thương) · `o` (không ưng cách làm) · `bi` (đồng cảm) · `lac` (vui đùa) · `giang` (đang giảng) · `nghe` (lắng nghe) |
| `branch` | `vung` · `dang-len` · `can-do` · `null` (tên nội bộ, không hiện) |
| `help_needed` | `true` → bục giảng hiện tín hiệu cho người đứng lớp |

`.lop-hoc/trainer.json` (chỉ người đào tạo): `gates`, `outcome`, `feedback`, `bai0_done` và thêm `concepts`: `{ "<id>": { "learned": date, "used": n, "recalled_ok": n, "last": date, "news": bool } }`.

## 4. Giáo án Buổi 1 (mod dùng để hẹn giờ)

```json
[
  { "id": "0", "title": "Vào lớp", "minutes": 2, "drive": "ket-noi" },
  { "id": "1", "title": "Nhập môn", "minutes": 7, "drive": "D2" },
  { "id": "2", "title": "Việc thật của tôi", "minutes": 11, "drive": "D1" },
  { "id": "3", "title": "Thử thách theo nhịp của bạn", "minutes": 7, "drive": "D3" },
  { "id": "4", "title": "Tổng kết", "minutes": 3, "drive": "ket-noi" }
]
```

15 phút: bỏ 3, rút 1 còn 4, 2 còn 7, 4 còn 2 (2+4+7+2 = 15). 45 phút: 2 thành 16, 3 thành 14, thêm phần `{ "id": "nghi", "title": "Nghỉ giải lao", "minutes": 3 }` sau phần 2 (2+7+16+3+14+3 = 45). Giáo viên phải chấp nhận `segment.id = "nghi"`.

## 5. Nút trên bục giảng (từ ngữ đã chốt)

- **Luôn có:** **Giơ tay** · **Xin phép** · **Xin nghỉ**.
- **Theo lúc:** Có mặt · Chậm lại một chút · Nhanh hơn được · Giao việc (form 4 ý) · Cô/thầy gợi ý giúp · Thưa cô, chỗ này chưa đúng.
- **Không dùng:** Runtime, prompt, state, Nhắc Claude, Tạm dừng, Kết thúc.

## 6. Hình

- Hai giáo viên **thầy** và **cô** theo bản phác đã duyệt: người cách điệu, áo xanh NNC; thầy đeo kính, cà vạt vàng; cô tóc búi, khăn vàng.
- Mỗi người 8 cảm xúc theo `teacher.emotion`.
- Màu động lực: D1 `#3CC85A` · D2 `#4A90E2` · D3 `#F5A524` · Kết nối `#F4F4EC`.
- Bảng lớp `#123F1E`; chữ `#FFFFFF` / `#FFEA00`.

## 7. Chốt sau tích hợp (15/10/2026)

- **Lựa chọn mặc định:** giáo viên luôn đặt phương án mặc định **đứng đầu** (options[0]), có thể ghi "(đề xuất)". Hết 60 giây, lớp đóng hộp câu hỏi và gửi `Hết hạn trả lời · chọn giúp {label}` với nhãn đó. Nhãn không khớp phương án nào thì giáo viên dùng phương án đầu.
- **Ngôn ngữ:** thêm trường tùy chọn `"language": "vi" | "lo"` vào `state.json`. Giáo viên hỏi ở buổi đầu rồi ghi lại.
- **Buổi sau Buổi 1:** dùng lại id phần 0–4, tiêu đề do giáo án của buổi đó đặt.
- **Thuộc định nghĩa:** mỗi thẻ được cộng tối đa +2 lần nhớ lại đúng trong một buổi, nên "3 lần đúng" luôn trải qua ít nhất 2 buổi.
- **Điểm danh khi đang thực hành:** 60 giây ngồi im ở lượt của học viên tính là một lần không tương tác. Pilot sẽ quan sát; nếu quá chặt thì nâng lên khi đang ở phần thực hành.

## 8. Bổ sung v0.6 — bộ năng lực giáo viên

Nguồn thiết kế: [LOP-HOC-NANG-LUC-GIAO-VIEN.md](LOP-HOC-NANG-LUC-GIAO-VIEN.md). Bổ sung này không bỏ gì của §1–7.

### 8.1 Trường mới trong `state.json` (giáo viên ghi, mod đọc)

```json
{
  "one_touch": { "label": "Cho Claude đọc bảng đơn hàng", "text": "Đọc file Thuc-hanh/bang-tinh-mau.xlsx và cho tôi biết có mấy kênh bán hàng, mỗi kênh bao nhiêu dòng." },
  "activity": { "kind": "game:doan-xem", "started_at": "2026-10-16T09:05:00+07:00" },
  "challenge": { "title": "Tìm 3 dòng thiếu giá", "seconds": 60, "started_at": "2026-10-16T09:06:00+07:00" },
  "stars": 3,
  "badges_new": [{ "id": "giao-viec-dau-tien", "label": "Người giao việc đầu tiên" }],
  "gift_box": true
}
```

| Trường | Kiểu | Mod làm |
|---|---|---|
| `one_touch` | `{label, text} \| null` | Nút lớn **"▶ {label}"** trên bục. Bấm thì `$.prompt.fill({ text, mode: 'replace' })`; **học viên tự bấm Enter**. Sau khi bấm, nút ẩn đến khi `label` hoặc `text` đổi |
| `activity` | `{kind, started_at} \| null` | Cùng `kind` và `started_at` quá 4 phút thì gửi **một lần** `[Giáo án] Đổi kiểu tương tác · {kind} · {n} phút` |
| `challenge` | `{title, seconds, started_at} \| null` | Vòng đếm ngược trên bục. Về 0 thì gửi **một lần** `[Giáo án] Hết giờ thử thách · {title}` (vẫn theo luật: Claude rảnh, ô nhập trống) |
| `stars` | số | Hiện ★ {n} trên bục |
| `badges_new` | `[{id, label}]` | Gộp vào `.lop-hoc/huy-hieu.json` (bỏ trùng theo `id`). Với `id` mới: toast *"Huy hiệu mới: {label}"* và bục giảng đổi cảm xúc `hi` trong 6 giây |
| `gift_box` | `true \| false` | Nút **"Mở hộp quà"** → gửi `[Lớp học] Mở hộp quà` (học viên bấm) |

Giá trị `activity.kind`: `giang` · `demo` · `one-touch` · `quiz` · `hands-on` · `form` · `game:{ten}`, trong đó tên trò viết kebab-case, ví dụ `game:doan-xem`, `game:thu-thach-60s`, `game:nguoi-voi-may`, `game:tim-loi`, `game:ban-la-sep`, `game:dung-sai`, `game:doi-vai`, `game:hop-qua`, hoặc trò giáo viên tự chế.

### 8.2 File mới

`.lop-hoc/huy-hieu.json` (mod ghi, học viên thấy trên bục; giáo viên đọc được):

```json
{ "schema": "lop-hoc/huy-hieu-1", "badges": [{ "id": "giao-viec-dau-tien", "label": "Người giao việc đầu tiên", "date": "2026-10-16" }] }
```

`trainer.json` thêm: `autonomy` (0–5) cùng `autonomy_log: [{date, from, to, reason}]`; `games_proposed: [{name, why}]` (trò tự chế đáng đưa vào kho; giáo viên chỉ đề xuất, không tự sửa kho).

### 8.3 Tín hiệu mới

| Tín hiệu | Từ | Giáo viên làm |
|---|---|---|
| `[Giáo án] Đổi kiểu tương tác · {kind} · {n} phút` | mod | Chọn nước đi khác kiểu ngay lượt này |
| `[Giáo án] Hết giờ thử thách · {title}` | mod | Công bố kết quả, ghi nhận, chuyển tiếp |
| `[Lớp học] Mở hộp quà` | học viên | Mở 3–4 thẻ khả năng bằng hộp câu hỏi gốc; thẻ được chọn thành `one_touch` |

### 8.4 Hình mới (`hooks/art.ts`)

- `starRowSvg(n)`
- `badgeSvg(id, label)`: huy hiệu tròn nhỏ, màu theo nhóm
- `badgeShelfSvg(badges: {id,label}[])`: tối đa 4 cái gần nhất, kèm "+n"
- `giftBoxSvg(open: boolean)`
- `challengeRingSvg({remainingMs, totalMs})`: đỏ cam ở 10 giây cuối

### 8.5 Chốt sau tích hợp v0.6 (15/10/2026)

- **Đường dẫn:** `one_touch.text` chỉ nhắc file mẫu đã chép vào `Thuc-hanh/` trong thư mục lớp (một tên thống nhất, viết hoa chữ T). Không bao giờ chép đáp án.
- **Giờ bắt đầu thử thách:** `challenge.started_at` là tùy chọn. Thiếu, sai, hoặc ở tương lai quá 1 phút thì mod tự đóng dấu lúc thấy lần đầu (mất khi nạp lại mod thì đếm lại).
- **Thử thách và hạn 60 giây:** khi thử thách đang chạy, mod tạm ngưng hạn 60 giây của hộp câu hỏi gốc; hạn tính lại từ lúc thử thách xong. Giáo viên vẫn không mở hộp hỏi trong lúc chơi có giờ.
- **Huy hiệu:** danh sách đầy đủ duy nhất là `.lop-hoc/huy-hieu.json`. `trainer.json` không giữ bản sao; người đào tạo đọc file này.
- **Hộp quà:** bỏ trường `capability_cards`. Các thẻ khả năng do giáo viên đưa ra bằng hộp câu hỏi gốc sau tín hiệu `[Lớp học] Mở hộp quà`. Mod chỉ dùng cờ `gift_box`.
- **Huy hiệu ngoài danh mục ban đầu** (ví dụ `giu-an-toan-du-lieu`, `tu-viet-loi-giao`, `viec-that-cua-toi`): hình hiện biểu tượng chung, không lỗi.

## 9. Bổ sung v0.7 — lớp luôn mở, vòng việc, nhịp theo hạn mức

Nguồn quyết định: người thiết kế chương trình, 16/10/2026. Học với giáo viên AI không tính theo buổi: lớp **luôn mở**, đơn vị tiến bộ là **vòng việc** (một việc thật đi trọn: giao → kiểm → dùng), nhịp theo **hạn mức** chứ không theo thời gian hay khối lượng. §9 thay các phần về giờ của §2, §4 và §7; mọi thứ khác giữ nguyên.

### 9.1 Mod thay đổi

| | v0.6 | v0.7 |
|---|---|---|
| Vào lớp | chọn giáo viên và 15/30/45 phút | chọn giáo viên → **Vào lớp** |
| Phần học | mod đổi theo giờ, gửi "Bắt đầu phần", "Còn n phút", "Kết thúc buổi" | **giáo viên ghi `segment` khi đạt mốc**; mod chỉ hiển thị |
| Hạn 60 giây | mọi hộp câu hỏi | chỉ khi `activity.kind` là `quiz` hoặc `game:*` |
| Điểm danh | 2 lần không tương tác → điểm danh → tạm nghỉ | **bỏ**; giữa hai lần học viên tác động mod gửi tối đa một tín hiệu |
| Mở lại app | trong 3 giờ, lớp tạm nghỉ, nút Có mặt | bất kỳ lúc nào; nút **Tiếp tục** |
| Đổi kiểu tương tác 4 phút | mọi kiểu | trừ `hands-on`, `form` (đang làm việc thật) |
| Hạn mức | chỉ hiển thị | tín hiệu khi chạm ngưỡng (§9.2) |
| Nút mới | — | **Phiếu kết quả**; **Soạn tin nhờ hỗ trợ** (khi `help_needed`) |

Phần học v0.7: `"0"` Vào lớp · `"1"` Làm quen nhanh · `"2"` Việc thật của tôi · `"3"` Thử thách theo nhịp của bạn · `"4"` Chốt vòng việc.

### 9.2 Tín hiệu v0.7

| Tín hiệu | Khi | Giáo viên làm |
|---|---|---|
| `[Giáo án] Mở lớp · giáo viên {thay\|co} · hạn mức 5 giờ {p}% · tuần {q}%` | học viên bấm Vào lớp (phần hạn mức thiếu nếu chưa đọc được) | mở vòng việc; ghi nhớ số hạn mức |
| `[Giáo án] Hạn mức · 5 giờ {p}% · reset {HH:MM}` | 5 giờ chạm 70% rồi 90%, mỗi ngưỡng một lần trong một chu kỳ reset | 70%: giảng gọn; 90%: lưu điểm dừng |
| `[Giáo án] Hạn mức · tuần {q}% · reset {dd/MM HH:MM}` | tuần chạm 90% | chốt vòng việc ở điểm gọn kế tiếp |
| `[Giáo án] Học viên trở lại` | bấm Tiếp tục hoặc Quay lại lớp | đọc lại state và vòng việc, tiếp đúng chỗ |

Giữ nguyên: `Hết hạn trả lời · chọn giúp` (chỉ câu đố, trò chơi), `Xin phép`, `Xin nghỉ` (lưu chỗ), `Giơ tay`, `Nhịp`, `Đổi kiểu tương tác`, `Hết giờ thử thách`. Nút học viên mới: `[Lớp học] Xuất phiếu kết quả`, `[Lớp học] Soạn tin nhờ hỗ trợ`. Bỏ: `Mở buổi`, `Bắt đầu phần`, `Còn {n} phút`, `Học viên vắng · tạm nghỉ`, `Kết thúc buổi` (Skill vẫn xử lý nếu bục giảng cũ gửi).

### 9.3 Dữ liệu v0.7

- `state.json`: `lesson` không còn `minutes`; thêm `loops_done` (số vòng việc đã chốt).
- `.lop-hoc/vong-viec.json` (giáo viên ghi, schema `lop-hoc/vong-viec-1`): mỗi vòng việc theo khuôn checkpoint của NNC OSER (không phải Mission): việc (lời thường, không tên file), mẫu hay việc thật, 4 ý học viên tự đưa, cách tự kiểm, kết quả (GUIDED … REUSED_IN_WORK), bậc tự chủ, người nhận đã xác nhận chưa, việc kế tiếp.
- `.lop-hoc/phieu-ket-qua.md` (giáo viên ghi khi học viên bấm Phiếu kết quả): một trang, nhãn thường, không mã nội bộ, không tên file, không số liệu.

### 9.4 Kèm việc ở thư mục của học viên

Không cài plugin cho cả máy, không dùng Bypass permissions. Phiên lớp học ở lại thư mục lớp; Claude làm việc ở thư mục khác bằng đường dẫn đầy đủ. Lần đầu truy cập ngoài thư mục lớp hiện hộp xin quyền (thẻ 9). Chế độ việc thật: mọi thao tác trên file thật do học viên bắt đầu; kết quả ghi ra file mới cạnh file nguồn; không chép dữ liệu thật vào thư mục lớp.

### 9.5 Sách tự học

`references/sach-tu-hoc.md` là sách tự học của học viên (bản Word có 11 hình). Giáo viên dạy theo mục tiêu từng phần, dùng sách làm **nguồn chuẩn** và **đường lui**: khi Claude làm không được hoặc màn hình khác, chỉ đúng mục và hình để học viên tự làm theo.

### 9.6 Bổ sung v0.7.1 (rủi ro khi triển khai)

| Tín hiệu / thay đổi | Khi | Giáo viên làm |
|---|---|---|
| `[Giáo án] Hạn mức · context {c}%` | context của phiên chạm 70% (một lần) | khi chốt vòng việc, đề nghị mở phiên mới; lớp khôi phục từ file |
| `[Giáo án] Kiểm phần học · phần {id} · {n} phút` | phần 0 quá 8 phút, phần 1 quá 15 phút (một lần mỗi phần) | đã đạt mốc thì ghi `segment` kế tiếp; chưa thì làm tiếp |
| Phiếu kết quả | — | ghi `Phieu-ket-qua.md` ở thư mục lớp (gói cho phép sửa file này), đọc lại để bỏ tên file, số liệu |
| Làm quen hai chiều | lần gặp đầu | giáo viên tự giới thiệu; hai hộp làm quen; hồ sơ nhỏ ở `trainer.json` `learner` |
| Dữ liệu mẫu | máy không có Python | đọc bằng Excel qua PowerShell, hoặc bản `.csv` đi kèm mỗi file mẫu |

### 9.7 Bổ sung v0.7.2 (song ngữ, cập nhật, người hỗ trợ)

| Thay đổi | Ai làm | Chi tiết |
|---|---|---|
| `state.json` `language`: `vi` · `lo` | giáo viên ghi ngay khi có câu trả lời "Ngôn ngữ" ở hộp làm quen A | mod chuyển chữ trên bục giảng, nút, form Giao việc, dòng công cụ, tiêu đề sang tiếng đó và nhớ trong store cho lần mở sau; cửa lớp chưa biết tiếng thì hiện cả hai |
| Lời giao việc tiếng Lào | mod | bắt đầu `ມອບວຽກ —` (cùng 4 ý: ເປົ້າໝາຍ · ແຫຼ່ງຂໍ້ມູນ · ຜົນທີ່ຕ້ອງການ · ວິທີກວດ); giáo viên xử lý như `Giao việc —` |
| Tín hiệu giữ tiếng Việt | mod | mọi `[Giáo án] …` và `[Lớp học] …` vẫn tiếng Việt ở cả hai tiếng (lý do Xin phép gửi theo bản tiếng Việt), nên bảng tín hiệu không đổi |
| Câu tiếng Lào | người bản ngữ | nằm ở `hooks/i18n.ts` bảng `lo`; cần người bản ngữ duyệt trước khi dùng rộng |
| Cập nhật | gói | `.claude/settings.json` trỏ nhánh `lop-hoc-release` và `autoUpdate: true`; người phát hành đẩy nhánh này tới commit của mỗi tag |
| Người hỗ trợ | người phát hành | điền khi đóng ZIP (`--support` hoặc `.lien-he-ho-tro.txt` đã gitignore); repo giữ dòng trống |
