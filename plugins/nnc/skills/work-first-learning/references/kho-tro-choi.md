# Kho trò chơi — 8 trò hạt giống và luật tự chế (v0.6)

Kho này **mở**: 8 trò dưới đây là hạt giống; giáo viên được tự chế trò mới theo 6 luật ở cuối file. Mỗi trò là một kiểu tương tác `game:{ten}` trong `state.activity.kind` ([nang-luc-giao-vien.md](nang-luc-giao-vien.md) §3.2). Thẻ khả năng dùng trong trò: [tu-kha-nang.md](tu-kha-nang.md). Sao và huy hiệu: [huy-hieu.md](huy-hieu.md). Lời chung khi mở/đóng trò, hết giờ, trao huy hiệu: [tuong-tac.md](tuong-tac.md) T37–T41.

## Luật chung cho mọi trò

- **Một trò ≤ 3 phút**, có **một thao tác chạm được ngay**, có **điều kiện thắng rõ ràng**, kết bằng **một câu bài học** và một nước đi tiếp.
- **Chỉ dữ liệu mẫu**, chép vào `Thuc-hanh/` trước (tu-kha-nang.md §0), trừ khi học viên đồng ý dùng file của mình qua hộp an toàn dữ liệu.
- **Hộp câu hỏi gốc** (`AskUserQuestion`): phương án mặc định **đứng đầu**, an toàn nhất (thường là "Chưa chắc — cô gợi ý"). Hết 60 giây, lớp chọn giúp phương án đầu; với câu đố, phương án đó **không** tính là đúng.
- **Thử thách có giờ — không đặt trong hộp câu hỏi.** Hộp tự đóng sau 60 giây, sẽ đụng đồng hồ thử thách. Mẫu đúng: giáo viên giao việc + ghi `challenge`, kết lượt **không mở hộp**, đặt `one_touch` *"Tôi xong rồi"* để học viên báo xong sớm. Học viên bấm Enter hoặc tới tín hiệu `[Giáo án] Hết giờ thử thách · {title}` → lúc đó mới mở hộp hỏi kết quả.
- **Không có giờ khi học viên đang vấp** (vừa vấp trong phần này, nhánh cần đỡ, năng lượng *Hơi mệt*): chơi bản không đồng hồ, hoặc chọn trò khác.
- **Học viên từ chối trò → tôn trọng ngay** (T46), không thuyết phục; đổi sang một kiểu không phải trò, cùng động lực.
- Ghi khi mở trò: `activity {kind:"game:…", started_at}`; khi đóng: kiểu tương tác tiếp theo khác `game:` vừa chơi (không bắt buộc, nhưng hiếm khi cần hai trò liền).
- Không chế giễu, không xếp hạng người, không so với người khác. Nói về **cách làm**, không nói về con người.

Giọng: **thầy** điềm đạm, có cấu trúc, ít cảm thán; **cô** ấm áp, nhanh, hình ảnh đời thường. Câu tiếng Lào dưới đây **cần người bản ngữ duyệt** trước khi dùng thật.

---

## 1. Đoán xem — `game:doan-xem`

- **Động lực:** D2 (khám phá Claude làm được gì) → khoảnh khắc "À".
- **Khi dùng:** phần 1 giữa hai nhóm thẻ; bất cứ phần nào còn thiếu "À"; khi học viên nghi ngờ "Claude làm được thật không?".
- **Chuẩn bị:** file của thẻ khả năng định dùng đã ở `Thuc-hanh/` (mặc định `bang-tinh-mau.xlsx`).
- **Hộp:**

```json
{ "questions": [ { "header": "Đoán xem", "question": "Claude vẽ được biểu đồ doanh số theo kênh từ bảng vừa đọc không?", "multiSelect": false,
  "options": [ { "label": "Chưa chắc — thử xem", "description": "Bấm nút trên bục để Claude làm thật" },
               { "label": "Có", "description": "Mình đoán là được" },
               { "label": "Không", "description": "Mình đoán là không" } ] } ] }
```

