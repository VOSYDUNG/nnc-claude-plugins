# Work-first learning v0.1 — Claude Code pilot runbook

**Branch:** feat/learning-work-first-v0.1 (draft learning layer).
**Baseline:** NNC OSER 5.1.0-alpha.2, GitHub main commit 94ddf8b5a7cd69a65a3bf54991486da70c2a0282.
**Status:** new Skill + simulated scenarios; no live learner or Claude Code conformance claim.
**Authority:** training exploration in a clean permitted folder. No production changes, silent account switching, raw private data, auto OSER init, telemetry or separate kernel.

## What is and is not being changed

Adds **/nnc:work-first-learning** as a first encounter for someone who does not yet have a clear improvement Mission. It begins from what happened today, yesterday or the latest shift, with one relevant question at a time, coaching through one safe step and changed/missing input.

It does **not** rewrite /nnc:ai-oser, /nnc:mission-formation, /nnc:adaptive-delivery, R1 state, the R2 Decision Guard, plugin version or the existing marketplace source. A/B here means *learning to improve current work* and *learning to build/update a tool where justified*. These are not the two R2 workflow names.

## Before testing on a person's Claude Code Desktop

1. Make an **empty local test directory** containing only synthetic or permitted input. Keep it separate from any live project, the NNC OSER source checkout on XEON, and personal/private folders.
2. Confirm Python 3.9+ and Git, and inspect installed plugin sources/versions. The existing nnc marketplace may point at main/alpha.2 or a local checkout; do **not** install an identically named marketplace on top of another.
3. Obtain this exact feature branch via a **separate checkout** rather than the default main. Keep the baseline intact. Ask Claude to inspect the local checkout's marketplace descriptor and the new Skill before installation.
4. Install/reload this checkout only using the Claude Code Desktop plugin mechanism supported by that installed version. A GitHub marketplace entry with no branch pin can load main, where the new Skill does **not** exist. Verify that /nnc:work-first-learning actually appears; if not, record INSTALL_NOT_VERIFIED and stop rather than claiming the test ran.
5. Do not enable Experience Observer during the first pilot. It is opt-in, not proof of learning.

## Suggested first message

Start the /nnc:work-first-learning Skill, then send:

> Tôi muốn thực hành làm việc cùng Claude với NNC OSER. Đừng hỏi chức danh hay bắt mô tả công việc tổng quát. Hãy giúp tôi từ một việc hôm nay, hôm qua hoặc ca gần nhất, **mỗi lượt một câu hỏi quan trọng**, rồi chuyển sang một bước làm thử an toàn khi đủ thông tin. Dùng dữ liệu giả hoặc bản được phép. Tôi muốn tự kiểm kết quả và thử lại khi đầu vào thay đổi. Không tự mở Mission chính thức, tự cài phần mềm, chia sẻ dữ liệu hoặc xây web/app khi chưa rõ vấn đề. Hãy bắt đầu.

If the learner gives a concrete recent work item immediately, Claude should **not** ask them to name it again.

## Suggested bounded session

- **Entry:** capture first 3–5 turns; observe one-question progressive discovery and a small safe first action.
- **Guided practice:** learner performs/checks one output with Claude.
- **Recovery:** evaluator introduces a synthetic changed field, stale source or missing fact; learner catches and resolves or correctly blocks.
- **Transfer:** learner gets a new instance. Distinguish teacher-driven completion from independent use of Claude; don't award real operational reuse without a real next occurrence.
- **Handoff:** keep only non-sensitive outcome/check/help-needed/next-action references.

Use the [scenario catalog](../../plugins/nnc/skills/work-first-learning/references/scenarios.md); choose contrasting work contexts, not preset departments.

## Exit criteria and honest reporting

**Offline gate:** plugin structure and rule text checked; CI tests passing if the branch CI triggers.

**Claude host gate:** actual loaded plugin/version and the Skill invocation observed; no assumptions from GitHub CI.

**Learning behavior gate:** the evaluator witnesses the questions, safe tool actions, changed-input handling and level of coaching. A text-only dry-run is not proof of learner independence.

**Business gate:** a separate later work instance accepted by the right receiver, with appropriate permissions. A prototype result cannot replace owner approval or company SOP acceptance.

Keep the pilot in draft if any gate is unobserved. A failed case should improve the learning method before adding UI Mods or changing the OSER kernel.
