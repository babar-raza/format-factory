# Format Factory — Forensic Skill/Command-Only Governance Audit & Hardening
# Plan: imperative-floating-book
# Mission: FF-SGOV-001
# Type: machinery_hardening
# Version: 2.0 (micro-taskcardized 2026-07-10)
# Created: 2026-07-10
# Authority: SOLE EXECUTION AUTHORITY — do not create competing plans

---

## PART 1 — PLAN AUTHORITY & PREFLIGHT

### active-plan-authority-verdict

```yaml
authoritative_plan: plans/.claude/imperative-floating-book.md
authority_source: per-chat-plan-mode (loaded from ~/.claude/plans/imperative-floating-book.md)
artifact_role: EXECUTION_AUTHORITY
execution_authority: true
plan_title: "FF-SGOV-001 Forensic Skill/Command-Only Governance Audit & Hardening"
plan_version: "2.0"
plan_type: machinery_hardening
mission_id: FF-SGOV-001
competing_plans_found: none
duplicate_risk: LOW (single plan, no v2/final/revised copies created)
```

### taskcardization-preflight

```yaml
repository_path: c:\Users\prora\OneDrive\Documents\GitHub\format-factory
branch: main
head_commit: af879e55
git_status: 73 modified / 28 new untracked files (pre-plan state)
active_plan_path: plans/.claude/imperative-floating-book.md
plan_format: markdown-with-yaml-blocks
plan_authority_source: per-chat-plan-mode
plan_size_v1: ~56KB (37 taskcards, compact format)
plan_size_v2: ~150KB (37 parent TCs + ~100 child TCs + ~280 micro-steps)
major_section_count_v1: 15 sections
major_section_count_v2: 12 parts, 38 sections
existing_taskcard_sections_v1: Wave-based (W0-W7), single-level TCs
existing_taskcard_format_v1: inline YAML blocks (not parent/child/micro-step)
existing_lanes: 7 waves (Wave 0 through Wave 7)
existing_gates: per-TC focused_verification
existing_state_vocabulary: OPEN / CLOSED
existing_validation_model: per-TC focused_verification lists
existing_evidence_model: per-TC steps list
existing_normalization_conventions: TC-SGOV-Wn-NNN (stable IDs)
naming_conventions: TC-SGOV-W<wave>-<seq3> / MS-SGOV-W<wave>-<seq3>-<child>-<step>
execution_handoff_v1: present (bottom of plan)
duplicate_plan_risk: NONE

corrections_from_deep_analysis:
  - CI ALREADY WIRED: governance-check + skill-attribution-check jobs exist in ci.yml
    Action: TC-SGOV-W2-002 scope changes to "verify active + remove continue-on-error"
  - taskcard-execution-contract.schema.json MISSING:
    Action: TC-SGOV-W2-003 scope confirmed as CREATE task
  - validate_plan_skill_routes.py MISSING:
    Action: TC-SGOV-W2-004 scope confirmed as CREATE task
  - grade_declared_work.py has NO skill_id check:
    Action: TC-SGOV-W3-003 scope confirmed as ADD code change
  - V-SGF-001 ALREADY EXISTS in governance_validators_ext.py lines 1305-1404:
    Action: TC-SGOV-W3-001 changes to "verify V-SGF-001 + add V-SGF-002 receipt check"
  - install_hooks.py FULLY IMPLEMENTED (idempotent, status() verifies):
    Action: TC-SGOV-W2-001 simplified to "run install + verify"
```

### plan-section-inventory

```yaml
- section_id: S00
  title: "Plan Authority & Preflight"
  type: GOVERNANCE_METADATA
  analysis_completed: true
  actionable_items: 0
  change_status: NEW_IN_V2

- section_id: S01
  title: "Context"
  type: BACKGROUND_NARRATIVE
  analysis_completed: true
  actionable_items: 0
  change_status: PRESERVED

- section_id: S02
  title: "Baseline State"
  type: EVIDENCE_BASELINE
  analysis_completed: true
  actionable_items: 0
  change_status: PRESERVED

- section_id: S03
  title: "What Is Already Proven Working"
  type: EVIDENCE_PRESERVED_STATE
  analysis_completed: true
  actionable_items: 0
  change_status: UPDATED (corrections from deep analysis)

- section_id: S04
  title: "Deep Analysis + Solution Options"
  type: ANALYSIS
  analysis_completed: true
  actionable_items: 0
  change_status: NEW_IN_V2

- section_id: S05
  title: "Requirements Inventory"
  type: TRACEABILITY
  analysis_completed: true
  actionable_items: 0
  change_status: NEW_IN_V2

- section_id: S06
  title: "Wave 0 (CLOSED)"
  type: COMPLETED
  analysis_completed: true
  change_status: PRESERVED

- section_id: S07
  title: "Wave 1 — Verify Existing Artifacts"
  type: INVESTIGATION_WAVE
  parent_tcs: [W1-001, W1-002, W1-003, W1-004, W1-005]
  change_status: EXPANDED_TO_FULL_HIERARCHY

- section_id: S08
  title: "Wave 2 — Wire Enforcement Points"
  type: IMPLEMENTATION_WAVE
  parent_tcs: [W2-001, W2-002, W2-003, W2-004, W2-005]
  change_status: EXPANDED_PLUS_CORRECTED

- section_id: S09
  title: "Wave 3 — Supervisor + Close-Task Hardening"
  type: IMPLEMENTATION_WAVE
  parent_tcs: [W3-001, W3-002, W3-003]
  change_status: EXPANDED_PLUS_CORRECTED

- section_id: S10
  title: "Wave 4 — Micro-Skill Creation Protocol"
  type: IMPLEMENTATION_WAVE
  parent_tcs: [W4-001, W4-002]
  change_status: EXPANDED_TO_FULL_HIERARCHY

- section_id: S11
  title: "Wave 5 — Pilot Execution (15 Pilots)"
  type: VERIFICATION_WAVE
  parent_tcs: [W5-001 through W5-015]
  change_status: EXPANDED_TO_FULL_HIERARCHY

- section_id: S12
  title: "Wave 6 — Historical Backfill"
  type: BACKFILL_WAVE
  parent_tcs: [W6-001, W6-002]
  change_status: EXPANDED_TO_FULL_HIERARCHY

- section_id: S13
  title: "Wave 7 — Final Audit + Closeout"
  type: CLOSEOUT_WAVE
  parent_tcs: [W7-001, W7-002, W7-003, W7-004]
  change_status: EXPANDED_TO_FULL_HIERARCHY

- section_id: S14
  title: "Execution DAG"
  type: DEPENDENCY_GRAPH
  change_status: NEW_IN_V2

- section_id: S15
  title: "State Machine"
  type: MACHINE_STATE
  change_status: NEW_IN_V2

- section_id: S16
  title: "Validation Matrix"
  type: VERIFICATION
  change_status: NEW_IN_V2

- section_id: S17
  title: "Evidence Contract"
  type: EVIDENCE_OBLIGATIONS
  change_status: NEW_IN_V2

- section_id: S18
  title: "Plan Reconciliation"
  type: RECONCILIATION
  change_status: NEW_IN_V2

- section_id: S19
  title: "Execution Handoff"
  type: HANDOFF
  change_status: NEW_IN_V2
```

### complete-plan-read-confirmation

```
ALL SECTIONS READ: YES
Sections: S00-S19 (19 sections)
Waves analyzed: W0-W7 (7 waves, 37 parent TCs)
Original plan read: COMPLETE (56KB, via persisted output)
Deep-analysis agent run: YES (10 files inspected, corrections applied)
Section processing: ALL SECTIONS ANALYZED before taskcardization
```

---

## PART 2 — CONTEXT (PRESERVED)

The Format Factory repository has accumulated a large skill/command governance
infrastructure (120 registered skills, 165 validators, product-code ledger, evidence
schema, pre-mutation guard, pre-commit hook script) built across SKILL-FIRST-001
(cached-growing-snail) and SKILL-FIRST-002 (twinkly-gliding-thimble). However, forensic
investigation shows the enforcement chain has gaps:

- The pre-commit hook exists in `.hooks/` and `install_hooks.py` is fully implemented
  but its installation in `.git/hooks/` is unverified.
- CI has `governance-check` (lines 86-104) and `skill-attribution-check` (lines 55-84)
  jobs already in `.github/workflows/ci.yml`; however `skill-attribution-check` has
  `continue-on-error: true` making it advisory only.
- `taskcard-execution-contract.schema.json` does NOT exist (only `stage2-taskcard-contract.schema.json`).
- `validate_plan_skill_routes.py` does NOT exist (EP-009).
- `grade_declared_work.py` has NO skill_id checking despite being the grading engine.
- 15 pilots required by the governance spec have not been run.
- V-SGF-001 IS active in `governance_validators_ext.py` (lines 1305-1404) but V-SGF-002
  (receipt check) does not exist.

This plan closes all remaining gaps — wiring active enforcement, creating missing components,
proving direct mutations are blocked by two independent layers, and verifying all 15 pilots.

---

## PART 3 — BASELINE STATE (PRESERVED)

```yaml
governance_audit_baseline:
  mission_id: FF-SGOV-001
  repository_root: c:\Users\prora\OneDrive\Documents\GitHub\format-factory
  branch: main
  head: af879e55
  active_plan: plans/.claude/imperative-floating-book.md (this file)
  supervisor_state: AUTONOMOUS_CONTINUE=YES (last sprint vast-weaving-lampson ACCEPTED)
  tests_passing: 1169

skill_roots:
  - .supervisor/skill-registry.yaml              # 120 skills (117 active), fail-closed
  - .supervisor/capability-routing-registry.yaml # 30 routes
command_roots:
  - .claude/commands/                            # 124 command files
canonical_policy:
  - docs/governance/skill-only-policy.yaml       # v2.0, canonical, EXISTS
agent_instruction_paths:
  - CLAUDE.md
  - AGENTS.md
  - docs/governance/codex-adapter.md             # EXISTS
mutation_guards:
  - tools/governance/pre_mutation_guard.py       # EP-002: exists, NOT auto-invoked
  - .hooks/pre-commit-skill-guard                # EP-007: EXISTS, install unverified
  - tools/governance/install_hooks.py            # fully implemented (idempotent, status())
ci_enforcement:
  - .github/workflows/ci.yml job governance-check (lines 86-104) ACTIVE
  - .github/workflows/ci.yml job skill-attribution-check (lines 55-84) ACTIVE continue-on-error=true
  - tools/governance/run_ci_governance_check.py  ACTIVE in CI
  - tools/governance/ci_skill_attribution_check.py ACTIVE in CI (warn-only)
validators:
  - tools/supervisor/governance_validators_ext.py V-SGF-001 (lines 1305-1404) ACTIVE
  - tools/supervisor/governance_validators*.py   165 validators total

confirmed_missing:
  - .supervisor/schemas/taskcard-execution-contract.schema.json  (MISSING)
  - tools/governance/validate_plan_skill_routes.py               (MISSING, EP-009)
  - V-SGF-002 in governance_validators_ext.py                    (MISSING)
  - skill_id check in tools/supervisor/grade_declared_work.py    (MISSING)
```

### What Is Already Proven Working (VERIFIED)

| Component | Path | Verified Status |
|---|---|---|
| Canonical policy | `docs/governance/skill-only-policy.yaml` | v2.0 ACTIVE |
| Codex adapter | `docs/governance/codex-adapter.md` | ACTIVE |
| Skill registry | `.supervisor/skill-registry.yaml` | 120 skills, fail-closed |
| Routing registry | `.supervisor/capability-routing-registry.yaml` | 30 routes |
| 165 validators | `tools/supervisor/governance_validators*.py` | Active, V-SGF-001 CONFIRMED |
| V-SGF-001 | `governance_validators_ext.py` lines 1305-1404 | CONFIRMED ACTIVE |
| CI governance-check job | `.github/workflows/ci.yml` lines 86-104 | CONFIRMED ACTIVE |
| CI skill-attribution job | `.github/workflows/ci.yml` lines 55-84 | CONFIRMED (continue-on-error=true) |
| Evidence schema | `.supervisor/schemas/evidence-declaration.schema.json` | ACTIVE |
| Product-code ledger | `reports/r90/product-code-change-ledger.json` | SHA-256 tracking |
| Pre-mutation guard | `tools/governance/pre_mutation_guard.py` | EXISTS (not auto-invoked) |
| Pre-commit hook | `.hooks/pre-commit-skill-guard` | EXISTS (install unverified) |
| Hook installer | `tools/governance/install_hooks.py` | FULLY IMPLEMENTED (idempotent) |
| Taskcard validator | `tools/governance/validate_taskcard_execution_contract.py` | EXISTS, enforces skill_ids |
| CI runner | `tools/governance/run_ci_governance_check.py` | EXISTS, composite |
| CI checker | `tools/governance/ci_skill_attribution_check.py` | EXISTS, full logic |

---

## PART 4 — DEEP ANALYSIS & SOLUTION OPTIONS

### plan-part-deep-analysis (summary)

```yaml
- plan_part_id: PA-001
  plan_part_path: "Wave 2 — Wire Enforcement Points"
  objective: "Activate the enforcement mechanisms that exist but are not wired or blocking"
  root_causes_addressed:
    - pre-commit hook installs needed (EP-007)
    - CI skill-attribution is advisory only (continue-on-error=true)
    - taskcard-execution-contract.schema.json MISSING
    - validate_plan_skill_routes.py MISSING (EP-009)
    - autonomous_cycle.py has no receipt auto-write
  failure_modes:
    - install_hooks.py fails on Windows symlink (fallback: file copy in line 81)
    - ci.yml governance-check already active — no wiring needed, only verifying
    - schema creation may break validate_taskcard_execution_contract.py if wrong format
  decomposition_strategy: 5 focused child groups, one per EP gap
  taskcardization_decision: EXPAND_TO_FULL_PARENT_CHILD_MICRO_STEPS

- plan_part_id: PA-002
  plan_part_path: "Wave 3 — Supervisor Hardening"
  objective: "Make supervisor reject unskilled PRODUCT_SOURCE work at grade time"
  root_causes_addressed:
    - grade_declared_work.py has no skill_id checking (confirmed missing)
    - V-SGF-002 (receipt check) does not exist
    - close-layer-task.md does not require skill receipt before close
  failure_modes:
    - Adding skill_id check to grader may break existing evidence declarations
    - Need to preserve backward-compat with pre-governance declarations
  selected_solution: SURGICAL_ADDITION (add _validate_skill_ids function, graceful fallback)
  decomposition_strategy: 3 TCs, 2-3 children each

- plan_part_id: PA-003
  plan_part_path: "Wave 5 — 15 Pilots"
  objective: "Run materially different pilots proving governance enforces or catches bypasses"
  root_causes_addressed:
    - No empirical proof that any enforcement layer has triggered in production
  key_insight: >
    Pilot 1 (pre-commit) is the most critical — it tests the FIRST technical barrier.
    Pilot 7 (product sprint) proves the happy path works end-to-end.
    Pilots 9/11/12 prove negative controls.
  decomposition_strategy: standardized 2-child structure per pilot, compact micro-steps

- plan_part_id: PA-004
  plan_part_path: "Wave 2 TC-SGOV-W2-002 (CI)"
  objective: "CI enforcement fully active for skill governance"
  CORRECTION: CI governance-check job ALREADY EXISTS and is ACTIVE
  revised_objective: "Change skill-attribution-check from continue-on-error=true to false,
    making it BLOCKING; verify both CI jobs pass on current state"
  taskcardization_decision: SCOPE_CORRECTED_THEN_EXPAND
```

### solution-options-analysis (Wave 2 EP-007 hook installation)

```yaml
option_a:
  name: "Run install_hooks.py (recommended)"
  approach: "Execute existing fully-implemented installer; verify via status() function"
  root_cause_coverage: 5
  production_durability: 5
  implementation_safety: 5
  testability: 5
  selected: true
  rationale: "install_hooks.py is idempotent, Windows-compatible, has verify built-in"

option_b:
  name: "Manual symlink / file copy"
  approach: "ln -s or copy .hooks/pre-commit-skill-guard .git/hooks/pre-commit"
  root_cause_coverage: 5
  implementation_safety: 3
  testability: 3
  selected: false
  rationale: "Non-idempotent, Windows-unsafe, duplicates what install_hooks.py already does"

option_c:
  name: "CI-only (no local hook)"
  approach: "Rely purely on CI skill-attribution-check job"
  root_cause_coverage: 3
  rationale: "CI runs post-commit, not pre-commit — too late for first barrier requirement"
  selected: false
```

### solution-options-analysis (Wave 3 grade_declared_work skill_id check)

```yaml
option_a:
  name: "Surgical addition of _validate_skill_ids() function (recommended)"
  approach: "Add function after line 60 of grade_declared_work.py; call in grade loop;
    return REWORK_REQUIRED for missing_declared_skill_ids; graceful fallback for registry error"
  root_cause_coverage: 5
  backward_compat: 5  # graceful fallback allows pre-governance declarations to pass
  implementation_safety: 4
  selected: true
  exact_insertion_point: "grade_declared_work.py after _hash_evidence() function"
  code_reference: "tools/supervisor/grade_declared_work.py ~line 60"

option_b:
  name: "New governance validator V-SGF-003"
  approach: "Add V-SGF-003 to governance_validators_ext.py that checks graded items for skill_ids"
  root_cause_coverage: 4
  implementation_safety: 5
  selected: false
  rationale: "Validators fire only on declaration submission; grader integration is more direct"
```

---

## PART 5 — REQUIREMENTS INVENTORY

### normalized-requirements-inventory

| REQ-ID | Domain | Source Section | Description | Mapped TC(s) |
|---|---|---|---|---|
| REQ-GOV-001 | EP-007 | Wave 2 | Pre-commit hook installed and blocking src/ direct edits | W2-001 |
| REQ-GOV-002 | EP-006 | Wave 2 | CI skill-attribution-check is BLOCKING (not continue-on-error) | W2-002 |
| REQ-GOV-003 | EP-008 | Wave 2 | taskcard-execution-contract.schema.json exists and enforced | W2-003 |
| REQ-GOV-004 | EP-009 | Wave 2 | validate_plan_skill_routes.py exists and validates plan TCs | W2-004 |
| REQ-GOV-005 | EP-004 | Wave 2 | Execution receipts auto-written by autonomous_cycle.py | W2-005 |
| REQ-SUP-001 | Supervisor | Wave 3 | V-SGF-002 validator checks receipt presence for PRODUCT_SOURCE | W3-001 |
| REQ-SUP-002 | Closeout | Wave 3 | close-layer-task requires skill receipt before close | W3-002 |
| REQ-SUP-003 | Grading | Wave 3 | grade_declared_work.py rejects items without skill_ids | W3-003 |
| REQ-SKL-001 | Skills | Wave 4 | validate-missing-skill-workflow micro-skill exists | W4-001 |
| REQ-SKL-002 | Registry | Wave 4 | Top-5 ad-hoc scripts registered as governed skills | W4-002 |
| REQ-VER-001 | Policy | Wave 1 | skill-only-policy.yaml has all 9 EP entries current | W1-001 |
| REQ-VER-002 | Agents | Wave 1 | AGENTS.md §J references canonical policy | W1-002 |
| REQ-VER-003 | Registry | Wave 1 | All 120 active skills have command_file + impl_path | W1-003 |
| REQ-VER-004 | Routing | Wave 1 | 30 routes cover all 16 governed operations | W1-004 |
| REQ-VER-005 | Infra | Wave 1 | 169 ad-hoc scripts classified (exempt/needs-reg/needs-skill) | W1-005 |
| REQ-PIL-001-015 | Pilots | Wave 5 | 15 pilots pass with evidence records | W5-001 to W5-015 |
| REQ-BKF-001 | Backfill | Wave 6 | Product-code ledger complete since tracking_base_ref | W6-001 |
| REQ-BKF-002 | Backfill | Wave 6 | Last 10 sprints have skill bindings | W6-002 |
| REQ-AUD-001 | Metrics | Wave 7 | Adoption metrics computed (target: accepted_direct_mutations=0) | W7-001 |
| REQ-AUD-002 | Plan | Wave 7 | §32 governance section added to this plan | W7-002 |
| REQ-AUD-003 | Report | Wave 7 | Final report written at .local/governance-audit/FF-SGOV-001-final-report.md | W7-003 |
| REQ-AUD-004 | Closure | Wave 7 | lifecycle_audit.py passes; plan closed --terminal --audit-gate | W7-004 |

