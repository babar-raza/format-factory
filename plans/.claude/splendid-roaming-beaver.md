# Plan: splendid-roaming-beaver (Enhanced v2 — Micro-Taskcardized)
# Format Factory — Forensic Sprint Healing & Production Supervision Engine
# Plan type: machinery_hardening
# Mission ID: SRB-SPRINT-ENGINE-PRODUCTIONIZATION-001
# Authority: per-chat-plan
# Authoritative plan path: C:\Users\prora\.claude\plans\splendid-roaming-beaver.md
# In-repo copy (target after TC-SRB-000): plans/.claude/splendid-roaming-beaver.md
# Created: 2026-07-10 | Enhanced: 2026-07-10

---

## PART A — PREFLIGHT AND AUTHORITY RECORDS
### (Deliverables: taskcardization-preflight, active-plan-authority-verdict, duplicate-plan-risk-check, plan-section-inventory, plan-structure-and-normalization-profile)

### A.1 Taskcardization Preflight

```yaml
preflight:
  repository_path: c:\Users\prora\OneDrive\Documents\GitHub\format-factory
  branch: main
  head_commit: see git log (not read in plan mode)
  active_plan_path: C:\Users\prora\.claude\plans\splendid-roaming-beaver.md
  in_repo_target: plans/.claude/splendid-roaming-beaver.md
  plan_title: "Format Factory Forensic Sprint Healing & Production Supervision Engine"
  plan_format: markdown_with_embedded_yaml
  plan_authority_source: per-chat-plan (user invoked via plan mode)
  plan_size_v1: ~780 lines (original)
  plan_size_v2: ~1200 lines (this enhanced version)
  major_sections: 7 phases + appendices
  existing_taskcard_count: 29 (TC-SRB-000 through TC-SRB-090)
  existing_taskcard_format: flat (no parent/child/micro-step hierarchy)
  existing_lanes: none (sequential phases only)
  existing_waves: none
  existing_gates: acceptance criteria per TC (informal)
  existing_state_vocabulary: OPEN (single status only)
  existing_validation_model: Acceptance criteria prose (not structured)
  existing_evidence_model: evidence_at paths (informal)
  existing_execution_handoff: none (missing)
  duplicate_plan_risk: LOW (single SRB plan, no competing versions found)
```

### A.2 Active Plan Authority Verdict

```yaml
authority_verdict:
  authoritative_plan: C:\Users\prora\.claude\plans\splendid-roaming-beaver.md
  authority_source: per-chat-plan (plan mode session)
  competing_plans_found: false
  stale_plans_found: false
  verdict: AUTHORITATIVE_SINGLE_PLAN
  action: enhance in place
```

### A.3 State Discovery (critical corrections vs original)

**Corrections from deep analysis (2026-07-10):**

| Field | Original (v1) | Corrected (v2) | Source |
|---|---|---|---|
| Sprint count | ~585 | **840** | maturity-trend.json |
| Last sprint | vast-weaving-lampson | **PQ-BUNDLE-FORENSICS-REPAIR-001** | session-resume.md |
| Test count | 1169 | **21558** | session-resume.md |
| Rework items | none identified | **PQ-029-ADDRECORD, PQ-019-020-CLI-STUBS** | continuation-signal.json |
| continuation_state | YES | **YES_WITH_REWORK** | continuation-signal.json |
| sprint_number_allocator.py | assumed would be created | **confirmed does not exist** | filesystem |
| sprint-ledger.json | assumed would be created | **confirmed does not exist** | filesystem |
| `reason_codes` field | plan assumed it existed | **does NOT exist in schema** | autonomous_cycle.py |
| File locking on Windows | assumed fcntl or filelock | **use os.replace() atomic writes** | write_plan_lock.py pattern |

### A.4 Current State (corrected baseline)

```yaml
current_state:
  autonomous_continue: true_with_rework
  iteration: 5
  max_iterations: 12
  last_sprint_id: PQ-BUNDLE-FORENSICS-REPAIR-001
  tests_passing: 21558
  tests_failing: 0
  rework_items:
    - id: PQ-029-ADDRECORD
      title: "Add AddRecord() to NdjsonDocument (.NET)"
      grade: ACCEPTED_WITH_LIMITATIONS
      issue: "Path-only evidence; no actual AddRecord() method found in NdjsonDocument.cs"
    - id: PQ-019-020-CLI-STUBS
      title: "Extend CLI entry points and type stubs to all 20 Python packages"
      grade: REWORK_REQUIRED
      issue: "Only 2/20 packages covered (fods, fodt). 18 packages missing CLI+stubs."
  active_plan_lock: TERMINAL_CLOSED (session 033f6a1ae2f3 — different session, will be skipped)
  maturity_sprints: 840
  maturity_avg_quality: 0.756
  govblock_rate: 0.155 (130/840 sprints had governance blocks)
```

---

## PART B — SECTION PROCESSING LEDGER
### (Deliverables: section-processing-ledger, complete-plan-read-confirmation)

### B.1 Section Processing Ledger

```yaml
section_processing_ledger:
  - section_id: S-CTX
    title: Context
    type: background
    analyzed: yes
    corrections_required: yes (sprint count, last sprint, test count, rework items)
    change_status: UPDATED_IN_CONTEXT_SECTION

  - section_id: S-P-MINUS1
    title: "Phase -1: Rework Resolution (NEW)"
    type: execution
    analyzed: yes
    actionable_items_found: 2 (PQ-029-ADDRECORD, PQ-019-020-CLI-STUBS)
    existing_taskcards: none
    missing_taskcards: TC-SRB-RW1, TC-SRB-RW2
    ambiguities: precise fix scope for each rework item
    change_status: INSERTED (new phase)

  - section_id: S-P0
    title: "Phase 0: Session Bootstrap"
    type: execution
    analyzed: yes
    actionable_items_found: 3
    existing_taskcards: TC-SRB-000, TC-SRB-001, TC-SRB-002
    missing_taskcards: child decomposition missing
    ambiguities: none
    change_status: DECOMPOSED

  - section_id: S-P1
    title: "Phase 1: Sprint Forensic Inventory"
    type: execution
    analyzed: yes
    actionable_items_found: 4
    existing_taskcards: TC-SRB-010 through TC-SRB-013
    missing_taskcards: child decomposition
    ambiguities: bootstrapping 840 sprints (too large for full ledger)
    change_status: DECOMPOSED

  - section_id: S-P2
    title: "Phase 2: Atomic Sprint Number Allocator"
    type: execution + implementation
    analyzed: yes
    actionable_items_found: 5
    defects_found:
      - fcntl not available on Windows; use os.replace() pattern
      - no filelock dependency available
    change_status: DECOMPOSED + DEFECTS_CORRECTED

  - section_id: S-P3
    title: "Phase 3: Governance Violation Investigation"
    type: execution + investigation
    analyzed: yes
    defects_found:
      - reason_codes field does not exist in continuation-signal schema
      - must extend using new field name or use continuation_state
    change_status: DECOMPOSED + DEFECTS_CORRECTED

  - section_id: S-P4
    title: "Phase 4: Production Plan Section"
    type: documentation
    analyzed: yes
    change_status: DECOMPOSED

  - section_id: S-P5
    title: "Phase 5: Pilot Programs"
    type: pilot execution
    analyzed: yes
    defects_found:
      - P02/P03/P04 are stub references (need actual steps)
      - P09 needs mock gate 10 state (no real format at Gate 10)
      - P05 V7 trigger mechanism needs precise specification
    change_status: DECOMPOSED + DEFECTS_CORRECTED

  - section_id: S-P6
    title: "Phase 6: Product Deepening"
    type: execution
    analyzed: yes
    defects_found:
      - must address rework items FIRST (now in Phase -1)
      - specific gap selection criteria missing
    change_status: DECOMPOSED

  - section_id: S-P7
    title: "Phase 7: Final Audit"
    type: closeout
    analyzed: yes
    change_status: ENHANCED

complete_plan_read_confirmation:
  all_sections_read: yes
  all_taskcards_analyzed: yes
  all_ambiguities_recorded: yes
  all_defects_documented: yes
```

---

## PART C — REQUIREMENTS INVENTORY
### (Deliverables: normalized-requirements-inventory, section-to-requirement-map)

```yaml
requirements:
  REQ-SRB-001:
    domain: REWORK_RESOLUTION
    title: "Resolve PQ-029-ADDRECORD before new sprint work"
    source_section: S-P-MINUS1 (new)
    priority: BLOCKER (must resolve before TC-SRB-000 proceeds to new work)

  REQ-SRB-002:
    domain: REWORK_RESOLUTION
    title: "Resolve PQ-019-020-CLI-STUBS before new sprint work"
    source_section: S-P-MINUS1 (new)
    priority: BLOCKER

  REQ-SRB-003:
    domain: SESSION_BOOTSTRAP
    title: "Copy plan to repo and write plan lock before any execution"
    source_section: S-P0
    priority: CRITICAL

  REQ-SRB-004:
    domain: SESSION_BOOTSTRAP
    title: "Confirm check_continuation returns CONTINUE before product work"
    source_section: S-P0
    priority: CRITICAL

  REQ-SRB-005:
    domain: SPRINT_INVENTORY
    title: "Build canonical sprint inventory from all sources"
    source_section: S-P1
    priority: HIGH

  REQ-SRB-006:
    domain: SPRINT_INVENTORY
    title: "Detect and fix stale/orphan plan locks"
    source_section: S-P1
    priority: HIGH

  REQ-SRB-007:
    domain: SPRINT_IDENTITY
    title: "Establish sprint identity contract (SPRINT-NNNNN format)"
    source_section: S-P1
    priority: HIGH

  REQ-SRB-008:
    domain: SPRINT_ALLOCATOR
    title: "Implement atomic sprint number allocator using os.replace() pattern"
    source_section: S-P2
    priority: HIGH
    constraint: "Windows-compatible: os.replace() not fcntl"

  REQ-SRB-009:
    domain: SPRINT_ALLOCATOR
    title: "Register allocator as a governed skill in skill-registry.yaml"
    source_section: S-P2
    priority: HIGH

  REQ-SRB-010:
    domain: SPRINT_ALLOCATOR
    title: "Prove allocator idempotency and concurrent safety"
    source_section: S-P2
    priority: HIGH

  REQ-SRB-011:
    domain: GOVERNANCE
    title: "Document all 7 CRITICAL contradiction triggers with reproduction steps"
    source_section: S-P3
    priority: MEDIUM

  REQ-SRB-012:
    domain: GOVERNANCE
    title: "Extend continuation-signal.json with structured reason field"
    source_section: S-P3
    priority: MEDIUM
    constraint: "Field name: continuation_reason_codes (list) — NOT reason_codes (not in schema)"

  REQ-SRB-013:
    domain: PLAN_SECTION
    title: "Add 22-subsection production design to plans/master-plan.md"
    source_section: S-P4
    priority: MEDIUM

  REQ-SRB-014:
    domain: PILOTS
    title: "Run 10 diverse pilots covering all proof categories"
    source_section: S-P5
    priority: HIGH

  REQ-SRB-015:
    domain: PRODUCT_DEEPENING
    title: "Execute 2+ consecutive product-deepening sprints with unique allocated numbers"
    source_section: S-P6
    priority: HIGH

  REQ-SRB-016:
    domain: CLOSEOUT
    title: "Pass 20-item production readiness audit"
    source_section: S-P7
    priority: CRITICAL
```

---

## PART D — DEEP ANALYSIS PER PLAN PART
### (Deliverables: plan-part-deep-analysis, phase-section-step-analysis)

### D.1 Phase -1 (New): Rework Items
```yaml
plan_part_id: S-P-MINUS1
objective: Resolve two rework items before any new SRB work
root_causes_addressed:
  - PQ-029-ADDRECORD: AddRecord() evidence was path-only, not verified
  - PQ-019-020-CLI-STUBS: Only 2/20 packages had CLI+stub evidence; 18 missing
failure_modes:
  - If not resolved: continuation signal may block further autonomous cycles
  - If partially resolved: grade remains REWORK_REQUIRED
decomposition_strategy:
  - TC-SRB-RW1: Verify NdjsonDocument.cs contains AddRecord() OR implement it
  - TC-SRB-RW2: Create CLI entry points + type stubs for remaining 18 Python packages
```

### D.2 Phase 2 (Allocator) — Key Design Decision
```yaml
plan_part_id: S-P2-LOCK
objective: Atomic sprint number allocation on Windows
root_cause: fcntl not available on Windows; filelock not in dependencies
options_evaluated:
  - A: Add filelock package dependency (cross-platform) — requires pyproject.toml change
  - B: Use os.replace() atomic rename (already in use by write_plan_lock.py) — no new deps
  - C: Use msvcrt.locking (Windows-only, not portable)
  - D: Database-based (overkill)
selected_option: B (os.replace() pattern)
rationale: Already proven in write_plan_lock.py; zero new dependencies; portable
algorithm:
  1. Load current ledger JSON
  2. Find highest allocated_number
  3. Write to .lock.tmp file with new record
  4. Use os.replace() to atomically rename to .lock.json
  5. If lock file exists: read it; if >30s old, treat as stale and overwrite
  6. Idempotency: check if semantic_alias already in ledger before allocating
```

### D.3 Phase 3 (Governance) — Schema Correction
```yaml
plan_part_id: S-P3-REASON-CODES
objective: Add structured reason codes to continuation signal
root_cause: Original plan assumed reason_codes field exists; it does NOT
actual_schema:
  existing_field: stop_reason (string, nullable)
  existing_field: continuation_state (e.g., "YES_WITH_REWORK", "YES", "NO")
correction:
  - Do NOT rename stop_reason (breaking change)
  - ADD new field: continuation_reason_codes (list of strings)
  - ADD alongside existing fields in autonomous_cycle.py signal writer
implementation_target: tools/supervisor/autonomous_cycle.py around line 2207
test_strategy: Run autonomous-cycle on a test declaration; verify new field appears
```

### D.4 Phase 5 Pilot 9 (Gate 11) — Mock Strategy
```yaml
plan_part_id: S-P5-P09
objective: Prove Gate 11 stop behavior without a real format at Gate 10
constraint: No format is currently at Gate 10 in the real system
mock_strategy:
  - Create .local/supervisor/mock-gate-state.json with gate_10: COMPLETE for format "test-mock"
  - Create a test check_continuation call that reads mock gate state
  - Verify that when gate_10 is COMPLETE and gate_11 not authorized, continuation returns STOP
  - Verify independent formats continue normally
limitation: This is a simulated pilot, not a real Gate 10 advancement
documentation: Mark as SIMULATED_PILOT in evidence
```

---

## PART E — SOLUTION OPTIONS ANALYSIS
### (Deliverables: solution-options-analysis, solution-option-scorecard, selected-solution-rationale)

