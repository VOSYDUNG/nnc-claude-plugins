import type { CharId, Moment, PodiumMode } from '../types'

// Trợ giảng NNC và bục giảng, vẽ bằng Svg. Chuyển động dùng SMIL nên chỉ chạy khi Svg isInteractive.
// Hàm thuần: không dùng $, chỉ trả về chuỗi <svg>.

const G = '#008816'
const GD = '#006D11'
const Y = '#FFEA00'
const YD = '#C9A800'
const INK = '#1f2a1f'
const CHEEK = '#F4A6A0'

export const CHARS: { id: CharId; name: string }[] = [
  { id: 'la', name: 'Bé Lá' },
  { id: 'nang', name: 'Viên Nang' },
  { id: 'hop', name: 'Hộp Giao' },
]

export const isCharId = (v: string): v is CharId => CHARS.some(c => c.id === v)

function eyes(m: Moment, cx: number, cy: number, sp: number): string {
  const l = cx - sp
  const r = cx + sp
  if (m === 'read') {
    // Mắt mở, con ngươi dò qua lại theo dòng chữ, lông mày nhướng: đang đọc, không phải đang ngủ.
    const scan = '<animateTransform attributeName="transform" type="translate" values="-1.6 0;1.6 0;-1.6 0" dur="1.8s" repeatCount="indefinite"/>'
    return `<ellipse cx="${l}" cy="${cy}" rx="3.6" ry="3.4" fill="#fff" stroke="${INK}" stroke-width="1.4"/><ellipse cx="${r}" cy="${cy}" rx="3.6" ry="3.4" fill="#fff" stroke="${INK}" stroke-width="1.4"/><g>${scan}<circle cx="${l}" cy="${cy + 1.4}" r="1.8" fill="${INK}"/><circle cx="${r}" cy="${cy + 1.4}" r="1.8" fill="${INK}"/></g><path d="M${l - 4} ${cy - 6} q4 -2 8 0 M${r - 4} ${cy - 6} q4 -2 8 0" stroke="${INK}" stroke-width="1.6" fill="none" stroke-linecap="round"/>`
  }
  if (m === 'done') return `<path d="M${l - 4} ${cy + 2} q4 -5 8 0 M${r - 4} ${cy + 2} q4 -5 8 0" stroke="${INK}" stroke-width="2.2" fill="none" stroke-linecap="round"/>`
  const rr = m === 'catch' ? 4.2 : 3.2
  const blink = `<animate attributeName="ry" values="${rr};${rr};0.4;${rr}" keyTimes="0;0.92;0.96;1" dur="4s" repeatCount="indefinite"/>`
  return `<ellipse cx="${l}" cy="${cy}" rx="${rr}" ry="${rr}" fill="${INK}">${blink}</ellipse><ellipse cx="${r}" cy="${cy}" rx="${rr}" ry="${rr}" fill="${INK}">${blink}</ellipse>`
}

function mouth(m: Moment, cx: number, cy: number): string {
  if (m === 'catch') return `<ellipse cx="${cx}" cy="${cy + 1}" rx="3" ry="3.6" fill="${INK}"/>`
  if (m === 'done') return `<path d="M${cx - 6} ${cy - 1} q6 8 12 0 z" fill="${INK}"/>`
  if (m === 'read') return `<path d="M${cx - 3} ${cy} q3 3 6 0" stroke="${INK}" stroke-width="2" fill="none" stroke-linecap="round"/>`
  return `<path d="M${cx - 5} ${cy} q5 5 10 0" stroke="${INK}" stroke-width="2.2" fill="none" stroke-linecap="round"/>`
}

const cheeks = (cx: number, cy: number, sp: number) =>
  `<circle cx="${cx - sp - 6}" cy="${cy + 7}" r="3.2" fill="${CHEEK}" opacity=".8"/><circle cx="${cx + sp + 6}" cy="${cy + 7}" r="3.2" fill="${CHEEK}" opacity=".8"/>`

// Thân nhân vật trong khung 120×112, tâm mặt quanh (60, 55).
export function body(c: CharId, m: Moment): string {
  if (c === 'la')
    return `<path d="M60 108 V92" stroke="${GD}" stroke-width="4" stroke-linecap="round"/><path d="M60 94 C24 88 22 40 60 16 C98 40 96 88 60 94 Z" fill="${G}"/><path d="M60 90 V30" stroke="${GD}" stroke-width="2" opacity=".5"/><ellipse cx="60" cy="58" rx="22" ry="17" fill="#E6F7E8"/>${eyes(m, 60, 55, 9)}${mouth(m, 60, 64)}${cheeks(60, 55, 9)}`
  if (c === 'nang')
    return `<g transform="rotate(-12 60 60)"><rect x="36" y="14" width="48" height="90" rx="24" fill="${G}"/><path d="M36 59 V38 a24 24 0 0 1 48 0 V59 Z" fill="${Y}"/><line x1="36" y1="59" x2="84" y2="59" stroke="${YD}" stroke-width="2"/></g>${eyes(m, 60, 48, 9)}${mouth(m, 60, 57)}${cheeks(60, 48, 9)}`
  return `<rect x="30" y="30" width="60" height="58" rx="6" fill="${Y}" stroke="${YD}" stroke-width="2"/><rect x="54" y="30" width="12" height="58" fill="${G}"/><path d="M60 30 V18" stroke="${GD}" stroke-width="3" stroke-linecap="round"/><circle cx="60" cy="15" r="4" fill="${G}"/><rect x="36" y="50" width="48" height="26" rx="5" fill="#FFFDF0"/>${eyes(m, 60, 59, 10)}${mouth(m, 60, 68)}<path d="M38 88 v8 M82 88 v8" stroke="${GD}" stroke-width="4" stroke-linecap="round"/>`
}

// Avatar nhỏ cạnh lời giảng: tĩnh (không SMIL) để khung hội thoại nhẹ.
export function avatarSvg(c: CharId): string {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="10 8 100 100" width="100" height="100">${body(c, 'turn')}</svg>`
}

const MODE_MOMENT: Record<PodiumMode, Moment> = { wait: 'turn', turn: 'turn', work: 'read', hint: 'hint', done: 'done' }

// Bục giảng: trợ giảng đứng sau bục, chỉ lộ nửa trên.
// wait: mờ, chỉ ló đầu · turn: trồi lên rồi nhún · work: đọc · done: nhảy, sao lấp lánh.
export function podiumSvg(c: CharId, mode: PodiumMode, label = 'Lớp học NNC'): string {
  const m = MODE_MOMENT[mode]
  const rise =
    mode === 'wait'
      ? '<animateTransform attributeName="transform" type="translate" values="0 14;0 8;0 14" dur="3s" repeatCount="indefinite"/>'
      : mode === 'turn'
        ? '<animateTransform attributeName="transform" type="translate" values="0 34;0 0" dur="0.6s" fill="freeze"/>'
        : mode === 'done'
          ? '<animateTransform attributeName="transform" type="translate" values="0 0;0 -8;0 0" dur="0.7s" repeatCount="indefinite"/>'
          : '<animateTransform attributeName="transform" type="translate" values="0 0;0 -2;0 0" dur="2.2s" repeatCount="indefinite"/>'
  const opacity = mode === 'wait' ? '0.75' : '1'
  const sparks =
    mode === 'done'
      ? `<path d="M22 20 l2 4 4 2 -4 2 -2 4 -2 -4 -4 -2 4 -2z" fill="${Y}" stroke="${YD}"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.2s" repeatCount="indefinite"/></path><path d="M150 14 l2 4 4 2 -4 2 -2 4 -2 -4 -4 -2 4 -2z" fill="${Y}" stroke="${YD}"><animate attributeName="opacity" values="1;0.2;1" dur="1.2s" repeatCount="indefinite"/></path>`
      : ''
  const bulb =
    mode === 'hint'
      ? `<circle cx="138" cy="22" r="12" fill="${Y}" opacity=".35"><animate attributeName="r" values="9;14;9" dur="1.6s" repeatCount="indefinite"/></circle><circle cx="138" cy="22" r="8" fill="${Y}" stroke="${YD}" stroke-width="1.5"/><rect x="134.5" y="29" width="7" height="5" rx="1.5" fill="#B4B2A9"/>`
      : ''
  const book =
    mode === 'work'
      ? `<rect x="62" y="60" width="36" height="14" rx="2" fill="#fff" stroke="${GD}" stroke-width="1.5"/><line x1="80" y1="60" x2="80" y2="74" stroke="${GD}" stroke-width="1.5"/>`
      : ''
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 176 110" width="176" height="110">${sparks}${bulb}<g opacity="${opacity}"><g>${rise}<g transform="translate(40 0) scale(0.8)">${body(c, m)}</g></g></g>${book}<path d="M40 70 h96 l-7 38 h-82 z" fill="${G}"/><rect x="34" y="64" width="108" height="9" rx="3" fill="${GD}"/><rect x="54" y="80" width="68" height="16" rx="4" fill="${Y}"/><text x="88" y="92" text-anchor="middle" font-size="9" fill="${INK}" font-family="sans-serif">${label}</text></svg>`
}

// ── v0.5: hai giảng viên (thầy/cô), cảm xúc, thẻ usage, đồng hồ phần học ─────────
// KHUNG (stub) — subagent làm hình sẽ thay phần thân, GIỮ NGUYÊN tên và tham số.
export type TeacherKind = 'thay' | 'co'
export type Emotion = 'hi' | 'no' | 'ai' | 'o' | 'bi' | 'lac' | 'giang' | 'nghe'
export type Drive = 'D1' | 'D2' | 'D3' | 'ket-noi'
// present: đang dạy · wait: chờ lớp (mờ, ló đầu) · away: học viên vắng, lớp tạm nghỉ
export type TeacherPresence = 'present' | 'wait' | 'away'