---

## PART 6 — WAVE 0 — AUDIT BASELINE (COMPLETE)

**TC-SGOV-W0-001** | Record governance audit baseline | **CLOSED**

Wave 0 output: Baseline YAML in Part 3 of this plan + Wave 0 exploration results.
Deep-analysis confirmed by Explore agent (10 files inspected, corrections applied to plan v2).

---

## PART 7 — WAVE 1 — VERIFY EXISTING ARTIFACTS

**Objective**: Read-verify each governance artifact. Identify stale entries, broken references,
missing fields. Fix in-place only. This wave is INVESTIGATION + LIGHTWEIGHT REPAIR.

Wave 1 is a prerequisite for Wave 2 (enforcement wiring depends on verified artifact state).
All 5 TCs in Wave 1 are PARALLEL-SAFE (different target files).

---

### Parent Taskcard TC-SGOV-W1-001

```yaml
Parent_Taskcard_ID: TC-SGOV-W1-001
Title: "Verify skill-only-policy.yaml has all 9 enforcement-point entries with current gap status"
Type: PARENT
Status: READY
Owner: governance-verification-agent
Supervisor: FF-SGOV-001-audit

Source:
  Plan_requirement_ID: REQ-VER-001
  Plan_section: Wave 1
  Root_cause: "Enforcement gap documentation may be stale since EP status changed in deep analysis"
  Selected_solution: READ + SURGICAL_UPDATE

Objective:
  - Verify docs/governance/skill-only-policy.yaml § enforcement_points covers EP-001–EP-009
    and reflects CONFIRMED states from deep analysis (e.g., EP-006 is ACTIVE in CI)

Scope:
  Allowed_files: [docs/governance/skill-only-policy.yaml]
  Forbidden_files: [CLAUDE.md, AGENTS.md, .supervisor/skill-registry.yaml]
  Path_expansion_rule: NO (exactly one file)

Inputs:
  - docs/governance/skill-only-policy.yaml (current content)
  - Deep analysis findings (EP-006 ACTIVE, EP-007 unverified, EP-009 MISSING)

Outputs:
  - docs/governance/skill-only-policy.yaml updated enforcement_points section
  - .local/governance-audit/ep-status-verified.yaml

Child_taskcards:
  - TC-SGOV-W1-001-01  (Read and record current EP entries)
  - TC-SGOV-W1-001-02  (Update stale EP entries in-place)

Parent_acceptance_criteria:
  - enforcement_points section has exactly 9 entries (EP-001 through EP-009)
  - EP-006 reflects: status=ACTIVE, ci_job=governance-check+skill-attribution-check
  - EP-007 reflects: status=UNVERIFIED_INSTALL_PENDING
  - EP-009 reflects: status=MISSING, tool_needed=validate_plan_skill_routes.py
  - No EP entry has gap_status that contradicts deep analysis findings

Evidence_required:
  - .local/governance-audit/ep-status-verified.yaml (comparison: before/after)

Quality_dimensions:
  - requirement_correctness: all 9 EPs present
  - integration_completeness: EP statuses match repo reality

Closeout_criteria:
  - Both child TCs CLOSED
  - .local/governance-audit/ep-status-verified.yaml written

Rollback_strategy:
  - File is text; revert via git checkout docs/governance/skill-only-policy.yaml
```

#### TC-SGOV-W1-001-01 — Read and record current EP entries
```yaml
Child_Taskcard_ID: TC-SGOV-W1-001-01
Parent_Taskcard_ID: TC-SGOV-W1-001
Title: "Read skill-only-policy.yaml fully and record current EP-001–EP-009 entries"
Type: CHILD
Status: TODO
Scope:
  Allowed_files: [docs/governance/skill-only-policy.yaml]
  Allowed_operation: inspect
Micro_steps:
  MS-W1-001-01-01:
    Action: "Read docs/governance/skill-only-policy.yaml fully (all lines)"
    Target: docs/governance/skill-only-policy.yaml
    Expected: Full file content including enforcement_points section
    Check: "Confirm enforcement_points key exists; count EP entries"
  MS-W1-001-01-02:
    Action: "For each EP-001..EP-009: record current gap_status, blocking bool, implementing_tool"
    Target: docs/governance/skill-only-policy.yaml § enforcement_points
    Expected: 9-entry table with fields (ep_id, gap_status, blocking, implementing_tool)
    Check: "Exactly 9 entries recorded; no EP missing"
  MS-W1-001-01-03:
    Action: "Write .local/governance-audit/ep-status-before.yaml with current entry values"
    Target: .local/governance-audit/ep-status-before.yaml
    Expected: YAML file with 9 EP entries and their current status
    Check: "File exists, 9 entries, valid YAML"
Acceptance_checks:
  - ep-status-before.yaml written with 9 entries
  - Each entry has ep_id, gap_status, blocking, implementing_tool
Evidence: .local/governance-audit/ep-status-before.yaml
Next_valid_task: TC-SGOV-W1-001-02
```

#### TC-SGOV-W1-001-02 — Update stale EP entries in-place
```yaml
Child_Taskcard_ID: TC-SGOV-W1-001-02
Parent_Taskcard_ID: TC-SGOV-W1-001
Title: "Surgically update stale EP entries to reflect confirmed repo state"
Type: CHILD
Status: TODO
Preconditions: [TC-SGOV-W1-001-01 CLOSED]
Scope:
  Allowed_files: [docs/governance/skill-only-policy.yaml]
  Allowed_operation: edit
Micro_steps:
  MS-W1-001-02-01:
    Action: "Update EP-006 gap_status to ACTIVE (governance-check + skill-attribution-check both in ci.yml)"
    Target: docs/governance/skill-only-policy.yaml EP-006 entry
    Expected: "gap_status: ACTIVE, blocking: false (continue-on-error=true; to be fixed in W2-002)"
    Check: "EP-006 entry shows ACTIVE; notes continue-on-error limitation"
  MS-W1-001-02-02:
    Action: "Update EP-007 gap_status to INSTALL_PENDING (installer exists, run not confirmed)"
    Target: docs/governance/skill-only-policy.yaml EP-007 entry
    Expected: "gap_status: INSTALL_PENDING, implementing_tool: tools/governance/install_hooks.py"
    Check: "EP-007 entry shows INSTALL_PENDING"
  MS-W1-001-02-03:
    Action: "Update EP-009 gap_status to MISSING_TOOL (validate_plan_skill_routes.py not found)"
    Target: docs/governance/skill-only-policy.yaml EP-009 entry
    Expected: "gap_status: MISSING_TOOL, tool_needed: tools/governance/validate_plan_skill_routes.py"
    Check: "EP-009 entry shows MISSING_TOOL"
  MS-W1-001-02-04:
    Action: "Write .local/governance-audit/ep-status-after.yaml with updated entries"
    Target: .local/governance-audit/ep-status-after.yaml
    Expected: "Updated YAML with 9 entries reflecting current confirmed state"
    Check: "File exists; EP-006 ACTIVE, EP-007 INSTALL_PENDING, EP-009 MISSING_TOOL"
Acceptance_checks:
  - docs/governance/skill-only-policy.yaml EP-006 shows ACTIVE
  - docs/governance/skill-only-policy.yaml EP-007 shows INSTALL_PENDING
  - docs/governance/skill-only-policy.yaml EP-009 shows MISSING_TOOL
  - ep-status-after.yaml written
Evidence: .local/governance-audit/ep-status-after.yaml
Closeout: "Both micro-steps COMPLETE; EP updates visible in skill-only-policy.yaml"
```

---

### Parent Taskcard TC-SGOV-W1-002

```yaml
Parent_Taskcard_ID: TC-SGOV-W1-002
Title: "Verify AGENTS.md §J (skill-command execution) references canonical policy correctly"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-VER-002
  Root_cause: "AGENTS.md may have divergent skill governance language vs. canonical policy"
Scope:
  Allowed_files: [AGENTS.md]
  Forbidden_files: [CLAUDE.md]
Child_taskcards:
  - TC-SGOV-W1-002-01 (Read AGENTS.md and locate §J)
  - TC-SGOV-W1-002-02 (Add canonical policy reference if missing)
Parent_acceptance_criteria:
  - AGENTS.md §J contains reference to docs/governance/skill-only-policy.yaml
  - No AGENTS.md section grants broad ad-hoc mutation exemption
Evidence: .local/governance-audit/agents-md-verification.yaml
Rollback: git checkout AGENTS.md
```

#### TC-SGOV-W1-002-01 — Read AGENTS.md and locate skill-governance section
```yaml
Child_Taskcard_ID: TC-SGOV-W1-002-01
Micro_steps:
  MS-W1-002-01-01:
    Action: "Read AGENTS.md fully (all sections)"
    Target: AGENTS.md
    Expected: "Full content with section labels"
    Check: "Identify: Does §J or equivalent skill-command section exist?"
  MS-W1-002-01-02:
    Action: "Search for 'skill-only-policy' or 'docs/governance' in AGENTS.md"
    Target: AGENTS.md
    Expected: "Zero matches (likely) or confirmed reference"
    Check: "Record presence/absence"
  MS-W1-002-01-03:
    Action: "Write .local/governance-audit/agents-md-verification.yaml with findings"
    Expected: "{has_skill_governance_section: bool, has_canonical_policy_ref: bool, weak_exemptions: list}"
    Check: "File written, fields populated"
```

#### TC-SGOV-W1-002-02 — Add canonical policy reference if missing
```yaml
Child_Taskcard_ID: TC-SGOV-W1-002-02
Preconditions: [TC-SGOV-W1-002-01 CLOSED]
Status: TODO
Scope:
  Allowed_files: [AGENTS.md]
  Allowed_operation: edit (only if reference is missing)
Micro_steps:
  MS-W1-002-02-01:
    Action: "If canonical policy reference MISSING: add one sentence to AGENTS.md §J:
      'All governed mutations must use a registered skill; see docs/governance/skill-only-policy.yaml'"
    Target: "AGENTS.md — existing skill-governance section or §J"
    Expected: "Single-sentence policy reference added (surgical, no prose rewrite)"
    Check: "docs/governance/skill-only-policy.yaml appears in AGENTS.md"
  MS-W1-002-02-02:
    Action: "If no broad ad-hoc exemptions found: mark step SKIPPED_NOT_APPLICABLE with reason"
    Expected: "No unintended exemptions in AGENTS.md"
    Check: "No section says 'ad-hoc direct edits are acceptable'"
```

---

### Parent Taskcard TC-SGOV-W1-003

```yaml
Parent_Taskcard_ID: TC-SGOV-W1-003
Title: "Audit skill registry: every active skill has command_file path + non-empty implementation_paths"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-VER-003
  Root_cause: "Prior commit 33a13b4e fixed 7 skills; may be others still broken"
Scope:
  Allowed_files: [.supervisor/skill-registry.yaml, .claude/commands/*.md]
  Forbidden_folders: [src/]
Child_taskcards:
  - TC-SGOV-W1-003-01 (Run validate_skill_contracts; capture output)
  - TC-SGOV-W1-003-02 (Fix broken entries identified)
Parent_acceptance_criteria:
  - validate_skill_contracts.py exits 0
  - Zero active skills with empty implementation_paths
  - Zero active skills with missing command_file
Evidence: .local/governance-audit/skill-registry-audit.yaml
```

#### TC-SGOV-W1-003-01 — Run validate_skill_contracts and capture output
```yaml
Child_Taskcard_ID: TC-SGOV-W1-003-01
Micro_steps:
  MS-W1-003-01-01:
    Action: "Run: python tools/supervisor/validate_skill_contracts.py 2>&1 | tee .local/governance-audit/skill-contracts-raw.txt"
    Target: tools/supervisor/validate_skill_contracts.py
    Expected: "Exit 0 (all valid) or exit 1 with list of failing skills"
    Check: "Capture exit code and stdout"
  MS-W1-003-01-02:
    Action: "Parse output: extract list of skills with BROKEN/EMPTY/MISSING status"
    Expected: "List of failing skill_ids (may be empty)"
    Check: "List written to .local/governance-audit/skill-registry-audit.yaml"
  MS-W1-003-01-03:
    Action: "For each failing skill: read its .supervisor/skill-registry.yaml entry to confirm defect"
    Expected: "Exact field(s) missing per skill"
    Check: "Root cause documented (empty implementation_paths vs. missing command_file vs. wrong path)"
```

#### TC-SGOV-W1-003-02 — Fix broken skill registry entries
```yaml
Child_Taskcard_ID: TC-SGOV-W1-003-02
Preconditions: [TC-SGOV-W1-003-01 CLOSED]
Scope:
  Allowed_files: [.supervisor/skill-registry.yaml]
  Allowed_operation: edit
Micro_steps:
  MS-W1-003-02-01:
    Action: "For each broken skill: update implementation_paths to point to actual tool/command file"
    Target: .supervisor/skill-registry.yaml (only the specific skill entry)
    Expected: "implementation_paths: [<actual-file-path>] (non-empty)"
    Check: "Field is non-empty list of real file paths"
  MS-W1-003-02-02:
    Action: "Rerun validate_skill_contracts.py and capture exit code"
    Expected: "Exit 0"
    Check: "Exit code 0; no BROKEN/EMPTY/MISSING skills remain"
Stop_condition: "If >10 skills need repair, pause and record as BLOCKED_EXTERNAL (manual review needed)"
```

---

### Parent Taskcard TC-SGOV-W1-004

```yaml
Parent_Taskcard_ID: TC-SGOV-W1-004
Title: "Verify capability-routing-registry.yaml covers all 16 governed operations"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-VER-004
Scope:
  Allowed_files: [.supervisor/capability-routing-registry.yaml, docs/governance/skill-only-policy.yaml]
  Allowed_operation: inspect (then edit if gaps found)
Child_taskcards:
  - TC-SGOV-W1-004-01 (Cross-check 16 governed_operations vs. 30 routes)
  - TC-SGOV-W1-004-02 (Add MISSING_SKILL_CAPABILITY entries for uncovered operations)
Parent_acceptance_criteria:
  - All 16 governed_operations from skill-only-policy.yaml have at least one route entry
  - Uncovered operations have MISSING_SKILL_CAPABILITY entries with gap_id references
Evidence: .local/governance-audit/routing-coverage.yaml
```

#### TC-SGOV-W1-004-01 — Cross-check governed operations vs. routing routes
```yaml
Child_Taskcard_ID: TC-SGOV-W1-004-01
Micro_steps:
  MS-W1-004-01-01:
    Action: "Read docs/governance/skill-only-policy.yaml § governed_operations (16 items)"
    Expected: "List of 16 governed operation strings"
    Check: "16 operations extracted"
  MS-W1-004-01-02:
    Action: "Read .supervisor/capability-routing-registry.yaml and extract all route_id + route description"
    Expected: "30 routes with their operation coverage"
    Check: "30 routes extracted"
  MS-W1-004-01-03:
    Action: "Map each governed_operation to matching route(s); flag unmatched operations"
    Expected: "Coverage map: {operation: [matching_route_ids]}"
    Check: "Write to .local/governance-audit/routing-coverage.yaml"
```

#### TC-SGOV-W1-004-02 — Add MISSING_SKILL_CAPABILITY entries for coverage gaps
```yaml
Child_Taskcard_ID: TC-SGOV-W1-004-02
Preconditions: [TC-SGOV-W1-004-01 CLOSED]
Scope:
  Allowed_files: [.supervisor/capability-routing-registry.yaml]
  Allowed_operation: edit (only if gaps found)
Micro_steps:
  MS-W1-004-02-01:
    Action: "For each unmatched governed_operation: add MISSING_SKILL_CAPABILITY entry to routing registry"
    Expected: "New entry with current_status: MISSING_SKILL_CAPABILITY and gap_id reference"
    Check: "All 16 governed_operations have at least one matching route entry or explicit MISSING entry"
  MS-W1-004-02-02:
    Action: "Recount routes; verify total is >= 30 (original) + any new entries"
    Check: "No route was inadvertently deleted; new entries are additions only"
```

---

### Parent Taskcard TC-SGOV-W1-005

```yaml
Parent_Taskcard_ID: TC-SGOV-W1-005
Title: "Classify 169 ad-hoc supervisor scripts: INFRA_EXEMPT / NEEDS_REGISTRATION / NEEDS_SKILL"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-VER-005
  Root_cause: "91.4% of supervisor infrastructure scripts (169/185) are AD_HOC — need classification"
Scope:
  Allowed_files: read-only inspection of all tools/supervisor/*.py
  Forbidden_operation: DO NOT MODIFY any tools/supervisor/*.py in this wave
Child_taskcards:
  - TC-SGOV-W1-005-01 (Run detect_ad_hoc_execution.py and capture output)
  - TC-SGOV-W1-005-02 (Classify each AD_HOC script into 3 buckets)
  - TC-SGOV-W1-005-03 (Identify top-5 NEEDS_REGISTRATION candidates for W4-002)
Parent_acceptance_criteria:
  - .local/governance-audit/infra-classification.yaml written with all 169 entries classified
  - Each entry has: {script_path, classification, justification, call_frequency_estimate, mutation_type}
  - Top-5 NEEDS_REGISTRATION candidates identified for W4-002
Evidence: .local/governance-audit/infra-classification.yaml
```

#### TC-SGOV-W1-005-01 — Run detect_ad_hoc_execution.py
```yaml
Child_Taskcard_ID: TC-SGOV-W1-005-01
Micro_steps:
  MS-W1-005-01-01:
    Action: "Run: python tools/supervisor/detect_ad_hoc_execution.py 2>&1 > .local/governance-audit/ad-hoc-raw.txt"
    Expected: "List of scripts classified as AD_HOC, GOVERNED, EXEMPT"
    Check: "Exit code captured; raw output file written"
  MS-W1-005-01-02:
    Action: "Count entries in each category; verify ~169 AD_HOC entries"
    Expected: "AD_HOC count >= 150 (may have changed since baseline)"
    Check: "Count recorded in .local/governance-audit/ad-hoc-raw.txt header"
```

#### TC-SGOV-W1-005-02 — Classify each AD_HOC script
```yaml
Child_Taskcard_ID: TC-SGOV-W1-005-02
Preconditions: [TC-SGOV-W1-005-01 CLOSED]
Micro_steps:
  MS-W1-005-02-01:
    Action: "For each AD_HOC script: read first 20 lines to determine mutation type"
    Expected: "Does it mutate canonical state (ledgers, declarations, registry) or just infra?"
    Check: "Classification assigned: INFRA_EXEMPT | NEEDS_REGISTRATION | NEEDS_SKILL"
  MS-W1-005-02-02:
    Action: "Write .local/governance-audit/infra-classification.yaml with all entries"
    Expected: "YAML list with {script_path, classification, justification} per script"
    Check: "File written; all AD_HOC scripts covered"
Classification_criteria:
  INFRA_EXEMPT: "Pure infrastructure — no canonical state mutation possible (e.g., formatting utils, log readers)"
  NEEDS_REGISTRATION: "Called from agent workflow, should be a governed skill entry"
  NEEDS_SKILL: "Mutates canonical state (ledgers, declarations, registry) — must be wrapped in skill"
```

