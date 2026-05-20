# R35 Probe Format Gate Correction Report

**Sprint:** R35
**Date:** 2026-05-20

## Gate Corrections Applied (Lane C)

| Format | Previous Claimed | Evidence-Backed | Maturity | Pack.yaml Updated |
|--------|-----------------|-----------------|----------|-------------------|
| FODP | G10 (verified) | G4 | probe_only | YES — gate_correction section |
| FODG | G10 (verified) | G4 | probe_only | YES — gate_correction section |
| Gnumeric | G10 (verified) | G4 | probe_only | YES — gate_correction section |
| ABW | G10 (verified) | G4 | probe_only | YES — gate_correction section |

All corrections preserve historical gate records (G1-G3 entries unchanged). `gate_correction` section added with:
- `previous_claimed_gate`
- `evidence_backed_gate`
- `maturity_class`
- `correction_reason`
- `correction_artifact`
- `next_action: deepen_or_quarantine`

## Scope Finalizations Applied (Lane D)

| Format | Scope | Binary Status | Pack.yaml Updated |
|--------|-------|---------------|-------------------|
| XCF | header_and_metadata_only | pixel decode not implemented | YES — scope_finalization |
| PPM | read_only_ascii_p3 | P6 not implemented | YES — scope_finalization |
| PGM | read_only_ascii_p2 | P5 not implemented | YES — scope_finalization |
| PBM | read_only_ascii_p1 | P4 not implemented | YES — scope_finalization |

## DRIFT Taskcard Status

| Taskcard | R33 Status | R35 Status |
|----------|-----------|-----------|
| DRIFT-FODP | GATE_CORRECTION_REQUIRED | CORRECTED_CLOSED |
| DRIFT-FODG | GATE_CORRECTION_REQUIRED | CORRECTED_CLOSED |
| DRIFT-GNUMERIC | GATE_CORRECTION_REQUIRED | CORRECTED_CLOSED |
| DRIFT-ABW | GATE_CORRECTION_REQUIRED | CORRECTED_CLOSED |
| DRIFT-XCF | DEEPENING_REQUIRED | SCOPE_FINALIZED |
| DRIFT-PPM | READ_ONLY_SCOPE_APPROVED | SCOPE_FINALIZED |
| DRIFT-PGM-PBM | CURRENT_GATE_SUPPORTED | SCOPE_FINALIZED |