### E.1 Sprint Allocator Solution Options

| Option | Root-cause coverage | Durability | Safety | Testability | Complexity | Selected |
|---|---|---|---|---|---|---|
| A: filelock package | 5 | 5 | 5 | 5 | 3 (new dep) | NO |
| B: os.replace() atomic | 4 | 4 | 4 | 5 | 1 (no new dep) | **YES** |
| C: msvcrt.locking | 3 | 2 (Windows-only) | 3 | 3 | 2 | NO |
| D: SQLite DB | 5 | 5 | 5 | 4 | 5 (overkill) | NO |

Selected: **Option B** — matches existing patterns in write_plan_lock.py, zero new dependencies, portable.

### E.2 Continuation Reason Codes Solution Options

| Option | Root-cause coverage | Schema compat | Testability | Selected |
|---|---|---|---|---|
| A: Rename stop_reason to reason_codes list | 5 | 1 (breaking) | 3 | NO |
| B: Add continuation_reason_codes alongside stop_reason | 5 | 5 | 5 | **YES** |
| C: Embed in continuation_state string only | 2 | 5 | 3 | NO |

Selected: **Option B** — non-breaking addition.

---

## PART F — TASKCARD STATUS MASTER TABLE

| ID | Title | Type | Status | Parent |
|---|---|---|---|---|
| TC-SRB-RW1 | Resolve PQ-029-ADDRECORD | PARENT | PROPOSED | — |
| TC-SRB-RW1-01 | Verify AddRecord in NdjsonDocument.cs | CHILD | TODO | TC-SRB-RW1 |
| TC-SRB-RW1-02 | Implement AddRecord if missing | CHILD | TODO | TC-SRB-RW1 |
| TC-SRB-RW1-03 | Write test and declare evidence | CHILD | TODO | TC-SRB-RW1 |
| TC-SRB-RW2 | Resolve PQ-019-020-CLI-STUBS | PARENT | PROPOSED | — |
| TC-SRB-RW2-01 | Audit 18 missing packages | CHILD | TODO | TC-SRB-RW2 |
| TC-SRB-RW2-02 | Implement CLI entry points for 18 packages | CHILD | TODO | TC-SRB-RW2 |
| TC-SRB-RW2-03 | Implement type stubs for 18 packages | CHILD | TODO | TC-SRB-RW2 |
| TC-SRB-RW2-04 | Test and declare evidence | CHILD | TODO | TC-SRB-RW2 |
| TC-SRB-000 | Copy plan and write plan lock | PARENT | PROPOSED | — |
| TC-SRB-000-01 | Copy plan file to repo | CHILD | TODO | TC-SRB-000 |
| TC-SRB-000-02 | Write plan lock | CHILD | TODO | TC-SRB-000 |
| TC-SRB-001 | Run check_continuation baseline | PARENT | PROPOSED | — |
| TC-SRB-001-01 | Run check_continuation.py | CHILD | TODO | TC-SRB-001 |
| TC-SRB-001-02 | Fix any STOP condition | CHILD | TODO | TC-SRB-001 |
| TC-SRB-002 | Capture state baseline | PARENT | PROPOSED | — |
| TC-SRB-010 | Build sprint inventory | PARENT | PROPOSED | — |
| TC-SRB-010-01 | Enumerate plan-locks | CHILD | TODO | TC-SRB-010 |
| TC-SRB-010-02 | Enumerate evidence bundles | CHILD | TODO | TC-SRB-010 |
| TC-SRB-010-03 | Write sprint-inventory.json | CHILD | TODO | TC-SRB-010 |
| TC-SRB-011 | Detect sprint anomalies | PARENT | PROPOSED | — |
| TC-SRB-012 | Fix stale/orphan locks | PARENT | PROPOSED | — |
| TC-SRB-013 | Establish sprint identity contract | PARENT | PROPOSED | — |
| TC-SRB-020 | Implement sprint_number_allocator.py | PARENT | PROPOSED | — |
| TC-SRB-020-01 | Create ledger schema + empty ledger | CHILD | TODO | TC-SRB-020 |
| TC-SRB-020-02 | Implement load_ledger + find_highest | CHILD | TODO | TC-SRB-020 |
| TC-SRB-020-03 | Implement allocate subcommand | CHILD | TODO | TC-SRB-020 |
| TC-SRB-020-04 | Implement recover subcommand | CHILD | TODO | TC-SRB-020 |
| TC-SRB-020-05 | Implement status + list subcommands | CHILD | TODO | TC-SRB-020 |
| TC-SRB-021 | Register allocator as skill | PARENT | PROPOSED | — |
| TC-SRB-022 | Test allocator idempotency | PARENT | PROPOSED | — |
| TC-SRB-022-01 | Test same alias → same number | CHILD | TODO | TC-SRB-022 |
| TC-SRB-022-02 | Test different alias → next number | CHILD | TODO | TC-SRB-022 |
| TC-SRB-022-03 | Verify ledger entry count | CHILD | TODO | TC-SRB-022 |
| TC-SRB-022-04 | Verify no stale lock file remains | CHILD | TODO | TC-SRB-022 |
| TC-SRB-023 | Concurrent allocation safety pilot | PARENT | PROPOSED | — |
| TC-SRB-024 | Interrupted allocation recovery | PARENT | PROPOSED | — |
| TC-SRB-030 | Reproduce AUTONOMOUS_CONTINUE:NO | PARENT | PROPOSED | — |
| TC-SRB-031 | Add continuation_reason_codes field | PARENT | PROPOSED | — |
| TC-SRB-031-01 | Read autonomous_cycle.py signal writer | CHILD | TODO | TC-SRB-031 |
| TC-SRB-031-02 | Add continuation_reason_codes field | CHILD | TODO | TC-SRB-031 |
| TC-SRB-031-03 | Test field appears after autonomous-cycle | CHILD | TODO | TC-SRB-031 |
| TC-SRB-032 | Governance recovery pilot | PARENT | PROPOSED | — |
| TC-SRB-040 | Add production section to master-plan.md | PARENT | PROPOSED | — |
| TC-SRB-P01 | Pilot 1: Sprint monotonicity | PARENT | PROPOSED | — |
| TC-SRB-P02 | Pilot 2: Concurrent allocation | PARENT | PROPOSED | — |
| TC-SRB-P03 | Pilot 3: Interrupted recovery | PARENT | PROPOSED | — |
| TC-SRB-P04 | Pilot 4: Governance repair | PARENT | PROPOSED | — |
| TC-SRB-P05 | Pilot 5: Missing skill handling | PARENT | PROPOSED | — |
| TC-SRB-P06 | Pilot 6: Product deepening | PARENT | PROPOSED | — |
| TC-SRB-P07 | Pilot 7: Shared machinery regression | PARENT | PROPOSED | — |
| TC-SRB-P08 | Pilot 8: 3 consecutive autonomous sprints | PARENT | PROPOSED | — |
| TC-SRB-P09 | Pilot 9: Gate 11 simulated stop | PARENT | PROPOSED | — |
| TC-SRB-P10 | Pilot 10: No-change idempotency | PARENT | PROPOSED | — |
| TC-SRB-070 | Product deepening sprint 1 | PARENT | PROPOSED | — |
| TC-SRB-071 | Product deepening sprint 2 | PARENT | PROPOSED | — |
| TC-SRB-090 | Production readiness audit | PARENT | PROPOSED | — |

---

## PART G — MACHINE STATE DEFINITIONS
### (Deliverables: taskcard-state-machine, taskcard-state-machine-validation-rules)

### G.1 Parent Taskcard State Machine

```
PROPOSED → READY (when all dependencies are CLOSED)
READY → IN_PROGRESS (when execution starts)
IN_PROGRESS → CHILDREN_IN_PROGRESS (when child taskcards created and started)
CHILDREN_IN_PROGRESS → INTEGRATION_PENDING (when all mandatory children CLOSED)
INTEGRATION_PENDING → VERIFIED (when parent integration checks pass)
VERIFIED → SCORED (when quality dimensions scored)
SCORED → CLOSED (when all dimensions >= 4/5)
SCORED → REROUTED (when any dimension < 4/5)
REROUTED → IN_PROGRESS (after repair)
any → BLOCKED (when external dependency blocks)
BLOCKED → READY (after unblock)
any → BLOCKED_EXTERNAL (when TRUE_EXTERNAL_GATE encountered)
any → DEFERRED_WITH_REASON (when deprioritized with documentation)
```

### G.2 Child Taskcard State Machine

```
TODO → READY (dependencies met)
READY → IN_PROGRESS
IN_PROGRESS → IMPLEMENTED (implementation complete, not yet tested)
IMPLEMENTED → VERIFIED (tests and checks pass)
VERIFIED → SCORED
SCORED → CLOSED (all quality gates pass)
SCORED → REROUTED (any gate fails)
REROUTED → IN_PROGRESS
any → BLOCKED
BLOCKED → READY
```

### G.3 Micro-Step State Machine

```
PENDING → READY
READY → ACTIVE
ACTIVE → COMPLETE
ACTIVE → FAILED
FAILED → READY (retry)
ACTIVE → BLOCKED
BLOCKED → READY
PENDING → SKIPPED_NOT_APPLICABLE (with documented reason)
```

### G.4 Invalid Transitions (must be blocked)

```
- TODO → CLOSED (must pass READY → IN_PROGRESS → IMPLEMENTED → VERIFIED → SCORED)
- READY → CLOSED (no direct close)
- IMPLEMENTED → CLOSED (must verify first)
- Child CLOSED while mandatory micro-steps are PENDING
- Parent CLOSED while mandatory children are not CLOSED
- REROUTED → CLOSED (must pass through IN_PROGRESS again)
- BLOCKED_EXTERNAL → CLOSED (must have documented unblock evidence)
```

---

## PART H — PHASE -1: REWORK RESOLUTION (NEW — MUST RUN BEFORE PHASE 0)

**CLAUDE.md rule:** "If `rework_items` exist in the output, address them FIRST before new work"
**Rationale:** Two rework items exist from PQ-BUNDLE-FORENSICS-REPAIR-001. These must be resolved first.

---

### TC-SRB-RW1 — Resolve PQ-029-ADDRECORD: AddRecord() for NdjsonDocument (.NET)

```yaml
taskcard_id: TC-SRB-RW1
title: "Resolve PQ-029-ADDRECORD: AddRecord() for NdjsonDocument (.NET)"
type: PARENT
status: PROPOSED
requirement_id: REQ-SRB-001
source_section: S-P-MINUS1
root_cause: "Evidence accepted as path-only; AddRecord() method not verified to exist in NdjsonDocument.cs"
objective: "Verify or implement AddRecord() and produce proof-positive evidence"

scope:
  allowed_files:
    - src/net/ndjson/NdjsonDocument.cs
    - tests/net/ndjson/NdjsonAddRecordRoundtripTests.cs
  forbidden_files:
    - src/python/ (Python changes not in scope)
    - any other .cs files unless directly required

dependencies: none (runs first)

child_taskcards:
  - TC-SRB-RW1-01
  - TC-SRB-RW1-02
  - TC-SRB-RW1-03

parent_acceptance_criteria:
  - AddRecord() method exists in NdjsonDocument.cs with implementation (not stub)
  - NdjsonAddRecordRoundtripTests.cs runs and passes
  - evidence declaration declared with execution_method != MANUAL_UNGOVERNED
  - autonomous-cycle grades item ACCEPTED (not ACCEPTED_WITH_LIMITATIONS)

rollback: If AddRecord() doesn't exist and cannot be implemented in this sprint → defer with DEFERRED_WITH_REASON status and document exact implementation gap.
```

#### TC-SRB-RW1-01 — Verify AddRecord() in NdjsonDocument.cs

```yaml
child_taskcard_id: TC-SRB-RW1-01
parent_taskcard_id: TC-SRB-RW1
title: "Inspect NdjsonDocument.cs for AddRecord() method"
type: CHILD
status: TODO

micro_steps:
  - MS-RW1-01-01:
      action: "Read src/net/ndjson/NdjsonDocument.cs in full"
      expected_output: "Content of file; note if AddRecord() method exists"
      allowed_operation: inspect
      completion_check: "Can confirm presence or absence of AddRecord() method"

  - MS-RW1-01-02:
      action: "If AddRecord() exists: confirm it has a real implementation (not just a stub/throw NotImplementedException)"
      expected_output: "Method body inspection result"
      allowed_operation: inspect
      completion_check: "Method body identified as real or stub"

  - MS-RW1-01-03:
      action: "Record finding in analysis note: AddRecord_exists: true/false, is_stub: true/false"
      expected_output: "Finding documented"
      allowed_operation: record

preconditions: none
acceptance_checks:
  - Inspection complete, finding recorded
next_valid_task:
  - If AddRecord() exists and is real: TC-SRB-RW1-03 (skip implementation)
  - If AddRecord() missing or stub: TC-SRB-RW1-02
```

#### TC-SRB-RW1-02 — Implement AddRecord() in NdjsonDocument.cs (conditional)

```yaml
child_taskcard_id: TC-SRB-RW1-02
parent_taskcard_id: TC-SRB-RW1
title: "Implement AddRecord() in NdjsonDocument.cs if missing or stub"
type: CHILD
status: TODO
preconditions:
  - TC-SRB-RW1-01 completed
  - Finding: AddRecord() missing or is a stub

micro_steps:
  - MS-RW1-02-01:
      action: "Read existing NdjsonDocument.cs mutation methods (e.g., AppendRow, AddRow) to understand the pattern"
      expected_output: "Pattern identified for consistent implementation"
      allowed_operation: inspect

  - MS-RW1-02-02:
      action: "Add AddRecord(object record) method to NdjsonDocument.cs following the existing mutation pattern"
      expected_output: "Method implemented and compiles"
      allowed_operation: edit
      target_file: src/net/ndjson/NdjsonDocument.cs

  - MS-RW1-02-03:
      action: "Add entry to reports/r90/product-code-change-ledger.json for this edit"
      expected_output: "Ledger entry added"
      allowed_operation: edit
      target_file: reports/r90/product-code-change-ledger.json

acceptance_checks:
  - AddRecord() method exists with non-stub implementation
  - Product code ledger entry added
note: "SKIP if TC-SRB-RW1-01 found AddRecord() already real"
```

#### TC-SRB-RW1-03 — Write test and declare evidence for PQ-029-ADDRECORD

