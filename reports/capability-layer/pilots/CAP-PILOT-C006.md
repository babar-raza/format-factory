# Pilot Report: CAP-PILOT-C006

**Format**: Netpbm  
**Product Type**: commercial  
**Verdict**: PASS_WITH_LIMITATIONS  
**Generated**: 2026-06-22T08:06:54.560239+00:00  
**Run ID**: capability-layer-healing-20260621-329b910

## Authority Inputs

- product-capability-matrix/poc-targets.yaml (commercial_net_products.Netpbm)
- reports/capability-layer/unified-capability-map.json (sprint CAPABILITY-LAYER-HEALING-20260621-ed51041)
- Gate 11 G11-G approval by Babar Raza 2026-06-05 (inherited from C003)

## Inspected

- Source files: src/python/netpbm/, src/net/netpbm/
- Test files: 90
- Examples: None

## Generated Records

- Count: 25
- Sample: load, probe_netpbm, parse_pbm, parse_pgm, parse_ppm, write_netpbm

## Gaps Found

0 gaps. Netpbm commercial records present in unified map

## Validator Result

Exit code: 2 - PASS advisory warnings only

## Test Result

90 pass / 0 fail

## Contradictions

- LIMITATION: Python Netpbm split into pbm/pgm/ppm packages — naming mismatch with commercial unified format ID

## Final Verdict

**PASS_WITH_LIMITATIONS**

Netpbm commercial records current. 90 Python tests pass. Python sub-package split limitation inherited from C003.
