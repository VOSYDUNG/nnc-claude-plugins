import { test, expect, mock } from 'claude-code/testing'
import type { On } from 'claude-code'
import { feedbackOf, feedbackConfigOf, feedbackBody, feedbackDelivered, CLASS_VERSION, challengeLeft, foldPreview, silenceDue, fitBudget, paletteOf, DARK, LIGHT, stepView, stepOf, bubbleKind, railText, addrLabel, permissionLabel, modelLabel, touchesLedger, podiumOf, boardOf, choicesOf, describeTool, groupParts, toolKind } from '../hooks/register'
import { STR } from '../hooks/i18n'
import { jpegBytes, pngBytes, toB64 } from './shot-fixtures'

// Lớp học NNC v0.7 — lớp luôn mở: phần học theo mốc giáo viên ghi, không điểm danh, hạn 60 giây chỉ cho câu đố,
// tín hiệu hạn mức; v0.6 giữ: một chạm, đổi kiểu, thử thách, sao, huy hiệu, hộp quà.
// Bộ test chạy không có fs thật: trả lời fs.* từ bộ nhớ, bắt tin gửi đi, giả đồng hồ.

const T0 = Date.UTC(2026, 9, 16, 2, 0, 0) // 09:00 Vientiane
const SEC = 1000
const MIN = 60 * SEC

const STATE2 = JSON.stringify({
  schema: 'lop-hoc/2',
  status: 'active',
  segment: { id: '2', title: 'Việc thật của tôi', drive: 'D1' },
  teacher: { kind: 'co', emotion: 'hi' },
  address: 'chị',
  next_action: 'Bấm Giao việc, điền 4 ý',
  destination: 'Bảng tổng hợp theo kênh',
  result_parts: [{ label: 'Đọc file', done: true }, { label: 'Tổng hợp', done: false }],
  help_needed: true,
})

// v0.13 — Mở lớp mang thêm ngôn ngữ và cách gọi (mặc định "Bạn"; có state.address thì lấy từ đó).
const OPEN_BAN = '[Giáo án] Mở lớp · giáo viên co · ngôn ngữ vi · gọi “Bạn”'
const OPEN_CHI = '[Giáo án] Mở lớp · giáo viên co · ngôn ngữ vi · gọi “Chị”'

const FORBIDDEN = /runtime|prompt|state|hook|mod |token|Nhắc Claude|Tạm dừng|Lưu và dừng/i

type Io = {
  sent: string[]
  filled: string[]
  toasts: string[]
  writes: { path: string; text: string }[]
  aborted: string[]
  box: { text: string }
  clock: ReturnType<typeof mock.clock>
  onAbort: () => void
  // Props mới nhất mà nơi vẽ gốc (engine giả) nhận được, theo thành phần.
  renders: Record<string, Record<string, unknown>>
  // Số lần mod đọc byte của tệp nhị phân giả (ảnh chụp).
  blobReads: number
  // Mọi giá trị mod đã ghi vào $.store (khoá → giá trị cuối).
  stored: Record<string, unknown>
}

// Tệp nhị phân giả (ảnh chụp): base64 + giờ sửa; fs.read { as: 'bytes' } và fs.stat đọc từ đây.
type Blob = { b64: string; mtime: number }
const blobBytes = (b64: string) => Math.floor((b64.length * 3) / 4) - (b64.endsWith('==') ? 2 : b64.endsWith('=') ? 1 : 0)

function classroom(on: On, files: Record<string, string>, store: Record<string, unknown> = {}, blobs: Record<string, Blob> = {}): Io {
  const io: Io = { sent: [], filled: [], toasts: [], writes: [], aborted: [], box: { text: '' }, clock: mock.clock(on, { now: T0 }), onAbort: () => {}, renders: {}, blobReads: 0, stored: { ...store } }
  // $.store trong bộ nhớ (như mock.store) nhưng cho test đọc lại mọi giá trị mod đã lưu.
  on('store.get', async (_$, e) => ({ value: io.stored[e.key] }) as never)
  on('store.set', async (_$, e) => {
    io.stored[e.key] = e.value
    return { value: undefined } as never
  })
  on('store.delete', async (_$, e) => {
    delete io.stored[e.key]
    return { value: undefined } as never
  })
  on('store.keys', async () => ({ value: Object.keys(io.stored) }) as never)
  on('session.cwd', async () => ({ value: 'D:/sandbox' }) as never)
  on('session.start', async (_$, e) => ({ cwd: e.cwd }))
  // Engine giả: nơi plugin nhường (next) vẽ một Box có key "engine" — tham chiếu hộp gốc.
  on('ui.render', async ($, e) => {
    io.renders[e.component] = e.props as Record<string, unknown>
    if (e.component === 'AskUserQuestion') return { type: 'engine', ref: 0 } as never
    const { Box } = $.ui.resolve(e as never) as { Box: (p: object) => never }
    return <Box key="engine" />
  })
  const rel = (p: string) => p.split('\\').join('/')
  const find = (p: string) => Object.keys(files).find(k => rel(p) === k || rel(p).endsWith('/' + k))
  const isDir = (p: string) => Object.keys(files).some(k => k.includes('/') && rel(p).endsWith('/' + k.split('/')[0]))
  const findBlob = (p: string) => Object.keys(blobs).find(k => rel(p) === k || rel(p).endsWith('/' + k))
  on('fs.exists', async (_$, e) => ({ value: find(e.path) !== undefined || findBlob(e.path) !== undefined || isDir(e.path) }))
  on('fs.stat', async (_$, e) => {
    const b = findBlob(e.path)
    if (b === undefined) return { deny: 'ENOENT ' + e.path }
    return { value: { kind: 'file', size: blobBytes(blobs[b]!.b64), mtimeMs: blobs[b]!.mtime, isLink: false } } as never
  })
  on('fs.read', async (_$, e) => {
    if ((e as { as?: string }).as === 'bytes') {
      const b = findBlob(e.path)
      if (b === undefined) return { deny: 'missing ' + e.path }
      io.blobReads += 1
      return { value: { base64: blobs[b]!.b64 } } as never
    }
    const k = find(e.path)
    const t = k === undefined ? undefined : files[k]
    if (t === undefined) return { deny: 'missing ' + e.path }
    return { value: t }
  })
  on('fs.write', async (_$, e) => {
    io.writes.push({ path: rel(e.path), text: e.text })
    files[find(e.path) ?? rel(e.path)] = e.text
    return { value: undefined } as never
  })
  on('ui.toast', async (_$, e) => {
    io.toasts.push(e.text)
    return { value: undefined } as never
  })
  on('prompt.submit', async (_$, e) => {
    io.sent.push(e.text)
    return { text: e.text }
  })
  on('prompt.fill', async (_$, e) => {
    io.filled.push(e.text)
    return { isFilled: true }
  })
  on('prompt.read', async () => ({ value: { text: io.box.text, cursor: io.box.text.length } }) as never)
  on('turn.start', async (_$, e) => ({ turnId: e.turnId }))
  on('turn.complete', async () => ({ text: '' }))
  on('turn.abort', async (_$, e) => {
    io.aborted.push(e.turnId)
    io.onAbort()
    return { value: undefined } as never
  })
  on('ui.notice', async () => ({ value: undefined }) as never)
  return io
}

const LONG = { timeoutMs: 60_000 }

const BAND = {
  component: 'AbovePrompt',
  props: { hasSurvey: false, isWorking: false, maxRows: 40, bodyColumns: 100 },
} as const

const cues = (io: Io, s: string) => io.sent.filter(t => t === `[Giáo án] ${s}`).length
const ALL_BUTTONS = ['raise-hand', 'ask-leave', 'leave', 'slower', 'faster', 'hint', 'result-sheet', 'delegate']
const WITH_ALL = { podium: { buttons: ALL_BUTTONS } }

let turnNo = 0
// Giáo viên nói một lượt (Claude chạy một lượt rồi xong).
async function teacherTalks($: never) {
  const d = $ as unknown as { turn: { start: (e: object) => Promise<unknown>; complete: (e: object) => Promise<unknown> } }
  const turnId = `turn-${++turnNo}`
  await d.turn.start({ text: '', turnId })
  await d.turn.complete({ answer: '', durationMs: 0, isAborted: false, turnId, reason: 'answer' })
}

// Chạy đồng hồ, giáo viên nói mỗi 50 giây.
async function run($: never, io: Io, ms: number) {
  let left = ms
  while (left > 0) {
    const step = Math.min(50 * SEC, left)
    await teacherTalks($)
    await io.clock.advance(step)
    left -= step
  }
}

async function noForbiddenWords(ui: { findAll: (q: object) => Promise<{ text: string; props: Record<string, unknown> }[]> }) {
  const all = await ui.findAll({})
  const shown = all.map(el => [el.text, el.props.label, el.props.placeholder, el.props.alt].filter(x => typeof x === 'string').join(' ')).join('\n')
  expect(FORBIDDEN.test(shown)).toBe(false)
}

const iso = (ms: number) => new Date(ms).toISOString()
const v7 = (extra: Record<string, unknown>) =>
  JSON.stringify({ schema: 'lop-hoc/2', status: 'active', segment: { id: '2', title: 'Việc thật của tôi', drive: 'D1' }, teacher: { kind: 'co', emotion: 'giang' }, address: 'chị', ...extra })

const usageOf = (five: number, week: number) => ({
  value: {
    startedAt: 0,
    context: { window: 200000, percent: 34 },
    rateLimits: [
      { kind: 'five_hour', percentUsed: five, resetsAt: '2026-10-16T07:20:00Z' },
      { kind: 'seven_day', percentUsed: week, resetsAt: '2026-10-20T03:00:00Z' },
    ],
  },
})

for (const surface of ['terminal', 'desktop'] as const) {
  test(`${surface}: chọn thầy, Vào lớp gửi "[Giáo án] Mở lớp" (không có thời lượng)`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    expect(await ui.find({ text: /Lớp đang chờ giáo viên/ })).toBeDefined()
    expect(await ui.find({ key: 'm-15' })).toBeUndefined()
    expect(await ui.findAll({ type: 'Svg' })).toHaveLength(surface === 'desktop' ? 1 : 0)
    await noForbiddenWords(ui as never)
    await ui.press({ key: 't-thay' })
    await ui.press({ key: 'enter' })
    expect(io.sent).toContain('[Giáo án] Mở lớp · giáo viên thay · ngôn ngữ vi · gọi “Bạn”')
    expect(await ui.find({ text: /Phần 0 · Vào lớp/ })).toBeDefined()
    // Tầng 3: Giơ tay · Xin phép · ⋯ luôn thấy; Xin nghỉ · Phiếu kết quả nằm sau nhóm "⋯".
    expect(await ui.find({ key: 'more' })).toBeDefined()
    for (const key of ['gio-tay', 'xin-phep']) expect(await ui.find({ key })).toBeDefined()
    expect(await ui.find({ key: 'phieu' })).toBeUndefined()
    expect(await ui.find({ key: 'xin-nghi' })).toBeUndefined()
    await ui.press({ key: 'more' })
    for (const key of ['thiet-lap', 'xin-nghi', 'phieu', 'claude-cua-toi', 'tien-do']) expect(await ui.find({ key })).toBeDefined()
    await noForbiddenWords(ui as never)
    await ui.unmount()
  })

  test(`${surface}: Mở lớp kèm hạn mức thật; ngưỡng đã vượt lúc mở thì không báo lại`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    on('session.usage', async () => usageOf(72, 22))
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    await io.clock.settle()
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(io.sent).toContain('[Giáo án] Mở lớp · giáo viên co · ngôn ngữ vi · gọi “Bạn” · hạn mức 5 giờ 72% · tuần 22%')
    await run($ as never, io, 3 * MIN)
    expect(io.sent.filter(x => x.includes('Hạn mức ·'))).toHaveLength(0)
    await ui.unmount()
  })

  test(`${surface}: lớp luôn mở — không tự chuyển phần, không điểm danh, không giảng khi học viên không tác động`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': STATE2 })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    await teacherTalks($ as never)
    await io.clock.advance(45 * MIN)
    // v0.11: chỉ còn thang im lặng (nấc 1 · 2 · 3, mỗi nấc một lần); không điểm danh, không tín hiệu nào khác.
    expect(io.sent).toEqual([OPEN_CHI, ...[1, 2, 3].map(n => `[Giáo án] Học viên im lặng · nấc ${n}`)])
    expect(await ui.find({ text: /còn ở lớp không|tạm nghỉ/ })).toBeUndefined()
    expect(await ui.find({ key: 'co-mat' })).toBeUndefined()
    expect(await ui.find({ text: /Phần 2 · Việc thật của tôi/ })).toBeDefined()
    await ui.unmount()
  })

  test(`${surface}: phần học theo mốc giáo viên ghi; đếm vòng việc đã chốt`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ segment: { id: '1', title: 'Làm quen nhanh', drive: 'D2' } }) }
    classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(await ui.find({ text: /Phần 1 · Làm quen nhanh/ })).toBeDefined()
    files['.lop-hoc/state.json'] = v7({ segment: { id: '4', title: 'Chốt vòng việc', drive: 'ket-noi' }, loops_done: 2 })
    await teacherTalks($ as never)
    expect(await ui.find({ text: /Phần 4 · Chốt vòng việc/ })).toBeDefined()
    expect(await ui.find({ text: /đã chốt 2 vòng việc/ })).toBeDefined()
    const pane = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'Pane', requestId: 'lop-hoc', props: { title: 'Lớp học NNC' } } as never)
    expect(await pane.find({ text: /→ Phần 4 · Chốt vòng việc/ })).toBeDefined()
    expect(await pane.find({ text: /✓ Phần 2 · Việc thật của tôi/ })).toBeDefined()
    await noForbiddenWords(pane as never)
    await pane.unmount()
    await ui.unmount()
  })

  test(`${surface}: câu hỏi lúc làm việc thật thì chờ học viên; câu đố thì chọn giúp sau 60 giây`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ activity: { kind: 'hands-on', started_at: iso(T0) } }) }
    const io = classroom(on, files)
    let release: () => void = () => {}
    let gate = new Promise<void>(r => { release = r })
    io.onAbort = () => release()
    on('tool.call', async () => {
      await gate
      return { deny: 'Người dùng đã đóng hộp câu hỏi' }
    })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    const d = $ as unknown as { turn: { start: (e: object) => Promise<unknown> }; tool: { call: (e: object) => Promise<unknown> } }
    const questions = [{ question: 'Claude chỉ thấy file ở đâu?', header: 'Hỏi nhanh', multiSelect: false, options: [{ label: 'Trong thư mục làm việc', description: '' }, { label: 'Cả máy', description: '' }] }]
    // Làm việc thật: học viên đang ở Excel, hộp chờ, không đếm giờ.
    await d.turn.start({ text: '', turnId: 'viec' })
    const work = d.tool.call({ tool: 'AskUserQuestion', questions })
    await io.clock.advance(3 * MIN)
    expect(io.aborted).toHaveLength(0)
    expect(await ui.find({ text: /chọn giúp sau/ })).toBeUndefined()
    release()
    await work.catch(() => undefined)
    // Câu đố: 60 giây rồi chọn giúp.
    gate = new Promise<void>(r => { release = r })
    files['.lop-hoc/state.json'] = v7({ activity: { kind: 'quiz', started_at: iso(T0) } })
    await teacherTalks($ as never)
    await d.turn.start({ text: '', turnId: 'do' })
    const quiz = d.tool.call({ tool: 'AskUserQuestion', questions })
    await io.clock.advance(30 * SEC)
    expect(await ui.find({ text: /Cô chọn giúp sau 0:[0-9]{2}/ })).toBeDefined()
    await io.clock.advance(35 * SEC)
    expect(io.aborted).toContain('do')
    expect(io.sent).toContain('[Giáo án] Hết hạn trả lời · chọn giúp Trong thư mục làm việc')
    await quiz.catch(() => undefined)
    await ui.unmount()
  })

  test(`${surface}: hạn mức chạm 70% rồi 90%: báo từng ngưỡng một lần, cần học viên tác động giữa hai tín hiệu`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    let five = 50
    on('session.usage', async () => usageOf(five, 22))
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    await io.clock.settle()
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    five = 75
    await run($ as never, io, 2 * MIN)
    expect(io.sent.filter(x => x.startsWith('[Giáo án] Hạn mức'))).toEqual(['[Giáo án] Hạn mức · 5 giờ 75% · reset 14:20'])
    five = 92
    await run($ as never, io, 2 * MIN)
    // Học viên chưa tác động sau tín hiệu trước: lớp chờ.
    expect(io.sent.filter(x => x.startsWith('[Giáo án] Hạn mức'))).toHaveLength(1)
    io.box.text = 'vâng'
    await io.clock.advance(10 * SEC)
    io.box.text = ''
    await run($ as never, io, MIN)
    expect(io.sent.filter(x => x.startsWith('[Giáo án] Hạn mức'))).toEqual(['[Giáo án] Hạn mức · 5 giờ 75% · reset 14:20', '[Giáo án] Hạn mức · 5 giờ 92% · reset 14:20'])
    await run($ as never, io, 3 * MIN)
    expect(io.sent.filter(x => x.startsWith('[Giáo án] Hạn mức'))).toHaveLength(2)
    await ui.unmount()
  })

  test(`${surface}: Xin phép, Quay lại lớp; Giơ tay mở ô Kể cô nghe; nhịp; Xin nghỉ lưu chỗ`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7(WITH_ALL) })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    await ui.press({ key: 'xin-phep' })
    expect(await ui.find({ key: 'ly-do-gap' })).toBeDefined()
    await ui.press({ key: 'ly-do-nuoc' })
    expect(io.sent).toContain('[Giáo án] Xin phép · đi uống nước')
    expect(await ui.find({ text: /Đang xin phép · đi uống nước/ })).toBeDefined()
    const before = io.sent.length
    await io.clock.advance(10 * MIN)
    expect(io.sent.length).toBe(before)
    await ui.press({ key: 'quay-lai' })
    expect(cues(io, 'Học viên trở lại')).toBe(1)
    await ui.press({ key: 'gio-tay' })
    expect(io.sent).toContain('[Giáo án] Giơ tay')
    expect(await ui.find({ key: 'ke' })).toBeDefined()
    await noForbiddenWords(ui as never)
    await ui.input({ key: 'ke', text: 'Em chưa hiểu context là gì' })
    expect(io.sent).toContain('Em chưa hiểu context là gì')
    expect(await ui.find({ key: 'ke' })).toBeUndefined()
    await ui.press({ key: 'cham' })
    expect(io.sent).toContain('[Giáo án] Nhịp: chậm lại')
    await ui.press({ key: 'nhanh' })
    expect(io.sent).toContain('[Giáo án] Nhịp: nhanh hơn')
    await ui.press({ key: 'xin-nghi' })
    expect(io.sent).toContain('[Giáo án] Xin nghỉ')
    expect(await ui.find({ text: /Đã xin nghỉ · cô đã lưu chỗ/ })).toBeDefined()
    const after = io.sent.length
    await io.clock.advance(40 * MIN)
    expect(io.sent.length).toBe(after)
    await ui.unmount()
  })

  test(`${surface}: bục giảng đọc state: lượt của bạn, kết quả, cần hỗ trợ + soạn tin, phiếu kết quả, form giao việc, thưa cô`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': JSON.stringify({ ...JSON.parse(STATE2), ...WITH_ALL }) })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(await ui.find({ text: /Phần 2 · Việc thật của tôi/ })).toBeDefined()
    expect(await ui.find({ text: /Lượt của bạn · Bấm Giao việc, điền 4 ý/ })).toBeDefined()
    // v0.13: hàng kết quả đã bỏ khỏi bục chính; nằm trong ⋯ → Tiến độ.
    expect(await ui.find({ text: /✓ Đọc file/ })).toBeUndefined()
    expect(await ui.find({ text: /Đang cần người hỗ trợ/ })).toBeDefined()
    expect(await ui.findAll({ type: 'Svg' })).toHaveLength(surface === 'desktop' ? 2 : 0) // hình thầy + thanh bước
    await noForbiddenWords(ui as never)
    await ui.press({ key: 'more' })
    await ui.press({ key: 'tien-do' })
    expect(await ui.find({ text: /✓ Đọc file/ })).toBeDefined()
    expect(await ui.find({ text: /○ Tổng hợp/ })).toBeDefined()
    await ui.press({ key: 'tien-do' })
    expect(await ui.find({ text: /✓ Đọc file/ })).toBeUndefined()
    await ui.press({ key: 'more' })
    await ui.press({ key: 'nho-ho-tro' })
    expect(io.sent).toContain('[Lớp học] Soạn tin nhờ hỗ trợ')
    await ui.press({ key: 'phieu' })
    expect(io.sent).toContain('[Lớp học] Xuất phiếu kết quả')
    await ui.press({ key: 'chua-dung' })
    expect(io.filled).toContain('Thưa cô, chỗ này chưa đúng: ')
    await ui.press({ key: 'b-form' })
    await ui.press({ key: 'form-fill' })
    expect(await ui.find({ text: /Ghi "Mục tiêu" trước/ })).toBeDefined()
    await ui.input({ key: 'f-goal', text: 'Tổng hợp doanh số theo kênh' })
    await ui.input({ key: 'f-check', text: 'Đối chiếu tổng với cột gốc' })
    await ui.press({ key: 'form-fill' })
    const filled = io.filled.find(t => t.startsWith('Giao việc —')) ?? ''
    expect(filled).toContain('Mục tiêu: Tổng hợp doanh số theo kênh')
    expect(filled).toContain('Cách kiểm: Đối chiếu tổng với cột gốc')
    expect(await ui.find({ key: 'f-goal' })).toBeUndefined()
    await ui.unmount()
  })

  test(`${surface}: lớp tiếng Lào — cửa lớp một thứ tiếng, nút chọn ngôn ngữ ghi bằng chính tiếng đó; bục, nút, giao việc bằng tiếng Lào; tín hiệu giáo viên vẫn tiếng Việt`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC' }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    // v0.13: một ngôn ngữ cho cả bục — chưa chọn thì tiếng Việt, không có dòng tiếng Lào; nút ພາສາລາວ ghi bằng tiếng Lào.
    expect(await ui.find({ text: /Lớp đang chờ giáo viên/ })).toBeDefined()
    expect(await ui.find({ text: /ຫ້ອງຮຽນລໍຖ້າຄູ/ })).toBeUndefined()
    expect(await ui.find({ key: 'lang-lo' })).toBeDefined()
    // Chọn tiếng Lào: mọi chữ đổi sang tiếng Lào, không còn dòng tiếng Việt (lựa chọn của học viên thắng state.json).
    await ui.press({ key: 'lang-lo' })
    expect(await ui.find({ text: /ເລືອກພາສາ/ })).toBeDefined()
    expect(await ui.find({ text: /ຫ້ອງຮຽນລໍຖ້າຄູ/ })).toBeDefined()
    expect(await ui.find({ text: /Lớp đang chờ giáo viên/ })).toBeUndefined()
    await ui.press({ key: 'enter' })
    expect(io.sent).toContain('[Giáo án] Mở lớp · giáo viên co · ngôn ngữ lo · gọi “ທ່ານ”')
    // Giáo viên ghi language: 'vi' — không đổi được lựa chọn của học viên.
    files['.lop-hoc/state.json'] = v7({ language: 'vi', segment: { id: '2', title: 'Việc thật của tôi', drive: 'D1' }, ...WITH_ALL })
    await teacherTalks($ as never)
    expect(await ui.find({ text: /ພາກ 2 · ວຽກແທ້ຂອງຂ້ອຍ/ })).toBeDefined()
    expect(await ui.find({ text: /Phần 2/ })).toBeUndefined()
    await ui.press({ key: 'xin-phep' })
    expect(await ui.find({ text: /ໄປດື່ມນ້ຳ/ })).toBeDefined()
    await ui.press({ key: 'ly-do-nuoc' })
    expect(io.sent).toContain('[Giáo án] Xin phép · đi uống nước')
    expect(await ui.find({ text: /ກຳລັງຂໍອະນຸຍາດ · ໄປດື່ມນ້ຳ/ })).toBeDefined()
    await ui.press({ key: 'quay-lai' })
    await ui.press({ key: 'goi-y' })
    expect(io.sent).toContain('[Lớp học] Cô gợi ý giúp')
    await ui.press({ key: 'b-form' })
    await ui.input({ key: 'f-goal', text: 'ສັງລວມຍອດຂາຍ' })
    await ui.press({ key: 'form-fill' })
    const filled = io.filled.find(t => t.startsWith('ມອບວຽກ —')) ?? ''
    expect(filled).toContain('ເປົ້າໝາຍ: ສັງລວມຍອດຂາຍ')
    await ui.unmount()
    // Lần mở sau: nhớ tiếng Lào ngay từ cửa lớp, dòng công cụ cũng tiếng Lào.
    const tool = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'ToolUse', props: { tool_use_id: 't1', tool: 'Read', input: { file_path: 'D:/x/bang-tinh-mau.xlsx' }, isRunning: true, isErrored: false, isInterrupted: false } } as never)
    expect(await tool.find({ text: /ຄູກຳລັງອ່ານ bang-tinh-mau.xlsx…/ })).toBeDefined()
    await tool.unmount()
  })

  test(`${surface}: bảng usage giáo viên mở (panel) có số liệu thật, giờ reset Vientiane`, LONG, async ($, on) => {
    const st = JSON.stringify({ schema: 'lop-hoc/2', status: 'active', segment: { id: '1', title: 'Làm quen nhanh', drive: 'D2' }, teacher: { kind: 'thay', emotion: 'giang' }, panel: 'usage' })
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': st })
    on('session.model', async () => ({ value: 'claude-opus-5-5' }))
    on('session.usage', async () => usageOf(41, 22))
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    await io.clock.settle()
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    expect(await ui.find({ text: /claude-opus-5-5 · context 34% · 5 giờ 41% \(reset 14:20\) · tuần 22% \(reset 20\/10 10:00\)/ })).toBeDefined()
    await ui.press({ key: 'enter' })
    expect(await ui.find({ text: /5 giờ: đã dùng 41% · reset lúc 14:20/ })).toBeDefined()
    expect(await ui.findAll({ type: 'Svg' })).toHaveLength(surface === 'desktop' ? 4 : 0) // thầy + hai thẻ hạn mức + thanh bước
    await noForbiddenWords(ui as never)
    await ui.unmount()
  })

  test(`${surface}: mọi tín hiệu "[Giáo án]" ẩn với học viên`, LONG, async ($, on) => {
    classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const msg = (text: string) => $.ui.mount({ plugin: 'lop-hoc', surface, component: 'UserMessage', props: { text, origin: { kind: 'plugin', name: 'lop-hoc' }, isExpanded: false } } as never)
    for (const t of ['[Giáo án] Giơ tay', '[Giáo án] Mở lớp · giáo viên co · hạn mức 5 giờ 41% · tuần 22%', '[Giáo án] Hạn mức · 5 giờ 92% · reset 14:20', '[Giáo án] Học viên trở lại']) {
      const hidden = await msg(t)
      expect(await hidden.find({ text: /\S/ })).toBeUndefined()
      expect(await hidden.find({ key: 'engine' })).toBeUndefined()
      await hidden.unmount()
    }
    const chip = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'UserMessage', props: { text: '[Lớp học] Xuất phiếu kết quả', origin: { kind: 'plugin', name: 'lop-hoc' }, isExpanded: false } } as never)
    expect(await chip.find({ text: /Bạn bấm · Xuất phiếu kết quả/ })).toBeDefined()
    await chip.unmount()
    const typed = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'UserMessage', props: { text: 'bảng doanh số tuần', origin: { kind: 'composer' }, isExpanded: false } } as never)
    expect(await typed.find({ text: /^Bạn$/ })).toBeDefined()
    await typed.unmount()
  })

  test(`${surface}: hộp câu hỏi gốc có một dòng tiêu đề lớp học và giữ hộp gốc đúng một lần`, LONG, async ($, on) => {
    classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const band = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await band.press({ key: 't-thay' })
    await band.press({ key: 'enter' })
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'AskUserQuestion', props: { tool: 'AskUserQuestion', questions: [{ question: 'Chọn?', header: 'Hỏi', multiSelect: false, options: [{ label: 'A', description: '' }, { label: 'B', description: '' }] }] } } as never)
    expect(await ui.find({ text: 'Thầy hỏi · Phần 0 · Vào lớp' })).toBeDefined()
    expect(await ui.findAll({ type: 'engine' })).toHaveLength(1)
    await noForbiddenWords(ui as never)
    await ui.unmount()
    await band.unmount()
  })

  test(`${surface}: lời Claude thành lời giáo viên, có avatar và tiêu đề phần`, LONG, async ($, on) => {
    classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const band = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await band.press({ key: 'enter' })
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'AssistantMessage', props: { text: 'Chào chị', isFirstOfReply: true } } as never)
    expect(await ui.find({ text: /^\s*Cô · Phần 0 · Vào lớp\s*$/ })).toBeDefined()
    expect(await ui.findAll({ type: 'Svg' })).toHaveLength(surface === 'desktop' ? 1 : 0)
    expect(await ui.findAll({ key: 'engine' })).toHaveLength(1)
    await ui.unmount()
    await band.unmount()
  })

  test(`${surface}: dòng công cụ có câu dễ hiểu`, LONG, async ($, on) => {
    classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'ToolUse', props: { tool_use_id: 't1', tool: 'Read', input: { file_path: 'D:/x/bang-tinh-mau.xlsx' }, isRunning: true, isErrored: false, isInterrupted: false } } as never)
    expect(await ui.find({ text: /Cô đang đọc bang-tinh-mau.xlsx…/ })).toBeDefined()
    await ui.unmount()
  })

  test(`${surface}: state lop-hoc/1 cũ vẫn đọc được, không vỡ`, LONG, async ($, on) => {
    const v1 = JSON.stringify({ schema: 'lop-hoc/1', status: 'active', stage: 3, next_action: 'Tạo bản nháp biên bản', result_parts: [{ label: 'Bản nháp', done: false }] })
    classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v1 })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(await ui.find({ text: /Lượt của bạn · Tạo bản nháp biên bản/ })).toBeDefined()
    await ui.press({ key: 'more' })
    await ui.press({ key: 'tien-do' })
    expect(await ui.find({ text: /○ Bản nháp/ })).toBeDefined()
    const pane = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'Pane', requestId: 'lop-hoc', props: { title: 'Lớp học NNC' } } as never)
    expect(await pane.find({ text: /→ Phần 2 · Việc thật của tôi/ })).toBeDefined()
    expect(await pane.find({ text: /○ Phần 4 · Chốt vòng việc/ })).toBeDefined()
    await noForbiddenWords(pane as never)
    await pane.unmount()
    await ui.unmount()
  })

  test(`${surface}: mở lại app sau 2 ngày (cả lớp lưu từ bản 0.6): giáo viên chờ, bấm Tiếp tục thì học tiếp`, LONG, async ($, on) => {
    const saved06 = { minutes: 30, teacher: 'thay', startedAt: T0 - 2 * 24 * 60 * MIN, shiftMs: 0, pausedAt: null, pause: null, pauseNote: '', over: null, announced: 2, sent: ['open', 'seg-1', 'seg-2'], lastCueAt: T0 - 2 * 24 * 60 * MIN, strikes: 0, idleFrom: T0, rollCallAt: null, absences: 0 }
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': STATE2 }, { 'lesson:d:/sandbox': { lesson: saved06, savedAt: T0 - 2 * 24 * 60 * MIN } })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    expect(await ui.find({ text: /Thầy: thầy vẫn ở đây — bấm Tiếp tục/ })).toBeDefined()
    await io.clock.advance(MIN)
    expect(io.sent).toHaveLength(0)
    await ui.press({ key: 'tiep-tuc' })
    expect(io.sent).toContain('[Giáo án] Học viên trở lại')
    expect(await ui.find({ text: /Phần 2 · Việc thật của tôi/ })).toBeDefined()
    await ui.unmount()
  })

  test(`${surface}: không còn tín hiệu "Kiểm phần học" theo phút — phần 0 hay 1 đứng yên bao lâu cũng không nhắc`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC' }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    await run($ as never, io, 20 * MIN)
    io.box.text = 'vâng'
    await io.clock.advance(10 * SEC)
    io.box.text = ''
    files['.lop-hoc/state.json'] = v7({ segment: { id: '1', title: 'Làm quen nhanh', drive: 'D2' } })
    await run($ as never, io, 30 * MIN)
    expect(io.sent.filter(x => x.includes('Kiểm phần học'))).toHaveLength(0)
    expect(io.sent).toEqual([OPEN_BAN])
    await ui.unmount()
  })

  test(`${surface}: context của phiên đầy 70% thì báo giáo viên một lần`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': STATE2 })
    let ctx = 40
    on('session.usage', async () => ({ value: { startedAt: 0, context: { window: 200000, percent: ctx }, rateLimits: [] } }))
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    await io.clock.settle()
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    ctx = 75
    await run($ as never, io, 2 * MIN)
    expect(io.sent.filter(x => x.includes('context'))).toEqual(['[Giáo án] Hạn mức · context 75%'])
    io.box.text = 'vâng'
    await io.clock.advance(10 * SEC)
    io.box.text = ''
    await run($ as never, io, 3 * MIN)
    expect(io.sent.filter(x => x.includes('context'))).toHaveLength(1)
    await ui.unmount()
  })

  test(`${surface}: ngoài thư mục lớp học thì không vẽ gì, không gửi gì`, LONG, async ($, on) => {
    const io = classroom(on, { 'README.md': 'x' })
    await $.session.start({ cwd: 'D:/other', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    expect(await ui.find({ text: /Lớp học NNC/ })).toBeUndefined()
    await io.clock.advance(10 * MIN)
    expect(io.sent).toHaveLength(0)
    const msg = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'UserMessage', props: { text: '[Giáo án] Giơ tay', origin: { kind: 'plugin', name: 'x' }, isExpanded: false } } as never)
    expect(await msg.find({ key: 'engine' })).toBeDefined()
    await msg.unmount()
    await ui.unmount()
  })
}

