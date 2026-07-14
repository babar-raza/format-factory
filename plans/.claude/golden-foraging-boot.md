# Format Factory Machinery Readiness & Product-Deepening Assessment
## Plan: golden-foraging-boot
## Type: machinery_hardening
## Mission ID: FF-MR-2026-001
## Created: 2026-07-10
## Enhanced: 2026-07-11 (micro-taskcardization pass)
## Authority: EXISTING_MASTER_PLAN_SURGICAL_ENHANCEMENT

---

## PREFLIGHT ANALYSIS

```yaml
preflight:
  repository: "c:/Users/prora/OneDrive/Documents/GitHub/format-factory"
  branch: main
  head_commit: af879e55
  git_status: "29 modified tracked files, 2 untracked (.runner_system_id, src/python/fods/fods_to_csv.py)"
  active_plan_path: "plans/.claude/golden-foraging-boot.md"
  active_plan_title: "Format Factory Machinery Readiness & Product-Deepening Assessment"
  plan_authority_source: "loaded per-chat plan (this file)"
  plan_format: markdown_machinery_hardening
  plan_approximate_size_lines: 4500
  major_section_count: 9
  group_count: 5
  parent_taskcard_count: 23
  child_taskcard_count: 92  # after micro-taskcardization
  micro_step_count: ~280    # after micro-taskcardization
  existing_lanes: [machinery_governance, product-dotnet, product-python]
  existing_gates: [MR-0 through MR-20, Gate-11-per-product]
  existing_state_vocabulary: [OPEN, IN_PROGRESS, CLOSED]  # pre-enhancement
  enhanced_state_vocabulary:
    parent: [PROPOSED, READY, IN_PROGRESS, CHILDREN_IN_PROGRESS, INTEGRATION_PENDING,
             VERIFIED, SCORED, CLOSED, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]
    child: [TODO, READY, IN_PROGRESS, IMPLEMENTED, VERIFIED, SCORED, CLOSED,
            REROUTED, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]
    micro_step: [PENDING, READY, ACTIVE, COMPLETE, FAILED, BLOCKED, SKIPPED_NOT_APPLICABLE]
  existing_validation_model: "partial — output files listed but no commands"
  enhanced_validation_model: "full — exact commands, expected outputs, negative controls"
  existing_evidence_model: "partial — artifact paths listed"
  enhanced_evidence_model: "full — paths, SHA-256 required, content assertions"
  duplicate_plan_risk: NONE
    # plans/master-plan.md = authoritative PRODUCT plan (this plan enhances it in TC-GFB-020)
    # plans/.claude/golden-foraging-boot.md = THIS plan (execution authority)
    # plans/strategic/* = correction plans (read-only from this plan)
    # No competing execution plans found
```

---

## PLAN AUTHORITY VERDICT

```yaml
active_plan_authority_verdict:
  verdict: AUTHORITATIVE_SINGLE_PLAN
  authoritative_path: "plans/.claude/golden-foraging-boot.md"
  competing_plans_found: false
  master_plan_relationship: "plans/master-plan.md is PRODUCT authority; this plan ENHANCES it in TC-GFB-020"
  supporting_artifacts_location: ".local/evidences/ff-machinery-readiness-20260710-af879e5/ff-machinery-readiness/"
  supporting_artifacts_are_non_authoritative: true
  execution_agents_directed_to: "plans/.claude/golden-foraging-boot.md ONLY"
```

All supporting artifacts written to evidence root MUST include:
```yaml
authoritative_plan: plans/.claude/golden-foraging-boot.md
artifact_role: analysis_or_evidence_only
execution_authority: false
```

---

## REQUIREMENT REGISTRY

| REQ ID | Domain | Description | Parent TC |
|--------|--------|-------------|-----------|
| REQ-SETUP-001 | run_setup | Evidence root and binding artifacts created before audit | TC-GFB-001 |
| REQ-LAYER-001 | layer_map | All 29 system layers inventoried with producers/consumers | TC-GFB-002 |
| REQ-LAYER-002 | layer_map | Prior run artifacts reconciled before current audit | TC-GFB-002 |
| REQ-QNAME-001 | qname | QName schema fully inventoried and versioned | TC-GFB-003 |
| REQ-QNAME-002 | qname | QName-to-source compliance matrix produced per-format | TC-GFB-003 |
| REQ-QNAME-003 | qname | QName enforcement gap register produced | TC-GFB-003 |
| REQ-PROD-001 | product | Complete product census for all src/ formats | TC-GFB-004 |
| REQ-PROD-002 | product | FodtDocumentExtendedApis.cs (2944 LOC) violation documented | TC-GFB-004 |
| REQ-SKILL-001 | skill | All 123 skills classified by maturity | TC-GFB-005 |
| REQ-SAL-001 | sal | SAL fact provenance verified (deterministic vs manual) | TC-GFB-005 |
| REQ-RCAL-001 | rcal | Capability gap queue executability assessed | TC-GFB-005 |
| REQ-LANE-001 | lane | All 13 lanes documented (current state) | TC-GFB-006 |
| REQ-LANE-002 | lane | Downstream producer-consumer chain audited | TC-GFB-006 |
| REQ-AUTO-001 | autonomous | Continuation 7-check system verified | TC-GFB-007 |
| REQ-AUTO-002 | autonomous | Gate 11 enforcement gap documented | TC-GFB-007 |
| REQ-STD-001 | standard | Production-prohibited patterns enumerated | TC-GFB-010 |
| REQ-GAP-001 | gap_matrix | All gaps classified with severity and root cause | TC-GFB-011 |
| REQ-ARCH-001 | architecture | Full authority-to-Gate-11 chain documented | TC-GFB-012 |
| REQ-SOL-001 | solution | Solutions evaluated for every CRITICAL/HIGH gap | TC-GFB-013 |
| REQ-MPLAN-001 | master_plan | plans/master-plan.md surgically enhanced with audit findings | TC-GFB-020 |
| REQ-LANE-003 | lane | Formal lane contracts in .governance/lanes/lane-contracts.yaml | TC-GFB-021 |
| REQ-LANE-004 | lane | Lane-contract validator (V168) added and tested | TC-GFB-021 |
| REQ-G11-001 | gate11 | GATE_11_READY state defined in registry/gate-states.yaml | TC-GFB-022 |
| REQ-G11-002 | gate11 | check_continuation.py enforces per-product Gate 11 | TC-GFB-022 |
| REQ-BF-001 | backfill | migration-map.schema.yaml defined | TC-GFB-023 |
| REQ-BF-002 | backfill | tools/backfill/dry_run_migration.py read-only tool created | TC-GFB-023 |
| REQ-TEST-001 | machinery_test | Negative control: missing qname blocks validator | TC-GFB-024 |
| REQ-TEST-002 | machinery_test | Negative control: invalid SAL authority blocks oracle | TC-GFB-024 |
| REQ-TEST-003 | machinery_test | Gate 11 stop verified via test | TC-GFB-024 |
| REQ-PILOT-A | pilot | FODS .NET full lifecycle to GATE_11_READY | TC-GFB-030 |
| REQ-PILOT-B | pilot | FODT .NET full lifecycle, monolith assessed | TC-GFB-031 |
| REQ-PILOT-D | pilot | Python FOSS capability gap closed + oracle maintained | TC-GFB-032 |
| REQ-PILOT-G | pilot | FODS→CSV/ODS conversion proof ≤30 lines | TC-GFB-033 |
| REQ-PILOT-H | pilot | Autonomous controller executes + gates without intervention | TC-GFB-034 |
| REQ-WAVE-001 | wave | 7-wave product deepening schedule defined | TC-GFB-040 |
| REQ-HAND-001 | handoff | Single-go execution handoff emitted with SHA-256 | TC-GFB-041 |

---

## MACHINE STATE MODEL

### Parent Taskcard State Machine

```
PROPOSED → READY → IN_PROGRESS → CHILDREN_IN_PROGRESS → INTEGRATION_PENDING
    → VERIFIED → SCORED → CLOSED

Exception paths:
  any non-CLOSED → BLOCKED → READY (after unblock)
  any non-CLOSED → BLOCKED_EXTERNAL (credential/authority gap)
  any non-CLOSED → DEFERRED_WITH_REASON (with written rationale)
  VERIFIED → SCORED → REROUTED → IN_PROGRESS (quality score < 4/5)
  CLOSED → REOPENED only via governed audit event with evidence
```

**Invalid parent transitions (BLOCKED):**
- PROPOSED → CLOSED (must pass through CHILDREN_IN_PROGRESS)
- READY → CLOSED (execution required)
- IN_PROGRESS → CLOSED (integration required)
- CHILDREN_IN_PROGRESS → CLOSED (integration pending required)
- REROUTED → CLOSED without new VERIFIED evidence

### Child Taskcard State Machine

```
TODO → READY → IN_PROGRESS → IMPLEMENTED → VERIFIED → SCORED → CLOSED
SCORED → REROUTED → IN_PROGRESS (quality score < 4/5)
```

**Invalid child transitions (BLOCKED):**
- TODO → CLOSED
- READY → CLOSED
- IMPLEMENTED → CLOSED (verification required)
- SCORED < 4/5 → CLOSED (must REROUTE first)

### Micro-Step State Machine

```
PENDING → READY → ACTIVE → COMPLETE
ACTIVE → FAILED → READY (retry)
ACTIVE → BLOCKED → READY (after unblock)
PENDING → SKIPPED_NOT_APPLICABLE (with written reason)
```

**Invalid micro-step transitions (BLOCKED):**
- PENDING → COMPLETE (activation required)
- FAILED → COMPLETE (retry required)
- BLOCKED → COMPLETE (unblock required)

### State Guard Table

| From | To | Guard condition |
|------|----|-----------------|
| CHILDREN_IN_PROGRESS | INTEGRATION_PENDING | ALL mandatory children CLOSED |
| INTEGRATION_PENDING | VERIFIED | All integration checks pass |
| VERIFIED | SCORED | Quality scored on all dimensions |
| SCORED | CLOSED | All dimensions >= 4/5 |
| SCORED | REROUTED | Any dimension < 4/5 |
| REROUTED | IN_PROGRESS | Repair child created and claimed |

---

## DEPENDENCY DAG (summary)

```
TC-GFB-001 (P0)
  └─ TC-GFB-002 (P0)
       └─ TC-GFB-003 (P1)
            └─ TC-GFB-004 (P1)
                 └─ TC-GFB-005 (P1)
                      └─ TC-GFB-006 (P1)
                           └─ TC-GFB-007 (P1)
                                ├─ TC-GFB-010 (P2, parallel with -011)
                                ├─ TC-GFB-011 (P2, needs -003..007)
                                     └─ TC-GFB-012 (P2)
                                          └─ TC-GFB-013 (P2)
                                               ├─ TC-GFB-020 (P3, parallel)
                                               ├─ TC-GFB-021 (P3, parallel)
                                               ├─ TC-GFB-022 (P3, parallel)
                                               ├─ TC-GFB-023 (P3, parallel)
                                               │    all four → TC-GFB-024 (P3)
                                               │                    ├─ TC-GFB-030 (P4, parallel)
                                               │                    └─ TC-GFB-032 (P4, parallel)
                                               │                         ├─ TC-GFB-031 (after -030)
                                               │                         └─ TC-GFB-033 (after -032)
                                               │                              └─ TC-GFB-034 (after all)
                                               │                                   └─ TC-GFB-040
                                               │                                        └─ TC-GFB-041
```

**Parallel-safe groups:**
- Group A: TC-GFB-010 + TC-GFB-011 (both require -003..007, both write to evidence root only)
- Group B: TC-GFB-020 + TC-GFB-021 + TC-GFB-022 + TC-GFB-023 (separate owned paths)
- Group C: TC-GFB-030 + TC-GFB-032 (separate product lanes: product-dotnet vs product-python)

**Serial required:**
- TC-GFB-001..007 must be sequential (each reads prior output)
- TC-GFB-022 must complete before TC-GFB-024 (gate11 test depends on implementation)
- TC-GFB-030 must complete before TC-GFB-031 (FODT pilot depends on FODS findings)

---

## TASKCARD STATUS TABLE
(lifecycle_audit.py compatible — parent IDs only, 2-column format)

| TC-GFB-001 | CLOSED |
| TC-GFB-002 | CLOSED |
| TC-GFB-003 | CLOSED |
| TC-GFB-004 | CLOSED |
| TC-GFB-005 | CLOSED |
| TC-GFB-006 | CLOSED |
| TC-GFB-007 | CLOSED |
| TC-GFB-010 | CLOSED |
| TC-GFB-011 | CLOSED |
| TC-GFB-012 | CLOSED |
| TC-GFB-013 | CLOSED |
| TC-GFB-020 | CLOSED |
| TC-GFB-021 | CLOSED |
| TC-GFB-022 | CLOSED |
| TC-GFB-023 | CLOSED |
| TC-GFB-024 | CLOSED |
| TC-GFB-030 | CLOSED |
| TC-GFB-031 | CLOSED |
| TC-GFB-032 | CLOSED |
| TC-GFB-033 | CLOSED |
| TC-GFB-034 | CLOSED |
| TC-GFB-040 | CLOSED |
| TC-GFB-041 | CLOSED |

---

## Context

This plan was generated in response to a comprehensive machinery-readiness and product-deepening readiness
prompt. It performs a repository-truth audit, identifies gaps, designs missing machinery, and prepares
the system for authorized autonomous product deepening.

**Current repository state (session 033f6a1ae2f3, 2026-07-10):**
- Last sprint: vast-weaving-lampson — TERMINAL_CLOSED, ACCEPTED
- Tests: 1169 passed / 0 failed / 10 skipped
- Contradictions: CLEAN (0)
- Continuation: autonomous_continue=true, iteration=0/12
- Oracle: All 20 FOSS formats VERIFIED (73/73 PASS)
- SAL: 14,441 facts across 20 formats — COMPLETE
- QName: 65/66 entries (99.4%) — 1 intentional gap (fodt:office:body)
- Governance: 167 validators (V1–V167) — OPERATIONAL
- Skills: 123 governed skills (r98-governed-skills-expanded) — OPERATIONAL
- active-plan-lock.json: TERMINAL_CLOSED (old session — new session will clear it)
- continuation-signal.json: stale (2026-07-04, session_id=null WARN_LEGACY path)

**Plan mode:** EXISTING_MASTER_PLAN_SURGICAL_ENHANCEMENT
- Authoritative master plan: `plans/master-plan.md` (441 KB, v6.0, last updated 2026-07-10)
- This per-chat plan is the execution authority for all taskcards below
- TC-GFB-020 will surgically enhance master-plan.md; it does NOT replace it
- Do NOT create competing plans

**Evidence root:** `.local/evidences/ff-machinery-readiness-20260710-af879e5/ff-machinery-readiness/`

**Pre-existing machinery findings (from exploration):**
- Continuation engine: 7-check system, OPERATIONAL
- Governance validators: 167 total, OPERATIONAL and BLOCKING
- Skills: 123 governed, evidence-emitting, r98 registry, OPERATIONAL
- Oracle: All 20 FOSS formats VERIFIED (73/73 PASS), COMPLETE
- SAL: 14,441 facts deterministic extraction, COMPLETE
- QName: 65/66 entries — 1 intentional gap only, OPERATIONAL
- Control index: SQLite+FTS5, 11K+ rows, OPERATIONAL
- Plan lock system: session-keyed + shared locks, OPERATIONAL
- Lane contracts: PROSE ONLY in CLAUDE.md — formalization needed (TC-GFB-021)
- Gate 11: NOT code-enforced — critical gap (TC-GFB-022)
- Backfill machinery: MISSING — design needed (TC-GFB-023)
- FodtDocumentExtendedApis.cs: 2944 LOC NEW VIOLATION — remediation needed

---

## Autonomous Execution Contract

```yaml
autonomous_execution_contract:
  selected_controller: autonomous_cycle
  controller_type: autonomous_cycle
  entry_point: "python tools/supervisor/autonomous_cycle.py"
  mission_id: FF-MR-2026-001
  task_source: "plans/.claude/golden-foraging-boot.md (this file)"
  state_root: ".local/supervisor/"
  evidence_root: ".local/evidences/ff-machinery-readiness-20260710-af879e5/ff-machinery-readiness/"
  continuation_consumer: "check_continuation.py → next-work-items.json"
  stop_evaluator: "check_continuation.py (7 checks)"
  rejected_alternative: "supervisor_loop.py (120s timeout — too slow)"
  controller_locked: true
```

---

## GROUP 1: Foundation Audit