- **one_touch:** lệnh của thẻ khả năng tương ứng, ví dụ `{ "label": "Cho Claude vẽ biểu đồ", "text": "Vẽ biểu đồ cột tổng thành tiền theo kênh từ Thuc-hanh/bang-tinh-mau.xlsx, lưu thành file mới trong Thuc-hanh và cho tôi biết kênh nào cao nhất." }`
- **Có cả câu "Không":** thỉnh thoảng hỏi một việc Claude **không làm trong lớp** để dạy ranh giới — *"Claude tự gửi thư này cho khách được không?"* → trong lớp: không; Claude chỉ soạn nháp, người gửi là mình. Không có one-touch cho câu này; giáo viên giải thích một câu.
- **Thắng:** không có thắng thua — đoán là để vui. Đoán đúng: khen một câu; đoán sai: chính là "À".
- **Sao/huy hiệu:** không (đoán không phải kỹ năng).
- **Câu bài học:** *"Chưa chắc Claude làm được không thì thử trên mẫu — nửa phút là biết."*
- **Cảm xúc:** `lac` (đoán) → `giang` (Claude làm) → `hi` (À).
- **Thầy:** "Một câu đoán trước khi xem: việc này Claude làm được hay không? Chọn rồi mình kiểm bằng việc thật." · đóng: "Vậy là được. Điều cần nhớ: không chắc thì thử trên mẫu."
- **Cô:** "Đoán vui nè: Claude vẽ được biểu đồ từ bảng này không? Chọn đi rồi mình bấm thử liền!" · đóng: "À há, được thật! Lần sau chưa chắc thì cứ thử trên mẫu nhé."
- **Lào:** "ເດົາເບິ່ງ: Claude ແຕ້ມແຜນພູມຍອດຂາຍຕາມຊ່ອງທາງຈາກຕາຕະລາງນີ້ໄດ້ບໍ່?" *(cần người bản ngữ duyệt)*
- **Đổi theo nghề:** kho → "Claude chép phiếu nhận hàng từ ảnh thành bảng được không?" (thẻ 7); kế toán → "Claude chỉ ra chỗ khác nhau giữa hai bảng được không?" (thẻ 3); hành chính → "Claude dịch thông báo này sang tiếng Lào được không?" (thẻ 5).

## 2. Hộp quà khả năng — `game:hop-qua`

- **Động lực:** D2 / D1 (khám phá, gần việc của mình).
- **Khi dùng:** sau khi đúng hai lần liền hoặc thắng một thử thách; khi cần đổi kiểu; khi học viên bấm **Mở hộp quà**. Không mở khi đang dừng vì an toàn dữ liệu hay đang chốt phần.
- **Chuẩn bị:** ghi `gift_box: true` → bục hiện nút **Mở hộp quà**. Học viên bấm → tin `[Lớp học] Mở hộp quà`.
- **Hộp:** 3–4 thẻ từ tu-kha-nang.md, thẻ gần việc học viên **đứng đầu** kèm "(đề xuất)":

```json
{ "questions": [ { "header": "Hộp quà", "question": "Hộp quà có ba thẻ — chị muốn mở thẻ nào?", "multiSelect": false,
  "options": [ { "label": "Chép phiếu thành bảng (đề xuất)", "description": "Claude đọc ảnh phiếu mẫu ra bảng Excel" },
               { "label": "Gộp đơn hàng 3 tuần", "description": "Ba file thành một bảng" },
               { "label": "Dịch thông báo", "description": "Việt sang Lào, giữ nguyên số" } ] } ] }
```

- **one_touch:** lệnh của thẻ được chọn (chép file mẫu trước nếu chưa có).
- **Thắng:** mở được và thấy Claude làm thật.
- **Sao/huy hiệu:** không.
- **Câu bài học:** câu "À" của thẻ đó.
- **Ghi:** `gift_box: false` sau khi mở; bật lại sau một thành tích khác (tối đa 2 lần mỗi buổi để còn thời gian cho việc chính).
- **Cảm xúc:** `lac` → `hi`.
- **Thầy:** "Chị vừa làm đúng hai lần liền. Thầy mở cho chị một hộp quà: ba việc Claude làm được, chị chọn một."
- **Cô:** "Có quà nè! Hộp này có ba thẻ, chị chọn một cái — bấm là thấy Claude làm liền."
- **Lào:** "ມາເປີດກ່ອງຂອງຂວັນກັນ! ເລືອກບັດໜຶ່ງໃບເດີ້." *(cần người bản ngữ duyệt)*
- **Đổi theo nghề:** chọn ba thẻ theo bảng "Chọn thẻ theo việc" trong tu-kha-nang.md §1.

## 3. Thử thách 60 giây — `game:thu-thach-60s`

