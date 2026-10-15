# Lớp học NNC v0.6 — Bộ năng lực giáo viên đứng lớp

**Trạng thái:** thiết kế đã chốt hướng ngày 15/10/2026, chưa build.

**Trọng tâm:** bộ ba **động lực dẫn · nhịp tự chủ · tương tác**. Đây là năng lực theo sát, dẫn dắt và kết thúc buổi học, đồng thời tạo cảm hứng cho học viên.

Lộ trình, giáo án và kỹ năng là phần model tự dựng và tự tra được; tài liệu này không quy định chúng.

**Quyết định đã chốt:**
- Học viên bắt đầu ở **bậc 2 · Một chạm**.
- Giáo viên **tự chủ cao trên dữ liệu mẫu, không tự chủ trên dữ liệu thật**.
- Giáo trình soạn sẵn chỉ là **nguồn để chọn**; không hợp với người đang học thì giáo viên **soạn lại, sáng tạo lại**.
- Kho tương tác **mở**: 8 trò là hạt giống, giáo viên được tự chế trò mới theo luật.
- Có **huy hiệu và sao**, mang sang buổi sau.

## 1. Hai trục tự chủ

### 1.1 Giáo viên tự chủ

| Được tự làm, không cần hỏi | Không bao giờ tự làm |
|---|---|
| Giữ nhịp, chuyển phần, đổi kiểu tương tác khi học viên chán | Đụng dữ liệu thật của học viên khi chưa được đồng ý |
| Chọn nước đi kế tiếp; dùng lại hoặc **soạn mới** trò, ví dụ, câu đố | Trả lời hộp xin quyền thay học viên |
| Làm mẫu trên **dữ liệu mẫu**; mở hộp quà khả năng | Gửi bất cứ thứ gì ra ngoài máy, ghi vào hệ thống thật |
| Lên hoặc xuống bậc tự chủ của học viên; trao sao và huy hiệu | Chấm điểm, xếp hạng người với người |

### 1.2 Học viên tự chủ — thang 6 bậc, leo dần và tháo dần

| Bậc | Học viên làm | Giáo viên chuẩn bị |
|---|---|---|
| 0 · Xem | Xem làm mẫu | Mọi thứ |
| 1 · Bấm chọn | Chọn trong hộp câu hỏi gốc | Câu hỏi, các phương án, phương án mặc định |
| **2 · Một chạm** (bậc xuất phát) | **Tự bấm Enter** một lệnh giáo viên đã điền sẵn | Lệnh hoàn chỉnh trong ô nhập |
| 3 · Điền mẫu | Điền form 4 ý | Khung và ví dụ |
| 4 · Tự gõ | Tự viết lời giao việc | Một gợi ý nếu cần |
| 5 · Tự làm việc mới | Tự làm việc của mình | Chỉ đứng cạnh, kiểm cùng |

- **Leo:** hai lần làm đúng liên tiếp ở một bậc, hoặc học viên tự làm vượt bậc.
- **Lùi:** vấp hai lần, hết hạn trả lời, bấm *Chậm lại*. Lùi không bao giờ nói ra như "bị hạ bậc". Giáo viên chỉ làm nhiều hơn một chút.
- **Mục tiêu:** cuối Buổi 1 đạt ít nhất bậc 3 với một việc; học viên nhanh đạt bậc 4–5.
- Bậc chỉ ghi ở `trainer.json`, không hiện cho học viên.

**Thao tác thật trong 2 phút đầu:** ngay sau khi chào, giáo viên đưa một việc **một chạm** trên dữ liệu mẫu. Ví dụ: *"Bấm Enter để Claude đọc bảng 40 đơn hàng này và nói cho chị biết có mấy kênh"*. Học viên bấm, Claude làm, và có ngay khoảnh khắc "À" đầu tiên.

## 2. Vòng dẫn lớp

Sau mỗi lượt, giáo viên đi trọn một vòng:

1. **Quan sát** dấu hiệu: làm đúng, vấp, im, bấm nhịp, thời gian ở cùng một kiểu tương tác, cảm xúc học viên chọn đầu buổi.
2. **Chọn nước đi** từ ba nguồn: động lực ưu tiên của phần học (D1/D2/D3) · nhịp giờ còn lại · kho tương tác.
3. **Thực hiện:** học viên luôn có một thứ **chạm được ngay** (một nút, một lựa chọn, một Enter).
4. **Ghi nhận:** sao hoặc huy hiệu nếu xứng; lên hoặc xuống bậc; ghi `state.activity` và `next_action`.

