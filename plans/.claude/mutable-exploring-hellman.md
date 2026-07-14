# Code Quality Governance Audit — CQGA-002
# Plan: mutable-exploring-hellman
# Type: governance_audit_production_hardening
# Mission ID: CQGA-002
# Authority: this file is the sole execution authority — do not create alternatives
# Status: READY_FOR_EXECUTION

---

## PREFLIGHT RECORD
<!-- Required before any execution agent reads this plan -->

```
repository:       c:\Users\prora\OneDrive\Documents\GitHub\format-factory
branch:           main
head_at_plan:     af879e55 (2026-07-10)
active_plan_path: C:\Users\prora\.claude\plans\mutable-exploring-hellman.md
plan_title:       Code Quality Governance Audit CQGA-002
plan_format:      markdown-taskcarded
authority_source: plan mode — mutable-exploring-hellman
plan_size_lines:  ~750 before enhancement; ~2200 after full micro-taskcardization
major_sections:   10 pre-enhancement; 26 post-enhancement (added: REQUIREMENT TRACEABILITY, QUALITY SCORING)
existing_tc_count: 32 (indexes TC-CQGA2-001 through TC-CQGA2-032)
tc_children_count: ~68 child taskcards across all phases
micro_step_count:  ~320 numbered micro-steps (MS-XXX-YY-ZZ)
state_vocabulary: OPEN → CLOSED (pre-enhancement; see §Machine State for full model)
validation_model: full 5-phase Validation Matrix with Negative Controls table
evidence_model:   22 required artifacts listed in Evidence Contract + full Supporting Artifacts Schedule
naming_convention: TC-CQGA2-NNN (parent), TC-CQGA2-NNN-NN (child), MS-CQGA2-NNN-NN-NN (micro)
duplicate_plan_risk: NONE — no competing plan files found
baseline_plan:    plans/.claude/mutable-doodling-blossom.md (CQGA-001, read-only)
supporting_artifacts_root: .local/evidences/CQGA-002/planning/ (created during execution)
```

---

## SECTION INVENTORY
<!-- Produced as part of complete-plan-read-confirmation -->

| § | Section | Type | Enhancement status |
|---|---|---|---|
| 1 | Context: The Production Problem | Analysis | Preserved |
| 2 | Root Cause Analysis (RCA-A–G) | Diagnosis | Preserved + REQ IDs added |
| 3 | What This Means In Practice | Impact table | Preserved |
| 4 | What Must Be Preserved | Constraint | Preserved |
| 5 | Production-Grade Repairs 1-5 | Design | Preserved |
| 6 | Audit Scope Adjustment | Scope | Preserved |
| 7 | REQUIREMENTS INVENTORY | New | Added |
| 8 | TASKCARD INDEX + DAG | Index | Expanded with hierarchy + deps |
| 9 | PHASE A: Audit Micro-Taskcards | Execution | Added |
| 10 | PHASE B: Gap Ledger Micro-Taskcards | Execution | Added |
| 11 | PHASE C: Repair Parent/Child/Micro-Steps | Execution | Full 3-level added |
| 12 | PHASE D: Pilot Micro-Steps | Execution | Added |
| 13 | PHASE E: Final Report Micro-Steps | Execution | Added |
| 14 | MACHINE STATE VOCABULARY | Machine | Added |
| 15 | DEPENDENCY DAG | Machine | Added |
| 16 | VALIDATION MATRIX | Machine | Added |
| 17 | EVIDENCE CONTRACT | Machine | Added |
| 18 | EXECUTION HANDOFF | Machine | Added |
| 19 | Gap Ledger Updates | Planning | Preserved |
| 20 | Tradeoffs and Limits | Analysis | Preserved |
| 21 | Verification Completion Gate | Gate | Preserved + updated |
| 22 | Critical Files | Reference | Preserved + expanded |
| 23 | Supporting Artifacts Schedule | Reference | Expanded to full 22-artifact table |
| 24 | REQUIREMENT TRACEABILITY | Machine | Added — REQ→TC→child→MS chains |
| 25 | PHASE A QUALITY SCORING | Execution | Added — 6-dimension scoring for investigation TCs |

---

## Context: The Production Problem

A prior audit (CQGA-001, 2026-07-07) concluded
`CODE_QUALITY_GOVERNANCE_HEALED_ENFORCED_PROMOTED_AND_PROTECTED`.
That verdict was premature. It audited what the rules *say*, not whether the rules *hold*.

This plan treats the governance system as a production system that must produce consistent,
verifiable outcomes across repeated autonomous runs — not just pass a one-time checklist.

Since CQGA-001 (HEAD dc1d94d8), 45 commits landed with material governance impact:
- V145 added: `validate_maintenance_obligation_overdue` (TC-MOR-C5, 2026-07-08)
- V149 added: `validate_source_stubs` via `no_stub_scan.py` (TC-PFF-R1, 2026-07-09)
- V87 demoted FAIL → WARN (commit 147b63fa — V87 is `validate_dotnet_constant_return_public_api`)
- V105/V106 detection windows extended (GOV-WINDOW-FIX-001)
- expected_count changed: 162 → 183 (overcounting bug) → 166 → 167 (V149 added)
- CI green-path fixes (11 failing tests, encoding, LOC cap)
- PQLM-001 Phase 4 residual closed (TC-PQLM-026 to TC-PQLM-029)
- Maintenance Obligation Register (MOR) added

---

## Root Cause Analysis

### RCA-A — REQ-CQGA2-001: The Supreme Directive neutralises `blocks_sprint=True`

54 validator return paths carry `blocks_sprint=True`, producing exit code 3.
CLAUDE.md §"Sprint Closeout" step 3 says explicitly:

> "Exit 3 → log rework items, attempt quick fix, **continue regardless**"
> "Sprint closeout (evidence declaration, autonomous-cycle, review package) is **best-effort infrastructure**"

Result: 54 allegedly-blocking validator paths are not actually binding. Every agent following
CLAUDE.md correctly will continue past them. The governance system has no teeth for 52 of its
54 blocking paths.

**Exception:** Only 2 GOV_BLOCK types in `check_continuation.py` lines 519-520 create actual
hard stops:
```python
"GOV_BLOCK:monolith_detection_validator",
"GOV_BLOCK:validate_source_architecture",
```

CLAUDE.md lists 4 validators as GOV_BLOCK (`validate_multi_responsibility_file` and
`validate_analytics_naming_enforced` are also listed), but the code only checks 2.
The documented intent and the enforcement code are inconsistent.

### RCA-B — REQ-CQGA2-002: Declared-files scope enables bypass-by-omission

All 167 validators fire on `changed_files` extracted from `planned_work_items` in the
declaration (governance_validators_ext3.py lines 893-923). The pipeline has no independent
mechanism to verify that declared `changed_files` matches what git actually changed.

Result: An agent that modifies `src/python/csv/csv_parser.py` but does not list it in
`changed_files` → zero quality validators fire on that file. The bypass requires only
an incomplete declaration, not active deception.

### RCA-C — REQ-CQGA2-003: Validator count tested by headcount, not by function

CI tests `expected_count == 167`. This passes when the right number of validators are
*registered*, not when they *execute correctly*. A validator that imports successfully
but returns a wrong schema, misses its target pattern, or silently errors still
contributes to the count of 167. The CI test is a registration census, not a
functional fitness check.

Evidence: The count went 162 → 183 (overcounting bug) → 166 → 167 across 4 commits,
each requiring a manual CI fix. A functional test suite would have caught the overcount
immediately because individual validators would have returned wrong results.

### RCA-D — REQ-CQGA2-004: Enforcement level drift with no governance record

V87 (`validate_dotnet_constant_return_public_api`) was demoted from FAIL to WARN via a
CI fix commit (`147b63fa`). The commit message says "readme freshness" but the code is
constant-return detection. Either the message is wrong or the code was silently changed.
Either way: an enforcement-level reduction with no gap entry, no policy rationale, no
ACKNOWLEDGED_BY_DESIGN record.

CQGA-001 identified this as a pattern risk but did not produce a governance gate to
prevent it. The gap exists: there is no policy requiring a gap entry before demoting
`blocks_sprint=True` to `blocks_sprint=False`.

### RCA-E — REQ-CQGA2-005: Pre-commit hooks never installed

CQG-001 (CRITICAL, OPEN since CQGA-001): `.git/hooks/` contains only `.sample` files.
All pre-commit hooks (`scope-guard`, `validate-source-architecture`, `ruff`) are inert.
Local commits bypass all pre-commit quality gates. This gap has a documented remediation
(`pre-commit install`) but no automated enforcement of the remediation.

### RCA-F — REQ-CQGA2-006: SAL-conditional traceability produces false-green

V13 (`validate_spec_fact_refs_wired`) and V47 (`validate_spec_fact_refs_in_sal_output`)
both require `.local/supervisor/sal-facts-latest.json` to exist. If absent, they pass
vacuously. The CQGA-001 audit noted this as CQG-008 (PARTIAL) but did not add a
pre-flight check that blocks product declarations when SAL is absent. Result: the
spec→stub→domain traceability chain — the most important architectural invariant in
the system — is unenforced when SAL is not populated.

### RCA-G — REQ-CQGA2-007: No independent scan of git state at closeout

`autonomous_cycle.py` does not call `git diff HEAD~1..HEAD --name-only` and compare
it against the declared `changed_files`. If an agent changes 5 files but declares 2,
the 3 undeclared files never appear in any validator's input. This is a structural gap:
the pipeline trusts self-reporting exclusively.

---

## What This Means In Practice

The 167-validator framework is architecturally sound but operationally permissive:

| Control | Documented Strength | Operational Reality |
|---|---|---|
| 54 `blocks_sprint=True` paths | Block product sprints | Exit 3 → continue regardless |
| 4 GOV_BLOCK validators | Hard stop on structural failures | 2 of 4 wired in code |
| Spec→stub traceability (V13/V47) | Enforced | Vacuous when SAL absent |
| Pre-commit hooks | Prevent bad local commits | Never installed (inert) |
| Declared `changed_files` scope | All changed files checked | Trust model — self-reported |
| Validator count CI test | Confirms 167 registered | Does not confirm they fire correctly |
| Enforcement level changes | Policy-governed | No policy — CI fix commits |

---

## What Must Be Preserved

Do not weaken or remove:

- The 167-validator detection layer (expand the GOV_BLOCK list; do not remove validators)
- `proof_adequacy_contract.py` AST analysis (fixed CQG-003; functional)
- `promotion-ledger.yaml` + hash comparison (functional, needs signature upgrade — CQG-006)
- `source-structure-baseline.json` write-once caps (functional)
- `@validator` decorator contract (TC-CQGA-033-02 — the pattern is correct)
- Skill command files with blocking validator IDs (TC-CQGA-033-04 — correct direction)

---

## Production-Grade Solution: Five Structural Repairs

### Repair 1: GOV_BLOCK Registry (closes RCA-A, RCA-D / REQ-CQGA2-001, REQ-CQGA2-004)

**Problem:** 2-item hardcoded list in `check_continuation.py`; CLAUDE.md says 4 validators
but code checks 2; enforcement level changes undocumented.

**Solution:**
Create `tools/supervisor/governance_block_registry.py` — a machine-readable registry of
which validator conditions create hard-stop GOV_BLOCKs.

```python
# governance_block_registry.py
STRUCTURAL_GOV_BLOCKS = [
    # Original 2 (already wired)
    "GOV_BLOCK:monolith_detection_validator",
    "GOV_BLOCK:validate_source_architecture",
    # Fix: add the 2 in CLAUDE.md that are missing from code
    "GOV_BLOCK:validate_multi_responsibility_file",
    "GOV_BLOCK:validate_analytics_naming_enforced",
    # New: code quality guards for new files only
    "GOV_BLOCK:validate_suspicious_filenames",               # V100
    "GOV_BLOCK:validate_undocumented_public_python_apis",    # V102 (new files only)
    "GOV_BLOCK:validate_constant_return_public_methods",     # V104 (new files only)
    "GOV_BLOCK:validate_source_stubs",                       # V149
]

ENFORCEMENT_LEVEL_CHANGE_POLICY = "docs/code-quality/enforcement-level-change-policy.md"
```

**Tradeoff:** V102/V104 new-file scope must carry over; legacy file violations remain exit-3.
Do NOT add V103, V107 (high false-positive risk).

**Regression control:** `tests/supervisor/test_governance_block_registry.py`

---

### Repair 2: Declaration Integrity Check (closes RCA-B, RCA-G / REQ-CQGA2-002, REQ-CQGA2-007)

**Problem:** Validators fire only on self-declared `changed_files`. Undeclared git changes
bypass all quality enforcement.

**Solution:** Create `tools/supervisor/declaration_integrity_check.py`:

```python
def check_declaration_integrity(declaration: dict, repo_root: Path) -> dict:
    """Compare declared changed_files vs git diff HEAD~1..HEAD --diff-filter=ACMR --name-only."""
```

Rules:
- If `quality_paths` non-empty (undeclared in `src/python/` or `src/net/`):
  → `blocks_sprint=True`, add `GOV_BLOCK:undeclared_source_change` to `rework_items`
- If non-source undeclared changes: WARN only
- First commit (no HEAD~1): skip with WARN

Wire into `autonomous_cycle.py` as Step 0a (before validators run).

**Tradeoff:** Requires git at closeout (already available). ~1s latency. Edge cases: merge
commits, first commit, detached HEAD.

**Regression control:** `tests/supervisor/test_declaration_integrity.py`

---

### Repair 3: Validator Functional Test Suite (closes RCA-C / REQ-CQGA2-003)

**Problem:** CI tests `expected_count == 167`. Does not test validators fire correctly.

**Solution:** `tests/governance/test_validators_functional.py` — parametrized pytest.

Priority 10 validators (P0):
```
V100 validate_suspicious_filenames
V102 validate_undocumented_public_python_apis
V104 validate_constant_return_public_methods
V109 validate_files_outside_approved_layout
V149 validate_source_stubs
V105 validate_getter_without_parser_source
V106 validate_setter_without_writer_path
GOV_BLOCK:monolith_detection_validator
GOV_BLOCK:validate_source_architecture
GOV_BLOCK:validate_multi_responsibility_file
```

Each test: call validator with known-bad synthetic declaration → assert FAIL + blocks_sprint=True.

**Tradeoff:** Start with 10 P0; expand to full 54 over 2-3 sprints. Replace count test after
80% functional coverage.

**Regression control:** `pytest tests/governance/ -k functional` in CI.

---

### Repair 4: Pre-commit Installation Verification (closes RCA-E / REQ-CQGA2-005)

**Problem:** CQG-001 CRITICAL — pre-commit never installed; all local hooks inert.

**Solution (3-part):**

- Part A: AGENTS.md §A-precommit — "Verify pre-commit hooks installed before source modification"
- Part B: `autonomous_cycle.py` pre-flight `_check_precommit_installed()` → WARN when absent
- Part C: CI step runs `pre-commit run ruff --all-files` as independent quality gate

**Tradeoff:** Parts A/B are prompt-based; Part C is the only structural enforcement.
CQG-001 moves to OPEN_WITH_PARTIAL_MITIGATION; full close requires CI part C.

**Regression control:** `tests/governance/test_precommit.py`

---

### Repair 5: SAL Population Gate + Enforcement Level Change Policy

#### 5A — SAL gate (closes RCA-F / REQ-CQGA2-006)

Add `sprint_executor_validate.py` Phase 14:
```python
def _phase14_sal_population_gate(declaration, repo_root) -> list[str]:
    # WARN if PRODUCT_SOURCE items declared but sal-facts-latest.json absent
```
Severity: WARN (not GOV_BLOCK — would halt all product work for SAL-less formats).

#### 5B — Enforcement level change policy (closes RCA-D / REQ-CQGA2-004)

Create `docs/code-quality/enforcement-level-change-policy.md`:
- Rule ELP-001: any FAIL→WARN demotion requires gap entry with ACKNOWLEDGED_BY_DESIGN
- Rule ELP-002: CI-pressure demotions are prohibited
Add CQG-017 gap entry for V87 demotion.

**Regression control:** V-ELP-001 (new validator checking for policy compliance).

---

## Audit Scope Adjustment

CQGA-002 must do two things:

1. **Delta audit** — reconcile 45 post-CQGA-001 commits (validator counts, V87 demotion,
   V105/V106 window, V145/V149 additions)

2. **Structural hardening** — implement Repairs 1-5 as concrete code changes

The CQGA-001 verdict cannot stand unchanged because RCA-A proves the governance system does not
enforce its own `blocks_sprint=True` rules in production.

---

## REQUIREMENTS INVENTORY

| REQ-ID | RCA | Statement | Repair |
|---|---|---|---|
| REQ-CQGA2-001 | RCA-A | GOV_BLOCK list must match CLAUDE.md documentation and cover all structural-failure validators | Repair 1 |
| REQ-CQGA2-002 | RCA-B | Declared changed_files must be cross-checked against git diff before validators run | Repair 2 |
| REQ-CQGA2-003 | RCA-C | Every blocking validator must have a functional test asserting it fires on known-bad input | Repair 3 |
| REQ-CQGA2-004 | RCA-D | Any enforcement level reduction must produce a gap ledger entry before the change | Repair 5B |
| REQ-CQGA2-005 | RCA-E | Pre-commit hook absence must be detected and reported at sprint start | Repair 4 |
| REQ-CQGA2-006 | RCA-F | PRODUCT_SOURCE declarations must warn when SAL absent (V13/V47 would be vacuous) | Repair 5A |
| REQ-CQGA2-007 | RCA-G | (Absorbed by REQ-CQGA2-002 — same repair addresses both) | Repair 2 |
| REQ-CQGA2-008 | CQGA-001 baseline | Gap ledger must be reconciled with CQGA-002 findings | TC-CQGA2-011 |
| REQ-CQGA2-009 | Audit scope | Delta audit of 45 post-CQGA-001 commits must produce evidence artifacts | TC-CQGA2-001–010 |
| REQ-CQGA2-010 | Pilots | All 14 pilots must pass with live test evidence | TC-CQGA2-018–031 |
| REQ-CQGA2-011 | Reporting | Final audit report must produce a verdict based on pilot results and repair status | TC-CQGA2-032 |
| REQ-CQGA2-012 | Idempotency | Second run of all pilots must produce zero material changes | TC-CQGA2-029 |

---

## MACHINE STATE VOCABULARY

