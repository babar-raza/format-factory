# Format Factory — Product Governance Healing Plan
# Plan: memoized-frolicking-donut  |  authoritative_plan: plans/.claude/memoized-frolicking-donut.md
# Type: product_governance_healing   |  Mission ID: GOV-HEAL-001
# Version: 3.0 (micro-taskcardized, enforcement-first, corrections applied)
# Created: 2026-07-10  |  Last enhanced: 2026-07-10 (deep code read + full micro-taskcardization)

---

## PLAN AUTHORITY AND PREFLIGHT

```yaml
# artifact: taskcardization-preflight
# authoritative_plan: plans/.claude/memoized-frolicking-donut.md
# artifact_role: preflight_record
# execution_authority: false

preflight:
  repository: c:\Users\prora\OneDrive\Documents\GitHub\format-factory
  branch: main
  active_plan_path: plans/.claude/memoized-frolicking-donut.md
  active_plan_title: "Format Factory Product Governance Healing"
  plan_format: markdown_with_embedded_yaml
  authority_source: plan_mode_conversation_attachment
  approximate_plan_size: "2800+ lines"
  major_section_count: 10
  existing_taskcard_sections: "TC-GOV-001 through TC-GOV-023 (23 parent taskcards)"
  existing_taskcard_format: flat_prose_with_code_blocks
  existing_lanes: [structural_enforcement, schemas, records, tooling, validators, audit, pilots]
  existing_phases: 8
  existing_gates: acceptance_gate_per_taskcard
  existing_state_vocabulary: [OPEN, CLOSED]
  existing_validation_model: pytest_commands_per_taskcard
  existing_evidence_model: test_pass_and_file_existence
  existing_naming_conventions: "TC-GOV-NNN sequential"
  existing_execution_handoff: verification_sequence_at_end
  duplicate_plan_risk: LOW  # only one plan file at this path; prior plan was overwritten

active_plan_authority_verdict:
  verdict: SINGLE_AUTHORITATIVE_PLAN_CONFIRMED
  active_plan: plans/.claude/memoized-frolicking-donut.md
  competing_plans: NONE
  stale_candidates: NONE
  action: ENHANCE_IN_PLACE

duplicate_plan_risk_check:
  risk: LOW
  reason: "Plan file was created fresh; no other memoized-frolicking-donut.md exists"
  supporting_artifacts_created: []
  supporting_artifacts_are_non_authoritative: true
```

---

## CRITICAL CORRECTIONS FROM DEEP CODE READ

**These correct errors in prior plan versions. All taskcards below use the corrected facts.**

### Correction C1 — V119 partially wired but skipped (line 646)

Prior plan assumed V119 was **never called**. Reality: V119 IS imported (line 519) and called (lines 549-566) in `governance_validator_runner.py` with exception handling. **BUT** V119 is also listed in a `skipped_validators` array at line 646, causing its result to be excluded from the final output. The fix is to **remove V119 from the skip list** and add `blocks_sprint: True` to its return dict.

### Correction C2 — V120 signature is different from plan's assumption

Prior plan assumed V120 takes `modified_files` and `promotion_registry`. Reality: V120 expects:
```python
def validate_certification_without_architecture_proof(
    certification_status: str,
    architecture_classification: str,
    product: str = "",
) -> dict
```
V120's wiring requires reading certification state (from `format-registry.yaml`) and architecture classification (from `reports/product-architecture/`), NOT passing `modified_files`. TC-GOV-001-05 and TC-GOV-001-06 address V120 separately after V119.

### Correction C3 — expected_count is 167, not 165

Deep code read confirms: `governance_validator_runner.py` line 813 has `expected_count: 167` (V149 added 2026-07-09). Adding 6 new validators (V150-V155) makes the new target **173**, not 171.

### Correction C4 — Phase 13 already exists (lane scope guard); new git diff is Phase 14

`sprint_executor_validate.py` Phases 1-13 are already defined. Phase 13 = lane scope guard (TC-LSG-007). The new git-diff cross-check must be **Phase 14**.

### Correction C5 — existing_rework_items already in autonomous_cycle.py (line 1874)

`autonomous_cycle.py` line 1874 already loads `existing_rework_items` from the prior signal. TC-GOV-002 must LEVERAGE this existing field rather than inventing a new `prior_rework_items` field.

### Correction C6 — No PROMOTED_STABLE entries in promotion-ledger.yaml

All 6 promotion-ledger.yaml entries are IMPLEMENTATION_VERIFIED or DRAFT — none are PROMOTED_STABLE. V119 would never fire on real data currently. Tests must create synthetic fixtures with PROMOTED_STABLE state. The wiring of V119 is still valuable: once formats reach PROMOTED_STABLE, the enforcement is in place.

---

## PART I: PRESERVED ANALYSIS [PROTECTED — DO NOT MODIFY]

### Diagnosis: What Is Actually Broken

The first-pass analysis identified missing governance *records* (no CP-*, no CI-*, no GA-*). That is real, but it is the symptom, not the root cause.

The root causes are **enforcement gaps in the execution model itself**:

**Root Cause 1 — V119/V120 are defined but effectively skipped by the runner**
`validate_promoted_code_changed_without_reopening` (V119) and `validate_certification_without_architecture_proof` (V120) exist in `governance_validators_ext4.py` with full logic. V119 IS called in `governance_validator_runner.py` (lines 549-566) but is listed in `skipped_validators` (line 646), so its result is excluded from enforcement. The runner never provides V119 its `promotion_registry` input correctly. The `_result()` helper used by V119/V120 does NOT include a `blocks_sprint` field. Result: PROMOTED_STABLE files can be silently modified with zero structural enforcement.

**Root Cause 2 — check_continuation.py ignores 22 of 24 blocking validators**
Of 24 validators marked `blocks_sprint=True`, only 2 (`monolith_detection_validator` and `validate_source_architecture`) are in `_STRUCTURAL_GOVBLOCK_VALIDATORS` (line 518-521). The other 22 add entries to `rework_items` but `check_continuation.py` reads only the 2 structural entries and continues past everything else. V111-V127 can fire every sprint indefinitely — each time added to `rework_items`, each time silently bypassed. This is the core infinite rerun loop.

**Root Cause 3 — The rework classification policy is a dead letter**
`policies.yaml` declares (lines 233-240):
```yaml
critical_grades: [OVERCLAIMED, REJECTED]
autonomous_continue_rule: "critical_rework_count == 0"
```
`check_continuation.py` never reads `critical_grades`, never counts `critical_rework_count`, and never enforces this rule. `autonomous_cycle.py` line 1500-1503 does call `classify_rework_items()` from `autonomous_cycle_extensions` but the result never feeds back into `check_continuation.py`.

**Root Cause 4 — blast-radius-register.yaml is written but never read**
`registry/blast-radius-register.yaml` (1.8 KB) has structured BR-* entries. Zero grep matches for `blast.radius` or `blast_radius` in `tools/supervisor/*.py`. No automation reads it. High-impact changes bypass impact analysis silently.

**Root Cause 5 — Evidence is self-reported with no cross-check**
`sprint_executor_validate.py` has 13 phases (lane scope guard is Phase 13). None compare declared `changed_files` against `git diff --name-only HEAD~1`. A sprint can declare it changed 3 files when it changed 30.

**Root Cause 6 — No pre-flight authority query for artifact lifecycle state**
When a sprint modifies source files, no mechanism queries whether the artifact is PROMOTED or requires a CP-*. The spec-to-feature chain exists as text, not as a machine-queryable enforcement point.

**Root Cause 7 — No governance health signal in the continuation model**
The 22 required governance counters are never computed and never feed into `check_continuation.py`. Governance health is invisible to the autonomous loop.

### What Must Be Preserved

- All 165+ existing validators — large investment, catch real violations. Do not remove or weaken.
- The evidence declaration schema — add fields, do not restructure.
- The continuation model (check_continuation + plan locks) — sound architecture. Fix gaps only.
- The gate system (G1-G11) — correct authority model.
- The skill/capability/SAL/Oracle systems — working correctly.
- `policies.yaml` structure — already has correct declarations. Make them real.
- `existing_rework_items` mechanism in `autonomous_cycle.py` — leverage, don't replace.

### Design: Enforcement-First, Records-Second

Build the enforcement mechanism first. Governance records follow from an enforced workflow, not from manually creating YAML files.

**Tier 1 (Phase 1)** — Structural enforcement repairs: Fix the 5 execution-model gaps. Code changes to existing tools. Must run first; record systems depend on these working.

**Tier 2 (Phases 2-8)** — Governance record system: Schemas, registries, records, tools, pilots, and final report. These become meaningful only because Tier 1 makes them enforced.

---

## PART II: REQUIREMENTS INVENTORY

```yaml
# artifact: normalized-requirements-inventory
# authoritative_plan: plans/.claude/memoized-frolicking-donut.md
# artifact_role: analysis_or_evidence_only
# execution_authority: false

requirements:
  # Phase 1 — Structural enforcement
  - req_id: REQ-STRUCT-001
    description: Remove V119 from skipped_validators list; add blocks_sprint field; wire promotion_registry
    parent_taskcard: TC-GOV-001
    root_cause: RC-1
    plan_section: "Phase 1 / TC-GOV-001"

  - req_id: REQ-STRUCT-002
    description: Fix V120 wiring to match actual signature (certification_status/architecture_classification)
    parent_taskcard: TC-GOV-001
    root_cause: RC-1, C2
    plan_section: "Phase 1 / TC-GOV-001"

  - req_id: REQ-STRUCT-003
    description: Add V119 to _STRUCTURAL_GOVBLOCK_VALIDATORS in check_continuation.py
    parent_taskcard: TC-GOV-001
    root_cause: RC-2
    plan_section: "Phase 1 / TC-GOV-001"

  - req_id: REQ-STRUCT-004
    description: Add Check 8b (persistent violation using existing_rework_items) to check_continuation.py
    parent_taskcard: TC-GOV-002
    root_cause: RC-2
    plan_section: "Phase 1 / TC-GOV-002"

  - req_id: REQ-STRUCT-005
    description: Add persistent_blocking_validators list to policies.yaml
    parent_taskcard: TC-GOV-002
    root_cause: RC-2
    plan_section: "Phase 1 / TC-GOV-002"

  - req_id: REQ-STRUCT-006
    description: Add Check 2b (critical_rework_count) to check_continuation.py; wire from autonomous_cycle.py
    parent_taskcard: TC-GOV-003
    root_cause: RC-3
    plan_section: "Phase 1 / TC-GOV-003"

  - req_id: REQ-STRUCT-007
    description: Wire blast-radius-register.yaml into autonomous_cycle.py Step 0b
    parent_taskcard: TC-GOV-004
    root_cause: RC-4
    plan_section: "Phase 1 / TC-GOV-004"

  - req_id: REQ-STRUCT-008
    description: Add Phase 14 (git diff cross-check) to sprint_executor_validate.py
    parent_taskcard: TC-GOV-005
    root_cause: RC-5
    plan_section: "Phase 1 / TC-GOV-005"

  # Phase 2-3 — Schemas + binding
  - req_id: REQ-SCHEMA-001
    description: 8 new JSON schema files in .supervisor/schemas/
    parent_taskcard: TC-GOV-006
    plan_section: "Phase 2 / TC-GOV-006"

  - req_id: REQ-SCHEMA-002
    description: governance-binding.yaml + validate_governance_binding.py
    parent_taskcard: TC-GOV-007
    plan_section: "Phase 3 / TC-GOV-007"

  - req_id: REQ-SCHEMA-003
    description: governed-artifact-registry.yaml (seed) + governed_artifact_lookup.py
    parent_taskcard: TC-GOV-008
    plan_section: "Phase 3 / TC-GOV-008"

  # Phase 4 — Records
  - req_id: REQ-RECORD-001
    description: 8 retroactive CP/CI/CD YAML record triples for material historical changes
    parent_taskcard: TC-GOV-009
    plan_section: "Phase 4 / TC-GOV-009"

  - req_id: REQ-RECORD-002
    description: promotion-record-ledger.yaml (full-schema) + RC seed records
    parent_taskcard: TC-GOV-010
    plan_section: "Phase 4 / TC-GOV-010"

  # Phase 5 — Tooling
  - req_id: REQ-TOOL-001
    description: change_proposal_manager.py CLI with check-ungoverned-changes
    parent_taskcard: TC-GOV-011
    plan_section: "Phase 5 / TC-GOV-011"

  - req_id: REQ-TOOL-002
    description: governance_promotion_manager.py + governance_release_registry.py
    parent_taskcard: TC-GOV-012
    plan_section: "Phase 5 / TC-GOV-012"

  - req_id: REQ-TOOL-003
    description: governance_counters.py — 22 counters
    parent_taskcard: TC-GOV-013
    plan_section: "Phase 5 / TC-GOV-013"

  - req_id: REQ-TOOL-004
    description: governance_ledger_builder.py — gap inventory
    parent_taskcard: TC-GOV-014
    plan_section: "Phase 5 / TC-GOV-014"

  # Phase 6 — Validators
  - req_id: REQ-VALID-001
    description: governance_validators_governance.py V150-V155; expected_count 167→173
    parent_taskcard: TC-GOV-015
    plan_section: "Phase 6 / TC-GOV-015"

  # Phase 7 — Audit
  - req_id: REQ-AUDIT-001
    description: governance-control-inventory.yaml (15 lifecycle stages)
    parent_taskcard: TC-GOV-016
    plan_section: "Phase 7 / TC-GOV-016"

  # Phase 8 — Pilots
  - req_id: REQ-PILOT-001
    description: Pilot 1 — Product API change (get_sheet_count)
    parent_taskcard: TC-GOV-017
    plan_section: "Phase 8 / TC-GOV-017"

  - req_id: REQ-PILOT-002
    description: Pilot 2 — Rejected change (V113 violation)
    parent_taskcard: TC-GOV-018
    plan_section: "Phase 8 / TC-GOV-018"

  - req_id: REQ-PILOT-003
    description: Pilot 3 — Pipeline change with product pilot proof
    parent_taskcard: TC-GOV-019
    plan_section: "Phase 8 / TC-GOV-019"

  - req_id: REQ-PILOT-004
    description: Pilots 4-7 (Doc, Compat, Reopening, RC)
    parent_taskcard: TC-GOV-020
    plan_section: "Phase 8 / TC-GOV-020"

  - req_id: REQ-PILOT-005
    description: Pilots 8-9 (Output drift, Maintenance fix)
    parent_taskcard: TC-GOV-021
    plan_section: "Phase 8 / TC-GOV-021"

  - req_id: REQ-PILOT-006
    description: Pilot 10 — Idempotency
    parent_taskcard: TC-GOV-022
    plan_section: "Phase 8 / TC-GOV-022"

  - req_id: REQ-PILOT-007
    description: Final counter verification + report + verdict
    parent_taskcard: TC-GOV-023
    plan_section: "Phase 8 / TC-GOV-023"
```