// ── v0.6 (hợp đồng §8) ─────────────────────────────────────────────────────────
const v6 = (extra: Record<string, unknown>) =>
  JSON.stringify({ schema: 'lop-hoc/2', status: 'active', segment: { id: '1', title: 'Nhập môn', drive: 'D2' }, teacher: { kind: 'co', emotion: 'giang' }, address: 'chị', ...extra })
const ONE = { label: 'Cho Claude đọc bảng đơn hàng', text: 'Đọc file assets/mau/bang-tinh-mau.xlsx và cho tôi biết có mấy kênh bán hàng.' }
const BADGE1 = { id: 'giao-viec-dau-tien', label: 'Người giao việc đầu tiên' }
const BADGE2 = { id: 'bat-loi', label: 'Người bắt lỗi' }
// Khoá của Svg/Text không lộ ra khi tìm; tìm hình theo lời mô tả (alt).
type Found = { type: string; text: string; props: Record<string, unknown> }
async function svgByAlt(ui: unknown, re: RegExp): Promise<Found | undefined> {
  const all = (await (ui as { findAll: (q: object) => Promise<Found[]> }).findAll({ type: 'Svg' })) ?? []
  return all.find(el => typeof el.props.alt === 'string' && re.test(el.props.alt))
}

for (const surface of ['terminal', 'desktop'] as const) {
  test(`${surface}: một chạm điền sẵn ô nhập (không gửi), ẩn sau khi bấm, hiện lại khi đổi lệnh`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v6({ one_touch: ONE }) }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    const btn = await ui.find({ key: 'one-touch' })
    expect(btn?.props.label).toBe('▶ Cho Claude đọc bảng đơn hàng')
    await noForbiddenWords(ui as never)
    const sentBefore = io.sent.length
    await ui.press({ key: 'one-touch' })
    expect(io.filled).toContain(ONE.text)
    expect(io.sent.length).toBe(sentBefore)
    expect(io.sent).not.toContain(ONE.text)
    expect(io.toasts).toContain('Đã điền sẵn — bấm Enter để giao cho Claude')
    expect(await ui.find({ key: 'one-touch' })).toBeUndefined()
    // Nạp lại state, lệnh không đổi: vẫn ẩn.
    await teacherTalks($ as never)
    expect(await ui.find({ key: 'one-touch' })).toBeUndefined()
    // Giáo viên đổi lệnh: nút hiện lại.
    files['.lop-hoc/state.json'] = v6({ one_touch: { label: 'Cho Claude tổng hợp theo kênh', text: 'Tổng hợp doanh số theo kênh.' } })
    await teacherTalks($ as never)
    expect((await ui.find({ key: 'one-touch' }))?.props.label).toBe('▶ Cho Claude tổng hợp theo kênh')
    await ui.unmount()
  })

  test(`${surface}: cùng kiểu tương tác quá 4 phút giờ học thì báo đổi kiểu một lần; lúc xin phép không tính; làm việc thật không nhắc`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v6({ activity: { kind: 'game:doan-xem', started_at: iso(T0) }, ...WITH_ALL }) })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    await run($ as never, io, 130 * SEC)
    // Xin phép 3 phút: đồng hồ lớp dừng.
    await ui.press({ key: 'xin-phep' })
    await ui.press({ key: 'ly-do-nuoc' })
    await io.clock.advance(3 * MIN)
    await ui.press({ key: 'quay-lai' })
    await run($ as never, io, 100 * SEC)
    const changed = (t: string) => t.startsWith('[Giáo án] Đổi kiểu tương tác')
    expect(io.sent.filter(changed)).toHaveLength(0)
    await run($ as never, io, 30 * SEC)
    expect(io.sent.filter(changed)).toEqual(['[Giáo án] Đổi kiểu tương tác · game:doan-xem · 4 phút'])
    await run($ as never, io, 3 * MIN)
    expect(io.sent.filter(changed)).toHaveLength(1)
    await ui.unmount()
  })

  test(`${surface}: thử thách có vòng đếm ngược; về 0 báo hết giờ một lần, theo luật ô nhập trống`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v6({ challenge: { title: 'Tìm 3 dòng thiếu giá', seconds: 60, started_at: iso(T0) } }) })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    await io.clock.advance(30 * SEC)
    expect(await ui.find({ text: /Tìm 3 dòng thiếu giá/ })).toBeDefined()
    if (surface === 'desktop') expect(await svgByAlt(ui, /^Thử thách còn 0:[0-9]{2}$/)).toBeDefined()
    else expect(await ui.find({ text: /Thử thách 0:[0-9]{2} · Tìm 3 dòng thiếu giá/ })).toBeDefined()
    await noForbiddenWords(ui as never)
    io.box.text = 'em đang gõ'
    await io.clock.advance(40 * SEC)
    expect(cues(io, 'Hết giờ thử thách · Tìm 3 dòng thiếu giá')).toBe(0)
    io.box.text = ''
    await io.clock.advance(10 * SEC)
    expect(cues(io, 'Hết giờ thử thách · Tìm 3 dòng thiếu giá')).toBe(1)
    await run($ as never, io, 2 * MIN)
    expect(cues(io, 'Hết giờ thử thách · Tìm 3 dòng thiếu giá')).toBe(1)
    await ui.unmount()
  })

  test(`${surface}: thử thách đã hết giờ quá 10 phút thì bỏ qua`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v6({ challenge: { title: 'Thử thách cũ', seconds: 60, started_at: iso(T0 - 20 * MIN) } }) })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    await run($ as never, io, 3 * MIN)
    expect(io.sent.filter(t => t.includes('Hết giờ thử thách'))).toHaveLength(0)
    expect(await ui.find({ text: /Thử thách cũ/ })).toBeUndefined()
    expect(await svgByAlt(ui, /Thử thách/)).toBeUndefined()
    await ui.unmount()
  })

  test(`${surface}: sao hiện trên bục`, LONG, async ($, on) => {
    classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v6({ stars: 3 }) })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    if (surface === 'terminal') expect(await ui.find({ text: '★ 3' })).toBeDefined()
    else expect(await svgByAlt(ui, /^3 sao trong buổi$/)).toBeDefined()
    expect(await ui.findAll({ type: 'Svg' })).toHaveLength(surface === 'desktop' ? 3 : 0) // thầy + sao + thanh bước
    await noForbiddenWords(ui as never)
    await ui.unmount()
  })

  test(`${surface}: huy hiệu mới chép vào huy-hieu.json, chúc mừng một lần, nạp lại không trùng; ẩn kệ khi có câu hỏi`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v6({ badges_new: [BADGE1, { ...BADGE1 }] }) }
    const io = classroom(on, files)
    let release: () => void = () => {}
    const gate = new Promise<void>(r => { release = r })
    on('tool.call', async () => {
      await gate
      return { deny: 'Người dùng đã đóng hộp câu hỏi' }
    })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    expect(io.writes).toHaveLength(1)
    expect(io.writes[0]?.path).toMatch(/\.lop-hoc\/huy-hieu\.json$/)
    const saved = JSON.parse(io.writes[0]?.text ?? '{}')
    expect(saved).toEqual({ schema: 'lop-hoc/huy-hieu-1', badges: [{ ...BADGE1, date: '2026-10-16' }] })
    expect(io.toasts.filter(t => t === 'Huy hiệu mới: Người giao việc đầu tiên')).toHaveLength(1)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    if (surface === 'terminal') expect(await ui.find({ text: /Huy hiệu: Người giao việc đầu tiên/ })).toBeDefined()
    else expect(await svgByAlt(ui, /^Huy hiệu: Người giao việc đầu tiên$/)).toBeDefined()
    // Giáo viên vui 6 giây rồi trở lại cảm xúc giáo viên ghi.
    if (surface === 'desktop') {
      const cheering = (await svgByAlt(ui, /trên bục giảng/))?.props.source
      await io.clock.advance(7 * SEC)
      const calm = (await svgByAlt(ui, /trên bục giảng/))?.props.source
      expect(typeof cheering).toBe('string')
      expect(cheering).not.toBe(calm)
    }
    // Nạp lại nhiều lần: không ghi lại, không chúc mừng lại.
    await teacherTalks($ as never)
    await teacherTalks($ as never)
    expect(io.writes).toHaveLength(1)
    expect(io.toasts.filter(t => t.startsWith('Huy hiệu mới'))).toHaveLength(1)
    // Thêm một huy hiệu: ghi đúng một lần nữa, giữ cái cũ.
    files['.lop-hoc/state.json'] = v6({ badges_new: [BADGE1, BADGE2] })
    await teacherTalks($ as never)
    expect(io.writes).toHaveLength(2)
    expect(JSON.parse(io.writes[1]?.text ?? '{}').badges.map((b: { id: string }) => b.id)).toEqual([BADGE1.id, BADGE2.id])
    expect(io.toasts.filter(t => t.startsWith('Huy hiệu mới'))).toEqual(['Huy hiệu mới: Người giao việc đầu tiên', 'Huy hiệu mới: Người bắt lỗi'])
    await noForbiddenWords(ui as never)
    // Hộp câu hỏi gốc đang mở: ẩn kệ huy hiệu.
    const d = $ as unknown as { turn: { start: (e: object) => Promise<unknown> }; tool: { call: (e: object) => Promise<unknown> } }
    await d.turn.start({ text: '', turnId: 'hoi' })
    const call = d.tool.call({ tool: 'AskUserQuestion', questions: [{ question: 'Chọn?', header: 'Hỏi', multiSelect: false, options: [{ label: 'A', description: '' }] }] })
    await io.clock.advance(5 * SEC)
    expect(await ui.find({ text: /Huy hiệu:/ })).toBeUndefined()
    expect(await svgByAlt(ui, /Huy hiệu/)).toBeUndefined()
    release()
    await call.catch(() => undefined)
    await ui.unmount()
  })

  test(`${surface}: hộp quà — bấm Mở hộp quà gửi "[Lớp học] Mở hộp quà" như học viên`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v6({ gift_box: true }) })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(await ui.find({ key: 'hop-qua' })).toBeDefined()
    if (surface === 'desktop') expect(await svgByAlt(ui, /^Hộp quà$/)).toBeDefined()
    else expect(await ui.find({ text: /Có một hộp quà cho bạn/ })).toBeDefined()
    await noForbiddenWords(ui as never)
    await ui.press({ key: 'hop-qua' })
    expect(io.sent.filter(t => t === '[Lớp học] Mở hộp quà')).toHaveLength(1)
    expect(await ui.find({ key: 'hop-qua' })).toBeUndefined()
    if (surface === 'desktop') expect(await svgByAlt(ui, /^Hộp quà đang mở$/)).toBeDefined()
    else expect(await ui.find({ text: /Hộp quà đang mở/ })).toBeDefined()
    await io.clock.advance(5 * SEC)
    expect(await svgByAlt(ui, /Hộp quà/)).toBeUndefined()
    expect(await ui.find({ text: /Hộp quà|hộp quà cho bạn/ })).toBeUndefined()
    expect(await ui.find({ key: 'hop-qua' })).toBeUndefined()
    await ui.unmount()
  })

  test(`${surface}: ngân sách dòng — hình thu thành "Xem hình" khi có nút một chạm hoặc khi chật; dải chật chỉ còn thanh bước + ⋯; không có hàng đích/kết quả/nhãn sống; không có từ kỹ thuật`, LONG, async ($, on) => {
    const board = { title: 'Bảng tổng hợp', lines: ['Kênh OTC', 'Kênh HC'] }
    const st = v6({ one_touch: ONE, stars: 2, challenge: { title: 'Thử 60 giây', seconds: 60, started_at: iso(T0) }, gift_box: true, badges_new: [BADGE1], destination: 'Bảng tổng hợp theo kênh', result_parts: [{ label: 'Đọc file', done: true }], board, podium: { show: ['model', 'mode'] }, ...WITH_ALL })
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': st })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const roomy = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND, props: { ...BAND.props, maxRows: 80 } } as never)
    await roomy.press({ key: 'enter' })
    // Hàng đích, hàng kết quả, nhãn thông tin sống đã bỏ khỏi bục chính.
    expect(await roomy.find({ text: /Đích:/ })).toBeUndefined()
    expect(await roomy.find({ text: /Đọc file/ })).toBeUndefined()
    expect(await roomy.find({ text: /^Model |^Chế độ / })).toBeUndefined()
    // Tầng 1 có nút một chạm: hình thu thành nút "Xem hình" (bấm mở, "Ẩn hình" đóng).
    expect(await roomy.find({ key: 'one-touch' })).toBeDefined()
    expect(await roomy.find({ text: 'Bảng tổng hợp' })).toBeUndefined()
    expect((await roomy.find({ key: 'xem-hinh' }))?.props.label).toBe('Xem hình')
    await roomy.press({ key: 'xem-hinh' })
    expect(await roomy.find({ text: 'Bảng tổng hợp' })).toBeDefined()
    expect((await roomy.find({ key: 'xem-hinh' }))?.props.label).toBe('Ẩn hình')
    await roomy.press({ key: 'xem-hinh' })
    expect(await roomy.find({ text: 'Bảng tổng hợp' })).toBeUndefined()
    await roomy.unmount()
    // Chật (8 dòng): vẫn có nút một chạm và hộp quà; tầng 3 chỉ còn thanh bước + ⋯ (Giơ tay, Xin phép chuyển vào ⋯).
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND, props: { ...BAND.props, maxRows: 8 } } as never)
    expect(await ui.find({ key: 'one-touch' })).toBeDefined()
    expect(await ui.find({ key: 'hop-qua' })).toBeDefined()
    expect(await ui.find({ key: 'gio-tay' })).toBeUndefined()
    expect(await ui.find({ key: 'xin-phep' })).toBeUndefined()
    expect(await ui.find({ key: 'more' })).toBeDefined()
    await ui.press({ key: 'more' })
    expect(await ui.find({ key: 'gio-tay' })).toBeDefined()
    expect(await ui.find({ key: 'xin-phep' })).toBeDefined()
    await noForbiddenWords(ui as never)
    expect(io.toasts.some(t => FORBIDDEN.test(t))).toBe(false)
    await ui.unmount()
  })

  test(`${surface}: ngân sách dòng — không có nút một chạm: hình hiện khi đủ chỗ, thu thành "Xem hình" khi chật; học viên mở thì giữ mở đến khi state.json đổi`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({ board: { title: 'Bảng nhỏ', lines: ['một', 'hai'] } }) }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const roomy = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await roomy.press({ key: 'enter' })
    expect(await roomy.find({ text: 'Bảng nhỏ' })).toBeDefined()
    expect(await roomy.find({ key: 'xem-hinh' })).toBeUndefined()
    await roomy.unmount()
    const tight = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND, props: { ...BAND.props, maxRows: 9 } } as never)
    expect(await tight.find({ text: 'Bảng nhỏ' })).toBeUndefined()
    expect(await tight.find({ key: 'gio-tay' })).toBeDefined()
    await tight.press({ key: 'xem-hinh' })
    expect(await tight.find({ text: 'Bảng nhỏ' })).toBeDefined()
    expect((await tight.find({ key: 'xem-hinh' }))?.props.label).toBe('Ẩn hình')
    // Giáo viên ghi lại state: lựa chọn của học viên hết hiệu lực, chật thì thu lại.
    files['.lop-hoc/state.json'] = v8({ board: { title: 'Bảng nhỏ', lines: ['một', 'hai', 'ba'] } })
    await io.clock.advance(2 * SEC)
    expect(await tight.find({ text: 'Bảng nhỏ' })).toBeUndefined()
    await tight.unmount()
  })
}

