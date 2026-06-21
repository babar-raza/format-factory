# Pilot Report: CAP-PILOT-F003

**Format**: NDJSON  
**Product Type**: foss_reduced  
**Verdict**: PASS_WITH_LIMITATIONS  
**Generated**: 2026-06-21T17:09:20.897325+00:00  
**Run ID**: capability-layer-healing-20260621-ed51041

## Authority Inputs

- reports/capability-layer/foss-reduced-capability-map.json (source scan discovery)

## Inspected

- Source files: src/python/ndjson/ndjson_codec.py
- Test files: 4
- Examples: None

## Generated Records

- Count: 12
- Sample: load_ndjson, probe_ndjson, get_record_count, get_field_names, write_ndjson, append_record, filter_records, export_to_csv

## Gaps Found

1 gaps. NDJSON not in poc-targets.yaml foss_reduced_products

## Validator Result

Exit code: 2 - PASS advisory warnings only

## Test Result

32 pass / 0 fail

## Contradictions

- NDJSON not in poc-targets.yaml foss_reduced_products despite being implemented

## Final Verdict

**PASS_WITH_LIMITATIONS**

NDJSON FOSS implemented with 12 functions, 4 test files. poc-targets.yaml needs updating (CAP-PROD-005).
