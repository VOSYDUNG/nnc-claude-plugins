import { test, expect } from 'claude-code/testing'
import {
  TEACHERS,
  badgeShelfSvg,
  badgeSvg,
  bottomBarSvg,
  challengeRingSvg,
  giftBoxSvg,
  sanitizeSvg,
  segmentClockSvg,
  starRowSvg,
  svgBox,
  teacherAvatarSvg,
  teacherPodiumSvg,
  usageTimelineSvg,
  vientianeHHMM,
  weekResetSvg,
  type Drive,
  type Emotion,
  type BadgeRef,
  type TeacherPresence,
} from '../hooks/art'

const EMOTIONS: Emotion[] = ['hi', 'no', 'ai', 'o', 'bi', 'lac', 'giang', 'nghe']
const PRESENCES: TeacherPresence[] = ['present', 'wait', 'away']
const DRIVES: Drive[] = ['D1', 'D2', 'D3', 'ket-noi']
const RESET = '2026-10-15T07:20:00Z' // 14:20 giờ Viêng Chăn
const NOW = '2026-10-15T04:05:00Z' // 11:05 giờ Viêng Chăn, thứ Năm

function wellFormed(s: string) {
  expect(s.startsWith('<svg')).toBe(true)
  expect(s.endsWith('</svg>')).toBe(true)
  expect(s.length).toBeLessThan(131072)
  expect(s.includes('<script')).toBe(false)
  expect(s.includes('href=')).toBe(false)
}

test('bục giảng: mọi giảng viên × cảm xúc × có mặt', async () => {
  for (const t of TEACHERS)
    for (const e of EMOTIONS)
      for (const p of PRESENCES) {
        const s = teacherPodiumSvg(t.id, e, p)
        wellFormed(s)
        expect(s).toContain('Lớp học NNC')
        if (p === 'away') {
          expect(s).toContain('Lớp tạm nghỉ')
          expect(s.includes('<animate')).toBe(false)
        } else expect(s.includes('<animate')).toBe(true)
      }
})

test('bục giảng: thầy đeo kính, cô có búi tóc, hai hình khác nhau', async () => {
  const thay = teacherPodiumSvg('thay', 'hi', 'present')
  const co = teacherPodiumSvg('co', 'hi', 'present')
  expect(thay).not.toBe(co)
  expect(thay).toContain('#2B2420')
  expect(co).toContain('#3A2A22')
})

test('mỗi cảm xúc cho một hình riêng', async () => {
  for (const t of TEACHERS) {
    const seen = new Set(EMOTIONS.map(e => teacherPodiumSvg(t.id, e, 'present')))
    expect(seen.size).toBe(EMOTIONS.length)
  }
})

test('avatar tĩnh: không có SMIL', async () => {
  for (const t of TEACHERS) {
    const s = teacherAvatarSvg(t.id)
    wellFormed(s)
    expect(s.includes('<animate')).toBe(false)
  }
})

test('giờ Viêng Chăn tính tay (UTC+7)', async () => {
  expect(vientianeHHMM(RESET)).toBe('14:20')
  expect(vientianeHHMM('2026-10-15T14:20:00+07:00')).toBe('14:20')
  expect(vientianeHHMM('2026-10-15T20:30:00Z')).toBe('03:30')
  expect(vientianeHHMM('không phải giờ')).toBe('')
})

test('thẻ 5 giờ: đầu phiên, bây giờ, reset theo UTC+7', async () => {
  const s = usageTimelineSvg({ percentUsed: 42, resetsAt: RESET, now: NOW })
  wellFormed(s)
  expect(s).toContain('reset 14:20')
  expect(s).toContain('đầu phiên 09:20')
  expect(s).toContain('bây giờ 11:05')
  expect(s).toContain('42%')
  const missing = usageTimelineSvg({ percentUsed: 10, now: NOW })
  wellFormed(missing)
  expect(missing).toContain('Chưa đọc được giờ reset')
  expect(missing.includes('reset 1')).toBe(false)
  wellFormed(usageTimelineSvg({ percentUsed: Number.NaN, resetsAt: 'rác', now: 'rác' }))
  wellFormed(usageTimelineSvg({ percentUsed: 250, resetsAt: RESET, now: '2026-10-16T00:00:00Z' }))
})

