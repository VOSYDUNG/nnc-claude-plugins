// Lớp học NNC v0.10 — ảnh chụp màn hình có đánh dấu trên bảng (board.shot, thiết kế docs/oser-r2/LOP-HOC-V10-THIET-KE.md §2).
// Chỉ có hàm thuần: kiểm đường dẫn, giải base64, đọc cỡ ảnh từ đầu tệp (JPEG SOF / PNG IHDR), dựng Svg.
// SVG này CHỈ do mod dựng (một thẻ <image> data:) — không đi qua sanitizeSvg (sẽ bị cắt mất href data:);
// SVG do giáo viên ghi (board.svg) vẫn luôn được lọc ở boardOf.

export const SHOT_DIR = '.lop-hoc/'
export const SHOT_MAX_BYTES = 96 * 1024
export const SHOT_SVG_MAX_CHARS = 131_072
// Hộp mặc định khi biết là ảnh nhưng không đọc được cỡ.
export const SHOT_FALLBACK = { w: 960, h: 540 } as const

// Đường dẫn do giáo viên ghi: tương đối, nằm trong `.lop-hoc/`, đuôi .jpg/.jpeg/.png, không có `..`. Sai thì null (bỏ qua).
export function shotPathOf(v: unknown): string | null {
  if (typeof v !== 'string') return null
  // eslint-disable-next-line no-control-regex
  if (/[\u0000-\u001f]/.test(v)) return null
  let p = v.trim().split('\\').join('/')
  while (p.startsWith('./')) p = p.slice(2)
  if (!p.startsWith(SHOT_DIR) || p.length > 200) return null
  if (p.includes(':')) return null
  const segs = p.split('/')
  if (segs.some(s => s === '' || s === '.' || s === '..')) return null
  if (segs.length < 2 || !/\.(jpe?g|png)$/i.test(p)) return null
  return p
}

const B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
const B64_RE = /^[A-Za-z0-9+/]+={0,2}$/

// Số byte của chuỗi base64 chuẩn (có đệm =).
export function base64Bytes(b64: string): number {
  const pad = b64.endsWith('==') ? 2 : b64.endsWith('=') ? 1 : 0
  return Math.max(0, Math.floor((b64.length * 3) / 4) - pad)
}

export function b64ToBytes(b64: string): Uint8Array {
  const out = new Uint8Array(base64Bytes(b64))
  let acc = 0
  let bits = 0
  let n = 0
  for (let i = 0; i < b64.length && n < out.length; i++) {
    const v = B64.indexOf(b64.charAt(i))
    if (v < 0) continue
    acc = (acc << 6) | v
    bits += 6
    if (bits >= 8) {
      bits -= 8
      out[n++] = (acc >> bits) & 0xff
    }
  }
  return out
}

export type ImageInfo = { mime: 'image/jpeg' | 'image/png'; w: number | null; h: number | null }

const goodDim = (v: number) => Number.isInteger(v) && v > 0 && v <= 30_000

// Nhận dạng theo chữ ký đầu tệp (không tin đuôi tệp) và đọc cỡ: JPEG lấy từ khối SOFn, PNG từ IHDR.
// Không phải JPEG/PNG thì null; đúng loại nhưng cụt/hỏng phần đầu thì w, h là null.
export function sniffImage(b: Uint8Array): ImageInfo | null {
  const at = (i: number) => b[i] ?? 0
  const u16 = (i: number) => (at(i) << 8) | at(i + 1)
  if (b.length >= 8 && at(0) === 0x89 && at(1) === 0x50 && at(2) === 0x4e && at(3) === 0x47 && at(4) === 0x0d && at(5) === 0x0a && at(6) === 0x1a && at(7) === 0x0a) {
    const isIhdr = b.length >= 24 && at(12) === 0x49 && at(13) === 0x48 && at(14) === 0x44 && at(15) === 0x52
    const w = isIhdr ? u16(16) * 65536 + u16(18) : 0
    const h = isIhdr ? u16(20) * 65536 + u16(22) : 0
    return { mime: 'image/png', w: goodDim(w) ? w : null, h: goodDim(h) ? h : null }
  }
  if (b.length >= 3 && at(0) === 0xff && at(1) === 0xd8 && at(2) === 0xff) {
    let i = 2
    while (i + 3 < b.length) {
      if (at(i) !== 0xff) {
        i++
        continue
      }
      const m = at(i + 1)
      if (m === 0xff) {
        i++
        continue
      }
      // Không có độ dài: SOI, TEM, RSTn, hoặc 0x00 (byte đệm).
      if (m === 0x00 || m === 0x01 || m === 0xd8 || (m >= 0xd0 && m <= 0xd7)) {
        i += 2
        continue
      }
      // EOI hoặc SOS: tới dữ liệu ảnh mà chưa thấy SOF.
      if (m === 0xd9 || m === 0xda) break
      const len = u16(i + 2)
      if (len < 2) break
      if (m >= 0xc0 && m <= 0xcf && m !== 0xc4 && m !== 0xc8 && m !== 0xcc) {
        if (i + 9 > b.length) break
        const h = u16(i + 5)
        const w = u16(i + 7)
        return { mime: 'image/jpeg', w: goodDim(w) ? w : null, h: goodDim(h) ? h : null }
      }
      i += 2 + len
    }
    return { mime: 'image/jpeg', w: null, h: null }
  }
  return null
}

// Svg một thẻ <image data:> đúng cỡ ảnh. Thêm xlink:href (cho bộ vẽ cũ) khi vẫn vừa giới hạn 131 072 ký tự;
// vẫn vượt thì chỉ href; vẫn vượt nữa (hoặc base64 sai) thì null = không vẽ.
export function shotSvg(b64: string, mime: ImageInfo['mime'], w: number, h: number): string | null {
  if (!B64_RE.test(b64) || !goodDim(w) || !goodDim(h)) return null
  const uri = `data:${mime};base64,${b64}`
  const head = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}">`
  const img = (attrs: string) => `${head}<image ${attrs} width="${w}" height="${h}" preserveAspectRatio="xMidYMid meet"/></svg>`
  const dual = img(`href="${uri}" xlink:href="${uri}"`)
  if (dual.length <= SHOT_SVG_MAX_CHARS) return dual
  const single = img(`href="${uri}"`)
  return single.length <= SHOT_SVG_MAX_CHARS ? single : null
}

export type ShotDrawn = { svg: string; w: number; h: number }

// Từ base64 của tệp đến hình sẽ vẽ (hoặc null: quá lớn, không phải JPEG/PNG, quá giới hạn Svg).
export function shotFromBase64(b64: unknown): ShotDrawn | null {
  if (typeof b64 !== 'string' || !b64) return null
  if (base64Bytes(b64) > SHOT_MAX_BYTES) return null
  const info = sniffImage(b64ToBytes(b64))
  if (!info) return null
  const known = info.w != null && info.h != null
  const w = known ? info.w! : SHOT_FALLBACK.w
  const h = known ? info.h! : SHOT_FALLBACK.h
  const svg = shotSvg(b64, info.mime, w, h)
  return svg ? { svg, w, h } : null
}