export const TEACHERS: { id: TeacherKind; label: string }[] = [
  { id: 'thay', label: 'Thầy' },
  { id: 'co', label: 'Cô' },
]
export const isTeacherKind = (v: unknown): v is TeacherKind => v === 'thay' || v === 'co'
export const isEmotion = (v: unknown): v is Emotion => typeof v === 'string' && ['hi', 'no', 'ai', 'o', 'bi', 'lac', 'giang', 'nghe'].includes(v)
export const DRIVE_COLOR: Record<Drive, string> = { D1: '#3CC85A', D2: '#4A90E2', D3: '#F5A524', 'ket-noi': '#F4F4EC' }

// ── Vẽ giảng viên ───────────────────────────────────────────────────────────
// Hình người cách điệu (thiết kế riêng của NNC). Khung riêng 120×124: tâm mặt (60, 40),
// vai ở y≈72, thân kéo xuống y=124. Bục giảng và avatar đặt khung này bằng transform.
// anim = false: không có SMIL (avatar, Svg không tương tác) — hình tĩnh vẫn phải đủ nghĩa.

const SKIN = '#F2C9A0'
const NECK = '#D9A87E'
const TINK = '#2a2a2a'
const MOUTH_IN = '#6E2A24'
const TONGUE = '#E07B70'
const BOARD = '#123F1E'
const TRACK = '#0B2A14'
const WHITE = '#FFFFFF'
const AMBER = '#F5A524'
const HAIR: Record<TeacherKind, string> = { thay: '#2B2420', co: '#3A2A22' }
const FONT = 'font-family="sans-serif"'
const EMOTIONS: Emotion[] = ['hi', 'no', 'ai', 'o', 'bi', 'lac', 'giang', 'nghe']

const EL = 52.8 // tâm mắt trái (phía người xem)
const ER = 67.2
const EY = 40.2

const f = (v: number) => String(Math.round(v * 10) / 10)
const svgOpen = (vb: string, w: number, h: number) =>
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb}" width="${w}" height="${h}">`
const ln = (d: string, color: string, w: number, extra = '') =>
  `<path d="${d}" stroke="${color}" stroke-width="${w}" fill="none" stroke-linecap="round" stroke-linejoin="round"${extra}/>`

// Mắt mở; chớp mắt bằng scale theo trục y quanh tâm mắt.
function eyeOpen(k: TeacherKind, cx: number, cy: number, r: number, look: number, side: -1 | 1, anim: boolean, gleam = 0.32): string {
  const blink = anim
    ? '<animateTransform attributeName="transform" type="scale" values="1 1;1 1;1 0.12;1 1" keyTimes="0;0.92;0.96;1" dur="4.6s" repeatCount="indefinite"/>'
    : ''
  const lash = k === 'co' ? ln(`M${f(side * 1.9)} -1.4 l${f(side * 1.9)} -1.5`, TINK, 1) : ''
  return `<g transform="translate(${f(cx)} ${f(cy)})"><g>${blink}<ellipse cx="${f(look)}" cy="0" rx="${f(r * 0.88)}" ry="${f(r)}" fill="${TINK}"/><circle cx="${f(look + 0.7)}" cy="-0.8" r="${f(r * gleam)}" fill="${WHITE}"/>${lash}</g></g>`
}
// Mắt cười khép (∩).
const eyeArc = (cx: number, cy: number) => ln(`M${f(cx - 3)} ${f(cy + 1.2)} Q${f(cx)} ${f(cy - 2.8)} ${f(cx + 3)} ${f(cy + 1.2)}`, TINK, 2)
// Mắt dịu (ái): khép cong xuống, hiền.
const eyeSoft = (k: TeacherKind, cx: number, cy: number, side: -1 | 1) =>
  ln(`M${f(cx - 3)} ${f(cy - 0.4)} Q${f(cx)} ${f(cy + 2.4)} ${f(cx + 3)} ${f(cy - 0.4)}`, TINK, 1.8) +
  (k === 'co' ? ln(`M${f(cx + side * 3)} ${f(cy - 0.4)} l${f(side * 1.5)} -1`, TINK, 1) : '')

function tEyes(k: TeacherKind, e: Emotion, anim: boolean): string {
  switch (e) {
    case 'hi':
      return eyeArc(EL, EY) + eyeArc(ER, EY)
    case 'ai':
      return eyeSoft(k, EL, EY, -1) + eyeSoft(k, ER, EY, 1)
    case 'no':
      return eyeOpen(k, EL, EY, 2.2, 0, -1, anim) + eyeOpen(k, ER, EY, 2.2, 0, 1, anim)
    case 'o':
      return eyeOpen(k, EL, EY + 0.3, 1.9, 0.7, -1, anim) + eyeOpen(k, ER, EY + 0.3, 1.9, 0.7, 1, anim)
    case 'bi':
      return eyeOpen(k, EL, EY + 0.7, 2.2, 0, -1, anim, 0.42) + eyeOpen(k, ER, EY + 0.7, 2.2, 0, 1, anim, 0.42)
    case 'lac':
      return eyeOpen(k, EL, EY, 2.3, 0, -1, false) + eyeArc(ER, EY)
    case 'nghe':
      return eyeOpen(k, EL, EY, 2.3, -0.8, -1, anim) + eyeOpen(k, ER, EY, 2.3, -0.8, 1, anim)
    default:
      return eyeOpen(k, EL, EY, 2.3, 0, -1, anim) + eyeOpen(k, ER, EY, 2.3, 0, 1, anim)
  }
}

// Lông mày: [đầu ngoài dy, đầu trong dy, độ cong] cho mày trái và phải.
type BrowSpec = readonly [number, number, number]
const BROWS: Record<Emotion, readonly [BrowSpec, BrowSpec]> = {
  hi: [[-1, -1.4, -1.4], [-1, -1.4, -1.4]],
  no: [[-0.5, 1.2, 0.1], [-0.5, 1.2, 0.1]],
  ai: [[0.4, -0.6, -1], [0.4, -0.6, -1]],
  o: [[0, 1.1, -0.2], [-1.3, 0.2, -0.8]],
  bi: [[1.1, -1.9, -0.2], [1.1, -1.9, -0.2]],
  lac: [[-1.4, -0.8, -1.2], [0.8, 0.8, -0.4]],
  giang: [[0, 0, -1], [0, 0, -1]],
  nghe: [[-1.8, -1, -1.2], [0, 0, -0.8]],
}
function brows(k: TeacherKind, e: Emotion): string {
  const by = k === 'thay' ? 32.4 : 33.6
  const w = k === 'thay' ? 2.1 : 1.5
  const knit = e === 'no' ? 0.4 : 0
  const one = (s: BrowSpec, ox: number, ix: number) => {
    const oy = by + s[0]
    const iy = by + s[1]
    return ln(`M${f(ox)} ${f(oy)} Q${f((ox + ix) / 2)} ${f((oy + iy) / 2 + s[2])} ${f(ix)} ${f(iy)}`, HAIR[k], w)
  }
  const [l, r] = BROWS[e]
  return one(l, 48.5, 57 + knit) + one(r, 71.5, 63 - knit)
}

function tMouth(k: TeacherKind, e: Emotion, anim: boolean): string {
  const lip = k === 'co' ? '#8E3B34' : TINK
  switch (e) {
    case 'hi':
      return `<path d="M54 50.5 Q60 50 66 50.5 Q65 57.5 60 57.5 Q55 57.5 54 50.5 Z" fill="${MOUTH_IN}"/><path d="M55 50.6 Q60 50.2 65 50.6 L64.6 52 Q60 51.7 55.4 52 Z" fill="${WHITE}"/><path d="M57 55.9 Q60 54.1 63 55.9 Q60 57.5 57 55.9 Z" fill="${TONGUE}"/>`
    case 'no':
      return ln('M56 52.6 L64 52.6', lip, 1.9)
    case 'ai':
      return ln('M55.5 51.4 Q60 55 64.5 51.4', lip, 1.8)
    case 'o':
      return ln('M56 53.2 Q58 51.8 60 52.8 Q62 53.8 64.5 52.2', lip, 1.7)
    case 'bi':
      return ln('M57 53.6 Q60 51.6 63 53.6', lip, 1.7)
    case 'lac':
      return `<path d="M54.5 50.5 Q60.5 51.5 66.5 49.5 Q64 55.8 59.5 55.6 Q55.6 55.3 54.5 50.5 Z" fill="${WHITE}" stroke="${TINK}" stroke-width="1.3" stroke-linejoin="round"/>${ln('M55.6 52.5 Q60.5 53.4 65.6 51.6', TINK, 0.8)}`
    case 'nghe':
      return `<ellipse cx="60" cy="53" rx="1.7" ry="2.1" fill="${MOUTH_IN}"/>`
    default: {
      // đang giảng: miệng mở nhẹ, mấp máy khi có hoạt ảnh
      const talk = anim ? '<animate attributeName="ry" values="1.5;2.4;1.1;2.1;1.5" dur="1.4s" repeatCount="indefinite"/>' : ''
      return `${ln('M55.4 51.2 Q56 51.8 56.6 51.6 M63.4 51.6 Q64 51.8 64.6 51.2', lip, 1.2)}<ellipse cx="60" cy="52.4" rx="3" ry="1.6" fill="${MOUTH_IN}">${talk}</ellipse>`
    }
  }
}

function nose(k: TeacherKind, e: Emotion): string {
  const base = k === 'thay' ? ln('M60.5 42.6 Q62 46.4 59.3 47', TINK, 1.2, ' opacity=".55"') : ln('M59 46.6 Q60 47.6 61.2 46.6', TINK, 1.1, ' opacity=".55"')
  // ố: nhăn mũi nhẹ ở sống mũi
  return e === 'o' ? base + ln('M58.2 43.4 Q60 42.6 61.8 43.4 M58.7 44.9 Q60 44.3 61.3 44.9', TINK, 0.9, ' opacity=".55"') : base
}

const tCheeks = () =>
  `<circle cx="50.3" cy="47.6" r="3.4" fill="${CHEEK}" opacity=".6"/><circle cx="69.7" cy="47.6" r="3.4" fill="${CHEEK}" opacity=".6"/>`

