import { test, expect, mock } from 'claude-code/testing'
import type { On } from 'claude-code'
import { challengeLeft } from '../hooks/register'

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
}

function classroom(on: On, files: Record<string, string>, store: Record<string, unknown> = {}): Io {
  const io: Io = { sent: [], filled: [], toasts: [], writes: [], aborted: [], box: { text: '' }, clock: mock.clock(on, { now: T0 }), onAbort: () => {} }
  mock.store(on, store)
  on('session.cwd', async () => ({ value: 'D:/sandbox' }) as never)
  on('session.start', async (_$, e) => ({ cwd: e.cwd }))
  // Engine giả: nơi plugin nhường (next) vẽ một Box có key "engine" — tham chiếu hộp gốc.
  on('ui.render', async ($, e) => {
    if (e.component === 'AskUserQuestion') return { type: 'engine', ref: 0 } as never
    const { Box } = $.ui.resolve(e as never) as { Box: (p: object) => never }
    return <Box key="engine" />
  })
  const rel = (p: string) => p.split('\\').join('/')
  const find = (p: string) => Object.keys(files).find(k => rel(p) === k || rel(p).endsWith('/' + k))
  const isDir = (p: string) => Object.keys(files).some(k => k.includes('/') && rel(p).endsWith('/' + k.split('/')[0]))
  on('fs.exists', async (_$, e) => ({ value: find(e.path) !== undefined || isDir(e.path) }))
  on('fs.read', async (_$, e) => {
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
  props: { hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 100 },
} as const

const cues = (io: Io, s: string) => io.sent.filter(t => t === `[Giáo án] ${s}`).length

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
    expect(io.sent).toContain('[Giáo án] Mở lớp · giáo viên thay')
    expect(await ui.find({ text: /Phần 0 · Vào lớp/ })).toBeDefined()
    for (const key of ['gio-tay', 'xin-phep', 'xin-nghi', 'phieu']) expect(await ui.find({ key })).toBeDefined()
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
    expect(io.sent).toContain('[Giáo án] Mở lớp · giáo viên co · hạn mức 5 giờ 72% · tuần 22%')
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
    expect(io.sent).toEqual(['[Giáo án] Mở lớp · giáo viên co'])
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
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC' })
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
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': STATE2 })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(await ui.find({ text: /Phần 2 · Việc thật của tôi/ })).toBeDefined()
    expect(await ui.find({ text: /Lượt của bạn · Bấm Giao việc, điền 4 ý/ })).toBeDefined()
    expect(await ui.find({ text: /✓ Đọc file/ })).toBeDefined()
    expect(await ui.find({ text: /○ Tổng hợp/ })).toBeDefined()
    expect(await ui.find({ text: /Đang cần người hỗ trợ/ })).toBeDefined()
    expect(await ui.findAll({ type: 'Svg' })).toHaveLength(surface === 'desktop' ? 1 : 0)
    await noForbiddenWords(ui as never)
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
    expect(await ui.findAll({ type: 'Svg' })).toHaveLength(surface === 'desktop' ? 3 : 0)
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
    expect(await ui.find({ text: /Cô đọc bang-tinh-mau.xlsx · không sửa gì/ })).toBeDefined()
    await ui.unmount()
  })

  test(`${surface}: state lop-hoc/1 cũ vẫn đọc được, không vỡ`, LONG, async ($, on) => {
    const v1 = JSON.stringify({ schema: 'lop-hoc/1', status: 'active', stage: 3, next_action: 'Tạo bản nháp biên bản', result_parts: [{ label: 'Bản nháp', done: false }] })
    classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v1 })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    expect(await ui.find({ text: /Lượt của bạn · Tạo bản nháp biên bản/ })).toBeDefined()
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

  test(`${surface}: phần 0 đứng yên quá 8 phút thì nhắc giáo viên kiểm phần học một lần; phần 2 dài không nhắc`, LONG, async ($, on) => {
    const files: Record<string, string> = { 'CLAUDE.md': '# Lớp học NNC' }
    const io = classroom(on, files)
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    await ui.press({ key: 'enter' })
    await run($ as never, io, 7 * MIN)
    expect(io.sent.filter(x => x.includes('Kiểm phần học'))).toHaveLength(0)
    await run($ as never, io, 2 * MIN)
    expect(io.sent.filter(x => x.includes('Kiểm phần học'))).toEqual(['[Giáo án] Kiểm phần học · phần 0 · 8 phút'])
    files['.lop-hoc/state.json'] = v7({})
    io.box.text = 'vâng'
    await io.clock.advance(10 * SEC)
    io.box.text = ''
    await run($ as never, io, 40 * MIN)
    expect(io.sent.filter(x => x.includes('Kiểm phần học'))).toHaveLength(1)
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
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': v6({ activity: { kind: 'game:doan-xem', started_at: iso(T0) } }) })
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
    expect(await ui.findAll({ type: 'Svg' })).toHaveLength(surface === 'desktop' ? 2 : 0)
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

  test(`${surface}: dải chật thì nút một chạm lên đầu, bỏ dòng phụ; không có từ kỹ thuật`, LONG, async ($, on) => {
    const st = v6({ one_touch: ONE, stars: 2, challenge: { title: 'Thử 60 giây', seconds: 60, started_at: iso(T0) }, gift_box: true, badges_new: [BADGE1], destination: 'Bảng tổng hợp theo kênh' })
    const io = classroom(on, { 'CLAUDE.md': '# Lớp học NNC', '.lop-hoc/state.json': st })
    await $.session.start({ cwd: 'D:/sandbox', surface, isInteractive: true } as never)
    const roomy = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND, props: { ...BAND.props, maxRows: 80 } } as never)
    await roomy.press({ key: 'enter' })
    expect(await roomy.find({ text: /Đích: Bảng tổng hợp theo kênh/ })).toBeDefined()
    await roomy.unmount()
    const ui = await $.ui.mount({ plugin: 'lop-hoc', surface, ...BAND } as never)
    expect(await ui.find({ text: /Đích:/ })).toBeUndefined()
    expect(await ui.find({ key: 'one-touch' })).toBeDefined()
    expect(await ui.find({ key: 'hop-qua' })).toBeDefined()
    expect(await ui.find({ key: 'gio-tay' })).toBeDefined()
    await noForbiddenWords(ui as never)
    expect(io.toasts.some(t => FORBIDDEN.test(t))).toBe(false)
    await ui.unmount()
  })
}

test('thử thách thiếu giờ bắt đầu: mod tự đóng dấu lúc thấy lần đầu, đếm lùi từ đó', async () => {
  const c = { title: 'Tìm 3 dòng lỗi — kiểm đóng dấu', seconds: 60, started_at: '' }
  const t0 = 1_800_000_000_000
  expect(challengeLeft(c, t0)?.leftMs).toBe(60_000)
  expect(challengeLeft(c, t0 + 20_000)?.leftMs).toBe(40_000)
  expect(challengeLeft(c, t0 + 61_000)?.leftMs).toBe(0)
  const future = { title: 'Giờ ghi sai ở tương lai', seconds: 30, started_at: new Date(t0 + 3_600_000).toISOString() }
  expect(challengeLeft(future, t0)?.leftMs).toBe(30_000)
})
