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

## Required Inputs

- `layer_id` — layer identifier from the permanent layer plan
- `canonical_slug` — value for `canonical_slug`
- `canonical_name` — value for `canonical_name`
- `maturity_current` — value for `maturity_current`
- `maturity_target` — value for `maturity_target`
- `status` — value for `status`
- `dependencies` — value for `dependencies`

## Allowed Paths

- `plans/layers/`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no product source mutation
- `src/python/**` — no product source mutation
- `plans/strategic/**` — strategic plans are read-only
- `.supervisor/skill-registry.yaml` — skill registry is read-only here

## Stop Conditions

- Stop if the skill's mandatory validations cannot be completed
- Stop if any required input field is missing or invalid

## Output Format

- Layer task register updated with the result of this operation
- Work log entry appended to the permanent layer plan
- Structured verdict: PASS / FAIL with supporting evidence
