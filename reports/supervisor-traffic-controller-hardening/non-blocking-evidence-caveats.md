# Non-Blocking Evidence Caveats — Hardening IV

## From Prior Supervisor Bundle (R2)

These caveats from the prior sprint are classified as NON-BLOCKING for this hardening sprint:

| Caveat | Classification | Reason |
|---|---|---|
| evidence_quality_score was 0.0 in R1 | NON-BLOCKING | Fixed in R2 (0.27); prior R1 score is historical |
| missing_raw_logs in R1 | NON-BLOCKING | Fixed in R2 — 6 raw log files captured |
| missing_lane_ledger in R1 | NON-BLOCKING | Fixed in R2 — lane-execution-ledger.yaml |
| missing_sample_outputs in R1 | NON-BLOCKING | Fixed in R2 — 5 CLI output files |
| wrong_stream_next_sprint (caveat in R2) | NON-BLOCKING | ARCHIVED_LAST_WRITER_SNAPSHOT; non-blocking per anti-skip checker |
| continuation discrepancy | NON-BLOCKING | Root cause documented in continuation-consistency.md; not a real contradiction |
| generic next-work-items SUP-PIPE/SUP-EVIDENCE | NON-BLOCKING | Addressed in Lane D — product routing hardened |
| work items as path-only evidence (8/11) | NON-BLOCKING | Doc/planning items are legitimately path-only; 3 key items now ACCEPTED_VERIFIED |

## Non-Blocking Architectural Notes

- Acceleration `ai_output_status = no_ai` in R113 replay — NON-BLOCKING (Acceleration stream hadn't produced ai_draft yet)
- Skills `skills_breadth_score = 0` in R113 replay — NON-BLOCKING (Skills hadn't produced product breadth yet; now has packet)
- Mainstream `breadth=2/3` needed — NON-BLOCKING (addressed in routing handoff; 3-family target is the goal)

## These caveats do NOT require code fixes

None of the above warrant implementation changes in this sprint. They are historical evidence packaging concerns that were resolved in R2 or are design-level limitations well understood and documented.