test('fitBudget: bỏ khoảng cách → thu hình → hàng sao/quà thành chữ → tầng 3 chỉ còn ⋯; hình do học viên mở thì không bị thu', () => {
  const base = { maxRows: 20, base: 8, board: 10, boardHidden: 1, deco: 4, decoCompact: 2, tier3: 2, tier3Min: 1, seps: 2, boardMode: 'auto' as const }
  expect(fitBudget({ ...base, maxRows: 26 })).toMatchObject({ showBoard: true, compact: false, tier3Min: false, gap: 1, rows: 26 })
  expect(fitBudget({ ...base, maxRows: 24 })).toMatchObject({ showBoard: true, gap: 0, rows: 24 })
  expect(fitBudget({ ...base, maxRows: 16 })).toMatchObject({ showBoard: false, compact: false, tier3Min: false, gap: 0, rows: 15 })
  expect(fitBudget({ ...base, maxRows: 13 })).toMatchObject({ showBoard: false, compact: true, tier3Min: false })
  expect(fitBudget({ ...base, maxRows: 12 })).toMatchObject({ showBoard: false, compact: true, tier3Min: true, rows: 12 })
  expect(fitBudget({ ...base, maxRows: 5 })).toMatchObject({ showBoard: false, compact: true, tier3Min: true })
  expect(fitBudget({ ...base, maxRows: 0 })).toMatchObject({ showBoard: true, compact: false, tier3Min: false, gap: 1 })
  expect(fitBudget({ ...base, boardMode: 'hide' })).toMatchObject({ showBoard: false })
  expect(fitBudget({ ...base, maxRows: 5, boardMode: 'show' })).toMatchObject({ showBoard: true, compact: true, tier3Min: true })
})
test('thử thách thiếu giờ bắt đầu: mod tự đóng dấu lúc thấy lần đầu, đếm lùi từ đó', async () => {
  const c = { title: 'Tìm 3 dòng lỗi — kiểm đóng dấu', seconds: 60, started_at: '' }
  const t0 = 1_800_000_000_000
  expect(challengeLeft(c, t0)?.leftMs).toBe(60_000)
  expect(challengeLeft(c, t0 + 20_000)?.leftMs).toBe(40_000)
  expect(challengeLeft(c, t0 + 61_000)?.leftMs).toBe(0)
  const future = { title: 'Giờ ghi sai ở tương lai', seconds: 30, started_at: new Date(t0 + 3_600_000).toISOString() }
  expect(challengeLeft(future, t0)?.leftMs).toBe(30_000)
})

// ── v0.8: giáo viên dựng sân khấu (thiết kế docs/oser-r2/LOP-HOC-V08-THIET-KE.md) ───────────────
const v8 = (extra: Record<string, unknown>) => v7(extra)
const mockClaude = (on: On) => {
  on('session.model', async () => ({ value: 'claude-opus-5-5' }))
  on('session.usage', async () => usageOf(41, 22))
}
const SVG_DIRTY =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100" onload="boom()"><script>alert(1)</script><foreignObject><div>x</div></foreignObject><a href="https://evil.example/x"><rect width="10" height="10" onclick="y()"/></a><circle cx="5" cy="5" r="4" fill="#008816"/></svg>'

for (const surface of ['terminal', 'desktop'] as const) {
  test(`${surface}: đồng hồ 1,5 giây nạp lại state.json khi chữ đổi — bục theo kịp phần 0 → 1 → 3 dù không có lượt giảng nào; file ghi dở không tụt về Phần 0`, LONG, async ($, on) => {
    const seg = (id: string, title: string, drive: string) => v8({ segment: { id, title, drive } })
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': seg('0', 'Vào lớp', 'ket-noi') }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(await ui.find({ text: /Phần 0 · Vào lớp/ })).toBeDefined()
    files['.lop-hoc/state.json'] = seg('1', 'Làm quen nhanh', 'D2')
    await io.clock.advance(2 * SEC)
    expect(await ui.find({ text: /Phần 1 · Làm quen nhanh/ })).toBeDefined()
    files['.lop-hoc/state.json'] = seg('3', 'Thử thách theo nhịp của bạn', 'D3')
    await io.clock.advance(2 * SEC)
    expect(await ui.find({ text: /Phần 3 · Thử thách theo nhịp của bạn/ })).toBeDefined()
    // Giáo viên đang ghi dở (JSON cụt) hoặc ghi thiếu segment: giữ phần đang hiển thị.
    files['.lop-hoc/state.json'] = '{"schema":"lop-hoc/2","status":"act'
    await io.clock.advance(2 * SEC)
    expect(await ui.find({ text: /Phần 3 ·/ })).toBeDefined()
    files['.lop-hoc/state.json'] = JSON.stringify({ schema: 'lop-hoc/2', status: 'active', next_action: 'Làm bước tiếp' })
    await io.clock.advance(2 * SEC)
    expect(await ui.find({ text: /Phần 3 ·/ })).toBeDefined()
    expect(await ui.find({ text: /Phần 0/ })).toBeUndefined()
    // Lời giảng vẽ lúc này mang đúng phần, không dính Phần 0.
    const msg = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'AssistantMessage', props: { text: 'Chào', isFirstOfReply: true } } as never)
    expect(await msg.find({ text: /Cô · Phần 3 · Thử thách theo nhịp của bạn/ })).toBeDefined()
    await msg.unmount()
    files['.lop-hoc/state.json'] = seg('4', 'Chốt vòng việc', 'ket-noi')
    await io.clock.advance(2 * SEC)
    expect(await ui.find({ text: /Phần 4 · Chốt vòng việc/ })).toBeDefined()
    // Đồng hồ chỉ đọc: không gửi thêm gì.
    expect(io.sent).toEqual([OPEN_CHI])
    await ui.unmount()
  })

  test(`${surface}: chế độ quyền — Mở lớp kèm chế độ, model, hạn mức; đổi chế độ gửi một lần; Bypass có nhãn cảnh báo`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    mockClaude(on)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    await io.clock.settle()
    // Thanh dưới do app vẽ: mod chỉ đọc nhãn, giữ nguyên thanh gốc.
    const bar = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'SessionMode', props: { modes: ['focus', 'Bypass permissions'] } } as never)
    expect(await bar.find({ key: 'engine' })).toBeDefined()
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    expect(await ui.find({ text: /⚠ Bypass permissions/ })).toBeDefined()
    await ui.press({ key: 'enter' })
    expect(io.sent).toContain('[Giáo án] Mở lớp · giáo viên co · ngôn ngữ vi · gọi “Bạn” · chế độ Bypass permissions · model claude-opus-5-5 · hạn mức 5 giờ 41% · tuần 22%')
    expect(await ui.find({ text: /⚠ Bypass permissions/ })).toBeDefined()
    await noForbiddenWords(ui as never)
    await io.clock.advance(5 * SEC)
    expect(io.sent.filter(x => x.includes('Chế độ quyền'))).toHaveLength(0)
    // Học viên chuyển sang Auto: một tín hiệu, nhãn cảnh báo tắt.
    await bar.unmount()
    const bar2 = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'SessionMode', props: { modes: ['Auto'] } } as never)
    await io.clock.advance(3 * SEC)
    expect(cues(io, 'Chế độ quyền · Auto')).toBe(1)
    expect(await ui.find({ text: /⚠/ })).toBeUndefined()
    await io.clock.advance(10 * SEC)
    expect(cues(io, 'Chế độ quyền · Auto')).toBe(1)
    // Không còn nhãn nào (chế độ thường): báo "mặc định".
    await bar2.unmount()
    const bar3 = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'SessionMode', props: { modes: [] } } as never)
    await io.clock.advance(3 * SEC)
    expect(cues(io, 'Chế độ quyền · mặc định')).toBe(1)
    await bar3.unmount()
    await ui.unmount()
  })

  test(`${surface}: bục yên tĩnh mặc định — không có hàng thông tin sống (kể cả khi giáo viên ghi show); chỉ thẻ bước, thanh bước, Giơ tay · Xin phép · ⋯`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({ next_action: 'Mở thư mục lớp' }) }
    const io = classroom(on, files)
    mockClaude(on)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    await io.clock.settle()
    const bar = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'SessionMode', props: { modes: ['Auto'] } } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(await ui.find({ text: /Lượt của bạn · Mở thư mục lớp/ })).toBeDefined()
    expect(await ui.find({ text: /Model|Effort|Context|5 giờ|Chế độ|Opus/ })).toBeUndefined()
    expect(await ui.find({ text: /▼|▲/ })).toBeUndefined()
    expect(await ui.findAll({ type: 'Svg' })).toHaveLength(surface === 'desktop' ? 2 : 0) // hình thầy + thanh bước
    // Xong · Chưa được · Gợi ý + Giơ tay · Xin phép + ⋯
    expect((await ui.findAll({ type: 'Button' })).map(b => b.key)).toEqual(['xong', 'chua-duoc', 'goi-y-buoc', 'gio-tay', 'xin-phep', 'more'])
    files['.lop-hoc/state.json'] = v8({ podium: { show: ['model', 'usage5', 'mode', 'nonsense'] } })
    await io.clock.advance(2 * SEC)
    // v0.13: hàng nhãn sống đã bỏ — chế độ quyền, model, hạn mức xem ở ⋯ → Claude của tôi.
    expect(await ui.find({ text: 'Model Opus 5.5' })).toBeUndefined()
    expect(await ui.find({ text: 'Chế độ Auto' })).toBeUndefined()
    await ui.press({ key: 'more' })
    await ui.press({ key: 'claude-cua-toi' })
    expect(await ui.find({ text: /claude-opus-5-5 · context 34% · 5 giờ 41%/ })).toBeDefined()
    await ui.press({ key: 'claude-cua-toi' })
    expect(await ui.find({ text: /claude-opus-5-5 · context 34%/ })).toBeUndefined()
    await bar.unmount()
    await ui.unmount()
  })

  test(`${surface}: podium.point vẽ thanh dưới ô nhập với vùng được chỉ, kèm dòng "ở thanh dưới ô nhập" (nhãn vàng đã bỏ)`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({ podium: { point: 'model' } }) }
    const io = classroom(on, files)
    mockClaude(on)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    await io.clock.settle()
    const bar = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'SessionMode', props: { modes: ['Auto'] } } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(await ui.find({ type: 'Text', text: /^▼ Model Opus 5.5$/ })).toBeUndefined()
    expect(await ui.find({ text: /ở thanh dưới ô nhập/ })).toBeDefined()
    if (surface === 'desktop') {
      const mock = await svgByAlt(ui, /^Thanh dưới ô nhập, chỗ cần nhìn: Model Opus 5.5$/)
      expect(mock).toBeDefined()
      const src = String(mock?.props.source)
      expect(src).toContain('#FFEA00')
      expect(src).toContain('Auto')
      expect(src).toContain('Opus 5.5')
      expect(src).toContain('<path d="M') // mũi tên
      expect(/This computer|thư mục/i.test(src)).toBe(false)
      expect(await ui.findAll({ type: 'Svg' })).toHaveLength(3) // thầy + thanh dưới ô nhập + thanh bước
    } else {
      expect(await ui.findAll({ type: 'Svg' })).toHaveLength(0)
      expect(await ui.find({ text: '▼ Opus 5.5' })).toBeDefined()
    }
    // Chỉ vào effort chưa biết; chỉ vào hạn mức.
    files['.lop-hoc/state.json'] = v8({ podium: { point: 'effort' } })
    await io.clock.advance(2 * SEC)
    if (surface === 'desktop') expect(await svgByAlt(ui, /^Thanh dưới ô nhập, chỗ cần nhìn: Effort$/)).toBeDefined()
    else expect(await ui.find({ text: '▼ —' })).toBeDefined()
    files['.lop-hoc/state.json'] = v8({ podium: { point: 'usage5' } })
    await io.clock.advance(2 * SEC)
    if (surface === 'desktop') expect(await svgByAlt(ui, /^Thanh dưới ô nhập, chỗ cần nhìn: 5 giờ 41%$/)).toBeDefined()
    else expect(await ui.find({ text: '▼ ◔ 41%' })).toBeDefined()
    // point: null xoá hết.
    files['.lop-hoc/state.json'] = v8({ podium: { point: null } })
    await io.clock.advance(2 * SEC)
    expect(await ui.find({ text: /▼|ở thanh dưới ô nhập/ })).toBeUndefined()
    expect(await ui.findAll({ type: 'Svg' })).toHaveLength(surface === 'desktop' ? 2 : 0)
    await bar.unmount()
    await ui.unmount()
  })

  test(`${surface}: cỡ bục mini · normal · wide; nút do giáo viên chọn đi cùng Giơ tay · Xin phép; còn lại nằm sau "⋯"`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({ destination: 'Bảng tổng hợp', podium: { size: 'mini', buttons: ['slower', 'raise-hand', 'slower', 'bogus'] } }) }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(await ui.find({ text: /Đích:/ })).toBeUndefined()
    if (surface === 'desktop') expect((await svgByAlt(ui, /trên bục giảng/))?.props.width).toBe(56)
    // Chọn 'slower' và 'raise-hand' (trùng và lạ bị bỏ); Giơ tay · Xin phép luôn có; Xin nghỉ · Nhanh hơn nằm sau "⋯".
    expect(await ui.find({ key: 'cham' })).toBeDefined()
    expect(await ui.find({ key: 'gio-tay' })).toBeDefined()
    expect(await ui.find({ key: 'xin-phep' })).toBeDefined()
    expect(await ui.find({ key: 'nhanh' })).toBeUndefined()
    expect(await ui.find({ key: 'xin-nghi' })).toBeUndefined()
    await ui.press({ key: 'more' })
    expect(await ui.find({ key: 'nhanh' })).toBeDefined()
    expect(await ui.find({ key: 'xin-nghi' })).toBeDefined()
    expect(await ui.find({ key: 'cham' })).toBeDefined() // không có hai nút cùng khoá
    expect(await ui.findAll({ key: 'cham' })).toHaveLength(1)
    await ui.press({ key: 'more' })
    expect(await ui.find({ key: 'xin-nghi' })).toBeUndefined()
    files['.lop-hoc/state.json'] = v8({ destination: 'Bảng tổng hợp', podium: { size: 'wide', buttons: ALL_BUTTONS } })
    await io.clock.advance(2 * SEC)
    expect(await ui.find({ text: /Đích:/ })).toBeUndefined()
    for (const key of ['gio-tay', 'xin-phep', 'xin-nghi', 'cham', 'nhanh', 'goi-y', 'phieu', 'b-form']) expect(await ui.find({ key })).toBeDefined()
    expect(await ui.find({ key: 'more' })).toBeDefined() // ⋯ luôn có (Thiết lập · Claude của tôi · Tiến độ)
    if (surface === 'desktop') expect((await svgByAlt(ui, /trên bục giảng/))?.props.width).toBe(140)
    files['.lop-hoc/state.json'] = v8({ destination: 'Bảng tổng hợp' })
    await io.clock.advance(2 * SEC)
    if (surface === 'desktop') expect((await svgByAlt(ui, /trên bục giảng/))?.props.width).toBe(96)
    await ui.unmount()
  })
}

