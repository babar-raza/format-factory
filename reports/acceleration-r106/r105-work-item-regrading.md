# R105 Work Item Regrading — Machine-Readable

| Item ID | R105 Grade | R106 Regrade | Change | Rationale |
|---------|-----------|-------------|--------|-----------|
| ACCEL-R105-W0 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_VERIFIED | UPGRADED | 3 substantive reports with root cause analysis |
| ACCEL-R105-W1 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_VERIFIED | UPGRADED | Real tool (234 lines) + 16 passing tests |
| ACCEL-R105-W2 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_WITH_LIMITATIONS | UNCHANGED | Local gaps fresh, global gaps still stale |
| ACCEL-R105-W3 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_VERIFIED | UPGRADED | Classification documented and embedded in schema |
| ACCEL-R105-W4 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_VERIFIED | UPGRADED | 2 new detectors + 8 new tests (42 total) |
| ACCEL-R105-W5 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_VERIFIED | UPGRADED | Real validator (119 lines) + 7 tests + 4 prompts |
| ACCEL-R105-W6 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_WITH_LIMITATIONS | UNCHANGED | Documentation pilot only, no ZIP built |
| ACCEL-R105-W7 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_WITH_LIMITATIONS | UNCHANGED | Self-IV, no independent validation |

## Aggregate
- Upgraded: 5/8 (62.5%)
- Unchanged: 3/8 (37.5%)
- Downgraded: 0/8 (0%)

## Forward Deficiencies from R105
1. Global selected-product-gaps.json still stale (R98) — fix in Lane D
2. No actual package pilot ZIP built — fix in Lane G
3. Grade engine lacks raw-proof inspection — fix in Lane C
4. Autonomous-cycle doesn't call package identity or anti-skip validators — fix in Lane B
