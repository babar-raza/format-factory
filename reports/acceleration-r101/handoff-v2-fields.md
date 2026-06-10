# Train E: Execution Handoff Generator v2

## Changes
- Added `implementation_steps`: ordered work steps, work-type-aware (different for product_source_change vs test_only_change vs dogfood_export)
- Added `stop_conditions`: when to abort (test failure, scope exceed, etc.)
- Added `evidence_declaration_entries`: pre-built declaration snippet with item_id, title, status, evidence_paths
- Added `purpose` field: human-readable purpose string
- Added `source_track` field: commercial_dotnet / foss_python / unknown (via classify_source_track)
- Added `raw_logs` field: path to raw log file for this handoff
- Added `product_code_ledger` field: path to product-code-change-ledger.json

## Tests Added (13 new)
- `test_handoff_has_implementation_steps` — present and has >= 3 steps
- `test_handoff_implementation_steps_product` — product type mentions implement + test
- `test_handoff_implementation_steps_test_only` — test type mentions test
- `test_handoff_implementation_steps_dogfood` — dogfood type mentions export
- `test_handoff_has_stop_conditions` — present with >= 2 conditions
- `test_handoff_has_evidence_declaration_entries` — present with sprint ID in item_id
- `test_handoff_has_purpose` — present with format name
- `test_handoff_has_source_track` — commercial_dotnet for commercial_net track
- `test_handoff_source_track_foss` — foss_python for foss_reduced track
- `test_handoff_has_raw_logs` — raw_logs path present
- `test_handoff_has_product_code_ledger` — ledger path present
- `test_handoff_negative_no_extra_fields` — negative: no unexpected keys

## Sample Outputs
- `reports/acceleration-r101/generated-handoffs/handoff-fods-api-merge_sheets.yaml`
- `reports/acceleration-r101/generated-handoffs/handoff-sylk-sylk_to_html.yaml`
