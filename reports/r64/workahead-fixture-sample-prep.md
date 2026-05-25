# R64 W2 — Fixture/Sample Preparation

**Sprint:** FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
**Date:** 2026-05-25

---

## Fixture Inventories

| Format | Existing Fixtures | R64 Additions | Expected Behavior Notes |
|---|---|---|---|
| XPM | 0 samples | Inventory prepared (no downloads) | ASCII image, X11 color names |
| PAM | 0 samples | Inventory prepared (no downloads) | P7 header, TUPLTYPE field |
| QOI | 4 samples | Existing sufficient | RGB/RGBA, run-length + diff encoding |
| ODT | 4 samples | Existing sufficient | ZIP-based ODF text document |
| ODS | 4 samples | Existing sufficient | ZIP-based ODF spreadsheet |
| DIF | samples present | Existing sufficient | TABLE/VECTORS/TUPLES/DATA structure |
| PPM | samples present | Existing sufficient | P3 ASCII Netpbm RGB |
| SYLK | samples present | Existing sufficient | Symbolic Link text spreadsheet |

## Notes

- No external downloads performed (repo policy compliance)
- No copyrighted/spec text committed
- XPM and PAM will need sample creation in R65/R66 (synthetic generation from existing Netpbm/X11 patterns)

---

W2_FIXTURE_PREP_STATUS: COMPLETE
