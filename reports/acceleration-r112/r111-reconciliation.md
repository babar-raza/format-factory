# R111 Reconciliation — Acceleration R112

## R111 Package Identity
- Sprint ID: FORMAT-FACTORY-ACCELERATION-R111-STREAM-OUTPUT-AUTHORITY-GLOBAL-NEXT-SPRINT-CLEANUP-AND-EVIDENCE-QUALITY-CAMPAIGN-001
- Tests: 428 passed, 0 failed, 0 skipped (27 new)
- Prompt quality: valid=true (6/6 checks)
- Evidence quality: 0.78 (7/9 ACCEPTED_VERIFIED, 2/9 ACCEPTED_WITH_LIMITATIONS)
- Package missing_count: 0
- Raw log: PRESENT (.local/evidences/acceleration-r111/raw-test-log.txt)
- Lane ledger: PRESENT (9 waves, all DONE)
- Review package SHA: 57cd5caf6878a284aaf61ae84713539c105289c2130e73225cc1a77f64ce8781

## Anti-Skip Result
- total_checks: 14
- violations: 2
- all_pass: false
- Violation 1: missing_sample_outputs (LOW) — sample-outputs/ directory empty
- Violation 2: wrong_stream_next_sprint (MEDIUM) — detected_stream=skills

## Contradictions Found
| Finding | R111 Claim | Actual | Severity |
|---------|-----------|--------|----------|
| Anti-skip all_pass | "all quotas met" (final IV) | false (2 violations) | Consistency gap |
| Sample outputs | 5 in manifest | 0 in directory check | Detection gap |
| Wrong-stream source | skills | workspace global (last writer) | Source tracing gap |
| Continuation state | YES | Should be YES_WITH_LIMITATIONS | Semantics gap |

## Classification
- R111 progress: ACCELERATION_PROGRESS_ACCEPTED
- Anti-skip consistency: REWORK_REQUIRED
- Continuation semantics: REWORK_REQUIRED