```yaml
child_taskcard_id: TC-SRB-RW1-03
parent_taskcard_id: TC-SRB-RW1
title: "Verify AddRecord test passes and declare resolution evidence"
type: CHILD
status: TODO
preconditions:
  - TC-SRB-RW1-01 and TC-SRB-RW1-02 completed

micro_steps:
  - MS-RW1-03-01:
      action: "Read tests/net/ndjson/NdjsonAddRecordRoundtripTests.cs to confirm test exists and targets AddRecord()"
      expected_output: "Test file content; verify test calls AddRecord()"
      allowed_operation: inspect

  - MS-RW1-03-02:
      action: "Run: .venv/Scripts/pytest tests/ -k ndjson -v (or dotnet test for .NET)"
      expected_output: "All ndjson tests pass including AddRecord roundtrip test"
      allowed_operation: run
      failure_handling: "If tests fail: fix implementation in NdjsonDocument.cs and rerun"

  - MS-RW1-03-03:
      action: "Write evidence at .local/evidences/srb-rw1/ndjson-addrecord-proof.txt with test output"
      expected_output: "Evidence file written with passing test output"
      allowed_operation: create

  - MS-RW1-03-04:
      action: "Declare this as resolved in the evidence declaration for the next autonomous-cycle run"
      expected_output: "evidence-declaration.yaml includes PQ-029-ADDRECORD as resolved with execution_method: SKILL_GENERATED or GOVERNED_DIRECT"
      allowed_operation: record

acceptance_checks:
  - Tests pass (not path-only evidence)
  - Evidence file exists at .local/evidences/srb-rw1/
  - execution_method != MANUAL_UNGOVERNED in declaration
```

---

### TC-SRB-RW2 — Resolve PQ-019-020-CLI-STUBS: CLI + Type Stubs for 20 Python Packages

```yaml
taskcard_id: TC-SRB-RW2
title: "Resolve PQ-019-020-CLI-STUBS: CLI entry points and type stubs for all 20 packages"
type: PARENT
status: PROPOSED
requirement_id: REQ-SRB-002
root_cause: "Only fods and fodt covered; 18 packages (abw, ods, odt, csv, tsv, dif, gnumeric, ndjson, toml, sylk, pbm, pgm, ppm, qoi, xcf, zst, fodg, fodp) missing CLI+stubs"

dependencies: none (parallel with TC-SRB-RW1 — different files)

child_taskcards:
  - TC-SRB-RW2-01
  - TC-SRB-RW2-02
  - TC-SRB-RW2-03
  - TC-SRB-RW2-04

parent_acceptance_criteria:
  - All 20 packages have cli.py entry point
  - All 20 packages have __init__.pyi type stub with __all__ defined
  - Tests pass for CLI invocation on at least 5 formats
  - autonomous-cycle grades item ACCEPTED
```

#### TC-SRB-RW2-01 — Audit 18 missing packages

```yaml
child_taskcard_id: TC-SRB-RW2-01
title: "Audit which of 18 packages have partial vs complete CLI+stubs"
type: CHILD
status: TODO

micro_steps:
  - MS-RW2-01-01:
      action: "For each of the 18 packages, check if src/python/{package}/cli.py exists"
      packages: [abw, ods, odt, csv, tsv, dif, gnumeric, ndjson, toml, sylk, pbm, pgm, ppm, qoi, xcf, zst, fodg, fodp]
      allowed_operation: inspect
      expected_output: "List of packages with/without cli.py"

  - MS-RW2-01-02:
      action: "For each of the 18 packages, check if src/python/{package}/__init__.pyi exists"
      allowed_operation: inspect
      expected_output: "List of packages with/without __init__.pyi"

  - MS-RW2-01-03:
      action: "Read existing fods/cli.py and fods/__init__.pyi as reference patterns"
      allowed_operation: inspect
      expected_output: "Template pattern documented"

  - MS-RW2-01-04:
      action: "Record audit results in .local/evidences/srb-rw2/cli-stub-audit.json"
      expected_output: "Audit JSON with per-package status"
      allowed_operation: create

acceptance_checks:
  - Audit complete for all 18 packages
  - Reference patterns documented
```

#### TC-SRB-RW2-02 — Implement CLI entry points for 18 missing packages

```yaml
child_taskcard_id: TC-SRB-RW2-02
title: "Create cli.py for each of 18 missing packages"
type: CHILD
status: TODO
preconditions: TC-SRB-RW2-01 completed

micro_steps:
  - MS-RW2-02-01:
      action: "For each package without cli.py: create src/python/{package}/cli.py following fods/cli.py template"
      scope: "One file per package — create sequentially if needed, or batch if pattern is identical"
      allowed_operation: create (18 files)
      target_pattern: src/python/{pkg}/cli.py for each missing package
      constraint: "Must add ledger entry in reports/r90/product-code-change-ledger.json for each file"

  - MS-RW2-02-02:
      action: "Add batch ledger entry covering all 18 cli.py creations"
      target_file: reports/r90/product-code-change-ledger.json
      allowed_operation: edit

acceptance_checks:
  - All 18 cli.py files exist
  - Ledger entry exists for the batch
```

#### TC-SRB-RW2-03 — Implement type stubs for 18 missing packages

```yaml
child_taskcard_id: TC-SRB-RW2-03
title: "Create __init__.pyi for each of 18 missing packages"
type: CHILD
status: TODO
preconditions: TC-SRB-RW2-01 completed

micro_steps:
  - MS-RW2-03-01:
      action: "For each package without __init__.pyi: create src/python/{package}/__init__.pyi following fods/__init__.pyi template"
      constraint: "Must include __all__ variable with exported symbols"
      allowed_operation: create (18 files)

  - MS-RW2-03-02:
      action: "Verify each __init__.pyi includes __all__ definition"
      allowed_operation: inspect
      expected_output: "All 18 files have __all__"

acceptance_checks:
  - All 18 __init__.pyi files exist with __all__ defined
```

#### TC-SRB-RW2-04 — Test CLI invocation and declare evidence

```yaml
child_taskcard_id: TC-SRB-RW2-04
title: "Test CLI entry points work and declare resolution evidence"
type: CHILD
status: TODO
preconditions: TC-SRB-RW2-02 and TC-SRB-RW2-03 completed

micro_steps:
  - MS-RW2-04-01:
      action: "Run: python -m {package} --help for at least 5 formats (fods, fodt, abw, csv, ods)"
      expected_output: "Help text displayed without import errors"
      allowed_operation: run

  - MS-RW2-04-02:
      action: "Run existing pytest tests for CLI where available"
      expected_output: "0 test failures"
      allowed_operation: run

  - MS-RW2-04-03:
      action: "Capture test output to .local/evidences/srb-rw2/cli-test-output.txt"
      allowed_operation: create

  - MS-RW2-04-04:
      action: "Declare PQ-019-020-CLI-STUBS as resolved in next evidence declaration"
      expected_output: "Declaration entry with all_packages_covered: true"
      allowed_operation: record

acceptance_checks:
  - 5+ formats tested successfully
  - Test output captured
  - Evidence declared
```

---

## PART I — PHASE 0: SESSION BOOTSTRAP

### TC-SRB-000 — Copy plan to repo and write plan lock

```yaml
taskcard_id: TC-SRB-000
title: "Copy plan file to repo and write IN_PROGRESS plan lock"
type: PARENT
status: PROPOSED
requirement_id: REQ-SRB-003
dependencies: [TC-SRB-RW1, TC-SRB-RW2] (rework items resolved first)

scope:
  allowed_files:
    - plans/.claude/splendid-roaming-beaver.md (target of copy)
    - .local/supervisor/active-plan-lock.json (written by write_plan_lock.py)
    - .local/supervisor/plan-locks/<session_id>-*.json (written by write_plan_lock.py)
  forbidden_files:
    - src/ (no product mutations during bootstrap)

child_taskcards: [TC-SRB-000-01, TC-SRB-000-02]

parent_acceptance_criteria:
  - plans/.claude/splendid-roaming-beaver.md exists and matches source
  - active-plan-lock.json has status=IN_PROGRESS and correct plan_path
```

#### TC-SRB-000-01 — Copy plan file

```yaml
child_taskcard_id: TC-SRB-000-01
parent_taskcard_id: TC-SRB-000
title: "Copy plan from external location to in-repo plans/.claude/"
type: CHILD
status: TODO

micro_steps:
  - MS-000-01-01:
      action: "Verify plans/.claude/ directory exists"
      command: "ls plans/.claude/"
      expected_output: "Directory exists"
      allowed_operation: inspect

  - MS-000-01-02:
      action: "Copy: cp 'C:/Users/prora/.claude/plans/splendid-roaming-beaver.md' plans/.claude/splendid-roaming-beaver.md"
      expected_output: "File copied successfully"
      allowed_operation: create (copy)
      failure_handling: "If directory missing: mkdir -p plans/.claude/ then retry"

  - MS-000-01-03:
      action: "Verify plans/.claude/splendid-roaming-beaver.md is not empty and matches source (check line count)"
      expected_output: "File size matches original"
      allowed_operation: inspect

acceptance_checks:
  - plans/.claude/splendid-roaming-beaver.md exists
  - Content is not empty
next_valid_task: TC-SRB-000-02
```

#### TC-SRB-000-02 — Write plan lock

```yaml
child_taskcard_id: TC-SRB-000-02
parent_taskcard_id: TC-SRB-000
title: "Write IN_PROGRESS plan lock for splendid-roaming-beaver"
type: CHILD
status: TODO
preconditions: [TC-SRB-000-01 CLOSED]

micro_steps:
  - MS-000-02-01:
      action: "Run: python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/splendid-roaming-beaver.md"
      expected_output: "Exit code 0; lock written"
      allowed_operation: run

  - MS-000-02-02:
      action: "Read .local/supervisor/active-plan-lock.json and verify status=IN_PROGRESS and plan_path contains splendid-roaming-beaver"
      expected_output: "Lock file has correct values"
      allowed_operation: inspect
      failure_handling: "If lock shows wrong values: re-run write_plan_lock.py"

  - MS-000-02-03:
      action: "From this point: all taskcard status updates go to plans/.claude/splendid-roaming-beaver.md ONLY (not the external file)"
      expected_output: "Mental note for execution agent"
      allowed_operation: record

acceptance_checks:
  - active-plan-lock.json has status=IN_PROGRESS
  - plan_path in lock file matches plans/.claude/splendid-roaming-beaver.md
next_valid_task: TC-SRB-001
```

---

### TC-SRB-001 — Run check_continuation.py to assess current state

```yaml
taskcard_id: TC-SRB-001
title: "Run check_continuation.py and resolve any STOP conditions"
type: PARENT
status: PROPOSED
requirement_id: REQ-SRB-004
dependencies: [TC-SRB-000]

child_taskcards: [TC-SRB-001-01, TC-SRB-001-02]

parent_acceptance_criteria:
  - check_continuation.py returns verdict=CONTINUE
  - Verdict JSON documented in evidence
```

#### TC-SRB-001-01 — Run check_continuation.py

```yaml
child_taskcard_id: TC-SRB-001-01
parent_taskcard_id: TC-SRB-001
title: "Execute check_continuation.py and capture output"
type: CHILD
status: TODO

micro_steps:
  - MS-001-01-01:
      action: "Run: python tools/supervisor/check_continuation.py"
      expected_output: "JSON output to stdout with verdict field"
      allowed_operation: run

  - MS-001-01-02:
      action: "Parse JSON output. Record: verdict, reason (if any), iteration, max_iterations"
      expected_output: "Values documented"
      allowed_operation: record

  - MS-001-01-03:
      action: "If verdict=CONTINUE: proceed to TC-SRB-001-02 (skip) then TC-SRB-002"
      action_if_stop: "If verdict=STOP: proceed to TC-SRB-001-02 to fix"
      allowed_operation: decision

acceptance_checks:
  - Output captured and parsed
```

#### TC-SRB-001-02 — Fix STOP condition (conditional)

```yaml
child_taskcard_id: TC-SRB-001-02
parent_taskcard_id: TC-SRB-001
title: "Fix STOP condition from check_continuation.py (if applicable)"
type: CHILD
status: TODO
note: "SKIP if TC-SRB-001-01 returned CONTINUE"

micro_steps:
  - MS-001-02-01:
      action: "Read the reason field from check_continuation output"
      expected_output: "Reason code identified"
      decision_tree:
        POST_PLAN_TERMINAL:
          action: "The TERMINAL_CLOSED lock (session 033f6a1ae2f3) from vast-weaving-lampson is a different session. It should be filtered by session_id check. If it still blocks, run: python -c \"import json; from pathlib import Path; p=Path('.local/supervisor/active-plan-lock.json'); d=json.loads(p.read_text()); d['status']='SUPERSEDED'; p.write_text(json.dumps(d,indent=2))\""
        SESSION_MISMATCH:
          action: "Run: python tools/supervisor/reset_track_signal.py --track product"
        MAX_ITERATIONS:
          action: "Reset iteration to 0 in continuation-signal.json. This is NOT a stop condition."
        ACTIVE_PLAN_INCOMPLETE:
          action: "This is expected AFTER TC-SRB-000-02 writes the new IN_PROGRESS lock. check_continuation now correctly blocks until ALL taskcards in this plan are CLOSED. Continue executing this plan's taskcards — the plan lock IS the authority."

  - MS-001-02-02:
      action: "Re-run check_continuation.py after fix. For ACTIVE_PLAN_INCOMPLETE: this is correct behavior when a plan is active — it means continue executing plan taskcards, not that continuation is broken."
      note: "ACTIVE_PLAN_INCOMPLETE is the EXPECTED verdict once TC-SRB-000-02 writes the lock. The execution agent should proceed to TC-SRB-002 regardless of this verdict since the plan IS the authority."

acceptance_checks:
  - Either CONTINUE returned OR ACTIVE_PLAN_INCOMPLETE (expected for active plan)
next_valid_task: TC-SRB-002
```

---

### TC-SRB-002 — Capture state baseline

```yaml
taskcard_id: TC-SRB-002
title: "Capture full state baseline before sprint work"
type: PARENT
status: PROPOSED
requirement_id: REQ-SRB-004
dependencies: [TC-SRB-001]

micro_steps:
  - MS-002-01:
      action: "Read reports/supervisor/approval-gates.md — record AUTONOMOUS_CONTINUE value"
      expected_output: "AUTONOMOUS_CONTINUE: YES (expected)"

  - MS-002-02:
      action: "Read reports/supervisor/contradictions.json — record critical_count"
      expected_output: "critical_count: 0 (expected)"

  - MS-002-03:
      action: "Read .local/supervisor/continuation-signal.json — record iteration, source_sprint_id, rework_items"
      expected_output: "iteration=5, rework_items=[PQ-029-ADDRECORD, PQ-019-020-CLI-STUBS] (expected; rework should be resolved by Phase -1)"

  - MS-002-04:
      action: "Count items in .local/supervisor/next-work-items.json (use wc -l or parse JSON)"
      expected_output: "Work queue depth recorded (expected: >100 items)"

  - MS-002-05:
      action: "Write baseline to .local/evidences/srb-baseline/baseline.json"
      expected_output: "Baseline JSON written with all above values"

acceptance_checks:
  - Baseline file exists at .local/evidences/srb-baseline/baseline.json
  - All 5 values recorded
```

