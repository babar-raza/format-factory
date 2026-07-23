---
version: "1.0"
last-updated: "2026-07-16"
phase-available: "all"
gate-required: null
skill_type: PIPELINE_TOOL
idempotency: "idempotent"
loc_budget: "tools/format_contract/contract_compiler.py (~430 lines, shared with --check/--verify-idempotency harness)"
test_path: "tests/format_contract/test_determinism_foundation.py"
risk_level: MEDIUM
created-by: TC-FCL-020
product_track: format_contract
---

# /compile-format-contract

Compile the canonical developer-product contract for one format
(`shared/format-contracts/{format_id}.yaml`) from committed hash-bound stores:
SAL facts + research findings + family pack + shared library contract.

This is the ONLY governed writer of contract bodies. Hand-editing a contract
is detected by the V240 hand-edit guard (input digests cannot be reproduced).
The compiler is deterministic: same committed inputs produce byte-identical
output. The reference contract file under `plans/from_chat/` is DENYLISTED as
an input (DEC-038: comparison oracle only).

## Prerequisites

1. Format present in `shared/format-contracts/policy/format-family-map.yaml`
2. Family pack exists at `shared/format-contracts/policy/family-packs/{family}.yaml`
3. SAL fact store exists at `shared/sal-facts/{format_id}.yaml`
4. Readiness gate passes (fact-category coverage >= family threshold) — thin
   stores yield exit 2 BLOCKED_NEEDS_AUTHORITY, never a fabricated contract

## Execution

```
.venv/Scripts/python tools/format_contract/contract_compiler.py --format-id <fmt>
```

Options: `--readiness-only` (report the gate verdict without compiling),
`--check` (recompile to memory, diff against committed body — exit 3 on drift),
`--verify-idempotency` (compile twice, byte-compare).

## Mandatory Validations

- **readiness_gate_enforced**: exit 2 + registry `BLOCKED_NEEDS_AUTHORITY` entry
  with named missing categories when coverage < threshold
- **deterministic_output**: `--verify-idempotency` passes
- **registry_updated**: `registry/format-contract-registry.yaml` entry carries
  state, readiness score, capability count, and input digests
- **no_product_source_mutation**: never writes under `src/`

## Required Inputs

| Field | Description |
|---|---|
| `format_id` | Lowercase format identifier present in the family map |

## Allowed Paths

- `shared/format-contracts/{format_id}.yaml` (write — compiler only)
- `registry/format-contract-registry.yaml` (write — volatile state)
- `shared/sal-facts/`, `shared/format-contracts/research/`, `shared/format-contracts/policy/` (read)

- `schemas/format-contracts/format-contract.schema.json` (write only for a
  regression-proven, cross-format contract vocabulary)

## Forbidden Paths

- `src/python/**`, `src/net/**` — no product source mutation
- `shared/sal-facts/**` (write) — SAL commits belong to L01
- `plans/from_chat/**` — denylisted comparison oracle (DEC-038)

## Stop Conditions

- Exit 2 (BLOCKED_NEEDS_AUTHORITY): stop and route to SAL/research seeding
  (`/check-contract-sal-readiness`); do NOT lower thresholds to proceed
- Exit 3 (`--check` drift): committed contract does not match inputs — investigate
  hand-edit or stale inputs before any recompile

## Output Format

- Compiled contract path + capability count on stdout
- Registry entry updated with volatile state
- Blocked path: readiness report YAML on stdout naming missing categories

## Idempotency Contract

Same committed inputs -> byte-identical contract body and unchanged registry
semantic state (only `updated_at` moves, and only in the volatile registry).