- **Động lực:** D3 (hồi hộp, làm nhanh mà vẫn kiểm).
- **Khi dùng:** học viên đang thuận tay (đúng hai lần liền), nhánh vững hoặc đang lên ở phần 3, sau *Nhanh hơn được*. **Không** khi vừa vấp, nhánh cần đỡ, hay *Hơi mệt*.
- **Chuẩn bị:** `bang-tinh-mau-tuan-sau.xlsx` → `Thuc-hanh/` (học viên mở trong Excel hoặc đọc kết quả Claude vừa đưa).
- **Mở:** giao việc bằng một câu, ghi `challenge: { "title": "Tìm chỗ khác của file tuần sau", "seconds": 60 }` và `one_touch: { "label": "Tôi xong rồi", "text": "Tôi xong thử thách rồi, mời cô chấm." }` (thầy: "mời thầy chấm"). Kết lượt, **không mở hộp**.
- **Hộp kết quả** (khi học viên bấm Enter hoặc tới `Hết giờ thử thách`):

```json
{ "questions": [ { "header": "Kết quả", "question": "Mình tìm được những chỗ khác nào?", "multiSelect": true,
  "options": [ { "label": "Chưa thấy — cô gợi ý", "description": "Cô chỉ chỗ đầu tiên" },
               { "label": "Cột đổi tên", "description": "Một tiêu đề cột khác tuần trước" },
               { "label": "Dòng thiếu giá", "description": "Có ô giá để trống" },
               { "label": "Trùng dòng hoặc lệch đơn vị", "description": "Một dòng lặp lại hoặc khác đơn vị" } ] } ] }
```

- **Thắng:** chọn đúng ít nhất **2** loại khác biệt có thật (đối chiếu `assets/mau/README.md`). Ba loại trong hộp đều có thật trong file này; chọn *Chưa thấy* thì giáo viên gợi ý, không tính thua.
- **Sao/huy hiệu:** thắng → ★ +1; lần thắng thử thách có giờ đầu tiên → huy hiệu `nhanh-tay`.
- **Câu bài học:** *"File đổi thì kiểm cấu trúc trước, rồi mới tin con số tổng."*
- **Ghi:** `challenge: null` khi công bố; `one_touch: null`.
- **Cảm xúc:** `lac` (mở) → `nghe` (chờ) → `hi` (thắng) / `ai` (chưa thắng: "mình xem cùng nhau").
- **Thầy:** mở: "Sáu mươi giây. Một nhiệm vụ: tìm những chỗ file tuần sau khác tuần này. Xong sớm thì bấm nút trên bục." · hết giờ: "Hết giờ. Chị tìm được gì, mình đối chiếu."
- **Cô:** mở: "Thử thách 60 giây nè! Soi file tuần sau xem khác tuần này chỗ nào — xong sớm bấm *Tôi xong rồi* nha!" · hết giờ: "Hết giờ rồi! Chị bắt được mấy chỗ, kể cô nghe."
- **Lào:** "ສິ່ງທ້າທາຍ 60 ວິນາທີ — ເລີ່ມໄດ້!" *(cần người bản ngữ duyệt)*
- **Đổi theo nghề:** kho → "Tìm dòng phiếu chép sai số lượng" (thẻ 7, 90 giây); kế toán → "Tìm dòng có trong file gộp mà không có trong file tuần" (thẻ 2).

## 4. Người với máy — `game:nguoi-voi-may`

- **Động lực:** D1 (thấy giá trị thật của việc giao cho Claude) + tự kiểm.
- **Khi dùng:** phần 2 khi bảng tổng hợp đã có; vòng "em làm" thứ hai ở buổi 45 phút; khi học viên nghi "tự làm cũng nhanh mà".
- **Chuẩn bị:** `Thuc-hanh/bang-tinh-mau.xlsx` (học viên mở trong Excel).
- **Mở:** học viên cộng tay **một kênh** (OTC, 14 dòng: lọc cột Kênh, chọn cột Thành tiền, nhìn tổng ở thanh trạng thái). `challenge: { "title": "Cộng tay kênh OTC", "seconds": 120 }`, `one_touch: { "label": "Tôi xong rồi", "text": "Tôi cộng xong kênh OTC rồi, mời cô so với Claude." }`. Claude đã làm cả ba kênh (hoặc làm ngay bằng thẻ 1).
- **Hộp kết quả:**

```json
{ "questions": [ { "header": "So kết quả", "question": "Số chị cộng tay cho kênh OTC có khớp số của Claude không?", "multiSelect": false,
  "options": [ { "label": "Chưa cộng xong", "description": "Cô chỉ cách cộng nhanh trong Excel" },
               { "label": "Khớp", "description": "Hai con số bằng nhau" },
               { "label": "Lệch", "description": "Mình cùng tìm chỗ lệch" } ] } ] }
```