const glasses = () =>
  `<rect x="47" y="35.8" width="11.5" height="8.6" rx="2.6" fill="${WHITE}" fill-opacity=".18" stroke="${TINK}" stroke-width="1.6"/><rect x="61.5" y="35.8" width="11.5" height="8.6" rx="2.6" fill="${WHITE}" fill-opacity=".18" stroke="${TINK}" stroke-width="1.6"/>` +
  ln('M58.5 39.4 Q60 38.2 61.5 39.4 M47 38.8 L44.4 38.2 M73 38.8 L75.6 38.2', TINK, 1.6)

function head(k: TeacherKind, e: Emotion, anim: boolean): string {
  const hair = HAIR[k]
  const face = `<ellipse cx="60" cy="40" rx="16" ry="19" fill="${SKIN}"/>${tCheeks()}${nose(k, e)}${tEyes(k, e, anim)}${brows(k, e)}${tMouth(k, e, anim)}`
  if (k === 'thay') {
    const ears = `<circle cx="44.2" cy="42" r="3.6" fill="${SKIN}"/><circle cx="75.8" cy="42" r="3.6" fill="${SKIN}"/><path d="M43.6 40.6 q1.2 1.4 0 2.8 M76.4 40.6 q-1.2 1.4 0 2.8" stroke="${NECK}" stroke-width="1" fill="none"/>`
    // tóc ngắn vuốt sang một bên
    const top =
      `<path d="M43.4 42 C41.6 26 49.6 16.6 61 16.6 C72.4 16.6 79.6 25 76.6 42 C75.6 35 73.6 30.6 70.6 28.4 C64 31.6 54.6 31.4 49 27.4 C46 31 44.4 36 43.4 42 Z" fill="${hair}"/>` +
      ln('M49.4 21.6 Q59 16.8 70.4 22.4 M52.4 25.2 Q61 21.2 69.6 25.6', '#4A3D36', 1.1, ' opacity=".8"')
    return ears + face + top + glasses()
  }
  // cô: búi tóc + dây buộc vàng, tóc dài ôm mặt, mái lệch
  const back =
    `<circle cx="60" cy="11.6" r="7.6" fill="${hair}"/>` +
    `<path d="M40.5 66 C36 52 36 30 43 22 C48 16.5 54 14.5 60 14.5 C66 14.5 72 16.5 77 22 C84 30 84 52 79.5 66 Q74 68.5 71 63 L71 46 L49 46 L49 63 Q46 68.5 40.5 66 Z" fill="${hair}"/>` +
    `<ellipse cx="60" cy="16.6" rx="6.2" ry="1.9" fill="${Y}" stroke="${YD}" stroke-width=".7"/>`
  const fringe =
    `<path d="M44 38.5 C43 25 51 19.4 60 19.4 C69 19.4 77 25 76 38.5 C74 31 70 26.6 64 26.4 C57.4 27.6 49.6 30.8 44 38.5 Z" fill="${hair}"/>` +
    ln('M50 24.6 Q57 21.4 66 23', '#5A463B', 1, ' opacity=".8"')
  return back + face + fringe
}

function torso(k: TeacherKind): string {
  const neck = `<rect x="54" y="52" width="12" height="18" fill="${NECK}"/>`
  const body = `<path d="M16 124 C16 88 24 74.6 45 70.4 L50 69.5 Q60 72 70 69.5 L75 70.4 C96 74.6 104 88 104 124 Z" fill="${G}"/>`
  const seams = ln('M30 84 Q27 104 29 124 M90 84 Q93 104 91 124', GD, 1.4, ' opacity=".7"')
  if (k === 'thay') {
    // cổ áo sơ mi trắng chữ V, cà vạt vàng
    return (
      neck +
      body +
      seams +
      `<path d="M50.5 69.6 L60 86 L69.5 69.6 Q60 72.5 50.5 69.6 Z" fill="${WHITE}"/>` +
      `<path d="M50.5 69.4 L57.6 77.4 L52.2 80.2 L48.6 71 Z M69.5 69.4 L62.4 77.4 L67.8 80.2 L71.4 71 Z" fill="${WHITE}" stroke="#D8D8CF" stroke-width=".8" stroke-linejoin="round"/>` +
      `<path d="M57.6 72.4 L62.4 72.4 L61.6 77 L58.4 77 Z" fill="${Y}" stroke="${YD}" stroke-width=".7"/>` +
      `<path d="M58.4 77 L61.6 77 L64 95 L60 100 L56 95 Z" fill="${Y}" stroke="${YD}" stroke-width=".7" stroke-linejoin="round"/>`
    )
  }
  // cô: khăn quàng vàng + trâm cài vàng
  return (
    neck +
    body +
    seams +
    `<path d="M51.5 69.6 Q60 80 68.5 69.6 Q60 72 51.5 69.6 Z" fill="${NECK}"/>` +
    `<path d="M48.4 68 Q60 77 71.6 68 L73 71.6 Q60 82 47 71.6 Z" fill="${Y}" stroke="${YD}" stroke-width=".7" stroke-linejoin="round"/>` +
    `<path d="M63 76 Q67.4 82 66.2 90.4 L61.6 88.6 Q62.6 82 59.6 77.6 Z" fill="${Y}" stroke="${YD}" stroke-width=".7" stroke-linejoin="round"/>` +
    `<circle cx="61.6" cy="77" r="2.4" fill="${Y}" stroke="${YD}" stroke-width=".7"/>` +
    `<circle cx="78" cy="84" r="3.3" fill="${Y}" stroke="${YD}" stroke-width="1"/><circle cx="78" cy="84" r="1.3" fill="#FFF7B0"/>`
  )
}

// Cánh tay: nét xanh dày có viền đậm; bàn tay màu da.
const arm = (d: string) => ln(d, GD, 10.5) + ln(d, G, 8)
const palm = (x: number, y: number, rot: number) =>
  `<g transform="translate(${f(x)} ${f(y)}) rotate(${f(rot)})"><ellipse cx="-4.1" cy="1.4" rx="1.6" ry="2.9" transform="rotate(-30 -4.1 1.4)" fill="${SKIN}" stroke="${NECK}" stroke-width=".8"/><ellipse rx="4.4" ry="5.3" fill="${SKIN}" stroke="${NECK}" stroke-width=".8"/>${ln('M-1.7 -4.6 V-1.5 M0.5 -5.1 V-1.7 M2.6 -4.4 V-1.5', NECK, 0.8)}</g>`
// Bàn tay mở, lòng bàn tay hướng ra (chào / "khoan đã").
const openHand = (x: number, y: number, rot: number) => {
  const fingers = [6.2, 7.4, 7.1, 6]
    .map((h, i) => `<rect x="${f(-4.5 + i * 2.3)}" y="${f(-1.5 - h)}" width="2.1" height="${f(h + 2)}" rx="1.05" fill="${SKIN}" stroke="${NECK}" stroke-width=".7"/>`)
    .join('')
  return `<g transform="translate(${f(x)} ${f(y)}) rotate(${f(rot)})">${fingers}<ellipse cx="-5.2" cy="1.8" rx="1.5" ry="3" transform="rotate(-38 -5.2 1.8)" fill="${SKIN}" stroke="${NECK}" stroke-width=".7"/><rect x="-4.7" y="-2.6" width="9.4" height="8.4" rx="3.2" fill="${SKIN}" stroke="${NECK}" stroke-width=".8"/><path d="M-4.1 -2.2 h8.2" stroke="${SKIN}" stroke-width="1.4"/></g>`
}
const fist = (x: number, y: number) =>
  `<circle cx="${f(x)}" cy="${f(y)}" r="4.4" fill="${SKIN}" stroke="${NECK}" stroke-width=".8"/>${ln(`M${f(x - 2.4)} ${f(y - 1)} h4.6 M${f(x - 2.4)} ${f(y + 1.2)} h4.6`, NECK, 0.7)}`

function gesture(e: Emotion, anim: boolean): string {
  switch (e) {
    case 'hi': {
      const wave = anim
        ? '<animateTransform attributeName="transform" type="rotate" values="0 89 80;-11 89 80;3 89 80;-11 89 80;0 89 80" dur="1.6s" repeatCount="indefinite"/>'
        : ''
      return `<g>${wave}${arm('M89 80 Q102 78 103 61')}${openHand(103.4, 55, 12)}</g>`
    }
    case 'no': {
      // lòng bàn tay giơ "khoan đã" — dứt khoát nhưng ôn hoà
      const push = anim ? '<animateTransform attributeName="transform" type="translate" values="0 3;0 0" dur="0.45s" fill="freeze"/>' : ''
      return `<g>${push}${arm('M89 80 Q100 77 98.6 63')}${openHand(98.6, 57, 0)}</g>`
    }
    case 'ai':
      // tay đặt lên ngực
      return arm('M89 80 Q93 98 74 88') + `<ellipse cx="71" cy="85.4" rx="5.6" ry="3.9" transform="rotate(-24 71 85.4)" fill="${SKIN}" stroke="${NECK}" stroke-width=".8"/>`
    case 'giang': {
      // tay cầm que chỉ vàng hướng lên bảng
      const nudge = anim ? '<animateTransform attributeName="transform" type="translate" values="0 0;1.8 -2;0 0" dur="1.4s" repeatCount="indefinite"/>' : ''
      return `<g>${nudge}${arm('M89 80 Q104 84 107 70')}${ln('M106 71 L131 43', YD, 3.4)}${ln('M106 71 L131 43', Y, 2.2)}<circle cx="131.4" cy="42.6" r="1.7" fill="${WHITE}"/>${fist(107, 69)}</g>`
    }
    case 'nghe':
      // tay khum gần tai
      return arm('M31 80 Q22 68 36.4 52') + palm(38.6, 47, -18)
    default:
      return ''
  }
}