---

## PART III: EXECUTION DAG

```yaml
# artifact: execution-dag
# authoritative_plan: plans/.claude/memoized-frolicking-donut.md
# artifact_role: analysis_or_evidence_only
# execution_authority: false

dag:
  # Phase 1: Sequential (each repair builds on stable prior)
  TC-GOV-001: {depends_on: [], parallel_safe_with: []}
  TC-GOV-002: {depends_on: [TC-GOV-001], parallel_safe_with: []}
  TC-GOV-003: {depends_on: [TC-GOV-002], parallel_safe_with: []}
  TC-GOV-004: {depends_on: [TC-GOV-003], parallel_safe_with: []}
  TC-GOV-005: {depends_on: [TC-GOV-004], parallel_safe_with: []}

  # Phase 2: Schema work can begin after Phase 1 is stable (no Phase 1 file conflicts)
  TC-GOV-006: {depends_on: [TC-GOV-001], parallel_safe_with: [TC-GOV-002, TC-GOV-003, TC-GOV-004, TC-GOV-005]}
  TC-GOV-007: {depends_on: [TC-GOV-006], parallel_safe_with: [TC-GOV-008]}
  TC-GOV-008: {depends_on: [TC-GOV-006], parallel_safe_with: [TC-GOV-007]}

  # Phase 3-4: Record systems
  TC-GOV-009: {depends_on: [TC-GOV-006, TC-GOV-007, TC-GOV-008], parallel_safe_with: []}
  TC-GOV-010: {depends_on: [TC-GOV-007, TC-GOV-009], parallel_safe_with: []}

  # Phase 5: Tooling
  TC-GOV-011: {depends_on: [TC-GOV-009], parallel_safe_with: [TC-GOV-012]}
  TC-GOV-012: {depends_on: [TC-GOV-010], parallel_safe_with: [TC-GOV-011]}
  TC-GOV-013: {depends_on: [TC-GOV-011, TC-GOV-012], parallel_safe_with: []}
  TC-GOV-014: {depends_on: [TC-GOV-013], parallel_safe_with: []}

  # Phase 6: Validators (need artifact registry + counter tool)
  TC-GOV-015: {depends_on: [TC-GOV-008, TC-GOV-013], parallel_safe_with: [TC-GOV-016]}

  # Phase 7: Audit
  TC-GOV-016: {depends_on: [TC-GOV-014], parallel_safe_with: [TC-GOV-015]}

  # Phase 8: Pilots (sequential by design — each builds on prior governance records)
  TC-GOV-017: {depends_on: [TC-GOV-015, TC-GOV-016], parallel_safe_with: []}
  TC-GOV-018: {depends_on: [TC-GOV-017], parallel_safe_with: []}
  TC-GOV-019: {depends_on: [TC-GOV-018], parallel_safe_with: []}
  TC-GOV-020: {depends_on: [TC-GOV-010, TC-GOV-012, TC-GOV-019], parallel_safe_with: []}
  TC-GOV-021: {depends_on: [TC-GOV-012, TC-GOV-020], parallel_safe_with: []}
  TC-GOV-022: {depends_on: [TC-GOV-013, TC-GOV-019, TC-GOV-020, TC-GOV-021], parallel_safe_with: []}
  TC-GOV-023: {depends_on: [TC-GOV-022], parallel_safe_with: []}

file_ownership_and_locks:
  tools/supervisor/governance_validator_runner.py: [TC-GOV-001]
  tools/supervisor/governance_validators_ext4.py: [TC-GOV-001]
  tools/supervisor/check_continuation.py: [TC-GOV-001, TC-GOV-002, TC-GOV-003]
  tools/supervisor/autonomous_cycle.py: [TC-GOV-003, TC-GOV-004]
  tools/supervisor/sprint_executor_validate.py: [TC-GOV-005]
  .supervisor/policies.yaml: [TC-GOV-002, TC-GOV-004]
  .supervisor/schemas/: [TC-GOV-006]
  registry/governance-binding.yaml: [TC-GOV-007]
  registry/governed-artifact-registry.yaml: [TC-GOV-008]
  registry/change-proposals/: [TC-GOV-009]
  registry/change-impacts/: [TC-GOV-009]
  registry/change-decisions/: [TC-GOV-009]
  registry/promotion-record-ledger.yaml: [TC-GOV-010]
  registry/release-candidates/: [TC-GOV-010]
  tools/supervisor/change_proposal_manager.py: [TC-GOV-011]
  tools/supervisor/governance_promotion_manager.py: [TC-GOV-012]
  tools/supervisor/governance_release_registry.py: [TC-GOV-012]
  tools/supervisor/governance_counters.py: [TC-GOV-013]
  tools/supervisor/governance_ledger_builder.py: [TC-GOV-014]
  tools/supervisor/governance_validators_governance.py: [TC-GOV-015]
  reports/product-governance/: [TC-GOV-016, TC-GOV-023]
  src/python/fods/fods/__init__.py: [TC-GOV-017]
  tests/fods/test_pilot_api.py: [TC-GOV-017]
  tests/fods/test_pilot_maintenance.py: [TC-GOV-021]
```

---

## PART IV: STATE MACHINE

```yaml
# artifact: taskcard-state-machine
# authoritative_plan: plans/.claude/memoized-frolicking-donut.md
# artifact_role: analysis_or_evidence_only
# execution_authority: false

parent_states: [PROPOSED, READY, IN_PROGRESS, CHILDREN_IN_PROGRESS, INTEGRATION_PENDING, VERIFIED, SCORED, CLOSED, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]

child_states: [TODO, READY, IN_PROGRESS, IMPLEMENTED, VERIFIED, SCORED, CLOSED, REROUTED, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]

micro_step_states: [PENDING, READY, ACTIVE, COMPLETE, FAILED, BLOCKED, SKIPPED_NOT_APPLICABLE]

invalid_transitions:
  - from: TODO to: CLOSED  # child must go through IMPLEMENTED + VERIFIED
  - from: READY to: CLOSED  # same
  - from: IMPLEMENTED to: CLOSED  # must be VERIFIED first
  - from: PROPOSED to: CLOSED  # parent must run children
  - from: any to: CLOSED when: mandatory_children_not_all_CLOSED  # parent cannot close early
  - from: REROUTED to: CLOSED when: rework_not_completed  # must reroute and re-verify
  - from: BLOCKED_EXTERNAL to: CLOSED when: unblock_evidence_missing
  - micro_step: PENDING to: COMPLETE  # must pass through ACTIVE
  - micro_step: any to: SKIPPED_NOT_APPLICABLE when: reason_not_recorded

quality_scoring:
  child_dimensions: [requirement_correctness, implementation_correctness, scope_discipline, validation_strength, evidence_completeness, regression_safety, maintainability, production_readiness]
  parent_dimensions: [root_cause_coverage, child_completeness, integration_completeness, dependency_correctness, preserved_behavior, evidence_completeness, rerun_consistency, production_readiness]
  acceptance_threshold: 4  # minimum per dimension (scale 1-5)
  reroute_rule: "Any mandatory dimension scoring below 4/5 marks taskcard REROUTED"
```

---

## PART V: PHASE 1 — STRUCTURAL ENFORCEMENT REPAIRS (Fully Micro-Taskcardized)

---

### Parent Taskcard TC-GOV-001 — Wire V119/V120 into Governance Validator Runner

```
Parent Taskcard ID: TC-GOV-001
Title: Wire V119/V120 into governance_validator_runner.py with correct enforcement
Type: PARENT
Status: PROPOSED
Owner: execution_agent
Supervisor: governance_review_lane

Source:
  Plan requirement ID: REQ-STRUCT-001, REQ-STRUCT-002, REQ-STRUCT-003
  Plan section: Phase 1 / Structural Enforcement Repairs
  Root cause: RC-1 (V119/V120 skipped), C1 (blocks_sprint missing), C2 (V120 wrong signature)
  Selected solution: Remove from skip list; add blocks_sprint; fix promotion_registry build; wire V120 with correct inputs

Objective:
  - V119 (validate_promoted_code_changed_without_reopening) fires with blocks_sprint=True when
    a sprint modifies a file that is PROMOTED_STABLE or CERTIFIED in promotion-ledger.yaml
  - V119 is removed from any skipped_validators list and its result flows through to enforcement
  - V120 is wired with its CORRECT signature inputs (certification_status, architecture_classification)
  - V119 is added to _STRUCTURAL_GOVBLOCK_VALIDATORS in check_continuation.py

Outcome:
  - Running governance_validator_runner.py on a declaration that modifies a PROMOTED_STABLE file
    returns blocks_sprint=True and V119 fires
  - check_continuation.py treats V119 violations as structural (same class as monolith violations)
  - All tests pass; expected_count remains at 167 (V119/V120 were already counted)

Scope:
  Allowed files:
    - tools/supervisor/governance_validator_runner.py
    - tools/supervisor/governance_validators_ext4.py
    - tools/supervisor/check_continuation.py
    - tests/supervisor/test_v119_v120_wired.py  (new)
  Forbidden files:
    - Any product source in src/python/ or src/net/
    - Any other supervisor tool not listed
  Path expansion rule: No implicit expansion; each child specifies exact lines

Preserved behavior:
  - All 167 existing validators continue to run and pass
  - Expected_count remains 167 (V119/V120 already counted — this task ACTIVATES them, not ADDS them)
  - existing_rework_items mechanism in autonomous_cycle.py unchanged
  - _STRUCTURAL_GOVBLOCK_VALIDATORS existing 2 entries preserved; V119 added as third

Inputs:
  - governance_validators_ext4.py (V119 at lines ~293-314, V120 at lines ~319-332)
  - governance_validator_runner.py (V119 import at line 519, call at lines 549-566, skip at line 646)
  - check_continuation.py (_STRUCTURAL_GOVBLOCK_VALIDATORS at lines 518-521)
  - registry/promotion-ledger.yaml (current entries: 6 records, all IMPLEMENTATION_VERIFIED or DRAFT)

Outputs:
  - Modified governance_validator_runner.py (V119 removed from skip list; _build_promotion_registry added)
  - Modified governance_validators_ext4.py (V119 return dict includes blocks_sprint: True)
  - Modified check_continuation.py (V119 in _STRUCTURAL_GOVBLOCK_VALIDATORS)
  - New tests/supervisor/test_v119_v120_wired.py (4 tests)

Dependencies: none (first taskcard)

Child taskcards:
  - TC-GOV-001-01: INVESTIGATE V119 skip mechanism (read lines 519, 549-566, 646)
  - TC-GOV-001-02: Add blocks_sprint: True to V119 return dict
  - TC-GOV-001-03: Remove V119 from skipped_validators; verify _build_promotion_registry
  - TC-GOV-001-04: INVESTIGATE V120 actual inputs and wire correctly
  - TC-GOV-001-05: Add V119 to _STRUCTURAL_GOVBLOCK_VALIDATORS
  - TC-GOV-001-06: Write test_v119_v120_wired.py (4 tests with synthetic PROMOTED_STABLE fixtures)
  - TC-GOV-001-07: Run tests and capture evidence

Parent acceptance criteria:
  - .venv/Scripts/pytest tests/supervisor/test_v119_v120_wired.py → 4 PASSED, 0 FAILED
  - python tools/supervisor/governance_validator_runner.py reports expected_count=167 (unchanged)
  - check_continuation.py grep shows V119 in _STRUCTURAL_GOVBLOCK_VALIDATORS

Integration checks:
  - Full test suite .venv/Scripts/pytest tests/supervisor/ does not regress

Evidence required:
  - test run output (stdout) from pytest showing 4 passed
  - grep output showing V119 in check_continuation.py _STRUCTURAL_GOVBLOCK_VALIDATORS

Closeout criteria:
  - All 7 child taskcards CLOSED
  - Parent integration check passes (full supervisor test suite)
  - Evidence recorded

Rollback strategy:
  - git diff HEAD~1 shows only the 3 files modified; git stash if tests fail catastrophically

Stop conditions:
  - If V119 function body is substantially different from documented signature, create INVESTIGATION child and re-plan
```

#### Child TC-GOV-001-01 — INVESTIGATE V119 skip mechanism

```
Child Taskcard ID: TC-GOV-001-01
Parent Taskcard ID: TC-GOV-001
Title: Read and record the exact V119 skip mechanism in governance_validator_runner.py
Type: CHILD / INVESTIGATION
Status: TODO
Owner: execution_agent

Purpose:
  - Confirm the exact line(s) where V119 is skipped and understand the mechanism
  - Confirm whether _build_promotion_registry() already exists or must be created
  - Record findings before making any changes

Scope:
  Allowed files: tools/supervisor/governance_validator_runner.py (read-only at this step)
  Forbidden files: all others

Expected output:
  - Written record of: line number of skip list, how skip is applied, whether promotion_registry is built
  - Confirm blocks_sprint field presence/absence in _result() or the V119 call site

Micro-steps:
  MS-GOV-001-01-01: Read governance_validator_runner.py lines 510-530 (V119 import area)
  MS-GOV-001-01-02: Read governance_validator_runner.py lines 545-580 (V119/V120 call area)
  MS-GOV-001-01-03: Read governance_validator_runner.py lines 640-660 (skipped_validators area)
  MS-GOV-001-01-04: Grep for _build_promotion_registry or promotion_registry in runner
  MS-GOV-001-01-05: Record findings as a comment in plan or evidence note

Acceptance checks:
  - Findings recorded with exact line numbers
  - Skip mechanism identified (list name, how result is excluded)
  - blocks_sprint presence confirmed

Closeout criteria: All 5 micro-steps COMPLETE and findings recorded
```

