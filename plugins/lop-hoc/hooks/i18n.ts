// Lớp học NNC — chữ trên bục giảng và các dòng của lớp, tiếng Việt và tiếng Lào.
// Ngôn ngữ lấy từ state.json `language` (giáo viên ghi sau khi học viên chọn), nhớ cho lần mở sau.
// Câu tiếng Lào CẦN NGƯỜI BẢN NGỮ DUYỆT trước khi dùng rộng: sửa thẳng trong bảng `lo` bên dưới, không đổi khoá.
// Tín hiệu "[Giáo án] …" gửi giáo viên luôn bằng tiếng Việt (ẩn với học viên), nên lý do Xin phép gửi đi theo `vi`.

export type Lang = 'vi' | 'lo'

export type Strings = {
  title: string
  waiting: string
  teacherWord: string
  teacherLabel: (kind: 'thay' | 'co') => string
  teacherSelf: (kind: 'thay' | 'co') => string
  enter: string
  leftSaved: (t: string) => string
  waitingResume: (T: string, t: string) => string
  resume: string
  inBreak: (note: string) => string
  keepSeat: (T: string, addr: string) => string
  backToClass: string
  chooseReason: (t: string) => string
  reasons: { key: string; vi: string; label: string }[]
  cancel: string
  raised: (addr: string, t: string) => string
  tellLabel: (t: string) => string
  tellPlaceholder: string
  send: string
  formTitle: string
  formFields: { goal: [string, string]; src: [string, string]; out: [string, string]; check: [string, string] }
  formFill: string
  formClose: string
  formGoalFirst: string
  formToast: string
  delegation: { head: string; goal: string; src: string; out: string; check: string; noSrc: string; noOut: string; noCheck: string }
  usageTitle: string
  usageFive: (p: number, reset: string) => string
  usageWeek: (p: number, reset: string) => string
  usageUnknown: (t: string) => string
  mine: string
  mineHelp: string
  myClaude: (line: string) => string
  working: (T: string, addr: string) => string
  yourTurn: string
  oneTouchToast: string
  badgeToast: (label: string) => string
  badgesText: string
  starsAlt: (n: number) => string
  giftWaiting: string
  giftOpening: string
  giftOpen: string
  part: string
  loops: (T: string, n: number) => string
  pickFor: (T: string, mmss: string) => string
  helpNeeded: string
  helpButton: string
  dest: string
  raiseHand: string
  askLeave: string
  leave: string
  slower: string
  faster: string
  hint: (T: string) => string
  delegate: string
  notRight: (t: string) => string
  notRightFill: (t: string) => string
  resultSheet: string
  segments: Record<string, string>
  askHead: (T: string) => string
  demoWord: (T: string) => string
  teachWord: (T: string) => string
  tips: string[]
  promptBefore: string
  promptIn: (t: string) => string
  youPressed: string
  you: string
  youDelegated: string
  tool: { read: (f: string) => string; find: string; write: (f: string) => string; edit: (f: string) => string; run: string; web: string; skill: string; mcp: string; draw: string; other: string; aFile: string }
  // v0.8 — sân khấu bục giảng do giáo viên dựng.
  more: string
  moreClose: string
  foldMore: string
  foldLess: string
  bypassChip: (label: string) => string
  facts: { mode: string; effort: string; model: string; context: string; usage5: string; usageWeek: string }
  barNote: string
  barAlt: (what: string) => string
  boardAlt: (title: string) => string
  // v0.10 — ảnh chụp màn hình có đánh dấu.
  shotAlt: (title: string) => string
  shotNote: (T: string) => string
  choiceExpired: (t: string) => string
  ledger: (T: string) => string
  waitHint: (t: string) => string
  // v0.12 — mọi thứ học viên thấy đều nằm trong khung thầy: dòng việc, nhóm việc, kết quả, hộp câu hỏi, lệnh, suy nghĩ.
  act: {
    doing: (T: string, what: string) => string
    did: (T: string, what: string) => string
    errored: (T: string) => string
    interrupted: (T: string) => string
    detail: string
    less: string
    groupDoing: (T: string, parts: string) => string
    groupDid: (T: string, parts: string) => string
    groupErr: (t: string) => string
    // Đếm theo loại việc trong một nhóm.
    count: { read: (n: number) => string; find: (n: number) => string; write: (n: number) => string; edit: (n: number) => string; run: (n: number) => string; web: (n: number) => string; skill: (n: number) => string; mcp: (n: number) => string; draw: (n: number) => string; other: (n: number) => string }
    result: string
    resultError: (t: string) => string
    reloaded: string
    command: (T: string, cmd: string) => string
    commandError: (T: string, cmd: string) => string
    thinking: (T: string) => string
  }
}