const star = (x: number, y: number, s: number) =>
  `M${f(x)} ${f(y - s)} L${f(x + s * 0.28)} ${f(y - s * 0.28)} L${f(x + s)} ${f(y)} L${f(x + s * 0.28)} ${f(y + s * 0.28)} L${f(x)} ${f(y + s)} L${f(x - s * 0.28)} ${f(y + s * 0.28)} L${f(x - s)} ${f(y)} L${f(x - s * 0.28)} ${f(y - s * 0.28)} Z`
const twinkle = (anim: boolean, begin: string) =>
  anim ? `<animate attributeName="opacity" values="0.25;1;0.25" dur="1.4s" begin="${begin}" repeatCount="indefinite"/>` : ''

function extras(e: Emotion, anim: boolean): string {
  if (e === 'hi')
    return `<path d="${star(22, 26, 3.6)}" fill="${Y}">${twinkle(anim, '0s')}</path><path d="${star(31, 14, 2.4)}" fill="${Y}">${twinkle(anim, '0.7s')}</path>`
  if (e === 'lac')
    return `<path d="${star(95, 20, 4.4)}" fill="${Y}" stroke="${YD}" stroke-width=".5">${twinkle(anim, '0s')}</path><path d="${star(104, 32, 2.6)}" fill="${Y}">${twinkle(anim, '0.7s')}</path>`
  if (e === 'ai') {
    const float = anim
      ? '<animateTransform attributeName="transform" type="translate" values="0 2;0 -3;0 2" dur="2.8s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.5;1;0.5" dur="2.8s" repeatCount="indefinite"/>'
      : ''
    return `<g opacity=".9">${float}<path d="M98 31 C92.6 27 94.4 21.6 98 24.4 C101.6 21.6 103.4 27 98 31 Z" fill="${CHEEK}" stroke="#E07B70" stroke-width=".7"/></g>`
  }
  return ''
}

// Đầu: nghiêng tĩnh (ai: đồng cảm, nghe: lắng nghe) hoặc lắc nhẹ (ố).
function headGroup(k: TeacherKind, e: Emotion, anim: boolean): string {
  const tilt = e === 'bi' ? ' transform="rotate(6 60 60)"' : e === 'nghe' ? ' transform="rotate(-7 60 60)"' : ''
  const shake =
    e === 'o' && anim
      ? '<animateTransform attributeName="transform" type="rotate" values="0 60 60;-4 60 60;4 60 60;-3 60 60;0 60 60;0 60 60" keyTimes="0;0.1;0.2;0.3;0.4;1" dur="2.6s" repeatCount="indefinite"/>'
      : ''
  return `<g${tilt}><g>${shake}${head(k, e, anim)}</g></g>`
}

function figure(k: TeacherKind, e: Emotion, anim: boolean): string {
  const bob = anim
    ? `<animateTransform attributeName="transform" type="translate" values="0 0;0 -1.4;0 0" dur="${e === 'giang' ? '2.6s' : '3.2s'}" repeatCount="indefinite"/>`
    : ''
  // nghe: tay khum vẽ sau đầu để nằm trước tai/tóc
  // thân và tay nâng 5 đơn vị cho cổ ngắn lại, vai lộ trên bục
  return `<g>${bob}<g transform="translate(0 -5)">${torso(k)}</g>${headGroup(k, e, anim)}<g transform="translate(0 -5)">${gesture(e, anim)}</g>${extras(e, anim)}</g>`
}

const safeKind = (k: unknown): TeacherKind => (isTeacherKind(k) ? k : 'thay')
const safeEmotion = (e: unknown): Emotion => (isEmotion(e) ? e : 'giang')

function lectern(flashRed: boolean, anim: boolean): string {
  const front = 'M40 78 h96 l-7 30 h-82 z'
  const flash = flashRed
    ? `<path d="${front}" fill="#E5484D" opacity="0">${anim ? '<animate attributeName="opacity" values="0;0.45;0" dur="1.4s" fill="freeze"/>' : ''}</path>`
    : ''
  return (
    `<path d="${front}" fill="${G}"/>${flash}` +
    `<rect x="34" y="72" width="108" height="9" rx="3" fill="${GD}"/>` +
    `<rect x="52" y="85" width="72" height="15" rx="4" fill="${Y}"/>` +
    `<text x="88" y="95.6" text-anchor="middle" font-size="9.5" font-weight="700" fill="${INK}" ${FONT}>Lớp học NNC</text>`
  )
}

// Bục giảng có giảng viên (Svg isInteractive, SMIL). Khoảng 176×110.
export function teacherPodiumSvg(kind: TeacherKind, emotion: Emotion, presence: TeacherPresence): string {
  const k = safeKind(kind)
  const e = safeEmotion(emotion)
  const p: TeacherPresence = presence === 'wait' || presence === 'away' ? presence : 'present'
  const place = 'translate(34 -2) scale(0.9)'
  let scene: string
  if (p === 'away') {
    // vắng: bục trống, nét phấn mờ chỗ giảng viên đứng, biển "Lớp tạm nghỉ"
    const ghost = `<g opacity=".32" stroke="${WHITE}" stroke-width="1.4" stroke-dasharray="3 3" fill="none"><ellipse cx="88" cy="34" rx="14.4" ry="17"/><path d="M53 74 C54 64 62 59 76 57.4 L100 57.4 C114 59 122 64 123 74"/></g>`
    const sign =
      `${ln('M68 69 L65 73 M108 69 L111 73', GD, 1.6)}` +
      `<rect x="55" y="53.6" width="66" height="16" rx="3" fill="${Y}" stroke="${YD}" stroke-width="1"/>` +
      `<text x="88" y="64.6" text-anchor="middle" font-size="8.6" font-weight="700" fill="${INK}" ${FONT}>Lớp tạm nghỉ</text>`
    return `${svgOpen('0 0 176 110', 176, 110)}${ghost}${lectern(false, false)}${sign}</svg>`
  }
  const fig = `<g transform="${place}">${figure(k, e, true)}</g>`
  if (p === 'wait') {
    // chờ lớp: mờ, thấp xuống chỉ ló đầu và vai, nhún chậm
    scene = `<g opacity=".75" transform="translate(0 13)"><g><animateTransform attributeName="transform" type="translate" values="0 0;0 -3.5;0 0" dur="3.8s" repeatCount="indefinite"/>${fig}</g></g>`
  } else {
    scene = `<g><animateTransform attributeName="transform" type="translate" values="0 34;0 -2;0 0" keyTimes="0;0.75;1" dur="0.7s" fill="freeze"/>${fig}</g>`
  }
  // đang giảng: vài dòng phấn trên bảng ở góc phải để que chỉ hướng vào
  const board =
    e === 'giang' && p === 'present'
      ? ln('M141 11 h24 M141 17 h17 M141 23 h22', WHITE, 1.4, ' opacity=".55"') + ln('M162 15.6 l2 2 l4 -4.4', Y, 1.4, ' opacity=".8"')
      : ''
  return `${svgOpen('0 0 176 110', 176, 110)}${board}${scene}${lectern(e === 'no' && p === 'present', true)}</svg>`
}

// Avatar tĩnh cạnh lời giảng (không SMIL). Khoảng 100×100: đầu và vai, cảm xúc "hỉ".
export function teacherAvatarSvg(kind: TeacherKind): string {
  const k = safeKind(kind)
  const id = `lhav-${k}`
  return (
    `${svgOpen('0 0 100 100', 100, 100)}<defs><clipPath id="${id}"><circle cx="50" cy="50" r="48"/></clipPath></defs>` +
    `<circle cx="50" cy="50" r="48" fill="${BOARD}"/>` +
    `<g clip-path="url(#${id})"><g transform="translate(50 52) scale(0.9) translate(-60 -46)">${figure(k, 'hi', false)}</g></g>` +
    `<circle cx="50" cy="50" r="48" fill="none" stroke="${Y}" stroke-width="2"/></svg>`
  )
}

// ── Giờ Viêng Chăn (UTC+7), tính tay từ chuỗi ISO — không dùng Intl / múi giờ máy ──
const HOUR = 3600000
const VIENTIANE_OFFSET = 7 * HOUR

// ISO 8601 (có Z hoặc ±hh:mm; không có múi giờ thì coi là UTC) hoặc epoch giây/mili-giây dạng chữ số.
function parseIsoMs(s: unknown): number | undefined {
  if (typeof s !== 'string') return undefined
  const t = s.trim()
  if (/^\d{9,13}$/.test(t)) {
    const v = Number(t)
    return v < 1e12 ? v * 1000 : v
  }
  const m = /^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2})(?:[.,](\d+))?)?)?\s*(Z|z|[+-]\d{2}(?::?\d{2})?)?$/.exec(t)
  if (!m) return undefined
  const num = (i: number) => Number(m[i] ?? '0')
  const [y, mo, d, hh, mi, ss] = [num(1), num(2), num(3), num(4), num(5), num(6)]
  if (mo < 1 || mo > 12 || d < 1 || d > 31 || hh > 24 || mi > 59 || ss > 60) return undefined
  const ms = m[7] ? Math.round(Number(`0.${m[7]}`) * 1000) : 0
  let off = 0
  const tz = m[8]
  if (tz && tz !== 'Z' && tz !== 'z') {
    const sign = tz[0] === '-' ? -1 : 1
    const digits = tz.slice(1).replace(':', '')
    off = sign * (Number(digits.slice(0, 2)) * 60 + Number(digits.slice(2, 4) || '0'))
  }
  const v = Date.UTC(y, mo - 1, d, hh, mi, ss, ms) - off * 60000
  return Number.isFinite(v) ? v : undefined
}

const pad2 = (n: number) => (n < 10 ? '0' : '') + String(n)
const hhmmAt = (ms: number) => {
  const d = new Date(ms + VIENTIANE_OFFSET)
  return `${pad2(d.getUTCHours())}:${pad2(d.getUTCMinutes())}`
}
// Thứ trong tuần theo giờ Viêng Chăn, bắt đầu từ thứ Hai: 0 = T2 … 6 = CN.
const mondayIndexAt = (ms: number) => (new Date(ms + VIENTIANE_OFFSET).getUTCDay() + 6) % 7