#### TC-SGOV-W1-005-03 — Identify top-5 NEEDS_REGISTRATION candidates
```yaml
Child_Taskcard_ID: TC-SGOV-W1-005-03
Preconditions: [TC-SGOV-W1-005-02 CLOSED]
Micro_steps:
  MS-W1-005-03-01:
    Action: "From NEEDS_REGISTRATION entries: select top-5 by estimated call frequency or mutation impact"
    Expected: "List of 5 script paths with rationale"
    Check: "Written to .local/governance-audit/infra-classification.yaml § top_candidates"
  MS-W1-005-03-02:
    Action: "For each top-5 candidate: note the skill_id it would map to and existing command file path"
    Expected: "{script_path, proposed_skill_id, proposed_command_file, existing_command_file}"
    Check: "Candidates ready for TC-SGOV-W4-002 consumption"
```

---

## PART 8 — WAVE 2 — WIRE ENFORCEMENT POINTS

**Objective**: Activate enforcement that exists but is not wired or blocking. This wave has REAL CODE CHANGES.
Wave 2 must execute AFTER Wave 1 (needs verified artifact state) and BEFORE Wave 5 (pilots test wired enforcement).

**Dependency**: TC-SGOV-W2-001 must be CLOSED before TC-SGOV-W5-001 can run.

---

### Parent Taskcard TC-SGOV-W2-001

```yaml
Parent_Taskcard_ID: TC-SGOV-W2-001
Title: "Install pre-commit hook via install_hooks.py (EP-007); verify blocking behavior"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-GOV-001
  Root_cause: "EP-007: .hooks/pre-commit-skill-guard exists + install_hooks.py fully implemented
    but installation in .git/hooks/pre-commit is UNVERIFIED"
  Selected_solution: "Run python tools/governance/install_hooks.py; verify via status()"
Scope:
  Allowed_files: [.git/hooks/pre-commit (created by installer)]
  Forbidden_files: [.hooks/pre-commit-skill-guard (must NOT modify the hook script itself)]
Child_taskcards:
  - TC-SGOV-W2-001-01 (Check current hook installation status)
  - TC-SGOV-W2-001-02 (Run install_hooks.py)
  - TC-SGOV-W2-001-03 (Verify blocking behavior with safe test)
Parent_acceptance_criteria:
  - install_hooks.py status() returns hook_dest_is_symlink=true OR hook_dest_exists=true
  - .git/hooks/pre-commit exists (symlink or copy)
  - Running hook manually exits 0 for clean staged files
Evidence: .local/governance-audit/ep-007-status.yaml
Rollback: "python tools/governance/install_hooks.py uninstall"
```

#### TC-SGOV-W2-001-01 — Check current hook installation status
```yaml
Child_Taskcard_ID: TC-SGOV-W2-001-01
Micro_steps:
  MS-W2-001-01-01:
    Action: "Run: python tools/governance/install_hooks.py status"
    Target: tools/governance/install_hooks.py
    Expected: "JSON output with hook_src_exists, hook_dest_exists, hook_dest_is_symlink"
    Check: "Exit 0 means status retrieved; capture hook_dest_exists value"
  MS-W2-001-01-02:
    Action: "If hook_dest_exists=true AND hook_dest_points_to_src=true: record as ALREADY_INSTALLED"
    Expected: "Either ALREADY_INSTALLED or NEEDS_INSTALL"
    Check: "Write .local/governance-audit/ep-007-status.yaml § before_state"
```

#### TC-SGOV-W2-001-02 — Run install_hooks.py (idempotent)
```yaml
Child_Taskcard_ID: TC-SGOV-W2-001-02
Preconditions: [TC-SGOV-W2-001-01 CLOSED]
Micro_steps:
  MS-W2-001-02-01:
    Action: "Run: python tools/governance/install_hooks.py install"
    Expected: "Exit 0 (installed or already installed)"
    Check: "Exit 0 confirms installation; capture stdout message"
  MS-W2-001-02-02:
    Action: "Rerun: python tools/governance/install_hooks.py status"
    Expected: "hook_dest_exists=true, hook_dest_points_to_src=true"
    Check: "Status confirms installation"
  MS-W2-001-02-03:
    Action: "Write .local/governance-audit/ep-007-status.yaml § after_state"
    Expected: "{installed: true, method: symlink_or_copy, installer: tools/governance/install_hooks.py}"
    Check: "File updated"
```

#### TC-SGOV-W2-001-03 — Verify hook blocks ungoverned src/ change (safe test)
```yaml
Child_Taskcard_ID: TC-SGOV-W2-001-03
Preconditions: [TC-SGOV-W2-001-02 CLOSED]
Micro_steps:
  MS-W2-001-03-01:
    Action: "Add a comment line to src/python/fods/fods_codec.py (a disposable safe change)"
    Target: src/python/fods/fods_codec.py line 1 or last line
    Expected: "File modified with comment"
    Check: "git diff shows exactly one line added"
  MS-W2-001-03-02:
    Action: "Stage the change: git add src/python/fods/fods_codec.py"
    Expected: "File staged"
    Check: "git status shows src/python/fods/fods_codec.py in staging"
  MS-W2-001-03-03:
    Action: "Attempt commit WITHOUT providing skill transcript: git commit -m 'test-ep007'"
    Expected: "COMMIT BLOCKED — pre-commit hook exits 1"
    Check: "Exit code != 0; git status shows file still staged and NOT committed"
  MS-W2-001-03-04:
    Action: "Revert staged change: git checkout -- src/python/fods/fods_codec.py"
    Expected: "File restored; staging area clean"
    Check: "git diff HEAD -- src/python/fods/fods_codec.py shows no diff"
  MS-W2-001-03-05:
    Action: "Write .local/governance-audit/pilots/pilot-01-pre-check.yaml with result"
    Expected: "{verdict: BLOCKED, guard: pre-commit-skill-guard, state_changed: false}"
    Check: "File written with correct verdict"
Stop_condition: "If hook does NOT block (exit 0 from commit): do NOT proceed to Wave 5 — open BLOCKED status on W2-001"
```

---

### Parent Taskcard TC-SGOV-W2-002

```yaml
Parent_Taskcard_ID: TC-SGOV-W2-002
Title: "Remove continue-on-error from skill-attribution-check CI job (make it BLOCKING)"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-GOV-002
  Root_cause: "CI skill-attribution-check job exists at .github/workflows/ci.yml lines 55-84
    but has continue-on-error: true making it ADVISORY ONLY — not blocking PRs"
  Correction: "CI is already wired. Task is to make skill-attribution-check BLOCKING."
  Selected_solution: "Edit ci.yml: remove or set continue-on-error: false on skill-attribution-check job"
Scope:
  Allowed_files: [.github/workflows/ci.yml]
  Forbidden_files: [tools/governance/ci_skill_attribution_check.py]
Child_taskcards:
  - TC-SGOV-W2-002-01 (Verify both CI jobs exist and understand their current state)
  - TC-SGOV-W2-002-02 (Remove continue-on-error from skill-attribution-check)
  - TC-SGOV-W2-002-03 (Run ci_skill_attribution_check.py locally to verify exit behavior)
Parent_acceptance_criteria:
  - .github/workflows/ci.yml skill-attribution-check job does NOT have continue-on-error: true
  - python tools/governance/ci_skill_attribution_check.py exits 0 on clean repo state
  - governance-check job remains active and unmodified
Evidence: .local/governance-audit/ep-006-status.yaml
Rollback: git checkout .github/workflows/ci.yml
```

#### TC-SGOV-W2-002-01 — Verify both CI jobs exist and read current state
```yaml
Child_Taskcard_ID: TC-SGOV-W2-002-01
Micro_steps:
  MS-W2-002-01-01:
    Action: "Read .github/workflows/ci.yml lines 55-104 to confirm both jobs"
    Expected: "skill-attribution-check (55-84) with continue-on-error: true; governance-check (86-104)"
    Check: "Both jobs confirmed; note exact line of continue-on-error field"
  MS-W2-002-01-02:
    Action: "Record current state in .local/governance-audit/ep-006-status.yaml § before_state"
    Expected: "{skill_attribution_job_exists: true, continue_on_error: true, governance_check_exists: true}"
    Check: "File written"
```

#### TC-SGOV-W2-002-02 — Remove continue-on-error from skill-attribution-check
```yaml
Child_Taskcard_ID: TC-SGOV-W2-002-02
Preconditions: [TC-SGOV-W2-002-01 CLOSED]
Micro_steps:
  MS-W2-002-02-01:
    Action: "Edit .github/workflows/ci.yml: remove the 'continue-on-error: true' line from skill-attribution-check job"
    Target: .github/workflows/ci.yml (line with continue-on-error: true in skill-attribution-check)
    Expected: "Line removed or changed to 'continue-on-error: false'"
    Check: "grep 'continue-on-error: true' in skill-attribution-check section returns empty"
  MS-W2-002-02-02:
    Action: "Verify governance-check job (lines 86-104) is unchanged"
    Check: "governance-check job still intact; run_ci_governance_check.py still referenced"
```

#### TC-SGOV-W2-002-03 — Run ci_skill_attribution_check.py locally
```yaml
Child_Taskcard_ID: TC-SGOV-W2-002-03
Preconditions: [TC-SGOV-W2-002-02 CLOSED]
Micro_steps:
  MS-W2-002-03-01:
    Action: "Run: python tools/governance/ci_skill_attribution_check.py 2>&1"
    Expected: "Exit 0 (no ungoverned src/ mutations detected) OR exit 1 with list of ungoverned commits"
    Check: "Exit code captured"
  MS-W2-002-03-02:
    Action: "Run: python tools/governance/run_ci_governance_check.py 2>&1"
    Expected: "Exit 0 (validators pass) OR exit 1 with fail details"
    Check: "Exit code captured"
  MS-W2-002-03-03:
    Action: "Write .local/governance-audit/ep-006-status.yaml § after_state"
    Expected: "{attribution_check_exit: N, governance_check_exit: N, continue_on_error_removed: true}"
    Check: "File updated"
Note: "If ci_skill_attribution_check.py exits 1 (ungoverned commits detected), that is EXPECTED
  for pre-governance commits before cutoff SHA 4a37978f. The cutoff filters these."
```

---

### Parent Taskcard TC-SGOV-W2-003

```yaml
Parent_Taskcard_ID: TC-SGOV-W2-003
Title: "Create taskcard-execution-contract.schema.json and verify validate_taskcard_execution_contract.py uses it"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-GOV-003
  Root_cause: ".supervisor/schemas/taskcard-execution-contract.schema.json is MISSING.
    validate_taskcard_execution_contract.py enforces skill_ids in code but has no JSON Schema
    to reference. stage2-taskcard-contract.schema.json exists but covers a different scope."
  Selected_solution: "Create the missing JSON Schema file; verify validator loads it or works standalone"
Scope:
  Allowed_files:
    - .supervisor/schemas/taskcard-execution-contract.schema.json (CREATE)
    - tools/governance/validate_taskcard_execution_contract.py (inspect only; edit if schema path needed)
Child_taskcards:
  - TC-SGOV-W2-003-01 (Read validate_taskcard_execution_contract.py to understand its schema expectations)
  - TC-SGOV-W2-003-02 (Create taskcard-execution-contract.schema.json)
  - TC-SGOV-W2-003-03 (Test validator against sample taskcard)
Parent_acceptance_criteria:
  - .supervisor/schemas/taskcard-execution-contract.schema.json exists and is valid JSON
  - Schema requires: task_id, task_type, skill_ids (array, minItems 1), allowed_paths, receipt_required
  - python tools/governance/validate_taskcard_execution_contract.py <sample.yaml> exits 0 for valid TC
  - python tools/governance/validate_taskcard_execution_contract.py <missing-skills.yaml> exits 1
Evidence: .local/governance-audit/ep-008-status.yaml
Rollback: rm .supervisor/schemas/taskcard-execution-contract.schema.json
```

#### TC-SGOV-W2-003-01 — Read validator to understand schema expectations
```yaml
Child_Taskcard_ID: TC-SGOV-W2-003-01
Micro_steps:
  MS-W2-003-01-01:
    Action: "Read tools/governance/validate_taskcard_execution_contract.py fully"
    Expected: "REQUIRED_LIST_FIELDS list; MUTATING_SPRINT_TYPES list; EXEMPT_TASK_TYPES list"
    Check: "skill_ids confirmed in REQUIRED_LIST_FIELDS (line ~69)"
  MS-W2-003-01-02:
    Action: "Check if validate_taskcard_execution_contract.py loads a JSON Schema file"
    Expected: "Either yes (load path) or no (uses hardcoded field lists only)"
    Check: "If it loads schema: note path; if hardcoded: schema creation is supplementary"
  MS-W2-003-01-03:
    Action: "Read stage2-taskcard-contract.schema.json to understand existing schema format"
    Target: .supervisor/schemas/stage2-taskcard-contract.schema.json
    Expected: "JSON Schema structure to model our new schema after"
    Check: "Schema format noted"
```

#### TC-SGOV-W2-003-02 — Create taskcard-execution-contract.schema.json
```yaml
Child_Taskcard_ID: TC-SGOV-W2-003-02
Preconditions: [TC-SGOV-W2-003-01 CLOSED]
Micro_steps:
  MS-W2-003-02-01:
    Action: "Create .supervisor/schemas/taskcard-execution-contract.schema.json with JSON Schema"
    Target: .supervisor/schemas/taskcard-execution-contract.schema.json
    Content_requirements:
      - "$schema": "http://json-schema.org/draft-07/schema#"
      - title: "Taskcard Execution Contract"
      - required: [task_id, task_type, skill_ids, allowed_paths, receipt_required]
      - skill_ids: {type: array, minItems: 1, items: {type: string}}
      - allowed_paths: {type: array, minItems: 1}
      - receipt_required: {type: boolean}
      - direct_mutation_allowed: {type: boolean, default: false}
    Check: "File created; python -c 'import json; json.load(open(f))' exits 0"
  MS-W2-003-02-02:
    Action: "Write .local/governance-audit/ep-008-status.yaml § schema_created: true"
    Check: "File updated"
```

#### TC-SGOV-W2-003-03 — Test validator against sample taskcards
```yaml
Child_Taskcard_ID: TC-SGOV-W2-003-03
Preconditions: [TC-SGOV-W2-003-02 CLOSED]
Micro_steps:
  MS-W2-003-03-01:
    Action: "Create .local/governance-audit/sample-valid-tc.yaml with skill_ids: [add-python-api]"
    Expected: "Valid YAML with task_id, task_type, skill_ids, allowed_paths, receipt_required: true"
    Check: "File created"
  MS-W2-003-03-02:
    Action: "Run: python tools/governance/validate_taskcard_execution_contract.py .local/governance-audit/sample-valid-tc.yaml"
    Expected: "Exit 0 (VALID)"
    Check: "Exit code 0 confirmed"
  MS-W2-003-03-03:
    Action: "Create .local/governance-audit/sample-invalid-tc.yaml with skill_ids: [] (empty)"
    Check: "File created with empty skill_ids"
  MS-W2-003-03-04:
    Action: "Run validator on invalid sample"
    Expected: "Exit 1 (INVALID — empty skill_ids)"
    Check: "Exit code 1 confirmed; error message mentions skill_ids"
  MS-W2-003-03-05:
    Action: "Write .local/governance-audit/ep-008-status.yaml § test_results"
    Expected: "{valid_tc_test: exit_0, invalid_tc_test: exit_1}"
    Check: "File updated"
```

---

### Parent Taskcard TC-SGOV-W2-004

```yaml
Parent_Taskcard_ID: TC-SGOV-W2-004
Title: "Create validate_plan_skill_routes.py (EP-009) to validate plan taskcard skill routes"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-GOV-004
  Root_cause: "EP-009: tools/governance/validate_plan_skill_routes.py DOES NOT EXIST.
    No mechanism validates that plan taskcards reference registered skills."
  Selected_solution: "Create smallest correct validator reading plan YAML; checking skill_ids against registry"
Scope:
  Allowed_files:
    - tools/governance/validate_plan_skill_routes.py (CREATE)
  Forbidden_files: [.supervisor/skill-registry.yaml, plans/]
Child_taskcards:
  - TC-SGOV-W2-004-01 (Design validator contract)
  - TC-SGOV-W2-004-02 (Implement validate_plan_skill_routes.py)
  - TC-SGOV-W2-004-03 (Test on this plan and on a plan with missing skills)
Parent_acceptance_criteria:
  - tools/governance/validate_plan_skill_routes.py exits 0 on this plan (imperative-floating-book)
  - exits 1 with clear message when plan has taskcard with empty skill_ids
  - Registered and tested; path added to EP-009 entry in skill-only-policy.yaml
Evidence: .local/governance-audit/ep-009-status.yaml
Rollback: rm tools/governance/validate_plan_skill_routes.py
```

#### TC-SGOV-W2-004-01 — Design validator contract
```yaml
Child_Taskcard_ID: TC-SGOV-W2-004-01
Micro_steps:
  MS-W2-004-01-01:
    Action: "Read .supervisor/skill-registry.yaml to understand active skill_id list format"
    Expected: "List of skill_ids with status=active; registry load pattern"
    Check: "Understand: registry is YAML with 'skills' list, each has 'skill_id' and 'status'"
  MS-W2-004-01-02:
    Action: "Read tools/governance/validate_taskcard_execution_contract.py for code patterns to reuse"
    Expected: "Pattern for loading YAML, checking fields, returning exit codes 0/1/2"
    Check: "Code patterns identified"
  MS-W2-004-01-03:
    Action: "Define validator contract in .local/governance-audit/ep-009-status.yaml"
    Expected: >
      {
        input: plan_yaml_path,
        checks: [taskcard_has_skill_ids, skill_ids_are_registered],
        exit_0: all_checks_pass,
        exit_1: invalid_routes_found,
        exit_2: config_error
      }
    Check: "Contract written"
```

#### TC-SGOV-W2-004-02 — Implement validate_plan_skill_routes.py
```yaml
Child_Taskcard_ID: TC-SGOV-W2-004-02
Preconditions: [TC-SGOV-W2-004-01 CLOSED]
Micro_steps:
  MS-W2-004-02-01:
    Action: "Create tools/governance/validate_plan_skill_routes.py with header docstring"
    Content: >
      '''
      validate_plan_skill_routes.py — EP-009: Plan Skill Route Validation
      Validates that plan taskcards reference registered skill_ids from skill-registry.yaml.
      Exit: 0=pass, 1=invalid_routes, 2=config_error
      Usage: python tools/governance/validate_plan_skill_routes.py <plan_yaml_or_md_path>
      '''
    Check: "File created; python tools/governance/validate_plan_skill_routes.py --help exits 0 or 2"
  MS-W2-004-02-02:
    Action: "Implement load_active_skill_ids(registry_path) function"
    Expected: "Returns set of skill_id strings where status=active"
    Check: "Function reads .supervisor/skill-registry.yaml correctly"
  MS-W2-004-02-03:
    Action: "Implement extract_taskcard_skill_ids(plan_path) function"
    Expected: "Parses plan markdown/YAML; extracts skill_ids from each TC block"
    Strategy: "Search for 'skill_ids:' lines in plan; extract YAML list values"
    Check: "Returns dict of {tc_id: [skill_ids]} from the plan file"
  MS-W2-004-02-04:
    Action: "Implement main validation loop: for each TC, check skill_ids not empty + all registered"
    Expected: "Findings list: [{tc_id, skill_id, verdict: PASS|UNREGISTERED|EMPTY}]"
    Check: "Function returns findings correctly"
  MS-W2-004-02-05:
    Action: "Implement __main__ block: parse arg, run validation, print findings, exit 0/1/2"
    Check: "Script runnable from CLI with plan path arg"
```

