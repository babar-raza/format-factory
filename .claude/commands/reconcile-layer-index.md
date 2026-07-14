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
6. For each layer, compare index.yaml's skill_ids array against .supervisor/skill-registry.yaml entries whose product_track plausibly maps to that layer; report additions/removals.

## Output

```yaml
reconcile_result:
  total_layers: 29
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
  skill_id_mismatches:
    - layer_id: L13
      skill_id: reconcile-layer-index
      product_track: layer_governance
      issue: present_in_registry_not_in_index
```

## Mandatory Validations

- This skill is read-only — no writes occur
- If mismatches found, emit WARN (never FAIL) and list all discrepancies

## Required Inputs

- `layer_id` — layer identifier from the permanent layer plan

## Allowed Paths

- `plans/layers/index.yaml`
- `plans/layers/`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no product source mutation
- `src/python/**` — no product source mutation
- `plans/strategic/**` — strategic plans are read-only
- `.supervisor/skill-registry.yaml` — skill registry is read-only here

## Stop Conditions

- Stop if the layer index is inconsistent after reconciliation
- Stop if the execution would modify any file under src/

## Output Format

- PASS / FAIL / PARTIAL verdict printed to stdout
- Per-item findings list with skill_id, issue, and severity
- Report file at `reports/` with structured YAML findings
