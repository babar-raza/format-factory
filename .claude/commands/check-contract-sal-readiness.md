---
version: "1.0"
last-updated: "2026-07-16"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "idempotent"
loc_budget: "readiness gate inside tools/format_contract/contract_compiler.py (--readiness-only)"
test_path: "tests/format_contract/test_determinism_foundation.py"
risk_level: LOW
created-by: TC-FCL-030
product_track: format_contract
---

# /check-contract-sal-readiness

Score a format's SAL fact-category coverage against its family threshold
(`shared/format-contracts/policy/fact-category-requirements.yaml`) and report
whether contract compilation may run. Readiness is CATEGORY COVERAGE, never
raw fact count — thin stores yield BLOCKED_NEEDS_AUTHORITY with the missing
categories named, which become SAL/research seeding tasks.

## Execution

```
.venv/Scripts/python tools/format_contract/contract_compiler.py --format-id <fmt> --readiness-only
```

Exit 0 ready · exit 2 blocked (registry entry updated with missing categories).

## Mandatory Validations

- **category_report_complete**: every required family category listed with
  matched fact IDs, min_facts, covered flag, weight
- **no_threshold_tampering**: thresholds/min_facts change ONLY via a reviewed
  policy revision in fact-category-requirements.yaml, never inline to unblock
- **read_only_except_registry**: only registry/format-contract-registry.yaml is written

## Required Inputs

| Field | Description |
|---|---|
| `format_id` | Lowercase format identifier in the family map |

## Allowed Paths

- `shared/sal-facts/**` (read), `shared/format-contracts/**` (read)
- `registry/format-contract-registry.yaml` (write — blocked-state record)

## Forbidden Paths

- `src/**`; any write to SAL stores, policy stores, or contract bodies

## Stop Conditions

- Blocked verdict: route to `/research-format-contract-sources` (findings +
  SAL candidates) and the ingest-spec-sal seed path; do NOT compile

## Output Format

Readiness report YAML (categories, score, threshold, missing_categories).

## Idempotency Contract

Same stores -> identical report; registry entry semantically unchanged on rerun.