### Parent Taskcard States
```
PROPOSED           → identified, not yet sized or resourced
READY              → inputs available, predecessors CLOSED
IN_PROGRESS        → agent has started
CHILDREN_IN_PROGRESS → parent active, children executing
INTEGRATION_PENDING  → all children CLOSED, parent integration checks pending
VERIFIED           → integration checks passed
SCORED             → quality scored (≥4/5 required)
CLOSED             → all criteria met, evidence complete
BLOCKED            → predecessor or input not available
BLOCKED_EXTERNAL   → blocked by a TRUE_EXTERNAL_GATE
DEFERRED_WITH_REASON → scoped-out with documented reason
```

### Child Taskcard States
```
TODO → READY → IN_PROGRESS → IMPLEMENTED → VERIFIED → SCORED → CLOSED
       REROUTED (score <4/5 on mandatory dimension)
       BLOCKED / BLOCKED_EXTERNAL / DEFERRED_WITH_REASON
```

### Micro-Step States
```
PENDING → READY → ACTIVE → COMPLETE
                          → FAILED (→ READY on retry)
                          → BLOCKED
         SKIPPED_NOT_APPLICABLE (must record reason)
```

### Forbidden Transitions
- Child: TODO → CLOSED (must pass IMPLEMENTED and VERIFIED)
- Child: IN_PROGRESS → CLOSED (must pass IMPLEMENTED)
- Parent: CLOSED while any mandatory child not CLOSED
- Parent: SCORED → CLOSED when any dimension score <4/5
- Micro-step: SKIPPED_NOT_APPLICABLE without written reason

### Quality Scoring
Every child taskcard scored 1–5 on: requirement_correctness, implementation_correctness,
scope_discipline, validation_strength, evidence_completeness, regression_safety.
Mandatory threshold: ≥4/5 on each. Any dimension <4/5 → REROUTED.

---

## DEPENDENCY DAG

```
TC-CQGA2-001 ──► TC-CQGA2-002 ──► TC-CQGA2-003
     │                │                 │
     │                │                 ▼
     │                │           TC-CQGA2-004
     │                │                 │
     │                ▼                 ▼
     │           TC-CQGA2-005 ─► TC-CQGA2-006
     │                │                 │
     │                ▼                 ▼
     └──────────► TC-CQGA2-007 ─► TC-CQGA2-008
                       │                │
                       ▼                ▼
                  TC-CQGA2-009 ─► TC-CQGA2-010
                                        │
                                        ▼
                                  TC-CQGA2-011 (Gap Ledger)
                                        │
                          ┌─────────────┼──────────────┐
                          ▼             ▼               ▼
                    TC-CQGA2-012  TC-CQGA2-013    TC-CQGA2-016
                    (Repair 1)    (Repair 2)      (Repair 5A)
                          │             │               │
                          ▼             ▼               ▼
                    TC-CQGA2-014  TC-CQGA2-015    TC-CQGA2-017
                    (Repair 3)    (Repair 4)      (Repair 5B)
                          │
                          ▼
                All Phase D pilots (TC-018 through TC-031) in sequence
                          │
                          ▼
                    TC-CQGA2-032 (Final Report)
```

**Parallel-safe groups:**
- TC-CQGA2-001 through TC-CQGA2-010: sequential (each feeds next)
- TC-CQGA2-012 + TC-CQGA2-016 + TC-CQGA2-017: parallel after TC-011
- TC-CQGA2-013 + TC-CQGA2-014 + TC-CQGA2-015: parallel after TC-012 closes

**File ownership locks** (no two parallel TCs may touch same file):
- `check_continuation.py`: TC-CQGA2-012 only
- `autonomous_cycle.py`: TC-CQGA2-013 then TC-CQGA2-015 (sequential)
- `sprint_executor_validate.py`: TC-CQGA2-016 only
- `reports/code-quality/code-quality-governance-ledger.yaml`: TC-CQGA2-011 then TC-CQGA2-017

---

## PHASE A: AUDIT TASKCARDS (TC-CQGA2-001 through TC-CQGA2-010)

Phase A tasks are investigative. Each follows the pattern:
`inspect → record findings → compute delta from CQGA-001 → write evidence artifact`.

### TC-CQGA2-001: Bind System — Baseline + Delta Enumeration
**Type:** PARENT | **Status:** READY | **REQ:** REQ-CQGA2-009
**Prereqs:** None | **Successor:** TC-CQGA2-002

**Objective:** Establish CQGA-002 baseline; enumerate and classify 45 post-CQGA-001 commits.

**Children:**
- TC-CQGA2-001-01: Read CQGA-001 audit report in full; record current head git SHA
- TC-CQGA2-001-02: Run `git log dc1d94d8..HEAD --oneline` and classify each commit into:
  VALIDATOR_CHANGE | PRODUCT_SOURCE | GOVERNANCE_INFRA | TEST_FIX | PROCESS | OTHER
- TC-CQGA2-001-03: Write `.local/evidences/CQGA-002/planning/mission.yaml` with classified commit list

**Micro-steps for TC-CQGA2-001-02:**
- MS-001-02-01: Run `git log dc1d94d8..HEAD --oneline` → capture output
- MS-001-02-02: For each of the 45 commits, assign one category label
- MS-001-02-03: Identify the 5-8 commits with VALIDATOR_CHANGE classification for deeper inspection
- MS-001-02-04: Read those commits via `git show <SHA> --stat` to confirm what changed

**Completion evidence:** `mission.yaml` exists with `classified_commits` field.
**Validation:** `python -c "import yaml; d=yaml.safe_load(open('.local/evidences/CQGA-002/planning/mission.yaml')); assert 'classified_commits' in d"`

---

### TC-CQGA2-002: Inventory V1-V167 Delta
**Type:** PARENT | **Status:** READY (after TC-001 CLOSED) | **REQ:** REQ-CQGA2-009
**Prereqs:** TC-CQGA2-001 | **Successor:** TC-CQGA2-003

**Objective:** Document what changed in the validator set since CQGA-001 (V1-V162 → V1-V167).

**Children:**
- TC-CQGA2-002-01: Confirm expected_count=167 in `governance_validator_runner.py`; list V145 and V149 registration entries
- TC-CQGA2-002-02: Resolve V87 discrepancy — run `git show 147b63fa -- tools/supervisor/governance_validators_dotnet_semantic.py` to see what actually changed
- TC-CQGA2-002-03: Read V145 definition; classify as AUTHORITATIVE_AND_ENFORCED or ADVISORY_ONLY; note blocks_sprint value
- TC-CQGA2-002-04: Read V149 registration in runner (already found at line 757); confirm blocks_sprint value
- TC-CQGA2-002-05: Write `.local/evidences/CQGA-002/planning/validator-delta-table.yaml`

**Micro-steps for TC-CQGA2-002-02 (V87 discrepancy resolution):**
- MS-002-02-01: Run `git show 147b63fa --stat` → confirm which files changed
- MS-002-02-02: Run `git show 147b63fa -- tools/supervisor/governance_validators_dotnet_semantic.py` → read diff
- MS-002-02-03: Compare diff against current file content (read governance_validators_dotnet_semantic.py lines 140-230)
- MS-002-02-04: Determine: (a) commit message was wrong, (b) code was silently changed, or (c) different validator
- MS-002-02-05: Record finding in validator-delta-table.yaml as `v87_discrepancy_resolution`

**Completion evidence:** `validator-delta-table.yaml` with entries for V145, V149, V87.
**Validation:** V87 discrepancy is unambiguously resolved with commit evidence.

---

### TC-CQGA2-003: Verify Code-Creation and Modification Path Accuracy
**Type:** PARENT | **Status:** READY (after TC-002) | **REQ:** REQ-CQGA2-009

**Children:**
- TC-CQGA2-003-01: Read `.claude/commands/add-python-api.md` → verify V100/V102/V104/V109 listed in Governance Validators section
- TC-CQGA2-003-02: Read `.claude/commands/add-dotnet-api.md` → verify V90/V91/V92/V95/V105/V106/V108/V109 listed
- TC-CQGA2-003-03: Check if V145 or V149 should be added to these skill files (per TC-CQGA-033-04 pattern)
- TC-CQGA2-003-04: Search `.claude/commands/` for any skill files added since CQGA-001 that touch src/python/ or src/net/
- TC-CQGA2-003-05: Confirm CCP-BYPASS (direct Edit/Bash) still has no preventive gate; V149 is detective only

**Micro-steps for TC-CQGA2-003-01:**
- MS-003-01-01: Locate `.claude/commands/add-python-api.md` — confirm file exists
- MS-003-01-02: Read file completely (do not skim)
- MS-003-01-03: Find "Governance Validators" or "Blocking Validators" section in the file
- MS-003-01-04: List all V-numbers present; check if V100, V102, V104, V109 all appear
- MS-003-01-05: Record finding: ALL_PRESENT | MISSING_VXXX | SECTION_ABSENT

**Micro-steps for TC-CQGA2-003-02:**
- MS-003-02-01: Locate `.claude/commands/add-dotnet-api.md` — confirm file exists
- MS-003-02-02: Read file completely
- MS-003-02-03: Find governance validator section
- MS-003-02-04: List all V-numbers; check V90/V91/V92/V95/V105/V106/V108/V109 each present
- MS-003-02-05: Record finding: ALL_PRESENT | MISSING_VXXX | SECTION_ABSENT

**Micro-steps for TC-CQGA2-003-03:**
- MS-003-03-01: Read V145 definition in governance_validators file — what does it validate?
- MS-003-03-02: Read V149 definition — what does it validate (stubs/TODOs in source)?
- MS-003-03-03: Assess: does V145 apply to code added via add-python-api.md skill? (MAINTENANCE_OBLIGATION scope)
- MS-003-03-04: Assess: does V149 apply? (stub detection — yes, any new Python file)
- MS-003-03-05: Record: "V149 SHOULD be listed in add-python-api.md" or "V149 already listed" (defer edit to execution)

**Micro-steps for TC-CQGA2-003-04:**
- MS-003-04-01: `git log dc1d94d8..HEAD --oneline -- .claude/commands/` → list new or modified skill command files
- MS-003-04-02: For each new/modified file: read it; check for any `changed_files` declarations touching `src/python/` or `src/net/`
- MS-003-04-03: For any new skill file referencing source paths: confirm its governance validator list is complete
- MS-003-04-04: Record any gap (new skill file missing required validator references)

**Micro-steps for TC-CQGA2-003-05:**
- MS-003-05-01: Search `governance_validators_ext3.py` for any write-time interception on Edit or Bash tool calls
- MS-003-05-02: Confirm there is no mechanical prevention for CCP-BYPASS path
- MS-003-05-03: Confirm V149 documentation says "detective" not "preventive"
- MS-003-05-04: Record: "CCP-BYPASS confirmed: no preventive gate; V149 detects stubs at closeout only"

**Completion evidence:** Code-creation path table (CCP-001 through CCP-BYPASS) confirmed accurate or updated.
**Validation:** All 5 child findings recorded; no child left with status UNKNOWN.

---

### TC-CQGA2-004: Audit Organization, Naming, Hierarchy (Delta Only)
**Type:** PARENT | **Status:** READY (after TC-003) | **REQ:** REQ-CQGA2-009

**Children:**
- TC-CQGA2-004-01: Read `docs/code-quality/product-file-layout-contract.yaml` — check if any new per-file layout entries added since CQGA-001
- TC-CQGA2-004-02: Verify FODS gitignore fix (commit 5eae2cd7) — does it affect tracked source files?
- TC-CQGA2-004-03: Confirm V109 still enforces approved_layout for FODS; confirm V100 pattern list unchanged
- TC-CQGA2-004-04: CQG-012 status: still OPEN_DESIGN_GAP (19/20 formats no per-file layout)?

**Micro-steps for TC-CQGA2-004-01:**
- MS-004-01-01: Read `docs/code-quality/product-file-layout-contract.yaml` fully
- MS-004-01-02: Count existing `per_file_layout` entries; compare to CQGA-001 count (1 entry: FODS)
- MS-004-01-03: If new entries added since CQGA-001: record format_id, required files list, approval date
- MS-004-01-04: Record: "per_file_layout count: X (CQGA-001 baseline: 1)"

**Micro-steps for TC-CQGA2-004-02:**
- MS-004-02-01: `git show 5eae2cd7 --stat` — identify which files changed
- MS-004-02-02: If `.gitignore` changed: read the diff; confirm it only affects untracked build artifacts (not tracked source)
- MS-004-02-03: Run `git ls-files src/python/fods/` — confirm no previously-tracked files became ignored
- MS-004-02-04: Record: "FODS gitignore fix: source-safe (ignores build artifacts only)" or note if risk found

**Micro-steps for TC-CQGA2-004-03:**
- MS-004-03-01: Read `governance_validators_ext3.py` — find `validate_files_outside_approved_layout` (V109)
- MS-004-03-02: Read `validate_suspicious_filenames` (V100) — extract current FORBIDDEN_PATTERN list
- MS-004-03-03: Compare V100 pattern list to CQGA-001 baseline (expected: no additions since CQGA-001)
- MS-004-03-04: Record: "V109 FODS scope: [status]"; "V100 patterns: [count] (unchanged | +X added)"

**Micro-steps for TC-CQGA2-004-04:**
- MS-004-04-01: Count formats with `per_file_layout` entries in `product-file-layout-contract.yaml`
- MS-004-04-02: Count total active Python formats (expected: 20 from oracle records)
- MS-004-04-03: Compute: formats_without_layout = 20 - formats_with_layout
- MS-004-04-04: Record CQG-012 status: OPEN_DESIGN_GAP (if still 19/20 without layout) | IMPROVED (if more formats added)

**Completion evidence:** Organization section delta recorded; CQG-012 status confirmed.
**Validation:** All 4 child findings recorded with numeric evidence.

---

### TC-CQGA2-005: Audit Writing Practices — V149 and V105/V106 Window
**Type:** PARENT | **Status:** READY (after TC-004) | **REQ:** REQ-CQGA2-009

**Children:**
- TC-CQGA2-005-01: Read `no_stub_scan.py` fully; confirm FORBIDDEN_TERMS list and allowlist patterns
- TC-CQGA2-005-02: Run V149 live: `python -c "from tools.review.no_stub_scan import scan_path; import json; print(json.dumps(scan_path('src/python/csv'), indent=2)[:2000])"` on a format
- TC-CQGA2-005-03: Confirm V149 blocks_sprint value by reading runner line 757-765
- TC-CQGA2-005-04: Read GOV-WINDOW-FIX-001 commit (`6bc5ad75`) — what exactly was masked before?
- TC-CQGA2-005-05: Live-test V105: synthesize a declaration with a new .NET file containing a getter without XML read path; call validate_getter_without_parser_source; confirm FAIL

**Micro-steps for TC-CQGA2-005-01:**
- MS-005-01-01: Read `tools/review/no_stub_scan.py` completely (all lines)
- MS-005-01-02: Extract and record: FORBIDDEN_TERMS list (all entries)
- MS-005-01-03: Extract and record: allowlist patterns (files/patterns excluded from scanning)
- MS-005-01-04: Note: does the scanner detect bare `pass` methods? Does it have a "bare_pass" mode?
- MS-005-01-05: Record: FORBIDDEN_TERMS count; allowlist entry count; bare_pass detection: yes/no

**Micro-steps for TC-CQGA2-005-02:**
- MS-005-02-01: Run the V149 live command: `python -c "from tools.review.no_stub_scan import scan_path; import json; print(json.dumps(scan_path('src/python/csv'), indent=2)[:2000])"`
- MS-005-02-02: Capture stdout output
- MS-005-02-03: Inspect output: does it return a list of violations or a clean result?
- MS-005-02-04: Record: "V149 live scan of csv: [CLEAN | N violations found at path X]"

**Micro-steps for TC-CQGA2-005-03:**
- MS-005-03-01: Read `tools/supervisor/governance_validator_runner.py` lines 757-765
- MS-005-03-02: Find the `validate_source_stubs` registration entry
- MS-005-03-03: Record: `blocks_sprint` value (True | False) and any scope conditions
- MS-005-03-04: If `blocks_sprint=False`: record "V149 is WARN-only — GOV_BLOCK registry addition needed (Repair 1)"

**Micro-steps for TC-CQGA2-005-04:**
- MS-005-04-01: `git show 6bc5ad75 -- tools/supervisor/governance_validators_ext3.py` → read diff
- MS-005-04-02: Identify what "detection window" means: was it a date-range check? a line-count check?
- MS-005-04-03: Confirm the fix is now correct and V105/V106 fire on current declarations with new .NET files

**Micro-steps for TC-CQGA2-005-05:**
- MS-005-05-01: Find `validate_getter_without_parser_source` import path in governance_validators_ext3.py
- MS-005-05-02: Construct minimal synthetic declaration: `{"planned_work_items": [{"item_id": "T1", "item_type": "PRODUCT_SOURCE", "changed_files": ["src/net/csv/CsvReader.cs"], "is_new_file": True, "file_content_excerpt": "public string GetValue() { return ...; }"}]}`
- MS-005-05-03: Call validator: `result = validate_getter_without_parser_source(declaration, repo_root)`
- MS-005-05-04: Assert `result["status"] == "FAIL"` — if PASS, the window fix is not working
- MS-005-05-05: Record: "V105 live test: FAIL (correct) | PASS (window fix broken)" with full result dict

**Completion evidence:** V149 live test output; V105/V106 window fix confirmed; all 5 child findings recorded.

---

### TC-CQGA2-006: Audit Comments/Docs — V87 Demotion Impact
**Type:** PARENT | **Status:** READY (after TC-005) | **REQ:** REQ-CQGA2-009
**Prereqs:** TC-CQGA2-002 (V87 discrepancy must be resolved first)

**Children:**
- TC-CQGA2-006-01: Based on TC-CQGA2-002-02 findings — document what V87 actually covers post-demotion
- TC-CQGA2-006-02: Assess whether V87 demotion creates a governance documentation gap (if V87 covered comments/README accuracy, WARN-only is weaker)
- TC-CQGA2-006-03: Check V88/V89 still FAIL-level for relevant .NET documentation validators

**Micro-steps for TC-CQGA2-006-01:**
- MS-006-01-01: Read `root-cause-proof-bundle.yaml` (from TC-CQGA2-010-07) — find `v87_discrepancy_resolution` field
- MS-006-01-02: Read `tools/supervisor/governance_validators_dotnet_semantic.py` lines 140-230 — find V87 function body
- MS-006-01-03: Document: what specific .NET code pattern does V87 detect POST-demotion? (e.g., `return constant` patterns in public APIs)
- MS-006-01-04: Document: what was its behavior PRE-demotion? (blocks_sprint=True → False, same detection logic or changed?)
- MS-006-01-05: Record: "V87 post-demotion: detects [pattern], severity WARN (was FAIL), scope [unchanged | narrowed]"