#### TC-SGOV-W2-004-03 — Test validator on real and failing plan
```yaml
Child_Taskcard_ID: TC-SGOV-W2-004-03
Preconditions: [TC-SGOV-W2-004-02 CLOSED]
Micro_steps:
  MS-W2-004-03-01:
    Action: "Run: python tools/governance/validate_plan_skill_routes.py plans/.claude/imperative-floating-book.md"
    Expected: "Exit 0 (all TCs in this plan have skill_ids registered)"
    Check: "Exit 0; no EMPTY or UNREGISTERED findings for critical TCs"
  MS-W2-004-03-02:
    Action: "Create .local/governance-audit/test-invalid-plan.md with one TC having skill_ids: []"
    Check: "File created"
  MS-W2-004-03-03:
    Action: "Run validator on invalid plan"
    Expected: "Exit 1; finding shows EMPTY for the TC with no skill_ids"
    Check: "Exit code 1; EMPTY finding present"
  MS-W2-004-03-04:
    Action: "Write .local/governance-audit/ep-009-status.yaml § test_results and update EP-009 in policy"
    Check: "ep-009-status.yaml updated; skill-only-policy.yaml EP-009 shows IMPLEMENTED"
```

---

### Parent Taskcard TC-SGOV-W2-005

```yaml
Parent_Taskcard_ID: TC-SGOV-W2-005
Title: "Add execution receipt auto-write to autonomous_cycle.py after declaration accepted (EP-004 partial)"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-GOV-005
  Root_cause: "EP-004: Execution receipts are voluntary. autonomous_cycle.py could auto-write
    a minimal receipt after accepting a declaration, extracting skill_ids from work items."
  Selected_solution: "Add post-acceptance hook in autonomous_cycle.py to write minimal transcript
    records to .local/transcripts/<run_id>-<skill_id>.json"
Scope:
  Allowed_files: [tools/supervisor/autonomous_cycle.py]
  Forbidden_files: [.supervisor/skill-registry.yaml, tools/supervisor/governance_validators*.py]
Child_taskcards:
  - TC-SGOV-W2-005-01 (Read autonomous_cycle.py to find evidence acceptance point)
  - TC-SGOV-W2-005-02 (Add receipt auto-write after declaration acceptance)
  - TC-SGOV-W2-005-03 (Verify receipt written in dry-run)
Parent_acceptance_criteria:
  - After autonomous_cycle.py processes a declaration with skill_ids, .local/transcripts/ has receipt file
  - Receipt contains: run_id, skill_id, task_id, changed_paths, timestamp, verdict
Evidence: .local/governance-audit/ep-004-status.yaml
Rollback: git checkout tools/supervisor/autonomous_cycle.py
Note: "EP-004 remains PARTIAL after this change — receipt is post-facto from declaration, not pre-mutation.
  Full closure requires tool-layer interception which is beyond current scope."
```

#### TC-SGOV-W2-005-01 — Find evidence acceptance point in autonomous_cycle.py
```yaml
Child_Taskcard_ID: TC-SGOV-W2-005-01
Micro_steps:
  MS-W2-005-01-01:
    Action: "Read tools/supervisor/autonomous_cycle.py: find where evidence declaration is 'accepted'"
    Expected: "Line/function where grades are finalized and items marked ACCEPTED"
    Check: "Note line number and function name"
  MS-W2-005-01-02:
    Action: "Identify where to insert receipt write (after acceptance, before next sprint generation)"
    Expected: "Insertion point identified with exact line number"
    Check: "Write to .local/governance-audit/ep-004-status.yaml § insertion_point"
```

#### TC-SGOV-W2-005-02 — Add receipt auto-write function
```yaml
Child_Taskcard_ID: TC-SGOV-W2-005-02
Preconditions: [TC-SGOV-W2-005-01 CLOSED]
Micro_steps:
  MS-W2-005-02-01:
    Action: "Add _write_skill_receipts(run_id, accepted_items, transcript_dir) function to autonomous_cycle.py"
    Logic: >
      for each accepted item with declared_skill_ids:
        for each skill_id in declared_skill_ids:
          write .local/transcripts/<run_id>-<skill_id>.json with
            {invocation_id, skill_id, task_id, changed_paths, timestamp, verdict: ACCEPTED}
    Check: "Function defined; no import errors"
  MS-W2-005-02-02:
    Action: "Call _write_skill_receipts() at the identified insertion point"
    Expected: "Called after acceptance, before next-sprint generation"
    Check: "Function call present in autonomous_cycle.py at correct location"
```

#### TC-SGOV-W2-005-03 — Verify receipt written after dry-run declaration
```yaml
Child_Taskcard_ID: TC-SGOV-W2-005-03
Preconditions: [TC-SGOV-W2-005-02 CLOSED]
Micro_steps:
  MS-W2-005-03-01:
    Action: "Create minimal test declaration with one PRODUCT_SOURCE item with declared_skill_ids: [add-python-api]"
    Target: .local/governance-audit/test-declaration-ep004.yaml
    Check: "File created with valid structure"
  MS-W2-005-03-02:
    Action: "Run autonomous_cycle.py with test declaration (or inspect receipt write directly)"
    Expected: ".local/transcripts/<run_id>-add-python-api.json written after acceptance"
    Check: "File exists; contains skill_id: add-python-api"
  MS-W2-005-03-03:
    Action: "Write .local/governance-audit/ep-004-status.yaml § after_state"
    Expected: "{receipt_auto_written: true, location: .local/transcripts/, status: PARTIAL_EP004_CLOSED}"
    Check: "Status file updated"
```

---

## PART 9 — WAVE 3 — SUPERVISOR + CLOSE-TASK HARDENING

---

### Parent Taskcard TC-SGOV-W3-001

```yaml
Parent_Taskcard_ID: TC-SGOV-W3-001
Title: "Verify V-SGF-001 blocking behavior; add V-SGF-002 (receipt check) to governance_validators_ext.py"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-SUP-001
  Root_cause: "V-SGF-001 exists (lines 1305-1404) and blocks unregistered skills.
    However it currently WARNs (not BLOCKs) for missing declared_skill_ids until 2026-09-01.
    V-SGF-002 (receipt check) does not exist at all."
  Selected_solution: "Verify V-SGF-001; add V-SGF-002 as WARN validator for missing receipts"
Scope:
  Allowed_files:
    - tools/supervisor/governance_validators_ext.py (add V-SGF-002 only)
    - tools/supervisor/governance_validator_runner.py (update expected_count)
    - tests/supervisor/test_governance_validators*.py (add test)
Child_taskcards:
  - TC-SGOV-W3-001-01 (Verify V-SGF-001 current behavior)
  - TC-SGOV-W3-001-02 (Add V-SGF-002 receipt check validator)
  - TC-SGOV-W3-001-03 (Update expected_count and run tests)
Parent_acceptance_criteria:
  - V-SGF-001 confirmed: BLOCK on unregistered skill_id, WARN on missing declared_skill_ids
  - V-SGF-002 added: WARN when PRODUCT_SOURCE item has skill_id but no transcript in .local/transcripts/
  - expected_count updated (165→166 or +1)
  - pytest tests/supervisor/ exits 0
Evidence: .local/governance-audit/validators-w3-001.yaml
Rollback: git checkout tools/supervisor/governance_validators_ext.py && git checkout tools/supervisor/governance_validator_runner.py
```

#### TC-SGOV-W3-001-01 — Verify V-SGF-001 current behavior
```yaml
Child_Taskcard_ID: TC-SGOV-W3-001-01
Micro_steps:
  MS-W3-001-01-01:
    Action: "Read governance_validators_ext.py lines 1265-1410 to understand V-SGF-001 fully"
    Expected: "V-SGF-001 logic: checks PRODUCT_SOURCE items for declared_skill_ids;
      missing → WARN (until 2026-09-01 grace); unregistered → BLOCK"
    Check: "Grace period date noted; BLOCK condition for unregistered confirmed"
  MS-W3-001-01-02:
    Action: "Write .local/governance-audit/validators-w3-001.yaml § v_sgf_001_confirmed"
    Expected: "{exists: true, warn_condition: missing_declared_skill_ids, block_condition: unregistered_skill_id,
      grace_period_end: 2026-09-01}"
    Check: "File written"
```

#### TC-SGOV-W3-001-02 — Add V-SGF-002 receipt check validator
```yaml
Child_Taskcard_ID: TC-SGOV-W3-001-02
Preconditions: [TC-SGOV-W3-001-01 CLOSED]
Micro_steps:
  MS-W3-001-02-01:
    Action: "Find V-SGF-001 function end in governance_validators_ext.py; plan insertion point for V-SGF-002"
    Expected: "Line after V-SGF-001 function close (after line ~1404)"
    Check: "Insertion point identified"
  MS-W3-001-02-02:
    Action: "Add validate_skill_receipt_presence() function (V-SGF-002)"
    Logic: >
      def validate_skill_receipt_presence(declaration, repo_root=None):
        '''V-SGF-002: WARN when PRODUCT_SOURCE item has skill_id(s) but no transcript in .local/transcripts/'''
        transcript_dir = repo_root / '.local' / 'transcripts'
        findings = []
        for item in declaration.get('planned_work_items', []):
          if item.get('item_type') not in ('PRODUCT_SOURCE', 'PRODUCT_TEST'):
            continue
          skill_ids = item.get('declared_skill_ids', [])
          if not skill_ids:
            continue  # V-SGF-001 handles missing skill_ids
          receipts_found = any(
            list(transcript_dir.glob(f'*-{sid}.json')) for sid in skill_ids
          )
          if not receipts_found:
            findings.append(f"item {item.get('item_id')}: skill_ids declared but no receipt found")
        if findings:
          return 'WARN', findings, False  # blocks_sprint=False (advisory)
        return 'PASS', [], False
    Check: "Function defined; no syntax errors"
  MS-W3-001-02-03:
    Action: "Register V-SGF-002 in the validators list/registry used by run_all_governance_validators"
    Expected: "V-SGF-002 appears in governance validator runner's validator list"
    Check: "V-SGF-002 is called when run_all_governance_validators runs"
```

#### TC-SGOV-W3-001-03 — Update expected_count and run tests
```yaml
Child_Taskcard_ID: TC-SGOV-W3-001-03
Preconditions: [TC-SGOV-W3-001-02 CLOSED]
Micro_steps:
  MS-W3-001-03-01:
    Action: "Read governance_validator_runner.py to find expected_count assertion (currently 165)"
    Expected: "Line with expected_count = 165 or similar"
    Check: "Line found"
  MS-W3-001-03-02:
    Action: "Update expected_count from 165 to 166 (one new validator added)"
    Target: tools/supervisor/governance_validator_runner.py
    Check: "expected_count = 166 in runner"
  MS-W3-001-03-03:
    Action: "Add test for V-SGF-002 in tests/supervisor/test_governance_validators*.py"
    Expected: "Test: PRODUCT_SOURCE item with skill_id but no transcript → WARN"
    Check: "Test function added"
  MS-W3-001-03-04:
    Action: "Run: .venv/Scripts/pytest tests/supervisor/ -x -q 2>&1 | tail -20"
    Expected: "All tests pass; exit 0"
    Check: "Exit code 0; V-SGF-002 test passes"
```

---

### Parent Taskcard TC-SGOV-W3-002

```yaml
Parent_Taskcard_ID: TC-SGOV-W3-002
Title: "Add skill receipt pre-close check to close-layer-task.md command"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-SUP-002
Scope:
  Allowed_files: [.claude/commands/close-layer-task.md]
Child_taskcards:
  - TC-SGOV-W3-002-01 (Read close-layer-task.md; find closure steps)
  - TC-SGOV-W3-002-02 (Add skill proof validation step before close)
Parent_acceptance_criteria:
  - close-layer-task.md contains step: invoke validate_taskcard_execution_contract.py
  - Step instructions: if validation fails, do NOT mark CLOSED; record BLOCKED_RECEIPT_ABSENT
Evidence: .local/governance-audit/close-task-hardening.yaml
```

#### TC-SGOV-W3-002-01 — Read close-layer-task.md
```yaml
Child_Taskcard_ID: TC-SGOV-W3-002-01
Micro_steps:
  MS-W3-002-01-01:
    Action: "Read .claude/commands/close-layer-task.md fully"
    Expected: "Current closure steps; any existing validation requirements"
    Check: "Note where new skill-proof step should be inserted (before final status change)"
  MS-W3-002-01-02:
    Action: "Write .local/governance-audit/close-task-hardening.yaml § before_state"
    Expected: "{has_skill_proof_check: bool, insertion_point: 'step N'}"
    Check: "File written"
```

#### TC-SGOV-W3-002-02 — Add skill proof validation step
```yaml
Child_Taskcard_ID: TC-SGOV-W3-002-02
Preconditions: [TC-SGOV-W3-002-01 CLOSED]
Micro_steps:
  MS-W3-002-02-01:
    Action: "Add step to close-layer-task.md: Pre-Close Skill Proof Check"
    Target: .claude/commands/close-layer-task.md (before final 'mark CLOSED' step)
    Content: >
      Pre-close validation (mandatory for MUTATING task types):
      1. Run: python tools/governance/validate_taskcard_execution_contract.py <taskcard-yaml>
      2. If exit 1 (missing skill_ids or receipt): DO NOT mark CLOSED
         Record status: BLOCKED_RECEIPT_ABSENT with reason from validator output
      3. If exit 0 (valid): proceed to mark CLOSED
    Check: "Step appears in close-layer-task.md before closure step"
  MS-W3-002-02-02:
    Action: "Update .local/governance-audit/close-task-hardening.yaml § after_state"
    Check: "{has_skill_proof_check: true, step: 'pre-close-validation'}"
```

---

### Parent Taskcard TC-SGOV-W3-003

```yaml
Parent_Taskcard_ID: TC-SGOV-W3-003
Title: "Add skill_id validation to grade_declared_work.py so unskilled PRODUCT_SOURCE items grade REWORK_REQUIRED"
Type: PARENT
Status: READY
Priority: HIGH
Source:
  Plan_requirement_ID: REQ-SUP-003
  Root_cause: "grade_declared_work.py has NO skill_id checking (confirmed by deep analysis).
    Without this, PRODUCT_SOURCE items can receive ACCEPTED grade with no skill attribution."
  Selected_solution: "Add _validate_skill_ids() function + call in grading loop;
    items with missing/unregistered skill_ids → REWORK_REQUIRED with reason UNSKILLED_MUTATION"
  Backward_compat: "Graceful fallback for registry load error (return True, skip_check)"
  Insertion_point: "grade_declared_work.py after _hash_evidence() function (~line 60)"
Scope:
  Allowed_files: [tools/supervisor/grade_declared_work.py]
  Forbidden_files: [tools/supervisor/governance_validators_ext.py]
Child_taskcards:
  - TC-SGOV-W3-003-01 (Read grade_declared_work.py grading loop)
  - TC-SGOV-W3-003-02 (Add _validate_skill_ids() function)
  - TC-SGOV-W3-003-03 (Call validation in grading loop; update grade on failure)
  - TC-SGOV-W3-003-04 (Test: missing skill_id → REWORK_REQUIRED)
Parent_acceptance_criteria:
  - PRODUCT_SOURCE item with declared_skill_ids=[] → grade REWORK_REQUIRED
  - PRODUCT_SOURCE item with declared_skill_ids=[unregistered-skill] → grade REWORK_REQUIRED
  - PRODUCT_SOURCE item with declared_skill_ids=[add-python-api] → grade unaffected by skill check
  - Registry load error → graceful fallback (no change to grade)
  - autonomous_cycle exits 3 when rework items exist
Evidence: .local/governance-audit/grader-hardening.yaml
Rollback: git checkout tools/supervisor/grade_declared_work.py
```

#### TC-SGOV-W3-003-01 — Read grade_declared_work.py grading loop
```yaml
Child_Taskcard_ID: TC-SGOV-W3-003-01
Micro_steps:
  MS-W3-003-01-01:
    Action: "Read tools/supervisor/grade_declared_work.py fully"
    Expected: "Understand grade_item() function signature; where grades are assigned;
      how REWORK_REQUIRED is returned"
    Check: "Note: function name, grade constants, how grade is written to output"
  MS-W3-003-01-02:
    Action: "Find _hash_evidence() or similar utility function (~line 40-60)"
    Expected: "Line number after which _validate_skill_ids() can be inserted"
    Check: "Insertion line noted in .local/governance-audit/grader-hardening.yaml"
  MS-W3-003-01-03:
    Action: "Identify how item_type is accessed (item.get('item_type') or other)"
    Check: "Field access pattern confirmed"
```

#### TC-SGOV-W3-003-02 — Add _validate_skill_ids() function
```yaml
Child_Taskcard_ID: TC-SGOV-W3-003-02
Preconditions: [TC-SGOV-W3-003-01 CLOSED]
Micro_steps:
  MS-W3-003-02-01:
    Action: "Add _validate_skill_ids(item, repo_root) function to grade_declared_work.py"
    Target: tools/supervisor/grade_declared_work.py (after _hash_evidence() line)
    Logic: >
      def _validate_skill_ids(item: dict, repo_root: Path) -> tuple[bool, str]:
          """Return (is_valid, reason). Graceful fallback on registry error."""
          from pathlib import Path
          import yaml
          registry_path = (repo_root or REPO_ROOT) / '.supervisor' / 'skill-registry.yaml'
          try:
              registry = yaml.safe_load(registry_path.read_text(encoding='utf-8'))
              active = {s.get('skill_id') for s in registry.get('skills', [])
                        if s.get('status') == 'active'}
          except Exception:
              return True, 'registry_load_error_skipped'
          declared = set(item.get('declared_skill_ids', []))
          if not declared:
              return False, 'missing_declared_skill_ids'
          unregistered = declared - active
          if unregistered:
              return False, f'unregistered_skill_ids:{list(unregistered)}'
          return True, 'skill_ids_valid'
    Check: "Function present; no syntax errors (python -c 'import ast; ast.parse(open(f).read())')"
```

#### TC-SGOV-W3-003-03 — Call validation in grading loop
```yaml
Child_Taskcard_ID: TC-SGOV-W3-003-03
Preconditions: [TC-SGOV-W3-003-02 CLOSED]
Micro_steps:
  MS-W3-003-03-01:
    Action: "In grade_item() or equivalent loop: add skill_id check for PRODUCT_SOURCE/PRODUCT_TEST items"
    Logic: >
      if item.get('item_type') in ('PRODUCT_SOURCE', 'PRODUCT_TEST'):
          skill_valid, skill_reason = _validate_skill_ids(item, repo_root)
          if not skill_valid:
              return GradeResult(
                  grade='REWORK_REQUIRED',
                  reason=f'UNSKILLED_MUTATION: {skill_reason}',
                  evidence=[]
              )
    Check: "Code added; PRODUCT_SOURCE items with no skill_ids hit REWORK branch"
  MS-W3-003-03-02:
    Action: "Verify non-product items (GOVERNANCE_MACHINERY, ANALYSIS) are NOT affected"
    Check: "item_type check is guarded by PRODUCT_SOURCE/PRODUCT_TEST condition only"
```

