---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /detect-stale-layer-state

Find permanent layer plan files whose §9 (Current Implementation) does not
reflect recent changes to the codebase. A layer file is stale if its implementation
section was last updated before relevant source files were modified.

## Execution

1. Read `plans/layers/index.yaml` — load all layer entries with `owned_paths`
2. For each layer, scan `owned_paths` for recently modified files (git mtime)
3. Compare against `last_updated_at` in the layer plan metadata
4. Report layers where `last_updated_at` predates significant source changes

## Output

```yaml
stale_layers:
  - layer_id: L11
    layer_plan: plans/layers/supervisor-sprint-layer.md
    last_updated: "2026-06-20"
    source_changed_after: "2026-06-26"
    changed_files:
      - tools/supervisor/autonomous_cycle.py
    action: UPDATE_CURRENT_STATE
```

## Mandatory Validations

- This skill is read-only — no writes occur
- Stale detection is advisory only — WARN output, never FAIL

## Required Inputs

- `layer_id` — layer identifier from the permanent layer plan

## Allowed Paths

- `plans/layers/`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no product source mutation
- `src/python/**` — no product source mutation
- `plans/strategic/**` — strategic plans are read-only
- `.supervisor/skill-registry.yaml` — skill registry is read-only here

## Stop Conditions

- Stop if the stale state report file cannot be written
- Stop if the execution would modify any file under src/

## Output Format

- Layer task register updated with the result of this operation
- Work log entry appended to the permanent layer plan
- Structured verdict: PASS / FAIL with supporting evidence
