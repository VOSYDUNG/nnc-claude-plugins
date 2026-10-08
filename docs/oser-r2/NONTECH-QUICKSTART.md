# NNC OSER R2 — Quickstart for non-technical users

NNC OSER is designed so you can start with a normal sentence such as:

> I want a chatbot for our fanpages but I do not know where to start.

You do not need to prepare a PRD, choose a framework, select a database, or know how agents work.

## 1. Install the plugin once

In Claude Code Desktop, open a local project/folder, then use **+ → Plugins**.
Install the **nnc** plugin from the NNC marketplace/repository configured by your team.
Claude Code supports plugins at user or project scope.

After an update, use /reload-plugins or start a new session so the latest skills/hooks are loaded.

Repository:
https://github.com/VOSYDUNG/nnc-claude-plugins

## 2. Start with your real job

Tell Claude what you want in business language. Examples:

- "I want a chatbot for our fanpages but do not know where to start."
- "This monthly report takes too long; help me improve it."
- "I want AI to help check these documents before accounting closes them."

NNC OSER should first use Mission Formation:
- understand the current work;
- identify what is actually painful;
- research simpler/native/existing options before custom building;
- show important decisions with consequences;
- form a Mission only after direction is clear.

## 3. Decisions

For material choices, do not pick only from technical names.
Ask Claude to explain:
- what happens if you choose each option;
- benefits and tradeoffs;
- major risk;
- whether it is reversible;
- data/access impact;
- recurring cost/maintenance;
- what happens next.

A valid material decision also includes:
**"I am not sure — investigate/test first."**

## 4. Local experience observer

For a pilot, Claude can run:

    oser experience-enable --project .

It records only local workflow events under .nnc-oser/ such as:
- Formation stage checked;
- an OSER material decision was presented/completed;
- a decision prompt needed correction;
- runtime interruption/compaction/session lifecycle.

It does **not** record prompt text, answer text, filenames, personal names, credentials, or transcripts.

View a summary:

    oser experience-report --project .

Disable:

    oser experience-disable --project .

Behavioral telemetry measures friction; it does not prove user satisfaction.

## 5. What the user should focus on

You only need to decide:
- what outcome you want;
- whether Claude understood the current work;
- whether the consequences of a choice make sense;
- whether the result works in real work.

Claude/OSER handles the technical workflow underneath.
