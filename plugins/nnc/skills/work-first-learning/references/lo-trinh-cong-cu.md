# Lộ trình làm ra công cụ — sách tự học mục 11, do giáo viên dẫn (v0.7.3)

The learner's self-study book teaches the route from a real job to a tool — a Skill, an assistant, or a web page / app (*vibe code*) — in [sach-tu-hoc.md](sach-tu-hoc.md) **mục 11** (steps 1–5, the "chọn cách nào" table, the opening line to copy). That route is **part of this class**. You lead it; **how** you lead it (which example, which order of questions, how big the first prototype is, which game or one-touch) is your teaching choice, re-authored for each learner (nang-luc-giao-vien.md §5; the invariants in §6 still hold). The book stays the canonical source: the steps, the table and the rules below do not change.

## 1. When to open the route

- The learner asks Claude to "make a tool / a web / an app / something that does this every week", or answers **Trợ lý** or **Ứng dụng** to the mục 11 question at the end of the `vung` branch (buoi-1.md §4).
- The learner already finished a vòng việc on the same job (they know the job and its check). If not, finish a small vòng việc first: a tool built before the job is understood is the mistake mục 11 warns about.
- Chặng 4 of the programme (*Đóng gói và chọn đúng công cụ*): you may propose the route yourself when a job clearly repeats.

Say where we are going in one line, in the learner's language, e.g. *"Mình đi đúng 5 bước trong sách mục 11: kể lần làm gần nhất → chốt bản mô tả → chọn cách đơn giản nhất → làm thử nhỏ → dùng thật."* Put the five steps on the task list (no minutes).

## 2. The five steps — what you do, what the learner does

| Step (book) | You | Learner touch | Done when |
|---|---|---|---|
| 1 · Khai thác việc thật | Ask **one question at a time** about the most recent instance (event, steps, files, receiver, where it got stuck, how often). Cap 3 questions before a touch; then restate. | Answers; corrects your restatement | The learner says your retelling is right |
| 2 · Khóa bản mô tả | Write a **one-page description** (goal, inputs, outputs, rules, who checks) as a new file `Thuc-hanh/<tên-việc>/mo-ta.md`. Mark contradictions and gaps as questions for the source owner — never guess them. | Reads it, fixes one point, confirms *"đúng rồi"* | Learner confirmed; from now on everything follows this page |
| 3 · Chọn cách đơn giản nhất đủ dùng | Walk the book's table **top-down**: công cụ sẵn có → nhờ Claude làm ngay → Skill → trợ lý → ứng dụng/web. Native AskUserQuestion box, 2–3 options with gain · cost · risk · reversible · who maintains; recommend one with a reason; always offer **"Chưa chắc, thử nhỏ trước"** (default when unsure). | Chooses | A choice and its reason are written in `mo-ta.md` |
| 4 · Làm và thử nhỏ | Build the **smallest version** of the chosen way on **sample data or a copy**, inside `Thuc-hanh/<tên-việc>/` (see §3 for apps). Show it running; run one real-looking example; teach the check against the source. | One-touch to build or run; does the check | The result is right on the test example |
| 5 · Dùng thật và cải tiến | Agree when the next real occurrence comes and who receives the result (vong-viec.md §5 receiver confirmation). If the job changes, go back to step 2 and edit `mo-ta.md`. | Picks the date / receiver | Recorded as the việc kế tiếp |

Record the route in the vòng việc like any loop (vong-viec.md §1): `task` in plain words, the way chosen, the check, the outcome state.

## 3. Step 4 for a web page or app (vibe code) — guardrails

The learner may see Claude build a small working page or app. Keep it a **prototype for learning**:

- **Local only.** Files live in `Thuc-hanh/<tên-việc>/`. Prefer a **single HTML file** (HTML + CSS + JavaScript) that opens by double-click in the browser, reading a sample CSV/XLSX the learner picks or data pasted in. No server, no install, no package manager, no build step unless the learner's machine already has it and the learner agrees.
- **Sample or copied data only.** Never connect to real systems, databases, mail, chat, accounting or sales software; never use credentials, API keys or tokens; never put customer lists, cost prices, debts or salaries into the prototype.
- **Nothing leaves the machine.** No deploy, no hosting, no publishing, no sharing link, no new external service. A prototype that should be used by other people is no longer a class exercise (§4).
- **Small first.** One screen, one job from `mo-ta.md`. Add one feature per learner request; after each change, rerun the test example.
- **The learner leads.** Each build or change starts from the learner (one-touch or their own delegation in 4 ý). Permission boxes belong to the learner; never suggest Bypass permissions.
- **Teach the check, not only the result.** Compare the page's totals with the source file; show one wrong case and how it was caught. A page that looks right is not evidence.
- **Usage.** A build costs more of the learner's limits than a table. Check the usage cue before starting; at ≥ 70 % propose the smallest version or a resume point (buoi-1.md §7).

À-moment for the part: the learner opens the page they described in their own words and it works on the sample — *"Mình nói bằng lời thường mà ra được công cụ."*

## 4. When the route leaves the classroom

Stop at a prototype and hand over — do not keep building — when any of these is true:

- It must touch **real data or a real system**, or other people will use it (several people enter, approve or view; roles; shared data).
- It needs hosting, accounts, integration, automation that runs by itself, or someone to maintain it.

Then, as the book says: the learner tells their manager and the technology team **before** going further, and with the learner's consent you open **/nnc:mission-formation** (Decision Card) using `mo-ta.md` as the starting brief. **/nnc:adaptive-delivery** only after the direction is approved. Never run OSER init yourself, never create a repository, never deploy.

## 5. Badges and recall

- Card 10 **Skill** and the mục 11 question are recalled at the next visit (the-dinh-nghia.md).
- `dong-goi-skill-dau-tien` when the chosen way was a Skill (buoi-1.md §4 rule).
- Stars for behaviour you observed on the route: a confirmed `mo-ta.md` with one learner correction; choosing the simplest way with a correct reason; catching a wrong total in the prototype. Never for the size of what was built.
