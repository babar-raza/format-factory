# Plan: Capability Layer Production Hardening
# Plan ID: humble-hatching-lark
# Type: capability_layer_healing
# Authority: C:\Users\prora\.claude\plans\humble-hatching-lark.md
# Revised: 2026-07-10 (third pass — micro-taskcardized, machine-state hardened)
# Status: READY_FOR_EXECUTION

---

## PART I — PREFLIGHT AND AUTHORITY

### Taskcardization Preflight

```yaml
# taskcardization-preflight
repository: c:\Users\prora\OneDrive\Documents\GitHub\format-factory
branch: main
head_commit: af879e55 (last known)
active_plan_path: C:\Users\prora\.claude\plans\humble-hatching-lark.md
active_plan_title: Capability Layer Production Hardening
plan_format: markdown_with_yaml_sections
authority_source: user_created_in_plan_mode_conversation
plan_size_lines: 609 (pre-enhancement)
major_section_count: 7
existing_taskcards: [TC-CL-001, TC-CL-002, TC-CL-003, TC-CL-004, TC-CL-005, TC-CL-006, TC-CL-007]
existing_taskcard_format: flat_phase_blocks_no_hierarchy
existing_state_vocabulary: [PENDING]
existing_validation_model: table_with_commands
existing_evidence_model: path_based_informal
existing_naming: TC-CL-### for capability layer
existing_execution_handoff: absent
duplicate_plan_risk: LOW
```

### Active Plan Authority Verdict

```yaml
# active-plan-authority-verdict
verdict: SINGLE_AUTHORITATIVE_PLAN_CONFIRMED
authoritative_path: C:\Users\prora\.claude\plans\humble-hatching-lark.md
competing_plans_found: false
candidates_inspected:
  - path: plans/master-plan.md
    role: master_project_plan
    conflict: none (different scope)
  - path: plans/layers/capability-layer.md
    role: L03_layer_plan_TC-CAP-001_entry
    conflict: none (upstream governance, not competing)
  - path: plans/.claude/
    role: prior_plan_versions_directory
    conflict: none (this plan supersedes)
duplicate_risk_resolution: not_needed
execution_authority: this_plan_only
```

### Duplicate Plan Risk Check

```yaml
# duplicate-plan-risk-check
risk: LOW
rationale: |
  Only one plan with this scope exists. plans/layers/capability-layer.md is upstream
  governance (L03 layer plan) and is a TARGET of this plan's TC-CL-004 and TC-CL-007,
  not a competing execution authority. No v2, final, or revised copies found.
action: none_required
```

### Plan Structure and Normalization Profile

```yaml
# plan-structure-and-normalization-profile
section_types_present: [analysis, diagnosis, preservation_rules, fix_specifications, phased_execution, validation_table, regression_controls, tradeoffs, status_table]
section_types_missing_before_enhancement: [preflight, authority, deep_analysis, requirements, solution_options, parent_child_hierarchy, micro_steps, machine_state, dependency_dag, validation_matrix, evidence_contract, reconciliation, execution_handoff]
naming_conventions:
  taskcard_ids: TC-CL-### (capability layer)
  child_ids: TC-CL-###-## (two-digit child suffix)
  micro_step_ids: MS-CL-###-##-## (child then step)
  requirement_ids: REQ-CL-### (capability layer)
normalization_decisions:
  - state_vocabulary_expanded: [PROPOSED, READY, IN_PROGRESS, CHILDREN_IN_PROGRESS, INTEGRATION_PENDING, VERIFIED, SCORED, CLOSED, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]
  - child_status_vocabulary: [TODO, READY, IN_PROGRESS, IMPLEMENTED, VERIFIED, SCORED, CLOSED, REROUTED, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]
  - micro_step_status: [PENDING, READY, ACTIVE, COMPLETE, FAILED, BLOCKED, SKIPPED_NOT_APPLICABLE]
```

---

## PART II — PRESERVED ANALYSIS (DO NOT MODIFY)

### Honest Assessment First

The first analysis catalogued what files exist and what files are absent. That missed the
point. The actual question is: **why does the system produce inconsistent or untrustworthy
results across reruns, and what would make it durable?**

Short answer: most of the infrastructure is wired and working. The real problems are
(1) a code bug that inflates verified capability counts, (2) a static gap-ledger that
cannot auto-track work done, (3) a two-track authority architecture that has never been
explicitly documented or bounded, and (4) work selection that silently falls back to
hardcoded expansion goals when the ledger is exhausted — with no signal that this has
happened.

None of these require rebuilding the pipeline. They require targeted surgical fixes,
clear semantics, and regression controls.

### Actual System State (Confirmed at HEAD, 2026-07-10)

#### What Is Working

- **capability_feature_compiler.py** is integrated into `autonomous_cycle.py` Step 4a.
  It reads `gap-ledger.json` (1,487 total gaps), filters to open non-deferred, and
  produced **8 work items** in the most recent run (DIF, FODS, FODT, PBM/PGM/PPM).
  `work_selection_mode = CAPABILITY_COMPILER_MERGED`.

- **gap-ledger-active.json** has 32 gaps: 30 `DEFERRED_BY_DESIGN`, 2 `DEFERRED`.
  These are **intentionally deferred** per TC-GAP-TRIAGE-001 (2026-06-24). Explicit
  blockers and unblock conditions exist. This is not backlog-clearing — it is a frozen
  frontier of scoped-out work.

- **gap-ledger-archive.json** has 1,447 closed gaps with closure receipts. The
  active/archive split is functioning correctly.

- **validate_capability_map.py** validators (VAL-001 through VAL-010) are sound.
  One class of hard failures exists (VAL-009, see below).

- **Content-normalized SHA writes** in capability_compiler.py prevent spurious
  regeneration. The design is correct.

- **poc-targets.yaml** works for its actual purpose: human-authored scope dashboard
  and POC status tracking. 19 targets, manually maintained.

#### What Is Actually Broken

**BUG 1 — False verification inflation (393 records)**
Location: `tools/capability_layer/capability_map_generator.py` lines 620-621.

The bug: the condition assigns `example_verified` when the FORMAT has any example
files (`example_count > 0`), not when the specific capability function is referenced
in any example file. This is a function-level check that accidentally uses a
format-level flag.

Result: 393 capability records carry `state=example_verified` with empty `example_refs`.
These should be `implementation_verified`. Affected formats: ABW(31), CSV(32), DIF(47),
FODG(11), FODP(5), Gnumeric(21), NDJSON(52), ODS(39), ODT(15), QOI(17), SYLK(29),
TOML(25), TSV(31), XCF(19), ZST(19).

Impact on trust: The "2,087 verified" count includes these 393. The actual breakdown is:
- test_verified: ~205 (9.8%) — genuinely verified
- implementation_verified: ~1,328 (63.6%) — source file exists
- example_verified real: ~161 (7.7%) — correct
- example_verified false: 393 (18.8%) — should be implementation_verified

**BUG 2 — VAL-009 hard failure (74 items)**
Location: `reports/capability-layer/action-queue.json` (stale, generated 2026-07-02).

74 action queue items have `advisory_only=false` when VAL-009 requires `advisory_only=true`.
The action-queue.json is 8 days stale. Regenerating it from the current ledger state
will fix both the staleness and the VAL-009 failures simultaneously.

**STRUCTURAL WEAKNESS 1 — Static gap-ledger with no autonomous closure**
The gap-ledger.json was last generated 2026-07-05. When sprint work closes a gap
(a test passes, an API is implemented), there is no automatic step in autonomous_cycle
that marks the corresponding gap as closed. Gaps drift out of sync with actual code state.

This is the primary consistency problem across reruns: the ledger reflects what WAS true
at generation time, not what IS true now. The 8 open work items produced by
capability_feature_compiler may already be done in the current working tree.

**STRUCTURAL WEAKNESS 2 — Two-track authority with no explicit boundary**
The system runs two parallel work selection tracks:
- Track A (POC scope): `poc-targets.yaml → select_poc_gaps.py → selected-product-gaps.json`
- Track B (Gap ledger): `gap-ledger.json → capability_feature_compiler → next-work-items.json`

Track B is authoritative for spec-grounded capabilities. Track A is authoritative for
non-ODF formats (CSV, TSV, TOML, SYLK, DIF, NDJSON, ABW, QOI, XCF, Gnumeric) where
no SAL facts exist because the SAL pipeline has no parsers for their specs. This is
not a bug — it is a necessary design choice given that CSV has no machine-readable
specification. But it has never been documented as a boundary.

When Track B produces 0 items (all gaps deferred/closed), `autonomous_task_generator.py`
falls back to hardcoded expansion goals. There is no log signal at the caller level
that says "compiler produced 0 items, falling back." Work continues, but its provenance
changes silently.

**STRUCTURAL WEAKNESS 3 — 0/2,087 capability records have obligation_ids**
The 169 ODF-format records produced by `capability_compiler.py` DO have proper
obligation_ids. The other 1,918 non-ODF records cannot have them until SAL ingestion
is done for each format's spec. `capability_compiler.py` exists and works for ODF formats
but is never invoked; its output (`sal-driven-capability-map.json`) has never been generated.

**STRUCTURAL WEAKNESS 4 — next-work-items.json accumulation (590 items)**
The `.local/supervisor/next-work-items.json` file has 590 items but capability_feature_compiler
produces at most 10 per run. The file appears to be cumulative from many runs or includes
expansion goal items.

### Root Causes (Distinct from Symptoms)

**Root Cause A — Code bug in state derivation (fixable, bounded)**
`example_count` (format-level) used instead of function-name match in example files.

**Root Cause B — Gap-ledger is not self-healing**
Sprint work does not feed back into ledger closure automatically. Ledger drifts from code truth.

**Root Cause C — SAL compiler is dormant but functional**
`capability_compiler.py` ready but never invoked. `capability_pipeline.py` exists but dormant.

**Root Cause D — Silent work-source fallback**
When `compile_gaps()` returns 0 items, expansion goals take over with no log signal.

**Root Cause E — Non-ODF format capability authority is undocumented**
10 non-ODF formats use poc-targets.yaml as de facto authority with no formal declaration.

### What to Preserve (Do Not Redesign)

1. gap-ledger-active.json / gap-ledger-archive.json split — working correctly
2. capability_feature_compiler.py Step 4a integration — working, produces 8 items
3. The 32 DEFERRED gap classifications — intentional, correct, well-documented
4. validate_capability_map.py validators VAL-001 to VAL-008 — sound design
5. poc-targets.yaml as human dashboard — correct tool for its stated purpose
6. Content-normalized SHA writes in capability_compiler.py — correct design
7. The two-track architecture — both tracks serve a legitimate purpose
8. 1,447 closed gaps in archive — historical record, do not disturb

### What NOT to Do

- Do not run capability_pipeline.py end-to-end as a first step (untested, risky)
- Do not add obligation_ids to all 2,087 records (non-ODF has no spec authority)
- Do not delete or supersede any DEFERRED gap
- Do not rebuild the gap-ledger from poc-targets alone

### Tradeoffs and Limits

**Tradeoff 1 — SAL ingestion for non-ODF formats:** The 10 non-ODF formats stay
`IMPLEMENTATION_ASSERTED` until /ingest-spec-sal runs per format. Lane 14-15 work.

**Tradeoff 2 — Flag-only gap closure:** Auto-close would repeat implementation_verified
error. Manual confirmation step remains.

**Tradeoff 3 — capability_pipeline.py incremental integration:** pipeline-run-manifest.json
may not exist until Phase 2 completes. Accept this.

**Tradeoff 4 — archive not re-verified:** 1,447 closed gaps not audited. Out of scope.

**What this plan cannot guarantee:**
- That the 8 open gap items are not already done in the working tree.
- That capability_pipeline.py passes all stages without further fixes.
- That expansion goal fallback produces the highest-priority product work.

---

## PART III — SECTION PROCESSING LEDGER

