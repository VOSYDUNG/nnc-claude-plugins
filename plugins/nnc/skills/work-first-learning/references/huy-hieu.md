# Huy hiệu và sao (v0.6)

Ghi nhận **hành vi thật** của học viên — điều giáo viên đã thấy trong buổi — để học viên tự hào và nhớ thói quen tốt. Không phải điểm số, không phải xếp hạng.

## Nguyên tắc

- **Chỉ trao theo hành vi quan sát được** trong buổi này. Không trao theo cảm tưởng, theo lời học viên tự kể mà không có bằng chứng, hay theo thời gian ngồi lớp.
- **Không bao giờ có huy hiệu hay sao cho số lần bấm**, số tin nhắn, số phút, việc có mặt, hay việc chọn phương án mặc định / hết giờ.
- **Không xếp hạng người với người.** Không bảng xếp hạng, không so với học viên khác, không "giỏi nhất lớp". Nói về cách làm, không chấm con người.
- Mỗi huy hiệu chỉ trao **một lần** cho mỗi học viên (đọc `.lop-hoc/huy-hieu.json` trước; đã có thì chỉ khen hành vi). Một khoảnh khắc chỉ trao **một** huy hiệu — chọn cái sát hành vi nhất.
- Trao ngay khi thấy hành vi, kèm **một câu khen cụ thể** (T40). Không trao lúc học viên đang dừng vì an toàn dữ liệu hay đang buồn vì vấp — đợi lúc gỡ được.
- Học viên thấy huy hiệu trên bục giảng (lớp chép từ `badges_new` sang `.lop-hoc/huy-hieu.json`); người đào tạo đọc cùng file đó.

**Cách ghi (model instruction):** write `badges_new: [{ "id": "<id>", "label": "<label>" }]` in `.lop-hoc/state.json` with only the badge just earned; set `badges_new: []` on your next state write. Never write `.lop-hoc/huy-hieu.json` yourself — the classroom merges it (dedupe by `id`) and shows the toast.

## Danh mục huy hiệu

| id | Nhãn | Hành vi quan sát được để trao | Không trao khi |
|---|---|---|---|
| `giao-viec-dau-tien` | Người giao việc đầu tiên | Học viên **tự soạn** lời giao việc đầu tiên đủ 4 ý (Mục tiêu · Nguồn · Đầu ra · Cách kiểm) — qua form hoặc lời của mình — và Claude làm được việc đó | Học viên chỉ bấm Enter một lệnh giáo viên đã điền sẵn; thiếu *Cách kiểm*; việc không chạy |
| `mat-tinh` | Mắt tinh | Học viên **bắt được một lỗi thật của Claude** (hoặc của giáo viên) trong buổi — con số, dòng, cách hiểu sai — và chỉ ra được bằng nguồn | Lỗi cài sẵn trong trò Tìm lỗi (được sao, không phải huy hiệu này); học viên nói "sai rồi" nhưng thực ra kết quả đúng |
| `thuoc-9-the` | Thuộc 9 thẻ | Sổ định nghĩa (`trainer.json` `concepts`) cho thấy **cả 9 thẻ** đã thuộc: mỗi thẻ 3 lần nhớ lại đúng qua ít nhất 2 ngày khác nhau | Trong ngày học đầu tiên (không thể đủ điều kiện); thắng một chuỗi Đúng/sai; vé vào lớp 3/3 |
| `tu-kiem-co-tam` | Tự kiểm có tâm | Học viên **tự kiểm** một kết quả với nguồn bằng cách cụ thể (ít nhất 3 dòng, hoặc cộng tay một kênh) **trước khi** nhận dùng, và báo lại kết quả kiểm | Bấm *Khớp* mà chưa thực sự kiểm; chọn mặc định do hết giờ; giáo viên làm hộ phần kiểm |
| `nguoi-day-lai` | Người dạy lại | Trong **Đổi vai**, học viên giải thích đúng một bước **bằng lời của mình**, đủ ý chính | Bản chọn phương án (không gõ) — chỉ được sao; lời giải thích thiếu ý chính |
| `dong-goi-skill-dau-tien` | Đóng gói Skill đầu tiên | Skill nháp của học viên có đủ 4 ý, học viên **đã đọc và sửa hoặc duyệt** một điểm, và nó được **chạy thử trên một file khác** có kiểm | Chỉ xem Skill mẫu của lớp; Skill do giáo viên viết mà học viên chưa đọc; chưa chạy thử |
| `ban-la-sep` | Bạn là sếp | Trong **Bạn là sếp** (hoặc với kết quả thật), học viên **trả lại một kết quả sai kèm lý do đúng** | Bấm *Đạt* đúng nhưng chưa kiểm; trả lại mà lý do sai; chọn mặc định |
| `nhanh-tay` | Nhanh tay | **Thắng một thử thách có giờ**: kết quả đúng trong thời gian (ví dụ Thử thách 60 giây) | Nhanh mà sai; thắng nhờ giáo viên gợi ý gần hết đáp án; buổi học viên đang vấp (khi đó không có thử thách có giờ) |
| `giu-an-toan-du-lieu` | Giữ dữ liệu an toàn | Học viên **tự nhận ra** file có thông tin nhạy cảm (khách hàng, giá vốn, công nợ, lương) và **tự chọn** che hoặc dùng mẫu **trước khi** Claude mở | Giáo viên phải dừng học viên (T16); học viên chỉ chọn phương án mặc định "dùng mẫu" mà không nhận ra gì |
| `tu-viet-loi-giao` | Tự viết lời giao việc | Học viên viết trọn lời giao việc **không dùng form**, có ít nhất 3 trong 4 ý, việc chạy đúng | Chép lại nguyên văn ví dụ của giáo viên; cần giáo viên viết lại |
| `viec-that-cua-toi` | Việc thật của tôi | Học viên mang **file việc thật của mình** (đã che thông tin nhạy cảm, đã qua hộp an toàn dữ liệu) và hoàn thành một kết quả **có tự kiểm** trên đó trong lớp | Dùng file mẫu; file còn dữ liệu nhạy cảm; chưa kiểm |

