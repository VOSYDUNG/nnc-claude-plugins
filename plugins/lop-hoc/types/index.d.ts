// Lớp học NNC v0.6 — kiểu dữ liệu của mod lop-hoc.
// Hợp đồng: docs/oser-r2/LOP-HOC-V05-CONTRACT.md (§3 state lop-hoc/2, §4 giáo án, §8 bộ năng lực giáo viên).

export type LessonStatus = 'active' | 'paused' | 'done'
export type TeacherKindId = 'thay' | 'co'
export type EmotionId = 'hi' | 'no' | 'ai' | 'o' | 'bi' | 'lac' | 'giang' | 'nghe'
export type DriveId = 'D1' | 'D2' | 'D3' | 'ket-noi'
export type BranchId = 'vung' | 'dang-len' | 'can-do'
export type PanelKind = 'usage' | 'claude'
export type LessonMinutes = 15 | 30 | 45

export type LessonPart = { label: string; done: boolean }
export type LessonSkill = { label: string; done: boolean }
export type LessonTask = { title?: string; source?: string; check?: string }

// v0.6 (hợp đồng §8.1): lệnh một chạm, kiểu tương tác, thử thách có giờ, sao, huy hiệu, hộp quà.
export type OneTouch = { label: string; text: string }
export type LessonActivity = { kind: string; started_at: string }
export type LessonChallenge = { title: string; seconds: number; started_at: string }
export type LessonBadge = { id: string; label: string }
// .lop-hoc/huy-hieu.json (mod ghi, §8.2).
export type BadgeEntry = { id: string; label: string; date: string }
export type BadgeFile = { schema: 'lop-hoc/huy-hieu-1'; badges: BadgeEntry[] }

// .lop-hoc/state.json do giáo viên (Skill) ghi; mod chỉ đọc.
export type LessonState = {
  schema: 'lop-hoc/2'
  status: LessonStatus
  lesson?: { id?: string; minutes?: number; started_at?: string }
  segment?: { id: string; title: string; drive: DriveId }
  teacher?: { kind?: TeacherKindId; name?: string; emotion?: EmotionId }
  address?: string
  branch?: BranchId | null
  next_action?: string
  destination?: string
  result_parts?: LessonPart[]
  skills?: LessonSkill[]
  help_needed?: boolean
  // Giáo viên xin bục giảng mở một bảng đặc biệt: dòng thời gian usage, hoặc "Claude của tôi".
  panel?: PanelKind | null
  updated_at?: string
  clock?: { segment_started_at?: string; paused?: boolean; absent_strikes?: number }
  // v0.6 — đều tuỳ chọn; mod đọc phòng thủ, sai kiểu thì bỏ qua.
  one_touch?: OneTouch | null
  activity?: LessonActivity | null
  challenge?: LessonChallenge | null
  stars?: number
  badges_new?: LessonBadge[]
  gift_box?: boolean
}

// Bản cũ v0.4 (lop-hoc/1) vẫn đọc được: stage 0–5 được đổi sang phần học.
export type LessonStateV1 = {
  schema: 'lop-hoc/1'
  status: LessonStatus
  stage: number
  question_count?: number
  destination?: string
  task?: LessonTask
  skills?: LessonSkill[]
  work_folder?: string | null
  next_action?: string
  result_parts?: LessonPart[]
  updated_at?: string
}

// Giáo án theo giờ (hợp đồng §4).
export type PlanSegment = { id: string; title: string; minutes: number; drive: DriveId }

// Đồng hồ buổi học do mod giữ ($.state), không ghi vào state.json.
export type Lesson = {
  minutes: LessonMinutes
  teacher: TeacherKindId
  startedAt: number
  // Tổng thời gian đã tạm nghỉ/xin phép (ms), cộng vào lịch các phần còn lại.
  shiftMs: number
  pausedAt: number | null
  pause: 'absent' | 'xin-phep' | null
  pauseNote: string
  over: 'ket-thuc' | 'xin-nghi' | null
  // Chỉ số phần đã báo cho giáo viên (0 = Vào lớp, báo bằng "Mở buổi").
  announced: number
  // Khoá các tín hiệu đã gửi: không gửi trùng.
  sent: string[]
  lastCueAt: number
  // Số lần liên tiếp không tương tác (hết hạn trả lời hoặc ngồi im 60 giây).
  strikes: number
  idleFrom: number
  rollCallAt: number | null
  absences: number
}

// Hộp câu hỏi gốc đang mở.
export type AskOpen = { id: string; openedAt: number; label: string; handled: boolean }

export type UsageInfo = {
  model: string
  context: number | null
  five: { percentUsed: number; resetsAt?: string } | null
  week: { percentUsed: number; resetsAt?: string } | null
}

// Phần v0.6 mod cần giữa các lần vẽ (đọc lại state.json mới cập nhật).
export type LiveState = { activity: LessonActivity | null; challenge: LessonChallenge | null; giftBox: boolean }
// Kiểu tương tác đang theo dõi: thời điểm bắt đầu tính theo giờ buổi học (không tính lúc nghỉ).
export type ActivityTrack = { key: string; fromEl: number }
// Hộp quà: chưa mở · đang mở (hình nắp bật) · đã mở (chờ giáo viên tắt).
export type GiftPhase = 'closed' | 'opening' | 'opened'

// Bục giảng: bình thường · form giao việc 4 ý · chọn lý do xin phép · ô "Kể cô nghe".
export type BandMode = 'normal' | 'form' | 'xin-phep' | 'gio-tay'

// Kiểu cũ (v0.4) còn được hooks/art.ts dùng cho các hình cũ.
export type CharId = 'la' | 'nang' | 'hop'
export type Moment = 'read' | 'turn' | 'hint' | 'catch' | 'done'
export type PodiumMode = 'wait' | 'turn' | 'work' | 'hint' | 'done'

declare module 'claude-code' {
  interface PluginState {
    'lop-hoc': {
      rev: number
      isClassroom: boolean
      entered: boolean
      teacherPick: TeacherKindId
      minutesPick: LessonMinutes
      mode: BandMode
      usage: UsageInfo | null
      effort: string
      lesson: Lesson | null
      working: boolean
      turnId: string
      ask: AskOpen | null
      now: number
      oneTouchUsed: string
      live: LiveState
      activityTrack: ActivityTrack | null
      badges: BadgeEntry[]
      cheer: boolean
      gift: GiftPhase
    }
  }
}
