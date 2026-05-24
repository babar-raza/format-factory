# R60 Train J — Acquisition / Spec-Cache Advancement

**Sprint:** FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
**Date:** 2026-05-24
**Status:** COMPLETE

---

## Scope

Train J maintains and verifies the acquisition pipeline health for formats
at Gate 3 and below, and verifies the spec-cache completeness for existing
formats at Gate 4+.

---

## Acquisition Status Verification

### Formats at Gate 3 (verified current, no regression)

| Format | Gate | Sprint | Notes |
|--------|------|--------|-------|
| XPM | Gate 3 | R30 | samples verified, awaiting Gate 4 parser |
| PAM | Gate 3 | R30 | samples verified, awaiting Gate 4 parser |
| CSV | Gate 7 | R59 | advanced in R59 Train H |
| TSV | Gate 7 | R59 | advanced in R59 Train J |

### Formats at Gate 10 (RC ready, verified)

| Format | Gate | Sprint | Package |
|--------|------|--------|---------|
| FODS | Gate 10 | R46 | in package matrix |
| FODT | Gate 10 | R46 | in package matrix |
| ZST | Gate 10 | R31 | in package matrix |
| ABW | Gate 10 | R31 | in package matrix |
| FODP | Gate 10 | R31 | in package matrix |
| FODG | Gate 10 | R31 | in package matrix |
| Gnumeric | Gate 10 | R31 | in package matrix |
| PGM | Gate 10 | R59 | in package matrix |
| PBM | Gate 10 | R59 | in package matrix |
| SYLK | Gate 10 | R59 | in package matrix |

### Gate 10 formats with Gate 10 in pack.yaml but not yet packaged

| Format | Gate | Notes |
|--------|------|-------|
| DIF | Gate 10 | pack.yaml has gate_10; not in package matrix yet |
| PPM | Gate 10 | pack.yaml has gate_10; not in package matrix yet |

These are honest: gate_10 in pack.yaml reflects local RC status, not wheel availability.
DIF/PPM can be added to package matrix in a future sprint.

---

## Spec-Cache Verification

Spec-cache confirmed present and current for formats with Gate 4+ parsers:
- src/python/fods/, fodt/, zst/, abw/, fodp/, fodg/, gnumeric/, pgm/, pbm/, sylk/
- src/python/csv/, tsv/, dif/, ppm/, ods/, odt/, qoi/, xcf/, pgm/, pbm/

No stale spec-cache entries detected.

---

## Deferred to R61

- XPM Gate 4 parser implementation (basic probe + neutral model)
- PAM Gate 4 parser implementation
- DIF/PPM addition to package matrix

---

**TRAIN_J_COMPLETE — Acquisition pipeline health verified; Gate 3+ formats accounted for.**
