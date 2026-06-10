# Product-Output Floor Policy

## Floor Classes

| Class | Condition | Outcome |
|-------|-----------|---------|
| PRODUCT_DELTA_PASS | ≥2 source files changed + tests pass + sample output | Counts as product progress |
| SINGLE_CRITICAL_GAP_PASS | 1 POC-closing gap fully closed | Counts as product progress |
| BLOCKER_WITH_REROUTE_PASS | Lane blocked + another target advanced | Counts as product progress |
| EVIDENCE_ONLY_NO_PASS | Only evidence/report files changed | Does NOT count as product progress |

## Rules

- EVIDENCE_ONLY in normal product mode → EVIDENCE_ONLY_CONTINUE, loop continues.
- Missing sample output is a repair task, not a stop.
- Dogfood pipeline required for export capabilities before marking accepted_for_poc.
- Source diff required for every source-changing lane.
- Test log required for every product lane.
