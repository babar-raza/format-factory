---
sprint: R92
generated_by: r92-worker
---

# Declaration Schema Hardening (Train D)

Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

## Problem

R91 declaration-only manifest listed only `evidence-declaration.yaml`. Future declarations
need richer per-item evidence so the materializer can fully verify claims.

## Required New Fields (per work item)

```yaml
# New required work item fields
work_item:
  item_id: string
  title: string
  status: completed|partial|not_started|blocked_external_gate
  claim_type: source_change|test_change|report|state_update|supervisor_change|product_capability
  changed_files: [list]
  evidence_paths: [list]
  tests_supporting: [list]
  acceptance_criteria: string
  # NEW:
  validation_commands: [list]     # commands to verify the claim
  raw_log_paths: [list]           # test log files
  capability_matrix_refs: [list]  # poc-targets.yaml entries affected
  product_code_ledger_refs: [list] # ledger entry IDs
  external_gate_refs: [list]       # gate identifiers if blocked
```

## Required New Top-Level Fields

```yaml
declared_artifact_count: integer
declared_changed_file_count: integer
materialization_required: true
package_optional: true
supervisor_should_materialize: true
```

## Implementation Status

- New fields documented here
- `evidence_declaration.py` validator to be updated to check new fields in R93
- For R92: materializer handles both old and new schemas gracefully

## R92 Declaration Compliance

R92 declaration will include `materialization_required: true` and
`supervisor_should_materialize: true` per this hardening.