- **Thắng:** số của học viên khớp số của Claude (20.950.000 LAK). Cả "người" và "máy" cùng thắng: máy nhanh, người kiểm chắc.
- **Sao/huy hiệu:** khớp → ★ +1; nếu học viên dùng chính phép cộng tay này để kiểm kết quả của mình → `tu-kiem-co-tam` (khi chưa có).
- **Câu bài học:** *"Máy làm nhanh cả bảng, người cộng tay một kênh để kiểm — đó là cách kiểm rẻ nhất."*
- **Cảm xúc:** `lac` → `nghe` → `hi`.
- **Thầy:** "Thầy đề nghị một phép so: chị cộng tay một kênh, Claude làm cả ba. Rồi mình so thời gian và con số."
- **Cô:** "Người với máy nè! Chị cộng tay kênh OTC, Claude làm cả bảng — xem ai nhanh, và quan trọng hơn: có khớp không!"
- **Lào:** "ຄົນກັບເຄື່ອງ: ເອື້ອຍບວກດ້ວຍມືຊ່ອງທາງ OTC, Claude ເຮັດທັງໝົດ — ມາທຽບກັນ!" *(cần người bản ngữ duyệt)*
- **Đổi theo nghề:** kho → đếm tay số dòng của một mã hàng trong phiếu; kế toán → cộng tay tổng một tuần trong file gộp.

## 5. Tìm lỗi — `game:tim-loi`

- **Động lực:** D3 (thói quen tự kiểm).
- **Khi dùng:** phần 3 nhánh đang lên; sau khi học viên tin ngay một kết quả không kiểm (T17 rồi chơi); bất cứ lúc nào cần luyện mắt kiểm.
- **Chuẩn bị:** `tim-loi/bang-tim-loi.xlsx` → `Thuc-hanh/tim-loi/`. **Đọc trước** `<base>/assets/mau/tim-loi/dap-an-tim-loi.md` (không chép, không cho học viên xem). Biến thể: giáo viên tự cài 3 lỗi vào một **bản sao** trong `Thuc-hanh/` — chỉ trên mẫu, ghi danh sách lỗi trong hội thoại trước khi học viên tìm.
- **Đáp án (giáo viên, không đọc to):** 25 dòng, **đúng 3 lỗi** mỗi lỗi một kiểu — dòng 7 kênh "OCT" (đúng là OTC); dòng 15 thành tiền 785.000 thay vì 25 × 35.000 = 875.000; dòng 21 ngày 24/11/2026 nằm ngoài tuần 19–24/10/2026.
- **Hộp 1 (soát theo loại — gợi hướng, không lộ dòng):**

```json
{ "questions": [ { "header": "Tìm lỗi", "question": "Bảng có 3 lỗi cài sẵn. Mình soát loại nào trước?", "multiSelect": false,
  "options": [ { "label": "Chưa biết — cô gợi ý", "description": "Cô chỉ cột nên nhìn trước" },
               { "label": "Soát mã kênh", "description": "Kênh chỉ có OTC, HC, SPM" },
               { "label": "Soát phép tính", "description": "Thành tiền = Số lượng × Đơn giá" },
               { "label": "Soát ngày", "description": "Ngày phải nằm trong tuần của bảng" } ] } ] }
```

  Học viên có thể nhờ Claude soát đúng loại đã chọn bằng một chạm (*"Soát cột Kênh trong Thuc-hanh/tim-loi/bang-tim-loi.xlsx, chỉ ra dòng có mã kênh lạ"*), rồi **tự mở dòng đó ra xem**.