---

## PART J — PHASE 1: SPRINT FORENSIC INVENTORY

### TC-SRB-010 — Build canonical sprint inventory

```yaml
taskcard_id: TC-SRB-010
title: "Build canonical sprint inventory from all sources"
type: PARENT
status: PROPOSED
requirement_id: REQ-SRB-005
dependencies: [TC-SRB-002]

context:
  known_sprint_count: 840 (from maturity-trend.json)
  plan_lock_files: ~100+ in .local/supervisor/plan-locks/
  evidence_bundles: in .local/supervisor/reviews/

scope_limit: "Do NOT load all 840 sprint records. Build a representative sample of the 20 most recent plan locks + maturity-trend.json summary."
```

#### TC-SRB-010-01 — Enumerate plan-locks

```yaml
child_taskcard_id: TC-SRB-010-01
parent_taskcard_id: TC-SRB-010
title: "List and parse all plan-lock JSON files"
type: CHILD
status: TODO

micro_steps:
  - MS-010-01-01:
      action: "List all files in .local/supervisor/plan-locks/ and count them"
      command: "ls .local/supervisor/plan-locks/*.json | wc -l"
      expected_output: "Count of lock files"

  - MS-010-01-02:
      action: "For each lock file: extract plan_path, status, session_id, updated_at (parse JSON)"
      scope: "Process all lock files in a single Python script"
      command: |
        python -c "
        import json, glob, sys
        from pathlib import Path
        records = []
        for f in sorted(glob.glob('.local/supervisor/plan-locks/*.json')):
            try:
                d = json.loads(Path(f).read_text())
                records.append({'file': f, 'status': d.get('status'), 'plan_path': d.get('plan_path'), 'session_id': d.get('session_id'), 'updated_at': d.get('updated_at')})
            except Exception as e:
                records.append({'file': f, 'error': str(e)})
        print(json.dumps(records, indent=2))
        "
      expected_output: "JSON array of lock records"

  - MS-010-01-03:
      action: "Write extracted records to .local/supervisor/sprint-inventory-locks.json"
      expected_output: "File written"

acceptance_checks:
  - sprint-inventory-locks.json exists and is valid JSON
  - Count matches actual file count
```

#### TC-SRB-010-02 — Enumerate evidence bundles

```yaml
child_taskcard_id: TC-SRB-010-02
parent_taskcard_id: TC-SRB-010
title: "List evidence bundle directories"
type: CHILD
status: TODO

micro_steps:
  - MS-010-02-01:
      action: "List subdirectories in .local/supervisor/reviews/"
      command: "ls -la .local/supervisor/reviews/"
      expected_output: "List of evidence bundle dirs"

  - MS-010-02-02:
      action: "For each bundle dir, read its evidence-review.json or grade-cache.json if present"
      expected_output: "Dict of bundle_id → verdict"

  - MS-010-02-03:
      action: "Write to .local/supervisor/sprint-inventory-bundles.json"
      expected_output: "File written"

acceptance_checks:
  - sprint-inventory-bundles.json exists
```

#### TC-SRB-010-03 — Write sprint-inventory.json

```yaml
child_taskcard_id: TC-SRB-010-03
parent_taskcard_id: TC-SRB-010
title: "Merge all sources into sprint-inventory.json"
type: CHILD
status: TODO
preconditions: [TC-SRB-010-01, TC-SRB-010-02]

micro_steps:
  - MS-010-03-01:
      action: "Read maturity-trend.json for total sprint count"
      expected_output: "total_sprints=840"

  - MS-010-03-02:
      action: "Merge lock records and bundle records into unified sprint-inventory.json"
      format: |
        {
          "generated_at": "<timestamp>",
          "total_sprints_historical": 840,
          "lock_files_found": N,
          "evidence_bundles_found": M,
          "most_recent_sprint_id": "PQ-BUNDLE-FORENSICS-REPAIR-001",
          "lock_records": [...],
          "bundle_records": [...],
          "anomalies": []
        }
      expected_output: "sprint-inventory.json written at .local/supervisor/sprint-inventory.json"

acceptance_checks:
  - sprint-inventory.json valid JSON
  - total_sprints_historical matches maturity-trend.json
```

---

### TC-SRB-011 — Detect sprint anomalies

```yaml
taskcard_id: TC-SRB-011
title: "Detect anomalies in sprint records"
type: PARENT
status: PROPOSED
dependencies: [TC-SRB-010]

micro_steps:
  - MS-011-01:
      action: "From sprint-inventory-locks.json: find all IN_PROGRESS entries"
      expected_output: "List of IN_PROGRESS locks"

  - MS-011-02:
      action: "For each IN_PROGRESS lock: check if updated_at > 7 days ago (stale) AND session_id != current session"
      expected_output: "Stale lock list"

  - MS-011-03:
      action: "For each lock: check if plan_path file exists (orphan check)"
      expected_output: "Orphan lock list"

  - MS-011-04:
      action: "Write sprint-anomaly-register.json"
      format: |
        {
          "generated_at": "<ts>",
          "stale_locks": [...],
          "orphan_locks": [...],
          "active_in_progress_count": 0,
          "anomaly_count": 0
        }

acceptance_checks:
  - sprint-anomaly-register.json written
```

---

### TC-SRB-012 — Fix stale and orphan locks

```yaml
taskcard_id: TC-SRB-012
title: "Supersede stale/orphan plan locks"
type: PARENT
status: PROPOSED
dependencies: [TC-SRB-011]

micro_steps:
  - MS-012-01:
      action: "For each lock in stale_locks and orphan_locks from anomaly register: write status=SUPERSEDED"
      command: |
        python -c "
        import json
        from pathlib import Path
        anomaly = json.loads(Path('.local/supervisor/sprint-anomaly-register.json').read_text())
        for lock_path in anomaly.get('stale_locks', []) + anomaly.get('orphan_locks', []):
            p = Path(lock_path)
            if p.exists():
                d = json.loads(p.read_text())
                d['status'] = 'SUPERSEDED'
                p.write_text(json.dumps(d, indent=2))
                print(f'SUPERSEDED: {lock_path}')
        "
      constraint: "NEVER delete lock files — only change status to SUPERSEDED"

  - MS-012-02:
      action: "Re-run check_continuation.py and verify no STALE_LOCK or ORPHAN errors remain"
      expected_output: "No lock-related STOP reasons"

acceptance_checks:
  - No stale/orphan IN_PROGRESS locks remain
  - check_continuation.py does not return lock-related STOP
```

---

### TC-SRB-013 — Establish sprint identity contract

```yaml
taskcard_id: TC-SRB-013
title: "Create sprint identity contract and bootstrap sprint ledger"
type: PARENT
status: PROPOSED
dependencies: [TC-SRB-012]

micro_steps:
  - MS-013-01:
      action: "Write .local/supervisor/sprint-identity-contract.json"
      content: |
        {
          "policy_id": "FORMAT_FACTORY_SPRINT_IDENTITY_V1",
          "number_type": "positive_integer",
          "ordering": "strictly_monotonic",
          "uniqueness_scope": "repository",
          "allocation_mode": "atomic_os_replace",
          "lock_algorithm": "os.replace() with .tmp suffix",
          "reuse_allowed": false,
          "identity_format": "SPRINT-{number:05d}",
          "semantic_alias_format": "{adjective}-{verb}-{noun}",
          "authoritative_ledger": ".local/supervisor/sprint-ledger.json",
          "allocation_script": "python tools/supervisor/sprint_number_allocator.py allocate",
          "note": "840 historical sprints existed before this ledger was created. Bootstrap starts at SPRINT-00841."
        }

  - MS-013-02:
      action: "Create bootstrap sprint-ledger.json with starting number based on maturity-trend.json"
      content: |
        {
          "schema_version": "1.0",
          "created_at": "<timestamp>",
          "bootstrap_note": "Historical sprints before this ledger: 840 (from maturity-trend.json). New allocations start at 841.",
          "highest_allocated_number": 840,
          "entries": []
        }
      target: .local/supervisor/sprint-ledger.json

  - MS-013-03:
      action: "Verify sprint-ledger.json is valid JSON and highest_allocated_number = 840"
      expected_output: "File readable, value correct"

acceptance_checks:
  - sprint-identity-contract.json exists
  - sprint-ledger.json exists with highest_allocated_number: 840
  - No entries yet (new allocations start fresh)
```

---

## PART K — PHASE 2: ATOMIC SPRINT NUMBER ALLOCATOR

### TC-SRB-020 — Implement sprint_number_allocator.py

```yaml
taskcard_id: TC-SRB-020
title: "Create tools/supervisor/sprint_number_allocator.py"
type: PARENT
status: PROPOSED
requirement_id: REQ-SRB-008
dependencies: [TC-SRB-013]

design_notes:
  file_locking: "Use os.replace() atomic write (same as write_plan_lock.py). No fcntl on Windows."
  lock_file: ".local/supervisor/sprint-allocation.lock.json"
  algorithm: |
    1. Load sprint-ledger.json
    2. Find highest allocated_number where status != 'abandoned'
    3. Check idempotency: if semantic_alias already in entries → return existing
    4. Write new entry to sprint-ledger.json.tmp with next number
    5. os.replace() sprint-ledger.json.tmp → sprint-ledger.json
    6. Write receipt to .local/supervisor/sprint-receipts/{sprint_id}.json
    7. Return receipt JSON to stdout

scope:
  allowed_files:
    - tools/supervisor/sprint_number_allocator.py (create)
    - .local/supervisor/sprint-ledger.json (modify via allocator)
    - .local/supervisor/sprint-receipts/ (create receipts)
  forbidden_files:
    - tools/supervisor/check_continuation.py (do not modify)
    - tests/ (test file creation is a separate child TC)
```

#### TC-SRB-020-01 — Create sprint-ledger.json schema and directory

```yaml
child_taskcard_id: TC-SRB-020-01
title: "Verify sprint-ledger.json and sprint-receipts/ directory exist"
type: CHILD
status: TODO
preconditions: [TC-SRB-013 CLOSED]

micro_steps:
  - MS-020-01-01:
      action: "Verify .local/supervisor/sprint-ledger.json exists (created in TC-SRB-013)"
      expected_output: "File exists with highest_allocated_number: 840"

  - MS-020-01-02:
      action: "Create directory .local/supervisor/sprint-receipts/ if it doesn't exist"
      command: "mkdir -p .local/supervisor/sprint-receipts/"
      expected_output: "Directory exists"

acceptance_checks:
  - sprint-ledger.json valid
  - sprint-receipts/ directory exists
```

#### TC-SRB-020-02 — Implement load_ledger and find_highest functions

```yaml
child_taskcard_id: TC-SRB-020-02
title: "Implement core ledger read functions in sprint_number_allocator.py"
type: CHILD
status: TODO

micro_steps:
  - MS-020-02-01:
      action: "Create tools/supervisor/sprint_number_allocator.py with module docstring and imports"
      expected_output: "File exists with header, imports (json, os, uuid, datetime, sys, argparse, pathlib)"

  - MS-020-02-02:
      action: "Implement load_ledger(ledger_path: Path) -> dict"
      expected_output: "Function reads ledger JSON, returns dict with defaults if missing"

  - MS-020-02-03:
      action: "Implement find_highest_number(ledger: dict) -> int"
      expected_output: "Returns max(entry['sprint_number'] for entries where status != 'abandoned'), or ledger.get('highest_allocated_number', 0)"

  - MS-020-02-04:
      action: "Implement find_existing_allocation(ledger: dict, semantic_alias: str) -> dict | None"
      expected_output: "Returns existing entry if semantic_alias already allocated, else None (idempotency check)"

acceptance_checks:
  - File exists with all 3 functions
  - Functions have type hints and docstrings
```

#### TC-SRB-020-03 — Implement allocate subcommand

```yaml
child_taskcard_id: TC-SRB-020-03
title: "Implement the allocate subcommand (main allocation logic)"
type: CHILD
status: TODO
preconditions: [TC-SRB-020-02 CLOSED]

micro_steps:
  - MS-020-03-01:
      action: "Implement allocate_sprint_number(mission_id, semantic_alias, plan_id, ledger_path) -> dict"
      algorithm: |
        1. Load ledger
        2. existing = find_existing_allocation(ledger, semantic_alias)
        3. If existing: return receipt with verdict='ALREADY_ALLOCATED', same sprint_id
        4. highest = find_highest_number(ledger)
        5. new_number = highest + 1
        6. new_sprint_id = f'SPRINT-{new_number:05d}'
        7. new_entry = {sprint_number, sprint_id, semantic_alias, mission_id, plan_id, status='ALLOCATED', allocated_at, supervisor_id}
        8. ledger['entries'].append(new_entry)
        9. ledger['highest_allocated_number'] = new_number
        10. tmp_path = ledger_path.with_suffix('.tmp')
        11. tmp_path.write_text(json.dumps(ledger, indent=2))
        12. os.replace(str(tmp_path), str(ledger_path))  # atomic
        13. Write receipt to sprint-receipts/{sprint_id}.json
        14. return receipt dict

  - MS-020-03-02:
      action: "Add argparse subcommand 'allocate' to main() function"
      expected_output: "python sprint_number_allocator.py allocate --mission-id X --semantic-alias Y works"

  - MS-020-03-03:
      action: "Test manually: run allocate with mission_id=SRB-TEST semantic_alias=test-sprint-001"
      expected_output: "Receipt JSON printed; SPRINT-00841 allocated; ledger updated"
      failure_handling: "Fix bug and rerun until receipt is correct"

acceptance_checks:
  - allocate subcommand runs without error
  - Returns valid receipt JSON
  - sprint-ledger.json updated with new entry
  - sprint-receipts/SPRINT-00841.json created
```

#### TC-SRB-020-04 — Implement recover subcommand

```yaml
child_taskcard_id: TC-SRB-020-04
title: "Implement recover subcommand for interrupted allocation"
type: CHILD
status: TODO
preconditions: [TC-SRB-020-03 CLOSED]

micro_steps:
  - MS-020-04-01:
      action: "Implement recover(ledger_path) -> dict that finds entries with status='ALLOCATING' and sets them to 'ALLOCATED'"
      expected_output: "Function changes ALLOCATING → ALLOCATED; returns count of recovered"

  - MS-020-04-02:
      action: "Also check for .tmp file left from interrupted os.replace(): if sprint-ledger.json.tmp exists, complete the replace"
      expected_output: "Orphaned .tmp file merged"

  - MS-020-04-03:
      action: "Add 'recover' subcommand to argparse"
      expected_output: "python sprint_number_allocator.py recover works"

acceptance_checks:
  - recover subcommand runs
  - Converts ALLOCATING entries to ALLOCATED
  - Handles orphaned .tmp file
```