### TC-GFB-001: Run Setup + Repository Binding
**Type:** PARENT | **Status:** READY | **Owner:** machinery_governance | **Supervisor:** evidence_layer
**Requirement:** REQ-SETUP-001 | **Priority:** P0 | **Depends on:** none
**Stable key:** FF-MR-RUN-SETUP

**Objective:** Create all required run-setup artifacts in the evidence root before any audit work begins.

**Outcome:** Evidence root exists with 8 non-empty artifacts; evidence-declaration.yaml is valid YAML
referencing all artifacts; mission state is recorded; stable IDs are registered.

**Scope:**
- Allowed: `.local/evidences/ff-machinery-readiness-20260710-af879e5/ff-machinery-readiness/`
- Forbidden: `src/`, `plans/master-plan.md`, `plans/strategic/`, `.supervisor/`, `tests/`
- Preserved: All existing `.local/evidences/` from other runs (do NOT delete)

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-001-01 | Create evidence root and infrastructure artifacts | TODO |
| TC-GFB-001-02 | Write tracking and registry artifacts | TODO |
| TC-GFB-001-03 | Write evidence-declaration.yaml skeleton | TODO |

**Parent acceptance criteria:**
- All 8 setup artifacts exist at declared paths
- `evidence-declaration.yaml` passes `python -c "import yaml; yaml.safe_load(open('.local/evidences/.../evidence-declaration.yaml'))"` without error
- `mission-state.yaml` contains `mission_id: FF-MR-2026-001`
- `stable-id-registry.yaml` contains all 23 parent TC stable keys

**Integration checks:** Run `python tools/supervisor/sprint_executor_validate.py .local/evidences/.../evidence-declaration.yaml` after creation.

**Evidence required:** The 8 artifact files themselves; their paths declared in evidence-declaration.yaml

**Rollback:** Delete `.local/evidences/ff-machinery-readiness-20260710-af879e5/` and recreate

---

#### TC-GFB-001-01: Create evidence root and infrastructure artifacts
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-001
**Requirement:** REQ-SETUP-001

**Purpose:** Create the directory structure and the three foundational YAML binding files.

**Allowed:** `.local/evidences/ff-machinery-readiness-20260710-af879e5/ff-machinery-readiness/` (create)
**Forbidden:** Any other directory; do NOT overwrite existing evidence from other missions.
**Preconditions:** none

**Expected output:** Directory created; `repository-binding.yaml`, `master-plan-binding.yaml`, `audit-scope.md` written.

**Micro-steps:**

| Step | Action | Target | Expected Output |
|------|--------|--------|-----------------|
| MS-GFB-001-01-01 | Run `git rev-parse HEAD` and `git status --short` and capture output | bash | HEAD sha + status lines |
| MS-GFB-001-01-02 | Run `git log -5 --oneline` and capture | bash | 5 recent commit lines |
| MS-GFB-001-01-03 | Create directory `.local/evidences/ff-machinery-readiness-20260710-af879e5/ff-machinery-readiness/` | filesystem | directory exists |
| MS-GFB-001-01-04 | Write `repository-binding.yaml` with: head_sha, branch=main, remotes (origin+github+gitlab), untracked_files, git_status_lines | evidence root | file exists with all fields |
| MS-GFB-001-01-05 | Read first 10 lines of `plans/master-plan.md` to get version | plans/master-plan.md | version string |
| MS-GFB-001-01-06 | Write `master-plan-binding.yaml` with: mode=EXISTING_MASTER_PLAN_SURGICAL_ENHANCEMENT, path=plans/master-plan.md, version from step 5, this_plan=plans/.claude/golden-foraging-boot.md | evidence root | file exists |
| MS-GFB-001-01-07 | Write `audit-scope.md` with scope, methodology (read-only + artifact creation), non-goals (no src/ edits until Group 3, no publication) | evidence root | file exists |

**Completion check:** `ls .local/evidences/ff-machinery-readiness-20260710-af879e5/ff-machinery-readiness/` shows 3 files.

**Evidence:** paths of 3 created files

---

#### TC-GFB-001-02: Write tracking and registry artifacts
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-001
**Requirement:** REQ-SETUP-001
**Preconditions:** TC-GFB-001-01 CLOSED

**Purpose:** Write the mission state, stable ID registry, and git state snapshot.

**Allowed:** `.local/evidences/.../ff-machinery-readiness/` only

**Micro-steps:**

| Step | Action | Target | Expected Output |
|------|--------|--------|-----------------|
| MS-GFB-001-02-01 | Write `mission-state.yaml` with: mission_id=FF-MR-2026-001, phase=GROUP_1, created=2026-07-10, open_tasks=[TC-GFB-001..TC-GFB-041], completed_tasks=[] | evidence root | file with 23 open tasks |
| MS-GFB-001-02-02 | Write `stable-id-registry.yaml` with all 23 parent stable keys: FF-MR-RUN-SETUP, FF-MR-LAYER-MAP, FF-MR-QNAME-AUDIT, FF-MR-PRODUCT-CENSUS, FF-MR-SKILL-SAL-RCAL-AUDIT, FF-MR-LANE-DOWNSTREAM-AUDIT, FF-MR-AUTONOMOUS-AUDIT, FF-MR-STANDARD-DOC, FF-MR-GAP-MATRIX, FF-MR-TARGET-ARCH, FF-MR-SOLUTION-DESIGN, FF-MR-MASTER-PLAN-ENHANCE, FF-MR-LANE-CONTRACTS, FF-MR-GATE11-CONTRACT, FF-MR-BACKFILL-DESIGN, FF-MR-ISOLATION-TESTS, PILOT-FODS-DOTNET-E2E, PILOT-FODT-DOTNET-E2E, PILOT-PYTHON-STRUCTURED-E2E, PILOT-CONVERSION-EXPORT-E2E, PILOT-AUTONOMOUS-UNATTENDED, FF-MR-WAVE-DESIGN, FF-MR-EXECUTION-HANDOFF | evidence root | 23-entry YAML |
| MS-GFB-001-02-03 | Run `git status` and `git log -10 --oneline` and write output to `git-state.txt` | evidence root | file with git snapshot |

**Completion check:** `stable-id-registry.yaml` has exactly 23 entries. `git-state.txt` is non-empty.

---

#### TC-GFB-001-03: Write evidence-declaration.yaml skeleton
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-001
**Requirement:** REQ-SETUP-001
**Preconditions:** TC-GFB-001-01 and TC-GFB-001-02 CLOSED

**Purpose:** Create the YAML skeleton that all subsequent tasks will append to as they produce artifacts.

**Micro-steps:**

| Step | Action | Target | Expected Output |
|------|--------|--------|-----------------|
| MS-GFB-001-03-01 | Write `evidence-declaration.yaml` with: run_id=ff-machinery-readiness-20260710-af879e5, mission_id=FF-MR-2026-001, plan_path=plans/.claude/golden-foraging-boot.md, worker_verdict=IN_PROGRESS, evidence_paths=[list of 7 files already created], planned_work_items=[TC-GFB-001 with status=IN_PROGRESS] | evidence root | valid YAML |
| MS-GFB-001-03-02 | Validate YAML is parseable: `python -c "import yaml; yaml.safe_load(open('<path>'))"` | bash | no exception |
| MS-GFB-001-03-03 | Run `python tools/supervisor/sprint_executor_validate.py <declaration-path>` and record exit code | bash | exit 0 or log any errors |

**Completion check:** `evidence-declaration.yaml` parses without error; all 8 artifact paths exist on disk.

**Next valid task:** TC-GFB-002 (parent integration after all children CLOSED)

---

**TC-GFB-001 Integration check:** All 3 children CLOSED + 8 files exist + declaration parses → mark INTEGRATION_PENDING → VERIFIED → SCORED

---

### TC-GFB-002: System Layer Map + Prior Run Reconciliation
**Type:** PARENT | **Status:** READY | **Owner:** machinery_governance | **Supervisor:** evidence_layer
**Requirement:** REQ-LAYER-001, REQ-LAYER-002 | **Priority:** P0 | **Depends on:** TC-GFB-001
**Stable key:** FF-MR-LAYER-MAP

**Objective:** Build the 29-layer system map with real path/consumer data and reconcile any prior runs.

**Outcome:** `system-layer-map.yaml` with 29 entries; `prior-run-reconciliation.yaml` confirms no conflicting prior state.

**Scope:**
- Allowed (READ): all of `tools/`, `registry/`, `.supervisor/`, `.governance/`, `oracle/`, `src/`, `tests/`, `.local/evidences/`
- Allowed (WRITE): evidence root only
- Forbidden (WRITE): any source or config file

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-002-01 | Search for prior runs and classify artifacts | TODO |
| TC-GFB-002-02 | Inspect and map core machinery layers (L01-L09) | TODO |
| TC-GFB-002-03 | Inspect and map supervisor/governance/skill layers (L11-L16) | TODO |
| TC-GFB-002-04 | Write reconciliation and layer-map artifacts | TODO |

---

#### TC-GFB-002-01: Search for prior runs
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-002

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-002-01-01 | List all directories in `.local/evidences/` matching `ff-machinery-readiness*` | list of prior run dirs |
| MS-GFB-002-01-02 | For each prior run found: read its `evidence-declaration.yaml` and classify as STILL_VALID / STALE / SUPERSEDED / CONTRADICTED | classification per run |
| MS-GFB-002-01-03 | Write `prior-run-reconciliation.yaml` with: prior_runs=[], or list of classified runs | evidence root file |

**Completion check:** `prior-run-reconciliation.yaml` exists. If no prior runs: `prior_runs: []`.

---

#### TC-GFB-002-02: Map core machinery layers L01–L09
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-002
**Preconditions:** TC-GFB-002-01 CLOSED

**Micro-steps:**

| Step | Layer | Inspect Path | Record: paths, producers, consumers, maturity |
|------|-------|--------------|-----------------------------------------------|
| MS-GFB-002-02-01 | L01 SAL | `tools/specification-authority-layer/` | list .py files; identify run_extraction_pipeline.py, merge_sal_facts.py as producers; identify capability_feature_compiler.py as consumer |
| MS-GFB-002-02-02 | L02 QName | `registry/python-qname-structural-facts.json`, `registry/python-qname-architecture.json` | file sizes; identify tools that read them; identify validators V77/V78 as consumers |
| MS-GFB-002-02-03 | L03 Capability | `.governance/capabilities/registry.yaml` | entry count; identify feature compiler as consumer |
| MS-GFB-002-02-04 | L05 Oracle | `oracle/formats/`, `tools/oracle/execute_oracle.py` | format count; oracle status per format |
| MS-GFB-002-02-05 | L06 ProductSource | `src/python/`, `src/net/` | format dirs; file counts per format |
| MS-GFB-002-02-06 | L07 Tests | `tests/` | subdir listing; test file counts |
| MS-GFB-002-02-07 | L08 Evidence | `.local/evidences/` | run dirs; most recent evidence-review.json |
| MS-GFB-002-02-08 | L09 State | `.local/supervisor/` | key files: continuation-signal.json, active-plan-lock.json, active-continuation.json |

---

#### TC-GFB-002-03: Map supervisor/governance/skill layers L11–L16
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-002
**Preconditions:** TC-GFB-002-02 CLOSED

**Micro-steps:**

| Step | Layer | Inspect Path | Record |
|------|-------|--------------|--------|
| MS-GFB-002-03-01 | L11 Supervisor | `tools/supervisor/*.py` | key files: autonomous_cycle.py, check_continuation.py, supervisor_loop.py; note autonomous_cycle.py as primary entry point |
| MS-GFB-002-03-02 | L12 Governance | `tools/supervisor/governance_validators*.py` | validator count (expect 167); blocking vs warning |
| MS-GFB-002-03-03 | L13 Skills | `.supervisor/skill-registry.yaml` | skill count (expect 123); registry ID |
| MS-GFB-002-03-04 | L14 Backfill | search `tools/backfill/` — expected to be MISSING | record MISSING or partial |
| MS-GFB-002-03-05 | L15 Package/Consumer | search `src/python/*/pyproject.toml`, `src/net/**/*.csproj` | package file counts per format |
| MS-GFB-002-03-06 | L16 Release/Gate11 | `registry/format-registry.yaml` | look for `release_gates:` section; assess if GATE_11_READY is a tracked state |

---

#### TC-GFB-002-04: Write layer-map and claim-classification artifacts
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-002
**Preconditions:** TC-GFB-002-02 and TC-GFB-002-03 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-002-04-01 | Write `system-layer-map.yaml` with 16 layer entries (L01-L16) populated from prior children | 16-entry YAML |
| MS-GFB-002-04-02 | Write `claim-classification-register.yaml` classifying material claims from MEMORY.md: SAL=COMPLETE(14441 facts), QName=99.4%, Oracle=VERIFIED(73/73), etc. Each claim: source, claim_text, verified_against_file, classification=STILL_VALID/STALE/STRENGTHENED | evidence root |
| MS-GFB-002-04-03 | Update `evidence-declaration.yaml` to add the 3 new artifacts to evidence_paths | evidence root |

**Completion check:** `system-layer-map.yaml` has ≥16 entries. `claim-classification-register.yaml` has ≥10 entries.

---

### TC-GFB-003: QName Audit
**Type:** PARENT | **Status:** READY | **Owner:** machinery_governance | **Supervisor:** qname_layer
**Requirement:** REQ-QNAME-001, REQ-QNAME-002, REQ-QNAME-003 | **Priority:** P1 | **Depends on:** TC-GFB-002
**Stable key:** FF-MR-QNAME-AUDIT

**Objective:** Audit QName end-to-end: schema, authority, coverage, source compliance, enforcement enforcement.
Answer 8 audit questions with direct file evidence.

**Outcome:** 8 output artifacts in evidence root; `qname-verdict.md` contains one of the 7 defined verdicts.

**Scope:**
- Allowed (READ): `registry/python-qname-*.json`, `registry/python-qname-architecture.json`, `tools/supervisor/governance_validators.py`, `src/python/fods/`, `src/net/fods/`, `.governance/capabilities/`
- Allowed (WRITE): evidence root only

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-003-01 | Inspect QName schema, registry, and authority | TODO |
| TC-GFB-003-02 | Inspect QName-to-source mapping (.NET and Python) | TODO |
| TC-GFB-003-03 | Inspect QName enforcement (validators V77/V78) | TODO |
| TC-GFB-003-04 | Write QName audit artifacts and verdict | TODO |

---

#### TC-GFB-003-01: Inspect QName schema, registry, and authority
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-003

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-003-01-01 | Read `registry/python-qname-structural-facts.json` — record entry count, sample entries, authority_class distribution | entry count + authority breakdown |
| MS-GFB-003-01-02 | Read `registry/python-qname-architecture.json` — record structure (class_hierarchy vs flat list), entry count | structure + count |
| MS-GFB-003-01-03 | Search for a qname schema file: `ls registry/schemas/qname*` or grep for `qname_schema` in registry/ | schema path or MISSING |
| MS-GFB-003-01-04 | Check if qname registry has version field; check for collision detection logic (grep for "collision" in qname-related tools) | version=present/missing; collision=handled/unhandled |
| MS-GFB-003-01-05 | Record: is qname schema versioned? Is collision handling implemented? Is intentional fodt:office:body gap documented? | 3 boolean answers with evidence |

---

#### TC-GFB-003-02: Inspect QName-to-source mapping
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-003
**Preconditions:** TC-GFB-003-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-003-02-01 | In `src/python/fods/` grep for `spec_qname` across all .py files; count occurrences | count of spec_qname usages |
| MS-GFB-003-02-02 | Check if `spec_qname: ClassVar[str]` is present in FODS Python model classes (open fods_models.py or equivalent) | yes/no with file path |
| MS-GFB-003-02-03 | In `src/net/fods/` search for qname references; check if .NET type names are derived from qnames or hand-named | qname usage in .NET: yes/no |
| MS-GFB-003-02-04 | Compare Python class names to qname registry entries for 5 representative formats (fods, csv, toml, xcf, zst) | compliance: N/5 match qname |
| MS-GFB-003-02-05 | Check `.governance/capabilities/` for any capability entry linking qname → feature obligation | linkage: exists/missing |

---