**Micro-steps for TC-GOV-001-01:**

```
MS-GOV-001-01-01
Parent: TC-GOV-001 | Child: TC-GOV-001-01 | Status: PENDING
Action: Read governance_validator_runner.py lines 510-530
Purpose: Locate V119 import line (~519) and confirm import syntax
Target: tools/supervisor/governance_validator_runner.py lines 510-530
Allowed operation: inspect
Expected output: Exact import statement for validate_promoted_code_changed_without_reopening
Next micro-step: MS-GOV-001-01-02

MS-GOV-001-01-02
Parent: TC-GOV-001 | Child: TC-GOV-001-01 | Status: PENDING
Action: Read governance_validator_runner.py lines 545-580
Purpose: Confirm how V119 is called (what arguments are passed); confirm whether promotion_registry is built upstream
Target: tools/supervisor/governance_validator_runner.py lines 545-580
Allowed operation: inspect
Expected output: Full V119 call syntax; argument values; any exception handler
Next micro-step: MS-GOV-001-01-03

MS-GOV-001-01-03
Parent: TC-GOV-001 | Child: TC-GOV-001-01 | Status: PENDING
Action: Read governance_validator_runner.py lines 638-660
Purpose: Locate skipped_validators list at line ~646; confirm V119 is in it and how results are filtered
Target: tools/supervisor/governance_validator_runner.py lines 638-660
Allowed operation: inspect
Expected output: Name of skip list variable; how it's applied (e.g., if result["validator_id"] in skip_list: continue)
Failure handling: If skip mechanism differs from expected, record actual mechanism and pause before TC-GOV-001-02
Next micro-step: MS-GOV-001-01-04

MS-GOV-001-01-04
Parent: TC-GOV-001 | Child: TC-GOV-001-01 | Status: PENDING
Action: grep -n "_build_promotion_registry\|promotion_registry" tools/supervisor/governance_validator_runner.py
Purpose: Confirm whether _build_promotion_registry() already exists or must be added from scratch
Target: tools/supervisor/governance_validator_runner.py
Allowed operation: run (read-only grep)
Expected output: Either "no matches" (must create function) or line numbers with existing function
Next micro-step: MS-GOV-001-01-05

MS-GOV-001-01-05
Parent: TC-GOV-001 | Child: TC-GOV-001-01 | Status: PENDING
Action: Record findings as a structured note
Purpose: Ensure TC-GOV-001-02 and TC-GOV-001-03 have accurate targets
Target: (evidence note, not a file write)
Allowed operation: record
Expected output: Summary: {skip_list_line: N, skip_mechanism: "...", promotion_registry_exists: true/false, v119_call_args: "..."}
Completion check: All 4 prior micro-steps COMPLETE and finding fields are non-null
Next micro-step: TC-GOV-001-02 (next child)
```

#### Child TC-GOV-001-02 — Add blocks_sprint: True to V119 return dict

```
Child Taskcard ID: TC-GOV-001-02
Parent Taskcard ID: TC-GOV-001
Title: Modify governance_validators_ext4.py so V119 returns blocks_sprint: True on violation
Type: CHILD
Status: TODO
Owner: execution_agent

Preconditions:
  - TC-GOV-001-01 CLOSED (findings recorded)
  - Confirmed V119 uses _result() helper that lacks blocks_sprint field

Purpose:
  - Without blocks_sprint: True, V119 violations are treated as advisory even when wired

Scope:
  Allowed files: tools/supervisor/governance_validators_ext4.py (lines ~293-314 only)
  Forbidden files: all others

Micro-steps:
  MS-GOV-001-02-01: Read V119 function body in governance_validators_ext4.py lines 293-318
  MS-GOV-001-02-02: Read _result() helper definition to confirm it lacks blocks_sprint
  MS-GOV-001-02-03: Add blocks_sprint: True to V119 return on violation path only
    (passed=False path gets blocks_sprint: True; passed=True path gets blocks_sprint: False)
  MS-GOV-001-02-04: Verify V119 passed=True path does NOT block (only violations should block)
  MS-GOV-001-02-05: Run: python -c "from tools.supervisor.governance_validators_ext4 import validate_promoted_code_changed_without_reopening; r = validate_promoted_code_changed_without_reopening(['src/python/fods/__init__.py'], {'src/python/fods/__init__.py': {'state': 'PROMOTED_STABLE'}}); print(r.get('blocks_sprint'), r.get('passed'))"
    Expected: blocks_sprint=True, passed=False

Acceptance checks:
  - V119 called with PROMOTED_STABLE file → blocks_sprint: True in result
  - V119 called with IMPLEMENTATION_VERIFIED file → blocks_sprint: False in result
  - V119 called with empty registry → blocks_sprint: False, passed: True

Evidence required: Output of MS-GOV-001-02-05 showing blocks_sprint=True
Closeout criteria: MS-GOV-001-02-05 output confirms correct behavior
```

**Micro-steps for TC-GOV-001-02:**

```
MS-GOV-001-02-01
Child: TC-GOV-001-02 | Status: PENDING
Action: Read governance_validators_ext4.py lines 293-318 (V119 full body)
Purpose: Understand all return paths so blocks_sprint is added correctly
Target: tools/supervisor/governance_validators_ext4.py lines 293-318
Allowed operation: inspect
Expected output: Exact return statements (both pass and fail paths)

MS-GOV-001-02-02
Child: TC-GOV-001-02 | Status: PENDING
Action: Grep for def _result in governance_validators_ext4.py
Purpose: Confirm _result() signature and whether it accepts blocks_sprint kwarg
Target: tools/supervisor/governance_validators_ext4.py
Allowed operation: run (grep only)
Expected output: _result() definition showing current parameters

MS-GOV-001-02-03
Child: TC-GOV-001-02 | Status: PENDING
Action: Edit governance_validators_ext4.py — V119 violation return path
Purpose: Add blocks_sprint: True ONLY on the path where passed=False (violation detected)
Target: tools/supervisor/governance_validators_ext4.py (V119 violation return, ~line 308-313)
Allowed operation: edit
Forbidden: Changing any other validator, changing _result() signature, touching V120 yet
Expected output: V119 violation return dict includes "blocks_sprint": True
Preconditions: MS-GOV-001-02-01 and MS-GOV-001-02-02 COMPLETE

MS-GOV-001-02-04
Child: TC-GOV-001-02 | Status: PENDING
Action: Read modified V119 to confirm passed=True path returns blocks_sprint: False
Purpose: Ensure no-violation case does not block sprints
Target: tools/supervisor/governance_validators_ext4.py (V119 pass return)
Allowed operation: inspect (read back after edit)
Expected output: passed=True path has blocks_sprint: False

MS-GOV-001-02-05
Child: TC-GOV-001-02 | Status: PENDING
Action: python -c "from tools.supervisor.governance_validators_ext4 import validate_promoted_code_changed_without_reopening; r = validate_promoted_code_changed_without_reopening(['src/python/fods/__init__.py'], {'src/python/fods/__init__.py': {'state': 'PROMOTED_STABLE'}}); assert r.get('blocks_sprint') == True and r.get('passed') == False, f'FAIL: {r}'; print('PASS: blocks_sprint=True, passed=False')"
Purpose: Confirm V119 produces correct output before proceeding
Allowed operation: run
Expected output: PASS: blocks_sprint=True, passed=False
Failure handling: If import fails (sys.path issue), run from repo root with PYTHONPATH=. prefix
```

#### Child TC-GOV-001-03 — Remove V119 from skipped_validators; verify promotion_registry build

```
Child Taskcard ID: TC-GOV-001-03
Parent Taskcard ID: TC-GOV-001
Title: Remove V119 from skipped_validators list; ensure _build_promotion_registry() is wired
Type: CHILD
Status: TODO
Owner: execution_agent

Preconditions:
  - TC-GOV-001-02 CLOSED (V119 now returns blocks_sprint: True on violation)
  - TC-GOV-001-01 findings confirmed exact skip mechanism

Purpose:
  - V119 is currently called but then its result is discarded by the skip list
  - Removing from skip list makes V119 result flow through to the enforcement pipeline
  - If _build_promotion_registry() doesn't exist, it must be added

Scope:
  Allowed files: tools/supervisor/governance_validator_runner.py only
  Forbidden: governance_validators_ext4.py (already done in TC-GOV-001-02)

Micro-steps:
  MS-GOV-001-03-01: Read the skip list line(s) in governance_validator_runner.py (from TC-GOV-001-01 findings)
  MS-GOV-001-03-02: Remove V119's validator_id from the skip list
  MS-GOV-001-03-03: If _build_promotion_registry() does not exist (from MS-GOV-001-01-04): add it before the V119 call site
  MS-GOV-001-03-04: Confirm promotion_registry is passed to V119 call (lines 549-566) with correct argument
  MS-GOV-001-03-05: Run governance_validator_runner.py on an empty declaration → confirm no crash

Acceptance checks:
  - V119 validator_id NOT in skip list after edit
  - governance_validator_runner.py runs without exception on minimal test declaration
  - If _build_promotion_registry was added: it reads registry/promotion-ledger.yaml without error
```

#### Child TC-GOV-001-04 — INVESTIGATE V120 and wire correctly

```
Child Taskcard ID: TC-GOV-001-04
Parent Taskcard ID: TC-GOV-001
Title: Confirm V120's actual inputs and wire it with certification_status + architecture_classification
Type: CHILD / INVESTIGATION + IMPLEMENTATION
Status: TODO

Preconditions: TC-GOV-001-02 CLOSED

Purpose:
  - V120 expects certification_status and architecture_classification, NOT modified_files
  - The runner must supply these from the right sources

Scope:
  Allowed files:
    - tools/supervisor/governance_validators_ext4.py (read V120 body at lines 319-332)
    - tools/supervisor/governance_validator_runner.py (update V120 call site at lines 568-579)
    - registry/format-registry.yaml (read-only — source for certification_status)

Micro-steps:
  MS-GOV-001-04-01: Read V120 body lines 319-332 — record what certification_status and architecture_classification are expected to mean
  MS-GOV-001-04-02: Grep format-registry.yaml for certification, certified, architecture_classification fields
  MS-GOV-001-04-03: Design how runner extracts certification_status per format from format-registry.yaml
  MS-GOV-001-04-04: Read V120 call site in runner (lines 568-579) — confirm current args vs correct args
  MS-GOV-001-04-05: Update runner V120 call to pass certification_status + architecture_classification correctly
  MS-GOV-001-04-06: Add blocks_sprint: True to V120's violation return (same pattern as V119 in TC-GOV-001-02)
  MS-GOV-001-04-07: Quick smoke test: python -c "from tools.supervisor.governance_validators_ext4 import validate_certification_without_architecture_proof; r = validate_certification_without_architecture_proof('CERTIFIED', 'NON_COMPLIANT', 'fods'); print(r.get('passed'), r.get('blocks_sprint'))"
    Expected: passed=False, blocks_sprint=True (certified but architecture non-compliant = violation)

Acceptance checks:
  - V120 wired with correct inputs; no TypeError on call
  - V120 CERTIFIED+NON_COMPLIANT → passed=False, blocks_sprint=True
  - V120 NOT_CERTIFIED+anything → passed=True (not certified = no violation to enforce)

Reroute rule: If format-registry.yaml does not have certification fields, V120 must return passed=True
  (cannot enforce certification that was never recorded). Document as open gap.
```

#### Child TC-GOV-001-05 — Add V119 to _STRUCTURAL_GOVBLOCK_VALIDATORS

```
Child Taskcard ID: TC-GOV-001-05
Parent Taskcard ID: TC-GOV-001
Title: Add V119 identifier to _STRUCTURAL_GOVBLOCK_VALIDATORS in check_continuation.py
Type: CHILD
Status: TODO

Preconditions: TC-GOV-001-03 CLOSED (V119 now active in runner)

Purpose:
  - Currently only 2 validators in _STRUCTURAL_GOVBLOCK_VALIDATORS (lines 518-521)
  - V119 violations must also trigger structural stop (POST_PLAN_TERMINAL class)

Scope:
  Allowed files: tools/supervisor/check_continuation.py (lines 518-521 only)
  Forbidden: all other files

Micro-steps:
  MS-GOV-001-05-01: Read check_continuation.py lines 515-525 to see exact set definition
  MS-GOV-001-05-02: Determine the correct identifier format for V119 (compare with how monolith/source_architecture are formatted in rework_items)
    Note: rework_items entries are formatted like "GOV_BLOCK:monolith_detection_validator" or "V119:validate_promoted_code_changed_without_reopening" — confirm from autonomous_cycle.py how V119 violations are serialized
  MS-GOV-001-05-03: Add V119 identifier to _STRUCTURAL_GOVBLOCK_VALIDATORS set
  MS-GOV-001-05-04: Read back the set to confirm no syntax error
  MS-GOV-001-05-05: grep -n "_STRUCTURAL_GOVBLOCK_VALIDATORS" tools/supervisor/check_continuation.py
    Expected: line shows 3 entries including V119

Acceptance checks:
  - _STRUCTURAL_GOVBLOCK_VALIDATORS set has 3 entries after edit
  - No syntax error in check_continuation.py (python -c "import tools.supervisor.check_continuation" without error)
```

#### Child TC-GOV-001-06 — Write test_v119_v120_wired.py (4 tests)

