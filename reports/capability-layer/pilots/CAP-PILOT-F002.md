# Pilot Report: CAP-PILOT-F002

**Format**: Gnumeric  
**Product Type**: foss_reduced  
**Verdict**: PASS_VERIFIED  
**Generated**: 2026-06-22T08:06:54.560239+00:00  
**Run ID**: capability-layer-healing-20260621-329b910

## Authority Inputs

- product-capability-matrix/poc-targets.yaml (foss_reduced_products.Gnumeric)
- acquisition-packs/gnumeric/pack.yaml

## Inspected

- Source files: src/python/gnumeric/gnumeric_codec.py
- Test files: 7
- Examples: None

## Generated Records

- Count: 23
- Sample: load, probe_gnumeric, create_gnumeric, write_gnumeric, export_to_csv, export_to_json, get_sheet_names, get_cell_value, set_cell_value

## Gaps Found

0 gaps. All expected capabilities present

## Validator Result

Exit code: 2 - PASS advisory warnings only

## Test Result

189 pass / 0 fail

## Contradictions

- Plan said set_cell_value needed implementing - already present since R123

## Final Verdict

**PASS_VERIFIED**

Gnumeric FOSS fully implemented. set_cell_value already present (DEC-001). 189 tests pass.