#### TC-SRB-020-05 — Implement status and list subcommands

```yaml
child_taskcard_id: TC-SRB-020-05
title: "Implement status and list subcommands"
type: CHILD
status: TODO
preconditions: [TC-SRB-020-03 CLOSED]

micro_steps:
  - MS-020-05-01:
      action: "Implement status() that prints: highest_allocated_number, total_entries, status distribution"
      expected_output: "Status summary JSON"

  - MS-020-05-02:
      action: "Implement list(n=10) that prints last N sprint entries in reverse chronological order"
      expected_output: "Last 10 entries printed"

  - MS-020-05-03:
      action: "Add 'status' and 'list' subcommands to argparse"
      expected_output: "Both subcommands work"

acceptance_checks:
  - status and list subcommands work
  - Output is valid JSON
```

---

### TC-SRB-021 — Register sprint_number_allocator as a governed skill

```yaml
taskcard_id: TC-SRB-021
title: "Add allocate-sprint-number to .supervisor/skill-registry.yaml"
type: PARENT
status: PROPOSED
requirement_id: REQ-SRB-009
dependencies: [TC-SRB-020]

micro_steps:
  - MS-021-01:
      action: "Read .supervisor/skill-registry.yaml to find correct insertion point (BEFORE top-level sprint: or version: keys)"
      expected_output: "Insertion point identified"

  - MS-021-02:
      action: "Add skill block for allocate-sprint-number following existing entry format"
      insertion: |
        - skill_id: allocate-sprint-number
          command: python tools/supervisor/sprint_number_allocator.py allocate
          description: "Atomically allocate the next unique sprint number from the canonical ledger"
          category: sprint_lifecycle
          status: active
          inputs:
            - name: mission_id
              required: true
            - name: semantic_alias
              required: false
            - name: plan_id
              required: false
          outputs:
            - name: sprint_id
            - name: allocated_number
            - name: receipt_path
      constraint: "Place skill block BEFORE any top-level keys (sprint:, version:)"

  - MS-021-03:
      action: "Verify skill-registry.yaml is valid YAML after edit"
      command: "python -c \"import yaml; yaml.safe_load(open('.supervisor/skill-registry.yaml').read()); print('VALID')\""
      expected_output: "VALID"

  - MS-021-04:
      action: "Run /inventory-skills or equivalent to confirm allocate-sprint-number appears"
      expected_output: "Skill listed"

acceptance_checks:
  - Skill entry in skill-registry.yaml
  - YAML valid after edit
  - Skill appears in inventory
```

---

### TC-SRB-022 — Test allocator idempotency

```yaml
taskcard_id: TC-SRB-022
title: "Prove allocator idempotency: same alias → same number, different alias → next number"
type: PARENT
status: PROPOSED
requirement_id: REQ-SRB-010
dependencies: [TC-SRB-021]
```

#### TC-SRB-022-01 — Test same alias → same number

```yaml
child_taskcard_id: TC-SRB-022-01
title: "Run allocate twice for same semantic alias; verify same sprint number returned"
type: CHILD
status: TODO

micro_steps:
  - MS-022-01-01:
      action: "Record current highest_allocated_number from sprint-ledger.json (call it H)"
      expected_output: "H = 840 + any previous test allocations"

  - MS-022-01-02:
      action: "Run: python tools/supervisor/sprint_number_allocator.py allocate --mission-id IDEMPOTENCY-TEST --semantic-alias idem-test-alpha"
      expected_output: "Receipt with allocated_number=H+1, sprint_id=SPRINT-0{H+1:04d}, verdict=ALLOCATED"
      record: "N1 = allocated_number"

  - MS-022-01-03:
      action: "Run same command again (same alias)"
      expected_output: "Receipt with verdict=ALREADY_ALLOCATED, same allocated_number=N1"

  - MS-022-01-04:
      action: "Verify sprint-ledger.json has exactly ONE entry for idem-test-alpha"
      command: "python -c \"import json; d=json.load(open('.local/supervisor/sprint-ledger.json')); print(sum(1 for e in d['entries'] if e.get('semantic_alias')=='idem-test-alpha'))\""
      expected_output: "1"

acceptance_checks:
  - Second run returns same number as first run
  - Ledger has exactly one entry for this alias
```

#### TC-SRB-022-02 — Test different alias → next number

```yaml
child_taskcard_id: TC-SRB-022-02
title: "Run allocate for different alias; verify next unique number"
type: CHILD
status: TODO
preconditions: [TC-SRB-022-01 CLOSED]

micro_steps:
  - MS-022-02-01:
      action: "Run: python tools/supervisor/sprint_number_allocator.py allocate --mission-id IDEMPOTENCY-TEST --semantic-alias idem-test-beta"
      expected_output: "allocated_number = N1+1, verdict=ALLOCATED"
      record: "N2 = allocated_number"

  - MS-022-02-02:
      action: "Verify N2 = N1 + 1"
      expected_output: "Strict monotonicity confirmed"

acceptance_checks:
  - N2 = N1 + 1
  - Two entries in ledger for the two aliases
```

#### TC-SRB-022-03 — Verify ledger entry count

```yaml
child_taskcard_id: TC-SRB-022-03
title: "Verify ledger has exactly 2 entries after 3 allocation calls"
type: CHILD
status: TODO
preconditions: [TC-SRB-022-02 CLOSED]

micro_steps:
  - MS-022-03-01:
      action: "Count entries in sprint-ledger.json added since TC-SRB-022 started"
      expected_output: "Exactly 2 new entries (idem-test-alpha, idem-test-beta) — not 3 despite 3 calls"

acceptance_checks:
  - Total new entries = 2 (idempotency proven)
```

#### TC-SRB-022-04 — Verify no stale lock file remains

```yaml
child_taskcard_id: TC-SRB-022-04
title: "Verify sprint-ledger.json.tmp does not exist after clean allocation"
type: CHILD
status: TODO

micro_steps:
  - MS-022-04-01:
      action: "Check: if .local/supervisor/sprint-ledger.json.tmp exists → FAIL (stale lock)"
      expected_output: "File does NOT exist (clean)"

acceptance_checks:
  - No .tmp file remains
  - Evidence written to .local/evidences/srb-pilot-02/idempotency-results.json
```

---

### TC-SRB-023 — Concurrent allocation safety pilot (Pilot 2)

```yaml
taskcard_id: TC-SRB-023
title: "Pilot 2: Prove two concurrent allocations get unique sprint numbers"
type: PARENT
status: PROPOSED
dependencies: [TC-SRB-022]

micro_steps:
  - MS-023-01:
      action: "Write Python test script: tests/supervisor/test_sprint_allocator_concurrent.py"
      content: |
        import threading, json
        from pathlib import Path
        import sys; sys.path.insert(0, 'tools/supervisor')
        from sprint_number_allocator import allocate_sprint_number

        LEDGER = Path('.local/supervisor/sprint-ledger.json')
        results = {}
        errors = {}

        def allocate_worker(alias):
            try:
                r = allocate_sprint_number('CONCURRENT-TEST', alias, None, LEDGER)
                results[alias] = r['allocated_number']
            except Exception as e:
                errors[alias] = str(e)

        t1 = threading.Thread(target=allocate_worker, args=('concurrent-alpha',))
        t2 = threading.Thread(target=allocate_worker, args=('concurrent-beta',))
        t1.start(); t2.start()
        t1.join(); t2.join()

        assert len(errors) == 0, f"Errors: {errors}"
        assert results['concurrent-alpha'] != results['concurrent-beta'], "DUPLICATE ALLOCATION"
        assert abs(results['concurrent-alpha'] - results['concurrent-beta']) == 1, "Not consecutive"
        print(json.dumps({'verdict': 'PASS', 'results': results}))

  - MS-023-02:
      action: "Run test 3 times consecutively"
      command: "for i in 1 2 3; do python tests/supervisor/test_sprint_allocator_concurrent.py; done"
      expected_output: "PASS all 3 times"

  - MS-023-03:
      action: "If any run fails (race condition): investigate and fix in TC-SRB-020-03 allocation logic"
      expected_output: "All 3 runs pass"

  - MS-023-04:
      action: "Write evidence to .local/evidences/srb-pilot-02/concurrent-test.json"
      expected_output: "Evidence file with pass verdict"

acceptance_checks:
  - 3 consecutive test runs pass
  - No duplicate sprint numbers in ledger
  - Evidence file written
```

---

### TC-SRB-024 — Interrupted allocation recovery pilot (Pilot 3)

```yaml
taskcard_id: TC-SRB-024
title: "Pilot 3: Prove recovery from interrupted allocation"
type: PARENT
status: PROPOSED
dependencies: [TC-SRB-023]

micro_steps:
  - MS-024-01:
      action: "Record current highest number H from sprint-ledger.json"

  - MS-024-02:
      action: "Manually inject an interrupted allocation: add entry with status='ALLOCATING' and sprint_number=H+1 and semantic_alias='recovery-test' to sprint-ledger.json"
      command: |
        python -c "
        import json, datetime
        from pathlib import Path
        p = Path('.local/supervisor/sprint-ledger.json')
        d = json.loads(p.read_text())
        d['entries'].append({'sprint_number': d['highest_allocated_number']+1, 'sprint_id': f'SPRINT-{d[\"highest_allocated_number\"]+1:05d}', 'semantic_alias': 'recovery-test', 'status': 'ALLOCATING', 'allocated_at': datetime.datetime.utcnow().isoformat()})
        p.write_text(json.dumps(d, indent=2))
        print('Injected ALLOCATING entry')
        "

  - MS-024-03:
      action: "Run: python tools/supervisor/sprint_number_allocator.py recover"
      expected_output: "1 entry recovered: status ALLOCATING → ALLOCATED"

  - MS-024-04:
      action: "Verify recovery-test entry now has status=ALLOCATED in sprint-ledger.json"

  - MS-024-05:
      action: "Run allocate for new alias 'post-recovery-sprint' → must get H+2, NOT re-use H+1"
      expected_output: "New sprint number is H+2 (recovery-test kept H+1)"

  - MS-024-06:
      action: "Write evidence to .local/evidences/srb-pilot-03/recovery-test.json"

acceptance_checks:
  - ALLOCATING → ALLOCATED conversion proven
  - Next allocation gets correct sequential number
  - Evidence written
```

---

## PART L — PHASE 3: GOVERNANCE VIOLATION INVESTIGATION

### TC-SRB-030 — Document all 7 CRITICAL contradiction triggers

```yaml
taskcard_id: TC-SRB-030
title: "Document all 7 CRITICAL triggers for AUTONOMOUS_CONTINUE:NO with reproduction steps"
type: PARENT
status: PROPOSED
requirement_id: REQ-SRB-011
dependencies: [TC-SRB-002]

context:
  source_file: tools/supervisor/compare_goal_to_evidence.py
  7_triggers_confirmed:
    1: "check_no_bundle() — verdict in [BLOCKED_NO_BUNDLE, BLOCKED_MALFORMED_ZIP]"
    2: "check_missing_final_verdict() — no final-verdict.md in bundle"
    3: "check_bundle_validation_fail() — bundle_validation_pass == False"
    4: "check_tests_failed() — fail_count > 0"
    5: "check_pending_markers() — PENDING tokens in final-verdict.md"
    6: "check_stale_sha() — SHA fields marked PENDING"
    7: "check_gate_overclaim() — Gate 11 appears self-approved"

micro_steps:
  - MS-030-01:
      action: "Create a test evidence declaration at .local/evidences/srb-gov-test/evidence-declaration.yaml with fail_count: 1"
      expected_output: "Test declaration written"

  - MS-030-02:
      action: "Run: python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/srb-gov-test/evidence-declaration.yaml"
      expected_output: "Exit code 3 (critical rework); AUTONOMOUS_CONTINUE: NO in approval-gates.md"

  - MS-030-03:
      action: "Fix test declaration: set fail_count: 0, remove PENDING markers"
      expected_output: "Corrected declaration"

  - MS-030-04:
      action: "Re-run autonomous-cycle with fixed declaration"
      expected_output: "AUTONOMOUS_CONTINUE: YES restored"

  - MS-030-05:
      action: "Write .local/evidences/srb-gov-001/gov-violation-catalog.json with all 7 triggers documented"
      content_includes:
        - trigger_id, function_name, condition, severity, autonomous_repair_possible

acceptance_checks:
  - gov-violation-catalog.json written with all 7 triggers
  - Can reliably trigger and resolve AUTONOMOUS_CONTINUE:NO
```

---

### TC-SRB-031 — Add continuation_reason_codes to continuation-signal.json

```yaml
taskcard_id: TC-SRB-031
title: "Add continuation_reason_codes list field to continuation-signal.json schema"
type: PARENT
status: PROPOSED
requirement_id: REQ-SRB-012
dependencies: [TC-SRB-030]

design:
  correction: "Original plan assumed reason_codes field. ACTUAL schema uses stop_reason (string). Add NEW field continuation_reason_codes (list) alongside existing fields."
  target_file: tools/supervisor/autonomous_cycle.py
  approximate_line: 2207 (where atomic_write_json(signal_path, signal) is called)
  non_breaking: "Add new field alongside existing fields; do NOT rename stop_reason"

allowed_reason_codes:
  - CONTINUE_ELIGIBLE_WORK_REMAINS
  - CONTINUE_REWORK_REQUIRED
  - CONTINUE_INDEPENDENT_LANES_AVAILABLE
  - CONTINUE_PLAN_HARDENING_REQUIRED
  - STOP_VALID_GATE_11_AUTHORIZATION
  - STOP_TRUE_EXTERNAL_DEPENDENCY
  - STOP_PORTFOLIO_COMPLETE
  - ERROR_STATE_RECONCILIATION_FAILED
  - ERROR_SPRINT_ALLOCATION_FAILED
```

#### TC-SRB-031-01 — Read autonomous_cycle.py signal writer location

```yaml
child_taskcard_id: TC-SRB-031-01
title: "Find exact location where continuation-signal.json is built in autonomous_cycle.py"
type: CHILD
status: TODO

micro_steps:
  - MS-031-01-01:
      action: "Read tools/supervisor/autonomous_cycle.py around line 2180-2230 to find signal dict construction"
      expected_output: "Lines where signal dict is built and where atomic_write_json is called"

  - MS-031-01-02:
      action: "Identify ALL fields set in the signal dict before atomic_write_json is called"
      expected_output: "Full list of existing fields (autonomous_continue, iteration, stop_reason, rework_items, continuation_state, etc.)"

  - MS-031-01-03:
      action: "Identify where rework_items and stop_reason are populated — understand the logic that determines them"
      expected_output: "Source logic documented"

acceptance_checks:
  - Exact line range identified for signal construction
  - All existing fields documented
```

