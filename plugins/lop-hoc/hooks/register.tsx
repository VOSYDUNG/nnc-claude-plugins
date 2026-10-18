import { atom, read, update } from 'claude-code'
import type { Register, EngineInterface, RenderChildren } from 'claude-code'

import type {
  ActivityTrack,
  AskOpen,
  BadgeEntry,
  BandMode,
  BoardSpec,
  ChoicesSpec,
  DriveId,
  FactId,
  GiftPhase,
  Lesson,
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
  PodiumButtonId,
  PodiumSpec,
  TeacherKindId,
  UsageInfo,
} from '../types'
import type { BadgeRef, Emotion, TeacherKind, TeacherPresence } from './art'
import {
  DRIVE_COLOR,
  TEACHERS,
  badgeShelfSvg,
  bottomBarSvg,
  challengeRingSvg,
  giftBoxSvg,
  isEmotion,
  isTeacherKind,
  sanitizeSvg,
  starRowSvg,
  svgBox,
  teacherAvatarSvg,
  teacherPodiumSvg,
  usageTimelineSvg,
  weekResetSvg,
} from './art'
import { DELEGATION_HEADS, STR, isLang } from './i18n'
import type { Lang } from './i18n'
import { SHOT_MAX_BYTES, shotFromBase64, shotPathOf } from './shot'
import type { ShotDrawn } from './shot'

// Lớp học NNC v0.8 — giáo viên là người dựng sân khấu: bục giảng yên tĩnh theo mặc định, mỗi lượt giáo viên có thể
//   ghi podium (cỡ, nhãn hiện, chỗ chỉ, nút), board (bảng nhỏ), choices (nút lớn không chặn) vào state.json
//   (thiết kế docs/oser-r2/LOP-HOC-V08-THIET-KE.md). Đồng hồ nhịp 1,5 giây đọc lại state.json khi chữ đổi;
//   mod đọc chế độ quyền ở thanh dưới (SessionMode); dòng công cụ ghi vào .lop-hoc/ chỉ còn một dòng mờ.
// Lớp học NNC v0.7 — lớp luôn mở, giáo viên đứng lớp, nhịp theo việc và hạn mức (hợp đồng §9).
//   Bục giảng (dải trên ô nhập, nền bảng lớp): chọn thầy/cô → Vào lớp; giáo viên trên bục với cảm xúc;
//     phần học do giáo viên ghi khi đạt mốc (không theo giờ); "Lượt của bạn"; nút Giơ tay · Xin phép · Xin nghỉ;
//     Phiếu kết quả; Soạn tin nhờ hỗ trợ khi cần người hỗ trợ.
//   Không có thời lượng, không điểm danh. Giữa hai lần học viên tác động, mod gửi tối đa một tín hiệu
//     "[Giáo án] …" (lớp chỉ chờ, không giảng vào phòng trống, không tốn hạn mức).
//   Hạn 60 giây chọn giúp chỉ áp cho câu đố và trò chơi (activity.kind = quiz | game:*): lúc học viên
//     đang làm việc thật ở Excel, email… đồng hồ không chạy.
//   Mod đọc hạn mức 5 giờ và tuần, báo giáo viên khi chạm ngưỡng để giáo viên giảng gọn hoặc lưu điểm dừng.
//   Câu hỏi dùng hộp câu hỏi gốc (AskUserQuestion); mod chỉ thêm một dòng tiêu đề lớp học.
// v0.6 giữ nguyên: nút một chạm, đổi kiểu tương tác (trừ lúc làm việc thật), thử thách có giờ, sao, huy hiệu, hộp quà.
// Mod chỉ ĐỌC .lop-hoc/state.json (giáo viên ghi). Hộp xin quyền, ô nhập và khung app là của Claude Code.

const PANE = 'lop-hoc'
const TITLE = 'Lớp học NNC'
const STATE = '.lop-hoc/state.json'
const BADGES = '.lop-hoc/huy-hieu.json'
const TAG = '[Lớp học] '
const CUE = '[Giáo án] '

const TICK_MS = 5_000
// Nhịp đọc lại state.json (chỉ đọc chữ, đổi mới nạp lại) và hẹn giờ lựa chọn trên bục.
const WATCH_MS = 1_500
// Hộp câu hỏi gốc (không phải câu đố/trò chơi) mở quá 90 giây: báo giáo viên một lần.
const LONG_BOX_MS = 90_000
const ANSWER_MS = 60_000
const CUE_GAP_MS = 20_000
// v0.11 — thang im lặng: học viên không tác động từ lúc giáo viên nói xong. Nấc 1 sau 90 giây, nấc 2 sau 3 phút,
// nấc 3 sau 5 phút nữa; lúc thử thách có giờ hoặc làm việc thật (hands-on | form) thì nấc 1 chờ 3 phút.
const SILENCE_FIRST_MS = 90_000
const SILENCE_WORK_MS = 3 * 60_000
const SILENCE_WAIT_MS = [SILENCE_FIRST_MS, 3 * 60_000, 5 * 60_000] as const
// v0.11 — lời giáo viên dài hơn ngưỡng này (ký tự) thì gập: 3 dòng đầu + nút "Xem đầy đủ".
const FOLD_CHARS = 600
const FOLD_LINES = 3
const FOLD_LINE_CHARS = 200
// Ngưỡng hạn mức (%) báo giáo viên: 5 giờ ở 70 (giảng gọn) và 90 (lưu điểm dừng); tuần ở 90.
const FIVE_STEPS = [70, 90]
const WEEK_STEPS = [90]
// Context của phiên đầy tới mức này thì báo giáo viên một lần (đề nghị mở phiên mới khi chốt vòng việc).
const CONTEXT_STEP = 70
const ACTIVITY_MS = 4 * 60_000
const CHALLENGE_STALE_MS = 10 * 60_000
const MIN = 60_000
const CHEER_MS = 6_000
const GIFT_OPEN_MS = 4_000

// Bảng lớp: nền xanh đậm, chữ phấn.
// Cỡ hình giáo viên theo cỡ bục: mini gọn một dòng, normal vừa, wide có chỗ cho bảng.
const AVATAR_DIMS: Record<'mini' | 'normal' | 'wide', { w: number; h: number }> = { mini: { w: 56, h: 36 }, normal: { w: 96, h: 60 }, wide: { w: 140, h: 88 } }
const BAR_DIMS: Record<'mini' | 'normal' | 'wide', { w: number; h: number }> = { mini: { w: 300, h: 40 }, normal: { w: 360, h: 48 }, wide: { w: 480, h: 64 } }
const BOARD_W: Record<'mini' | 'normal' | 'wide', number> = { mini: 180, normal: 260, wide: 380 }
// Ảnh chụp màn hình có đánh dấu rộng hơn hình SVG thường (cỡ rộng: 560 × 340 điểm).
const SHOT_W: Record<'mini' | 'normal' | 'wide', number> = { mini: 280, normal: 420, wide: 560 }
const SHOT_H = 340
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
const liveAtom = atom({ plugin: 'lop-hoc', key: 'live' } as const, { activity: null, challenge: null, giftBox: false, segment: null, choices: null } as LiveState)
const activityTrack = atom({ plugin: 'lop-hoc', key: 'activityTrack' } as const, null as ActivityTrack | null)
const badgesAtom = atom({ plugin: 'lop-hoc', key: 'badges' } as const, [] as BadgeEntry[])
const cheerAtom = atom({ plugin: 'lop-hoc', key: 'cheer' } as const, false)
const giftAtom = atom({ plugin: 'lop-hoc', key: 'gift' } as const, 'closed' as GiftPhase)
// v0.8
const modesAtom = atom({ plugin: 'lop-hoc', key: 'modes' } as const, [] as string[])
const stateVer = atom({ plugin: 'lop-hoc', key: 'stateVer' } as const, 0)
const choiceDone = atom({ plugin: 'lop-hoc', key: 'choiceDone' } as const, '')
const choiceExpired = atom({ plugin: 'lop-hoc', key: 'choiceExpired' } as const, '')
const moreOpen = atom({ plugin: 'lop-hoc', key: 'moreOpen' } as const, false)
// v0.11
// Lần tác động cuối của học viên hoặc lúc giáo viên nói xong (at, giờ đồng hồ) và nấc im lặng đã gửi (0 = chưa).
type Silence = { at: number; rung: 0 | 1 | 2 | 3 }
const silenceAtom = atom({ plugin: 'lop-hoc', key: 'silence' } as const, { at: 0, rung: 0 } as Silence)
// Lời giáo viên dài đã được học viên mở ra (theo requestId của khối).
const foldOpen = atom({ plugin: 'lop-hoc', key: 'foldOpen' } as const, [] as string[])

// ── Phần học (v0.7: giáo viên chuyển phần khi đạt mốc; mod chỉ hiển thị) ────────
const S0: PlanSegment = { id: '0', title: 'Vào lớp', drive: 'ket-noi' }
const S1: PlanSegment = { id: '1', title: 'Làm quen nhanh', drive: 'D2' }
const S2: PlanSegment = { id: '2', title: 'Việc thật của tôi', drive: 'D1' }
const S3: PlanSegment = { id: '3', title: 'Thử thách theo nhịp của bạn', drive: 'D3' }
const S4: PlanSegment = { id: '4', title: 'Chốt vòng việc', drive: 'ket-noi' }
export const SEGMENTS: PlanSegment[] = [S0, S1, S2, S3, S4]
const SEGMENTS_BY_ID: Record<string, PlanSegment> = { '0': S0, '1': S1, '2': S2, '3': S3, '4': S4 }

