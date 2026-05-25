# R63 Train K — Acquisition / Spec-Cache / Sample Authority

**Sprint:** FORMAT-FACTORY-R63-AI-ASSISTED-RC-CLOSURE-AND-WORKAHEAD-MULTI-SPRINT-MEGA-TRAIN-001
**Date:** 2026-05-24

---

## Spec-Cache Status (R63)

All format spec-caches verified against acquisition-packs/*.yaml. No new spec-cache entries added in R63 (R63 is a closure sprint, not an acquisition sprint).

| Format | Spec-Cache Location | Status |
|---|---|---|
| FODS | acquisition-packs/fods/ | CLEAN |
| FODT | acquisition-packs/fodt/ | CLEAN |
| CSV | acquisition-packs/csv/ | CLEAN (Gate 8 PASS R61) |
| TSV | acquisition-packs/tsv/ | CLEAN |
| DIF | acquisition-packs/dif/ | CLEAN |
| PPM | acquisition-packs/ppm/ | CLEAN |
| ODS | acquisition-packs/ods/ | CLEAN |
| PGM | acquisition-packs/pgm/ | CLEAN |
| PBM | acquisition-packs/pbm/ | CLEAN |
| SYLK | acquisition-packs/sylk/ | CLEAN |

---

## Sample Authority

| Format | Samples Location | Status |
|---|---|---|
| FODS | samples/by-format/fods/ | PRESENT |
| FODT | samples/by-format/fodt/ | PRESENT |
| CSV | samples/by-format/csv/ | PRESENT |
| ODS | samples/by-format/ods/ | PRESENT |
| DIF | samples/by-format/dif/ | PRESENT |
| PPM | samples/by-format/ppm/ | PRESENT |

---

## Acquisition Policy

- All acquisition-packs/*.yaml files carry `unsupported_by_aspose: needs_audit` for new candidates
- Gate approval is delegated per DEC-034 (human IV required before agent-requested human review)
- No new candidates added in R63

---

SPEC_CACHE_AUTHORITY_STATUS: CLEAN
TRAIN_K_STATUS: COMPLETE