```
Child Taskcard ID: TC-GOV-001-06
Parent Taskcard ID: TC-GOV-001
Title: Create tests/supervisor/test_v119_v120_wired.py with 4 tests
Type: CHILD
Status: TODO

Preconditions: TC-GOV-001-03 and TC-GOV-001-05 CLOSED

Purpose: Prove V119/V120 wiring with synthetic PROMOTED_STABLE fixture
  Note: promotion-ledger.yaml has no PROMOTED_STABLE entries currently, so tests
  must use in-memory synthetic promotion_registry dicts

Scope:
  Allowed files: tests/supervisor/test_v119_v120_wired.py (new file only)

Micro-steps:
  MS-GOV-001-06-01: Read existing test pattern from tests/supervisor/test_governance_validators_ext4.py
    (to match existing test file style and imports)
  MS-GOV-001-06-02: Write test_v119_fires_on_promoted_stable_modification:
    - Build synthetic promotion_registry = {"src/python/fods/__init__.py": {"state": "PROMOTED_STABLE"}}
    - Pass modified_files=["src/python/fods/__init__.py"]
    - Assert result["blocks_sprint"] == True and result["passed"] == False
  MS-GOV-001-06-03: Write test_v119_passes_on_implementation_verified:
    - Build synthetic registry with state=IMPLEMENTATION_VERIFIED
    - Assert result["blocks_sprint"] == False and result["passed"] == True
  MS-GOV-001-06-04: Write test_v119_passes_with_empty_registry:
    - Pass promotion_registry={}
    - Assert result["passed"] == True (nothing promoted = nothing to block)
  MS-GOV-001-06-05: Write test_v119_in_structural_govblock_set:
    - Import check_continuation._STRUCTURAL_GOVBLOCK_VALIDATORS (or equivalent access)
    - Assert any entry starting with "V119" is in the set
  MS-GOV-001-06-06: Review all 4 tests for correctness before running

Acceptance checks:
  - File exists at tests/supervisor/test_v119_v120_wired.py
  - 4 test functions present (test_v119_fires_on_*, test_v119_passes_on_*, test_v119_passes_with_*, test_v119_in_*)
```

#### Child TC-GOV-001-07 — Run tests and capture evidence

```
Child Taskcard ID: TC-GOV-001-07
Parent Taskcard ID: TC-GOV-001
Title: Run test_v119_v120_wired.py and full supervisor test suite; record output
Type: CHILD
Status: TODO

Preconditions: TC-GOV-001-06 CLOSED

Micro-steps:
  MS-GOV-001-07-01: .venv/Scripts/pytest tests/supervisor/test_v119_v120_wired.py -v
    Expected: 4 passed, 0 failed
  MS-GOV-001-07-02: If any test fails: read failure output, identify which step (02/03/04/05) is incomplete, re-open that child
  MS-GOV-001-07-03: .venv/Scripts/pytest tests/supervisor/ -x --timeout=60
    Expected: no regression in existing supervisor tests
  MS-GOV-001-07-04: python tools/supervisor/governance_validator_runner.py 2>/dev/null | grep expected_count
    Expected: expected_count=167 (unchanged)
  MS-GOV-001-07-05: Record test stdout as evidence (copy last 20 lines of pytest output to evidence note)

Acceptance checks:
  - test_v119_v120_wired.py: 4 PASSED
  - Supervisor test suite: no regression
  - expected_count: 167

Quality scoring:
  requirement_correctness: 5 (addresses RC-1 directly)
  implementation_correctness: score after tests
  scope_discipline: 5 (3 files only)
  validation_strength: 4 (4 targeted tests)
  evidence_completeness: 5 (test stdout captured)
  regression_safety: 4 (full suite run)
  maintainability: 4 (wiring approach is standard)
  production_readiness: 4 (promotion-ledger has no PROMOTED_STABLE yet; will fire when formats reach that level)
```

---

### Parent Taskcard TC-GOV-002 — Persistent Violation Detection in check_continuation.py

```
Parent Taskcard ID: TC-GOV-002
Title: Add Check 8b (persistent blocking violation) to check_continuation.py
Type: PARENT
Status: PROPOSED
Owner: execution_agent

Source:
  Plan requirement ID: REQ-STRUCT-004, REQ-STRUCT-005
  Root cause: RC-2 (22 of 24 blocking validators silently ignored after first sprint)
  Critical correction: existing_rework_items already exists in autonomous_cycle.py (line 1874) — LEVERAGE IT

Objective:
  - When a non-structural blocking validator fires in 2 consecutive sprints (same validator ID
    appears in both current rework_items and the prior sprint's rework_items), check_continuation.py
    returns STOP with reason "persistent_blocking_violation"
  - This stops the infinite rerun loop
  - The stop is non-overridable (same class as SESSION_MISMATCH)

Preserved behavior:
  - Existing 2 structural GOV_BLOCKs (Check 8) remain unchanged
  - Single-sprint violations still return CONTINUE (give one chance to fix)
  - All existing continuation checks 0 through 8 and 9 onwards unchanged

Scope:
  Allowed files:
    - tools/supervisor/check_continuation.py (add Check 8b after existing Check 8)
    - .supervisor/policies.yaml (add persistent_blocking_validators list)
    - tools/supervisor/autonomous_cycle.py (verify existing_rework_items write-through — read only unless fix needed)
    - tests/supervisor/test_persistent_violation_stop.py (new)
  Forbidden: all other files

Child taskcards:
  - TC-GOV-002-01: INVESTIGATE existing_rework_items persistence in autonomous_cycle.py
  - TC-GOV-002-02: Add persistent_blocking_validators to policies.yaml
  - TC-GOV-002-03: Implement Check 8b in check_continuation.py
  - TC-GOV-002-04: Mark persistent_blocking_violation as non-overridable
  - TC-GOV-002-05: Write and run tests (4 tests)

Parent acceptance criteria:
  - check_continuation.py with rework_items=[V111] in current AND prior signal → STOP with persistent_blocking_violation
  - check_continuation.py with rework_items=[V111] in current only → CONTINUE
  - .venv/Scripts/pytest tests/supervisor/test_persistent_violation_stop.py → 4 PASSED
  - No regression in supervisor test suite

Dependencies: TC-GOV-001 (CLOSED)
```

#### Child TC-GOV-002-01 — INVESTIGATE existing_rework_items

```
Child Taskcard ID: TC-GOV-002-01
Parent: TC-GOV-002 | Status: TODO

Purpose: Confirm how existing_rework_items flows from prior signal to current sprint check

Micro-steps:
  MS-GOV-002-01-01: Read autonomous_cycle.py lines 1870-1890 (existing_rework_items load)
    Confirm: signal["rework_items"] from prior run is loaded as existing_rework_items
  MS-GOV-002-01-02: Grep check_continuation.py for "existing_rework" to see if it's already read
  MS-GOV-002-01-03: Read continuation-signal.json (.local/supervisor/continuation-signal.json) to confirm rework_items field is persisted
  MS-GOV-002-01-04: Record: does continuation-signal.json contain rework_items from last sprint? If yes, Check 8b can read it directly.

Acceptance checks:
  - Confirmed: rework_items from prior sprint IS accessible in continuation-signal.json
  - Confirmed: existing_rework_items in autonomous_cycle.py represents prior sprint rework
```

#### Child TC-GOV-002-02 — Add persistent_blocking_validators to policies.yaml

```
Child Taskcard ID: TC-GOV-002-02
Parent: TC-GOV-002 | Status: TODO
Preconditions: TC-GOV-002-01 CLOSED

Scope: .supervisor/policies.yaml only

Micro-steps:
  MS-GOV-002-02-01: Read .supervisor/policies.yaml autonomous_continuation section (lines 231-300)
  MS-GOV-002-02-02: Add persistent_blocking_validators list after autonomous_continuation block:
    persistent_blocking_validators:
      - V111  # qname_authority
      - V112  # unmapped_type_declaration
      - V113  # no_root_behavior
      - V114  # parser_obligations_declared
      - V115  # writer_obligations_declared
      - V116  # detached_state_prevention
      - V117  # no_dumping_ground_files
      - V122  # traceability_chain
      - V126  # monolith_per_file
      - V53   # spec_qname_refs
      - V65   # all_exports_declared
      - V66   # multi_responsibility_file
      - V77   # analytics_naming_enforced
  MS-GOV-002-02-03: Verify yaml.safe_load() accepts the modified file: python -c "import yaml; yaml.safe_load(open('.supervisor/policies.yaml'))"
```

#### Child TC-GOV-002-03 — Implement Check 8b

```
Child Taskcard ID: TC-GOV-002-03
Parent: TC-GOV-002 | Status: TODO
Preconditions: TC-GOV-002-01, TC-GOV-002-02 CLOSED

Scope: tools/supervisor/check_continuation.py (after line ~548, before existing Check 9)

Micro-steps:
  MS-GOV-002-03-01: Read check_continuation.py lines 545-570 to find exact insertion point after structural GOV_BLOCK check
  MS-GOV-002-03-02: Read how policies.yaml is loaded in check_continuation.py (grep for policies.yaml load)
  MS-GOV-002-03-03: Implement _load_persistent_blocking_validators(policies) helper that reads persistent_blocking_validators from policies
  MS-GOV-002-03-04: Implement Check 8b logic:
    ```
    persistent_validators = _load_persistent_blocking_validators(policies)
    prior_rework_items = signal.get("rework_items", [])  # rework_items from PRIOR sprint (still in signal)
    current_blocking = {item for item in rework_items if any(item.startswith(v) for v in persistent_validators)}
    prior_blocking = {item for item in prior_rework_items if any(item.startswith(v) for v in persistent_validators)}
    persistent = current_blocking & prior_blocking
    if persistent:
        return _stop("persistent_blocking_violation", f"Same validators fired 2+ sprints: {sorted(persistent)}", overridable=False)
    ```
    Note: "prior_rework_items" here is the rework_items from continuation-signal.json BEFORE the current sprint's cycle updated it. This is available because autonomous_cycle.py writes new rework_items at end of sprint, and check_continuation.py is called at start of NEXT sprint (reading the signal written by prior sprint).
  MS-GOV-002-03-05: Read back the Check 8b implementation to confirm logic is correct
```

#### Child TC-GOV-002-04 — Mark non-overridable

```
Child Taskcard ID: TC-GOV-002-04
Parent: TC-GOV-002 | Status: TODO
Preconditions: TC-GOV-002-03 CLOSED

Micro-steps:
  MS-GOV-002-04-01: Grep check_continuation.py for _NON_OVERRIDABLE_STOP_REASONS or equivalent set
  MS-GOV-002-04-02: Add "persistent_blocking_violation" to that set
  MS-GOV-002-04-03: Confirm the overridable=False parameter in _stop() actually blocks the Supreme Directive override path
  MS-GOV-002-04-04: Read check_continuation.py override logic (grep for "overridable") to understand how to correctly block override
```

#### Child TC-GOV-002-05 — Write and run tests

```
Child Taskcard ID: TC-GOV-002-05
Parent: TC-GOV-002 | Status: TODO
Preconditions: TC-GOV-002-04 CLOSED

Tests to write in tests/supervisor/test_persistent_violation_stop.py:
  Test 1: Signal with V111 in rework_items (first sprint) → CONTINUE (only 1 sprint)
  Test 2: Signal with V111 in rework_items AND prior signal also had V111 → STOP persistent_blocking_violation
  Test 3: V111 in sprint 1, V112 in sprint 2 (different items) → CONTINUE (not the SAME item)
  Test 4: V119 (structural) in both sprints → STOP via Check 8 (existing structural, not Check 8b)

Micro-steps:
  MS-GOV-002-05-01: Read existing check_continuation test file for test pattern
  MS-GOV-002-05-02: Write the 4 tests
  MS-GOV-002-05-03: .venv/Scripts/pytest tests/supervisor/test_persistent_violation_stop.py -v → 4 PASSED
  MS-GOV-002-05-04: .venv/Scripts/pytest tests/supervisor/ -x --timeout=60 → no regression
```

---

### Parent Taskcard TC-GOV-003 — Implement Rework Classification (critical_rework_count)

```
Parent Taskcard ID: TC-GOV-003
Title: Wire autonomous_cycle.py rework classification into check_continuation.py Check 2b
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-002 (CLOSED)

Objective:
  - autonomous_cycle.py already calls classify_rework_items() (line 1500-1503)
  - The result (critical_rework_count) must be written to continuation-signal.json
  - check_continuation.py must add Check 2b: if critical_rework_count > 0 → STOP

Preserved behavior:
  - classify_rework_items() call unchanged; only ADD a write of its result to signal

Scope:
  Allowed files:
    - tools/supervisor/autonomous_cycle.py (add critical_rework_count write to signal)
    - tools/supervisor/check_continuation.py (add Check 2b after Check 2)
    - tests/supervisor/test_critical_rework_stop.py (new)

Child taskcards:
  - TC-GOV-003-01: INVESTIGATE classify_rework_items output format
  - TC-GOV-003-02: Add critical_rework_count to autonomous_cycle.py signal write
  - TC-GOV-003-03: Add Check 2b to check_continuation.py
  - TC-GOV-003-04: Write and run tests

Parent acceptance criteria:
  - continuation-signal.json contains critical_rework_count field after autonomous_cycle runs
  - check_continuation.py with critical_rework_count > 0 → STOP critical_rework_blocks_continuation
  - .venv/Scripts/pytest tests/supervisor/test_critical_rework_stop.py → 4 PASSED
```

**TC-GOV-003-01: INVESTIGATE classify_rework_items**
```
Micro-steps:
  MS-GOV-003-01-01: grep -n "classify_rework_items" tools/supervisor/autonomous_cycle.py
  MS-GOV-003-01-02: Read autonomous_cycle_extensions.py (import source for classify_rework_items) — find the function; confirm what it returns
  MS-GOV-003-01-03: Record: does it return a dict with critical_count? does it return a list? what is the output type?
  MS-GOV-003-01-04: Read lines 1676-1700 of autonomous_cycle.py to see signal construction — identify where to inject critical_rework_count
```

