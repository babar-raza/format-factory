---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /identify-primary-layer

Given a task or work item, identify the primary layer that owns it and return the
permanent layer plan path from `plans/layers/`.

## Handoff Fields (required)

| Field | Description |
|---|---|
| `task_id` | Task or work item ID to classify |
| `work_type` | Type of work (e.g., PRODUCT_SOURCE, GOVERNANCE, SAL_INGESTION) |
| `changed_paths` | List of file paths being modified |

## Execution

1. Read `plans/layers/index.yaml` to load all layer definitions
2. Match `changed_paths` prefixes to each layer's `owned_paths`
3. If multiple layers match, use the layer with the most specific path match
4. Return `layer_id`, `canonical_slug`, and `permanent_plan_path`

## Output

```yaml
primary_layer_id: L06
canonical_slug: product-architecture-layer
permanent_plan_path: plans/layers/product-architecture-layer.md
confidence: HIGH
rationale: "changed_paths includes src/python/ — owned by L06"
```

## Mandatory Validations

- `layer_plan_exists`: `permanent_plan_path` must exist on disk
- `layer_in_index`: `layer_id` must appear in `plans/layers/index.yaml`
