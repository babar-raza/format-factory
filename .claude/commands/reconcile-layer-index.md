---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /reconcile-layer-index

Verify that `plans/layers/index.yaml` is consistent with all layer plan files.
Each layer in index.yaml must have a corresponding `.md` file with matching metadata.
Reports discrepancies without auto-fixing (read-only audit).

## Execution

1. Read `plans/layers/index.yaml`
2. For each layer entry, check that `permanent_plan_path` exists on disk
3. Read each plan file's metadata block — compare `layer_id`, `status`, `maturity_current`
4. Report any mismatches between index.yaml and plan file metadata
5. Report any plan files in `plans/layers/` that are NOT in index.yaml

## Output

```yaml
reconcile_result:
  total_layers: 27
  consistent: 25
  mismatches:
    - layer_id: L03
      field: status
      index_value: ACTIVE
      plan_value: IN_PROGRESS
  missing_from_index:
    - plans/layers/new-layer.md
  missing_plan_files:
    - L28 (in index, no .md file)
```

## Mandatory Validations

- This skill is read-only — no writes occur
- If mismatches found, emit WARN (never FAIL) and list all discrepancies