**Micro-steps for TC-CQGA2-006-02:**
- MS-006-02-01: Assess: does V87 cover constant-return in public .NET APIs? Is WARN severity adequate?
- MS-006-02-02: Are there other validators that catch this pattern with FAIL severity? (check V88, V89, V90 scope)
- MS-006-02-03: Determine documentation gap severity: CRITICAL (if V87 is sole detector, now WARN) | MODERATE (if other FAILs exist) | LOW (if V87 was redundant)
- MS-006-02-04: Record: "V87 demotion documentation gap: [severity] — [rationale]"

**Micro-steps for TC-CQGA2-006-03:**
- MS-006-03-01: Find V88 and V89 definitions in governance_validators_dotnet_semantic.py
- MS-006-03-02: Read V88 registration in runner — confirm `blocks_sprint` value
- MS-006-03-03: Read V89 registration in runner — confirm `blocks_sprint` value
- MS-006-03-04: Record: "V88: [name], blocks_sprint=[value]"; "V89: [name], blocks_sprint=[value]"

**Completion evidence:** V87 governance impact documented with severity; V88/V89 enforcement levels confirmed; CQG-017 candidate confirmed.

---

### TC-CQGA2-007: Audit Traceability — SAL State, CQG-008/013
**Type:** PARENT | **Status:** READY (after TC-006) | **REQ:** REQ-CQGA2-009

**Children:**
- TC-CQGA2-007-01: Check `.local/supervisor/sal-facts-latest.json` existence and content size
- TC-CQGA2-007-02: If SAL exists: call V13 with a bad spec_fact_ref → confirm FAIL (not vacuous pass)
- TC-CQGA2-007-03: Inspect PQLM-001 Phase 4 commits (TC-PQLM-026 to TC-PQLM-029) — did they affect traceability?
- TC-CQGA2-007-04: Confirm CQG-008 and CQG-013 status unchanged (or document improvement)

**Micro-steps for TC-CQGA2-007-01:**
- MS-007-01-01: Check if `.local/supervisor/sal-facts-latest.json` exists: `ls -la .local/supervisor/sal-facts-latest.json`
- MS-007-01-02: If exists: read first 50 lines; record: total fact count (`wc -l` or `jq length`)
- MS-007-01-03: If absent: record "SAL absent — V13/V47 will pass vacuously (CQG-008 CONFIRMED)"
- MS-007-01-04: Record: "SAL state: [PRESENT size=X | ABSENT]"

**Micro-steps for TC-CQGA2-007-02:**
- MS-007-02-01: PRECONDITION: only execute if SAL is PRESENT (skip if absent, record SKIPPED_NOT_APPLICABLE with reason)
- MS-007-02-02: Find `validate_spec_fact_refs_wired` (V13) import path
- MS-007-02-03: Construct declaration with `spec_fact_refs: ["INVALID_QNAME:does_not_exist"]`
- MS-007-02-04: Call V13; assert `result["status"] == "FAIL"` (not PASS)
- MS-007-02-05: Record: "V13 behavior: FAIL on bad ref (correct enforcement)" or "V13 PASS (vacuous — SAL absent path confirmed)"

**Micro-steps for TC-CQGA2-007-03:**
- MS-007-03-01: `git log --oneline` | grep -i "pqlm\|TC-PQLM-02[6-9]" → find the 4 commits
- MS-007-03-02: For each commit: `git show <SHA> --stat` — which files changed?
- MS-007-03-03: Did any commit change: governance_validators files? sprint_executor_validate? SAL ingestion tools? spec/ directories?
- MS-007-03-04: Record: "PQLM-001 Phase 4 traceability impact: [NONE | affects SAL at X | affects validators at Y]"

**Micro-steps for TC-CQGA2-007-04:**
- MS-007-04-01: Read current gap ledger entries for CQG-008 and CQG-013 (status field only)
- MS-007-04-02: Compare to CQGA-001 baseline: CQG-008 was PARTIAL; CQG-013 was OPEN_DESIGN_GAP
- MS-007-04-03: Assess: have any PQLM commits or other changes improved either gap? (e.g., SAL now populated, test-to-spec enforcement added)
- MS-007-04-04: Record: "CQG-008: [unchanged=PARTIAL | improved=...]"; "CQG-013: [unchanged=OPEN_DESIGN_GAP | improved=...]"

**Completion evidence:** SAL state confirmed; V13 behavior documented; PQLM-001 traceability impact assessed; CQG-008/013 status confirmed.

---

### TC-CQGA2-008: Audit Review/Acceptance — Grader and Closeout Integrity
**Type:** PARENT | **Status:** READY (after TC-007) | **REQ:** REQ-CQGA2-009

**Children:**
- TC-CQGA2-008-01: Verify `proof_adequacy_contract.py` still classifies WEAK_PROOF → adequate=False (read lines defining classify logic)
- TC-CQGA2-008-02: Check CI fix commits (3b1d7443) — did any change grader behavior?
- TC-CQGA2-008-03: Verify fallback_grade_cap="ACCEPTED_WITH_LIMITATIONS" still enforced in `grade_intermediate_verify.py`
- TC-CQGA2-008-04: Confirm `validate_skill_contracts.py` extended check (TC-CQGA-033-03) still functional

**Micro-steps for TC-CQGA2-008-01:**
- MS-008-01-01: Find `tools/supervisor/proof_adequacy_contract.py` — confirm file exists
- MS-008-01-02: Read file; find the `classify` or `assess_proof_adequacy` function
- MS-008-01-03: Find where WEAK_PROOF is assigned `adequate=False` — record the line number and logic
- MS-008-01-04: Confirm the logic is unchanged (no commit in dc1d94d8..HEAD modified this function)
- MS-008-01-05: Record: "WEAK_PROOF → adequate=False at line X: [CONFIRMED | CHANGED — detail]"

**Micro-steps for TC-CQGA2-008-02:**
- MS-008-02-01: `git show 3b1d7443 --stat` — list which files changed
- MS-008-02-02: If `grade_intermediate_verify.py` or `proof_adequacy_contract.py` changed: read the diff carefully
- MS-008-02-03: Determine: did the CI fix change grading logic, acceptance thresholds, or just test infrastructure?
- MS-008-02-04: Record: "CI fix 3b1d7443 grader impact: [NONE | CHANGED grader at lines X-Y]"

**Micro-steps for TC-CQGA2-008-03:**
- MS-008-03-01: Find `tools/supervisor/grade_intermediate_verify.py` — confirm file exists
- MS-008-03-02: Search for `fallback_grade_cap` or `ACCEPTED_WITH_LIMITATIONS` in the file
- MS-008-03-03: Read the lines around it; confirm the cap is still `"ACCEPTED_WITH_LIMITATIONS"` (not `"ACCEPTED"` or removed)
- MS-008-03-04: Record: "fallback_grade_cap: [value confirmed | CHANGED to X]"

**Micro-steps for TC-CQGA2-008-04:**
- MS-008-04-01: Find `tools/supervisor/validate_skill_contracts.py` — confirm file exists
- MS-008-04-02: Search for the TC-CQGA-033-03 extended check (e.g., contract field validation beyond basic schema)
- MS-008-04-03: Confirm it is still registered and called in the validation pipeline
- MS-008-04-04: Record: "validate_skill_contracts.py extended check: [FUNCTIONAL | BROKEN — detail]"

**Completion evidence:** Grader integrity confirmed at line-level; fallback_grade_cap confirmed; any changes documented.

---

### TC-CQGA2-009: Audit Promotion/Reopening — promotion-ledger.yaml
**Type:** PARENT | **Status:** READY (after TC-008) | **REQ:** REQ-CQGA2-009

**Children:**
- TC-CQGA2-009-01: Read `registry/promotion-ledger.yaml` — has any entry been promoted to PROMOTED_STABLE?
- TC-CQGA2-009-02: Verify `autonomous_cycle.py` reopening trigger still at lines ~1039/1063; read those lines
- TC-CQGA2-009-03: Confirm CQG-006 (name-only hash) still PARTIALLY_FIXED (no signature hash added)
- TC-CQGA2-009-04: Verify V119 `validate_promoted_code_changed_without_reopening` registered in runner

**Micro-steps for TC-CQGA2-009-01:**
- MS-009-01-01: Read `registry/promotion-ledger.yaml` fully
- MS-009-01-02: List all entries and their current status field values
- MS-009-01-03: Count: entries at IMPLEMENTATION_VERIFIED; entries at PROMOTED_STABLE; entries at DRAFT
- MS-009-01-04: Compare to CQGA-001 baseline (5 entries, all IMPLEMENTATION_VERIFIED or DRAFT, none PROMOTED_STABLE)
- MS-009-01-05: Record: "promotion-ledger.yaml: N entries; PROMOTED_STABLE: [0 | X]; delta from CQGA-001: [none | +X promoted]"

**Micro-steps for TC-CQGA2-009-02:**
- MS-009-02-01: Read `tools/supervisor/autonomous_cycle.py` lines 1030-1075
- MS-009-02-02: Find the reopening trigger: logic that checks if promoted code hash changed
- MS-009-02-03: Confirm the hash comparison uses `api_baseline_hash` from promotion-ledger.yaml
- MS-009-02-04: Record: "Reopening trigger at lines [X-Y]: [CONFIRMED | MOVED to line Z | REMOVED]"

**Micro-steps for TC-CQGA2-009-03:**
- MS-009-03-01: Read `registry/promotion-ledger.yaml` — look at what fields are stored per entry
- MS-009-03-02: Confirm: is only `api_baseline_hash` (name-based) stored? Or has `api_baseline_signature` (content-based) been added?
- MS-009-03-03: Check if any commit in dc1d94d8..HEAD added signature hash support
- MS-009-03-04: Record: "CQG-006 hash type: [name_only=PARTIALLY_FIXED | content_signature=FIXED]"

**Micro-steps for TC-CQGA2-009-04:**
- MS-009-04-01: Search governance_validator_runner.py for `validate_promoted_code_changed_without_reopening` or `V119`
- MS-009-04-02: Confirm the registration entry exists with correct validator function reference
- MS-009-04-03: Note `blocks_sprint` value for V119
- MS-009-04-04: Record: "V119 registered: [yes | no]; blocks_sprint: [value]"

**Completion evidence:** promotion-ledger.yaml current state documented; reopening trigger confirmed at exact line numbers; CQG-006 hash type confirmed; V119 registration confirmed.

---

### TC-CQGA2-010: Identify Bypasses — Prove Each Root Cause
**Type:** PARENT | **Status:** READY (after TC-009) | **REQ:** REQ-CQGA2-009
**This is the synthesis task — produces the root cause proof bundle.**

**Children:**
- TC-CQGA2-010-01: Prove RCA-A: run `check_continuation.py` Check 8 logic manually; show only 2 of 4 GOV_BLOCK are checked
- TC-CQGA2-010-02: Prove RCA-B: show that governance_validators_ext3.py line 896 reads `changed_files` from declaration (not git)
- TC-CQGA2-010-03: Prove RCA-C: show `expected_count=167` test in test file; show it does not call any validator with bad input
- TC-CQGA2-010-04: Prove RCA-D: show V87 commit has no gap ledger entry
- TC-CQGA2-010-05: Prove RCA-E: check `.git/hooks/pre-commit` existence
- TC-CQGA2-010-06: Prove RCA-F: show V13/V47 pass-through when SAL absent (read their code)
- TC-CQGA2-010-07: Write `.local/evidences/CQGA-002/planning/root-cause-proof-bundle.yaml`

**Micro-steps for TC-CQGA2-010-01:**
- MS-010-01-01: Read `check_continuation.py` lines 507-545
- MS-010-01-02: List the exact strings in the hardcoded GOV_BLOCK set
- MS-010-01-03: Read CLAUDE.md §"GOV_BLOCK Exception"
- MS-010-01-04: Record discrepancy: CLAUDE.md=4 validators, code=2 validators
- MS-010-01-05: Write finding to root-cause-proof-bundle.yaml as RCA-A

**Micro-steps for TC-CQGA2-010-02 (Prove RCA-B):**
- MS-010-02-01: Read `tools/supervisor/governance_validators_ext3.py` lines 880-930
- MS-010-02-02: Find where `changed_files` is extracted — is it from `declaration["planned_work_items"]` or from git?
- MS-010-02-03: Record the exact line and expression: `changed_files = wi.get("changed_files", [])` (or similar)
- MS-010-02-04: Confirm: no git call, no `subprocess`, no `git diff` within validator file scope
- MS-010-02-05: Write finding to root-cause-proof-bundle.yaml as `rca_b: {file: ..., line: ..., code_excerpt: ...}`

**Micro-steps for TC-CQGA2-010-03 (Prove RCA-C):**
- MS-010-03-01: Find test file that asserts `expected_count == 167`: `grep -r "expected_count" tests/`
- MS-010-03-02: Read that test file's assertion — confirm it only checks the count, not validator behavior
- MS-010-03-03: Confirm: the test does NOT call any validator with a known-bad synthetic declaration
- MS-010-03-04: Record exact test file path and line: "count-only test at tests/supervisor/test_X.py:L_N"
- MS-010-03-05: Write finding to root-cause-proof-bundle.yaml as `rca_c: {test_file: ..., line: ..., assertion_type: count_only}`

**Micro-steps for TC-CQGA2-010-04 (Prove RCA-D):**
- MS-010-04-01: Read `reports/code-quality/code-quality-governance-ledger.yaml` fully (current state BEFORE TC-011 edits)
- MS-010-04-02: Search for any entry referencing commit `147b63fa` or validator `V87` or `validate_dotnet_constant_return_public_api`
- MS-010-04-03: Confirm: NO such entry exists in the ledger (gap confirms no governance record was created)
- MS-010-04-04: Record: "Gap ledger scan for 147b63fa/V87: ENTRY_NOT_FOUND — RCA-D confirmed"
- MS-010-04-05: Write finding to root-cause-proof-bundle.yaml as `rca_d: {commit: "147b63fa", ledger_entry: null, finding: "no_governance_record"}`

**Micro-steps for TC-CQGA2-010-05:**
- MS-010-05-01: Run `ls -la .git/hooks/` to see hook files
- MS-010-05-02: Check if `pre-commit` hook file exists (not `.pre-commit.sample`)
- MS-010-05-03: If absent: write finding "CQG-001 CONFIRMED OPEN"; if present: write "CQG-001 RESOLVED"

**Micro-steps for TC-CQGA2-010-06 (Prove RCA-F):**
- MS-010-06-01: Find `validate_spec_fact_refs_wired` (V13) source in governance_validators files
- MS-010-06-02: Read the function — find where it checks for SAL file existence
- MS-010-06-03: Find the conditional: `if not sal_path.exists(): return {..., "status": "PASS"}` (or similar vacuous pass)
- MS-010-06-04: Record exact line: "V13 vacuous pass at line X when SAL absent: [CONFIRMED | logic differs]"
- MS-010-06-05: Repeat for V47 (`validate_spec_fact_refs_in_sal_output`) — same early-return pattern
- MS-010-06-06: Write finding to root-cause-proof-bundle.yaml as `rca_f: {v13_line: X, v47_line: Y, finding: "vacuous_pass_when_sal_absent"}`

**Micro-steps for TC-CQGA2-010-07 (Write root-cause-proof-bundle.yaml):**
- MS-010-07-01: Create directory `.local/evidences/CQGA-002/planning/` if it doesn't exist
- MS-010-07-02: Write `.local/evidences/CQGA-002/planning/root-cause-proof-bundle.yaml` with all 7 RCA entries:
  ```yaml
  authoritative_plan: C:\Users\prora\.claude\plans\mutable-exploring-hellman.md
  artifact_role: evidence_only
  execution_authority: false
  rca_a: {file: check_continuation.py, lines: "519-520", finding: "2_of_4_govblock_checked"}
  rca_b: {file: governance_validators_ext3.py, line: N, finding: "changed_files_from_declaration_not_git"}
  rca_c: {test_file: tests/supervisor/test_X.py, line: N, finding: "count_only_not_functional"}
  rca_d: {commit: "147b63fa", ledger_entry: null, finding: "no_governance_record"}
  rca_e: {hooks_dir: .git/hooks/, finding: "pre_commit_absent_or_sample_only"}
  rca_f: {v13_line: N, v47_line: N, finding: "vacuous_pass_when_sal_absent"}
  rca_g: {absorbed_by: rca_b, finding: "no_git_diff_scan_at_closeout"}
  ```
- MS-010-07-03: Validate YAML: `python -c "import yaml; d=yaml.safe_load(open('.local/evidences/CQGA-002/planning/root-cause-proof-bundle.yaml')); assert all(k in d for k in ['rca_a','rca_b','rca_c','rca_d','rca_e','rca_f','rca_g']); print('OK')"`

**Completion evidence:** `root-cause-proof-bundle.yaml` with entries for RCA-A through RCA-G; YAML validation passes.
**Stop condition:** If any RCA cannot be proved with file+line evidence, record as UNPROVEN and note in finding — do not fabricate line numbers.

---

## PHASE B: GAP LEDGER TASKCARD (TC-CQGA2-011)

### TC-CQGA2-011: Update Gap Ledger
**Type:** PARENT | **Status:** READY (after TC-CQGA2-010) | **REQ:** REQ-CQGA2-008
**Prereqs:** TC-CQGA2-001 through TC-CQGA2-010 all CLOSED
**File lock:** `reports/code-quality/code-quality-governance-ledger.yaml`

**Objective:** Reconcile all 13 existing gaps + add 6 new gaps from RCA-A–G.

**Children:**

**TC-CQGA2-011-01: Re-assess 7 open gaps**
- MS-011-01-01: Read current gap ledger fully
- MS-011-01-02: For each of CQG-001, CQG-004, CQG-006, CQG-008, CQG-009, CQG-012, CQG-013: write new status based on Phase A findings
- MS-011-01-03: Update `date` and `updated_by: CQGA-002` header fields
- Acceptance: all 7 gaps have updated status that contradicts no Phase A evidence

**TC-CQGA2-011-02: Add 6 new gaps**