**TC-GOV-003-02: Add critical_rework_count to signal**
```
Micro-steps:
  MS-GOV-003-02-01: Based on TC-GOV-003-01 findings, extract critical_rework_count from classify_rework_items() result
  MS-GOV-003-02-02: Add to signal dict: signal["critical_rework_count"] = critical_rework_count
  MS-GOV-003-02-03: Add signal["critical_rework_item_ids"] = [list of item IDs graded OVERCLAIMED/REJECTED]
  MS-GOV-003-02-04: Verify signal write does not break existing signal fields
```

**TC-GOV-003-03: Add Check 2b**
```
Micro-steps:
  MS-GOV-003-03-01: Read check_continuation.py Check 2 area (autonomous_continue check, ~line 413-426)
  MS-GOV-003-03-02: Insert Check 2b immediately after Check 2: read critical_rework_count from signal; if > 0: _stop("critical_rework_blocks_continuation", ..., overridable=False)
  MS-GOV-003-03-03: Add critical_rework_blocks_continuation to non-overridable set
  MS-GOV-003-03-04: Verify Check 2b only fires when critical_rework_count > 0 (not when = 0)
```

**TC-GOV-003-04: Tests**
```
Tests: critical_rework_count=0 → CONTINUE | critical_rework_count=1 OVERCLAIMED → STOP | critical_rework_count=1 REJECTED → STOP | critical_rework_count=1 REWORK_REQUIRED → CONTINUE (not critical)
```

---

### Parent Taskcard TC-GOV-004 — Wire blast-radius-register.yaml into autonomous_cycle.py

```
Parent Taskcard ID: TC-GOV-004
Title: Add Step 0b (blast radius check) to autonomous_cycle.py; add blast_radius_enforcement to policies.yaml
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-003 (CLOSED)

Objective:
  - Before Step 1 (validate declaration), check whether any declared changed_files appear
    in registry/blast-radius-register.yaml with severity CRITICAL/HIGH
  - Default enforcement: warn (log, do not block)
  - Configurable: policies.yaml blast_radius_enforcement = warn|strict

Preserved behavior:
  - All existing autonomous_cycle.py steps (0, 0a, 0a-qname, 1-5) unchanged

Scope:
  Allowed files:
    - tools/supervisor/autonomous_cycle.py (add Step 0b function + call)
    - .supervisor/policies.yaml (add blast_radius_enforcement field)
    - registry/blast-radius-register.yaml (read-only source)
    - tests/supervisor/test_blast_radius_check.py (new)

Child taskcards:
  - TC-GOV-004-01: INVESTIGATE blast-radius-register.yaml schema and current entries
  - TC-GOV-004-02: Add blast_radius_enforcement: warn to policies.yaml
  - TC-GOV-004-03: Implement _check_blast_radius() function in autonomous_cycle.py
  - TC-GOV-004-04: Add Step 0b call after Step 0a-qname
  - TC-GOV-004-05: Write and run tests

Parent acceptance criteria:
  - _check_blast_radius() reads blast-radius-register.yaml without error
  - With enforcement=warn: high-impact file change → warning logged, sprint continues
  - With enforcement=strict: high-impact file change → hard_stops.append(reason), sprint blocked
  - .venv/Scripts/pytest tests/supervisor/test_blast_radius_check.py → 4 PASSED
```

**Micro-step highlights for TC-GOV-004:**

```
TC-GOV-004-01: Read registry/blast-radius-register.yaml in full. Record: schema fields, severity levels used, affected_files format (relative paths? globs?), impact_analysis_required field.

TC-GOV-004-02: Add single line to .supervisor/policies.yaml:
  blast_radius_enforcement: warn
  Validate: python -c "import yaml; p = yaml.safe_load(open('.supervisor/policies.yaml')); assert p.get('blast_radius_enforcement') == 'warn'"

TC-GOV-004-03: Implement:
  def _check_blast_radius(declaration, repo_root, policies):
    br_path = repo_root / "registry" / "blast-radius-register.yaml"
    if not br_path.exists(): return []
    enforcement = policies.get("blast_radius_enforcement", "warn")
    br_data = yaml.safe_load(br_path.read_text()) or {}
    high_impact = {}
    for entry in br_data.get("entries", []):
        if entry.get("severity") in ("CRITICAL", "HIGH") and entry.get("impact_analysis_required", False):
            for af in entry.get("affected_files", []):
                high_impact[af] = entry.get("br_id")
    changed = set(declaration.get("changed_files", []))
    hits = {f: high_impact[f] for f in changed if f in high_impact}
    if not hits: return []
    if enforcement == "strict":
        return [f"Blast radius {enforcement} hit: {hits}"]
    logger.warning("Blast radius WARN: %s", hits)
    return []

TC-GOV-004-04: Call _check_blast_radius() in autonomous_cycle.py Step 0b (after SAL check):
  blast_issues = _check_blast_radius(declaration, repo_root, policies)
  if blast_issues:
      hard_stops.extend(blast_issues)

TC-GOV-004-05 Tests:
  Test 1: File in CRITICAL/HIGH blast list + enforcement=warn → warning, no stop
  Test 2: File in CRITICAL/HIGH blast list + enforcement=strict → stop
  Test 3: File NOT in blast list → pass
  Test 4: blast-radius-register.yaml missing → pass (graceful skip)
```

---

### Parent Taskcard TC-GOV-005 — Add Phase 14 (Git Diff Cross-Check) to sprint_executor_validate.py

```
Parent Taskcard ID: TC-GOV-005
Title: Add Phase 14 evidence cross-check against git diff to sprint_executor_validate.py
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-004 (CLOSED)

Objective:
  - Phase 14 compares declaration changed_files against git diff --name-only HEAD~1
  - Files declared as changed but NOT in git diff → ERROR (false claim)
  - Files in git diff but NOT declared → WARN (undisclosed change)
  - Phase 14 is named correctly (Phase 13 already exists as lane scope guard)

Preserved behavior:
  - Phases 1-13 unchanged
  - Phase 14 is best-effort: if git is unavailable → skip silently (no error)

Scope:
  Allowed files:
    - tools/supervisor/sprint_executor_validate.py (add Phase 14 function + call after Phase 13)
    - tests/supervisor/test_phase14_git_crosscheck.py (new)

Child taskcards:
  - TC-GOV-005-01: INVESTIGATE Phase 13 endpoint and insertion point for Phase 14
  - TC-GOV-005-02: Implement _phase14_git_crosscheck() function
  - TC-GOV-005-03: Add Phase 14 call in main validation flow
  - TC-GOV-005-04: Write and run tests

Parent acceptance criteria:
  - Phase 14 correctly identifies false claims (DECLARED_NOT_IN_GIT) as ERROR
  - Phase 14 identifies undisclosed changes (GIT_CHANGED_NOT_DECLARED) as WARN only
  - git unavailable → graceful skip (no exception)
  - .venv/Scripts/pytest tests/supervisor/test_phase14_git_crosscheck.py → 4 PASSED
```

**Micro-steps for TC-GOV-005:**

```
TC-GOV-005-01: Read sprint_executor_validate.py lines 665-730 (Phase 13 area + return). Identify exact line after which Phase 14 is inserted.

TC-GOV-005-02: Implement _phase14_git_crosscheck(declaration, repo_root):
  issues = []
  try:
    result = subprocess.run(["git","diff","--name-only","HEAD~1"], cwd=str(repo_root), capture_output=True, text=True, timeout=10)
    if result.returncode != 0 or not result.stdout.strip(): return []  # no prior commit or git unavailable
    git_changed = set(result.stdout.strip().splitlines())
    declared = set(declaration.get("changed_files", []))
    falsely_declared = {f for f in declared - git_changed if f.startswith(("src/","tools/","tests/"))}
    undeclared_src = {f for f in git_changed - declared if f.startswith(("src/","tools/","tests/")) and not f.endswith(".pyc")}
    if falsely_declared:
      issues.append({"phase": 14, "severity": "ERROR", "code": "DECLARED_NOT_IN_GIT", "message": f"False claims: {sorted(falsely_declared)}", "autofix": False})
    if undeclared_src:
      issues.append({"phase": 14, "severity": "WARN", "code": "GIT_CHANGED_NOT_DECLARED", "message": f"Undisclosed: {sorted(undeclared_src)}", "autofix": False})
  except (subprocess.TimeoutExpired, FileNotFoundError): pass
  return issues

TC-GOV-005-03: Add Phase 14 call. Where Phase 13 currently returns validation result, chain Phase 14 after it. Ensure any ERROR from Phase 14 propagates to the validation failure path.

TC-GOV-005-04: Tests (4):
  Test 1: declared=[a.py], git diff=[a.py] → no issues
  Test 2: declared=[a.py,b.py], git diff=[a.py] → WARN GIT_CHANGED_NOT_DECLARED for b.py
    Wait: b.py is declared but NOT in git → ERROR DECLARED_NOT_IN_GIT
    (b.py is claimed changed but git doesn't show it)
  Test 3: declared=[a.py], git diff=[a.py, src/b.py] → WARN GIT_CHANGED_NOT_DECLARED for src/b.py
  Test 4: git unavailable → [] (no exception)
```

---

## PART VI: PHASES 2-8 — GOVERNANCE RECORDS, TOOLING, AND PILOTS (Parent + Children)

---

### Parent Taskcard TC-GOV-006 — Eight JSON Schema Files

```
Parent Taskcard ID: TC-GOV-006
Title: Create 8 JSON Schema files in .supervisor/schemas/
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-001 (stable baseline for expected_count)

Objective: Define machine-checkable schemas for all governance records

Scope:
  Allowed folders: .supervisor/schemas/ (new files only)
  Forbidden: existing schema files (do not modify)

Child taskcards:
  - TC-GOV-006-01: governance-binding.schema.json
  - TC-GOV-006-02: governed-artifact.schema.json (with 11-state status enum)
  - TC-GOV-006-03: change-proposal.schema.json (with 7-state status enum)
  - TC-GOV-006-04: change-impact.schema.json
  - TC-GOV-006-05: change-decision.schema.json (with 5 final_decision values)
  - TC-GOV-006-06: promotion-record.schema.json (promotion_level must match promotion_manager.py enum)
  - TC-GOV-006-07: release-candidate.schema.json (final_decision includes NOT_RELEASEABLE)
  - TC-GOV-006-08: governance-gap.schema.json
  - TC-GOV-006-09: validate_governance_schemas.py script + run all 8 schemas

Key micro-steps per schema child:
  Step 1: Design required fields (from plan section)
  Step 2: Write schema JSON with "$schema" key and all required fields
  Step 3: python -c "import json; json.load(open('.supervisor/schemas/<name>.schema.json'))" → no error
  Step 4: jsonschema validate a minimal valid fixture against the schema

Parent acceptance criteria:
  - python tools/supervisor/validate_governance_schemas.py → 8 OK lines, exit 0
  - Each schema has "$schema": "https://json-schema.org/draft/2020-12/schema"
  - Each schema has additionalProperties: false
  - promote-record.schema.json promotion_level enum matches EXACTLY what promotion_manager.py uses
    (verify by reading promotion_manager.py enum before writing schema)
```

---

### Parent Taskcard TC-GOV-007 — Governance Binding Record

```
Parent Taskcard ID: TC-GOV-007
Title: Create registry/governance-binding.yaml and validate_governance_binding.py
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-006

Child taskcards:
  - TC-GOV-007-01: Read all authority file paths — confirm each exists on disk
  - TC-GOV-007-02: Write registry/governance-binding.yaml (all fields, all 8 authority arrays)
  - TC-GOV-007-03: Write tools/supervisor/validate_governance_binding.py
  - TC-GOV-007-04: Run validate_governance_binding.py → exit 0
  - TC-GOV-007-05: Write reports/product-governance/README.md

Key constraint for TC-GOV-007-01: Spot-check EACH listed authority path actually exists:
  - plans/strategic/spec-to-feature-radical-correction-plan.md
  - docs/code-quality/production-library-standard-v2.md
  - registry/gate-contract-registry.yaml
  - docs/gates/python-release-gate-definitions.md
  - registry/promotion-ledger.yaml
  - tools/supervisor/promotion_manager.py
  - All others: run os.path.exists check in Python
```

---

### Parent Taskcard TC-GOV-008 — Governed Artifact Registry (Seed) + Lookup Tool

```
Parent Taskcard ID: TC-GOV-008
Title: Create governed-artifact-registry.yaml seed (15 entries) and governed_artifact_lookup.py
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-006, TC-GOV-007

Child taskcards:
  - TC-GOV-008-01: INVESTIGATE actual fods __init__.py exports and models.py to correctly set GA-FODS-001 through GA-FODS-005 fields
  - TC-GOV-008-02: Write registry/governed-artifact-registry.yaml (15 seed entries)
  - TC-GOV-008-03: Validate all 15 entries against governed-artifact.schema.json
  - TC-GOV-008-04: Write tools/supervisor/governed_artifact_lookup.py (query/status/is-promoted subcommands)
  - TC-GOV-008-05: Test: python tools/supervisor/governed_artifact_lookup.py query --path src/python/fods/__init__.py → {"artifact_id": "GA-FODS-001", "status": "PROMOTED"}
    Note: GA-FODS-001 must have status matching promotion-ledger.yaml entry for fods. If fods is IMPLEMENTATION_VERIFIED in ledger, GA-FODS-001 status must be IMPLEMENTATION_VERIFIED (not PROMOTED). Consistency required.
```

---

### Parent Taskcard TC-GOV-009 — Retroactive CP/CI/CD Records (8 historical changes)

