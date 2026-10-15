import { atom, read, update } from 'claude-code'
import type { Register, EngineInterface, RenderChildren } from 'claude-code'

import type {
  ActivityTrack,
  AskOpen,
  BadgeEntry,
  BandMode,
  DriveId,
  GiftPhase,
  Lesson,
  LessonMinutes,
  LessonActivity,
  LessonBadge,
  LessonChallenge,
  LessonPart,
  LessonSkill,
  LessonState,
  LiveState,
  OneTouch,
  PanelKind,
  PlanSegment,
  TeacherKindId,
  UsageInfo,
} from '../types'
import type { BadgeRef, Emotion, TeacherKind, TeacherPresence } from './art'
import {
  DRIVE_COLOR,
  TEACHERS,
  badgeShelfSvg,
  challengeRingSvg,
  giftBoxSvg,
  isEmotion,
  isTeacherKind,
  segmentClockSvg,
  starRowSvg,
  teacherAvatarSvg,
  teacherPodiumSvg,
  usageTimelineSvg,
  weekResetSvg,
} from './art'

// Lớp học NNC v0.6 — buổi học có giáo viên đứng lớp, chạy theo giờ.
//   Bục giảng (dải trên ô nhập, nền bảng lớp): chọn thầy/cô và thời lượng → Vào lớp; giáo viên trên bục
//     với cảm xúc; tên phần + màu động lực + vòng giờ; "Lượt của bạn"; nút Giơ tay · Xin phép · Xin nghỉ.
//   Mod giữ đồng hồ và giáo án (hợp đồng §4), gửi tín hiệu "[Giáo án] …" cho giáo viên khi giáo viên
//     rảnh và ô nhập trống; vẽ lại các tín hiệu đó thành dòng chia phần hoặc ẩn hẳn.
//   Câu hỏi/đố dùng hộp câu hỏi gốc (AskUserQuestion); mod chỉ thêm một dòng tiêu đề lớp học.
// v0.6 (hợp đồng §8): nút một chạm (điền sẵn ô nhập), đổi kiểu tương tác sau 4 phút, thử thách có giờ,
//   sao, huy hiệu (mod chép vào .lop-hoc/huy-hieu.json), hộp quà.
// Mod chỉ ĐỌC .lop-hoc/state.json (giáo viên ghi). Hộp xin quyền, ô nhập và khung app là của Claude Code.

const PANE = 'lop-hoc'
const TITLE = 'Lớp học NNC'
const STATE = '.lop-hoc/state.json'
const BADGES = '.lop-hoc/huy-hieu.json'
const TAG = '[Lớp học] '
const CUE = '[Giáo án] '

const TICK_MS = 5_000
const ANSWER_MS = 60_000
const IDLE_MS = 60_000
const ROLLCALL_MS = 60_000
const CUE_GAP_MS = 20_000
const WARN_MS = 120_000
const ACTIVITY_MS = 4 * 60_000
const CHALLENGE_STALE_MS = 10 * 60_000
const CHEER_MS = 6_000
const GIFT_OPEN_MS = 4_000

// Bảng lớp: nền xanh đậm, chữ phấn.
const BOARD = '#123F1E'
const CHALK = '#F4F4EC'
const CHALK_DIM = '#B9D3BF'
const CHALK_Y = '#FFEA00'
const INK = '#1f2a1f'
const ALERT = '#FF8A80'

const rev = atom({ plugin: 'lop-hoc', key: 'rev' } as const, 0)
const isClassroom = atom({ plugin: 'lop-hoc', key: 'isClassroom' } as const, false)
const entered = atom({ plugin: 'lop-hoc', key: 'entered' } as const, false)
const teacherPick = atom({ plugin: 'lop-hoc', key: 'teacherPick' } as const, 'co' as TeacherKindId)
const minutesPick = atom({ plugin: 'lop-hoc', key: 'minutesPick' } as const, 30 as LessonMinutes)
const modeAtom = atom({ plugin: 'lop-hoc', key: 'mode' } as const, 'normal' as BandMode)
const usageAtom = atom({ plugin: 'lop-hoc', key: 'usage' } as const, null as UsageInfo | null)
const effortAtom = atom({ plugin: 'lop-hoc', key: 'effort' } as const, '')
const lessonAtom = atom({ plugin: 'lop-hoc', key: 'lesson' } as const, null as Lesson | null)
const workingAtom = atom({ plugin: 'lop-hoc', key: 'working' } as const, false)
const turnIdAtom = atom({ plugin: 'lop-hoc', key: 'turnId' } as const, '')
const askAtom = atom({ plugin: 'lop-hoc', key: 'ask' } as const, null as AskOpen | null)
const nowAtom = atom({ plugin: 'lop-hoc', key: 'now' } as const, 0)
// v0.6
const oneTouchUsed = atom({ plugin: 'lop-hoc', key: 'oneTouchUsed' } as const, '')
const liveAtom = atom({ plugin: 'lop-hoc', key: 'live' } as const, { activity: null, challenge: null, giftBox: false } as LiveState)
const activityTrack = atom({ plugin: 'lop-hoc', key: 'activityTrack' } as const, null as ActivityTrack | null)
const badgesAtom = atom({ plugin: 'lop-hoc', key: 'badges' } as const, [] as BadgeEntry[])
const cheerAtom = atom({ plugin: 'lop-hoc', key: 'cheer' } as const, false)
const giftAtom = atom({ plugin: 'lop-hoc', key: 'gift' } as const, 'closed' as GiftPhase)

// ── Giáo án (hợp đồng §4) ─────────────────────────────────────────────────────
const S0: PlanSegment = { id: '0', title: 'Vào lớp', minutes: 2, drive: 'ket-noi' }
const S1: PlanSegment = { id: '1', title: 'Nhập môn', minutes: 7, drive: 'D2' }
const S2: PlanSegment = { id: '2', title: 'Việc thật của tôi', minutes: 11, drive: 'D1' }
const S3: PlanSegment = { id: '3', title: 'Thử thách theo nhịp của bạn', minutes: 7, drive: 'D3' }
const S4: PlanSegment = { id: '4', title: 'Tổng kết', minutes: 3, drive: 'ket-noi' }
const BREAK: PlanSegment = { id: 'nghi', title: 'Nghỉ giải lao', minutes: 3, drive: 'ket-noi' }
const SEGMENTS_BY_ID: Record<string, PlanSegment> = { '0': S0, '1': S1, '2': S2, '3': S3, '4': S4, nghi: BREAK }

// 15 phút: bỏ phần 3, phần 1 còn 4, phần 2 còn 7, tổng kết 2 (= 15). 45 phút: phần 2 thành 16, phần 3 thành 14, nghỉ 3 phút sau phần 2.
export function lessonPlan(minutes: number): PlanSegment[] {
  if (minutes === 15) return [S0, { ...S1, minutes: 4 }, { ...S2, minutes: 7 }, { ...S4, minutes: 2 }]
  if (minutes === 45) return [S0, S1, { ...S2, minutes: 16 }, BREAK, { ...S3, minutes: 14 }, S4]
  return [S0, S1, S2, S3, S4]
}

const MIN = 60_000

// Thời gian buổi học đã trôi, không tính lúc tạm nghỉ / xin phép.
export function lessonElapsed(l: Pick<Lesson, 'startedAt' | 'shiftMs' | 'pausedAt'>, now: number): number {
  return Math.max(0, now - l.startedAt - l.shiftMs - (l.pausedAt != null ? now - l.pausedAt : 0))
}

function segmentIndexAt(plan: PlanSegment[], ms: number): number {
  let end = 0
  for (let i = 0; i < plan.length; i++) {
    end += (plan[i]?.minutes ?? 0) * MIN
    if (ms < end) return i
  }
  return plan.length
}

function segmentStart(plan: PlanSegment[], i: number): number {
  let s = 0
  for (let k = 0; k < i; k++) s += (plan[k]?.minutes ?? 0) * MIN
  return s
}

type DueCue = { key: string; text: string; patch: Partial<Lesson> }

// Tín hiệu giáo án đến hạn (nếu có). Chuyển phần trước, nhắc "còn 2 phút" sau; trễ thì bỏ nhắc cũ.
export function dueCue(l: Lesson, now: number): DueCue | null {
  const plan = lessonPlan(l.minutes)
  const el = lessonElapsed(l, now)
  const total = segmentStart(plan, plan.length)
  if (el >= total) return { key: 'end', text: 'Kết thúc buổi', patch: { over: 'ket-thuc', pausedAt: null, pause: null } }
  const cur = segmentIndexAt(plan, el)
  const s = plan[cur]
  if (!s) return null
  if (cur > l.announced) return { key: `seg-${s.id}`, text: `Bắt đầu phần ${s.id} · ${s.title} · ${s.minutes} phút`, patch: { announced: cur } }
  const left = segmentStart(plan, cur + 1) - el
  if (s.minutes >= 5 && left <= WARN_MS && left > 30_000) return { key: `warn-${s.id}`, text: `Còn 2 phút phần ${s.id}`, patch: {} }
  return null
}

// ── Đọc .lop-hoc/state.json (lop-hoc/2, vẫn nhận lop-hoc/1) ──────────────────
type ClassState = Omit<LessonState, 'schema'> & { schema: 'lop-hoc/2' | 'lop-hoc/1' }