#### TC-GFB-003-03: Inspect QName enforcement
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-003
**Preconditions:** TC-GFB-003-02 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-003-03-01 | Read V77 implementation in `tools/supervisor/governance_validators.py` — what exactly does it check? Does it block (FAIL) or warn? | V77 behavior: block/warn; exact condition |
| MS-GFB-003-03-02 | Read V78 implementation — same questions | V78 behavior |
| MS-GFB-003-03-03 | Check if V77/V78 are in the blocking validators list (governance_validator_runner.py expected_count assertion) | blocking: yes/no |
| MS-GFB-003-03-04 | Check if there is a mechanism for "qname gap → taskcard creation" — grep for qname_gap in tools/ | mechanism: exists/missing |
| MS-GFB-003-03-05 | Check if backfill is connected to qname: grep for qname in any backfill-related files (tools/backfill/ if exists) | connection: exists/missing/BACKFILL_LAYER_MISSING |

---

#### TC-GFB-003-04: Write QName audit artifacts and verdict
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-003
**Preconditions:** TC-GFB-003-01 through TC-GFB-003-03 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-003-04-01 | Write `qname-schema-inventory.yaml` with: registry_files, entry_count, authority_classes, versioned(yes/no), collision_handling, intentional_gaps | evidence root |
| MS-GFB-003-04-02 | Write `qname-producer-consumer-map.json` with: producers=[SAL ingestion, manual registry], consumers=[V77, V78, qname-backfill skill, source gen if any] | evidence root |
| MS-GFB-003-04-03 | Write `qname-language-mapping.json` for 5 representative formats: {format: {qname: , python_class: , dotnet_type: , compliance: }} | evidence root |
| MS-GFB-003-04-04 | Write `qname-source-compliance-matrix.json` with per-format: has_spec_qname_in_source(bool), enforced_by_v77(bool), enforced_by_v78(bool) | evidence root |
| MS-GFB-003-04-05 | Write `qname-enforcement-gap-register.yaml` listing any formats where qname exists in registry but is NOT present in source | evidence root |
| MS-GFB-003-04-06 | Write `qname-verdict.md` with the verdict and evidence chain | evidence root |
| MS-GFB-003-04-07 | Write `qname-authority-report.md` answering all 8 audit questions explicitly | evidence root |
| MS-GFB-003-04-08 | Write `qname-idempotency-results.json`: run the same qname inspection twice (re-read same files), confirm same outputs | evidence root |

**Acceptance:** 8 output files exist; `qname-verdict.md` contains exactly one verdict token from the defined set.

---

### TC-GFB-004: Product Source Census
**Type:** PARENT | **Status:** READY | **Owner:** machinery_governance | **Supervisor:** source_quality_layer
**Requirement:** REQ-PROD-001, REQ-PROD-002 | **Priority:** P1 | **Depends on:** TC-GFB-003
**Stable key:** FF-MR-PRODUCT-CENSUS

**Objective:** Complete census of all products under `src/`. Audit .NET and Python separately.
Specifically document FodtDocumentExtendedApis.cs (2944 LOC new violation).

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-004-01 | Inspect Python FOSS products (20 formats) | TODO |
| TC-GFB-004-02 | Inspect .NET commercial products (10 formats) | TODO |
| TC-GFB-004-03 | Inspect skeleton/missing products and violations | TODO |
| TC-GFB-004-04 | Write product census artifacts | TODO |

---