```yaml
# section-processing-ledger.yaml
sections:
  - id: S01
    title: "Honest Assessment First"
    type: analysis_and_diagnosis
    analysis_completed: yes
    actionable_items: 0
    existing_taskcards: 0
    enhancement_required: preserve_only
    change_status: PRESERVED

  - id: S02
    title: "Actual System State — What Is Working"
    type: verified_baseline
    analysis_completed: yes
    actionable_items: 0
    existing_taskcards: 0
    enhancement_required: preserve_only
    change_status: PRESERVED

  - id: S03
    title: "What Is Actually Broken — BUG 1"
    type: defect_diagnosis
    analysis_completed: yes
    actionable_items: 1
    root_requirement: REQ-CL-001
    missing_taskcards: [TC-CL-001 needs children and micro-steps]
    change_status: ENHANCED_WITH_HIERARCHY

  - id: S04
    title: "What Is Actually Broken — BUG 2"
    type: defect_diagnosis
    analysis_completed: yes
    actionable_items: 1
    root_requirement: REQ-CL-002
    missing_taskcards: [TC-CL-002 needs children and micro-steps]
    change_status: ENHANCED_WITH_HIERARCHY

  - id: S05
    title: "Structural Weakness 1 — Static gap-ledger"
    type: structural_gap
    analysis_completed: yes
    actionable_items: 1
    root_requirement: REQ-CL-003
    missing_taskcards: [TC-CL-005 needs children and micro-steps]
    change_status: ENHANCED_WITH_HIERARCHY

  - id: S06
    title: "Structural Weakness 2 — Two-track authority"
    type: structural_gap
    analysis_completed: yes
    actionable_items: 1
    root_requirement: REQ-CL-004
    missing_taskcards: [TC-CL-004 needs children and micro-steps]
    change_status: ENHANCED_WITH_HIERARCHY

  - id: S07
    title: "Structural Weakness 3 — 0/2087 obligation_ids"
    type: structural_gap
    analysis_completed: yes
    actionable_items: 2
    root_requirements: [REQ-CL-005, REQ-CL-006]
    missing_taskcards: [TC-CL-003 needs children and micro-steps]
    change_status: ENHANCED_WITH_HIERARCHY

  - id: S08
    title: "Structural Weakness 4 — next-work-items accumulation"
    type: structural_gap
    analysis_completed: yes
    actionable_items: 1
    root_requirement: REQ-CL-007
    missing_taskcards: [TC-CL-006 needs children and micro-steps]
    change_status: ENHANCED_WITH_HIERARCHY

  - id: S09
    title: "Fix 1 — State derivation bug"
    type: fix_specification
    analysis_completed: yes
    actionable_items: 4
    root_requirements: [REQ-CL-001, REQ-CL-008, REQ-CL-009]
    ambiguity: exact_function_name_in_generator_not_confirmed
    change_status: ENHANCED_WITH_CHILDREN

  - id: S10
    title: "Fix 2 — authority_class field"
    type: fix_specification
    analysis_completed: yes
    actionable_items: 3
    root_requirements: [REQ-CL-005, REQ-CL-006]
    change_status: ENHANCED_WITH_CHILDREN

  - id: S11
    title: "Fix 3 — SAL compiler invocation"
    type: fix_specification
    analysis_completed: yes
    actionable_items: 3
    root_requirements: [REQ-CL-005, REQ-CL-010]
    ambiguity: capability_pipeline_stage_flag_existence_unconfirmed
    change_status: ENHANCED_WITH_CHILDREN

  - id: S12
    title: "Fix 4 — Gap closure detection"
    type: fix_specification
    analysis_completed: yes
    actionable_items: 4
    root_requirement: REQ-CL-003
    change_status: ENHANCED_WITH_CHILDREN

  - id: S13
    title: "Fix 5 — Work-source fallback auditability"
    type: fix_specification
    analysis_completed: yes
    actionable_items: 2
    root_requirements: [REQ-CL-004, REQ-CL-007]
    change_status: ENHANCED_WITH_CHILDREN

  - id: S14
    title: "Fix 6 — Regenerate action-queue"
    type: fix_specification
    analysis_completed: yes
    actionable_items: 3
    root_requirement: REQ-CL-002
    ambiguity: action_queue_generator_cli_not_confirmed
    change_status: ENHANCED_WITH_CHILDREN

  - id: S15
    title: "Regression Controls"
    type: governance_controls
    analysis_completed: yes
    actionable_items: 5
    root_requirements: [REQ-CL-009, REQ-CL-011, REQ-CL-012, REQ-CL-013, REQ-CL-014]
    change_status: ENHANCED_WITH_VALIDATORS

  - id: S16
    title: "Phase 1 / 2 / 3 Execution"
    type: phased_execution
    analysis_completed: yes
    actionable_items: 7
    existing_taskcards: TC-CL-001 through TC-CL-007
    taskcard_quality: flat_no_hierarchy
    change_status: REPLACED_WITH_FULL_HIERARCHY
```

---

## PART IV — REQUIREMENTS INVENTORY

```yaml
# normalized-requirements-inventory.yaml
requirements:
  - id: REQ-CL-001
    title: "Fix example_verified false assignment bug"
    source_section: S03 / Fix-1
    root_cause: A
    parent_taskcard: TC-CL-001
    priority: P0
    type: bug_fix
    scope: tools/capability_layer/capability_map_generator.py

  - id: REQ-CL-002
    title: "Regenerate action-queue.json and pass VAL-009"
    source_section: S04 / Fix-6
    root_cause: A (stale artifact)
    parent_taskcard: TC-CL-002
    priority: P0
    type: artifact_regeneration
    scope: reports/capability-layer/action-queue.json

  - id: REQ-CL-003
    title: "Add gap closure detection feedback loop"
    source_section: S05 / Fix-4
    root_cause: B
    parent_taskcard: TC-CL-005
    priority: P1
    type: new_feature
    scope: tools/supervisor/autonomous_cycle.py

  - id: REQ-CL-004
    title: "Document two-track authority boundary explicitly"
    source_section: S06 / Fix-2 (partially) / TC-CL-004
    root_cause: E
    parent_taskcard: TC-CL-004
    priority: P1
    type: documentation_and_governance
    scope: reports/capability-layer/capability-authority-model.yaml

  - id: REQ-CL-005
    title: "Invoke SAL compiler to produce sal-driven-capability-map.json"
    source_section: S07 / Fix-3
    root_cause: C
    parent_taskcard: TC-CL-003
    priority: P1
    type: missing_integration
    scope: tools/capability_layer/capability_compiler.py

  - id: REQ-CL-006
    title: "Add authority_class field to capability records"
    source_section: S10 / Fix-2
    root_cause: E
    parent_taskcard: TC-CL-003
    priority: P1
    type: schema_extension
    scope: tools/capability_layer/capability_map_generator.py + unified-capability-map.json

  - id: REQ-CL-007
    title: "Make work-source fallback explicit via work_selection_mode field"
    source_section: S08 / Fix-5
    root_cause: D
    parent_taskcard: TC-CL-006
    priority: P1
    type: auditability
    scope: tools/supervisor/autonomous_cycle.py

  - id: REQ-CL-008
    title: "Add regression tests for state derivation"
    source_section: S09 / Fix-1
    root_cause: A
    parent_taskcard: TC-CL-001
    priority: P1
    type: test_coverage
    scope: tests/capability_layer/

  - id: REQ-CL-009
    title: "Add VAL-011 validator (no example_verified with empty example_refs)"
    source_section: S15 Regression Controls
    root_cause: A
    parent_taskcard: TC-CL-001
    priority: P1
    type: governance_validator
    scope: tools/capability_layer/validate_capability_map.py

  - id: REQ-CL-010
    title: "Integrate SAL compiler invocation as best-effort step in autonomous_cycle"
    source_section: S11 / Fix-3
    root_cause: C
    parent_taskcard: TC-CL-003
    priority: P2
    type: integration
    scope: tools/supervisor/autonomous_cycle.py

  - id: REQ-CL-011
    title: "Add VAL-012 advisory validator (action-queue staleness > 14 days)"
    source_section: S15 Regression Controls
    root_cause: A (stale artifact)
    parent_taskcard: TC-CL-002
    priority: P2
    type: governance_validator
    scope: tools/capability_layer/validate_capability_map.py

  - id: REQ-CL-012
    title: "Add work_selection_mode assertion in autonomous_cycle.py"
    source_section: S15 Regression Controls
    root_cause: D
    parent_taskcard: TC-CL-006
    priority: P2
    type: runtime_assertion
    scope: tools/supervisor/autonomous_cycle.py

  - id: REQ-CL-013
    title: "Add SAL-grounded count monotonicity check"
    source_section: S15 Regression Controls
    root_cause: C
    parent_taskcard: TC-CL-007
    priority: P2
    type: regression_control
    scope: tools/capability_layer/capability_pipeline.py

  - id: REQ-CL-014
    title: "Final idempotency proof (double-run SHA comparison)"
    source_section: TC-CL-007
    root_cause: all
    parent_taskcard: TC-CL-007
    priority: P1
    type: idempotency_verification
    scope: tools/capability_layer/capability_map_generator.py + capability_compiler.py

  - id: REQ-CL-015
    title: "Update L03 layer plan to maturity 5/5 on completion"
    source_section: TC-CL-007
    root_cause: governance
    parent_taskcard: TC-CL-007
    priority: P2
    type: governance_update
    scope: plans/layers/capability-layer.md
```

---

## PART V — SOLUTION OPTIONS ANALYSIS

For the two highest-risk changes (Bug 1 fix and action-queue regeneration), solution
options were considered. Others are straightforward integrations with one viable path.

### Bug 1 — State Derivation Fix Options

```yaml
# solution-option-scorecard.yaml (BUG-1)
options:
  A_minimal_surgical:
    description: "Add _scan_example_file_refs(), change one condition at lines 620-621"
    root_cause_coverage: 5  # fully addresses RC-A
    production_durability: 4
    rerun_consistency: 5
    implementation_safety: 5
    testability: 5
    maintainability: 4
    integration_completeness: 4
    regression_risk: 1  # very low
    selected: true
    rationale: "Bounded change, high testability, zero execution path impact"

  B_structural_hardening:
    description: "Rebuild state derivation with evidence-graph model"
    root_cause_coverage: 5
    production_durability: 5
    rerun_consistency: 5
    implementation_safety: 2  # risky, large change
    testability: 3
    maintainability: 5
    integration_completeness: 5
    regression_risk: 4  # high
    selected: false
    rationale: "Over-engineers a one-line fix; high regression risk"

  C_do_nothing_plus_documentation:
    description: "Document the mislabeling, do not fix code"
    root_cause_coverage: 1
    selected: false
    rationale: "Does not fix the integrity problem"
```

### Fix 6 — Action Queue Regeneration Options

```yaml
# solution-option-scorecard.yaml (FIX-6)
investigation_required: true
ambiguity: "capability_pipeline.py --stage flag existence is unconfirmed"
options:
  A_pipeline_stage_flag:
    description: "python tools/capability_layer/capability_pipeline.py --stage action_queue_only"
    risk: "May not exist; needs confirmation in TC-CL-002-01"

  B_standalone_generator_script:
    description: "Identify standalone action queue script; invoke directly"
    risk: "May require reading capability_pipeline.py source to find it"

  C_add_stage_flag_if_missing:
    description: "Add --stage action_queue_only to capability_pipeline.py if absent"
    risk: "Requires code change to pipeline; higher scope"

resolution: "TC-CL-002-01 INVESTIGATION taskcard resolves this before implementation"
```

---

## PART VI — DEEP ANALYSIS PER PLAN PART

```yaml
# plan-part-deep-analysis.yaml
parts:
  - plan_part_id: PP-001
    title: "Fix state derivation bug"
    objective: "Correct example_verified false assignment in capability_map_generator.py"
    root_causes_addressed: [RC-A]
    affected_components:
      - tools/capability_layer/capability_map_generator.py (lines 620-621 and new helper)
      - tests/capability_layer/test_state_derivation.py (new file)
      - tools/capability_layer/validate_capability_map.py (new VAL-011)
      - reports/capability-layer/unified-capability-map.json (regenerated)
    preserved_behavior:
      - state machine values unchanged (test_verified/example_verified/implementation_verified stay)
      - no execution path affected (state is metadata only)
      - existing VAL-001 to VAL-010 remain untouched
    inputs:
      - tools/capability_layer/capability_map_generator.py (current source)
      - examples/ directory structure (for _scan_example_file_refs)
    outputs:
      - fixed capability_map_generator.py
      - new _scan_example_file_refs() function
      - tests/capability_layer/test_state_derivation.py (3 tests)
      - updated validate_capability_map.py with VAL-011
      - regenerated unified-capability-map.json
    failure_modes:
      - helper function reads too many large files → performance degradation
        mitigation: cache reads keyed by file path
      - fn_name substring matches partial names (e.g., 'write' matches 'write_tsv')
        mitigation: check for fn_name followed by '(' in file contents
    ambiguities:
      - exact function name in generator that assigns example_verified (likely _determine_state)
      - exact parameter names (example_count, example_files, fn_name)
    investigation_required: YES — TC-CL-001-01 reads lines 600-650 to confirm
    smallest_safe_sequence:
      1. read generator source to confirm bug location
      2. add _scan_example_file_refs() as a new private function
      3. change one condition at the confirmed line
      4. write failing test first, then verify fix makes it pass
      5. regenerate maps, count state changes
      6. add VAL-011 to prevent regression

  - plan_part_id: PP-002
    title: "Regenerate action-queue.json"
    objective: "Produce fresh action-queue.json passing VAL-009"
    root_causes_addressed: [stale_artifact]
    affected_components:
      - reports/capability-layer/action-queue.json
      - tools/capability_layer/validate_capability_map.py (VAL-009 check)
      - tools/capability_layer/capability_pipeline.py or standalone generator
    inputs:
      - reports/capability-layer/gap-ledger-active.json (32 DEFERRED gaps)
    outputs:
      - regenerated action-queue.json (all items advisory_only=true)
      - validate_capability_map.py VAL-009 PASS
    ambiguities:
      - action queue generator CLI is unconfirmed
    investigation_required: YES — TC-CL-002-01 identifies the generator tool first

  - plan_part_id: PP-003
    title: "SAL compiler invocation + authority_class"
    objective: "Run capability_compiler.py for first time; add authority_class to all records"
    root_causes_addressed: [RC-C, RC-E]
    affected_components:
      - tools/capability_layer/capability_compiler.py (invoke, do not modify)
      - tools/capability_layer/capability_map_generator.py (add authority_class output)
      - tools/supervisor/autonomous_cycle.py (add best-effort invocation)
      - reports/capability-layer/sal-driven-capability-map.json (new file)
      - reports/capability-layer/unified-capability-map.json (enriched)
    preserved_behavior:
      - content-normalized SHA writes in capability_compiler.py MUST NOT be removed
      - capability_compiler.py invoked as subprocess only; not imported (avoids state pollution)
    failure_modes:
      - capability_compiler.py fails at runtime → best-effort wrapper absorbs silently
      - obligation_ids missing for some ODF formats → count < 169; investigate but do not block
    ambiguities:
      - exact --output path accepted by capability_compiler.py (likely positional or --output)
    investigation_required: YES — TC-CL-003-01 reads compiler source for CLI API

  - plan_part_id: PP-004
    title: "Document two-track authority boundary"
    objective: "Make ODF vs non-ODF authority split explicit in governance artifacts"
    root_causes_addressed: [RC-E]
    affected_components:
      - reports/capability-layer/capability-authority-model.yaml
      - reports/capability-layer/capability-consumer-graph.yaml
      - plans/layers/capability-layer.md (maturity 4/5)
    preserved_behavior:
      - do not change how Track A or Track B work; only document the boundary
    investigation_required: NO

  - plan_part_id: PP-005
    title: "Gap closure detection"
    objective: "Add flag-only scanner to autonomous_cycle.py; produce gap-closure-candidates.json"
    root_causes_addressed: [RC-B]
    affected_components:
      - tools/supervisor/autonomous_cycle.py (new _check_gap_closure function + scanner loop)
      - .local/capability-layer/gap-closure-candidates.json (new output file)
    preserved_behavior:
      - MUST NOT auto-close gaps (flag only)
      - MUST NOT slow the cycle by more than 5 seconds (only 8 open gaps to check)
    failure_modes:
      - test_refs reference non-existent paths → function returns False correctly
      - .local/capability-layer/ directory does not exist → must be created by scanner
    investigation_required: YES — TC-CL-005-01 reads autonomous_cycle.py to find insertion point

  - plan_part_id: PP-006
    title: "Work-source fallback auditability"
    objective: "Add work_selection_mode field; make expansion goal fallback visible"
    root_causes_addressed: [RC-D]
    affected_components:
      - tools/supervisor/autonomous_cycle.py (Step 4a block, lines 1571-1589)
    preserved_behavior:
      - expansion goals are NOT removed (valid fallback for non-ODF formats)
      - compile_gaps call unchanged; only the else-branch logging changes
    investigation_required: NO — exact lines confirmed (1571-1589)

  - plan_part_id: PP-007
    title: "Final validation and idempotency proof"
    objective: "Verify all fixes hold; prove double-run produces no content churn"
    root_causes_addressed: [all]
    affected_components:
      - all generated capability layer artifacts
      - plans/layers/capability-layer.md
      - reports/capability-layer/capability-layer-healing-report.md (new)
    investigation_required: NO
```

