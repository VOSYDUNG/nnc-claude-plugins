# Clean Desk Contract

A long-running AI project should have a small Active Desk.

Classify files as:
- CURRENT AUTHORITY — approved truth, explicit scope, locked/versioned;
- CURRENT STATE — Mission/frontier/blockers/decisions;
- WORKING DRAFT — research/proposals, never authority by proximity;
- EVIDENCE / ARTIFACT — proof and deliverables;
- HISTORY / ARCHIVE — audit-only unless explicitly promoted.

Default context should use current authority plus current state. Load drafts and
evidence on demand. History is audit-only.

If two locked authorities claim the same scope, stop that affected gate and
surface a conflict. Research/propose resolution, but never silently merge
contradictory business decisions.

A fresh session should not need to reread the whole repository to know what is
currently true.