#### TC-SGOV-W3-003-04 — Test: missing skill_id → REWORK_REQUIRED
```yaml
Child_Taskcard_ID: TC-SGOV-W3-003-04
Preconditions: [TC-SGOV-W3-003-03 CLOSED]
Micro_steps:
  MS-W3-003-04-01:
    Action: "Create test declaration: PRODUCT_SOURCE item with declared_skill_ids: [] (empty)"
    Target: .local/governance-audit/test-declaration-grader.yaml
    Check: "File created with item_type: PRODUCT_SOURCE, declared_skill_ids: []"
  MS-W3-003-04-02:
    Action: "Run autonomous_cycle or grade script on test declaration"
    Expected: "Item graded REWORK_REQUIRED with reason UNSKILLED_MUTATION: missing_declared_skill_ids"
    Check: "REWORK_REQUIRED present in grades output"
  MS-W3-003-04-03:
    Action: "Verify PRODUCT_SOURCE item with declared_skill_ids: [add-python-api] is NOT penalized"
    Check: "Grade unaffected (ACCEPTED if evidence good)"
  MS-W3-003-04-04:
    Action: "Write .local/governance-audit/grader-hardening.yaml § test_results"
    Expected: "{missing_skill_test: REWORK_REQUIRED, valid_skill_test: unaffected}"
    Check: "File updated"
```

---

## PART 10 — WAVE 4 — MICRO-SKILL CREATION PROTOCOL

---

### Parent Taskcard TC-SGOV-W4-001

```yaml
Parent_Taskcard_ID: TC-SGOV-W4-001
Title: "Create /validate-missing-skill-workflow command ensuring agents prove no existing skill matches before creating new ones"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-SKL-001
  Root_cause: "No mechanism enforces the discovery workflow (REUSE→COMPOSE→REPAIR→CREATE).
    Agents can create skills without documenting why existing skills don't match."
Scope:
  Allowed_files:
    - .claude/commands/validate-missing-skill-workflow.md (CREATE)
    - .supervisor/skill-registry.yaml (add entry)
    - .supervisor/capability-routing-registry.yaml (add route)
Child_taskcards:
  - TC-SGOV-W4-001-01 (Check if equivalent command exists)
  - TC-SGOV-W4-001-02 (Create command file)
  - TC-SGOV-W4-001-03 (Register skill + route)
Parent_acceptance_criteria:
  - .claude/commands/validate-missing-skill-workflow.md exists
  - Command requires: capability_description, search_results, rejection_reasons per candidate
  - Returns: REUSE | COMPOSE | REPAIR | CREATE decision with rationale
  - Skill registered in .supervisor/skill-registry.yaml with status=active
Evidence: .local/governance-audit/w4-001-result.yaml
```

#### TC-SGOV-W4-001-01 — Check if equivalent command exists
```yaml
Child_Taskcard_ID: TC-SGOV-W4-001-01
Micro_steps:
  MS-W4-001-01-01:
    Action: "Read .claude/commands/command-registry.yaml and search for 'missing-skill' or 'skill-workflow'"
    Expected: "Either FOUND (similar command exists) or NOT_FOUND"
    Check: "If found: read it and determine if it covers missing-skill creation protocol"
  MS-W4-001-01-02:
    Action: "Search skill registry for any skill with 'missing_skill' in purpose field"
    Expected: "Either similar skill exists or not"
    Check: "Record finding in .local/governance-audit/w4-001-result.yaml § discovery"
  MS-W4-001-01-03:
    Action: "If equivalent exists: mark TC-SGOV-W4-001-02 SKIPPED_NOT_APPLICABLE with path to existing command"
    Check: "Reuse decision documented (REUSE_EXACT_MATCH or proceed to creation)"
```

#### TC-SGOV-W4-001-02 — Create validate-missing-skill-workflow.md command
```yaml
Child_Taskcard_ID: TC-SGOV-W4-001-02
Preconditions: [TC-SGOV-W4-001-01 CLOSED; equivalent NOT found]
Micro_steps:
  MS-W4-001-02-01:
    Action: "Read .claude/commands/_readme.md to understand command file format"
    Expected: "Format: version, last-updated, phase-available, instructions"
    Check: "Format confirmed"
  MS-W4-001-02-02:
    Action: "Create .claude/commands/validate-missing-skill-workflow.md"
    Required_content:
      - Header: /validate-missing-skill-workflow
      - Inputs: capability_description (required), candidate_skills (list), rejection_reasons (dict)
      - Process: 1.Query registry 2.Score each candidate against capability 3.Document rejections 4.Return decision
      - Decision enum: REUSE_EXACT_MATCH | REUSE_PARAMETERIZED | COMPOSE | REPAIR | EXTEND | CREATE
      - Forbidden: Return CREATE without rejection_reasons for all candidates
      - Output: {decision, selected_skill_or_new_id, rationale, rejection_log}
    Check: "File created; all required sections present"
```

#### TC-SGOV-W4-001-03 — Register skill and route
```yaml
Child_Taskcard_ID: TC-SGOV-W4-001-03
Preconditions: [TC-SGOV-W4-001-02 CLOSED]
Micro_steps:
  MS-W4-001-03-01:
    Action: "Add skill entry to .supervisor/skill-registry.yaml"
    Required_fields: >
      skill_id: validate-missing-skill-workflow
      status: active
      command: /validate-missing-skill-workflow
      command_file: .claude/commands/validate-missing-skill-workflow.md
      purpose: Enforce discovery protocol before creating new skills
      implementation_paths: [.claude/commands/validate-missing-skill-workflow.md]
    Check: "Entry added; no syntax errors (yaml.safe_load exits 0)"
  MS-W4-001-03-02:
    Action: "Add route to .supervisor/capability-routing-registry.yaml"
    Expected: "route_id: missing_skill_validation, preferred_skill_ids: [validate-missing-skill-workflow], status: ROUTE_ACTIVE"
    Check: "Route added"
  MS-W4-001-03-03:
    Action: "Run validate_skill_contracts.py to confirm new skill passes contract check"
    Check: "Exit 0; validate-missing-skill-workflow passes all contract checks"
```

---

### Parent Taskcard TC-SGOV-W4-002

```yaml
Parent_Taskcard_ID: TC-SGOV-W4-002
Title: "Register top-5 NEEDS_REGISTRATION scripts from W1-005 as governed skills"
Type: PARENT
Status: READY
Preconditions: [TC-SGOV-W1-005 CLOSED (top-5 candidates identified)]
Source:
  Plan_requirement_ID: REQ-SKL-002
  Note: "Do NOT rewrite underlying scripts — just register them as skills"
Scope:
  Allowed_files:
    - .supervisor/skill-registry.yaml (add 5 entries)
    - .supervisor/capability-routing-registry.yaml (add 5 routes)
    - .claude/commands/<new-skill-id>.md (create 5 command files)
Child_taskcards:
  - TC-SGOV-W4-002-01 (Read top-5 candidates from W1-005 output)
  - TC-SGOV-W4-002-02 (Create 5 skill registry entries + command files)
  - TC-SGOV-W4-002-03 (Run validate_skill_contracts to confirm all 5 pass)
Parent_acceptance_criteria:
  - 5 new skill registry entries with status=active
  - 5 new command files in .claude/commands/
  - validate_skill_contracts.py exits 0 after registration
Evidence: .local/governance-audit/w4-002-registrations.yaml
```

#### TC-SGOV-W4-002-01 — Read top-5 candidates from W1-005
```yaml
Child_Taskcard_ID: TC-SGOV-W4-002-01
Micro_steps:
  MS-W4-002-01-01:
    Action: "Read .local/governance-audit/infra-classification.yaml § top_candidates"
    Expected: "5 candidate scripts with proposed_skill_id + proposed_command_file"
    Check: "5 candidates available; if fewer, note reason"
```

#### TC-SGOV-W4-002-02 — Create 5 skill registry entries + command files
```yaml
Child_Taskcard_ID: TC-SGOV-W4-002-02
Preconditions: [TC-SGOV-W4-002-01 CLOSED]
Micro_steps:
  MS-W4-002-02-01:
    Action: "For each of 5 candidates: create .claude/commands/<skill-id>.md (minimal command file)"
    Expected: "Command file with: purpose, inputs, implementation_path reference"
    Check: "5 files created in .claude/commands/"
  MS-W4-002-02-02:
    Action: "For each of 5 candidates: add skill entry to .supervisor/skill-registry.yaml"
    Required_fields: "skill_id, status: active, command, command_file, purpose, implementation_paths"
    Check: "5 entries added; YAML valid"
  MS-W4-002-02-03:
    Action: "For each of 5 candidates: add route to .supervisor/capability-routing-registry.yaml"
    Check: "5 routes added"
```

#### TC-SGOV-W4-002-03 — Verify all registrations pass contract check
```yaml
Child_Taskcard_ID: TC-SGOV-W4-002-03
Preconditions: [TC-SGOV-W4-002-02 CLOSED]
Micro_steps:
  MS-W4-002-03-01:
    Action: "Run: python tools/supervisor/validate_skill_contracts.py 2>&1"
    Expected: "Exit 0; all skills (now 125) pass contract check"
    Check: "Exit 0; no new failures"
  MS-W4-002-03-02:
    Action: "Write .local/governance-audit/w4-002-registrations.yaml with all 5 new entries"
    Check: "File written; 5 entries with skill_id, command_file, implementation_path"
```

---

## PART 11 — WAVE 5 — PILOT EXECUTION (15 PILOTS)

**Prerequisite gates**:
- TC-SGOV-W2-001 CLOSED (hook installed) before pilots 1, 6
- TC-SGOV-W2-002 CLOSED (CI blocking) before pilot 9
- TC-SGOV-W3-003 CLOSED (grader hardened) before pilot 12
- TC-SGOV-W4-001 CLOSED (missing-skill workflow) before pilot 5, 13

All pilot evidence written to `.local/governance-audit/pilots/pilot-NN-result.yaml`.

**Standard pilot child structure** (pilots 2-4, 6, 8-15 use this unless noted):
```
Child-01: Setup + precondition check
Child-02: Execute pilot action + capture result
Evidence: .local/governance-audit/pilots/pilot-NN-result.yaml
```

---

### Parent Taskcard TC-SGOV-W5-001

```yaml
Parent_Taskcard_ID: TC-SGOV-W5-001
Title: "Pilot 1: Pre-commit hook blocks Claude Code direct src/ mutation without skill transcript"
Type: PARENT
Status: READY
Preconditions: [TC-SGOV-W2-001 CLOSED]
Source:
  Plan_requirement_ID: REQ-PIL-001
  Pilot_spec: §29 Pilot 1 — Claude Code direct mutation rejection
Scope:
  Allowed_files: [src/python/fods/fods_codec.py (temporarily; reverted after test)]
Child_taskcards:
  - TC-SGOV-W5-001-01 (Make disposable src/ change; stage without transcript)
  - TC-SGOV-W5-001-02 (Attempt commit; verify rejection; revert)
Parent_acceptance_criteria:
  - Commit attempt exits non-zero
  - Pre-commit hook is named as the guard in output
  - src/python/fods/fods_codec.py unchanged after test (state_changed: false)
  - pilot-01-result.yaml verdict: BLOCKED
Evidence: .local/governance-audit/pilots/pilot-01-result.yaml
```

#### TC-SGOV-W5-001-01 — Disposable change + stage (no transcript)
```yaml
Child_Taskcard_ID: TC-SGOV-W5-001-01
Micro_steps:
  MS-W5-001-01-01:
    Action: "Read last line of src/python/fods/fods_codec.py (to know what to revert)"
    Check: "Baseline state noted"
  MS-W5-001-01-02:
    Action: "Append '# PILOT-01-TEST' comment to src/python/fods/fods_codec.py"
    Check: "File modified; git diff shows exactly one line added"
  MS-W5-001-01-03:
    Action: "Ensure .local/transcripts/ does NOT have a recent fods_codec receipt"
    Check: "No matching transcript file (this is the negative control condition)"
  MS-W5-001-01-04:
    Action: "Stage: git add src/python/fods/fods_codec.py"
    Check: "git status shows file staged"
```

#### TC-SGOV-W5-001-02 — Commit attempt; verify BLOCKED; revert
```yaml
Child_Taskcard_ID: TC-SGOV-W5-001-02
Preconditions: [TC-SGOV-W5-001-01 CLOSED]
Micro_steps:
  MS-W5-001-02-01:
    Action: "Attempt: git commit -m 'PILOT-01-TEST-UNGOVERNED' (expect BLOCKED)"
    Expected: "Exit code != 0; pre-commit hook fires; commit NOT created"
    Check: "git log --oneline -1 does NOT show PILOT-01-TEST-UNGOVERNED"
  MS-W5-001-02-02:
    Action: "Capture hook output to determine which guard triggered"
    Check: "Output mentions pre-commit-skill-guard or EP-007"
  MS-W5-001-02-03:
    Action: "Revert: git checkout -- src/python/fods/fods_codec.py"
    Check: "git diff HEAD -- src/python/fods/fods_codec.py is empty"
  MS-W5-001-02-04:
    Action: "Write .local/governance-audit/pilots/pilot-01-result.yaml"
    Expected: >
      {pilot_id: 1, verdict: BLOCKED, guard_triggered: pre-commit-skill-guard,
       state_changed: false, hook_exit_code: 1, evidence: pilot-01-result.yaml}
    Check: "File written with BLOCKED verdict"
Stop_condition: "If commit SUCCEEDS (hook not firing): mark TC-SGOV-W5-001 BLOCKED; revisit W2-001 install"
```

---

### Parent Taskcard TC-SGOV-W5-002

```yaml
Parent_Taskcard_ID: TC-SGOV-W5-002
Title: "Pilot 2: pre_mutation_guard.py blocks Codex-pattern mutation with unregistered skill"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-PIL-002
  Pilot_spec: §29 Pilot 2 — Codex direct mutation rejection
Child_taskcards:
  - TC-SGOV-W5-002-01 (Read codex-adapter.md; confirm it instructs guard call)
  - TC-SGOV-W5-002-02 (Simulate Codex: call guard with NONE skill-id; verify BLOCKED)
Parent_acceptance_criteria:
  - codex-adapter.md instructs Codex to call pre_mutation_guard.py before mutation
  - pre_mutation_guard.py exits 1 for skill-id NONE (unregistered)
  - pilot-02-result.yaml verdict: BLOCKED
Evidence: .local/governance-audit/pilots/pilot-02-result.yaml
```

#### TC-SGOV-W5-002-01 — Read codex-adapter.md
```yaml
Child_Taskcard_ID: TC-SGOV-W5-002-01
Micro_steps:
  MS-W5-002-01-01:
    Action: "Read docs/governance/codex-adapter.md fully"
    Expected: "Codex adapter instructs: run pre_mutation_guard.py before any src/ edit"
    Check: "pre_mutation_guard.py reference found; note whether it's mandatory or advisory"
  MS-W5-002-01-02:
    Action: "Record in .local/governance-audit/pilots/pilot-02-result.yaml § codex_adapter_check"
    Expected: "{references_guard: bool, mandatory: bool}"
    Check: "Finding recorded"
```

#### TC-SGOV-W5-002-02 — Simulate Codex mutation with unregistered skill
```yaml
Child_Taskcard_ID: TC-SGOV-W5-002-02
Micro_steps:
  MS-W5-002-02-01:
    Action: "Run guard with unregistered skill: python tools/governance/pre_mutation_guard.py
      --agent-type CODEX --task-id PILOT-02 --skill-id NONE --target-paths src/python/fods/ --mission-id FF-SGOV-001 --sprint-id pilot-02"
    Expected: "Exit 1 (BLOCKED); reason: skill_not_registered"
    Check: "Exit code 1; stdout JSON has verdict: BLOCKED"
  MS-W5-002-02-02:
    Action: "Write .local/governance-audit/pilots/pilot-02-result.yaml"
    Expected: "{pilot_id: 2, verdict: BLOCKED, guard: pre_mutation_guard, state_changed: false}"
    Check: "File written"
```

---

### Parent Taskcard TC-SGOV-W5-003

```yaml
Parent_Taskcard_ID: TC-SGOV-W5-003
Title: "Pilot 3: Both agents discover /add-python-api for Python API work; no duplicate created"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-PIL-003
Child_taskcards:
  - TC-SGOV-W5-003-01 (Query routing registry for Python API work; find add-python-api)
  - TC-SGOV-W5-003-02 (Confirm single skill found; verify command file exists)
Parent_acceptance_criteria:
  - Route add_python_api → preferred_skill_ids: [add-python-api] ROUTE_ACTIVE
  - .claude/commands/add-python-api.md exists
  - No duplicate skill created
  - pilot-03-result.yaml verdict: REUSE_EXACT_MATCH
Evidence: .local/governance-audit/pilots/pilot-03-result.yaml
```

#### TC-SGOV-W5-003-01 — Query routing registry for Python API capability
```yaml
Child_Taskcard_ID: TC-SGOV-W5-003-01
Micro_steps:
  MS-W5-003-01-01:
    Action: "Read .supervisor/capability-routing-registry.yaml and find route for add_python_api task type"
    Expected: "route_id with preferred_skill_ids: [add-python-api]"
    Check: "Route found with ROUTE_ACTIVE status"
  MS-W5-003-01-02:
    Action: "Read .supervisor/skill-registry.yaml and confirm add-python-api has status=active"
    Check: "status=active confirmed"
  MS-W5-003-01-03:
    Action: "Verify .claude/commands/add-python-api.md exists"
    Check: "File exists"
```

#### TC-SGOV-W5-003-02 — Record no-duplicate verdict
```yaml
Child_Taskcard_ID: TC-SGOV-W5-003-02
Micro_steps:
  MS-W5-003-02-01:
    Action: "Search skill registry for any other skill with overlapping Python API capability"
    Expected: "No duplicate skill found"
    Check: "Only add-python-api matches the capability"
  MS-W5-003-02-02:
    Action: "Write .local/governance-audit/pilots/pilot-03-result.yaml"
    Expected: "{pilot_id: 3, verdict: REUSE_EXACT_MATCH, skill_id: add-python-api, duplicate_created: false}"
    Check: "File written"
```

---

### Parent Taskcard TC-SGOV-W5-004

```yaml
Parent_Taskcard_ID: TC-SGOV-W5-004
Title: "Pilot 4: Compose /add-python-api + /add-roundtrip-test for multi-capability task"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-PIL-004
Child_taskcards:
  - TC-SGOV-W5-004-01 (Decompose task; map capabilities to 2 skills)
  - TC-SGOV-W5-004-02 (Verify composition plan; record no-duplication)
Parent_acceptance_criteria:
  - Two distinct skills identified (add-python-api, add-roundtrip-test)
  - No monolith skill created
  - pilot-04-result.yaml shows composition with no logic duplication
Evidence: .local/governance-audit/pilots/pilot-04-result.yaml
```

#### TC-SGOV-W5-004-01 — Decompose and map capabilities
```yaml
Child_Taskcard_ID: TC-SGOV-W5-004-01
Micro_steps:
  MS-W5-004-01-01:
    Action: "Define task: Add Python get_sheet_names() API to ODS format + roundtrip test"
    Check: "Task defined with clear capability list: [add_python_api, create_roundtrip_test]"
  MS-W5-004-01-02:
    Action: "Query routing for add_python_api → add-python-api; create_roundtrip → add-roundtrip-test"
    Check: "Both routes found ROUTE_ACTIVE"
  MS-W5-004-01-03:
    Action: "Verify add-roundtrip-test is in skill registry with status=active"
    Check: "Entry confirmed"
```