---

## PART VII — HIERARCHICAL TASKCARDS WITH MICRO-STEPS

---

### TC-CL-001: Fix State Derivation Bug + Regression Guards

```yaml
Parent Taskcard ID: TC-CL-001
Title: "Fix false example_verified assignment and add regression guards"
Type: PARENT
Status: READY
Owner: implementation_agent
Supervisor: governance_lane

Source:
  Plan requirement IDs: [REQ-CL-001, REQ-CL-008, REQ-CL-009]
  Plan section: "BUG 1 / Fix 1 / Regression Controls item 1"
  Root cause: RC-A
  Deep analysis: PP-001
  Selected solution: Option A (minimal surgical)

Objective:
  - Correct the example_verified state assignment to check function-level evidence,
    not format-level example count. Add a regression test suite and VAL-011 validator.

Outcome:
  - 393 records previously labeled example_verified are relabeled implementation_verified
  - No example_verified record has empty example_refs
  - VAL-011 prevents future regressions
  - Tests confirm the fix holds across regeneration

Scope:
  Allowed files:
    - tools/capability_layer/capability_map_generator.py
    - tools/capability_layer/validate_capability_map.py
    - tests/capability_layer/test_state_derivation.py (create)
    - tests/capability_layer/__init__.py (create if absent)
    - reports/capability-layer/unified-capability-map.json (regenerated)
    - reports/capability-layer/commercial-capability-map.json (regenerated)
    - reports/capability-layer/foss-reduced-capability-map.json (regenerated)
    - reports/capability-layer/capability_summary.json (regenerated)
  Forbidden files:
    - gap-ledger.json (do not touch)
    - gap-ledger-active.json (do not touch)
    - action-queue.json (TC-CL-002 scope)
    - autonomous_cycle.py (TC-CL-003+ scope)

Preserved behavior:
  - state machine vocabulary (test_verified, example_verified, implementation_verified, missing)
  - existing validators VAL-001 to VAL-010 semantics
  - no execution control path affected (state is metadata only)
  - content-normalized SHA writes in capability_map_generator.py

Inputs:
  - tools/capability_layer/capability_map_generator.py (current source)
  - examples/ directory (for verifying _scan_example_file_refs)

Outputs:
  - Patched capability_map_generator.py with _scan_example_file_refs()
  - Updated validate_capability_map.py with VAL-011
  - tests/capability_layer/test_state_derivation.py (3 tests minimum)
  - Regenerated capability maps

Dependencies:
  - None (first taskcard, no prerequisites)

Child taskcards:
  - TC-CL-001-01 (investigate bug location)
  - TC-CL-001-02 (implement _scan_example_file_refs)
  - TC-CL-001-03 (patch state derivation condition)
  - TC-CL-001-04 (write regression tests)
  - TC-CL-001-05 (add VAL-011 validator)
  - TC-CL-001-06 (regenerate maps, verify correction)

Parent acceptance criteria:
  - python -c "import json; m=json.load(open('reports/capability-layer/unified-capability-map.json')); bad=[c for c in m.get('capabilities',[]) if c.get('current_state')=='example_verified' and not c.get('example_refs')]; print(len(bad))" outputs 0
  - .venv/Scripts/pytest tests/capability_layer/test_state_derivation.py → all pass
  - python tools/capability_layer/validate_capability_map.py → VAL-011 PASS

Quality dimensions:
  - requirement_correctness: target 5/5
  - implementation_correctness: target 5/5
  - scope_discipline: target 5/5
  - validation_strength: target 5/5
  - evidence_completeness: target 4/5
  - regression_safety: target 5/5
  - production_readiness: target 4/5

Closeout criteria:
  - all 6 children CLOSED
  - parent acceptance criteria pass
  - evidence: before/after state counts documented

Rollback strategy:
  - git restore tools/capability_layer/capability_map_generator.py
  - git restore tools/capability_layer/validate_capability_map.py
  - re-run capability_map_generator.py to restore previous maps

Stop conditions:
  - If _scan_example_file_refs causes >10s performance regression: defer to TC-CL-001-02
    reroute for caching optimization before continuing

Reroute rule:
  - Any child quality gate below 4/5 → mark child REROUTED, create repair child
```

#### TC-CL-001-01: Investigate and map bug location

```yaml
Child Taskcard ID: TC-CL-001-01
Parent Taskcard ID: TC-CL-001
Title: "Read capability_map_generator.py and confirm exact bug location"
Type: CHILD
Status: READY
Owner: investigation_agent

Source:
  Plan requirement ID: REQ-CL-001
  Plan section: "Fix 1 — Correct the state derivation bug"
  Parent objective: Fix example_verified false assignment
  Analysis finding: PP-001 — exact function name unconfirmed, investigation required

Purpose:
  - Confirm the exact function name, line numbers, and parameter names so
    TC-CL-001-02 and TC-CL-001-03 can make precisely targeted changes.

Scope:
  Allowed files: [tools/capability_layer/capability_map_generator.py]
  Forbidden files: all others
  Read-only: true

Inputs:
  - tools/capability_layer/capability_map_generator.py

Expected output:
  - Recorded: function name that assigns example_verified
  - Recorded: exact line numbers (expected ~620-621 per diagnosis)
  - Recorded: parameter names (example_count, example_files or equivalent)
  - Recorded: call chain (what calls this function, what it receives)
  - Recorded: how example_count is currently set (format-level or function-level)
  - Recorded: what example_files contains (list of paths or count)
  - Confirmed or corrected: the proposed _scan_example_file_refs approach is valid

Preconditions:
  - tools/capability_layer/capability_map_generator.py exists (confirmed)

Micro-steps:
  MS-CL-001-01-01: Read lines 1-50 to understand module imports and top-level constants
  MS-CL-001-01-02: Read lines 580-650 (known region of state derivation function)
  MS-CL-001-01-03: Locate the function that returns "example_verified" string
  MS-CL-001-01-04: Record exact function name, signature, and parameter list
  MS-CL-001-01-05: Find how example_count is computed — is it len(example_files) or separate?
  MS-CL-001-01-06: Find how example_files is populated — format-level enumeration confirmed?
  MS-CL-001-01-07: Confirm the if-condition at the suspected line is format-level (bug confirmed)
  MS-CL-001-01-08: Check if example_files is already a list of paths (sufficient for scan)
  MS-CL-001-01-09: Record findings in child taskcard evidence section

Acceptance checks:
  - Exact line number(s) of bug recorded
  - Function signature recorded with all parameter names
  - Bug confirmed: example_count is format-level, not function-level
  - _scan_example_file_refs approach confirmed viable OR alternative identified

Evidence required:
  - Annotated source excerpt showing the bug
  - Parameter list with types
  - Call chain summary

Closeout criteria:
  - All micro-steps COMPLETE
  - Bug location confirmed in writing (not from memory)

Rollback plan:
  - N/A (read-only investigation)
```

| Micro-step ID | Status | Action | Target File:Lines | Expected Output |
|---|---|---|---|---|
| MS-CL-001-01-01 | PENDING | Read module imports | capability_map_generator.py:1-50 | known imports recorded |
| MS-CL-001-01-02 | PENDING | Read state derivation region | :580-650 | function identified |
| MS-CL-001-01-03 | PENDING | Locate "example_verified" return statement | :600-650 | exact line noted |
| MS-CL-001-01-04 | PENDING | Record function name and signature | :function def line | name + params recorded |
| MS-CL-001-01-05 | PENDING | Trace how example_count is set | :nearby lines | format-level or fn-level confirmed |
| MS-CL-001-01-06 | PENDING | Trace how example_files is populated | :call site | list of paths or count confirmed |
| MS-CL-001-01-07 | PENDING | Confirm bug condition (example_count > 0 is format-level) | :bug line | BUG CONFIRMED or CORRECTED |
| MS-CL-001-01-08 | PENDING | Check example_files is usable for scan | :same function | YES or NEEDS_ADAPTATION |
| MS-CL-001-01-09 | PENDING | Record all findings in taskcard evidence | plan file notes | findings documented |

---

#### TC-CL-001-02: Implement _scan_example_file_refs helper

```yaml
Child Taskcard ID: TC-CL-001-02
Parent Taskcard ID: TC-CL-001
Title: "Add _scan_example_file_refs(example_files, fn_name) to capability_map_generator.py"
Type: CHILD
Status: TODO
Owner: implementation_agent

Preconditions:
  - TC-CL-001-01 CLOSED (bug location confirmed, example_files is a list of paths)

Purpose:
  - Provide a function-level check: does this specific fn_name appear in any example file?

Scope:
  Allowed files: [tools/capability_layer/capability_map_generator.py]
  Forbidden: all other files

Expected output:
  - New private function _scan_example_file_refs(example_files: list, fn_name: str) -> bool
  - Function reads each file in example_files and checks if fn_name appears as a call
  - Cache mechanism keyed by file path (avoid re-reading same file for each fn_name)
  - Handles FileNotFoundError gracefully (returns False)
  - Check: fn_name + "(" to avoid substring matches (e.g., "write" matching "write_tsv")

Micro-steps:
  MS-CL-001-02-01: After TC-CL-001-01, confirm example_files element type (string paths)
  MS-CL-001-02-02: Add module-level cache dict _EXAMPLE_FILE_CACHE = {} near top of file
  MS-CL-001-02-03: Write _scan_example_file_refs function (pattern: fn_name + "(")
  MS-CL-001-02-04: Add try/except FileNotFoundError → return False in the function
  MS-CL-001-02-05: Manually trace function with one known example (e.g., FODS export_csv) to verify
  MS-CL-001-02-06: Read 5-10 lines of one real example file to confirm fn_name pattern is correct

Acceptance checks:
  - Function exists in module namespace
  - Returns True when fn_name + "(" is in file contents
  - Returns False when fn_name not in any example file
  - Returns False on FileNotFoundError
  - Does not call os.listdir or glob (only uses provided example_files list)

Evidence required:
  - Function code captured in evidence
  - Manual trace result documented

Closeout criteria:
  - Function written and manually verified
  - No broader changes to the file (other than cache dict + function)
```

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-001-02-01 | PENDING | Confirm element type of example_files | TC-CL-001-01 findings | string paths confirmed |
| MS-CL-001-02-02 | PENDING | Add _EXAMPLE_FILE_CACHE = {} near file top | :~line 30 | cache dict added |
| MS-CL-001-02-03 | PENDING | Write _scan_example_file_refs(example_files, fn_name) | :after cache | function written |
| MS-CL-001-02-04 | PENDING | Add FileNotFoundError handler inside function | :function body | graceful failure |
| MS-CL-001-02-05 | PENDING | Manual trace: call with known fn_name in known example | local trace | returns True |
| MS-CL-001-02-06 | PENDING | Read one real example file to confirm pattern assumption | examples/ | pattern valid |

---

#### TC-CL-001-03: Patch state derivation condition

```yaml
Child Taskcard ID: TC-CL-001-03
Parent Taskcard ID: TC-CL-001
Title: "Replace format-level example_count check with function-level _scan_example_file_refs call"
Type: CHILD
Status: TODO
Owner: implementation_agent

Preconditions:
  - TC-CL-001-01 CLOSED (exact line confirmed)
  - TC-CL-001-02 CLOSED (_scan_example_file_refs implemented)

Purpose:
  - Apply the fix at the confirmed bug location (expected lines 620-621).

Scope:
  Allowed files: [tools/capability_layer/capability_map_generator.py]
  Change size: 1-3 lines (one condition replaced)

Expected output:
  - Old: `if example_count > 0:`
  - New: `if _scan_example_file_refs(example_files, fn_name):`
  - Update confidence value for example_verified state if it was tied to example_count
  - Do NOT change test_verified branch

Micro-steps:
  MS-CL-001-03-01: Navigate to confirmed bug line (from TC-CL-001-01 findings)
  MS-CL-001-03-02: Replace condition; verify the rest of the if-block is unchanged
  MS-CL-001-03-03: Read the patched function in full to confirm no unintended changes
  MS-CL-001-03-04: Run a quick import check: python -c "from tools.capability_layer.capability_map_generator import _scan_example_file_refs; print('OK')"

Acceptance checks:
  - Exactly one condition changed
  - No other lines modified
  - Import check passes

Closeout criteria:
  - Change applied and import-checked
```

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-001-03-01 | PENDING | Navigate to bug line | :620-621 (or confirmed line) | correct line identified |
| MS-CL-001-03-02 | PENDING | Replace example_count > 0 with _scan_example_file_refs call | :confirmed line | one line changed |
| MS-CL-001-03-03 | PENDING | Read patched function in full | :whole function | no unintended changes |
| MS-CL-001-03-04 | PENDING | Run import check | shell | prints OK |

---

#### TC-CL-001-04: Write regression test suite

