---
name: ai-oser
description: NNC OSER — control plane tái dùng cho một repo Claude Code. Cài (install), cập nhật (update), chuyển từ bố cục NNC-AI-OSer 1.0 (migrate), và khám drift (doctor) cho cấu hình hiệu lực của dự án — phase/mode, authority, capability, model class, provenance, Firebase target. Dùng khi người dùng nói "init dự án", "dựng đội agent", "xưởng AI", "NNC OSER", "doctor", "kiểm control plane", "đổi mode", "migrate OSER", "đo quota", hoặc khi CLAUDE.md/TRANG-THAI/agent của repo có dấu hiệu trỏ sai (branch chết, phase cũ, model cũ).
---

# NNC OSER 2 (`/nnc:ai-oser`)

**Plugin sở hữu framework. Repo sở hữu cấu hình hiệu lực.** Mọi sự thật của dự án nằm trong
`.claude/oser/project.json` (PROJECT-OWNED). OSER chỉ *sinh* các phần có dấu `NNC-OSER:GENERATED` /
`NNC-OSER:BEGIN…END`, và ghi provenance vào `.claude/oser/lock.json`. Chi tiết: `references/`.

## Mô hình tổ chức

**PHASE/MODE + CAPABILITY + ASSIGNMENT + MODEL CLASS** — không phải "hồ sơ theo tên model".

| Mode | Trạng thái trong 2.0 | Nghĩa |
|---|---|---|
| `setup` | **active** | Founder + Strategy Session + ROOT (investigator). **Không subagent, không build crew, audit TẮT.** OSER ép bằng `permissions.deny` (Agent · Task · Workflow). |
| `build` | contract-only | Plugin **không** định sẵn đội build. Dự án khai `assignments` sau khi kiến trúc kỹ thuật chốt. |
| `operate` | contract-only | Như trên, cho vận hành. |

Capability **đã khai ≠ đang chạy**: `configured` nghĩa là có định nghĩa, không được gọi trong mode này.

## ROOT model và Fable

- **ROOT = `inherit`.** Model phiên chính do client chọn (bảng chọn model của Claude Desktop, cờ CLI).
  Đo trên dự án pilot: `settings.json` ghim `claude-opus-5` trong khi phiên thật chạy `claude-fable-5-1`
  (13/09) và `claude-opus-5-5` (25/09) — file không điều khiển ROOT ở Desktop. OSER không ghim ROOT,
  và `oser doctor` báo **EXPECTED / CONFIGURED / OBSERVED** (OBSERVED đọc từ transcript thật).
- **Fable = capability `audit`**, model class `frontier-audit`, chỉ bật tại audit gate tường minh; mode
  `setup` luôn TẮT. Không có "hồ sơ ROOT Fable".
- Model class dùng alias họ model (`opus`/`sonnet`/`haiku`) để không mục theo thế hệ; id cứng nào cũ
  hơn thế hệ đã quan sát trên máy → doctor cảnh báo.

## Gọi CLI

Plugin đặt `bin/` lên PATH của phiên Claude Code khi đã cài: `oser <lệnh>`. Chưa cài / ngoài phiên:
`python <thư-mục-skill>/../../oser/oser.py <lệnh>`.

| Lệnh | Việc |
|---|---|
| `oser doctor [--manifest F]` | khám drift; exit 2 = critical, 1 = warning, 0 = sạch |
| `oser install --name … --authority-repo … --authority-entry … [--authority-hint ../repo] [--baseline sha]` | dự án mới, mode `setup` |
| `oser migrate [--dry-run]` | dự án NNC-AI-OSer 1.0 → 2.x (cần `project.json` trước) |
| `oser update [--dry-run]` | sinh lại phần GENERATED; chạy lần hai không đổi gì |
| `oser status` · `oser quota --ngay 7` | mode/capability/model · thước đo quota (thay `do-quota.py`) |

## Quy trình

**Dự án mới:** hỏi người dùng đúng ba điều — repo authority (WHAT/WHY) ở đâu và file entry nào;
đường clone local tương đối; lệnh kiểm test. Rồi `oser install …` → `oser doctor` phải 0 critical 0 warning.

**Dự án 1.0 (có `cong-cu/doi-bac.py`, `.claude/BAC-DANG-DUNG.md`, 9 ghế):**
1. Viết `.claude/oser/project.json` từ `oser/templates/project.example.json` — khai authority, phase,
   file hiện hành, file lịch sử, stale marker, (tuỳ) Firebase target.
2. `oser doctor --manifest <file>` trên cây CHƯA đổi → ghi số BEFORE.
3. Dọn phần PROJECT-OWNED (CLAUDE.md prose, TRANG-THAI) — OSER không tự viết lại văn của dự án.
4. `oser migrate` → `oser doctor` → `oser migrate` lần hai phải 0 thay đổi.

Migrate chỉ thay tool 1.0 khi fingerprint chứng minh đó là bản chép nguyên (sửa rồi = dừng, không ghi
gì); định nghĩa agent chuyển nguyên byte sang `.claude/oser/inactive/`; không xoá mã, không đụng product.

## Luật khi dùng skill này

- Không sửa tay file GENERATED — sửa `project.json` rồi `oser update`; muốn tự giữ thì khai `overrides`.
- Không chép canon nghiệp vụ của authority vào repo — trỏ tới nó.
- Mode `setup`: không gọi subagent, không bật audit, không dựng đội build "cho sẵn".
- Đo, đừng tin: `oser quota` + `oser doctor` là bằng chứng, không phải cảm giác.
