---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /create-permanent-layer-plan

Bootstrap a new layer plan file in `plans/layers/` using the 39-section template.
Registers the new layer in `plans/layers/index.yaml` and `plans/layers/change-ledger.jsonl`.

## Handoff Fields (required)

| Field | Description |
|---|---|
| `layer_id` | Layer ID (e.g., L28) — must not already exist in index.yaml |
| `canonical_slug` | Kebab-case slug (e.g., `my-new-layer`) |
| `canonical_name` | Human-readable name |
| `maturity_current` | Current maturity level (0-5) |
| `maturity_target` | Target maturity level (0-5) |
| `status` | Initial status (NOT_ASSESSED / RECON_IN_PROGRESS) |
| `dependencies` | List of upstream layer IDs |

## Execution

1. Check `plans/layers/index.yaml` — confirm layer_id does not already exist
2. Write `plans/layers/<canonical-slug>.md` with full 39-section template
3. Append new layer entry to `plans/layers/index.yaml`
4. Append change entry to `plans/layers/change-ledger.jsonl`

## Mandatory Validations

- `no_duplicate_layer_id`: layer_id must not exist in index.yaml before creation
- `file_written`: plan file must exist on disk after creation
- `index_updated`: layer_id must appear in index.yaml after creation
