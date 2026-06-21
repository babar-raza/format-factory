# Lane Separation and Collision Risk — Format Factory Machinery Audit v2
# Sprint ID: ff-machinery-readiness-audit-v2-20260621-827f5a52

## Current Lane Architecture

### What exists:
- `.local/supervisor/session-machinery.id` — machinery session identity file
- `.local/supervisor/session-product.id` — product session identity file
- `continuation-signal.json` has `track_type` field (added in sprint repairs)
- `active-plan-lock.json` has `track_type: product` (GAP-WF-004 fix)

### What does NOT exist:
- Separate machinery work queue (machine has one action-queue shared with product)
- Separate ledger files per lane
- File ownership enforcement (no tool blocks product skill from modifying machinery file)
- Separate evidence bundles per lane
- Separate stop/resume rules per lane
- Coordinator agent routing requests to correct lane

## Lane Boundary Map

| Component | Expected Lane | Actual Enforcement |
|-----------|--------------|-------------------|
| src/python/{format}/ | Product | NONE — any agent can modify |
| src/net/{format}/ | Product | NONE |
| tools/supervisor/ | Machinery | NONE |
| tools/specification-authority-layer/ | Machinery | NONE |
| registry/ | Shared (read-mostly) | NONE |
| tests/python/ | Product | NONE |
| tests/supervisor/ | Machinery | NONE |
| reports/supervisor/ | Supervisor output | Generated, not edited |
| .local/supervisor/ | Supervisor state | Modified by any sprint |

## Shared File Risk Map

| File | Risk | Collision Scenario |
|------|------|-------------------|
| registry/source-structure-baseline.json | MEDIUM | Machinery sprint updates cap; product sprint uses stale cap |
| .local/supervisor/continuation-signal.json | MEDIUM | Both lanes write signal; one overwrites other |
| reports/capability-layer/gap-ledger.json | HIGH | Machinery closes gaps that product sprint hasn't implemented |
| .supervisor/skill-registry.yaml | MEDIUM | Machinery adds skill; product sprint uses old registry |
| tools/supervisor/governance_validators.py | HIGH | Machinery adds validator that BREAKS in-progress product sprint |

## Contamination/Collision Risk Matrix

| Risk | Severity | Likelihood | Current Control |
|------|---------|-----------|----------------|
| Machinery sprint breaks product tests | HIGH | MEDIUM | V35 (monolith) only |
| Product sprint corrupts machinery state | HIGH | MEDIUM | NONE |
| Both tracks write continuation signal simultaneously | CRITICAL | LOW (single agent) | NONE |
| Backfill sprint migrates product files while product sprint adds to them | CRITICAL | LOW (sequential) | NONE |
| Gap ledger shows closed when product code not actually there | HIGH | HIGH (932 closed) | NONE |
| Stale plan lock from machinery track blocks product track | MEDIUM | LOW | track_type field (partial) |

## Current Risk Assessment

For the current operational pattern (single agent, sequential sprints, no backfill):
- **Actual collision risk: LOW** — the agent runs one sprint at a time
- **Theoretical risk from concurrent access: HIGH** — but not exercised currently

For the planned future (headless daemon + product + machinery separate tracks):
- **Collision risk: CRITICAL** — shared state files, no ownership, no locking

## Required Guardrails (NOT YET IMPLEMENTED)

1. File ownership manifest: each file tagged to a lane
2. Machinery sprint cannot write src/python/ or src/net/
3. Product sprint cannot write tools/supervisor/ or tools/specification-authority-layer/
4. Backfill sprint gets exclusive lock on migrating files
5. Separate continuation signals per lane (product-signal.json, machinery-signal.json)
6. Separate gap ledgers per lane

## Practical Recommendation

For the immediate next product-deepening sprint:
- Run sequentially (no concurrent lanes) — collision risk is LOW
- Do not start machinery repairs and product deepening in the same sprint
- If backfill is started, FREEZE product deepening for the affected format
