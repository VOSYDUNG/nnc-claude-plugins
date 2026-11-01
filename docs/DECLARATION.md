# Tuyên bố chung — NNC OSER

Ngày đối chiếu: 12/10/2026. Phạm vi: kernel và tổ chức nghiệp vụ của NNC OSER; cách thực thi tuân theo host đang chạy. Đây là tuyên bố kiến trúc của bản sửa, không phải xác nhận hoàn thiện sản phẩm hay phê duyệt một Mission kinh doanh.

NNC OSER giúp con người giữ một mục tiêu rõ ràng, quyền quyết định và bằng chứng xuyên suốt quá trình hình thành, thực hiện, sử dụng và thay đổi công việc. Một mô hình hay một cuộc trò chuyện có thể thay đổi; nguồn sự thật và ý nghĩa của quyết định không được đổi âm thầm theo nó.

## Kernel giữ những gì

Kernel giữ hợp đồng Mission, nguồn thẩm quyền, tiêu chí nghiệm thu, giới hạn nguồn lực, trạng thái thực thi, checkpoint, bằng chứng và các quan sát Health/usage có nguồn. Revision, ownership epoch, idempotency và reconciliation bảo vệ tính nhất quán của các trạng thái đó. Chúng không chứng minh dữ liệu bên ngoài đúng, không tự cấp quyền và không thực thi thay host.

Mục tiêu và acceptance đã duyệt là baseline hiện hành. Bổ sung dữ liệu mới có nguồn trong cùng phạm vi là cập nhật nghiệp vụ. Đổi mục tiêu, quyền, nguồn lực hoặc hành vi được nghiệm thu cần một Delta Mission rõ tác động, với thẩm quyền tương ứng. Lịch sử được bảo toàn; đề xuất và ghi chú cũ không thay thế baseline.

UNKNOWN được giữ là UNKNOWN. Đã yêu cầu khác với đã chạy; admission khác với execution; receipt khác với outcome; hash khác với bằng chứng hành vi; test pass khác với sử dụng thực tế đạt yêu cầu. Hoàn tất đòi bằng chứng phù hợp, mới và không còn execution/blocker chưa đối soát.

## Nghiệp vụ tổ chức quanh công việc thật

Formation làm rõ vấn đề, thực tế, lựa chọn và hệ quả trước khi cam kết. Adaptive Delivery chọn cách giao kết quả phù hợp loại công việc. Operation ghi nhận kết quả sử dụng và nghẽn; Delta Mission xử lý thay đổi có ảnh hưởng. Finance, strategy, product hay vận hành là nghiệp vụ có hợp đồng dữ liệu và acceptance riêng, không là một đội agent cố định.

Mỗi nghiệp vụ giữ nguồn chuẩn của nó. Kernel chỉ lưu tham chiếu, trạng thái và chứng cứ cần cho quyết định; không sao chép sổ tiền, dữ liệu khách hàng hay trạng thái sản xuất để tạo nguồn đúng thứ hai. Báo cáo là view có thời điểm trên nguồn chuẩn. Lưu ý khác thời kỳ không mặc nhiên là mâu thuẫn; mâu thuẫn thật cần chỉ ra cùng phạm vi/thời điểm và nguồn.

Một thay đổi phải có lý do: lỗi tái hiện, bằng chứng mới, mâu thuẫn có nguồn hoặc thay đổi được người có quyền yêu cầu. Trước khi sửa: nêu hợp đồng bị vi phạm, phạm vi và phép kiểm. Sau khi sửa: lưu kết quả, ảnh hưởng và điều còn chưa xác minh. Phần nhất quán được giữ; không xây lại chỉ vì đổi agent/model.

## Host thực thi theo tài liệu hãng

Codex, Claude Code, API và desktop là các môi trường riêng. Subagent, team, context, model/effort, skill discovery, permissions, interruption và continuation phải dùng giao diện thực sự được host hỗ trợ, theo tài liệu hãng và khả năng quan sát tại phiên. Không dịch tên công cụ hoặc định dạng cấu hình giữa các host bằng suy đoán. Không coi tài liệu API là bằng chứng công cụ đã có trong desktop.

OSER không áp danh sách ghế, đội, wave, model family hay effort ladder toàn cục. Chọn direct work/tool/delegation theo công việc và quyền đã có. Số slot và quyền phải đọc từ phiên; không ghi đè lựa chọn model toàn máy. Agent chỉ sửa phạm vi được giao; người tích hợp chịu trách nhiệm kiểm chứng kết quả.

Sự kiện hoàn tất/blocker mở công việc phụ thuộc. Có việc độc lập thì làm; hết việc độc lập thì dùng event wait/yield được host cung cấp. Không polling status, sleep-and-retry hoặc lịch polling thay cơ chế sự kiện. Giữ một báo cáo hiện hành mỗi repo; evidence chi tiết ở workspace nghiệp vụ.

Thông tin kỹ thuật và nguồn chính thức nằm ở [Host integrations](oser-r1/INTEGRATIONS.md). Giao kèo hiện có của kernel ở [Operations](oser-r1/OPERATIONS.md). Tuyên bố này không thêm daemon, scheduler, UI adapter hay live conformance mà implementation chưa có.

## Cấp và ký hiệu

Workflow A (Formation/Decision) là bước thành lập ở cấp dự án hoặc nhánh: làm rõ vấn đề, lựa chọn và quyết định trước khi cam kết. Trong thành lập, QA/QC sơ bộ là giai đoạn đầu của kiểm chứng: sau khi hướng được duyệt và trước `MISSION_READY`, nó hình thành luật chung của Mission (tiêu chí nghiệm thu kèm loại bằng chứng, bất biến, các phép kiểm QC và điều chưa biết), được kernel R1 khóa làm mẫu số nghiệm thu cố định; thay đổi sau khi khóa là Delta Mission. Workflow B (Adaptive Delivery/Operation) là bước xúc tiến ở cấp dự án hoặc nhánh: giao kết quả, ghi nhận sử dụng và xử lý nghẽn trong phạm vi đã thành lập.

Cổng `MISSION_READY` kèm `direction_approval` (từ alpha.3) là cổng chuyển sang tự chủ: hướng đã chọn phải có người duyệt, thời điểm và tham chiếu quyết định. Mission kernel R1 là điều kiện bắt buộc của cấp tự chủ; không có kernel giữ hợp đồng, thẩm quyền và bằng chứng thì không vận hành tự chủ.

Số alpha là cấp năng lực của phương pháp, không phải "bản cũ" hay "bản mới" để thay thế lẫn nhau. Dự án ứng dụng phương pháp (ví dụ Lớp học NNC) sống ở repo riêng; repo này chỉ giữ phương pháp.

## Khi nào được coi là tốt

Hệ thống tốt khi giúp con người quyết định đúng trên nguồn có thể kiểm tra, thực hiện trong quyền đã có, nhận ra nghẽn và tiếp tục mà không mất mục tiêu. Lượng tài liệu, số agent, số test hay lời khẳng định tự tin không thay thế kết quả đó. Phương thức có thể điều chỉnh từ bằng chứng; thay đổi không được phá sự liên tục hoặc xóa điều chưa biết.