for (const surface of ['terminal', 'desktop'] as const) {
  test(`${surface}: choices — nút lớn không chặn; bấm gửi "[Lớp học] Chọn · id · nhãn" một lần rồi ẩn đến khi state được ghi lại; option.send thay chữ`, LONG, async ($, on) => {
    const choices = { id: 'viec-dau', prompt: 'Chọn việc đầu tiên', options: [{ label: 'Tổng hợp doanh số' }, { label: 'Soạn thư ngắn', send: 'Soạn giúp tôi một thư ngắn' }, { label: 'Để sau' }], default: 0 }
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({ choices }) }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(await ui.find({ text: 'Chọn việc đầu tiên' })).toBeDefined()
    expect((await ui.find({ key: 'choice-0' }))?.props.label).toBe('Tổng hợp doanh số')
    expect(await ui.find({ key: 'choice-2' })).toBeDefined()
    await noForbiddenWords(ui as never)
    await ui.press({ key: 'choice-0' })
    expect(io.sent).toContain('[Lớp học] Chọn · viec-dau · Tổng hợp doanh số')
    expect(await ui.find({ key: 'choice-0' })).toBeUndefined()
    // Giáo viên chưa ghi lại: vẫn ẩn. Ghi lại state (chữ đổi) thì hiện lại.
    await io.clock.advance(10 * SEC)
    expect(await ui.find({ key: 'choice-1' })).toBeUndefined()
    files['.lop-hoc/state.json'] = v8({ choices, next_action: 'Chọn tiếp' })
    await io.clock.advance(2 * SEC)
    await ui.press({ key: 'choice-1' })
    expect(io.sent).toContain('Soạn giúp tôi một thư ngắn')
    expect(io.sent.filter(x => x.startsWith('[Lớp học] Chọn'))).toHaveLength(1)
    // Không có hạn: không bao giờ gửi "Hết hạn chọn".
    files['.lop-hoc/state.json'] = v8({ choices, next_action: 'Lần nữa' })
    await io.clock.advance(5 * MIN)
    expect(io.sent.filter(x => x.includes('Hết hạn chọn'))).toHaveLength(0)
    await ui.unmount()
  })

  test(`${surface}: choices quá hạn → "[Giáo án] Hết hạn chọn · id" một lần và tô lựa chọn mặc định, mod không bấm thay`, LONG, async ($, on) => {
    const choices = { id: 'tiep', prompt: 'Đi tiếp thế nào?', options: [{ label: 'Làm mẫu' }, { label: 'Tự làm' }], default: 1, timeout_s: 20 }
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({ choices }) }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    await io.clock.advance(12 * SEC)
    expect(cues(io, 'Hết hạn chọn · tiep')).toBe(0)
    expect((await ui.find({ key: 'choice-1' }))?.props.label).toBe('Tự làm')
    await io.clock.advance(12 * SEC)
    expect(cues(io, 'Hết hạn chọn · tiep')).toBe(1)
    expect((await ui.find({ key: 'choice-1' }))?.props.label).toBe('★ Tự làm')
    expect((await ui.find({ key: 'choice-0' }))?.props.label).toBe('Làm mẫu')
    expect(await ui.find({ text: /Hết giờ rồi — cô gợi ý ô nổi bật/ })).toBeDefined()
    expect(io.sent.filter(x => x.startsWith('[Lớp học] Chọn'))).toHaveLength(0)
    await io.clock.advance(3 * MIN)
    expect(cues(io, 'Hết hạn chọn · tiep')).toBe(1)
    await ui.unmount()
  })

  test(`${surface}: choices — làm việc thật thì không hạn; câu đố/trò chơi mặc định 60 giây; học viên gõ trả lời thì không hết hạn`, LONG, async ($, on) => {
    const choices = { id: 'doan', prompt: 'Đoán đi', options: [{ label: 'A' }, { label: 'B' }], default: 0 }
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({ choices, activity: { kind: 'hands-on', started_at: iso(T0) } }) }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    await io.clock.advance(5 * MIN)
    expect(io.sent.filter(x => x.includes('Hết hạn chọn'))).toHaveLength(0)
    // Câu đố: 60 giây.
    files['.lop-hoc/state.json'] = v8({ choices, activity: { kind: 'quiz', started_at: iso(T0) } })
    await io.clock.advance(2 * SEC)
    await io.clock.advance(50 * SEC)
    expect(cues(io, 'Hết hạn chọn · doan')).toBe(0)
    await io.clock.advance(15 * SEC)
    expect(cues(io, 'Hết hạn chọn · doan')).toBe(1)
    // Học viên gõ câu trả lời trong ô nhập thay vì bấm: nhóm mới không hết hạn.
    files['.lop-hoc/state.json'] = v8({ choices: { ...choices, id: 'doan2' }, activity: { kind: 'quiz', started_at: iso(T0) } })
    await io.clock.advance(2 * SEC)
    await ($ as unknown as { prompt: { submit: (e: object) => Promise<unknown> } }).prompt.submit({ text: 'em nghĩ là B' })
    await io.clock.advance(3 * MIN)
    expect(cues(io, 'Hết hạn chọn · doan2')).toBe(0)
    await ui.unmount()
  })

  test(`${surface}: board — tiêu đề, ≤ 5 dòng; SVG đã lọc script, foreignObject, on…, href ngoài; quá 16 KB hoặc không phải SVG thì bỏ hình (giữ chữ)`, LONG, async ($, on) => {
    const lines = ['Mức nghĩ kỹ', 'Cao = chậm hơn', 'Thấp = nhanh hơn', 'Tốn usage hơn', 'Bốn chữ', 'Dòng thứ sáu bị cắt']
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({ board: { title: 'Effort là gì', lines, svg: SVG_DIRTY } }) }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(await ui.find({ text: 'Effort là gì' })).toBeDefined()
    expect(await ui.find({ text: 'Mức nghĩ kỹ' })).toBeDefined()
    expect(await ui.find({ text: 'Bốn chữ' })).toBeDefined()
    expect(await ui.find({ text: /thứ sáu/ })).toBeUndefined()
    if (surface === 'desktop') {
      const pic = await svgByAlt(ui, /^Bảng của lớp: Effort là gì$/)
      const src = String(pic?.props.source)
      expect(src).toContain('<circle')
      expect(src).toContain('<rect')
      expect(/script|foreignobject|onload|onclick|evil\.example|href/i.test(src)).toBe(false)
      expect(await ui.findAll({ type: 'Svg' })).toHaveLength(3) // thầy + hình bảng + thanh bước
    } else expect(await ui.findAll({ type: 'Svg' })).toHaveLength(0)
    // SVG quá 16 KB: bỏ hình, chữ vẫn còn.
    const big = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">${'<rect width="1" height="1"/>'.repeat(700)}</svg>`
    expect(big.length).toBeGreaterThan(16 * 1024)
    files['.lop-hoc/state.json'] = v8({ board: { title: 'Bảng to', lines: ['một'], svg: big } })
    await io.clock.advance(2 * SEC)
    expect(await ui.find({ text: 'Bảng to' })).toBeDefined()
    expect(await ui.findAll({ type: 'Svg' })).toHaveLength(surface === 'desktop' ? 2 : 0)
    files['.lop-hoc/state.json'] = v8({ board: { title: 'Không phải hình', lines: ['hai'], svg: '<div>x</div>' } })
    await io.clock.advance(2 * SEC)
    expect(await ui.find({ text: 'Không phải hình' })).toBeDefined()
    expect(await ui.findAll({ type: 'Svg' })).toHaveLength(surface === 'desktop' ? 2 : 0)
    // Bỏ board: bảng biến mất.
    files['.lop-hoc/state.json'] = v8({})
    await io.clock.advance(2 * SEC)
    expect(await ui.find({ text: 'Không phải hình' })).toBeUndefined()
    await ui.unmount()
  })

  test(`${surface}: board.shot — ảnh chụp có đánh dấu thắng svg; tiêu đề và dòng vẫn hiện; terminal chỉ có dòng chữ; đổi tệp hoặc state thì đọc lại, không đổi thì không đọc`, LONG, async ($, on) => {
    const PATH = '.lop-hoc/chi-tay.jpg'
    const board = { title: 'Chỗ cần bấm', lines: ['Bấm ô vàng', 'Ở góc phải'], svg: SVG_DIRTY, shot: PATH }
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({ board }) }
    const blobs: Record<string, { b64: string; mtime: number }> = { [PATH]: { b64: toB64(jpegBytes(960, 540, { total: 20_000 })), mtime: 1000 } }
    const io = classroom(on, files, {}, blobs)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(await ui.find({ text: 'Chỗ cần bấm' })).toBeDefined()
    expect(await ui.find({ text: 'Bấm ô vàng' })).toBeDefined()
    expect(await ui.find({ text: 'Ở góc phải' })).toBeDefined()
    if (surface === 'terminal') {
      expect(await ui.find({ text: 'Cô đã đánh dấu trên ảnh màn hình — xem trong Claude Desktop' })).toBeDefined()
      expect(await ui.findAll({ type: 'Svg' })).toHaveLength(0)
      expect(io.blobReads).toBe(0)
    } else {
      expect(await ui.find({ text: /đánh dấu trên ảnh màn hình/ })).toBeUndefined()
      const pic = await svgByAlt(ui, /^Ảnh màn hình có đánh dấu: Chỗ cần bấm$/)
      const src = String(pic?.props.source)
      expect(src).toContain('viewBox="0 0 960 540"')
      expect(src).toContain('href="data:image/jpeg;base64,')
      // Một Svg của giáo viên (bục) + một Svg ảnh + thanh bước; svg của giáo viên (đã lọc) không vẽ khi có ảnh.
      expect(await ui.findAll({ type: 'Svg' })).toHaveLength(3)
      expect(await svgByAlt(ui, /^Bảng của lớp/)).toBeUndefined()
      expect(src).not.toContain('<circle')
      // Ảnh co theo hộp bảng (không to quá cỡ rộng 560 × 260).
      expect(Number(pic?.props.width)).toBeLessThanOrEqual(560)
      expect(Number(pic?.props.height)).toBeLessThanOrEqual(260)
      const reads = io.blobReads
      expect(reads).toBeGreaterThan(0)
      // Không đổi gì: các nhịp sau không đọc lại byte.
      await io.clock.advance(10 * SEC)
      expect(io.blobReads).toBe(reads)
      // Giáo viên ghi đè ảnh (cùng đường dẫn, state.json không đổi): vẽ lại bằng ảnh mới.
      blobs[PATH] = { b64: toB64(pngBytes(800, 450, 5000)), mtime: 2000 }
      await io.clock.advance(3 * SEC)
      const pic2 = await svgByAlt(ui, /^Ảnh màn hình có đánh dấu/)
      expect(String(pic2?.props.source)).toContain('viewBox="0 0 800 450"')
      expect(String(pic2?.props.source)).toContain('href="data:image/png;base64,')
      expect(io.blobReads).toBeGreaterThan(reads)
      // state.json được ghi lại (tệp ảnh y nguyên): đọc lại theo hợp đồng.
      const before = io.blobReads
      files['.lop-hoc/state.json'] = v8({ board: { ...board, lines: ['Bấm ô vàng', 'Ở góc phải', 'Rồi báo thầy'] } })
      await io.clock.advance(3 * SEC)
      expect(await ui.find({ text: 'Rồi báo thầy' })).toBeDefined()
      expect(io.blobReads).toBeGreaterThan(before)
      expect(String((await svgByAlt(ui, /^Ảnh màn hình có đánh dấu/))?.props.source)).toContain('viewBox="0 0 800 450"')
      // Xoá tệp (dọn sau khi học viên bấm xong): quay về svg của giáo viên.
      delete blobs[PATH]
      await io.clock.advance(3 * SEC)
      expect(await svgByAlt(ui, /^Ảnh màn hình có đánh dấu/)).toBeUndefined()
      expect(String((await svgByAlt(ui, /^Bảng của lớp/))?.props.source)).toContain('<circle')
    }
    // Xoá board.shot khỏi state: không còn ảnh, không còn dòng chữ.
    files['.lop-hoc/state.json'] = v8({ board: { title: 'Chỗ cần bấm', lines: ['Bấm ô vàng'] } })
    await io.clock.advance(3 * SEC)
    expect(await ui.find({ text: /đánh dấu trên ảnh màn hình/ })).toBeUndefined()
    expect(await svgByAlt(ui, /^Ảnh màn hình có đánh dấu/)).toBeUndefined()
    await ui.unmount()
  })

  test(`${surface}: board.shot — đường dẫn ngoài .lop-hoc/, có .., sai đuôi, ảnh quá 96 KB, rác, thiếu tệp: bỏ qua ảnh (không đọc byte khi đã biết quá lớn); svg giáo viên vẫn lọc href data:`, LONG, async ($, on) => {
    const small = toB64(jpegBytes(960, 540, { total: 10_000 }))
    const blobs: Record<string, { b64: string; mtime: number }> = {
      '.lop-hoc/ok.jpg': { b64: small, mtime: 1 },
      '.lop-hoc/lon.jpg': { b64: toB64(jpegBytes(960, 540, { total: 96 * 1024 + 1 })), mtime: 1 },
      '.lop-hoc/rac.png': { b64: toB64(new TextEncoder().encode('day khong phai anh')), mtime: 1 },
      'ngoai/ok.jpg': { b64: small, mtime: 1 },
      'x.jpg': { b64: small, mtime: 1 },
      '.lop-hoc/ok.gif': { b64: small, mtime: 1 },
    }
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({}) }
    const io = classroom(on, files, {}, blobs)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    const pics = async () => (surface === 'desktop' ? (await ui.findAll({ type: 'Svg' })).filter(x => /^Ảnh màn hình/.test(String(x.props.alt))) : [])
    for (const shot of ['ngoai/ok.jpg', 'x.jpg', '../.lop-hoc/ok.jpg', '.lop-hoc/../x.jpg', '.lop-hoc/ok.gif', 'D:/sandbox/.lop-hoc/ok.jpg', 7, '']) {
      files['.lop-hoc/state.json'] = v8({ board: { title: `Ảnh bị bỏ ${String(shot)}`, lines: ['chữ vẫn hiện'], svg: SVG_DIRTY, shot } })
      await io.clock.advance(2 * SEC)
      expect(await ui.find({ text: 'chữ vẫn hiện' })).toBeDefined()
      expect(await pics()).toHaveLength(0)
      expect(await ui.find({ text: /đánh dấu trên ảnh màn hình/ })).toBeUndefined()
      // Đường dẫn bị bỏ qua thì svg của giáo viên (đã lọc) vẫn vẽ như v0.8.
      if (surface === 'desktop') expect(String((await svgByAlt(ui, /^Bảng của lớp/))?.props.source)).toContain('<circle')
    }
    expect(io.blobReads).toBe(0)
    // Hợp lệ nhưng tệp quá 96 KB: không đọc byte, không vẽ ảnh, không có dòng chữ "đã đánh dấu".
    files['.lop-hoc/state.json'] = v8({ board: { title: 'Quá lớn', lines: ['chữ vẫn hiện'], shot: '.lop-hoc/lon.jpg' } })
    await io.clock.advance(2 * SEC)
    expect(await ui.find({ text: 'Quá lớn' })).toBeDefined()
    expect(await pics()).toHaveLength(0)
    expect(await ui.find({ text: /đánh dấu trên ảnh màn hình/ })).toBeUndefined()
    expect(io.blobReads).toBe(0)
    // Không phải JPEG/PNG dù đuôi .png: không vẽ.
    files['.lop-hoc/state.json'] = v8({ board: { title: 'Rác', lines: ['chữ vẫn hiện'], shot: '.lop-hoc/rac.png' } })
    await io.clock.advance(2 * SEC)
    expect(await pics()).toHaveLength(0)
    // Thiếu tệp: không vẽ, không có dòng chữ.
    files['.lop-hoc/state.json'] = v8({ board: { title: 'Thiếu', lines: ['chữ vẫn hiện'], shot: '.lop-hoc/khong-co.jpg' } })
    await io.clock.advance(2 * SEC)
    expect(await pics()).toHaveLength(0)
    expect(await ui.find({ text: /đánh dấu trên ảnh màn hình/ })).toBeUndefined()
    // Ảnh nhỏ hợp lệ: vẽ (desktop) hoặc có dòng chữ (terminal).
    files['.lop-hoc/state.json'] = v8({ board: { title: 'Sau', lines: ['chữ vẫn hiện'], shot: '.lop-hoc/ok.jpg' } })
    await io.clock.advance(2 * SEC)
    expect(await pics()).toHaveLength(surface === 'desktop' ? 1 : 0)
    if (surface === 'terminal') expect(await ui.find({ text: 'Cô đã đánh dấu trên ảnh màn hình — xem trong Claude Desktop' })).toBeDefined()
    // svg của giáo viên không bao giờ mang được ảnh data: vào (chỉ mod dựng Svg ảnh).
    const sneaky = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 10 10"><image href="data:image/png;base64,AAAA" xlink:href="data:image/png;base64,AAAA" width="10" height="10"/><rect width="5" height="5"/></svg>'
    files['.lop-hoc/state.json'] = v8({ board: { title: 'Lén', lines: ['chữ vẫn hiện'], svg: sneaky } })
    await io.clock.advance(2 * SEC)
    if (surface === 'desktop') {
      const src = String((await svgByAlt(ui, /^Bảng của lớp: Lén$/))?.props.source)
      expect(src).toContain('<rect')
      expect(src).not.toContain('data:')
    }
    await ui.unmount()
  })

  test(`${surface}: board.shot — lớp tiếng Lào: dòng chữ và lời mô tả ảnh bằng tiếng Lào`, LONG, async ($, on) => {
    const PATH = '.lop-hoc/chi-tay.png'
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({ language: 'lo', board: { title: 'ກົດບ່ອນນີ້', lines: [], shot: PATH } }) }
    const blobs = { [PATH]: { b64: toB64(pngBytes(640, 360, 3000)), mtime: 5 } }
    const io = classroom(on, files, {}, blobs)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    await io.clock.advance(3 * SEC)
    if (surface === 'terminal') expect(await ui.find({ text: STR.lo.shotNote('ຄູ') })).toBeDefined()
    else expect(await svgByAlt(ui, /^ຮູບໜ້າຈໍທີ່ມີການໝາຍ: ກົດບ່ອນນີ້$/)).toBeDefined()
    await ui.unmount()
  })

  test(`${surface}: dòng công cụ ghi vào .lop-hoc/ chỉ còn một dòng mờ "ghi sổ lớp"; công cụ khác giữ nguyên`, LONG, async ($, on) => {
    classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const tool = (name: string, input: object) => $.ui.mount({ plugin: 'lop-hoc', surface, component: 'ToolUse', props: { tool_use_id: 't1', tool: name, input, isRunning: false, isErrored: false, isInterrupted: false } } as never)
    const ledger = await tool('Write', { file_path: 'D:/sandbox/.lop-hoc/state.json', content: '{}' })
    expect(await ledger.find({ text: 'Cô ghi sổ lớp' })).toBeDefined()
    expect(await ledger.find({ key: 'engine' })).toBeUndefined()
    await ledger.unmount()
    const bash = await tool('Bash', { command: 'cat .lop-hoc/state.json' })
    expect(await bash.find({ text: 'Cô ghi sổ lớp' })).toBeDefined()
    expect(await bash.find({ key: 'engine' })).toBeUndefined()
    await bash.unmount()
    const win = await tool('Write', { file_path: 'D:\\sandbox\\.lop-hoc\\huy-hieu.json', content: '{}' })
    expect(await win.find({ text: 'Cô ghi sổ lớp' })).toBeDefined()
    await win.unmount()
    const other = await tool('Write', { file_path: 'D:/sandbox/bao-cao.docx', content: 'x' })
    expect(await other.find({ text: /Cô vừa ghi bao-cao.docx/ })).toBeDefined()
    expect(await other.find({ text: 'Cô ghi sổ lớp' })).toBeUndefined()
    // v0.12: dòng gốc nằm sau nút "Xem chi tiết".
    expect(await other.find({ key: 'engine' })).toBeUndefined()
    await other.press({ key: 'detail' })
    expect(await other.find({ key: 'engine' })).toBeDefined()
    await other.unmount()
  })

  test(`${surface}: nhóm dòng công cụ — toàn ghi sổ lớp thì một dòng mờ; lẫn việc khác thì một dòng thầy đếm việc (không tính ghi sổ), nút mở nhóm; onScreen không đổi`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const call = (tool: string, input: object) => ({ tool, input, isRunning: false, isErrored: false, isInterrupted: false })
    const group = (calls: object[]) => $.ui.mount({ plugin: 'lop-hoc', surface, component: 'ToolGroup', props: { calls, isActive: false, isExpanded: false, onScreen: null } } as never)
    const only = await group([call('Read', { file_path: '.lop-hoc/state.json' }), call('Edit', { file_path: '.lop-hoc/huy-hieu.json' })])
    expect(await only.find({ text: 'Cô ghi sổ lớp' })).toBeDefined()
    expect(await only.find({ key: 'engine' })).toBeUndefined()
    expect(await only.find({ key: 'detail' })).toBeUndefined()
    await only.unmount()
    const mixed = await group([call('Read', { file_path: 'a.xlsx' }), call('Write', { file_path: '.lop-hoc/state.json' })])
    expect(await mixed.find({ text: 'Cô vừa: đọc 1 file' })).toBeDefined()
    expect(await mixed.find({ key: 'engine' })).toBeUndefined()
    await mixed.press({ key: 'detail' })
    expect(await mixed.find({ key: 'engine' })).toBeDefined()
    expect(io.renders.ToolGroup?.isExpanded).toBe(true)
    expect(io.renders.ToolGroup?.onScreen).toBeNull()
    await mixed.unmount()
    const plain = await group([call('Read', { file_path: 'a.xlsx' })])
    expect(await plain.find({ text: 'Cô vừa: đọc 1 file' })).toBeDefined()
    expect(await plain.find({ key: 'engine' })).toBeUndefined()
    await plain.unmount()
  })

  test(`${surface}: hộp câu hỏi gốc mở quá 90 giây (không phải câu đố/trò chơi) → "[Giáo án] Hộp chờ lâu · nhãn mặc định" một lần; không đóng hộp`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({ activity: { kind: 'hands-on', started_at: iso(T0) } }) }
    const io = classroom(on, files)
    let release: () => void = () => {}
    let gate = new Promise<void>(r => { release = r })
    on('tool.call', async () => {
      await gate
      return { deny: 'Người dùng đã đóng hộp câu hỏi' }
    })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    const d = $ as unknown as { turn: { start: (e: object) => Promise<unknown> }; tool: { call: (e: object) => Promise<unknown> } }
    const questions = [{ question: 'Chọn chế độ?', header: 'Chế độ', multiSelect: false, options: [{ label: 'Hỏi từng bước', description: '' }, { label: 'Tự động (đề xuất)', description: '' }] }]
    await d.turn.start({ text: '', turnId: 'hop' })
    const box = d.tool.call({ tool: 'AskUserQuestion', questions })
    await io.clock.advance(80 * SEC)
    expect(io.sent.filter(x => x.includes('Hộp chờ lâu'))).toHaveLength(0)
    await io.clock.advance(15 * SEC)
    expect(io.sent.filter(x => x.includes('Hộp chờ lâu'))).toEqual(['[Giáo án] Hộp chờ lâu · Tự động (đề xuất)'])
    expect(io.aborted).toHaveLength(0)
    await io.clock.advance(4 * MIN)
    expect(io.sent.filter(x => x.includes('Hộp chờ lâu'))).toHaveLength(1)
    release()
    await box.catch(() => undefined)
    // Câu đố: hộp có hạn 60 giây riêng, không có tín hiệu "chờ lâu".
    gate = new Promise<void>(r => { release = r })
    io.onAbort = () => release()
    files['.lop-hoc/state.json'] = v8({ activity: { kind: 'quiz', started_at: iso(T0) } })
    await io.clock.advance(2 * SEC)
    await d.turn.start({ text: '', turnId: 'do' })
    const quiz = d.tool.call({ tool: 'AskUserQuestion', questions })
    await io.clock.advance(3 * MIN)
    expect(io.sent.filter(x => x.includes('Hộp chờ lâu'))).toHaveLength(1)
    await quiz.catch(() => undefined)
    await ui.unmount()
  })

  test(`${surface}: lớp tiếng Lào — nhãn mới (⋯, ghi sổ lớp, thanh dưới ô nhập, lựa chọn) bằng tiếng Lào`, LONG, async ($, on) => {
    const choices = { id: 'lua', prompt: 'ເລືອກ', options: [{ label: 'ກ' }, { label: 'ຂ' }], default: 0, timeout_s: 10 }
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({ language: 'lo', podium: { point: 'effort' }, choices }) }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    // Có lựa chọn ở tầng 1 nên hình thu thành nút; bấm "ເບິ່ງຮູບ" thì thấy chỗ chỉ.
    expect((await ui.find({ key: 'xem-hinh' }))?.props.label).toBe(STR.lo.showPic)
    await ui.press({ key: 'xem-hinh' })
    expect((await ui.find({ key: 'xem-hinh' }))?.props.label).toBe(STR.lo.hidePic)
    expect(await ui.find({ text: /ຢູ່ແຖບລຸ່ມຊ່ອງພິມ/ })).toBeDefined()
    expect((await ui.find({ key: 'more' }))?.props.label).toBe('⋯ ເພີ່ມ')
    await io.clock.advance(20 * SEC)
    expect(await ui.find({ text: /ໝົດເວລາແລ້ວ/ })).toBeDefined()
    const tool = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'ToolUse', props: { tool_use_id: 't1', tool: 'Write', input: { file_path: '.lop-hoc/state.json' }, isRunning: false, isErrored: false, isInterrupted: false } } as never)
    expect(await tool.find({ text: 'ຄູຈົດບັນທຶກຫ້ອງຮຽນ' })).toBeDefined()
    await tool.unmount()
    await ui.unmount()
  })
}

