# R78 SYLK/DIF Product Decision

**sprint_id:** FORMAT-FACTORY-R78-TRUE-STATE-AND-FIRST-PRODUCT-FINISH-REPRODUCIBILITY-MEGA-TRAIN-001
**date:** 2026-05-30
**train:** L

## Formats Under Decision

| Format | Description | Current Gate |
|---|---|---|
| SYLK | Symbolic Link (SLK) — text spreadsheet | Gates 1-7 |
| DIF | Data Interchange Format — text spreadsheet | Gates 1-7 |

## Decision Criteria

| Criterion | SYLK | DIF |
|---|---|---|
| Acquisition score | 8.2/10 (Accept) | ~8.0/10 (Accept) |
| Public spec | YES (documented; Multiplan-era) | YES (VisiCalc-era; public domain) |
| Implementation done | YES (src/python/sylk) | YES (src/python/dif) |
| Package built | YES (wheel+sdist) | NO package built |
| Market/use case | Legacy spreadsheet interchange | Legacy spreadsheet interchange |
| Gate 8 security | LOW (text-only) | LOW (text-only) |
| Dependency | None | None |

## Decision

SYLK_DECISION: CONTINUE_TO_GATE_8

Rationale: SYLK has a package already built, 8.2/10 score, text-only format,
and serves as a useful legacy spreadsheet import format. Gate 8 is straightforward.
The SYLK parser exists and is tested through Gate 7.

DIF_DECISION: CONTINUE_TO_GATE_8

Rationale: DIF has 8.0/10 score, a working parser (src/python/dif/dif_parser.py,
303 lines), tests through Gate 7, and is historically significant as the first
spreadsheet interchange format. Text-only, no security concerns.
Note: DIF package was not built in R77; build required before Gate 8.

## Legacy Format Note

Both SYLK and DIF are legacy formats (1980s-era) that are no longer in mainstream use.
However, they are still encountered in data migration scenarios from old software.
The Format Factory acquisition model accepts formats with sufficient public technical info,
and both formats meet that criterion.

## Next Steps Required

1. SYLK: Submit Gate 8 security review packet (human approval required)
2. DIF: Build wheel+sdist; submit Gate 8 security review packet
3. Both: After Gate 8 approval, advance to Gates 9-10

SYLK_DECISION: CONTINUE
DIF_DECISION: CONTINUE
GATE_8_REQUIRED: YES (human approval for both)
DIF_PACKAGE_BUILD_REQUIRED: YES (not built yet)