- **Hộp 2 (dòng cụ thể):** giáo viên dựng từ đáp án — phương án đầu "Chưa chắc — cô gợi ý", rồi "Dòng 7", "Dòng 15", "Dòng 21" xen một dòng đúng làm nhiễu (tối đa 4 phương án; hỏi tiếp lượt sau nếu cần). Học viên nói được **vì sao** dòng đó sai.
- **Thắng:** tìm đủ **3 lỗi** và nói được vì sao, trong 3 phút (theo đáp án của lớp). Tìm được 1–2 lỗi: vẫn có sao cho mỗi lỗi, giáo viên chỉ nốt phần còn lại.
- **Sao/huy hiệu:** ★ +1 cho mỗi lỗi tìm đúng kèm lý do, tối đa 3 mỗi lượt chơi. (Huy hiệu `mat-tinh` dành cho lỗi **của Claude** trong việc thật, không trao ở trò này.)
- **Câu bài học:** *"Nhờ Claude soát từng loại lỗi một — mã, phép tính, ngày — rồi tự xem lại đúng các dòng nó chỉ ra: kiểm trước khi tin."*
- **Cảm xúc:** `lac` → `nghe` → `hi`.
- **Thầy:** "Bảng này có lỗi cài sẵn. Thầy không nói có mấy lỗi. Chị soát từng cột, chọn loại lỗi chị thấy."
- **Cô:** "Trò tìm lỗi nè! Cô giấu vài lỗi trong bảng mẫu — chị làm thám tử nhé, soi kỹ cột giá với cột đơn vị!"
- **Lào:** "ຕາຕະລາງນີ້ມີຂໍ້ຜິດພາດທີ່ຄູເຊື່ອງໄວ້ — ລອງຊອກເບິ່ງ!" *(cần người bản ngữ duyệt)*
- **Đổi theo nghề:** kho → lỗi số lượng/đơn vị trong bảng chép từ phiếu; kế toán → dòng trùng, số âm lạ trong bảng đối chiếu mẫu; hiện trường → vật tư ghi sai đơn vị.

## 6. Bạn là sếp — `game:ban-la-sep`

- **Động lực:** D3 (dám kiểm, dám trả lại).
- **Khi dùng:** bước tự kiểm của phần 2 (thay cho hai hộp kiểm thường, trên kết quả của chính học viên); phần 3; khi cần đổi kiểu từ `hands-on`.
- **Chuẩn bị:** bản mẫu `ban-la-sep/ket-qua-claude-mau.xlsx` (bảng tổng hợp theo kênh "như thể Claude làm" từ `bang-tinh-mau.xlsx`) → `Thuc-hanh/ban-la-sep/`, cùng file nguồn `Thuc-hanh/bang-tinh-mau.xlsx`. Đọc trước `<base>/assets/mau/ban-la-sep/dap-an.md` (không chép). Hoặc dùng kết quả học viên vừa làm ở phần 2.
- **Đáp án bản mẫu (giáo viên, không đọc to):** **Trả lại**, hai lý do — tổng thành tiền HC ghi 43.250.000, đúng là 44.200.000 (OTC + HC + SPM = 100.920.000 không bằng dòng Tổng cộng 101.870.000: sếp thấy được mà không cần mở nguồn); và phần Ghi chú thiếu nguồn, kỳ dữ liệu.
- **Hộp:** phương án đầu là an toàn nhất; lý do "Trả lại" gồm lý do đúng và một lý do nhiễu:

```json
{ "questions": [ { "header": "Bạn là sếp", "question": "Chị là sếp: duyệt bảng tổng hợp này thế nào?", "multiSelect": false,
  "options": [ { "label": "Chưa duyệt — kiểm đã", "description": "Cộng ba kênh, so với dòng Tổng cộng, đọc ghi chú" },
               { "label": "Đạt", "description": "Ký duyệt kết quả" },
               { "label": "Trả lại: tổng một kênh sai", "description": "Ba kênh cộng lại không ra tổng cộng" },
               { "label": "Trả lại: sai tên kênh", "description": "Tên kênh không đúng OTC, HC, SPM" } ] } ] }
```

  *Chưa duyệt — kiểm đã* → giáo viên đưa bước kiểm (`hands-on`: cộng ngang ba kênh, đối chiếu tổng, đọc ghi chú) rồi hỏi lại. "Other" để học viên tự viết thêm lý do (ví dụ thiếu ghi chú nguồn).
