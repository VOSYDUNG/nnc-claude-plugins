// Lớp học NNC v0.13 — giáo án vòng việc đầu, dựng sẵn (nguồn duy nhất).
// Bục giảng hiện bước 0 ngay khi học viên bấm Vào lớp; giáo viên đọc cùng các bước này ở
// references/giao-an-vong-1.md của Skill (bài kiểm hợp đồng so mã và tên bước giữa hai nơi).
// Câu tiếng Lào CẦN NGƯỜI BẢN NGỮ DUYỆT; giữ nguyên khoá.

export type StepCheck = { question: string; options: string[]; right: number }
export type StepText = { title: string; why: string; hints: [string, string, string]; check?: StepCheck }
export type LessonStep = { id: string; vi: StepText; lo: StepText }

export const LESSON_V1: readonly LessonStep[] = [
  {
    id: '0',
    vi: {
      title: 'Tham quan lớp học',
      why: 'biết dùng chính công cụ học',
      hints: [
        'Bấm thử từng chỗ thầy chỉ: ô nhập, chế độ quyền, nút Gợi ý, nút Xong.',
        'Ô nhập ở đáy cửa sổ; chế độ quyền ở thanh ngay dưới ô nhập.',
        'Thầy chỉ từng chỗ trên ảnh, bạn bấm theo.',
      ],
      check: { question: 'Bí thì bấm nút nào?', options: ['Gợi ý', 'Xin nghỉ', 'Đóng cửa sổ'], right: 0 },
    },
    lo: {
      title: 'ທ່ຽວຊົມຫ້ອງຮຽນ',
      why: 'ຮູ້ຈັກໃຊ້ເຄື່ອງມືຮຽນ',
      hints: [
        'ລອງກົດແຕ່ລະບ່ອນທີ່ຄູຊີ້: ຊ່ອງພິມ, ໂໝດສິດ, ປຸ່ມ ແນະນຳ, ປຸ່ມ ແລ້ວ.',
        'ຊ່ອງພິມຢູ່ລຸ່ມສຸດ; ໂໝດສິດຢູ່ແຖບລຸ່ມຊ່ອງພິມ.',
        'ຄູຊີ້ແຕ່ລະບ່ອນໃນຮູບ, ເຈົ້າກົດຕາມ.',
      ],
      check: { question: 'ຕິດຂັດໃຫ້ກົດປຸ່ມໃດ?', options: ['ແນະນຳ', 'ຂໍພັກ', 'ປິດໜ້າຕ່າງ'], right: 0 },
    },
  },
  {
    id: '1',
    vi: {
      title: 'Học ở đây thế nào',
      why: 'biết vai của mình trong lớp',
      hints: [
        'Ba bước lặp lại: thầy cho xem → bạn bấm làm → bạn tự kiểm.',
        'Đọc ba ô trên bảng, rồi bấm Hiểu rồi.',
        'Thầy đọc từng ô cùng bạn.',
      ],
    },
    lo: {
      title: 'ຮຽນຢູ່ນີ້ແນວໃດ',
      why: 'ຮູ້ບົດບາດຂອງຕົນໃນຫ້ອງ',
      hints: [
        'ສາມຂັ້ນຊ້ຳໆ: ຄູໃຫ້ເບິ່ງ → ເຈົ້າກົດເຮັດ → ເຈົ້າກວດເອງ.',
        'ອ່ານສາມຫ້ອງໃນກະດານ, ແລ້ວກົດ ເຂົ້າໃຈແລ້ວ.',
        'ຄູອ່ານແຕ່ລະຫ້ອງກັບເຈົ້າ.',
      ],
    },
  },
  {
    id: '2',
    vi: {
      title: 'Việc đầu tiên',
      why: 'thấy Claude làm việc thật',
      hints: [
        'Bấm nút ▶ rồi nhấn Enter: Claude sẽ đọc bảng đơn hàng mẫu.',
        'Nút ▶ ở dòng đầu bảng lớp; Enter là phím xuống dòng.',
        'Thầy điền sẵn lời giao việc, bạn chỉ nhấn Enter.',
      ],
      check: { question: 'Claude vừa đếm được mấy kênh bán hàng?', options: ['3 kênh', '1 kênh', '40 kênh'], right: 0 },
    },
    lo: {
      title: 'ວຽກທຳອິດ',
      why: 'ເຫັນ Claude ເຮັດວຽກແທ້',
      hints: [
        'ກົດປຸ່ມ ▶ ແລ້ວກົດ Enter: Claude ຈະອ່ານຕາຕະລາງອໍເດີຕົວຢ່າງ.',
        'ປຸ່ມ ▶ ຢູ່ແຖວທຳອິດຂອງກະດານ.',
        'ຄູຕື່ມຄຳມອບວຽກໃຫ້, ເຈົ້າພຽງແຕ່ກົດ Enter.',
      ],
      check: { question: 'Claude ນັບໄດ້ຈັກຊ່ອງທາງຂາຍ?', options: ['3 ຊ່ອງທາງ', '1 ຊ່ອງທາງ', '40 ຊ່ອງທາງ'], right: 0 },
    },
  },
  {
    id: '3',
    vi: {
      title: 'Chế độ Auto',
      why: 'Claude làm mà không hỏi từng việc nhỏ',
      hints: [
        'Đổi chế độ quyền sang Auto, rồi bấm Xong.',
        'Chế độ quyền nằm ở thanh ngay dưới ô nhập; bấm vào chữ đang hiện để chọn Auto.',
        'Thầy khoanh đúng chỗ trên ảnh, bạn bấm theo từng bước.',
      ],
      check: { question: 'Auto giúp gì cho bạn?', options: ['Claude tự làm việc an toàn, không hỏi từng bước nhỏ', 'Claude được làm mọi thứ không cần hỏi', 'Claude chạy nhanh hơn'], right: 0 },
    },
    lo: {
      title: 'ໂໝດ Auto',
      why: 'ໃຫ້ Claude ເຮັດວຽກໂດຍບໍ່ຖາມທຸກເລື່ອງນ້ອຍ',
      hints: [
        'ປ່ຽນໂໝດສິດເປັນ Auto, ແລ້ວກົດ ແລ້ວ.',
        'ໂໝດສິດຢູ່ແຖບລຸ່ມຊ່ອງພິມ; ກົດໃສ່ຄຳທີ່ສະແດງຢູ່ເພື່ອເລືອກ Auto.',
        'ຄູວົງບ່ອນໃນຮູບ, ເຈົ້າກົດຕາມ.',
      ],
      check: { question: 'Auto ຊ່ວຍເຈົ້າແນວໃດ?', options: ['Claude ເຮັດວຽກທີ່ປອດໄພເອງ ບໍ່ຖາມທຸກຂັ້ນນ້ອຍ', 'Claude ເຮັດໄດ້ທຸກຢ່າງໂດຍບໍ່ຖາມ', 'Claude ແລ່ນໄວຂຶ້ນ'], right: 0 },
    },
  },
  {
    id: '4',
    vi: {
      title: 'Tự kiểm',
      why: 'biết kết quả nào tin được',
      hints: [
        'Chọn 3 dòng trong kết quả, tìm đúng 3 dòng đó trong bảng gốc.',
        'Mở bảng gốc thầy chỉ; so cột kênh và cột doanh số.',
        'Thầy so dòng đầu cùng bạn, bạn so hai dòng còn lại.',
      ],
      check: { question: 'Ba dòng bạn so: khớp hay lệch?', options: ['Khớp', 'Có chỗ lệch'], right: -1 },
    },
    lo: {
      title: 'ກວດເອງ',
      why: 'ຮູ້ວ່າຜົນໃດເຊື່ອໄດ້',
      hints: [
        'ເລືອກ 3 ແຖວໃນຜົນ, ຫາ 3 ແຖວນັ້ນໃນຕາຕະລາງຕົ້ນສະບັບ.',
        'ເປີດຕາຕະລາງທີ່ຄູຊີ້; ທຽບຖັນຊ່ອງທາງ ແລະ ຍອດຂາຍ.',
        'ຄູທຽບແຖວທຳອິດກັບເຈົ້າ, ເຈົ້າທຽບສອງແຖວທີ່ເຫຼືອ.',
      ],
      check: { question: 'ສາມແຖວທີ່ເຈົ້າທຽບ: ກົງ ຫຼື ບໍ່ກົງ?', options: ['ກົງ', 'ມີບ່ອນບໍ່ກົງ'], right: -1 },
    },
  },
  {
    id: '5',
    vi: {
      title: 'Giao việc 4 ý',
      why: 'tự giao việc cho Claude',
      hints: [
        'Bấm Giao việc, điền 4 ý: mục tiêu, nguồn, đầu ra, cách kiểm.',
        'Mỗi ô một câu ngắn; ô Mục tiêu bắt buộc.',
        'Thầy điền mẫu một ô, bạn điền ba ô còn lại.',
      ],
    },
    lo: {
      title: 'ມອບວຽກ 4 ຂໍ້',
      why: 'ມອບວຽກໃຫ້ Claude ເອງ',
      hints: [
        'ກົດ ມອບວຽກ, ຕື່ມ 4 ຂໍ້: ເປົ້າໝາຍ, ແຫຼ່ງ, ຜົນ, ວິທີກວດ.',
        'ແຕ່ລະຊ່ອງໜຶ່ງປະໂຫຍກສັ້ນ; ຊ່ອງເປົ້າໝາຍຕ້ອງມີ.',
        'ຄູຕື່ມຕົວຢ່າງໜຶ່ງຊ່ອງ, ເຈົ້າຕື່ມສາມຊ່ອງທີ່ເຫຼືອ.',
      ],
    },
  },
  {
    id: '6',
    vi: {
      title: 'Việc của tôi',
      why: 'dùng được ngay trong việc thật',
      hints: [
        'Chọn một việc thật có file (bản sao, đã che thông tin) hoặc dùng bảng mẫu tuần sau.',
        'Chỉ thầy thư mục chứa file; thầy hỏi quyền trước khi đọc.',
        'Thầy làm phần đầu, bạn làm phần sau và tự kiểm.',
      ],
    },
    lo: {
      title: 'ວຽກຂອງຂ້ອຍ',
      why: 'ໃຊ້ໄດ້ທັນທີໃນວຽກແທ້',
      hints: [
        'ເລືອກວຽກແທ້ທີ່ມີໄຟລ໌ (ສຳເນົາ, ປິດຂໍ້ມູນແລ້ວ) ຫຼື ໃຊ້ຕາຕະລາງຕົວຢ່າງອາທິດໜ້າ.',
        'ບອກຄູໂຟນເດີທີ່ມີໄຟລ໌; ຄູຂໍສິດກ່ອນອ່ານ.',
        'ຄູເຮັດພາກທຳອິດ, ເຈົ້າເຮັດພາກຕໍ່ ແລະ ກວດເອງ.',
      ],
    },
  },
  {
    id: '7',
    vi: {
      title: 'Chốt vòng việc',
      why: 'nhớ lâu và quay lại đúng chỗ',
      hints: [
        'Trả lời 2 câu nhớ lại, rồi chọn khi nào việc kế tiếp đến.',
        'Câu trả lời nằm trong các bước vừa làm.',
        'Thầy nhắc lại một bước, bạn trả lời câu còn lại.',
      ],
    },
    lo: {
      title: 'ສະຫຼຸບຮອບວຽກ',
      why: 'ຈື່ໄດ້ດົນ ແລະ ກັບມາຖືກບ່ອນ',
      hints: [
        'ຕອບ 2 ຄຳຖາມທົບທວນ, ແລ້ວເລືອກວ່າວຽກຕໍ່ໄປມາເມື່ອໃດ.',
        'ຄຳຕອບຢູ່ໃນຂັ້ນທີ່ຫາກໍເຮັດ.',
        'ຄູທົບທວນໜຶ່ງຂັ້ນ, ເຈົ້າຕອບຄຳຖາມທີ່ເຫຼືອ.',
      ],
    },
  },
]

export const stepById = (id: string | null | undefined): LessonStep | null => LESSON_V1.find(s => s.id === id) ?? null
