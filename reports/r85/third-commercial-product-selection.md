# R85 Train K — Third Commercial Product Selection

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## Decision

THIRD_COMMERCIAL_TARGET_SELECTED: Netpbm family (PBM/PGM/PPM)

## Candidates Compared

| Factor | QOI | Netpbm (PBM/PGM/PPM) |
|--------|-----|----------------------|
| Python FOSS libraries | Gate 7 (1 format) | Gate 10 RC (3 formats) |
| .NET complexity | Medium (run-length encoding) | Low (text header + pixel array) |
| Family-based dogfooding | No | Yes — PBM→PGM→PPM |
| Load/edit/save feasibility | Medium | Very simple |
| Professional API value | Moderate | Clear (image manipulation) |
| Testability | Medium | Excellent (pixel-level assertions) |
| Spec availability | Public | Public domain (netpbm.sourceforge.net) |

## Selection Rationale

1. Netpbm Python packages (PBM/PGM/PPM) are all at Gate 10 RC — three FF libraries exist
2. .NET load/inspect/save is trivially implementable (simple text header + pixel array)
3. Family-based export (PBM→PGM using FF's own pgm model) is natural dogfooding
4. PBM (1-bit) → PGM (8-bit grayscale) conversion is well-defined
5. Simpler than QOI for .NET first slice (no run-length state machine)

QOI: HOLD — reconsider when Netpbm .NET POC complete; Python Gate 7 already done.

## THIRD_COMMERCIAL_TARGET_SELECTED: NETPBM (PBM/PGM/PPM)