test('bộ đọc podium · board · choices: bỏ trường sai, giữ giới hạn trong thiết kế', async () => {
  expect(podiumOf(null)).toBeNull()
  expect(podiumOf({ size: 'huge', show: ['mode', 'mode', 'x', 7, 'usageWeek'], point: 'effort', buttons: ['hint', 'nope', 'hint', 'delegate'] })).toEqual({ size: 'normal', show: ['mode', 'usageWeek'], point: 'effort', buttons: ['hint', 'delegate'] })
  expect(podiumOf({ size: 'mini', point: 'xyz' })).toEqual({ size: 'mini', show: [], point: null, buttons: [] })
  expect(boardOf({})).toBeNull()
  const b = boardOf({ title: 'T'.repeat(80), lines: ['a', 7, '', 'b'.repeat(120), 'c', 'd', 'e', 'f'] })
  expect(b?.title.length).toBe(60)
  expect(b?.lines).toHaveLength(5)
  expect(b?.lines.every(l => l.length <= 90)).toBe(true)
  expect(b?.svg).toBeNull()
  expect(choicesOf({ id: 'a', options: [{ label: 'chỉ một' }] })).toBeNull()
  expect(choicesOf({ id: 'a', options: 'x' })).toBeNull()
  const c = choicesOf({ id: 'chon so', prompt: 'P', options: Array.from({ length: 8 }, (_, i) => ({ label: `${'L'.repeat(60)}${i}`, send: i === 0 ? 'gửi' : undefined })), default: 99, timeout_s: 1 })
  expect(c?.options).toHaveLength(5)
  expect(c?.options[0]?.label.length).toBe(40)
  expect(c?.options[0]?.send).toBe('gửi')
  expect(c?.options[1]).not.toHaveProperty('send')
  expect(c?.default).toBe(0)
  expect(c?.timeout_s).toBe(5)
  expect(c?.id).toBe('chon-so')
  expect(choicesOf({ options: [{ label: 'a' }, { label: 'b' }], default: 1, timeout_s: 45 })).toMatchObject({ id: 'chon', default: 1, timeout_s: 45 })
})

test('nhãn chế độ quyền, tên model, dòng ghi sổ lớp', async () => {
  expect(permissionLabel([])).toBe('')
  expect(permissionLabel(['focus'])).toBe('')
  expect(permissionLabel(['memory paused', 'Bypass permissions'])).toBe('Bypass permissions')
  expect(permissionLabel(['focus', 'Auto'])).toBe('Auto')
  expect(modelLabel('claude-opus-5-5')).toBe('Opus 5.5')
  expect(modelLabel('claude-sonnet-4-20250514')).toBe('Sonnet 4')
  expect(modelLabel('mô hình lạ')).toBe('mô hình lạ')
  expect(touchesLedger({ file_path: 'D:\\x\\.lop-hoc\\state.json' })).toBe(true)
  expect(touchesLedger({ command: 'ls' })).toBe(false)
  expect(touchesLedger(undefined)).toBe(false)
})

test('i18n: mọi chữ mới của v0.8 có đủ tiếng Việt và tiếng Lào', async () => {
  expect(Object.keys(STR.lo).sort()).toEqual(Object.keys(STR.vi).sort())
  const LAO = /[\u0E80-\u0EFF]/
  for (const [name, S] of Object.entries(STR)) {
    const strings = [S.more, S.moreClose, S.barNote, S.bypassChip('Bypass permissions'), S.barAlt('x'), S.boardAlt('x'), S.shotAlt('x'), S.shotNote('Cô'), S.choiceExpired('cô'), S.ledger('Cô'), ...Object.values(S.facts)]
    for (const t of strings) expect(typeof t === 'string' && t.length > 0).toBe(true)
    expect(S.bypassChip('Bypass permissions')).toContain('Bypass permissions')
    expect(Object.keys(S.facts).sort()).toEqual(['context', 'effort', 'mode', 'model', 'usage5', 'usageWeek'])
    if (name === 'lo') for (const t of [S.more, S.moreClose, S.barNote, S.bypassChip('x'), S.barAlt('x'), S.boardAlt('x'), S.shotAlt('x'), S.shotNote('ຄູ'), S.choiceExpired('ຄູ'), S.ledger('ຄູ'), S.facts.mode, S.facts.usage5, S.facts.usageWeek]) expect(LAO.test(t)).toBe(true)
  }
  expect(STR.vi.ledger('Thầy')).toBe('Thầy ghi sổ lớp')
  expect(STR.vi.barNote).toBe('ở thanh dưới ô nhập')
  expect(STR.vi.shotNote('Thầy')).toBe('Thầy đã đánh dấu trên ảnh màn hình — xem trong Claude Desktop')
})

for (const surface of ['terminal', 'desktop'] as const) {
  test(`${surface}: hộp câu hỏi gốc mở từ 90 giây — bục hiện dòng vàng "chọn dòng đầu tiên" đến khi hộp đóng; câu đố không có; tiếng Lào`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({ activity: { kind: 'hands-on', started_at: iso(T0) } }) }
    const io = classroom(on, files)
    let release: () => void = () => {}
    const gate = new Promise<void>(r => { release = r })
    on('tool.call', async () => {
      await gate
      return { deny: 'Người dùng đã đóng hộp câu hỏi' }
    })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    const d = $ as unknown as { turn: { start: (e: object) => Promise<unknown> }; tool: { call: (e: object) => Promise<unknown> } }
    const questions = [{ question: 'Chọn?', header: 'Hỏi', multiSelect: false, options: [{ label: 'A', description: '' }, { label: 'B', description: '' }] }]
    await d.turn.start({ text: '', turnId: 'hop' })
    const box = d.tool.call({ tool: 'AskUserQuestion', questions })
    await io.clock.advance(60 * SEC)
    expect(await ui.find({ text: /Chưa chắc thì chọn dòng đầu tiên/ })).toBeUndefined()
    await io.clock.advance(40 * SEC)
    const hint = await ui.find({ type: 'Text', text: /Chưa chắc thì chọn dòng đầu tiên — cô sẽ chỉ lại bằng hình\./ })
    expect(hint).toBeDefined()
    expect(hint?.props.backgroundColor).toBe('#FFEA00')
    release()
    await box.catch(() => undefined)
    await ($ as unknown as { turn: { complete: (e: object) => Promise<unknown> } }).turn.complete({ answer: '', durationMs: 0, isAborted: false, turnId: 'hop', reason: 'answer' })
    expect(await ui.find({ text: /Chưa chắc thì chọn dòng đầu tiên/ })).toBeUndefined()
    await ui.unmount()
  })

  test(`${surface}: chế độ quyền không rõ thì không có nhãn Bypass, không nhãn "Chế độ" hỏng`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({ podium: { show: ['mode'], point: 'mode' } }) }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    for (const modes of [[], ['focus'], ['memory paused'], ['   '], [null, 7]]) {
      const bar = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'SessionMode', props: { modes } } as never)
      await io.clock.advance(3 * SEC)
      expect(await ui.find({ text: /⚠|undefined|null|NaN|Chế độ/ })).toBeUndefined()
      await bar.unmount()
    }
    expect(io.sent.filter(x => x.includes('Chế độ quyền'))).toHaveLength(0)
    expect(permissionLabel([null, 7] as never)).toBe('')
    expect(permissionLabel(['a'.repeat(80)]).length).toBeLessThanOrEqual(40)
    await ui.unmount()
  })
}

// ── v0.11: thang im lặng ──────────────────────────────────────────────────────────
const RUNG = (n: number) => `Học viên im lặng · nấc ${n}`
const rungs = (io: Io) => io.sent.filter(t => t.startsWith('[Giáo án] Học viên im lặng')).map(t => t.slice(-1))

test('silenceDue: 2 phút · 3,5 phút · 5 phút (cộng dồn); làm việc thật / thử thách thì nấc 1 chờ 3 phút; sau nấc 3 không còn gì', async () => {
  const at = 1_000_000
  expect(silenceDue({ at, rung: 0 }, at + 119 * SEC, false)).toBeNull()
  expect(silenceDue({ at, rung: 0 }, at + 2 * MIN, false)).toBe(1)
  expect(silenceDue({ at, rung: 0 }, at + 179 * SEC, true)).toBeNull()
  expect(silenceDue({ at, rung: 0 }, at + 3 * MIN, true)).toBe(1)
  expect(silenceDue({ at, rung: 1 }, at + 3.5 * MIN - SEC, true)).toBeNull()
  expect(silenceDue({ at, rung: 1 }, at + 3.5 * MIN, false)).toBe(2)
  expect(silenceDue({ at, rung: 2 }, at + 5 * MIN - SEC, false)).toBeNull()
  expect(silenceDue({ at, rung: 2 }, at + 5 * MIN, false)).toBe(3)
  expect(silenceDue({ at, rung: 3 }, at + 999 * MIN, false)).toBeNull()
})

for (const surface of ['terminal', 'desktop'] as const) {
  const open = async ($: never, on: On, files: Record<string, string>) => {
    const io = classroom(on, files)
    await ($ as unknown as { session: { start: (e: object) => Promise<unknown> } }).session.start({ cwd: 'D:/sandbox', surface, isInteractive: true })
    const ui = await ($ as unknown as { ui: { mount: (e: object) => Promise<{ press: (q: object) => Promise<unknown>; unmount: () => Promise<void> }> } }).ui.mount({ plugin: 'lop-hoc', surface, ...BAND })
    await ui.press({ key: 'enter' })
    await teacherTalks($)
    return { io, ui }
  }

  test(`${surface}: thang im lặng — nhắc trên bục sau 45 giây (không gửi gì), nấc 1 sau 2 phút, nấc 2 sau 3,5 phút, nấc 3 sau 5 phút (cộng dồn từ lúc thầy nói xong), rồi dừng đến khi học viên tác động`, LONG, async ($, on) => {
    const { io, ui } = await open($ as never, on, { 'CLAUDE.md': '# Lớp học NNC' })
    const NUDGE = /Làm xong thì bấm Xong — chưa biết làm thì bấm Gợi ý/
    await io.clock.advance(40 * SEC)
    expect(await ui.find({ text: NUDGE })).toBeUndefined()
    await io.clock.advance(15 * SEC)
    expect(await ui.find({ text: NUDGE })).toBeDefined()
    expect(rungs(io)).toEqual([])
    expect(io.sent).toEqual([OPEN_BAN])
    await io.clock.advance(55 * SEC)
    expect(rungs(io)).toEqual([])
    await io.clock.advance(15 * SEC)
    expect(rungs(io)).toEqual(['1'])
    expect(io.sent).toContain(`[Giáo án] ${RUNG(1)}`)
    // Thầy đáp xong: mốc giữ nguyên (cộng dồn), nấc 2 ở 3,5 phút kể từ lúc thầy nói xong lần đầu.
    await teacherTalks($ as never)
    await io.clock.advance(80 * SEC)
    expect(rungs(io)).toEqual(['1'])
    await io.clock.advance(15 * SEC)
    expect(rungs(io)).toEqual(['1', '2'])
    await teacherTalks($ as never)
    await io.clock.advance(70 * SEC)
    expect(rungs(io)).toEqual(['1', '2'])
    await io.clock.advance(15 * SEC)
    expect(rungs(io)).toEqual(['1', '2', '3'])
    // Sau nấc 3: không gì nữa, dù giáo viên nói thêm.
    await teacherTalks($ as never)
    await io.clock.advance(60 * MIN)
    expect(rungs(io)).toEqual(['1', '2', '3'])
    await teacherTalks($ as never)
    await io.clock.advance(60 * MIN)
    expect(rungs(io)).toEqual(['1', '2', '3'])
    await ui.unmount()
  })

  test(`${surface}: thang im lặng — mọi tác động của học viên (gửi, chọn trên bục, gõ) xoá thang; giáo viên làm việc thì không đếm`, LONG, async ($, on) => {
    const choices = { id: 'buoc', prompt: 'Bạn đang ở bước nào?', options: [{ label: 'Bước 1' }, { label: 'Chưa rõ' }], default: 0 }
    const { io, ui } = await open($ as never, on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({ choices }) })
    const d = $ as unknown as { prompt: { submit: (e: object) => Promise<unknown> }; turn: { start: (e: object) => Promise<unknown>; complete: (e: object) => Promise<unknown> } }
    await io.clock.advance(130 * SEC)
    expect(rungs(io)).toEqual(['1'])
    // Bấm lựa chọn trên bục là tác động: thang về 0; nấc 1 mới chỉ đến sau 2 phút kể từ lúc giáo viên đáp xong.
    await ui.press({ key: 'choice-1' })
    await teacherTalks($ as never)
    await io.clock.advance(110 * SEC)
    expect(rungs(io)).toEqual(['1'])
    await io.clock.advance(15 * SEC)
    expect(rungs(io)).toEqual(['1', '1'])
    // Học viên gõ và gửi một câu cũng là tác động.
    await d.prompt.submit({ text: 'em chưa hiểu' })
    await teacherTalks($ as never)
    await io.clock.advance(110 * SEC)
    expect(rungs(io)).toEqual(['1', '1'])
    await io.clock.advance(15 * SEC)
    expect(rungs(io)).toEqual(['1', '1', '1'])
    // Đang gõ (ô nhập có chữ) là có mặt: không đếm, gõ xong mới tính lại từ đầu.
    io.box.text = 'em đang nghĩ'
    await io.clock.advance(10 * MIN)
    expect(rungs(io)).toEqual(['1', '1', '1'])
    io.box.text = ''
    await io.clock.advance(110 * SEC)
    expect(rungs(io)).toEqual(['1', '1', '1'])
    await io.clock.advance(20 * SEC)
    expect(rungs(io)).toEqual(['1', '1', '1', '1'])
    // Giáo viên đang làm việc: không đếm; xong rồi mới tính 90 giây.
    await d.prompt.submit({ text: 'tiếp đi' })
    await d.turn.start({ text: '', turnId: 'dai' })
    await io.clock.advance(10 * MIN)
    expect(rungs(io)).toHaveLength(4)
    await d.turn.complete({ answer: '', durationMs: 0, isAborted: false, turnId: 'dai', reason: 'answer' })
    await io.clock.advance(110 * SEC)
    expect(rungs(io)).toHaveLength(4)
    await io.clock.advance(20 * SEC)
    expect(rungs(io)).toHaveLength(5)
    await ui.unmount()
  })

  test(`${surface}: thang im lặng — Xin phép dừng thang, Quay lại tính lại từ đầu`, LONG, async ($, on) => {
    const { io, ui } = await open($ as never, on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7(WITH_ALL) })
    await io.clock.advance(60 * SEC)
    await ui.press({ key: 'xin-phep' })
    await ui.press({ key: 'ly-do-nuoc' })
    await io.clock.advance(20 * MIN)
    expect(rungs(io)).toEqual([])
    await ui.press({ key: 'quay-lai' })
    await teacherTalks($ as never)
    await io.clock.advance(110 * SEC)
    expect(rungs(io)).toEqual([])
    await io.clock.advance(15 * SEC)
    expect(rungs(io)).toEqual(['1'])
    await ui.unmount()
  })

  for (const [name, extra] of [
    ['làm việc thật (hands-on)', { activity: { kind: 'hands-on', started_at: iso(T0) } }],
    ['form', { activity: { kind: 'form', started_at: iso(T0) } }],
    ['thử thách đang chạy giờ', { challenge: { title: 'Tìm 3 dòng thiếu giá', seconds: 900, started_at: iso(T0) } }],
  ] as const) {
    test(`${surface}: thang im lặng — ${name}: nấc 1 chờ 3 phút`, LONG, async ($, on) => {
      const { io, ui } = await open($ as never, on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8(extra) })
      await io.clock.advance(150 * SEC)
      expect(rungs(io)).toEqual([])
      await io.clock.advance(35 * SEC)
      expect(rungs(io)).toEqual(['1'])
      await ui.unmount()
    })
  }

  test(`${surface}: thang im lặng — mỗi lúc một tín hiệu, cách ≥ 20 giây; thử thách hết giờ rồi nấc 1 tính từ lúc giáo viên nói xong`, LONG, async ($, on) => {
    const { io, ui } = await open($ as never, on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v8({ challenge: { title: 'Tìm 3 dòng thiếu giá', seconds: 60, started_at: iso(T0) } }) })
    const seen: number[] = []
    let prev = io.sent.length
    for (let t = 5; t <= 20 * 60; t += 5) {
      await io.clock.advance(5 * SEC)
      if (io.sent.length > prev) {
        expect(io.sent.length - prev).toBe(1)
        seen.push(t)
        prev = io.sent.length
        // Giáo viên đáp.
        await teacherTalks($ as never)
      }
    }
    expect(cues(io, 'Hết giờ thử thách · Tìm 3 dòng thiếu giá')).toBe(1)
    expect(rungs(io)).toEqual(['1', '2', '3'])
    for (let i = 1; i < seen.length; i++) expect(seen[i]! - seen[i - 1]!).toBeGreaterThanOrEqual(20)
    // Tín hiệu hết giờ ở giây 60; nấc 1 sau 2 phút kể từ lúc giáo viên đáp xong, không sớm hơn.
    expect(seen[0]).toBe(60)
    expect(seen[1]! - seen[0]!).toBeGreaterThanOrEqual(120)
    await ui.unmount()
  })

  test(`${surface}: thang im lặng — các tín hiệu khác vẫn "không giảng vào phòng trống": sau nấc 1, hạn mức chờ học viên tác động`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    let five = 50
    on('session.usage', async () => usageOf(five, 22))
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    await io.clock.settle()
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    await teacherTalks($ as never)
    await io.clock.advance(125 * SEC)
    expect(rungs(io)).toEqual(['1'])
    five = 75
    await teacherTalks($ as never)
    await io.clock.advance(60 * SEC)
    expect(io.sent.filter(x => x.startsWith('[Giáo án] Hạn mức'))).toHaveLength(0)
    io.box.text = 'vâng'
    await io.clock.advance(10 * SEC)
    io.box.text = ''
    await io.clock.advance(30 * SEC)
    expect(io.sent.filter(x => x.startsWith('[Giáo án] Hạn mức'))).toEqual(['[Giáo án] Hạn mức · 5 giờ 75% · reset 14:20'])
    await ui.unmount()
  })

  test(`${surface}: thang im lặng — ngoài thư mục lớp học không gửi gì`, LONG, async ($, on) => {
    const io = classroom(on, { 'README.md': 'x' })
    await $.session.start({ cwd: 'D:/other', surface, isInteractive: true } as never)
    await teacherTalks($ as never)
    await io.clock.advance(30 * MIN)
    expect(io.sent).toHaveLength(0)
  })
}

// ── v0.11: lời giáo viên dài gập lại (Desktop) ───────────────────────────────────
const LONG_TEXT = Array.from({ length: 12 }, (_, i) => `Dòng ${i + 1}: Claude đọc file, so từng cột rồi ghi lại kết quả vào bảng.`).join('\n')
const SHORT_TEXT = 'Chào chị, mình bắt đầu với một việc nhỏ nhé.'
const FOLDED = `${LONG_TEXT.split('\n').slice(0, 3).join('\n')}\n…`
const engineText = (io: Io) => (io.renders['AssistantMessage'] as { text?: string } | undefined)?.text

test('foldPreview: ngưỡng ~600 ký tự, 3 dòng đầu; ngắn hoặc không có gì để ẩn thì không gập', async () => {
  expect(foldPreview(SHORT_TEXT)).toBeNull()
  expect(foldPreview('a'.repeat(600))).toBeNull()
  expect(foldPreview(LONG_TEXT)).toBe(FOLDED)
  // Hai dòng rất dài: dòng được cắt, có dấu "…".
  const p = foldPreview(`${'x'.repeat(400)}\n${'y'.repeat(400)}`)!
  expect(p.length).toBeLessThan(500)
  expect(p).toContain('…')
  // Dòng trống đầu bị bỏ.
  expect(foldPreview(`\n${LONG_TEXT}`)).toBe(FOLDED)
})