// "HH:MM" theo giờ Viêng Chăn (UTC+7); chuỗi rỗng nếu không đọc được giờ.
export function vientianeHHMM(iso: string): string {
  const ms = parseIsoMs(iso)
  return ms === undefined ? '' : hhmmAt(ms)
}

const pctOf = (v: unknown) => (typeof v === 'number' && Number.isFinite(v) ? Math.min(100, Math.max(0, v)) : 0)
const textW = (s: string, fs: number) => s.length * fs * 0.58
const NO_RESET = 'Chưa đọc được giờ reset — xem /status'

// Thẻ 7: dòng thời gian 5 giờ từ số liệu thật. resetsAt/now: ISO. Hiển thị giờ UTC+7.
export function usageTimelineSvg(o: { percentUsed: number; resetsAt?: string; now: string }): string {
  const X0 = 20
  const X1 = 580
  const BW = X1 - X0
  const pct = pctOf(o.percentUsed)
  const end = parseIsoMs(o.resetsAt)
  const now = parseIsoMs(o.now)
  const parts: string[] = [
    `<rect width="600" height="80" rx="10" fill="${BOARD}"/>`,
    `<text x="${X0}" y="17" font-size="13" font-weight="700" fill="${WHITE}" ${FONT}>Khung 5 giờ</text>`,
    `<text x="${X1}" y="17" text-anchor="end" font-size="13" font-weight="700" fill="${Y}" ${FONT}>đã dùng ${Math.round(pct)}%</text>`,
    `<rect x="${X0}" y="28" width="${BW}" height="16" rx="8" fill="${TRACK}"/>`,
  ]
  const fw = (BW * pct) / 100
  if (fw > 0) parts.push(`<rect x="${X0}" y="28" width="${f(Math.max(fw, 2))}" height="16" rx="${f(Math.min(8, Math.max(fw, 2) / 2))}" fill="${AMBER}"/>`)
  for (let i = 1; i < 5; i++) {
    const x = X0 + (BW * i) / 5
    parts.push(`<line x1="${f(x)}" y1="30" x2="${f(x)}" y2="42" stroke="${WHITE}" stroke-opacity=".22" stroke-width="1"/>`)
  }
  if (end === undefined) {
    parts.push(`<text x="${X0}" y="66" font-size="12" fill="${WHITE}" fill-opacity=".85" ${FONT}>${NO_RESET}</text>`)
  } else {
    const start = end - 5 * HOUR
    const sTxt = `đầu phiên ${hhmmAt(start)}`
    const eTxt = `reset ${hhmmAt(end)}`
    parts.push(
      `<text x="${X0}" y="66" font-size="12" fill="${WHITE}" fill-opacity=".8" ${FONT}>${sTxt}</text>`,
      `<text x="${X1}" y="66" text-anchor="end" font-size="12" font-weight="700" fill="${Y}" ${FONT}>${eTxt}</text>`,
    )
    if (now !== undefined) {
      const frac = Math.min(1, Math.max(0, (now - start) / (5 * HOUR)))
      const nx = X0 + frac * BW
      const nTxt = `bây giờ ${hhmmAt(now)}`
      const wN = textW(nTxt, 12)
      let left = nx - wN / 2
      const minL = X0 + textW(sTxt, 12) + 10
      const maxR = X1 - textW(eTxt, 12) - 10
      if (left < minL) left = minL
      if (left + wN > maxR) left = maxR - wN
      const lx = left + wN / 2
      parts.push(
        `<line x1="${f(nx)}" y1="26" x2="${f(nx)}" y2="47" stroke="${WHITE}" stroke-width="2.4" stroke-linecap="round"/>`,
        `<path d="M${f(nx - 4)} 22 h8 l-4 4.5 z" fill="${WHITE}"/>`,
        ln(`M${f(nx)} 48 L${f(lx)} 54`, WHITE, 1, ' opacity=".55"'),
        `<text x="${f(lx)}" y="66" text-anchor="middle" font-size="12" font-weight="700" fill="${WHITE}" ${FONT}>${nTxt}</text>`,
      )
    }
  }
  return `${svgOpen('0 0 600 80', 600, 80)}${parts.join('')}</svg>`
}

const WEEKDAYS = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']

// Thẻ 8: lịch tuần, đánh dấu ngày/giờ reset tuần cố định (UTC+7).
export function weekResetSvg(o: { percentUsed: number; resetsAt?: string; now: string }): string {
  const pct = Math.round(pctOf(o.percentUsed))
  const end = parseIsoMs(o.resetsAt)
  const now = parseIsoMs(o.now)
  const today = now === undefined ? undefined : mondayIndexAt(now)
  const resetDay = end === undefined ? undefined : mondayIndexAt(end)
  const parts: string[] = [
    `<rect width="600" height="70" rx="10" fill="${BOARD}"/>`,
    `<text x="20" y="17" font-size="13" font-weight="700" fill="${WHITE}" ${FONT}>đã dùng <tspan fill="${Y}">${pct}%</tspan> tuần này</text>`,
  ]
  if (end === undefined) parts.push(`<text x="580" y="17" text-anchor="end" font-size="11.5" fill="${WHITE}" fill-opacity=".85" ${FONT}>${NO_RESET}</text>`)
  const W = 74
  const GAP = 7
  const Y0 = 25
  const BH = 38
  WEEKDAYS.forEach((name, i) => {
    const x = 20 + i * (W + GAP)
    const isReset = i === resetDay
    const isToday = i === today
    const past = today !== undefined && i < today
    const cx = x + W / 2
    let cell =
      `<rect x="${x}" y="${Y0}" width="${W}" height="${BH}" rx="6" fill="${isReset ? Y : TRACK}"/>` +
      `<text x="${cx}" y="${Y0 + 15}" text-anchor="middle" font-size="12" font-weight="700" fill="${isReset ? INK : WHITE}" ${FONT}>${name}</text>`
    if (isReset && end !== undefined)
      cell += `<text x="${cx}" y="${Y0 + 31}" text-anchor="middle" font-size="10" font-weight="700" fill="${INK}" ${FONT}>reset ${hhmmAt(end)}</text>`
    else if (isToday) cell += `<text x="${cx}" y="${Y0 + 31}" text-anchor="middle" font-size="10" fill="${WHITE}" fill-opacity=".85" ${FONT}>hôm nay</text>`
    parts.push(past && !isReset ? `<g opacity=".55">${cell}</g>` : cell)
    if (isToday) parts.push(`<rect x="${x - 2}" y="${Y0 - 2}" width="${W + 4}" height="${BH + 4}" rx="8" fill="none" stroke="${WHITE}" stroke-width="2"/>`)
  })
  return `${svgOpen('0 0 600 70', 600, 70)}${parts.join('')}</svg>`
}

// Đồng hồ phần học: vòng còn lại, màu theo động lực. Khoảng 44×44.
export function segmentClockSvg(o: { elapsedMs: number; totalMs: number; drive: Drive }): string {
  const total = Number.isFinite(o.totalMs) && o.totalMs > 0 ? o.totalMs : 0
  const elapsed = Number.isFinite(o.elapsedMs) ? Math.max(0, o.elapsedMs) : 0
  const leftMs = Math.max(0, total - elapsed)
  const frac = total > 0 ? Math.min(1, leftMs / total) : 0
  const minutes = Math.ceil(leftMs / 60000)
  const color = DRIVE_COLOR[o.drive] ?? G
  const C = 2 * Math.PI * 17
  const ring =
    frac >= 0.999
      ? `<circle cx="22" cy="22" r="17" fill="none" stroke="${color}" stroke-width="4.5"/>`
      : frac > 0
        ? `<circle cx="22" cy="22" r="17" fill="none" stroke="${color}" stroke-width="4.5" stroke-linecap="round" stroke-dasharray="${f(frac * C)} ${f(C)}" transform="rotate(-90 22 22)"/>`
        : ''
  const pulse = leftMs > 0 && leftMs <= 120000 ? '<animate attributeName="opacity" values="1;0.35;1" dur="1s" repeatCount="indefinite"/>' : ''
  return (
    `${svgOpen('0 0 44 44', 44, 44)}<circle cx="22" cy="22" r="21.5" fill="${TRACK}"/>` +
    `<circle cx="22" cy="22" r="17" fill="none" stroke="${WHITE}" stroke-opacity=".15" stroke-width="4.5"/>` +
    `<g>${pulse}${ring}<text x="22" y="24" text-anchor="middle" font-size="13" font-weight="700" fill="${WHITE}" ${FONT}>${minutes}</text>` +
    `<text x="22" y="32" text-anchor="middle" font-size="6.5" fill="${WHITE}" fill-opacity=".75" ${FONT}>phút</text></g></svg>`
  )
}

// Dùng cho test/preview: danh sách cảm xúc theo thứ tự hỉ, nộ, ái, ố, ai, lạc, giảng, nghe.
export const EMOTION_LIST: readonly Emotion[] = EMOTIONS

// ── v0.6: sao, huy hiệu, hộp quà, vòng thử thách ─────────────────────────────
// Tên và tham số cố định (register.tsx dùng). Không dùng id="…" nào: lồng nhiều huy hiệu vào kệ không bao giờ trùng id.
export type BadgeRef = { id: string; label: string }

const HOT = '#FF6B3D' // đỏ cam 10 giây cuối
const HEART = '#E5484D'
const PAPER = '#FFFFFF'

// Chữ người dùng/giáo viên đưa vào: thoát ký tự XML.
const xmlEsc = (s: unknown) =>
  String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')

const intOf = (v: unknown) => (typeof v === 'number' && Number.isFinite(v) ? Math.max(0, Math.round(v)) : 0)