// Thời gian lớp đã mở, không tính lúc xin phép / chờ.
export function lessonElapsed(l: Pick<Lesson, 'startedAt' | 'shiftMs' | 'pausedAt'>, now: number): number {
  return Math.max(0, now - l.startedAt - l.shiftMs - (l.pausedAt != null ? now - l.pausedAt : 0))
}

// Câu đố và trò chơi có hạn 60 giây; câu hỏi lúc làm việc thật thì chờ học viên.
export function timedKind(kind: string | undefined | null): boolean {
  return !!kind && (kind === 'quiz' || kind.startsWith('game:'))
}

// Luật "cùng một kiểu quá 4 phút thì đổi" không áp cho lúc học viên đang làm việc thật.
export function switchableKind(kind: string | undefined | null): boolean {
  return !!kind && kind !== 'hands-on' && kind !== 'form'
}

// Lời dài thì gập: 3 dòng đầu (mỗi dòng cắt ở 200 ký tự). Trả null khi không cần gập (ngắn, hoặc gập rồi không ẩn gì).
export function foldPreview(text: string): string | null {
  if (text.length <= FOLD_CHARS) return null
  const lines = text.replace(/^\s*\n/, '').split('\n')
  const first = lines.slice(0, FOLD_LINES)
  const cutLine = first.some(x => x.length > FOLD_LINE_CHARS)
  if (lines.length <= FOLD_LINES && !cutLine) return null
  const head = first.map(x => (x.length > FOLD_LINE_CHARS ? `${x.slice(0, FOLD_LINE_CHARS).trimEnd()}…` : x)).join('\n').trimEnd()
  return lines.length > FOLD_LINES && !cutLine ? `${head}\n…` : head
}

// Nấc im lặng kế tiếp đã đến giờ chưa (đủ điều kiện khác do nơi gọi kiểm). slow = thử thách có giờ / làm việc thật.
export function silenceDue(sil: Silence, now: number, slow: boolean): 1 | 2 | 3 | null {
  if (sil.rung >= 3) return null
  const wait = sil.rung === 0 && slow ? SILENCE_WORK_MS : SILENCE_WAIT_MS[sil.rung]!
  return now - sil.at >= wait ? ((sil.rung + 1) as 1 | 2 | 3) : null
}

type UsageCue = { key: string; text: string; also: string[] }

// Tín hiệu hạn mức đến hạn (ngưỡng cao nhất vừa chạm, chưa báo trong chu kỳ reset này).
export function usageCue(u: UsageInfo | null, sent: string[]): UsageCue | null {
  if (!u) return null
  const pick = (scope: 'u5' | 'uw', r: UsageInfo['five'], steps: number[], label: string, when: string): UsageCue | null => {
    if (!r) return null
    const crossed = steps.filter(s => r.percentUsed >= s)
    if (!crossed.length) return null
    const keys = crossed.map(s => `${scope}-${s}-${r.resetsAt ?? ''}`)
    const top = keys[keys.length - 1] ?? ''
    if (sent.includes(top)) return null
    return { key: top, text: `Hạn mức · ${label} ${Math.round(r.percentUsed)}%${when ? ` · reset ${when}` : ''}`, also: keys.slice(0, -1) }
  }
  const ctx = u.context != null && u.context >= CONTEXT_STEP && !sent.includes(`ctx-${CONTEXT_STEP}`)
    ? { key: `ctx-${CONTEXT_STEP}`, text: `Hạn mức · context ${Math.round(u.context)}%`, also: [] }
    : null
  return pick('uw', u.week, WEEK_STEPS, 'tuần', resetDay(u.week?.resetsAt)) ?? pick('u5', u.five, FIVE_STEPS, '5 giờ', resetTime(u.five?.resetsAt)) ?? ctx
}