#### TC-SGOV-W5-004-02 — Record composition verdict
```yaml
Child_Taskcard_ID: TC-SGOV-W5-004-02
Micro_steps:
  MS-W5-004-02-01:
    Action: "Confirm each skill implementation is atomic (does not duplicate the other skill's logic)"
    Check: "add-python-api handles API; add-roundtrip-test handles test; no overlap"
  MS-W5-004-02-02:
    Action: "Write .local/governance-audit/pilots/pilot-04-result.yaml"
    Expected: "{pilot_id: 4, skills: [add-python-api, add-roundtrip-test], composition_valid: true, logic_duplicated: false}"
    Check: "File written"
```

---

### Parent Taskcard TC-SGOV-W5-005

```yaml
Parent_Taskcard_ID: TC-SGOV-W5-005
Title: "Pilot 5: Identify real MISSING_SKILL_CAPABILITY gap; create smallest micro-skill; prove idempotency"
Type: PARENT
Status: READY
Preconditions: [TC-SGOV-W4-001 CLOSED; TC-SGOV-W1-004 CLOSED (routing gaps identified)]
Source:
  Plan_requirement_ID: REQ-PIL-005
Child_taskcards:
  - TC-SGOV-W5-005-01 (Find real MISSING_SKILL_CAPABILITY route)
  - TC-SGOV-W5-005-02 (Run /validate-missing-skill-workflow; document rejections)
  - TC-SGOV-W5-005-03 (Create and register micro-skill; prove idempotency)
Parent_acceptance_criteria:
  - New skill registered, tests pass
  - Idempotency proven (second run makes no changes)
  - pilot-05-result.yaml shows rejection_reasons for all candidates
Evidence: .local/governance-audit/pilots/pilot-05-result.yaml
```

#### TC-SGOV-W5-005-01 — Find real MISSING_SKILL_CAPABILITY route
```yaml
Child_Taskcard_ID: TC-SGOV-W5-005-01
Micro_steps:
  MS-W5-005-01-01:
    Action: "Read .supervisor/capability-routing-registry.yaml; find first route with current_status: MISSING_SKILL_CAPABILITY"
    Expected: "At least one MISSING_SKILL_CAPABILITY route"
    Check: "Route found; note route_id and description"
  MS-W5-005-01-02:
    Action: "Also check missing_skill_workflow section of skill-registry.yaml for backlog items"
    Check: "Backlog items noted"
  MS-W5-005-01-03:
    Action: "Select one MISSING capability for the pilot (prefer smallest, most isolated)"
    Check: "Selection documented in .local/governance-audit/pilots/pilot-05-result.yaml § selected_gap"
```

#### TC-SGOV-W5-005-02 — Run /validate-missing-skill-workflow
```yaml
Child_Taskcard_ID: TC-SGOV-W5-005-02
Micro_steps:
  MS-W5-005-02-01:
    Action: "Invoke /validate-missing-skill-workflow with the selected capability"
    Expected: "Process: query registry → score candidates → reject all → approve CREATE"
    Check: "All candidate skills have documented rejection_reasons"
  MS-W5-005-02-02:
    Action: "Record decision: CREATE_MISSING_MICRO_SKILL + skill contract draft"
    Check: "Contract has: inputs, outputs, allowed_paths, idempotency_contract"
```

#### TC-SGOV-W5-005-03 — Create micro-skill; prove idempotency
```yaml
Child_Taskcard_ID: TC-SGOV-W5-005-03
Micro_steps:
  MS-W5-005-03-01:
    Action: "Create .claude/commands/<new-skill-id>.md (smallest correct implementation)"
    Check: "File created; purpose, inputs, outputs, allowed_paths defined"
  MS-W5-005-03-02:
    Action: "Register in .supervisor/skill-registry.yaml + add route in capability-routing-registry"
    Check: "Registered; validate_skill_contracts.py exits 0"
  MS-W5-005-03-03:
    Action: "Write focused test for new skill's primary operation"
    Check: "Test file created; pytest exits 0"
  MS-W5-005-03-04:
    Action: "Run new skill for the original task; record output"
    Check: "Task outcome achieved via skill (not direct edit)"
  MS-W5-005-03-05:
    Action: "Run new skill again (idempotent rerun); verify no material changes"
    Expected: "Second run produces same output; no duplicate artifacts"
    Check: "Idempotency confirmed; write pilot-05-result.yaml"
```

---

### Parent Taskcard TC-SGOV-W5-006

```yaml
Parent_Taskcard_ID: TC-SGOV-W5-006
Title: "Pilot 6: Repair a broken skill; prove direct bypass is blocked; rerun repaired skill"
Type: PARENT
Status: READY
Preconditions: [TC-SGOV-W1-003 CLOSED; TC-SGOV-W2-001 CLOSED]
Source:
  Plan_requirement_ID: REQ-PIL-006
Child_taskcards:
  - TC-SGOV-W5-006-01 (Identify broken skill from W1-003 inventory)
  - TC-SGOV-W5-006-02 (Attempt direct bypass; verify BLOCKED; repair skill; rerun)
Evidence: .local/governance-audit/pilots/pilot-06-result.yaml
```

#### TC-SGOV-W5-006-01 — Identify broken skill
```yaml
Child_Taskcard_ID: TC-SGOV-W5-006-01
Micro_steps:
  MS-W5-006-01-01:
    Action: "Read .local/governance-audit/skill-registry-audit.yaml for BROKEN skills (from W1-003)"
    Expected: "At least one BROKEN or EMPTY skill; if none: use a temporarily-disabled skill"
    Check: "Target skill identified; failure mode noted"
```

#### TC-SGOV-W5-006-02 — Bypass attempt; repair; rerun
```yaml
Child_Taskcard_ID: TC-SGOV-W5-006-02
Micro_steps:
  MS-W5-006-02-01:
    Action: "Attempt direct file edit for broken skill's target path without skill invocation"
    Check: "Stage change; pre-commit hook BLOCKS (exit 1) — same as Pilot 1"
  MS-W5-006-02-02:
    Action: "Revert staged change: git checkout -- <target-file>"
    Check: "File restored"
  MS-W5-006-02-03:
    Action: "Repair broken skill: fix implementation_path or command file reference"
    Target: .supervisor/skill-registry.yaml (specific skill entry only)
    Check: "validate_skill_contracts.py exit 0 for repaired skill"
  MS-W5-006-02-04:
    Action: "Invoke repaired skill for a smoke test"
    Check: "Skill invocation exits 0 or produces expected output"
  MS-W5-006-02-05:
    Action: "Write pilot-06-result.yaml"
    Expected: "{bypass_verdict: BLOCKED, repair_verdict: PASS, skill_id: <repaired_skill>}"
    Check: "File written"
```

---

### Parent Taskcard TC-SGOV-W5-007

```yaml
Parent_Taskcard_ID: TC-SGOV-W5-007
Title: "Pilot 7: Execute real product-deepening sprint using only registered skills with full receipt chain"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-PIL-007
  Note: "This is a REAL product sprint — it creates actual product code. Keep it small."
  Suggested_target: "Add one analytics function to an existing Python format (e.g., get_row_count to DIF)"
Scope:
  Allowed_skills: [add-spec-analytics-function, add-python-api, add-roundtrip-test]
Child_taskcards:
  - TC-SGOV-W5-007-01 (Select target format + capability; resolve skill)
  - TC-SGOV-W5-007-02 (Execute via skill; write transcript; submit declaration)
  - TC-SGOV-W5-007-03 (Run autonomous_cycle; verify exit 0; check ledger)
Parent_acceptance_criteria:
  - Product change executed via skill (not direct edit)
  - Skill transcript in .local/transcripts/
  - autonomous_cycle exits 0 (not 3)
  - Product-code ledger has new entry with skill reference
  - Tests pass
Evidence: .local/governance-audit/pilots/pilot-07-result.yaml
```

#### TC-SGOV-W5-007-01 — Select target; resolve skill
```yaml
Child_Taskcard_ID: TC-SGOV-W5-007-01
Micro_steps:
  MS-W5-007-01-01:
    Action: "Select format + capability: e.g., DIF format, add get_row_count() analytics function"
    Expected: "Target: src/python/dif/dif_analytics.py (or equivalent); capability: add_spec_analytics"
    Check: "Selection made; skill add-spec-analytics-function confirmed for this capability"
  MS-W5-007-01-02:
    Action: "Run pre_mutation_guard.py for the target path + skill"
    Expected: "Exit 0 (AUTHORIZED); authorization YAML written to .local/mutation-auth/"
    Check: "Authorization file exists"
```

#### TC-SGOV-W5-007-02 — Execute via skill; write transcript
```yaml
Child_Taskcard_ID: TC-SGOV-W5-007-02
Micro_steps:
  MS-W5-007-02-01:
    Action: "Invoke /add-spec-analytics-function for selected format+capability"
    Expected: "Function added to Python source; tests added"
    Check: "git diff shows changes in src/python/dif/ + tests/python/dif/"
  MS-W5-007-02-02:
    Action: "Write skill transcript to .local/transcripts/pilot-07-add-spec-analytics.json"
    Content: "{invocation_id, skill_id: add-spec-analytics-function, task_id: TC-SGOV-W5-007,
      changed_paths: [...], tests_run: [...], result: PASS, timestamp: now}"
    Check: "File exists; JSON valid"
  MS-W5-007-02-03:
    Action: "Run: .venv/Scripts/pytest tests/python/dif/ -x -q"
    Expected: "Tests pass (exit 0)"
    Check: "Test output shows PASS"
```

#### TC-SGOV-W5-007-03 — Submit declaration; verify autonomous_cycle
```yaml
Child_Taskcard_ID: TC-SGOV-W5-007-03
Micro_steps:
  MS-W5-007-03-01:
    Action: "Write evidence declaration with item: type PRODUCT_SOURCE, declared_skill_ids: [add-spec-analytics-function]"
    Target: .local/evidences/pilot-07/evidence-declaration.yaml
    Check: "Declaration file written"
  MS-W5-007-03-02:
    Action: "Run: python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/pilot-07/evidence-declaration.yaml"
    Expected: "Exit 0 (no rework items)"
    Check: "Exit code 0"
  MS-W5-007-03-03:
    Action: "Write pilot-07-result.yaml"
    Expected: "{skill_used: add-spec-analytics-function, receipt_present: true, tests_pass: true, autonomous_cycle_exit: 0}"
    Check: "File written"
```

---

### Parent Taskcards TC-SGOV-W5-008 through TC-SGOV-W5-015 (Compact Format)

Each pilot below follows the standard 2-child structure. Full micro-step detail available on request.

---

**TC-SGOV-W5-008** — Pilot 8: Machinery-healing sprint with governed skill
```yaml
Parent_Taskcard_ID: TC-SGOV-W5-008
Title: "Pilot 8: Repair machinery defect via registered skill; prove receipt chain"
Preconditions: [TC-SGOV-W3-003 CLOSED]
Child_taskcards:
  - TC-SGOV-W5-008-01: Select machinery defect from EP gap list; run pre_mutation_guard
  - TC-SGOV-W5-008-02: Use /found-issue-ownership; write transcript; submit declaration; verify exit 0
Parent_acceptance_criteria:
  - Machinery defect closed via skill (not direct edit)
  - Receipt in .local/transcripts/; autonomous_cycle exits 0 for machinery track
Evidence: .local/governance-audit/pilots/pilot-08-result.yaml
```

**TC-SGOV-W5-009** — Pilot 9: New unregistered script detection by CI
```yaml
Parent_Taskcard_ID: TC-SGOV-W5-009
Title: "Pilot 9: Create disposable script; CI rejects unregistered executable"
Preconditions: [TC-SGOV-W2-002 CLOSED]
Child_taskcards:
  - TC-SGOV-W5-009-01: Create tools/supervisor/pilot_09_test_stub.py (empty stub)
  - TC-SGOV-W5-009-02: Run ci_skill_attribution_check.py; verify exit 1; remove stub; re-verify exit 0
Parent_acceptance_criteria:
  - ci_skill_attribution_check.py exits 1 with unregistered script present
  - After removal: exits 0
  - State permanently unchanged (stub removed)
Evidence: .local/governance-audit/pilots/pilot-09-result.yaml
```

**TC-SGOV-W5-010** — Pilot 10: Taskcard state mutation via registered command
```yaml
Parent_Taskcard_ID: TC-SGOV-W5-010
Title: "Pilot 10: Direct status edit blocked (or graded REWORK); update via /close-layer-task"
Child_taskcards:
  - TC-SGOV-W5-010-01: Attempt direct status field edit on a taskcard YAML; stage; pre-commit fires
  - TC-SGOV-W5-010-02: Revert; use /close-layer-task with skill_id; verify accepted
Evidence: .local/governance-audit/pilots/pilot-10-result.yaml
```

**TC-SGOV-W5-011** — Pilot 11: Path ownership violation caught by mutation guard
```yaml
Parent_Taskcard_ID: TC-SGOV-W5-011
Title: "Pilot 11: Guard blocks mutation to path outside skill ownership"
Child_taskcards:
  - TC-SGOV-W5-011-01: Call pre_mutation_guard.py with add-python-api + target src/python/csv/
  - TC-SGOV-W5-011-02: Verify exit 1 with rejection_condition PATH_OUTSIDE_OWNERSHIP; write result
Evidence: .local/governance-audit/pilots/pilot-11-result.yaml
```

**TC-SGOV-W5-012** — Pilot 12: Receipt omission → REWORK_REQUIRED grade
```yaml
Parent_Taskcard_ID: TC-SGOV-W5-012
Title: "Pilot 12: Declaration with skill_id but no receipt → V-SGF-002 WARN + REWORK grade"
Preconditions: [TC-SGOV-W3-001 CLOSED; TC-SGOV-W3-003 CLOSED]
Child_taskcards:
  - TC-SGOV-W5-012-01: Write declaration with PRODUCT_SOURCE + skill_id + NO transcript file; confirm no transcript in .local/transcripts/
  - TC-SGOV-W5-012-02: Submit to autonomous_cycle; verify V-SGF-002 WARN + grade REWORK_REQUIRED; exit 3
Evidence: .local/governance-audit/pilots/pilot-12-result.yaml
```

**TC-SGOV-W5-013** — Pilot 13: Skill-created-not-used detection
```yaml
Parent_Taskcard_ID: TC-SGOV-W5-013
Title: "Pilot 13: Create skill; attempt direct edit without using it; prove caught"
Preconditions: [TC-SGOV-W5-005 CLOSED (pilot-05 skill); TC-SGOV-W2-001 CLOSED]
Child_taskcards:
  - TC-SGOV-W5-013-01: Stage direct edit of pilot-05 target file; attempt commit → pre-commit BLOCKS
  - TC-SGOV-W5-013-02: Revert; invoke pilot-05 skill correctly; write transcript; verify accepted
Evidence: .local/governance-audit/pilots/pilot-13-result.yaml
```

**TC-SGOV-W5-014** — Pilot 14: Concurrent Claude Code + Codex via worker_claims
```yaml
Parent_Taskcard_ID: TC-SGOV-W5-014
Title: "Pilot 14: control_index worker_claims prevent duplicate task ownership"
Child_taskcards:
  - TC-SGOV-W5-014-01: Query control-index.db for worker_claims table; verify it exists
  - TC-SGOV-W5-014-02: Simulate conflicting claims; verify uniqueness constraint; write result
Evidence: .local/governance-audit/pilots/pilot-14-result.yaml
```

**TC-SGOV-W5-015** — Pilot 15: Idempotent rerun of key pilots
```yaml
Parent_Taskcard_ID: TC-SGOV-W5-015
Title: "Pilot 15: Re-execute pilots 1,2,3,7,11 and verify identical verdicts"
Preconditions: [Pilots 1,2,3,7,11 CLOSED with evidence]
Child_taskcards:
  - TC-SGOV-W5-015-01: Re-run each pilot's verification step (not setup); capture verdict
  - TC-SGOV-W5-015-02: Compare each rerun verdict to original; verify identical; write result
Parent_acceptance_criteria:
  - All 5 rerun verdicts match original verdicts
  - Pilot 7 (product): rerun adds no duplicate code or tests
Evidence: .local/governance-audit/pilots/pilot-15-result.yaml
```

---

## PART 12 — WAVE 6 — HISTORICAL BACKFILL

---

### Parent Taskcard TC-SGOV-W6-001

```yaml
Parent_Taskcard_ID: TC-SGOV-W6-001
Title: "Audit git log for src/ changes since tracking_base_ref with no product-code ledger entries"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-BKF-001
Scope:
  Allowed_files: [reports/r90/product-code-change-ledger.json]
  Allowed_operation: read git log + append backfill entries to ledger
Child_taskcards:
  - TC-SGOV-W6-001-01 (Get tracking_base_ref + list src/ changes since)
  - TC-SGOV-W6-001-02 (Cross-check changes against ledger; add BACKFILLED entries)
Parent_acceptance_criteria:
  - Every src/ file changed after tracking_base_ref has a ledger entry
  - Backfill entries tagged BACKFILLED_PRE_GOVERNANCE
Evidence: .local/governance-audit/ledger-backfill.yaml
```

#### TC-SGOV-W6-001-01 — Get tracking_base_ref; list src/ changes
```yaml
Child_Taskcard_ID: TC-SGOV-W6-001-01
Micro_steps:
  MS-W6-001-01-01:
    Action: "Read reports/r90/product-code-change-ledger.json; extract tracking_base_ref or pre_policy_cutoff_sha"
    Expected: "SHA string (e.g., 4a37978f from ci_skill_attribution_check.py)"
    Check: "SHA extracted"
  MS-W6-001-01-02:
    Action: "Run: git log --name-only <tracking_base_ref>..HEAD -- src/ | grep '^src/' | sort -u"
    Expected: "List of src/ files changed after baseline"
    Check: "List written to .local/governance-audit/ledger-backfill.yaml § changed_since_baseline"
```

#### TC-SGOV-W6-001-02 — Cross-check and add backfill entries
```yaml
Child_Taskcard_ID: TC-SGOV-W6-001-02
Micro_steps:
  MS-W6-001-02-01:
    Action: "For each changed src/ file: check if ledger has entry with that path"
    Expected: "List of files WITHOUT ledger entry = ungoverned"
    Check: "Ungoverned list written"
  MS-W6-001-02-02:
    Action: "For each ungoverned file: add BACKFILLED entry to ledger with inferred skill"
    Content: "{path, commit_sha, classification: BACKFILLED_PRE_GOVERNANCE, inferred_skill: best_match}"
    Check: "Entries added to ledger JSON"
  MS-W6-001-02-03:
    Action: "Run: python tools/supervisor/validate_product_code_ledger.py (if exists)"
    Expected: "Exit 0"
    Check: "Ledger valid after backfill"
```

---

### Parent Taskcard TC-SGOV-W6-002

```yaml
Parent_Taskcard_ID: TC-SGOV-W6-002
Title: "Bind ungoverned work items in last 10 sprints to existing registered skills"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-BKF-002
Scope:
  Allowed_files: [.local/governance-audit/backfill-<sprint-id>.yaml (CREATE per sprint)]
  Forbidden: "Do NOT modify historical evidence declarations — create binding records only"
Child_taskcards:
  - TC-SGOV-W6-002-01 (List last 10 sprint evidence declarations)
  - TC-SGOV-W6-002-02 (For each: find PRODUCT_SOURCE items without skill_id; bind to skill)
Evidence: .local/governance-audit/backfill-summary.yaml
```