test('desktop: lời giáo viên > ~600 ký tự gập thành 3 dòng + "▸ Xem đầy đủ"; bấm mở "▾ Thu gọn"; tin ngắn và khối tóm tắt giữ nguyên', LONG, async ($, on) => {
  const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
  await $.session.start({ cwd: 'D:/sandbox', surface: 'desktop', isInteractive: true } as never)
  const band = await $.ui.mount({ plugin: 'lop-hoc', surface: 'desktop', ...BAND } as never)
  await band.press({ key: 'enter' })
  const msg = (text: string, extra: object = {}) => $.ui.mount({ plugin: 'lop-hoc', surface: 'desktop', component: 'AssistantMessage', props: { text, isFirstOfReply: true, ...extra } } as never)
  const short = await msg(SHORT_TEXT)
  expect(await short.find({ key: 'fold' })).toBeUndefined()
  expect(engineText(io)).toBe(SHORT_TEXT)
  await short.unmount()
  const ui = await msg(LONG_TEXT)
  expect(engineText(io)).toBe(FOLDED)
  expect((await ui.find({ key: 'fold' }))?.props.label).toBe('▸ Xem đầy đủ')
  await ui.press({ key: 'fold' })
  expect(engineText(io)).toBe(LONG_TEXT)
  expect((await ui.find({ key: 'fold' }))?.props.label).toBe('▾ Thu gọn')
  await ui.press({ key: 'fold' })
  expect(engineText(io)).toBe(FOLDED)
  expect((await ui.find({ key: 'fold' }))?.props.label).toBe('▸ Xem đầy đủ')
  await ui.unmount()
  const sum = await msg(LONG_TEXT, { isFirstOfReply: false, isSummary: true })
  expect(await sum.find({ key: 'fold' })).toBeUndefined()
  expect(engineText(io)).toBe(LONG_TEXT)
  await sum.unmount()
  await band.unmount()
})

test('desktop: lớp tiếng Lào — nút gập bằng tiếng Lào', LONG, async ($, on) => {
  const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ language: 'lo' }) }
  classroom(on, files)
  await $.session.start({ cwd: 'D:/sandbox', surface: 'desktop', isInteractive: true } as never)
  const band = await $.ui.mount({ plugin: 'lop-hoc', surface: 'desktop', ...BAND } as never)
  await band.press({ key: 'enter' })
  await teacherTalks($ as never)
  const ui = await $.ui.mount({ plugin: 'lop-hoc', surface: 'desktop', component: 'AssistantMessage', props: { text: LONG_TEXT, isFirstOfReply: true } } as never)
  expect((await ui.find({ key: 'fold' }))?.props.label).toBe(STR.lo.foldMore)
  expect(STR.lo.foldMore).toMatch(/[\u0E80-\u0EFF]/)
  await ui.press({ key: 'fold' })
  expect((await ui.find({ key: 'fold' }))?.props.label).toBe(STR.lo.foldLess)
  await ui.unmount()
  await band.unmount()
})

test('terminal: lời giáo viên dài không gập (lịch sử cuộn, nút chưa chắc bấm được) — giữ nguyên', LONG, async ($, on) => {
  const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
  await $.session.start({ cwd: 'D:/sandbox', surface: 'terminal', isInteractive: true } as never)
  const band = await $.ui.mount({ plugin: 'lop-hoc', surface: 'terminal', ...BAND } as never)
  await band.press({ key: 'enter' })
  const ui = await $.ui.mount({ plugin: 'lop-hoc', surface: 'terminal', component: 'AssistantMessage', props: { text: LONG_TEXT, isFirstOfReply: true } } as never)
  expect(await ui.find({ key: 'fold' })).toBeUndefined()
  expect(engineText(io)).toBe(LONG_TEXT)
  await ui.unmount()
  await band.unmount()
})

test('ngoài thư mục lớp học: lời dài không gập', LONG, async ($, on) => {
  const io = classroom(on, { 'README.md': 'x' })
  await $.session.start({ cwd: 'D:/other', surface: 'desktop', isInteractive: true } as never)
  const ui = await $.ui.mount({ plugin: 'lop-hoc', surface: 'desktop', component: 'AssistantMessage', props: { text: LONG_TEXT, isFirstOfReply: true } } as never)
  expect(await ui.find({ key: 'fold' })).toBeUndefined()
  expect(engineText(io)).toBe(LONG_TEXT)
  await ui.unmount()
})

// ── v0.12 — bọc kín khung thầy: dòng việc, nhóm việc, kết quả, hộp câu hỏi, lệnh, suy nghĩ ──────────────
type Mounted = {
  find: (q: object) => Promise<{ props: Record<string, any>; text: string } | undefined>
  findAll: (q: object) => Promise<{ props: Record<string, any>; text: string }[]>
  press: (q: object) => Promise<unknown>
  unmount: () => Promise<void>
}
const useProps = (tool: string, input: object, extra: object = {}) => ({ tool_use_id: 't1', tool, input, isRunning: false, isErrored: false, isInterrupted: false, ...extra })
const gcall = (tool: string, input: object, extra: object = {}) => ({ tool, input, isRunning: false, isErrored: false, isInterrupted: false, ...extra })

test('toolKind · groupParts: đếm theo loại, đúng thứ tự, vi và lo; show_widget là "vẽ hình"', () => {
  expect(toolKind('Read')).toBe('read')
  expect(toolKind('Glob')).toBe('find')
  expect(toolKind('Bash')).toBe('run')
  expect(toolKind('mcp__visualize__show_widget')).toBe('draw')
  expect(toolKind('mcp__x__y')).toBe('mcp')
  expect(toolKind('TodoWrite')).toBe('other')
  const calls = [{ tool: 'Bash' }, { tool: 'Read' }, { tool: 'Write' }, { tool: 'Write' }, { tool: 'Read' }]
  expect(groupParts(calls, 'vi')).toBe('đọc 2 file · tạo 2 file · chạy 1 lệnh')
  expect(groupParts(calls, 'lo')).toBe('ອ່ານ 2 ໄຟລ໌ · ສ້າງ 2 ໄຟລ໌ · ແລ່ນ 1 ຄຳສັ່ງ')
  expect(groupParts([], 'vi')).toBe('')
  expect(describeTool('mcp__visualize__show_widget', {}, 'vi')).toBe('vẽ hình')
  expect(describeTool('mcp__visualize__show_widget', {}, 'lo')).toBe(STR.lo.tool.draw)
  expect(describeTool('Bash', {}, 'vi')).toBe('chạy một lệnh trên máy')
})

for (const surface of ['terminal', 'desktop'] as const) {
  const start = async ($: never, on: On, files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC' }) => {
    const io = classroom(on, files)
    const d = $ as unknown as { session: { start: (e: object) => Promise<unknown> } }
    await d.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true })
    return io
  }
  const mount = ($: never, component: string, props: object, requestId?: string) =>
    ($ as unknown as { ui: { mount: (e: object) => Promise<Mounted> } }).ui.mount({ plugin: 'lop-hoc', surface, component, props, ...(requestId ? { requestId } : {}) })
  const avatars = surface === 'desktop' ? 1 : 0

  test(`${surface} v0.12: dòng việc thành dòng thầy — đang / vừa / trục trặc / dừng; hình thầy nhỏ chỉ trên Desktop; chi tiết gốc sau nút`, LONG, async ($, on) => {
    await start($ as never, on)
    const file = { file_path: 'D:/x/phieu.xlsx' }
    const running = await mount($ as never, 'ToolUse', useProps('Read', file, { isRunning: true }))
    expect(await running.find({ text: '▸ Cô đang đọc phieu.xlsx…' })).toBeDefined()
    expect(await running.findAll({ type: 'Svg' })).toHaveLength(avatars)
    if (surface === 'desktop') {
      const sv = (await running.findAll({ type: 'Svg' }))[0]!
      expect(sv.props.width).toBe(18)
    }
    expect(await running.find({ key: 'engine' })).toBeUndefined()
    expect((await running.find({ key: 'detail' }))?.props.label).toBe('Xem chi tiết')
    await running.press({ key: 'detail' })
    expect(await running.find({ key: 'engine' })).toBeDefined()
    expect((await running.find({ key: 'detail' }))?.props.label).toBe('Thu gọn')
    await running.press({ key: 'detail' })
    expect(await running.find({ key: 'engine' })).toBeUndefined()
    await running.unmount()
    const done = await mount($ as never, 'ToolUse', useProps('Write', { file_path: 'bao-cao.docx' }))
    expect(await done.find({ text: '▸ Cô vừa ghi bao-cao.docx' })).toBeDefined()
    await done.unmount()
    const err = await mount($ as never, 'ToolUse', useProps('Bash', { command: 'dir' }, { isErrored: true }))
    expect(await err.find({ text: '▸ Cô gặp trục trặc, đang xử lý' })).toBeDefined()
    await err.unmount()
    const stop = await mount($ as never, 'ToolUse', useProps('Bash', { command: 'dir' }, { isInterrupted: true, isErrored: true }))
    expect(await stop.find({ text: '▸ Cô đã dừng việc này' })).toBeDefined()
    await stop.unmount()
    const draw = await mount($ as never, 'ToolUse', useProps('mcp__visualize__show_widget', { title: 'x' }, { isRunning: true }))
    expect(await draw.find({ text: '▸ Cô đang vẽ hình…' })).toBeDefined()
    await draw.unmount()
    const other = await mount($ as never, 'ToolUse', useProps('TodoWrite', { todos: [] }))
    expect(await other.find({ text: '▸ Cô vừa làm một việc' })).toBeDefined()
    await other.unmount()
  })

  test(`${surface} v0.12: dòng việc tiếng Lào; ghi sổ lớp vẫn một dòng mờ không nút`, LONG, async ($, on) => {
    await start($ as never, on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ language: 'lo' }) })
    const run = await mount($ as never, 'ToolUse', useProps('Read', { file_path: 'a.xlsx' }, { isRunning: true }))
    expect(await run.find({ text: '▸ ຄູກຳລັງອ່ານ a.xlsx…' })).toBeDefined()
    expect((await run.find({ key: 'detail' }))?.props.label).toBe(STR.lo.act.detail)
    expect(STR.lo.act.detail).toMatch(/[\u0E80-\u0EFF]/)
    await run.unmount()
    const done = await mount($ as never, 'ToolUse', useProps('Bash', { command: 'dir' }))
    expect(await done.find({ text: '▸ ຄູຫາກໍແລ່ນຄຳສັ່ງໃນເຄື່ອງ' })).toBeDefined()
    await done.unmount()
    const led = await mount($ as never, 'ToolUse', useProps('Write', { file_path: '.lop-hoc/state.json' }))
    expect(await led.find({ text: 'ຄູຈົດບັນທຶກຫ້ອງຮຽນ' })).toBeDefined()
    expect(await led.find({ key: 'detail' })).toBeUndefined()
    expect(await led.findAll({ type: 'Svg' })).toHaveLength(0)
    await led.unmount()
  })

  test(`${surface} v0.12: nhóm việc — một dòng thầy đếm theo loại (vi), đang/vừa, lỗi; nút mở nhóm`, LONG, async ($, on) => {
    const io = await start($ as never, on)
    const calls = [gcall('Read', { file_path: 'a' }), gcall('Glob', { pattern: '*' }), gcall('Write', { file_path: 'b' }), gcall('Write', { file_path: 'c' }), gcall('Bash', { command: 'ls' }), gcall('mcp__visualize__show_widget', {})]
    const g = await mount($ as never, 'ToolGroup', { calls, isActive: false, isExpanded: false })
    expect(await g.find({ text: '▸ Cô vừa: đọc 1 file · tìm 1 lần · tạo 2 file · chạy 1 lệnh · vẽ 1 hình' })).toBeDefined()
    expect(await g.findAll({ type: 'Svg' })).toHaveLength(avatars)
    expect(await g.find({ key: 'engine' })).toBeUndefined()
    expect(io.renders.ToolGroup).toBeUndefined()
    await g.press({ key: 'detail' })
    expect(io.renders.ToolGroup?.isExpanded).toBe(true)
    expect(await g.find({ key: 'engine' })).toBeDefined()
    expect((await g.find({ key: 'detail' }))?.props.label).toBe('Thu gọn')
    await g.press({ key: 'detail' })
    expect(await g.find({ key: 'engine' })).toBeUndefined()
    await g.unmount()
    const live = await mount($ as never, 'ToolGroup', { calls: [gcall('Read', { file_path: 'a' }, { isRunning: true })], isActive: true, isExpanded: false })
    expect(await live.find({ text: '▸ Cô đang: đọc 1 file' })).toBeDefined()
    await live.unmount()
    const bad = await mount($ as never, 'ToolGroup', { calls: [gcall('Bash', { command: 'x' }, { isErrored: true })], isActive: false, isExpanded: false })
    expect(await bad.find({ text: '▸ Cô vừa: chạy 1 lệnh · có trục trặc, cô đang xử lý' })).toBeDefined()
    await bad.unmount()
    // Nhóm engine đã mở (--verbose): từng dòng là ToolUse của thầy, không bọc thêm.
    const open = await mount($ as never, 'ToolGroup', { calls: [gcall('Read', { file_path: 'a' })], isActive: false, isExpanded: true })
    expect(await open.find({ key: 'engine' })).toBeDefined()
    expect(await open.find({ key: 'detail' })).toBeUndefined()
    await open.unmount()
  })

  test(`${surface} v0.12: nhóm việc tiếng Lào`, LONG, async ($, on) => {
    await start($ as never, on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ language: 'lo' }) })
    const g = await mount($ as never, 'ToolGroup', { calls: [gcall('Read', { file_path: 'a' }), gcall('Bash', { command: 'x' })], isActive: false, isExpanded: false })
    expect(await g.find({ text: '▸ ຄູຫາກໍ: ອ່ານ 1 ໄຟລ໌ · ແລ່ນ 1 ຄຳສັ່ງ' })).toBeDefined()
    await g.unmount()
  })

  test(`${surface} v0.12: kết quả công cụ gập sẵn "Kết quả · xem"; lỗi "Có lỗi — thầy đang xử lý · xem"; nút mở/thu; kết quả ghi sổ ẩn`, LONG, async ($, on) => {
    await start($ as never, on)
    const ok = await mount($ as never, 'ToolResult', { tool_use_id: 'r1', tool: 'Bash', output: { stdout: 'x', stderr: '' }, isErrored: false }, 'r1')
    expect((await ok.find({ key: 'detail' }))?.props.label).toBe('Kết quả · xem')
    expect(await ok.find({ key: 'engine' })).toBeUndefined()
    await ok.press({ key: 'detail' })
    expect(await ok.find({ key: 'engine' })).toBeDefined()
    expect((await ok.find({ key: 'detail' }))?.props.label).toBe('Thu gọn')
    await ok.press({ key: 'detail' })
    expect((await ok.find({ key: 'detail' }))?.props.label).toBe('Kết quả · xem')
    await ok.unmount()
    const bad = await mount($ as never, 'ToolResult', { tool_use_id: 'r2', tool: 'Bash', output: 'lỗi', isErrored: true }, 'r2')
    expect((await bad.find({ key: 'detail' }))?.props.label).toBe('Có lỗi — cô đang xử lý · xem')
    await bad.unmount()
    // Dòng ghi sổ → kết quả của nó biến mất (nhưng lỗi vẫn hiện).
    const led = await mount($ as never, 'ToolUse', useProps('Write', { file_path: '.lop-hoc/state.json' }), 'led1')
    expect(await led.find({ text: 'Cô ghi sổ lớp' })).toBeDefined()
    const hid = await mount($ as never, 'ToolResult', { tool_use_id: 'led1', tool: 'Write', output: {}, isErrored: false }, 'led1')
    expect(await hid.find({ key: 'detail' })).toBeUndefined()
    expect(await hid.find({ key: 'engine' })).toBeUndefined()
    await hid.unmount()
    const hidErr = await mount($ as never, 'ToolResult', { tool_use_id: 'led1', tool: 'Write', output: 'x', isErrored: true }, 'led1')
    expect(await hidErr.find({ key: 'detail' })).toBeDefined()
    await hidErr.unmount()
    await led.unmount()
  })

  test(`${surface} v0.12: kết quả công cụ tiếng Lào`, LONG, async ($, on) => {
    await start($ as never, on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ language: 'lo' }) })
    const ok = await mount($ as never, 'ToolResult', { tool_use_id: 'r1', tool: 'Bash', output: {}, isErrored: false })
    expect((await ok.find({ key: 'detail' }))?.props.label).toBe(STR.lo.act.result)
    await ok.unmount()
    const bad = await mount($ as never, 'ToolResult', { tool_use_id: 'r2', tool: 'Bash', output: 'x', isErrored: true })
    expect((await bad.find({ key: 'detail' }))?.props.label).toBe(STR.lo.act.resultError('ຄູ'))
    await bad.unmount()
  })

  test(`${surface} v0.12: hộp câu hỏi có khung đầy đủ — viền tròn #008816, hình thầy trên Desktop, dòng tiêu đề, hộp gốc đúng một lần`, LONG, async ($, on) => {
    await start($ as never, on)
    const ui = await mount($ as never, 'AskUserQuestion', { tool: 'AskUserQuestion', questions: [{ question: 'Chọn?', header: 'Hỏi', multiSelect: false, options: [{ label: 'A', description: '' }, { label: 'B', description: '' }] }] })
    expect(await ui.find({ text: 'Cô hỏi' })).toBeDefined()
    const frames = (await ui.findAll({ type: 'Box' })).filter(b => b.props.borderStyle === 'round' && b.props.borderColor === '#008816')
    expect(frames).toHaveLength(1)
    expect(await ui.findAll({ type: 'Svg' })).toHaveLength(surface === 'desktop' ? 1 : 0)
    expect(await ui.findAll({ type: 'engine' })).toHaveLength(1)
    await ui.unmount()
  })

  test(`${surface} v0.12: lệnh /reload-plugins → "Đã nạp lại lớp học ✓"; lệnh khác → một dòng thầy + nút tới chữ gốc; /lop-hoc giữ nguyên`, LONG, async ($, on) => {
    await start($ as never, on)
    const out = (command: string, text: string, extra: object = {}) => mount($ as never, 'CommandOutput', { command, args: '', text, isErrored: false, ...extra })
    const re = await out('reload-plugins', 'Reloaded: 31 plugins · 191 skills')
    expect(await re.find({ text: 'Đã nạp lại lớp học ✓' })).toBeDefined()
    expect(await re.find({ key: 'engine' })).toBeUndefined()
    expect(await re.find({ key: 'detail' })).toBeUndefined()
    expect(await re.findAll({ type: 'Svg' })).toHaveLength(avatars)
    await re.unmount()
    const cost = await out('cost', 'Total cost: $0.12')
    expect(await cost.find({ text: '▸ Cô vừa chạy lệnh /cost' })).toBeDefined()
    expect(await cost.find({ key: 'engine' })).toBeUndefined()
    await cost.press({ key: 'detail' })
    expect(await cost.find({ key: 'engine' })).toBeDefined()
    await cost.unmount()
    const bad = await out('cost', 'boom', { isErrored: true })
    expect(await bad.find({ text: '▸ Lệnh /cost gặp trục trặc — Cô đang xử lý' })).toBeDefined()
    await bad.unmount()
    const bad2 = await out('reload-plugins', 'boom', { isErrored: true })
    expect(await bad2.find({ text: 'Đã nạp lại lớp học ✓' })).toBeUndefined()
    expect(await bad2.find({ key: 'detail' })).toBeDefined()
    await bad2.unmount()
    const own = await out('lop-hoc', 'Đã mở bảng tóm tắt Lớp học NNC.')
    expect(await own.find({ key: 'engine' })).toBeDefined()
    expect(await own.find({ key: 'detail' })).toBeUndefined()
    await own.unmount()
  })

  test(`${surface} v0.12: lệnh tải lại bằng tiếng Lào`, LONG, async ($, on) => {
    await start($ as never, on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ language: 'lo' }) })
    const re = await mount($ as never, 'CommandOutput', { command: 'reload-plugins', args: '', text: 'Reloaded', isErrored: false })
    expect(await re.find({ text: 'ໂຫຼດຫ້ອງຮຽນໃໝ່ແລ້ວ ✓' })).toBeDefined()
    await re.unmount()
    const cost = await mount($ as never, 'CommandOutput', { command: 'cost', args: '', text: 'x', isErrored: false })
    expect(await cost.find({ text: '▸ ຄູຫາກໍແລ່ນຄຳສັ່ງ /cost' })).toBeDefined()
    await cost.unmount()
  })

  test(`${surface} v0.12: ngoài thư mục lớp học mọi thành phần giữ nguyên (không nút, không khung)`, LONG, async ($, on) => {
    const io = classroom(on, { 'README.md': 'x' })
    await ($ as unknown as { session: { start: (e: object) => Promise<unknown> } }).session.start({ cwd: 'D:/other', surface, isInteractive: true })
    const cases: [string, object][] = [
      ['ToolUse', useProps('Read', { file_path: 'a.xlsx' }, { isRunning: true })],
      ['ToolGroup', { calls: [gcall('Read', { file_path: 'a' })], isActive: false, isExpanded: false }],
      ['ToolResult', { tool_use_id: 'r1', tool: 'Bash', output: {}, isErrored: false }],
      ['CommandOutput', { command: 'reload-plugins', args: '', text: 'Reloaded', isErrored: false }],
    ]
    for (const [component, props] of cases) {
      const ui = await mount($ as never, component, props)
      expect(await ui.find({ key: 'engine' })).toBeDefined()
      expect(await ui.find({ key: 'detail' })).toBeUndefined()
      expect(await ui.findAll({ type: 'Svg' })).toHaveLength(0)
      await ui.unmount()
    }
    expect(io.renders.ToolGroup?.isExpanded).toBe(false)
    const ask = await mount($ as never, 'AskUserQuestion', { tool: 'AskUserQuestion', questions: [{ question: 'Chọn?', header: 'Hỏi', multiSelect: false, options: [{ label: 'A', description: '' }, { label: 'B', description: '' }] }] })
    expect(await ask.findAll({ type: 'Box' })).toHaveLength(0)
    await ask.unmount()
  })

  // Luồng turn.step: engine giả nói "Tôi chấm lại…" trong khối suy nghĩ.
  type Chunk = { kind: string; text?: string; index?: number }
  const stepOf = ($: never, on: On, chunks: object[]) => {
    on('turn.step', async function* (_$, e) {
      for (const c of chunks) yield c as never
      return { turnId: e.turnId, index: e.index, answer: 'Chào chị', toolUses: [], stopReason: 'end_turn', usage: null } as never
    })
    return async () => {
      const out: Chunk[] = []
      const stream = ($ as unknown as { turn: { step: (e: object) => AsyncIterable<Chunk> } }).turn.step({ turnId: 'tt', index: 0, model: 'claude-opus-5-5', messageCount: 1 })
      for await (const c of stream) out.push(c)
      return out
    }
  }
  const SAID = [
    { kind: 'thinking', index: 0, text: 'Tôi chấm lại 3 câu' },
    { kind: 'thinking', index: 0, text: ' rồi so với đáp án' },
    { kind: 'text', index: 1, text: 'Chào chị' },
    { kind: 'thinking', index: 2, text: 'Tôi nghĩ tiếp' },
  ]

  test(`${surface} v0.12: suy nghĩ hiện lúc đang chạy chỉ còn một dòng của thầy, phần còn lại để trống; chữ trả lời giữ nguyên`, LONG, async ($, on) => {
    const run = stepOf($ as never, on, SAID)
    await start($ as never, on)
    const out = await run()
    expect(out.map(c => c.kind)).toEqual(['thinking', 'thinking', 'text', 'thinking'])
    expect(out[0]?.text).toBe('Cô đang suy nghĩ…')
    expect(out[1]?.text).toBe('')
    expect(out[3]?.text).toBe('')
    expect(out[2]?.text).toBe('Chào chị')
    expect(out.map(c => c.text).join('')).not.toMatch(/Tôi/)
  })

  test(`${surface} v0.12: suy nghĩ tiếng Lào`, LONG, async ($, on) => {
    const run = stepOf($ as never, on, SAID)
    await start($ as never, on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ language: 'lo' }) })
    expect((await run())[0]?.text).toBe('ຄູກຳລັງຄິດ…')
  })

  test(`${surface} v0.12: ngoài lớp học suy nghĩ không đổi`, LONG, async ($, on) => {
    const run = stepOf($ as never, on, SAID)
    classroom(on, { 'README.md': 'x' })
    await ($ as unknown as { session: { start: (e: object) => Promise<unknown> } }).session.start({ cwd: 'D:/other', surface, isInteractive: true })
    const out = await run()
    expect(out[0]?.text).toBe('Tôi chấm lại 3 câu')
    expect(out[1]?.text).toBe(' rồi so với đáp án')
  })
}