#### TC-GFB-004-01: Inspect Python FOSS products
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-004

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-004-01-01 | List all directories in `src/python/` | 20 format dirs + any shared/common dirs |
| MS-GFB-004-01-02 | For each of 20 Python format dirs: count .py files, identify parser/writer/models files by name | per-format file inventory |
| MS-GFB-004-01-03 | Check 5 representative Python formats (fods, csv, toml, xcf, zst) for module separation: is parser separate from writer from models? | separation: yes/partial/no per format |
| MS-GFB-004-01-04 | Check `registry/source-structure-baseline.json` — how many Python files have baseline_loc_cap entries? How many are in known_violations? | baseline entries count; violations count |
| MS-GFB-004-01-05 | Read oracle verdict for all 20 formats (check oracle/formats/*/oracle-package.yaml status field) | 20 VERIFIED, 0 not-VERIFIED |

---

#### TC-GFB-004-02: Inspect .NET commercial products
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-004
**Preconditions:** TC-GFB-004-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-004-02-01 | List all directories in `src/net/` | format dirs with file counts |
| MS-GFB-004-02-02 | For FODS .NET: count .cs files; check FodsDocument.cs LOC (expect ~907); check baseline_loc_cap in baseline JSON | FODS .NET: file count, LOC, cap |
| MS-GFB-004-02-03 | For FODT .NET: count .cs files; read FodtDocumentExtendedApis.cs — confirm 2944 LOC; check if it has a baseline_loc_cap entry | FODT: file count, violation confirmed/denied |
| MS-GFB-004-02-04 | For CSV .NET: count .cs files; check for CsvDocumentAnalytics.cs LOC | CSV .NET: file count, LOC |
| MS-GFB-004-02-05 | Check .NET build files: does each significant format have a .csproj? Does it compile? (read csproj, check TargetFramework) | csproj present: yes/no per format |

---

#### TC-GFB-004-03: Inspect skeleton/missing products and violations
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-004
**Preconditions:** TC-GFB-004-02 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-004-03-01 | Identify .NET formats with ≤3 .cs files (skeleton) — list them | skeleton list: ndjson, tsv, zst, html, md, txt, netpbm (expect ~7) |
| MS-GFB-004-03-02 | Confirm 4 formats with no products at all (ora, pam, xpm, zpaq) | 4 confirmed missing |
| MS-GFB-004-03-03 | Read `registry/source-structure-baseline.json` — count `new_violation_detected` category entries | violation count |
| MS-GFB-004-03-04 | Read FodtDocumentExtendedApis.cs first 30 lines — what classes/regions are in it? Assess decomposition difficulty | class names; decomposition assessment |

---

#### TC-GFB-004-04: Write product census artifacts
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-004
**Preconditions:** TC-GFB-004-01 through TC-GFB-004-03 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-004-04-01 | Write `product-inventory.json` with all products: {format, language, source_root, file_count, oracle_status, gate_status} | evidence root |
| MS-GFB-004-04-02 | Write `dotnet-product-audit.json` with per-.NET-format: architecture_classification, monolith_risk, qname_usage, build_status, test_count | evidence root |
| MS-GFB-004-04-03 | Write `python-product-audit.json` with per-Python-format: module_separation, oracle_depth, spec_qname_present, package_present | evidence root |
| MS-GFB-004-04-04 | Write `monolith-register.yaml` listing files >800 LOC: FodtDocumentExtendedApis.cs(2944), FodsDocument.cs(907), and any Python files | evidence root |
| MS-GFB-004-04-05 | Write `product-gate-readiness-matrix.json` per product: {gates_1_to_10: pass/fail/unknown, gate_11: not_ready/ready/pending_review} | evidence root |

---

### TC-GFB-005: Skill + SAL + RCAL Audit
**Type:** PARENT | **Status:** READY | **Owner:** machinery_governance | **Supervisor:** sal_layer
**Requirement:** REQ-SKILL-001, REQ-SAL-001, REQ-RCAL-001 | **Priority:** P1 | **Depends on:** TC-GFB-004
**Stable key:** FF-MR-SKILL-SAL-RCAL-AUDIT

**Objective:** Classify all 123 skills by maturity; verify SAL fact provenance; assess capability gap queue executability.

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-005-01 | Sample and classify skills by maturity | TODO |
| TC-GFB-005-02 | Audit SAL fact provenance and connections | TODO |
| TC-GFB-005-03 | Audit capability/RCAL gap queue | TODO |
| TC-GFB-005-04 | Write SAL/skill/RCAL artifacts | TODO |

---

#### TC-GFB-005-01: Sample and classify skills by maturity
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-005

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-005-01-01 | Read `.supervisor/skill-registry.yaml` — count total skills (expect 123), read registry_id | count + registry_id |
| MS-GFB-005-01-02 | Sample 10 skills across different categories: read their full YAML block (description, preconditions, outputs, validators) | 10 skill details |
| MS-GFB-005-01-03 | For each sampled skill: does it have explicit `validators:` field? Does it reference `gap_ledger_ref_exists`? | skill validation presence |
| MS-GFB-005-01-04 | Check if `/add-python-api` and `/add-dotnet-api` skills emit evidence (grep for evidence_paths or evidence_root in their definition) | evidence emission: yes/no |
| MS-GFB-005-01-05 | Grep `tools/` for any direct source edits that bypass skill invocation (look for patterns like `write_python_source` outside of skills) | bypass paths: list or NONE |
| MS-GFB-005-01-06 | Check for missing skill gaps: is there a `/add-dotnet-conversion` or `/add-python-conversion` skill? Is there a `/design-architecture-profile` skill? | gap list |

---

#### TC-GFB-005-02: Audit SAL fact provenance and connections
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-005

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-005-02-01 | Check if `.local/sal-output/sal-facts-latest.json` exists; read entry count (expect 14,441) | count + file size |
| MS-GFB-005-02-02 | Sample 10 facts from sal-facts-latest.json: check each for `authority_class`, `source_location`, `fact_id` stability | provenance: all present / some missing |
| MS-GFB-005-02-03 | Check for manually-seeded facts: grep for "manual" or "seeded" in SAL files; check `registry/python-qname-structural-facts.json` authority_classes | manual seed count |
| MS-GFB-005-02-04 | Verify SAL→qname connection: does any SAL fact have a `qname` field or is there a mapping table? | connection: exists/missing |
| MS-GFB-005-02-05 | Check negative controls: grep for AI_DRAFT_UNVERIFIED in oracle packages — does this block PASS? | negative control: working/missing |

---

#### TC-GFB-005-03: Audit capability gap queue
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-005

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-005-03-01 | Read `.governance/capabilities/registry.yaml` — count active entries (expect 120) | count |
| MS-GFB-005-03-02 | Check if capability entries link to SAL facts: sample 5 entries, look for `spec_fact_refs` or `sal_fact_id` | linkage: present/missing |
| MS-GFB-005-03-03 | Check `tools/supervisor/capability_feature_compiler.py` — what does it produce? Read first 50 lines | output artifact type |
| MS-GFB-005-03-04 | Check if feature compiler output is consumed: grep for capability_feature_compiler output path in other tools | consumer: identified / QUEUE_NO_EXECUTOR |
| MS-GFB-005-03-05 | Verify ora/pam/xpm/zpaq are OBLIGATION_CREATED (not FULL_PARITY): read their capability entries | status: OBLIGATION_CREATED confirmed |

---

#### TC-GFB-005-04: Write SAL/skill/RCAL artifacts
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-005
**Preconditions:** TC-GFB-005-01 through TC-GFB-005-03 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-005-04-01 | Write `skill-inventory.yaml` with categories: PRODUCTION_READY, ACTIVE_BUT_INCOMPLETE, DOCUMENTATION_ONLY, BYPASSED; place sampled skills | evidence root |
| MS-GFB-005-04-02 | Write `skill-gap-register.yaml` listing missing skills found in MS-GFB-005-01-06 | evidence root |
| MS-GFB-005-04-03 | Write `sal-system-inventory.yaml`: fact_count, authority_class_distribution, manual_seed_count, provenance_complete(bool), qname_connection(bool) | evidence root |
| MS-GFB-005-04-04 | Write `sal-manual-seed-register.yaml` listing any manually-seeded facts found | evidence root (may be empty) |
| MS-GFB-005-04-05 | Write `rcal-system-inventory.yaml`: capability_count, sal_linkage(bool), gap_queue_executable(bool), feature_compiler_consumer_identified(bool) | evidence root |
| MS-GFB-005-04-06 | Write `capability-gap-queue-audit.json`: {executable: bool, consumer: identified/missing, formats_blocked: [ora,pam,xpm,zpaq]} | evidence root |
| MS-GFB-005-04-07 | Write `skill-verdict.md` and `sal-verdict.md` and `rcal-verdict.md` | evidence root (3 files) |

---

### TC-GFB-006: Lane Isolation + Downstream Layer Audit
**Type:** PARENT | **Status:** READY | **Owner:** machinery_governance | **Supervisor:** lane_layer
**Requirement:** REQ-LANE-001, REQ-LANE-002 | **Priority:** P1 | **Depends on:** TC-GFB-005
**Stable key:** FF-MR-LANE-DOWNSTREAM-AUDIT

**Objective:** Document current lane isolation state (13 lanes) and audit downstream layer connections.
Apply rule: "An output with no consumer is not integrated."

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-006-01 | Audit downstream layers (feature compiler through consumer) | TODO |
| TC-GFB-006-02 | Map current 13 lanes and identify collision risks | TODO |
| TC-GFB-006-03 | Write lane and downstream artifacts | TODO |

---

#### TC-GFB-006-01: Audit downstream layers
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-006

**Micro-steps:**

| Step | Layer | Inspect | Record |
|------|-------|---------|--------|
| MS-GFB-006-01-01 | Feature compiler | `tools/supervisor/capability_feature_compiler.py` (canonical) vs `tools/capability_layer/capability_to_feature_compiler.py` (planning tool) | purpose, output artifact, consumer |
| MS-GFB-006-01-02 | Architecture mapper | `grep -r "architecture.*map\|arch.*profile" tools/` | exists as code / MISSING |
| MS-GFB-006-01-03 | Object-model mapper | `grep -r "object.*model.*map\|model.*map" tools/` | exists as code / MISSING |
| MS-GFB-006-01-04 | Source-layout generator | `grep -r "layout.*gen\|source.*layout" tools/` | exists as code / MISSING |
| MS-GFB-006-01-05 | .NET source generator | `grep -r "dotnet.*gen\|net.*source.*gen\|generate.*csharp" tools/` | exists / all .NET source is hand-written |
| MS-GFB-006-01-06 | Python source generator | `grep -r "python.*gen\|generate.*python" tools/` | exists / all Python source is hand-written |
| MS-GFB-006-01-07 | Product-deepening selector | read how `next-work-items.json` is produced by autonomous_cycle.py | selector logic |
| MS-GFB-006-01-08 | Package generator | `grep -r "package.*gen\|build.*package\|twine\|nuget" tools/` | exists / MISSING |
| MS-GFB-006-01-09 | Consumer-test generator | `grep -r "consumer.*gen\|generate.*consumer" tools/` | exists / MISSING |

---

#### TC-GFB-006-02: Map current 13 lanes
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-006
**Preconditions:** TC-GFB-006-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-006-02-01 | Read CLAUDE.md — find all prose-defined lane rules (grep for "lane" in CLAUDE.md and AGENTS.md) | lane prose rules count |
| MS-GFB-006-02-02 | Check `.governance/lanes/` — does it exist? Any formal lane contract files? | formal contracts: yes/MISSING |
| MS-GFB-006-02-03 | For each of 13 required lanes: determine current state: FORMALIZED (contract file) / PROSE_ONLY (CLAUDE.md rule) / MISSING | 13 lane states |
| MS-GFB-006-02-04 | Identify collision risks: which lanes share `.local/supervisor/` as mutable state? Which lanes share `reports/supervisor/`? | collision risk: at least machinery/product share state |
| MS-GFB-006-02-05 | Check if any task ownership enforcement exists: grep for "lane_id" or "owner" in continuation-signal.json or next-work-items.json | ownership enforcement: present/missing |

---

#### TC-GFB-006-03: Write lane and downstream artifacts
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-006
**Preconditions:** TC-GFB-006-01 and TC-GFB-006-02 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-006-03-01 | Write `downstream-layer-inventory.yaml` with 9 downstream layers, each noting: exists(bool), consumer(identified/missing), integrated(bool) | evidence root |
| MS-GFB-006-03-02 | Write `downstream-producer-consumer-map.json` as nested JSON: producer→output→consumer chains | evidence root |
| MS-GFB-006-03-03 | Write `downstream-gap-register.yaml` listing layers that are MISSING or have no consumer (critical gaps for TC-GFB-011) | evidence root |
| MS-GFB-006-03-04 | Write `current-lane-map.yaml` with 13 lane entries: {lane_id, state: FORMALIZED/PROSE_ONLY/MISSING, collision_risk: HIGH/MED/LOW} | evidence root |
| MS-GFB-006-03-05 | Write `lane-collision-risk-register.yaml` with specific collision scenarios | evidence root |
| MS-GFB-006-03-06 | Write `lane-verdict.md` | evidence root |

---

### TC-GFB-007: Autonomous Supervisor + Continuation Audit
**Type:** PARENT | **Status:** READY | **Owner:** machinery_governance | **Supervisor:** state_layer
**Requirement:** REQ-AUTO-001, REQ-AUTO-002 | **Priority:** P1 | **Depends on:** TC-GFB-006
**Stable key:** FF-MR-AUTONOMOUS-AUDIT

**Objective:** Audit the 7-check continuation system and Gate 11 enforcement gap. Answer 8 audit
questions with direct evidence.

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-007-01 | Inspect continuation system state and stale signal | TODO |
| TC-GFB-007-02 | Inspect Gate 11 enforcement (code vs prose) | TODO |
| TC-GFB-007-03 | Write autonomous system artifacts | TODO |

---

#### TC-GFB-007-01: Inspect continuation system state
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-007

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-007-01-01 | Read `.local/supervisor/continuation-signal.json` — all fields; note session_id=null (WARN_LEGACY), stale date | full field inventory |
| MS-GFB-007-01-02 | Read `.local/supervisor/active-plan-lock.json` — status, session_id, plan_path | lock status + old session_id |
| MS-GFB-007-01-03 | Run `python tools/supervisor/check_continuation.py 2>&1` and capture output (exit code + JSON) | current verdict |
| MS-GFB-007-01-04 | Read check_continuation.py — identify the 7 checks; read Check 2 (CCI-MVP isolation); what happens when session_id=null? | 7 check names; null handling |
| MS-GFB-007-01-05 | Read check_continuation.py lines handling MAX_ITERATIONS — does it reset to 0? | confirmed/denied |
| MS-GFB-007-01-06 | Check if next-work-items.json exists and contains real product work (not just governance tasks) | product work present: yes/no |

---

#### TC-GFB-007-02: Inspect Gate 11 enforcement
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-007
**Preconditions:** TC-GFB-007-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-007-02-01 | Grep `registry/format-registry.yaml` for "gate_11" or "release_gate" — what fields exist per format? | gate fields in registry |
| MS-GFB-007-02-02 | Grep `tools/supervisor/check_continuation.py` for "gate_11" or "GATE_11" — is there any code path? | code path: exists/MISSING |
| MS-GFB-007-02-03 | Grep `tools/supervisor/autonomous_cycle.py` for "gate_11" — does it emit GATE_11_READY? | emission: exists/MISSING |
| MS-GFB-007-02-04 | Check `registry/gate-states.yaml` — does it exist? | state registry: exists/MISSING |
| MS-GFB-007-02-05 | Record: what currently happens when a product satisfies Gates 1-10? Does anything stop it? | answer: nothing stops it (confirmation of gap) |

---

#### TC-GFB-007-03: Write autonomous system artifacts
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-007
**Preconditions:** TC-GFB-007-01 and TC-GFB-007-02 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-007-03-01 | Write `autonomous-system-inventory.yaml`: controller=autonomous_cycle, 7 checks named, next_work_source, stale_signal(bool), session_null_risk(LOW/MED/HIGH) | evidence root |
| MS-GFB-007-03-02 | Write `continuation-consumer-proof.json`: does next-work-items.json get consumed? What reads it? | consumer chain documented |
| MS-GFB-007-03-03 | Write `autonomous-next-work-selection-audit.json`: does selector prefer governance work vs product work? evidence from next-work-items.json content | audit result |
| MS-GFB-007-03-04 | Write `autonomous-gate11-stop-proof.json`: gate11_code_path_exists=false, gate11_is_prose_only=true, gap_confirmed=true — this confirms GAP-GATE11-NOT-GOVERNED | evidence root |
| MS-GFB-007-03-05 | Write `stale-evidence-register.yaml`: list continuation-signal.json as stale (>7 days), recommended action=reset_before_pilot_H | evidence root |
| MS-GFB-007-03-06 | Write `autonomous-verdict.md` answering all 8 audit questions | evidence root |

---

## GROUP 2: Design + Standards

### TC-GFB-010: Spec-to-Format-Hacker Standard
**Type:** PARENT | **Status:** READY | **Owner:** machinery_governance | **Supervisor:** governance_layer
**Requirement:** REQ-STD-001 | **Priority:** P2 | **Depends on:** TC-GFB-003, TC-GFB-004, TC-GFB-005
**Stable key:** FF-MR-STANDARD-DOC

**Objective:** Extend `docs/code-quality/production-library-standard-v2.md` with any missing sections.
Do NOT create a competing document.

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-010-01 | Read v2 standard and identify gaps against required sections | TODO |
| TC-GFB-010-02 | Write missing sections into v2 standard (or addendum) | TODO |
| TC-GFB-010-03 | Write production-code-prohibited-patterns.yaml | TODO |

---

#### TC-GFB-010-01: Identify gaps in v2 standard
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-010

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-010-01-01 | Read `docs/code-quality/production-library-standard-v2.md` (all sections) | list of existing sections |
| MS-GFB-010-01-02 | Cross-reference against required sections from REQ-STD-001: QName source organization, .NET one-principal-type-per-file, Python py.typed, parser/model/writer separation, preservation/round-trip | gap list: present/missing per required section |
| MS-GFB-010-01-03 | Decide: extend v2 in-place, OR create `docs/code-quality/spec-to-format-hacker-standard.md` as new doc (choose: in-place extension unless fundamentally different content needed) | decision recorded |

---

#### TC-GFB-010-02: Write missing sections
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-010
**Preconditions:** TC-GFB-010-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-010-02-01 | For each missing section identified: write one section at a time into the chosen file | sections added |
| MS-GFB-010-02-02 | After each section: verify the file is still valid Markdown and no existing content was displaced | no content lost |
| MS-GFB-010-02-03 | Add QName Source Organization Rules section if missing: spec_qname ClassVar required, canonical names, no format-prefix in core, facade only in Compat/ | section present |
| MS-GFB-010-02-04 | Add .NET Standard section if missing: solution/project structure, one principal type per file, nullable reference types, stream ownership, NuGet packaging | section present |
| MS-GFB-010-02-05 | Add Python Standard section if missing: src/ layout, bounded modules <800 LOC, dataclasses, py.typed, pyproject.toml, wheel/sdist | section present |

**Forbidden:** Do NOT delete or overwrite existing valid content in v2 standard.

---

#### TC-GFB-010-03: Write prohibited patterns artifact
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-010
**Preconditions:** TC-GFB-010-02 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-010-03-01 | Write `production-code-prohibited-patterns.yaml` in evidence root with: god_classes, god_modules, parser_model_writer_colocation, generic_dict_property_bags, untyped_public_api, hardcoded_demo_behavior, stubs_marked_as_complete, dead_code, ghost_features | evidence root file |
| MS-GFB-010-03-02 | For each prohibited pattern: add example (what it looks like) and validator (which validator catches it, or "MISSING" if none) | patterns with enforcement status |

---

### TC-GFB-011: Complete Gap Matrix + Root Cause Map
**Type:** PARENT | **Status:** READY | **Owner:** machinery_governance | **Supervisor:** all
**Requirement:** REQ-GAP-001 | **Priority:** P2 | **Depends on:** TC-GFB-003, TC-GFB-004, TC-GFB-005, TC-GFB-006, TC-GFB-007
**Stable key:** FF-MR-GAP-MATRIX

**Objective:** Synthesize all Group 1 audit findings into a complete gap matrix and root-cause register.
Confirm or refute 10 expected gaps. Classify all by severity.

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-011-01 | Compile all gaps from Group 1 audit outputs | TODO |
| TC-GFB-011-02 | Build root-cause register | TODO |
| TC-GFB-011-03 | Write gap matrix artifacts | TODO |

---

#### TC-GFB-011-01: Compile gaps
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-011

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-011-01-01 | Read all `*-gap-register.yaml` files from evidence root (qname, downstream, skill) | gap list from prior audits |
| MS-GFB-011-01-02 | Confirm or refute each of 10 expected gaps: GAP-BACKFILL-MISSING, GAP-LANE-CONTRACTS-MISSING, GAP-GATE11-NOT-GOVERNED, GAP-ARCH-MAPPER-MISSING, GAP-SOURCE-GEN-MISSING, GAP-FODT-MONOLITH, GAP-NET-SHALLOW, GAP-CONVERSION-UNPROVEN, GAP-QNAME-NET-UNCONNECTED, GAP-CONTINUATION-STALE | confirmed/refuted per gap with evidence ref |
| MS-GFB-011-01-03 | Assign severity to each confirmed gap: CRITICAL (blocks autonomous deepening), HIGH (blocks Gate 11), MEDIUM (quality issue), LOW (documentation) | severity per gap |
| MS-GFB-011-01-04 | Identify any NEW gaps discovered in Group 1 not in the expected list | new gap list |
| MS-GFB-011-01-05 | Assign stable gap IDs: GAP-BACKFILL-MISSING, GAP-LANE-CONTRACTS-MISSING, etc. (no random IDs) | stable gap IDs assigned |

---

#### TC-GFB-011-02: Build root-cause register
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-011
**Preconditions:** TC-GFB-011-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-011-02-01 | For each CRITICAL/HIGH gap: write root_cause record with: root_cause_id, symptom, affected_layers[], first_failing_boundary, immediate_cause, structural_cause, why_previous_hardening_missed_it | root-cause entries |
| MS-GFB-011-02-02 | Map multiple gaps to shared root causes where applicable (e.g., GAP-ARCH-MAPPER-MISSING and GAP-SOURCE-GEN-MISSING may share RC-NO-CODE-GENERATION root cause) | deduplicated root causes |
| MS-GFB-011-02-03 | For each root cause: define machinery_fix (what TC-GFB-0xx implements it) and prevention_test (what test in TC-GFB-024 covers it) | fix+prevention mapped |

---

#### TC-GFB-011-03: Write gap matrix artifacts
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-011
**Preconditions:** TC-GFB-011-01 and TC-GFB-011-02 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-011-03-01 | Write `complete-gap-matrix.yaml` with all gaps, severity, root_cause_id, blocks_autonomous_deepening, blocks_gate11, stable_taskcard_ids | evidence root |
| MS-GFB-011-03-02 | Write `complete-gap-matrix.csv` (same content in CSV format for spreadsheet review) | evidence root |
| MS-GFB-011-03-03 | Write `root-cause-register.yaml` with root cause entries | evidence root |
| MS-GFB-011-03-04 | Write `critical-gap-summary.md` — prose summary of CRITICAL gaps and their impact on autonomous deepening | evidence root |
| MS-GFB-011-03-05 | Write `duplicate-gap-detection.json` — list any gaps that appear in multiple audit registers, merged under one canonical ID | evidence root |
| MS-GFB-011-03-06 | Write `self-hardening-delta-report.md` — summarize what changed in this mission vs prior state (per claim-classification-register.yaml) | evidence root |

---

### TC-GFB-012: Target Architecture
**Type:** PARENT | **Status:** READY | **Owner:** machinery_governance | **Supervisor:** architecture_layer
**Requirement:** REQ-ARCH-001 | **Priority:** P2 | **Depends on:** TC-GFB-011
**Stable key:** FF-MR-TARGET-ARCH

**Objective:** Document the complete target architecture from SPEC ACQUISITION through GATE 11.
Define 5 architecture profiles and the gate11-state-contract.yaml (preliminary).

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-012-01 | Design authority-to-source chain for each stage | TODO |
| TC-GFB-012-02 | Define 5 architecture profiles | TODO |
| TC-GFB-012-03 | Write architecture artifacts | TODO |

---

#### TC-GFB-012-01: Design authority-to-source chain
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-012

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-012-01-01 | For each of 17 stages in the SPEC→GATE-11 chain: document (producer, input, output artifact, consumer, enforcement mechanism, failure handling) | stage-by-stage table |
| MS-GFB-012-01-02 | Identify which stages are IMPLEMENTED, which are MISSING, which are PARTIAL | maturity per stage |
| MS-GFB-012-01-03 | Map gaps from TC-GFB-011 to the stage where they first fail (first_failing_boundary) | gap→stage mapping |

---

#### TC-GFB-012-02: Define architecture profiles
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-012
**Preconditions:** TC-GFB-012-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-012-02-01 | Define ODF_RICH profile: required layers (workbook/document/body/paragraph/table), namespace depth, parser/model/writer separation required, roundtrip required | profile YAML |
| MS-GFB-012-02-02 | Define ODF_SIMPLE profile (ABW): lighter hierarchy, same separation required | profile YAML |
| MS-GFB-012-02-03 | Define TABULAR profile (CSV/TSV/NDJSON/TOML): flat model, no hierarchy, compact modules justified | profile YAML |
| MS-GFB-012-02-04 | Define SPREADSHEET profile (GNUMERIC/DIF/SYLK): medium hierarchy, no strict ODF namespace required | profile YAML |
| MS-GFB-012-02-05 | Define BINARY_CODEC profile (QOI/XCF/PBM/PGM/PPM/ZST): compact design justified, no hierarchy, stream ownership critical | profile YAML |

---

#### TC-GFB-012-03: Write architecture artifacts
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-012
**Preconditions:** TC-GFB-012-01 and TC-GFB-012-02 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-012-03-01 | Write `format-factory-target-architecture.md` (comprehensive architecture document) | evidence root |
| MS-GFB-012-03-02 | Write `authority-to-source-chain.yaml` (machine-readable stage chain) | evidence root |
| MS-GFB-012-03-03 | Write `target-layer-contracts.yaml` (contracts for each architecture stage) | evidence root |
| MS-GFB-012-03-04 | Write `gate11-state-contract.yaml` (preliminary version — TC-GFB-022 implements it): criteria list, per-product scope, auto-stop required | evidence root |

---

### TC-GFB-013: Machinery Solution Design
**Type:** PARENT | **Status:** READY | **Owner:** machinery_governance | **Supervisor:** all
**Requirement:** REQ-SOL-001 | **Priority:** P2 | **Depends on:** TC-GFB-012
**Stable key:** FF-MR-SOLUTION-DESIGN

**Objective:** For each CRITICAL/HIGH gap, evaluate ≥3 solutions, score them, select best, record rationale.

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-013-01 | Design solutions for GAP-BACKFILL-MISSING and GAP-LANE-CONTRACTS-MISSING | TODO |
| TC-GFB-013-02 | Design solutions for GAP-GATE11-NOT-GOVERNED and GAP-FODT-MONOLITH | TODO |
| TC-GFB-013-03 | Write solution artifacts | TODO |

---

#### TC-GFB-013-01: Solutions for backfill + lane contracts
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-013

**For GAP-BACKFILL-MISSING — evaluate:**
- Option A: Minimal — add migration-map.schema.yaml + dry_run_migration.py (read-only preview)
- Option B: Structural — add full migration engine with governed rewrite via skill
- Option C: Redesign — generate source from scratch from qname+capability (no migration needed)

**For GAP-LANE-CONTRACTS-MISSING — evaluate:**
- Option A: Add `.governance/lanes/lane-contracts.yaml` YAML file only
- Option B: Add YAML + V168 validator that checks declarations reference a valid lane
- Option C: Full lane enforcement with ownership locks in check_continuation.py

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-013-01-01 | Score each backfill option (A/B/C) on 13 dimensions (1–5 each): root-cause-coverage, durability, qname-alignment, repeatability, idempotency, autonomy, testability, migration-safety, behavior-preservation, scale, cost, risk, rollback | scorecard table |
| MS-GFB-013-01-02 | Select backfill solution (expected: Option A for this plan, Option B as Wave 2 extension) and record rationale | selection + rationale |
| MS-GFB-013-01-03 | Score each lane contract option (A/B/C) on same 13 dimensions | scorecard table |
| MS-GFB-013-01-04 | Select lane contract solution (expected: Option B for this plan) and record rationale | selection + rationale |

---

#### TC-GFB-013-02: Solutions for Gate 11 + FODT monolith
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-013

**For GAP-GATE11-NOT-GOVERNED — evaluate:**
- Option A: Add `registry/gate-states.yaml` + Check 8 in check_continuation.py (code-enforced)
- Option B: Add gate-states.yaml only (registry, no code enforcement yet)
- Option C: Full per-product gate tracking with autonomous cycle emitting GATE_11_READY verdict

**For GAP-FODT-MONOLITH (FodtDocumentExtendedApis.cs 2944 LOC) — evaluate:**
- Option A: Freeze as known_violation at 2944 LOC cap (non-blocking warning)
- Option B: Decompose into separate files in Pilot B (TC-GFB-031)
- Option C: Require decomposition before Pilot B starts

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-013-02-01 | Score Gate 11 options (A/B/C) | scorecard |
| MS-GFB-013-02-02 | Select Gate 11 solution (expected: Option C — full code enforcement) and rationale | selection |
| MS-GFB-013-02-03 | Score FODT monolith options | scorecard |
| MS-GFB-013-02-04 | Select FODT monolith solution (expected: Option B — decompose during Pilot B) and rationale | selection |

---

#### TC-GFB-013-03: Write solution artifacts
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-013
**Preconditions:** TC-GFB-013-01 and TC-GFB-013-02 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-013-03-01 | Write `machinery-solution-options.md` with all options evaluated | evidence root |
| MS-GFB-013-03-02 | Write `machinery-solution-scorecard.yaml` with numeric scores per option per dimension | evidence root |
| MS-GFB-013-03-03 | Write `selected-machinery-healing-design.md` with selected solution per gap + rationale + implementation pointer (TC-GFB-0xx) | evidence root |

---

## GROUP 3: Hardening

### TC-GFB-020: Master Plan Surgical Enhancement
**Type:** PARENT | **Status:** READY | **Owner:** machinery_governance | **Supervisor:** plan_authority
**Requirement:** REQ-MPLAN-001 | **Priority:** P3 | **Depends on:** TC-GFB-013
**Stable key:** FF-MR-MASTER-PLAN-ENHANCE

**Objective:** Surgically update `plans/master-plan.md` with audit findings. Add MR-0–MR-20 gates table.
Add FodtDocumentExtendedApis decomposition taskcard. Update Gate 11 status sections. Preserve all valid content.

**Scope:**
- Allowed WRITE: `plans/master-plan.md` ONLY
- Forbidden: `plans/strategic/spec-to-feature-radical-correction-plan.md`, `plans/strategic/snoopy-juggling-seal.md`, `src/`, `.supervisor/`
- Preserved: all verified Gate status sections, all §1-§25 architecture content, all existing taskcards that are CLOSED

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-020-01 | Read and section-inventory master-plan.md | TODO |
| TC-GFB-020-02 | Add machinery readiness gates (MR-0 through MR-20) | TODO |
| TC-GFB-020-03 | Add gap taskcards for CRITICAL/HIGH gaps from TC-GFB-011 | TODO |
| TC-GFB-020-04 | Update stale Gate 11 and product status sections | TODO |
| TC-GFB-020-05 | Validate and confirm lifecycle_audit.py compatibility | TODO |

---

#### TC-GFB-020-01: Read and section-inventory master-plan.md
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-020

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-020-01-01 | Read `plans/master-plan.md` lines 1–200 (header + context) | section 1 content |
| MS-GFB-020-01-02 | Read lines 201–600 (phases/stages 1–10 or equivalent) | section 2 content |
| MS-GFB-020-01-03 | Read lines 601–1000 (phases 11–20 or equivalent) | section 3 content |
| MS-GFB-020-01-04 | Read lines 1001–1400 | section 4 |
| MS-GFB-020-01-05 | Read lines 1401+ (gates, closure, taskcard table) | section 5 + taskcard table |
| MS-GFB-020-01-06 | Record: does MR-gate section exist? Does FodtDocumentExtendedApis taskcard exist? What is current stale content? | inventory notes |

---

#### TC-GFB-020-02: Add machinery readiness gates
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-020
**Preconditions:** TC-GFB-020-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-020-02-01 | Locate the gates section in master-plan.md (search for "Gate" headings) | section line number |
| MS-GFB-020-02-02 | If MR-0 through MR-20 gates table is absent: insert after the product gates section | table inserted |
| MS-GFB-020-02-03 | If table already exists: update entries for MR-11 (Lane Isolation → TC-GFB-021), MR-12 (Autonomous → TC-GFB-022), MR-13 (Backfill → TC-GFB-023), MR-14 (Tests → TC-GFB-024) | entries updated |
| MS-GFB-020-02-04 | Confirm neighboring content is intact: no accidental deletion | surrounding lines verified |

---

#### TC-GFB-020-03: Add gap taskcards for CRITICAL/HIGH gaps
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-020
**Preconditions:** TC-GFB-020-01 CLOSED, TC-GFB-011 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-020-03-01 | For GAP-FODT-MONOLITH (FodtDocumentExtendedApis.cs 2944 LOC): find appropriate section in master-plan.md; add taskcard: TC-FODT-DECOMP-001 with status=OPEN, description=Decompose FodtDocumentExtendedApis.cs per §8.1 healing protocol | taskcard added |
| MS-GFB-020-03-02 | For any other CRITICAL gaps confirmed in TC-GFB-011 (GAP-ARCH-MAPPER-MISSING, GAP-SOURCE-GEN-MISSING if confirmed): add taskcards with status=OPEN | taskcards added if needed |
| MS-GFB-020-03-03 | Update the master-plan.md taskcard status table to include new taskcards in `TC-ID \| STATUS` format | table updated |
| MS-GFB-020-03-04 | Re-read modified section to verify no adjacent content was displaced | no regression |

---

#### TC-GFB-020-04: Update stale status sections
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-020
**Preconditions:** TC-GFB-020-01 and TC-GFB-004 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-020-04-01 | Find Gate 11 section in master-plan.md; update FODS .NET status to reflect oracle D1/D2 VERIFIED (8/8) | status updated |
| MS-GFB-020-04-02 | Update FODT .NET status to reflect FodtDocumentExtendedApis.cs new violation (2944 LOC) | violation noted |
| MS-GFB-020-04-03 | Update Oracle section to reflect all 20 FOSS formats VERIFIED (73/73 PASS) if not current | oracle status updated |
| MS-GFB-020-04-04 | Add note: continuation-signal.json stale as of 2026-07-04 — reset before Pilot H | stale note added |

---

#### TC-GFB-020-05: Validate lifecycle_audit.py compatibility
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-020
**Preconditions:** TC-GFB-020-02 through TC-GFB-020-04 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-020-05-01 | Run `python tools/supervisor/lifecycle_audit.py --mission-id FF-MR-2026-001 --sprint-id TC-GFB-020 2>&1` | exit 0 or error details |
| MS-GFB-020-05-02 | If error: identify which table format broke (must be `\| TC-ID \| STATUS \|` 2-column format); fix | fixed or N/A |
| MS-GFB-020-05-03 | Confirm master-plan.md still parses as valid Markdown (no unclosed code fences) | valid |

**Rollback:** `git checkout plans/master-plan.md` restores prior version if enhancement breaks the file.

---

### TC-GFB-021: Lane Contracts Implementation
**Type:** PARENT | **Status:** READY | **Owner:** machinery_governance | **Supervisor:** lane_layer
**Requirement:** REQ-LANE-003, REQ-LANE-004 | **Priority:** P3 | **Depends on:** TC-GFB-006, TC-GFB-012
**Stable key:** FF-MR-LANE-CONTRACTS

**Objective:** Create `.governance/lanes/lane-contracts.yaml` with 13 formal lane definitions.
Add V168 validator to governance_validators_ext4.py. Write passing test.

**Scope:**
- Allowed WRITE: `.governance/lanes/lane-contracts.yaml` (new), `tools/supervisor/governance_validators_ext4.py`, `tests/supervisor/test_lane_contracts.py` (new)
- Forbidden: `src/`, `plans/master-plan.md` (TC-GFB-020 owns it)

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-021-01 | Design lane contracts schema | TODO |
| TC-GFB-021-02 | Write .governance/lanes/lane-contracts.yaml | TODO |
| TC-GFB-021-03 | Add V168 validator to governance_validators_ext4.py | TODO |
| TC-GFB-021-04 | Write and run test_lane_contracts.py | TODO |

---

#### TC-GFB-021-01: Design lane contracts schema
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-021

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-021-01-01 | Read `tools/supervisor/governance_validators_ext4.py` — understand current structure and how to add V168 | current validator structure |
| MS-GFB-021-01-02 | Read `.governance/` directory listing — understand existing YAML schemas | existing schemas |
| MS-GFB-021-01-03 | Design schema for one lane entry: {lane_id, mission_scope, owner_role, task_sources[], queue_root, state_root, evidence_root, allowed_paths[], forbidden_paths[], shared_paths[], collision_checks[], commit_policy, continuation_policy, stop_conditions[], handoff} | schema definition |
| MS-GFB-021-01-04 | List all 13 lanes to include: coordinator, specification_sal, qname, capability_rcal, skill_hardening, machinery_development, product_dotnet, product_python, backfill_migration, verification_adversarial, evidence_ledger, package_consumer, release_gate11 | 13 lane IDs |

---

#### TC-GFB-021-02: Write lane-contracts.yaml
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-021
**Preconditions:** TC-GFB-021-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-021-02-01 | Create `.governance/lanes/` directory | directory created |
| MS-GFB-021-02-02 | Write `.governance/lanes/lane-contracts.yaml` with entries for all 13 lanes. For each lane include: lane_id, mission_scope (brief), owner_role, task_sources (which plan sections feed this lane), evidence_root (relative path), allowed_paths (list), forbidden_paths (list), collision_checks (list of other lane IDs that could collide) | 13-entry YAML |
| MS-GFB-021-02-03 | Validate YAML is parseable: `python -c "import yaml; print(len(yaml.safe_load(open('.governance/lanes/lane-contracts.yaml'))['lanes']))"` → expect 13 | count = 13 |

---

#### TC-GFB-021-03: Add V168 validator
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-021
**Preconditions:** TC-GFB-021-02 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-021-03-01 | Read `tools/supervisor/governance_validators_ext4.py` lines 1–80 to understand validator function signature | signature pattern |
| MS-GFB-021-03-02 | Read existing validator (e.g. V125 or V143) as template for structure | template structure |
| MS-GFB-021-03-03 | Write V168 function `validate_lane_contract_exists(declaration, context)`: checks if declaration's `lane_id` field matches an entry in `.governance/lanes/lane-contracts.yaml`; returns WARNING if lane_contracts.yaml missing (non-blocking — file may not exist yet), FAIL if lane_id is invalid | V168 function written |
| MS-GFB-021-03-04 | Register V168 in the validators list within governance_validators_ext4.py | V168 registered |
| MS-GFB-021-03-05 | Update expected_count in `tools/supervisor/governance_validator_runner.py` from 167 to 168 | count updated |
| MS-GFB-021-03-06 | Run `python -m pytest tests/supervisor/test_governance_validators*.py -v -k "not slow" 2>&1 | tail -20` | no new failures |

---

#### TC-GFB-021-04: Write and run test
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-021
**Preconditions:** TC-GFB-021-03 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-021-04-01 | Write `tests/supervisor/test_lane_contracts.py` with tests: (1) valid lane ID passes V168, (2) invalid lane ID fails V168, (3) missing lane_contracts.yaml gives WARNING not FAIL, (4) all 13 lanes have non-empty allowed_paths | 4 test functions |
| MS-GFB-021-04-02 | Run `.venv/Scripts/pytest tests/supervisor/test_lane_contracts.py -v` | all 4 PASS |
| MS-GFB-021-04-03 | If any FAIL: diagnose and fix before marking CLOSED | all PASS |
| MS-GFB-021-04-04 | Write `lane-state-isolation-results.json` in evidence root: {test_file, tests_passed: 4, v168_blocking: false, lane_contracts_path: .governance/lanes/lane-contracts.yaml} | evidence root |

---

### TC-GFB-022: Gate 11 State Contract Implementation
**Type:** PARENT | **Status:** READY | **Owner:** machinery_governance | **Supervisor:** gate_layer
**Requirement:** REQ-G11-001, REQ-G11-002 | **Priority:** P3 | **Depends on:** TC-GFB-012, TC-GFB-007
**Stable key:** FF-MR-GATE11-CONTRACT

**Objective:** Implement Gate 11 as code-enforced state. Define `registry/gate-states.yaml`.
Add Check 8 to `check_continuation.py`. Update `autonomous_cycle.py` to emit GATE_11_READY.
Write and pass tests.

**Scope:**
- Allowed WRITE: `registry/gate-states.yaml` (new), `tools/supervisor/check_continuation.py`, `tools/supervisor/autonomous_cycle.py`, `tests/supervisor/test_gate11_state_contract.py` (new)
- Forbidden: `src/`, `plans/`, `.supervisor/skill-registry.yaml`

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-022-01 | Define gate states registry (registry/gate-states.yaml) | TODO |
| TC-GFB-022-02 | Add Check 8 to check_continuation.py | TODO |
| TC-GFB-022-03 | Update autonomous_cycle.py to emit GATE_11_READY verdicts | TODO |
| TC-GFB-022-04 | Write and run tests | TODO |

---

#### TC-GFB-022-01: Define gate states registry
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-022

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-022-01-01 | Check if `registry/gate-states.yaml` already exists | exists/MISSING |
| MS-GFB-022-01-02 | Write `registry/gate-states.yaml` with: version, gate_states (list), per-state: state_id, description, entry_criteria[], exit_criteria[], per_product(true), blocks_autonomous_continue(true for GATE_11_READY), allows_other_products_to_continue(true) | file created |
| MS-GFB-022-01-03 | Define GATE_11_READY criteria (from TC-GFB-012 preliminary contract): gates_1_to_10_pass=true, oracle_depth_d1_plus=true, package_artifact_present=true, consumer_proof_present=true, evidence_bundle_complete=true, zero_critical_high_open_gaps=true | criteria defined |
| MS-GFB-022-01-04 | Validate YAML: `python -c "import yaml; d=yaml.safe_load(open('registry/gate-states.yaml')); print([s['state_id'] for s in d['gate_states']])"` | GATE_11_READY in list |

---

#### TC-GFB-022-02: Add Check 8 to check_continuation.py
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-022
**Preconditions:** TC-GFB-022-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-022-02-01 | Read `tools/supervisor/check_continuation.py` lines 1–80 to understand current check structure | check_n function pattern |
| MS-GFB-022-02-02 | Read the 7 existing checks — identify where Check 8 should be inserted (after check_7, before final verdict) | insertion point line number |
| MS-GFB-022-02-03 | Read how continuation-signal.json is structured — identify where per-product gate verdicts would live | field location |
| MS-GFB-022-02-04 | Write Check 8 function `check_8_gate11_per_product(signal)`: reads `registry/gate-states.yaml` for GATE_11_READY criteria; reads per-product gate status from format-registry.yaml; if any product meets all criteria: return STOP(reason=GATE_11_READY, product=<format_id>, note="other safe work may continue") | Check 8 written |
| MS-GFB-022-02-05 | Add Check 8 to the main `run_checks()` function in check_continuation.py | Check 8 registered |
| MS-GFB-022-02-06 | Run `python tools/supervisor/check_continuation.py 2>&1` — verify it still returns CONTINUE (no product is at Gate 11 yet) | CONTINUE verdict, no crash |

**Rollback:** If check_continuation.py is broken: `git checkout tools/supervisor/check_continuation.py`

---

#### TC-GFB-022-03: Update autonomous_cycle.py
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-022
**Preconditions:** TC-GFB-022-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-022-03-01 | Read `tools/supervisor/autonomous_cycle.py` — find where per-product verdicts are emitted (search for "verdict" near product loop) | verdict emission location |
| MS-GFB-022-03-02 | Add function `evaluate_gate11_readiness(format_id, declaration)`: checks declared evidence against GATE_11_READY criteria from registry/gate-states.yaml; returns {gate_11_ready: bool, criteria_met: [], criteria_missing: []} | function added |
| MS-GFB-022-03-03 | Call the function in the evidence inspection phase and append GATE_11_READY to per-product verdict if criteria met | verdict includes GATE_11_READY flag |
| MS-GFB-022-03-04 | Update format-registry.yaml entry for FODS to add `gate_11_status: NOT_READY` (placeholder — Pilot A will set to READY) | FODS gate_11_status field exists |

---

#### TC-GFB-022-04: Write and run tests
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-022
**Preconditions:** TC-GFB-022-02 and TC-GFB-022-03 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-022-04-01 | Write `tests/supervisor/test_gate11_state_contract.py` with tests: (1) product meeting all criteria → GATE_11_READY verdict emitted, (2) product missing one criterion → not GATE_11_READY, (3) check_continuation.py returns STOP(GATE_11_READY) when product is ready, (4) other products can continue when one product is GATE_11_READY | 4 test functions |
| MS-GFB-022-04-02 | Run `.venv/Scripts/pytest tests/supervisor/test_gate11_state_contract.py -v` | all 4 PASS |
| MS-GFB-022-04-03 | Run full governance validator test suite to confirm no regressions: `.venv/Scripts/pytest tests/supervisor/test_governance_validators*.py -v 2>&1 | tail -5` | no new failures |
| MS-GFB-022-04-04 | Write `gate11-state-contract.yaml` in evidence root: {implementation_status: IMPLEMENTED, code_paths: [check_continuation.py check_8, autonomous_cycle.py evaluate_gate11_readiness], test_file: tests/supervisor/test_gate11_state_contract.py, tests_passed: 4} | evidence root |

---

### TC-GFB-023: Backfill Machinery Design
**Type:** PARENT | **Status:** CLOSED | **Owner:** machinery_governance | **Supervisor:** backfill_layer
**Requirement:** REQ-BF-001, REQ-BF-002 | **Priority:** P3 | **Depends on:** TC-GFB-004, TC-GFB-012
**Stable key:** FF-MR-BACKFILL-DESIGN

**Objective:** Design and create the read-only backfill preview tool.
Create `tools/backfill/dry_run_migration.py` — preview only, zero source mutations.
Define schemas for migration maps and behavior preservation.

**Scope:**
- Allowed WRITE: `tools/backfill/` (new directory), `.governance/backfill/` (new directory), evidence root
- Forbidden: `src/` (no source mutations), `plans/`, `.supervisor/`
- CRITICAL: `dry_run_migration.py` must make ZERO changes to source. It reads and prints only.

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-023-01 | Define migration-map and behavior-preservation schemas | TODO |
| TC-GFB-023-02 | Create tools/backfill/dry_run_migration.py | TODO |
| TC-GFB-023-03 | Write backfill design artifacts | TODO |

---

#### TC-GFB-023-01: Define schemas
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-023

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-023-01-01 | Create `.governance/backfill/` directory | directory created |
| MS-GFB-023-01-02 | Write `.governance/backfill/migration-map.schema.yaml`: defines migration_map entry fields: {format_id, source_file, old_symbol, new_symbol, symbol_type, old_path, new_path, namespace_change, reason, authority_ref, behavior_preservation_class} | schema file |
| MS-GFB-023-01-03 | Write `.governance/backfill/behavior-preservation.schema.yaml`: defines behavior_classification values: PRESERVED_UNCHANGED, PRESERVED_WITH_COMPATIBILITY_LAYER, INTENTIONALLY_IMPROVED, DEPRECATED_WITH_AUTHORITY, REMOVED_WITH_AUTHORITY, PREVIOUSLY_BROKEN_NOW_FIXED, UNVERIFIED | schema file |
| MS-GFB-023-01-04 | Write `.governance/backfill/backfill-rollback-contract.yaml`: rollback procedure = git checkout <format-source-root>; rollback precondition = git status shows committed baseline; recovery steps | schema file |
| MS-GFB-023-01-05 | Write `backfill-dry-run-contract.yaml` in evidence root: dry_run means READ-ONLY, produces preview only, no writes to src/ | evidence root |

---

#### TC-GFB-023-02: Create dry_run_migration.py
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-023
**Preconditions:** TC-GFB-023-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-023-02-01 | Create `tools/backfill/` directory; create `tools/backfill/__init__.py` (empty) | directory + init |
| MS-GFB-023-02-02 | Write `tools/backfill/dry_run_migration.py` with CLI: `python tools/backfill/dry_run_migration.py --format <format_id> --target-profile <profile_name>`. Reads: source files from src/, qname registry, architecture profile. Produces: preview of proposed renames/moves. Makes ZERO writes to src/. | file written |
| MS-GFB-023-02-03 | Test dry run: `python tools/backfill/dry_run_migration.py --format fods --target-profile ODF_RICH 2>&1 | head -30` | preview output, no src/ changes |
| MS-GFB-023-02-04 | Verify no src/ changes occurred: `git diff src/` → must be empty | git diff is empty |
| MS-GFB-023-02-05 | Test with a format that has no qname gaps: output should report "no migrations proposed" | clean output |

---

#### TC-GFB-023-03: Write backfill artifacts
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-023
**Preconditions:** TC-GFB-023-02 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-023-03-01 | Write `backfill-system-inventory.yaml` in evidence root: current_capabilities (NONE before this task), required_capabilities (list 10), implemented_by_this_task: [dry_run_migration.py, schemas], still_missing: [governed_rewrite, wave_execution] | evidence root |
| MS-GFB-023-03-02 | Write `backfill-target-architecture.md` in evidence root: describes the full 10-step backfill flow; marks steps 1-5 as IMPLEMENTED (this task), steps 6-10 as FUTURE (Wave 2) | evidence root |
| MS-GFB-023-03-03 | Write `backfill-verdict.md` in evidence root: PARTIAL_IMPLEMENTATION — design + dry-run complete; governed rewrite deferred to post-pilot | evidence root |

---

### TC-GFB-024: Machinery Isolation Tests
**Type:** PARENT | **Status:** CLOSED | **Owner:** machinery_governance | **Supervisor:** test_layer
**Requirement:** REQ-TEST-001, REQ-TEST-002, REQ-TEST-003 | **Priority:** P3
**Depends on:** TC-GFB-021, TC-GFB-022, TC-GFB-023
**Stable key:** FF-MR-ISOLATION-TESTS

**Objective:** Write 6 machinery test files covering negative controls, idempotency, and lane isolation.
All tests must PASS before any pilots begin.

**Scope:**
- Allowed WRITE: `tests/machinery/` (new directory), evidence root
- Forbidden: `src/`, `tools/supervisor/` (tests must not modify validators they test)

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-024-01 | Create tests/machinery/ + QName enforcement + SAL authority tests | TODO |
| TC-GFB-024-02 | Create lane isolation + Gate 11 stop tests | TODO |
| TC-GFB-024-03 | Create backfill dry-run + continuation idempotency tests | TODO |
| TC-GFB-024-04 | Run full test suite and capture results | TODO |

---

#### TC-GFB-024-01: QName enforcement + SAL authority tests
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-024

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-024-01-01 | Create `tests/machinery/` directory and `tests/machinery/__init__.py` | directory created |
| MS-GFB-024-01-02 | Write `tests/machinery/test_qname_enforcement.py`: test_missing_spec_qname_triggers_v77 — create minimal mock declaration with a model class lacking spec_qname; run governance_validators; assert V77 fires. test_valid_spec_qname_passes_v77 — add spec_qname field; assert V77 passes. | 2 tests |
| MS-GFB-024-01-03 | Write `tests/machinery/test_sal_authority.py`: test_ai_draft_unverified_blocks_oracle_pass — create oracle case with authority_class=AI_DRAFT_UNVERIFIED; assert verdict is not PASS. test_spec_normative_allows_oracle_pass — authority_class=SPEC_NORMATIVE; assert verdict can be PASS. | 2 tests |
| MS-GFB-024-01-04 | Run the 4 new tests: `.venv/Scripts/pytest tests/machinery/test_qname_enforcement.py tests/machinery/test_sal_authority.py -v` | 4 PASS |

---

#### TC-GFB-024-02: Lane isolation + Gate 11 stop tests
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-024
**Preconditions:** TC-GFB-024-01 CLOSED, TC-GFB-022 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-024-02-01 | Write `tests/machinery/test_lane_isolation.py`: test_lane_contracts_yaml_valid — load .governance/lanes/lane-contracts.yaml, assert 13 lanes, assert each has required fields. test_no_overlapping_owned_paths — assert no two lanes have the same path in both allowed_paths. | 2 tests |
| MS-GFB-024-02-02 | Write `tests/machinery/test_gate11_stop.py`: test_gate11_ready_product_stops_continuation — mock a product that meets all GATE_11_READY criteria; run check_continuation.py logic; assert verdict=STOP reason=GATE_11_READY. test_other_products_continue_at_gate11 — mock one product at Gate 11, one not; assert the non-Gate-11 product still gets CONTINUE. | 2 tests |
| MS-GFB-024-02-03 | Run: `.venv/Scripts/pytest tests/machinery/test_lane_isolation.py tests/machinery/test_gate11_stop.py -v` | 4 PASS |

---

#### TC-GFB-024-03: Backfill + continuation idempotency tests
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-024
**Preconditions:** TC-GFB-024-01 CLOSED, TC-GFB-023 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-024-03-01 | Write `tests/machinery/test_backfill_dry_run.py`: test_dry_run_produces_no_src_changes — run dry_run_migration.py for fods; check git diff src/ is empty after run. test_dry_run_output_is_deterministic — run twice; assert outputs are identical. | 2 tests |
| MS-GFB-024-03-02 | Write `tests/machinery/test_continuation_idempotency.py`: test_check_continuation_deterministic — run check_continuation.py twice on same state; assert JSON output identical. test_stale_signal_detected — mock continuation-signal.json with date 8 days ago; assert stale detection triggered. | 2 tests |
| MS-GFB-024-03-03 | Run: `.venv/Scripts/pytest tests/machinery/test_backfill_dry_run.py tests/machinery/test_continuation_idempotency.py -v` | 4 PASS |

---

#### TC-GFB-024-04: Run full machinery test suite and capture results
**Type:** CHILD | **Status:** TODO | **Parent:** TC-GFB-024
**Preconditions:** TC-GFB-024-01 through TC-GFB-024-03 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-024-04-01 | Run complete machinery test suite: `.venv/Scripts/pytest tests/machinery/ -v 2>&1 | tee /tmp/machinery-test-run.txt` | full output captured |
| MS-GFB-024-04-02 | Check for any FAIL: if any fail, diagnose and fix before continuing | 0 FAIL |
| MS-GFB-024-04-03 | Run full project test suite to confirm no regression: `.venv/Scripts/pytest tests/ -v --ignore=tests/machinery/ 2>&1 | tail -5` | same counts as baseline (1169 pass + new pass) |
| MS-GFB-024-04-04 | Write `machinery-isolation-results.json` in evidence root: {total_tests: N, passed: N, failed: 0, test_files: 6} | evidence root |
| MS-GFB-024-04-05 | Write `machinery-readiness-verdict.md`: MACHINERY_READY — all negative controls pass, all isolation tests pass, Gate 11 stop verified, backfill read-only verified | evidence root |

---

## GROUP 4: Pilots

### TC-GFB-030: Pilot A — FODS .NET End-to-End
**Type:** PARENT | **Status:** CLOSED | **Owner:** product-dotnet | **Supervisor:** gate_layer
**Requirement:** REQ-PILOT-A | **Priority:** P4 | **Depends on:** TC-GFB-024
**Stable key:** PILOT-FODS-DOTNET-E2E

**Objective:** Prove FODS .NET full lifecycle: SAL → QName → Capability → Source → Tests → Package → Consumer → GATE_11_READY.

**Scope:**
- Allowed WRITE: `src/net/fods/` (only if capability gap work needed), `tests/net/fods/`, evidence root
- Forbidden: `src/python/`, `src/net/fodt/`, other formats

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-030-01 | Baseline verification (build + all existing tests pass + oracle D1 confirmed) | CLOSED |
| TC-GFB-030-02 | Consumer proof (clean .NET project installation) | CLOSED |
| TC-GFB-030-03 | Gate 11 evaluation and GATE_11_READY state check | CLOSED |

---

#### TC-GFB-030-01: Baseline verification
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-030

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-030-01-01 | Build FODS .NET: `dotnet build src/net/fods/FormatFactory.Fods.csproj 2>&1 | tail -5` | BUILD SUCCEEDED |
| MS-GFB-030-01-02 | Run all FODS .NET tests: `dotnet test src/net/fods/ 2>&1 | tail -10` | all 102 pass (or current count) |
| MS-GFB-030-01-03 | Run oracle for FODS: `python tools/oracle/execute_oracle.py --format fods 2>&1` | 8/8 PASS, D1 or D2 depth |
| MS-GFB-030-01-04 | Load a .fods file using the API → inspect cell at [0,0] → mutate to "PILOT_TEST_VALUE" → save → reload → assert value preserved | round-trip preserved |
| MS-GFB-030-01-05 | Confirm export capabilities still work: CSV export and JSON export from FODS (run existing export tests) | exports pass |

---

#### TC-GFB-030-02: Consumer proof
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-030
**Preconditions:** TC-GFB-030-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-030-02-01 | Pack FODS .NET to NuGet: `dotnet pack src/net/fods/FormatFactory.Fods.csproj -c Release 2>&1 | tail -5` | .nupkg file created |
| MS-GFB-030-02-02 | Create temporary consumer project in system temp: `dotnet new console -n FodsConsumerProof --output /tmp/FodsConsumerProof` | project created |
| MS-GFB-030-02-03 | Add local NuGet source and install FODS package in consumer project | package installed |
| MS-GFB-030-02-04 | Write `Program.cs` consumer: load .fods file, read first worksheet name, print cell count. Uses ONLY public API types. Maximum 30 lines. | consumer program written |
| MS-GFB-030-02-05 | Run consumer: `dotnet run --project /tmp/FodsConsumerProof` | runs without error, output printed |
| MS-GFB-030-02-06 | Write `pilot-a-consumer-program.cs` to evidence root (copy of the consumer program) | evidence root |

---

#### TC-GFB-030-03: Gate 11 evaluation
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-030
**Preconditions:** TC-GFB-030-01 and TC-GFB-030-02 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-030-03-01 | Update FODS entry in `registry/format-registry.yaml`: set gate_11_status=GATE_11_READY (all criteria met: oracle D1+, package present, consumer proof present, evidence complete, no open CRITICAL gaps) | registry updated |
| MS-GFB-030-03-02 | Run `python tools/supervisor/check_continuation.py` — verify it now returns STOP with reason=GATE_11_READY for FODS .NET | STOP(GATE_11_READY, product=fods-dotnet) |
| MS-GFB-030-03-03 | Write `pilot-a-fods-dotnet-results.json` in evidence root: {build: PASS, tests: N/N, oracle: 8/8, consumer_proof: PASS, gate_11: GATE_11_READY} | evidence root |
| MS-GFB-030-03-04 | Write `pilot-a-gate11-verdict.yaml` in evidence root with all Gate 11 criteria and their status | evidence root |

---

### TC-GFB-031: Pilot B — FODT .NET End-to-End
**Type:** PARENT | **Status:** CLOSED | **Owner:** product-dotnet | **Supervisor:** gate_layer
**Requirement:** REQ-PILOT-B | **Priority:** P4 | **Depends on:** TC-GFB-030
**Stable key:** PILOT-FODT-DOTNET-E2E

**Objective:** Prove FODT .NET full lifecycle. Assess FodtDocumentExtendedApis.cs (2944 LOC) and determine
if decomposition is required before Gate 11 or if it can be frozen at 2944 cap.

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-031-01 | Baseline verification + monolith assessment | CLOSED |
| TC-GFB-031-02 | Consumer proof + Gate 11 evaluation | CLOSED |

---

#### TC-GFB-031-01: Baseline + monolith assessment
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-031

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-031-01-01 | Build FODT .NET: `dotnet build src/net/fodt/ 2>&1 | tail -5` | BUILD SUCCEEDED |
| MS-GFB-031-01-02 | Run all FODT .NET tests: `dotnet test src/net/fodt/ 2>&1 | tail -10` | all pass |
| MS-GFB-031-01-03 | Load `samples/by-format/fodt/minimal-document.fodt` via API → inspect paragraph count → add one paragraph → save → reload → assert paragraph count increased by 1 | round-trip + mutation preserved |
| MS-GFB-031-01-04 | Read FodtDocumentExtendedApis.cs: count public methods; identify which domain areas they serve (conversion? mutation? analytics?) | method count + domain breakdown |
| MS-GFB-031-01-05 | Assess decomposition: can FodtDocumentExtendedApis.cs be split into 2–3 files (e.g., FodtConversions.cs, FodtMutations.cs) without breaking public API? Record assessment. | decomposition feasibility: YES/RISKY/DEFER |
| MS-GFB-031-01-06 | Check if FodtDocumentExtendedApis.cs is in `registry/source-structure-baseline.json` known_violations — if yes at 2944 cap, V35 is non-blocking warning; if not present, add it to prevent future growth | status: capped or needs adding |

---

#### TC-GFB-031-02: Consumer proof + Gate 11
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-031
**Preconditions:** TC-GFB-031-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-031-02-01 | Pack FODT .NET and create consumer program (same steps as TC-GFB-030-02 but for FODT) | consumer runs |
| MS-GFB-031-02-02 | Write consumer: loads minimal-document.fodt, reads first paragraph text, prints it | consumer output |
| MS-GFB-031-02-03 | Decision: if decomposition was DEFER in MS-GFB-031-01-05: add TC-FODT-DECOMP-001 to plans/master-plan.md (already done in TC-GFB-020-03 if assessment done there); mark GATE_11_READY with known limitation noted | gate11 status set |
| MS-GFB-031-02-04 | Write pilot-b artifacts in evidence root: `pilot-b-fodt-dotnet-results.json`, `pilot-b-consumer-program.cs`, `pilot-b-gate11-verdict.yaml` | 3 evidence files |

---

### TC-GFB-032: Pilot D — Python Structured Product
**Type:** PARENT | **Status:** CLOSED | **Owner:** product-python | **Supervisor:** oracle_layer
**Requirement:** REQ-PILOT-D | **Priority:** P4 | **Depends on:** TC-GFB-024
**Stable key:** PILOT-PYTHON-STRUCTURED-E2E

**Objective:** Prove Python FOSS pipeline works end-to-end. Close one FODS capability gap via governed skill.
Maintain all 8 oracle cases passing. Package + consumer proof.

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-032-01 | Oracle baseline + capability gap selection | CLOSED |
| TC-GFB-032-02 | Implement one capability via governed skill | CLOSED |
| TC-GFB-032-03 | Package install + consumer proof | CLOSED |

---

#### TC-GFB-032-01: Oracle baseline + gap selection
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-032

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-032-01-01 | Run FODS oracle: `.venv/Scripts/python tools/oracle/execute_oracle.py --format fods 2>&1` | 8/8 PASS (baseline confirmed) |
| MS-GFB-032-01-02 | Read `.governance/capabilities/registry.yaml` — find FOSS Python FODS capabilities with status NOT FULL_PARITY | gap list |
| MS-GFB-032-01-03 | Select ONE capability gap: must be safe to implement (no architecture risk), small scope, verifiable by oracle or unit test | selected gap ID + rationale |

---

#### TC-GFB-032-02: Implement capability via governed skill
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-032
**Preconditions:** TC-GFB-032-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-032-02-01 | Invoke `/add-python-api` or `/format-feature-expansion` skill (via Skill tool) for the selected FODS gap | skill execution record |
| MS-GFB-032-02-02 | Run focused test for the new capability: `.venv/Scripts/pytest tests/fods/ -v -k "<new_test>" 2>&1` | new test PASS |
| MS-GFB-032-02-03 | Run full FODS test suite to confirm no regression: `.venv/Scripts/pytest tests/fods/ -v 2>&1 | tail -5` | all pass |
| MS-GFB-032-02-04 | Re-run oracle: `.venv/Scripts/python tools/oracle/execute_oracle.py --format fods` | still 8/8 PASS |

---

#### TC-GFB-032-03: Package install + consumer proof
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-032
**Preconditions:** TC-GFB-032-02 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-032-03-01 | Create clean venv: `python -m venv /tmp/fods-consumer-test-env` | venv created |
| MS-GFB-032-03-02 | Install FODS package in clean venv: `/tmp/fods-consumer-test-env/Scripts/pip install src/python/fods/ -q` | installed without error |
| MS-GFB-032-03-03 | Write consumer program (≤30 lines) in /tmp/: import fods, load a sample file, read data, print summary. Uses only public API. | consumer program |
| MS-GFB-032-03-04 | Run consumer: `/tmp/fods-consumer-test-env/Scripts/python /tmp/fods_consumer_proof.py` | runs, output printed |
| MS-GFB-032-03-05 | Write `pilot-d-python-results.json`, `pilot-d-consumer-program.py`, `pilot-d-capability-closed.yaml` to evidence root | 3 evidence files |

---

### TC-GFB-033: Pilot G — Conversion/Export Proof
**Type:** PARENT | **Status:** CLOSED | **Owner:** product-python | **Supervisor:** oracle_layer
**Requirement:** REQ-PILOT-G | **Priority:** P4 | **Depends on:** TC-GFB-032
**Stable key:** PILOT-CONVERSION-EXPORT-E2E

**Objective:** Prove end-to-end conversion: FODS Python → domain model → CSV Python (or ODS).
Consumer program ≤30 lines. Both libraries' oracle cases must still PASS after conversion.

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-033-01 | Design and implement conversion path | CLOSED |
| TC-GFB-033-02 | Consumer program + evidence | CLOSED |

---

#### TC-GFB-033-01: Design and implement conversion
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-033

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-033-01-01 | Select target format: CSV (simpler) or ODS (richer). CSV is preferred for first proof. | target selected |
| MS-GFB-033-01-02 | Read FODS Python public API: what method returns cell data as iterable? | API method name |
| MS-GFB-033-01-03 | Read CSV Python public API: what constructor accepts rows + headers? | API method name |
| MS-GFB-033-01-04 | Write conversion function: load FODS → extract first worksheet rows → create CSV document → save. ≤20 lines. | conversion function |
| MS-GFB-033-01-05 | Test conversion with a sample .fods file containing known data; assert CSV output contains expected values | assertion pass |
| MS-GFB-033-01-06 | Re-run FODS oracle: `execute_oracle.py --format fods` → 8/8 PASS (unchanged) | oracle unchanged |
| MS-GFB-033-01-07 | Run CSV oracle: `execute_oracle.py --format csv` → all PASS (unchanged) | oracle unchanged |

---

#### TC-GFB-033-02: Consumer program + evidence
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-033
**Preconditions:** TC-GFB-033-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-033-02-01 | Write final consumer program `pilot_g_conversion.py` (≤30 lines): import fods, import csv (Format Factory), convert, print "Conversion complete: N rows" | ≤30 lines |
| MS-GFB-033-02-02 | Run in clean venv with both packages installed: assert output is correct | runs correctly |
| MS-GFB-033-02-03 | Write `pilot-g-conversion-results.json` and `pilot-g-consumer-conversion.py` to evidence root | 2 evidence files |

---

### TC-GFB-034: Pilot H — Autonomous Unattended Proof
**Type:** PARENT | **Status:** CLOSED | **Owner:** machinery_governance | **Supervisor:** continuation_layer
**Requirement:** REQ-PILOT-H | **Priority:** P4 | **Depends on:** TC-GFB-033
**Stable key:** PILOT-AUTONOMOUS-UNATTENDED

**Objective:** Prove the autonomous controller selects, executes, verifies, and gates product work without
human intervention. Verify lane isolation maintained. Verify Gate 11 stop fires for eligible product.

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-034-01 | Reset stale state and verify CONTINUE | CLOSED |
| TC-GFB-034-02 | Execute one product sprint via governed path | CLOSED |
| TC-GFB-034-03 | Run autonomous-cycle and verify evidence + state updates | CLOSED |
| TC-GFB-034-04 | Verify Gate 11 stop fires; verify other products continue | CLOSED |

---

#### TC-GFB-034-01: Reset stale state and verify CONTINUE
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-034

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-034-01-01 | Snapshot current `continuation-signal.json`: write `continuation-signal-before.json` to evidence root | snapshot written |
| MS-GFB-034-01-02 | Update continuation-signal.json `updated_at` to now (remove staleness): `python -c "import json,datetime; d=json.load(open('.local/supervisor/continuation-signal.json')); d['updated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat(); open('.local/supervisor/continuation-signal.json','w').write(json.dumps(d))"` | signal is fresh |
| MS-GFB-034-01-03 | Ensure no active plan lock is blocking: check `.local/supervisor/active-plan-lock.json` session_id; if old session, mark SUPERSEDED | lock cleared |
| MS-GFB-034-01-04 | Run `python tools/supervisor/check_continuation.py 2>&1` | CONTINUE verdict (exit 0) |

---

#### TC-GFB-034-02: Execute one product sprint
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-034
**Preconditions:** TC-GFB-034-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-034-02-01 | Read `reports/supervisor/next-work-items.json` — identify one legitimate product deepening task | task_id + format + description |
| MS-GFB-034-02-02 | Identify the correct governed skill for that task type (from skill-registry.yaml) | skill_id |
| MS-GFB-034-02-03 | Execute the governed skill via Skill tool | skill execution |
| MS-GFB-034-02-04 | Write an evidence declaration for the executed task: `.local/evidences/<new_run_id>/evidence-declaration.yaml` | declaration written |

---

#### TC-GFB-034-03: Run autonomous-cycle and verify updates
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-034
**Preconditions:** TC-GFB-034-02 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-034-03-01 | Run: `python tools/supervisor/autonomous_cycle.py --declaration <path> 2>&1 | tail -20` | exit 0 or 3 (not 1 or 9) |
| MS-GFB-034-03-02 | Verify `reports/supervisor/evidence-review.json` was updated (check timestamp) | timestamp newer |
| MS-GFB-034-03-03 | Verify `reports/supervisor/next-sprint.md` was updated | timestamp newer |
| MS-GFB-034-03-04 | Verify `continuation-signal.json` iteration incremented | iteration = prior + 1 |
| MS-GFB-034-03-05 | Verify no cross-lane state contamination: machinery evidence root only has machinery artifacts, product evidence has product artifacts | no contamination |

---

#### TC-GFB-034-04: Verify Gate 11 + other products
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-034
**Preconditions:** TC-GFB-034-03 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-034-04-01 | Run `python tools/supervisor/check_continuation.py 2>&1` for a product that has been set to GATE_11_READY | STOP(GATE_11_READY, product=<id>) |
| MS-GFB-034-04-02 | Verify other products that are NOT at Gate 11 are still eligible: check next-work-items.json still contains them | other products present |
| MS-GFB-034-04-03 | Write `continuation-signal-after.json` snapshot to evidence root | snapshot |
| MS-GFB-034-04-04 | Write `autonomous-unattended-execution-log.yaml` to evidence root: {task_executed, skill_used, evidence_declaration, autonomous_cycle_exit_code, iteration_before, iteration_after, gate11_fired_for, other_products_available: N} | evidence root |

---

## GROUP 5: Execution Handoff

### TC-GFB-040: Product Deepening Wave Design
**Type:** PARENT | **Status:** CLOSED | **Owner:** machinery_governance | **Supervisor:** planning_layer
**Requirement:** REQ-WAVE-001 | **Priority:** P5 | **Depends on:** TC-GFB-034
**Stable key:** FF-MR-WAVE-DESIGN

**Objective:** Define the 7-wave product deepening schedule using all findings from audit + pilots.

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-040-01 | Design wave structure using audit findings | CLOSED |
| TC-GFB-040-02 | Write product-deepening-wave-plan.yaml | CLOSED |

---

#### TC-GFB-040-01: Design wave structure
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-040

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-040-01-01 | Read product-gate-readiness-matrix.json from TC-GFB-004 — identify which formats are ready for which waves | per-format readiness |
| MS-GFB-040-01-02 | Order Wave 1 products (pilot products) as Wave 1: FODS Python, FODS .NET, FODT .NET (already running) | Wave 1 defined |
| MS-GFB-040-01-03 | Group remaining Python formats by complexity: ODF rich (ODS/ODT/FODP/FODG) = Wave 2, medium (ABW/GNUMERIC/DIF/SYLK) = Wave 3 | Waves 2-3 defined |
| MS-GFB-040-01-04 | Group .NET expansion: NDJSON/TSV/ZST/ODS (skeleton to functional) = Wave 4 | Wave 4 defined |
| MS-GFB-040-01-05 | Define Waves 5-7: imaging formats (XCF/QOI/PBM/PGM/PPM .NET), cross-language alignment, residual | Waves 5-7 defined |
| MS-GFB-040-01-06 | Define per-wave entry_criteria (which MR gates must pass), exit_criteria (Gate 11 capacity), lane_assignments | wave contracts |

---

#### TC-GFB-040-02: Write wave plan artifact
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-040
**Preconditions:** TC-GFB-040-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-040-02-01 | Write `product-deepening-wave-plan.yaml` in evidence root with 7 waves, each containing: wave_id, formats[], entry_criteria[], exit_criteria[], lane_assignments[], gate11_capacity (max products in review simultaneously) | evidence root |
| MS-GFB-040-02-02 | Validate YAML: `python -c "import yaml; d=yaml.safe_load(open('<path>')); print(len(d['waves']))"` → 7 | count = 7 |

---

### TC-GFB-041: Single-Go Execution Handoff
**Type:** PARENT | **Status:** CLOSED | **Owner:** machinery_governance | **Supervisor:** all
**Requirement:** REQ-HAND-001 | **Priority:** P5 | **Depends on:** TC-GFB-040
**Stable key:** FF-MR-EXECUTION-HANDOFF

**Objective:** Emit the single-go execution handoff. Emit ONLY after all MR-0 through MR-19 gates pass.
Print absolute path + SHA-256.

**Children:**

| Child ID | Title | Status |
|----------|-------|--------|
| TC-GFB-041-01 | Verify all MR-0 through MR-19 gates pass | CLOSED |
| TC-GFB-041-02 | Write execution-handoff.yaml and print SHA-256 | CLOSED |

---

#### TC-GFB-041-01: Verify MR gates
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-041

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-041-01-01 | Read evidence root — verify all required artifacts for MR-0 through MR-14 exist (from Groups 1-3) | all present |
| MS-GFB-041-01-02 | Read evidence root — verify pilot artifacts exist for MR-15 through MR-19 (from Group 4) | all present |
| MS-GFB-041-01-03 | Run machinery test suite one final time: `.venv/Scripts/pytest tests/machinery/ -v` | all pass |
| MS-GFB-041-01-04 | Write `machinery-gates-verification.json` in evidence root: {gates: [{id: MR-0, satisfied_by: TC-GFB-001, evidence: repository-binding.yaml, status: PASS}, ...]} for all 20 gates | 20-entry verification |

---

#### TC-GFB-041-02: Write execution handoff
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-GFB-041
**Preconditions:** TC-GFB-041-01 CLOSED

**Micro-steps:**

| Step | Action | Expected Output |
|------|--------|-----------------|
| MS-GFB-041-02-01 | Write `execution-handoff.yaml` in evidence root with full content as defined in this plan's handoff section | file created |
| MS-GFB-041-02-02 | Compute SHA-256: `python -c "import hashlib; print(hashlib.sha256(open('<path>','rb').read()).hexdigest())"` | sha256 hex string |
| MS-GFB-041-02-03 | Print absolute path: `C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\evidences\ff-machinery-readiness-20260710-af879e5\ff-machinery-readiness\execution-handoff.yaml` | path printed |
| MS-GFB-041-02-04 | Print SHA-256 in the response to user | hash printed |

---

## VALIDATION MATRIX

| Taskcard | Type | Command / Method | Expected Result | Mandatory |
|----------|------|------------------|-----------------|-----------|
| TC-GFB-001 | evidence | `python -c "import yaml; yaml.safe_load(open('evidence-declaration.yaml'))"` | no exception | YES |
| TC-GFB-001 | integration | 8 artifact files exist at declared paths | all present | YES |
| TC-GFB-002 | integration | `system-layer-map.yaml` has ≥16 entries | count >= 16 | YES |
| TC-GFB-003 | verdict | `qname-verdict.md` contains one of 7 verdict tokens | token present | YES |
| TC-GFB-004 | negative | FodtDocumentExtendedApis.cs LOC verified ≥2900 | LOC >= 2900 | YES |
| TC-GFB-005 | integration | `sal-facts-latest.json` entry count ≥ 14000 | count >= 14000 | YES |
| TC-GFB-006 | negative | Lane contracts absent before TC-GFB-021 | absent confirmed | YES |
| TC-GFB-007 | negative | Gate 11 code path absent before TC-GFB-022 | absent confirmed | YES |
| TC-GFB-021 | unit | `.venv/Scripts/pytest tests/supervisor/test_lane_contracts.py -v` | 4 PASS | YES |
| TC-GFB-021 | regression | `.venv/Scripts/pytest tests/supervisor/test_governance_validators*.py` | no new FAIL | YES |
| TC-GFB-022 | unit | `.venv/Scripts/pytest tests/supervisor/test_gate11_state_contract.py -v` | 4 PASS | YES |
| TC-GFB-022 | functional | `python tools/supervisor/check_continuation.py` | CONTINUE (not STOP before any product at Gate 11) | YES |
| TC-GFB-023 | negative | `git diff src/` after dry_run_migration.py | empty (no src changes) | YES |
| TC-GFB-023 | idempotency | Run dry_run_migration.py twice → diff outputs | identical | YES |
| TC-GFB-024 | full suite | `.venv/Scripts/pytest tests/machinery/ -v` | 0 FAIL | YES |
| TC-GFB-024 | regression | `.venv/Scripts/pytest tests/ --ignore=tests/machinery/` | ≥ 1169 PASS, 0 new FAIL | YES |
| TC-GFB-030 | build | `dotnet build src/net/fods/FormatFactory.Fods.csproj` | BUILD SUCCEEDED | YES |
| TC-GFB-030 | oracle | `python tools/oracle/execute_oracle.py --format fods` | 8/8 PASS | YES |
| TC-GFB-030 | gate11 | check_continuation.py after setting GATE_11_READY | STOP(GATE_11_READY) | YES |
| TC-GFB-031 | build | `dotnet build src/net/fodt/` | BUILD SUCCEEDED | YES |
| TC-GFB-032 | oracle | `python tools/oracle/execute_oracle.py --format fods` | 8/8 PASS (after capability add) | YES |
| TC-GFB-032 | package | fresh venv install + consumer program | runs without error | YES |
| TC-GFB-033 | conversion | conversion produces valid CSV from .fods source | valid CSV | YES |
| TC-GFB-034 | autonomous | autonomous_cycle.py exit code | 0 or 3 (not 1, not 9) | YES |
| TC-GFB-034 | iteration | continuation-signal.json iteration | incremented | YES |
| TC-GFB-041 | handoff | execution-handoff.yaml SHA-256 printed | hash printed | YES |

**Negative controls (must FAIL the expected wrong behavior):**

| Control | Scenario | Expected Wrong Behavior (must NOT happen) | Verified By |
|---------|----------|--------------------------------------------|-------------|
| NC-001 | Model class without spec_qname | V77 should block → if V77 PASSES this is a REWORK | TC-GFB-024-01 |
| NC-002 | AI_DRAFT_UNVERIFIED oracle case | Oracle should NOT emit PASS → if PASS emitted this is a REWORK | TC-GFB-024-01 |
| NC-003 | dry_run_migration.py | src/ must not change → if git diff shows src/ changes this is a CRITICAL FAIL | TC-GFB-024-03 |
| NC-004 | GATE_11_READY product | check_continuation must return STOP → if CONTINUE this is a REWORK | TC-GFB-024-02 |

---

## EVIDENCE CONTRACT

```yaml
evidence_contract:
  evidence_root: ".local/evidences/ff-machinery-readiness-20260710-af879e5/ff-machinery-readiness/"
  absolute_path: "C:\\Users\\prora\\OneDrive\\Documents\\GitHub\\format-factory\\.local\\evidences\\ff-machinery-readiness-20260710-af879e5\\ff-machinery-readiness\\"

  required_structure:
    - evidence-declaration.yaml          # master declaration (TC-GFB-001)
    - repository-binding.yaml            # (TC-GFB-001)
    - master-plan-binding.yaml           # (TC-GFB-001)
    - mission-state.yaml                 # (TC-GFB-001)
    - stable-id-registry.yaml            # (TC-GFB-001)
    - git-state.txt                      # (TC-GFB-001)
    - audit-scope.md                     # (TC-GFB-001)
    - system-layer-map.yaml              # (TC-GFB-002)
    - prior-run-reconciliation.yaml      # (TC-GFB-002)
    - claim-classification-register.yaml # (TC-GFB-002)
    - qname-schema-inventory.yaml        # (TC-GFB-003)
    - qname-authority-report.md          # (TC-GFB-003)
    - qname-verdict.md                   # (TC-GFB-003)
    - product-inventory.json             # (TC-GFB-004)
    - monolith-register.yaml             # (TC-GFB-004)
    - skill-inventory.yaml               # (TC-GFB-005)
    - sal-verdict.md                     # (TC-GFB-005)
    - rcal-verdict.md                    # (TC-GFB-005)
    - downstream-layer-inventory.yaml    # (TC-GFB-006)
    - current-lane-map.yaml              # (TC-GFB-006)
    - autonomous-verdict.md              # (TC-GFB-007)
    - autonomous-gate11-stop-proof.json  # (TC-GFB-007)
    - complete-gap-matrix.yaml           # (TC-GFB-011)
    - root-cause-register.yaml           # (TC-GFB-011)
    - critical-gap-summary.md            # (TC-GFB-011)
    - format-factory-target-architecture.md # (TC-GFB-012)
    - gate11-state-contract.yaml         # (TC-GFB-012 + TC-GFB-022)
    - selected-machinery-healing-design.md # (TC-GFB-013)
    - lane-state-isolation-results.json  # (TC-GFB-021)
    - machinery-isolation-results.json   # (TC-GFB-024)
    - machinery-readiness-verdict.md     # (TC-GFB-024)
    - pilot-a-fods-dotnet-results.json   # (TC-GFB-030)
    - pilot-a-gate11-verdict.yaml        # (TC-GFB-030)
    - pilot-d-python-results.json        # (TC-GFB-032)
    - pilot-g-conversion-results.json    # (TC-GFB-033)
    - autonomous-unattended-execution-log.yaml # (TC-GFB-034)
    - product-deepening-wave-plan.yaml   # (TC-GFB-040)
    - execution-handoff.yaml             # (TC-GFB-041)
    - machinery-gates-verification.json  # (TC-GFB-041)

  mandatory_fields_per_artifact:
    - authoritative_plan: plans/.claude/golden-foraging-boot.md
    - artifact_role: analysis_or_evidence_only
    - execution_authority: false
    # (for JSON/YAML artifacts that aren't narrative docs)

  sha256_required_for:
    - execution-handoff.yaml
    - machinery-readiness-verdict.md
    - complete-gap-matrix.yaml

  content_assertion_rules:
    - qname-verdict.md: must contain exactly one verdict token from defined set
    - autonomous-gate11-stop-proof.json: must contain gate11_code_path_exists field
    - machinery-readiness-verdict.md: must contain MACHINERY_READY or MACHINERY_NOT_READY token
```

---

## QUALITY SCORING RUBRIC

Score every child taskcard after IMPLEMENTED state, before VERIFIED.

**Dimensions (1–5 each):**

| Dimension | Description | Pass threshold |
|-----------|-------------|----------------|
| Requirement correctness | Does the output satisfy the stated REQ-ID? | >= 4 |
| Implementation correctness | Is the implementation technically accurate? | >= 4 |
| Scope discipline | Did the task stay within allowed files/paths? | >= 4 |
| Validation strength | Were all validation commands run and passing? | >= 4 |
| Evidence completeness | Are all required artifact files present with content? | >= 4 |
| Regression safety | Did existing tests still pass after the change? | >= 4 |
| Maintainability | Is the code/artifact readable and maintainable? | >= 4 |
| Production readiness | Is the output ready for use by the next task? | >= 4 |

**Reroute rule:** Any dimension score < 4/5 → mark child REROUTED → create repair micro-step → re-execute → re-score.

**Parent quality dimensions:**

| Dimension | Description |
|-----------|-------------|
| Root-cause coverage | Do all children together address the root cause? |
| Child completeness | Are all mandatory children CLOSED? |
| Integration completeness | Does the integrated result work end-to-end? |
| Dependency correctness | Are all declared dependencies satisfied? |
| Evidence completeness | Are all parent-level evidence artifacts present? |

---

## SELF-HARDENING REVIEW

After each group completes, score 1–5; any score < 4 requires a repair pass before next group:

| Dimension | After Group 1 | After Group 2 | After Group 3 | After Group 4 | After Group 5 |
|-----------|---------------|---------------|---------------|---------------|---------------|
| Repository coverage | __ | __ | __ | __ | __ |
| QName integration | __ | __ | __ | __ | __ |
| SAL maturity | __ | __ | __ | __ | __ |
| Skill repeatability | __ | __ | __ | __ | __ |
| Source-quality governance | __ | __ | __ | __ | __ |
| Backfill readiness | n/a | __ | __ | __ | __ |
| .NET readiness | __ | __ | __ | __ | __ |
| Python readiness | __ | __ | __ | __ | __ |
| Autonomous continuation | __ | __ | __ | __ | __ |
| Lane isolation | __ | __ | __ | __ | __ |
| Gate 11 correctness | __ | __ | __ | __ | __ |
| Evidence quality | __ | __ | __ | __ | __ |

---

## EXECUTION HANDOFF PROTOCOL

The future execution agent MUST follow this protocol for every micro-step:

1. Read this plan file (`plans/.claude/golden-foraging-boot.md`) — it is the SOLE execution authority.
2. Identify the current parent taskcard (first READY or IN_PROGRESS parent, in DAG order).
3. Identify the first TODO child of that parent.
4. Read the child's micro-steps table.
5. Identify the first PENDING or READY micro-step.
6. Confirm preconditions are satisfied.
7. Confirm allowed paths — do NOT touch forbidden paths.
8. Execute exactly ONE micro-step.
9. Capture evidence immediately (write to evidence root, NOT src/).
10. Update micro-step status to COMPLETE or FAILED.
11. If FAILED: create repair micro-step; do NOT skip.
12. When all micro-steps COMPLETE: run acceptance checks; score child (1–5).
13. If any score < 4: mark child REROUTED; do NOT close.
14. If all scores >= 4: mark child CLOSED.
15. When all children CLOSED: run parent integration checks.
16. If integration passes: mark parent CLOSED; update Taskcard Status Table.
17. Proceed to next parent per DAG.

The execution agent MUST NOT:
- Choose work not in this plan.
- Broaden scope beyond allowed paths.
- Skip micro-steps (mark SKIPPED_NOT_APPLICABLE only with written reason).
- Close a parent before all mandatory children are CLOSED.
- Treat code existence as passing validation.
- Treat evidence paths as evidence without reading the file content.
- Stop for MAX_ITERATIONS (reset and continue).
- Stop for ADVISORY reasons (continue).
- Stop for EXIT_3_REWORK (repair rework item, continue).

Legitimate stops (do NOT override):
- GATE_11_READY: product ready for Gate 11 human review.
- POST_PLAN_TERMINAL: all 23 taskcards CLOSED.
- TRUE_EXTERNAL_GATE: credentials/authority unavailable.
- context_exhaustion: window full — resume from last COMPLETE micro-step.

---

## FINAL EXECUTION HANDOFF CONTENT

```yaml
execution_handoff:
  mission_id: FF-MR-2026-001
  authoritative_plan_path: plans/.claude/golden-foraging-boot.md
  plan_revision: "v2.0 micro-taskcardized 2026-07-11"
  repository: format-factory
  branch: main
  selected_controller: autonomous_cycle
  entry_point: "python tools/supervisor/autonomous_cycle.py"
  machinery_lane_root: .governance/lanes/
  product_lane_root: .governance/capabilities/
  taskcard_root: plans/.claude/
  state_root: .local/supervisor/
  evidence_root: .local/evidences/ff-machinery-readiness-20260710-af879e5/ff-machinery-readiness/
  absolute_evidence_path: "C:\\Users\\prora\\OneDrive\\Documents\\GitHub\\format-factory\\.local\\evidences\\ff-machinery-readiness-20260710-af879e5\\ff-machinery-readiness\\"
  first_parent_taskcard: TC-GFB-001
  first_child_taskcard: TC-GFB-001-01
  first_micro_step: MS-GFB-001-01-01
  required_machinery_gates: [MR-0, MR-1, MR-2, MR-3, MR-4, MR-5, MR-6, MR-7, MR-8, MR-9,
                              MR-10, MR-11, MR-12, MR-13, MR-14, MR-15, MR-16, MR-17, MR-18, MR-19]
  required_product_gates: [Gates-1-10, Gate-11-per-product]
  gate11_stop_contract: registry/gate-states.yaml
  rollback_entry_point: "git checkout <format-source-root>"
  recovery_entry_point: "python tools/supervisor/check_continuation.py"
  allowed_stop_conditions:
    - GATE_11_READY
    - POST_PLAN_TERMINAL
    - TRUE_EXTERNAL_GATE
    - context_exhaustion
  prohibited_stop_conditions:
    - MAX_ITERATIONS
    - ADVISORY
    - EXIT_3_REWORK
    - EXIT_1_DECLARATION_ERROR
  absolute_evidence_path_required: true
  final_evidence_bundle_required: true
  sha256_of_evidence_handoff: EMIT_AT_TC_GFB_041
```

---

## Machinery Gates Reference

| Gate | Name | Satisfied By |
|------|------|-------------|
| MR-0 | Repository and Plan Authority | TC-GFB-001 |
| MR-1 | Prior-Run Reconciliation | TC-GFB-002 |
| MR-2 | Complete Layer Inventory | TC-GFB-002 |
| MR-3 | QName Definition Proven | TC-GFB-003 |
| MR-4 | QName Source Enforcement Proven | TC-GFB-003 |
| MR-5 | Complete Product Census | TC-GFB-004 |
| MR-6 | SAL Authority Proven | TC-GFB-005 |
| MR-7 | RCAL Authority Proven | TC-GFB-005 |
| MR-8 | Feature Compilation Proven | TC-GFB-005 |
| MR-9 | Skills Repeatability Proven | TC-GFB-005 |
| MR-10 | Downstream Consumers Proven | TC-GFB-006 |
| MR-11 | Lane Isolation Proven | TC-GFB-021 |
| MR-12 | Autonomous Continuation Proven | TC-GFB-007 |
| MR-13 | Backfill Design Proven | TC-GFB-023 |
| MR-14 | Machinery Isolation Tests Proven | TC-GFB-024 |
| MR-15 | .NET Pilot Proven | TC-GFB-030 |
| MR-16 | Python Pilot Proven | TC-GFB-032 |
| MR-17 | Cross-Language Pilot Proven | TC-GFB-033 |
| MR-18 | Conversion/Export Pilot Proven | TC-GFB-033 |
| MR-19 | Product-Deepening Readiness Proven | TC-GFB-034 |
| MR-20 | Single-Go Execution Handoff Ready | TC-GFB-041 |

---

## Non-Goals

- Do NOT publish to PyPI or NuGet (requires Babar Raza Gate 11 authorization)
- Do NOT broadly rewrite all 20 Python FOSS formats (pilots only in this plan)
- Do NOT create a competing authoritative plan (enhance plans/master-plan.md only in TC-GFB-020)
- Do NOT merge through branch protection without explicit authorization
- Do NOT run broad source backfill before TC-GFB-030 pilot passes
- Do NOT stop at MAX_ITERATIONS (reset and continue)
- Do NOT interpret "sprint loop becomes available" as authorization to begin it now
- Do NOT write plan amendments to plans/strategic/snoopy-juggling-seal.md

---

## Closure Rules (machinery_hardening)

When all 23 parent taskcards reach CLOSED status and all quality scores are ≥ 4/5:

```bash
# Step 1: Run lifecycle audit
python tools/supervisor/lifecycle_audit.py \
  --mission-id FF-MR-2026-001 \
  --sprint-id TC-GFB-041

# Step 2: If ITERATION_REQUIRED:
#   Read .local/supervisor/lifecycle-audit-results.json
#   Add any new taskcards to the Taskcard Status Table above
#   Execute new taskcards and return to Step 1

# Step 3: If audit passed, close with terminal flag:
python tools/supervisor/write_plan_lock.py \
  --plan-path plans/.claude/golden-foraging-boot.md \
  --terminal --audit-gate
```

Final report to user:
"Plan golden-foraging-boot complete. All 23 taskcards closed. Awaiting your next instruction."

**POST-PLAN TERMINAL RULE:** After `--terminal` is written → STOP immediately.
Do NOT call check_continuation.py. Do NOT read next-sprint.md. Do NOT start ledger work.
The Supreme Directive does NOT override POST_PLAN_TERMINAL.

---

## CHANGE LEDGER (enhancement pass)

| Change ID | Type | Section | Description |
|-----------|------|---------|-------------|
| CL-001 | ADD | Preflight Analysis | Embedded preflight YAML with all required fields |
| CL-002 | ADD | Plan Authority Verdict | Single-plan authority confirmed, artifact rules defined |
| CL-003 | ADD | Requirement Registry | 36 REQ-IDs mapped to parent taskcards |
| CL-004 | ADD | Machine State Model | Full state machine with transition guards |
| CL-005 | ADD | Dependency DAG | Visual DAG + parallel-safe groups defined |
| CL-006 | ENHANCE | All 23 parent TCs | Converted to full parent format with children + micro-steps |
| CL-007 | ADD | 92 child taskcards | Full child format with micro-steps, acceptance checks |
| CL-008 | ADD | ~280 micro-steps | One concrete action per step with target + expected output |
| CL-009 | ADD | Validation Matrix | 26-row validation table + 4 negative controls |
| CL-010 | ADD | Evidence Contract | Complete artifact listing with mandatory fields |
| CL-011 | ADD | Quality Scoring Rubric | 8 dimensions, 4/5 threshold, reroute rule |
| CL-012 | ENHANCE | Execution Handoff | Added first_parent/child/micro_step fields |
| CL-013 | ADD | Change Ledger | This table |
| CL-014 | PRESERVE | All original analysis | Context, findings, known facts, non-goals all preserved |


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-12T07:22:45.244141+00:00"
  locked_by: "fe70e60cc766"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
