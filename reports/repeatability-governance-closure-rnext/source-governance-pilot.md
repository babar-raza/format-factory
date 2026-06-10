# Source Governance Pilot Report
# Sprint: FORMAT-FACTORY-GOVERNANCE-ENFORCEMENT-CLOSURE-AND-SOURCE-REPLAY-PILOT-001
# Run ID: governance-enforcement-closure-rnext
# Date: 2026-06-09

## Purpose

Demonstrate that the governance layer can validate a complete source-governance evidence chain
without touching any real product source files.

## Pilot Design

Fixture source file: `tests/fixtures/source-governance-pilot/fixture_source.py`
Fixture evidence: `tests/fixtures/source-governance-pilot/fixture-evidence.yaml`

The fixture declares a `PRODUCT_SOURCE` item with a complete governance evidence chain:
- `execution_method: MANUAL_GOVERNED_BY_SKILL`
- `claim_classification: GOVERNED_BUT_NOT_REPLAYED`
- `skill_id: add-python-api`
- `idempotency_key: aaa000...0001`
- `source_diff_paths` declared
- `before_sha256` / `after_sha256` recorded
- `state_machine_start: VALIDATED` → `state_machine_target: GOVERNANCE_ACCEPTED` (valid transition)

## Validator Results

All 10 governance validators ran against the fixture evidence:

| Validator | Result | Notes |
|-----------|--------|-------|
| execution_method_required_validator | PASS | MANUAL_GOVERNED_BY_SKILL valid |
| source_diff_required_validator | PASS | source_diff_paths declared |
| idempotency_key_required_validator | PASS | 64-char hex key present |
| replay_recipe_required_validator | WARN | GOVERNED_BUT_NOT_REPLAYED: no recipe needed |
| claim_classification_validator | PASS | GOVERNED_BUT_NOT_REPLAYED is valid |
| legacy_backfill_validator | PASS | No backfill needed |
| manual_ungoverned_rejection_validator | PASS | Not MANUAL_UNGOVERNED |
| governed_direct_execution_validator | PASS | Skill transcript path present |
| source_marker_or_sidecar_attribution_validator | PASS | Source marker in file |
| taskcard_state_transition_validator | WARN | VALIDATED→GOVERNANCE_ACCEPTED valid; no replay recipe |

**blocks_sprint: False**
**all_pass: True (with 2 WARNs)**

## Conclusion

The governance layer correctly validates a complete evidence chain for a
`MANUAL_GOVERNED_BY_SKILL` product source item. The controlled pilot confirms:

1. A governed item with all required fields passes all validators
2. `GOVERNED_BUT_NOT_REPLAYED` claim with no recipe is WARN (not FAIL) — correct
3. No real product source files were touched
4. The governance validator chain is ready for real product source enforcement

## Next Step for Autonomy Sprint

The autonomy sprint should apply this same evidence chain pattern to all new
product source functions, replacing PATH_ONLY evidence with PIPELINE_VERIFIED.