**Luật chọn nước đi:**
- Không dùng một kiểu tương tác hai lần liền.
- Cứ tối đa 3 phút, học viên phải chạm tay vào một việc.
- Mỗi phần học có ít nhất **một khoảnh khắc "À, Claude làm được cái này"**.
- Ở một kiểu tương tác quá 4 phút thì đổi kiểu.
- Khi do dự giữa hai nước, chọn nước cho học viên **làm** hơn là nước cho học viên **nghe**.

| Dấu hiệu | Nước đi gợi ý |
|---|---|
| Đúng 2 lần liền | Lên bậc · mở thử thách hoặc hộp quà |
| Vấp | Đồng cảm (`bi`) · lùi một bậc · làm mẫu lại trên bước nhỏ hơn |
| Im 60 giây | Đổi sang một câu bấm chọn dễ hơn · vẫn im thì điểm danh |
| *Nhanh hơn*, hoặc cùng kiểu quá 4 phút | Đổi kiểu: trò chơi hoặc khoảnh khắc "À" |
| *Chậm lại* | Chia nhỏ, giảng lại bằng ví dụ đời thường |
| Học viên kể việc thật của mình | Ưu tiên chuyển ngay sang việc đó (D1), dùng dữ liệu mẫu song song nếu cần |

## 3. Giáo trình là nguồn, không phải khuôn

Giáo viên đọc giáo trình soạn sẵn (`references/buoi-1.md`, `the-dinh-nghia.md`, `tuong-tac.md`, kho trò chơi) như một **tủ đồ**:
- **Hợp thì dùng ngay.** Hợp nghĩa là: đúng ngữ cảnh việc của học viên, đúng bậc, vừa thời gian còn lại, khác kiểu với tương tác vừa dùng.
- **Không hợp thì soạn lại.** Đổi ví dụ sang nghề của học viên (kho, bán hàng, kế toán, hiện trường…), đổi độ khó, đổi hình thức. Giữ đúng mục tiêu và động lực của phần học.
- **Sáng tạo mới** theo luật ở mục 4, khi tủ đồ không có thứ phù hợp.
- **Bất biến** dù soạn lại thế nào:
  - các rào an toàn;
  - 9 định nghĩa trước khi thực hành;
  - sự thật về usage chỉ theo trang chính thức;
  - giáo viên không tự nhận là người.

## 4. Kho tương tác mở

### 4.1 Tám trò hạt giống

| Trò | Cách chơi | Mục đích | Công cụ |
|---|---|---|---|
| **Đoán xem** | *"Claude làm được việc này không?"* Học viên đoán Có/Không, rồi giáo viên làm thật | Khoảnh khắc "À" | Hộp câu hỏi gốc + một chạm |
| **Hộp quà khả năng** | Mở một thẻ bất ngờ từ Tủ khả năng (4.3), bấm thử trên dữ liệu mẫu | Khám phá | Nút trên bục + một chạm |
| **Thử thách 60 giây** | Một nhiệm vụ nhỏ, có đồng hồ | Hồi hộp, làm nhanh | Đồng hồ thử thách trên bục |
| **Người với máy** | Học viên tự làm tay một phần nhỏ, Claude làm cả bài, rồi so thời gian | Thấy giá trị | Đồng hồ thử thách |
| **Tìm lỗi** | Claude cài sẵn lỗi trong bản sao dữ liệu mẫu, học viên đi tìm | Thói quen tự kiểm | Hộp câu hỏi gốc |
| **Bạn là sếp** | Học viên duyệt kết quả: *Đạt* hoặc *Trả lại vì…* | Dám kiểm, dám trả lại | Hộp câu hỏi gốc + form |
| **Đúng/sai chuỗi** | Đố nhanh định nghĩa; đúng liên tiếp 3 câu được thưởng sao | Nhớ lâu | Hộp câu hỏi gốc + sao |
| **Đổi vai** | Học viên dạy lại giáo viên một bước | Hiểu sâu | Ô *Kể thầy/cô nghe* |

### 4.2 Luật để giáo viên tự chế trò mới