// Ngôi sao 5 cánh tâm (cx, cy), bán kính ngoài R, trong r.
function starD(cx: number, cy: number, R: number, r: number): string {
  let d = ''
  for (let i = 0; i < 10; i++) {
    const a = -Math.PI / 2 + (i * Math.PI) / 5
    const rr = i % 2 === 0 ? R : r
    d += `${i === 0 ? 'M' : 'L'}${f(cx + rr * Math.cos(a))} ${f(cy + rr * Math.sin(a))}`
  }
  return `${d}Z`
}

// Lấp lánh 4 cánh nhỏ tâm (cx, cy), bán kính s.
const sparkD = (cx: number, cy: number, s: number) => {
  const k = s * 0.28
  return `M${f(cx)} ${f(cy - s)}Q${f(cx + k)} ${f(cy - k)} ${f(cx + s)} ${f(cy)}Q${f(cx + k)} ${f(cy + k)} ${f(cx)} ${f(cy + s)}Q${f(cx - k)} ${f(cy + k)} ${f(cx - s)} ${f(cy)}Q${f(cx - k)} ${f(cy - k)} ${f(cx)} ${f(cy - s)}Z`
}

// Lấp lánh nhấp nháy: tĩnh vẫn hiện (opacity gốc), có SMIL thì nhạt–đậm.
const sparkle = (cx: number, cy: number, s: number, color: string, dur: number, begin = 0) =>
  `<path d="${sparkD(cx, cy, s)}" fill="${color}" opacity=".9"><animate attributeName="opacity" values=".9;.15;.9" dur="${dur}s" begin="${begin}s" repeatCount="indefinite"/></path>`

// Hàng sao trong buổi. Rộng 28 + 24·(min(n,5)−1) (+ chỗ cho "+k"), cao 24.
// n = 0: một sao viền mờ. Sao mới nhất (cuối hàng) lấp lánh.
export function starRowSvg(n: number): string {
  const total = intOf(n)
  const shown = Math.min(total, 5)
  const extra = total - shown
  const slots = Math.max(1, shown)
  const extraTxt = extra > 0 ? `+${extra}` : ''
  const extraW = extra > 0 ? Math.ceil(textW(extraTxt, 13)) + 6 : 0
  const w = 28 + 24 * (slots - 1) + extraW
  const parts: string[] = [`<title>${total} sao</title>`]
  if (total === 0) {
    parts.push(`<path d="${starD(14, 12.5, 10, 4.3)}" fill="none" stroke="${Y}" stroke-opacity=".45" stroke-width="1.4" stroke-linejoin="round"/>`)
  } else {
    for (let i = 0; i < shown; i++) {
      const cx = 14 + i * 24
      const star = `<path d="${starD(0, 0, 10, 4.3)}" fill="${Y}" stroke="${YD}" stroke-width="1.2" stroke-linejoin="round"/><path d="M-3.2 -2.6 L0 -8 L1 -3.4 Z" fill="${PAPER}" opacity=".55"/>`
      if (i === shown - 1)
        parts.push(
          `<g transform="translate(${cx} 12.5)"><g><animateTransform attributeName="transform" type="scale" values="1;1.14;1;1" keyTimes="0;0.15;0.3;1" dur="2.4s" repeatCount="indefinite"/>${star}</g></g>`,
          sparkle(cx + 8, 4, 3.2, PAPER, 2.4),
        )
      else parts.push(`<g transform="translate(${cx} 12.5)">${star}</g>`)
    }
    if (extra > 0)
      parts.push(`<text x="${28 + 24 * (slots - 1) + 2}" y="17.5" font-size="13" font-weight="700" fill="${Y}" ${FONT}>${extraTxt}</text>`)
  }
  return `${svgOpen(`0 0 ${w} 24`, w, 24)}${parts.join('')}</svg>`
}

// ── Huy hiệu ──
// Nhóm màu theo động lực: D3 cam = giao việc, D2 xanh dương = hiểu biết, D1 xanh lá = làm thật/kiểm tra.
// Hình vẽ trong khung 48×48, tâm mề đay (24, 20); hình vẽ nằm trong vòng bán kính ~11.
const PIC_STROKE = `stroke="${INK}" stroke-width="1" stroke-linejoin="round"`

const BADGE_ART: Record<string, { drive: 'D1' | 'D2' | 'D3'; pic: string }> = {
  // Bàn tay trao một tờ giấy
  'giao-viec-dau-tien': {
    drive: 'D3',
    pic:
      `<g transform="rotate(14 27 16)"><rect x="21.5" y="8.5" width="11" height="14" rx="1.3" fill="${PAPER}" ${PIC_STROKE}/>` +
      `<path d="M24 12.5h6M24 15h6M24 17.5h4" stroke="${G}" stroke-width="1.1" stroke-linecap="round"/></g>` +
      `<rect x="10.5" y="24" width="4" height="8" rx="1" fill="${GD}"/>` +
      `<path d="M14.5 24.5h4.5l2.5 -1.6h5.2a1.5 1.5 0 0 1 0 3h-3.6h4.6l4.2 -2.6a1.3 1.3 0 0 1 1.6 2l-4.6 4.2a3 3 0 0 1 -2 .8h-12.4z" fill="${PAPER}" ${PIC_STROKE}/>`,
  },
  // Kính lúp có con mắt
  'mat-tinh': {
    drive: 'D1',
    pic:
      `<path d="M27.6 23.6L33 29" stroke="${INK}" stroke-width="3.4" stroke-linecap="round"/>` +
      `<circle cx="22" cy="18" r="7.8" fill="${PAPER}" stroke="${INK}" stroke-width="1.8"/>` +
      `<path d="M16.4 18q5.6 -5.2 11.2 0q-5.6 5.2 -11.2 0z" fill="${PAPER}" ${PIC_STROKE}/>` +
      `<circle cx="22" cy="18" r="2.3" fill="${INK}"/><circle cx="22.9" cy="17.1" r=".75" fill="${PAPER}"/>`,
  },
  // Chồng thẻ, thẻ trên cùng ghi 9
  'thuoc-9-the': {
    drive: 'D2',
    pic:
      `<rect x="18" y="10" width="12" height="17" rx="1.6" fill="#DCEBFA" ${PIC_STROKE} transform="rotate(-18 24 28)"/>` +
      `<rect x="18" y="10" width="12" height="17" rx="1.6" fill="#DCEBFA" ${PIC_STROKE} transform="rotate(18 24 28)"/>` +
      `<rect x="18" y="10" width="12" height="17" rx="1.6" fill="${PAPER}" ${PIC_STROKE}/>` +
      `<text x="24" y="22.6" text-anchor="middle" font-size="11.5" font-weight="700" fill="${GD}" ${FONT}>9</text>`,
  },
  // Dấu tích trong vòng tròn, kèm trái tim nhỏ ("có tâm")
  'tu-kiem-co-tam': {
    drive: 'D1',
    pic:
      `<circle cx="23" cy="21" r="8.6" fill="${PAPER}" stroke="${INK}" stroke-width="1.2"/>` +
      `<path d="M18.9 21.2l3 3.1l5.6 -6.2" stroke="${GD}" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>` +
      `<path d="M31 15.8l-3.2 -3.1a1.8 1.8 0 0 1 3.2 -1.9a1.8 1.8 0 0 1 3.2 1.9z" fill="${HEART}" stroke="${PAPER}" stroke-width=".8" stroke-linejoin="round"/>`,
  },
  // Người đứng chỉ lên bảng
  'nguoi-day-lai': {
    drive: 'D2',
    pic:
      `<rect x="20.5" y="9.5" width="14" height="11" rx="1" fill="${PAPER}" ${PIC_STROKE}/>` +
      `<path d="M23 13h6M23 15.5h8.5M23 18h4" stroke="${G}" stroke-width="1.1" stroke-linecap="round"/>` +
      `<path d="M18.5 24.2l4 -4.4" stroke="${INK}" stroke-width="1.7" stroke-linecap="round"/>` +
      `<circle cx="15.2" cy="17.6" r="2.8" fill="${PAPER}" ${PIC_STROKE}/>` +
      `<path d="M10.8 31.5v-5.8q0 -4.2 4.4 -4.2q4.4 0 4.4 4.2v5.8z" fill="${PAPER}" ${PIC_STROKE}/>`,
  },
  // Hộp đóng gói có bánh răng
  'dong-goi-skill-dau-tien': {
    drive: 'D3',
    pic:
      `<path d="M24 9.5L33.5 13.3L24 17.1L14.5 13.3Z" fill="${PAPER}" ${PIC_STROKE}/>` +
      `<path d="M14.5 13.3L24 17.1V28.6L14.5 24.8Z" fill="#F1EFE6" ${PIC_STROKE}/>` +
      `<path d="M24 17.1L33.5 13.3V24.8L24 28.6Z" fill="#DCD6C2" ${PIC_STROKE}/>` +
      `<path d="M19.2 11.4L28.8 15.2" stroke="${G}" stroke-width="2"/>` +
      `<g transform="translate(30.5 26)">${[0, 45, 90, 135, 180, 225, 270, 315].map(a => `<rect x="-1.1" y="-6" width="2.2" height="3" fill="${Y}" ${PIC_STROKE} transform="rotate(${a})"/>`).join('')}` +
      `<circle r="4.4" fill="${Y}" ${PIC_STROKE}/><circle r="1.5" fill="${INK}"/></g>`,
  },
  // Vương miện trên cà vạt
  'ban-la-sep': {
    drive: 'D3',
    pic:
      `<path d="M16.5 15.2l1.6 -7l3.6 3.8l2.3 -4.8l2.3 4.8l3.6 -3.8l1.6 7z" fill="${Y}" ${PIC_STROKE}/>` +
      `<path d="M17.8 17l5 .6l-1.6 3.6z M30.2 17l-5 .6l1.6 3.6z" fill="${PAPER}" ${PIC_STROKE}/>` +
      `<path d="M22.2 17.4h3.6l-.8 2.6h-2z" fill="${GD}" ${PIC_STROKE}/>` +
      `<path d="M23 20h2l2.2 7.6l-3.2 3.4l-3.2 -3.4z" fill="${G}" ${PIC_STROKE}/>`,
  },
  // Tia chớp và vệt tốc độ (nhanh tay)
  'nhanh-tay': {
    drive: 'D1',
    pic:
      `<path d="M11.5 15.5h5M10.5 20h6M12 24.5h4" stroke="${PAPER}" stroke-width="1.8" stroke-linecap="round"/>` +
      `<path d="M27.5 7.5l-9 13.5h5.4l-3.2 10.5l10 -14h-5.6z" fill="${Y}" stroke="${INK}" stroke-width="1.1" stroke-linejoin="round"/>`,
  },
}