const isObj = (v: unknown): v is Record<string, unknown> => typeof v === 'object' && v !== null && !Array.isArray(v)
const str = (v: unknown): string | undefined => (typeof v === 'string' ? v : undefined)
const isDrive = (v: unknown): v is DriveId => v === 'D1' || v === 'D2' || v === 'D3' || v === 'ket-noi'
const STATUSES = ['active', 'paused', 'done'] as const
const asStatus = (v: unknown) => (STATUSES as readonly unknown[]).includes(v) ? (v as (typeof STATUSES)[number]) : 'active'

function parts(v: unknown): LessonPart[] {
  if (!Array.isArray(v)) return []
  return v.filter(isObj).filter(p => typeof p.label === 'string').map(p => ({ label: String(p.label), done: p.done === true }))
}

// Chặng cũ 0–5 → phần mới.
function stageToSegment(stage: number, done: boolean): PlanSegment {
  if (done) return S4
  if (stage <= 0) return S1
  if (stage <= 3) return S2
  return S3
}

export function parseState(raw: unknown): ClassState | null {
  if (!isObj(raw)) return null
  const status = asStatus(raw.status)
  const common = {
    status,
    next_action: str(raw.next_action),
    destination: str(raw.destination),
    result_parts: parts(raw.result_parts),
    skills: parts(raw.skills) as LessonSkill[],
  }
  if (raw.schema === 'lop-hoc/1') {
    const stage = typeof raw.stage === 'number' ? Math.min(5, Math.max(0, Math.round(raw.stage))) : 0
    const seg = stageToSegment(stage, status === 'done')
    return { schema: 'lop-hoc/1', ...common, segment: { id: seg.id, title: seg.title, drive: seg.drive } }
  }
  if (raw.schema !== 'lop-hoc/2') return null
  const segRaw = isObj(raw.segment) ? raw.segment : null
  const segId = segRaw ? str(segRaw.id) : undefined
  const known = segId ? SEGMENTS_BY_ID[segId] : undefined
  const segment = segRaw && segId ? { id: segId, title: str(segRaw.title) ?? known?.title ?? '', drive: isDrive(segRaw.drive) ? segRaw.drive : (known?.drive ?? 'ket-noi') } : undefined
  const t = isObj(raw.teacher) ? raw.teacher : null
  const teacher = t ? { kind: isTeacherKind(t.kind) ? t.kind : undefined, name: str(t.name), emotion: isEmotion(t.emotion) ? t.emotion : undefined } : undefined
  const panel: PanelKind | null = raw.panel === 'usage' || raw.panel === 'claude' ? raw.panel : null
  return {
    schema: 'lop-hoc/2',
    ...common,
    segment,
    teacher,
    address: str(raw.address),
    help_needed: raw.help_needed === true,
    panel,
    one_touch: oneTouchOf(raw.one_touch),
    activity: activityOf(raw.activity),
    challenge: challengeOf(raw.challenge),
    stars: typeof raw.stars === 'number' && Number.isFinite(raw.stars) ? Math.min(99, Math.max(0, Math.round(raw.stars))) : undefined,
    badges_new: badgesOf(raw.badges_new),
    gift_box: raw.gift_box === true,
  }
}

// ── v0.6: các trường mới, đọc phòng thủ (sai kiểu thì coi như không có) ─────────
const nonEmpty = (v: unknown): string | undefined => (typeof v === 'string' && v.trim() ? v.trim() : undefined)
const isoMs = (v: string | undefined): number | null => {
  if (!v) return null
  const t = Date.parse(v)
  return Number.isNaN(t) ? null : t
}

function oneTouchOf(v: unknown): OneTouch | null {
  if (!isObj(v)) return null
  const label = nonEmpty(v.label)
  const text = nonEmpty(v.text)
  return label && text ? { label, text } : null
}

function activityOf(v: unknown): LessonActivity | null {
  if (!isObj(v)) return null
  const kind = nonEmpty(v.kind)
  return kind ? { kind, started_at: str(v.started_at) ?? '' } : null
}

function challengeOf(v: unknown): LessonChallenge | null {
  if (!isObj(v)) return null
  const title = nonEmpty(v.title)
  const started = str(v.started_at)
  const seconds = typeof v.seconds === 'number' && Number.isFinite(v.seconds) ? Math.round(v.seconds) : 0
  if (!title || seconds <= 0) return null
  // Giáo viên thường không biết giờ hiện tại: thiếu hoặc sai started_at thì mod tự đóng dấu lúc thấy lần đầu.
  return { title, seconds: Math.min(seconds, 3600), started_at: isoMs(started) == null ? '' : (started ?? '') }
}

function badgesOf(v: unknown): LessonBadge[] {
  if (!Array.isArray(v)) return []
  const out: LessonBadge[] = []
  for (const b of v) {
    if (!isObj(b)) continue
    const id = nonEmpty(b.id)
    if (!id || out.some(x => x.id === id)) continue
    out.push({ id, label: nonEmpty(b.label) ?? id })
    if (out.length >= 20) break
  }
  return out
}

// Ngày theo Vientiane (UTC+7): YYYY-MM-DD.
export function vientianeDate(now: number): string {
  return new Date(now + 7 * 3600_000).toISOString().slice(0, 10)
}

// Gộp huy hiệu mới vào danh sách đã có, bỏ trùng theo id. `added` = những cái thật sự mới.
export function mergeBadges(have: BadgeEntry[], incoming: LessonBadge[], date: string): { badges: BadgeEntry[]; added: BadgeEntry[] } {
  const added: BadgeEntry[] = []
  for (const b of incoming) {
    if (have.some(x => x.id === b.id) || added.some(x => x.id === b.id)) continue
    added.push({ id: b.id, label: b.label, date })
  }
  return { badges: [...have, ...added], added }
}

export function parseBadgeFile(raw: unknown): BadgeEntry[] {
  if (!isObj(raw) || !Array.isArray(raw.badges)) return []
  const out: BadgeEntry[] = []
  for (const b of raw.badges) {
    if (!isObj(b)) continue
    const id = nonEmpty(b.id)
    if (!id || out.some(x => x.id === id)) continue
    out.push({ id, label: nonEmpty(b.label) ?? id, date: str(b.date) ?? '' })
  }
  return out
}

// Thử thách: còn bao lâu (ms), hoặc null khi đã hết giờ quá 10 phút (cũ, bỏ qua).
// Giờ bắt đầu do mod đóng dấu cho thử thách không có (hoặc có giờ sai) started_at. Mất khi nạp lại mod: đếm lại từ đầu.
const challengeStamps = new Map<string, number>()

export function challengeLeft(c: LessonChallenge | null | undefined, now: number): { leftMs: number; totalMs: number } | null {
  if (!c) return null
  let start = isoMs(c.started_at)
  // Giờ do giáo viên ghi ở tương lai quá 1 phút cũng coi như chưa có.
  if (start == null || start - now > 60_000) {
    const key = `${c.title}@${c.seconds}@${c.started_at}`
    const stamped = challengeStamps.get(key)
    if (stamped == null) challengeStamps.set(key, now)
    start = stamped ?? now
  }
  const totalMs = c.seconds * 1000
  const end = start + totalMs
  if (now - end > CHALLENGE_STALE_MS) return null
  return { leftMs: Math.min(totalMs, Math.max(0, end - now)), totalMs }
}

// Cỡ hình lấy từ thẻ <svg> gốc (hình do hooks/art.ts vẽ, cỡ có thể đổi theo nội dung).
function svgSize(src: string, w: number, h: number): { width: number; height: number } {
  const head = /<svg\b[^>]*>/.exec(src)?.[0] ?? ''
  const num = (re: RegExp) => {
    const m = re.exec(head)
    const v = m ? Number(m[1]) : NaN
    return Number.isFinite(v) && v > 0 ? v : null
  }
  return { width: num(/\swidth="([0-9.]+)"/) ?? w, height: num(/\sheight="([0-9.]+)"/) ?? h }
}

const activityKey = (a: LessonActivity) => `${a.kind}@${a.started_at}`
const challengeKey = (c: LessonChallenge) => `${c.title}@${c.started_at}@${c.seconds}`

// Theo dõi kiểu tương tác theo giờ buổi học (đồng hồ dừng khi nghỉ thì thời gian này cũng dừng).
// Lần đầu thấy: lùi về started_at nếu hợp lệ, nhưng không trước lúc vào lớp.
export function trackActivity(prev: ActivityTrack | null, a: LessonActivity | null, el: number, now: number): ActivityTrack | null {
  if (!a) return null
  const key = activityKey(a)
  if (prev && prev.key === key) return prev
  const start = isoMs(a.started_at)
  const back = start != null && start <= now ? Math.min(el, now - start) : 0
  return { key, fromEl: el - back }
}

async function loadState($: EngineInterface): Promise<ClassState | null> {
  try {
    if (!(await $.fs.exists(STATE))) return null
    const raw = await $.fs.read(STATE)
    return parseState(JSON.parse(typeof raw === 'string' ? raw : ''))
  } catch {
    return null
  }
}

// ── v0.6: nạp lại state sau mỗi lần giáo viên cập nhật; huy hiệu mới chép vào huy-hieu.json ──
let syncing: Promise<void> = Promise.resolve()
const toasted = new Set<string>()
let cheerTimer: { cancel: () => void } | null = null

function syncState($: EngineInterface): Promise<void> {
  syncing = syncing.then(() => syncBody($)).catch(() => undefined)
  return syncing
}

