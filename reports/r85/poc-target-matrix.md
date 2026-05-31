# R85 Train B — POC Target Matrix

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

Authority file: product-capability-matrix/poc-targets.yaml

## Commercial .NET Products (3/3 confirmed)

| # | Format | Load | Edit | Save | Export | Dogfood | Tests | Status |
|---|--------|------|------|------|--------|---------|-------|--------|
| 1 | FODS | PASS | PASS | PASS | CSV+HTML+JSON | PARTIAL | 161 .NET | POC_TARGET_CONFIRMED |
| 2 | FODT | PASS | PASS | PASS | TXT+MD+HTML | PARTIAL | 145 .NET | POC_TARGET_CONFIRMED |
| 3 | Netpbm | R85 | R85 | R85 | R85 | R85 | R85 | POC_TARGET_CONFIRMED |

Notes:
- FODS/FODT: G11-G NOT_STARTED; Gate 11 requires Babar Raza approval
- Netpbm: .NET first slice is R85 deliverable
- Dogfood "PARTIAL" = Python path dogfoods FF libraries; .NET exporters write directly (GAP)

## Reduced/FOSS Python Products (3/3 confirmed)

| # | Format | Load | Edit | Save | Export | Dogfood | Tests | Status |
|---|--------|------|------|------|--------|---------|-------|--------|
| 1 | ZST | PASS | N/A | PASS | N/A | N/A | PASS | POC_TARGET_CONFIRMED |
| 2 | PBM+PGM+PPM | PASS | PARTIAL | PBM+PGM | PBM→PGM (R85) | R85 | PASS | POC_TARGET_CONFIRMED |
| 3 | SYLK | PASS | PARTIAL | READ_ONLY | SYLK→CSV | IMPLEMENTED | PASS | POC_TARGET_CONFIRMED |

Notes:
- ZST: dependency mode = ZST_LOCAL_RC_DEPENDENCY_RESOLUTION_REQUIRED (zstandard PyPI dep)
- Netpbm Python: PPM writer not implemented (R85 scope)
- SYLK: read+export-only scope; no SYLK writer

## On-Hold Candidates

| Format | Reason | Reconsider When |
|--------|--------|----------------|
| QOI | .NET complexity > Netpbm; Python Gate 7 done | After Netpbm .NET POC |
| DIF | Overlaps SYLK | After SYLK POC complete |

## Blockers Summary

| Product | Blocker | Who Unblocks |
|---------|---------|-------------|
| FODS .NET | Gate 11 G11-G approval | Babar Raza |
| FODT .NET | Gate 11 G11-G approval | Babar Raza |
| Netpbm .NET | Not yet implemented | Claude Code (R85) |
| ZST FOSS | Offline zstandard dependency | Build engineering |
| Netpbm FOSS | PBM→PGM dogfood not yet | Claude Code (R85) |
| SYLK FOSS | No SYLK writer (out of scope) | Future sprint |

## TRAIN_B_STATUS: COMPLETE

Files created:
- product-capability-matrix/poc-targets.yaml
- reports/r85/poc-target-matrix.md