// Huy hiệu lạ: ngôi sao trên nền xanh NNC.
const GENERIC_PIC = `<path d="${starD(24, 20.5, 9.5, 4)}" fill="${PAPER}" ${PIC_STROKE}/><circle cx="24" cy="20.5" r="1.6" fill="${Y}"/>`

// Thân huy hiệu (không có thẻ <svg>, không có id): dây đeo, vòng vàng, lõi màu động lực, hình vẽ.
function medal(id: string): string {
  const art = BADGE_ART[id]
  const core = art ? DRIVE_COLOR[art.drive] : G
  return (
    `<path d="M15.5 28L10 46.5L14 43.6L17.6 47L23 32Z" fill="${G}"/><path d="M32.5 28L38 46.5L34 43.6L30.4 47L25 32Z" fill="${GD}"/>` +
    `<circle cx="24" cy="20" r="18" fill="${Y}" stroke="${YD}" stroke-width="1"/>` +
    `<path d="M10.4 15.5A14.6 14.6 0 0 1 19.5 6.2" fill="none" stroke="${PAPER}" stroke-opacity=".7" stroke-width="1.6" stroke-linecap="round"/>` +
    `<circle cx="24" cy="20" r="14" fill="${core}" stroke="${YD}" stroke-width="1"/>` +
    (art ? art.pic : GENERIC_PIC)
  )
}

// Một huy hiệu tròn 48×48, có dây đeo; <title> là tên huy hiệu.
export function badgeSvg(id: string, label: string): string {
  return `${svgOpen('0 0 48 48', 48, 48)}<title>${xmlEsc(label)}</title>${medal(String(id ?? ''))}</svg>`
}

const EMPTY_SHELF = 'Chưa có huy hiệu — làm việc thật để nhận!'

// Kệ huy hiệu 240×56: 4 huy hiệu gần nhất (mới nhất bên trái) + "+n" số còn lại.
export function badgeShelfSvg(badges: BadgeRef[]): string {
  const list = Array.isArray(badges) ? badges.filter(b => b && typeof b === 'object') : []
  const parts: string[] = []
  if (list.length === 0) {
    parts.push(
      `<title>${EMPTY_SHELF}</title>`,
      `<circle cx="28" cy="26" r="17" fill="none" stroke="${WHITE}" stroke-opacity=".35" stroke-width="1.6" stroke-dasharray="4 3"/>`,
      `<path d="${starD(28, 26.5, 8, 3.4)}" fill="none" stroke="${Y}" stroke-opacity=".45" stroke-width="1.3" stroke-linejoin="round"/>`,
      `<text x="54" y="24" font-size="12" font-weight="700" fill="${WHITE}" fill-opacity=".6" ${FONT}>Chưa có huy hiệu —</text>`,
      `<text x="54" y="40" font-size="11" fill="${WHITE}" fill-opacity=".6" ${FONT}>làm việc thật để nhận!</text>`,
    )
  } else {
    const latest = list.slice(-4).reverse()
    const more = list.length - latest.length
    latest.forEach((b, i) =>
      parts.push(`<g transform="translate(${2 + i * 52} 4)"><title>${xmlEsc(b.label)}</title>${medal(String(b.id ?? ''))}</g>`),
    )
    if (more > 0) parts.push(`<text x="236" y="33" text-anchor="end" font-size="13" font-weight="700" fill="${Y}" ${FONT}>+${more}</text>`)
  }
  return `${svgOpen('0 0 240 56', 240, 56)}${parts.join('')}</svg>`
}

// Khung hộp quà rộng hơn 64 đơn vị để nắp bật lên không bị cắt; vẫn hiện 64×64.
const GIFT_VB = '-4 -8 72 72'

// Hộp quà khả năng 64×64, vàng/xanh NNC. Đóng: lắc nhẹ. Mở: nắp bật lên, lấp lánh, tấm thẻ ló ra.
export function giftBoxSvg(open: boolean): string {
  const ribbonV = `<rect x="29" y="30" width="6" height="28" fill="${G}"/>`
  const boxBody = `<rect x="12" y="30" width="40" height="28" rx="2" fill="${Y}" stroke="${YD}" stroke-width="1.2"/>${ribbonV}<rect x="12" y="30" width="40" height="4" fill="${YD}" opacity=".35"/>`
  const bow =
    `<path d="M32 22C26 13 18 16 22 21.5C24 23.5 28 23 32 22Z" fill="${G}" stroke="${GD}" stroke-width="1"/>` +
    `<path d="M32 22C38 13 46 16 42 21.5C40 23.5 36 23 32 22Z" fill="${G}" stroke="${GD}" stroke-width="1"/>` +
    `<circle cx="32" cy="22" r="2.4" fill="${GD}"/>`
  const lid = `<rect x="9" y="22" width="46" height="9" rx="2" fill="${Y}" stroke="${YD}" stroke-width="1.2"/><rect x="29" y="22" width="6" height="9" fill="${G}"/>${bow}`
  if (!open) {
    const wobble = `<animateTransform attributeName="transform" type="rotate" values="0 32 58;0 32 58;-5 32 58;4.5 32 58;-3 32 58;1.5 32 58;0 32 58" keyTimes="0;0.55;0.65;0.75;0.85;0.93;1" dur="3s" repeatCount="indefinite"/>`
    return `${svgOpen(GIFT_VB, 64, 64)}<title>Hộp quà khả năng</title><ellipse cx="32" cy="59.5" rx="22" ry="2.5" fill="#000" opacity=".25"/><g>${wobble}${boxBody}${lid}</g></svg>`
  }
  const rays = [-38, -14, 14, 38]
    .map(a => `<path d="M32 30L28.5 4H35.5Z" fill="${Y}" opacity=".22" transform="rotate(${a} 32 30)"/>`)
    .join('')
  const card =
    `<g transform="rotate(-6 32 30)"><rect x="22" y="13" width="20" height="24" rx="2" fill="${PAPER}" stroke="${GD}" stroke-width="1.2"/>` +
    `<rect x="22" y="13" width="20" height="5" rx="2" fill="${G}"/>` +
    `<path d="${starD(32, 25, 4, 1.7)}" fill="${Y}" stroke="${YD}" stroke-width=".8"/></g>`
  const cardRise = `<animateTransform attributeName="transform" type="translate" values="0 0;0 -1.5;0 0" dur="2s" repeatCount="indefinite"/>`
  const lidFloat = `<animateTransform attributeName="transform" type="translate" values="0 0;0 -1.8;0 0" dur="2s" repeatCount="indefinite"/>`
  return (
    `${svgOpen(GIFT_VB, 64, 64)}<title>Hộp quà đã mở</title><ellipse cx="32" cy="59.5" rx="22" ry="2.5" fill="#000" opacity=".25"/>${rays}` +
    `<rect x="12" y="28" width="40" height="5" rx="1.5" fill="${GD}"/>` +
    `<g>${cardRise}${card}</g>${boxBody}` +
    `<g>${lidFloat}<g transform="translate(-4 -14) rotate(-20 9 31)">${lid}</g></g>` +
    sparkle(51, 15, 4, Y, 1.6) +
    sparkle(8, 40, 3, PAPER, 1.9, 0.5) +
    sparkle(56, 38, 2.6, PAPER, 1.4, 0.9) +
    sparkle(44, 6, 2.4, PAPER, 2.1, 0.3) +
    `</svg>`
  )
}

// Vòng đếm ngược thử thách 56×56: số giây (làm tròn lên, không âm); 10 giây cuối đỏ cam và nhịp; 0 → "Hết giờ".
export function challengeRingSvg(o: { remainingMs: number; totalMs: number }): string {
  const total = Number.isFinite(o?.totalMs) && o.totalMs > 0 ? o.totalMs : 0
  const leftMs = Number.isFinite(o?.remainingMs) ? Math.max(0, o.remainingMs) : 0
  const secs = Math.max(0, Math.ceil(leftMs / 1000))
  const frac = total > 0 ? Math.min(1, leftMs / total) : secs > 0 ? 1 : 0
  const last = secs > 0 && secs <= 10
  const color = last ? HOT : AMBER
  const R = 22.5
  const C = 2 * Math.PI * R
  const ring =
    secs === 0
      ? ''
      : frac >= 0.999
        ? `<circle cx="28" cy="28" r="${R}" fill="none" stroke="${color}" stroke-width="5"/>`
        : `<circle cx="28" cy="28" r="${R}" fill="none" stroke="${color}" stroke-width="5" stroke-linecap="round" stroke-dasharray="${f(Math.max(0.5, frac * C))} ${f(C)}" transform="rotate(-90 28 28)"/>`
  const pulse = last
    ? `<animate attributeName="opacity" values="1;.4;1" dur="1s" repeatCount="indefinite"/>`
    : ''
  const halo = last
    ? `<circle cx="28" cy="28" r="26.5" fill="none" stroke="${HOT}" stroke-width="1.5" opacity=".6"><animate attributeName="r" values="24;27.2;24" dur="1s" repeatCount="indefinite"/><animate attributeName="opacity" values=".7;0;.7" dur="1s" repeatCount="indefinite"/></circle>`
    : ''
  const fs = secs >= 1000 ? 11 : secs >= 100 ? 14 : 17
  const centre =
    secs === 0
      ? `<text x="28" y="31.5" text-anchor="middle" font-size="8.5" font-weight="700" fill="${Y}" ${FONT}>Hết giờ</text>`
      : `<text x="28" y="${f(28 + fs * 0.25)}" text-anchor="middle" font-size="${fs}" font-weight="700" fill="${last ? Y : WHITE}" ${FONT}>${secs}</text>` +
        `<text x="28" y="${f(28 + fs * 0.25 + 9)}" text-anchor="middle" font-size="7" fill="${WHITE}" fill-opacity=".75" ${FONT}>giây</text>`
  return (
    `${svgOpen('0 0 56 56', 56, 56)}<title>${secs === 0 ? 'Hết giờ' : `Còn ${secs} giây`}</title>` +
    `<circle cx="28" cy="28" r="27.5" fill="${TRACK}"/>${halo}` +
    `<circle cx="28" cy="28" r="${R}" fill="none" stroke="${secs === 0 ? HOT : WHITE}" stroke-opacity="${secs === 0 ? '.75' : '.15'}" stroke-width="5"/>` +
    `<g>${pulse}${ring}</g>${centre}</svg>`
  )
}