#### TC-SRB-031-02 — Add continuation_reason_codes field

```yaml
child_taskcard_id: TC-SRB-031-02
title: "Insert continuation_reason_codes into signal dict in autonomous_cycle.py"
type: CHILD
status: TODO
preconditions: [TC-SRB-031-01 CLOSED]

micro_steps:
  - MS-031-02-01:
      action: "Design the mapping logic: derive reason_codes from existing fields"
      mapping: |
        if stop_reason is None and rework_items is empty:
          codes = ['CONTINUE_ELIGIBLE_WORK_REMAINS']
        elif rework_items is not empty:
          codes = ['CONTINUE_REWORK_REQUIRED']
        elif continuation_state == 'NO' and stop_reason == 'gate_11':
          codes = ['STOP_VALID_GATE_11_AUTHORIZATION']
        elif continuation_state == 'NO':
          codes = ['STOP_TRUE_EXTERNAL_DEPENDENCY']
        else:
          codes = ['CONTINUE_ELIGIBLE_WORK_REMAINS']

  - MS-031-02-02:
      action: "Add logic to compute continuation_reason_codes list in the signal dict construction"
      target_file: tools/supervisor/autonomous_cycle.py
      constraint: "Add AFTER existing fields, BEFORE atomic_write_json call"
      constraint2: "Add entry to reports/r90/product-code-change-ledger.json for this edit"

  - MS-031-02-03:
      action: "Add ledger entry for autonomous_cycle.py modification"
      target_file: reports/r90/product-code-change-ledger.json

acceptance_checks:
  - continuation_reason_codes key added to signal dict
  - Logic maps from existing fields correctly
  - Ledger entry added
```

#### TC-SRB-031-03 — Test continuation_reason_codes appears in output

```yaml
child_taskcard_id: TC-SRB-031-03
title: "Run autonomous-cycle and verify continuation_reason_codes in output"
type: CHILD
status: TODO
preconditions: [TC-SRB-031-02 CLOSED]

micro_steps:
  - MS-031-03-01:
      action: "Run: python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/srb-gov-test/evidence-declaration.yaml"
      note: "Use a clean (passing) test declaration"
      expected_output: "Exit 0 or 3; signal updated"

  - MS-031-03-02:
      action: "Read .local/supervisor/continuation-signal.json"
      expected_output: "Field continuation_reason_codes exists as a list"

  - MS-031-03-03:
      action: "Verify value is one of the allowed codes (e.g., CONTINUE_ELIGIBLE_WORK_REMAINS)"
      expected_output: "Code is valid"

  - MS-031-03-04:
      action: "Run existing pytest tests to confirm no regressions from the edit"
      command: ".venv/Scripts/pytest tests/supervisor/ -v"
      expected_output: "0 failures"

acceptance_checks:
  - continuation_reason_codes present in signal
  - Value is from allowed list
  - Existing tests still pass
```

---

### TC-SRB-032 — Governance violation recovery pilot (Pilot 4)

```yaml
taskcard_id: TC-SRB-032
title: "Pilot 4: Prove repairable governance violation → autonomous rework (not human stop)"
type: PARENT
status: PROPOSED
dependencies: [TC-SRB-031]

micro_steps:
  - MS-032-01:
      action: "Create test declaration with V57-triggering condition: edit reports/r90/product-code-change-ledger.json to remove an entry for a changed file"
      purpose: "Trigger V57 changed_files_in_ledger WARN → REWORK_REQUIRED"

  - MS-032-02:
      action: "Run autonomous-cycle with this declaration"
      expected_output: "rework_items populated; exit 3"

  - MS-032-03:
      action: "Read continuation-signal.json; verify autonomous_continue=true_with_rework and rework_items contains the item"
      expected_output: "CONTINUE_REWORK_REQUIRED in continuation_reason_codes"

  - MS-032-04:
      action: "Run check_continuation.py; verify verdict=CONTINUE (not STOP) since V57 is non-critical"
      expected_output: "CONTINUE verdict"

  - MS-032-05:
      action: "Repair: re-add the missing ledger entry"

  - MS-032-06:
      action: "Re-run autonomous-cycle with corrected declaration"
      expected_output: "Exit 0; rework_items empty"

  - MS-032-07:
      action: "Write evidence to .local/evidences/srb-pilot-04/governance-recovery.json"

acceptance_checks:
  - 7-step flow proven
  - REWORK_REQUIRED is non-blocking (CONTINUE returned by check_continuation)
  - After repair: AUTONOMOUS_CONTINUE: YES
```

---

## PART M — PHASE 4: PRODUCTION PLAN SECTION

### TC-SRB-040 — Add production sprint design section to plans/master-plan.md

```yaml
taskcard_id: TC-SRB-040
title: "Append 22-subsection production design to plans/master-plan.md"
type: PARENT
status: PROPOSED
requirement_id: REQ-SRB-013
dependencies: [TC-SRB-031]

constraint: "supervisor must NOT write to plans/master-plan.md (per policies.yaml). The AGENT (not supervisor) may write to it directly."
note: "Insert AFTER the last existing section, BEFORE any closing markers."
```

#### TC-SRB-040-01 — Locate insertion point in master-plan.md

```yaml
child_taskcard_id: TC-SRB-040-01
title: "Read master-plan.md to find insertion point and avoid duplication"
type: CHILD
status: TODO

micro_steps:
  - MS-040-01-01:
      action: "Search plans/master-plan.md for existing 'Autonomous Sprint Numbering' section"
      command: "grep -n 'Autonomous Sprint' plans/master-plan.md"
      expected_output: "No match (section doesn't exist yet) OR line number if it exists"

  - MS-040-01-02:
      action: "Find last line of master-plan.md"
      command: "wc -l plans/master-plan.md"
      expected_output: "Total line count"

  - MS-040-01-03:
      action: "If section already exists: note its line range (don't duplicate)"
      expected_output: "Decision: INSERT or UPDATE"

acceptance_checks:
  - Insertion point identified
  - No pre-existing duplicate section
```

#### TC-SRB-040-02 — Append production design section

```yaml
child_taskcard_id: TC-SRB-040-02
title: "Append all 22 sub-sections of production sprint design to master-plan.md"
type: CHILD
status: TODO
preconditions: [TC-SRB-040-01 CLOSED, no duplicate found]

section_structure_required:
  heading: "## Autonomous Sprint Numbering, Continuation, Skill Governance, and Production Supervision"
  subsections_required_22:
    1: "Problem Statement"
    2: "Historical Sprint Findings (840 sprints, 0.756 avg quality)"
    3: "Sprint Identity Contract (SPRINT-NNNNN, starts at 841)"
    4: "Atomic Number Allocation (sprint_number_allocator.py, os.replace)"
    5: "Supervisor Ownership (one-mechanism lock, AGENTS.md §AH1)"
    6: "Skill/Command-Only Execution (.supervisor/skill-registry.yaml)"
    7: "Continuation Decision Contract (continuation_reason_codes)"
    8: "Governance-Violation Recovery (REWORK_REQUIRED → CONTINUE_REWORK_REQUIRED)"
    9: "Gate 0-10 Autonomy (AGENTS.md §AG5)"
    10: "Gate 11 Authorization Boundary (G11-G: Babar Raza only)"
    11: "Micro-Taskcard State Machine (PROPOSED → CLOSED)"
    12: "Product-Deepening Sprint Template (spec→facts→qname→capabilities→...)"
    13: "Pilot Matrix (10 pilots, evidence paths)"
    14: "Parallelism and Locking (os.replace atomic, single-writer)"
    15: "Failure Recovery (bounded retries, circuit breakers for repeated failures)"
    16: "Evidence and Receipts (.local/evidences/<run_id>/, declaration-driven)"
    17: "Monitoring and Operational Metrics (.local/supervisor/sprint-metrics.json)"
    18: "Rollback (SUPERSEDED status, never delete records)"
    19: "Idempotency Keys (mission_id + plan_id + sprint_number + semantic_key)"
    20: "Production Rollout (pilot-proven before production-wide)"
    21: "Closeout Criteria (20 conditions)"
    22: "Autonomous Execution Handoff (check_continuation → next-sprint.md)"

  minimum_words: 500
  format: "Markdown with ### subsection headers"

micro_steps:
  - MS-040-02-01:
      action: "Write all 22 subsections to plans/master-plan.md (append)"
      expected_output: "Section added; wc -l increases by 200+ lines"

  - MS-040-02-02:
      action: "Verify section exists: grep -n 'Autonomous Sprint Numbering' plans/master-plan.md"
      expected_output: "Section heading found"

  - MS-040-02-03:
      action: "Verify all 22 subsection headings are present"
      expected_output: "22/22 found"

acceptance_checks:
  - Section added to plans/master-plan.md
  - All 22 subsections present
  - Minimum 500 words
```

---

## PART N — PHASE 5: PILOTS

### TC-SRB-P01 — Pilot 1: Sprint Number Monotonicity

```yaml
taskcard_id: TC-SRB-P01
title: "Pilot 1: Prove strict sprint number monotonicity"
type: PARENT
status: PROPOSED
dependencies: [TC-SRB-022]

micro_steps:
  - MS-P01-01:
      action: "Read current highest_allocated_number from sprint-ledger.json"
      record: H

  - MS-P01-02:
      action: "Run allocate with alias monoton-test-A → record N1"
      expected_output: "N1 = H + 1"

  - MS-P01-03:
      action: "Run: python tools/supervisor/sprint_number_allocator.py status"
      expected_output: "highest shows N1"

  - MS-P01-04:
      action: "Mark N1 as COMPLETED in ledger"
      command: "python -c \"import json; from pathlib import Path; p=Path('.local/supervisor/sprint-ledger.json'); d=json.loads(p.read_text()); [e.update({'status':'COMPLETED','completed_at':'now'}) for e in d['entries'] if e.get('sprint_number')==N1]; p.write_text(json.dumps(d,indent=2))\""

  - MS-P01-05:
      action: "Run allocate with alias monoton-test-B → record N2"
      expected_output: "N2 = N1 + 1 (strict monotonicity)"

  - MS-P01-06:
      action: "Assert N2 = N1 + 1"
      expected_output: "PASS"

  - MS-P01-07:
      action: "Write .local/evidences/srb-pilot-01/monotonicity-proof.json"
      content: |
        {"H": H, "N1": N1, "N2": N2, "strict_monotonicity": true, "verdict": "PASS"}

acceptance_checks:
  - N2 = N1 + 1
  - monotonicity-proof.json written
  - verdict: PASS
```

### TC-SRB-P02 through TC-SRB-P04 — References to Prior TCs

```yaml
TC-SRB-P02:
  title: "Pilot 2: Concurrent allocation"
  status: PROPOSED
  execution: "Performed as TC-SRB-023. Evidence at .local/evidences/srb-pilot-02/"
  acceptance: "3 consecutive concurrent tests pass"

TC-SRB-P03:
  title: "Pilot 3: Interrupted allocation recovery"
  status: PROPOSED
  execution: "Performed as TC-SRB-024. Evidence at .local/evidences/srb-pilot-03/"
  acceptance: "Recovery returns same sprint ID; next allocation gets correct sequential number"

TC-SRB-P04:
  title: "Pilot 4: Governance violation recovery"
  status: PROPOSED
  execution: "Performed as TC-SRB-032. Evidence at .local/evidences/srb-pilot-04/"
  acceptance: "REWORK_REQUIRED is non-blocking; repair → autonomous rework; not human stop"
```

---

### TC-SRB-P05 — Pilot 5: Missing Skill Handling (V7 validator)

```yaml
taskcard_id: TC-SRB-P05
title: "Pilot 5: V7 blocks ungoverned mutation; skill creation flow proven"
type: PARENT
status: PROPOSED
dependencies: [TC-SRB-021]

v7_facts:
  function: validate_manual_ungoverned_rejection
  triggers_on: PRODUCT_SOURCE items with execution_method=MANUAL_UNGOVERNED AND claim_classification != LEGACY_BACKFILLED
  severity: FAIL (blocks sprint)

micro_steps:
  - MS-P05-01:
      action: "Create test evidence declaration with a PRODUCT_SOURCE item and execution_method: MANUAL_UNGOVERNED and claim_classification: COMPLETED"
      target: .local/evidences/srb-pilot-05/test-declaration.yaml
      expected_output: "Declaration written"

  - MS-P05-02:
      action: "Run autonomous-cycle with this declaration"
      expected_output: "Exit 3 (critical); work-item-grades.json shows V7 failure for the item"

  - MS-P05-03:
      action: "Read work-item-grades.json to confirm V7 (validate_manual_ungoverned_rejection) caused the failure"
      expected_output: "V7 failure confirmed in grades"

  - MS-P05-04:
      action: "Fix the declaration: change execution_method to SKILL_GENERATED and add skill_id: allocate-sprint-number"
      expected_output: "Corrected declaration"

  - MS-P05-05:
      action: "Re-run autonomous-cycle with corrected declaration"
      expected_output: "Exit 0 or 3 without V7 failure"

  - MS-P05-06:
      action: "Write evidence to .local/evidences/srb-pilot-05/v7-rejection-proof.json"

acceptance_checks:
  - V7 blocks the ungoverned declaration (exit 3)
  - After skill attribution: V7 passes
  - Evidence written
```

---

### TC-SRB-P06 — Pilot 6: Real Product Deepening

```yaml
taskcard_id: TC-SRB-P06
title: "Pilot 6: Close at least one real product gap using registered skills"
type: PARENT
status: PROPOSED
dependencies: [TC-SRB-040]

gap_selection_strategy:
  primary: "Read .local/supervisor/next-work-items.json and select a DIF or NDJSON gap (these have open FOSS gaps per inventory)"
  fallback: "Select any FOSS Python format gap that is not blocked"
  constraint: "Gap must have spec_facts defined in next-work-items.json"

micro_steps:
  - MS-P06-01:
      action: "Run: python -c \"import json; items=json.load(open('.local/supervisor/next-work-items.json')); print([i['item_id'] for i in items[:5]])\""
      expected_output: "First 5 work item IDs"

  - MS-P06-02:
      action: "Select one item. Run /select-poc-gap with the selected item_id, OR manually write .local/supervisor/selected-product-gaps.json with [{item_id, format_id, gap_id}]"
      expected_output: "selected-product-gaps.json written"

  - MS-P06-03:
      action: "Run /add-python-api or /add-python-object-model-feature for the selected gap following skill protocol"
      expected_output: "New function/method added to src/python/{format}/"

  - MS-P06-04:
      action: "Add entry to reports/r90/product-code-change-ledger.json for the source change"

  - MS-P06-05:
      action: "Run: .venv/Scripts/pytest tests/{format}/ -v"
      expected_output: "0 failures"

  - MS-P06-06:
      action: "Write evidence declaration at .local/evidences/srb-pilot-06/evidence-declaration.yaml"

  - MS-P06-07:
      action: "Run: python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/srb-pilot-06/evidence-declaration.yaml"
      expected_output: "ACCEPTED or ACCEPTED_WITH_REWORK; gap closes in ledger"

acceptance_checks:
  - At least 1 gap closed
  - Tests pass (0 failures)
  - autonomous-cycle accepts the evidence
  - Evidence at .local/evidences/srb-pilot-06/
```

