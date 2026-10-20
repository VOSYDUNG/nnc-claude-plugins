import { test, expect } from 'claude-code/testing'
import { SHOT_FALLBACK, SHOT_MAX_BYTES, SHOT_SVG_MAX_CHARS, b64ToBytes, base64Bytes, shotFromBase64, shotPathOf, shotSvg, sniffImage } from '../hooks/shot'
import { jpegBytes, pngBytes, toB64 } from './shot-fixtures'

// Lớp học NNC v0.10 — hợp đồng board.shot (docs/oser-r2/LOP-HOC-V10-THIET-KE.md §2): hàm thuần.

test('shot: đường dẫn hợp lệ phải nằm trong .lop-hoc/, đuôi .jpg/.jpeg/.png, không có ..', async () => {
  expect(shotPathOf('.lop-hoc/chi-tay.jpg')).toBe('.lop-hoc/chi-tay.jpg')
  expect(shotPathOf('.lop-hoc/Man-Hinh.PNG')).toBe('.lop-hoc/Man-Hinh.PNG')
  expect(shotPathOf('.lop-hoc\\chi-tay.jpeg')).toBe('.lop-hoc/chi-tay.jpeg')
  expect(shotPathOf('./.lop-hoc/a/b.png')).toBe('.lop-hoc/a/b.png')
  const bad: unknown[] = [
    'chi-tay.jpg',
    'assets/chi-tay.jpg',
    '../.lop-hoc/chi-tay.jpg',
    '.lop-hoc/../chi-tay.jpg',
    '.lop-hoc/a/../../x.jpg',
    '.lop-hoc/..\\x.jpg',
    '/.lop-hoc/chi-tay.jpg',
    'C:/lop/.lop-hoc/chi-tay.jpg',
    'D:\\lop\\.lop-hoc\\chi-tay.jpg',
    '.lop-hoc/state.json',
    '.lop-hoc/chi-tay.gif',
    '.lop-hoc/chi-tay.jpg.exe',
    '.lop-hoc/chi-tay',
    '.lop-hoc/',
    '.lop-hoc',
    '.lop-hoc//x.jpg',
    '.lop-hoc/x' + String.fromCharCode(0) + '.jpg',
    '.lop-hoc-khac/x.jpg',
    'https://x.example/.lop-hoc/a.jpg',
    '',
    7,
    null,
    { a: 1 },
  ]
  for (const b of bad) expect(shotPathOf(b)).toBeNull()
})

test('shot: giải base64 và đọc cỡ ảnh từ đầu tệp (JPEG SOF, PNG IHDR); rác thì không phải ảnh', async () => {
  const bytes = Uint8Array.from([0, 1, 2, 250, 251, 252, 253, 254, 255, 9, 8])
  for (let n = 0; n <= bytes.length; n++) {
    const part = bytes.subarray(0, n)
    expect(Array.from(b64ToBytes(toB64(part)))).toEqual(Array.from(part))
    expect(base64Bytes(toB64(part))).toBe(n)
  }
  expect(sniffImage(jpegBytes(960, 540))).toEqual({ mime: 'image/jpeg', w: 960, h: 540 })
  // EXIF/ICC dài trước SOF; SOF2 (progressive); ảnh dọc.
  expect(sniffImage(jpegBytes(1280, 720, { pad: 20_000 }))).toEqual({ mime: 'image/jpeg', w: 1280, h: 720 })
  expect(sniffImage(jpegBytes(640, 1136, { sof: 0xc2 }))).toEqual({ mime: 'image/jpeg', w: 640, h: 1136 })
  expect(sniffImage(pngBytes(1920, 1080))).toEqual({ mime: 'image/png', w: 1920, h: 1080 })
  // Cụt: đúng loại nhưng không đọc được cỡ.
  expect(sniffImage(jpegBytes(960, 540).subarray(0, 24))).toEqual({ mime: 'image/jpeg', w: null, h: null })
  expect(sniffImage(Uint8Array.from([0xff, 0xd8, 0xff, 0xe0]))).toEqual({ mime: 'image/jpeg', w: null, h: null })
  expect(sniffImage(pngBytes(10, 10).subarray(0, 12))).toEqual({ mime: 'image/png', w: null, h: null })
  expect(sniffImage(pngBytes(0, 10))).toEqual({ mime: 'image/png', w: null, h: 10 })
  // Rác: không phải JPEG/PNG.
  expect(sniffImage(new Uint8Array(0))).toBeNull()
  expect(sniffImage(Uint8Array.from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))).toBeNull()
  expect(sniffImage(new TextEncoder().encode('<svg xmlns="http://www.w3.org/2000/svg"/>'))).toBeNull()
  expect(sniffImage(new TextEncoder().encode('GIF89a......'))).toBeNull()
})

