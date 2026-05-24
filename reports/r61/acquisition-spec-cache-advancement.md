# R61 Train J: Acquisition/Spec-Cache Advancement

**Sprint:** FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
**Date:** 2026-05-24
**Status:** COMPLETE

## CSV Gate 8 Acquisition Update

CSV acquisition pack updated with Gate 8 status:
- `acquisition-packs/csv/pack.yaml` — gate_8.status: pass (R61)
- 18 security adversarial tests (see Train H)

## Format Status Summary

| Format | Highest Gate | Sprint | Notes |
|--------|-------------|--------|-------|
| FODS | Gate 10 | R57 | Python + .NET tracks |
| FODT | Gate 10 | R57 | Python + .NET tracks |
| ZST | Gate 10 | R51 | Gate 5 waived |
| CSV | Gate 8 | R61 | Formula injection adversarial |
| TSV | Gate 7 | R60 | Security regression |
| FODP | Gate 10 | R51 | Python track |
| FODG | Gate 10 | R51 | Python track |
| Gnumeric | Gate 10 | R51 | Python track |
| ABW | Gate 10 | R51 | Python track |
| ODS | Gate 7 | R29 | Awaiting Gate 8 human review |
| ODT | Gate 7 | R29 | Awaiting Gate 8 human review |
| QOI | Gate 7 | R29 | Awaiting Gate 8 human review |
| XCF | Gate 7 | R29 | Awaiting Gate 8 human review |
| DIF | Gate 7 | R29 | 2 pre-existing test failures |
| PPM | Gate 7 | R29 | 2 pre-existing test failures |
| PGM | Gate 3 | R29 | Alpha |
| PBM | Gate 3 | R29 | Alpha |
| SYLK | Gate 3 | R29 | Alpha |

## Deferred

- ODS/ODT/QOI/XCF Gate 8: Awaiting Babar Raza security review sign-off
- ZPAQ: Blocked (ZPAQL VM dependency)
- Gate 11 G11-G: Awaiting commercial approval
