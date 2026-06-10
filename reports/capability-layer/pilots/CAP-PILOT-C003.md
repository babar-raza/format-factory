# Pilot Report: CAP-PILOT-C003

**Format**: Netpbm  
**Product Type**: commercial  
**Verdict**: PASS_WITH_LIMITATIONS  
**Generated**: 2026-06-08T06:26:17.598368+00:00  
**Run ID**: capability-feature-understanding-layer-healing-20260608-e382e5f

## Authority Inputs

- product-capability-matrix/poc-targets.yaml (commercial_net_products.Netpbm)
- Gate 11 G11-G approval by Babar Raza 2026-06-05

## Inspected

- Source files: src/net/netpbm/
- Test files: 50
- Examples: examples/net/netpbm/ (3 files)

## Generated Records

- Count: 25
- Sample: load, save_same_format, parse_pbm, parse_pgm, parse_ppm

## Gaps Found

0 gaps. All expected capabilities implemented

## Validator Result

Exit code: 2 - PASS advisory warnings only

## Test Result

465 pass / 0 fail

## Contradictions

- LIMITATION: poc-targets.yaml Netpbm Python FOSS split into pbm/pgm/ppm packages

## Final Verdict

**PASS_WITH_LIMITATIONS**

Commercial Netpbm verified at Gate 11. Python FOSS naming limitation documented.