test('thẻ tuần: ô reset vàng, giờ UTC+7', async () => {
  // thứ Ba 13/10 (giờ Viêng Chăn): ô hôm nay viền trắng, ô thứ Năm (ngày reset) tô vàng
  const s = weekResetSvg({ percentUsed: 37, resetsAt: RESET, now: '2026-10-13T04:05:00Z' })
  wellFormed(s)
  expect(s).toContain('reset 14:20')
  expect(s).toContain('37%')
  expect(s).toContain('hôm nay')
  for (const d of ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']) expect(s).toContain(`>${d}<`)
  // hôm nay trùng ngày reset: vẫn ghi giờ reset, có viền hôm nay
  const same = weekResetSvg({ percentUsed: 37, resetsAt: RESET, now: NOW })
  expect(same).toContain('reset 14:20')
  expect(same).toContain('stroke="#FFFFFF" stroke-width="2"')
  const missing = weekResetSvg({ percentUsed: 37, now: NOW })
  wellFormed(missing)
  expect(missing).toContain('Chưa đọc được giờ reset')
  expect(missing.includes('#FFEA00"/>')).toBe(false)
})

test('đồng hồ phần học: mọi động lực, phút còn lại, nhấp nháy 2 phút cuối', async () => {
  for (const drive of DRIVES) {
    const s = segmentClockSvg({ elapsedMs: 5 * 60000, totalMs: 15 * 60000, drive })
    wellFormed(s)
    expect(s).toContain('>10<')
    expect(s.includes('<animate')).toBe(false)
  }
  const last = segmentClockSvg({ elapsedMs: 14 * 60000, totalMs: 15 * 60000, drive: 'D2' })
  expect(last).toContain('<animate')
  expect(last).toContain('>1<')
  wellFormed(segmentClockSvg({ elapsedMs: 99 * 60000, totalMs: 15 * 60000, drive: 'D3' }))
  wellFormed(segmentClockSvg({ elapsedMs: 0, totalMs: 0, drive: 'D1' }))
})

// ── v0.6 ──
const BADGES: BadgeRef[] = [
  { id: 'giao-viec-dau-tien', label: 'Người giao việc đầu tiên' },
  { id: 'mat-tinh', label: 'Mắt tinh' },
  { id: 'thuoc-9-the', label: 'Thuộc 9 thẻ' },
  { id: 'tu-kiem-co-tam', label: 'Tự kiểm có tâm' },
  { id: 'nguoi-day-lai', label: 'Người dạy lại' },
  { id: 'dong-goi-skill-dau-tien', label: 'Đóng gói Skill đầu tiên' },
  { id: 'ban-la-sep', label: 'Bạn là sếp' },
  { id: 'nhanh-tay', label: 'Nhanh tay' },
]
const ids = (s: string) => [...s.matchAll(/\sid="([^"]*)"/g)].map(m => m[1])

test('hàng sao: 0 là một sao viền mờ, 5 sao tối đa, quá 5 thì "+k"', async () => {
  const zero = starRowSvg(0)
  wellFormed(zero)
  expect(zero).toContain('fill="none"')
  expect(zero.includes('<animate')).toBe(false)
  const three = starRowSvg(3)
  wellFormed(three)
  expect(three.match(/fill="#FFEA00" stroke=/g)?.length).toBe(3)
  expect(three).toContain('<animateTransform')
  const seven = starRowSvg(7)
  wellFormed(seven)
  expect(seven.match(/fill="#FFEA00" stroke=/g)?.length).toBe(5)
  expect(seven).toContain('>+2<')
  expect(starRowSvg(5).includes('>+')).toBe(false)
  for (const bad of [-3, Number.NaN, Number.POSITIVE_INFINITY]) {
    const s = starRowSvg(bad)
    wellFormed(s)
    expect(s).toContain('<title>0 sao</title>')
  }
})

test('huy hiệu: mỗi id đã biết một hình riêng, id lạ vẫn có biểu tượng chung', async () => {
  const seen = new Set<string>()
  for (const b of BADGES) {
    const s = badgeSvg(b.id, b.label)
    wellFormed(s)
    expect(s).toContain(`<title>${b.label}</title>`)
    expect(s).toContain('#FFEA00') // vòng vàng chung
    expect(ids(s).length).toBe(0)
    seen.add(s.replace(/<title>.*?<\/title>/, ''))
  }
  const unknown = badgeSvg('chua-co-trong-kho', 'Huy hiệu lạ')
  wellFormed(unknown)
  expect(unknown).toContain('<title>Huy hiệu lạ</title>')
  seen.add(unknown.replace(/<title>.*?<\/title>/, ''))
  expect(seen.size).toBe(BADGES.length + 1)
  // màu theo động lực
  expect(badgeSvg('giao-viec-dau-tien', 'x')).toContain('#F5A524')
  expect(badgeSvg('thuoc-9-the', 'x')).toContain('#4A90E2')
  expect(badgeSvg('mat-tinh', 'x')).toContain('#3CC85A')
})

test('huy hiệu: tên được thoát ký tự XML', async () => {
  const s = badgeSvg('mat-tinh', `A & B <i>"x"</i> 'y'`)
  wellFormed(s)
  expect(s).toContain('<title>A &amp; B &lt;i&gt;&quot;x&quot;&lt;/i&gt; &apos;y&apos;</title>')
  expect(s.includes('<i>')).toBe(false)
  const shelf = badgeShelfSvg([{ id: 'x', label: '<b>&' }])
  expect(shelf).toContain('&lt;b&gt;&amp;')
  expect(shelf.includes('<b>')).toBe(false)
})

test('kệ huy hiệu: rỗng có lời nhắc, tối đa 4 cái + "+n", không trùng id', async () => {
  const empty = badgeShelfSvg([])
  wellFormed(empty)
  expect(empty).toContain('Chưa có huy hiệu — làm việc thật để nhận!')
  const two = badgeShelfSvg(BADGES.slice(0, 2))
  wellFormed(two)
  expect(two.match(/<title>/g)?.length).toBe(2)
  expect(two.includes('>+')).toBe(false)
  const all = badgeShelfSvg([...BADGES, { id: 'la', label: 'Lạ' }])
  wellFormed(all)
  expect(all.match(/<title>/g)?.length).toBe(4)
  expect(all).toContain('>+5<')
  expect(all).toContain('<title>Lạ</title>') // mới nhất được hiện
  expect(all.includes('<title>Mắt tinh</title>')).toBe(false) // cũ hơn thì gộp vào "+n"
  const idList = ids(all)
  expect(new Set(idList).size).toBe(idList.length)
})

test('hộp quà: đóng lắc nhẹ, mở có nắp bật và lấp lánh', async () => {
  const closed = giftBoxSvg(false)
  const opened = giftBoxSvg(true)
  wellFormed(closed)
  wellFormed(opened)
  expect(closed).not.toBe(opened)
  expect(closed).toContain('type="rotate"')
  expect(closed).toContain('#FFEA00')
  expect(closed).toContain('#008816')
  expect(opened).toContain('Hộp quà đã mở')
  expect(opened.match(/attributeName="opacity"/g)?.length).toBeGreaterThan(2)
})

test('vòng thử thách: đầy, 5 giây cuối đỏ cam và nhịp, 0 là "Hết giờ"', async () => {
  const full = challengeRingSvg({ remainingMs: 60000, totalMs: 60000 })
  wellFormed(full)
  expect(full).toContain('>60<')
  expect(full).toContain('#F5A524')
  expect(full.includes('#FF6B3D')).toBe(false)
  expect(full.includes('<animate')).toBe(false)
  const five = challengeRingSvg({ remainingMs: 4200, totalMs: 60000 })
  wellFormed(five)
  expect(five).toContain('>5<') // làm tròn lên
  expect(five).toContain('#FF6B3D')
  expect(five).toContain('<animate')
  expect(challengeRingSvg({ remainingMs: 11000, totalMs: 60000 }).includes('#FF6B3D')).toBe(false)
  for (const r of [0, -2500, Number.NaN]) {
    const s = challengeRingSvg({ remainingMs: r, totalMs: 60000 })
    wellFormed(s)
    expect(s).toContain('Hết giờ')
    expect(s.includes('>-')).toBe(false)
    expect(s.includes('<animate')).toBe(false)
  }
  wellFormed(challengeRingSvg({ remainingMs: 5000, totalMs: 0 }))
  wellFormed(challengeRingSvg({ remainingMs: 999000, totalMs: 60000 }))
})

test('thanh dưới ô nhập: trái là chế độ, phải là model · effort · vòng tròn; vùng được chỉ tô vàng có mũi tên', async () => {
  const none = bottomBarSvg({ mode: 'Bypass permissions', model: 'Opus 5.5', effort: 'Medium', percent: 34 })
  wellFormed(none)
  expect(none).toContain('Bypass permissions')
  expect(none).toContain('Opus 5.5')
  expect(none).toContain('Medium')
  expect(none.includes('#FFEA00')).toBe(false)
  expect(/This computer|thư mục/i.test(none)).toBe(false)
  for (const point of ['mode', 'model', 'effort', 'context', 'usage5', 'usageWeek']) {
    const s = bottomBarSvg({ mode: 'Auto', model: 'Opus 5.5', effort: 'High', percent: 80, point })
    wellFormed(s)
    expect(s).toContain('#FFEA00')
    expect(s).toContain('<path d="M') // mũi tên ▼
  }
  // Vùng tô nằm đúng chỗ: effort ở bên phải nhãn chế độ.
  const x = (s: string) => Number(/<rect x="([0-9.]+)" y="17"/.exec(s)?.[1])
  const mode = x(bottomBarSvg({ mode: 'Auto', model: 'Opus 5.5', effort: 'High', point: 'mode' }))
  const effort = x(bottomBarSvg({ mode: 'Auto', model: 'Opus 5.5', effort: 'High', point: 'effort' }))
  const circle = x(bottomBarSvg({ mode: 'Auto', model: 'Opus 5.5', effort: 'High', point: 'usage5' }))
  expect(mode).toBeLessThan(effort)
  expect(effort).toBeLessThan(circle)
  // Chữ lạ được thoát ký tự; thiếu số liệu vẫn vẽ được.
  const odd = bottomBarSvg({ mode: '<b>&"x"</b>', point: 'mode', percent: Number.NaN })
  wellFormed(odd)
  expect(odd.includes('<b>')).toBe(false)
  wellFormed(bottomBarSvg({}))
})

test('lọc SVG của bảng: bỏ script, foreignObject, thuộc tính on…, href ngoài; quá 16 KB hay không phải SVG thì bỏ', async () => {
  const ok = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60" width="120" height="60"><rect x="1" y="1" width="50" height="20" fill="#008816"/><text x="5" y="40">Xin chào</text><use href="#a"/></svg>'
  expect(sanitizeSvg(ok)).toBe(ok)
  const dirty = sanitizeSvg('<svg viewBox="0 0 9 9" onload="a()"><SCRIPT type="x">alert(1)</SCRIPT><foreignObject width="1"><p>x</p></foreignObject><image href="http://evil.example/p.png" width="3"/><a xlink:href="javascript:alert(1)"><rect onClick="b()" width="1" height="1" style="fill:url(http://x)"/></a><set attributeName="href" to="x"/><circle r="2"/></svg>') ?? ''
  expect(dirty.startsWith('<svg')).toBe(true)
  expect(dirty.endsWith('</svg>')).toBe(true)
  expect(/script|foreignobject|onload|onclick|evil|javascript|<set|url\(/i.test(dirty)).toBe(false)
  expect(dirty).toContain('<circle r="2"/>')
  expect(dirty).toContain('<rect')
  // Dựng chuỗi bằng cách ghép thẻ: sau khi lọc vẫn phải sạch hoặc bị bỏ.
  const nested = sanitizeSvg('<svg><scr<script></script>ipt>alert(1)</scr<script></script>ipt><rect/></svg>')
  expect(nested === null || !/<\s*\/?\s*script/i.test(nested)).toBe(true)
  for (const bad of [null, undefined, 5, '', '<div>x</div>', '<svg><rect/>', '<!DOCTYPE svg><svg></svg>', '<svg><![CDATA[x]]></svg>']) expect(sanitizeSvg(bad)).toBeNull()
  const big = `<svg viewBox="0 0 1 1">${'<rect width="1" height="1"/>'.repeat(700)}</svg>`
  expect(big.length).toBeGreaterThan(16 * 1024)
  expect(sanitizeSvg(big)).toBeNull()
  // Cỡ hiển thị: tỉ lệ giữ nguyên, không vượt khung.
  expect(svgBox('<svg viewBox="0 0 400 200">', 200)).toEqual({ width: 200, height: 100 })
  expect(svgBox('<svg width="100" height="50">', 200)).toEqual({ width: 100, height: 50 })
  expect(svgBox('<svg>', 200, 150)).toEqual({ width: 200, height: 150 })
})
