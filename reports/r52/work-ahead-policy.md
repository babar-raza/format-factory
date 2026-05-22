# R52 Work-Ahead Policy

**Sprint:** FORMAT-FACTORY-R52-STATE-CONSISTENT-INSTALLED-ARTIFACT-BASELINE-CLEAN-001

## Deferred to R53

| Item | Reason | R53 Priority |
|------|--------|--------------|
| FODS formula preservation (TC-0054) | Scoped out of R52 (state repair took full sprint) | HIGH |
| FODT structure preservation (TC-0057–0059) | Same | HIGH |
| FODT TXT/Markdown export | Deferred from R51 | MEDIUM |
| AI acceleration round 3 | Requires live endpoint | MEDIUM |
| Phase Audit 4 continuation (FODS/FODT gaps) | Deferred | MEDIUM |
| Phase Audit 5 planning | Deferred | LOW |
| Physical invariants + requirements matrix | Scoped out | MEDIUM |

## R53 Opening Invariants

1. State snapshot must return `R52_STATE_CONSISTENT_INSTALLED_ARTIFACT_BASELINE_CLEAN` as R52 verdict
2. All 827+ evidence tests pass
3. All 35 R52 guard tests pass
4. Auto-proof builder passes full 3-pass build in CI