async function readBadgeFile($: EngineInterface): Promise<BadgeEntry[]> {
  try {
    if (!(await $.fs.exists(BADGES))) return []
    const raw = await $.fs.read(BADGES)
    return parseBadgeFile(JSON.parse(typeof raw === 'string' ? raw : ''))
  } catch {
    return []
  }
}

async function syncBody($: EngineInterface) {
  if (!(await read($, isClassroom))) return
  const s = await loadState($)
  const live: LiveState = { activity: s?.activity ?? null, challenge: s?.challenge ?? null, giftBox: s?.gift_box === true }
  await update($, liveAtom, () => live)
  if (!live.giftBox) await update($, giftAtom, g => (g === 'closed' ? g : 'closed'))

  const have = await readBadgeFile($)
  const now = await $.clock.now()
  const { badges, added } = mergeBadges(have, s?.badges_new ?? [], vientianeDate(now))
  if (added.length) {
    try {
      await $.fs.write(BADGES, JSON.stringify({ schema: 'lop-hoc/huy-hieu-1', badges }, null, 2) + '\n')
    } catch {}
  }
  await update($, badgesAtom, () => badges)
  const fresh = added.filter(b => !toasted.has(b.id))
  if (!fresh.length) return
  for (const b of fresh) {
    toasted.add(b.id)
    try {
      $.ui.toast(`Huy hiệu mới: ${b.label}`)
    } catch {}
  }
  // Giáo viên vui (hỉ) 6 giây trên bục.
  cheerTimer?.cancel()
  try {
    cheerTimer = $.clock.after(CHEER_MS, () => void update($, cheerAtom, () => false))
    await update($, cheerAtom, () => true)
  } catch {
    cheerTimer = null
  }
}

async function detectClassroom($: EngineInterface): Promise<boolean> {
  try {
    if (await $.fs.exists('.lop-hoc')) return true
    if (!(await $.fs.exists('CLAUDE.md'))) return false
    const md = await $.fs.read('CLAUDE.md')
    return typeof md === 'string' && (md.includes('Lớp học NNC') || md.includes('classroom-CLAUDE.md'))
  } catch {
    return false
  }
}

// ── Lời lớp học ────────────────────────────────────────────────────────────────
const teacherName = (k: TeacherKind) => TEACHERS.find(t => t.id === k)?.label ?? (k === 'thay' ? 'Thầy' : 'Cô')
const teacherLower = (k: TeacherKind) => teacherName(k).toLowerCase()
const cap = (s: string) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s)
const cut = (s: string | undefined, n: number) => (!s ? '' : s.length > n ? s.slice(0, n - 1) + '…' : s)
const baseName = (p: unknown) => (typeof p === 'string' ? (p.split(/[\\/]/).pop() ?? p) : '')
const mmss = (ms: number) => {
  const s = Math.max(0, Math.ceil(ms / 1000))
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

// Giờ theo Vientiane (UTC+7), không phụ thuộc múi giờ của môi trường mod.
export function resetTime(iso: string | undefined): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  const v = new Date(d.getTime() + 7 * 3600_000)
  return `${String(v.getUTCHours()).padStart(2, '0')}:${String(v.getUTCMinutes()).padStart(2, '0')}`
}
function resetDay(iso: string | undefined): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  const v = new Date(d.getTime() + 7 * 3600_000)
  return `${String(v.getUTCDate()).padStart(2, '0')}/${String(v.getUTCMonth() + 1).padStart(2, '0')} ${resetTime(iso)}`
}

// Lời giao việc ghép từ form 4 ý (người học tự bấm Enter để giao).
export function delegationPrompt(f: { goal: string; src: string; out: string; check: string }): string {
  return ['Giao việc —', `Mục tiêu: ${f.goal.trim()}`, `Nguồn: ${f.src.trim() || '(chưa có — dùng mẫu giả)'}`, `Đầu ra: ${f.out.trim() || '(giáo viên đề xuất)'}`, `Cách kiểm: ${f.check.trim() || '(giáo viên gợi ý, tôi tự kiểm)'}`].join('\n')
}

// Một câu dễ hiểu cho mỗi thao tác công cụ. null = để nguyên dòng gốc.
export function describeTool(tool: string, input: unknown): string | null {
  const i = (input ?? {}) as Record<string, unknown>
  const file = baseName(i.file_path ?? i.notebook_path ?? i.path)
  if (tool === 'Read') return `đọc ${file || 'một file'} · không sửa gì`
  if (tool === 'Glob' || tool === 'Grep') return 'tìm trong thư mục · không sửa gì'
  if (tool === 'Write') return `ghi ${file || 'một file'}`
  if (tool === 'Edit' || tool === 'NotebookEdit') return `sửa ${file || 'một file'}`
  if (tool === 'Bash' || tool === 'PowerShell') return 'chạy một lệnh trên máy'
  if (tool === 'WebFetch' || tool === 'WebSearch') return 'tra cứu trên mạng · không sửa gì'
  if (tool === 'Skill') return 'mở bài học'
  if (tool.startsWith('mcp__')) return 'dùng một công cụ kết nối'
  return null
}

// Lựa chọn mặc định của một câu hỏi gốc: phương án ghi "mặc định"/"đề xuất", nếu không thì phương án đầu.
export function defaultLabel(questions: unknown): string {
  const q = Array.isArray(questions) ? questions[0] : undefined
  const opts = isObj(q) && Array.isArray(q.options) ? q.options : []
  const labels = opts.map(o => (isObj(o) && typeof o.label === 'string' ? o.label : '')).filter(Boolean)
  return labels.find(l => /mặc định|đề xuất|recommended/i.test(l)) ?? labels[0] ?? 'phương án đầu'
}

const TIPS = [
  'mẹo: effort cao nghĩ kỹ hơn nhưng tốn usage hơn',
  'mẹo: context gần đầy thì mở phiên mới, kèm ghi chú tiếp tục',
  'mẹo: giao việc rõ 4 ý — mục tiêu, nguồn, đầu ra, cách kiểm',
  'mẹo: Claude xin quyền là để bạn quyết — đọc kỹ rồi hãy đồng ý',
  'mẹo: kết quả nghe hợp lý chưa phải bằng chứng — đối chiếu nguồn',
]

// ── Trạng thái của module (mất khi nạp lại; đồng hồ buổi học nằm trong $.state) ──
let turns = 0
let ticks = 0
let ticking = false
let draft = { goal: '', src: '', out: '', check: '' }
let formError = ''
// Hộp câu hỏi thấy ở nơi vẽ nhưng chưa qua tool.call (dự phòng).
let askSeen: { id: string; label: string } | null = null
const askDone = new Set<string>()
// Tiêu đề lớp cho mỗi lời giảng, giữ theo phần lúc lời đó được viết.
const headerById = new Map<string, string>()
// Bộ nhớ đệm để các nơi vẽ không phải đăng ký theo dõi đồng hồ.
let view: { teacher: TeacherKind; seg: PlanSegment | null } = { teacher: 'co', seg: null }

function announcedSeg(l: Lesson | null): PlanSegment | null {
  if (!l || l.over) return null
  return lessonPlan(l.minutes)[l.announced] ?? null
}

async function refreshUsage($: EngineInterface) {
  try {
    const model = await $.session.model()
    const u = await $.session.usage()
    const pick = (kind: string) => {
      const r = u.rateLimits.find(x => x.kind === kind)
      return r ? { percentUsed: r.percentUsed, resetsAt: r.resetsAt } : null
    }
    const info: UsageInfo = { model: String(model ?? ''), context: typeof u.context?.percent === 'number' ? u.context.percent : null, five: pick('five_hour'), week: pick('seven_day') }
    await update($, usageAtom, () => info)
  } catch {
    // Không đọc được thì để trống; không đoán số liệu.
  }
}

function claudeLine(u: UsageInfo | null, effort: string): string {
  if (!u) return ''
  const five = u.five ? `5 giờ ${Math.round(u.five.percentUsed)}%${resetTime(u.five.resetsAt) ? ` (reset ${resetTime(u.five.resetsAt)})` : ''}` : ''
  const week = u.week ? `tuần ${Math.round(u.week.percentUsed)}%${resetDay(u.week.resetsAt) ? ` (reset ${resetDay(u.week.resetsAt)})` : ''}` : ''
  return [u.model, effort ? `effort ${effort}` : '', u.context != null ? `context ${Math.round(u.context)}%` : '', five, week].filter(Boolean).join(' · ')
}

// ── Gửi tín hiệu ─────────────────────────────────────────────────────────────
// Hook prompt.submit của chính mod KHÔNG chạy cho tin mod tự gửi, nên mọi thay đổi trạng thái
// làm ở nơi bấm / nơi hẹn giờ, trước khi gửi.
function submitCue($: EngineInterface, text: string) {
  return $.prompt.submit({ text: CUE + text }).then(
    () => undefined,
    () => undefined,
  )
}

// Tín hiệu theo giờ: chỉ gửi một lần (khoá `key`).
async function sendKeyedCue($: EngineInterface, key: string, text: string, now: number, patch: Partial<Lesson>): Promise<boolean> {
  let claimed = false
  await update($, lessonAtom, l => {
    if (!l || l.sent.includes(key)) {
      claimed = false
      return l
    }
    claimed = true
    return { ...l, ...patch, sent: [...l.sent, key], lastCueAt: now }
  })
  if (claimed) void submitCue($, text)
  return claimed
}