| Gap | RCA | Name | Status |
|---|---|---|---|
| CQG-014 | RCA-A | govblock_list_underspecified | OPEN → Repair 1 |
| CQG-015 | RCA-B/G | declaration_scope_bypass_by_omission | OPEN → Repair 2 |
| CQG-016 | RCA-C | validator_count_not_functional | OPEN → Repair 3 |
| CQG-017 | RCA-D | v87_demotion_without_governance_record | OPEN → Repair 5B |
| CQG-018 | RCA-F | sal_absence_silent_vacuous_pass | OPEN → Repair 5A |
| CQG-019 | RCA-E | precommit_absence_not_detected | OPEN_WITH_PARTIAL_MITIGATION → Repair 4 |

- MS-011-02-01: Add CQG-014 entry with full fields (gap_id, name, status, root_cause, remediation, task_ids)
- MS-011-02-02: Add CQG-015 entry
- MS-011-02-03: Add CQG-016 entry
- MS-011-02-04: Add CQG-017 entry (include V87 evidence from TC-CQGA2-002-02)
- MS-011-02-05: Add CQG-018 entry
- MS-011-02-06: Add CQG-019 entry
- MS-011-02-07: Update `total_gaps: 13 → 19` in ledger header

**TC-CQGA2-011-03: Validate updated ledger**
- MS-011-03-01: `python -c "import yaml; d=yaml.safe_load(open('reports/code-quality/code-quality-governance-ledger.yaml')); assert d['total_gaps'] == 19, f'Expected 19, got {d[\"total_gaps\"]}'; print('OK')"
- MS-011-03-02: Verify each new gap has: gap_id, name, status, root_cause, remediation, task_ids fields present

**Completion evidence:** Validated gap ledger with 19 entries; TC-CQGA2-011-03 passes.
**Allowed files:** `reports/code-quality/code-quality-governance-ledger.yaml` only
**Forbidden:** Do not modify any other report files

---

## PHASE C: REPAIR TASKCARDS (TC-CQGA2-012 through TC-CQGA2-017)
**All require TC-CQGA2-011 CLOSED before starting.**

---

### TC-CQGA2-012 (PARENT): Repair 1 — GOV_BLOCK Registry
**Type:** PARENT | **Status:** READY (after TC-011) | **REQ:** REQ-CQGA2-001, REQ-CQGA2-004
**Successor:** TC-CQGA2-014 (functional tests need the registry)

**Objective:** Create `governance_block_registry.py`; wire it into `check_continuation.py`;
update CLAUDE.md to match code; create enforcement level change policy.

**Scope:**
```
Allowed files:
  - tools/supervisor/governance_block_registry.py  (NEW)
  - tools/supervisor/check_continuation.py          (MODIFY lines 519-520 area)
  - CLAUDE.md                                       (MODIFY §GOV_BLOCK Exception)
  - docs/code-quality/enforcement-level-change-policy.md  (NEW)
  - tests/supervisor/test_governance_block_registry.py   (NEW)

Forbidden files:
  - Any governance_validators*.py files
  - Any product source files (src/python/, src/net/)
  - reports/code-quality/code-quality-governance-ledger.yaml (TC-011 already closed this)
```

**Preserved behavior:** The 2 existing GOV_BLOCK types (`monolith_detection_validator`,
`validate_source_architecture`) must continue to work exactly as before. Only the mechanism
changes (registry import vs hardcoded list). No functional change to existing blocking logic.

---

#### TC-CQGA2-012-01: Read check_continuation.py GOV_BLOCK section
**Type:** CHILD | **Status:** TODO | **Parent:** TC-CQGA2-012

**Micro-steps:**
- MS-012-01-01: Read `tools/supervisor/check_continuation.py` lines 505-545 fully
  - Target: GOV_BLOCK check section
  - Expected output: understand import structure, local variable names, exact set used
- MS-012-01-02: Record the exact Python code around lines 519-520 (the hardcoded set)
  - Expected output: excerpt showing `{"GOV_BLOCK:monolith_detection_validator", "GOV_BLOCK:validate_source_architecture"}`
- MS-012-01-03: Check if `check_continuation.py` has any other GOV_BLOCK references (grep)
  - Command: search for "GOV_BLOCK" in the file
  - Expected output: count of all occurrences

**Acceptance checks:**
- [ ] Lines 519-520 contain exactly the 2-item hardcoded set
- [ ] No other GOV_BLOCK sets exist in the file that need updating

**Evidence:** Screenshot/excerpt of lines 505-545

---

#### TC-CQGA2-012-02: Create governance_block_registry.py
**Type:** CHILD | **Status:** TODO | **Parent:** TC-CQGA2-012
**Prereq:** TC-CQGA2-012-01 CLOSED

**Micro-steps:**
- MS-012-02-01: Create `tools/supervisor/governance_block_registry.py` with:
  ```python
  """
  governance_block_registry.py — Registry of GOV_BLOCK hard-stop conditions.

  MAINTENANCE RULE (ELP-001): Any removal from or demotion within STRUCTURAL_GOV_BLOCKS
  requires a gap entry in reports/code-quality/code-quality-governance-ledger.yaml with
  status ACKNOWLEDGED_BY_DESIGN before the change is made.

  See docs/code-quality/enforcement-level-change-policy.md for full policy.
  """
  from typing import Final

  STRUCTURAL_GOV_BLOCKS: Final[frozenset[str]] = frozenset({
      # Original 2 — wired since TC-GOVBLK-001
      "GOV_BLOCK:monolith_detection_validator",
      "GOV_BLOCK:validate_source_architecture",
      # Fixed: previously in CLAUDE.md but not in code
      "GOV_BLOCK:validate_multi_responsibility_file",
      "GOV_BLOCK:validate_analytics_naming_enforced",
      # New: code quality hard-stops (new-files-only scope enforced by validators)
      "GOV_BLOCK:validate_suspicious_filenames",               # V100
      "GOV_BLOCK:validate_undocumented_public_python_apis",    # V102
      "GOV_BLOCK:validate_constant_return_public_methods",     # V104
      "GOV_BLOCK:validate_source_stubs",                       # V149
  })

  # Scope annotations: validators marked new_files_only fire only on NEW files
  SCOPE_ANNOTATIONS: Final[dict[str, str]] = {
      "GOV_BLOCK:validate_undocumented_public_python_apis": "new_files_only",
      "GOV_BLOCK:validate_constant_return_public_methods": "new_files_only",
  }

  ENFORCEMENT_LEVEL_CHANGE_POLICY_PATH = "docs/code-quality/enforcement-level-change-policy.md"
  ```
- MS-012-02-02: Verify file syntax: `python -c "from tools.supervisor.governance_block_registry import STRUCTURAL_GOV_BLOCKS; print(len(STRUCTURAL_GOV_BLOCKS))"`
  - Expected output: `8`
- MS-012-02-03: Verify `frozenset` type: `python -c "from tools.supervisor.governance_block_registry import STRUCTURAL_GOV_BLOCKS; assert isinstance(STRUCTURAL_GOV_BLOCKS, frozenset)"`

**Acceptance checks:**
- [ ] File imports cleanly with no errors
- [ ] `len(STRUCTURAL_GOV_BLOCKS) == 8`
- [ ] All 4 CLAUDE.md validators present
- [ ] All 4 new validators present
- [ ] `SCOPE_ANNOTATIONS` keys are a subset of `STRUCTURAL_GOV_BLOCKS`

---

#### TC-CQGA2-012-03: Wire registry into check_continuation.py
**Type:** CHILD | **Status:** TODO | **Parent:** TC-CQGA2-012
**Prereq:** TC-CQGA2-012-02 CLOSED
**File lock:** `tools/supervisor/check_continuation.py`

**Micro-steps:**
- MS-012-03-01: Read `check_continuation.py` fully (required before edit)
- MS-012-03-02: Add import at top of file (after existing imports):
  ```python
  from governance_block_registry import STRUCTURAL_GOV_BLOCKS as _STRUCTURAL_GOV_BLOCKS
  ```
- MS-012-03-03: Replace the hardcoded set near lines 519-520:
  ```python
  # BEFORE:
  # structural_block_types = {
  #     "GOV_BLOCK:monolith_detection_validator",
  #     "GOV_BLOCK:validate_source_architecture",
  # }
  # AFTER:
  structural_block_types = _STRUCTURAL_GOV_BLOCKS
  ```
- MS-012-03-04: Run `python -c "from tools.supervisor import check_continuation"` — confirm no import errors
- MS-012-03-05: Run existing check_continuation tests: `python -m pytest tests/supervisor/test_check_continuation*.py -v` — confirm all pass

**Acceptance checks:**
- [ ] `check_continuation.py` imports from registry (no hardcoded set)
- [ ] Existing tests all pass (no regression)
- [ ] Import adds `STRUCTURAL_GOV_BLOCKS` from the correct module path

**Rollback:** If tests fail, revert to hardcoded set and record failure as rework item.

---

#### TC-CQGA2-012-04: Update CLAUDE.md GOV_BLOCK section
**Type:** CHILD | **Status:** TODO | **Parent:** TC-CQGA2-012
**Prereq:** TC-CQGA2-012-02 CLOSED (registry is authoritative; CLAUDE.md must match it)

**Micro-steps:**
- MS-012-04-01: Read CLAUDE.md §"GOV_BLOCK Exception" section
- MS-012-04-02: Edit the validator list in CLAUDE.md to match `STRUCTURAL_GOV_BLOCKS` (8 entries)
- MS-012-04-03: Add a note: "Canonical list is `tools/supervisor/governance_block_registry.py::STRUCTURAL_GOV_BLOCKS`. Update that file; CLAUDE.md must match."
- MS-012-04-04: Verify CLAUDE.md does not reference the old hardcoded set anywhere

**Acceptance checks:**
- [ ] CLAUDE.md GOV_BLOCK list has exactly 8 entries matching the registry
- [ ] Registry reference note added to CLAUDE.md

---

#### TC-CQGA2-012-05: Create test_governance_block_registry.py
**Type:** CHILD | **Status:** TODO | **Parent:** TC-CQGA2-012
**Prereq:** TC-CQGA2-012-02 CLOSED

**Micro-steps:**
- MS-012-05-01: Create `tests/supervisor/test_governance_block_registry.py`:
  ```python
  """Tests for governance_block_registry.py — registry completeness and consistency."""
  import re
  from pathlib import Path
  from tools.supervisor.governance_block_registry import STRUCTURAL_GOV_BLOCKS, SCOPE_ANNOTATIONS

  def test_registry_contains_all_claude_md_validators():
      """All validators named in CLAUDE.md GOV_BLOCK section must be in the registry."""
      required = {
          "GOV_BLOCK:monolith_detection_validator",
          "GOV_BLOCK:validate_source_architecture",
          "GOV_BLOCK:validate_multi_responsibility_file",
          "GOV_BLOCK:validate_analytics_naming_enforced",
      }
      assert required <= STRUCTURAL_GOV_BLOCKS

  def test_registry_is_frozen():
      assert isinstance(STRUCTURAL_GOV_BLOCKS, frozenset)

  def test_scope_annotations_are_subset_of_registry():
      assert set(SCOPE_ANNOTATIONS.keys()) <= STRUCTURAL_GOV_BLOCKS

  def test_check_continuation_imports_from_registry():
      """check_continuation.py must import STRUCTURAL_GOV_BLOCKS from registry."""
      cc_path = Path("tools/supervisor/check_continuation.py")
      content = cc_path.read_text()
      assert "governance_block_registry" in content, (
          "check_continuation.py must import from governance_block_registry"
      )
      assert "STRUCTURAL_GOV_BLOCKS" in content

  def test_claude_md_lists_all_registry_entries():
      """CLAUDE.md GOV_BLOCK list must match registry (no stale/missing entries)."""
      claude = Path("CLAUDE.md").read_text()
      for block in STRUCTURAL_GOV_BLOCKS:
          validator_name = block.replace("GOV_BLOCK:", "")
          assert validator_name in claude, (
              f"CLAUDE.md missing registry entry: {block}"
          )
  ```
- MS-012-05-02: Run test: `.venv/Scripts/pytest tests/supervisor/test_governance_block_registry.py -v`
- MS-012-05-03: All 5 tests must pass; if not, fix the registry/CLAUDE.md before closing

**Acceptance checks:**
- [ ] All 5 tests PASS
- [ ] Test file imports cleanly

---

#### TC-CQGA2-012 Parent Integration Check
After all children CLOSED:
1. Run full TC-CQGA2-012-05 test suite → all pass
2. Run existing check_continuation tests → all pass
3. Confirm registry has 8 entries; CLAUDE.md matches
4. Write `CQG-014: CLOSED_PARTIALLY` in gap ledger (GOV_BLOCK list fixed; full Supreme Directive policy still requires human decision)

**Quality scoring (each dimension must be ≥4):**
- Requirement correctness: Does this address REQ-CQGA2-001? (registry matches CLAUDE.md)
- Implementation correctness: Does `check_continuation.py` use registry?
- Scope discipline: No product source files touched
- Validation strength: 5 tests covering registry completeness and CLAUDE.md sync
- Evidence completeness: test output + diff + registry file
- Regression safety: Existing check_continuation tests still pass

---

### TC-CQGA2-013 (PARENT): Repair 2 — Declaration Integrity Check
**Type:** PARENT | **Status:** READY (after TC-011) | **REQ:** REQ-CQGA2-002, REQ-CQGA2-007
**Successor:** TC-CQGA2-028 (Pilot 11 tests this)

**Objective:** Create `declaration_integrity_check.py`; wire into `autonomous_cycle.py` Step 0a.

**Scope:**
```
Allowed files:
  - tools/supervisor/declaration_integrity_check.py  (NEW)
  - tools/supervisor/autonomous_cycle.py             (MODIFY — add Step 0a call)
  - tests/supervisor/test_declaration_integrity.py   (NEW)
Forbidden:
  - Any governance_validators*.py (integrity check is separate)
  - Any product source (src/python/, src/net/)