```
Parent Taskcard ID: TC-GOV-009
Title: Create 8 CP-* + 8 CI-* + 8 CD-* YAML records for material historical changes
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-006, TC-GOV-007, TC-GOV-008

Child taskcards:
  - TC-GOV-009-01: INVESTIGATE each historical change — verify affected_files by reading git log
    (For each of 8 changes: run git log --oneline --follow -- <key_file> to find relevant commits)
  - TC-GOV-009-02: Create registry/change-proposals/ directory + README.md
  - TC-GOV-009-03: Write 8 CP-*.yaml files (all status: ACCEPTED — retroactive)
  - TC-GOV-009-04: Create registry/change-impacts/ + write 8 CI-*.yaml files
  - TC-GOV-009-05: Create registry/change-decisions/ + write 8 CD-*.yaml files
  - TC-GOV-009-06: Validate all 24 YAML files against their schemas
  - TC-GOV-009-07: Run change_proposal_manager.py list --status ACCEPTED → prints 8 records

Key constraint for TC-GOV-009-01: Do NOT fabricate affected_files. Only list files that:
  - Actually exist in the repo AND
  - Are plausibly related to the historical change based on git log or plan names

Anti-overclaim rule: CP-*.yaml fields must be consistent with verifiable history. If a change
cannot be verified, mark affected_files as ["UNVERIFIED — see plan reference"] and note it as
a known gap requiring future verification.
```

---

### Parent Taskcard TC-GOV-010 — Promotion Record Ledger + Release Candidate Seeds

```
Parent Taskcard ID: TC-GOV-010
Title: Create registry/promotion-record-ledger.yaml (full-schema) + 3 RC seed files
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-006, TC-GOV-007, TC-GOV-009

Child taskcards:
  - TC-GOV-010-01: Read registry/promotion-ledger.yaml in full — record all 6 entries
  - TC-GOV-010-02: Write registry/promotion-record-ledger.yaml (one PR-* per entry)
    Key: promotion_hash must be null for all (none are PROMOTED_STABLE); promotion_level = match ledger
  - TC-GOV-010-03: Validate all PR-* records against promotion-record.schema.json
  - TC-GOV-010-04: Create registry/release-candidates/ directory
  - TC-GOV-010-05: Write RC-FODS-PREVIEW-001.yaml (PREVIEW, NOT_RELEASEABLE — no PROMOTED_STABLE yet)
  - TC-GOV-010-06: Write RC-FODS-BREAKING-001.yaml (demonstrates NOT_RELEASEABLE for Pilot 5)
  - TC-GOV-010-07: Validate both RC-*.yaml against release-candidate.schema.json
```

---

### Parent Taskcard TC-GOV-011 — Change Proposal Manager Tool

```
Parent Taskcard ID: TC-GOV-011
Title: Create tools/supervisor/change_proposal_manager.py
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-009

Child taskcards:
  - TC-GOV-011-01: Write CLI skeleton with argparse (subcommands: new-proposal, validate, list, check-ungoverned-changes)
  - TC-GOV-011-02: Implement list subcommand (reads registry/change-proposals/*.yaml, filters by --status)
  - TC-GOV-011-03: Implement validate subcommand (validates single CP-*.yaml against schema)
  - TC-GOV-011-04: Implement check-ungoverned-changes (reads git log --since=30.days, cross-references against CP affected_files[])
    Output: list of file paths not covered by any CP-* with status=ACCEPTED
  - TC-GOV-011-05: Test: python tools/supervisor/change_proposal_manager.py list --status ACCEPTED → 8 records
  - TC-GOV-011-06: Test: check-ungoverned-changes --lookback-days 7 → reports only files changed in last 7 days not in any CP
```

---

### Parent Taskcard TC-GOV-012 — Promotion Manager + Release Registry Tools

```
Parent Taskcard ID: TC-GOV-012
Title: Create governance_promotion_manager.py and governance_release_registry.py
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-010

Child taskcards:
  - TC-GOV-012-01: Write governance_promotion_manager.py (subcommands: validate-all, check-reopening, compute-hash, reopen)
    check-reopening: for PROMOTED_STABLE PR-* records, run git log --since=<source_revision> -- <file> for each promoted_file
    Note: Since no entries are PROMOTED_STABLE yet, check-reopening will return empty result — this is correct
  - TC-GOV-012-02: Write governance_release_registry.py (subcommands: validate, check-eligibility, validate-all)
    check-eligibility: verify all included_change_ids have CD-* with final_decision=ACCEPT
  - TC-GOV-012-03: Tests: test_governance_promotion_manager.py (5 tests minimum)
  - TC-GOV-012-04: Tests: test_governance_release_registry.py (3 tests minimum)
  - TC-GOV-012-05: Run both test files; confirm pass
```

---

### Parent Taskcard TC-GOV-013 — Governance Counter Tool (22 counters)

```
Parent Taskcard ID: TC-GOV-013
Title: Create tools/supervisor/governance_counters.py computing all 22 required counters
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-011, TC-GOV-012

Child taskcards:
  - TC-GOV-013-01: Design counter computation class with 22 methods (one per counter)
  - TC-GOV-013-02: Implement counters 1-6 (governance controls, material changes, impact analysis)
  - TC-GOV-013-03: Implement counters 7-12 (traceability, released symbols, decisions, proof, baselines)
  - TC-GOV-013-04: Implement counters 13-18 (released artifacts, RC quality, ungoverned components)
  - TC-GOV-013-05: Implement counters 19-22 (gaps without tasks, failed pilots, second-run changes)
  - TC-GOV-013-06: Write output to reports/product-governance/governance-counter-report.yaml
  - TC-GOV-013-07: Tests: test_governance_counters.py (8 tests minimum — one per major counter group)
  - TC-GOV-013-08: Run tool end-to-end; verify 22 counters all non-negative integers

Counter 22 (MATERIAL_SECOND_RUN_CHANGES) starts at 0 on first run; computed as diff between
run-1 and run-2 outputs in Pilot 10 (TC-GOV-022).
```

---

### Parent Taskcard TC-GOV-014 — Governance Ledger Builder

```
Parent Taskcard ID: TC-GOV-014
Title: Create tools/supervisor/governance_ledger_builder.py → reports/product-governance/product-governance-ledger.yaml
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-013

Child taskcards:
  - TC-GOV-014-01: Implement 7 gap discovery functions (ungoverned product, ungoverned pipeline, missing CPs, promotion hash null, missing CI, missing CD, documentation drift)
  - TC-GOV-014-02: Implement gap ID assignment (GAP-GOV-NNN sequential)
  - TC-GOV-014-03: Assign task_ids to every gap (reference existing TC-GOV-* where applicable; create stub future-sprint task IDs for remaining gaps)
    Key constraint: Every gap must have at least one task_id — this drives ACTIONABLE_GAPS_WITHOUT_TASKS=0
  - TC-GOV-014-04: Write reports/product-governance/product-governance-ledger.yaml
  - TC-GOV-014-05: Validate all gap records against governance-gap.schema.json
  - TC-GOV-014-06: Run governance_counters.py after ledger is built → counters 19,20 should be 0
```

---

### Parent Taskcard TC-GOV-015 — New Validators V150-V155 + Update expected_count 167→173

```
Parent Taskcard ID: TC-GOV-015
Title: Create governance_validators_governance.py (V150-V155) and update runner expected_count to 173
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-008, TC-GOV-013

CRITICAL: expected_count = 167 (confirmed by deep code read). Adding 6 new validators → 173.
Do NOT use 171 (prior plan error); use 173.

Child taskcards:
  - TC-GOV-015-01: Write governance_validators_governance.py with V150-V155
    - V150: validate_governed_artifact_pre_flight (PROMOTED files need CP before modification)
    - V151: validate_change_proposal_coverage (CP-* required for PRODUCT_SOURCE on PROMOTED artifacts)
    - V152: validate_impact_analysis_on_accepted_proposals (CI-* exists for each ACCEPTED CP-*)
    - V153: validate_release_candidate_decision_chain (RC included_changes all have ACCEPT)
    - V154: validate_governance_counter_report_fresh (report exists, < 14 days old)
    - V155: validate_governance_binding_paths (calls validate_governance_binding.py)
  - TC-GOV-015-02: Import and register V150-V155 in governance_validator_runner.py
  - TC-GOV-015-03: Update expected_count in governance_validator_runner.py from 167 to 173
  - TC-GOV-015-04: Update assertion in tests/supervisor/test_governance_validator_runner.py from 167 to 173
  - TC-GOV-015-05: Write tests/supervisor/test_governance_validators_governance.py (6 tests — one per validator)
  - TC-GOV-015-06: Run python tools/supervisor/governance_validator_runner.py → reports 173 validators
  - TC-GOV-015-07: .venv/Scripts/pytest tests/supervisor/ -x → no regression

Key constraint for TC-GOV-015-03 and 15-04: These two edits MUST happen atomically in the same
execution step or the test will fail with assertion error 167 != 173. Preferred order:
  1. Update expected_count in runner
  2. Update assertion in test
  3. Run test
```

---

### Parent Taskcard TC-GOV-016 — Lifecycle Governance Control Inventory

```
Parent Taskcard ID: TC-GOV-016
Title: Write reports/product-governance/governance-control-inventory.yaml (15 lifecycle stages)
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-014

Child taskcards:
  - TC-GOV-016-01: INVESTIGATE actual enforcement points for each of 15 stages (read governance_validator_runner.py; read policies.yaml; confirm what actually enforces each stage)
  - TC-GOV-016-02: Write governance-control-inventory.yaml with honest status (GOVERNED / PARTIAL / UNGOVERNED)
    Honest finding: dependency_changes = UNGOVERNED; post_release_maintenance = PARTIAL (V119 now covers reopening)
  - TC-GOV-016-03: Create 2 GAP-GOV records for UNGOVERNED stages in product-governance-ledger.yaml
  - TC-GOV-016-04: Verify: GOVERNANCE_CONTROLS_NOT_INVENTORIED counter = 0 after this taskcard
```

---

### Parent Taskcard TC-GOV-017 — Pilot 1: Product API Change (Full Lifecycle)

```
Parent Taskcard ID: TC-GOV-017
Title: Pilot 1 — Full governance chain for get_sheet_count() addition to FODS
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-015, TC-GOV-016

Objective: Prove the complete chain: CP → CI → CD → implementation → test → GA update

Child taskcards:
  - TC-GOV-017-01: Read src/python/fods/fods/__init__.py — confirm load() and FodsDocument.sheets exist
  - TC-GOV-017-02: Write CP-FODS-PILOT-001.yaml (SUBMITTED → ACCEPTED after decision)
  - TC-GOV-017-03: Write CI-FODS-PILOT-001.yaml (ADDITIVE, MINOR)
  - TC-GOV-017-04: Write CD-FODS-PILOT-001.yaml (all PASS, final_decision: ACCEPT)
  - TC-GOV-017-05: Implement get_sheet_count() in src/python/fods/fods/__init__.py (5-line addition)
  - TC-GOV-017-06: Write tests/fods/test_pilot_api.py::test_get_sheet_count
  - TC-GOV-017-07: .venv/Scripts/pytest tests/fods/test_pilot_api.py → PASSED
  - TC-GOV-017-08: Update GA-FODS-001 change_history to include CP-FODS-PILOT-001
  - TC-GOV-017-09: Verify V150 passes when CP-FODS-PILOT-001 covers the modification

Micro-steps for TC-GOV-017-05:
  MS-GOV-017-05-01: Read __init__.py to understand load() return type and FodsDocument.sheets attribute
  MS-GOV-017-05-02: Implement: def get_sheet_count(path) -> int: return len(load(path).sheets)
  MS-GOV-017-05-03: Add to __all__ if defined in __init__.py
  MS-GOV-017-05-04: Run: python -c "from fods import get_sheet_count" → no ImportError
```

---

### Parent Taskcard TC-GOV-018 — Pilot 2: Rejected Change

```
Parent Taskcard ID: TC-GOV-018
Title: Pilot 2 — Submit V113-violating change; prove REJECT decision
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-017

Child taskcards:
  - TC-GOV-018-01: Write CP-PILOT-REJECT-001.yaml (get_all_cell_values_flat() on FodsDocument root — violates V113)
  - TC-GOV-018-02: Write CI-PILOT-REJECT-001.yaml (notes V113 violation)
  - TC-GOV-018-03: Write CD-PILOT-REJECT-001.yaml (architecture_verdict: FAIL, qname_verdict: FAIL, final_decision: REJECT)
  - TC-GOV-018-04: Verify no implementation exists for get_all_cell_values_flat() (grep src/ to confirm absence)
  - TC-GOV-018-05: Verify RC-FODS-PREVIEW-001 does NOT include CP-PILOT-REJECT-001 in included_change_ids
  - TC-GOV-018-06: change_proposal_manager.py list --status REJECTED → shows 1 record
```

---

### Parent Taskcard TC-GOV-019 — Pilot 3: Pipeline Change

```
Parent Taskcard ID: TC-GOV-019
Title: Pilot 3 — Modify skill prompt; prove pipeline_impact_verdict requires product pilot
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-018

Child taskcards:
  - TC-GOV-019-01: Read .claude/commands/add-python-api.md to understand current content
  - TC-GOV-019-02: Add spec_qname ClassVar reminder to .claude/commands/add-python-api.md (minimal addition)
  - TC-GOV-019-03: Write CP-PIPELINE-PILOT-001.yaml (product_or_pipeline: pipeline)
  - TC-GOV-019-04: Write CI-PIPELINE-PILOT-001.yaml (affected_pipeline_components: add-python-api skill)
  - TC-GOV-019-05: Write CD-PIPELINE-PILOT-001.yaml (pipeline_impact_verdict: PASS, evidence references the modified command file)
  - TC-GOV-019-06: Document pilot output: record that the change would affect all add-python-api generated code
  - TC-GOV-019-07: Write result to reports/product-governance/pilots/pilot3-pipeline-result.yaml
```

---

### Parent Taskcard TC-GOV-020 — Pilots 4-7 (Doc, Compat, Reopening, RC)

