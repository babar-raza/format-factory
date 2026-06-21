# Pilot Report: CAP-PILOT-F006

**Format**: ZST  
**Product Type**: foss_reduced  
**Verdict**: PASS_VERIFIED  
**Generated**: 2026-06-21T17:09:20.897325+00:00  
**Run ID**: capability-layer-healing-20260621-ed51041

## Authority Inputs

- product-capability-matrix/poc-targets.yaml (foss_reduced_products.ZST)
- reports/capability-layer/foss-reduced-capability-map.json (sprint CAPABILITY-LAYER-HEALING-20260621-ed51041)
- acquisition-packs/zst/pack.yaml

## Inspected

- Source files: src/python/zst/zst_codec.py, src/python/zst/zst_analytics.py
- Test files: 4149
- Examples: None

## Generated Records

- Count: 32
- Sample: load, write_zst, probe_zst, compress, decompress, get_compression_ratio, analyze_entropy

## Gaps Found

0 gaps. All ZST FOSS capabilities verified in current map

## Validator Result

Exit code: 2 - PASS advisory warnings only

## Test Result

4149 pass / 0 fail

## Contradictions

None

## Final Verdict

**PASS_VERIFIED**

ZST FOSS fully implemented. 4149 tests pass. Analytics extracted. 32 public functions.