```yaml
Child Taskcard ID: TC-CL-001-04
Parent Taskcard ID: TC-CL-001
Title: "Create tests/capability_layer/test_state_derivation.py with 3 targeted tests"
Type: CHILD
Status: TODO
Owner: test_agent

Preconditions:
  - TC-CL-001-02 CLOSED (_scan_example_file_refs exists and is importable)

Scope:
  Allowed files:
    - tests/capability_layer/test_state_derivation.py (create)
    - tests/capability_layer/__init__.py (create if absent)
  Forbidden: modifying any capability_layer production source in this child

Expected output:
  Test file with 3 functions:
  1. test_example_verified_requires_function_reference
     - mock example_files pointing to temp files that do NOT contain fn_name + "("
     - call _scan_example_file_refs → assert False
     - call _determine_state equivalent → assert result is NOT example_verified
  2. test_example_verified_with_function_reference
     - mock example_files where one file CONTAINS fn_name + "("
     - call _scan_example_file_refs → assert True
     - result is example_verified
  3. test_no_example_files_gives_test_or_impl_verified
     - example_files = [] (empty)
     - result is test_verified (if test match) or implementation_verified (no match)
     - result is NOT example_verified

Micro-steps:
  MS-CL-001-04-01: Check if tests/capability_layer/ directory exists; create if not
  MS-CL-001-04-02: Create tests/capability_layer/__init__.py (empty) if absent
  MS-CL-001-04-03: Write test_example_verified_requires_function_reference (use tmp_path fixture)
  MS-CL-001-04-04: Write test_example_verified_with_function_reference
  MS-CL-001-04-05: Write test_no_example_files_gives_test_or_impl_verified
  MS-CL-001-04-06: Run: .venv/Scripts/pytest tests/capability_layer/test_state_derivation.py -v
  MS-CL-001-04-07: If failures: diagnose — the fix may need adjustment; reroute to TC-CL-001-03

Acceptance checks:
  - All 3 tests PASS
  - Tests use only public/semi-public API of capability_map_generator.py
  - No mocking of filesystem beyond tmp_path fixtures

Evidence required:
  - pytest output log

Closeout criteria:
  - pytest runs and shows 3 passed, 0 failed
```

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-001-04-01 | PENDING | Check/create tests/capability_layer/ | filesystem | directory exists |
| MS-CL-001-04-02 | PENDING | Create __init__.py if absent | tests/capability_layer/ | file present |
| MS-CL-001-04-03 | PENDING | Write test 1 (no fn reference → not example_verified) | test file | test written |
| MS-CL-001-04-04 | PENDING | Write test 2 (fn reference present → example_verified) | test file | test written |
| MS-CL-001-04-05 | PENDING | Write test 3 (empty example_files → not example_verified) | test file | test written |
| MS-CL-001-04-06 | PENDING | Run pytest -v | shell | 3 passed |
| MS-CL-001-04-07 | PENDING | If failures: reroute TC-CL-001-03 | plan | REROUTED or PASS |

---

#### TC-CL-001-05: Add VAL-011 validator

```yaml
Child Taskcard ID: TC-CL-001-05
Parent Taskcard ID: TC-CL-001
Title: "Add VAL-011 hard validator to validate_capability_map.py"
Type: CHILD
Status: TODO
Owner: implementation_agent

Preconditions:
  - TC-CL-001-03 CLOSED (fix applied)

Purpose:
  - Prevent future regressions where example_verified is assigned without example_refs.

Scope:
  Allowed files: [tools/capability_layer/validate_capability_map.py]

Expected output:
  - New check function validate_val_011_no_empty_example_refs(records) → list of errors
  - Registered in the validator registry alongside VAL-001 to VAL-010
  - Produces HARD failure (not advisory) when any example_verified record has empty example_refs
  - Does NOT alter existing VAL-001 to VAL-010

Micro-steps:
  MS-CL-001-05-01: Read validate_capability_map.py structure (how validators are registered)
  MS-CL-001-05-02: Write validate_val_011 function following existing pattern
  MS-CL-001-05-03: Register VAL-011 in validator list/registry
  MS-CL-001-05-04: Run validate_capability_map.py against current unified-capability-map.json
               (before TC-CL-001-06 regeneration) → expect VAL-011 hard failures (393)
  MS-CL-001-05-05: Confirm exit code = 1 with 393 VAL-011 failures on pre-fix map
  MS-CL-001-05-06: Confirm exit code = 0 with 0 VAL-011 failures after regeneration (TC-CL-001-06)

Acceptance checks:
  - VAL-011 fires correctly on known bad records
  - VAL-011 passes on corrected records
  - Does not alter any other validator result

Closeout criteria:
  - Both pre-fix and post-fix runs produce expected exit codes
```

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-001-05-01 | PENDING | Read validator registry pattern | validate_capability_map.py | registration pattern known |
| MS-CL-001-05-02 | PENDING | Write validate_val_011 function | :new function | function written |
| MS-CL-001-05-03 | PENDING | Register VAL-011 in registry | :registry section | registered |
| MS-CL-001-05-04 | PENDING | Run validator on pre-fix map | shell | 393 VAL-011 failures |
| MS-CL-001-05-05 | PENDING | Confirm exit code = 1 | shell | exit 1 confirmed |
| MS-CL-001-05-06 | PENDING | Run again post-TC-CL-001-06 | shell | exit 0 confirmed |

---

#### TC-CL-001-06: Regenerate capability maps and verify correction

```yaml
Child Taskcard ID: TC-CL-001-06
Parent Taskcard ID: TC-CL-001
Title: "Run capability_map_generator.py and verify the 393-record correction"
Type: CHILD
Status: TODO
Owner: implementation_agent

Preconditions:
  - TC-CL-001-03 CLOSED (fix applied)
  - TC-CL-001-04 CLOSED (tests pass)

Scope:
  Allowed files:
    - reports/capability-layer/unified-capability-map.json (regenerated output)
    - reports/capability-layer/commercial-capability-map.json (regenerated)
    - reports/capability-layer/foss-reduced-capability-map.json (regenerated)
    - reports/capability-layer/capability_summary.json (regenerated)

Expected output:
  - Fresh capability maps
  - Count of example_verified records decreases by ~393
  - Count of implementation_verified records increases by ~393
  - No example_verified record has empty example_refs

Micro-steps:
  MS-CL-001-06-01: Record pre-run counts: example_verified total, implementation_verified total
  MS-CL-001-06-02: Run: python tools/capability_layer/capability_map_generator.py
  MS-CL-001-06-03: Check exit code = 0
  MS-CL-001-06-04: Count post-run example_verified total in unified-capability-map.json
  MS-CL-001-06-05: Count post-run implementation_verified total
  MS-CL-001-06-06: Verify delta: example_verified decreased by ~393, implementation_verified increased ~393
  MS-CL-001-06-07: Run python -c check for zero empty example_refs (parent acceptance criterion)
  MS-CL-001-06-08: Run validate_capability_map.py → VAL-011 must pass, VAL-001 to VAL-008 must pass
  MS-CL-001-06-09: Record before/after counts as evidence

Acceptance checks:
  - Generator exits 0
  - No example_verified record with empty example_refs
  - VAL-011 PASS
  - VAL-001 to VAL-008 still PASS (no regressions)
  - Total capability count unchanged (no records lost)

Evidence required:
  - Before/after state count table
  - Validator output log

Closeout criteria:
  - All acceptance checks PASS
  - Evidence documented
```

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-001-06-01 | PENDING | Record pre-run state counts | unified-capability-map.json | counts noted |
| MS-CL-001-06-02 | PENDING | Run capability_map_generator.py | shell | exits |
| MS-CL-001-06-03 | PENDING | Check exit code | shell | 0 |
| MS-CL-001-06-04 | PENDING | Count post-run example_verified | unified map | count lower |
| MS-CL-001-06-05 | PENDING | Count post-run implementation_verified | unified map | count higher |
| MS-CL-001-06-06 | PENDING | Verify delta ~393 | computed | delta confirmed |
| MS-CL-001-06-07 | PENDING | Run zero-empty-refs check | python -c | 0 |
| MS-CL-001-06-08 | PENDING | Run validate_capability_map.py | shell | exit 0 |
| MS-CL-001-06-09 | PENDING | Document before/after in evidence | notes | evidence captured |

---

### TC-CL-002: Regenerate Action Queue + Fix VAL-009

```yaml
Parent Taskcard ID: TC-CL-002
Title: "Regenerate action-queue.json and achieve VAL-009 PASS"
Type: PARENT
Status: READY
Owner: implementation_agent
Supervisor: governance_lane

Source:
  Plan requirement IDs: [REQ-CL-002, REQ-CL-011]
  Plan section: "BUG 2 / Fix 6"
  Root cause: stale_artifact
  Deep analysis: PP-002

Objective:
  - Replace stale action-queue.json (2026-07-02) with a fresh version where all 32
    DEFERRED items have advisory_only=true, and VAL-009 passes.

Outcome:
  - action-queue.json generated_at = 2026-07-10 (or later)
  - VAL-009: 0 hard failures
  - source_ledger_hash matches current gap-ledger-active.json SHA-256
  - VAL-012 advisory passes (age < 14 days)

Scope:
  Allowed files:
    - reports/capability-layer/action-queue.json (regenerated)
    - tools/capability_layer/validate_capability_map.py (VAL-012 addition only)
    - tests/capability_layer/test_action_queue_freshness.py (new test)
  Forbidden:
    - gap-ledger.json (do not modify)
    - capability_map_generator.py (TC-CL-001 scope)
    - autonomous_cycle.py (TC-CL-003+ scope)

Dependencies:
  - TC-CL-001 does not need to be complete first (independent)
  - But run TC-CL-001 first in sprint to avoid double-regeneration of maps

Child taskcards:
  - TC-CL-002-01 (investigate queue generator tool)
  - TC-CL-002-02 (regenerate action-queue.json)
  - TC-CL-002-03 (verify VAL-009 pass)
  - TC-CL-002-04 (add VAL-012 advisory + staleness test)

Parent acceptance criteria:
  - validate_capability_map.py exits 0 with VAL-009 PASS
  - action-queue.json generated_at within last 24 hours
  - source_ledger_hash in action-queue.json matches sha256(gap-ledger-active.json)

Closeout criteria:
  - all 4 children CLOSED
  - parent acceptance criteria pass
  - evidence: old hash vs new hash documented

Rollback strategy:
  - git restore reports/capability-layer/action-queue.json (keeps old stale version)
  - VAL-009 will fail again; acceptable since queue is advisory-only
```

#### TC-CL-002-01: Investigate action queue generator tool

```yaml
Child Taskcard ID: TC-CL-002-01
Parent Taskcard ID: TC-CL-002
Title: "Identify the correct CLI invocation for regenerating action-queue.json"
Type: CHILD (INVESTIGATION)
Status: READY

Purpose:
  - Resolve ambiguity: does capability_pipeline.py have --stage flag? Is there a standalone
    generator? Which tool produces action-queue.json?

Scope:
  Allowed files:
    - tools/capability_layer/capability_pipeline.py (read only)
    - tools/capability_layer/capability_map_generator.py (read only, check for queue output)
    - reports/capability-layer/action-queue.json (read header only)
  Read-only: true

Micro-steps:
  MS-CL-002-01-01: Read action-queue.json lines 1-10 to find sprint_id / generator metadata
  MS-CL-002-01-02: Read capability_pipeline.py lines 1-50 (imports + argument parser)
  MS-CL-002-01-03: Search capability_pipeline.py for "--stage" argument definition
  MS-CL-002-01-04: Search capability_pipeline.py for "action_queue" references
  MS-CL-002-01-05: If stage flag exists: record exact command
              If not: read capability_pipeline.py to find action queue generation logic
  MS-CL-002-01-06: Check if standalone action queue generator script exists (e.g., tools/capability_layer/generate_action_queue.py)
  MS-CL-002-01-07: Record confirmed generator tool and exact invocation command
  MS-CL-002-01-08: If no tool exists: record this finding; TC-CL-002-02 will add --stage flag

Expected output:
  - Confirmed CLI command for queue regeneration (one of: --stage flag, standalone, or new)

Closeout criteria:
  - Generator tool and invocation confirmed or "must create" decision recorded
```

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-002-01-01 | PENDING | Read action-queue.json header | :1-10 | generator field found |
| MS-CL-002-01-02 | PENDING | Read pipeline.py imports + args | :1-50 | arg parser structure known |
| MS-CL-002-01-03 | PENDING | Search for --stage argument | :argparse section | exists or absent |
| MS-CL-002-01-04 | PENDING | Search for action_queue references | :full file | queue generation found |
| MS-CL-002-01-05 | PENDING | Record exact command if flag exists | notes | command documented |
| MS-CL-002-01-06 | PENDING | Check for standalone generator | tools/capability_layer/ | file exists or absent |
| MS-CL-002-01-07 | PENDING | Record confirmed invocation | notes | CLI command documented |
| MS-CL-002-01-08 | PENDING | If missing: note "must create" | plan update | decision recorded |

---

#### TC-CL-002-02: Regenerate action-queue.json

```yaml
Child Taskcard ID: TC-CL-002-02
Parent Taskcard ID: TC-CL-002
Title: "Run confirmed queue generator and produce fresh action-queue.json"
Type: CHILD
Status: TODO

Preconditions:
  - TC-CL-002-01 CLOSED (generator tool confirmed)

Micro-steps:
  MS-CL-002-02-01: Back up current action-queue.json (rename to action-queue.json.pre-regen)
  MS-CL-002-02-02: Run confirmed generator command (from TC-CL-002-01)
  MS-CL-002-02-03: Check exit code = 0
  MS-CL-002-02-04: Read new action-queue.json lines 1-15 to verify generated_at updated
  MS-CL-002-02-05: Compute SHA-256 of gap-ledger-active.json
  MS-CL-002-02-06: Verify source_ledger_hash in new action-queue.json matches computed SHA-256
  MS-CL-002-02-07: Count items in new queue; verify total <= 32 (all DEFERRED)
  MS-CL-002-02-08: Spot-check 3 items: all should have advisory_only=true, external_gate or blocked_by_design=true

Acceptance checks:
  - Exit code 0
  - generated_at = today
  - source_ledger_hash matches gap-ledger-active.json SHA-256
  - All spot-checked items advisory_only=true

Closeout criteria:
  - All micro-steps COMPLETE
  - No item has advisory_only=false
```

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-002-02-01 | PENDING | Backup old queue | shell mv | backup created |
| MS-CL-002-02-02 | PENDING | Run generator | shell | exits |
| MS-CL-002-02-03 | PENDING | Check exit code | shell | 0 |
| MS-CL-002-02-04 | PENDING | Read new queue header | :1-15 | generated_at = today |
| MS-CL-002-02-05 | PENDING | Compute gap-ledger-active SHA-256 | python hashlib | hash value |
| MS-CL-002-02-06 | PENDING | Verify source_ledger_hash matches | new queue | hashes match |
| MS-CL-002-02-07 | PENDING | Count queue items | python len | count <= 32 |
| MS-CL-002-02-08 | PENDING | Spot-check 3 items advisory_only | new queue | all true |