- **Thắng:** kết luận đúng **kèm lý do đúng** (bản mẫu: *Trả lại: tổng một kênh sai*; nói thêm được "thiếu ghi chú nguồn" là trọn vẹn; với kết quả đúng của học viên: *Đạt* sau khi đã kiểm).
- **Sao/huy hiệu:** ★ +1; lần đầu trả lại đúng một kết quả sai kèm lý do → huy hiệu `ban-la-sep`.
- **Câu bài học:** *"Sếp giỏi không làm lại từ đầu — kiểm vài chỗ then chốt (cộng ngang, đối chiếu tổng, đọc ghi chú) rồi mới ký."*
- **Cảm xúc:** `lac` → `nghe` → `hi`; học viên bấm *Đạt* mà chưa kiểm một kết quả có lỗi → `o` nhẹ với cách làm (T17), rồi mời kiểm 3 dòng.
- **Thầy:** "Bây giờ chị là sếp. Claude nộp bảng này. Chị ký hay trả lại — và vì sao?"
- **Cô:** "Chị làm sếp nè! Claude vừa nộp bài, chị duyệt hay trả lại? Sếp được quyền khó tính đó!"
- **Lào:** "ຕອນນີ້ເອື້ອຍເປັນຫົວໜ້າ: ຈະອະນຸມັດ ຫຼື ສົ່ງຄືນ?" *(cần người bản ngữ duyệt)*
- **Đổi theo nghề:** kho → duyệt bảng nhập kho chép từ phiếu; bán hàng → duyệt báo cáo doanh số kênh; kế toán → duyệt bảng đối chiếu mẫu.

## 7. Đúng/sai chuỗi — `game:dung-sai`

- **Động lực:** D2 (nhớ lâu 9 thẻ).
- **Khi dùng:** vé vào lớp (cuối phần 1); nhớ lại đầu buổi sau; khi cần một kiểu nhanh, vui giữa hai phần làm.
- **Chuẩn bị:** câu nhớ lại trong [the-dinh-nghia.md](the-dinh-nghia.md), hoặc câu khẳng định Đúng/Sai dựng **đúng theo nội dung thẻ**.
- **Hộp:** một hộp 3 câu. Dạng câu nhớ lại (phương án đầu luôn *"Chưa chắc — cô nhắc lại"*, rồi ba đáp án) hoặc dạng Đúng/Sai:

```json
{ "questions": [
  { "header": "Câu 1", "question": "Đúng hay sai: Claude chỉ thấy file trong thư mục làm việc đã mở.", "multiSelect": false,
    "options": [ { "label": "Chưa chắc — cô nhắc lại", "description": "Cô nói lại thẻ trong 30 giây" },
                 { "label": "Đúng", "description": "Câu này đúng" }, { "label": "Sai", "description": "Câu này sai" } ] },
  { "header": "Câu 2", "question": "Đúng hay sai: claude.ai và Claude Code có hạn mức riêng, không ảnh hưởng nhau.", "multiSelect": false,
    "options": [ { "label": "Chưa chắc — cô nhắc lại", "description": "Cô nói lại thẻ trong 30 giây" },
                 { "label": "Đúng", "description": "Câu này đúng" }, { "label": "Sai", "description": "Câu này sai" } ] },
  { "header": "Câu 3", "question": "Đúng hay sai: hộp xin quyền hiện ra thì cứ bấm đồng ý cho nhanh.", "multiSelect": false,
    "options": [ { "label": "Chưa chắc — cô nhắc lại", "description": "Cô nói lại thẻ trong 30 giây" },
                 { "label": "Đúng", "description": "Câu này đúng" }, { "label": "Sai", "description": "Câu này sai" } ] } ] }
```

  Đáp án: 1 Đúng · 2 Sai (dùng chung hạn mức) · 3 Sai (đọc rồi mới đồng ý). Câu khác dùng được: "Việc mới thì nên mở phiên mới" (Đúng) · "Có một số tin nhắn cố định cho mỗi 5 giờ" (Sai). **Không** dùng câu về lúc bắt đầu cửa sổ 5 giờ.
- **Thắng:** đúng **3 câu liên tiếp**.
- **Sao/huy hiệu:** chuỗi 3 đúng → ★ +1 (tối đa 2 chuỗi mỗi buổi). Ghi sổ định nghĩa như the-dinh-nghia.md (tối đa +2 lần nhớ đúng mỗi thẻ mỗi buổi). Huy hiệu `thuoc-9-the` chỉ khi sổ định nghĩa cho thấy cả 9 thẻ đã thuộc — không trao từ một chuỗi.
- **Câu bài học:** câu sai nào → nhắc lại thẻ đó ≤ 30 giây; kết: *"Ba câu, ba thẻ — mình mang theo khi làm việc thật."*
- **Cảm xúc:** `lac` → `hi` / `giang` (nhắc lại).
- **Thầy:** "Ba câu đúng hay sai, trả lời liền một mạch. Đúng cả ba, thầy tặng một sao."
- **Cô:** "Đúng sai chớp nhoáng nè! Ba câu liền mà đúng hết là có sao nha!"
- **Lào:** "ສາມຄຳຖາມ ຖືກ ຫຼື ຜິດ — ຖືກໝົດໄດ້ດາວໜຶ່ງດວງ!" *(cần người bản ngữ duyệt)*
- **Đổi theo nghề:** giữ nội dung thẻ, đổi ví dụ trong câu: kho → "chép phiếu vào thư mục làm việc"; kế toán → "file đối chiếu ở ổ khác".