---

### TC-SRB-P07 — Pilot 7: Shared Machinery Regression

```yaml
taskcard_id: TC-SRB-P07
title: "Pilot 7: Fix shared tool, regress 3+ formats"
type: PARENT
status: PROPOSED
dependencies: [TC-SRB-P06]

target_selection_strategy:
  option_A: "Fix a V1-compliant docstring issue in a shared utility (e.g., tools/supervisor/path_resolver.py)"
  option_B: "If execute_oracle.py has a known issue: fix and regress all oracle-validated formats"
  constraint: "Fix must use a registered skill or governed execution"

micro_steps:
  - MS-P07-01:
      action: "Identify one shared tool with a minor verifiable fix (V100 doc issue, type annotation, etc.)"
      expected_output: "Target file identified"

  - MS-P07-02:
      action: "Apply the fix via governed execution (not MANUAL_UNGOVERNED)"
      expected_output: "Fix applied"

  - MS-P07-03:
      action: "Run tests for at least 3 formats that use the shared tool"
      command: ".venv/Scripts/pytest tests/fods/ tests/fodt/ tests/dif/ -v"
      expected_output: "0 failures for all 3"

  - MS-P07-04:
      action: "Write evidence to .local/evidences/srb-pilot-07/regression-proof.json with format list and test results"

acceptance_checks:
  - 3+ formats tested with 0 regressions
  - Evidence written
```

---

### TC-SRB-P08 — Pilot 8: Three Consecutive Autonomous Sprints

```yaml
taskcard_id: TC-SRB-P08
title: "Pilot 8: Execute 3 consecutive sprint cycles, each with unique allocated number"
type: PARENT
status: PROPOSED
dependencies: [TC-SRB-P06, TC-SRB-P07]

definition_of_autonomous: "User does NOT provide input between sprints. Each sprint selects, executes, verifies, audits, closes, and proceeds to next based on check_continuation output."

micro_steps:
  - MS-P08-01:
      action: "SPRINT A: Run allocate → get sprint_id SA. Select work items from next-work-items.json (different from Pilot 6). Execute. Run tests. Declare. Run autonomous-cycle. Check continuation."
      expected_output: "Sprint A ACCEPTED. continuation check → CONTINUE (or CONTINUE_WITH_REWORK)"
      record: "sprint_id_A"

  - MS-P08-02:
      action: "SPRINT B: Run allocate → get sprint_id SB (SB number = SA number + 1). Select different items. Execute. Run tests. Declare. Run autonomous-cycle. Check continuation."
      expected_output: "Sprint B ACCEPTED. SB number = SA number + 1."
      record: "sprint_id_B"

  - MS-P08-03:
      action: "SPRINT C: Run allocate → get sprint_id SC (SC number = SB number + 1). Select different items. Execute. Run tests. Declare. Run autonomous-cycle."
      expected_output: "Sprint C ACCEPTED. SC number = SB number + 1."
      record: "sprint_id_C"

  - MS-P08-04:
      action: "Verify: sprint_id_A < sprint_id_B < sprint_id_C (strict monotonicity across 3 sprints)"

  - MS-P08-05:
      action: "Verify: each sprint used the 7-lane format (C0-C6) per next-sprint.md"

  - MS-P08-06:
      action: "Write evidence to .local/evidences/srb-pilot-08/consecutive-sprints.json"
      content: |
        {"sprint_A": sprint_id_A, "sprint_B": sprint_id_B, "sprint_C": sprint_id_C,
         "monotonic": true, "no_user_prompts": true, "verdict": "PASS"}

acceptance_checks:
  - 3 sprints complete with unique numbers
  - Strict monotonicity proven
  - No duplicate taskcards or receipts
  - Evidence written
```

---

### TC-SRB-P09 — Pilot 9: Simulated Gate 11 Stop

```yaml
taskcard_id: TC-SRB-P09
title: "Pilot 9: Prove Gate 11 stop fires correctly while other lanes continue"
type: PARENT
status: PROPOSED
dependencies: [TC-SRB-P08]

approach: SIMULATED (no real format at Gate 10 — use mock gate state)
mock_strategy:
  - Create .local/supervisor/mock-gate-state.json with gate_10: COMPLETE for format "fods" (it has the most advancement)
  - This is a READ-ONLY inspection pilot — we inspect the EXISTING approval gate logic rather than actually advancing a real format to Gate 10

micro_steps:
  - MS-P09-01:
      action: "Read registry/format-registry.yaml to find current FODS gate status"
      expected_output: "FODS gate status at Gate 4 or whatever it currently shows"

  - MS-P09-02:
      action: "Read tools/supervisor/gate_executor.py to understand G1-G5 gate evaluation"
      expected_output: "Gate evaluation logic documented"

  - MS-P09-03:
      action: "Confirm: check_continuation.py returns CONTINUE (not STOP for Gate 11) since no format is at Gate 10+gate11"
      command: "python tools/supervisor/check_continuation.py"
      expected_output: "CONTINUE (Gate 11 not triggered)"

  - MS-P09-04:
      action: "Write .local/supervisor/mock-gate-state.json with content showing gate_11_waiting: true for fods"
      purpose: "Test that when gate_11_waiting would be set, the appropriate reason code appears"

  - MS-P09-05:
      action: "Inspect what check_continuation does when gate_11_approval is in hard_prohibitions of policies.yaml"
      expected_output: "Gate 11 classified as BLOCKED_EXTERNAL (Babar Raza)"

  - MS-P09-06:
      action: "Verify: non-FODS formats (e.g., DIF) would still have CONTINUE eligible lanes even if FODS were at Gate 11"
      expected_output: "Multiple lanes remain eligible"

  - MS-P09-07:
      action: "Write evidence to .local/evidences/srb-pilot-09/gate11-simulation.json"
      content: |
        {
          "pilot_type": "SIMULATED",
          "note": "No real format at Gate 10. Simulation confirmed gate_11_approval is in hard_prohibitions. Independent lanes remain eligible.",
          "verdict": "GATE_11_BOUNDARY_PROVEN_BY_POLICY_INSPECTION"
        }

acceptance_checks:
  - Confirmed gate_11_approval in hard_prohibitions
  - Confirmed non-Gate11 lanes would remain eligible
  - Evidence written (marked SIMULATED)
```

---

### TC-SRB-P10 — Pilot 10: No-Change Idempotency

```yaml
taskcard_id: TC-SRB-P10
title: "Pilot 10: Prove no new artifacts created when no work exists"
type: PARENT
status: PROPOSED
dependencies: [TC-SRB-P08]

micro_steps:
  - MS-P10-01:
      action: "Record current state: count entries in sprint-ledger.json, count files in .local/evidences/"
      record: "baseline counts"

  - MS-P10-02:
      action: "Run: python tools/supervisor/sprint_number_allocator.py allocate --mission-id IDEMPOTENCY-FINAL --semantic-alias idem-final-test"
      record: "sprint number N"

  - MS-P10-03:
      action: "Run same command again: same alias"
      expected_output: "Same N returned; verdict=ALREADY_ALLOCATED"

  - MS-P10-04:
      action: "Run check_continuation.py twice in a row"
      expected_output: "Both runs return same verdict (idempotent read)"

  - MS-P10-05:
      action: "Run autonomous-cycle with an already-accepted declaration (no new work)"
      expected_output: "No new sprint allocated; no duplicate evidence entries"

  - MS-P10-06:
      action: "Record final state: sprint-ledger entry count should be baseline + 1 (only idem-final-test added)"
      expected_output: "No unexpected new entries"

  - MS-P10-07:
      action: "Write evidence to .local/evidences/srb-pilot-10/idempotency-final.json"

acceptance_checks:
  - Second allocate call returns same number
  - No duplicate evidence entries created
  - check_continuation identical both times
  - Ledger grew by exactly 1 (the idem-final-test entry)
```

---

## PART O — PHASE 6: PRODUCT DEEPENING

### TC-SRB-070 — Product Deepening Sprint 1 (using productionized allocator)

```yaml
taskcard_id: TC-SRB-070
title: "Execute first product deepening sprint using the productionized sprint engine"
type: PARENT
status: PROPOSED
requirement_id: REQ-SRB-015
dependencies: [TC-SRB-P08]

prerequisite: "Rework items (PQ-029-ADDRECORD, PQ-019-020-CLI-STUBS) must be CLOSED before this TC begins."

micro_steps:
  - MS-070-01:
      action: "Run sprint allocator: python tools/supervisor/sprint_number_allocator.py allocate --mission-id SRB-PRODUCT-DEEPENING-001 --semantic-alias srb-product-sprint-1"
      record: "SPRINT-N"

  - MS-070-02:
      action: "Run /select-poc-gap to select 3-5 eligible gaps from next-work-items.json"
      expected_output: "selected-product-gaps.json updated"

  - MS-070-03:
      action: "Execute each selected gap through the appropriate registered skill (/add-python-api, /add-python-object-model-feature, etc.)"
      constraint: "Each src/ change must have ledger entry"

  - MS-070-04:
      action: "Run: .venv/Scripts/pytest tests/ -v (full suite)"
      expected_output: "0 failures; test count >= 21558 (must not decrease)"

  - MS-070-05:
      action: "Write evidence declaration at .local/evidences/srb-product-sprint-1/evidence-declaration.yaml"

  - MS-070-06:
      action: "Run: python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/srb-product-sprint-1/evidence-declaration.yaml"
      expected_output: "ACCEPTED; sprint-ledger.json updated with SPRINT-N completed"

  - MS-070-07:
      action: "Run check_continuation.py. Record verdict."
      expected_output: "CONTINUE (or ACTIVE_PLAN_INCOMPLETE — which is correct for active plan)"

acceptance_checks:
  - Sprint SPRINT-N allocated and completed in ledger
  - At least 2 product gaps closed
  - 0 test failures
  - ACCEPTED verdict
```

---

### TC-SRB-071 — Product Deepening Sprint 2

```yaml
taskcard_id: TC-SRB-071
title: "Execute second consecutive product deepening sprint"
type: PARENT
status: PROPOSED
dependencies: [TC-SRB-070]

micro_steps:
  - MS-071-01:
      action: "Run sprint allocator with alias srb-product-sprint-2 → get SPRINT-M (M = N+1)"

  - MS-071-02:
      action: "Select different gaps from next-work-items.json (not already claimed by Sprint N)"

  - MS-071-03:
      action: "Execute gaps through registered skills"

  - MS-071-04:
      action: "Run full test suite. 0 failures."

  - MS-071-05:
      action: "Write evidence declaration at .local/evidences/srb-product-sprint-2/"

  - MS-071-06:
      action: "Run autonomous-cycle. Record verdict."
      expected_output: "ACCEPTED; SPRINT-M completed in ledger"

  - MS-071-07:
      action: "If work queue exhausted: write STOP_PORTFOLIO_COMPLETE to .local/supervisor/sprint-metrics.json"

acceptance_checks:
  - Sprint SPRINT-M = SPRINT-N+1 (strict monotonicity)
  - Different gaps from Sprint N
  - 0 test failures
  - ACCEPTED verdict
```

---

## PART P — PHASE 7: PRODUCTION READINESS AUDIT

### TC-SRB-090 — Production Readiness Audit

```yaml
taskcard_id: TC-SRB-090
title: "Complete 20-item production readiness audit and generate final verdict"
type: PARENT
status: PROPOSED
requirement_id: REQ-SRB-016
dependencies: [TC-SRB-P01, TC-SRB-P02, TC-SRB-P03, TC-SRB-P04, TC-SRB-P05, TC-SRB-P06, TC-SRB-P07, TC-SRB-P08, TC-SRB-P09, TC-SRB-P10, TC-SRB-071]

audit_checklist:
  1: "All historical sprint records reconciled? → sprint-inventory.json exists"
  2: "Canonical highest sprint number established? → sprint-ledger.json with highest_allocated_number"
  3: "Next-sprint allocation atomic and idempotent? → Pilot 2+10 evidence"
  4: "Duplicate allocation prevented? → Pilot 2 concurrent test"
  5: "Interrupted sprint recovery proven? → Pilot 3 evidence"
  6: "Governance AUTONOMOUS_CONTINUE:NO root-caused? → gov-violation-catalog.json"
  7: "approval-gates.md from structured state? → confirmed not hand-edited"
  8: "Continuation uses reason codes? → continuation_reason_codes field added"
  9: "Repairable violations → autonomous rework? → Pilot 4 evidence"
  10: "All mutations via registered skills? → V7 pilot (Pilot 5) evidence"
  11: "Micro-taskcards used? → All TCs in this plan are micro-taskcards"
  12: "Production design in master-plan.md? → TC-SRB-040 evidence"
  13: "10 diverse pilots pass? → Pilots 1-10 evidence bundles"
  14: "3+ consecutive autonomous sprints? → Pilot 8 evidence"
  15: "Product deepening advanced? → Pilots 6+7, TC-SRB-070+071"
  16: "Gate 11 behavior correct? → Pilot 9 (simulated) evidence"
  17: "Regressions pass? → Pilot 7 evidence (3+ formats)"
  18: "No-change idempotency passes? → Pilot 10 evidence"
  19: "Final production-readiness audit complete? → this TC"
  20: "No eligible healing task remains? → all TCs CLOSED"

micro_steps:
  - MS-090-01:
      action: "For each of 20 items: read the referenced evidence file and mark PASS or FAIL"
      expected_output: "20-item checklist with PASS/FAIL for each"

  - MS-090-02:
      action: "If any FAIL: create a new child taskcard to address it and mark this TC as INTEGRATION_PENDING"

  - MS-090-03:
      action: "If all PASS: generate verdict AUTONOMOUS_SPRINT_ENGINE_PRODUCTIONIZED_AND_MULTI_PILOT_PROVEN"

  - MS-090-04:
      action: "Write .local/evidences/srb-final-audit/production-readiness-audit.json"
      content: |
        {
          "verdict": "AUTONOMOUS_SPRINT_ENGINE_PRODUCTIONIZED_AND_MULTI_PILOT_PROVEN",
          "audit_date": "<timestamp>",
          "checklist_results": [...20 items...],
          "sprint_ledger": ".local/supervisor/sprint-ledger.json",
          "highest_sprint_allocated": "SPRINT-NNNNN",
          "pilot_evidence_paths": {...}
        }

  - MS-090-05:
      action: "Run: python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/splendid-roaming-beaver.md --terminal --audit-gate"
      expected_output: "Lock written as TERMINAL_CLOSED"

acceptance_checks:
  - All 20 checklist items PASS
  - Audit JSON written
  - Plan lock written as TERMINAL_CLOSED
```

