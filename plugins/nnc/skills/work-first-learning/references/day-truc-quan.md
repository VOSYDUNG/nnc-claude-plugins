# Dạy bằng hình và bằng tay — the teacher's visual & interaction toolbox (v0.8)

Contract: `docs/oser-r2/LOP-HOC-V08-THIET-KE.md` §1, §2, §5. Model instructions are in English; everything the learner sees is in the learner's language (Vietnamese or Lao). Nothing here is ever quoted to the learner: no ids, no "widget", no "state".

**You are the visual author.** The podium is a stage you set every turn; the lesson canvas in the chat is your whiteboard. The six templates below are **ready to adapt**: change the words, the picture, the colours' emphasis, the size; combine two; or invent a new one. Only the rules in §0 are fixed.

## 0. Rules

1. **One idea per visual.** Title ≥ 20 px, ≤ 5 short lines, a **picture before words**. If a visual needs a second idea, make a second visual.
2. **Show, then ask.** A visual comes before the question about it. After Claude produces a result, show a **result explainer** (C) before asking anything.
3. **The learner does, not reads back.** A visual ends with something to touch: a button that answers (D, E), a podium choice, a one-touch, or "bấm vào chỗ này trên màn hình" with `podium.point`.
4. **Honest and sample-only.** Sample numbers are labelled *ví dụ*. A visual never shows a real file name, real customer, cost, debt or salary data. Usage and limit facts come only from the official pages ([the-dinh-nghia.md](the-dinh-nghia.md)); live numbers come from the `Mở lớp` cue or `podium.show`, never from memory.
5. **Palette and type** (the classroom's own colours): green `#008816` · dark green `#006D11` · deep `#0B3B16` · yellow `#FFEA00` · dark yellow `#C9A800` · paper `#FFFDF0` · ink `#1f2a1f`; drive colours D1 `#3CC85A` · D2 `#4A90E2` · D3 `#F5A524`. Font stack for every visual (Vietnamese and Lao): `"Leelawadee UI","Phetsarath OT","Noto Sans Lao",sans-serif`. Give each card its own paper background (`#FFFDF0`) so it reads the same in a light or dark chat.
6. **Density.** Every part has at least one visual and one non-native interaction; the first of each within your first two turns ([SKILL.md](../SKILL.md) §12.4). A visual is a move, not decoration: it replaces a paragraph of talk, it does not add one.

## 1. Which surface

| Surface | Use for | How |
|---|---|---|
| **Podium `board`** (state field) | one small slide that stays beside the input while the learner works: a 3-line rule, a tiny picture, a checklist | `board {title ≤ 60, lines ≤ 5 × 90, svg ≤ 16 KB}`; the mod sanitises the SVG (no `<script>`, no `<foreignObject>`, no event attributes, no external `href`) and drops it when invalid → always give `lines` too |
| **Podium `choices`** | the default way to ask: big non-blocking buttons | `choices {id, prompt, options[2–5], default, timeout_s}` — click → `[Lớp học] Chọn · <id> · <label>` |
| **Podium `point`** | "click this real control": the mod highlights the fact on the podium **and** draws the bottom-bar picture with an arrow and the line *"ở thanh dưới ô nhập"* | `podium.point: "mode" \| "effort" \| "model" \| "context" \| "usage5" \| "usageWeek"`; `null` clears |
| **Lesson canvas** (the session's visual tool `show_widget`) | slides, annotated mock-ups, result explainers, answer-button widgets, 60-second games | see below |
| **Artifact** (optional) | a keepsake giáo án or a longer illustrated explanation the learner can reopen | only when it earns its place |

**How to use the canvas tool.** It is the session's built-in visual tool (its listed name may carry a prefix, e.g. `…show_widget`). If its description says to read a guide first (`read_me`), call that **once, silently**, before the first widget; never mention it to the learner. Pass: a `title` (snake_case, specific), `widget_code` (an `<svg …>` or an HTML fragment — **no** `<!DOCTYPE>`, `<html>`, `<head>`, `<body>`), and `loading_messages` (1–4 short lines in the learner's language, plain and calm). A global `sendPrompt(text)` is available in the widget: it sends `text` to the chat **as if the learner typed it** — that is how a widget returns an answer.

**Fallback.** The tool is not in your tool list, or it fails once → do not retry in a loop: put the same idea on the podium `board` (`lines` + a small SVG) and ask with `choices`; in plain chat without the podium, use a short text picture and one native box. The lesson never depends on a widget.

## 2. Template A — bottom-bar mock-up (Claude Desktop)

The real Desktop layout: **left** = permission mode label; **right** = model name · effort · the round usage circle. Folder and *This computer* sit in the session header, not in this bar. Use it for the card the learner must find on screen (mode, model, effort, usage). Pair it with `podium.point` so the real control is lit as well.

Highlight an area: on that area's `<rect id="hl-…">` set `fill="#FFEA00" fill-opacity=".45" stroke="#C9A800" stroke-width="3"` (the others stay `fill="none" stroke="none"`), then move the arrow and its caption. The example below highlights **effort**.

| Area | rect id | arrow x (tip) | caption anchor |
|---|---|---|---|
| mode | `hl-mode` | 115 | middle, x 115 |
| model | `hl-model` | 402 | middle, x 402 |
| effort | `hl-effort` | 501 | middle, x 501 |
| usage | `hl-usage` | 582 | end, x 620 |

Mode dot colour: Auto `#3CC85A` · Manual `#4A90E2` · Plan `#C9A800` · Bypass `#F5A524` (draw it as a warning, never as a recommendation). Edit the labels to the live values from the cue (`Mở lớp` · `Chế độ quyền`), never from memory.

```svg
<svg viewBox="0 0 640 178" xmlns="http://www.w3.org/2000/svg" font-family="'Leelawadee UI','Phetsarath OT','Noto Sans Lao',sans-serif">
  <rect width="640" height="178" rx="14" fill="#FFFDF0" stroke="#008816" stroke-width="2"/>
  <text x="20" y="32" font-size="20" font-weight="700" fill="#0B3B16">Thanh dưới ô nhập</text>
  <rect x="20" y="44" width="600" height="44" rx="12" fill="#fff" stroke="#9aa89a"/>
  <text x="36" y="72" font-size="15" fill="#6b7a6b">Giao việc cho Claude…</text>
  <rect id="hl-mode" x="20" y="98" width="190" height="34" rx="17" fill="none" stroke="none"/>
  <circle cx="40" cy="115" r="6" fill="#3CC85A"/>
  <text x="54" y="121" font-size="15" fill="#1f2a1f">Auto</text>
  <rect id="hl-model" x="352" y="98" width="100" height="34" rx="17" fill="none" stroke="none"/>
  <text x="402" y="121" font-size="15" text-anchor="middle" fill="#1f2a1f">Opus 5.5</text>
  <rect id="hl-effort" x="458" y="98" width="86" height="34" rx="17" fill="#FFEA00" fill-opacity=".45" stroke="#C9A800" stroke-width="3"/>
  <text x="501" y="121" font-size="15" text-anchor="middle" fill="#1f2a1f">Medium</text>
  <rect id="hl-usage" x="556" y="98" width="52" height="34" rx="17" fill="none" stroke="none"/>
  <circle cx="582" cy="115" r="11" fill="none" stroke="#cfd8cf" stroke-width="4"/>
  <circle cx="582" cy="115" r="11" fill="none" stroke="#4A90E2" stroke-width="4" stroke-dasharray="28 41" transform="rotate(-90 582 115)"/>
  <path d="M501 156 V146" stroke="#006D11" stroke-width="4"/>
  <path d="M492 148 L501 136 L510 148 Z" fill="#006D11"/>
  <text x="501" y="171" font-size="16" font-weight="700" text-anchor="middle" fill="#006D11">Effort: bấm vào chữ này</text>
</svg>
```

Lao captions: ຊ່ອງ effort — ກົດໃສ່ຕົວໜັງສືນີ້ · ແຖບລຸ່ມຊ່ອງພິມ. Ask the learner to **click it** (*"Chị bấm thử vào chữ này, rồi cho cô biết đang có những mức nào nhé"*) — never *"chị đọc cho cô effort đang là gì"*: you already know it.

## 3. Template B — concept slide (HTML for the canvas)

Title · one everyday analogy · one **"Trên máy bạn"** line (where to find it on screen) · one picture area. The example is card 6, *context* (the desk).

```html
<div style="font-family:'Leelawadee UI','Phetsarath OT','Noto Sans Lao',sans-serif;background:#FFFDF0;color:#1f2a1f;border:2px solid #008816;border-radius:16px;overflow:hidden;max-width:620px">
  <div style="background:#008816;color:#fff;padding:12px 18px;font-size:22px;font-weight:700">Context — mặt bàn làm việc</div>
  <div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap;padding:16px 18px">
    <svg viewBox="0 0 180 120" width="180" height="120" xmlns="http://www.w3.org/2000/svg" aria-label="Mặt bàn đầy giấy">
      <rect x="10" y="88" width="160" height="10" rx="3" fill="#0B3B16"/>
      <rect x="22" y="40" width="64" height="48" rx="3" fill="#fff" stroke="#9aa89a"/>
      <rect x="30" y="28" width="64" height="48" rx="3" fill="#fff" stroke="#9aa89a"/>
      <rect x="40" y="16" width="64" height="48" rx="3" fill="#FFEA00" stroke="#C9A800"/>
      <rect x="112" y="52" width="48" height="36" rx="3" fill="#fff" stroke="#9aa89a"/>
      <text x="90" y="114" font-size="12" text-anchor="middle" fill="#006D11">bàn đầy → dọn bớt, mở bàn mới</text>
    </svg>
    <div style="flex:1;min-width:220px;font-size:18px;line-height:1.5">
      <p style="margin:0 0 10px">Context như <b>mặt bàn</b>: bày càng nhiều giấy càng khó tìm; đầy bàn thì phải dọn.</p>
      <p style="margin:0;background:#FFEA00;border-radius:8px;padding:8px 10px"><b>Trên máy bạn:</b> bục giảng ghi <i>context …%</i>; theo sách: gõ /context (Hình 4).</p>
    </div>
  </div>
</div>
```

Reusable pieces for any slide:

- **"Trên máy bạn" line** — the yellow strip above: always says *where on the screen* to find the thing.
- **"Làm theo" block** — a colour-framed step block for steps the learner performs on screen (one block per screen, ≤ 3 steps, verbs first):

```html
<div style="font-family:'Leelawadee UI','Phetsarath OT','Noto Sans Lao',sans-serif;border-left:8px solid #3CC85A;background:#EAF7EC;color:#1f2a1f;border-radius:10px;padding:12px 16px;max-width:560px;font-size:18px;line-height:1.55">
  <div style="font-weight:700;color:#006D11;font-size:20px;margin-bottom:6px">Làm theo</div>
  <ol style="margin:0;padding-left:22px"><li>Bấm vào chữ <b>Medium</b> ở thanh dưới ô nhập.</li><li>Chọn một mức khác.</li><li>Nói cho cô biết chị thấy mấy mức.</li></ol>
</div>
```

## 4. Template C — result explainer (source beside result)

Show it after **every** Claude result, before any question. Source rows on the left, result rows on the right, the **rows to check highlighted** (yellow) with a tag, and one line **"Cách tự kiểm"**. 3–6 rows; sample or masked data only; label *ví dụ* when the rows are samples.

```html
<div style="font-family:'Leelawadee UI','Phetsarath OT','Noto Sans Lao',sans-serif;background:#FFFDF0;color:#1f2a1f;border:2px solid #008816;border-radius:16px;overflow:hidden;max-width:640px">
  <div style="background:#008816;color:#fff;padding:12px 18px;font-size:22px;font-weight:700">Claude vừa làm gì? <span style="font-size:14px;font-weight:400">(ví dụ)</span></div>
  <div style="display:flex;gap:12px;padding:14px 18px;flex-wrap:wrap">
    <div style="flex:1;min-width:230px">
      <div style="font-weight:700;color:#006D11;margin-bottom:4px">Nguồn (file gốc)</div>
      <table style="width:100%;border-collapse:collapse;font-size:16px">
        <tr style="background:#fff"><td style="padding:5px 8px;border:1px solid #cfd8cf">Phiếu 001 · 12 hộp</td></tr>
        <tr style="background:#FFEA00"><td style="padding:5px 8px;border:1px solid #C9A800">Phiếu 002 · 8 hộp</td></tr>
        <tr style="background:#fff"><td style="padding:5px 8px;border:1px solid #cfd8cf">Phiếu 003 · 20 hộp</td></tr>
      </table>
    </div>
    <div style="flex:1;min-width:230px">
      <div style="font-weight:700;color:#006D11;margin-bottom:4px">Kết quả (bảng của Claude)</div>
      <table style="width:100%;border-collapse:collapse;font-size:16px">
        <tr style="background:#fff"><td style="padding:5px 8px;border:1px solid #cfd8cf">001 · 12</td></tr>
        <tr style="background:#FFEA00"><td style="padding:5px 8px;border:1px solid #C9A800">002 · 8 <b>← kiểm dòng này</b></td></tr>
        <tr style="background:#fff"><td style="padding:5px 8px;border:1px solid #cfd8cf">003 · 20</td></tr>
      </table>
    </div>
  </div>
  <div style="padding:0 18px 14px;font-size:18px"><b style="color:#006D11">Cách tự kiểm:</b> đặt dòng vàng ở hai bên cạnh nhau — số có khớp không?</div>
</div>
```

After the explainer, the next move is the learner's: *"Chị thử kiểm dòng vàng, rồi bấm Khớp hoặc Có chỗ lệch"* — as podium `choices` or template D.

## 5. Template D — interactive check (buttons answer in the chat)

A question with 2–4 big buttons. A click sends `[Lớp học] Trả lời · <id> · <value>` to the chat as the learner's own answer (`id` short and unique per widget, `value` readable). Buttons lock after one click and show a calm "đã nhận". Use it for a quiz item, a quick check, a multi-field form (one button group per field, one **Gửi** button that sends `<id> · field=value; field=value`), or a "which one is the mistake" picture.

```html
<div id="chk" style="font-family:'Leelawadee UI','Phetsarath OT','Noto Sans Lao',sans-serif;background:#FFFDF0;color:#1f2a1f;border:2px solid #008816;border-radius:16px;padding:16px 18px;max-width:560px">
  <div style="font-size:22px;font-weight:700;color:#0B3B16;margin-bottom:12px">Bảng khoảng 40 dòng — nên dùng effort nào?</div>
  <div style="display:flex;flex-wrap:wrap;gap:10px">
    <button onclick="pick(this,'Mức vừa')" style="font:inherit;font-size:18px;padding:10px 16px;border:2px solid #008816;border-radius:12px;background:#fff;cursor:pointer">Mức vừa</button>
    <button onclick="pick(this,'Mức cao nhất')" style="font:inherit;font-size:18px;padding:10px 16px;border:2px solid #008816;border-radius:12px;background:#fff;cursor:pointer">Mức cao nhất</button>
    <button onclick="pick(this,'Chưa rõ')" style="font:inherit;font-size:18px;padding:10px 16px;border:2px solid #008816;border-radius:12px;background:#fff;cursor:pointer">Chưa rõ</button>
  </div>
  <div id="chk-note" style="margin-top:10px;font-size:16px;color:#006D11;min-height:22px"></div>
</div>
<script>
function pick(b,v){
  var all=document.querySelectorAll('#chk button');
  for(var i=0;i<all.length;i++){all[i].disabled=true;}
  b.style.background='#FFEA00';b.style.borderColor='#C9A800';
  document.getElementById('chk-note').textContent='Đã nhận câu trả lời của bạn.';
  sendPrompt('[Lớp học] Trả lời · effort-40-dong · '+v);
}
</script>
```

Right and wrong answers are never judged inside the widget; you answer in the next turn (praise the specific thing, one correction, the check) like any other answer. "Chưa rõ" is always a fair button and never a failure.

## 6. Template E — 60-second game (widget)

A timed round of Đúng/Sai (the `game:dung-sai` kind; write `activity.kind` before the widget). The clock and the score live in the widget; at the end — all answered **or** 60 s — it sends one result line. No native box while it runs ([SKILL.md](../SKILL.md) §10.6). Replace the items with your own (facts only from the cards); 4–6 items.

```html
<div id="g" style="font-family:'Leelawadee UI','Phetsarath OT','Noto Sans Lao',sans-serif;background:#FFFDF0;color:#1f2a1f;border:2px solid #008816;border-radius:16px;padding:16px 18px;max-width:560px">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <div style="font-size:22px;font-weight:700;color:#0B3B16">Đúng hay sai? 60 giây</div>
    <div id="g-t" style="font-size:24px;font-weight:700;color:#C9A800">60</div>
  </div>
  <div id="g-q" style="font-size:19px;line-height:1.45;margin:14px 0;min-height:56px"></div>
  <div style="display:flex;gap:10px">
    <button onclick="ans(true)" style="font:inherit;font-size:20px;padding:10px 26px;border:2px solid #008816;border-radius:12px;background:#fff;cursor:pointer">Đúng</button>
    <button onclick="ans(false)" style="font:inherit;font-size:20px;padding:10px 26px;border:2px solid #006D11;border-radius:12px;background:#fff;cursor:pointer">Sai</button>
  </div>
  <div id="g-s" style="margin-top:12px;font-size:16px;color:#006D11;min-height:22px"></div>
</div>
<script>
(function(){
  var Q=[["Claude hỏi quyền thì mình đọc xong rồi mới đồng ý.",true],["Bypass permissions là chế độ khuyên dùng cho người mới.",false],["Làm trên bản sao thì file gốc vẫn nguyên.",true],["Effort cao hơn thì thường nghĩ kỹ hơn và dùng hạn mức nhiều hơn.",true]];
  var i=0,ok=0,t=60,over=false;
  var q=document.getElementById('g-q'),tm=document.getElementById('g-t'),s=document.getElementById('g-s');
  function show(){q.textContent=(i+1)+'/'+Q.length+' · '+Q[i][0];}
  function end(){
    if(over){return;} over=true; clearInterval(h);
    var b=document.querySelectorAll('#g button');
    for(var k=0;k<b.length;k++){b[k].disabled=true;}
    s.textContent='Xong: '+ok+'/'+Q.length+' đúng. Đã gửi cho thầy/cô.';
    sendPrompt('[Lớp học] Trả lời · game-dung-sai · '+ok+'/'+Q.length+' trong '+(60-t)+' giây');
  }
  window.ans=function(v){
    if(over){return;}
    if(v===Q[i][1]){ok++;}
    i++; if(i>=Q.length){end();}else{show();}
  };
  var h=setInterval(function(){t--;tm.textContent=t;if(t<=0){end();}},1000);
  show();
})();
</script>
```

The win is stated before the game (*"3/4 trong 60 giây là thắng"*); a timeout is not a failure — say the one lesson sentence kindly either way ([kho-tro-choi.md](kho-tro-choi.md)).

## 7. Template F — podium board (SVG ≤ 16 KB)

The board is a small slide on the podium, written into `state.json` (§12.1 of the Skill). Rules: `title` ≤ 60 characters, `lines` ≤ 5 × 90 characters, `svg` ≤ 16 KB, **plain SVG only**: no `<script>`, no `<foreignObject>`, no event attributes, no external `href` (an invalid SVG is dropped and the board shows `title` + `lines` only — so the lines must work alone). Use single quotes inside the SVG so it sits in JSON without escaping. Keep it small: the podium shows it beside the input.

```json
"board": {
  "title": "Effort — nghĩ kỹ đến đâu",
  "lines": ["Việc nhỏ, rõ ràng: mức vừa là đủ.", "Việc khó, nhiều bước: mới tăng.", "Tăng thì thường chậm hơn và tốn hạn mức hơn."],
  "svg": "<svg viewBox='0 0 300 110' xmlns='http://www.w3.org/2000/svg' font-family='Leelawadee UI,Phetsarath OT,Noto Sans Lao,sans-serif'><rect width='300' height='110' rx='10' fill='#FFFDF0'/><rect x='24' y='64' width='60' height='24' rx='6' fill='#cfd8cf'/><rect x='120' y='44' width='60' height='44' rx='6' fill='#FFEA00' stroke='#C9A800' stroke-width='3'/><rect x='216' y='20' width='60' height='68' rx='6' fill='#cfd8cf'/><text x='54' y='104' font-size='12' text-anchor='middle' fill='#1f2a1f'>Thấp</text><text x='150' y='104' font-size='12' text-anchor='middle' fill='#1f2a1f'>Vừa</text><text x='246' y='104' font-size='12' text-anchor='middle' fill='#1f2a1f'>Cao</text><text x='150' y='30' font-size='14' font-weight='700' text-anchor='middle' fill='#006D11'>40 dòng: ở đây</text></svg>"
}
```

A full stage for one turn (this is what the one `Write` of the turn can carry; leave a field out and it is cleared):

```json
"podium": { "size": "wide", "show": ["effort"], "point": "effort", "buttons": ["hint", "slower"] },
"board": { "title": "Effort — nghĩ kỹ đến đâu", "lines": ["…"], "svg": "<svg …>…</svg>" },
"choices": { "id": "effort-1", "prompt": "Bảng 40 dòng: effort nào là đủ?", "options": [{ "label": "Mức vừa" }, { "label": "Mức cao nhất" }, { "label": "Chưa rõ" }], "default": 0 }
```

## 8. Choosing and combining

| The learner needs to… | Reach for |
|---|---|
| find a control on screen | **A** + `podium.point` + a "Làm theo" block |
| understand an idea | **B** (analogy + "Trên máy bạn"), or **F** if it must stay beside the input |
| trust or check a result | **C**, then **D** or `choices` to answer |
| be checked without a test feeling | **D** (one question) or a podium `choices` |
| wake up after a long stretch | **E** (≤ 60 s) |
| a quick, quiet nudge | podium `board` + `choices` only |

Combine freely (a mock-up inside a slide; a result explainer whose last row is a button group). Re-author for the learner's trade and language; keep the one idea. Check before sending: one idea · picture first · ≤ 5 short lines · something to touch · sample data only · live numbers from the cue, not from memory.