// Tín hiệu do học viên bấm: gửi ngay (giáo viên đang làm thì chờ đến lượt).
async function sendPressCue($: EngineInterface, text: string, patch: Partial<Lesson> = {}) {
  const now = await $.clock.now()
  await update($, lessonAtom, l => (l ? { ...l, ...patch, lastCueAt: now, strikes: 0, rollCallAt: null, idleFrom: now } : l))
  await submitCue($, text)
}

// Học viên có mặt: xoá điểm danh, đếm lại từ đầu.
async function touch($: EngineInterface) {
  const now = await $.clock.now()
  await update($, lessonAtom, l => (l && !l.over && (l.strikes || l.rollCallAt != null || l.idleFrom !== now) ? { ...l, strikes: 0, rollCallAt: null, idleFrom: now } : l))
}

// Vào lại lớp sau tạm nghỉ / xin phép: dời các phần còn lại đúng bằng thời gian nghỉ.
async function resume($: EngineInterface): Promise<Lesson['pause']> {
  const now = await $.clock.now()
  let was: Lesson['pause'] = null
  await update($, lessonAtom, l => {
    if (!l || !l.pause || l.over) {
      was = null
      return l
    }
    was = l.pause
    return { ...l, pause: null, pauseNote: '', shiftMs: l.shiftMs + (now - (l.pausedAt ?? now)), pausedAt: null, strikes: 0, rollCallAt: null, idleFrom: now }
  })
  return was
}

async function abortTurn($: EngineInterface): Promise<boolean> {
  const turnId = await read($, turnIdAtom)
  if (!turnId) return false
  try {
    await $.turn.abort({ turnId })
    return true
  } catch {
    return false
  }
}

// Điểm danh hết hạn: lớp tạm nghỉ, báo giáo viên một lần, không gửi thêm tín hiệu nào.
async function goAbsent($: EngineInterface, now: number) {
  let claimed = false
  let n = 0
  await update($, lessonAtom, l => {
    if (!l || l.pause || l.over) {
      claimed = false
      return l
    }
    claimed = true
    n = l.absences + 1
    return { ...l, pause: 'absent' as const, pausedAt: now, rollCallAt: null, absences: n, lastCueAt: now, sent: [...l.sent, `vang-${n}`] }
  })
  if (!claimed) return
  // Hộp câu hỏi gốc còn mở thì đóng lượt đang chờ để giáo viên nhận được tin.
  const ask = await read($, askAtom)
  if (ask) {
    await update($, askAtom, a => (a && a.id === ask.id ? { ...a, handled: true } : a))
    await abortTurn($)
  }
  void submitCue($, 'Học viên vắng · tạm nghỉ')
}

// Hộp câu hỏi gốc để quá 60 giây.
async function answerTimeout($: EngineInterface, ask: AskOpen, now: number) {
  await update($, askAtom, a => (a && a.id === ask.id ? { ...a, handled: true } : a))
  let strikes = 0
  await update($, lessonAtom, l => {
    if (!l) return l
    strikes = l.strikes + 1
    return { ...l, strikes, idleFrom: now, rollCallAt: strikes >= 2 ? now : l.rollCallAt }
  })
  if (strikes >= 2) return // lần thứ hai liên tiếp: điểm danh trước, không chọn giúp
  try {
    $.ui.notice(ask.id, undefined)
  } catch {}
  // Mod không bấm được vào hộp gốc; đóng lượt đang chờ rồi báo giáo viên lựa chọn mặc định.
  if (await abortTurn($)) await sendKeyedCue($, `ask-${ask.id}`, `Hết hạn trả lời · chọn giúp ${ask.label}`, now, {})
}

async function tick($: EngineInterface) {
  if (ticking) return
  ticking = true
  try {
    await tickBody($)
  } catch {
    // Một nhịp lỗi không làm dừng đồng hồ.
  } finally {
    ticking = false
  }
}

async function tickBody($: EngineInterface) {
  if (!(await read($, isClassroom))) return
  const now = await $.clock.now()
  ticks += 1
  if (ticks % 6 === 0) void refreshUsage($)
  let l = await read($, lessonAtom)
  await persist($, l, now)
  if (!l || l.over) return
  await update($, nowAtom, () => now)
  view = { teacher: l.teacher, seg: announcedSeg(l) }
  // v0.6: kiểu tương tác đang dùng (giờ buổi học) và đồng hồ giây cho thử thách.
  const live = await read($, liveAtom)
  const el = lessonElapsed(l, now)
  const prevTrack = await read($, activityTrack)
  const track = trackActivity(prevTrack, live.activity, el, now)
  if (track !== prevTrack) await update($, activityTrack, () => track)
  const ch = challengeLeft(live.challenge, now)
  if (ch && ch.leftMs > 0 && !l.pause) startSecondClock($)
  const working = await read($, workingAtom)
  let ask = await read($, askAtom)
  if (!ask && askSeen && working && !askDone.has(askSeen.id)) {
    const seen = askSeen
    await update($, askAtom, () => ({ id: seen.id, openedAt: now, label: seen.label, handled: false }))
    ask = await read($, askAtom)
  }
  let box = ''
  try {
    box = (await $.prompt.read()).text.trim()
  } catch {}
  // Đang gõ = có mặt.
  if (box && !l.pause) {
    await touch($)
    l = (await read($, lessonAtom)) ?? l
  }

  // A. Câu hỏi gốc: đếm ngược 60 giây, hết hạn thì chọn giúp.
  //    Đang có thử thách chạy giờ thì tạm ngưng: hạn 60 giây tính lại từ lúc thử thách xong.
  if (ask && !ask.handled && ch && ch.leftMs > 0) {
    const a = ask
    await update($, askAtom, () => ({ ...a, openedAt: now }))
    ask = await read($, askAtom)
  }
  if (ask && !ask.handled && !l.pause && !(ch && ch.leftMs > 0)) {
    const left = ANSWER_MS - (now - ask.openedAt)
    if (left > 0) {
      try {
        $.ui.notice(ask.id, `${teacherName(l.teacher)} chọn giúp sau ${mmss(left)}`)
      } catch {}
    } else {
      await answerTimeout($, ask, now)
      return
    }
  }

  // B. Điểm danh hết 60 giây → lớp tạm nghỉ.
  if (l.rollCallAt != null && !l.pause && now - l.rollCallAt >= ROLLCALL_MS) {
    await goAbsent($, now)
    return
  }

  // C. Ngồi im 60 giây ở lượt của học viên = một lần không tương tác.
  if (!l.pause && l.rollCallAt == null && !working && !ask && !box && now - l.idleFrom >= IDLE_MS) {
    await update($, lessonAtom, x => {
      if (!x) return x
      const strikes = x.strikes + 1
      return { ...x, strikes, idleFrom: now, rollCallAt: strikes >= 2 ? now : x.rollCallAt }
    })
    return
  }

  // D. Giáo án theo giờ: chỉ khi giáo viên rảnh, ô nhập trống, lớp không nghỉ, cách tín hiệu trước ≥ 20 giây.
  if (l.pause || l.rollCallAt != null || working || ask || box || now - l.lastCueAt < CUE_GAP_MS) return
  const due = dueCue(l, now)
  if (due && (await sendKeyedCue($, due.key, due.text, now, due.patch))) {
    const after = await read($, lessonAtom)
    view = { teacher: after?.teacher ?? view.teacher, seg: announcedSeg(after) }
    return
  }
  // v0.6: hết giờ thử thách (một lần, bỏ thử thách cũ quá 10 phút).
  if (live.challenge && ch && ch.leftMs <= 0) {
    if (await sendKeyedCue($, `ch-${challengeKey(live.challenge)}`, `Hết giờ thử thách · ${live.challenge.title}`, now, {})) return
  }
  // v0.6: cùng một kiểu tương tác quá 4 phút giờ học → nhắc giáo viên đổi kiểu (một lần).
  if (live.activity && track && el - track.fromEl > ACTIVITY_MS) {
    const n = Math.floor((el - track.fromEl) / MIN)
    await sendKeyedCue($, `act-${track.key}`, `Đổi kiểu tương tác · ${live.activity.kind} · ${n} phút`, now, {})
  }
}

// Đồng hồ giây khi có thử thách đang chạy: vòng đếm ngược nhảy từng giây; về 0 thì xét gửi tín hiệu ngay.
let secondClock: { cancel: () => void } | null = null
function startSecondClock($: EngineInterface) {
  if (secondClock) return
  try {
    secondClock = $.clock.every(1000, () => void secondTick($))
  } catch {
    secondClock = null
  }
}

async function secondTick($: EngineInterface) {
  try {
    const now = await $.clock.now()
    const l = await read($, lessonAtom)
    const ch = challengeLeft((await read($, liveAtom)).challenge, now)
    if (!l || l.over || l.pause || !ch || ch.leftMs <= 0) {
      secondClock?.cancel()
      secondClock = null
      if (ch && ch.leftMs <= 0) void tick($)
      if (!l || l.over || l.pause || !ch) return
    }
    await update($, nowAtom, () => now)
  } catch {}
}