// ── v0.8: thanh dưới ô nhập (mô hình) và bộ lọc SVG của bảng ─────────────────────
// Thanh dưới ô nhập của app Claude Desktop: trái = nhãn chế độ quyền; phải = tên model, effort, vòng tròn dùng.
// Thư mục làm việc và "This computer" nằm ở đầu phiên, KHÔNG nằm trong thanh này.

const BAR_PAPER = '#FFFDF0'
const BAR_INK = '#1f2a1f'
const BAR_G = '#008816'
const BAR_GD = '#006D11'
const BAR_Y = '#FFEA00'
const BAR_YD = '#C9A800'
const BAR_FONT = `font-family="'Leelawadee UI','Phetsarath OT','Noto Sans Lao',sans-serif"`
const clip = (s: string | undefined, n: number) => (!s ? '' : s.length > n ? s.slice(0, n - 1) + '…' : s)

export type BarArea = 'mode' | 'model' | 'effort' | 'circle'
// Nhãn nào chỉ vào vùng nào: vòng tròn là chỗ xem context và hạn mức.
export const BAR_AREA: Record<string, BarArea> = { mode: 'mode', model: 'model', effort: 'effort', context: 'circle', usage5: 'circle', usageWeek: 'circle' }

export function bottomBarSvg(o: { mode?: string; model?: string; effort?: string; percent?: number | null; point?: string | null }): string {
  const W = 480
  const H = 64
  const mode = clip(o.mode, 22) || '—'
  const model = clip(o.model, 14) || '—'
  const effort = clip(o.effort, 10) || '—'
  const cw = 7.4
  const modeW = Math.max(70, mode.length * cw + 24)
  const effW = Math.max(54, effort.length * cw + 20)
  const modW = Math.max(60, model.length * cw + 20)
  const effX = 450 - effW
  const modX = effX - 4 - modW
  const area = o.point ? BAR_AREA[o.point] : undefined
  const zones: Record<BarArea, { x: number; w: number }> = {
    mode: { x: 8, w: modeW + 8 },
    model: { x: modX, w: modW },
    effort: { x: effX, w: effW },
    circle: { x: 436, w: 36 },
  }
  const hl = area
    ? (() => {
        const z = zones[area]
        const cx = z.x + z.w / 2
        return (
          `<rect x="${f(z.x)}" y="17" width="${f(z.w)}" height="38" rx="9" fill="${BAR_Y}" stroke="${BAR_YD}" stroke-width="2"/>` +
          `<path d="M${f(cx - 9)} 1 L${f(cx + 9)} 1 L${f(cx)} 13 Z" fill="${BAR_Y}" stroke="${BAR_YD}" stroke-width="1.5" stroke-linejoin="round"/>`
        )
      })()
    : ''
  const p = typeof o.percent === 'number' && Number.isFinite(o.percent) ? Math.min(100, Math.max(0, o.percent)) : null
  const R = 9
  const C = 2 * Math.PI * R
  const arc = p != null && p > 0 ? `<circle cx="454" cy="36" r="${R}" fill="none" stroke="${BAR_GD}" stroke-width="4" stroke-linecap="round" stroke-dasharray="${f(Math.max(1, (p / 100) * C))} ${f(C)}" transform="rotate(-90 454 36)"/>` : ''
  const t = (x: number, txt: string, extra = '') => `<text x="${f(x)}" y="41" font-size="13" fill="${BAR_INK}" ${BAR_FONT}${extra}>${xmlEsc(txt)}</text>`
  const what = area === 'mode' ? mode : area === 'model' ? model : area === 'effort' ? effort : area === 'circle' ? 'usage' : ''
  return (
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}"><title>${xmlEsc(`Claude Desktop · ${mode} · ${model} · ${effort}${what && area ? ` · ▼ ${what}` : ''}`)}</title>` +
    `<rect x="1" y="15" width="${W - 2}" height="46" rx="12" fill="${BAR_PAPER}" stroke="${BAR_INK}" stroke-opacity=".25" stroke-width="1.5"/>` +
    hl +
    `<circle cx="20" cy="36" r="4" fill="${BAR_G}"/>` +
    t(30, mode, ' font-weight="600"') +
    t(modX + 10, model) +
    t(effX + 10, effort) +
    `<circle cx="454" cy="36" r="${R}" fill="none" stroke="${BAR_INK}" stroke-opacity=".18" stroke-width="4"/>${arc}` +
    `</svg>`
  )
}

// Bảng lớp: SVG của giáo viên chỉ nhận khi sạch và ≤ 16 KB. Bỏ script, foreignObject, thuộc tính on…, href ra ngoài.
export const SVG_MAX_BYTES = 16 * 1024
const byteLen = (s: string) => (typeof TextEncoder !== 'undefined' ? new TextEncoder().encode(s).length : s.length)
const BAD_TAGS = 'script|foreignobject|iframe|object|embed|audio|video|link|meta|base'
const TAG_RE = /<(\/?)([a-zA-Z][^\s/>]*)((?:\s+[^\s=>/]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>"']+))?)*)\s*(\/?)>/g
const ATTR_RE = /([^\s=>/]+)(?:\s*=\s*("[^"]*"|'[^']*'|[^\s>"']+))?/g

export function sanitizeSvg(src: unknown): string | null {
  if (typeof src !== 'string') return null
  if (byteLen(src) > SVG_MAX_BYTES) return null
  let s = src.trim()
  if (!/^<svg[\s>]/i.test(s) || !/<\/svg>$/i.test(s)) return null
  if (/<!doctype|<!entity|<\?|<!\[cdata/i.test(s)) return null
  s = s.replace(/<!--[\s\S]*?-->/g, '')
  const badEl = new RegExp(`<\s*(${BAD_TAGS})\b[\s\S]*?<\s*/\s*\1\s*>`, 'gi')
  const badStyle = /<\s*style\b[^>]*>[^]*?(@import|url\s*\()[^]*?<\s*\/\s*style\s*>/gi
  for (let i = 0; i < 6; i++) {
    const before = s
    s = s.replace(badEl, '').replace(badStyle, '')
    s = s.replace(TAG_RE, (_m, close: string, name: string, attrs: string, selfClose: string) => {
      const lower = name.toLowerCase()
      if (new RegExp(`^(${BAD_TAGS})$`).test(lower)) return ''
      if (close) return `</${name}>`
      const kept: string[] = []
      let dropTag = false
      for (const a of attrs.matchAll(ATTR_RE)) {
        const an = a[1] ?? ''
        const raw = a[2] ?? ''
        const val = raw.replace(/^["']|["']$/g, '')
        const al = an.toLowerCase()
        if (/^on/.test(al) || al === 'src') continue
        if (/^(xlink:)?href$/.test(al) && !val.trim().startsWith('#')) continue
        if (/javascript:|vbscript:|data:text\/html/i.test(val)) continue
        if (al === 'style' && /url\s*\(|expression|@import/i.test(val)) continue
        if (al === 'attributename' && /^(xlink:)?href$|^on/i.test(val.trim())) dropTag = true
        kept.push(raw ? `${an}=${/^["']/.test(raw) ? raw : `"${val}"`}` : an)
      }
      if (dropTag || lower === 'set') return ''
      return `<${name}${kept.length ? ' ' + kept.join(' ') : ''}${selfClose ? '/' : ''}>`
    })
    if (s === before) break
  }
  s = s.trim()
  if (!/^<svg[\s>]/i.test(s) || !/<\/svg>$/i.test(s)) return null
  if (new RegExp(`<\s*/?\s*(${BAD_TAGS})`, 'i').test(s) || /\son[a-z0-9_-]+\s*=/i.test(s) || /javascript:/i.test(s)) return null
  return byteLen(s) <= SVG_MAX_BYTES ? s : null
}

// Cỡ hiển thị của SVG giáo viên: lấy width/height hoặc viewBox, thu về tối đa maxW giữ tỉ lệ.
export function svgBox(src: string, maxW: number, maxH = 200): { width: number; height: number } {
  const head = /<svg\b[^>]*>/i.exec(src)?.[0] ?? ''
  const num = (re: RegExp) => {
    const m = re.exec(head)
    const v = m ? Number(m[1]) : NaN
    return Number.isFinite(v) && v > 0 ? v : null
  }
  let w = num(/\swidth="([0-9.]+)(?:px)?"/i)
  let h = num(/\sheight="([0-9.]+)(?:px)?"/i)
  const vb = /\sviewBox="\s*[-0-9.]+[ ,]+[-0-9.]+[ ,]+([0-9.]+)[ ,]+([0-9.]+)\s*"/i.exec(head)
  if ((!w || !h) && vb) {
    const vw = Number(vb[1])
    const vh = Number(vb[2])
    if (vw > 0 && vh > 0) {
      w = w ?? vw
      h = h ?? (w * vh) / vw
    }
  }
  w = w ?? maxW
  h = h ?? maxH
  const k = Math.min(1, maxW / w, maxH / h)
  return { width: Math.round(w * k), height: Math.round(h * k) }
}