// Các khoá hạn mức đã vượt lúc mở lớp (số liệu đã gửi kèm "Mở lớp", không báo lại).
export function usageKeysCrossed(u: UsageInfo | null): string[] {
  if (!u) return []
  const keys = (scope: string, r: UsageInfo['five'], steps: number[]) => (r ? steps.filter(s => r.percentUsed >= s).map(s => `${scope}-${s}-${r.resetsAt ?? ''}`) : [])
  return [...keys('u5', u.five, FIVE_STEPS), ...keys('uw', u.week, WEEK_STEPS), ...(u.context != null && u.context >= CONTEXT_STEP ? [`ctx-${CONTEXT_STEP}`] : [])]
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
    language: isLang(raw.language) ? raw.language : undefined,
    podium: podiumOf(raw.podium),
    board: boardOf(raw.board),
    choices: choicesOf(raw.choices),
    loops_done: typeof raw.loops_done === 'number' && Number.isFinite(raw.loops_done) ? Math.min(999, Math.max(0, Math.round(raw.loops_done))) : undefined,
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

// ── v0.8: sân khấu bục giảng (podium · board · choices), đọc phòng thủ ────────────
const FACTS: readonly FactId[] = ['mode', 'effort', 'model', 'context', 'usage5', 'usageWeek']
const BUTTON_IDS: readonly PodiumButtonId[] = ['raise-hand', 'ask-leave', 'leave', 'slower', 'faster', 'hint', 'result-sheet', 'delegate']
const isFact = (v: unknown): v is FactId => typeof v === 'string' && (FACTS as readonly string[]).includes(v)
const isButtonId = (v: unknown): v is PodiumButtonId => typeof v === 'string' && (BUTTON_IDS as readonly string[]).includes(v)
const cutStr = (s: string, n: number) => (s.length > n ? s.slice(0, n - 1) + '…' : s)

function uniqueOf<T>(v: unknown, ok: (x: unknown) => x is T): T[] {
  if (!Array.isArray(v)) return []
  const out: T[] = []
  for (const x of v) if (ok(x) && !out.includes(x)) out.push(x)
  return out
}

export function podiumOf(v: unknown): PodiumSpec | null {
  if (!isObj(v)) return null
  return {
    size: v.size === 'mini' || v.size === 'wide' ? v.size : 'normal',
    show: uniqueOf(v.show, isFact),
    point: isFact(v.point) ? v.point : null,
    buttons: uniqueOf(v.buttons, isButtonId),
  }
}

// Bảng: tiêu đề ≤ 60 ký tự, tối đa 5 dòng × 90 ký tự, SVG ≤ 16 KB đã lọc sạch (không sạch thì bỏ hình, giữ chữ).
// v0.10: shot = đường dẫn ảnh chụp có đánh dấu trong .lop-hoc/ (sai đường dẫn/đuôi thì bỏ qua); svg của giáo viên luôn qua sanitizeSvg.
export function boardOf(v: unknown): BoardSpec | null {
  if (!isObj(v)) return null
  const title = cutStr(nonEmpty(v.title) ?? '', 60)
  const lines = Array.isArray(v.lines) ? v.lines.map(nonEmpty).filter((x): x is string => !!x).slice(0, 5).map(x => cutStr(x, 90)) : []
  const svg = v.svg == null ? null : sanitizeSvg(v.svg)
  const shot = shotPathOf(v.shot)
  return title || lines.length || svg || shot ? { title, lines, svg, shot } : null
}

// Lựa chọn: 2–5 nhãn ≤ 40 ký tự; hạn mặc định chỉ có khi giáo viên ghi (câu đố/trò chơi: 60 giây, xét lúc chạy).
export function choicesOf(v: unknown): ChoicesSpec | null {
  if (!isObj(v) || !Array.isArray(v.options)) return null
  const options: ChoicesSpec['options'] = []
  for (const o of v.options) {
    if (!isObj(o)) continue
    const label = nonEmpty(o.label)
    if (!label) continue
    const send = nonEmpty(o.send)
    options.push({ label: cutStr(label, 40), ...(send ? { send: cutStr(send, 500) } : {}) })
    if (options.length >= 5) break
  }
  if (options.length < 2) return null
  const def = typeof v.default === 'number' && Number.isInteger(v.default) && v.default >= 0 && v.default < options.length ? v.default : 0
  const t = typeof v.timeout_s === 'number' && Number.isFinite(v.timeout_s) && v.timeout_s > 0 ? Math.min(900, Math.max(5, Math.round(v.timeout_s))) : null
  return { id: cutStr((nonEmpty(v.id) ?? 'chon').replace(/\s+/g, '-'), 40), prompt: cutStr(nonEmpty(v.prompt) ?? '', 120), options, default: def, timeout_s: t }
}

// Nhãn chế độ quyền ở thanh dưới (SessionMode): bỏ nhãn không phải quyền (focus, memory paused).
export function permissionLabel(modes: readonly string[]): string {
  const c = (Array.isArray(modes) ? modes : []).filter((m): m is string => typeof m === 'string').map(m => m.replace(/\s+/g, ' ').trim()).filter(m => m && !/focus|memory|paused/i.test(m))
  const pick = c.find(m => /bypass|auto|plan|accept|manual|ask|default|permission|edit/i.test(m)) ?? c[0] ?? ''
  return pick.length > 40 ? pick.slice(0, 39) + '…' : pick
}
export const isBypass = (label: string) => /bypass/i.test(label)

// Tên model như thanh dưới hiển thị: claude-opus-5-5 → Opus 5.5.
export function modelLabel(m: string): string {
  const x = /claude-([a-z]+)-(\d+)(?:-(\d{1,2})(?!\d))?/i.exec(m)
  if (!x) return m
  const name = (x[1] ?? '').charAt(0).toUpperCase() + (x[1] ?? '').slice(1)
  return `${name} ${x[2]}${x[3] ? `.${x[3]}` : ''}`
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

// Chữ thô của state.json (null = chưa có file hoặc không đọc được).
async function readRaw($: EngineInterface): Promise<string | null> {
  try {
    if (!(await $.fs.exists(STATE))) return null
    const raw = await $.fs.read(STATE)
    return typeof raw === 'string' ? raw : null
  } catch {
    return null
  }
}

function parseRaw(raw: string | null): ClassState | null {
  if (raw == null) return null
  try {
    return parseState(JSON.parse(raw))
  } catch {
    return null
  }
}

// Bản đọc được gần nhất: giáo viên đang ghi dở file (JSON cụt) thì giữ bản cũ, không tụt về "Phần 0".
let goodState: ClassState | null = null
// Chữ state.json lần nạp gần nhất (undefined = chưa nạp lần nào); đồng hồ 1,5 giây so với nó.
let lastRaw: string | null | undefined

async function loadState($: EngineInterface): Promise<ClassState | null> {
  const raw = await readRaw($)
  if (raw == null) {
    goodState = null
    return null
  }
  const s = parseRaw(raw)
  if (s) goodState = s
  return s ?? goodState
}

// ── v0.10: ảnh chụp màn hình có đánh dấu (board.shot) ─────────────────────────────
// Dấu tệp (kích cỡ + giờ sửa) để biết tệp đổi mà không phải đọc lại byte; 'none' = chưa có/không đọc được, 'na' = không có fs.stat.
async function shotFileSig($: EngineInterface, path: string): Promise<{ sig: string; size: number | null }> {
  try {
    const st = await $.fs.stat(path)
    if (st.kind !== 'file') return { sig: 'none', size: null }
    return { sig: `${st.size}:${st.mtimeMs}`, size: st.size }
  } catch (err) {
    const code = isObj(err) ? err.code : undefined
    return { sig: code === 'ENOENT' ? 'none' : 'na', size: null }
  }
}

// Bộ nhớ đệm một ảnh: chỉ đọc lại byte khi state.json đổi (stateVer) hoặc tệp đổi (dấu tệp).
let shotCache: { key: string; drawn: ShotDrawn | null } | null = null
// Dấu tệp ảnh ở nhịp 1,5 giây gần nhất (để vẽ lại khi giáo viên ghi đè ảnh mà không sửa state.json).
let lastShotSig = ''

// Ảnh sẽ vẽ trên Desktop (null = không vẽ: thiếu tệp, quá 96 KB, không phải JPEG/PNG, Svg quá 131 072 ký tự).
async function loadShot($: EngineInterface, path: string, ver: number): Promise<ShotDrawn | null> {
  const { sig, size } = await shotFileSig($, path)
  if (sig === 'none') return null
  const key = `${path}|${ver}|${sig}`
  if (shotCache?.key === key) return shotCache.drawn
  let drawn: ShotDrawn | null = null
  if (size == null || size <= SHOT_MAX_BYTES) {
    try {
      const r = await $.fs.read(path, { as: 'bytes' })
      drawn = shotFromBase64(typeof r === 'string' ? null : r.base64)
    } catch {
      drawn = null
    }
  }
  // Không có fs.stat thì không nhớ kết quả trống (tệp có thể xuất hiện sau, không có dấu để biết).
  if (drawn || sig !== 'na') shotCache = { key, drawn }
  return drawn
}

// Trên terminal chỉ cần biết ảnh có đó và đủ nhỏ (không đọc byte).
async function shotReady($: EngineInterface, path: string): Promise<boolean> {
  const { sig, size } = await shotFileSig($, path)
  if (sig === 'none') return false
  if (size != null) return size <= SHOT_MAX_BYTES
  try {
    return await $.fs.exists(path)
  } catch {
    return false
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
  const raw = await readRaw($)
  const parsed = parseRaw(raw)
  if (parsed) goodState = parsed
  else if (raw == null) goodState = null
  const s = parsed ?? goodState
  if (raw !== lastRaw) {
    lastRaw = raw
    await update($, stateVer, n => n + 1)
  }
  if (s?.language && s.language !== curLang) {
    curLang = s.language
    try {
      await $.store.set('language', curLang)
    } catch {}
  }
  // Có state mà thiếu segment: giữ phần đang hiển thị (không tụt về Phần 0). Không có state: chưa có phần nào.
  const prevLive = await read($, liveAtom)
  const seg = s?.segment ? (SEGMENTS_BY_ID[s.segment.id] ? { ...SEGMENTS_BY_ID[s.segment.id]!, title: s.segment.title || SEGMENTS_BY_ID[s.segment.id]!.title, drive: s.segment.drive } : { id: s.segment.id, title: s.segment.title, drive: s.segment.drive }) : s ? prevLive.segment : null
  const live: LiveState = { activity: s?.activity ?? null, challenge: s?.challenge ?? null, giftBox: s?.gift_box === true, segment: seg, choices: s?.choices ?? null }
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
      $.ui.toast(L().badgeToast(b.label))
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

// ── Lời lớp học (tiếng Việt / tiếng Lào, hooks/i18n.ts) ───────────────────────────
// Ngôn ngữ của lớp: state.json `language` (giáo viên ghi), nhớ trong $.store cho lần mở sau.
let curLang: Lang = 'vi'
const L = () => STR[curLang]
const teacherName = (k: TeacherKind) => STR[curLang].teacherSelf(k)
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
export function delegationPrompt(f: { goal: string; src: string; out: string; check: string }, lang: Lang = curLang): string {
  const d = STR[lang].delegation
  return [d.head, `${d.goal}: ${f.goal.trim()}`, `${d.src}: ${f.src.trim() || d.noSrc}`, `${d.out}: ${f.out.trim() || d.noOut}`, `${d.check}: ${f.check.trim() || d.noCheck}`].join('\n')
}

// Một câu dễ hiểu cho mỗi thao tác công cụ. null = để nguyên dòng gốc.
export function describeTool(tool: string, input: unknown, lang: Lang = curLang): string | null {
  const i = (input ?? {}) as Record<string, unknown>
  const w = STR[lang].tool
  const file = baseName(i.file_path ?? i.notebook_path ?? i.path) || w.aFile
  if (tool === 'Read') return w.read(file)
  if (tool === 'Glob' || tool === 'Grep') return w.find
  if (tool === 'Write') return w.write(file)
  if (tool === 'Edit' || tool === 'NotebookEdit') return w.edit(file)
  if (tool === 'Bash' || tool === 'PowerShell') return w.run
  if (tool === 'WebFetch' || tool === 'WebSearch') return w.web
  if (tool === 'Skill') return w.skill
  if (tool.startsWith('mcp__')) return w.mcp
  return null
}

// Thao tác công cụ có đụng tới sổ lớp (.lop-hoc/): lời giáo viên ghi trạng thái, không phải việc của học viên.
export function touchesLedger(input: unknown): boolean {
  try {
    return typeof input === 'string' ? input.includes('.lop-hoc') : JSON.stringify(input ?? null).includes('.lop-hoc')
  } catch {
    return false
  }
}

// Lựa chọn mặc định của một câu hỏi gốc: phương án ghi "mặc định"/"đề xuất", nếu không thì phương án đầu.
export function defaultLabel(questions: unknown): string {
  const q = Array.isArray(questions) ? questions[0] : undefined
  const opts = isObj(q) && Array.isArray(q.options) ? q.options : []
  const labels = opts.map(o => (isObj(o) && typeof o.label === 'string' ? o.label : '')).filter(Boolean)
  return labels.find(l => /mặc định|đề xuất|recommended/i.test(l)) ?? labels[0] ?? 'phương án đầu'
}


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

function shownSeg(l: Lesson | null, live: LiveState): PlanSegment | null {
  if (!l || l.over) return null
  return live.segment ?? S0
}

// Giáo viên và phần học đang hiển thị, tính lại từ trạng thái hiện tại (không dựa vào bộ nhớ đệm của nhịp trước).
async function classView($: EngineInterface): Promise<typeof view> {
  const lesson = await read($, lessonAtom)
  const live = await read($, liveAtom)
  view = { teacher: lesson?.teacher ?? view.teacher, seg: shownSeg(lesson, live) }
  return view
}

async function refreshUsage($: EngineInterface) {
  try {
    // Không đọc được tên model thì vẫn đọc hạn mức (hạn mức cần cho tín hiệu ngưỡng).
    let model: unknown = ''
    try {
      model = await $.session.model()
    } catch {}
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
    return { ...l, ...patch, sent: [...l.sent, key], lastCueAt: now, quiet: true }
  })
  if (claimed) void submitCue($, text)
  return claimed
}

// Tín hiệu do học viên bấm: gửi ngay (giáo viên đang làm thì chờ đến lượt).
async function sendPressCue($: EngineInterface, text: string, patch: Partial<Lesson> = {}) {
  const now = await $.clock.now()
  await update($, lessonAtom, l => (l ? { ...l, ...patch, lastCueAt: now, quiet: false } : l))
  await update($, silenceAtom, () => ({ at: now, rung: 0 }))
  await submitCue($, text)
}

// Học viên vừa tác động: lớp được gửi tín hiệu kế tiếp.
async function touch($: EngineInterface) {
  await update($, lessonAtom, l => (l && !l.over && l.quiet ? { ...l, quiet: false } : l))
  await silenceReset($)
}

// Học viên vừa tác động (gửi, bấm, chọn, gõ): thang im lặng tính lại từ đầu.
async function silenceReset($: EngineInterface) {
  const now = await $.clock.now()
  await update($, silenceAtom, () => ({ at: now, rung: 0 }))
}

// Tín hiệu im lặng: không khoá `sent`, vượt qua `quiet` (chỉ ba tín hiệu này), vẫn đặt quiet để các tín hiệu khác chờ.
async function sendSilenceCue($: EngineInterface, rung: 1 | 2 | 3, now: number): Promise<boolean> {
  let ok = false
  await update($, lessonAtom, l => {
    if (!l || l.over || l.pause) return l
    ok = true
    return { ...l, lastCueAt: now, quiet: true }
  })
  if (!ok) return false
  await update($, silenceAtom, () => ({ at: now, rung }))
  void submitCue($, `Học viên im lặng · nấc ${rung}`)
  return true
}

// Quay lại sau Xin phép, hoặc Tiếp tục sau khi mở lại app.
async function resume($: EngineInterface): Promise<Lesson['pause']> {
  const now = await $.clock.now()
  let was: Lesson['pause'] = null
  await update($, lessonAtom, l => {
    if (!l || !l.pause || l.over) {
      was = null
      return l
    }
    was = l.pause
    return { ...l, pause: null, pauseNote: '', shiftMs: l.shiftMs + (now - (l.pausedAt ?? now)), pausedAt: null, quiet: false }
  })
  if (was) await update($, silenceAtom, () => ({ at: now, rung: 0 }))
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

// Câu đố / trò chơi để quá 60 giây: giáo viên chọn giúp lựa chọn mặc định.
async function answerTimeout($: EngineInterface, ask: AskOpen, now: number) {
  await update($, askAtom, a => (a && a.id === ask.id ? { ...a, handled: true } : a))
  try {
    $.ui.notice(ask.id, undefined)
  } catch {}
  // Mod không bấm được vào hộp gốc; đóng lượt đang chờ rồi báo giáo viên lựa chọn mặc định.
  // Đây là tín hiệu của chính câu hỏi giáo viên vừa hỏi, nên gửi cả khi lớp đang chờ.
  if (await abortTurn($)) {
    await update($, lessonAtom, l => (l ? { ...l, quiet: false } : l))
    await sendKeyedCue($, `ask-${ask.id}`, `Hết hạn trả lời · chọn giúp ${ask.label}`, now, {})
  }
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
  const live = await read($, liveAtom)
  view = { teacher: l.teacher, seg: shownSeg(l, live) }
  // Kiểu tương tác đang dùng (giờ lớp mở) và đồng hồ giây cho thử thách.
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
  // Đang gõ = học viên đang tác động.
  if (box && !l.pause) {
    if (l.quiet) {
      await touch($)
      l = (await read($, lessonAtom)) ?? l
    } else await silenceReset($)
  }

  // A. Câu đố / trò chơi: đếm ngược 60 giây, hết hạn thì chọn giúp. Câu hỏi lúc làm việc thật: chờ, không đếm.
  //    Đang có thử thách chạy giờ thì tạm ngưng: hạn 60 giây tính lại từ lúc thử thách xong.
  const timed = timedKind(live.activity?.kind)
  if (ask && !ask.handled && ch && ch.leftMs > 0) {
    const a = ask
    await update($, askAtom, () => ({ ...a, openedAt: now }))
    ask = await read($, askAtom)
  }
  if (ask && !ask.handled && timed && !l.pause && !(ch && ch.leftMs > 0)) {
    const left = ANSWER_MS - (now - ask.openedAt)
    if (left > 0) {
      try {
        $.ui.notice(ask.id, L().pickFor(teacherName(l.teacher), mmss(left)))
      } catch {}
    } else {
      await answerTimeout($, ask, now)
      return
    }
  }

  // A2. Hộp câu hỏi gốc (không phải câu đố/trò chơi) mở quá 90 giây: báo giáo viên một lần để giúp mà không đóng hộp.
  if (ask && !ask.handled && !timed && !l.pause && !(ch && ch.leftMs > 0) && now - ask.openedAt >= LONG_BOX_MS) {
    await sendKeyedCue($, `long-${ask.id}`, `Hộp chờ lâu · ${ask.label}`, now, {})
    l = (await read($, lessonAtom)) ?? l
  }

  // B. Tín hiệu do mod gửi: chỉ khi giáo viên rảnh, ô nhập trống, lớp không xin phép/chờ, không có hộp câu hỏi mở,
  //    cách tín hiệu trước ≥ 20 giây (mỗi lúc một tín hiệu). Các tín hiệu theo giờ còn cần học viên đã tác động
  //    từ tín hiệu trước (lớp không giảng vào phòng trống); riêng thang im lặng (v0.11) đi qua chốt đó.
  if (l.pause || working || ask || box || now - l.lastCueAt < CUE_GAP_MS) return
  if (!l.quiet) {
    // Hạn mức chạm ngưỡng.
    const uc = usageCue(await read($, usageAtom), l.sent)
    if (uc) {
      await update($, lessonAtom, x => (x ? { ...x, sent: [...x.sent, ...uc.also.filter(k => !x.sent.includes(k))] } : x))
      if (await sendKeyedCue($, uc.key, uc.text, now, {})) return
    }
    // Hết giờ thử thách (một lần, bỏ thử thách cũ quá 10 phút).
    if (live.challenge && ch && ch.leftMs <= 0) {
      if (await sendKeyedCue($, `ch-${challengeKey(live.challenge)}`, `Hết giờ thử thách · ${live.challenge.title}`, now, {})) return
    }
    // Cùng một kiểu tương tác quá 4 phút → nhắc giáo viên đổi kiểu (một lần). Lúc làm việc thật thì không nhắc.
    if (live.activity && switchableKind(live.activity.kind) && track && el - track.fromEl > ACTIVITY_MS) {
      const n = Math.floor((el - track.fromEl) / MIN)
      if (await sendKeyedCue($, `act-${track.key}`, `Đổi kiểu tương tác · ${live.activity.kind} · ${n} phút`, now, {})) return
    }
  }
  // Thang im lặng: nấc 1 · 2 · 3 sau lần giáo viên nói xong, dừng sau nấc 3 đến khi học viên tác động.
  if (!(await read($, entered))) return
  const slow = !!(ch && ch.leftMs > 0) || live.activity?.kind === 'hands-on' || live.activity?.kind === 'form'
  const rung = silenceDue(await read($, silenceAtom), now, slow)
  if (rung) await sendSilenceCue($, rung, now)
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

// ── v0.8: nhịp 1,5 giây — nạp lại state.json khi chữ đổi, báo đổi chế độ quyền, hẹn giờ lựa chọn ──
let watching = false
// Nhãn ở thanh dưới ô nhập mới nhất do SessionMode đưa tới (mod chỉ đọc).
let curModes: string[] = []
// Nhãn chế độ quyền đã báo giáo viên (null = chưa biết, lần đọc kế tiếp chỉ ghi nhớ, không báo).
let modeSent: string | null = null
// Lúc bục bắt đầu chờ học viên bấm lựa chọn hiện tại (không tính lúc giáo viên đang giảng).
let choiceSince: { key: string; at: number } | null = null
const choiceKey = (c: ChoicesSpec, ver: number) => `${c.id}@${ver}`

async function watchTick($: EngineInterface) {
  if (watching) return
  watching = true
  try {
    await watchBody($)
  } catch {
    // Một nhịp lỗi không làm dừng đồng hồ.
  } finally {
    watching = false
  }
}

async function watchBody($: EngineInterface) {
  if (!(await read($, isClassroom))) return
  const raw = await readRaw($)
  if (raw !== lastRaw) {
    await syncState($)
    await update($, rev, n => n + 1)
  }
  await shotTick($)
  const cur = await read($, modesAtom)
  if (cur.length !== curModes.length || cur.some((m, i) => m !== curModes[i])) await update($, modesAtom, () => curModes)
  await modeTick($)
  await choiceTick($)
}

// Giáo viên ghi đè ảnh chụp (cùng đường dẫn, state.json không đổi): vẽ lại bảng.
async function shotTick($: EngineInterface) {
  const path = goodState?.board?.shot ?? null
  if (!path) {
    lastShotSig = ''
    return
  }
  const { sig } = await shotFileSig($, path)
  const next = `${path}|${sig}`
  if (next === lastShotSig) return
  const first = lastShotSig === ''
  lastShotSig = next
  if (!first) await update($, rev, n => n + 1)
}

// Học viên đổi chế độ quyền ở thanh dưới: báo giáo viên một lần mỗi lần đổi (chờ khi đang xin phép).
async function modeTick($: EngineInterface) {
  const l = await read($, lessonAtom)
  if (!l || l.over) return
  const label = permissionLabel(curModes)
  if (modeSent === null) {
    modeSent = label
    return
  }
  if (label === modeSent || l.pause) return
  modeSent = label
  await sendPressCue($, `Chế độ quyền · ${label || 'mặc định'}`)
}

// Lựa chọn trên bục hết hạn mà học viên chưa bấm: báo giáo viên một lần, tô đậm lựa chọn mặc định. Mod không bấm thay.
async function choiceTick($: EngineInterface) {
  const l = await read($, lessonAtom)
  const live = await read($, liveAtom)
  const c = live.choices
  if (!l || l.over || l.pause || !c) {
    choiceSince = null
    return
  }
  const key = choiceKey(c, await read($, stateVer))
  if ((await read($, choiceDone)) === key || (await read($, choiceExpired)) === key) return
  const limit = c.timeout_s ?? (timedKind(live.activity?.kind) ? 60 : null)
  if (limit == null) return
  const now = await $.clock.now()
  if (await read($, workingAtom)) {
    choiceSince = null
    return
  }
  if (!choiceSince || choiceSince.key !== key) choiceSince = { key, at: now }
  let box = ''
  try {
    box = (await $.prompt.read()).text.trim()
  } catch {}
  if (box || now - choiceSince.at < limit * 1000) return
  await update($, choiceExpired, () => key)
  await sendKeyedCue($, `choice-${key}`, `Hết hạn chọn · ${c.id}`, now, {})
}

// Học viên đã bấm một lựa chọn (hoặc tự gõ câu trả lời): ẩn nhóm lựa chọn này đến khi state.json được ghi lại.
async function markChoicesDone($: EngineInterface) {
  const c = (await read($, liveAtom)).choices
  if (c) {
    const key = choiceKey(c, await read($, stateVer))
    await update($, choiceDone, () => key)
  }
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

// Mở lại app: lớp vẫn mở (lớp luôn mở), ở trạng thái chờ — bấm Tiếp tục để học tiếp từ chỗ đã lưu.
// Nhận cả lớp lưu từ bản 0.6 (có thời lượng): chỉ giữ giáo viên, giờ mở lớp và các tín hiệu đã gửi.
async function restoreLesson($: EngineInterface) {
  if (await read($, lessonAtom)) return
  const key = await storeKey($)
  if (!key) return
  try {
    const saved = await $.store.get(key)
    if (!isObj(saved) || !isObj(saved.lesson) || typeof saved.savedAt !== 'number') return
    const l = saved.lesson as Record<string, unknown>
    if (l.over || typeof l.startedAt !== 'number' || !Array.isArray(l.sent) || !isTeacherKind(l.teacher)) return
    const restored: Lesson = {
      teacher: l.teacher,
      startedAt: l.startedAt,
      shiftMs: typeof l.shiftMs === 'number' ? l.shiftMs : 0,
      pausedAt: typeof l.pausedAt === 'number' ? l.pausedAt : saved.savedAt,
      pause: 'cho',
      pauseNote: '',
      over: null,
      sent: (l.sent as unknown[]).filter((x): x is string => typeof x === 'string'),
      lastCueAt: typeof l.lastCueAt === 'number' ? l.lastCueAt : saved.savedAt,
      quiet: false,
    }
    await update($, lessonAtom, () => restored)
    await update($, entered, () => true)
  } catch {}
}

function usagePart(u: UsageInfo | null): string {
  if (!u) return ''
  const five = u.five ? `5 giờ ${Math.round(u.five.percentUsed)}%` : ''
  const week = u.week ? `tuần ${Math.round(u.week.percentUsed)}%` : ''
  return five || week ? ` · hạn mức ${[five, week].filter(Boolean).join(' · ')}` : ''
}

async function startLesson($: EngineInterface) {
  const now = await $.clock.now()
  const teacher = await read($, teacherPick)
  const usage = await read($, usageAtom)
  const lesson: Lesson = {
    teacher,
    startedAt: now,
    shiftMs: 0,
    pausedAt: null,
    pause: null,
    pauseNote: '',
    over: null,
    sent: ['open', ...usageKeysCrossed(usage)],
    lastCueAt: now,
    quiet: false,
  }
  await update($, lessonAtom, () => lesson)
  await update($, entered, () => true)
  await update($, modeAtom, () => 'normal')
  await update($, nowAtom, () => now)
  await update($, silenceAtom, () => ({ at: now, rung: 0 }))
  await update($, activityTrack, () => null)
  await update($, giftAtom, () => 'closed')
  view = { teacher, seg: S0 }
  choiceSince = null
  modeSent = permissionLabel(curModes)
  try {
    await $.store.set('teacher', teacher)
  } catch {}
  const effort = await read($, effortAtom)
  const open = [
    `giáo viên ${teacher}`,
    modeSent ? `chế độ ${modeSent}` : '',
    usage?.model ? `model ${usage.model}` : '',
    effort ? `effort ${effort}` : '',
  ].filter(Boolean)
  await submitCue($, `Mở lớp · ${open.join(' · ')}${usagePart(usage)}`)
}

async function loadPrefs($: EngineInterface) {
  try {
    const t = await $.store.get('teacher')
    if (isTeacherKind(t)) await update($, teacherPick, () => t)
    const lg = await $.store.get('language')
    curLang = isLang(lg) ? lg : 'vi'
  } catch {}
}

async function setup($: EngineInterface) {
  const ok = await detectClassroom($)
  await update($, isClassroom, () => ok)
  if (!ok) return false
  await loadPrefs($)
  await restoreLesson($)
  await syncState($)
  await refreshUsage($)
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
      $.clock.every(WATCH_MS, () => void watchTick($))
    }
    return next(e)
  })

  // Chế độ quyền ở thanh dưới ô nhập: chỉ đọc, giữ nguyên thanh gốc (next(e) không đổi).
  on('ui.render', { component: 'SessionMode' }, async ($, e, next) => {
    // Vẽ là thuần (không ghi state): chỉ nhớ nhãn vào biến của mod; nhịp 1,5 giây chép sang atom và báo đổi.
    if (Array.isArray(e.props.modes)) curModes = e.props.modes.filter((m): m is string => typeof m === 'string')
    return next(e)
  }).catch(($, e, next) => next(e))

  // /clear, /resume, /branch xoá $.state: nhận lại lớp học và lựa chọn đã lưu.
  on('classic.SessionStart', { source: ['clear', 'resume', 'fork'] }, async ($, e, next) => {
    await setup($)
    return next(e)
  }).catch(($, e, next) => next(e))

  on('command.run', { command: 'lop-hoc' }, async $ => {
    await $.ui.open({ id: PANE, title: TITLE })
    return { text: 'Đã mở bảng tóm tắt Lớp học NNC.' }
  })

  // Học viên tự gửi một câu = đang tác động; đang xin phép/chờ thì vào lại lớp và báo giáo viên kèm câu đó.
  on('prompt.submit', async ($, e, next) => {
    if (!(await read($, isClassroom))) return next(e)
    const kind = (e.origin as { kind?: string } | undefined)?.kind
    if (kind && !PERSON_ORIGINS.has(kind)) return next(e)
    if (e.text.trimStart().startsWith(CUE.trim())) return next(e)
    const was = await resume($)
    await touch($)
    // Học viên tự gõ câu trả lời: nhóm lựa chọn trên bục coi như đã trả lời (không hết hạn).
    await markChoicesDone($)
    if (was) return next({ ...e, context: [...(e.context ?? []), `${CUE}Học viên trở lại`] })
    return next(e)
  }).catch(($, e, next) => next(e))

  // Dùng nút / ô / lựa chọn của mod khác cũng là tác động (nút của lớp tự ghi nhận trong handler).
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
    await update($, workingAtom, () => false)
    await update($, turnIdAtom, () => '')
    askSeen = null
    if (await read($, isClassroom)) {
      // Giáo viên nói xong: thang im lặng đếm từ đây (nấc đã gửi giữ nguyên, chỉ học viên tác động mới xoá).
      const doneAt = await $.clock.now()
      await update($, silenceAtom, x => ({ ...x, at: doneAt }))
      await update($, askAtom, () => null)
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
    const effort = await read($, effortAtom)
    const line = claudeLine(usage, effort)
    await read($, modesAtom)
    const modeLabel = permissionLabel(curModes)
    const s = await loadState($)
    const running = !!lesson && !lesson.over
    const kind: TeacherKind = lesson?.teacher ?? (await read($, teacherPick))
    const T = teacherName(kind)
    const t = teacherLower(kind)
    const S = L()
    const address = cap(s?.address || (curLang === 'lo' ? 'ເຈົ້າ' : 'anh/chị'))
    const live = await read($, liveAtom)
    const seg = shownSeg(lesson, live)
    view = { teacher: kind, seg }
    // Huy hiệu mới: giáo viên vui (hỉ) 6 giây, đè cảm xúc giáo viên ghi.
    const emotion: Emotion = (await read($, cheerAtom)) ? 'hi' : (s?.teacher?.emotion ?? 'giang')
    const presence: TeacherPresence = !running ? 'wait' : lesson.pause === 'cho' ? 'away' : lesson.pause ? 'wait' : 'present'

    // Cỡ bục do giáo viên chọn (mini · normal · wide); chưa vào lớp thì cỡ rộng như cũ.
    const spec: PodiumSpec = s?.podium ?? { size: 'normal', show: [], point: null, buttons: [] }
    const size = running ? spec.size : 'wide'
    const dims = AVATAR_DIMS[size]
    let podium = null
    if (isDesktop) {
      const { Svg } = $.ui.resolve(e)
      podium = <Svg key="podium" source={teacherPodiumSvg(kind, running ? emotion : 'hi', presence)} alt={curLang === 'lo' ? `${T} ຢູ່ກະດານ` : `${T} trên bục giảng`} width={dims.w} height={dims.h} isInteractive />
    }
    // Chế độ Bypass: nhãn cảnh báo luôn thấy được trên bục.
    const bypassChip = isBypass(modeLabel) ? <Text key="bypass" bold color={INK} backgroundColor={ALERT}>{L().bypassChip(modeLabel)}</Text> : null
    const board = (children: RenderChildren[], gap = 1) => (
      <Box flexDirection="row" gap={2} alignItems="center" backgroundColor={BOARD} paddingX={1} paddingY={1}>
        {podium}
        <Box flexDirection="column" gap={gap} flexGrow={1}>
          {children}
        </Box>
      </Box>
    )
    const claudeRow = line ? <Text color={CHALK_DIM}>{S.myClaude(line)}</Text> : null
    const pick = (key: string, label: string, isOn: boolean, onPress: () => unknown) =>
      isOn ? <Button key={key} label={label} variant="primary" onPress={onPress} /> : <Button key={key} label={label} onPress={onPress} />

    // Chưa vào lớp (hoặc đã xin nghỉ): chọn giáo viên rồi Vào lớp. Lớp luôn mở, không chọn thời lượng.
    if (!running) {
      const tp = await read($, teacherPick)
      return board([
        <Text bold color={CHALK_Y}>{S.title}</Text>,
        bypassChip,
        lesson?.over === 'xin-nghi' ? <Text color={CHALK}>{S.leftSaved(t)}</Text> : null,
        <Text color={CHALK}>{S.waiting}</Text>,
        // Chưa biết học viên dùng tiếng nào: thêm một dòng bằng thứ tiếng còn lại.
        <Text color={CHALK_DIM}>{STR[curLang === 'lo' ? 'vi' : 'lo'].waiting}</Text>,
        <Box flexDirection="row" gap={1} alignItems="center" flexWrap="wrap">
          <Text color={CHALK_DIM}>{S.teacherWord}</Text>
          {TEACHERS.map(x => pick(`t-${x.id}`, S.teacherLabel(x.id), tp === x.id, () => update($, teacherPick, () => x.id)))}
        </Box>,
        claudeRow,
        <Box flexDirection="row" gap={1}>
          <Button key="enter" label={S.enter} variant="primary" onPress={() => startLesson($)} />
        </Box>,
      ])
    }

    const xinNghi = <Button key="xin-nghi" label={S.leave} onPress={async () => {
      await update($, modeAtom, () => 'normal')
      await sendPressCue($, 'Xin nghỉ', { over: 'xin-nghi', pause: null, pausedAt: null })
    }} />

    // Mở lại app: lớp vẫn mở, giáo viên chờ học viên bấm Tiếp tục.
    if (lesson.pause === 'cho') {
      return board([
        <Text bold color={CHALK_Y}>{S.waitingResume(T, t)}</Text>,
        <Box flexDirection="row" gap={1}>
          <Button key="tiep-tuc" label={S.resume} variant="primary" onPress={async () => {
            if (await resume($)) await sendPressCue($, 'Học viên trở lại')
          }} />
          {xinNghi}
        </Box>,
      ])
    }

    // Xin phép: lớp chờ học viên quay lại.
    if (lesson.pause === 'xin-phep') {
      return board([
        <Text bold color={CHALK_Y}>{S.inBreak(S.reasons.find(r => r.vi === lesson.pauseNote)?.label ?? lesson.pauseNote)}</Text>,
        <Text color={CHALK_DIM}>{S.keepSeat(T, address.toLowerCase())}</Text>,
        <Box flexDirection="row" gap={1}>
          <Button key="quay-lai" label={S.backToClass} variant="primary" onPress={async () => {
            if (await resume($)) await sendPressCue($, 'Học viên trở lại')
          }} />
          {xinNghi}
        </Box>,
      ])
    }

    if (mode === 'xin-phep') {
      // Nhãn theo tiếng của học viên; tín hiệu gửi giáo viên luôn bằng tiếng Việt.
      const reason = (key: string, label: string, vi: string) => (
        <Button key={key} label={label} onPress={async () => {
          const at = await $.clock.now()
          await update($, modeAtom, () => 'normal')
          await sendPressCue($, `Xin phép · ${vi}`, { pause: 'xin-phep', pausedAt: at, pauseNote: vi })
        }} />
      )
      return board([
        <Text bold color={CHALK_Y}>{S.chooseReason(t)}</Text>,
        <Box flexDirection="row" gap={1} flexWrap="wrap">
          {S.reasons.map(r => reason(r.key, r.label, r.vi))}
          <Button key="xin-phep-thoi" label={S.cancel} onPress={() => update($, modeAtom, () => 'normal')} />
        </Box>,
      ])
    }

    if (mode === 'gio-tay' && (e.surface === 'desktop' || e.surface === 'terminal')) {
      const { Input } = $.ui.resolve(e)
      return board([
        <Text bold color={CHALK_Y}>{S.raised(address, t)}</Text>,
        <Input key="ke" label={S.tellLabel(t)} placeholder={S.tellPlaceholder} value="" submitLabel={S.send} autoFocus onSubmit={async (v: string) => {
          const text = v.trim()
          if (!text) return
          await update($, modeAtom, () => 'normal')
          await touch($)
          await $.prompt.submit({ text, asUser: true })
        }} />,
        <Box flexDirection="row" gap={1}>
          <Button key="gio-tay-thoi" label={S.cancel} onPress={() => update($, modeAtom, () => 'normal')} />
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
        <Text bold color={CHALK_Y}>{S.formTitle}</Text>,
        field('goal', ...S.formFields.goal),
        field('src', ...S.formFields.src),
        field('out', ...S.formFields.out),
        field('check', ...S.formFields.check),
        formError ? <Text color={ALERT}>{formError}</Text> : null,
        <Box flexDirection="row" gap={1}>
          <Button key="form-fill" label={S.formFill} variant="primary" onPress={async () => {
            if (!draft.goal.trim()) {
              formError = S.formGoalFirst
              await update($, rev, n => n + 1)
              return
            }
            formError = ''
            await touch($)
            await $.prompt.fill({ text: delegationPrompt(draft), mode: 'replace' })
            draft = { goal: '', src: '', out: '', check: '' }
            await update($, modeAtom, () => 'normal')
            $.ui.toast(S.formToast)
          }} />
          <Button key="form-cancel" label={S.formClose} onPress={() => update($, modeAtom, () => 'normal')} />
        </Box>,
      ])
    }

    // Bình thường: phần học (giáo viên ghi khi đạt mốc), lượt của học viên, nút.
    const shown = seg ?? S0
    const drive = shown.drive
    const ask = await read($, askAtom)
    const working = e.props.isWorking
    const parts = s?.status === 'active' ? (s.result_parts ?? []) : []
    const panel = s?.panel ?? null
    const isPractice = shown.id === '2' || shown.id === '3'
    const timedAsk = timedKind(live.activity?.kind)
    const loops = typeof s?.loops_done === 'number' && s.loops_done > 0 ? s.loops_done : 0

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
        <Text bold color={CHALK_Y}>{S.usageTitle}</Text>,
        ...pics,
        five ? <Text color={CHALK}>{S.usageFive(Math.round(five.percentUsed), resetTime(five.resetsAt))}</Text> : null,
        week ? <Text color={CHALK}>{S.usageWeek(Math.round(week.percentUsed), resetDay(week.resetsAt))}</Text> : null,
        !five && !week ? <Text color={CHALK_DIM}>{S.usageUnknown(t)}</Text> : null,
      ]
    } else if (panel === 'claude') {
      panelRows = [
        <Text bold color={CHALK_Y}>{S.mine}</Text>,
        <Text color={CHALK}>{line || S.usageUnknown(t)}</Text>,
        <Text color={CHALK_DIM}>{S.mineHelp}</Text>,
      ]
    }

    const headline = working ? S.working(T, address.toLowerCase()) : `${S.yourTurn}${s?.next_action ? ` · ${cut(s.next_action, 80)}` : ''}`

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
          $.ui.toast(S.oneTouchToast)
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
        extras.push(<Svg key="stars" source={src} alt={S.starsAlt(stars)} {...svgSize(src, 24 * Math.min(stars, 5) + 40, 24)} />)
      } else {
        extras.push(<Text key="stars" color={CHALK_Y}>{`★ ${stars}`}</Text>)
      }
    }
    if (badges.length) {
      if (isDesktop) {
        const { Svg } = $.ui.resolve(e)
        const shelf: BadgeRef[] = allBadges.map(b => ({ id: b.id, label: b.label }))
        const src = badgeShelfSvg(shelf)
        extras.push(<Svg key="badges" source={src} alt={`${S.badgesText}: ${badges.map(b => b.label).join(', ')}`} {...svgSize(src, 240, 56)} />)
      } else {
        const more = allBadges.length - badges.length
        extras.push(<Text key="badges" color={CHALK}>{`${S.badgesText}: ${badges.map(b => cut(b.label, 24)).join(' · ')}${more > 0 ? ` · +${more}` : ''}`}</Text>)
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
      let pic: RenderChildren = <Text color={CHALK_Y}>{isOpen ? S.giftOpening : S.giftWaiting}</Text>
      if (isDesktop) {
        const { Svg } = $.ui.resolve(e)
        const src = giftBoxSvg(isOpen)
        pic = <Svg key="gift" source={src} alt={isOpen ? 'Hộp quà đang mở' : 'Hộp quà'} {...svgSize(src, 64, 64)} />
      }
      giftRow = (
        <Box flexDirection="row" gap={1} alignItems="center">
          {pic}
          {isOpen ? null : <Button key="hop-qua" label={S.giftOpen} variant="primary" onPress={async () => {
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
        <Text backgroundColor={DRIVE_COLOR[drive]} color={INK}>{` ${S.part} ${shown.id} · ${curLang === 'vi' ? shown.title : (S.segments[shown.id] ?? shown.title)} `}</Text>
        <Text color={CHALK_DIM}>{loops ? S.loops(T, loops) : T}</Text>
      </Box>
    )
    const headRow = <Text bold={!working} color={working ? CHALK_DIM : CHALK_Y}>{headline}</Text>
    const askRow = ask && !ask.handled && timedAsk ? <Text color={CHALK}>{S.pickFor(T, mmss(ANSWER_MS - (now - ask.openedAt)))}</Text> : null
    // Hộp câu hỏi gốc (không phải câu đố/trò chơi) mở từ 90 giây: bục tự nhắc chọn dòng đầu, cho tới khi hộp đóng.
    const waitHint = ask && !ask.handled && !timedAsk && now - ask.openedAt >= LONG_BOX_MS ? <Text key="wait-hint" bold color={INK} backgroundColor={CHALK_Y}>{` ${S.waitHint(t)} `}</Text> : null
    const helpRow = s?.help_needed ? (
      <Box flexDirection="row" gap={1} alignItems="center" flexWrap="wrap">
        <Text bold color={INK} backgroundColor={ALERT}>{S.helpNeeded}</Text>
        <Button key="nho-ho-tro" label={S.helpButton} onPress={async () => {
          await touch($)
          await $.prompt.submit({ text: `${TAG}Soạn tin nhờ hỗ trợ`, asUser: true })
        }} />
      </Box>
    ) : null
    const destRow = s?.destination ? <Text color={CHALK_DIM}>{`${S.dest}: ${cut(s.destination, 80)}`}</Text> : null
    const partsRow = parts.length ? (
      <Box flexDirection="row" gap={2} flexWrap="wrap">
        {parts.map((p, i) => (
          <Text key={`rp-${i}`} color={p.done ? CHALK_Y : CHALK_DIM}>{`${p.done ? '✓' : '○'} ${cut(p.label, 30)}`}</Text>
        ))}
      </Box>
    ) : null
    // ── v0.8: sân khấu do giáo viên dựng ─────────────────────────────────────
    const isMini = size === 'mini'
    const ver = await read($, stateVer)
    // Nhãn thông tin sống: ẩn theo mặc định; chỉ hiện cái giáo viên ghi trong show, và cái đang chỉ (point).
    const pointed = spec.point
    const factIds = [...spec.show, ...(pointed && !spec.show.includes(pointed) ? [pointed] : [])]
    const pctOf = (id: FactId | null): number | null =>
      id === 'usage5' ? (usage?.five?.percentUsed ?? null) : id === 'usageWeek' ? (usage?.week?.percentUsed ?? null) : (usage?.context ?? null)
    const factValue = (id: FactId): string => {
      if (id === 'mode') return modeLabel
      if (id === 'effort') return cap(effort)
      if (id === 'model') return usage?.model ? modelLabel(usage.model) : ''
      const p = pctOf(id)
      return p == null ? '' : `${Math.round(p)}%`
    }
    const factChips: RenderChildren[] = []
    for (const id of factIds) {
      const v = factValue(id)
      if (id === 'mode' && !v) continue
      if (id === pointed) factChips.push(<Text key={`fact-${id}`} bold color={INK} backgroundColor={CHALK_Y}>{` ▼ ${S.facts[id]} ${v || '…'} `}</Text>)
      else if (v) factChips.push(<Text key={`fact-${id}`} color={CHALK}>{`${S.facts[id]} ${v}`}</Text>)
    }
    const factsRow = factChips.length && panel !== 'claude' ? (
      <Box flexDirection="row" gap={2} flexWrap="wrap">
        {factChips}
      </Box>
    ) : null

    // Chỉ vào thanh dưới ô nhập: hình thanh với vùng được tô vàng và mũi tên (desktop), hoặc một dòng chữ (terminal).
    let pointRow: RenderChildren = null
    if (pointed) {
      const areaText = factValue(pointed)
      const barOpts = { mode: modeLabel, model: usage?.model ? modelLabel(usage.model) : '', effort: cap(effort), percent: pctOf(pointed === 'mode' || pointed === 'model' || pointed === 'effort' ? 'context' : pointed), point: pointed }
      let mock: RenderChildren
      if (isDesktop) {
        const { Svg } = $.ui.resolve(e)
        const bd = BAR_DIMS[size]
        mock = <Svg key="bar-mock" source={bottomBarSvg(barOpts)} alt={S.barAlt(`${S.facts[pointed]}${areaText ? ` ${areaText}` : ''}`)} width={bd.w} height={bd.h} />
      } else {
        const seg = (id: FactId, text: string) => (id === pointed ? <Text key={`bar-${id}`} bold color={INK} backgroundColor={CHALK_Y}>{`▼ ${text}`}</Text> : <Text key={`bar-${id}`} color={CHALK}>{text}</Text>)
        mock = (
          <Box key="bar-mock" flexDirection="row" gap={2}>
            {seg('mode', modeLabel || '—')}
            {seg('model', barOpts.model || '—')}
            {seg('effort', barOpts.effort || '—')}
            {seg(pointed === 'usage5' || pointed === 'usageWeek' ? pointed : 'context', barOpts.percent != null ? `◔ ${Math.round(barOpts.percent)}%` : '◔')}
          </Box>
        )
      }
      pointRow = (
        <Box flexDirection="column">
          {mock}
          <Text bold color={CHALK_Y}>{`▲ ${S.barNote}`}</Text>
        </Box>
      )
    }

    // Bảng nhỏ (slide): tiêu đề, ≤ 5 dòng, hình SVG đã lọc (terminal chỉ có chữ).
    // v0.10: ảnh chụp màn hình có đánh dấu (shot) thắng svg; không vẽ được ảnh thì quay về svg. Terminal: một dòng chữ thay ảnh.
    const bd = s?.board ?? null
    let boardRow: RenderChildren = null
    if (bd) {
      let pic: RenderChildren = null
      let shotNote: RenderChildren = null
      const drawn = bd.shot && isDesktop ? await loadShot($, bd.shot, ver) : null
      if (drawn) {
        const { Svg } = $.ui.resolve(e)
        pic = <Svg key="board-shot" source={drawn.svg} alt={S.shotAlt(bd.title || '')} {...svgBox(drawn.svg, SHOT_W[size], SHOT_H)} />
      } else if (bd.shot && !isDesktop && (await shotReady($, bd.shot))) {
        shotNote = <Text key="board-shot-note" bold color={CHALK_Y}>{S.shotNote(T)}</Text>
      } else if (isDesktop && bd.svg) {
        const { Svg } = $.ui.resolve(e)
        pic = <Svg key="board-svg" source={bd.svg} alt={S.boardAlt(bd.title || '')} {...svgBox(bd.svg, BOARD_W[size])} />
      }
      boardRow = (
        <Box flexDirection="column" borderStyle="round" borderColor={CHALK_Y} paddingX={1}>
          {bd.title ? <Text bold color={CHALK_Y}>{bd.title}</Text> : null}
          {pic}
          {shotNote}
          {bd.lines.map((x, i) => (
            <Text key={`bl-${i}`} color={CHALK}>{x}</Text>
          ))}
        </Box>
      )
    }

    // Lựa chọn: nút lớn, không chặn ô nhập; bấm gửi một lần rồi ẩn đến khi state.json được ghi lại.
    const cs = live.choices
    const csKey = cs ? choiceKey(cs, ver) : ''
    const csExpired = !!cs && (await read($, choiceExpired)) === csKey
    const choicesRow = cs && !working && (await read($, choiceDone)) !== csKey ? (
      <Box flexDirection="column" gap={1}>
        {cs.prompt ? <Text bold color={CHALK_Y}>{cs.prompt}</Text> : null}
        <Box flexDirection="row" gap={2} flexWrap="wrap">
          {cs.options.map((o, i) => {
            const star = csExpired && i === cs.default
            const label = star ? `★ ${o.label}` : o.label
            const onPress = async () => {
              await markChoicesDone($)
              await touch($)
              await $.prompt.submit({ text: o.send ?? `${TAG}Chọn · ${cs.id} · ${o.label}`, asUser: true })
            }
            return star ? <Button key={`choice-${i}`} label={label} variant="primary" onPress={onPress} /> : <Button key={`choice-${i}`} label={label} onPress={onPress} />
          })}
        </Box>
        {csExpired ? <Text color={CHALK_DIM}>{S.choiceExpired(t)}</Text> : null}
      </Box>
    ) : null

    // Nút phụ: các nút giáo viên chọn (podium.buttons); Giơ tay · Xin phép · Xin nghỉ luôn với tới được qua nhóm "⋯".
    const btn: Record<PodiumButtonId, () => RenderChildren> = {
      'raise-hand': () => (
        <Button key="gio-tay" label={S.raiseHand} onPress={async () => {
          await update($, modeAtom, () => 'gio-tay')
          await sendPressCue($, 'Giơ tay')
        }} />
      ),
      'ask-leave': () => (
        <Button key="xin-phep" label={S.askLeave} onPress={async () => {
          await touch($)
          await update($, modeAtom, () => 'xin-phep')
        }} />
      ),
      leave: () => xinNghi,
      slower: () => <Button key="cham" label={S.slower} onPress={() => sendPressCue($, 'Nhịp: chậm lại')} />,
      faster: () => <Button key="nhanh" label={S.faster} onPress={() => sendPressCue($, 'Nhịp: nhanh hơn')} />,
      hint: () => (
        <Button key="goi-y" label={S.hint(T)} onPress={async () => {
          await touch($)
          // Tín hiệu cho giáo viên giữ tiếng Việt để Skill nhận ra, dù nhãn nút theo tiếng học viên.
          await $.prompt.submit({ text: `${TAG}${STR.vi.hint(STR.vi.teacherSelf(kind))}`, asUser: true })
        }} />
      ),
      'result-sheet': () => (
        <Button key="phieu" label={S.resultSheet} onPress={async () => {
          await touch($)
          await $.prompt.submit({ text: `${TAG}Xuất phiếu kết quả`, asUser: true })
        }} />
      ),
      delegate: () => (
        <Box key="delegate" flexDirection="row" gap={1}>
          <Button key="b-form" label={S.delegate} onPress={async () => { await touch($); await update($, modeAtom, () => 'form') }} />
          {isPractice ? <Button key="chua-dung" label={S.notRight(t)} onPress={async () => {
            await touch($)
            await $.prompt.fill({ text: S.notRightFill(t), mode: 'replace' })
          }} /> : null}
        </Box>
      ),
    }
    const ALWAYS: PodiumButtonId[] = ['raise-hand', 'ask-leave', 'leave']
    const chosen = spec.buttons.filter(id => !working || ALWAYS.includes(id))
    const hidden = ALWAYS.filter(id => !spec.buttons.includes(id))
    const open = await read($, moreOpen)
    const buttonsRow = chosen.length || hidden.length ? (
      <Box flexDirection="row" gap={1} flexWrap="wrap">
        {chosen.map(id => btn[id]())}
        {hidden.length && open ? hidden.map(id => btn[id]()) : null}
        {hidden.length ? <Button key="more" label={open ? S.moreClose : S.more} onPress={() => update($, moreOpen, v => !v)} /> : null}
      </Box>
    ) : null

    const infoRow = isMini ? null : factsRow

    // Dải chật (ước số dòng vượt chỗ) mà có phần v0.6: thu khoảng cách, bỏ dòng phụ, xếp theo thứ tự ưu tiên
    // nút một chạm → Lượt của bạn → thử thách/sao/huy hiệu → các nút khác. Nhãn Bypass luôn ở đầu.
    const hasSix = !!(oneTouch || choicesRow || extrasRow || giftRow)
    const miniDest = isMini ? null : destRow
    const miniParts = isMini ? null : partsRow
    const lines = [bypassChip, header, oneTouch, choicesRow, headRow, askRow, waitHint, extrasRow, helpRow, miniDest, miniParts, ...panelRows, boardRow, pointRow, infoRow, giftRow].filter(x => x != null).length + 2
    const maxRows = typeof e.props.maxRows === 'number' && e.props.maxRows > 0 ? e.props.maxRows : 0
    const crowded = hasSix && maxRows > 0 && 2 + lines * 2 - 1 > maxRows
    const top: RenderChildren[] = crowded
      ? [bypassChip, waitHint, oneTouch, choicesRow, headRow, askRow, extrasRow, header, helpRow, miniParts, ...panelRows, boardRow, pointRow, giftRow]
      : [bypassChip, header, headRow, askRow, waitHint, oneTouch, choicesRow, boardRow, pointRow, infoRow, extrasRow, helpRow, miniDest, miniParts, ...panelRows, giftRow]

    return board([...top, buttonsRow], crowded ? 0 : 1)
  })

  // ── Hộp câu hỏi gốc: thêm một dòng lớp học phía trên, giữ nguyên hộp ─────────
  on('ui.render', { component: 'AskUserQuestion' }, async ($, e, next) => {
    if (!(await read($, isClassroom))) return next(e)
    const theirs = await next(e)
    const { Box, Text } = $.ui.resolve(e)
    if (!askDone.has(e.requestId) && askSeen?.id !== e.requestId) askSeen = { id: e.requestId, label: defaultLabel(e.props.questions) }
    const v = await classView($)
    const T = teacherName(v.teacher)
    const S = L()
    const segTitle = v.seg ? (curLang === 'vi' ? v.seg.title : (S.segments[v.seg.id] ?? v.seg.title)) : ''
    const head = v.seg ? `${S.askHead(T)} · ${S.part} ${v.seg.id} · ${segTitle}` : S.askHead(T)
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
    const { Box, Text, Button } = $.ui.resolve(e)
    // v0.11: lời giáo viên dài (> ~600 ký tự) gập thành 3 dòng đầu + nút "Xem đầy đủ". Chỉ trên Desktop: nút bấm được ở đó;
    // dòng chữ ở terminal là lịch sử cuộn, chưa chắc bấm được nút nên không gập (tránh giấu chữ mà không mở ra được).
    // Khối tóm tắt (isSummary) và kết quả công cụ không đụng tới.
    const text = typeof e.props.text === 'string' ? e.props.text : ''
    const preview = e.surface === 'desktop' && !e.props.isSummary ? foldPreview(text) : null
    const opened = preview === null ? true : (await read($, foldOpen)).includes(e.requestId)
    const theirs = preview !== null && !opened ? await next({ ...e, props: { ...e.props, text: preview } }) : await next(e)
    const fold =
      preview === null ? null : (
        <Button
          key="fold"
          label={opened ? L().foldLess : L().foldMore}
          onPress={() => update($, foldOpen, ids => (ids.includes(e.requestId) ? ids.filter(x => x !== e.requestId) : [...ids, e.requestId]))}
        />
      )
    const first = e.props.isFirstOfReply
    const v = await classView($)
    const T = teacherName(v.teacher)
    // Tiêu đề phần chỉ chốt khi lượt giảng đã xong (giáo viên ghi phần mới ở cuối lượt); đang giảng thì tính lại,
    // và vẽ lại khi lớp đổi (rev) để lời giảng không dính "Phần 0" cũ.
    let title = headerById.get(e.requestId)
    if (!title) {
      const working = await read($, workingAtom)
      await read($, rev)
      const S = L()
      title = v.seg ? ` ${T} · ${S.part} ${v.seg.id} · ${curLang === 'vi' ? v.seg.title : (S.segments[v.seg.id] ?? v.seg.title)} ` : ` ${T} `
      if (!working) headerById.set(e.requestId, title)
    }
    const color = DRIVE_COLOR[v.seg?.drive ?? 'D1']
    let avatar = <Box width={e.surface === 'desktop' ? 5 : 2} />
    if (first && e.surface === 'desktop') {
      const { Svg } = $.ui.resolve(e)
      avatar = <Svg key="avatar" source={teacherAvatarSvg(v.teacher)} alt={T} width={34} height={34} />
    }
    return (
      <Box flexDirection="row" gap={1}>
        {avatar}
        <Box flexDirection="column" flexGrow={1} borderStyle="quote" borderColor="#008816" paddingLeft={1}>
          {first ? <Text bold backgroundColor={color} color={INK}>{title}</Text> : null}
          {theirs}
          {fold}
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
    if (at >= 0 && at < 200) return <Box />
    if (e.props.isExpanded) return next(e)
    if (text.startsWith(TAG)) {
      return (
        <Box flexDirection="row" borderStyle="round" borderColor="#C9A800" paddingX={1}>
          <Text color="#854F0B">{`${L().youPressed} · ${cut(text.slice(TAG.length).trim().split('\n')[0], 120)}`}</Text>
        </Box>
      )
    }
    const theirs = await next(e)
    const label = DELEGATION_HEADS.some(h => text.startsWith(h)) ? L().youDelegated : L().you
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
    // Giáo viên ghi sổ lớp (.lop-hoc/): một dòng mờ thay cho dòng công cụ. Công cụ khác giữ nguyên.
    if (touchesLedger(e.props.input)) {
      const { Text } = $.ui.resolve(e)
      return <Text dimColor>{L().ledger(teacherName(view.teacher))}</Text>
    }
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

  // Nhóm dòng công cụ: toàn việc ghi sổ lớp thì một dòng mờ; lẫn việc khác thì mở rộng nhóm để từng dòng
  // đi qua ToolUse (dòng ghi sổ ẩn, dòng khác giữ nguyên).
  on('ui.render', { component: 'ToolGroup' }, async ($, e, next) => {
    if (!(await read($, isClassroom))) return next(e)
    const calls = Array.isArray(e.props.calls) ? e.props.calls : []
    const hits = calls.filter(c => touchesLedger(c.input)).length
    if (!hits) return next(e)
    if (hits === calls.length) {
      const { Text } = $.ui.resolve(e)
      return <Text dimColor>{L().ledger(teacherName(view.teacher))}</Text>
    }
    return next({ ...e, props: { ...e.props, isExpanded: true } })
  }).catch(($, e, next) => next(e))

  // ── Spinner tiếng Việt + mẹo đổi theo lượt, giữ hoạt ảnh gốc ───────────────
  on('ui.render', { component: 'Spinner' }, async ($, e, next) => {
    if (!(await read($, isClassroom))) return next(e)
    const T = teacherName(view.teacher)
    const S = L()
    const word = e.props.mode === 'tool-use' || e.props.mode === 'tool-input' ? S.demoWord(T) : S.teachWord(T)
    const tip = S.tips[turns % S.tips.length] ?? ''
    return next({ ...e, props: { ...e.props, word, suffix: ` · ${tip}` } })
  })

  // ── Gợi ý dưới ô nhập ───────────────────────────────────────────────────────
  on('ui.render', { component: 'PromptHint' }, async ($, e, next) => {
    if (e.props.isDraft || e.props.isWorking || !(await read($, isClassroom))) return next(e)
    const isIn = await read($, entered)
    const hint = !isIn ? L().promptBefore : L().promptIn(teacherLower(view.teacher))
    return next({ ...e, props: { ...e.props, hint } })
  })

  // ── Bảng tóm tắt (chỉ khi gõ /lop-hoc) ─────────────────────────────────────
  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    await read($, rev)
    const lesson = await read($, lessonAtom)
    const s = await loadState($)
    const skills = s?.skills ?? []
    const curId = lesson && !lesson.over ? (s?.segment?.id ?? '0') : null
    const cur = curId == null ? -1 : SEGMENTS.findIndex(p => p.id === curId)
    const loops = typeof s?.loops_done === 'number' ? s.loops_done : 0

    return (
      <Box flexDirection="column" gap={1}>
        <Text bold color="#006D11">{TITLE}</Text>
        {lesson ? <Text>{`${teacherName(lesson.teacher)} · lớp luôn mở · đã chốt ${loops} vòng việc`}</Text> : <Text dimColor>Chưa vào lớp. Chọn thầy hoặc cô trên bảng lớp, rồi bấm Vào lớp.</Text>}
        <Box flexDirection="column">
          <Text dimColor>Một vòng việc</Text>
          {SEGMENTS.map((p, n) => {
            const mark = cur < 0 ? '○' : n < cur ? '✓' : n === cur ? '→' : '○'
            return (
              <Text key={`seg-${p.id}`} bold={n === cur} color={n < cur ? 'success' : undefined} dimColor={cur >= 0 && n > cur}>
                {`${mark} Phần ${p.id} · ${p.title}`}
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