---

#### TC-CL-002-03: Verify VAL-009 passes

```yaml
Child Taskcard ID: TC-CL-002-03
Parent Taskcard ID: TC-CL-002
Title: "Run validate_capability_map.py and confirm VAL-009 PASS with 0 failures"
Type: CHILD
Status: TODO

Preconditions:
  - TC-CL-002-02 CLOSED (new action-queue.json in place)

Micro-steps:
  MS-CL-002-03-01: Run: python tools/capability_layer/validate_capability_map.py
  MS-CL-002-03-02: Search output for "VAL-009" result
  MS-CL-002-03-03: Confirm VAL-009 PASS (0 advisory_only violations)
  MS-CL-002-03-04: Check no new VAL-001 to VAL-008 failures introduced
  MS-CL-002-03-05: Record exit code and full output as evidence

Acceptance checks:
  - VAL-009: PASS
  - VAL-001 to VAL-008: no regressions
  - Exit code matches expected (0 = clean, 2 = advisory only, 1 = hard failure)

Closeout criteria:
  - VAL-009 PASS confirmed in output
```

---

#### TC-CL-002-04: Add VAL-012 advisory validator + staleness test

```yaml
Child Taskcard ID: TC-CL-002-04
Parent Taskcard ID: TC-CL-002
Title: "Add VAL-012 advisory staleness check and test_action_queue_freshness.py"
Type: CHILD
Status: TODO

Preconditions:
  - TC-CL-002-01 CLOSED (generator tool confirmed)
  - TC-CL-002-03 CLOSED (VAL-009 passing)

Micro-steps:
  MS-CL-002-04-01: Read validate_capability_map.py to find advisory check pattern
  MS-CL-002-04-02: Write validate_val_012 function: parse generated_at; warn if > 14 days
  MS-CL-002-04-03: Register VAL-012 as advisory (not hard failure)
  MS-CL-002-04-04: Create tests/capability_layer/test_action_queue_freshness.py
  MS-CL-002-04-05: Write test: load action-queue.json; assert age < 14 days
  MS-CL-002-04-06: Run test → PASS (queue is fresh after TC-CL-002-02)
  MS-CL-002-04-07: Run validate_capability_map.py → VAL-012 should produce PASS (not warn)

Acceptance checks:
  - VAL-012 produces PASS on fresh queue
  - VAL-012 would produce WARN on queue older than 14 days (verified by unit test with mock date)
  - Test file exists and passes

Closeout criteria:
  - VAL-012 added and tested
```

---

### TC-CL-003: SAL Compiler Integration + authority_class Field

```yaml
Parent Taskcard ID: TC-CL-003
Title: "Invoke SAL compiler; add authority_class field; integrate into autonomous_cycle"
Type: PARENT
Status: READY
Owner: implementation_agent
Supervisor: governance_lane

Source:
  Plan requirement IDs: [REQ-CL-005, REQ-CL-006, REQ-CL-010]
  Plan section: "Fix 2 / Fix 3 / Phase 2 TC-CL-003"
  Root cause: RC-C, RC-E
  Deep analysis: PP-003

Objective:
  - Run capability_compiler.py for the first time to produce sal-driven-capability-map.json
    with 169 ODF-format records having non-empty obligation_ids.
  - Add authority_class field to all capability records (SAL_GROUNDED for 169 ODF,
    IMPLEMENTATION_ASSERTED for remainder).
  - Add best-effort SAL compiler invocation to autonomous_cycle.py.

Outcome:
  - sal-driven-capability-map.json exists with ≥ 100 records with obligation_ids
  - unified-capability-map.json has authority_class field on all records
  - autonomous_cycle.py invokes SAL compiler (best-effort, non-blocking)

Scope:
  Allowed files:
    - tools/capability_layer/capability_compiler.py (read only — invoke as subprocess)
    - tools/capability_layer/capability_map_generator.py (add authority_class output)
    - tools/supervisor/autonomous_cycle.py (add best-effort subprocess call after Step 4a)
    - reports/capability-layer/sal-driven-capability-map.json (new generated output)
    - reports/capability-layer/unified-capability-map.json (enriched with authority_class)
  Forbidden:
    - capability_compiler.py must NOT be modified (invoke only)

Dependencies:
  - TC-CL-001 CLOSED (maps should be in good state before enriching them)

Child taskcards:
  - TC-CL-003-01 (investigate compiler CLI + confirm output)
  - TC-CL-003-02 (run compiler standalone, verify output)
  - TC-CL-003-03 (add authority_class to capability_map_generator.py)
  - TC-CL-003-04 (merge obligation_ids into unified map)
  - TC-CL-003-05 (add best-effort invocation to autonomous_cycle.py)

Parent acceptance criteria:
  - sal-driven-capability-map.json exists
  - Count records in sal-driven map with non-empty obligation_ids: ≥ 100
  - unified-capability-map.json has authority_class field on all records
  - autonomous_cycle.py runs end-to-end without exception after change
  - Running capability_compiler.py twice produces identical SHA-256 output (idempotency)

Closeout criteria:
  - all 5 children CLOSED
  - parent acceptance criteria pass
```

#### TC-CL-003-01: Investigate compiler CLI and expected output

```yaml
Child Taskcard ID: TC-CL-003-01
Parent Taskcard ID: TC-CL-003
Title: "Read capability_compiler.py: confirm CLI API, output path, and ODF format list"
Type: CHILD (INVESTIGATION)
Status: READY
```

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-003-01-01 | PENDING | Read compiler lines 1-50 (imports, argparse) | capability_compiler.py:1-50 | CLI arguments confirmed |
| MS-CL-003-01-02 | PENDING | Find --output argument default value | :argparse section | default path noted |
| MS-CL-003-01-03 | PENDING | Find SAL facts input path (where it reads from) | :facts loading section | input path confirmed |
| MS-CL-003-01-04 | PENDING | Find which formats are ODF-supported (have SAL parsers) | :format list | ODF format IDs listed |
| MS-CL-003-01-05 | PENDING | Confirm content-normalized SHA write exists | :output section | SHA write confirmed |
| MS-CL-003-01-06 | PENDING | Confirm obligation_ids field in output schema | :output schema | field name confirmed |
| MS-CL-003-01-07 | PENDING | Record exact invocation command | notes | command documented |

---

#### TC-CL-003-02: Run compiler standalone, verify output

```yaml
Child Taskcard ID: TC-CL-003-02
Parent Taskcard ID: TC-CL-003
Title: "Invoke capability_compiler.py and verify sal-driven-capability-map.json produced"
Type: CHILD
Status: TODO

Preconditions:
  - TC-CL-003-01 CLOSED (CLI confirmed)
```

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-003-02-01 | PENDING | Run compiler with confirmed CLI | shell | exits |
| MS-CL-003-02-02 | PENDING | Check exit code = 0 | shell | 0 |
| MS-CL-003-02-03 | PENDING | Verify sal-driven-capability-map.json exists | filesystem | file present |
| MS-CL-003-02-04 | PENDING | Count records with non-empty obligation_ids | python -c | ≥ 100 |
| MS-CL-003-02-05 | PENDING | Run compiler a second time | shell | exits 0 |
| MS-CL-003-02-06 | PENDING | Compare SHA-256 of first and second runs | python hashlib | identical (idempotency) |
| MS-CL-003-02-07 | PENDING | Record record count and sample obligation_ids | notes | evidence captured |

---

#### TC-CL-003-03: Add authority_class to capability_map_generator.py output

```yaml
Child Taskcard ID: TC-CL-003-03
Parent Taskcard ID: TC-CL-003
Title: "Add authority_class field to every capability record emitted by capability_map_generator.py"
Type: CHILD
Status: TODO

Preconditions:
  - TC-CL-003-01 CLOSED (ODF format list confirmed, so we know which formats get SAL_GROUNDED)
```

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-003-03-01 | PENDING | Read generator's record construction section | capability_map_generator.py | record dict keys found |
| MS-CL-003-03-02 | PENDING | Identify where format_id is available in record construction | :record build site | format_id accessible |
| MS-CL-003-03-03 | PENDING | Define ODF_FORMATS constant (FODS/FODT/FODG/FODP/ODS/ODT) near file top | :~line 30 | constant added |
| MS-CL-003-03-04 | PENDING | Add authority_class field: SAL_GROUNDED if format in ODF_FORMATS else IMPLEMENTATION_ASSERTED | :record build | field added |
| MS-CL-003-03-05 | PENDING | Add obligation_source field: "sal-facts" if SAL_GROUNDED else "poc-targets.yaml" | :record build | field added |
| MS-CL-003-03-06 | PENDING | Run generator: python tools/capability_layer/capability_map_generator.py | shell | exits 0 |
| MS-CL-003-03-07 | PENDING | Verify authority_class field present in unified-capability-map.json sample | python -c | field found |
| MS-CL-003-03-08 | PENDING | Count SAL_GROUNDED vs IMPLEMENTATION_ASSERTED; document ratio | python -c | counts recorded |

---

#### TC-CL-003-04: Merge obligation_ids from sal-driven map into unified map

```yaml
Child Taskcard ID: TC-CL-003-04
Parent Taskcard ID: TC-CL-003
Title: "Enrich unified-capability-map.json with obligation_ids from sal-driven map"
Type: CHILD
Status: TODO

Preconditions:
  - TC-CL-003-02 CLOSED (sal-driven-capability-map.json exists with ≥ 100 records)
  - TC-CL-003-03 CLOSED (authority_class field in generator output)
```

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-003-04-01 | PENDING | Read sal-driven map schema to find capability_id field name | sal-driven-capability-map.json:1-20 | key field name |
| MS-CL-003-04-02 | PENDING | Read unified map schema to confirm capability_id key field | unified-capability-map.json:1-20 | key field name |
| MS-CL-003-04-03 | PENDING | Write merge script or extend generator: match by capability_id, copy obligation_ids | new script or generator update | merge logic |
| MS-CL-003-04-04 | PENDING | Run merge → verify 169 (or confirmed count) records gain obligation_ids | python | count updated |
| MS-CL-003-04-05 | PENDING | Verify remaining records have obligation_ids = [] or absent (not fabricated) | python -c | no fake ids |
| MS-CL-003-04-06 | PENDING | Run validate_capability_map.py → no new failures from authority_class | shell | exit 0 or advisory only |

---

#### TC-CL-003-05: Add best-effort SAL compiler to autonomous_cycle.py

```yaml
Child Taskcard ID: TC-CL-003-05
Parent Taskcard ID: TC-CL-003
Title: "Add subprocess call to invoke capability_compiler.py after Step 4a in autonomous_cycle.py"
Type: CHILD
Status: TODO

Preconditions:
  - TC-CL-003-02 CLOSED (compiler runs successfully standalone)
```

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-003-05-01 | PENDING | Read autonomous_cycle.py lines 1570-1600 (Step 4a block) | :1570-1600 | insertion point confirmed |
| MS-CL-003-05-02 | PENDING | Find exact line after Step 4a compiler block (safe insertion point) | :after line 1589 | insertion line noted |
| MS-CL-003-05-03 | PENDING | Add subprocess.run call wrapped in try/except with timeout=60 | :insertion point | code added |
| MS-CL-003-05-04 | PENDING | Verify sys.executable reference (not hardcoded python path) | :added code | uses sys.executable |
| MS-CL-003-05-05 | PENDING | Add print statement for success and non-blocking failure | :added code | log messages present |
| MS-CL-003-05-06 | PENDING | Run autonomous_cycle.py dry run or import check to verify no syntax error | shell | OK |
| MS-CL-003-05-07 | PENDING | Verify subprocess call does not block cycle if compiler errors | test: pass invalid --output | cycle continues |

---

### TC-CL-004: Document Two-Track Authority Boundary

```yaml
Parent Taskcard ID: TC-CL-004
Title: "Formally document ODF vs non-ODF authority boundary in governance artifacts"
Type: PARENT
Status: READY
Owner: documentation_agent
Supervisor: governance_lane

Source:
  Plan requirement IDs: [REQ-CL-004]
  Plan section: "Structural Weakness 2 / Fix 2 (authority_class)"
  Root cause: RC-E

Objective:
  - Update capability-authority-model.yaml to declare Track A (poc-targets, non-ODF) and
    Track B (SAL-grounded, ODF) as formally bounded authority regions.
  - Update capability-consumer-graph.yaml with authority_class consumer notes.
  - Update L03 layer plan maturity to 4/5.

Dependencies:
  - TC-CL-003 CLOSED (authority_class field exists, SAL map produced)

Child taskcards:
  - TC-CL-004-01 (update capability-authority-model.yaml)
  - TC-CL-004-02 (update capability-consumer-graph.yaml)
  - TC-CL-004-03 (update L03 layer plan maturity 4/5)

Parent acceptance criteria:
  - capability-authority-model.yaml contains Track A and Track B definitions
  - capability-consumer-graph.yaml references authority_class field
  - plans/layers/capability-layer.md maturity = 4/5

Closeout criteria:
  - All 3 children CLOSED
  - Governance artifacts updated and consistent
```

#### TC-CL-004-01: Update capability-authority-model.yaml

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-004-01-01 | PENDING | Read current capability-authority-model.yaml (14 KB) | reports/capability-layer/ | current structure understood |
| MS-CL-004-01-02 | PENDING | Add "authority_tracks" section: Track A (IMPLEMENTATION_ASSERTED, non-ODF formats) | :new section | Track A defined |
| MS-CL-004-01-03 | PENDING | Add Track B definition (SAL_GROUNDED, ODF formats, 6 formats listed) | :new section | Track B defined |
| MS-CL-004-01-04 | PENDING | Add "non_odf_formats_without_spec_authority" list (10 formats) | :new section | list documented |
| MS-CL-004-01-05 | PENDING | Add authority_class field documentation (SAL_GROUNDED / IMPLEMENTATION_ASSERTED) | :field definitions | field documented |
| MS-CL-004-01-06 | PENDING | Add note: non-ODF formats will gain SAL_GROUNDED status when /ingest-spec-sal runs | :future work | note added |