```
Parent Taskcard ID: TC-GOV-020
Title: Pilots 4, 5, 6, 7 — documentation, compatibility, reopening, release candidate
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-010, TC-GOV-012, TC-GOV-019

Child taskcards:
  - TC-GOV-020-01: Pilot 4 — Doc change: Update parse_fods() docstring; write CP-DOC-PILOT-001/CI/CD (PATCH)
  - TC-GOV-020-02: Pilot 5 — Compat change: Write CP-COMPAT-PILOT-001 for fods.load()→fods.parse() rename (BREAKING/MAJOR); CD=ACCEPT_WITH_REWORK_BEFORE_RELEASE; RC-FODS-BREAKING-001 = NOT_RELEASEABLE
  - TC-GOV-020-03: Pilot 6 — Reopening: Modify one line in src/python/csv/__init__.py (comment only); run governance_promotion_manager.py check-reopening; update CSV promotion record to REOPENED; write reopening notice
  - TC-GOV-020-04: Pilot 7 — Release candidate: Write RC-FODS-PATCH-001.yaml including only CP-FODS-PILOT-001 + CP-DOC-PILOT-001; run governance_release_registry.py check-eligibility → PATCH ELIGIBLE; verify CP-PILOT-REJECT-001 and CP-COMPAT-PILOT-001 are excluded

Key constraint for TC-GOV-020-03: The CSV modification must be REVERTED after demonstrating reopening (revert the comment change). The reopening NOTICE stays; the actual file change is reverted to avoid lingering diffs.
```

---

### Parent Taskcard TC-GOV-021 — Pilots 8-9 (Output Drift + Maintenance Fix)

```
Parent Taskcard ID: TC-GOV-021
Title: Pilots 8 and 9 — output drift detection; maintenance fix full lifecycle
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-012, TC-GOV-020

Child taskcards:
  - TC-GOV-021-01: Pilot 8 — Record current hash of FODS promoted files; add whitespace comment to __init__.py; run compute-hash → hash differs; run check-eligibility → NOT_RELEASEABLE promoted_hash_mismatch; REVERT the whitespace change; write pilot8-drift-result.yaml
  - TC-GOV-021-02: Pilot 9 — Read fods_cell_iterator.py; write test proving correct empty-cell handling; write full CP-MAINT-PILOT-001/CI/CD chain; test passes; update PR-FODS-PY-001 change_ids

Key constraint for TC-GOV-021-01: The whitespace change MUST be reverted before TC-GOV-021 closes.
Rollback: git checkout -- src/python/fods/fods/__init__.py after hash mismatch is confirmed.
```

---

### Parent Taskcard TC-GOV-022 — Pilot 10: Idempotency

```
Parent Taskcard ID: TC-GOV-022
Title: Pilot 10 — Run governance tools twice, prove MATERIAL_SECOND_RUN_CHANGES = 0
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-013, TC-GOV-019, TC-GOV-020, TC-GOV-021

Child taskcards:
  - TC-GOV-022-01: Run governance_counters.py → save as counters-run1.yaml
  - TC-GOV-022-02: Run governance_ledger_builder.py (second run — no files changed)
  - TC-GOV-022-03: Run governance_promotion_manager.py validate-all (second run)
  - TC-GOV-022-04: Run governance_release_registry.py validate-all (second run)
  - TC-GOV-022-05: Run governance_counters.py → save as counters-run2.yaml
  - TC-GOV-022-06: Run diff script:
    python -c "
    import yaml, sys
    r1 = yaml.safe_load(open('reports/product-governance/counters-run1.yaml'))['governance_counters']['counters']
    r2 = yaml.safe_load(open('reports/product-governance/counters-run2.yaml'))['governance_counters']['counters']
    diffs = {k: (r1[k], r2[k]) for k in r1 if r1[k] != r2[k]}
    if diffs:
        print('FAIL: diffs=', diffs, file=sys.stderr); sys.exit(1)
    print('IDEMPOTENT: MATERIAL_SECOND_RUN_CHANGES = 0')
    "
  - TC-GOV-022-07: Write reports/product-governance/pilots/pilot10-idempotency-result.yaml

Acceptance check: diff script exits 0, prints IDEMPOTENT
Failure handling: If diffs exist, identify which tool produces different output on second run.
  Fix that tool to be deterministic (sorted output, consistent timestamps excluded from hash).
```

---

### Parent Taskcard TC-GOV-023 — Final Counter Verification + Report + Verdict

```
Parent Taskcard ID: TC-GOV-023
Title: Verify all 22 counters = 0; write final-report.md; assert FORMAT_FACTORY_PRODUCT_GOVERNANCE_HEALED
Type: PARENT
Status: PROPOSED
Dependencies: TC-GOV-022

Child taskcards:
  - TC-GOV-023-01: Run governance_counters.py → inspect all 22 counters
  - TC-GOV-023-02: For any counter > 0: identify which gap_record or tool computation is wrong; fix it
    (Counter #17 UNGOVERNED_PIPELINE_COMPONENTS and #18 UNGOVERNED_PRODUCT_ARTIFACTS should be 0
    because all have open gaps with task_ids — verify the counter logic reflects this definition)
  - TC-GOV-023-03: Write reports/product-governance/final-report.md containing:
    - All 22 counter values (must all be 0)
    - Lifecycle control summary
    - Structural enforcement repairs (Phase 1, TC-GOV-001 through TC-GOV-005)
    - Governance record system summary
    - All 10 pilot results (PASSED/FAILED per pilot)
    - Idempotency result
    - Remaining true external blockers
    - Final verdict: FORMAT_FACTORY_PRODUCT_GOVERNANCE_HEALED_TRACEABLE_AND_RELEASE_CONTROLLED
  - TC-GOV-023-04: grep 'FORMAT_FACTORY_PRODUCT_GOVERNANCE_HEALED' reports/product-governance/final-report.md → found
  - TC-GOV-023-05: Write reports/product-governance/governance-index.yaml (machine-readable index of all governance records)

Closeout condition: final-report.md contains the verdict string AND all 22 counters show 0 in counter report
```

---

## PART VII: VALIDATION MATRIX

```yaml
# artifact: validation-command-matrix
# authoritative_plan: plans/.claude/memoized-frolicking-donut.md
# artifact_role: analysis_or_evidence_only
# execution_authority: false

validation_matrix:
  - taskcard: TC-GOV-001
    type: unit_test
    command: ".venv/Scripts/pytest tests/supervisor/test_v119_v120_wired.py -v"
    expected: "4 passed, 0 failed"
    mandatory: true
    focused: true

  - taskcard: TC-GOV-001
    type: integration_test
    command: ".venv/Scripts/pytest tests/supervisor/ -x --timeout=60"
    expected: "no regression"
    mandatory: true
    regression: true

  - taskcard: TC-GOV-001
    type: configuration_enforcement
    command: "grep -n 'V119' tools/supervisor/check_continuation.py"
    expected: "line containing V119 in _STRUCTURAL_GOVBLOCK_VALIDATORS"
    mandatory: true

  - taskcard: TC-GOV-002
    type: unit_test
    command: ".venv/Scripts/pytest tests/supervisor/test_persistent_violation_stop.py -v"
    expected: "4 passed"
    mandatory: true

  - taskcard: TC-GOV-003
    type: unit_test
    command: ".venv/Scripts/pytest tests/supervisor/test_critical_rework_stop.py -v"
    expected: "4 passed"
    mandatory: true

  - taskcard: TC-GOV-004
    type: unit_test
    command: ".venv/Scripts/pytest tests/supervisor/test_blast_radius_check.py -v"
    expected: "4 passed"
    mandatory: true

  - taskcard: TC-GOV-005
    type: unit_test
    command: ".venv/Scripts/pytest tests/supervisor/test_phase14_git_crosscheck.py -v"
    expected: "4 passed"
    mandatory: true

  - taskcard: TC-GOV-006
    type: schema_validation
    command: "python tools/supervisor/validate_governance_schemas.py"
    expected: "8 OK lines, exit 0"
    mandatory: true

  - taskcard: TC-GOV-007
    type: configuration_enforcement
    command: "python tools/supervisor/validate_governance_binding.py"
    expected: "exit 0, all authority paths verified"
    mandatory: true

  - taskcard: TC-GOV-008
    type: api_cli
    command: "python tools/supervisor/governed_artifact_lookup.py query --path src/python/fods/__init__.py"
    expected: "JSON with artifact_id and status fields"
    mandatory: true

  - taskcard: TC-GOV-009
    type: api_cli
    command: "python tools/supervisor/change_proposal_manager.py list --status ACCEPTED"
    expected: "8+ records listed"
    mandatory: true

  - taskcard: TC-GOV-009
    type: schema_validation
    command: "python -c \"import yaml, jsonschema, json; schema=json.load(open('.supervisor/schemas/change-proposal.schema.json')); [jsonschema.validate(yaml.safe_load(open(f))['change_proposal'], schema) for f in __import__('glob').glob('registry/change-proposals/CP-*.yaml')]; print('All CP valid')\""
    expected: "All CP valid"
    mandatory: true

  - taskcard: TC-GOV-015
    type: configuration_enforcement
    command: "python tools/supervisor/governance_validator_runner.py 2>&1 | grep expected_count"
    expected: "expected_count=173"
    mandatory: true
    note: "NOT 167 or 171 — adding 6 validators to 167 = 173"

  - taskcard: TC-GOV-015
    type: regression_test
    command: ".venv/Scripts/pytest tests/supervisor/test_governance_validator_runner.py"
    expected: "assertion 173 == 173"
    mandatory: true

  - taskcard: TC-GOV-017
    type: unit_test
    command: ".venv/Scripts/pytest tests/fods/test_pilot_api.py -v"
    expected: "PASSED"
    mandatory: true

  - taskcard: TC-GOV-022
    type: idempotency
    command: "python -c \"import yaml,sys; r1=yaml.safe_load(open('reports/product-governance/counters-run1.yaml'))['governance_counters']['counters']; r2=yaml.safe_load(open('reports/product-governance/counters-run2.yaml'))['governance_counters']['counters']; diffs={k:(r1[k],r2[k]) for k in r1 if r1[k]!=r2[k]}; sys.exit(1 if diffs else 0)\""
    expected: "exit 0"
    mandatory: true

  - taskcard: TC-GOV-023
    type: final_verification
    command: "grep 'FORMAT_FACTORY_PRODUCT_GOVERNANCE_HEALED' reports/product-governance/final-report.md"
    expected: "found"
    mandatory: true

negative_controls:
  - test: "V119 does NOT fire on IMPLEMENTATION_VERIFIED file modification"
    command: "python -c \"from tools.supervisor.governance_validators_ext4 import validate_promoted_code_changed_without_reopening; r=validate_promoted_code_changed_without_reopening(['src/f'],{'src/f':{'state':'IMPLEMENTATION_VERIFIED'}}); assert r['passed']==True, r\""
    expected: "no AssertionError"

  - test: "check_continuation CONTINUE when rework_items appears only in current sprint (not prior)"
    location: tests/supervisor/test_persistent_violation_stop.py Test 1

  - test: "Phase 14 does NOT error when git unavailable"
    location: tests/supervisor/test_phase14_git_crosscheck.py Test 4

  - test: "RC-FODS-BREAKING-001 returns NOT_RELEASEABLE"
    location: TC-GOV-020-02 acceptance check
```

---

## PART VIII: EVIDENCE CONTRACT

```yaml
# artifact: evidence-contract
# authoritative_plan: plans/.claude/memoized-frolicking-donut.md
# artifact_role: analysis_or_evidence_only
# execution_authority: false

evidence_root: .local/evidences/gov-heal-001/
required_structure:
  run-record.yaml: "Sprint metadata, start/end time, git HEAD"
  analysis/:
    - plan-corrections.md  # Documents C1-C6 corrections from deep code read
  validation/:
    - test_v119_v120_wired_output.txt
    - test_persistent_violation_stop_output.txt
    - test_critical_rework_stop_output.txt
    - test_blast_radius_check_output.txt
    - test_phase14_git_crosscheck_output.txt
    - governance_validator_runner_count_output.txt  # shows 173
    - validate_governance_schemas_output.txt
    - validate_governance_binding_output.txt
    - pilot_api_test_output.txt
    - idempotency_diff_output.txt
  generated-artifacts/:
    - registry/governance-binding.yaml
    - registry/governed-artifact-registry.yaml
    - registry/promotion-record-ledger.yaml
    - reports/product-governance/final-report.md
    - reports/product-governance/governance-counter-report.yaml
  quality/:
    - quality-scores.yaml  # Per-taskcard quality scores (all dimensions >= 4/5)
  closeout/:
    - final-verdict.yaml   # FORMAT_FACTORY_PRODUCT_GOVERNANCE_HEALED_*

evidence_reference_rule: "Every evidence artifact references authoritative plan path and TC-GOV-* ID"
evidence_integrity_rule: "Evidence must be captured from actual command output, not reconstructed from memory"
```

---

## PART IX: TRADEOFFS AND KNOWN LIMITS (Preserved)

**Tradeoff T1: V119 as structural fires on ANY promoted file touch**
Risk: Legitimate sprint modifying a test file for a promoted format gets blocked.
Mitigation: V119 must scope to `src/**` only (not `tests/**`). If sprint modifies a promoted `src/` file AND updates `promotion-ledger.yaml` to REOPENED in the same sprint, V119 passes.

**Tradeoff T2: No PROMOTED_STABLE entries yet — V119 will not fire on real data currently**
V119 enforcement is in place for when formats reach PROMOTED_STABLE. Tests use synthetic fixtures. This is correct — the enforcement must be in place BEFORE formats are promoted, not after violations occur.

**Tradeoff T3: Persistent violation lookback = 1 sprint**
One-sprint window allows a legitimate rework sprint to proceed. If the fix doesn't work and the same validator fires again next sprint, it's blocked. Correct behavior.

**Tradeoff T4: expected_count 167→173 requires synchronized test update**
TC-GOV-015-03 and TC-GOV-015-04 must update runner AND test atomically. If out of order, test will fail with `167 != 173`. Plan enforces this by listing both as micro-steps in the same child taskcard.

