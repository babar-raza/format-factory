# Pilot Report: CAP-PILOT-A002

**Format**: QOI  
**Product Type**: foss_reduced  
**Verdict**: PASS_WITH_LIMITATIONS  
**Generated**: 2026-06-21T17:09:20.897325+00:00  
**Run ID**: capability-layer-healing-20260621-ed51041

## Authority Inputs

- reports/capability-layer/foss-reduced-capability-map.json (source scan discovery)
- tests/python/qoi/ (545 passing tests discovered)

## Inspected

- Source files: src/python/qoi/
- Test files: 545
- Examples: None

## Generated Records

- Count: 8
- Sample: load_qoi, probe_qoi, decode_qoi, encode_qoi, get_dimensions, export_to_png

## Gaps Found

2 gaps. 2 QOI functions detected missing dedicated test functions via AST scan

## Validator Result

Exit code: 2 - PASS advisory warnings only

## Test Result

545 pass / 0 fail

## Contradictions

- LIMITATION: QOI not in poc-targets.yaml foss_reduced_products despite being implemented
- LIMITATION: 32 collection errors in analytics stub files (suspended rotation)

## Final Verdict

**PASS_WITH_LIMITATIONS**

QOI FOSS implemented with 545 passing tests. Not yet in poc-targets.yaml. Acquisition formalization needed. Analytics stubs from suspended rotation cause collection errors.
