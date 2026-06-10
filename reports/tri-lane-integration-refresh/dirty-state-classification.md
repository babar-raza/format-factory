# Dirty State Classification
# Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001

## Summary
All pre-existing dirty product source files are classified as PRE_EXISTING_PRODUCT_WIP.
No UNSAFE_DIRTY_STATE_REQUIRES_STOP found.

## Product Source Files (Modified Before This Sprint)

| File | Git Status | Classification | Sprint Origin |
|------|-----------|----------------|---------------|
| src/net/fods/FodsDocument.cs | M | PRE_EXISTING_PRODUCT_WIP | R85-R93 |
| src/net/fodt/FodtDocument.cs | M | PRE_EXISTING_PRODUCT_WIP | R85-R93 |
| src/net/netpbm/Model/NetpbmImage.cs | M | PRE_EXISTING_PRODUCT_WIP | R85-R93 |
| src/python/sylk/sylk_parser.py | M | PRE_EXISTING_PRODUCT_WIP | R93 SYLK |

## Classification Rationale

**PRE_EXISTING_PRODUCT_WIP** is assigned (not PRE_EXISTING_UNVERIFIED_SOURCE_CHANGE) because:
- Each file is referenced in reports/r90/product-code-change-ledger.json
- Each file is in the allowed_files list of the prior sprint contracts
- Changes are consistent with prior sprint declared work items (ACCEPTED)
- No evidence of unexpected out-of-scope mutations

## Mainstream Preflight Requirement
Before making new edits to any of these files, Mainstream MUST:
1. Confirm the current file state matches expected state from prior sprint ledger
2. Re-classify if unexpected content is found
3. If re-classification results in UNSAFE_DIRTY_STATE_REQUIRES_STOP, halt and report

## This Sprint's Action
This sprint (integration refresh) does NOT modify these files.
All product source files remain read-only from this sprint's perspective.