## 8. Đổi vai — `game:doi-vai`

- **Động lực:** D3 + kết nối (hiểu sâu, tự hào).
- **Khi dùng:** sau khi học viên vừa làm xong một bước tốt (tự kiểm, giao việc 4 ý); phần 3 nhánh vững; cuối phần 2 nếu còn thời gian.
- **Chuẩn bị:** không cần file. Giáo viên đóng vai **đồng nghiệp mới** (vẫn là giáo viên AI, nói rõ là đang đóng vai).
- **Mở:** `next_action: "Kể cô nghe: chị dạy cô bước tự kiểm"`. Học viên viết trong ô **Kể cô nghe** (chỗ được phép gõ tự do).
- **Bản không cần gõ** (học viên ngại gõ): hộp *"Chị sẽ nói câu nào với đồng nghiệp mới?"* — **Chưa nghĩ ra — cô gợi ý** (đầu) · ba câu giải thích, một câu đúng trọng tâm. Bản này chỉ được sao, không được huy hiệu.
- **Thắng:** lời giải thích của học viên có đủ ý chính của bước (với tự kiểm: đối chiếu với **nguồn**, và **bao nhiêu** dòng/kênh).
- **Sao/huy hiệu:** ★ +1; lần đầu dạy lại đúng bằng lời của mình → huy hiệu `nguoi-day-lai`.
- **Câu bài học:** *"Dạy lại được là hiểu thật."*
- **Cảm xúc:** `nghe` (giáo viên làm "học trò") → `hi`.
- **Thầy:** "Đổi vai một chút: thầy là nhân viên mới, chị là người hướng dẫn. Chị dạy thầy cách kiểm bảng tổng hợp này."
- **Cô:** "Mình đổi vai nha: giờ cô là lính mới, chị dạy cô bước tự kiểm đi — cô ghi chép đàng hoàng!"
- **Lào:** "ມາປ່ຽນບົດບາດກັນ: ຄູເປັນພະນັກງານໃໝ່, ເອື້ອຍສອນຄູແດ່." *(cần người bản ngữ duyệt)*
- **Đổi theo nghề:** kho → dạy cách soát phiếu với bảng; bán hàng → dạy cách giao việc 4 ý cho báo cáo tuần; kế toán → dạy cách đối chiếu tổng kiểm soát.

---

## Tự chế trò mới

Khi kho không có trò hợp (fit test ở [nang-luc-giao-vien.md](nang-luc-giao-vien.md) §5), giáo viên **được tự chế**. Trước khi mở trò, chạy hết danh sách sau — thiếu một ý là chưa được chơi.

### Danh sách kiểm 6 luật

- [ ] **1. Gắn một động lực** (D1, D2 hoặc D3) và đúng phần học đang diễn ra.
- [ ] **2. Có một thao tác chạm được ngay**: bấm một phương án, Enter một lệnh một chạm, hoặc nút trên bục.
- [ ] **3. Điều kiện thắng rõ ràng** (nói được trong một câu) và **kết thúc trong 3 phút** (có giờ thì `seconds` ≤ 120).
- [ ] **4. Chỉ dữ liệu mẫu** trong `Thuc-hanh/`, trừ khi học viên đã đồng ý dùng file của mình qua hộp an toàn dữ liệu.
- [ ] **5. Kết bằng một câu bài học** và một nước đi tiếp theo đã nghĩ sẵn.
- [ ] **6. Không chế giễu, không xếp hạng người, không áp lực thời gian khi học viên đang vấp.**

Thêm: đặt tên `game:{ten-kebab-case}`, hộp có mặc định đứng đầu, không lộ đáp án trước, không từ nội bộ.

### Ví dụ 1 — Kho: "Soát phiếu" — `game:soat-phieu`