Màu nhóm trên bục (lớp tự chọn theo `id`): việc thật · kiểm · giao việc · hiểu sâu. Giáo viên không cần biết màu.

## Sao trong buổi

Sao là phần thưởng nhỏ **trong một buổi** (`state.stars`). Mỗi lần mở lớp (`Mở lớp`) đặt `stars: 0`. Sao **không bao giờ bị trừ** và không ghi vào `trainer.json`.

| +1 sao khi | Giới hạn |
|---|---|
| Đúng **3 câu liên tiếp** trong Đúng/sai chuỗi (hoặc vé vào lớp 3/3) | tối đa 2 chuỗi mỗi buổi |
| **Thắng một thử thách** (Thử thách 60 giây, Người với máy khớp số, trò tự chế có điều kiện thắng) | mỗi thử thách một sao |
| **Bắt được một lỗi** có thật (Tìm lỗi, Soát phiếu, lỗi của Claude) | tối đa 3 sao mỗi lượt Tìm lỗi |
| Kết luận đúng kèm lý do đúng trong **Bạn là sếp** | mỗi lượt một sao |
| Dạy lại đúng trong **Đổi vai** (cả bản chọn phương án) | mỗi lượt một sao |

**Không có sao** cho: đoán trong Đoán xem, mở hộp quà, bấm Enter một lệnh một chạm, chọn mặc định hay hết giờ, có mặt, nhanh mà sai.

Nói về sao ngắn gọn, một câu, không đếm thành "điểm": *"Thêm một sao cho cú bắt lỗi đó!"* Cuối buổi có thể nhắc số sao như một kỷ niệm của buổi, không so với ai.

## Gợi ý trao trong Buổi 1

| Phần | Huy hiệu hay gặp (nếu hành vi xảy ra) |
|---|---|
| 2 · Việc thật | `giao-viec-dau-tien` (khi học viên tự điền form), `tu-kiem-co-tam`, `giu-an-toan-du-lieu`, `viec-that-cua-toi`, `mat-tinh` |
| 3 · Thử thách | `nhanh-tay`, `ban-la-sep`, `dong-goi-skill-dau-tien`, `nguoi-day-lai`, `tu-viet-loi-giao` |
| 4 · Tổng kết | nhắc lại huy hiệu và sao hôm nay; không trao mới chỉ để "cho có" |

Một buổi không có huy hiệu nào là bình thường — đừng tạo hành vi giả để trao.