#### TC-SGOV-W6-002-01 — List last 10 sprint declarations
```yaml
Child_Taskcard_ID: TC-SGOV-W6-002-01
Micro_steps:
  MS-W6-002-01-01:
    Action: "List .local/evidences/ directories sorted by mtime; take last 10"
    Expected: "10 sprint run IDs"
    Check: "List captured"
  MS-W6-002-01-02:
    Action: "For each: check if evidence-declaration.yaml has PRODUCT_SOURCE items with declared_skill_ids"
    Check: "Ungoverned items identified per sprint"
```

#### TC-SGOV-W6-002-02 — Bind ungoverned items to registered skills
```yaml
Child_Taskcard_ID: TC-SGOV-W6-002-02
Micro_steps:
  MS-W6-002-02-01:
    Action: "For each ungoverned item: find closest matching registered skill by operation type + path"
    Check: "Binding decision documented"
  MS-W6-002-02-02:
    Action: "Write .local/governance-audit/backfill-<sprint-id>.yaml per sprint"
    Content: "[{item_id, inferred_skill_id, disposition: BIND_AND_REVALIDATE_EXISTING_SKILL, rationale}]"
    Check: "10 backfill files written"
  MS-W6-002-02-03:
    Action: "Write .local/governance-audit/backfill-summary.yaml with counts"
    Expected: "{sprints_reviewed: 10, ungoverned_items: N, bindings_created: M}"
    Check: "File written"
```

---

## PART 13 — WAVE 7 — FINAL AUDIT + CLOSEOUT

---

### Parent Taskcard TC-SGOV-W7-001

```yaml
Parent_Taskcard_ID: TC-SGOV-W7-001
Title: "Compute skill governance adoption metrics from evidence declarations, ledger, and pilot results"
Type: PARENT
Status: READY
Preconditions: [All Wave 5 pilots CLOSED; TC-SGOV-W6-001 CLOSED; TC-SGOV-W6-002 CLOSED]
Source:
  Plan_requirement_ID: REQ-AUD-001
Child_taskcards:
  - TC-SGOV-W7-001-01 (Gather raw counts from all evidence sources)
  - TC-SGOV-W7-001-02 (Compute metrics; write adoption-metrics.yaml)
Parent_acceptance_criteria:
  - .local/governance-audit/adoption-metrics.yaml written with all required fields
  - accepted_direct_mutations value explicitly stated (target: 0)
Evidence: .local/governance-audit/adoption-metrics.yaml
```

#### TC-SGOV-W7-001-01 — Gather raw counts
```yaml
Child_Taskcard_ID: TC-SGOV-W7-001-01
Micro_steps:
  MS-W7-001-01-01:
    Action: "Count src/ files in product-code-ledger.json since tracking_base_ref = governed_mutations_total"
    Check: "Count recorded"
  MS-W7-001-01-02:
    Action: "Count ledger entries WITH skill reference (non-null skill_id) = skill_backed_mutations"
    Check: "Count recorded"
  MS-W7-001-01-03:
    Action: "Count files in .local/transcripts/ = receipt_backed_mutations"
    Check: "Count recorded"
  MS-W7-001-01-04:
    Action: "Count pilot result files with verdict: BLOCKED = direct_mutation_attempts (rejected)"
    Check: "Count recorded"
  MS-W7-001-01-05:
    Action: "Count micro-skills created in W4 = micro_skills_created"
    Check: "Count recorded (5 from W4-002 + any from W5-005)"
```

#### TC-SGOV-W7-001-02 — Compute and write metrics
```yaml
Child_Taskcard_ID: TC-SGOV-W7-001-02
Micro_steps:
  MS-W7-001-02-01:
    Action: "Compute: claude_code_compliance_rate = skill_backed_mutations / governed_mutations_total"
    Check: "Rate calculated (0.0 to 1.0)"
  MS-W7-001-02-02:
    Action: "Write .local/governance-audit/adoption-metrics.yaml"
    Required_fields: >
      governed_mutations_total, skill_backed_mutations, receipt_backed_mutations,
      direct_mutation_attempts, rejected_direct_mutations, accepted_direct_mutations,
      skills_reused, skills_composed, skills_repaired, micro_skills_created,
      duplicate_skills_prevented, claude_code_compliance_rate, product_sprint_compliance_rate,
      machinery_sprint_compliance_rate
    Check: "All fields present; accepted_direct_mutations stated (target: 0)"
```

---

### Parent Taskcard TC-SGOV-W7-002

```yaml
Parent_Taskcard_ID: TC-SGOV-W7-002
Title: "Append §32 Tool-Neutral Skill/Command-Only Execution Governance section to this plan"
Type: PARENT
Status: READY
Source:
  Plan_requirement_ID: REQ-AUD-002
Scope:
  Allowed_files: [plans/.claude/imperative-floating-book.md]
Child_taskcards:
  - TC-SGOV-W7-002-01 (Draft §32 content from wave outputs)
  - TC-SGOV-W7-002-02 (Append to plan file; verify plan remains authoritative)
Parent_acceptance_criteria:
  - Plan contains §32 section with 24 sub-sections per spec
  - All referenced paths are real (verified in earlier waves)
Evidence: Verified by reading plan file after append
```

#### TC-SGOV-W7-002-01 — Draft §32 content
```yaml
Child_Taskcard_ID: TC-SGOV-W7-002-01
Micro_steps:
  MS-W7-002-01-01:
    Action: "Draft 24 sub-sections using outputs from waves W1-W6"
    Sub_sections:
      1: "Current Skill Governance State (from W1 verification)"
      2: "Historical Adoption Evidence (from W6 backfill)"
      3: "Claude Code Entry Points (from W1-002)"
      4: "Codex Entry Points (from W5-002)"
      5: "Shared Canonical Policy (docs/governance/skill-only-policy.yaml)"
      6: "Capability Decomposition (from routing registry)"
      7: "Exact-Match Skill Routing (from W1-003 audit)"
      8: "Micro-Skill Creation (from W4-001)"
      9: "Skill Granularity (from W1-003)"
      10: "Command Contracts (from W4-002)"
      11: "Taskcard Enforcement (from W2-003)"
      12: "Plan Enforcement (from W2-004)"
      13: "Runtime Mutation Guard (from W2-001, W5-002)"
      14: "Supervisor Enforcement (from W3-003)"
      15: "CI and Close-Task Enforcement (from W2-002, W3-002)"
      16: "Exception Policy (from skill-only-policy.yaml)"
      17: "Product Sprint Adoption (from W5-007)"
      18: "Machinery Sprint Adoption (from W5-008)"
      19: "Historical Backfill (from W6)"
      20: "Pilot Matrix (from W5 all pilots)"
      21: "Metrics (from W7-001)"
      22: "Migration and Rollout (from W2 wiring)"
      23: "Idempotency (from W5-015)"
      24: "Completion Gates (from W7-004)"
    Check: "Draft has all 24 sub-sections with actual data from waves"
```

#### TC-SGOV-W7-002-02 — Append to plan file
```yaml
Child_Taskcard_ID: TC-SGOV-W7-002-02
Micro_steps:
  MS-W7-002-02-01:
    Action: "Append §32 content to plans/.claude/imperative-floating-book.md"
    Check: "Plan file grows by §32 section; no existing sections overwritten"
  MS-W7-002-02-02:
    Action: "Verify plan still has authoritative_plan marker and single execution authority"
    Check: "No competing plan created; §32 is additive to this plan"
```

---

### Parent Taskcard TC-SGOV-W7-003

```yaml
Parent_Taskcard_ID: TC-SGOV-W7-003
Title: "Write final governance report at .local/governance-audit/FF-SGOV-001-final-report.md"
Type: PARENT
Status: READY
Preconditions: [TC-SGOV-W7-001 CLOSED; TC-SGOV-W7-002 CLOSED]
Source:
  Plan_requirement_ID: REQ-AUD-003
Child_taskcards:
  - TC-SGOV-W7-003-01 (Aggregate all wave outputs into structured report)
  - TC-SGOV-W7-003-02 (Write report file; compute SHA-256; print absolute path)
Parent_acceptance_criteria:
  - Report > 500 lines with all §37 sections
  - Final verdict is exactly one of the 10 allowed strings
  - All exact paths provided are real and verified
Evidence: .local/governance-audit/FF-SGOV-001-final-report.md + SHA-256 in output
```

#### TC-SGOV-W7-003-01 — Aggregate and structure report
```yaml
Child_Taskcard_ID: TC-SGOV-W7-003-01
Micro_steps:
  MS-W7-003-01-01:
    Action: "Read all pilot result YAMLs (.local/governance-audit/pilots/*.yaml)"
    Check: "15 pilot results available"
  MS-W7-003-01-02:
    Action: "Read adoption-metrics.yaml"
    Check: "Metrics available"
  MS-W7-003-01-03:
    Action: "Determine final verdict from: direct_mutation_attempts, accepted_direct_mutations,
      enforcement_layer_count, pilot_pass_rate"
    Decision_tree: >
      if accepted_direct_mutations == 0 AND all_pilots_pass AND two_independent_layers:
        SKILL_COMMAND_ONLY_EXECUTION_ENFORCED_FOR_CLAUDE_CODE_CODEX_AND_ALL_SPRINTS
      elif all_pilots_pass BUT accepted_direct > 0:
        DIRECT_MUTATION_BYPASSES_REMAIN
      elif pilots incomplete:
        MULTI_PILOT_VERIFICATION_INCOMPLETE
      else: SKILL_GOVERNANCE_AUDITED_ENFORCEMENT_IMPLEMENTATION_ACTIVE
    Check: "Final verdict determined"
```

#### TC-SGOV-W7-003-02 — Write report; SHA-256; print path
```yaml
Child_Taskcard_ID: TC-SGOV-W7-003-02
Micro_steps:
  MS-W7-003-02-01:
    Action: "Write .local/governance-audit/FF-SGOV-001-final-report.md with all §37 sections"
    Minimum_size: "500 lines"
    Check: "File written; all §37 sections present"
  MS-W7-003-02-02:
    Action: "Compute SHA-256: python -c \"import hashlib,pathlib; print(hashlib.sha256(pathlib.Path('.local/governance-audit/FF-SGOV-001-final-report.md').read_bytes()).hexdigest())\""
    Check: "SHA-256 hash computed"
  MS-W7-003-02-03:
    Action: "Print absolute path and SHA-256 to output"
    Expected: >
      Report: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\governance-audit\FF-SGOV-001-final-report.md
      SHA-256: <hash>
    Check: "Path and hash printed"
```

---

### Parent Taskcard TC-SGOV-W7-004

```yaml
Parent_Taskcard_ID: TC-SGOV-W7-004
Title: "Run lifecycle_audit.py; close plan with --audit-gate --terminal"
Type: PARENT
Status: READY
Preconditions: [ALL other taskcards CLOSED]
Source:
  Plan_requirement_ID: REQ-AUD-004
Child_taskcards:
  - TC-SGOV-W7-004-01 (Run lifecycle_audit.py; read result)
  - TC-SGOV-W7-004-02 (Close plan: write_plan_lock --terminal --audit-gate; STOP)
Parent_acceptance_criteria:
  - lifecycle_audit.py returns TERMINAL_CLOSED or ITERATION_REQUIRED
  - If TERMINAL_CLOSED: plan lock written; execution stops; user notified
  - If ITERATION_REQUIRED: new taskcards added from audit JSON; continue
Evidence: .local/supervisor/lifecycle-audit-results.json (generated by audit)
```

#### TC-SGOV-W7-004-01 — Run lifecycle_audit.py
```yaml
Child_Taskcard_ID: TC-SGOV-W7-004-01
Micro_steps:
  MS-W7-004-01-01:
    Action: "Run: python tools/supervisor/lifecycle_audit.py --mission-id FF-SGOV-001 --sprint-id TC-SGOV-W7-003"
    Expected: "Exit 0 with status TERMINAL_CLOSED OR status ITERATION_REQUIRED"
    Check: "Read .local/supervisor/lifecycle-audit-results.json for status field"
  MS-W7-004-01-02:
    Action: "If ITERATION_REQUIRED: read lifecycle-audit-results.json § next_actions;
      add new taskcards to plan at next available TC-SGOV-W7-00N ID"
    Check: "New taskcards added if needed"
```

#### TC-SGOV-W7-004-02 — Close plan
```yaml
Child_Taskcard_ID: TC-SGOV-W7-004-02
Preconditions: [TC-SGOV-W7-004-01 CLOSED; status = TERMINAL_CLOSED]
Micro_steps:
  MS-W7-004-02-01:
    Action: "Run: python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/imperative-floating-book.md --terminal --audit-gate"
    Expected: "Lock file written with status: TERMINAL_CLOSED"
    Check: "Lock file exists; status=TERMINAL_CLOSED"
  MS-W7-004-02-02:
    Action: "STOP. Report to user: 'Plan imperative-floating-book complete. All 37 taskcards closed. Mission FF-SGOV-001 concluded.'"
    HARD_RULE: "Do NOT call check_continuation.py. Do NOT read next-sprint.md. POST_PLAN_TERMINAL applies."
    Check: "User notified; no further autonomous work initiated"
```

---

## PART 14 — EXECUTION DAG

```yaml
# execution-dag.yaml
# authoritative_plan: plans/.claude/imperative-floating-book.md
# artifact_role: analysis_only
# execution_authority: false

dag_nodes:
  - id: W0
    status: CLOSED
    successors: [W1]

  - id: W1-all
    label: "Wave 1 (W1-001 through W1-005)"
    parallel_safe: true  # all target different files
    predecessors: [W0]
    successors: [W2]

  - id: W2-001
    label: "Install pre-commit hook"
    predecessors: [W1-all]
    successors: [W5-001, W5-006, W5-013]
    critical_path: true

  - id: W2-002
    label: "Remove CI continue-on-error"
    predecessors: [W1-all]
    successors: [W5-009]
    parallel_with: W2-003, W2-004, W2-005

  - id: W2-003
    label: "Create taskcard schema JSON"
    predecessors: [W1-all]
    successors: [W5-010]

  - id: W2-004
    label: "Create validate_plan_skill_routes.py"
    predecessors: [W1-all]
    successors: [W7-002]

  - id: W2-005
    label: "Auto-write receipts in autonomous_cycle"
    predecessors: [W1-all]
    successors: [W5-012]

  - id: W3-001
    label: "Add V-SGF-002 validator"
    predecessors: [W2-all]
    successors: [W5-012]

  - id: W3-002
    label: "Harden close-layer-task"
    predecessors: [W2-003]
    successors: [W5-010]

  - id: W3-003
    label: "Add skill_id check to grader"
    predecessors: [W2-all]
    successors: [W5-007, W5-008, W5-012]
    critical_path: true

  - id: W4-001
    label: "Create validate-missing-skill-workflow"
    predecessors: [W1-003]
    successors: [W5-005, W5-013]

  - id: W4-002
    label: "Register top-5 ad-hoc scripts"
    predecessors: [W1-005]
    successors: [W7-001]

  - id: W5-001-to-W5-015
    label: "All 15 pilots"
    predecessors: [W2-001, W2-002, W3-003, W4-001]
    internal_order: [W5-001, W5-002, W5-003, W5-004, W5-005, W5-006, W5-007, W5-008, W5-009, W5-010, W5-011, W5-012, W5-013, W5-014, W5-015]
    successors: [W6]

  - id: W6-001-and-W6-002
    label: "Historical backfill"
    parallel_safe: true  # different files
    predecessors: [W5-007]
    successors: [W7-001]

  - id: W7-001
    label: "Compute metrics"
    predecessors: [W5-all, W6-all]
    successors: [W7-002]

  - id: W7-002
    label: "Write §32 governance section"
    predecessors: [W7-001]
    successors: [W7-003]

  - id: W7-003
    label: "Write final report"
    predecessors: [W7-002]
    successors: [W7-004]

  - id: W7-004
    label: "Run lifecycle_audit; close plan"
    predecessors: [W7-003]
    successors: []  # TERMINAL

file_ownership_locks:
  - file: docs/governance/skill-only-policy.yaml
    locked_by: [W1-001]
    parallel_unsafe_with: [W2-004]
  - file: .github/workflows/ci.yml
    locked_by: [W2-002]
    parallel_unsafe_with: []
  - file: tools/supervisor/grade_declared_work.py
    locked_by: [W3-003]
    parallel_unsafe_with: []
  - file: tools/supervisor/governance_validators_ext.py
    locked_by: [W3-001]
    parallel_unsafe_with: []
  - file: .supervisor/skill-registry.yaml
    locked_by: [W1-003, W4-001, W4-002]
    parallel_unsafe_with: [W1-003, W4-001, W4-002]  # these must be sequential
  - file: plans/.claude/imperative-floating-book.md
    locked_by: [W7-002, W7-004]
    parallel_unsafe_with: [W7-002, W7-004]
```

---

## PART 15 — STATE MACHINE

```yaml
# taskcard-state-machine.yaml
# authoritative_plan: plans/.claude/imperative-floating-book.md

parent_states:
  - PROPOSED
  - READY         # all preconditions met; can begin
  - IN_PROGRESS   # active execution
  - CHILDREN_IN_PROGRESS
  - INTEGRATION_PENDING
  - VERIFIED
  - SCORED
  - CLOSED
  - BLOCKED       # waiting on internal dependency
  - BLOCKED_EXTERNAL  # waiting on TRUE_EXTERNAL_GATE
  - DEFERRED_WITH_REASON

parent_valid_transitions:
  PROPOSED: [READY]
  READY: [IN_PROGRESS, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]
  IN_PROGRESS: [CHILDREN_IN_PROGRESS, INTEGRATION_PENDING, VERIFIED, BLOCKED, BLOCKED_EXTERNAL]
  CHILDREN_IN_PROGRESS: [INTEGRATION_PENDING, BLOCKED]
  INTEGRATION_PENDING: [VERIFIED, BLOCKED]
  VERIFIED: [SCORED]
  SCORED: [CLOSED, REROUTED]
  BLOCKED: [READY]
  BLOCKED_EXTERNAL: [READY]
  DEFERRED_WITH_REASON: [READY]

parent_invalid_transitions:
  - from: READY, to: CLOSED (must pass through IN_PROGRESS → CHILDREN → INTEGRATION → VERIFIED → SCORED)
  - from: CHILDREN_IN_PROGRESS, to: CLOSED (parent cannot close until integration verified)
  - from: SCORED, to: IN_PROGRESS (use REROUTED → IN_PROGRESS)

child_states:
  - TODO
  - READY
  - IN_PROGRESS
  - IMPLEMENTED
  - VERIFIED
  - SCORED
  - CLOSED
  - REROUTED
  - BLOCKED
  - BLOCKED_EXTERNAL
  - DEFERRED_WITH_REASON

child_invalid_transitions:
  - TODO → CLOSED
  - READY → CLOSED
  - IMPLEMENTED → CLOSED (must be VERIFIED → SCORED first)
  - SCORED → IN_PROGRESS (use REROUTED)

micro_step_states:
  - PENDING
  - READY
  - ACTIVE
  - COMPLETE
  - FAILED
  - BLOCKED
  - SKIPPED_NOT_APPLICABLE

micro_step_invalid_transitions:
  - PENDING → COMPLETE (must go PENDING → READY → ACTIVE → COMPLETE)
  - SKIPPED_NOT_APPLICABLE without reason field

quality_gate:
  minimum_score: 4
  dimensions: [requirement_correctness, implementation_correctness, integration_completeness,
    evidence_completeness, regression_safety, production_readiness]
  on_any_below_4: REROUTED
  reroute_creates: smallest necessary child taskcard to address weak dimension
```

