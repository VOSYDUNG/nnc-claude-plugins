# Lớp học NNC v0.11 — giáo viên tự chủ: thang im lặng, vòng học không ngừng, nói ngắn

Nguồn: kiểm tra 18/10 — giáo viên chỉ có 5 lượt trong 23 phút, mọi lượt đều là phản ứng; câu cuối "Thầy đang đợi" rồi đứng yên. Nguyên nhân: (1) không có tín hiệu nào khi học viên im lặng; (2) chốt "không giảng vào phòng trống" (`l.quiet`): học viên chưa tác động thì mod không gửi tín hiệu nữa; (3) giáo viên trao quyền lái cho học viên ("Bây giờ mình làm gì?").

Quyết định của người phụ trách (coaching nhiều người): **học viên im lặng thường vì chưa hiểu mình đang làm gì**, không phải vì không biết gì; AI hay đưa output rất dài để đọc thay vì trò chuyện tương tác, tập trung. Đó là lý do có "engine giáo viên" bọc ngoài Claude. Giữ nguyên tắc **không giảng vào phòng trống**, không chạy phiên liên tục; thêm thang có giới hạn.

## 1. Thang im lặng (mod)

When the class is active (entered, not paused, no Xin phép), no native box is open, the teacher's turn is not running, the input is empty, and the learner has not acted (no submit, no click, no choice) since the teacher's last reply ended:

| Nấc | After | Cue (hidden) |
|---|---|---|
| 1 | 90 s | `[Giáo án] Học viên im lặng · nấc 1` |
| 2 | 3 min after nấc 1 | `[Giáo án] Học viên im lặng · nấc 2` |
| 3 | 5 min after nấc 2 | `[Giáo án] Học viên im lặng · nấc 3` |

After nấc 3 the mod sends nothing more until the learner acts (the "no empty room" rule stays). Any learner action resets the ladder. The ladder replaces the old `l.quiet` blanket stop only for these three cues; the other cues keep their own rules. Challenge running (`challenge` with clock) or `activity.kind` `hands-on`/`form` → nấc 1 waits 3 min instead of 90 s (the learner is working).

## 2. Teacher reaction to silence (Skill)

Silence = the learner does not yet understand what they are doing. Never add more text.

- **Nấc 1 — khai thác:** one short question about what they **see or are doing now** (podium `choices` 2–3 options, e.g. *"Bạn đang ở bước nào?"* · *"Chưa rõ bước này để làm gì"* · *"Màn hình khác với hình"*) + **one line saying what this step is for** + the step shown (marked screenshot / mock-up). ≤ 3 lines.
- **Nấc 2 — làm nhỏ / làm mẫu:** cut the step into one tiny action, or demonstrate it yourself (one-touch demo), then hand back one touch. ≤ 3 lines.
- **Nấc 3 — lưu chỗ:** save the resume point, one warm line *"Lớp vẫn mở, lúc nào quay lại mình học tiếp đúng chỗ này"*, `status: "paused"`, stop.
- Never "Thầy đang đợi", never repeat the same instruction, never a paragraph.

## 3. Vòng học không ngừng (Skill)

At Chốt vòng việc the teacher **proposes the next loop itself** (default = continue), never an open "bạn muốn làm gì tiếp?". Content: the next open book sections (ban-do-sach.md) shaped to the learner's job; when the session has a web search/fetch tool, the teacher may research **public** information about the learner's line of work to make the example real, under 5 guardrails: public info only, source and date under the visual; label *"thông tin công khai, không phải số liệu NNC"*; never put learner or company data into a search query; ≤ 3 lookups per turn and none at ≥ 70 % usage; no tool → class library, silently. The loop stops only on Xin nghỉ, usage ≥ 90 %, or after silence nấc 3.

## 4. Nói ngắn, trò chuyện (Skill + mod)

- Skill: every teacher message ≤ 3 short lines (≈ 45 words) of text plus one touch; one idea; ask, don't lecture; Claude's own long work output is never shown raw to the learner as the teaching message — summarise it in one line and show a result explainer.
- Mod: a teacher message longer than ~600 characters renders collapsed — the first 3 lines plus a "▸ Xem đầy đủ" toggle (i18n vi/lo) — on surfaces that raise `AssistantMessage`; tool output untouched.

## 5. Góc nhìn độc lập (tối giản)

Facts and grading follow evidence (book, official page, the real result), not the learner's insistence; never mark a wrong answer right or award a star under pressure; change position only on new evidence and say why; the learner decides pace and style, the teacher decides correctness and safety; the learner's consent and right to stop stay absolute.

## 6. Checker (`tools/kiem-buoi-hoc.py`)

New rules: R9 every silence cue answered with an action within the next teacher turn (not "đợi"); R10 teacher messages: median ≤ 45 words, none > 120 words without a visual; R11 no open "làm gì tiếp" question at a loop end without a proposed default.

## 7. Versions

`lop-hoc` 0.11.0 · Skill 0.11.0 · `nnc` `5.1.0-alpha.2+lophoc.0.11.0` (never alpha.3) · tag `lop-hoc-v0.11.0` after the owner's review.
