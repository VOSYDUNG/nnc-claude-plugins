---
name: adaptive-delivery
description: Use when an NNC OSER Mission is already clear or approved and the user wants to build, configure, test, release, operate, fix or update the result. Chooses a delivery route appropriate to the product instead of forcing the NNC-Kho or web-app lifecycle.
version: 0.1.0
---

# NNC OSER — Adaptive Delivery

Read the active Mission and current authority first. Let the native agentic
runtime choose direct work, tools, subagents, workflows, parallelism, model and
effort inside approved boundaries.

Choose only the gates the product actually needs.

Examples:
- configuration/native automation: configure -> user test -> live -> measure;
- chatbot/assistant: knowledge/data -> behavior eval -> limited pilot -> live use;
- workflow automation: process contract -> dry-run -> monitored live run;
- Skill: examples -> build -> eval -> user use;
- report/sheet: source contract -> transform -> validate -> recurring use;
- production software: product behavior -> architecture -> build -> production
  readiness -> UAT -> release -> hypercare.

These are route examples, not a closed enum.

## Required invariants

- current authority cannot be silently replaced by a draft or history file;
- acceptance is outcome-based, not internal task count;
- build/test success is not automatically real-world acceptance;
- production-impacting actions follow host permissions and human authority;
- evidence and checkpoint state stay durable through session/agent changes;
- fix/update after live use becomes an explicit Delta Mission when it changes
  approved behavior or acceptance.

Use ai-oser for kernel state/evidence/health details. Use mission-formation if
the direction itself is still uncertain.