---

## PART Q — VALIDATION MATRIX
### (Deliverables: verification-matrix, validation-command-matrix, negative-control-matrix)

| TC | Validation Type | Command / Method | Expected Result | Mandatory |
|---|---|---|---|---|
| TC-SRB-RW1 | Unit test | `.venv/Scripts/pytest tests/net/ndjson/ -v` | 0 failures | YES |
| TC-SRB-RW2 | CLI invocation | `python -m fods --help` (5 formats) | Help displayed | YES |
| TC-SRB-000 | File existence | `ls plans/.claude/splendid-roaming-beaver.md` | File exists | YES |
| TC-SRB-001 | Tool output | `python tools/supervisor/check_continuation.py` | verdict=CONTINUE | YES |
| TC-SRB-010 | JSON validity | `python -c "import json; json.load(open('.local/supervisor/sprint-inventory.json'))"` | No exception | YES |
| TC-SRB-013 | JSON validity | `python -c "import json; d=json.load(open('.local/supervisor/sprint-ledger.json')); assert d['highest_allocated_number']==840"` | PASS | YES |
| TC-SRB-020 | Tool run | `python tools/supervisor/sprint_number_allocator.py allocate --mission-id TEST --semantic-alias alloc-test` | Valid JSON receipt | YES |
| TC-SRB-020 | File exists | `ls tools/supervisor/sprint_number_allocator.py` | File exists | YES |
| TC-SRB-021 | YAML validity | `python -c "import yaml; yaml.safe_load(open('.supervisor/skill-registry.yaml').read()); print('VALID')"` | VALID | YES |
| TC-SRB-022 | Idempotency | Run allocate same alias twice; compare numbers | Same number both times | YES |
| TC-SRB-023 | Concurrent test | `python tests/supervisor/test_sprint_allocator_concurrent.py` 3x | PASS all 3 | YES |
| TC-SRB-030 | Negative control | Run autonomous-cycle with fail_count:1 declaration | AUTONOMOUS_CONTINUE:NO | YES |
| TC-SRB-031 | Field existence | `python -c "import json; d=json.load(open('.local/supervisor/continuation-signal.json')); assert 'continuation_reason_codes' in d"` | PASS | YES |
| TC-SRB-031 | Regression | `.venv/Scripts/pytest tests/supervisor/ -v` | 0 failures | YES |
| TC-SRB-040 | Section present | `grep -c 'Autonomous Sprint Numbering' plans/master-plan.md` | ≥1 | YES |
| TC-SRB-P08 | Sprint monotonicity | Compare sprint numbers across 3 sprints | Strict N < N+1 < N+2 | YES |
| TC-SRB-090 | Evidence complete | All 10 pilot evidence dirs have required files | All exist | YES |

**Negative Controls:**

| Test | Trigger | Expected Block |
|---|---|---|
| V7 rejection | MANUAL_UNGOVERNED in PRODUCT_SOURCE declaration | autonomous-cycle exit 3 |
| AUTONOMOUS_CONTINUE:NO | fail_count > 0 in evidence | approval-gates shows NO |
| Duplicate allocation | Same alias twice | Second call returns ALREADY_ALLOCATED |
| ACTIVE_PLAN_INCOMPLETE | Plan lock IN_PROGRESS + check_continuation | verdict=STOP reason=ACTIVE_PLAN_INCOMPLETE |

---

## PART R — EVIDENCE CONTRACT
### (Deliverables: evidence-contract, evidence-obligation-matrix)

```yaml
evidence_contract:
  authoritative_plan: C:\Users\prora\.claude\plans\splendid-roaming-beaver.md
  evidence_root: .local/evidences/

  required_evidence_directories:
    srb-rw1: "NdjsonDocument AddRecord resolution"
    srb-rw2: "CLI+stubs for 20 packages resolution"
    srb-baseline: "Session state baseline"
    srb-gov-001: "Governance violation catalog"
    srb-gov-test: "Test declarations for governance testing"
    srb-pilot-01: "Monotonicity pilot evidence"
    srb-pilot-02: "Concurrent allocation pilot evidence"
    srb-pilot-03: "Recovery pilot evidence"
    srb-pilot-04: "Governance recovery pilot evidence"
    srb-pilot-05: "V7 rejection pilot evidence"
    srb-pilot-06: "Product deepening pilot evidence"
    srb-pilot-07: "Shared machinery regression pilot evidence"
    srb-pilot-08: "Consecutive sprints pilot evidence"
    srb-pilot-09: "Gate 11 simulation evidence"
    srb-pilot-10: "Idempotency final evidence"
    srb-product-sprint-1: "Product deepening sprint 1"
    srb-product-sprint-2: "Product deepening sprint 2"
    srb-final-audit: "Production readiness audit"

  evidence_format_per_dir:
    required_files:
      - evidence-declaration.yaml (for sprint-type evidence)
    optional_files:
      - *.json (test results, proofs)
      - *.txt (test output logs)

  each_evidence_artifact_references:
    - authoritative_plan: C:\Users\prora\.claude\plans\splendid-roaming-beaver.md
    - requirement_id: REQ-SRB-NNN
    - taskcard_id: TC-SRB-NNN
```

---

## PART S — EXECUTION DAG (Summary)
### (Deliverables: execution-dag, taskcard-dependency-matrix, file-ownership-and-locks, parallel-execution-safety-map)

```yaml
execution_order:
  wave_0_rework: [TC-SRB-RW1, TC-SRB-RW2]  # parallel safe (different files)
  wave_1_bootstrap: [TC-SRB-000, TC-SRB-001, TC-SRB-002]  # sequential
  wave_2_inventory: [TC-SRB-010, TC-SRB-011, TC-SRB-012, TC-SRB-013]  # sequential
  wave_3_allocator: [TC-SRB-020, TC-SRB-021, TC-SRB-022, TC-SRB-023, TC-SRB-024]  # sequential
  wave_4_governance: [TC-SRB-030, TC-SRB-031, TC-SRB-032]  # sequential
  wave_5_plan: [TC-SRB-040]  # after wave_4
  wave_6_pilots: [TC-SRB-P01, TC-SRB-P02(=023), TC-SRB-P03(=024), TC-SRB-P04(=032), TC-SRB-P05, TC-SRB-P06, TC-SRB-P07]  # some parallel
  wave_7_consecutive: [TC-SRB-P08]  # after P06+P07
  wave_8_boundary: [TC-SRB-P09, TC-SRB-P10]  # parallel safe
  wave_9_deepening: [TC-SRB-070, TC-SRB-071]  # sequential
  wave_10_audit: [TC-SRB-090]

parallel_safe:
  - [TC-SRB-RW1, TC-SRB-RW2]  # different files
  - [TC-SRB-P09, TC-SRB-P10]  # read-only/non-conflicting
  - [TC-SRB-P06, TC-SRB-P07]  # different format gaps (if different format files)

sequential_required:
  - sprint-ledger.json modifications (only one TC may modify at a time)
  - .supervisor/skill-registry.yaml (one TC at a time)
  - plans/master-plan.md (one TC at a time)
  - continuation-signal.json (one TC at a time)

file_ownership:
  sprint-ledger.json: TC-SRB-013 creates, TC-SRB-020+ modifies
  sprint_number_allocator.py: TC-SRB-020 creates
  skill-registry.yaml: TC-SRB-021 modifies
  master-plan.md: TC-SRB-040 modifies
  autonomous_cycle.py: TC-SRB-031 modifies
  sprint-inventory.json: TC-SRB-010 creates
  sprint-anomaly-register.json: TC-SRB-011 creates, TC-SRB-012 updates
```

---

## PART T — EXECUTION HANDOFF
### (Deliverable: final execution handoff)

**The execution agent must follow this exact sequence:**

```
STEP 1: Read this plan file fully (plans/.claude/splendid-roaming-beaver.md after copy)
STEP 2: Check Part H (Phase -1) for rework items. Execute TC-SRB-RW1 and TC-SRB-RW2 FIRST.
STEP 3: Execute TC-SRB-000 (copy plan, write lock). After this, all updates to in-repo copy.
STEP 4: Execute TC-SRB-001 (check_continuation). Note: ACTIVE_PLAN_INCOMPLETE is expected after step 3.
STEP 5: Execute TC-SRB-002 (baseline capture).
STEP 6: Execute TC-SRB-010 through TC-SRB-013 (sprint inventory and identity contract).
STEP 7: Execute TC-SRB-020 through TC-SRB-024 (allocator implementation and pilots).
STEP 8: Execute TC-SRB-030 through TC-SRB-032 (governance investigation).
STEP 9: Execute TC-SRB-040 (master-plan production section).
STEP 10: Execute TC-SRB-P01 through TC-SRB-P10 (all 10 pilots — some overlap with prior TCs).
STEP 11: Execute TC-SRB-070 and TC-SRB-071 (product deepening sprints).
STEP 12: Execute TC-SRB-090 (final audit). If all 20 items PASS: run write_plan_lock.py --terminal.
```

**After EACH child taskcard micro-step, the execution agent MUST:**
1. Verify the expected output is present
2. Update taskcard status in plans/.claude/splendid-roaming-beaver.md
3. Write or append evidence to the relevant .local/evidences/ directory
4. If any quality gate scores below 4/5: mark REROUTED and create repair step before continuing

**The execution agent MUST NOT:**
- Skip micro-steps without documenting SKIPPED_NOT_APPLICABLE reason
- Mark a parent CLOSED before all mandatory children are CLOSED
- Treat file existence as evidence of correct behavior (must inspect contents)
- Execute any src/ change without ledger entry in reports/r90/product-code-change-ledger.json
- Use MANUAL_UNGOVERNED execution_method for PRODUCT_SOURCE items (V7 will fail)
- Close the plan (--terminal) before TC-SRB-090 CLOSED

---

## PART U — PLAN RECONCILIATION
### (Deliverables: plan-reconciliation-report, single-plan-authority-audit, idempotency-check)

```yaml
plan_reconciliation:
  single_authoritative_plan: YES
  competing_plans: NONE
  duplicate_sections: NONE
  all_sections_analyzed: YES (8 sections in B.1)
  all_actionables_represented: YES (29 original + 9 new child TCs added)
  all_children_linked_to_parents: YES
  all_micro_steps_linked: YES (per each child taskcard)
  dependencies_consistent: YES
  stale_instructions: CORRECTED (reason_codes, Windows locking, sprint count)
  evidence_paths_all_explicit: YES

idempotency:
  plan_id: splendid-roaming-beaver
  stable_id_prefix: TC-SRB-
  rerun_behavior:
    - Re-read plan from plans/.claude/splendid-roaming-beaver.md
    - Check which TCs are already CLOSED (don't re-execute)
    - Continue from first PROPOSED/IN_PROGRESS TC
    - Do not allocate new sprint numbers if semantic_alias already in ledger
  duplicate_detection:
    - sprint-ledger.json: check semantic_alias before allocating
    - evidence dirs: check if evidence-declaration.yaml exists before re-running
    - plan amendments: check if section heading exists before inserting
```

---

## PART V — DEFECT LOG (CHANGES FROM V1)

| Defect ID | V1 Error | V2 Correction |
|---|---|---|
| DEF-001 | Sprint count ~585 | Corrected to 840 (maturity-trend.json) |
| DEF-002 | Last sprint: vast-weaving-lampson | Corrected to PQ-BUNDLE-FORENSICS-REPAIR-001 |
| DEF-003 | Tests: 1169 | Corrected to 21558 |
| DEF-004 | No rework items identified | Added PQ-029-ADDRECORD and PQ-019-020-CLI-STUBS (from continuation-signal.json) |
| DEF-005 | reason_codes field assumed | Field does not exist; added continuation_reason_codes as new field |
| DEF-006 | fcntl/filelock for Windows | Corrected to os.replace() atomic write (existing pattern in write_plan_lock.py) |
| DEF-007 | Ledger bootstraps all 840 | Corrected: only bootstrap highest_allocated_number=840; new allocations start at 841 |
| DEF-008 | Pilot 2+3 were stub references | Now have full micro-step decomposition in TC-SRB-023+024 |
| DEF-009 | Pilot 9 assumed real Gate 10 | Corrected to simulated pilot (no format actually at Gate 10) |
| DEF-010 | No Phase -1 for rework | Added Phase -1 with TC-SRB-RW1, TC-SRB-RW2 |

---

## Closure Conditions

This plan closes when:
1. TC-SRB-090 CLOSED with verdict AUTONOMOUS_SPRINT_ENGINE_PRODUCTIONIZED_AND_MULTI_PILOT_PROVEN
2. All 29 parent TCs and all child TCs are CLOSED
3. All 10 pilot evidence directories contain required files
4. plans/master-plan.md contains the 22-subsection production design

Close command: `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/splendid-roaming-beaver.md --terminal --audit-gate`

True external stops only:
- Gate 11 authorization (Babar Raza) for commercial release
- git push credentials unavailable
- Package publication credentials

---

## EXECUTION READINESS VERDICT

```
VERDICT: PLAN_MICRO_TASKCARDIZED_READY_FOR_EXECUTION

Active Plan:
  authoritative path: C:\Users\prora\.claude\plans\splendid-roaming-beaver.md
  in-repo copy target: plans/.claude/splendid-roaming-beaver.md
  authority source: per-chat-plan (user-invoked plan mode)
  duplicate active plans found: false
  duplicate risk resolved: N/A

Plan Analysis:
  sections analyzed: 8 major phases + 10 appendix parts
  phases analyzed: Phase -1 (new), Phase 0-7
  actionables extracted: 54 (29 parents + 25 child TCs)
  ambiguous actionables resolved: 10 (see DEF-001 through DEF-010)
  investigation taskcards: TC-SRB-031-01 (locate signal writer)

Decomposition:
  parent taskcards: 29
  child taskcards: 25 explicitly decomposed
  micro-steps: 90+ across all child TCs
  broad taskcards split: all Phase 0-3 TCs decomposed
  smallest-step quality: each micro-step has single action, single expected output

Machine State:
  state machine: defined in Part G
  invalid transitions: documented
  dependency DAG: defined in Part S
  file ownership: defined in Part S

Next Valid Actions:
  FIRST: Execute Phase -1 (TC-SRB-RW1 and TC-SRB-RW2) in parallel
  THEN: Execute TC-SRB-000 (copy plan, write lock)
  FIRST MICRO-STEP: MS-RW1-01-01 (Read NdjsonDocument.cs)
```