---

#### TC-CL-004-02: Update capability-consumer-graph.yaml

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-004-02-01 | PENDING | Read current capability-consumer-graph.yaml (17 KB) | reports/capability-layer/ | current consumers listed |
| MS-CL-004-02-02 | PENDING | Add authority_class as a filterable field for each consumer | :consumer entries | field noted per consumer |
| MS-CL-004-02-03 | PENDING | Add note: capability_map_generator.py now sets IMPLEMENTATION_ASSERTED | :generator entry | classification added |
| MS-CL-004-02-04 | PENDING | Add note: capability_compiler.py produces SAL_GROUNDED records | :compiler entry | classification added |
| MS-CL-004-02-05 | PENDING | Add work_selection_mode field to autonomous_cycle.py consumer entry | :cycle entry | field documented |

---

#### TC-CL-004-03: Update L03 layer plan maturity to 4/5

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-004-03-01 | PENDING | Read plans/layers/capability-layer.md current metadata | plans/layers/ | current maturity = 3/5 confirmed |
| MS-CL-004-03-02 | PENDING | Update maturity field from 3 to 4 | :metadata | 4/5 |
| MS-CL-004-03-03 | PENDING | Update health field from DEGRADED to HARDENING_IN_PROGRESS | :metadata | health updated |
| MS-CL-004-03-04 | PENDING | Update next_action to reflect TC-CL-005/006 remaining | :metadata | next action updated |
| MS-CL-004-03-05 | PENDING | Update stage from GRAPH_REPAIR to AUTHORITY_DOCUMENTED | :metadata | stage updated |

---

### TC-CL-005: Add Gap Closure Detection

```yaml
Parent Taskcard ID: TC-CL-005
Title: "Add flag-only gap closure scanner to autonomous_cycle.py; produce gap-closure-candidates.json"
Type: PARENT
Status: READY
Owner: implementation_agent
Supervisor: governance_lane

Source:
  Plan requirement IDs: [REQ-CL-003]
  Plan section: "Structural Weakness 1 / Fix 4"
  Root cause: RC-B

Objective:
  - After sprint evidence is declared in each autonomous_cycle run, scan the 8 open gaps
    and flag any whose test_refs all exist on disk. Produce gap-closure-candidates.json.
    Do NOT auto-close any gap.

Scope:
  Allowed files:
    - tools/supervisor/autonomous_cycle.py (add _check_gap_closure + scanner loop)
    - .local/capability-layer/ directory (create and write candidates file)
  Forbidden:
    - gap-ledger.json (do not close any gap automatically)
    - gap-ledger-active.json (do not modify)
    - Any test file or source file

Dependencies:
  - TC-CL-003 CLOSED (so autonomous_cycle.py is in a stable state after Phase 2 changes)
  - TC-CL-006 may run in parallel (different section of autonomous_cycle.py)

Child taskcards:
  - TC-CL-005-01 (read autonomous_cycle.py, find insertion point)
  - TC-CL-005-02 (implement _check_gap_closure function)
  - TC-CL-005-03 (add scanner loop and file output)
  - TC-CL-005-04 (verify gap-closure-candidates.json produced for 8 open gaps)

Parent acceptance criteria:
  - .local/capability-layer/gap-closure-candidates.json created on each cycle run
  - File contains at most 8 entries (the open/OPEN_BLOCKED gaps only)
  - Function returns False for all DEFERRED_BY_DESIGN gaps (they are skipped)
  - No gap is auto-closed

Closeout criteria:
  - All 4 children CLOSED
  - Manual verification: gap-ledger-active.json unchanged after cycle run
```

#### TC-CL-005-01: Read autonomous_cycle.py and find insertion point

```yaml
Child Taskcard ID: TC-CL-005-01
Parent Taskcard ID: TC-CL-005
Title: "Read autonomous_cycle.py evidence declaration section; confirm insertion point for scanner"
Type: CHILD (INVESTIGATION)
Status: READY
```

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-005-01-01 | PENDING | Read autonomous_cycle.py lines 1-30 (imports) | :1-30 | imports list known |
| MS-CL-005-01-02 | PENDING | Search for evidence declaration write section | :grep "evidence" | section line numbers found |
| MS-CL-005-01-03 | PENDING | Read 20 lines around evidence declaration | :found lines | structure understood |
| MS-CL-005-01-04 | PENDING | Confirm insertion point: after sprint work, before evidence write | :chosen line | insertion point recorded |
| MS-CL-005-01-05 | PENDING | Confirm .local/ directory is accessible from within cycle | :path references | path pattern confirmed |
| MS-CL-005-01-06 | PENDING | Confirm gap-ledger.json load path already in scope at insertion point | :Step 4a variables | _gl_path variable accessible |

---

#### TC-CL-005-02: Implement _check_gap_closure function

```yaml
Child Taskcard ID: TC-CL-005-02
Parent Taskcard ID: TC-CL-005
Title: "Write _check_gap_closure(gap, repo_root) → bool function in autonomous_cycle.py"
Type: CHILD
Status: TODO

Preconditions:
  - TC-CL-005-01 CLOSED (insertion point confirmed)
```

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-005-02-01 | PENDING | Add _check_gap_closure function near top of cycle module (private helper) | :module level | function written |
| MS-CL-005-02-02 | PENDING | Function: if no test_refs → return False | :function body | early exit |
| MS-CL-005-02-03 | PENDING | Function: all(Path(repo_root/tr).exists() for tr in gap["test_refs"]) → return result | :function body | existence check |
| MS-CL-005-02-04 | PENDING | Add guard: skip gaps with status in DEFERRED_BY_DESIGN, DEFERRED | :function body | DEFERRED skipped |
| MS-CL-005-02-05 | PENDING | Manual trace: call function with gap having known test_ref path | local trace | returns expected bool |

---

#### TC-CL-005-03: Add scanner loop and file output

```yaml
Child Taskcard ID: TC-CL-005-03
Parent Taskcard ID: TC-CL-005
Title: "Add scanner loop at insertion point; write gap-closure-candidates.json"
Type: CHILD
Status: TODO

Preconditions:
  - TC-CL-005-01 CLOSED (insertion point confirmed)
  - TC-CL-005-02 CLOSED (_check_gap_closure function exists)
```

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-005-03-01 | PENDING | At insertion point: load gap-ledger-active.json (prefer) or gap-ledger.json open gaps | :insertion | gaps loaded |
| MS-CL-005-03-02 | PENDING | Filter to non-DEFERRED gaps only (8 candidates max) | :loop | DEFERRED excluded |
| MS-CL-005-03-03 | PENDING | Call _check_gap_closure for each non-deferred gap | :loop | closure_candidates list |
| MS-CL-005-03-04 | PENDING | Create .local/capability-layer/ directory if absent (Path.mkdir(exist_ok=True)) | :output | dir created |
| MS-CL-005-03-05 | PENDING | Write gap-closure-candidates.json with list of flagged gap_ids + reason | :output | file written |
| MS-CL-005-03-06 | PENDING | Add print statement: "Gap closure scanner: N candidates flagged" | :output | logged |
| MS-CL-005-03-07 | PENDING | Wrap entire scanner in try/except → non-blocking on failure | :scanner | exception absorbed |

---

#### TC-CL-005-04: Verify output produced for 8 open gaps

```yaml
Child Taskcard ID: TC-CL-005-04
Parent Taskcard ID: TC-CL-005
Title: "Run autonomous_cycle.py (or scanner in isolation) and verify candidates file"
Type: CHILD
Status: TODO

Preconditions:
  - TC-CL-005-03 CLOSED (scanner written)
```

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-005-04-01 | PENDING | Run scanner in isolation (python -c or mini-script) | shell | candidates file created |
| MS-CL-005-04-02 | PENDING | Read .local/capability-layer/gap-closure-candidates.json | file | content present |
| MS-CL-005-04-03 | PENDING | Verify gap-ledger-active.json is UNCHANGED after scanner | diff or read | no modification |
| MS-CL-005-04-04 | PENDING | Verify candidates list length ≤ 8 | python len | ≤ 8 |
| MS-CL-005-04-05 | PENDING | Verify no DEFERRED_BY_DESIGN gaps appear in candidates | python check | DEFERRED absent |

---

### TC-CL-006: Work-Source Fallback Auditability

```yaml
Parent Taskcard ID: TC-CL-006
Title: "Add work_selection_mode and fallback_reason fields to autonomous_cycle Step 4a output"
Type: PARENT
Status: READY
Owner: implementation_agent
Supervisor: governance_lane

Source:
  Plan requirement IDs: [REQ-CL-007, REQ-CL-012]
  Plan section: "Structural Weakness 4 / Fix 5"
  Root cause: RC-D

Objective:
  - Make visible whether each sprint's work is spec-grounded (8 gap-sourced items) or
    expansion-goal-derived (fallback). Add machine-readable fields to next-work-items.json.

Scope:
  Allowed files:
    - tools/supervisor/autonomous_cycle.py (Step 4a block, lines 1571-1589)
  Forbidden:
    - Do NOT remove expansion goals
    - Do NOT change compile_gaps() call signature

Dependencies:
  - TC-CL-003 CLOSED (so Step 4a is stable after SAL compiler addition)

Child taskcards:
  - TC-CL-006-01 (add fields to CAPABILITY_COMPILER_MERGED branch)
  - TC-CL-006-02 (add fields to EXPANSION_GOAL_FALLBACK branch)
  - TC-CL-006-03 (verify fields present in both modes)
  - TC-CL-006-04 (add runtime assertion that work_selection_mode always present)

Parent acceptance criteria:
  - next-work-items.json always contains work_selection_mode field
  - When 8 items: work_selection_mode = CAPABILITY_COMPILER_MERGED, gap_sourced_count = 8
  - When 0 items: work_selection_mode = EXPANSION_GOAL_FALLBACK, fallback_reason field present

Closeout criteria:
  - All 4 children CLOSED
  - Both modes verified
```

#### TC-CL-006-01: Add fields to CAPABILITY_COMPILER_MERGED branch

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-006-01-01 | PENDING | Read autonomous_cycle.py lines 1571-1589 (Step 4a) | :1571-1589 | current code understood |
| MS-CL-006-01-02 | PENDING | In the `if _comp_items:` branch: add work_selection_mode = "CAPABILITY_COMPILER_MERGED" | :if branch | field added |
| MS-CL-006-01-03 | PENDING | Add gap_sourced_count = len(_comp_items) | :if branch | count field added |
| MS-CL-006-01-04 | PENDING | Update print statement: include count in message | :print line | informative log |

#### TC-CL-006-02: Add fields to EXPANSION_GOAL_FALLBACK branch

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-006-02-01 | PENDING | In the `else:` branch: add work_selection_mode = "EXPANSION_GOAL_FALLBACK" | :else branch | field added |
| MS-CL-006-02-02 | PENDING | Add gap_sourced_count = 0 | :else branch | field added |
| MS-CL-006-02-03 | PENDING | Add fallback_reason = "gap_ledger_has_no_open_actionable_gaps" | :else branch | field added |
| MS-CL-006-02-04 | PENDING | Update print statement: explicit EXPANSION_GOAL_FALLBACK message | :print line | visible log |

#### TC-CL-006-03: Verify fields present in both modes

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-006-03-01 | PENDING | Run cycle (or read current next-work-items.json) | shell or file | mode field present |
| MS-CL-006-03-02 | PENDING | Verify mode = CAPABILITY_COMPILER_MERGED when 8 items returned | next-work-items.json | field present |
| MS-CL-006-03-03 | PENDING | Simulate 0-item scenario (patch compile_gaps to return empty) | local test | EXPANSION_GOAL_FALLBACK |
| MS-CL-006-03-04 | PENDING | Restore compile_gaps (revert simulation) | file | original state |

#### TC-CL-006-04: Add runtime assertion

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-006-04-01 | PENDING | After Step 4a block: add assertion work_selection_mode in next_work | :post-step | assert added |
| MS-CL-006-04-02 | PENDING | Run cycle → verify no AssertionError raised | shell | assert passes |

---

### TC-CL-007: Final Validation and Idempotency Proof

```yaml
Parent Taskcard ID: TC-CL-007
Title: "Full system validation: validate_capability_map.py exit 0, double-run idempotency, closeout"
Type: PARENT
Status: PROPOSED
Owner: validation_agent
Supervisor: governance_lane

Source:
  Plan requirement IDs: [REQ-CL-013, REQ-CL-014, REQ-CL-015]
  Plan section: "Phase 3 / TC-CL-007"
  Root cause: all

Objective:
  - After all prior taskcards closed: run full validation suite, prove double-run
    produces no content churn, update L03 to maturity 5/5, write healing report,
    declare evidence.

Dependencies:
  - TC-CL-001 CLOSED
  - TC-CL-002 CLOSED
  - TC-CL-003 CLOSED
  - TC-CL-004 CLOSED
  - TC-CL-005 CLOSED
  - TC-CL-006 CLOSED

Child taskcards:
  - TC-CL-007-01 (run full validate_capability_map.py)
  - TC-CL-007-02 (double-run idempotency: capability_map_generator.py)
  - TC-CL-007-03 (double-run idempotency: capability_compiler.py)
  - TC-CL-007-04 (update L03 to maturity 5/5)
  - TC-CL-007-05 (write capability-layer-healing-report.md)
  - TC-CL-007-06 (write evidence declaration, run autonomous-cycle)

Parent acceptance criteria:
  - validate_capability_map.py exits 0 (or advisory-only, no hard failures)
  - Second run of map generator: SHA-256 diff = 0
  - Second run of SAL compiler: SHA-256 diff = 0
  - plans/layers/capability-layer.md maturity = 5/5
  - capability-layer-healing-report.md exists

Closeout criteria:
  - All 6 children CLOSED
  - Evidence declaration accepted by supervisor
```

