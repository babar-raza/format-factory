# Governance Validator Pilot Results
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-LAYER-HARDENING-PILOTS-001
# Lane: H (GRH-TC-010)
# Date: 2026-06-08
# Status: ALL 6 PILOTS PASS

## Summary

| Pilot | Description | Expected | Actual | Verdict |
|-------|-------------|----------|--------|---------|
| PILOT-001 | PRODUCT_SOURCE missing execution_method | FAIL | FAIL | PASS |
| PILOT-002 | MANUAL_UNGOVERNED without LEGACY_BACKFILLED | FAIL | FAIL | PASS |
| PILOT-003 | REPLAYABLE claim without replay_recipe_path | FAIL | FAIL | PASS |
| PILOT-004 | PRODUCT_SOURCE DISCOVERED→GOVERNANCE_ACCEPTED (forbidden) | FAIL | FAIL | PASS |
| PILOT-005 | Properly formed legacy backfill | PASS | PASS | PASS |
| PILOT-006 | GOVERNANCE_DOC short-circuit path | PASS | PASS | PASS |

All 21 pilot tests pass. All validators behave correctly for their targeted scenarios.

## Pilot Details

### PILOT-001: execution_method_required_validator — Negative

Fixture: `tests/supervisor/fixtures/governance-pilots/pilot-001-execution-method-missing.yaml`

Scenario: A `PRODUCT_SOURCE` work item with no `execution_method` field declared.

Expected behavior:
- `validate_execution_method_required` returns `result=FAIL`
- `blocks_sprint=True`
- Item `PILOT-001-TC-001` identified in fail list

Result: **PASS** (validator behaves correctly)

Significance: Confirms the execution_method field cannot be silently omitted. Any sprint
declaring PRODUCT_SOURCE work items without execution_method will be blocked.

---

### PILOT-002: manual_ungoverned_rejection_validator — Negative

Fixture: `tests/supervisor/fixtures/governance-pilots/pilot-002-queue-declared-deprecated.yaml`

Scenario: A `PRODUCT_SOURCE` item with `execution_method=MANUAL_UNGOVERNED` and
`claim_classification=WORKS_BUT_NOT_REPEATABLE` (not LEGACY_BACKFILLED).

Expected behavior:
- `validate_manual_ungoverned_rejection` returns `result=FAIL`
- `blocks_sprint=True`

Result: **PASS** (validator behaves correctly)

Significance: MANUAL_UNGOVERNED may not close a product taskcard unless the claim is
LEGACY_BACKFILLED (documenting backfill intent). This prevents post-hoc justification
of untracked code changes.

---

### PILOT-003: replay_recipe_required_validator — Negative

Fixture: `tests/supervisor/fixtures/governance-pilots/pilot-003-replayable-claim-without-recipe.yaml`

Scenario: A `PRODUCT_SOURCE` item claims `REPLAYABLE_NOT_YET_REPLAYED` but has no
`replay_recipe_path` artifact.

Expected behavior:
- `validate_replay_recipe_required` returns `result=FAIL`
- `blocks_sprint=True`
- Fail message references REPLAYABLE/replay_recipe

Result: **PASS** (validator behaves correctly)

Significance: Repeatability claims are enforced — you cannot claim REPLAYABLE without
providing a replay recipe path. This prevents inflation of repeatability status.

---

### PILOT-004: taskcard_state_transitions_validator — Negative

Fixture: `tests/supervisor/fixtures/governance-pilots/pilot-004-forbidden-state-jump.yaml`

Scenario: A `PRODUCT_SOURCE` item jumps from `DISCOVERED` directly to
`GOVERNANCE_ACCEPTED` — a forbidden transition for product source items.

Expected behavior:
- `validate_taskcard_state_transitions` returns `result=FAIL`
- Fail message contains "FORBIDDEN"

Result: **PASS** (validator behaves correctly)