const vi: Strings = {
  title: 'Lớp học NNC',
  waiting: 'Lớp đang chờ giáo viên · chọn thầy hoặc cô, rồi bấm Vào lớp',
  teacherWord: 'Giáo viên',
  teacherLabel: k => (k === 'thay' ? 'Thầy' : 'Cô'),
  teacherSelf: k => (k === 'thay' ? 'Thầy' : 'Cô'),
  enter: 'Vào lớp',
  leftSaved: t => `Đã xin nghỉ · ${t} đã lưu chỗ, quay lại lúc nào cũng được`,
  waitingResume: (T, t) => `${T}: ${t} vẫn ở đây — bấm Tiếp tục để học tiếp từ chỗ đã lưu`,
  resume: 'Tiếp tục',
  inBreak: note => `Đang xin phép · ${note}`,
  keepSeat: (T, addr) => `${T} giữ chỗ cho ${addr}`,
  backToClass: 'Quay lại lớp',
  chooseReason: t => `Xin phép ${t} một lát · chọn lý do`,
  reasons: [
    { key: 'ly-do-nuoc', vi: 'đi uống nước', label: 'đi uống nước' },
    { key: 'ly-do-gap', vi: 'có việc gấp', label: 'có việc gấp' },
    { key: 'ly-do-hoi', vi: 'cần hỏi riêng', label: 'cần hỏi riêng' },
  ],
  cancel: 'Thôi',
  raised: (addr, t) => `${addr} giơ tay · ${t} đang nghe`,
  tellLabel: t => `Kể ${t} nghe`,
  tellPlaceholder: 'Viết điều muốn hỏi hoặc kể, rồi bấm Enter',
  send: 'gửi',
  formTitle: 'Giao việc cho Claude · 4 ý',
  formFields: {
    goal: ['Mục tiêu', 'Tổng hợp doanh số theo kênh từ bảng tính'],
    src: ['Nguồn', 'File bảng tính mẫu / file của tôi đã che thông tin'],
    out: ['Đầu ra', 'Bảng: kênh – số đơn – doanh số'],
    check: ['Cách kiểm', 'Đối chiếu tổng với cột gốc'],
  },
  formFill: 'Đưa vào ô nhập',
  formClose: 'Đóng',
  formGoalFirst: 'Ghi "Mục tiêu" trước đã.',
  formToast: 'Đọc lại lời giao việc trong ô nhập, rồi bấm Enter để giao.',
  delegation: { head: 'Giao việc —', goal: 'Mục tiêu', src: 'Nguồn', out: 'Đầu ra', check: 'Cách kiểm', noSrc: '(chưa có — dùng mẫu giả)', noOut: '(giáo viên đề xuất)', noCheck: '(giáo viên gợi ý, tôi tự kiểm)' },
  usageTitle: 'Hạn mức sử dụng · 5 giờ và tuần',
  usageFive: (p, r) => `5 giờ: đã dùng ${p}%${r ? ` · reset lúc ${r}` : ''}`,
  usageWeek: (p, r) => `Tuần: đã dùng ${p}%${r ? ` · reset ${r}` : ''}`,
  usageUnknown: t => `Chưa đọc được số liệu · chờ ${t} giảng xong một lượt`,
  mine: 'Claude của tôi',
  mineHelp: 'Model: bộ não đang dùng · Effort: mức nghĩ kỹ · Context: trí nhớ của phiên · 5 giờ / tuần: hạn mức gói',
  myClaude: line => `Claude của tôi · ${line}`,
  working: (T, addr) => `${T} đang giảng — ${addr} xem bên trên`,
  yourTurn: 'Lượt của bạn',
  oneTouchToast: 'Đã điền sẵn — bấm Enter để giao cho Claude',
  badgeToast: l => `Huy hiệu mới: ${l}`,
  badgesText: 'Huy hiệu',
  starsAlt: n => `${n} sao trong buổi`,
  giftWaiting: 'Có một hộp quà cho bạn',
  giftOpening: 'Hộp quà đang mở…',
  giftOpen: 'Mở hộp quà',
  part: 'Phần',
  loops: (T, n) => `${T} · đã chốt ${n} vòng việc`,
  pickFor: (T, m) => `${T} chọn giúp sau ${m}`,
  helpNeeded: ' Đang cần người hỗ trợ ',
  helpButton: 'Soạn tin nhờ hỗ trợ',
  dest: 'Đích',
  raiseHand: 'Giơ tay',
  askLeave: 'Xin phép',
  leave: 'Xin nghỉ',
  slower: 'Chậm lại một chút',
  faster: 'Nhanh hơn được',
  hint: T => `${T} gợi ý giúp`,
  delegate: 'Giao việc',
  notRight: t => `Thưa ${t}, chỗ này chưa đúng`,
  notRightFill: t => `Thưa ${t}, chỗ này chưa đúng: `,
  resultSheet: 'Phiếu kết quả',
  segments: { '0': 'Vào lớp', '1': 'Làm quen nhanh', '2': 'Việc thật của tôi', '3': 'Thử thách theo nhịp của bạn', '4': 'Chốt vòng việc' },
  askHead: T => `${T} hỏi`,
  demoWord: T => `${T} đang làm mẫu`,
  teachWord: T => `${T} đang giảng`,
  tips: [
    'mẹo: effort cao nghĩ kỹ hơn nhưng tốn usage hơn',
    'mẹo: context gần đầy thì mở phiên mới, kèm ghi chú tiếp tục',
    'mẹo: giao việc rõ 4 ý — mục tiêu, nguồn, đầu ra, cách kiểm',
    'mẹo: Claude xin quyền là để bạn quyết — đọc kỹ rồi hãy đồng ý',
    'mẹo: kết quả nghe hợp lý chưa phải bằng chứng — đối chiếu nguồn',
  ],
  promptBefore: 'Chọn thầy hoặc cô trên bảng lớp, rồi bấm Vào lớp',
  promptIn: t => `Bấm nút trên bảng lớp, hoặc kể ${t} nghe ở đây`,
  youPressed: 'Bạn bấm',
  you: 'Bạn',
  youDelegated: 'Bạn giao việc',
  tool: {
    read: f => `đọc ${f}`, find: 'tìm trong thư mục', write: f => `ghi ${f}`, edit: f => `sửa ${f}`,
    run: 'chạy một lệnh trên máy', web: 'tra cứu trên mạng', skill: 'mở bài học', mcp: 'dùng một công cụ kết nối', draw: 'vẽ hình', other: 'làm một việc', aFile: 'một file',
  },
  more: '⋯ Thêm',
  moreClose: 'Thu gọn',
  foldMore: '▸ Xem đầy đủ',
  foldLess: '▾ Thu gọn',
  bypassChip: label => ` ⚠ ${label} · Claude làm không hỏi lại quyền, đọc kỹ trước khi giao việc `,
  facts: { mode: 'Chế độ', effort: 'Effort', model: 'Model', context: 'Context', usage5: '5 giờ', usageWeek: 'Tuần' },
  barNote: 'ở thanh dưới ô nhập',
  barAlt: what => `Thanh dưới ô nhập, chỗ cần nhìn: ${what}`,
  boardAlt: title => `Bảng của lớp: ${title}`,
  shotAlt: title => `Ảnh màn hình có đánh dấu: ${title}`,
  shotNote: T => `${T} đã đánh dấu trên ảnh màn hình — xem trong Claude Desktop`,
  choiceExpired: t => `Hết giờ rồi — ${t} gợi ý ô nổi bật, bạn vẫn tự bấm nhé`,
  ledger: T => `${T} ghi sổ lớp`,
  waitHint: t => `Chưa chắc thì chọn dòng đầu tiên — ${t} sẽ chỉ lại bằng hình.`,
  act: {
    doing: (T, what) => `▸ ${T} đang ${what}…`,
    did: (T, what) => `▸ ${T} vừa ${what}`,
    errored: T => `▸ ${T} gặp trục trặc, đang xử lý`,
    interrupted: T => `▸ ${T} đã dừng việc này`,
    detail: 'Xem chi tiết',
    less: 'Thu gọn',
    groupDoing: (T, parts) => `▸ ${T} đang: ${parts}`,
    groupDid: (T, parts) => `▸ ${T} vừa: ${parts}`,
    groupErr: t => `có trục trặc, ${t} đang xử lý`,
    count: {
      read: n => `đọc ${n} file`, find: n => `tìm ${n} lần`, write: n => `tạo ${n} file`, edit: n => `sửa ${n} file`, run: n => `chạy ${n} lệnh`,
      web: n => `tra cứu ${n} lần`, skill: n => `mở ${n} bài học`, mcp: n => `dùng ${n} công cụ kết nối`, draw: n => `vẽ ${n} hình`, other: n => `làm ${n} việc khác`,
    },
    result: 'Kết quả · xem',
    resultError: t => `Có lỗi — ${t} đang xử lý · xem`,
    reloaded: 'Đã nạp lại lớp học ✓',
    command: (T, cmd) => `▸ ${T} vừa chạy lệnh /${cmd}`,
    commandError: (T, cmd) => `▸ Lệnh /${cmd} gặp trục trặc — ${T} đang xử lý`,
    thinking: T => `${T} đang suy nghĩ…`,
  },
}

