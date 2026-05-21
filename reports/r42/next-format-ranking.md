# R42 Train 5: Next-Format Ranking

**Sprint:** R42
**Date:** 2026-05-21

---

## Tier 1 — Gate 9 Complete, Security Review Approved (ODS/ODT/QOI/XCF/DIF/PPM)

These formats have Gates 1-9 PASSED. Gate 8 (security review packets) were submitted
in R29-R30. Advancement to Gate 10+ requires human approval of Gate 8 packets.

| Format | Gates | Status | Blocker |
|--------|-------|--------|---------|
| ODS | 1-9 | G8 security packet AWAITING_HUMAN_APPROVAL | Human Gate 8 sign-off |
| ODT | 1-9 | G8 security packet AWAITING_HUMAN_APPROVAL | Human Gate 8 sign-off |
| QOI | 1-9 | G8 security packet AWAITING_HUMAN_APPROVAL | Human Gate 8 sign-off |
| XCF | 1-9 | G8 security packet AWAITING_HUMAN_APPROVAL | Human Gate 8 sign-off |
| DIF | 1-9 | G8 security packet AWAITING_HUMAN_APPROVAL | Human Gate 8 sign-off |
| PPM | 1-9 | G8 security packet AWAITING_HUMAN_APPROVAL | Human Gate 8 sign-off |

**Recommendation:** Human review of Gate 8 security packets (submitted R29/R30) is the critical path.

---

## Tier 2 — Gate 8 Complete (PGM/PBM/SYLK)

Passed Gates 1-8. Ready for Gate 9 (deep-dive capability).

| Format | Gates | Description | Next Action |
|--------|-------|-------------|-------------|
| PGM | 1-8 | P2 ASCII grayscale (Netpbm) | Gate 9 neutral model deepening |
| PBM | 1-8 | P1 ASCII bitmap (Netpbm) | Gate 9 neutral model deepening |
| SYLK | 1-8 | Symbolic Link text spreadsheet | Gate 9 neutral model deepening |

---

## Tier 3 — Gate 9 Adjacent (FODP/FODG/Gnumeric/ABW)

G9 probe-only status. These share ODF XML family with FODS/FODT.

| Format | Status | Track Note |
|--------|--------|------------|
| FODP | G9 probe_only | OpenDocument Presentation; closely related to FODS/FODT |
| FODG | G9 probe_only | OpenDocument Drawing; XML-family |
| Gnumeric | G9 passed | XML+gzip; has parser in src/python/gnumeric/ |
| ABW | G9 passed | AbiWord XML; has parser in src/python/abw/ |
| ZST | G9 passed | Zstandard compression; format-agnostic wrapper |

---

## Tier 4 — Gate 3 (CSV/TSV/XPM/PAM)

Early-stage candidates added in R30. All text or simple binary formats.

| Format | Gates | Description |
|--------|-------|-------------|
| CSV | 1-3 | Comma-separated values (universal) |
| TSV | 1-3 | Tab-separated values |
| XPM | 1-3 | X PixMap text format |
| PAM | 1-3 | Portable Arbitrary Map (Netpbm) |

---

## Blocked

| Format | Status | Reason |
|--------|--------|--------|
| ZPAQ | G2 BLOCKED | ZPAQL VM complexity; requires zpaq CLI |
| ORA | Deferred | 6.8/10 below 7.0 threshold |

---

## R42 Format Advancement Summary

- **ODS/ODT/QOI package readiness:** Gates 1-9 complete; Python source present. Wheel builds pending Gate 8 human approval.
- **ZST package readiness:** Gates 1-9; Python source in `src/python/zst/`. Wheel already built in prior sprint.
- **DIF/PPM/XCF advancement:** Gates 1-9 complete with full Gate 4-7 test suites. Ready for Gate 10 once Gate 8 approved.
- **Priority recommendation:** Human Gate 8 sign-off for ODS/ODT/QOI/XCF/DIF/PPM is the single highest-value next action.