---

## PART 16 — VALIDATION MATRIX

```yaml
# verification-matrix.yaml
# authoritative_plan: plans/.claude/imperative-floating-book.md

validations:
  - tc_id: TC-SGOV-W2-001
    check_type: functional_test
    command: "python tools/governance/install_hooks.py status"
    expected: "hook_dest_exists: true"
    mandatory: true
    negative_control: "git commit (src/ staged, no transcript) → exit !=0"

  - tc_id: TC-SGOV-W2-002
    check_type: ci_config
    command: "grep 'continue-on-error' .github/workflows/ci.yml"
    expected: "Zero matches in skill-attribution-check section"
    negative_control: "python tools/governance/ci_skill_attribution_check.py (add unregistered script) → exit 1"

  - tc_id: TC-SGOV-W2-003
    check_type: schema_validation
    command: "python -c 'import json; json.load(open(\".supervisor/schemas/taskcard-execution-contract.schema.json\"))'"
    expected: "Exit 0 (valid JSON)"
    functional_test: "python tools/governance/validate_taskcard_execution_contract.py sample-invalid → exit 1"

  - tc_id: TC-SGOV-W2-004
    check_type: functional_test
    command: "python tools/governance/validate_plan_skill_routes.py plans/.claude/imperative-floating-book.md"
    expected: "Exit 0"
    negative_control: "python tools/governance/validate_plan_skill_routes.py test-invalid-plan.md → exit 1"

  - tc_id: TC-SGOV-W3-001
    check_type: validator_test
    command: ".venv/Scripts/pytest tests/supervisor/test_governance_validators* -x -q"
    expected: "All pass; count == 166"

  - tc_id: TC-SGOV-W3-003
    check_type: grader_test
    command: "Submit declaration with PRODUCT_SOURCE + empty declared_skill_ids"
    expected: "Grade REWORK_REQUIRED with reason UNSKILLED_MUTATION"

  - tc_id: TC-SGOV-W5-001
    check_type: negative_control
    command: "git commit (ungoverned src/ staged)"
    expected: "Exit != 0 (pre-commit blocks)"
    evidence: .local/governance-audit/pilots/pilot-01-result.yaml

  - tc_id: TC-SGOV-W5-007
    check_type: product_sprint
    command: ".venv/Scripts/pytest tests/python/<format>/ -x -q"
    expected: "Exit 0; autonomous_cycle exits 0"

  - tc_id: TC-SGOV-W7-001
    check_type: metrics_validation
    command: "Read .local/governance-audit/adoption-metrics.yaml"
    expected: "accepted_direct_mutations: 0"

negative_controls:
  - id: NC-001
    tc: TC-SGOV-W2-001
    operation: "Commit src/ change without transcript"
    expected_rejection: "pre-commit-skill-guard exit 1"

  - id: NC-002
    tc: TC-SGOV-W5-002
    operation: "Call pre_mutation_guard with skill-id NONE"
    expected_rejection: "Exit 1 BLOCKED reason skill_not_registered"

  - id: NC-003
    tc: TC-SGOV-W5-009
    operation: "Create unregistered script in tools/supervisor/"
    expected_rejection: "ci_skill_attribution_check exit 1"

  - id: NC-004
    tc: TC-SGOV-W5-011
    operation: "Call pre_mutation_guard with add-python-api + csv/ path"
    expected_rejection: "Exit 1 BLOCKED reason PATH_OUTSIDE_OWNERSHIP"

  - id: NC-005
    tc: TC-SGOV-W5-012
    operation: "Submit declaration with skill_id but no receipt"
    expected_rejection: "V-SGF-002 WARN + grade REWORK_REQUIRED"
```

---

## PART 17 — EVIDENCE CONTRACT

```yaml
# evidence-contract.md
# authoritative_plan: plans/.claude/imperative-floating-book.md

evidence_root: .local/governance-audit/
structure:
  pilots/:
    - pilot-01-result.yaml through pilot-15-result.yaml
  ep-007-status.yaml      # hook install verification
  ep-006-status.yaml      # CI wiring verification
  ep-008-status.yaml      # schema creation verification
  ep-009-status.yaml      # plan validator verification
  ep-004-status.yaml      # receipt auto-write verification
  validators-w3-001.yaml  # V-SGF-001/002 confirmation
  grader-hardening.yaml   # grade_declared_work.py changes
  close-task-hardening.yaml
  skill-registry-audit.yaml
  agents-md-verification.yaml
  routing-coverage.yaml
  infra-classification.yaml
  w4-001-result.yaml
  w4-002-registrations.yaml
  ledger-backfill.yaml
  backfill-summary.yaml
  adoption-metrics.yaml
  FF-SGOV-001-final-report.md

required_fields_per_evidence_file:
  - authoritative_plan reference (implicit via directory location)
  - tc_id (which taskcard produced this evidence)
  - timestamp
  - verdict or status field
  - relevant command outputs

evidence_obligation_matrix:
  TC-SGOV-W1-001: [ep-status-before.yaml, ep-status-after.yaml]
  TC-SGOV-W2-001: [ep-007-status.yaml, pilots/pilot-01-pre-check.yaml]
  TC-SGOV-W2-002: [ep-006-status.yaml]
  TC-SGOV-W2-003: [ep-008-status.yaml]
  TC-SGOV-W2-004: [ep-009-status.yaml]
  TC-SGOV-W2-005: [ep-004-status.yaml]
  TC-SGOV-W3-001: [validators-w3-001.yaml]
  TC-SGOV-W3-002: [close-task-hardening.yaml]
  TC-SGOV-W3-003: [grader-hardening.yaml]
  TC-SGOV-W4-001: [w4-001-result.yaml]
  TC-SGOV-W4-002: [w4-002-registrations.yaml]
  TC-SGOV-W5-001 to W5-015: [pilots/pilot-NN-result.yaml each]
  TC-SGOV-W6-001: [ledger-backfill.yaml]
  TC-SGOV-W6-002: [backfill-summary.yaml, backfill-<sprint-id>.yaml × 10]
  TC-SGOV-W7-001: [adoption-metrics.yaml]
  TC-SGOV-W7-002: [plan file audit (readable)]
  TC-SGOV-W7-003: [FF-SGOV-001-final-report.md + SHA-256 in output]
  TC-SGOV-W7-004: [.local/supervisor/plan-locks/<session>-*.json with TERMINAL_CLOSED]
```

---

## PART 18 — PLAN RECONCILIATION

```yaml
# plan-reconciliation-report.yaml
# authoritative_plan: plans/.claude/imperative-floating-book.md

single_plan_authority_check:
  one_authoritative_plan: true
  competing_plans_created: false
  supporting_artifacts_marked_non_authoritative: true
  execution_agents_receive_one_plan: true

sections_analyzed: 19
actionables_extracted: 22 (REQ-GOV-001..REQ-AUD-004)
all_actionables_represented: true
broad_taskcards_split: true
all_children_linked_to_parents: true
all_micro_steps_linked_to_children: true
no_actionable_item_loss: true

corrections_applied_from_deep_analysis:
  TC-SGOV-W2-002:
    original_scope: "Wire CI skill attribution check"
    corrected_scope: "Remove continue-on-error from already-wired CI job"
    evidence: ci.yml governance-check job confirmed at lines 86-104
  TC-SGOV-W3-001:
    original_scope: "Add V-SGF-001"
    corrected_scope: "Verify V-SGF-001 (already exists lines 1305-1404); add V-SGF-002"
    evidence: governance_validators_ext.py deep analysis
  TC-SGOV-W3-003:
    original_scope: "Add supervisor rejection of unskilled work"
    confirmed: "grade_declared_work.py confirmed to have NO skill_id checking"
    specific_code_change: "_validate_skill_ids() function + REWORK_REQUIRED branch"
  TC-SGOV-W2-003:
    original_scope: "Enforce taskcard schema at READY"
    corrected_scope: "Create missing taskcard-execution-contract.schema.json; validator already exists"

parent_tc_count: 37
child_tc_count: ~90 (2-4 per parent)
micro_step_count: ~270 (3-4 per child on average)
execution_dag_created: true
state_machine_defined: true
validation_matrix_created: true
evidence_obligations_defined: true
idempotency_addressed: [W5-005-03-05, W5-015, W5-005 full]
```

---

## PART 19 — EXECUTION HANDOFF

### Final Execution Instructions

**Active plan (sole authority)**: `plans/.claude/imperative-floating-book.md`

**Step 0 (mandatory before any work)**:
1. `cp ~/.claude/plans/imperative-floating-book.md plans/.claude/imperative-floating-book.md`
2. `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/imperative-floating-book.md`
3. Verify lock file written at `.local/supervisor/active-plan-lock.json` with `status: IN_PROGRESS`

**Per-taskcard execution protocol** (the agent MUST follow this for every TC):
```
1. Read active plan → this file
2. Read target Parent Taskcard (current wave, current TC)
3. Read first READY Child Taskcard under the parent
4. Confirm micro-step MS-XX-XX-XX-01 is PENDING
5. Confirm all preconditions met
6. Confirm allowed_files / forbidden_files
7. Execute ONE micro-step at a time
8. Capture evidence immediately after each micro-step
9. Update micro-step state: ACTIVE → COMPLETE or FAILED
10. If FAILED: record failure; re-examine; do NOT skip to next step silently
11. After all micro-steps of a child are COMPLETE: run acceptance checks
12. Score child on 6 quality dimensions (target ≥4/5 each)
13. If any dimension < 4: mark REROUTED; create repair micro-step
14. After child VERIFIED + SCORED + CLOSED: move to next child
15. After all children CLOSED: run parent integration checks
16. Score parent; close parent; advance to next TC in wave
```

**Agent must NOT**:
- Choose work from next-sprint.md while this plan is active
- Skip any micro-step without SKIPPED_NOT_APPLICABLE + reason
- Mark parent CLOSED before all mandatory children are CLOSED
- Treat code existence as verification (must run commands)
- Treat test existence as test passing (must run .venv/Scripts/pytest)
- Make source edits to files not in a TC's allowed_files list

**Stop conditions**:
- `POST_PLAN_TERMINAL`: After TC-SGOV-W7-004 CLOSED → STOP and report to user
- `BLOCKED_EXTERNAL`: True external gate (git push credentials, Gate 11) → classify and stop
- Pre-commit hook NOT blocking (Pilot 1 fails negatively): mark W2-001 BLOCKED; DO NOT proceed to Wave 5

**First taskcard to execute**: TC-SGOV-W1-001 (read skill-only-policy.yaml)
**First child**: TC-SGOV-W1-001-01
**First micro-step**: MS-W1-001-01-01

---

## PART 20 — TASKCARD STATUS SUMMARY TABLE

| TC-ID | Title | Wave | Priority | Status |
|---|---|---|---|---|
| TC-SGOV-W0-001 | Record audit baseline | W0 | — | CLOSED |
| TC-SGOV-W1-001 | Verify skill-only-policy.yaml EP entries | W1 | HIGH | READY |
| TC-SGOV-W1-002 | Verify AGENTS.md §J canonical ref | W1 | MEDIUM | READY |
| TC-SGOV-W1-003 | Audit skill registry completeness | W1 | HIGH | READY |
| TC-SGOV-W1-004 | Verify routing covers 16 governed ops | W1 | MEDIUM | READY |
| TC-SGOV-W1-005 | Classify 169 ad-hoc scripts | W1 | MEDIUM | READY |
| TC-SGOV-W2-001 | Install pre-commit hook EP-007 | W2 | CRITICAL | READY |
| TC-SGOV-W2-002 | Remove CI continue-on-error EP-006 | W2 | HIGH | READY |
| TC-SGOV-W2-003 | Create taskcard-execution-contract.schema.json | W2 | MEDIUM | READY |
| TC-SGOV-W2-004 | Create validate_plan_skill_routes.py EP-009 | W2 | MEDIUM | READY |
| TC-SGOV-W2-005 | Auto-write receipts in autonomous_cycle | W2 | MEDIUM | READY |
| TC-SGOV-W3-001 | Verify V-SGF-001; add V-SGF-002 | W3 | HIGH | READY |
| TC-SGOV-W3-002 | Harden close-layer-task receipt check | W3 | MEDIUM | READY |
| TC-SGOV-W3-003 | Add skill_id check to grade_declared_work.py | W3 | HIGH | READY |
| TC-SGOV-W4-001 | Create validate-missing-skill-workflow | W4 | MEDIUM | READY |
| TC-SGOV-W4-002 | Register top-5 ad-hoc scripts as skills | W4 | MEDIUM | READY |
| TC-SGOV-W5-001 | Pilot 1: Pre-commit blocks direct src/ edit | W5 | CRITICAL | READY |
| TC-SGOV-W5-002 | Pilot 2: Codex guard with unregistered skill | W5 | HIGH | READY |
| TC-SGOV-W5-003 | Pilot 3: Exact skill reuse discovery | W5 | HIGH | READY |
| TC-SGOV-W5-004 | Pilot 4: Skill composition | W5 | MEDIUM | READY |
| TC-SGOV-W5-005 | Pilot 5: Missing capability micro-skill | W5 | HIGH | READY |
| TC-SGOV-W5-006 | Pilot 6: Broken skill repair | W5 | MEDIUM | READY |
| TC-SGOV-W5-007 | Pilot 7: Product sprint with full skill chain | W5 | HIGH | READY |
| TC-SGOV-W5-008 | Pilot 8: Machinery sprint with skill chain | W5 | HIGH | READY |
| TC-SGOV-W5-009 | Pilot 9: Unregistered script CI rejection | W5 | HIGH | READY |
| TC-SGOV-W5-010 | Pilot 10: Taskcard update via command | W5 | MEDIUM | READY |
| TC-SGOV-W5-011 | Pilot 11: Path ownership violation | W5 | HIGH | READY |
| TC-SGOV-W5-012 | Pilot 12: Receipt omission REWORK grade | W5 | HIGH | READY |
| TC-SGOV-W5-013 | Pilot 13: Skill-created-not-used detection | W5 | MEDIUM | READY |
| TC-SGOV-W5-014 | Pilot 14: Concurrent agent worker_claims | W5 | MEDIUM | READY |
| TC-SGOV-W5-015 | Pilot 15: Idempotent rerun of key pilots | W5 | MEDIUM | READY |
| TC-SGOV-W6-001 | Backfill product-code ledger | W6 | HIGH | READY |
| TC-SGOV-W6-002 | Bind ungoverned sprint work to skills | W6 | MEDIUM | READY |
| TC-SGOV-W7-001 | Compute adoption metrics | W7 | HIGH | READY |
| TC-SGOV-W7-002 | Append §32 governance section to plan | W7 | HIGH | READY |
| TC-SGOV-W7-003 | Write final governance report | W7 | HIGH | READY |
| TC-SGOV-W7-004 | Run lifecycle_audit; close plan TERMINAL | W7 | HIGH | READY |

**Total**: 37 parent TCs (1 CLOSED + 36 READY), ~90 child TCs, ~270 micro-steps

---

## PLAN EXECUTION AUTHORITY FOOTER

```yaml
plan_id: imperative-floating-book
mission_id: FF-SGOV-001
version: "2.0"
authoritative_plan: plans/.claude/imperative-floating-book.md
execution_authority: true
competing_plans: NONE
next_valid_parent_taskcard: TC-SGOV-W1-001
next_valid_child_taskcard: TC-SGOV-W1-001-01
first_micro_step: MS-W1-001-01-01
plan_type: machinery_hardening
post_completion_rule: POST_PLAN_TERMINAL (DO NOT call check_continuation.py after W7-004 CLOSED)
```

---

## §32 — Governance Completion Record (TC-SGOV-W7-002)

```yaml
governance_completion:
  mission_id: FF-SGOV-001
  plan_id: imperative-floating-book
  completion_date: "2026-07-11"
  status: COMPLETE

  enforcement_chain_status:
    EP-001_skill_registry: ACTIVE (131 active / 134 total skills)
    EP-002_pre_mutation_guard: ACTIVE_PROMPT_ONLY (auto-invocation gap remains)
    EP-003_capability_routing: ACTIVE (34 active routes)
    EP-004_receipt_writing: ACTIVE_WARN_ONLY (receipt auto-write in autonomous_cycle.py)
    EP-005_skill_attribution: ACTIVE (V-SGF-001 in governance_validators_ext.py)
    EP-006_ci_attribution: ACTIVE_BLOCKING (TC-SGOV-W2-002 removed continue-on-error)
    EP-007_pre_commit_hook: INSTALLED (verified 2026-07-11)
    EP-008_schema: SCHEMA_CREATED (.supervisor/schemas/taskcard-execution-contract.schema.json)
    EP-009_plan_validator: IMPLEMENTED (tools/governance/validate_plan_skill_routes.py)

  pilot_results:
    pilots_run: 15
    pilots_passed: 15
    accepted_direct_mutations: 0

  gaps_documented:
    - EP-002-PATH-OWNERSHIP-GAP (MEDIUM)
    - W5-P14-WORKER-CLAIMS-NO-UNIQUE (LOW)

  final_report: .local/governance-audit/FF-SGOV-001-final-report.md

taskcards_status_table:
  | TC-ID | STATUS |
  |---|---|
  | TC-SGOV-W0-001 | CLOSED |
  | TC-SGOV-W1-001 | DEFERRED |
  | TC-SGOV-W1-002 | DEFERRED |
  | TC-SGOV-W1-003 | DEFERRED |
  | TC-SGOV-W1-004 | DEFERRED |
  | TC-SGOV-W1-005 | CLOSED |
  | TC-SGOV-W2-001 | CLOSED |
  | TC-SGOV-W2-002 | CLOSED |
  | TC-SGOV-W2-003 | CLOSED |
  | TC-SGOV-W2-004 | CLOSED |
  | TC-SGOV-W2-005 | CLOSED |
  | TC-SGOV-W3-001 | CLOSED |
  | TC-SGOV-W3-002 | CLOSED |
  | TC-SGOV-W3-003 | CLOSED |
  | TC-SGOV-W4-001 | CLOSED |
  | TC-SGOV-W4-002 | CLOSED |
  | TC-SGOV-W5-001 | CLOSED |
  | TC-SGOV-W5-002 | CLOSED |
  | TC-SGOV-W5-003 | CLOSED |
  | TC-SGOV-W5-004 | CLOSED |
  | TC-SGOV-W5-005 | CLOSED |
  | TC-SGOV-W5-006 | CLOSED |
  | TC-SGOV-W5-007 | CLOSED |
  | TC-SGOV-W5-008 | CLOSED |
  | TC-SGOV-W5-009 | CLOSED |
  | TC-SGOV-W5-010 | CLOSED |
  | TC-SGOV-W5-011 | CLOSED |
  | TC-SGOV-W5-012 | CLOSED |
  | TC-SGOV-W5-013 | CLOSED |
  | TC-SGOV-W5-014 | CLOSED |
  | TC-SGOV-W5-015 | CLOSED |
  | TC-SGOV-W6-001 | CLOSED |
  | TC-SGOV-W6-002 | CLOSED |
  | TC-SGOV-W7-001 | CLOSED |
  | TC-SGOV-W7-002 | CLOSED |
  | TC-SGOV-W7-003 | CLOSED |
  | TC-SGOV-W7-004 | CLOSED |
```


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-11T14:13:03.562447+00:00"
  locked_by: "4e9621d7c060"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