// Đồng hồ buổi học cũng lưu vào $.store (theo thư mục lớp) để mở lại app vẫn học tiếp được.
let savedJson = ''
async function storeKey($: EngineInterface): Promise<string | null> {
  try {
    const cwd = await $.session.cwd()
    return cwd ? `lesson:${cwd.split(String.fromCharCode(92)).join('/').toLowerCase()}` : null
  } catch {
    return null
  }
}

async function persist($: EngineInterface, l: Lesson | null, now: number) {
  if (!l) return
  const json = JSON.stringify(l)
  if (json === savedJson && ticks % 6 !== 0) return
  const key = await storeKey($)
  if (!key) return
  try {
    await $.store.set(key, { lesson: l, savedAt: now })
    savedJson = json
  } catch {}
}

// Mở lại sau khi tắt app (trong 3 giờ): lớp ở trạng thái tạm nghỉ, bấm Có mặt để học tiếp.
async function restoreLesson($: EngineInterface) {
  if (await read($, lessonAtom)) return
  const key = await storeKey($)
  if (!key) return
  try {
    const saved = await $.store.get(key)
    if (!isObj(saved) || !isObj(saved.lesson) || typeof saved.savedAt !== 'number') return
    const l = saved.lesson as unknown as Lesson
    const now = await $.clock.now()
    if (l.over || typeof l.startedAt !== 'number' || !Array.isArray(l.sent) || now - saved.savedAt > 3 * 3600_000) return
    if (l.minutes !== 15 && l.minutes !== 30 && l.minutes !== 45) return
    if (!isTeacherKind(l.teacher)) return
    const restored: Lesson = { ...l, pause: l.pause ?? 'absent', pausedAt: l.pausedAt ?? saved.savedAt, rollCallAt: null, strikes: 0 }
    await update($, lessonAtom, () => restored)
    await update($, entered, () => true)
  } catch {}
}

async function startLesson($: EngineInterface) {
  const now = await $.clock.now()
  const teacher = await read($, teacherPick)
  const minutes = await read($, minutesPick)
  const lesson: Lesson = {
    minutes,
    teacher,
    startedAt: now,
    shiftMs: 0,
    pausedAt: null,
    pause: null,
    pauseNote: '',
    over: null,
    announced: 0,
    sent: ['open'],
    lastCueAt: now,
    strikes: 0,
    idleFrom: now,
    rollCallAt: null,
    absences: 0,
  }
  await update($, lessonAtom, () => lesson)
  await update($, entered, () => true)
  await update($, modeAtom, () => 'normal')
  await update($, nowAtom, () => now)
  await update($, activityTrack, () => null)
  await update($, giftAtom, () => 'closed')
  view = { teacher, seg: S0 }
  try {
    await $.store.set('teacher', teacher)
    await $.store.set('minutes', minutes)
  } catch {}
  await submitCue($, `Mở buổi · ${minutes} phút · giáo viên ${teacher}`)
}

async function loadPrefs($: EngineInterface) {
  try {
    const t = await $.store.get('teacher')
    if (isTeacherKind(t)) await update($, teacherPick, () => t)
    const m = await $.store.get('minutes')
    if (m === 15 || m === 30 || m === 45) await update($, minutesPick, () => m)
  } catch {}
}

async function setup($: EngineInterface) {
  const ok = await detectClassroom($)
  await update($, isClassroom, () => ok)
  if (!ok) return false
  await loadPrefs($)
  await restoreLesson($)
  await syncState($)
  void refreshUsage($)
  return true
}

