# Experience Observer — privacy and interpretation

Purpose: measure self-service workflow friction without asking users to fill out feedback forms after every session.

## Stored locally

When explicitly enabled for a project, .nnc-oser/experience.jsonl may contain:
- event type;
- timestamp;
- hashed session reference;
- OSER decision id/level;
- Formation stage;
- selected route id only when it matches a saved Decision Card;
- technical source label.

## Never stored

The observer intentionally does not persist:
- user prompt text;
- free-text answers;
- chat transcripts;
- names or email addresses;
- cwd/project path;
- filenames from user work;
- credentials/tokens;
- model chain-of-thought.

## Interpretation

Useful signals:
- Formation started/advanced;
- material decisions presented/completed;
- Decision Guard corrections;
- investigate-first route usage;
- runtime interruptions;
- context compactions;
- session lifecycle.

These are behavioral signals, not sentiment. A long decision may mean confusion, a deliberate pause, or unrelated interruption.
Use direct user questions only when the reason itself matters.

## Storage / export

The default observer is local-only and does not upload events.
Any future centralized analytics/export must be a separate, explicit capability with its own authority/privacy policy.