const lo: Strings = {
  title: 'ຫ້ອງຮຽນ NNC',
  waiting: 'ຫ້ອງຮຽນລໍຖ້າຄູ · ເລືອກຄູຜູ້ຊາຍ ຫຼື ຄູຜູ້ຍິງ, ແລ້ວກົດ ເຂົ້າຫ້ອງ',
  teacherWord: 'ຄູ',
  teacherLabel: k => (k === 'thay' ? 'ຄູຜູ້ຊາຍ' : 'ຄູຜູ້ຍິງ'),
  teacherSelf: () => 'ຄູ',
  enter: 'ເຂົ້າຫ້ອງ',
  leftSaved: () => 'ຂໍພັກແລ້ວ · ຄູບັນທຶກບ່ອນໄວ້ແລ້ວ, ກັບມາເມື່ອໃດກໍໄດ້',
  waitingResume: () => 'ຄູຍັງຢູ່ນີ້ — ກົດ ຮຽນຕໍ່ ເພື່ອຮຽນຕໍ່ຈາກບ່ອນທີ່ບັນທຶກໄວ້',
  resume: 'ຮຽນຕໍ່',
  inBreak: note => `ກຳລັງຂໍອະນຸຍາດ · ${note}`,
  keepSeat: () => 'ຄູຮັກສາບ່ອນໄວ້ໃຫ້',
  backToClass: 'ກັບເຂົ້າຫ້ອງ',
  chooseReason: () => 'ຂໍອະນຸຍາດຄູໜ້ອຍໜຶ່ງ · ເລືອກເຫດຜົນ',
  reasons: [
    { key: 'ly-do-nuoc', vi: 'đi uống nước', label: 'ໄປດື່ມນ້ຳ' },
    { key: 'ly-do-gap', vi: 'có việc gấp', label: 'ມີວຽກດ່ວນ' },
    { key: 'ly-do-hoi', vi: 'cần hỏi riêng', label: 'ຢາກຖາມສ່ວນຕົວ' },
  ],
  cancel: 'ຍົກເລີກ',
  raised: () => 'ຍົກມື · ຄູກຳລັງຟັງ',
  tellLabel: () => 'ເລົ່າໃຫ້ຄູຟັງ',
  tellPlaceholder: 'ຂຽນສິ່ງທີ່ຢາກຖາມ ຫຼື ເລົ່າ, ແລ້ວກົດ Enter',
  send: 'ສົ່ງ',
  formTitle: 'ມອບວຽກໃຫ້ Claude · 4 ຂໍ້',
  formFields: {
    goal: ['ເປົ້າໝາຍ', 'ສັງລວມຍອດຂາຍຕາມຊ່ອງທາງຈາກຕາຕະລາງ'],
    src: ['ແຫຼ່ງຂໍ້ມູນ', 'ໄຟລ໌ຕົວຢ່າງ / ໄຟລ໌ຂອງຂ້ອຍທີ່ປິດຂໍ້ມູນແລ້ວ'],
    out: ['ຜົນທີ່ຕ້ອງການ', 'ຕາຕະລາງ: ຊ່ອງທາງ – ຈຳນວນ – ຍອດຂາຍ'],
    check: ['ວິທີກວດ', 'ທຽບຍອດລວມກັບຖັນຕົ້ນສະບັບ'],
  },
  formFill: 'ໃສ່ໃນຊ່ອງພິມ',
  formClose: 'ປິດ',
  formGoalFirst: 'ຂຽນ "ເປົ້າໝາຍ" ກ່ອນ.',
  formToast: 'ອ່ານຄຳມອບວຽກໃນຊ່ອງພິມອີກເທື່ອ, ແລ້ວກົດ Enter.',
  delegation: { head: 'ມອບວຽກ —', goal: 'ເປົ້າໝາຍ', src: 'ແຫຼ່ງຂໍ້ມູນ', out: 'ຜົນທີ່ຕ້ອງການ', check: 'ວິທີກວດ', noSrc: '(ຍັງບໍ່ມີ — ໃຊ້ຂໍ້ມູນຕົວຢ່າງ)', noOut: '(ຄູສະເໜີ)', noCheck: '(ຄູແນະນຳ, ຂ້ອຍກວດເອງ)' },
  usageTitle: 'ໂຄຕ້າການໃຊ້ · 5 ຊົ່ວໂມງ ແລະ ອາທິດ',
  usageFive: (p, r) => `5 ຊົ່ວໂມງ: ໃຊ້ໄປແລ້ວ ${p}%${r ? ` · ຣີເຊັດເວລາ ${r}` : ''}`,
  usageWeek: (p, r) => `ອາທິດ: ໃຊ້ໄປແລ້ວ ${p}%${r ? ` · ຣີເຊັດ ${r}` : ''}`,
  usageUnknown: () => 'ຍັງອ່ານຕົວເລກບໍ່ໄດ້ · ລໍຖ້າຄູສອນຈົບໜຶ່ງເທື່ອ',
  mine: 'Claude ຂອງຂ້ອຍ',
  mineHelp: 'Model: ສະໝອງທີ່ໃຊ້ຢູ່ · Effort: ລະດັບການຄິດ · Context: ຄວາມຈຳຂອງເຊດຊັນ · 5 ຊົ່ວໂມງ / ອາທິດ: ໂຄຕ້າ',
  myClaude: line => `Claude ຂອງຂ້ອຍ · ${line}`,
  working: () => 'ຄູກຳລັງສອນ — ເບິ່ງຂ້າງເທິງ',
  yourTurn: 'ຮອດຕາເຈົ້າ',
  oneTouchToast: 'ຕື່ມໃຫ້ແລ້ວ — ກົດ Enter ເພື່ອມອບໃຫ້ Claude',
  badgeToast: l => `ຫຼຽນໃໝ່: ${l}`,
  badgesText: 'ຫຼຽນ',
  starsAlt: n => `${n} ດາວໃນມື້ນີ້`,
  giftWaiting: 'ມີກ່ອງຂອງຂວັນໃຫ້ເຈົ້າ',
  giftOpening: 'ກຳລັງເປີດກ່ອງຂອງຂວັນ…',
  giftOpen: 'ເປີດກ່ອງຂອງຂວັນ',
  part: 'ພາກ',
  loops: (_T, n) => `ຄູ · ສະຫຼຸບແລ້ວ ${n} ຮອບວຽກ`,
  pickFor: (_T, m) => `ຄູຈະເລືອກໃຫ້ໃນ ${m}`,
  helpNeeded: ' ຕ້ອງການຄົນຊ່ວຍ ',
  helpButton: 'ຂຽນຂໍ້ຄວາມຂໍຄວາມຊ່ວຍເຫຼືອ',
  dest: 'ເປົ້າໝາຍ',
  raiseHand: 'ຍົກມື',
  askLeave: 'ຂໍອະນຸຍາດ',
  leave: 'ຂໍພັກ',
  slower: 'ຊ້າລົງໜ້ອຍໜຶ່ງ',
  faster: 'ໄວຂຶ້ນໄດ້',
  hint: () => 'ຄູຊ່ວຍແນະນຳ',
  delegate: 'ມອບວຽກ',
  notRight: () => 'ຄູ, ບ່ອນນີ້ຍັງບໍ່ຖືກ',
  notRightFill: () => 'ຄູ, ບ່ອນນີ້ຍັງບໍ່ຖືກ: ',
  resultSheet: 'ໃບຜົນການຮຽນ',
  segments: { '0': 'ເຂົ້າຫ້ອງ', '1': 'ຮູ້ຈັກໄວ', '2': 'ວຽກແທ້ຂອງຂ້ອຍ', '3': 'ສິ່ງທ້າທາຍຕາມຈັງຫວະຂອງເຈົ້າ', '4': 'ສະຫຼຸບຮອບວຽກ' },
  askHead: () => 'ຄູຖາມ',
  demoWord: () => 'ຄູກຳລັງເຮັດໃຫ້ເບິ່ງ',
  teachWord: () => 'ຄູກຳລັງສອນ',
  tips: [
    'ເຄັດລັບ: effort ສູງ ຄິດລະອຽດກວ່າ ແຕ່ໃຊ້ໂຄຕ້າຫຼາຍກວ່າ',
    'ເຄັດລັບ: context ໃກ້ເຕັມ ໃຫ້ເປີດເຊດຊັນໃໝ່ ພ້ອມບັນທຶກບ່ອນຕໍ່',
    'ເຄັດລັບ: ມອບວຽກໃຫ້ຊັດ 4 ຂໍ້ — ເປົ້າໝາຍ, ແຫຼ່ງ, ຜົນ, ວິທີກວດ',
    'ເຄັດລັບ: Claude ຂໍອະນຸຍາດ ເພື່ອໃຫ້ເຈົ້າຕັດສິນ — ອ່ານກ່ອນແລ້ວຈຶ່ງເຫັນດີ',
    'ເຄັດລັບ: ຜົນທີ່ຟັງມີເຫດຜົນ ຍັງບໍ່ແມ່ນຫຼັກຖານ — ທຽບກັບແຫຼ່ງ',
  ],
  promptBefore: 'ເລືອກຄູຢູ່ກະດານ, ແລ້ວກົດ ເຂົ້າຫ້ອງ',
  promptIn: () => 'ກົດປຸ່ມຢູ່ກະດານ, ຫຼື ເລົ່າໃຫ້ຄູຟັງຢູ່ນີ້',
  youPressed: 'ເຈົ້າກົດ',
  you: 'ເຈົ້າ',
  youDelegated: 'ເຈົ້າມອບວຽກ',
  tool: {
    read: f => `ອ່ານ ${f}`, find: 'ຊອກໃນໂຟນເດີ', write: f => `ຂຽນ ${f}`, edit: f => `ແກ້ ${f}`,
    run: 'ແລ່ນຄຳສັ່ງໃນເຄື່ອງ', web: 'ຄົ້ນຫາໃນອິນເຕີເນັດ', skill: 'ເປີດບົດຮຽນ', mcp: 'ໃຊ້ເຄື່ອງມືເຊື່ອມຕໍ່', draw: 'ແຕ້ມຮູບ', other: 'ເຮັດວຽກໜຶ່ງ', aFile: 'ໄຟລ໌ໜຶ່ງ',
  },
  more: '⋯ ເພີ່ມ',
  moreClose: 'ຫຍໍ້',
  foldMore: '▸ ເບິ່ງທັງໝົດ',
  foldLess: '▾ ຫຍໍ້',
  bypassChip: label => ` ⚠ ${label} · Claude ຈະເຮັດໂດຍບໍ່ຖາມສິດ, ອ່ານໃຫ້ດີກ່ອນມອບວຽກ `,
  facts: { mode: 'ໂໝດສິດ', effort: 'Effort', model: 'Model', context: 'Context', usage5: '5 ຊົ່ວໂມງ', usageWeek: 'ອາທິດ' },
  barNote: 'ຢູ່ແຖບລຸ່ມຊ່ອງພິມ',
  barAlt: what => `ແຖບລຸ່ມຊ່ອງພິມ, ບ່ອນທີ່ຕ້ອງເບິ່ງ: ${what}`,
  boardAlt: title => `ກະດານຫ້ອງຮຽນ: ${title}`,
  shotAlt: title => `ຮູບໜ້າຈໍທີ່ມີການໝາຍ: ${title}`,
  shotNote: T => `${T}ໄດ້ໝາຍໃສ່ຮູບໜ້າຈໍແລ້ວ — ເບິ່ງໃນ Claude Desktop`,
  choiceExpired: () => 'ໝົດເວລາແລ້ວ — ຄູແນະນຳຊ່ອງທີ່ເດັ່ນ, ເຈົ້າກົດເອງໄດ້',
  ledger: () => 'ຄູຈົດບັນທຶກຫ້ອງຮຽນ',
  waitHint: () => 'ບໍ່ແນ່ໃຈກໍເລືອກແຖວທຳອິດ — ຄູຈະຊີ້ໃຫ້ເບິ່ງອີກດ້ວຍຮູບ.',
  act: {
    doing: (T, what) => `▸ ${T}ກຳລັງ${what}…`,
    did: (T, what) => `▸ ${T}ຫາກໍ${what}`,
    errored: T => `▸ ${T}ພົບບັນຫາ, ກຳລັງແກ້ໄຂ`,
    interrupted: T => `▸ ${T}ໄດ້ຢຸດວຽກນີ້ແລ້ວ`,
    detail: 'ເບິ່ງລາຍລະອຽດ',
    less: 'ຫຍໍ້',
    groupDoing: (T, parts) => `▸ ${T}ກຳລັງ: ${parts}`,
    groupDid: (T, parts) => `▸ ${T}ຫາກໍ: ${parts}`,
    groupErr: t => `ມີບັນຫາ, ${t}ກຳລັງແກ້ໄຂ`,
    count: {
      read: n => `ອ່ານ ${n} ໄຟລ໌`, find: n => `ຊອກ ${n} ຄັ້ງ`, write: n => `ສ້າງ ${n} ໄຟລ໌`, edit: n => `ແກ້ ${n} ໄຟລ໌`, run: n => `ແລ່ນ ${n} ຄຳສັ່ງ`,
      web: n => `ຄົ້ນຫາ ${n} ຄັ້ງ`, skill: n => `ເປີດ ${n} ບົດຮຽນ`, mcp: n => `ໃຊ້ ${n} ເຄື່ອງມືເຊື່ອມຕໍ່`, draw: n => `ແຕ້ມ ${n} ຮູບ`, other: n => `ເຮັດ ${n} ວຽກອື່ນ`,
    },
    result: 'ຜົນ · ເບິ່ງ',
    resultError: t => `ມີຂໍ້ຜິດພາດ — ${t}ກຳລັງແກ້ໄຂ · ເບິ່ງ`,
    reloaded: 'ໂຫຼດຫ້ອງຮຽນໃໝ່ແລ້ວ ✓',
    command: (T, cmd) => `▸ ${T}ຫາກໍແລ່ນຄຳສັ່ງ /${cmd}`,
    commandError: (T, cmd) => `▸ ຄຳສັ່ງ /${cmd} ມີບັນຫາ — ${T}ກຳລັງແກ້ໄຂ`,
    thinking: T => `${T}ກຳລັງຄິດ…`,
  },
}

export const STR: Record<Lang, Strings> = { vi, lo }
export const isLang = (v: unknown): v is Lang => v === 'vi' || v === 'lo'
// Lời giao việc mod điền vào ô nhập bắt đầu bằng một trong hai dòng này.
export const DELEGATION_HEADS = [vi.delegation.head, lo.delegation.head]