const PERSON_ORIGINS = new Set(['composer', 'bridge', 'sdk', 'unclassified'])

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    if (await setup($)) {
      try {
        await $.command.register({ name: 'lop-hoc', description: 'Mở bảng tóm tắt Lớp học NNC bên cạnh' })
      } catch {}
      $.clock.every(TICK_MS, () => void tick($))
    }
    return next(e)
  })

  // /clear, /resume, /branch xoá $.state: nhận lại lớp học và lựa chọn đã lưu.
  on('classic.SessionStart', { source: ['clear', 'resume', 'fork'] }, async ($, e, next) => {
    await setup($)
    return next(e)
  }).catch(($, e, next) => next(e))

  on('command.run', { command: 'lop-hoc' }, async $ => {
    await $.ui.open({ id: PANE, title: TITLE })
    return { text: 'Đã mở bảng tóm tắt Lớp học NNC.' }
  })

  // Học viên tự gửi một câu = có mặt; đang tạm nghỉ thì vào lại lớp và báo giáo viên kèm câu đó.
  on('prompt.submit', async ($, e, next) => {
    if (!(await read($, isClassroom))) return next(e)
    const kind = (e.origin as { kind?: string } | undefined)?.kind
    if (kind && !PERSON_ORIGINS.has(kind)) return next(e)
    if (e.text.trimStart().startsWith(CUE.trim())) return next(e)
    const was = await resume($)
    await touch($)
    if (was) return next({ ...e, context: [...(e.context ?? []), `${CUE}Học viên trở lại`] })
    return next(e)
  }).catch(($, e, next) => next(e))

  // Dùng nút / ô / lựa chọn của mod khác cũng là có mặt (nút của lớp tự ghi nhận trong handler).
  on('ui.press', async ($, e, next) => {
    if (e.plugin !== 'lop-hoc' && (await read($, isClassroom))) await touch($)
    return next(e)
  }).catch(($, e, next) => next(e))
  on('ui.input', async ($, e, next) => {
    if (e.kind === 'submit' && (await read($, isClassroom))) await touch($)
    return next(e)
  }).catch(($, e, next) => next(e))
  on('ui.select', async ($, e, next) => {
    if (await read($, isClassroom)) await touch($)
    return next(e)
  }).catch(($, e, next) => next(e))

  on('turn.start', async ($, e, next) => {
    turns += 1
    await update($, workingAtom, () => true)
    await update($, turnIdAtom, () => e.turnId)
    return next(e)
  })

  // Effort thật của mỗi lần gửi model, cho dòng "Claude của tôi".
  on('turn.step', async function* ($, e, next) {
    if (e.effort !== undefined) {
      const eff = String(e.effort)
      if ((await read($, effortAtom)) !== eff) await update($, effortAtom, () => eff)
    }
    return yield* next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const now = await $.clock.now()
    await update($, workingAtom, () => false)
    await update($, turnIdAtom, () => '')
    askSeen = null
    if (await read($, isClassroom)) {
      await update($, askAtom, () => null)
      await update($, lessonAtom, l => (l ? { ...l, idleFrom: now } : l))
      await syncState($)
      await update($, rev, n => n + 1)
      void refreshUsage($)
    }
    return next(e)
  })

  // Hộp câu hỏi gốc: ghi lúc mở, lựa chọn mặc định; học viên trả lời = có mặt.
  // Giáo viên ghi .lop-hoc/* → vẽ lại bục giảng.
  on('tool.call', async ($, e, next) => {
    if (!(await read($, isClassroom))) return next(e)
    if (e.tool === 'AskUserQuestion') {
      const id = e.tool_use_id
      const now = await $.clock.now()
      await update($, askAtom, () => ({ id, openedAt: now, label: defaultLabel(e.questions), handled: false }))
      try {
        return await next(e)
      } finally {
        askDone.add(id)
        if (askSeen?.id === id) askSeen = null
        const a = await read($, askAtom)
        if (a?.id === id) {
          if (!a.handled) await touch($)
          await update($, askAtom, () => null)
        }
      }
    }
    const ran = await next(e)
    if (JSON.stringify(e).includes('.lop-hoc')) {
      await syncState($)
      await update($, rev, n => n + 1)
    }
    return ran
  }).catch(($, e, next) => next(e))

  // ── Bục giảng: dải trên ô nhập ──────────────────────────────────────────────
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey || !(await read($, isClassroom))) return next(e)
    await read($, rev)
    const { Box, Text, Button } = $.ui.resolve(e)
    const isDesktop = e.surface === 'desktop'
    const lesson = await read($, lessonAtom)
    const now = (await read($, nowAtom)) || (lesson?.startedAt ?? 0)
    const mode = await read($, modeAtom)
    const usage = await read($, usageAtom)
    const line = claudeLine(usage, await read($, effortAtom))
    const s = await loadState($)
    const running = !!lesson && !lesson.over
    const kind: TeacherKind = lesson?.teacher ?? (await read($, teacherPick))
    const T = teacherName(kind)
    const t = teacherLower(kind)
    const address = cap(s?.address || 'anh/chị')
    const seg = announcedSeg(lesson)
    view = { teacher: kind, seg }
    // Huy hiệu mới: giáo viên vui (hỉ) 6 giây, đè cảm xúc giáo viên ghi.
    const emotion: Emotion = (await read($, cheerAtom)) ? 'hi' : (s?.teacher?.emotion ?? 'giang')
    const presence: TeacherPresence = !running ? 'wait' : lesson.pause === 'absent' ? 'away' : lesson.pause ? 'wait' : 'present'

    let podium = null
    if (isDesktop) {
      const { Svg } = $.ui.resolve(e)
      podium = <Svg key="podium" source={teacherPodiumSvg(kind, running ? emotion : 'hi', presence)} alt={`${T} trên bục giảng`} width={140} height={88} isInteractive />
    }
    const board = (children: RenderChildren[], gap = 1) => (
      <Box flexDirection="row" gap={2} alignItems="center" backgroundColor={BOARD} paddingX={1} paddingY={1}>
        {podium}
        <Box flexDirection="column" gap={gap} flexGrow={1}>
          {children}
        </Box>
      </Box>
    )
    const claudeRow = line ? <Text color={CHALK_DIM}>{`Claude của tôi · ${line}`}</Text> : null
    const pick = (key: string, label: string, isOn: boolean, onPress: () => unknown) =>
      isOn ? <Button key={key} label={label} variant="primary" onPress={onPress} /> : <Button key={key} label={label} onPress={onPress} />

    // Chưa vào lớp (hoặc buổi đã xong): chọn giáo viên, thời lượng, rồi Vào lớp.
    if (!running) {
      const tp = await read($, teacherPick)
      const mp = await read($, minutesPick)
      return board([
        <Text bold color={CHALK_Y}>{TITLE}</Text>,
        lesson?.over === 'xin-nghi' ? <Text color={CHALK}>{`Đã xin nghỉ · ${t} hẹn ${address.toLowerCase()} buổi sau`}</Text> : null,
        lesson?.over === 'ket-thuc' ? <Text color={CHALK}>Buổi học đã xong · hẹn gặp lại buổi sau</Text> : null,
        <Text color={CHALK}>Lớp đang chờ giáo viên · chọn giáo viên và thời lượng, rồi bấm Vào lớp</Text>,
        <Box flexDirection="row" gap={1} alignItems="center" flexWrap="wrap">
          <Text color={CHALK_DIM}>Giáo viên</Text>
          {TEACHERS.map(x => pick(`t-${x.id}`, x.label, tp === x.id, () => update($, teacherPick, () => x.id)))}
        </Box>,
        <Box flexDirection="row" gap={1} alignItems="center" flexWrap="wrap">
          <Text color={CHALK_DIM}>Thời lượng</Text>
          {([15, 30, 45] as const).map(m => pick(`m-${m}`, `${m} phút`, mp === m, () => update($, minutesPick, () => m)))}
        </Box>,
        claudeRow,
        <Box flexDirection="row" gap={1}>
          <Button key="enter" label="Vào lớp" variant="primary" onPress={() => startLesson($)} />
        </Box>,
      ])
    }

    const xinNghi = <Button key="xin-nghi" label="Xin nghỉ" onPress={async () => {
      await update($, modeAtom, () => 'normal')
      await sendPressCue($, 'Xin nghỉ', { over: 'xin-nghi', pause: null, pausedAt: null })
    }} />

    // Lớp tạm nghỉ vì vắng: chỉ còn thẻ Có mặt.
    if (lesson.pause === 'absent') {
      return board([
        <Text bold color={CHALK_Y}>{`${T}: Lớp đang tạm nghỉ — ${t} chờ ${address.toLowerCase()} quay lại`}</Text>,
        <Text color={CHALK_DIM}>Bấm Có mặt để học tiếp, thời gian các phần còn lại được dời theo.</Text>,
        <Box flexDirection="row" gap={1}>
          <Button key="co-mat" label="Có mặt" variant="primary" onPress={async () => {
            if (await resume($)) await sendPressCue($, 'Học viên trở lại')
          }} />
          {xinNghi}
        </Box>,
      ])
    }

    // Xin phép: đồng hồ dừng, chờ học viên quay lại.
    if (lesson.pause === 'xin-phep') {
      return board([
        <Text bold color={CHALK_Y}>{`Đang xin phép · ${lesson.pauseNote}`}</Text>,
        <Text color={CHALK_DIM}>{`Đồng hồ lớp đang dừng · ${t} chờ ${address.toLowerCase()}`}</Text>,
        <Box flexDirection="row" gap={1}>
          <Button key="quay-lai" label="Quay lại lớp" variant="primary" onPress={async () => {
            if (await resume($)) await sendPressCue($, 'Học viên trở lại')
          }} />
          {xinNghi}
        </Box>,
      ])
    }

    // Điểm danh: 60 giây để bấm Có mặt.
    if (lesson.rollCallAt != null) {
      return board([
        <Text bold color={CHALK_Y}>{`${T}: ${address} còn ở lớp không?`}</Text>,
        <Text color={CHALK}>{`Còn ${mmss(ROLLCALL_MS - (now - lesson.rollCallAt))} · không ai bấm thì lớp tạm nghỉ`}</Text>,
        <Box flexDirection="row" gap={1}>
          <Button key="co-mat" label="Có mặt" variant="primary" onPress={() => touch($)} />
          {xinNghi}
        </Box>,
      ])
    }

    if (mode === 'xin-phep') {
      const reason = (key: string, label: string) => (
        <Button key={key} label={label} onPress={async () => {
          const at = await $.clock.now()
          await update($, modeAtom, () => 'normal')
          await sendPressCue($, `Xin phép · ${label}`, { pause: 'xin-phep', pausedAt: at, pauseNote: label })
        }} />
      )
      return board([
        <Text bold color={CHALK_Y}>{`Xin phép ${t} một lát · chọn lý do`}</Text>,
        <Box flexDirection="row" gap={1} flexWrap="wrap">
          {reason('ly-do-nuoc', 'đi uống nước')}
          {reason('ly-do-gap', 'có việc gấp')}
          {reason('ly-do-hoi', 'cần hỏi riêng')}
          <Button key="xin-phep-thoi" label="Thôi" onPress={() => update($, modeAtom, () => 'normal')} />
        </Box>,
      ])
    }

    if (mode === 'gio-tay' && (e.surface === 'desktop' || e.surface === 'terminal')) {
      const { Input } = $.ui.resolve(e)
      return board([
        <Text bold color={CHALK_Y}>{`${address} giơ tay · ${t} đang nghe`}</Text>,
        <Input key="ke" label={`Kể ${t} nghe`} placeholder="Viết điều muốn hỏi hoặc kể, rồi bấm Enter" value="" submitLabel="gửi" autoFocus onSubmit={async (v: string) => {
          const text = v.trim()
          if (!text) return
          await update($, modeAtom, () => 'normal')
          await touch($)
          await $.prompt.submit({ text, asUser: true })
        }} />,
        <Box flexDirection="row" gap={1}>
          <Button key="gio-tay-thoi" label="Thôi" onPress={() => update($, modeAtom, () => 'normal')} />
        </Box>,
      ])
    }

    // Form giao việc 4 ý (D3): ghép lời giao việc, điền vào ô nhập — học viên tự bấm Enter.
    if (mode === 'form' && (e.surface === 'desktop' || e.surface === 'terminal')) {
      const { Input } = $.ui.resolve(e)
      const field = (key: keyof typeof draft, label: string, placeholder: string) => (
        <Input key={`f-${key}`} label={label} placeholder={placeholder} value={draft[key]} onInput={(v: string) => { draft = { ...draft, [key]: v } }} onSubmit={(v: string) => { draft = { ...draft, [key]: v } }} />
      )
      return board([
        <Text bold color={CHALK_Y}>Giao việc cho Claude · 4 ý</Text>,
        field('goal', 'Mục tiêu', 'Tổng hợp doanh số theo kênh từ bảng tính'),
        field('src', 'Nguồn', 'File bảng tính mẫu / file của tôi đã che thông tin'),
        field('out', 'Đầu ra', 'Bảng: kênh – số đơn – doanh số'),
        field('check', 'Cách kiểm', 'Đối chiếu tổng với cột gốc'),
        formError ? <Text color={ALERT}>{formError}</Text> : null,
        <Box flexDirection="row" gap={1}>
          <Button key="form-fill" label="Đưa vào ô nhập" variant="primary" onPress={async () => {
            if (!draft.goal.trim()) {
              formError = 'Ghi "Mục tiêu" trước đã.'
              await update($, rev, n => n + 1)
              return
            }
            formError = ''
            await touch($)
            await $.prompt.fill({ text: delegationPrompt(draft), mode: 'replace' })
            draft = { goal: '', src: '', out: '', check: '' }
            await update($, modeAtom, () => 'normal')
            $.ui.toast('Đọc lại lời giao việc trong ô nhập, rồi bấm Enter để giao.')
          }} />
          <Button key="form-cancel" label="Đóng" onPress={() => update($, modeAtom, () => 'normal')} />
        </Box>,
      ])
    }

    // Bình thường: phần học, vòng giờ, lượt của học viên, nút.
    const plan = lessonPlan(lesson.minutes)
    const shown = seg ?? S0
    const drive = shown.drive
    const segStartMs = segmentStart(plan, lesson.announced)
    const segTotal = shown.minutes * MIN
    const segElapsed = Math.min(segTotal, Math.max(0, lessonElapsed(lesson, now) - segStartMs))
    const ask = await read($, askAtom)
    const working = e.props.isWorking
    const parts = s?.status === 'active' ? (s.result_parts ?? []) : []
    const panel = s?.panel ?? null
    const isPractice = shown.id === '2' || shown.id === '3'

    let ring = <Text color={CHALK_DIM}>{`còn ${Math.max(0, Math.ceil((segTotal - segElapsed) / MIN))} phút`}</Text>
    if (isDesktop) {
      const { Svg } = $.ui.resolve(e)
      ring = <Svg key="ring" source={segmentClockSvg({ elapsedMs: segElapsed, totalMs: segTotal, drive })} alt="Thời gian còn lại của phần học" width={44} height={44} />
    }

    let panelRows: RenderChildren[] = []
    if (panel === 'usage') {
      const nowIso = new Date(now || Date.now()).toISOString()
      const five = usage?.five
      const week = usage?.week
      let pics: RenderChildren[] = []
      if (isDesktop && (five || week)) {
        const { Svg } = $.ui.resolve(e)
        pics = [
          five ? <Svg key="usage-5h" source={usageTimelineSvg({ percentUsed: five.percentUsed, resetsAt: five.resetsAt, now: nowIso })} alt={`Hạn mức 5 giờ: đã dùng ${Math.round(five.percentUsed)}%`} /> : null,
          week ? <Svg key="usage-week" source={weekResetSvg({ percentUsed: week.percentUsed, resetsAt: week.resetsAt, now: nowIso })} alt={`Hạn mức tuần: đã dùng ${Math.round(week.percentUsed)}%`} /> : null,
        ]
      }
      panelRows = [
        <Text bold color={CHALK_Y}>Hạn mức sử dụng · 5 giờ và tuần</Text>,
        ...pics,
        five ? <Text color={CHALK}>{`5 giờ: đã dùng ${Math.round(five.percentUsed)}%${resetTime(five.resetsAt) ? ` · reset lúc ${resetTime(five.resetsAt)}` : ''}`}</Text> : null,
        week ? <Text color={CHALK}>{`Tuần: đã dùng ${Math.round(week.percentUsed)}%${resetDay(week.resetsAt) ? ` · reset ${resetDay(week.resetsAt)}` : ''}`}</Text> : null,
        !five && !week ? <Text color={CHALK_DIM}>{`Chưa đọc được số liệu · chờ ${t} giảng xong một lượt`}</Text> : null,
      ]
    } else if (panel === 'claude') {
      panelRows = [
        <Text bold color={CHALK_Y}>Claude của tôi</Text>,
        <Text color={CHALK}>{line || `Chưa đọc được số liệu · chờ ${t} giảng xong một lượt`}</Text>,
        <Text color={CHALK_DIM}>Model: bộ não đang dùng · Effort: mức nghĩ kỹ · Context: trí nhớ của phiên · 5 giờ / tuần: hạn mức gói</Text>,
      ]
    }

    const headline = working ? `${T} đang giảng — ${address.toLowerCase()} xem bên trên` : `Lượt của bạn${s?.next_action ? ` · ${cut(s.next_action, 80)}` : ''}`

    // ── v0.6: nút một chạm, thử thách, sao, huy hiệu, hộp quà ──
    const isActive = !s || s.status === 'active'
    const one = isActive ? (s?.one_touch ?? null) : null
    const oneHash = one ? `${one.label}\n${one.text}` : ''
    const oneTouch = one && !working && (await read($, oneTouchUsed)) !== oneHash ? (
      <Box flexDirection="row">
        <Button key="one-touch" label={`▶ ${cut(one.label, 60)}`} variant="primary" onPress={async () => {
          await touch($)
          await update($, entered, () => true)
          await update($, oneTouchUsed, () => oneHash)
          await $.prompt.fill({ text: one.text, mode: 'replace' })
          $.ui.toast('Đã điền sẵn — bấm Enter để giao cho Claude')
        }} />
      </Box>
    ) : null

    const challenge = isActive ? (s?.challenge ?? null) : null
    const chLeft = challengeLeft(challenge, now)
    const stars = isActive && typeof s?.stars === 'number' && s.stars > 0 ? s.stars : 0
    // Kệ huy hiệu: hình tự lấy 4 cái gần nhất và ghi "+n"; ẩn khi hộp câu hỏi gốc đang mở.
    const allBadges = ask ? [] : await read($, badgesAtom)
    const badges = allBadges.slice(-4)
    const extras: RenderChildren[] = []
    if (challenge && chLeft) {
      if (isDesktop) {
        const { Svg } = $.ui.resolve(e)
        const src = challengeRingSvg({ remainingMs: chLeft.leftMs, totalMs: chLeft.totalMs })
        extras.push(<Svg key="challenge" source={src} alt={`Thử thách còn ${mmss(chLeft.leftMs)}`} {...svgSize(src, 56, 56)} />)
        extras.push(<Text key="challenge-title" bold color={chLeft.leftMs > 0 ? CHALK_Y : CHALK_DIM}>{`${cut(challenge.title, 40)}${chLeft.leftMs > 0 ? '' : ' · hết giờ'}`}</Text>)
      } else {
        extras.push(<Text key="challenge-title" bold color={chLeft.leftMs > 0 ? CHALK_Y : CHALK_DIM}>{`Thử thách ${mmss(chLeft.leftMs)} · ${cut(challenge.title, 40)}${chLeft.leftMs > 0 ? '' : ' · hết giờ'}`}</Text>)
      }
    }
    if (stars) {
      if (isDesktop) {
        const { Svg } = $.ui.resolve(e)
        const src = starRowSvg(stars)
        extras.push(<Svg key="stars" source={src} alt={`${stars} sao trong buổi`} {...svgSize(src, 24 * Math.min(stars, 5) + 40, 24)} />)
      } else {
        extras.push(<Text key="stars" color={CHALK_Y}>{`★ ${stars}`}</Text>)
      }
    }
    if (badges.length) {
      if (isDesktop) {
        const { Svg } = $.ui.resolve(e)
        const shelf: BadgeRef[] = allBadges.map(b => ({ id: b.id, label: b.label }))
        const src = badgeShelfSvg(shelf)
        extras.push(<Svg key="badges" source={src} alt={`Huy hiệu: ${badges.map(b => b.label).join(', ')}`} {...svgSize(src, 240, 56)} />)
      } else {
        const more = allBadges.length - badges.length
        extras.push(<Text key="badges" color={CHALK}>{`Huy hiệu: ${badges.map(b => cut(b.label, 24)).join(' · ')}${more > 0 ? ` · +${more}` : ''}`}</Text>)
      }
    }
    const extrasRow = extras.length ? (
      <Box flexDirection="row" gap={2} alignItems="center" flexWrap="wrap">
        {extras}
      </Box>
    ) : null

    const gift = await read($, giftAtom)
    let giftRow: RenderChildren = null
    if (gift === 'opening' || (gift === 'closed' && isActive && s?.gift_box && !working)) {
      const isOpen = gift === 'opening'
      let pic: RenderChildren = <Text color={CHALK_Y}>{isOpen ? 'Hộp quà đang mở…' : 'Có một hộp quà cho bạn'}</Text>
      if (isDesktop) {
        const { Svg } = $.ui.resolve(e)
        const src = giftBoxSvg(isOpen)
        pic = <Svg key="gift" source={src} alt={isOpen ? 'Hộp quà đang mở' : 'Hộp quà'} {...svgSize(src, 64, 64)} />
      }
      giftRow = (
        <Box flexDirection="row" gap={1} alignItems="center">
          {pic}
          {isOpen ? null : <Button key="hop-qua" label="Mở hộp quà" variant="primary" onPress={async () => {
            await touch($)
            await update($, giftAtom, () => 'opening')
            try {
              $.clock.after(GIFT_OPEN_MS, () => void update($, giftAtom, g => (g === 'opening' ? 'opened' : g)))
            } catch {}
            await $.prompt.submit({ text: `${TAG}Mở hộp quà`, asUser: true })
          }} />}
        </Box>
      )
    }

    const header = (
      <Box flexDirection="row" gap={1} alignItems="center">
        <Text backgroundColor={DRIVE_COLOR[drive]} color={INK}>{` Phần ${shown.id} · ${shown.title} `}</Text>
        {ring}
        <Text color={CHALK_DIM}>{`${T} · buổi ${lesson.minutes} phút`}</Text>
      </Box>
    )
    const headRow = <Text bold={!working} color={working ? CHALK_DIM : CHALK_Y}>{headline}</Text>
    const askRow = ask && !ask.handled ? <Text color={CHALK}>{`${T} chọn giúp sau ${mmss(ANSWER_MS - (now - ask.openedAt))}`}</Text> : null
    const helpRow = s?.help_needed ? <Text bold color={INK} backgroundColor={ALERT}>{' Đang cần người đứng lớp hỗ trợ '}</Text> : null
    const destRow = s?.destination ? <Text color={CHALK_DIM}>{`Đích: ${cut(s.destination, 80)}`}</Text> : null
    const partsRow = parts.length ? (
      <Box flexDirection="row" gap={2} flexWrap="wrap">
        {parts.map((p, i) => (
          <Text key={`rp-${i}`} color={p.done ? CHALK_Y : CHALK_DIM}>{`${p.done ? '✓' : '○'} ${cut(p.label, 30)}`}</Text>
        ))}
      </Box>
    ) : null
    const infoRow = panel === 'claude' ? null : claudeRow

    // Dải chật (ước số dòng vượt chỗ) mà có phần v0.6: thu khoảng cách, bỏ dòng phụ, xếp theo thứ tự ưu tiên
    // nút một chạm → Lượt của bạn → thử thách/sao/huy hiệu → các nút khác.
    const hasSix = !!(oneTouch || extrasRow || giftRow)
    const lines = [header, oneTouch, headRow, askRow, extrasRow, helpRow, destRow, partsRow, ...panelRows, infoRow, giftRow].filter(x => x != null).length + 2
    const maxRows = typeof e.props.maxRows === 'number' && e.props.maxRows > 0 ? e.props.maxRows : 0
    const crowded = hasSix && maxRows > 0 && 2 + lines * 2 - 1 > maxRows
    const top: RenderChildren[] = crowded
      ? [oneTouch, headRow, askRow, extrasRow, header, helpRow, partsRow, ...panelRows, giftRow]
      : [header, oneTouch, headRow, askRow, extrasRow, helpRow, destRow, partsRow, ...panelRows, infoRow, giftRow]

    return board([
      ...top,
      <Box flexDirection="row" gap={1} flexWrap="wrap">
        <Button key="gio-tay" label="Giơ tay" onPress={async () => {
          await update($, modeAtom, () => 'gio-tay')
          await sendPressCue($, 'Giơ tay')
        }} />
        <Button key="xin-phep" label="Xin phép" onPress={async () => {
          await touch($)
          await update($, modeAtom, () => 'xin-phep')
        }} />
        {xinNghi}
      </Box>,
      working ? null : (
        <Box flexDirection="row" gap={1} flexWrap="wrap">
          <Button key="cham" label="Chậm lại một chút" onPress={() => sendPressCue($, 'Nhịp: chậm lại')} />
          <Button key="nhanh" label="Nhanh hơn được" onPress={() => sendPressCue($, 'Nhịp: nhanh hơn')} />
          <Button key="goi-y" label={`${T} gợi ý giúp`} onPress={async () => {
            await touch($)
            await $.prompt.submit({ text: `${TAG}${T} gợi ý giúp`, asUser: true })
          }} />
          {isPractice ? <Button key="b-form" label="Giao việc" onPress={async () => { await touch($); await update($, modeAtom, () => 'form') }} /> : null}
          {isPractice ? <Button key="chua-dung" label={`Thưa ${t}, chỗ này chưa đúng`} onPress={async () => {
            await touch($)
            await $.prompt.fill({ text: `Thưa ${t}, chỗ này chưa đúng: `, mode: 'replace' })
          }} /> : null}
        </Box>
      ),
    ], crowded ? 0 : 1)
  })

  // ── Hộp câu hỏi gốc: thêm một dòng lớp học phía trên, giữ nguyên hộp ─────────
  on('ui.render', { component: 'AskUserQuestion' }, async ($, e, next) => {
    if (!(await read($, isClassroom))) return next(e)
    const theirs = await next(e)
    const { Box, Text } = $.ui.resolve(e)
    if (!askDone.has(e.requestId) && askSeen?.id !== e.requestId) askSeen = { id: e.requestId, label: defaultLabel(e.props.questions) }
    const T = teacherName(view.teacher)
    const head = view.seg ? `${T} hỏi · Phần ${view.seg.id} · ${view.seg.title}` : `${T} hỏi`
    return (
      <Box flexDirection="column">
        <Text bold color="#006D11">{head}</Text>
        {theirs}
      </Box>
    )
  })

  // ── Lời giáo viên: bọc lời Claude, giữ nguyên định dạng gốc ──────────────────
  on('ui.render', { component: 'AssistantMessage' }, async ($, e, next) => {
    if (!(await read($, isClassroom))) return next(e)
    const theirs = await next(e)
    const { Box, Text } = $.ui.resolve(e)
    const first = e.props.isFirstOfReply
    const T = teacherName(view.teacher)
    let title = headerById.get(e.requestId)
    if (!title) {
      title = view.seg ? ` ${T} · Phần ${view.seg.id} · ${view.seg.title} ` : ` ${T} `
      headerById.set(e.requestId, title)
    }
    const color = DRIVE_COLOR[view.seg?.drive ?? 'D1']
    let avatar = <Box width={e.surface === 'desktop' ? 5 : 2} />
    if (first && e.surface === 'desktop') {
      const { Svg } = $.ui.resolve(e)
      avatar = <Svg key="avatar" source={teacherAvatarSvg(view.teacher)} alt={T} width={34} height={34} />
    }
    return (
      <Box flexDirection="row" gap={1}>
        {avatar}
        <Box flexDirection="column" flexGrow={1} borderStyle="quote" borderColor="#008816" paddingLeft={1}>
          {first ? <Text bold backgroundColor={color} color={INK}>{title}</Text> : null}
          {theirs}
        </Box>
      </Box>
    )
  })

  // ── Tin nhắn: tín hiệu giáo án ẩn (chuyển phần = một dòng chia), tin của học viên thành thẻ ──
  on('ui.render', { component: 'UserMessage' }, async ($, e, next) => {
    if (!(await read($, isClassroom))) return next(e)
    const { Box, Text } = $.ui.resolve(e)
    const text = e.props.text ?? ''
    const at = text.indexOf(CUE.trim())
    if (at >= 0 && at < 200) {
      const body = text.slice(at + CUE.trim().length).trim()
      const m = /^Bắt đầu phần\s+(\S+)\s+·\s+([^·\n]+)/.exec(body)
      if (m) {
        const label = m[1] === BREAK.id ? `— ${BREAK.title} —` : `— Phần ${m[1]} · ${(m[2] ?? '').trim()} —`
        return (
          <Box flexDirection="row" justifyContent="center">
            <Text dimColor>{label}</Text>
          </Box>
        )
      }
      return <Box />
    }
    if (e.props.isExpanded) return next(e)
    if (text.startsWith(TAG)) {
      return (
        <Box flexDirection="row" borderStyle="round" borderColor="#C9A800" paddingX={1}>
          <Text color="#854F0B">{`Bạn bấm · ${cut(text.slice(TAG.length).trim().split('\n')[0], 120)}`}</Text>
        </Box>
      )
    }
    const theirs = await next(e)
    const label = text.startsWith('Giao việc —') ? 'Bạn giao việc' : 'Bạn'
    return (
      <Box flexDirection="column" borderStyle="round" borderColor="#C9A800" paddingX={1}>
        <Text bold color="#854F0B">{label}</Text>
        {theirs}
      </Box>
    )
  })

  // ── Dòng công cụ: thêm một câu dễ hiểu, giữ chi tiết gốc bên dưới ───────────
  on('ui.render', { component: 'ToolUse' }, async ($, e, next) => {
    if (!(await read($, isClassroom))) return next(e)
    const plain = describeTool(e.props.tool, e.props.input)
    if (!plain) return next(e)
    const theirs = await next(e)
    const { Box, Text } = $.ui.resolve(e)
    return (
      <Box flexDirection="column">
        <Text color="#006D11">{`▸ ${teacherName(view.teacher)} ${plain}`}</Text>
        {theirs}
      </Box>
    )
  })

  // ── Spinner tiếng Việt + mẹo đổi theo lượt, giữ hoạt ảnh gốc ───────────────
  on('ui.render', { component: 'Spinner' }, async ($, e, next) => {
    if (!(await read($, isClassroom))) return next(e)
    const T = teacherName(view.teacher)
    const word = e.props.mode === 'tool-use' || e.props.mode === 'tool-input' ? `${T} đang làm mẫu` : `${T} đang giảng`
    const tip = TIPS[turns % TIPS.length] ?? ''
    return next({ ...e, props: { ...e.props, word, suffix: ` · ${tip}` } })
  })

  // ── Gợi ý dưới ô nhập ───────────────────────────────────────────────────────
  on('ui.render', { component: 'PromptHint' }, async ($, e, next) => {
    if (e.props.isDraft || e.props.isWorking || !(await read($, isClassroom))) return next(e)
    const isIn = await read($, entered)
    const hint = !isIn ? 'Chọn giáo viên và thời lượng trên bảng lớp, rồi bấm Vào lớp' : `Bấm nút trên bảng lớp, hoặc kể ${teacherLower(view.teacher)} nghe ở đây`
    return next({ ...e, props: { ...e.props, hint } })
  })

  // ── Bảng tóm tắt (chỉ khi gõ /lop-hoc) ─────────────────────────────────────
  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    await read($, rev)
    const lesson = await read($, lessonAtom)
    const s = await loadState($)
    const skills = s?.skills ?? []
    const plan = lesson ? lessonPlan(lesson.minutes) : lessonPlan(30)
    const cur = lesson ? (lesson.over ? plan.length : lesson.announced) : -1

    return (
      <Box flexDirection="column" gap={1}>
        <Text bold color="#006D11">{TITLE}</Text>
        {lesson ? <Text>{`${teacherName(lesson.teacher)} · buổi ${lesson.minutes} phút`}</Text> : <Text dimColor>Chưa vào lớp. Chọn giáo viên và thời lượng trên bảng lớp, rồi bấm Vào lớp.</Text>}
        <Box flexDirection="column">
          <Text dimColor>Giáo án hôm nay</Text>
          {plan.map((p, n) => {
            const mark = n < cur ? '✓' : n === cur ? '→' : '○'
            return (
              <Text key={`seg-${p.id}`} bold={n === cur} color={n < cur ? 'success' : undefined} dimColor={n > cur}>
                {`${mark} Phần ${p.id} · ${p.title} · ${p.minutes} phút`}
              </Text>
            )
          })}
        </Box>
        {skills.length ? (
          <Box flexDirection="column">
            <Text dimColor>Đã làm được</Text>
            {skills.map((k, i) => (
              <Text key={`sk-${i}`} color={k.done ? 'success' : undefined} dimColor={!k.done}>
                {`${k.done ? '✓' : '○'} ${cut(k.label, 80)}`}
              </Text>
            ))}
          </Box>
        ) : null}
        {s?.next_action ? <Text>{`Bước tiếp: ${cut(s.next_action, 120)}`}</Text> : null}
      </Box>
    )
  })
}
