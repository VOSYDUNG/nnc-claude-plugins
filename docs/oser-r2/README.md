# NNC OSER R2 — Human Mission Space

R2 is an additive alpha over the provider-neutral R1 Mission kernel.

## Two connected workflows

### Workflow A — Formation / Decision

vague problem -> reality audit -> research available paths -> consequence-oriented
decision -> approved direction -> Mission draft.

The goal is to help a non-technical user form the right Mission before custom
building. Research may conclude that configuration, an existing product, a
reusable Skill, an integration or a custom build is appropriate.

### Workflow B — Adaptive Delivery / Operation

approved Mission -> product-appropriate delivery route -> evidence / user test ->
real use -> operation -> Delta Mission for fix/update.

The route is not fixed. A chatbot, spreadsheet, Skill, automation and production
web application do not need the same gates.

## R1 remains the kernel

R1 still owns durable Mission state, authority, acceptance, capability admission,
execution receipts, checkpoints, evidence, Health, usage and reconciliation.

R2 alpha currently adds:
- material Decision Card validation and native AskUserQuestion rendering;
- a plugin PreToolUse Decision Guard for saved D2/D3 cards;
- Clean Desk classification and same-scope authority conflict detection;
- Formation packet validation;
- mission-formation and adaptive-delivery skills;
- NNC-Kho lessons as optional case knowledge, not universal rules.

## CLI alpha

    oser decision-check --input decision.json
    oser decision-write --project PROJECT --input decision.json
    oser decision-ask --input decision.json
    oser desk-check --project PROJECT --input desk.json
    oser formation-check --input formation.json

These commands validate/draft. They do not approve a business decision, create a
Mission, deploy, or start a model.

## Claude Code decision guard

The plugin bundles a PreToolUse hook for AskUserQuestion. It only acts when an
incoming question exactly matches a saved OSER material Decision Card. If the
model strips the consequence-oriented option descriptions, the hook denies that
single question and asks Claude to regenerate it from the card.

Unrelated AskUserQuestion calls pass through untouched. The hook does not choose
an answer, auto-approve D3, or alter host permissions.

## UI adapter status

The Human Mission pane/band/toast concept is NOT a kernel dependency and is not
enabled by this alpha. The installed Claude Code environment must be probed with
plugin-authoring/mod support before shipping a UI adapter.

The stable fallback remains native chat + Skills + hooks + CLI/Mission state.
