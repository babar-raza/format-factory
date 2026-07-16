---
version: "1.0"
last-updated: "2026-07-16"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "idempotent"
loc_budget: "tools/format_contract/contract_validator.py (~230 lines)"
test_path: "tests/format_contract/test_determinism_foundation.py"
risk_level: LOW
created-by: TC-FCL-020
product_track: format_contract
---

# /validate-format-contract

Run the blocking check set over a compiled format contract. Read-only over
contract bodies; the JSON report is the evidence artifact.

Checks (mapped to governance validators V232-V241):
schema validity · provenance closure (every capability cites resolvable
SAL-/RF-/POL- ids) · depth completeness vs family floors · shallow-language
blocklist · capability-ID pattern/uniqueness · MUST test/gate completeness ·
input-digest freshness · family adequacy (all pack domains present, simplicity
budget kept).

## Execution

```
.venv/Scripts/python tools/format_contract/contract_validator.py --format-id <fmt>
```

Or `--contract-path <path>` for a not-yet-committed document.
`--skip <name,...>` skips named checks (evidence must record why).

## Mandatory Validations

- **all_checks_reported**: report lists every check with PASS/FAIL and items
- **exit_nonzero_on_fail**: any FAIL -> exit 1 (blocking)
- **read_only**: no file under `shared/format-contracts/` is modified

## Required Inputs

| Field | Description |
|---|---|
| `format_id` | Lowercase format id (or `contract_path` for ad-hoc documents) |

## Allowed Paths

- `shared/format-contracts/**` (read), `schemas/format-contracts/**` (read)
- `shared/sal-facts/**`, `shared/format-contracts/policy/**` (read — provenance resolution)

## Forbidden Paths

- `src/python/**`, `src/net/**`
- Any write to contract bodies or policy stores

## Stop Conditions

- FAIL verdict: stop; route to the owning repair (schema/provenance -> compiler
  or stores; freshness -> `/compile-format-contract --check` investigation)

## Output Format

JSON report `{verdict, checks: [{check, result, items}]}` on stdout.

## Idempotency Contract

Same contract + same stores -> identical report. No state mutation.