test('shot: Svg chỉ có một thẻ <image data:>, đúng cỡ ảnh; mime theo chữ ký tệp; cỡ lạ → hộp 960×540', async () => {
  const j = shotFromBase64(toB64(jpegBytes(960, 540, { total: 4000 })))
  expect(j).not.toBeNull()
  expect(j?.w).toBe(960)
  expect(j?.h).toBe(540)
  const src = j!.svg
  expect(src.startsWith('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 960 540" width="960" height="540">')).toBe(true)
  expect(src.match(/<image\b/g)).toHaveLength(1)
  expect(src.match(/<[a-z]+\b/gi)).toEqual(['<svg', '<image'])
  expect(src).toContain('href="data:image/jpeg;base64,')
  expect(src).toContain('xlink:href="data:image/jpeg;base64,')
  expect(src).toContain('width="960" height="540"')
  expect(src.length).toBeLessThanOrEqual(SHOT_SVG_MAX_CHARS)
  const p = shotFromBase64(toB64(pngBytes(800, 450, 3000)))
  expect(p?.svg).toContain('href="data:image/png;base64,')
  expect(p?.svg).toContain('viewBox="0 0 800 450"')
  // JPEG có chữ ký nhưng hỏng phần đầu: hộp mặc định.
  const broken = shotFromBase64(toB64(jpegBytes(960, 540).subarray(0, 24)))
  expect(broken).toMatchObject({ w: SHOT_FALLBACK.w, h: SHOT_FALLBACK.h })
  expect(broken?.svg).toContain('viewBox="0 0 960 540"')
  // Không phải JPEG/PNG, rỗng, không phải base64, không phải chữ: không vẽ.
  expect(shotFromBase64(toB64(new TextEncoder().encode('khong phai anh, chi la chu')))).toBeNull()
  expect(shotFromBase64('')).toBeNull()
  expect(shotFromBase64('****')).toBeNull()
  expect(shotFromBase64(undefined)).toBeNull()
  expect(shotFromBase64(42)).toBeNull()
})

test('shot: giới hạn 96 KB cho tệp và 131 072 ký tự cho Svg', async () => {
  // Quá 96 KB: không vẽ. Đúng 96 KB qua bước kiểm tệp nhưng Svg vượt 131 072 ký tự nên cũng không vẽ;
  // ảnh ≤ 90 KB (đích của danh-dau.ps1) vẽ được.
  expect(shotFromBase64(toB64(jpegBytes(960, 540, { total: SHOT_MAX_BYTES + 1 })))).toBeNull()
  expect(shotFromBase64(toB64(jpegBytes(960, 540, { total: SHOT_MAX_BYTES })))).toBeNull()
  const ninety = shotFromBase64(toB64(jpegBytes(960, 540, { total: 90 * 1024 })))
  expect(ninety).not.toBeNull()
  expect(ninety!.svg.length).toBeLessThanOrEqual(SHOT_SVG_MAX_CHARS)
  // Ảnh lớn (> 48 KB) bỏ xlink:href để Svg còn vừa 131 072 ký tự; ảnh nhỏ giữ cả hai.
  expect(ninety!.svg).not.toContain('xlink:href=')
  expect(ninety!.svg).toContain(' href="data:image/jpeg;base64,')
  expect(shotFromBase64(toB64(jpegBytes(960, 540, { total: 20_000 })))!.svg).toContain('xlink:href=')
  // shotSvg tự giữ giới hạn: base64 dài quá, cỡ 0 hoặc chuỗi không phải base64 thì null.
  expect(shotSvg('A'.repeat(SHOT_SVG_MAX_CHARS), 'image/png', 10, 10)).toBeNull()
  expect(shotSvg('AAAA', 'image/png', 0, 10)).toBeNull()
  expect(shotSvg('AA"onload=', 'image/png', 10, 10)).toBeNull()
})
