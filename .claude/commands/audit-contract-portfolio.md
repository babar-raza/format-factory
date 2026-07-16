---
version: "1.0"
last-updated: "2026-07-16"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "idempotent"
loc_budget: "tools/format_contract/staleness_checker.py + contract_registry.py readers"
test_path: "tests/format_contract/"
risk_level: LOW
created-by: TC-FCL-080
product_track: format_contract
---

# /audit-contract-portfolio

Portfolio-wide contract audit answering the supervisor's state questions:
which formats lack contracts, which are stale/blocked/shallow/unverified,
which capabilities are claimed without proof, and what runs next.

## Execution steps

1. `.venv/Scripts/python tools/format_contract/staleness_checker.py` — refresh
   healing conditions and repair tasks
2. Read `registry/format-contract-registry.yaml` + `.local/supervisor/contract-repair-tasks.json`
3. Produce the portfolio table: per format — state, readiness, quality score/verdict,
   review verdict, capability count, gap count, freshness
4. Write `reports/format-contract-layer/portfolio-audit.json` with the table +
   counts by state + next-action queue ordered by (BLOCKED first for seeding,
   then NO_CONTRACT by family readiness, then STALE, then SHALLOW)

## Mandatory Validations

- **counts_reconcile**: table totals match registry entry count + family-map coverage
- **no_silent_caps**: formats excluded from audit are listed with reasons, never dropped

## Required Inputs

None (portfolio-wide).

## Allowed Paths

- reports/format-contract-layer/portfolio-audit.json (write); registry + L30 stores (read)

## Forbidden Paths

- src/**; any contract body write

## Stop Conditions

- None (audit is data; findings route to owning skills)

## Output Format

portfolio-audit.json + stdout summary (totals by state, next actions).

## Idempotency Contract

Same repo state -> same audit content (timestamps only in volatile fields).