Significance: PRODUCT_SOURCE items must traverse the full state machine path through
DIFF_CAPTURED and VALIDATED before GOVERNANCE_ACCEPTED. The shortcut path is only
available to GOVERNANCE_DOC items.

---

### PILOT-005: Legacy Backfill — Positive

Fixture: `tests/supervisor/fixtures/governance-pilots/pilot-005-legacy-backfill-accepted.yaml`

Scenario: A properly formed `LEGACY_BACKFILL_METADATA` item with:
- `execution_method: BACKFILLED_LEGACY_EXECUTION`
- `claim_classification: LEGACY_BACKFILLED`
- `exception_classification: legacy_backfill`
- 64-char hex `idempotency_key`
- `sidecar_attribution_path` present
- State transition `EVIDENCE_LOCATED → BACKFILLED_LEGACY_ACCEPTED`

Expected behavior: All relevant validators PASS (no FAIL results).

Result: **PASS** (all validators behave correctly)

Validators tested:
- `execute_method_required` → PASS (method present)
- `claim_classification` → PASS (LEGACY_BACKFILLED is valid)
- `taskcard_state_transitions` → PASS (EVIDENCE_LOCATED→BACKFILLED_LEGACY_ACCEPTED is valid)
- `replay_recipe_required` → PASS (not required for LEGACY_BACKFILLED)
- `manual_ungoverned_rejection` → PASS (BACKFILLED_LEGACY_EXECUTION is not MANUAL_UNGOVERNED)

Significance: Confirms that a correctly documented legacy backfill clears all validator
gates. This is the expected path for the 4 autonomous-execution-spine functions.

---

### PILOT-006: GOVERNANCE_DOC Short-Circuit — Positive

Fixture: `tests/supervisor/fixtures/governance-pilots/pilot-006-governance-doc-short-circuit.yaml`

Scenario: A `GOVERNANCE_DOC` item with `exception_classification=investigation_only`
uses the `DISCOVERED → GOVERNANCE_ACCEPTED` transition — which is forbidden for
PRODUCT_SOURCE but valid for governance documentation.

Expected behavior:
- `validate_taskcard_state_transitions` returns PASS or WARN (not FAIL)
- `_has_explicit_exemption()` returns True for this item

Result: **PASS** (validators correctly distinguish GOVERNANCE_DOC from PRODUCT_SOURCE)

Significance: The state machine short-circuit restriction only applies to product source
items. Governance docs (investigations, contracts, schemas) legitimately jump from
DISCOVERED to GOVERNANCE_ACCEPTED without traversing mutation-specific states.

---

## Key Design Decisions Verified by Pilots

1. **Execution method required** — PRODUCT_SOURCE items without execution_method block
   the sprint immediately (Validator 1). No grace.

2. **MANUAL_UNGOVERNED gated** — allowed only with LEGACY_BACKFILLED claim (backfill
   intent documented). All other claims with MANUAL_UNGOVERNED are rejected (Validator 7).

3. **Repeatability inflation prevented** — REPLAYABLE_* claims require proof via
   replay_recipe_path. Claiming REPLAYABLE without a recipe path blocks sprint (Validator 4).

4. **State machine enforced for product items only** — PRODUCT_SOURCE items cannot jump
   DISCOVERED→GOVERNANCE_ACCEPTED. GOVERNANCE_DOC items can. The distinction is correct
   and tested (Validator 10).

5. **Legacy backfill is well-behaved** — all 4 backfilled functions (set_cell_value,
   get_headers, get_paragraph, export_to_csv) follow the path that passes all validators
   (LEGACY_BACKFILL_METADATA + EVIDENCE_LOCATED→BACKFILLED_LEGACY_ACCEPTED).

## Test Execution

Run: `pytest tests/supervisor/test_governance_pilots.py -v`
Expected: 21 passed, 0 failed

Actual result from 2026-06-08 run: **21 passed, 0 failed, in 0.91s**