// ── v0.13 — màn Thiết lập, thẻ bước, nút Xong · Chưa được · Gợi ý, bong bóng lời nói, im lặng 45 giây, giao diện sáng/tối ──────────
const HINT = (id: string, n: number, lang: 'vi' | 'lo' = 'vi') => stepView({ id }, lang).hints![n - 1]!

test('stepView · stepOf: bước 0 khi chưa có state.step; id có trong giáo án → k/N, why, gợi ý theo tiếng; title của giáo viên thắng; id lạ chỉ có title', () => {
  expect(stepView(null, 'vi')).toMatchObject({ id: '0', k: 1, n: 8, title: 'Tham quan lớp học', cueTitle: 'Tham quan lớp học', why: 'biết dùng chính công cụ học' })
  expect(stepView({ id: '3' }, 'vi')).toMatchObject({ k: 4, title: 'Chế độ Auto' })
  expect(stepView({ id: '0' }, 'lo')).toMatchObject({ k: 1, title: 'ທ່ຽວຊົມຫ້ອງຮຽນ', cueTitle: 'Tham quan lớp học' }) // tín hiệu luôn tiếng Việt
  expect(stepView({ id: '2', title: 'Việc đầu tiên của vòng 2' }, 'vi')).toMatchObject({ k: 3, title: 'Việc đầu tiên của vòng 2', cueTitle: 'Việc đầu tiên của vòng 2', why: null, hints: null })
  expect(stepView({ id: 'v2-1', title: 'Soạn thư nhắc nợ' }, 'vi')).toMatchObject({ id: 'v2-1', k: null, n: 8, title: 'Soạn thư nhắc nợ', why: null, hints: null })
  expect(stepView({ id: 'v2-1' }, 'vi')).toMatchObject({ title: '', cueTitle: '' })
  expect(stepOf({ id: '4', title: 'x' })).toEqual({ id: '4', title: 'x' })
  expect(stepOf({ id: 5 })).toEqual({ id: '5' })
  expect(stepOf('2')).toEqual({ id: '2' })
  expect(stepOf({ title: 'thiếu id' })).toBeNull()
  expect(stepOf(null)).toBeNull()
  expect(stepOf({ id: ['x'] })).toBeNull()
})

test('railText · addrLabel · paletteOf: thanh bước chữ, cách gọi theo tiếng, bảng màu sáng/tối', () => {
  expect(railText(2, 8)).toBe('●◉○○○○○○')
  expect(railText(8, 8)).toBe('●●●●●●●◉')
  expect(addrLabel('Chị', 'vi')).toBe('Chị')
  expect(addrLabel('Chị', 'lo')).toBe('ເອື້ອຍ')
  expect(addrLabel('Chị Lan', 'lo')).toBe('Chị Lan')
  expect(paletteOf('light')).toEqual(LIGHT)
  expect(paletteOf('Light-Daltonized')).toBe(LIGHT)
  expect(LIGHT).toMatchObject({ board: '#EAF4EC', ink: '#14301B', dim: '#3F6A4A', accent: '#006D11', frame: '#008816' })
  for (const v of ['dark', 'auto', 'dark-ansi', '', undefined, null, 7, true]) expect(paletteOf(v)).toBe(DARK)
  expect(DARK).toMatchObject({ board: '#123F1E', ink: '#F4F4EC', dim: '#B9D3BF', accent: '#FFEA00' })
})

test('bubbleKind: suy nghĩ · nói · đọc · ghi · chạy lệnh · tra cứu · việc khác; khối khác không đổi bong bóng', () => {
  expect(bubbleKind({ kind: 'thinking' })).toBe('think')
  expect(bubbleKind({ kind: 'text' })).toBe('say')
  for (const n of ['Read', 'Glob', 'Grep']) expect(bubbleKind({ kind: 'tool', name: n })).toBe('read')
  for (const n of ['Write', 'Edit', 'NotebookEdit']) expect(bubbleKind({ kind: 'tool', name: n })).toBe('write')
  for (const n of ['Bash', 'PowerShell']) expect(bubbleKind({ kind: 'tool', name: n })).toBe('run')
  for (const n of ['WebFetch', 'WebSearch']) expect(bubbleKind({ kind: 'tool', name: n })).toBe('web')
  for (const n of ['TodoWrite', 'mcp__x__y', 'Skill']) expect(bubbleKind({ kind: 'tool', name: n })).toBe('work')
  expect(bubbleKind({ kind: 'input' })).toBeNull()
  expect(bubbleKind({ kind: 'stop' })).toBeNull()
  expect(STR.vi.bubble('think', 'Thầy')).toBe('Thầy đang nghĩ cách làm…')
  expect(STR.vi.bubble('say', 'Cô')).toBe('Cô đang nói với bạn…')
  expect(STR.vi.bubble('read', 'Thầy')).toBe('Thầy đang đọc file…')
  expect(STR.vi.bubble('write', 'Thầy')).toBe('Thầy đang ghi file…')
  expect(STR.vi.bubble('run', 'Thầy')).toBe('Thầy đang chạy một lệnh trên máy…')
  expect(STR.vi.bubble('web', 'Thầy')).toBe('Thầy đang tra cứu…')
  expect(STR.vi.bubble('work', 'Thầy')).toBe('Thầy đang làm việc…')
  expect(STR.lo.bubble('read', 'ຄູ')).toMatch(/^ຄູ/)
})

test('i18n v0.13: mọi chữ mới có đủ tiếng Việt và tiếng Lào', () => {
  const LAO = /[\u0E80-\u0EFF]/
  const pick = (S: typeof STR.vi) => [S.setTitle, S.setLang, S.setAddress, S.setAddressFree, S.setAddressHint, S.save, S.setMenu, S.stepHead(1, 8, 'x'), S.stepWhy('y'), S.stepDone, S.stepNot, S.stepHint, S.hintLabel(1), S.nudge, S.showPic, S.hidePic, S.bubble('read', 'T'), S.menuProgress, S.progressNone, S.railAlt(1, 8), ...Object.values(S.addr)]
  for (const t of pick(STR.vi)) expect(t.length > 0).toBe(true)
  for (const t of pick(STR.lo)) expect(LAO.test(t)).toBe(true)
  expect(STR.vi.stepHead(1, 8, 'Tham quan lớp học')).toBe('Bước 1/8 · Tham quan lớp học')
  expect(STR.vi.stepWhy('biết dùng chính công cụ học')).toBe('để biết dùng chính công cụ học')
  expect(STR.lo.stepWhy('x')).toBe('ເພື່ອ x')
  expect(STR.lo.addr).toEqual({ anh: 'ອ້າຍ', chi: 'ເອື້ອຍ', em: 'ນ້ອງ', ban: 'ທ່ານ' })
  expect(STR.vi.nudge).toBe('👉 Làm xong thì bấm Xong — chưa biết làm thì bấm Gợi ý')
})

