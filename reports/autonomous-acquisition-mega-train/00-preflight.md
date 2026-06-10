# Sprint: FORMAT-FACTORY-AUTONOMOUS-FILE-FORMAT-ACQUISITION-MEGA-TRAIN-001

## Package 115 Baseline

- **SHA-256**: `8115d9438e559f4342896433416bc03000854c8f5484f157a98c8a418f582309`
- **Verdict**: `COMPLETE_QUEUE_DRIVEN_PRODUCT_SOURCE_PILOT_PROVEN`
- **Tests**: 44 new pass / 21 pre-existing failures unchanged

## Baseline Queue State

| ID | Type | Status |
|----|------|--------|
| h8-probe-abw-001 | PRODUCT_SOURCE_PATCH_BOUNDED | done |
| h6q-product-001 | PRODUCT_GAP_CLASSIFICATION_READONLY | done |
| h6-q-001 | RUN_JSON_VALIDATION | done |
| h6-q-002 | RUN_MD_NONEMPTY_CHECK | done |
| h6-q-003 | RUN_JSON_VALIDATION | done |
| h6-q-004 | RUN_JSON_VALIDATION | pending |
| h6-q-005 | RUN_JSON_VALIDATION | pending |

## Selected Product Tasks (Mega-Train)

| Task ID | Format | Change | Guard |
|---------|--------|--------|-------|
| h9-gnumeric-probe-001 | Gnumeric | Add probe_gnumeric() | AGENT_OWNED_SAFE |
| h9-gnumeric-write-001 | Gnumeric | Add create_gnumeric() + write_gnumeric() | AGENT_OWNED_SAFE |
| h9-abw-txt-export-001 | ABW | Add export_to_txt() | AGENT_OWNED_SAFE |

## Vertical Slice Target: Gnumeric

After mega-train tasks, Gnumeric will have:
- probe/detect: ✓ (new)
- parse/read: ✓ (existing)
- model/sheets: ✓ (existing)
- create/write: ✓ (new)
- export_to_csv: ✓ (existing)
- roundtrip: ✓ (new tests)

## Hard Rules

- No git commit, push, Gate approval, MCP activation
- All changes via queue-first orchestrator path
- Guard enforces FOSS Python only, no src/net/