- **Học viên:** thủ kho, hằng ngày gõ phiếu nhận hàng vào Excel.
- **Cách chơi:** học viên bấm Enter thẻ 7 (Claude chép `Thuc-hanh/phieu-nhan-hang-mau.png` thành bảng). Giáo viên sửa **một** số lượng trong một bản sao của bảng đó (chỉ trên mẫu, ghi lại dòng đã sửa trong hội thoại). Học viên so ảnh với bảng, chọn dòng sai trong hộp (*Chưa chắc — cô gợi ý* đầu, rồi 3 dòng).
- **Kiểm 6 luật:** 1 D3, phần 2 hoặc 3 ✓ · 2 Enter + một lựa chọn ✓ · 3 thắng = chọn đúng dòng bị sửa, ≤ 3 phút ✓ · 4 ảnh phiếu mẫu ✓ · 5 *"Chép từ ảnh xong luôn soát số lượng với phiếu gốc."* → nước tiếp: học viên tự giao việc chép phiếu với cách kiểm của mình ✓ · 6 không giờ, không so người ✓.
- **Sao:** ★ +1 khi tìm đúng.

### Ví dụ 2 — Bán hàng OTC: "Gọi ai trước?" — `game:goi-ai-truoc`

- **Học viên:** sale OTC, sáng nào cũng chọn nhà thuốc để gọi chăm sóc.
- **Cách chơi:** hộp: *"Hôm nay ưu tiên gọi khách theo tiêu chí nào?"* — **Chưa chắc — cô gợi ý** · Thành tiền tuần này lớn nhất · Số đơn nhiều nhất. Học viên chọn tiêu chí → `one_touch` *"Xếp các khách kênh OTC trong Thuc-hanh/bang-tinh-mau.xlsx theo {tiêu chí}, cho tôi 3 khách đầu kèm con số."* → học viên mở file, kiểm khách thứ nhất bằng tay.
- **Kiểm 6 luật:** 1 D1, phần 2 ✓ · 2 một lựa chọn + Enter ✓ · 3 thắng = con số của khách đầu danh sách khớp khi học viên tự lọc, ≤ 3 phút ✓ · 4 bảng mẫu ✓ · 5 *"Mình đặt tiêu chí, Claude xếp, mình kiểm một dòng."* → nước tiếp: giao việc 4 ý cho danh sách gọi tuần sau ✓ · 6 không giờ, không xếp hạng người (xếp khách mẫu, không xếp nhân viên) ✓.
- **Sao:** ★ +1 khi khớp; nếu học viên tự đề xuất kiểm thêm một khách → có thể là `tu-kiem-co-tam`.

### Ví dụ 3 — Kế toán: "Tổng kiểm soát" — `game:tong-kiem-soat`

- **Học viên:** kế toán, hay gộp số liệu nhiều tuần rồi đối chiếu.
- **Cách chơi:** học viên bấm Enter thẻ 2 (gộp 3 file tuần trong `Thuc-hanh/gop/`). Hộp: *"Kiểm file gộp cách nào chắc nhất?"* — **Chưa chắc — cô gợi ý** · Cộng tổng từng file rồi so với tổng file gộp · Nhìn lướt thấy đủ dòng là được · Đếm số cột. Chọn đúng → học viên đọc ba tổng Claude báo (58.475.000 · 67.550.000 · 68.060.000 LAK) và tổng file gộp (194.085.000 LAK), chọn *Khớp / Lệch*.
- **Kiểm 6 luật:** 1 D3, phần 3 ✓ · 2 Enter + lựa chọn ✓ · 3 thắng = chọn đúng cách kiểm và đối chiếu ra kết luận đúng, ≤ 3 phút ✓ · 4 file mẫu, **không** dùng công nợ thật ✓ · 5 *"Gộp xong luôn đối chiếu tổng kiểm soát."* → nước tiếp: thêm bước tổng kiểm soát vào lời giao việc của học viên ✓ · 6 không giờ, không so người ✓.
- **Sao:** ★ +1; lần đầu tự kiểm đúng cách → `tu-kiem-co-tam`.

### Đề xuất trò hay cho người đào tạo

Trò tự chế chạy tốt (học viên chạm ngay, đạt điều kiện thắng hoặc học được câu bài học, không gượng ép) → thêm một mục vào `.lop-hoc/trainer.json`:

```json
{ "games_proposed": [ { "name": "game:soat-phieu", "why": "Thủ kho: chép phiếu mẫu rồi tìm 1 dòng bị sửa; học viên tìm đúng trong 2 phút, tự xin làm thêm lần nữa." } ] }
```

- `why` mô tả **cách chơi và điều quan sát được** trong một câu; không tên học viên, không dữ liệu thật, không lời học viên.
- Giáo viên **chỉ đề xuất**: không bao giờ sửa file kho này hay bất kỳ file nào của Skill. Người đào tạo quyết định đưa vào kho ở bản sau.