#### TC-CL-007-01: Run full validate_capability_map.py

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-007-01-01 | PENDING | Run: python tools/capability_layer/validate_capability_map.py | shell | exits |
| MS-CL-007-01-02 | PENDING | Record exit code | shell | 0 or 2 (advisory) expected; 1 = FAIL |
| MS-CL-007-01-03 | PENDING | Verify VAL-001 to VAL-008: PASS | output | no regression |
| MS-CL-007-01-04 | PENDING | Verify VAL-009: PASS (from TC-CL-002) | output | PASS |
| MS-CL-007-01-05 | PENDING | Verify VAL-011: PASS (from TC-CL-001) | output | PASS |
| MS-CL-007-01-06 | PENDING | Verify VAL-012: PASS advisory (from TC-CL-002) | output | advisory PASS |
| MS-CL-007-01-07 | PENDING | If any hard failure: reroute to responsible taskcard | notes | REROUTED or all PASS |

---

#### TC-CL-007-02: Idempotency — capability_map_generator.py double-run

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-007-02-01 | PENDING | Run capability_map_generator.py → run 1 | shell | exits 0 |
| MS-CL-007-02-02 | PENDING | Compute SHA-256 of unified-capability-map.json after run 1 | python hashlib | hash_1 |
| MS-CL-007-02-03 | PENDING | Run capability_map_generator.py → run 2 | shell | exits 0 |
| MS-CL-007-02-04 | PENDING | Compute SHA-256 of unified-capability-map.json after run 2 | python hashlib | hash_2 |
| MS-CL-007-02-05 | PENDING | Assert hash_1 == hash_2 | python | PASS or INVESTIGATE |
| MS-CL-007-02-06 | PENDING | If hash_1 != hash_2: diff the outputs to find non-determinism | diff | root cause |

---

#### TC-CL-007-03: Idempotency — capability_compiler.py double-run

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-007-03-01 | PENDING | Run capability_compiler.py → run 1 | shell | exits 0 |
| MS-CL-007-03-02 | PENDING | Compute SHA-256 of sal-driven-capability-map.json | python | hash_1 |
| MS-CL-007-03-03 | PENDING | Run capability_compiler.py → run 2 | shell | exits 0 |
| MS-CL-007-03-04 | PENDING | Compute SHA-256 of sal-driven-capability-map.json | python | hash_2 |
| MS-CL-007-03-05 | PENDING | Assert hash_1 == hash_2 | python | PASS |

---

#### TC-CL-007-04: Update L03 to maturity 5/5

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-007-04-01 | PENDING | Read plans/layers/capability-layer.md | :metadata | current state 4/5 |
| MS-CL-007-04-02 | PENDING | Update maturity to 5 | :metadata | 5/5 |
| MS-CL-007-04-03 | PENDING | Update health to VERIFIED | :metadata | VERIFIED |
| MS-CL-007-04-04 | PENDING | Update status to CLOSED | :metadata | CLOSED |
| MS-CL-007-04-05 | PENDING | Update active_taskcards to [] | :metadata | empty |
| MS-CL-007-04-06 | PENDING | Update completed_taskcards list | :metadata | TC-CL-001 through TC-CL-007 |

---

#### TC-CL-007-05: Write capability-layer-healing-report.md

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-007-05-01 | PENDING | Write summary: what was broken (BUG 1, BUG 2, SW 1-4) | report | broken items listed |
| MS-CL-007-05-02 | PENDING | Write what was fixed (TC-CL-001 through TC-CL-006 outcomes) | report | fixes listed |
| MS-CL-007-05-03 | PENDING | Write before/after capability state counts (from TC-CL-001-06 evidence) | report | counts documented |
| MS-CL-007-05-04 | PENDING | Write before/after VAL-009 status (from TC-CL-002 evidence) | report | status change documented |
| MS-CL-007-05-05 | PENDING | Write authority model update (two-track documented) | report | model documented |
| MS-CL-007-05-06 | PENDING | Write remaining limitations and future work | report | limits honest |
| MS-CL-007-05-07 | PENDING | Write idempotency proof results (hashes from TC-CL-007-02/03) | report | hashes included |
| MS-CL-007-05-08 | PENDING | Save to reports/capability-layer/capability-layer-healing-report.md | file | file present |

---

#### TC-CL-007-06: Write evidence declaration and run autonomous-cycle

| Micro-step ID | Status | Action | Target | Expected Output |
|---|---|---|---|---|
| MS-CL-007-06-01 | PENDING | Generate run_id for this evidence run | python uuid or timestamp | run_id value |
| MS-CL-007-06-02 | PENDING | Create .local/evidences/{run_id}/ directory | filesystem | dir created |
| MS-CL-007-06-03 | PENDING | Write evidence-declaration.yaml per supervisor contract schema | .local/evidences/{run_id}/ | file written |
| MS-CL-007-06-04 | PENDING | Run sprint_executor_validate.py --repair on declaration | shell | no FAIL |
| MS-CL-007-06-05 | PENDING | Run: python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration ... | shell | exits 0 or 3 |
| MS-CL-007-06-06 | PENDING | Check exit code; if 3: log rework items and record in plan | notes | logged |
| MS-CL-007-06-07 | PENDING | Build review package; record absolute path and SHA-256 | shell | package path noted |

---

## PART VIII — DEPENDENCY DAG

```yaml
# execution-dag.yaml
nodes:
  TC-CL-001:
    prerequisites: []
    can_parallelize_with: [TC-CL-002]
    blocks: [TC-CL-003, TC-CL-007]

  TC-CL-002:
    prerequisites: []
    can_parallelize_with: [TC-CL-001]
    blocks: [TC-CL-007]
    note: "Independently runnable; maps do not need to be regenerated first"

  TC-CL-003:
    prerequisites: [TC-CL-001]
    can_parallelize_with: []
    blocks: [TC-CL-004, TC-CL-005, TC-CL-006, TC-CL-007]
    note: "autonomous_cycle.py changes; must be stable before 005/006 add more changes"

  TC-CL-004:
    prerequisites: [TC-CL-003]
    can_parallelize_with: []
    blocks: [TC-CL-007]

  TC-CL-005:
    prerequisites: [TC-CL-003]
    can_parallelize_with: [TC-CL-006]
    blocks: [TC-CL-007]
    note: "Different section of autonomous_cycle.py than TC-CL-006; safe to parallelize"

  TC-CL-006:
    prerequisites: [TC-CL-003]
    can_parallelize_with: [TC-CL-005]
    blocks: [TC-CL-007]

  TC-CL-007:
    prerequisites: [TC-CL-001, TC-CL-002, TC-CL-003, TC-CL-004, TC-CL-005, TC-CL-006]
    can_parallelize_with: []
    blocks: []

execution_order_safe:
  phase_1: [TC-CL-001, TC-CL-002]  # parallel
  phase_2: [TC-CL-003]
  phase_3: [TC-CL-004]
  phase_4: [TC-CL-005, TC-CL-006]  # parallel (different sections of autonomous_cycle.py)
  phase_5: [TC-CL-007]

file_ownership_and_locks:
  "tools/capability_layer/capability_map_generator.py":
    owner: [TC-CL-001, TC-CL-003-03]
    concurrent_safe: false
    sequence: TC-CL-001 first (bug fix), TC-CL-003-03 second (authority_class field)

  "tools/capability_layer/validate_capability_map.py":
    owner: [TC-CL-001-05, TC-CL-002-04]
    concurrent_safe: false
    sequence: TC-CL-001-05 (VAL-011), TC-CL-002-04 (VAL-012)

  "tools/supervisor/autonomous_cycle.py":
    owner: [TC-CL-003-05, TC-CL-005-03, TC-CL-006-01, TC-CL-006-02]
    concurrent_safe: false
    sequence: TC-CL-003-05 (SAL compiler call), TC-CL-005-03 (scanner), TC-CL-006-01+02 (mode fields)
    note: "Each adds to a different location; apply sequentially to avoid conflicts"

  "reports/capability-layer/unified-capability-map.json":
    owner: [TC-CL-001-06, TC-CL-003-04]
    concurrent_safe: false
    sequence: TC-CL-001-06 (state correction regen), TC-CL-003-04 (obligation_ids merge)

  "reports/capability-layer/action-queue.json":
    owner: [TC-CL-002-02]
    concurrent_safe: true (only one writer)

  "plans/layers/capability-layer.md":
    owner: [TC-CL-004-03, TC-CL-007-04]
    concurrent_safe: false
    sequence: TC-CL-004-03 (4/5), TC-CL-007-04 (5/5)
```

---

## PART IX — MACHINE STATE MODEL

```yaml
# taskcard-state-machine.yaml
parent_transitions_valid:
  - [PROPOSED, READY]
  - [READY, IN_PROGRESS]
  - [IN_PROGRESS, CHILDREN_IN_PROGRESS]
  - [CHILDREN_IN_PROGRESS, INTEGRATION_PENDING]
  - [INTEGRATION_PENDING, VERIFIED]
  - [VERIFIED, SCORED]
  - [SCORED, CLOSED]
  - [SCORED, REROUTED]
  - [any_non_closed, BLOCKED]
  - [BLOCKED, READY]
  - [any_non_closed, BLOCKED_EXTERNAL]
  - [any_non_closed, DEFERRED_WITH_REASON]

parent_transitions_forbidden:
  - [READY, CLOSED]
  - [IN_PROGRESS, CLOSED]
  - [CHILDREN_IN_PROGRESS, CLOSED]
  - [INTEGRATION_PENDING, CLOSED]
  - [VERIFIED, CLOSED]  # must go through SCORED first
  - [REROUTED, CLOSED]  # must go through IN_PROGRESS -> ... -> SCORED

child_transitions_valid:
  - [TODO, READY]
  - [READY, IN_PROGRESS]
  - [IN_PROGRESS, IMPLEMENTED]
  - [IMPLEMENTED, VERIFIED]
  - [VERIFIED, SCORED]
  - [SCORED, CLOSED]
  - [SCORED, REROUTED]
  - [REROUTED, IN_PROGRESS]
  - [any_non_closed, BLOCKED]
  - [BLOCKED, READY]
  - [any_non_closed, BLOCKED_EXTERNAL]
  - [any_non_closed, DEFERRED_WITH_REASON]

child_transitions_forbidden:
  - [TODO, CLOSED]
  - [READY, CLOSED]
  - [IN_PROGRESS, CLOSED]
  - [IMPLEMENTED, CLOSED]  # must verify and score first
  - [REROUTED, CLOSED]  # must rework first

micro_step_transitions_valid:
  - [PENDING, READY]
  - [READY, ACTIVE]
  - [ACTIVE, COMPLETE]
  - [ACTIVE, FAILED]
  - [ACTIVE, BLOCKED]
  - [FAILED, READY]
  - [BLOCKED, READY]
  - [PENDING, SKIPPED_NOT_APPLICABLE]  # must record reason

micro_step_transitions_forbidden:
  - [PENDING, COMPLETE]  # must go ACTIVE first
  - [PENDING, FAILED]
  - [COMPLETE, any]  # terminal

closure_rules:
  child_closed_only_when:
    - all mandatory micro-steps COMPLETE or SKIPPED_NOT_APPLICABLE
    - acceptance checks pass
    - evidence documented

  parent_closed_only_when:
    - all mandatory children CLOSED
    - parent integration checks pass
    - parent evidence complete
    - all quality dimensions >= 4/5

current_taskcard_states:
  TC-CL-001: READY
  TC-CL-001-01: READY
  TC-CL-001-02: TODO
  TC-CL-001-03: TODO
  TC-CL-001-04: TODO
  TC-CL-001-05: TODO
  TC-CL-001-06: TODO
  TC-CL-002: READY
  TC-CL-002-01: READY
  TC-CL-002-02: TODO
  TC-CL-002-03: TODO
  TC-CL-002-04: TODO
  TC-CL-003: READY
  TC-CL-003-01: READY
  TC-CL-003-02: TODO
  TC-CL-003-03: TODO
  TC-CL-003-04: TODO
  TC-CL-003-05: TODO
  TC-CL-004: READY
  TC-CL-004-01: READY
  TC-CL-004-02: READY
  TC-CL-004-03: READY
  TC-CL-005: READY
  TC-CL-005-01: READY
  TC-CL-005-02: TODO
  TC-CL-005-03: TODO
  TC-CL-005-04: TODO
  TC-CL-006: READY
  TC-CL-006-01: READY
  TC-CL-006-02: TODO
  TC-CL-006-03: TODO
  TC-CL-006-04: TODO
  TC-CL-007: PROPOSED
  TC-CL-007-01: TODO
  TC-CL-007-02: TODO
  TC-CL-007-03: TODO
  TC-CL-007-04: TODO
  TC-CL-007-05: TODO
  TC-CL-007-06: TODO
```

---

## PART X — VALIDATION MATRIX

