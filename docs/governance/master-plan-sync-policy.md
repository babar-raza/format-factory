# Master Plan Sync Policy

**Created:** 2026-06-10
**Authority:** This document defines update and freshness rules for `plans/master-plan.md`.

## Rules

### 1. No-Append-Only Rule
Every update to the master plan must review and condense existing content. Appending new sections without condensing old ones is forbidden. If a new section is added, at least one existing section must be reviewed for staleness.

### 2. Line Budget
The master plan must remain between 400 and 700 lines. Exceeding 700 lines triggers a mandatory condensation sprint before any other work proceeds.

### 3. Freshness Triggers
The master plan must be reviewed for freshness after any of these events:
- Phase change
- Gate transition
- Major decision (new DEC-xxx)
- Architecture amendment
- Stream reorganization

### 4. Stale-Claim Lint
At every healing sprint, run these 10 grep patterns against `plans/master-plan.md` and classify each finding:

1. `COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE` — must be 0 or HISTORICAL_OK only
2. `No functional commands exist` — must be 0
3. `bundle must be uploaded by human` — must be 0
4. `Product stages.*1 format` — must be 0
5. `Codex.*optional secondary` — must be 0
6. `SVG.*replace.*Netpbm` — must be 0
7. `commercial_product_ready.*true` — must be 0
8. `not yet authorized` — check context
9. Old run numbers (`run015|run016|run017|run027`) — must be 0
10. Old sprint names (`QUARTER-MILE|SWARM-001`) — must be 0

### 5. Source-of-Truth Rule
Any claim in the master plan that duplicates a canonical source (per `master-plan-canonical-source-map.md`) must be a pointer, not a copy. Inline copies of dynamic data (sprint status, product targets, format counts) are forbidden.

### 6. Split-Out Authorization
Documents in `docs/governance/` are authorized split-outs from the master plan. The master plan retains a brief canonical summary with a pointer to each governance doc.

### 7. Archive Rule
Historical content must be archived to `docs/history/`, never deleted. Every archived section must have a pointer in the master plan's ARCHIVE-PTR block.

### 8. Version Rule
The header version and the footer version in the master plan must always match. Both must be updated in the same edit.
