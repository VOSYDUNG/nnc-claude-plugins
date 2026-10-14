# Work-first learning v0.1 — Claude Code Desktop pilot runbook

**Target host:** Claude Desktop on Windows, **Code** tab, **Local** session only.
**Feature branch:** feat/learning-work-first-v0.1 (draft learning layer).
**Core plugin:** NNC OSER 5.1.0-alpha.2 from GitHub main commit 94ddf8b5a7cd69a65a3bf54991486da70c2a0282.
**Status:** static Skill and CI tests passed; no real Desktop behavior or learner independence is yet verified.

## Two separate layers, no plugin collision

1. **OSER core:** the existing installed **nnc** plugin from main/alpha.2 supplies Mission Formation, Decision Cards, Adaptive Delivery and OSER state. Do not replace, reinstall from alpha.3 or merge branches for this test.
2. **Learning layer:** copy **work-first-learning** from the feature branch into a disposable **project-local Skill** folder. This is the supported way to test the exact Skill instructions in Claude Code Desktop without replacing the marketplace/plugin name used by the core.

**Names differ during this first test:** project-local Skill is **/work-first-learning**; base OSER plugin Skills remain **/nnc:mission-formation**, **/nnc:adaptive-delivery** and **/nnc:ai-oser**. The proposed packaged name **/nnc:work-first-learning** can be tested separately after plugin integration/release. Do not claim the package installed simply because a project Skill works.

## Desktop-only setup (Windows, no CLI)

1. Open the [feature branch](https://github.com/VOSYDUNG/nnc-claude-plugins/tree/feat/learning-work-first-v0.1) in a browser. Click **Code → Download ZIP** and extract into a new folder. Do not extract on top of any existing NNC OSER checkout.
2. In File Explorer, create a new empty folder for simulated work, for example **NNC-Learning-Sandbox** in your user home folder (not a production repo). Inside it, create this exact structure:

~~~text
NNC-Learning-Sandbox/
└── .claude/
    └── skills/
        └── work-first-learning/
            ├── SKILL.md
            └── references/
                └── scenarios.md
~~~

3. Copy the **SKILL.md** and its **references** directory from the ZIP's **plugins/nnc/skills/work-first-learning/** into this new location. Do not copy the marketplace, plugin.json, hooks, .mcp.json, or OSER source into the sandbox.
4. Open **Claude Desktop → Code → New session**. Select **Local** and choose **NNC-Learning-Sandbox** as the project folder. Use **Manual** permission mode for first contact. On Windows, the Code tab requires Git for Windows installed.
5. In that Code session, click **+ → Plugins → Manage plugins** and verify **nnc** is enabled from the approved main/alpha.2 source. If the core is not installed, use **+ → Plugins → Add plugin** and install the existing NNC marketplace's main/alpha.2 core at local/project scope. **Do not add the feature branch as a second marketplace of the same name:** adding a marketplace with an existing name can replace the earlier source, and alpha.2 versus branch snapshots may share a version label. If the source/version is unclear, stop at **OSER_SOURCE_UNVERIFIED** and report the screenshot.
6. In the Code prompt box, type **/work-first-learning** or choose that Skill from **+ → Slash commands**. Confirm it appears. If absent, close this sandbox session and create a new Local Code session after checking the folder tree. Do not claim the Skill loaded until observed.
7. Confirm **/nnc:mission-formation** is separately available in the same session. Do not invoke it automatically: hand off only if the concrete learning case genuinely becomes a material improvement decision requiring Mission Formation.
8. Do **not** enable Experience Observer, run OSER init, grant broad filesystem permissions, upload private data or write to live systems during this first practice.

### First learner message

After selecting **/work-first-learning** in Claude Desktop Code, send:

> Tôi muốn thực hành với Claude từ một việc thực tế gần nhất. Không hỏi chức danh hoặc mô tả nhiệm vụ tổng quát. Hãy bắt đầu bằng đúng một câu hỏi về hôm nay, hôm qua hoặc ca gần nhất; mỗi lượt chỉ hỏi điều quan trọng tiếp theo. Khi đủ thông tin, hãy hướng dẫn tôi làm một bước nhỏ bằng dữ liệu giả hoặc đã được phép; để tôi tự kiểm kết quả, xử lý dữ liệu thay đổi và biết cách tiếp tục. Không tự tạo Mission, không xây web/app hoặc cài thêm công cụ nếu chưa có căn cứ.

If the user already described a concrete recent job, Claude should continue directly instead of asking for that same job again.

## What this proves — and does not prove

- **G1 Desktop discovery:** /work-first-learning project Skill appears under a Local Code session.
- **G2 OSER core:** /nnc:mission-formation is available from an independently verified main/alpha.2 install.
- **G3 Guidance:** first 3–5 turns start from recent work, one relevant question at a time; move to a safe action without a long intake form.
- **G4 Recovery:** use an invented changing/missing field; learner detects and verifies it, rather than Claude guessing.
- **G5 Independent transfer:** the learner handles a new instance without the trainer performing material decisions. Business reuse still requires a later real occurrence accepted by the responsible receiver.

**Separate future gate:** native installation of the feature-branch plugin package and hooks in Claude Desktop. The project-local Skill trial does **not** establish that branch plugin packaging, MCP configuration or global installation works.

Use the [seven simulated cases](../../plugins/nnc/skills/work-first-learning/references/scenarios.md). A person's actual legitimate job is preferable once permissions are clear; never use a mandatory department or role-based training exercise.

## Evidence to return for review

- Screenshot of **Code / Local / sandbox project**.
- Screenshot of **+ → Skills** showing **/work-first-learning** and **/nnc:mission-formation**, or errors.
- First 3–5 questions/answers and the changed-input test with synthetic information.
- Observed tool/version status, blocked step and one improvement to the method.

Keep the PR draft until actual Desktop behavior and teaching value are reviewed. Do not report a CLI, static CI or a successful file export as real learner acceptance.

**Official docs:** https://code.claude.com/docs/en/desktop and https://code.claude.com/docs/en/skills.