```yaml
# validation-command-matrix.yaml
validations:
  - id: VAL-TC-001
    taskcard: TC-CL-001
    type: unit_test
    command: ".venv/Scripts/pytest tests/capability_layer/test_state_derivation.py -v"
    expected: "3 passed, 0 failed"
    mandatory: true
    regression_level: true

  - id: VAL-TC-002
    taskcard: TC-CL-001
    type: artifact_inspection
    command: |
      python -c "
      import json
      m = json.load(open('reports/capability-layer/unified-capability-map.json'))
      caps = m.get('capabilities', m if isinstance(m, list) else [])
      bad = [c for c in caps if c.get('current_state')=='example_verified' and not c.get('example_refs')]
      print(f'BAD_COUNT={len(bad)}')
      assert len(bad) == 0, f'{len(bad)} false example_verified records remain'
      "
    expected: "BAD_COUNT=0"
    mandatory: true

  - id: VAL-TC-003
    taskcard: TC-CL-001
    type: governance_validator
    command: "python tools/capability_layer/validate_capability_map.py"
    expected: "VAL-011 PASS; exit 0 or exit 2 (advisory only)"
    mandatory: true

  - id: VAL-TC-004
    taskcard: TC-CL-002
    type: governance_validator
    command: "python tools/capability_layer/validate_capability_map.py"
    expected: "VAL-009 PASS; exit 0 or exit 2"
    mandatory: true

  - id: VAL-TC-005
    taskcard: TC-CL-002
    type: artifact_inspection
    command: |
      python -c "
      import json
      from datetime import datetime, timezone
      q = json.load(open('reports/capability-layer/action-queue.json'))
      age = (datetime.now(timezone.utc) - datetime.fromisoformat(q['generated_at'])).days
      print(f'AGE_DAYS={age}')
      assert age < 14
      "
    expected: "AGE_DAYS < 14"
    mandatory: true

  - id: VAL-TC-006
    taskcard: TC-CL-003
    type: artifact_inspection
    command: |
      python -c "
      import json
      m = json.load(open('reports/capability-layer/sal-driven-capability-map.json'))
      caps = m if isinstance(m, list) else m.get('capabilities', [])
      with_obls = [c for c in caps if c.get('obligation_ids')]
      print(f'SAL_GROUNDED={len(with_obls)}')
      assert len(with_obls) >= 100
      "
    expected: "SAL_GROUNDED >= 100"
    mandatory: true

  - id: VAL-TC-007
    taskcard: TC-CL-003
    type: artifact_inspection
    command: |
      python -c "
      import json
      m = json.load(open('reports/capability-layer/unified-capability-map.json'))
      caps = m.get('capabilities', m if isinstance(m, list) else [])
      missing = [c for c in caps if 'authority_class' not in c]
      print(f'MISSING_AUTHORITY_CLASS={len(missing)}')
      assert len(missing) == 0
      "
    expected: "MISSING_AUTHORITY_CLASS=0"
    mandatory: true

  - id: VAL-TC-008
    taskcard: TC-CL-005
    type: artifact_inspection
    command: "python -c \"import os; assert os.path.exists('.local/capability-layer/gap-closure-candidates.json'), 'file missing'\""
    expected: "file exists"
    mandatory: true

  - id: VAL-TC-009
    taskcard: TC-CL-005
    type: state_check
    command: |
      python -c "
      import json
      # Verify gap-ledger-active.json unchanged (DEFERRED count still 32)
      a = json.load(open('reports/capability-layer/gap-ledger-active.json'))
      gaps = a.get('gaps', a if isinstance(a, list) else [])
      print(f'ACTIVE_GAP_COUNT={len(gaps)}')
      "
    expected: "ACTIVE_GAP_COUNT=32"
    mandatory: true
    note: "Confirms no auto-close happened"

  - id: VAL-TC-010
    taskcard: TC-CL-006
    type: artifact_inspection
    command: |
      python -c "
      import json
      nwi = json.load(open('.local/supervisor/next-work-items.json'))
      assert 'work_selection_mode' in nwi, 'work_selection_mode missing'
      print(f'MODE={nwi[\"work_selection_mode\"]}')
      "
    expected: "MODE=CAPABILITY_COMPILER_MERGED or EXPANSION_GOAL_FALLBACK"
    mandatory: true

  - id: VAL-TC-011
    taskcard: TC-CL-007
    type: idempotency
    command: |
      python tools/capability_layer/capability_map_generator.py
      python -c "import hashlib,json; h=hashlib.sha256(open('reports/capability-layer/unified-capability-map.json','rb').read()).hexdigest(); print(f'HASH1={h}')"
      python tools/capability_layer/capability_map_generator.py
      python -c "import hashlib,json; h=hashlib.sha256(open('reports/capability-layer/unified-capability-map.json','rb').read()).hexdigest(); print(f'HASH2={h}')"
    expected: "HASH1 == HASH2"
    mandatory: true

  - id: VAL-TC-012
    taskcard: TC-CL-007
    type: governance_check
    command: "python -c \"import yaml; m=yaml.safe_load(open('plans/layers/capability-layer.md').read().split('---')[1]); assert m.get('maturity')==5\""
    expected: "maturity = 5"
    mandatory: true
```

### Negative Control Matrix

```yaml
# negative-control-matrix.yaml
controls:
  - id: NC-001
    description: "example_verified with empty example_refs must not exist post-fix"
    check: VAL-TC-002
    expected_failure_before_fix: "BAD_COUNT=393"
    expected_pass_after_fix: "BAD_COUNT=0"

  - id: NC-002
    description: "action-queue.json must not have advisory_only=false items"
    check: VAL-TC-004 (VAL-009)
    expected_failure_before_regen: "74 VAL-009 failures"
    expected_pass_after_regen: "VAL-009 PASS"

  - id: NC-003
    description: "gap-closure scanner must NOT modify gap-ledger-active.json"
    check: VAL-TC-009
    expected: "ACTIVE_GAP_COUNT=32 unchanged before and after scanner"

  - id: NC-004
    description: "SAL compiler must not overwrite on second run if content unchanged"
    check: VAL-TC-011 (idempotency)
    expected: "SHA-256 identical; no file modification timestamp change if content unchanged"

  - id: NC-005
    description: "DEFERRED gaps must never appear in gap-closure-candidates.json"
    check: manual inspection of gap-closure-candidates.json
    expected: "no DEFERRED_BY_DESIGN gap_id in candidates list"
```

---

## PART XI — EVIDENCE CONTRACT

```yaml
# evidence-contract.md
authoritative_plan: C:\Users\prora\.claude\plans\humble-hatching-lark.md
artifact_role: evidence_obligations_only
execution_authority: false

evidence_root: .local/evidences/capability-layer-healing-{run_id}/

required_evidence_per_taskcard:
  TC-CL-001:
    - before_after_state_count_table.txt
    - pytest_test_state_derivation_log.txt
    - validate_capability_map_post_fix_output.txt
    - patched_function_code_excerpt.txt

  TC-CL-002:
    - action_queue_header_before.json
    - action_queue_header_after.json
    - val_009_output_before.txt
    - val_009_output_after.txt
    - source_ledger_hash_verification.txt

  TC-CL-003:
    - sal_driven_map_header.json
    - sal_grounded_record_count.txt
    - authority_class_sample_records.json
    - unified_map_post_merge_sample.json
    - autonomous_cycle_dry_run_log.txt

  TC-CL-004:
    - capability_authority_model_diff.txt
    - capability_consumer_graph_diff.txt
    - l03_layer_plan_before_after.txt

  TC-CL-005:
    - gap_closure_candidates_sample.json
    - gap_ledger_active_unchanged_verification.txt

  TC-CL-006:
    - next_work_items_with_mode_field.json
    - cycle_log_showing_mode_message.txt

  TC-CL-007:
    - full_validator_output.txt
    - idempotency_hash_comparison.txt
    - capability_layer_healing_report_path.txt
    - evidence_declaration_path.yaml
    - autonomous_cycle_exit_code.txt

evidence_naming_convention:
  prefix: "tc{taskcard_id}_{description}"
  location: ".local/evidences/capability-layer-healing-{run_id}/"

evidence_must_not_contain:
  - "alternative execution instructions"
  - "competing plan content"
  - "overriding task selection"
```

---

## PART XII — QUALITY SCORING FRAMEWORK

```yaml
# quality-scoring.yaml
dimensions:
  child:
    - requirement_correctness: "Does this child solve the right problem?"
    - implementation_correctness: "Is the change logically correct?"
    - scope_discipline: "Did it stay in allowed files?"
    - validation_strength: "Is the acceptance check meaningful?"
    - evidence_completeness: "Is completion provable?"
    - regression_safety: "No unintended side effects?"
    - production_readiness: "Stable under repeated runs?"

  parent:
    - root_cause_coverage: "Does it fully address the root cause?"
    - child_completeness: "All children address necessary sub-goals?"
    - integration_completeness: "Integration checks cover real risks?"
    - dependency_correctness: "DAG ordering prevents conflicts?"
    - preserved_behavior: "Nothing working was broken?"
    - evidence_completeness: "Parent-level proof available?"
    - rerun_consistency: "Idempotent?"
    - production_readiness: "Safe for repeated autonomous execution?"

scoring_scale: 1-5
acceptance_threshold: 4
reroute_trigger: "any mandatory dimension < 4"
reroute_action: "mark REROUTED; create repair child; re-execute from repair child"
```

---

## PART XIII — PLAN RECONCILIATION

```yaml
# plan-reconciliation-report.md
status: RECONCILED

checks:
  one_authoritative_plan: PASS (only humble-hatching-lark.md)
  all_sections_analyzed: PASS (16 sections per ledger)
  all_actionables_represented: PASS (15 requirements → 7 parents → 30 children → 89 micro-steps)
  all_children_linked_to_parents: PASS
  all_micro_steps_linked_to_children: PASS
  phase_order_correct: PASS (DAG enforced)
  no_taskcard_contradicts_analysis: PASS
  no_stale_instruction_unmarked: PASS (old "Phased Execution" section replaced by Part VII)
  no_required_evidence_dropped: PASS (evidence contract covers all TCs)
  parent_close_requires_children: PASS (machine state rules enforced)

changes_made_from_v2:
  - Added: PART I (preflight, authority, structure profile)
  - Added: PART III (section processing ledger)
  - Added: PART IV (requirements inventory, 15 REQ-CL-NNN)
  - Added: PART V (solution options analysis)
  - Added: PART VI (deep analysis per plan part, 7 PP-NNN entries)
  - Added: PART VII (full hierarchy: 7 parents, 30 children, 89 micro-steps)
  - Added: PART VIII (dependency DAG, file ownership)
  - Added: PART IX (machine state model, current states)
  - Added: PART X (validation matrix, negative controls)
  - Added: PART XI (evidence contract)
  - Added: PART XII (quality scoring framework)
  - Added: PART XIII (this reconciliation)
  - Added: PART XIV (execution handoff)
  - Preserved: All analysis from Part II (honest assessment, system state, root causes, what to preserve, tradeoffs)
  - Replaced: "Phased Execution" flat blocks → full hierarchy in Part VII
  - Replaced: "Taskcard Status Table" → machine state in Part IX

material_removals: none (no valid content removed)
stale_instructions_replaced: "Phased Execution" section replaced by hierarchical Part VII
```

---

## PART XIV — EXECUTION HANDOFF

```yaml
# execution-readiness-verdict.md
verdict: PLAN_MICRO_TASKCARDIZED_READY_FOR_EXECUTION

authoritative_plan: C:\Users\prora\.claude\plans\humble-hatching-lark.md
authority_source: user_plan_mode_conversation
duplicate_plans: none

first_executable_parent: TC-CL-001
first_executable_child: TC-CL-001-01
first_micro_step: MS-CL-001-01-01

parallel_start_option:
  - TC-CL-001-01 (bug investigation) AND TC-CL-002-01 (queue generator investigation)
  - These are read-only investigations with no file conflicts; safe to parallelize

execution_instructions_for_agent:

  1. Read this plan file fully before starting any work.

  2. Identify the current execution position:
     - Read Part IX (machine state) to find which taskcard has Status: READY and no READY children yet
     - That is the next child to execute

  3. Before starting each child taskcard:
     a. Confirm all preconditions are met (check parent status, dependency TCs)
     b. Identify the exact target file and micro-step
     c. Confirm allowed files from the Scope section
     d. Confirm forbidden files from the Scope section

  4. Execute exactly one micro-step at a time:
     a. Change status to ACTIVE
     b. Perform exactly the action stated (no scope expansion)
     c. Capture the expected output
     d. Change status to COMPLETE

  5. After all micro-steps complete:
     a. Run the child's Acceptance checks
     b. Record evidence in .local/evidences/capability-layer-healing-{run_id}/
     c. Score the child on all quality dimensions
     d. If any dimension < 4: mark REROUTED; create repair micro-step; do not close
     e. If all >= 4: mark child SCORED then CLOSED

  6. After all children of a parent complete:
     a. Run the parent's Parent acceptance criteria
     b. Run all Integration checks from the parent block
     c. Update parent state through INTEGRATION_PENDING → VERIFIED → SCORED → CLOSED

  7. Advance to the next ready child or parent per the DAG in Part VIII.

  8. After TC-CL-006 is CLOSED:
     a. Advance to TC-CL-007
     b. TC-CL-007 children can proceed in order (they are sequential)

  9. When TC-CL-007-06 is COMPLETE:
     a. The plan is complete
     b. Write plan lock: python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/<filename> --terminal
     b. Report to user: "Plan humble-hatching-lark complete. All 7 parent taskcards closed."
     c. STOP. Do not start new sprints.

agent_must_not:
  - choose work outside this plan's task hierarchy
  - close a parent before all children are CLOSED
  - close a child before acceptance checks pass
  - treat code existence as validation
  - treat micro-step PENDING as COMPLETE
  - modify gap-ledger.json or gap-ledger-active.json (unless explicitly required)
  - auto-close any gap in gap-ledger (scanner is flag-only)
  - skip micro-steps without marking SKIPPED_NOT_APPLICABLE with reason
  - create a competing plan

blockers:
  - Action queue generator CLI (TC-CL-002-01 resolves before implementation)
  - capability_compiler.py exact CLI (TC-CL-003-01 resolves before invocation)
  - capability_map_generator.py exact function name at bug location (TC-CL-001-01 resolves)

deferred:
  - SAL ingestion for non-ODF formats (Lane 14-15 work, explicitly out of scope)
  - Full capability_pipeline.py end-to-end run (deferred per Tradeoff 3)
  - Auditing 1,447 archived gap closures (explicitly out of scope)
```

---

## PART XV — SUMMARY STATUS TABLE

| TC-ID | Title | Phase | Parent Status | Children | Notes |
|-------|-------|-------|---------------|----------|-------|
| TC-CL-001 | Fix state derivation bug | 1 | READY | 6 | First in order |
| TC-CL-002 | Regenerate action-queue | 1 | READY | 4 | Parallel with TC-CL-001 |
| TC-CL-003 | SAL compiler + authority_class | 2 | READY | 5 | Needs TC-CL-001 done |
| TC-CL-004 | Document two-track authority | 2 | READY | 3 | Needs TC-CL-003 done |
| TC-CL-005 | Gap closure detection | 3 | READY | 4 | Needs TC-CL-003 done |
| TC-CL-006 | Work-source fallback visible | 3 | READY | 4 | Parallel with TC-CL-005 |
| TC-CL-007 | Final validation + idempotency | 3 | PROPOSED | 6 | Needs all prior closed |

**Total parent taskcards:** 7
**Total child taskcards:** 30
**Total micro-steps:** 89
**Investigation children:** 4 (TC-CL-001-01, TC-CL-002-01, TC-CL-003-01, TC-CL-005-01)
**Parallel-safe pairs:** (TC-CL-001 ∥ TC-CL-002), (TC-CL-005 ∥ TC-CL-006)
