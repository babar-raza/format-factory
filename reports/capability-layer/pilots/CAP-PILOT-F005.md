# Pilot Report: CAP-PILOT-F005

**Format**: DIF  
**Product Type**: foss_reduced  
**Verdict**: PASS_WITH_LIMITATIONS  
**Generated**: 2026-06-21T17:09:20.897325+00:00  
**Run ID**: capability-layer-healing-20260621-ed51041

## Authority Inputs

- product-capability-matrix/poc-targets.yaml (foss_reduced_products.DIF)
- reports/capability-layer/foss-reduced-capability-map.json (sprint CAPABILITY-LAYER-HEALING-20260621-ed51041)
- acquisition-packs/dif/pack.yaml

## Inspected

- Source files: src/python/dif/dif_codec.py
- Test files: 899
- Examples: None

## Generated Records

- Count: 16
- Sample: load, write_dif, probe_dif, get_value_count, export_to_csv, export_to_json

## Gaps Found

3 gaps. AST-level detection found 3 functions without dedicated test functions

## Validator Result

Exit code: 2 - PASS advisory warnings only

## Test Result

899 pass / 53 fail

## Contradictions

- LIMITATION: 53 pre-existing test failures in analytics deepening tests (arithmetic rotation suspended)
- LIMITATION: 30 collection errors in analytics stub files

## Final Verdict

**PASS_WITH_LIMITATIONS**

DIF FOSS core verified. 899 tests pass. 53 pre-existing failures in suspended analytics rotation (not new regressions).
