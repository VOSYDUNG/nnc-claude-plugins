---
name: mission-formation
description: Use when a user has a vague improvement idea, wants to build an app, agent, chatbot, automation, skill or report, says they do not know where to start, or needs help deciding whether to configure, buy, integrate, reuse or custom-build. Guides a non-technical user from real work to an approved Mission without forcing technical vocabulary.
metadata:
  version: "0.1.0"
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
5. QA/QC sơ bộ (early verification) — after direction is approved, form the
   Mission's common rules: outcome acceptance criteria with the evidence kinds each
   `requires`; invariants (source-of-truth data, authority, safety, privacy); the
   QC checks/evaluators that will produce each evidence kind in delivery and who or
   what evaluates; remaining unknowns and how to reduce them. QA designs how the
   outcome will be assured; QC is the concrete checks. Without it, not MISSION_READY.
   See references/formation.md.
6. Mission draft — carry those rules into goal, authority, outcome acceptance and
   the resource/safety envelope. R1 oser init remains the durable Mission lock and
   fixes the acceptance denominator; changing the rules after lock is a Delta Mission.

Do not build merely because build is possible.

For an approved pilot, the local Experience Observer may be enabled with `oser experience-enable --project .`. Tell the user once that it records workflow events only and never chat/prompt content; do not upload those events.

## Progressive disclosure

Read only what applies:
- Formation details: references/formation.md
- Decision Contract: references/decision-contract.md
- Clean Desk: references/clean-desk.md
- NNC-Kho case lessons only when the product is similar:
  references/case-nnc-kho.md

## Material decisions

For D2/D3 decisions, save a Decision Card under .nnc-oser/decisions through
oser decision-write, then present the decision through the active host interface.
Use a host-native question tool when that host documents one; do not require a
Claude-only question API on Codex or another host.

Never hide business consequences behind labels such as Firebase, vector DB,
OAuth, agent team or event bus. Translate the decision into what changes for the
user, data, recurring cost, maintenance, reversibility and next action.

## Stop condition

Formation is done when the user has approved a direction, QA/QC sơ bộ has
produced the Mission's common rules, and the Mission draft has explicit authority
plus outcome acceptance. MISSION_READY is a validated
draft state, not approval and must not silently initialize or mutate production.
