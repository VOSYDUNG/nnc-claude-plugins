// Ảnh giả cho bộ test board.shot: chỉ có phần đầu tệp đúng chuẩn (JPEG có khối SOF, PNG có IHDR) và phần thân đệm.
export function toB64(bytes: Uint8Array): string {
  let bin = ''
  for (let i = 0; i < bytes.length; i += 4096) bin += String.fromCharCode(...bytes.subarray(i, i + 4096))
  return btoa(bin)
}

// JPEG: SOI · APP0 · (APP1 đệm `pad` byte, như EXIF dài) · SOF0 w×h · SOS · thân đệm · EOI. Tổng ≥ `total` byte.
export function jpegBytes(w: number, h: number, opts: { pad?: number; total?: number; sof?: number } = {}): Uint8Array {
  const out: number[] = [0xff, 0xd8]
  out.push(0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00)
  if (opts.pad) {
    const len = opts.pad + 2
    out.push(0xff, 0xe1, (len >> 8) & 0xff, len & 0xff)
    for (let i = 0; i < opts.pad; i++) out.push(0x45)
  }
  out.push(0xff, opts.sof ?? 0xc0, 0x00, 0x11, 0x08, (h >> 8) & 0xff, h & 0xff, (w >> 8) & 0xff, w & 0xff, 0x03, 0x01, 0x22, 0x00, 0x02, 0x11, 0x01, 0x03, 0x11, 0x01)
  out.push(0xff, 0xda, 0x00, 0x0c, 0x03, 0x01, 0x00, 0x02, 0x11, 0x03, 0x11, 0x00, 0x3f, 0x00)
  const body = Math.max(0, (opts.total ?? 0) - out.length - 2)
  for (let i = 0; i < body; i++) out.push(0x11 + (i % 7))
  out.push(0xff, 0xd9)
  return Uint8Array.from(out)
}

export function pngBytes(w: number, h: number, total = 0): Uint8Array {
  const u32 = (v: number) => [(v >>> 24) & 0xff, (v >>> 16) & 0xff, (v >>> 8) & 0xff, v & 0xff]
  const out: number[] = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, ...u32(13), 0x49, 0x48, 0x44, 0x52, ...u32(w), ...u32(h), 8, 2, 0, 0, 0, 0, 0, 0, 0]
  while (out.length < total) out.push(0x22 + (out.length % 5))
  return Uint8Array.from(out)
}