```

---

#### TC-CQGA2-013-01: Read autonomous_cycle.py declaration-parse section
**Type:** CHILD | **Status:** TODO | **Parent:** TC-CQGA2-013

**Micro-steps:**
- MS-013-01-01: Read `autonomous_cycle.py` lines 1-100 (imports, module-level)
- MS-013-01-02: Search for where `declaration` dict is first populated from YAML
- MS-013-01-03: Identify the exact line AFTER which Step 0a should be inserted
- MS-013-01-04: Record the exact function name, variable names, and return path for wiring

**Acceptance:** Line number confirmed; function signature known; no ambiguity about insertion point.

---

#### TC-CQGA2-013-02: Create declaration_integrity_check.py
**Type:** CHILD | **Status:** TODO | **Parent:** TC-CQGA2-013
**Prereq:** TC-CQGA2-013-01

**Micro-steps:**
- MS-013-02-01: Create `tools/supervisor/declaration_integrity_check.py` with:
  ```python
  """declaration_integrity_check.py — Cross-check declared changed_files against git diff.

  Rationale (CQG-015/019): Validators fire only on declared changed_files. An incomplete
  declaration allows quality violations to bypass all enforcement. This tool detects
  undeclared source changes and adds GOV_BLOCK:undeclared_source_change to rework_items.
  """
  from __future__ import annotations
  import subprocess
  from pathlib import Path
  from typing import TYPE_CHECKING

  QUALITY_PREFIXES = ("src/python/", "src/net/")

  def _get_git_changed_files(repo_root: Path) -> list[str] | None:
      """Return list of changed files (HEAD~1..HEAD) or None if git fails."""
      try:
          result = subprocess.run(
              ["git", "diff", "HEAD~1..HEAD", "--diff-filter=ACMR", "--name-only"],
              capture_output=True, text=True, cwd=str(repo_root), timeout=10
          )
          if result.returncode != 0:
              return None
          return [line.strip() for line in result.stdout.splitlines() if line.strip()]
      except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
          return None

  def _extract_declared_files(declaration: dict) -> set[str]:
      declared: set[str] = set()
      for wi in declaration.get("planned_work_items", []):
          for f in wi.get("changed_files", []):
              declared.add(str(f))
      return declared

  def check_declaration_integrity(declaration: dict, repo_root: Path) -> dict:
      """Compare declared changed_files vs git diff HEAD~1..HEAD.

      Returns:
        undeclared_changes: files in git diff but not in declaration
        declared_not_in_git: files in declaration but not in git diff (informational)
        quality_path_violations: subset of undeclared_changes matching src/python/ or src/net/
        blocks_sprint: True when quality_path_violations is non-empty
        skip_reason: non-empty string when check was skipped
      """
      git_files = _get_git_changed_files(repo_root)
      if git_files is None:
          return {
              "undeclared_changes": [], "declared_not_in_git": [],
              "quality_path_violations": [], "blocks_sprint": False,
              "skip_reason": "git diff unavailable or first commit",
          }

      declared = _extract_declared_files(declaration)
      git_set = set(git_files)

      undeclared = sorted(git_set - declared)
      declared_not_in_git = sorted(declared - git_set)
      quality_violations = [
          f for f in undeclared
          if any(f.startswith(p) for p in QUALITY_PREFIXES)
      ]

      return {
          "undeclared_changes": undeclared,
          "declared_not_in_git": declared_not_in_git,
          "quality_path_violations": quality_violations,
          "blocks_sprint": bool(quality_violations),
          "skip_reason": "",
      }
  ```
- MS-013-02-02: Syntax check: `python -c "from tools.supervisor.declaration_integrity_check import check_declaration_integrity; print('OK')"`
- MS-013-02-03: Smoke test: call `check_declaration_integrity({}, Path('.'))` — should return dict with all keys; blocks_sprint=False

**Acceptance checks:**
- [ ] Module imports cleanly
- [ ] Returns dict with 5 required keys on empty input
- [ ] `blocks_sprint` is False on empty declaration with no git changes

---

#### TC-CQGA2-013-03: Wire into autonomous_cycle.py as Step 0a
**Type:** CHILD | **Status:** TODO | **Parent:** TC-CQGA2-013
**Prereq:** TC-CQGA2-013-01 CLOSED, TC-CQGA2-013-02 CLOSED
**File lock:** `tools/supervisor/autonomous_cycle.py`

**Micro-steps:**
- MS-013-03-01: Read `autonomous_cycle.py` fully (required before edit)
- MS-013-03-02: Add import: `from declaration_integrity_check import check_declaration_integrity`
- MS-013-03-03: Insert Step 0a code immediately after declaration dict is parsed:
  ```python
  # Step 0a: Declaration integrity check (CQG-015/019 — REQ-CQGA2-002)
  _integrity = check_declaration_integrity(declaration, REPO_ROOT)
  if _integrity.get("skip_reason"):
      print(f"  [INTEGRITY] Skipped: {_integrity['skip_reason']}")
  elif _integrity["blocks_sprint"]:
      _integrity_rework = {
          "type": "GOV_BLOCK:undeclared_source_change",
          "message": (
              f"Quality-sensitive files changed in git but not declared: "
              f"{_integrity['quality_path_violations']}. "
              "Add these files to changed_files in declaration before re-running."
          ),
      }
      review.setdefault("rework_items", []).append(_integrity_rework)
      print(f"  [INTEGRITY] GOV_BLOCK: {len(_integrity['quality_path_violations'])} undeclared source file(s)")
  elif _integrity["undeclared_changes"]:
      print(f"  [INTEGRITY] WARN: {len(_integrity['undeclared_changes'])} non-source undeclared change(s)")
  ```
- MS-013-03-04: Run existing autonomous_cycle tests: `python -m pytest tests/supervisor/ -k "autonomous" -v`
- MS-013-03-05: Confirm no test failures

**Acceptance checks:**
- [ ] Step 0a code inserted at correct location
- [ ] Import added without breaking other imports
- [ ] Existing autonomous_cycle tests all pass

**Rollback:** If tests fail, remove Step 0a code block and record failure.

---

#### TC-CQGA2-013-04: Create test_declaration_integrity.py
**Type:** CHILD | **Status:** TODO | **Parent:** TC-CQGA2-013
**Prereq:** TC-CQGA2-013-02 CLOSED

**Micro-steps:**
- MS-013-04-01: Create `tests/supervisor/test_declaration_integrity.py`:
  ```python
  """Tests for declaration_integrity_check.py."""
  import pytest
  from pathlib import Path
  from unittest.mock import patch
  from tools.supervisor.declaration_integrity_check import check_declaration_integrity

  REPO_ROOT = Path(__file__).resolve().parent.parent.parent

  def make_declaration(changed_files: list[str]) -> dict:
      return {"planned_work_items": [{"item_id": "TEST-001", "changed_files": changed_files}]}

  def test_empty_declaration_no_blocks():
      result = check_declaration_integrity({}, REPO_ROOT)
      assert result["blocks_sprint"] is False

  def test_git_unavailable_returns_skip():
      with patch("tools.supervisor.declaration_integrity_check._get_git_changed_files", return_value=None):
          result = check_declaration_integrity({}, REPO_ROOT)
          assert result["skip_reason"] != ""
          assert result["blocks_sprint"] is False

  def test_source_undeclared_blocks():
      mock_git = ["src/python/csv/csv_parser.py"]
      with patch("tools.supervisor.declaration_integrity_check._get_git_changed_files", return_value=mock_git):
          result = check_declaration_integrity(make_declaration([]), REPO_ROOT)
          assert result["blocks_sprint"] is True
          assert "src/python/csv/csv_parser.py" in result["quality_path_violations"]

  def test_non_source_undeclared_does_not_block():
      mock_git = ["docs/README.md"]
      with patch("tools.supervisor.declaration_integrity_check._get_git_changed_files", return_value=mock_git):
          result = check_declaration_integrity(make_declaration([]), REPO_ROOT)
          assert result["blocks_sprint"] is False
          assert "docs/README.md" in result["undeclared_changes"]

  def test_declared_file_not_in_git_is_informational():
      mock_git = []
      with patch("tools.supervisor.declaration_integrity_check._get_git_changed_files", return_value=mock_git):
          result = check_declaration_integrity(make_declaration(["src/python/csv/csv_parser.py"]), REPO_ROOT)
          assert result["blocks_sprint"] is False
          assert "src/python/csv/csv_parser.py" in result["declared_not_in_git"]

  def test_fully_declared_source_does_not_block():
      mock_git = ["src/python/csv/csv_parser.py"]
      with patch("tools.supervisor.declaration_integrity_check._get_git_changed_files", return_value=mock_git):
          result = check_declaration_integrity(make_declaration(["src/python/csv/csv_parser.py"]), REPO_ROOT)
          assert result["blocks_sprint"] is False
          assert result["quality_path_violations"] == []
  ```
- MS-013-04-02: Run: `.venv/Scripts/pytest tests/supervisor/test_declaration_integrity.py -v`
- MS-013-04-03: All 6 tests must PASS

**Acceptance checks:**
- [ ] All 6 tests PASS
- [ ] Tests use mock for git calls (no real git I/O in unit tests)

---

#### TC-CQGA2-013 Parent Integration Check
After all children CLOSED:
1. Run `pytest tests/supervisor/test_declaration_integrity.py -v` → all PASS
2. Run `pytest tests/supervisor/ -k "autonomous" -v` → all PASS
3. Manually verify Step 0a is present in `autonomous_cycle.py`
4. Update CQG-015 and CQG-019 in gap ledger: status → OPEN_WITH_PARTIAL_MITIGATION

---

### TC-CQGA2-014 (PARENT): Repair 3 — Validator Functional Tests
**Type:** PARENT | **Status:** READY (after TC-012 closes — registry needed) | **REQ:** REQ-CQGA2-003
**Prereq:** TC-CQGA2-012 CLOSED

**Objective:** Create `tests/governance/test_validators_functional.py` covering 10 P0 validators.

**Scope:**
```
Allowed files:
  - tests/governance/test_validators_functional.py  (NEW)
  - tests/governance/__init__.py                    (NEW if directory doesn't exist)
Forbidden:
  - governance_validators*.py (do not change validators themselves)
  - Any source files outside tests/governance/
```

---

#### TC-CQGA2-014-01: Inspect governance test directory
- MS-014-01-01: Check if `tests/governance/` exists; if not, create directory + `__init__.py`
- MS-014-01-02: List existing test files in `tests/governance/` — avoid duplication
- MS-014-01-03: Read import paths needed for each of the 10 P0 validators (confirm callable)

#### TC-CQGA2-014-02: Build make_minimal_declaration helper and 5 P0 tests (V100, V102, V104, V109, V149)
**Prereq:** TC-CQGA2-014-01

**Micro-steps:**
- MS-014-02-01: Determine correct import path for each validator:
  - V100: `from tools.supervisor.governance_validators_ext3 import validate_suspicious_filenames`
  - V102: `from tools.supervisor.governance_validators_ext3 import validate_undocumented_public_python_apis`
  - V104: `from tools.supervisor.governance_validators_ext3 import validate_constant_return_public_methods`
  - V109: `from tools.supervisor.governance_validators_ext3 import validate_files_outside_approved_layout`
  - V149: `from tools.supervisor.governance_validators_ext3 import validate_source_stubs` (or governance_validators_ext4)
  - Confirm each import at Python level before writing test
- MS-014-02-02: Write `make_minimal_declaration` helper function
- MS-014-02-03: Write parametrized test for V100 (known-bad: `src/python/csv/csv_misc.py`)
- MS-014-02-04: Write parametrized test for V102 (known-bad: new file with undocumented public def)
- MS-014-02-05: Write parametrized test for V104 (known-bad: new file with `return None` always)
- MS-014-02-06: Write parametrized test for V109 (known-bad: fods file not in approved_layout)
- MS-014-02-07: Write parametrized test for V149 (known-bad: file with bare `pass` method body)
- MS-014-02-08: Run these 5 tests: `.venv/Scripts/pytest tests/governance/test_validators_functional.py -v -k "V100 or V102 or V104 or V109 or V149"`

#### TC-CQGA2-014-03: Add 5 remaining P0 tests (V105, V106, 3 GOV_BLOCK)
**Prereq:** TC-CQGA2-014-02 CLOSED

**Micro-steps:**
- MS-014-03-01: Determine import paths for V105, V106, and the 3 GOV_BLOCK validators
- MS-014-03-02: Write V105 test (known-bad: .NET getter without XML read)
- MS-014-03-03: Write V106 test (known-bad: .NET setter without XML write)
- MS-014-03-04: Write GOV_BLOCK:monolith_detection_validator test (known-bad: 900-LOC file declaration)
- MS-014-03-05: Write GOV_BLOCK:validate_source_architecture test
- MS-014-03-06: Write GOV_BLOCK:validate_multi_responsibility_file test
- MS-014-03-07: Run all 10 tests: `.venv/Scripts/pytest tests/governance/test_validators_functional.py -v`
- MS-014-03-08: All 10 must PASS

**Acceptance checks for TC-CQGA2-014:**
- [ ] 10 P0 tests exist and all PASS
- [ ] Each test asserts `status`, `blocks_sprint`, and violation content
- [ ] Tests run in <15s total
- [ ] No real disk I/O beyond reading REPO_ROOT for path resolution

---

### TC-CQGA2-015 (PARENT): Repair 4 — Pre-commit Installation Verification
**Type:** PARENT | **Status:** READY (after TC-011) | **REQ:** REQ-CQGA2-005

**Scope:**
```
Allowed files:
  - tools/supervisor/autonomous_cycle.py  (MODIFY — add pre-flight check)
  - AGENTS.md                             (MODIFY — add §A-precommit)
Forbidden:
  - .git/hooks/ (do not auto-install hooks)
  - .pre-commit-config.yaml (do not modify hook definitions)
```

#### TC-CQGA2-015-01: Add _check_precommit_installed to autonomous_cycle.py
**Prereq:** TC-CQGA2-013-03 CLOSED (TC-013 has already edited autonomous_cycle.py; sequential)

**Micro-steps:**
- MS-015-01-01: Read `autonomous_cycle.py` current state (after TC-013 edits)
- MS-015-01-02: Add helper function:
  ```python
  def _check_precommit_installed(repo_root: Path) -> bool:
      """Return True if pre-commit hooks are installed (not just sample files)."""
      hook = repo_root / ".git" / "hooks" / "pre-commit"
      return hook.exists() and not str(hook).endswith(".sample")
  ```
- MS-015-01-03: Add call in pre-flight section (before Step 0a):
  ```python
  # Pre-flight: pre-commit installation check (CQG-019 — REQ-CQGA2-005)
  if not _check_precommit_installed(REPO_ROOT):
      print("  [PRE-COMMIT] WARN: pre-commit hooks not installed. "
            "Run 'pre-commit install' to activate local quality gates. "
            "CQG-019: local commit hooks are currently INERT.")
  ```
- MS-015-01-04: Run existing tests: `python -m pytest tests/supervisor/ -k "autonomous" -v`

#### TC-CQGA2-015-02: Update AGENTS.md §A-precommit
- MS-015-02-01: Read AGENTS.md §A (first 50 lines)
- MS-015-02-02: Add new §A2c subsection (after A2b):
  ```markdown
  ## A2c. Pre-commit Hook Verification (mandatory before source modification)

  Before modifying any file in `src/python/` or `src/net/`, verify pre-commit hooks are installed:
  1. Check `.git/hooks/pre-commit` exists and is not a `.sample` file.
  2. If absent: run `pre-commit install` (idempotent, safe to run multiple times).
  3. Log the result (INSTALLED or WARN: ABSENT).
  This check is advisory — do NOT block a sprint when hooks are absent.
  The autonomous_cycle.py pre-flight also detects and warns (CQG-019).
  ```
- MS-015-02-03: Confirm no existing §A2c or similar conflicts

**Completion evidence:** `autonomous_cycle.py` has `_check_precommit_installed` + warning; AGENTS.md has §A2c.

---

### TC-CQGA2-016 (PARENT): Repair 5A — SAL Population Gate
**Type:** PARENT | **Status:** READY (after TC-011) | **REQ:** REQ-CQGA2-006
**File lock:** `tools/supervisor/sprint_executor_validate.py`

**Objective:** Add Phase 14 to `sprint_executor_validate.py` — warn when SAL absent on PRODUCT_SOURCE declarations.

#### TC-CQGA2-016-01: Inspect sprint_executor_validate.py phase structure
- MS-016-01-01: Read `sprint_executor_validate.py` fully (required before edit)
- MS-016-01-02: Find the existing 13-phase structure and the last phase call
- MS-016-01-03: Identify the exact insertion point for Phase 14
- MS-016-01-04: Record the function signature pattern used by other phases

#### TC-CQGA2-016-02: Add Phase 14 function
**Prereq:** TC-CQGA2-016-01

- MS-016-02-01: Add `_phase14_sal_population_gate` function:
  ```python
  def _phase14_sal_population_gate(declaration: dict, repo_root: Path) -> list[str]:
      """Phase 14: Warn when PRODUCT_SOURCE items declared but SAL absent.

      Without sal-facts-latest.json, V13 and V47 (spec_fact_refs) pass vacuously.
      The spec→stub traceability chain is unenforced. This phase makes the gap visible.

      Severity: WARN only (GOV_BLOCK would halt all product work for SAL-less formats).
      See CQG-008, CQG-018.
      """
      product_items = [
          wi for wi in declaration.get("planned_work_items", [])
          if wi.get("item_type") in ("PRODUCT_SOURCE", "PRODUCT_TEST")
      ]
      if not product_items:
          return []
      sal_path = repo_root / ".local" / "supervisor" / "sal-facts-latest.json"
      if not sal_path.exists():
          return [
              "WARN[SAL-GATE]: sal-facts-latest.json absent. "
              f"{len(product_items)} PRODUCT_SOURCE/TEST item(s) declared. "
              "V13/V47 (spec_fact_refs) will pass vacuously this sprint. "
              "spec→stub traceability is UNENFORCED. Run /ingest-spec-sal to populate SAL."
          ]
      return []
  ```
- MS-016-02-02: Update the phase count comment in file (13 → 14 phases)
- MS-016-02-03: Wire Phase 14 into the phase-execution loop
- MS-016-02-04: Run: `.venv/Scripts/pytest tests/supervisor/ -k "validate" -v` — confirm no regressions

**Acceptance checks:**
- [ ] `_phase14_sal_population_gate` exists and is wired into the validation loop
- [ ] Phase count comment updated to 14
- [ ] Existing sprint_executor_validate tests all pass

---

### TC-CQGA2-017 (PARENT): Repair 5B — Enforcement Level Change Policy
**Type:** PARENT | **Status:** READY (after TC-011) | **REQ:** REQ-CQGA2-004
**Prereqs:** TC-CQGA2-011 CLOSED (gap ledger ready for CQG-017)
**File lock (sequential):** gap ledger (after TC-011); then enforcement-level-change-policy.md (new file)

#### TC-CQGA2-017-01: Resolve V87 discrepancy (from TC-CQGA2-002-02 findings)
- MS-017-01-01: Read TC-CQGA2-002-02 evidence (root-cause-proof-bundle.yaml `v87_discrepancy_resolution`)
- MS-017-01-02: Write the definitive factual statement about V87: what it covers now, what it covered before, and whether the commit message was wrong

#### TC-CQGA2-017-02: Create enforcement-level-change-policy.md
- MS-017-02-01: Create `docs/code-quality/enforcement-level-change-policy.md` (~60 lines):
  ```markdown
  # Enforcement Level Change Policy

  **Authority:** CQGA-002 | **REQ:** REQ-CQGA2-004 | **Date:** 2026-07-10

  ## Rule ELP-001: Demotion requires gap entry BEFORE the change

  Any change that reduces a validator's enforcement level — `blocks_sprint=True → False`,
  FAIL → WARN, or removal from `STRUCTURAL_GOV_BLOCKS` — MUST be preceded by a gap entry
  in `reports/code-quality/code-quality-governance-ledger.yaml` with:
  - `status: ACKNOWLEDGED_BY_DESIGN`
  - `policy_rationale:` (why this is acceptable)
  - `demotion_date:` (planned date of change)
  - `review_date:` (when this decision should be re-evaluated, ≤6 months)
  - `responsible_authority:` (who approved the decision)

  ## Rule ELP-002: CI-pressure demotions are prohibited

  A validator MUST NOT be demoted because CI tests are failing. If a validator produces CI
  failures, the correct action is to fix the code or the test scope — not the enforcement level.

  Exception: if the validator has a provable false-positive rate >20% on the intended target
  population, document and apply a narrow scope limit (e.g., new-files-only) rather than
  removing the check entirely.

  ## Historical Violations

  | Validator | Demotion commit | Policy compliance |
  |---|---|---|
  | V87 validate_dotnet_constant_return_public_api | 147b63fa | NON-COMPLIANT — no gap entry |

  ## Enforcement

  V-ELP-001 (new validator) checks recent git history for `blocks_sprint` changes without
  corresponding gap ledger entries. Fires at sprint closeout as WARN.
  ```
- MS-017-02-02: Verify file is syntactically valid markdown

#### TC-CQGA2-017-03: Add CQG-017 gap entry for V87 demotion
**Prereq:** TC-CQGA2-011 CLOSED, TC-CQGA2-017-01 CLOSED
- MS-017-03-01: Add CQG-017 to `reports/code-quality/code-quality-governance-ledger.yaml`:
  ```yaml
  - gap_id: CQG-017
    name: v87_demotion_without_governance_record
    status: OPEN_WITH_PARTIAL_MITIGATION
    severity: MEDIUM
    root_cause: RCA-D
    summary: >
      V87 (validate_dotnet_constant_return_public_api) was demoted from FAIL to WARN in
      commit 147b63fa with no gap entry, no policy rationale, and no ACKNOWLEDGED_BY_DESIGN
      record. The commit message said "readme freshness" but the code is constant-return
      detection. Demotion reason is partially documented here retroactively.
    control_type: DOCUMENTATION
    control_gap: Policy (ELP-001) now exists; historical violation documented
    first_failed_boundary: ENFORCEMENT_LEVEL_CHANGE
    detection: V-ELP-001 (future validator)
    remediation: docs/code-quality/enforcement-level-change-policy.md created (ELP-001/ELP-002)
    task_ids: [TC-CQGA2-017]
  ```
- MS-017-03-02: Update total_gaps in ledger header: 19 → 20 (was 19 after TC-011; CQG-017 is new here)
  Wait — TC-CQGA2-011 already accounts for CQG-017 in the 6 new gaps. So total stays 19 after TC-011-02 which adds CQG-014 through CQG-019.

**CORRECTION:** TC-CQGA2-011 already adds CQG-017. TC-CQGA2-017-03 should ONLY update the status of CQG-017 (from OPEN to OPEN_WITH_PARTIAL_MITIGATION after the policy is written), not add it again.

- MS-017-03-02 (corrected): Find CQG-017 entry in ledger (added by TC-011); update `status: OPEN → OPEN_WITH_PARTIAL_MITIGATION`; add `remediation: enforcement-level-change-policy.md created`

**Completion evidence:** `enforcement-level-change-policy.md` exists; CQG-017 status updated; V87 discrepancy resolved.

---

## PHASE D: PILOT TASKCARDS (TC-CQGA2-018 through TC-CQGA2-031)
**All require Phase C CLOSED before starting.**

Each pilot follows: SETUP → EXECUTE TEST → ASSERT → CLEANUP → RECORD EVIDENCE.

Every pilot taskcard has these required fields:
```
method: LIVE_TEST | LIVE_VERIFICATION | DOCUMENTED
cleanup_required: yes | no
evidence_artifact: .local/evidences/CQGA-002/pilots/PILOT-N-result.yaml
verdict_options: PILOT_PASS | PILOT_PASS_WITH_SCOPE_LIMITATION | PILOT_FAIL
```

### TC-CQGA2-018 (PILOT-1): New code creation through official skill
**REQ:** REQ-CQGA2-010 | **Method:** LIVE_VERIFICATION | **Cleanup:** no

**Children:**
- TC-CQGA2-018-01: Read `.claude/commands/add-python-api.md` — verify blocking validator IDs present (V100/V102/V104/V109)
- TC-CQGA2-018-02: Call `validate_suspicious_filenames` with a synthetic declaration containing `src/python/csv/csv_misc.py` → assert FAIL, blocks_sprint=True
- TC-CQGA2-018-03: Record PILOT_PASS evidence to `.local/evidences/CQGA-002/pilots/pilot-01-result.yaml`

**Micro-steps for TC-CQGA2-018:**
- MS-018-01: SETUP — confirm Phase C (all repairs) is CLOSED before starting
- MS-018-02: Read `.claude/commands/add-python-api.md` — find "Governance Validators" or "Blocking Validators" section
- MS-018-03: Assert V100, V102, V104, V109 all appear by name or ID in the skill file
- MS-018-04: Import: `from tools.supervisor.governance_validators_ext3 import validate_suspicious_filenames`
- MS-018-05: Call: `result = validate_suspicious_filenames({"planned_work_items": [{"changed_files": ["src/python/csv/csv_misc.py"], "is_new_file": True}]}, REPO_ROOT)`
- MS-018-06: Assert: `result["status"] == "FAIL"` and `result.get("blocks_sprint") is True`
- MS-018-07: Write pilot-01-result.yaml with verdict=PILOT_PASS and code output as evidence
- MS-018-08: CLEANUP — no files to clean up (read-only test); confirm working tree unchanged

---

### TC-CQGA2-019 (PILOT-2): Existing code modification
**Method:** DOCUMENTED | **Cleanup:** no

**Children:**
- TC-CQGA2-019-01: Read `/product-source-task` skill file — verify it requires complete-file context and V46 transcript
- TC-CQGA2-019-02: Verify CCP-BYPASS (direct edit) still has no preventive gate
- TC-CQGA2-019-03: Record PILOT_PASS (context review is convention, detection via declaration_integrity_check added by Repair 2)

**Micro-steps for TC-CQGA2-019:**
- MS-019-01: SETUP — find `/product-source-task` skill file at `.claude/commands/product-source-task.md`
- MS-019-02: Read skill file completely; find the "context requirements" or "prerequisite" section
- MS-019-03: Assert: skill requires complete-file context before edit (not partial context)
- MS-019-04: Assert: skill references V46 or skill-transcript requirement
- MS-019-05: Read CLAUDE.md or AGENTS.md for CCP-BYPASS definition — confirm no preventive gate exists
- MS-019-06: Note: "declaration_integrity_check (Repair 2) provides detective coverage for CCP-BYPASS path"
- MS-019-07: Write pilot-02-result.yaml with verdict=PILOT_PASS and file inspection references as evidence

### TC-CQGA2-020 (PILOT-3): Wrong file placement
**Method:** LIVE_TEST | **Cleanup:** yes (any temp files created)

**Micro-steps:**
- MS-020-01: Call `validate_suspicious_filenames({}, REPO_ROOT)` with synthesized declaration containing `src/python/csv/csv_misc.py`
- MS-020-02: Assert `result["status"] == "FAIL"` and `result["blocks_sprint"] is True`
- MS-020-03: Assert `"csv_misc.py"` appears in violation output
- MS-020-04: Record PILOT_PASS

### TC-CQGA2-021 (PILOT-4): Wrong hierarchy ownership
**Method:** LIVE_VERIFICATION | **Cleanup:** no

- Read `governance_validators_ext4.py` V113 definition; confirm it's registered in runner
- Assert V113 fires for root document type with nested-concept methods (synthetic)

**Micro-steps for TC-CQGA2-021:**
- MS-021-01: SETUP — locate `validate_multi_responsibility_file` or V113 in governance_validators_ext4.py
- MS-021-02: Read V113 function body — understand what "wrong hierarchy ownership" means (root document type containing nested-concept methods)
- MS-021-03: Search runner for V113 registration: `grep -n "V113\|validate_multi_responsibility_file" tools/supervisor/governance_validator_runner.py`
- MS-021-04: Confirm registration exists with blocks_sprint value
- MS-021-05: Construct synthetic declaration: root doc type file with methods that belong to a sub-concept (e.g., worksheet methods on document class)
- MS-021-06: Call V113 with synthetic declaration; assert FAIL or blocks_sprint=True
- MS-021-07: Write pilot-04-result.yaml with verdict and evidence

### TC-CQGA2-022 (PILOT-5): Weak code writing
**Method:** LIVE_TEST | **Cleanup:** yes

**Micro-steps:**
- MS-022-01: Call V104 with a new-file declaration containing a constant-return public method → assert FAIL
- MS-022-02: Call V149 (via `no_stub_scan.scan_path`) on a temp file with bare `pass` method → assert violation found
- MS-022-03: Delete temp file; record PILOT_PASS

### TC-CQGA2-023 (PILOT-6): Documentation quality
**Method:** LIVE_TEST | **Cleanup:** yes

- Call V102 with a new-file declaration containing an undocumented public `def` → assert FAIL, blocks_sprint=True

**Micro-steps for TC-CQGA2-023:**
- MS-023-01: SETUP — import `validate_undocumented_public_python_apis` (V102) from governance_validators_ext3
- MS-023-02: Construct synthetic declaration: `{"planned_work_items": [{"changed_files": ["src/python/csv/csv_new.py"], "is_new_file": True, "public_apis": [{"name": "parse_document", "has_docstring": False}]}]}`
- MS-023-03: Call V102 with synthetic declaration; capture result
- MS-023-04: Assert `result["status"] == "FAIL"` and `result.get("blocks_sprint") is True`
- MS-023-05: Write pilot-06-result.yaml with verdict=PILOT_PASS and assertion output as evidence
- MS-023-06: CLEANUP — no disk files created; confirm working tree clean

---

### TC-CQGA2-024 (PILOT-7): Ungoverned marker
**Method:** LIVE_TEST | **Cleanup:** yes

- Call V103 with file containing `# TODO: fix this` → assert WARN, blocks_sprint=False (documents CQG-009 gap)
- Call V149 with same file → assert "TODO" in forbidden_term violations

**Micro-steps for TC-CQGA2-024:**
- MS-024-01: SETUP — create temp file: `import tempfile; tmpf = tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False); tmpf.write("def func():\n    # TODO: fix this\n    pass\n"); tmpf.close()`
- MS-024-02: Import V103 from governance_validators_ext3; call with declaration referencing temp file path
- MS-024-03: Assert `result["status"]` is NOT "FAIL" (V103 is WARN-only per CQG-009 gap)
- MS-024-04: Assert `result.get("blocks_sprint") is False` or not set
- MS-024-05: Call `no_stub_scan.scan_path(tmpdir)` or scan temp file via V149 mechanism
- MS-024-06: Assert "TODO" appears in the V149 violation output (stub scanner catches it)
- MS-024-07: CLEANUP: `os.unlink(tmpf.name)` — delete temp file
- MS-024-08: Write pilot-07-result.yaml with verdict=PILOT_PASS; note "V103=WARN(CQG-009); V149=FAIL(TODO detected)"

---

### TC-CQGA2-025 (PILOT-8): Traceability break
**Method:** LIVE_TEST | **Cleanup:** no

- Check SAL existence; call V13 with bad spec_fact_ref
- If SAL absent: PILOT_PASS_WITH_SCOPE_LIMITATION (V13 vacuous — documents CQG-008)
- If SAL present: assert FAIL on bad ref

**Micro-steps for TC-CQGA2-025:**
- MS-025-01: SETUP — check if `.local/supervisor/sal-facts-latest.json` exists
- MS-025-02: Import `validate_spec_fact_refs_wired` (V13) from governance_validators
- MS-025-03: Construct declaration with `spec_fact_refs: ["nonexistent:qname_that_does_not_exist"]`
- MS-025-04: Call V13 with declaration and REPO_ROOT
- MS-025-05: BRANCH A (SAL present): assert `result["status"] == "FAIL"` → verdict=PILOT_PASS
- MS-025-06: BRANCH B (SAL absent): assert result passes vacuously → verdict=PILOT_PASS_WITH_SCOPE_LIMITATION; note: "V13 vacuous pass confirmed; CQG-008 documents this gap; Repair 5A mitigates via SAL-gate warning"
- MS-025-07: Write pilot-08-result.yaml with appropriate verdict and branch evidence
- MS-025-08: CLEANUP — no disk changes; confirm working tree clean

---

### TC-CQGA2-026 (PILOT-9): Promotion baseline
**Method:** LIVE_VERIFICATION | **Cleanup:** no

- Read `registry/promotion-ledger.yaml` — verify at least one format has `api_baseline_hash` set
- Read `autonomous_cycle.py` lines ~1039/1063 — verify hash comparison logic present
- Assert both mechanisms exist

**Micro-steps for TC-CQGA2-026:**
- MS-026-01: SETUP — read `registry/promotion-ledger.yaml` fully
- MS-026-02: Find any entry with `api_baseline_hash` field populated (non-null)
- MS-026-03: Assert at least one such entry exists; record the format_id and hash value
- MS-026-04: Read `tools/supervisor/autonomous_cycle.py` lines 1030-1080
- MS-026-05: Find hash comparison logic: code that reads `api_baseline_hash` and compares to current source hash
- MS-026-06: Confirm the logic is not dead code (it has a code path that triggers a rework item or re-open)
- MS-026-07: Write pilot-09-result.yaml with verdict=PILOT_PASS and evidence references (line numbers)

---

### TC-CQGA2-027 (PILOT-10): Reopening trigger
**Method:** LIVE_VERIFICATION | **Cleanup:** no

- Confirm V119 `validate_promoted_code_changed_without_reopening` registered in runner
- Read ext4.py for V119 definition — confirm logic is sound
- Assert both detection mechanisms (V119 + autonomous_cycle) present

**Micro-steps for TC-CQGA2-027:**
- MS-027-01: SETUP — search runner for V119: `grep -n "V119\|validate_promoted_code_changed" tools/supervisor/governance_validator_runner.py`
- MS-027-02: Confirm V119 registration entry exists; record line number and blocks_sprint value
- MS-027-03: Read V119 function definition in `governance_validators_ext4.py`
- MS-027-04: Confirm logic: checks if promoted file's current hash differs from `api_baseline_hash`; returns FAIL if so
- MS-027-05: Confirm the autonomous_cycle reopening trigger (from TC-CQGA2-009-02 findings) operates independently of V119
- MS-027-06: Assert: both mechanisms present and non-redundant (V119 fires at closeout; autonomous_cycle checks at continuation)
- MS-027-07: Write pilot-10-result.yaml with verdict=PILOT_PASS and both mechanism evidence

### TC-CQGA2-028 (PILOT-11): Bypass attempt via undeclared file — Repair 2 test
**Method:** LIVE_TEST | **Cleanup:** yes (unstage any git changes)
**Prereq:** TC-CQGA2-013 CLOSED (declaration_integrity_check.py must exist)

**Micro-steps:**
- MS-028-01: Stage a change to an existing src/python/ file: `git add -N src/python/csv/csv_parser.py` (marks as intent-to-add without modifying content)
  ALTERNATIVE: use a temporary file approach to avoid staging real changes
- MS-028-02: Synthesize a declaration with `changed_files = []` (omitting the staged file)
- MS-028-03: Call `check_declaration_integrity(declaration, REPO_ROOT)`
- MS-028-04: Assert `result["blocks_sprint"] is True`
- MS-028-05: Assert `"src/python/csv/csv_parser.py"` in `result["quality_path_violations"]`
- MS-028-06: Unstage: `git restore --staged src/python/csv/csv_parser.py` (or equivalent cleanup)
- MS-028-07: Record PILOT_PASS

**Cleanup rule:** MUST unstage file in MS-028-06 regardless of test outcome. If cleanup fails, escalate to user.

### TC-CQGA2-029 (PILOT-12): Idempotency
**Method:** LIVE_TEST | **Cleanup:** no

**Micro-steps:**
- MS-029-01: Re-run TC-CQGA2-020 (PILOT-3): validate_suspicious_filenames with same input → same result
- MS-029-02: Re-run TC-CQGA2-022 (PILOT-5) subset: V104 with same bad input → same FAIL
- MS-029-03: Re-run TC-CQGA2-028 (PILOT-11) subset: declaration_integrity_check with same mock → same blocks_sprint=True
- MS-029-04: Assert zero material differences between first and second run for each
- MS-029-05: Record MATERIAL_SECOND_RUN_CHANGES = 0

### TC-CQGA2-030 (PILOT-13 NEW): Enforcement level demotion → ELP-001 fires
**Method:** LIVE_TEST | **Cleanup:** yes
**Prereq:** TC-CQGA2-017 CLOSED (enforcement-level-change-policy.md exists)

**Micro-steps:**
- MS-030-01: Check if V-ELP-001 validator exists yet; if not, use policy document as documented check
- MS-030-02: Verify `enforcement-level-change-policy.md` exists at `docs/code-quality/enforcement-level-change-policy.md`
- MS-030-03: Verify CQG-017 exists in gap ledger with status OPEN_WITH_PARTIAL_MITIGATION
- MS-030-04: Read the V87 demotion evidence from TC-CQGA2-017-01 — confirm retroactive documentation complete
- MS-030-05: Record PILOT_PASS (policy exists; historical violation documented; future demotions now governed)

### TC-CQGA2-031 (PILOT-14 NEW): SAL absent → Phase 14 warns
**Method:** LIVE_TEST | **Cleanup:** yes (restore SAL if renamed)
**Prereq:** TC-CQGA2-016 CLOSED

**Micro-steps:**
- MS-031-01: Check if `.local/supervisor/sal-facts-latest.json` exists
- MS-031-02: If exists: temporarily rename to `.local/supervisor/sal-facts-latest.json.bak`
- MS-031-03: Synthesize a PRODUCT_SOURCE declaration
- MS-031-04: Call `_phase14_sal_population_gate(declaration, REPO_ROOT)` — import from `sprint_executor_validate`
- MS-031-05: Assert result contains `"WARN[SAL-GATE]"` substring
- MS-031-06: Restore SAL file: rename `.bak` back to original name
- MS-031-07: Record PILOT_PASS

**Cleanup rule:** MS-031-06 MUST execute regardless of test outcome.

---

## PHASE E: FINAL REPORT TASKCARD (TC-CQGA2-032)

### TC-CQGA2-032 (PARENT): Final Report + Verdict
**Type:** PARENT | **Status:** READY (after all TC-018–031 CLOSED) | **REQ:** REQ-CQGA2-011
**Prereqs:** ALL previous taskcards CLOSED

**Objective:** Write `reports/code-quality/code-quality-governance-audit-report-CQGA-002.md`
with final verdict based on evidence from all phases.

**Children:**

**TC-CQGA2-032-01: Assemble evidence inventory**
- MS-032-01-01: List all files in `.local/evidences/CQGA-002/` recursively
- MS-032-01-02: Check each required artifact: mission.yaml, validator-delta-table.yaml, root-cause-proof-bundle.yaml — exists and valid YAML
- MS-032-01-03: Check pilot artifacts: pilot-01-result.yaml through pilot-14-result.yaml — all 14 present
- MS-032-01-04: Read each pilot result file; extract `verdict` field — build summary table
- MS-032-01-05: Count: PILOT_PASS | PILOT_PASS_WITH_SCOPE_LIMITATION | PILOT_FAIL per verdict type
- MS-032-01-06: Check repair test outputs: `repairs/governance_block_registry_test_output.txt`, `declaration_integrity_test_output.txt`, `validator_functional_test_output.txt`, `precommit_check_output.txt`, `sal_gate_test_output.txt` — all 5 present
- MS-032-01-07: PRECONDITION CHECK: if any pilot-NN-result.yaml missing → BLOCKED; do not proceed to TC-032-03

**TC-CQGA2-032-02: Compute required counters**
- MS-032-02-01: `CODE_QUALITY_CONTROLS_NOT_INVENTORIED` — count validators in runner minus validators in CQGA-002 audit coverage; expected=0
- MS-032-02-02: `GOV_BLOCK_LIST_INCONSISTENT_WITH_CLAUDE_MD` — run TC-012-05 test suite; if all pass=0, else count failures
- MS-032-02-03: `BLOCKING_VALIDATORS_BYPASSABLE_BY_DECLARATION_OMISSION` — declaration_integrity_check deployed? 0 if yes, else 1
- MS-032-02-04: `VALIDATORS_WITHOUT_FUNCTIONAL_TESTS` — 167 total - 10 P0 covered = 157 (acknowledged backlog); document as ACKNOWLEDGED
- MS-032-02-05: `PRE_COMMIT_HOOKS_UNDETECTED_WHEN_ABSENT` — _check_precommit_installed added? 0 if yes
- MS-032-02-06: `SAL_ABSENCE_PRODUCING_SILENT_VACUOUS_PASS` — Phase 14 gate deployed? 0 if yes
- MS-032-02-07: `ENFORCEMENT_LEVEL_CHANGES_WITHOUT_POLICY_RECORD` — enforcement-level-change-policy.md + CQG-017 entry? 0 if both present
- MS-032-02-08: `FAILED_REQUIRED_PILOTS` — count pilot results with verdict=PILOT_FAIL; expected=0
- MS-032-02-09: `MATERIAL_SECOND_RUN_CHANGES` — from TC-CQGA2-029 result; expected=0
- MS-032-02-10: Write counter summary to `.local/evidences/CQGA-002/counters.yaml`

**TC-CQGA2-032-03: Write audit report**

Micro-steps:
- MS-032-03-01: PRECONDITION — confirm TC-032-01 complete (all evidence present) and TC-032-02 complete (counters computed)
- MS-032-03-02: Read the CQGA-001 audit report for structural template reference (headings, table formats)
- MS-032-03-03: Create `reports/code-quality/code-quality-governance-audit-report-CQGA-002.md`
- MS-032-03-04: Write Section 1 — Executive Summary: verdict string + 3-sentence rationale; table of 9 counters with values
- MS-032-03-05: Write Section 2 — Delta from CQGA-001: 45 commits table classified by type; V145/V149/V87 delta table
- MS-032-03-06: Write Section 3 — Control Inventory: V1-V167 summary with delta (V162→V167 path documented)
- MS-032-03-07: Write Section 4 — Code-Creation Paths: CCP-001 through CCP-BYPASS table with governance coverage per path
- MS-032-03-08: Write Sections 5-9 — Organization/Writing/Docs/Traceability/Review/Promotion: pull from TC-004 through TC-009 findings
- MS-032-03-09: Write Section 10 — Bypasses and Conflicts: updated bypass table with all 7 RCAs (cite proof bundle)
- MS-032-03-10: Write Section 11 — Root Causes: RCA-A through RCA-G, each with proof reference (file:line from proof bundle)
- MS-032-03-11: Write Section 12 — System Repairs: Repairs 1-5 with evidence paths and test results
- MS-032-03-12: Write Section 13 — Pilot Results: 14 pilots table (pilot_id, title, method, verdict)
- MS-032-03-13: Write Section 14 — Idempotency: PILOT-12 result; MATERIAL_SECOND_RUN_CHANGES value
- MS-032-03-14: Write Section 15 — Gap Ledger Summary: 19 gaps table (status changes from CQGA-001)
- MS-032-03-15: Write Section 16 — Required Counters: all 9 counters with values and ACKNOWLEDGED notes
- MS-032-03-16: Write Section 17 — Final Verdict: one of the 3 allowed verdict strings; rationale

**Verdict decision logic:**
- If Repairs 1+2 deployed AND all 14 pilots PASS AND RCA-A acknowledged → `CODE_QUALITY_GOVERNANCE_HEALED_ENFORCED_PROMOTED_AND_PROTECTED`
- If Repairs 1+2 deployed but 3/4/5 partially done, no pilot FAIL → `GOVERNANCE_REPAIR_STILL_ACTIVE`
- If any pilot verdict=PILOT_FAIL → `CODE_QUALITY_GOVERNANCE_REQUIRES_REWORK`

**TC-CQGA2-032-04: Run completion gate checks**

Micro-steps:
- MS-032-04-01: Load counters from `.local/evidences/CQGA-002/counters.yaml`
- MS-032-04-02: Assert `CODE_QUALITY_CONTROLS_NOT_INVENTORIED == 0`; fail with detail if not
- MS-032-04-03: Assert `GOV_BLOCK_LIST_INCONSISTENT_WITH_CLAUDE_MD == 0` — Repair 1 deployed
- MS-032-04-04: Assert `BLOCKING_VALIDATORS_BYPASSABLE_BY_DECLARATION_OMISSION == 0` — Repair 2 deployed
- MS-032-04-05: Assert `VALIDATORS_WITHOUT_FUNCTIONAL_TESTS < 167` — 10 P0 covered minimum; note 157 backlogged as ACKNOWLEDGED
- MS-032-04-06: Assert `PRE_COMMIT_HOOKS_UNDETECTED_WHEN_ABSENT == 0` — Repair 4 deployed
- MS-032-04-07: Assert `SAL_ABSENCE_PRODUCING_SILENT_VACUOUS_PASS == 0` — Repair 5A deployed
- MS-032-04-08: Assert `ENFORCEMENT_LEVEL_CHANGES_WITHOUT_POLICY_RECORD == 0` — Repair 5B deployed
- MS-032-04-09: Assert `FAILED_REQUIRED_PILOTS == 0` — all 14 pilots PASS or PASS_WITH_SCOPE_LIMITATION
- MS-032-04-10: Assert `MATERIAL_SECOND_RUN_CHANGES == 0` — idempotency confirmed
- MS-032-04-11: If ALL assertions pass: mark TC-CQGA2-032 CLOSED; write verdict to report
- MS-032-04-12: If ANY assertion fails: mark TC-CQGA2-032 INTEGRATION_PENDING; record which counter failed and why

**Stop condition:** TC-CQGA2-032 may NOT close until MS-032-04-11 completes successfully.
**Reroute rule:** Any failed counter → create rework child taskcard TC-CQGA2-032-05 naming the exact counter and fix required.

---

## VALIDATION MATRIX

### Phase A Validations (TC-CQGA2-001 through TC-CQGA2-010)

| TC | Validation method | Command/approach | Pass condition | Blocking |
|---|---|---|---|---|
| TC-CQGA2-001 | File existence + YAML parse | `python -c "import yaml; d=yaml.safe_load(open('.local/evidences/CQGA-002/planning/mission.yaml')); assert 'classified_commits' in d"` | No exception; `classified_commits` key present | Yes |
| TC-CQGA2-002 | YAML file content | `python -c "import yaml; d=yaml.safe_load(open('.local/evidences/CQGA-002/planning/validator-delta-table.yaml')); assert all(k in d for k in ['v87_discrepancy_resolution','v145_entry','v149_entry'])"` | V145, V149, V87 entries present with resolution | Yes |
| TC-CQGA2-003 | Finding record check | At least 5 child findings in evidence YAML; no child with status UNKNOWN | All CCP paths have confirmed status | Yes |
| TC-CQGA2-004 | Numeric evidence | `python -c "import yaml; d=yaml.safe_load(open('.local/evidences/CQGA-002/planning/mission.yaml')); assert 'cqg_012_format_count' in d"` | per_file_layout count recorded with numeric value | Yes |
| TC-CQGA2-005 | Live test output | V149 live scan output captured; V105 test call recorded in evidence | V149 returns structured result; V105 asserts FAIL | Yes |
| TC-CQGA2-006 | V87 resolution | V87 post-demotion behavior documented with function body excerpt | V87 coverage and severity change documented | Yes |
| TC-CQGA2-007 | SAL state + V13 test | SAL state (PRESENT/ABSENT) recorded; V13 behavior documented | V13 behavior documented for actual SAL state | Yes |
| TC-CQGA2-008 | Line-level confirmation | `grep -n "WEAK_PROOF" tools/supervisor/proof_adequacy_contract.py` → returns line + `adequate=False` | Line number confirmed; fallback_grade_cap confirmed | Yes |
| TC-CQGA2-009 | Ledger state + line number | promotion-ledger.yaml entries listed; reopening trigger line confirmed | Reopening trigger at exact line X; V119 registered | Yes |
| TC-CQGA2-010 | YAML parse + key check | `python -c "import yaml; d=yaml.safe_load(open('.local/evidences/CQGA-002/planning/root-cause-proof-bundle.yaml')); assert all(k in d for k in ['rca_a','rca_b','rca_c','rca_d','rca_e','rca_f','rca_g'])"` | All 7 RCAs present with file+line evidence | Yes |

### Phase B Validation (TC-CQGA2-011)

| TC | Validation method | Command/approach | Pass condition | Blocking |
|---|---|---|---|---|
| TC-CQGA2-011 | YAML parse + count | `python -c "import yaml; d=yaml.safe_load(open('reports/code-quality/code-quality-governance-ledger.yaml')); assert d['total_gaps'] == 19"` | `total_gaps == 19` | Yes |
| TC-CQGA2-011 | Schema check | Each of CQG-014 through CQG-019 has: gap_id, name, status, root_cause, remediation, task_ids | All 6 new gaps have required fields | Yes |

### Phase C Validations (TC-CQGA2-012 through TC-CQGA2-017)

| TC | Validation method | Command/approach | Pass condition | Blocking |
|---|---|---|---|---|
| TC-CQGA2-012 | Test suite | `.venv/Scripts/pytest tests/supervisor/test_governance_block_registry.py -v` | All 5 tests PASS | Yes |
| TC-CQGA2-012 | Import check | `python -c "from tools.supervisor.governance_block_registry import STRUCTURAL_GOV_BLOCKS; assert len(STRUCTURAL_GOV_BLOCKS) == 8"` | len == 8 | Yes |
| TC-CQGA2-012 | Regression | `.venv/Scripts/pytest tests/supervisor/test_check_continuation*.py -v` | All existing tests PASS | Yes |
| TC-CQGA2-013 | Test suite | `.venv/Scripts/pytest tests/supervisor/test_declaration_integrity.py -v` | All 6 tests PASS | Yes |
| TC-CQGA2-013 | Regression | `.venv/Scripts/pytest tests/supervisor/ -k "autonomous" -v` | All existing tests PASS | Yes |
| TC-CQGA2-014 | Test suite | `.venv/Scripts/pytest tests/governance/test_validators_functional.py -v` | All 10 tests PASS | Yes |
| TC-CQGA2-014 | Timing | Same test run | Total runtime <15s | No |
| TC-CQGA2-015 | Code inspection | `grep "_check_precommit_installed" tools/supervisor/autonomous_cycle.py` | Match found | Yes |
| TC-CQGA2-015 | AGENTS.md inspection | `grep "A2c\|pre-commit" AGENTS.md` | §A2c found | Yes |
| TC-CQGA2-016 | Code inspection | `grep "_phase14_sal_population_gate" tools/supervisor/sprint_executor_validate.py` | Match found | Yes |
| TC-CQGA2-016 | Regression | `.venv/Scripts/pytest tests/supervisor/ -k "validate" -v` | All existing tests PASS | Yes |
| TC-CQGA2-017 | File existence | `python -c "from pathlib import Path; assert Path('docs/code-quality/enforcement-level-change-policy.md').exists()"` | File exists | Yes |
| TC-CQGA2-017 | Ledger check | CQG-017 in ledger with OPEN_WITH_PARTIAL_MITIGATION | Entry present with correct status | Yes |

### Phase D Validations (TC-CQGA2-018 through TC-CQGA2-031)

| TC | Validation method | Command/approach | Pass condition | Blocking |
|---|---|---|---|---|
| TC-CQGA2-018–031 | Per-pilot assertions | As defined in each pilot micro-step | verdict=PILOT_PASS (or PILOT_PASS_WITH_SCOPE_LIMITATION) | Yes |
| TC-CQGA2-018–031 | Evidence file presence | Each pilot-NN-result.yaml has `verdict` field present | 14 files, all have verdict field | Yes |
| TC-CQGA2-029 | Idempotency | Re-run pilots 3, 5, 11 — compare results to first run | Zero material differences | Yes |

### Phase E Validation (TC-CQGA2-032)

| TC | Validation method | Command/approach | Pass condition | Blocking |
|---|---|---|---|---|
| TC-CQGA2-032 | Evidence inventory | All 14 pilot-NN-result.yaml + 5 repairs/*.txt + 3 planning/*.yaml present | All 22 required artifacts exist | Yes |
| TC-CQGA2-032 | Completion counters | All 9 counters from TC-032-04 micro-steps | All 9 pass their assertions | Yes |
| TC-CQGA2-032 | Report structure | Audit report has all 17 required sections | All sections present, verdict string valid | Yes |

### Negative Controls (must prove validators FAIL on known-bad input)

| Validator | Known-bad input | Expected result | TC that proves it |
|---|---|---|---|
| V100 validate_suspicious_filenames | `src/python/csv/csv_misc.py` | status=FAIL, blocks_sprint=True | TC-CQGA2-018, TC-CQGA2-020 |
| V102 validate_undocumented_public_python_apis | new file with undocumented public def | status=FAIL, blocks_sprint=True | TC-CQGA2-023 |
| V104 validate_constant_return_public_methods | new file with constant-return public method | status=FAIL | TC-CQGA2-022 |
| V149 validate_source_stubs | file with bare `pass` body or `# TODO:` | violations non-empty | TC-CQGA2-022, TC-CQGA2-024 |
| V13 validate_spec_fact_refs_wired | spec_fact_ref="nonexistent:qname" (SAL present) | status=FAIL | TC-CQGA2-025 |
| declaration_integrity_check | git change not in changed_files | blocks_sprint=True | TC-CQGA2-028 |
| _phase14_sal_population_gate | SAL absent + PRODUCT_SOURCE items | WARN[SAL-GATE] in output | TC-CQGA2-031 |

---

## EVIDENCE CONTRACT

**Evidence root:** `.local/evidences/CQGA-002/`

Required artifacts by task:

| Artifact path | Produced by | Content |
|---|---|---|
| `planning/mission.yaml` | TC-CQGA2-001-03 | classified_commits, head SHA, baseline ref |
| `planning/validator-delta-table.yaml` | TC-CQGA2-002-05 | V145, V149, V87 delta entries |
| `planning/root-cause-proof-bundle.yaml` | TC-CQGA2-010-07 | RCA-A through RCA-G with file/line evidence |
| `pilots/pilot-01-result.yaml` | TC-CQGA2-018 | PILOT-1 verdict + evidence |
| ... (pilot-02 through pilot-14) | TC-CQGA2-019–031 | Per-pilot verdicts |
| `repairs/governance_block_registry_test_output.txt` | TC-CQGA2-012-05 | pytest -v output |
| `repairs/declaration_integrity_test_output.txt` | TC-CQGA2-013-04 | pytest -v output |
| `repairs/validator_functional_test_output.txt` | TC-CQGA2-014-03 | pytest -v output |
| `repairs/precommit_check_output.txt` | TC-CQGA2-015 | hook existence check output |
| `repairs/sal_gate_test_output.txt` | TC-CQGA2-031 | Phase 14 test result |

**Evidence artifact schema (each pilot-NN-result.yaml):**
```yaml
pilot_id: PILOT-N
tc_id: TC-CQGA2-NNN
title: <pilot title>
method: LIVE_TEST | LIVE_VERIFICATION | DOCUMENTED
verdict: PILOT_PASS | PILOT_PASS_WITH_SCOPE_LIMITATION | PILOT_FAIL
evidence:
  - type: code_output | file_inspection | test_assertion
    content: <excerpt or reference>
scope_limitation: <if PILOT_PASS_WITH_SCOPE_LIMITATION, explain limit>
cleanup_completed: yes | no | not_applicable
```

**Required before TC-CQGA2-032 may start:**
- ALL `pilot-NN-result.yaml` files present (14 total)
- ALL `repairs/*.txt` files present (5 total)
- `planning/root-cause-proof-bundle.yaml` present

---

## EXECUTION HANDOFF

The future execution agent must follow this protocol exactly:

**Step 1: Identify which TC to start**
- Check TC-CQGA2-001 status: if not CLOSED, start there
- Follow the dependency DAG for sequencing

**Step 2: Before starting any taskcard**
- Read the parent taskcard definition fully
- Read the first incomplete child taskcard definition fully
- Read the first PENDING micro-step
- Answer: Which parent TC does this serve? Which REQ? What files may be touched? What must not be changed? What evidence will prove completion?

**Step 3: Execute ONE micro-step at a time**
- Complete the micro-step action
- Capture expected output
- Check the completion condition
- Record evidence immediately
- Update micro-step status: ACTIVE → COMPLETE
- Do NOT start the next micro-step before confirming this one COMPLETE

**Step 4: After all micro-steps of a child complete**
- Run acceptance checks for that child taskcard
- Score the child on all 6 quality dimensions (each ≥4/5 required)
- If any dimension <4/5: mark child REROUTED; create fix micro-steps
- If all ≥4/5: mark child CLOSED

**Step 5: After all children of a parent close**
- Run parent integration checks (listed in parent definition)
- Run regression tests
- If all pass: mark parent CLOSED
- If any fail: mark parent INTEGRATION_PENDING; create child for the failure

**Step 6: Continue to next TC per DAG**
- After TC-CQGA2-010 closes → start TC-CQGA2-011
- After TC-CQGA2-011 closes → start TC-CQGA2-012 (and optionally TC-016, TC-017 in parallel)
- After TC-CQGA2-012 closes → start TC-CQGA2-013 and TC-CQGA2-014 and TC-CQGA2-015 (parallel)
- After all Phase C closes → start Phase D pilots (sequential)
- After TC-CQGA2-031 closes → start TC-CQGA2-032

**Forbidden:**
- Do NOT close a child before all its micro-steps are COMPLETE
- Do NOT close a parent before all mandatory children are CLOSED
- Do NOT skip a micro-step without marking SKIPPED_NOT_APPLICABLE with reason
- Do NOT treat "code exists" as validation — run the specified command
- Do NOT start TC-CQGA2-032 before all pilot evidence artifacts exist
- Do NOT touch product source files (src/python/, src/net/)
- Do NOT create alternative plan files

---

## Gap Ledger Updates (TC-CQGA2-011 reference)

| Gap | Prior Status | Phase A finding | New Status post-CQGA2 |
|---|---|---|---|
| CQG-001 | OPEN | Pre-commit hooks: check TC-CQGA2-010-05 result | OPEN_WITH_PARTIAL_MITIGATION (Repair 4) |
| CQG-004 | OPEN_DETECTIVE_ONLY | No change; declaration_integrity_check adds one more detective layer | OPEN_DETECTIVE_ONLY |
| CQG-006 | PARTIALLY_FIXED | Still name-only hash | PARTIALLY_FIXED |
| CQG-008 | PARTIAL | SAL gate makes absence visible | PARTIAL_WITH_DETECTION (Repair 5A) |
| CQG-009 | OPEN_DESIGN_GAP | V149 catches TODO/stub in new files — partial; V103 remains WARN | TBD by TC-CQGA2-002 (V149 blocks_sprint value) |
| CQG-012 | OPEN_DESIGN_GAP | No new layout entries | OPEN_DESIGN_GAP |
| CQG-013 | OPEN_DESIGN_GAP | No new test-to-spec enforcement | OPEN_DESIGN_GAP |
| CQG-014 (NEW) | — | RCA-A: GOV_BLOCK list 2-of-4 | OPEN → CLOSED after Repair 1 |
| CQG-015 (NEW) | — | RCA-B: declaration scope bypass | OPEN → OPEN_WITH_PARTIAL_MITIGATION after Repair 2 |
| CQG-016 (NEW) | — | RCA-C: count test not functional | OPEN → PARTIALLY_FIXED after Repair 3 (10/54 covered) |
| CQG-017 (NEW) | — | RCA-D: V87 demotion undocumented | OPEN → OPEN_WITH_PARTIAL_MITIGATION after Repair 5B |
| CQG-018 (NEW) | — | RCA-F: SAL absence silent | OPEN → OPEN_WITH_PARTIAL_MITIGATION after Repair 5A |
| CQG-019 (NEW) | — | RCA-E: pre-commit not detected | OPEN → OPEN_WITH_PARTIAL_MITIGATION after Repair 4 |

---

## Tradeoffs and Limits

**What this plan cannot fix:**

1. **The Supreme Directive conflict with blocks_sprint=True** — Repair 1 expands GOV_BLOCK to ~8 validators, but does not address the ~46 remaining `blocks_sprint=True` paths that exit with code 3 (continue regardless). Fully closing this gap requires amending the Supreme Directive — a product-level policy decision by Babar Raza. Acknowledge in final report; flag as TRUE_POLICY_DECISION.

2. **Write-time enforcement** — CQG-004 (direct Edit/Bash bypass) cannot be closed without tool-layer interception. Repair 2 detects undeclared source changes at closeout. But if an agent correctly declares the file while bypassing the skill, validators fire at closeout and the bypass is undetectable.

3. **Skill-first attestation** — V46 requires a skill transcript. V46 is WARN-only. An agent can declare a skill transcript in the declaration without actually running the skill. This is self-attestation fraud that the system cannot mechanically detect.

4. **Legacy file coverage** — V102/V104 are new-file-only for FAIL. 19/20 Python formats have no per-file layout contract (CQG-012). Backfill sprints required; out of scope for this audit.

5. **Rework item persistence** — rework_items in the continuation signal are overwritten each sprint, not accumulated. A persistent violation can be silently overwritten if the next sprint doesn't redeclare the affected file. The Mandatory Rework Register concept (MRR) is architecturally correct but not implemented by this plan — backlogged as future work.

**Confidence calibration:**

| Repair | Confidence | Reason |
|---|---|---|
| 1 (GOV_BLOCK registry) | HIGH | Straightforward code change; bounded scope |
| 2 (declaration integrity) | MEDIUM | Git integration; edge cases on merge/first commit |
| 3 (functional tests) | HIGH for 10 P0; MEDIUM for full 54 | Some validators need substantial synthetic declarations |
| 4 (pre-commit) | LOW as structural fix | AGENTS.md is prompt-based; only CI part (future) is structural |
| 5A (SAL gate) | HIGH for policy; MEDIUM for detection | Depends on sal-facts-latest.json location stability |
| 5B (ELP policy) | HIGH for policy | Document is created; enforcement requires V-ELP-001 (future) |

---

## Verification Completion Gate

After all 32 taskcards CLOSED, verify these counters:

```
CODE_QUALITY_CONTROLS_NOT_INVENTORIED = 0
CODE_QUALITY_RULES_WITH_UNKNOWN_AUTHORITY = 0
CONFLICTING_CODE_QUALITY_RULES_NOT_RESOLVED = 0 (V87 resolved via CQG-017)
GOV_BLOCK_LIST_INCONSISTENT_WITH_CLAUDE_MD = 0 (Repair 1: registry + CLAUDE.md synced)
BLOCKING_VALIDATORS_BYPASSABLE_BY_DECLARATION_OMISSION = 0 (Repair 2: integrity check)
VALIDATORS_WITHOUT_FUNCTIONAL_TESTS = 44 (10 P0 covered; 44 backlogged — not 0, documented)
PRE_COMMIT_HOOKS_UNDETECTED_WHEN_ABSENT = 0 (Repair 4: detection in place)
SAL_ABSENCE_PRODUCING_SILENT_VACUOUS_PASS = 0 (Repair 5A: WARN emitted)
ENFORCEMENT_LEVEL_CHANGES_WITHOUT_POLICY_RECORD = 0 (Repair 5B + CQG-017)
FAILED_REQUIRED_PILOTS = 0
MATERIAL_SECOND_RUN_CHANGES = 0
```

Note: `VALIDATORS_WITHOUT_FUNCTIONAL_TESTS = 44` is ACKNOWLEDGED with rationale (10 P0 done;
44 remaining are tracked as future work). This does not block the verdict if all other counters = 0.

**Final verdict logic:**
- Repairs 1+2 deployed AND all 14 pilots PASS AND RCA-A policy escalation documented:
  → `CODE_QUALITY_GOVERNANCE_HEALED_ENFORCED_PROMOTED_AND_PROTECTED`
- Repairs 1+2 deployed, 3/4/5 partial, no pilot FAIL:
  → `GOVERNANCE_REPAIR_STILL_ACTIVE`
- Any pilot FAIL:
  → `CODE_QUALITY_GOVERNANCE_REQUIRES_REWORK`

---

## Critical Files

**Read (reference, do not modify):**
- `reports/code-quality/code-quality-governance-audit-report-CQGA-001.md`
- `tools/supervisor/check_continuation.py` lines 507-545 (GOV_BLOCK check)
- `tools/supervisor/governance_validators_ext3.py` lines 893-923 (changed_files scope)
- `tools/supervisor/autonomous_cycle.py` (pre-flight + grading)
- `tools/supervisor/sprint_executor_validate.py` (phase structure)
- `CLAUDE.md` §"GOV_BLOCK Exception" and §"Sprint Closeout"
- `plans/.claude/mutable-doodling-blossom.md` (CQGA-001 plan — read only)

**Create (Repairs):**
- `tools/supervisor/governance_block_registry.py` (Repair 1 / TC-CQGA2-012)
- `tools/supervisor/declaration_integrity_check.py` (Repair 2 / TC-CQGA2-013)
- `tests/supervisor/test_governance_block_registry.py` (TC-CQGA2-012-05)
- `tests/supervisor/test_declaration_integrity.py` (TC-CQGA2-013-04)
- `tests/governance/test_validators_functional.py` (Repair 3 / TC-CQGA2-014)
- `docs/code-quality/enforcement-level-change-policy.md` (Repair 5B / TC-CQGA2-017)
- `reports/code-quality/code-quality-governance-audit-report-CQGA-002.md` (TC-CQGA2-032)
- `.local/evidences/CQGA-002/` (all evidence artifacts)

**Modify:**
- `tools/supervisor/check_continuation.py` (Repair 1 / TC-CQGA2-012-03)
- `tools/supervisor/autonomous_cycle.py` (Repair 2 TC-CQGA2-013-03; Repair 4 TC-CQGA2-015-01)
- `tools/supervisor/sprint_executor_validate.py` (Repair 5A / TC-CQGA2-016)
- `CLAUDE.md` (Repair 1 / TC-CQGA2-012-04; Repair 4 / TC-CQGA2-015-02)
- `AGENTS.md` (Repair 4 / TC-CQGA2-015-02)
- `reports/code-quality/code-quality-governance-ledger.yaml` (TC-CQGA2-011, TC-CQGA2-017-03)

---

## Supporting Artifacts Schedule

The following artifacts are to be created by the execution agent during execution,
not during planning. They are NOT alternative plans.

```yaml
# Each artifact must include:
authoritative_plan: C:\Users\prora\.claude\plans\mutable-exploring-hellman.md
artifact_role: analysis_or_evidence_only
execution_authority: false
```

**Phase A — Planning evidence (4 artifacts):**

| Artifact | Created by | Purpose |
|---|---|---|
| `.local/evidences/CQGA-002/planning/mission.yaml` | TC-CQGA2-001-03 | Baseline binding, classified commits |
| `.local/evidences/CQGA-002/planning/section-processing-ledger.yaml` | TC-CQGA2-001-01 | Plan read confirmation |
| `.local/evidences/CQGA-002/planning/validator-delta-table.yaml` | TC-CQGA2-002-05 | V145, V149, V87 delta inventory |
| `.local/evidences/CQGA-002/planning/root-cause-proof-bundle.yaml` | TC-CQGA2-010-07 | RCA-A through RCA-G with file+line proofs |

**Phase B — Gap ledger (updated in-place, no new artifact):**

The gap ledger is updated in `reports/code-quality/code-quality-governance-ledger.yaml` by TC-CQGA2-011.
No separate evidence artifact; validation uses the YAML parse command in §VALIDATION MATRIX.

**Phase C — Repair source files (6 new files + 3 modified):**

| Artifact | Created by | Phase |
|---|---|---|
| `tools/supervisor/governance_block_registry.py` | TC-CQGA2-012-02 | Repair 1 |
| `tools/supervisor/declaration_integrity_check.py` | TC-CQGA2-013-02 | Repair 2 |
| `tests/supervisor/test_governance_block_registry.py` | TC-CQGA2-012-05 | Repair 1 |
| `tests/supervisor/test_declaration_integrity.py` | TC-CQGA2-013-04 | Repair 2 |
| `tests/governance/__init__.py` | TC-CQGA2-014-01 | Repair 3 directory setup |
| `tests/governance/test_validators_functional.py` | TC-CQGA2-014-02–03 | Repair 3 |
| `docs/code-quality/enforcement-level-change-policy.md` | TC-CQGA2-017-02 | Repair 5B |

Modified (not created):
- `tools/supervisor/check_continuation.py` (Repair 1 / TC-CQGA2-012-03)
- `tools/supervisor/autonomous_cycle.py` (Repair 2 TC-013-03; Repair 4 TC-015-01)
- `tools/supervisor/sprint_executor_validate.py` (Repair 5A / TC-CQGA2-016-02)
- `CLAUDE.md` (Repair 1 / TC-012-04; AGENTS §A2c / TC-015-02)
- `AGENTS.md` (Repair 4 / TC-015-02)
- `reports/code-quality/code-quality-governance-ledger.yaml` (TC-011; TC-017-03)

**Phase C — Test evidence artifacts (5 .txt files):**

| Artifact | Created by | Content |
|---|---|---|
| `.local/evidences/CQGA-002/repairs/governance_block_registry_test_output.txt` | TC-CQGA2-012-05 | pytest -v output (5 tests PASS) |
| `.local/evidences/CQGA-002/repairs/declaration_integrity_test_output.txt` | TC-CQGA2-013-04 | pytest -v output (6 tests PASS) |
| `.local/evidences/CQGA-002/repairs/validator_functional_test_output.txt` | TC-CQGA2-014-03 | pytest -v output (10 tests PASS) |
| `.local/evidences/CQGA-002/repairs/precommit_check_output.txt` | TC-CQGA2-015-01 | hook existence check output |
| `.local/evidences/CQGA-002/repairs/sal_gate_test_output.txt` | TC-CQGA2-031 | Phase 14 gate test result |

**Phase D — Pilot evidence (14 YAML files):**

| Artifact | Created by | Pilot |
|---|---|---|
| `.local/evidences/CQGA-002/pilots/pilot-01-result.yaml` | TC-CQGA2-018 | PILOT-1: New code via skill |
| `.local/evidences/CQGA-002/pilots/pilot-02-result.yaml` | TC-CQGA2-019 | PILOT-2: Existing code modification |
| `.local/evidences/CQGA-002/pilots/pilot-03-result.yaml` | TC-CQGA2-020 | PILOT-3: Wrong file placement |
| `.local/evidences/CQGA-002/pilots/pilot-04-result.yaml` | TC-CQGA2-021 | PILOT-4: Wrong hierarchy ownership |
| `.local/evidences/CQGA-002/pilots/pilot-05-result.yaml` | TC-CQGA2-022 | PILOT-5: Weak code writing |
| `.local/evidences/CQGA-002/pilots/pilot-06-result.yaml` | TC-CQGA2-023 | PILOT-6: Documentation quality |
| `.local/evidences/CQGA-002/pilots/pilot-07-result.yaml` | TC-CQGA2-024 | PILOT-7: Ungoverned marker |
| `.local/evidences/CQGA-002/pilots/pilot-08-result.yaml` | TC-CQGA2-025 | PILOT-8: Traceability break |
| `.local/evidences/CQGA-002/pilots/pilot-09-result.yaml` | TC-CQGA2-026 | PILOT-9: Promotion baseline |
| `.local/evidences/CQGA-002/pilots/pilot-10-result.yaml` | TC-CQGA2-027 | PILOT-10: Reopening trigger |
| `.local/evidences/CQGA-002/pilots/pilot-11-result.yaml` | TC-CQGA2-028 | PILOT-11: Bypass via undeclared file |
| `.local/evidences/CQGA-002/pilots/pilot-12-result.yaml` | TC-CQGA2-029 | PILOT-12: Idempotency |
| `.local/evidences/CQGA-002/pilots/pilot-13-result.yaml` | TC-CQGA2-030 | PILOT-13: ELP-001 fires |
| `.local/evidences/CQGA-002/pilots/pilot-14-result.yaml` | TC-CQGA2-031 | PILOT-14: SAL absent → Phase 14 warns |

**Phase E — Counters and final report (2 artifacts):**

| Artifact | Created by | Content |
|---|---|---|
| `.local/evidences/CQGA-002/counters.yaml` | TC-CQGA2-032-02 | All 9 completion counters with values |
| `reports/code-quality/code-quality-governance-audit-report-CQGA-002.md` | TC-CQGA2-032-03 | Final audit report (17 sections) |

**Total artifact count: 4 planning + 5 repair test outputs + 7 repair source files + 14 pilot YAMLs + 2 final = 32 artifacts produced during execution.**

---

## REQUIREMENT TRACEABILITY

Maps each REQ-CQGA2-NNN → parent TC → child TCs → first micro-step.
Used by execution agent to verify scope discipline: no work performed that cannot be traced to a requirement.

| REQ-ID | Statement (abbreviated) | Parent TC | Child TCs | First micro-step |
|---|---|---|---|---|
| REQ-CQGA2-001 | GOV_BLOCK list must match CLAUDE.md | TC-CQGA2-012 | 012-01, 012-02, 012-03, 012-04, 012-05 | MS-012-01-01 |
| REQ-CQGA2-002 | declared changed_files cross-checked vs git | TC-CQGA2-013 | 013-01, 013-02, 013-03, 013-04 | MS-013-01-01 |
| REQ-CQGA2-003 | Every blocking validator has functional test | TC-CQGA2-014 | 014-01, 014-02, 014-03 | MS-014-01-01 |
| REQ-CQGA2-004 | Enforcement level reduction requires gap entry | TC-CQGA2-017 | 017-01, 017-02, 017-03 | MS-017-01-01 |
| REQ-CQGA2-005 | Pre-commit absence detected at sprint start | TC-CQGA2-015 | 015-01, 015-02 | MS-015-01-01 |
| REQ-CQGA2-006 | PRODUCT_SOURCE decl warns when SAL absent | TC-CQGA2-016 | 016-01, 016-02 | MS-016-01-01 |
| REQ-CQGA2-007 | (Absorbed by REQ-CQGA2-002) | TC-CQGA2-013 | — | — |
| REQ-CQGA2-008 | Gap ledger reconciled with CQGA-002 findings | TC-CQGA2-011 | 011-01, 011-02, 011-03 | MS-011-01-01 |
| REQ-CQGA2-009 | Delta audit of 45 post-CQGA-001 commits | TC-CQGA2-001–010 | all Phase A children | MS-001-02-01 |
| REQ-CQGA2-010 | All 14 pilots pass with live test evidence | TC-CQGA2-018–031 | per-pilot children | MS-018-01 |
| REQ-CQGA2-011 | Final report produces verdict | TC-CQGA2-032 | 032-01, 032-02, 032-03, 032-04 | MS-032-01-01 |
| REQ-CQGA2-012 | Second run of all pilots produces zero material changes | TC-CQGA2-029 | idempotency child | MS-029-01 |

**Traceability rules for execution agent:**
1. Before starting any child taskcard, confirm it maps to a REQ-ID above.
2. If a child taskcard cannot be mapped to a REQ-ID, it is out-of-scope work — stop and ask.
3. Phase A TCs (TC-001–010) all serve REQ-CQGA2-009 (delta audit evidence requirement).
4. Phase D pilots all serve REQ-CQGA2-010 (pilot pass requirement).
5. No REQ-ID maps to product source (src/python/, src/net/) — any work touching those files is unauthorized.

---

## PHASE A QUALITY SCORING

Investigation taskcards (TC-CQGA2-001 through TC-CQGA2-010) are graded on the same 6-dimension
rubric as repair taskcards. Scoring applies after all children of a parent TC close.

**Scoring rubric for Phase A (Investigation) children:**

| Dimension | 5 (Excellent) | 4 (Acceptable) | <4 (REROUTED) |
|---|---|---|---|
| requirement_correctness | Finding directly proves or disproves a RCA | Finding is relevant but indirect | Finding is off-topic or unfalsifiable |
| implementation_correctness | Command run and output captured verbatim | Command run; output paraphrased | Command not run; claim not verified |
| scope_discipline | Only allowed files read; no source modified | Read one extra file accidentally | Source files modified or out-of-scope edit made |
| validation_strength | Evidence contains file path + line number | Evidence contains file path only | Evidence is a paraphrase with no file reference |
| evidence_completeness | YAML artifact written with all required fields | YAML written but missing 1 field | No YAML artifact written |
| regression_safety | Read-only throughout; zero git state changes | One benign git query run | Staged changes, edits, or git state altered |

**Phase A child taskcards that require REROUTE (auto-disqualified):**
- Any child where `implementation_correctness < 4`: the command was not run; evidence is fabricated.
  → Mark child REROUTED; create a redo micro-step with the explicit command to run.
- Any child where `evidence_completeness < 4`: no YAML artifact was written.
  → Mark child REROUTED; add micro-step to write the artifact before re-scoring.

**Stop rules for Phase A:**
- If TC-CQGA2-010-07 (root-cause-proof-bundle.yaml) cannot be written with all 7 RCA keys proved →
  Phase A is BLOCKED_EXTERNAL (evidence gap). Record which RCA is UNPROVEN and stop Phase A.
  Do NOT proceed to Phase B until all 7 RCA keys have at least PARTIAL evidence.
- If YAML validation fails: `python -c "import yaml; yaml.safe_load(open(...))"` — fix file before advancing.

**Phase A → Phase B transition gate:**
Phase B (TC-CQGA2-011, gap ledger update) may NOT start until:
1. `planning/root-cause-proof-bundle.yaml` exists and passes YAML validation
2. All 7 RCA keys present in the bundle (UNPROVEN entries are allowed, but keys must exist)
3. All 10 Phase A parent TCs are marked VERIFIED or SCORED