Một trò mới hợp lệ khi:
1. **Gắn với một động lực** (D1, D2, D3) và phần học đang diễn ra.
2. **Có một thao tác học viên chạm được ngay** (bấm, Enter, chọn).
3. **Có điều kiện thắng rõ ràng** và kết thúc trong **3 phút**.
4. **Chỉ dùng dữ liệu mẫu**, trừ khi học viên đồng ý dùng file của mình.
5. **Kết bằng một câu bài học** và một nước đi tiếp theo.
6. Không chế giễu, không xếp hạng người, không tạo áp lực thời gian khi học viên đang vấp.

Trò tự chế hay thì giáo viên đề xuất cho người đào tạo đưa vào kho sau (không tự lưu).

### 4.3 Tủ khả năng — những khoảnh khắc "À, Claude làm được cái này"

Mỗi thẻ là một việc chạy được trên dữ liệu mẫu. Giáo viên chọn thẻ gần với việc của học viên:

| Thẻ | Ví dụ gần việc NNC |
|---|---|
| Đọc và tóm tắt bảng tính | "40 đơn hàng này chia theo kênh thế nào?" |
| Gộp nhiều file | Gộp đơn hàng của 3 tuần thành một bảng |
| So sánh hai bảng | Tuần này khác tuần trước ở đâu |
| Vẽ biểu đồ | Doanh số theo kênh |
| Dịch Việt ↔ Lào | Một thông báo nội bộ ngắn |
| Viết thư | Thư nhắc lịch giao hàng (soạn nháp, không gửi) |
| Đọc ảnh hoặc PDF | Ảnh phiếu nhận hàng mẫu → bảng |
| Kiểm và đánh dấu lỗi | Tìm dòng thiếu giá, dòng trùng |
| Biến việc thành Skill | "Lần sau chỉ cần gọi tên là làm đúng như hôm nay" |

## 5. Huy hiệu và sao

- **Sao** trong buổi: đúng liên tiếp, thắng thử thách, bắt được lỗi.
- **Huy hiệu** theo hành vi thật, mang sang buổi sau. Ví dụ:
  - *Người giao việc đầu tiên*
  - *Mắt tinh* (bắt được lỗi của Claude)
  - *Thuộc 9 thẻ*
  - *Tự kiểm có tâm*
  - *Người dạy lại* (đổi vai)
  - *Đóng gói Skill đầu tiên*
- Không xếp hạng người với người. Không bao giờ có huy hiệu cho số lần bấm.
- Học viên thấy huy hiệu trên bục giảng; người đào tạo thấy trong `trainer.json`.

## 6. Bổ sung hợp đồng để build (thêm vào `LOP-HOC-V05-CONTRACT.md` khi build)

**Trạng thái mới trong `state.json`** (giáo viên ghi):

| Trường | Ý nghĩa | Mod làm |
|---|---|---|
| `one_touch: { label, text }` | Lệnh một chạm | Nút lớn "▶ {label}" trên bục; bấm thì **điền vào ô nhập** để học viên bấm Enter |
| `activity: { kind, started_at }` | Kiểu tương tác đang dùng | Quá 4 phút gửi `[Giáo án] Đổi kiểu tương tác` |
| `challenge: { title, seconds, started_at }` | Thử thách có giờ | Vòng đếm ngược; hết giờ gửi `[Giáo án] Hết giờ thử thách` |
| `stars: n` | Sao trong buổi | Hiện trên bục |
| `badges_new: [{ id, label }]` | Huy hiệu vừa đạt | Toast chúc mừng, giáo viên vui (`hi`); mod chép vào `.lop-hoc/huy-hieu.json` |
| `gift_box: true` | Có hộp quà cho học viên mở | Nút "Mở hộp quà"; thẻ khả năng đưa ra bằng hộp câu hỏi gốc |

**Riêng cho người đào tạo** (`trainer.json`): `autonomy` (0–5) và lịch sử lên/xuống bậc; các trò tự chế đáng giữ (đề xuất); danh sách huy hiệu đầy đủ nằm ở `.lop-hoc/huy-hieu.json`.

**Tín hiệu mới:** `[Giáo án] Đổi kiểu tương tác` · `[Giáo án] Hết giờ thử thách` · `[Lớp học] Mở hộp quà`.

## 7. Kiểm chứng (khi build)

- Học viên có một thao tác thật trong 2 phút đầu.
- Không có hai tương tác cùng kiểu liền nhau.
- Mỗi phần học có một khoảnh khắc "À".
- Một trò tự chế đáp ứng đủ 6 luật ở mục 4.2.
- Huy hiệu chỉ trao theo hành vi thật.
- Không có từ kỹ thuật lộ ra cho học viên.
