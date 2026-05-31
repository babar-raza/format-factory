# R82 Train N — Probe Format Truth

**Sprint:** FORMAT-FACTORY-R82
**Date:** 2026-05-31

## Objective

Correct the overclaimed probe coverage from R78. R78 probe overclaimed FODP/FODG/Gnumeric/ABW as beyond current state.

## Probe Format Status (Corrected R78 IV Finding)

### Formats Currently at Gate 10 (local RC ready)
| Format | Python Source | Gate 10 Status | commercial_product_ready |
|--------|--------------|----------------|--------------------------|
| ZST | src/python/zst/ | VERIFIED | false |
| FODS | src/python/fods/ | VERIFIED | false |
| FODT | src/python/fodt/ | VERIFIED | false |
| FODP | src/python/fodp/ | VERIFIED | false |
| FODG | src/python/fodg/ | VERIFIED | false |
| Gnumeric | src/python/gnumeric/ | VERIFIED | false |
| ABW | src/python/abw/ | VERIFIED | false |
| PGM | src/python/pgm/ | VERIFIED | false |
| PBM | src/python/pbm/ | VERIFIED | false |
| SYLK | src/python/sylk/ | VERIFIED | false |

### Probe Overclaim Correction (D79-11)

R78 CORRECTED the probe overclaim: FODP/FODG/Gnumeric/ABW are at Gate 10 VERIFIED status — they do NOT have Gate 11 approved or commercial_product_ready=true. They are NOT beyond ZST/FODS/FODT in the pipeline.

All 10 formats at Gate 10 are equal in product-ready status: none are commercially ready, none have G11-G approval.

### Next Format Advancement

No new format advancement in R82 (not in scope). The sprint focuses on:
- Authority recovery for existing formats
- FODS/FODT installed workflow proof
- Package artifact production

### Format Probe Decision: NO_NEW_FORMAT_ADVANCEMENT_IN_R82
### PROBE_OVERCLAIM_CORRECTION: SUSTAINED_FROM_R78_IV