for (const surface of ['terminal', 'desktop'] as const) {
  test(`${surface}: màn Thiết lập — chọn tiếng Lào, tên tự viết, cô/thầy → Vào lớp gửi đúng câu Mở lớp và lưu $.store; học viên thắng state.json`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ language: 'vi', address: 'anh' }) }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    // Một ngôn ngữ (v0.13): dòng chờ chỉ bằng tiếng đang chọn; ba hàng thiết lập, nút Vào lớp.
    expect(await ui.find({ text: /Lớp đang chờ giáo viên/ })).toBeDefined()
    expect(await ui.find({ text: /ຫ້ອງຮຽນລໍຖ້າຄູ/ })).toBeUndefined()
    for (const key of ['lang-vi', 'lang-lo', 'addr-anh', 'addr-chi', 'addr-em', 'addr-ban', 'addr-text', 't-thay', 't-co', 'enter']) expect(await ui.find({ key })).toBeDefined()
    expect((await ui.find({ key: 'lang-vi' }))?.props.variant).toBe('primary')
    expect((await ui.find({ key: 'addr-anh' }))?.props.variant).toBe('primary') // state.address làm mặc định khi học viên chưa chọn
    await ui.press({ key: 'lang-lo' })
    expect((await ui.find({ key: 'lang-lo' }))?.props.variant).toBe('primary')
    expect((await ui.find({ key: 'addr-ban' }))?.props.label).toBe('ທ່ານ')
    expect((await ui.find({ key: 'addr-chi' }))?.props.label).toBe('ເອື້ອຍ')
    expect(await ui.find({ text: /ເລືອກພາສາ/ })).toBeDefined()
    await ui.press({ key: 't-thay' })
    await ui.input({ key: 'addr-text', text: 'Chị Lan' })
    await ui.press({ key: 'enter' })
    expect(io.sent).toEqual(['[Giáo án] Mở lớp · giáo viên thay · ngôn ngữ lo · gọi “Chị Lan”'])
    expect(io.stored.language).toBe('lo')
    expect(io.stored.address).toBe('Chị Lan')
    expect(io.stored.teacher).toBe('thay')
    // Giáo viên ghi language 'vi' · address 'em': lựa chọn của học viên thắng.
    files['.lop-hoc/state.json'] = v7({ language: 'vi', address: 'em' })
    await teacherTalks($ as never)
    expect(await ui.find({ text: /ພາກ 2/ })).toBeDefined()
    expect(await ui.find({ text: /Phần 2/ })).toBeUndefined()
    await ui.unmount()
  })

  test(`${surface}: màn Thiết lập — ô tự viết cắt ở 30 ký tự; chọn nút sẵn thì bỏ chữ tự viết; cô mặc định, Bạn mặc định`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    expect((await ui.find({ key: 'addr-ban' }))?.props.variant).toBe('primary')
    expect((await ui.find({ key: 't-co' }))?.props.variant).toBe('primary')
    await ui.input({ key: 'addr-text', text: 'x'.repeat(45) })
    await ui.press({ key: 'addr-em' })
    expect((await ui.find({ key: 'addr-em' }))?.props.variant).toBe('primary')
    await ui.input({ key: 'addr-text', text: 'y'.repeat(45) })
    await ui.press({ key: 'enter' })
    expect(io.sent).toEqual([`[Giáo án] Mở lớp · giáo viên co · ngôn ngữ vi · gọi “${'y'.repeat(30)}”`])
    await ui.unmount()
  })

  test(`${surface}: ⋯ → Thiết lập → Lưu: gửi "[Giáo án] Thiết lập …" chỉ khi có đổi; Thôi thì không đổi gì; quay lại bục thường`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    const saved = async (k: string) => io.stored[k]
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(io.sent).toEqual([OPEN_BAN])
    // Mở rồi Lưu không đổi gì: không gửi.
    await ui.press({ key: 'more' })
    await ui.press({ key: 'thiet-lap' })
    expect(await ui.find({ key: 'enter' })).toBeUndefined()
    expect((await ui.find({ key: 'luu' }))?.props.label).toBe('Lưu')
    expect(await ui.find({ key: 'xong' })).toBeUndefined()
    expect(await ui.find({ text: /Lớp đang chờ giáo viên/ })).toBeUndefined()
    await ui.press({ key: 'luu' })
    expect(io.sent).toEqual([OPEN_BAN])
    expect(await ui.find({ key: 'xong' })).toBeDefined()
    // Thôi: bỏ các thay đổi.
    await ui.press({ key: 'more' })
    await ui.press({ key: 'thiet-lap' })
    await ui.press({ key: 'lang-lo' })
    await ui.press({ key: 'addr-anh' })
    await ui.press({ key: 'thiet-lap-thoi' })
    expect(io.sent).toEqual([OPEN_BAN])
    expect(await ui.find({ key: 'xong' })).toBeDefined()
    expect((await ui.find({ key: 'xong' }))?.props.label).toBe('Xong') // vẫn tiếng Việt
    // Đổi thật: tiếng Lào, "ອ້າຍ" (Anh), thầy.
    await ui.press({ key: 'more' })
    await ui.press({ key: 'thiet-lap' })
    await ui.press({ key: 'lang-lo' })
    await ui.press({ key: 'addr-anh' })
    await ui.press({ key: 't-thay' })
    await ui.press({ key: 'luu' })
    expect(io.sent).toEqual([OPEN_BAN, '[Giáo án] Thiết lập · ngôn ngữ lo · gọi “ອ້າຍ” · giáo viên thay'])
    expect((await ui.find({ key: 'xong' }))?.props.label).toBe('ແລ້ວ')
    expect(await saved('language')).toBe('lo')
    expect(await saved('address')).toBe('Anh')
    expect(await saved('teacher')).toBe('thay')
    // Tên tự viết cũng lưu, bằng tiếng Việt.
    await ui.press({ key: 'more' })
    await ui.press({ key: 'thiet-lap' })
    await ui.press({ key: 'lang-vi' })
    await ui.input({ key: 'addr-text', text: 'Lan' })
    await ui.press({ key: 'luu' })
    expect(io.sent[io.sent.length - 1]).toBe('[Giáo án] Thiết lập · ngôn ngữ vi · gọi “Lan” · giáo viên thay')
    expect(await ui.find({ text: /Thầy/ })).toBeDefined()
    await ui.unmount()
  })

  test(`${surface}: thẻ bước — "Bước 1/8 · Tham quan lớp học" + "để …" + Xong · Chưa được · Gợi ý ngay sau Vào lớp, trước cả lời giáo viên`, LONG, async ($, on) => {
    classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(await ui.find({ text: 'Bước 1/8 · Tham quan lớp học' })).toBeDefined()
    expect(await ui.find({ text: 'để biết dùng chính công cụ học' })).toBeDefined()
    for (const [key, label] of [['xong', 'Xong'], ['chua-duoc', 'Chưa được'], ['goi-y-buoc', 'Gợi ý']]) expect((await ui.find({ key }))?.props.label).toBe(label)
    // Thanh bước: Svg trên desktop, chữ trên terminal.
    if (surface === 'desktop') expect((await svgByAlt(ui, /^Bước 1 trên 8$/))?.props.source).toContain('<circle')
    else expect(await ui.find({ text: '◉○○○○○○○' })).toBeDefined()
    await noForbiddenWords(ui as never)
    await ui.unmount()
  })

  test(`${surface}: thẻ bước theo state.step — bước 3, đổi tên bước, id lạ có tên, id lạ không tên (ẩn tiêu đề, giữ nút); tiếng Lào; thanh bước`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ step: { id: '3' } }) }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(await ui.find({ text: 'Bước 4/8 · Chế độ Auto' })).toBeDefined()
    // Lời "để …" không lặp chữ "để" khi lời của giáo án đã bắt đầu bằng "để".
    expect(await ui.find({ text: 'để Claude làm mà không hỏi từng việc nhỏ' })).toBeDefined()
    if (surface === 'terminal') expect(await ui.find({ text: '●●●◉○○○○' })).toBeDefined()
    files['.lop-hoc/state.json'] = v7({ step: { id: '3', title: 'Chế độ Auto lần hai' } })
    await io.clock.advance(2 * SEC)
    expect(await ui.find({ text: 'Bước 4/8 · Chế độ Auto lần hai' })).toBeDefined()
    expect(await ui.find({ text: /^để / })).toBeUndefined()
    files['.lop-hoc/state.json'] = v7({ step: { id: 'v2-1', title: 'Soạn thư nhắc nợ' } })
    await io.clock.advance(2 * SEC)
    expect(await ui.find({ text: 'Soạn thư nhắc nợ' })).toBeDefined()
    expect(await ui.find({ text: /^Bước / })).toBeUndefined()
    expect(await ui.find({ key: 'xong' })).toBeDefined()
    if (surface === 'desktop') expect(await svgByAlt(ui, /^Bước \d trên 8$/)).toBeUndefined()
    files['.lop-hoc/state.json'] = v7({ step: { id: 'v2-1' } })
    await io.clock.advance(2 * SEC)
    expect(await ui.find({ text: /^Bước |Soạn thư/ })).toBeUndefined()
    for (const key of ['xong', 'chua-duoc', 'goi-y-buoc']) expect(await ui.find({ key })).toBeDefined()
    await ui.press({ key: 'xong' })
    expect(io.sent[io.sent.length - 1]).toBe('[Giáo án] Xong · bước v2-1')
    await ui.unmount()
  })

  test(`${surface}: thẻ bước tiếng Lào — Bước k/N → ຂັ້ນ k/N, "để" → ເພື່ອ, nút ແລ້ວ · ຍັງບໍ່ໄດ້ · ແນະນຳ; tín hiệu vẫn tiếng Việt`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'lang-lo' })
    await ui.press({ key: 'enter' })
    expect(await ui.find({ text: 'ຂັ້ນ 1/8 · ທ່ຽວຊົມຫ້ອງຮຽນ' })).toBeDefined()
    expect(await ui.find({ text: 'ເພື່ອ ຮູ້ຈັກໃຊ້ເຄື່ອງມືຮຽນ' })).toBeDefined()
    expect((await ui.find({ key: 'xong' }))?.props.label).toBe('ແລ້ວ')
    expect((await ui.find({ key: 'chua-duoc' }))?.props.label).toBe('ຍັງບໍ່ໄດ້')
    expect((await ui.find({ key: 'goi-y-buoc' }))?.props.label).toBe('ແນະນຳ')
    await ui.press({ key: 'goi-y-buoc' })
    expect(await ui.find({ text: `ແນະນຳ 1/3 · ${HINT('0', 1, 'lo')}` })).toBeDefined()
    await ui.press({ key: 'xong' })
    expect(io.sent[io.sent.length - 1]).toBe('[Giáo án] Xong · bước 0 · Tham quan lớp học')
    await ui.unmount()
  })

  test(`${surface}: Xong · Chưa được gửi đúng câu "[Giáo án] Xong · bước {id} · {tên}"; tính là học viên tác động (xoá nhắc, xoá thang im lặng)`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ step: { id: '2' } }) }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    await teacherTalks($ as never)
    await io.clock.advance(125 * SEC)
    expect(rungs(io)).toEqual(['1'])
    await ui.press({ key: 'xong' })
    expect(io.sent[io.sent.length - 1]).toBe('[Giáo án] Xong · bước 2 · Việc đầu tiên')
    expect(await ui.find({ text: /Làm xong thì bấm Xong/ })).toBeUndefined()
    await ui.press({ key: 'chua-duoc' })
    expect(io.sent[io.sent.length - 1]).toBe('[Giáo án] Chưa được · bước 2 · Việc đầu tiên')
    // Thầy đáp; thang im lặng tính lại từ đầu sau lần bấm.
    await teacherTalks($ as never)
    await io.clock.advance(110 * SEC)
    expect(rungs(io)).toEqual(['1'])
    await io.clock.advance(15 * SEC)
    expect(rungs(io)).toEqual(['1', '1'])
    await ui.unmount()
  })

  test(`${surface}: Gợi ý — nấc 1 hiện gợi ý đầu tại chỗ, không gửi gì; nấc 2 · 3 gửi "[Giáo án] Gợi ý · bước {id} · nấc n" và hiện gợi ý tương ứng; bấm nữa thì quay lại nấc 1; đổi bước thì về 0`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ step: { id: '3' } }) }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    const before = io.sent.length
    expect(await ui.find({ text: /^Gợi ý \d\/3/ })).toBeUndefined()
    await ui.press({ key: 'goi-y-buoc' })
    expect(io.sent.length).toBe(before)
    expect(await ui.find({ text: `Gợi ý 1/3 · ${HINT('3', 1)}` })).toBeDefined()
    await ui.press({ key: 'goi-y-buoc' })
    expect(io.sent[io.sent.length - 1]).toBe('[Giáo án] Gợi ý · bước 3 · nấc 2')
    expect(await ui.find({ text: `Gợi ý 2/3 · ${HINT('3', 2)}` })).toBeDefined()
    expect(await ui.find({ text: /^Gợi ý 1\/3/ })).toBeUndefined()
    await ui.press({ key: 'goi-y-buoc' })
    expect(io.sent[io.sent.length - 1]).toBe('[Giáo án] Gợi ý · bước 3 · nấc 3')
    expect(await ui.find({ text: `Gợi ý 3/3 · ${HINT('3', 3)}` })).toBeDefined()
    expect(io.sent.filter(t => t.includes('Gợi ý ·'))).toHaveLength(2)
    await ui.press({ key: 'goi-y-buoc' })
    expect(io.sent.filter(t => t.includes('Gợi ý ·'))).toHaveLength(2)
    expect(await ui.find({ text: `Gợi ý 1/3 · ${HINT('3', 1)}` })).toBeDefined()
    // Đổi bước: gợi ý cũ biến mất, nút bắt đầu lại từ nấc 1 (cục bộ).
    await ui.press({ key: 'goi-y-buoc' })
    files['.lop-hoc/state.json'] = v7({ step: { id: '4' } })
    await io.clock.advance(2 * SEC)
    expect(await ui.find({ text: 'Bước 5/8 · Tự kiểm' })).toBeDefined()
    expect(await ui.find({ text: /^Gợi ý \d\/3/ })).toBeUndefined()
    const n = io.sent.length
    await ui.press({ key: 'goi-y-buoc' })
    expect(io.sent.length).toBe(n)
    expect(await ui.find({ text: `Gợi ý 1/3 · ${HINT('4', 1)}` })).toBeDefined()
    // Bước không có gợi ý sẵn: bỏ nấc 1, đi thẳng nấc 2.
    files['.lop-hoc/state.json'] = v7({ step: { id: 'v2-1', title: 'Soạn thư nhắc nợ' } })
    await io.clock.advance(2 * SEC)
    await ui.press({ key: 'goi-y-buoc' })
    expect(io.sent[io.sent.length - 1]).toBe('[Giáo án] Gợi ý · bước v2-1 · nấc 2')
    await ui.unmount()
  })

  test(`${surface}: nhắc trên bục sau 45 giây là cục bộ (không có tín hiệu nào); ẩn khi đang gõ, khi thầy đang làm, khi xin phép`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7(WITH_ALL) })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    await teacherTalks($ as never)
    const NUDGE = { text: /^👉 Làm xong thì bấm Xong — chưa biết làm thì bấm Gợi ý$/ }
    await io.clock.advance(50 * SEC)
    const nudge = await ui.find({ type: 'Text', ...NUDGE })
    expect(nudge).toBeDefined()
    expect(nudge?.props.color).toBe('#FFEA00') // vàng trên nền tối
    expect(io.sent).toEqual([OPEN_CHI])
    // Đang gõ: không nhắc.
    io.box.text = 'em đang nghĩ'
    await io.clock.advance(10 * SEC)
    expect(await ui.find(NUDGE)).toBeUndefined()
    io.box.text = ''
    await io.clock.advance(35 * SEC)
    expect(await ui.find(NUDGE)).toBeUndefined() // gõ xong tính lại từ đầu
    await io.clock.advance(15 * SEC)
    expect(await ui.find(NUDGE)).toBeDefined()
    // Xin phép: không nhắc.
    await ui.press({ key: 'xin-phep' })
    await ui.press({ key: 'ly-do-nuoc' })
    await io.clock.advance(MIN)
    expect(await ui.find(NUDGE)).toBeUndefined()
    await ui.unmount()
  })

  test(`${surface}: bong bóng lời nói — tầng 1 hàng đầu khi thầy đang làm: nghĩ · nói · đọc file · ghi file · chạy lệnh · tra cứu; hết lượt thì về thẻ bước; Lào dùng ຄູ`, LONG, async ($, on) => {
    const chunks: object[] = []
    on('turn.step', async function* (_$, e) {
      for (const c of chunks) yield c as never
      return { turnId: e.turnId, index: e.index, answer: '', toolUses: [], stopReason: 'end_turn', usage: null } as never
    })
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ board: { title: 'Bảng nhỏ', lines: ['một'] } }) }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const working = { ...BAND, props: { ...BAND.props, isWorking: true } }
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    await ui.unmount()
    const bub = await $.ui.mount({ plugin: 'lop-hoc', surface, ...working } as never)
    const d = $ as unknown as { turn: { start: (e: object) => Promise<unknown>; step: (e: object) => AsyncIterable<unknown>; complete: (e: object) => Promise<unknown> } }
    const run = async (cs: object[]) => {
      chunks.length = 0
      chunks.push(...cs)
      for await (const _ of d.turn.step({ turnId: 'bb', index: 0, model: 'claude-opus-5-5', messageCount: 1 })) void _
    }
    await d.turn.start({ text: '', turnId: 'bb' })
    // Chưa có khối nào: "đang làm việc…"; thẻ bước và nút Xong ẩn.
    expect(await bub.find({ text: 'Cô đang làm việc…' })).toBeDefined()
    expect(await bub.find({ key: 'xong' })).toBeUndefined()
    expect(await bub.find({ text: /^Bước 1\/8/ })).toBeUndefined()
    const cases: [object[], string][] = [
      [[{ kind: 'thinking', index: 0, text: 'x' }], 'Cô đang nghĩ cách làm…'],
      [[{ kind: 'text', index: 1, text: 'Chào' }], 'Cô đang nói với bạn…'],
      [[{ kind: 'tool', index: 2, id: 't1', name: 'Read' }], 'Cô đang đọc file…'],
      [[{ kind: 'tool', index: 2, id: 't2', name: 'Write' }], 'Cô đang ghi file…'],
      [[{ kind: 'tool', index: 2, id: 't3', name: 'Bash' }], 'Cô đang chạy một lệnh trên máy…'],
      [[{ kind: 'tool', index: 2, id: 't4', name: 'WebSearch' }], 'Cô đang tra cứu…'],
      [[{ kind: 'tool', index: 2, id: 't5', name: 'mcp__a__b' }], 'Cô đang làm việc…'],
    ]
    for (const [cs, text] of cases) {
      await run(cs)
      expect(await bub.find({ text })).toBeDefined()
    }
    // Bong bóng là hàng đầu của tầng 1 (trước hình), thẻ bước ẩn.
    await run([{ kind: 'tool', index: 0, id: 't9', name: 'Read' }])
    const texts = (await bub.findAll({ type: 'Text' })).map(x => x.text)
    expect(texts.indexOf('Cô đang đọc file…')).toBeGreaterThanOrEqual(0)
    expect(texts.indexOf('Cô đang đọc file…')).toBeLessThan(texts.indexOf('Bảng nhỏ'))
    await bub.unmount()
    // Hết lượt: bong bóng xoá, thẻ bước trở lại.
    await d.turn.complete({ answer: '', durationMs: 0, isAborted: false, turnId: 'bb', reason: 'answer' })
    const idle = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    expect(await idle.find({ text: /đang (đọc|làm việc)/ })).toBeUndefined()
    expect(await idle.find({ text: 'Bước 1/8 · Tham quan lớp học' })).toBeDefined()
    // Ngoài lượt chạy mà vẫn "isWorking" (props của engine): quay về "đang làm việc…".
    await idle.unmount()
    expect(io.sent.length).toBe(1)
  })

  test(`${surface}: bong bóng lời nói — lớp tiếng Lào dùng ຄູ; suy nghĩ vẫn là một dòng của thầy`, LONG, async ($, on) => {
    on('turn.step', async function* (_$, e) {
      yield { kind: 'thinking', index: 0, text: 'Tôi nghĩ' } as never
      yield { kind: 'tool', index: 1, id: 'x', name: 'Bash' } as never
      return { turnId: e.turnId, index: e.index, answer: '', toolUses: [], stopReason: 'end_turn', usage: null } as never
    })
    classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'lang-lo' })
    await ui.press({ key: 'enter' })
    await ui.unmount()
    const d = $ as unknown as { turn: { start: (e: object) => Promise<unknown>; step: (e: object) => AsyncIterable<{ kind: string; text?: string }> } }
    await d.turn.start({ text: '', turnId: 'lo' })
    const out: { kind: string; text?: string }[] = []
    for await (const c of d.turn.step({ turnId: 'lo', index: 0, model: 'claude-opus-5-5', messageCount: 1 })) out.push(c)
    expect(out[0]?.text).toBe('ຄູກຳລັງຄິດ…')
    const w = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND, props: { ...BAND.props, isWorking: true } } as never)
    expect(await w.find({ text: STR.lo.bubble('run', 'ຄູ') })).toBeDefined()
    expect(STR.lo.bubble('run', 'ຄູ')).toMatch(/^ຄູ/)
    await w.unmount()
  })

  test(`${surface}: giao diện sáng — hàng cài đặt theme chứa "light" thì bục dùng bảng màu sáng; đọc lại mỗi 30 giây; không đọc được thì tối`, LONG, async ($, on) => {
    let theme: unknown = 'light'
    let boom = false
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ board: { title: 'Bảng nhỏ', lines: ['một'] }, help_needed: true }) })
    on('config.list', async () => {
      if (boom) return { deny: 'không đọc được' } as never
      return { value: [{ key: 'verbose', label: 'Verbose', kind: 'boolean', value: true }, { key: 'theme', label: 'Theme', kind: 'choice', value: theme }] } as never
    })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    const bg = async () => (await ui.findAll({ type: 'Box' })).map(b => b.props.backgroundColor).find(c => c === '#EAF4EC' || c === '#123F1E')
    expect(await bg()).toBe('#EAF4EC') // màn Thiết lập đã sáng
    await ui.press({ key: 'enter' })
    expect(await bg()).toBe('#EAF4EC')
    const board = await ui.find({ type: 'Box', key: 'board-row' })
    expect(board?.props.borderColor).toBe('#008816')
    const head = await ui.find({ type: 'Text', text: 'Bước 1/8 · Tham quan lớp học' })
    expect(head?.props.color).toBe('#006D11')
    const why = await ui.find({ type: 'Text', text: /^để / })
    expect(why?.props.color).toBe('#14301B')
    const help = await ui.find({ type: 'Text', text: /Đang cần người hỗ trợ/ })
    expect(help?.props.color).toBe('#14301B')
    // Đổi sang tối: lần đọc kế tiếp (≤ 30 giây) đổi bảng màu.
    theme = 'dark'
    await io.clock.advance(35 * SEC)
    expect(await bg()).toBe('#123F1E')
    expect((await ui.find({ type: 'Text', text: 'Bước 1/8 · Tham quan lớp học' }))?.props.color).toBe('#FFEA00')
    // Lại sáng; rồi không đọc được: tối.
    theme = 'light-daltonized'
    await io.clock.advance(35 * SEC)
    expect(await bg()).toBe('#EAF4EC')
    boom = true
    await io.clock.advance(35 * SEC)
    expect(await bg()).toBe('#123F1E')
    await ui.unmount()
  })

  test(`${surface}: không có hàng theme hoặc không có bộ đọc cài đặt → bảng màu tối như 0.12`, LONG, async ($, on) => {
    classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
    on('config.list', async () => ({ value: [{ key: 'verbose', label: 'Verbose', kind: 'boolean', value: true }] }) as never)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect((await ui.findAll({ type: 'Box' })).some(b => b.props.backgroundColor === '#123F1E')).toBe(true)
    expect((await ui.findAll({ type: 'Box' })).some(b => b.props.backgroundColor === '#EAF4EC')).toBe(false)
    await ui.unmount()
  })

  test(`${surface}: thứ tự ba tầng — Bypass (nếu có) → tầng 1 (thẻ bước, nút) → tầng 2 (hình) → tầng 3 (thanh bước, Giơ tay · Xin phép · ⋯)`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ board: { title: 'Bảng nhỏ', lines: ['một dòng'] }, stars: 2, help_needed: true }) }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const bar = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'SessionMode', props: { modes: ['Bypass permissions'] } } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await io.clock.advance(3 * SEC)
    await ui.press({ key: 'enter' })
    const order = (await ui.findAll({})).map(x => (x.type === 'Button' ? `k:${x.key}` : x.type === 'Text' ? `t:${x.text}` : ''))
    const at = (m: string | RegExp) => order.findIndex(o => (typeof m === 'string' ? o === m : m.test(o)))
    const idx = [at(/^t:.*Bypass permissions/), at('t:Bước 1/8 · Tham quan lớp học'), at('k:xong'), at('k:goi-y-buoc'), at('k:nho-ho-tro'), at('t:Bảng nhỏ'), at('t:một dòng'), at('k:gio-tay'), at('k:xin-phep'), at('k:more')]
    expect(idx.every(i => i >= 0)).toBe(true)
    expect([...idx].sort((a, b) => a - b)).toEqual(idx)
    await bar.unmount()
    await ui.unmount()
  })

  test(`${surface}: hình thu thành "Xem hình" khi tầng 1 có lựa chọn; bấm xem được và ẩn lại; giáo viên ghi lại state thì thu lại`, LONG, async ($, on) => {
    const choices = { id: 'kiem', prompt: 'Ba dòng khớp hay lệch?', options: [{ label: 'Khớp' }, { label: 'Có chỗ lệch' }], default: 0 }
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ step: { id: '4' }, choices, board: { title: 'Bảng nhỏ', lines: ['một'] } }) }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    // Lựa chọn nằm trong tầng 1, ngay dưới thẻ bước, trước nút Xong.
    const order = (await ui.findAll({})).map(x => (x.type === 'Button' ? `k:${x.key}` : x.type === 'Text' ? `t:${x.text}` : ''))
    expect(order.indexOf('t:Bước 5/8 · Tự kiểm')).toBeLessThan(order.indexOf('k:choice-0'))
    expect(order.indexOf('k:choice-1')).toBeLessThan(order.indexOf('k:xong'))
    expect(await ui.find({ text: 'Bảng nhỏ' })).toBeUndefined()
    expect((await ui.find({ key: 'xem-hinh' }))?.props.label).toBe('Xem hình')
    await ui.press({ key: 'xem-hinh' })
    expect(await ui.find({ text: 'Bảng nhỏ' })).toBeDefined()
    expect((await ui.find({ key: 'xem-hinh' }))?.props.label).toBe('Ẩn hình')
    await ui.press({ key: 'choice-0' })
    expect(io.sent[io.sent.length - 1]).toBe('[Lớp học] Chọn · kiem · Khớp')
    // Học viên đã mở hình thì giữ mở (kể cả khi chọn xong); bấm "Ẩn hình" thì đóng.
    expect(await ui.find({ text: 'Bảng nhỏ' })).toBeDefined()
    await ui.press({ key: 'xem-hinh' })
    expect(await ui.find({ text: 'Bảng nhỏ' })).toBeUndefined()
    await ui.unmount()
  })

  test(`${surface}: bypass chip đứng trước tầng 1; trợ giúp (Soạn tin nhờ hỗ trợ) nằm trong tầng 1 khi help_needed`, LONG, async ($, on) => {
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({ help_needed: true }) })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const bar = await $.ui.mount({ plugin: 'lop-hoc', surface, component: 'SessionMode', props: { modes: ['Bypass permissions'] } } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await io.clock.advance(3 * SEC)
    await ui.press({ key: 'enter' })
    const chip = await ui.find({ type: 'Text', text: /⚠ Bypass permissions/ })
    expect(chip?.props.backgroundColor).toBe('#FF8A80')
    expect(await ui.find({ key: 'nho-ho-tro' })).toBeDefined()
    await bar.unmount()
    await ui.unmount()
  })
}

// ── v0.13: góp ý — thầy ghi, bục gửi lên Drive người phụ trách ─────────────────────
test('góp ý: đọc bản thầy ghi và cấu hình nơi nhận; sai thì bỏ', async () => {
  expect(feedbackOf({ id: 'v1-chot', loai: 'chot-vong', muc: 'lon', thay_danh_gia: 'Bước 3 học viên lúng túng', de_xuat: 'Thêm ảnh' }))
    .toEqual({ id: 'v1-chot', loai: 'chot-vong', muc: 'lon', thay_danh_gia: 'Bước 3 học viên lúng túng', de_xuat: 'Thêm ảnh' })
  expect(feedbackOf({ id: 'x', thay_danh_gia: 'ok', loai: 'la', muc: 'la' })).toEqual({ id: 'x', loai: 'gop-y', muc: 'gop-y', thay_danh_gia: 'ok' })
  expect(feedbackOf({ id: 'x' })).toBeNull()
  expect(feedbackOf({ thay_danh_gia: 'ok' })).toBeNull()
  expect(feedbackConfigOf({ url: 'https://script.google.com/macros/s/abc/exec', token: 't1' })).toEqual({ url: 'https://script.google.com/macros/s/abc/exec', token: 't1' })
  expect(feedbackConfigOf({ url: 'http://x', token: 't1' })).toBeNull()
  expect(feedbackConfigOf({ url: 'https://x' })).toBeNull()
  const body = JSON.parse(feedbackBody({ id: 'a', loai: 'gop-y', muc: 'nho', thay_danh_gia: 'tốt' }, { token: 't', hoc_vien: 'Laty', ngon_ngu: 'lo', giao_vien: 'co', gui_luc: '2026-10-20T03:00:00.000Z' }))
  expect(feedbackDelivered({ status: 200, ok: true, text: '{"ok":true}', headers: {} })).toBe(true)
  expect(feedbackDelivered({ status: 200, ok: true, text: '{"ok":false,"error":"token"}', headers: {} })).toBe(false)
  expect(feedbackDelivered({ status: 302, ok: false, text: '', headers: { location: 'https://script.googleusercontent.com/macros/echo?x=1' } })).toBe(true)
  expect(feedbackDelivered({ status: 302, ok: false, text: '', headers: { location: 'https://evil.example/' } })).toBe(false)
  expect(feedbackDelivered({ status: 500, ok: false, text: '', headers: {} })).toBe(false)
  expect(body).toEqual({ token: 't', ban: CLASS_VERSION, hoc_vien: 'Laty', ngon_ngu: 'lo', giao_vien: 'co', gui_luc: '2026-10-20T03:00:00.000Z', id: 'a', loai: 'gop-y', muc: 'nho', thay_danh_gia: 'tốt' })
})

test('desktop: thầy ghi góp ý → bục gửi một lần kèm tên học viên đã chọn, báo học viên; không có cấu hình thì không gửi', LONG, async ($, on) => {
  const files: Record<string, string> = {
    'CLAUDE.md': '# Lớp học NNC',
    '.claude/phan-hoi.json': JSON.stringify({ url: 'https://script.google.com/macros/s/abc/exec', token: 'tk' }),
  }
  const io = classroom(on, files)
  const posts: { url: string; body: string }[] = []
  on('http.fetch', async (_$, e) => {
    const ev = e as unknown as { url: string; init?: { body?: string } }
    posts.push({ url: ev.url, body: ev.init?.body ?? '' })
    return { value: { status: 200, ok: true, headers: {}, text: '{"ok":true}' } } as never
  })
  await $.session.start({ cwd: 'D:/sandbox', surface: 'desktop', isInteractive: true } as never)
  const ui = await $.ui.mount({ plugin: 'lop-hoc', surface: 'desktop', ...BAND } as never)
  await ui.input({ key: 'addr-text', text: 'Laty' })
  await ui.press({ key: 'enter' })
  files['.lop-hoc/state.json'] = v7({ feedback: { id: 'v1-chot', loai: 'chot-vong', muc: 'lon', thay_danh_gia: 'Bước 3: Laty chưa tìm thấy chế độ quyền', de_xuat: 'Ảnh phóng to' } })
  await teacherTalks($ as never)
  await io.clock.advance(10 * SEC)
  expect(posts).toHaveLength(1)
  expect(posts[0].url).toBe('https://script.google.com/macros/s/abc/exec')
  const b = JSON.parse(posts[0].body)
  expect(b.token).toBe('tk')
  expect(b.hoc_vien).toBe('Laty')
  expect(b.id).toBe('v1-chot')
  expect(b.ban).toBe(CLASS_VERSION)
  expect(io.toasts.some(x => /đã gửi góp ý/.test(x))).toBe(true)
  // Cùng id: không gửi lại.
  await teacherTalks($ as never)
  await io.clock.advance(60 * SEC)
  expect(posts).toHaveLength(1)
  // Bỏ cấu hình: id mới cũng không gửi.
  delete files['.claude/phan-hoi.json']
  files['.lop-hoc/state.json'] = v7({ feedback: { id: 'v1-nghi', loai: 'xin-nghi', muc: 'nho', thay_danh_gia: 'Nghỉ giữa bước 4' } })
  await teacherTalks($ as never)
  await io.clock.advance(60 * SEC)
  expect(posts).toHaveLength(1)
  await ui.unmount()
})

test('desktop: ⋯ → Góp ý cho lớp: học viên viết, lời đến thầy như tin của học viên', LONG, async ($, on) => {
  const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v7({}) })
  await $.session.start({ cwd: 'D:/sandbox', surface: 'desktop', isInteractive: true } as never)
  const ui = await $.ui.mount({ plugin: 'lop-hoc', surface: 'desktop', ...BAND } as never)
  await ui.press({ key: 'enter' })
  await ui.press({ key: 'more' })
  await ui.press({ key: 'gop-y' })
  expect(await ui.find({ key: 'gop-y-o' })).toBeDefined()
  await ui.input({ key: 'gop-y-o', text: 'Bước chế độ quyền hơi khó tìm' })
  expect(io.sent).toContain('[Lớp học] Góp ý: Bước chế độ quyền hơi khó tìm')
  expect(await ui.find({ key: 'gop-y-o' })).toBeUndefined()
  await ui.unmount()
})
