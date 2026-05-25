# R64 W1 — R65/R66 Readiness Matrix

**Sprint:** FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
**Date:** 2026-05-25

---

## Top 10 Format Candidates

| Rank | Format | Source Maturity | Parser | Writer/Export | Fixtures | Tests | Pkg Ready | Security | Publication | Score |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | QOI | HIGH | Gate 7 | N/A | 4 samples | 37 | MEDIUM | Gate 7 fuzz | NOT_READY | 8.1 |
| 2 | ODT | HIGH | Gate 7 | N/A | 4 samples | 41 | MEDIUM | Gate 7 fuzz | NOT_READY | 8.0 |
| 3 | ODS | HIGH | Gate 9 | N/A | 4 samples | 34 | MEDIUM | Gate 7 fuzz | NOT_READY | 8.0 |
| 4 | DIF | HIGH | Gate 9 | N/A | samples | 39 | MEDIUM | Gate 7 fuzz | NOT_READY | 7.8 |
| 5 | PPM | HIGH | Gate 8+ | N/A | samples | 40 | MEDIUM | Gate 7 fuzz | NOT_READY | 7.6 |
| 6 | XPM | MEDIUM | Gate 3 | N/A | 0 | 0 | LOW | NOT_STARTED | NOT_READY | 7.5 |
| 7 | PGM | HIGH | Gate 10 | N/A | samples | 20+ | HIGH | Gate 7 | NOT_READY | 7.4 |
| 8 | PBM | HIGH | Gate 10 | N/A | samples | 20+ | HIGH | Gate 7 | NOT_READY | 7.3 |
| 9 | PAM | MEDIUM | Gate 3 | N/A | 0 | 0 | LOW | NOT_STARTED | NOT_READY | 7.2 |
| 10 | SYLK | MEDIUM | Gate 10 | N/A | samples | 20+ | HIGH | Gate 7 | NOT_READY | 7.1 |

## Top 4 Package Candidates (R65)

1. **QOI** — Gate 7 complete, encoder/corpus hardening ready
2. **ODT** — Gate 7 complete, stats/export continuation
3. **ODS** — Gate 9 complete, export ready
4. **DIF** — Gate 9 complete, Windows path repair needed

## Top 4 Prototype Candidates (R66)

1. **XPM** — parser prototype feasible
2. **PAM** — parser prototype feasible (Netpbm family)
3. **PGM** — installed package smoke ready
4. **PBM** — installed package smoke ready

---

W1_READINESS_MATRIX_STATUS: COMPLETE
