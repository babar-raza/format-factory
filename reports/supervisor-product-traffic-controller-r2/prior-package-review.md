# Prior Package Review — R1 Regrading

## Prior Sprint
`FORMAT-FACTORY-SUPERVISOR-PRODUCT-TRAFFIC-CONTROLLER-INTEGRATION-001`

## Confirmed Facts from R1 Package

| Metric | Value |
|--------|-------|
| evidence_quality_score | 0.0 |
| verified_item_count | 0 |
| total items | 11 |
| items ACCEPTED_WITH_LIMITATIONS | 11/11 |
| items ACCEPTED_VERIFIED | 0/11 |
| anti-skip violations | 6 |
| missing raw logs | YES |
| missing lane ledger | YES |
| missing sample outputs | YES (0 found, 1+ required) |
| dirty_git_state classified | NO (has_classification: false) |
| wrong_stream_next_sprint | YES (mainstream not supervisor) |
| autonomous_continue (review) | True |
| continuation_state (signal) | YES_WITH_LIMITATIONS |

## Anti-Skip Violation Details

1. **missing_raw_logs** (medium) — No raw test logs found anywhere in evidence or reports.
2. **missing_lane_ledger** (medium) — No lane-execution-ledger.yaml/json found.
3. **missing_sample_outputs** (low) — 0 sample output files found, checker requires 1+.
4. **dirty_git_state** (medium) — Git state is dirty, `has_classification: false` in anti-skip.
5. **wrong_stream_next_sprint** (medium) — Global next-sprint.md targets mainstream, not supervisor stream.
6. **Continuation discrepancy** — R1 continuation_signal.json for supervisor-product-traffic-controller had autonomous_continue=True but stop_reason="Evidence quality: 0% verified".

## R1 Item Regrading

| Item | R1 Grade | R2 Regrade | Reason |
|------|---------|-----------|--------|
| TC-COORD-001 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_WITH_LIMITATIONS | Path-only; docs present |
| TC-DIAG-001 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_WITH_LIMITATIONS | Path-only; docs present |
| TC-WIRE-001 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_VERIFIED (R2) | CLI output captured in lane ledger |
| TC-ROUTE-001 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_WITH_LIMITATIONS | JSON files present but no run proof |
| TC-CONS-001 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_VERIFIED (R2) | CLI output captured in lane ledger |
| TC-CONT-001 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_WITH_LIMITATIONS | Examples JSON present, test verified by raw log |
| TC-EXT-001 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_WITH_LIMITATIONS | JSON present; governance status verified |
| TC-HANDOFF-001 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_WITH_LIMITATIONS | Handoff docs present; content verified |
| TC-TEST-001 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_VERIFIED (R2) | Raw logs prove 53/53 pass |
| TC-SYNC-001 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_WITH_LIMITATIONS | Files present; sync verified |
| TC-CLOSE-001 | ACCEPTED_WITH_LIMITATIONS | ACCEPTED_WITH_LIMITATIONS | autonomous-cycle exit 0 proven |

## Verdict
**PRIOR_PACKAGE_REVIEWED** — 3 items upgradeable to ACCEPTED_VERIFIED with R2 evidence.
Remaining 8 items remain ACCEPTED_WITH_LIMITATIONS (path-only acceptable for doc/plan items).
