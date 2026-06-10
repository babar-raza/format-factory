# Weak Proof Reduction (Skills R105 Train G)

## Definition
"Weak proof" = path-only evidence where a file exists but no validator/test/log confirms its content is correct.

## R105 Proof Dimensions

| Proof Type | R104 Count | R105 Count | Improvement |
|-----------|-----------|-----------|-------------|
| Automated tests | 50 | 63 | +13 new tests |
| Validator JSON outputs | 3 | 3 | Maintained |
| Machine-readable JSONs | 1 | 4+ | +regrading, contamination, transcript matrix |
| Raw test logs | 1 | 1 | Maintained |
| Transcripts validated | 4 | 6 | +2 R105 transcripts |
| Handoff schemas | 1 template | 2 structured YAML | +2 complete handoffs |

## Items That Remain Path-Only

| Item | Reason | Acceptable? |
|------|--------|-------------|
| Adoption checklists | Human-facing markdown, no automation | Yes — checklists are process docs |
| Stream-state isolation | Documents infra limitation, can't auto-fix | Yes — classification is the evidence |
| Next prompt | Standalone text, no test needed | Yes — content is the evidence |

## Rule: No ACCEPTED_VERIFIED Without Direct Proof

Applied in R105 regrading (Train A):
- W2 (skill promotion): ACCEPTED_VERIFIED — 21 tests prove it
- W3 (validator hardening): ACCEPTED_VERIFIED — 50 tests, raw log, JSON results
- W4 (transcripts): ACCEPTED_VERIFIED — validator confirms 4/4
- W0, W1, W5, W6: ACCEPTED_WITH_LIMITATIONS — path evidence only
