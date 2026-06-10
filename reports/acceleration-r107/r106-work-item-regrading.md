# R106 Work Item Regrading — Acceleration R107

| Item ID | R106 Grade | R107 Regrade | Change | Rationale |
|---------|-----------|-------------|--------|-----------|
| ACCEL-R106-W0 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_VERIFIED | UPGRADED | 2 substantive review reports with honest analysis |
| ACCEL-R106-W1 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_VERIFIED | UPGRADED | autonomous_cycle.py Step 3b + 3 passing tests |
| ACCEL-R106-W2 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_VERIFIED | UPGRADED | grade_declared_work.py + 4 passing evidence quality tests |
| ACCEL-R106-W3 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_WITH_LIMITATIONS | UNCHANGED | Gaps are report-only, no tool change |
| ACCEL-R106-W4 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_VERIFIED | UPGRADED | 3 new detectors + 15 tests passing |
| ACCEL-R106-W5 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_VERIFIED | UPGRADED | Structure check + 4 tests passing |
| ACCEL-R106-W6 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_WITH_LIMITATIONS | UNCHANGED | Pilot was sample output, not full package validation |
| ACCEL-R106-W7 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_WITH_LIMITATIONS | UNCHANGED | Report-only lane |
| ACCEL-R106-W8 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_WITH_LIMITATIONS | UNCHANGED | Self-IV, no independent validation |

## Aggregate
- Upgraded: 5/9 (55.6%)
- Unchanged: 4/9 (44.4%)
- Downgraded: 0/9

## Forward Deficiencies from R106
1. Anti-skip violations are informational, do not block → Fix in Lane B
2. Evidence quality score does not affect verdict → Fix in Lane C
3. Prompt quality not called from cycle → Fix in Lane E
4. Continuation policy lacks evidence-quality gate → Fix in Lane G
