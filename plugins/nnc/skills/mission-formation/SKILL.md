---
name: mission-formation
description: Use when a user has a vague improvement idea, wants to build an app, agent, chatbot, automation, skill or report, says they do not know where to start, or needs help deciding whether to configure, buy, integrate, reuse or custom-build. Guides a non-technical user from real work to an approved Mission without forcing technical vocabulary.
version: 0.1.0
---

# NNC OSER — Mission Formation

Treat the user's language as the starting point. Do not require PRD, architecture,
database or agent terminology before the real job is understood.

## Flow

1. Intake — restate the real problem and intended outcome in business language.
2. Reality audit — learn the current process, actor, tools/data, frequency, pain,
   baseline if known, constraints and permissions. Do not invent missing data.
3. Research before custom build — check whether a native platform capability,
   configuration, existing tool/SaaS, reusable Skill/automation, composition or
   custom build best fits the problem. Search current sources when the answer is
   time-sensitive or product-specific.
4. Decision — for material choices, write a Decision Card and present consequences
   in user language. A recommendation is not approval. Always include an
   investigate/test-first path when uncertainty can be reduced safely.
5. Mission draft — only after direction is approved, propose goal, authority,
   outcome acceptance and the resource/safety envelope. R1 oser init remains the
   durable Mission lock.

Do not build merely because build is possible.

## Progressive disclosure

Read only what applies:
- Formation details: references/formation.md
- Decision Contract: references/decision-contract.md
- Clean Desk: references/clean-desk.md
- NNC-Kho case lessons only when the product is similar:
  references/case-nnc-kho.md

## Material decisions

For D2/D3 decisions, save a Decision Card under .nnc-oser/decisions through
oser decision-write, then generate the native question shape with oser decision-ask.

Never hide business consequences behind labels such as Firebase, vector DB,
OAuth, agent team or event bus. Translate the decision into what changes for the
user, data, recurring cost, maintenance, reversibility and next action.

## Stop condition

Formation is done when the user has approved a direction and the Mission draft
has explicit authority plus outcome acceptance. MISSION_READY is a validated
draft state, not approval and must not silently initialize or mutate production.
