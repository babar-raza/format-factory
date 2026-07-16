---
version: "1.0"
last-updated: "2026-07-16"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "idempotent"
loc_budget: "tools/format_contract/contract_reconciler.py"
test_path: "tests/format_contract/"
risk_level: LOW
created-by: TC-FCL-070
product_track: format_contract
---

# /reconcile-contract-capabilities

Reconcile a format's compiled contract against observed implementation (AST/tests/oracle, read-only) producing per-capability observed depth, proof status, and false-claim flags.

## Execution

```
.venv/Scripts/python tools/format_contract/contract_reconciler.py --format-id <fmt>
```

## Mandatory Validations

- **read_only_product_source**: never writes under src/
- **no_contract_body_writes**: contract bodies change only via /compile-format-contract (V240)

## Required Inputs

| Field | Description |
|---|---|
| `format_id` | Lowercase format identifier (portfolio-wide tools accept none) |

## Allowed Paths

- reports/format-contract-layer/{fmt}-reconciliation.json (write)
- shared/format-contracts/** (read), shared/sal-facts/** (read)

## Forbidden Paths

- src/python/**, src/net/**; shared/format-contracts/{fmt}.yaml (write); plans/from_chat/**

## Stop Conditions

- Tool exit non-zero: stop and route per the tool's stderr instruction

## Output Format

- Machine-readable report at the output path above; summary line on stdout

## Idempotency Contract

Same inputs -> same outputs; reruns update in place without duplication.