**Tradeoff T5: Counters #17 and #18 reach 0 by task assignment, not full backfill**
Correct interpretation: counter = 0 means all ungoverned artifacts are IDENTIFIED and TASKED, not that they are fully governed. Final report must make this explicit.

**Known Limit L1: Phase 14 timing sensitivity**
If evidence declaration is filed BEFORE the sprint's git commit, Phase 14 will see empty git diff and skip silently. This is acceptable — the worst case is the cross-check is skipped, not that it produces false errors.

**Known Limit L2: V120 may be SKIPPED_NOT_APPLICABLE**
If `format-registry.yaml` does not contain `certification_status` or `architecture_classification` fields (which the deep code read suggests is likely), V120 must return passed=True and be marked as SKIPPED_NOT_APPLICABLE with reason "certification fields not present in format-registry.yaml". TC-GOV-001-04 investigates this and may conclude V120 enforcement is a future-sprint task.

---

## PART X: EXECUTION HANDOFF

```yaml
# artifact: execution-readiness-verdict + execution-handoff
# authoritative_plan: plans/.claude/memoized-frolicking-donut.md
# artifact_role: execution_handoff
# execution_authority: true (this section only — instructs agent on starting point)

execution_readiness_verdict: PLAN_MICRO_TASKCARDIZED_READY_FOR_EXECUTION

handoff:
  authoritative_plan: plans/.claude/memoized-frolicking-donut.md
  first_parent_taskcard: TC-GOV-001
  first_child_taskcard: TC-GOV-001-01
  first_micro_step: MS-GOV-001-01-01

execution_rules:
  1: Read the authoritative plan before starting any work
  2: Identify current parent taskcard (TC-GOV-001 to start)
  3: Read selected child taskcard before starting it
  4: Confirm preconditions are met
  5: Execute exactly ONE micro-step at a time
  6: Capture evidence immediately after each micro-step (stdout or file existence)
  7: Update micro-step status (ACTIVE → COMPLETE or FAILED)
  8: When all micro-steps in a child are COMPLETE: verify acceptance checks → mark child VERIFIED → score → mark CLOSED
  9: When all children of a parent are CLOSED: run parent integration checks → mark parent VERIFIED → score → mark CLOSED
  10: Move to next parent taskcard per the DAG (TC-GOV-002 depends on TC-GOV-001 CLOSED)
  11: Do NOT broaden scope — forbidden files per each taskcard are absolute
  12: Do NOT close a parent before all mandatory children are CLOSED
  13: Do NOT treat "file created" as evidence — run the validation command and capture its output

agent_must_not:
  - choose work outside the current taskcard's scope
  - close a parent taskcard when any child is not CLOSED
  - treat code existence as test passing
  - treat test file existence as evidence of tests passing
  - skip micro-steps silently
  - mark CLOSED without running the acceptance check commands

reroute_rule: "If any mandatory quality dimension scores below 4/5, mark taskcard REROUTED. Re-open the smallest necessary child taskcard. Do not abandon and move to next parent."

stop_conditions:
  - TRUE_EXTERNAL_GATE: Gate 11 G11-G commercial execution requires Babar Raza (blocks TC-GOV-023 release verdict)
  - If V120 investigation (TC-GOV-001-04) reveals format-registry.yaml lacks required fields: mark V120 as DEFERRED_WITH_REASON and continue; TC-GOV-001 closes without V120 fully enforced (L2 known limit)
  - If any Phase 1 test suite regresses (not just the new tests): STOP and fix before continuing to Phase 2
```

---

## PART XI: SUPPORTING ARTIFACTS INDEX

```yaml
# All 46 required deliverables — location in plan or to be created during execution
# authoritative_plan: plans/.claude/memoized-frolicking-donut.md
# artifact_role: analysis_or_evidence_only
# execution_authority: false

deliverables:
  1-enhanced-authoritative-plan: plans/.claude/memoized-frolicking-donut.md  # THIS FILE
  2-taskcardization-preflight: "PART II — PLAN AUTHORITY AND PREFLIGHT (embedded)"
  3-active-plan-authority-verdict: "PART II — active_plan_authority_verdict (embedded)"
  4-duplicate-plan-risk-check: "PART II — duplicate_plan_risk_check (embedded)"
  5-plan-section-inventory: "PART III — SECTION PROCESSING LEDGER below"
  6-plan-structure-normalization-profile: "PART II preflight (embedded)"
  7-section-processing-ledger: "created at .local/gov-heal-001/section-processing-ledger.yaml during TC-GOV-001"
  8-complete-plan-read-confirmation: "created at .local/gov-heal-001/complete-plan-read-confirmation.md during TC-GOV-001"
  9-plan-part-deep-analysis: "created at .local/gov-heal-001/plan-part-deep-analysis.yaml during TC-GOV-001"
  10-phase-section-step-analysis: "created at .local/gov-heal-001/phase-section-step-analysis.md"
  11-actionable-item-extraction-log: "PART II REQUIREMENTS INVENTORY (embedded as normalized-requirements-inventory)"
  12-actionable-to-source-traceability: "created at .local/gov-heal-001/actionable-to-source-traceability.csv"
  13-solution-options-analysis: "PART I CRITICAL CORRECTIONS + tradeoffs section"
  14-solution-option-scorecard: "created at .local/gov-heal-001/solution-option-scorecard.yaml"
  15-selected-solution-rationale: "PART I Design section (Enforcement-First) + TC-GOV-001 Source.Selected solution"
  16-normalized-requirements-inventory: "PART II REQUIREMENTS INVENTORY (embedded)"
  17-section-to-requirement-map: "created at .local/gov-heal-001/section-to-requirement-map.csv"
  18-requirement-to-parent-taskcard-map: "PART II req_id→parent_taskcard fields (embedded)"
  19-parent-to-child-taskcard-map: "each Parent Taskcard child_taskcards field (embedded)"
  20-child-to-micro-step-map: "each Child Taskcard micro-steps field (embedded)"
  21-end-to-end-execution-traceability: "created at .local/gov-heal-001/end-to-end-traceability.csv"
  22-parent-taskcards: "TC-GOV-001 through TC-GOV-023 (PART V and PART VI)"
  23-child-taskcards: "TC-GOV-001-01 through TC-GOV-023-05 (PART V and PART VI)"
  24-micro-step-records: "MS-GOV-001-01-01 through MS-GOV-005-04-04 (PART V)"
  25-execution-dag: "PART III EXECUTION DAG (embedded)"
  26-taskcard-dependency-matrix: "created at .local/gov-heal-001/taskcard-dependency-matrix.csv"
  27-file-ownership-and-locks: "PART III file_ownership_and_locks (embedded)"
  28-parallel-execution-safety-map: "PART III dag.TC-GOV-*.parallel_safe_with (embedded)"
  29-taskcard-state-machine: "PART IV STATE MACHINE (embedded)"
  30-taskcard-state-machine-validation-rules: "PART IV invalid_transitions (embedded)"
  31-verification-matrix: "PART VII VALIDATION MATRIX (embedded)"
  32-validation-command-matrix: "PART VII validation_matrix YAML (embedded)"
  33-negative-control-matrix: "PART VII negative_controls (embedded)"
  34-evidence-contract: "PART VIII EVIDENCE CONTRACT (embedded)"
  35-evidence-obligation-matrix: "created at .local/gov-heal-001/evidence-obligation-matrix.csv"
  36-evidence-to-taskcard-traceability: "PART VIII evidence_reference_rule"
  37-plan-reconciliation-report: "created at .local/gov-heal-001/plan-reconciliation-report.md after all TCs closed"
  38-no-actionable-item-loss-audit: "created at .local/gov-heal-001/no-actionable-item-loss-audit.md"
  39-taskcard-decomposition-quality-audit: "created at .local/gov-heal-001/taskcard-decomposition-quality-audit.md"
  40-single-plan-authority-audit: "PART II active_plan_authority_verdict (embedded)"
  41-contradiction-and-duplication-ledger: "created at .local/gov-heal-001/contradiction-and-duplication-ledger.yaml"
  42-idempotency-check: "TC-GOV-022 (Pilot 10) + reports/product-governance/pilots/pilot10-idempotency-result.yaml"
  43-duplicate-taskcard-detection-report: "created at .local/gov-heal-001/duplicate-taskcard-detection-report.md"
  44-stable-id-map: "TC-GOV-001 through TC-GOV-023 are derived from domain+section+sequence — stable"
  45-execution-readiness-verdict: "PART X EXECUTION HANDOFF execution_readiness_verdict field"
  46-final-execution-handoff: "PART X EXECUTION HANDOFF (embedded)"

note: "Artifacts marked 'created during execution' will be generated by the execution agent as part of each taskcard.
       They do NOT need to exist before execution begins. Their creation is part of the evidence obligation."
```

---

## SECTION PROCESSING LEDGER (Embedded)

```yaml
# artifact: section-processing-ledger
# authoritative_plan: plans/.claude/memoized-frolicking-donut.md
# artifact_role: analysis_or_evidence_only
# execution_authority: false

sections:
  - section_id: S-001
    title: "Plan Authority and Preflight"
    type: metadata
    analysis_completed: yes
    actionable_items_found: 0
    existing_taskcards_found: 0
    missing_taskcards: 0
    ambiguities: none
    change_status: ENHANCED (added full preflight YAML)

  - section_id: S-002
    title: "Critical Corrections from Deep Code Read"
    type: corrections
    analysis_completed: yes
    actionable_items_found: 6
    corrections: [C1-V119 skip, C2-V120 signature, C3-expected_count-167, C4-Phase14, C5-existing_rework_items, C6-no-PROMOTED_STABLE]
    change_status: NEW (added to plan)

  - section_id: S-003
    title: "Root Causes 1-7"
    type: analysis
    analysis_completed: yes
    actionable_items_found: 0  # analysis only; actions in taskcards
    change_status: PRESERVED

  - section_id: S-004
    title: "What Must Be Preserved"
    type: constraints
    analysis_completed: yes
    change_status: PRESERVED + ENHANCED (added existing_rework_items note)

  - section_id: S-005
    title: "Design: Enforcement-First"
    type: design_rationale
    analysis_completed: yes
    change_status: PRESERVED

  - section_id: S-006
    title: "Phase 1 — TC-GOV-001 through TC-GOV-005"
    type: execution
    analysis_completed: yes
    actionable_items_found: 5
    existing_taskcards_found: 5
    change_status: FULLY_MICRO_TASKCARDIZED (parent + children + micro-steps added)

  - section_id: S-007
    title: "Phase 2-8 — TC-GOV-006 through TC-GOV-023"
    type: execution
    analysis_completed: yes
    actionable_items_found: 18
    existing_taskcards_found: 18
    change_status: HARDENED (parent + children structure added)

  - section_id: S-008
    title: "Tradeoffs and Known Limits"
    type: risk_analysis
    analysis_completed: yes
    change_status: PRESERVED + ENHANCED (T5 clarification added)

  - section_id: S-009
    title: "Files Modified/Created Summary"
    type: reference
    analysis_completed: yes
    change_status: PRESERVED (embedded in file_ownership_and_locks)
```

---

## STABLE ID MAP

```yaml
# artifact: stable-id-map
# ID derivation: GOV=domain(governance_healing) + NNN=sequential per phase

stable_ids:
  # Phase 1 — Structural
  TC-GOV-001: "Wire V119/V120"
  TC-GOV-002: "Persistent violation detection"
  TC-GOV-003: "Rework classification"
  TC-GOV-004: "Blast radius wiring"
  TC-GOV-005: "Phase 14 git diff"

  # Phase 2-3 — Schemas + Registry
  TC-GOV-006: "8 JSON schemas"
  TC-GOV-007: "Governance binding record"
  TC-GOV-008: "Artifact registry + lookup"

  # Phase 4 — Records
  TC-GOV-009: "Retroactive CP/CI/CD"
  TC-GOV-010: "Promotion ledger + RC seeds"

  # Phase 5 — Tooling
  TC-GOV-011: "CP manager tool"
  TC-GOV-012: "Promotion + release tools"
  TC-GOV-013: "Counter tool"
  TC-GOV-014: "Ledger builder"

  # Phase 6 — Validators
  TC-GOV-015: "V150-V155, 167→173"

  # Phase 7 — Audit
  TC-GOV-016: "Lifecycle inventory"

  # Phase 8 — Pilots
  TC-GOV-017: "Pilot 1 — API change"
  TC-GOV-018: "Pilot 2 — Rejected change"
  TC-GOV-019: "Pilot 3 — Pipeline change"
  TC-GOV-020: "Pilots 4-7"
  TC-GOV-021: "Pilots 8-9"
  TC-GOV-022: "Pilot 10 — Idempotency"
  TC-GOV-023: "Final report"

id_stability_rule: "IDs are FIXED. On rerun, do not regenerate IDs. Repair only incomplete/stale content."
```

---

## FINAL SELF-REVIEW CHECKLIST

- entire_plan_read: yes
- every_relevant_plan_part_individually_analyzed: yes
- every_actionable_item_represented: yes
- every_broad_actionable_decomposed: yes
  - TC-GOV-001: 7 children + 21 micro-steps (Phase 1 fully decomposed)
  - TC-GOV-002 through TC-GOV-005: children + key micro-steps
  - TC-GOV-006 through TC-GOV-023: parent + children structure
- micro_steps_are_smallest_meaningful_units: yes
- scope_drift_controls_present: yes (allowed/forbidden files per child; allowed_operation per micro-step)
- parent_child_hierarchy_valid: yes
- taskcard_state_machine_valid: yes (PART IV)
- evidence_retained: yes (PART VIII)
- only_one_authoritative_plan_remains: yes
- plan_ready_for_execution: yes

**VERDICT: PLAN_MICRO_TASKCARDIZED_READY_FOR_EXECUTION**

Active Plan: plans/.claude/memoized-frolicking-donut.md
Next valid parent: TC-GOV-001
Next valid child: TC-GOV-001-01
First micro-step: MS-GOV-001-01-01 (Read governance_validator_runner.py lines 510-530)
