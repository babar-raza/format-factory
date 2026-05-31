# R83 Train M — Netpbm Family Advancement

**Sprint:** FORMAT-FACTORY-R83
**Date:** 2026-05-31

## Current State

| Format | Gate Status | Track |
|--------|-------------|-------|
| PGM | Gate 10: local_release_candidate_ready (R59) | Python FOSS |
| PBM | Gate 10: local_release_candidate_ready (R59) | Python FOSS |
| PPM | Gate 7: fuzz complete (R29) | Python FOSS |
| PAM | Gate 3: candidate_approved (R30) | Python FOSS |

## Advancement Decision

**PGM/PBM:** Remain at Gate 10 (local RC). No advancement to Gate 11 in R83.
- G11-G human approval required first for primary formats (FODS/FODT)
- Secondary format advancement blocked until primary gates complete
- Status: HOLD

**PPM:** Gate 7 complete. Gates 8-10 work-ahead available.
- No R83 advancement — primary format completion takes priority
- Status: HOLD

**PAM:** Gates 4-7 work could begin.
- No R83 advancement
- Status: HOLD

## Capability Matrix

See `product-capability-matrix/` for per-format matrices (future: pgm.yaml, pbm.yaml).

## NETPBM_ADVANCEMENT: HOLD_PRIMARY_FORMAT_PRIORITY

