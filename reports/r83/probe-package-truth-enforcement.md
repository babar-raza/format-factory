# R83 Train P — Probe Package Truth Enforcement

**Sprint:** FORMAT-FACTORY-R83
**Date:** 2026-05-31

## Overclaim Correction (Sustained from R78)

In R78, a probe overclaim was corrected:
- FODP, FODG, Gnumeric, ABW: removed incorrect "supported" claims
- Actual status: Gate 10 local RC (not Gate 11 complete)
- Commercial product ready: false for all

## Current Probe Truth

| Format | probe() Result | Truth |
|--------|---------------|-------|
| FODS | SUPPORTED | Gate 10 PASS + installed workflow PASS |
| FODT | SUPPORTED | Gate 10 PASS + structural proof PASS |
| ZST | SUPPORTED (dep required) | Gate 10 PASS, zstandard dep required |
| FODP | local_rc_available | Gate 10 only |
| FODG | local_rc_available | Gate 10 only |
| Gnumeric | local_rc_available | Gate 10 only |
| ABW | local_rc_available | Gate 10 only |
| PGM | local_rc_available | Gate 10 only |
| PBM | local_rc_available | Gate 10 only |
| SYLK | local_rc_available | Gate 10 only |

## Package Probe Policy

`probe()` must NOT claim:
- commercial_product_ready: true (for any format currently)
- Gate 11 complete (for any format — G11-G not started)
- PyPI/NuGet available (no publication authorized)

## PROBE_TRUTH: ACCURATE_NO_OVERCLAIM

