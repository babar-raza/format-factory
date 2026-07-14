# Vast Wibbling Moon — Specialist Machinery and Output Assurance Sprint

**Plan type:** machinery_hardening
**Mission ID:** VWM-2026-07-10
**Authority:** `plans/.claude/vast-wibbling-moon.md` — SOLE authoritative plan
**Enhancement pass:** MICRO-TASKCARDIZATION v2.0 (2026-07-10)
**Enhancement mode:** MODE B — TASKCARD_SECTION_HARDENING

> **Supporting artifacts** produced during execution must each carry:
> `authoritative_plan: plans/.claude/vast-wibbling-moon.md`
> `artifact_role: analysis_or_evidence_only`
> `execution_authority: false`

---

## SECTION 1 — CONTEXT (PRESERVED)

The format-factory supervisor machinery has grown to ~242 modules, 165+ governance
validators, a dual-track continuation system, oracle layer, SQLite control index,
skill-first execution framework, and a multi-format product pipeline spanning .NET and
Python tracks. Prior machinery assurance (MA-2026-07-02-R1227-NDJSON-TOML) covered
only 10 stages for a single sprint scope. This sprint performs a **system-wide
specialist assurance** across every machinery stage, all output classes, and the
complete pipeline from declaration through output publication.

**Known issues triggering this sprint:**

| # | Issue | Severity | Source |
|---|---|---|---|
| I-001 | Continuation signal (2026-07-04) has `stop_reason: critical_rework_blocks_continuation` but `rework_items: []` — contradictory | HIGH | .local/supervisor/continuation-signal.json |
| I-002 | `session_id: null` in continuation signal — CCI-MVP isolation not in effect | MEDIUM | .local/supervisor/continuation-signal.json |
| I-003 | GAP-MA-001 OPEN: site-packages sync has no automated enforcement | MEDIUM | reports/machinery-assurance/gap-ledger.yaml |
| I-004 | GAP-MA-006 DOCUMENTED in MEMORY.md but NOT in formal gap-ledger.yaml | MEDIUM | MEMORY.md |
| I-005 | MEMORY.md claims 165 governance validators; runner `expected_count` may have drifted (V149 added 2026-07-09) | HIGH | tools/supervisor/governance_validator_runner.py |
| I-006 | Vast-weaving-lampson plan lock is TERMINAL_CLOSED — verify check_continuation handles new session correctly | MEDIUM | .local/supervisor/active-plan-lock.json |
| I-007 | `reports/machinery-assurance/gap-ledger.yaml` still has format from MA-2026-07-02 scope; needs system-wide update | LOW | reports/machinery-assurance/ |

---

## SECTION 2 — MISSION BINDING RECORD (PRESERVED)

```yaml
assurance_mission:
  mission_id: VWM-2026-07-10
  repository: format-factory
  branch: main
  head: af879e55
  plan_path: plans/.claude/vast-wibbling-moon.md
  plan_revision: "2.0"
  machinery_roots:
    - tools/supervisor/
    - tools/review/
    - tools/assurance/
    - .supervisor/
    - tools/oracle/
  official_entry_points:
    - "python tools/supervisor/autonomous_cycle.py"
    - "python tools/supervisor/check_continuation.py"
    - "python tools/supervisor/governance_validator_runner.py"
    - "python tools/supervisor/write_plan_lock.py"
    - "python tools/supervisor/sprint_executor.py run-loop"
  state_stores:
    - .local/supervisor/continuation-signal.json
    - .local/supervisor/active-plan-lock.json
    - .local/supervisor/next-work-items.json
    - .local/supervisor/control-index.db
    - .supervisor/state/current-run.json
  output_roots:
    - reports/supervisor/
    - reports/machinery-assurance/
    - .local/evidences/
    - src/python/
    - src/net/
  consumer_roots:
    - tests/
    - src/python/
    - src/net/
  governing_skills:
    - /autonomous-loop
    - /check-gate
    - /post-sprint-audit
    - /plan-hardening
    - /validate-skill-contracts
    - /append-layer-verification-log
    - /run-oracle
  evidence_roots:
    - .local/evidences/
    - .local/supervisor/reviews/
  explicit_non_goals:
    - Gate 11 execution (Babar Raza only)
    - PyPI/NuGet publication
    - git push (SCM Agent task)
    - MODE 5 autonomous sprint loop activation
```

---

## SECTION 3 — REQUIREMENTS REGISTRY

Stable requirement IDs. Every parent taskcard maps to one or more REQ-VWM-NNN.

| REQ-ID | Requirement | Maps To |
|---|---|---|
| REQ-VWM-001 | Write plan lock at session start before any other work | TC-VWM-001 |
| REQ-VWM-002 | Read and record complete session state from state files | TC-VWM-001 |
| REQ-VWM-003 | Carry forward all open gaps from prior assurance mission | TC-VWM-001 |
| REQ-VWM-004 | Write assurance-mission.yaml with all required fields | TC-VWM-001 |
| REQ-VWM-005 | Enumerate and classify all machinery files from real code | TC-VWM-002 |
| REQ-VWM-006 | Trace all import chains from official entry points | TC-VWM-002 |
| REQ-VWM-007 | Map all state write operations and identify ownership | TC-VWM-002 |
| REQ-VWM-008 | Find and classify all bypass paths and legacy paths | TC-VWM-002 |
| REQ-VWM-009 | Write machinery-stage-inventory.yaml with all required fields | TC-VWM-002 |
| REQ-VWM-010 | Manually review Stage S01: Evidence Declaration Validation | TC-VWM-003 |
| REQ-VWM-011 | Manually review Stage S02: Declaration Inspection & Materialization | TC-VWM-004 |
| REQ-VWM-012 | Manually review Stage S03: Governance Validation (165+ validators) | TC-VWM-005 |
| REQ-VWM-013 | Manually review Stage S04: Work Item Grading | TC-VWM-006 |
| REQ-VWM-014 | Manually review Stage S05: Sprint Planning & Next-Sprint Generation | TC-VWM-007 |
| REQ-VWM-015 | Manually review Stage S06: Continuation Checking & Session Identity | TC-VWM-008 |
| REQ-VWM-016 | Manually review Stage S07: Plan Lock Management | TC-VWM-009 |
| REQ-VWM-017 | Manually review Stage S08: Evidence Manifest & Review Package | TC-VWM-010 |
| REQ-VWM-018 | Manually review Stage S09: Gap Ledger & Work Item Selection | TC-VWM-011 |
| REQ-VWM-019 | Manually review Stage S10: Anti-Skip & Stub Detection | TC-VWM-012 |
| REQ-VWM-020 | Manually review Stage S11: Control Index | TC-VWM-013 |
| REQ-VWM-021 | Manually review Stage S12: Skill Registry & Skill-First Execution | TC-VWM-014 |
| REQ-VWM-022 | Manually review Stage S13: Oracle Layer | TC-VWM-015 |
| REQ-VWM-023 | Manually review Stage S14: Autonomous Loop Orchestration | TC-VWM-016 |
| REQ-VWM-024 | Manually review Stage S15: Lifecycle Audit | TC-VWM-017 |
| REQ-VWM-025 | Build and review all 18 output classes | TC-VWM-018 |
| REQ-VWM-026 | Score all quality dimensions 1-5, flag any < 4 | TC-VWM-019 |
| REQ-VWM-027 | Reconcile all major claims against direct evidence | TC-VWM-020 |
| REQ-VWM-028 | Build canonical gap ledger with all required fields | TC-VWM-021 |
| REQ-VWM-029 | Map every actionable gap to a bounded taskcard | TC-VWM-022 |
| REQ-VWM-030 | Heal machinery gaps starting from root cause | TC-VWM-023 |
| REQ-VWM-031 | Verify healed machinery passes proof-level targets | TC-VWM-024 |
| REQ-VWM-032 | Regenerate all outputs affected by healed machinery | TC-VWM-025 |
| REQ-VWM-033 | Revalidate output quality after regeneration | TC-VWM-026 |
| REQ-VWM-034 | Run all 10 required pilots with evidence | TC-VWM-027 |
| REQ-VWM-035 | Perform independent fresh specialist review after healing | TC-VWM-028 |
| REQ-VWM-036 | Verify all completion gate counters = 0 before closure | TC-VWM-029 |
| REQ-VWM-037 | Write final report with exactly one of three verdicts | TC-VWM-029 |
| REQ-VWM-038 | Write evidence declaration and run autonomous cycle | TC-VWM-029 |
| REQ-VWM-039 | Run lifecycle audit before writing --terminal lock | TC-VWM-029 |
| REQ-VWM-040 | Second run produces zero material changes (idempotency) | TC-VWM-029 |

---

## SECTION 4 — STATE MACHINE SPECIFICATION

### Parent Taskcard States

```
PROPOSED → READY → IN_PROGRESS → CHILDREN_IN_PROGRESS → INTEGRATION_PENDING
→ VERIFIED → SCORED → CLOSED

SCORED → REROUTED (if any quality gate < 4/5)
REROUTED → IN_PROGRESS (after rework)
any → BLOCKED (waiting on prerequisite)
BLOCKED → READY (when unblocked)
any → BLOCKED_EXTERNAL (TRUE_EXTERNAL_GATE only)
any → DEFERRED_WITH_REASON (approved deferral only)
```

**Invalid parent transitions (blocked):**
- PROPOSED → CLOSED (must traverse all states)
- READY → CLOSED (must traverse IN_PROGRESS minimum)
- CHILDREN_IN_PROGRESS → CLOSED (must pass INTEGRATION_PENDING)
- REROUTED → CLOSED (must pass through rework cycle)
- BLOCKED_EXTERNAL → CLOSED (must have unblock evidence)

### Child Taskcard States

```
TODO → READY → IN_PROGRESS → IMPLEMENTED → VERIFIED → SCORED → CLOSED
SCORED → REROUTED (if quality gate < 4/5)
REROUTED → IN_PROGRESS
any → BLOCKED / BLOCKED_EXTERNAL / DEFERRED_WITH_REASON
```

**Invalid child transitions (blocked):**
- TODO → CLOSED (must traverse IN_PROGRESS, IMPLEMENTED, VERIFIED)
- IMPLEMENTED → CLOSED (must be VERIFIED first)
- REROUTED → CLOSED (must pass through rework)

### Micro-Step States

```
PENDING → READY → ACTIVE → COMPLETE
ACTIVE → FAILED → READY (retry)
ACTIVE → BLOCKED → READY (when unblocked)
PENDING → SKIPPED_NOT_APPLICABLE (must record reason)
```

**Invalid micro-step transitions (blocked):**
- PENDING → COMPLETE (must be ACTIVE first)
- ACTIVE → COMPLETE without recorded output
- FAILED → COMPLETE without repair

### Quality Gate Rule

Any child scoring < 4/5 on any mandatory dimension:
1. Mark child REROUTED
2. Record which dimension failed and exact score
3. Create or reopen the specific repair micro-step
4. Re-execute, re-verify, re-score
5. Only advance to CLOSED when all mandatory dimensions ≥ 4/5

---

## SECTION 5 — DEPENDENCY DAG

```
TC-VWM-001 (BIND)
  └── TC-VWM-002 (DISCOVER)
        ├── TC-VWM-003 (S01 — can run in parallel with 004-017)
        ├── TC-VWM-004 (S02)
        ├── TC-VWM-005 (S03 — PRIORITY: run first among stage reviews)
        ├── TC-VWM-006 (S04)
        ├── TC-VWM-007 (S05)
        ├── TC-VWM-008 (S06 — PRIORITY: run second among stage reviews)
        ├── TC-VWM-009 (S07)
        ├── TC-VWM-010 (S08)
        ├── TC-VWM-011 (S09)
        ├── TC-VWM-012 (S10)
        ├── TC-VWM-013 (S11)
        ├── TC-VWM-014 (S12)
        ├── TC-VWM-015 (S13)
        ├── TC-VWM-016 (S14)
        └── TC-VWM-017 (S15)
              └── TC-VWM-018 (OUTPUT CLASSES — needs all stage reviews)
                    ├── TC-VWM-019 (QUALITY SCORES — needs 018)
                    └── TC-VWM-020 (CLAIM RECONCILIATION — needs 018)
                          └── TC-VWM-021 (GAP LEDGER — needs 019 + 020)
                                └── TC-VWM-022 (HARDEN PLAN — needs 021)
                                      └── TC-VWM-023 (HEAL — needs 022)
                                            └── TC-VWM-024 (VERIFY HEALED — needs 023)
                                                  └── TC-VWM-025 (REGENERATE — needs 024)
                                                        └── TC-VWM-026 (REVALIDATE — needs 025)
                                                              └── TC-VWM-027 (PILOTS — needs 026)
                                                                    └── TC-VWM-028 (FINAL REVIEW — needs 027)
                                                                          └── TC-VWM-029 (CLOSURE — needs 028)
```

**Parallel-safe groups** (can run simultaneously after TC-VWM-002 completes):
- Group A: TC-VWM-003, TC-VWM-004, TC-VWM-006, TC-VWM-007, TC-VWM-009, TC-VWM-010, TC-VWM-011, TC-VWM-012, TC-VWM-013, TC-VWM-014
- Group B (separate file ownership): TC-VWM-005 (governance_validators only), TC-VWM-008 (continuation only), TC-VWM-015 (oracle only), TC-VWM-016 (orchestration only), TC-VWM-017 (lifecycle only)

**File ownership locks** (must not run concurrently):
- TC-VWM-005 owns: `governance_validator_runner.py`, `governance_validators*.py`
- TC-VWM-008 owns: `check_continuation.py`, `continuation_*.py`, `.local/supervisor/continuation-signal.json`
- TC-VWM-009 owns: `write_plan_lock.py`, `plan_lock_gc.py`, `.local/supervisor/active-plan-lock.json`
- TC-VWM-023 owns: all healed machinery files (to be specified in TC-VWM-022 hardening)
- TC-VWM-025 owns: all affected output files (defined in output-healing-run.yaml)

---

## SECTION 6 — SECTION PROCESSING LEDGER

| Section | Type | Analysis | Actionables | Children Added | Ambiguities | Status |
|---|---|---|---|---|---|---|
| S0 Plan Metadata | metadata | DONE | 0 | N/A | None | RECONCILED |
| S1 Context | background | DONE | 0 | N/A | None | PRESERVED |
| S2 Known Issues | findings | DONE | 7 issues → gaps | TC-VWM-021 will register | I-005 count unconfirmed | TRACKED |
| S3 Mission Binding | configuration | DONE | 0 | N/A | None | PRESERVED |
| S4 Requirements Registry | NEW | DONE | 40 REQs | all TCs | None | COMPLETE |
| S5 State Machine | NEW | DONE | 0 | N/A | None | COMPLETE |
| S6 Dependency DAG | NEW | DONE | 0 | N/A | None | COMPLETE |
| S7 Section Ledger | NEW | DONE | 0 | N/A | None | COMPLETE |
| S8 Taskcard Index | index | DONE | 29 TCs | children in TC sections | None | ENHANCED |
| TC-VWM-001 | taskcard | DONE | 5 children | TC-VWM-001-01 through -05 | None | DECOMPOSED |
| TC-VWM-002 | taskcard | DONE | 6 children | TC-VWM-002-01 through -06 | None | DECOMPOSED |
| TC-VWM-003 | taskcard | DONE | 4 children (standard) | TC-VWM-003-01 through -04 | None | DECOMPOSED |
| TC-VWM-004 | taskcard | DONE | 4 children (standard) | TC-VWM-004-01 through -04 | None | DECOMPOSED |
| TC-VWM-005 | taskcard | DONE | 5 children | TC-VWM-005-01 through -05 | Count drift I-005 | DECOMPOSED |
| TC-VWM-006 | taskcard | DONE | 4 children (standard) | TC-VWM-006-01 through -04 | None | DECOMPOSED |
| TC-VWM-007 | taskcard | DONE | 4 children (standard) | TC-VWM-007-01 through -04 | None | DECOMPOSED |
| TC-VWM-008 | taskcard | DONE | 5 children | TC-VWM-008-01 through -05 | I-001 I-002 | DECOMPOSED |
| TC-VWM-009 | taskcard | DONE | 4 children (standard) | TC-VWM-009-01 through -04 | None | DECOMPOSED |
| TC-VWM-010 | taskcard | DONE | 4 children (standard) | TC-VWM-010-01 through -04 | None | DECOMPOSED |
| TC-VWM-011 | taskcard | DONE | 4 children (standard) | TC-VWM-011-01 through -04 | I-004 | DECOMPOSED |
| TC-VWM-012 | taskcard | DONE | 4 children (standard) | TC-VWM-012-01 through -04 | None | DECOMPOSED |
| TC-VWM-013 | taskcard | DONE | 4 children (standard) | TC-VWM-013-01 through -04 | None | DECOMPOSED |
| TC-VWM-014 | taskcard | DONE | 4 children (standard) | TC-VWM-014-01 through -04 | None | DECOMPOSED |
| TC-VWM-015 | taskcard | DONE | 4 children (standard) | TC-VWM-015-01 through -04 | None | DECOMPOSED |
| TC-VWM-016 | taskcard | DONE | 4 children (standard) | TC-VWM-016-01 through -04 | None | DECOMPOSED |
| TC-VWM-017 | taskcard | DONE | 4 children (standard) | TC-VWM-017-01 through -04 | None | DECOMPOSED |
| TC-VWM-018 | taskcard | DONE | 5 children | TC-VWM-018-01 through -05 | None | DECOMPOSED |
| TC-VWM-019 | taskcard | DONE | 3 children | TC-VWM-019-01 through -03 | None | DECOMPOSED |
| TC-VWM-020 | taskcard | DONE | 3 children | TC-VWM-020-01 through -03 | None | DECOMPOSED |
| TC-VWM-021 | taskcard | DONE | 4 children | TC-VWM-021-01 through -04 | None | DECOMPOSED |
| TC-VWM-022 | taskcard | DONE | 3 children | TC-VWM-022-01 through -03 | None | DECOMPOSED |
| TC-VWM-023 | taskcard | DONE | 4 children | TC-VWM-023-01 through -04 | Gaps TBD | DECOMPOSED |
| TC-VWM-024 | taskcard | DONE | 4 children | TC-VWM-024-01 through -04 | None | DECOMPOSED |
| TC-VWM-025 | taskcard | DONE | 3 children | TC-VWM-025-01 through -03 | None | DECOMPOSED |
| TC-VWM-026 | taskcard | DONE | 3 children | TC-VWM-026-01 through -03 | None | DECOMPOSED |
| TC-VWM-027 | taskcard | DONE | 5 children (pilots 1-10) | TC-VWM-027-01 through -05 | None | DECOMPOSED |
| TC-VWM-028 | taskcard | DONE | 3 children | TC-VWM-028-01 through -03 | None | DECOMPOSED |
| TC-VWM-029 | taskcard | DONE | 5 children | TC-VWM-029-01 through -05 | None | DECOMPOSED |
| S Supporting Artifacts | manifest | DONE | 45 artifacts | defined in Section 7 | None | DEFINED |
| S Execution Handoff | handoff | DONE | 0 | N/A | None | COMPLETE |
| S Status Table | lifecycle_audit | DONE | 0 | N/A | None | COMPLETE |

---

## SECTION 7 — SUPPORTING ARTIFACT MANIFEST

Artifacts to be created DURING EXECUTION. All carry:
`authoritative_plan: plans/.claude/vast-wibbling-moon.md | execution_authority: false`

| Artifact | Path | Created By | Phase |
|---|---|---|---|
| taskcardization-preflight.md | reports/machinery-assurance/vwm-analysis/taskcardization-preflight.md | TC-VWM-001 | Bind |
| active-plan-authority-verdict.md | reports/machinery-assurance/vwm-analysis/active-plan-authority-verdict.md | TC-VWM-001 | Bind |
| duplicate-plan-risk-check.md | reports/machinery-assurance/vwm-analysis/duplicate-plan-risk-check.md | TC-VWM-001 | Bind |
| assurance-mission.yaml | reports/machinery-assurance/assurance-mission.yaml | TC-VWM-001-05 | Bind |
| plan-section-inventory.md | reports/machinery-assurance/vwm-analysis/plan-section-inventory.md | TC-VWM-002-01 | Discover |
| plan-structure-and-normalization-profile.md | reports/machinery-assurance/vwm-analysis/plan-structure-profile.md | TC-VWM-002-01 | Discover |
| machinery-stage-inventory.yaml | reports/machinery-assurance/machinery-stage-inventory.yaml | TC-VWM-002-06 | Discover |
| section-processing-ledger.yaml | reports/machinery-assurance/vwm-analysis/section-processing-ledger.yaml | TC-VWM-002-06 | Discover |
| complete-plan-read-confirmation.md | reports/machinery-assurance/vwm-analysis/complete-plan-read-confirmation.md | TC-VWM-002-06 | Discover |
| plan-part-deep-analysis.yaml | reports/machinery-assurance/vwm-analysis/plan-part-deep-analysis.yaml | TC-VWM-002-06 | Discover |
| phase-section-step-analysis.md | reports/machinery-assurance/vwm-analysis/phase-section-step-analysis.md | TC-VWM-002-06 | Discover |
| actionable-item-extraction-log.yaml | reports/machinery-assurance/vwm-analysis/actionable-item-extraction-log.yaml | TC-VWM-002-06 | Discover |
| actionable-to-source-traceability.csv | reports/machinery-assurance/vwm-analysis/actionable-to-source-traceability.csv | TC-VWM-002-06 | Discover |
| stage-reviews.yaml | reports/machinery-assurance/stage-reviews.yaml | TC-VWM-003 through TC-VWM-017 | Stage Reviews |
| solution-options-analysis.md | reports/machinery-assurance/vwm-analysis/solution-options-analysis.md | TC-VWM-021 | Gap Ledger |
| solution-option-scorecard.yaml | reports/machinery-assurance/vwm-analysis/solution-option-scorecard.yaml | TC-VWM-021 | Gap Ledger |
| selected-solution-rationale.md | reports/machinery-assurance/vwm-analysis/selected-solution-rationale.md | TC-VWM-021 | Gap Ledger |
| normalized-requirements-inventory.yaml | reports/machinery-assurance/vwm-analysis/normalized-requirements-inventory.yaml | TC-VWM-022 | Harden |
| section-to-requirement-map.csv | reports/machinery-assurance/vwm-analysis/section-to-requirement-map.csv | TC-VWM-022 | Harden |
| requirement-to-parent-taskcard-map.csv | reports/machinery-assurance/vwm-analysis/requirement-to-parent-taskcard-map.csv | TC-VWM-022 | Harden |
| parent-to-child-taskcard-map.csv | reports/machinery-assurance/vwm-analysis/parent-to-child-taskcard-map.csv | TC-VWM-022 | Harden |
| child-to-micro-step-map.csv | reports/machinery-assurance/vwm-analysis/child-to-micro-step-map.csv | TC-VWM-022 | Harden |
| end-to-end-execution-traceability.csv | reports/machinery-assurance/vwm-analysis/end-to-end-execution-traceability.csv | TC-VWM-022 | Harden |
| execution-dag.yaml | reports/machinery-assurance/vwm-analysis/execution-dag.yaml | TC-VWM-022 | Harden |
| taskcard-dependency-matrix.csv | reports/machinery-assurance/vwm-analysis/taskcard-dependency-matrix.csv | TC-VWM-022 | Harden |
| file-ownership-and-locks.yaml | reports/machinery-assurance/vwm-analysis/file-ownership-and-locks.yaml | TC-VWM-022 | Harden |
| parallel-execution-safety-map.yaml | reports/machinery-assurance/vwm-analysis/parallel-execution-safety-map.yaml | TC-VWM-022 | Harden |
| taskcard-state-machine.yaml | reports/machinery-assurance/vwm-analysis/taskcard-state-machine.yaml | TC-VWM-022 | Harden |
| taskcard-state-machine-validation-rules.md | reports/machinery-assurance/vwm-analysis/taskcard-state-machine-validation-rules.md | TC-VWM-022 | Harden |
| output-class-inventory.yaml | reports/machinery-assurance/output-class-inventory.yaml | TC-VWM-018 | Output |
| quality-scores.yaml | reports/machinery-assurance/quality-scores.yaml | TC-VWM-019 | Quality |
| claim-reconciliation.yaml | reports/machinery-assurance/claim-reconciliation.yaml | TC-VWM-020 | Recon |
| gap-ledger.yaml | reports/machinery-assurance/gap-ledger.yaml | TC-VWM-021 | Gap Ledger |
| verification-matrix.md | reports/machinery-assurance/vwm-analysis/verification-matrix.md | TC-VWM-024 | Verify |
| validation-command-matrix.yaml | reports/machinery-assurance/vwm-analysis/validation-command-matrix.yaml | TC-VWM-024 | Verify |
| negative-control-matrix.yaml | reports/machinery-assurance/vwm-analysis/negative-control-matrix.yaml | TC-VWM-024 | Verify |
| output-healing-run.yaml | reports/machinery-assurance/output-healing-run.yaml | TC-VWM-025 | Output Heal |
| evidence-contract.md | reports/machinery-assurance/vwm-analysis/evidence-contract.md | TC-VWM-029 | Closure |
| evidence-obligation-matrix.csv | reports/machinery-assurance/vwm-analysis/evidence-obligation-matrix.csv | TC-VWM-029 | Closure |
| evidence-to-taskcard-traceability.csv | reports/machinery-assurance/vwm-analysis/evidence-to-taskcard-traceability.csv | TC-VWM-029 | Closure |
| plan-reconciliation-report.md | reports/machinery-assurance/vwm-analysis/plan-reconciliation-report.md | TC-VWM-029 | Closure |
| no-actionable-item-loss-audit.md | reports/machinery-assurance/vwm-analysis/no-actionable-item-loss-audit.md | TC-VWM-029 | Closure |
| taskcard-decomposition-quality-audit.md | reports/machinery-assurance/vwm-analysis/taskcard-decomposition-quality-audit.md | TC-VWM-029 | Closure |
| single-plan-authority-audit.md | reports/machinery-assurance/vwm-analysis/single-plan-authority-audit.md | TC-VWM-029 | Closure |
| idempotency-check.md | reports/machinery-assurance/vwm-analysis/idempotency-check.md | TC-VWM-029 | Closure |
| execution-readiness-verdict.md | reports/machinery-assurance/vwm-analysis/execution-readiness-verdict.md | TC-VWM-029 | Closure |
| final-report-vwm-2026-07-10.md | reports/machinery-assurance/final-report-vwm-2026-07-10.md | TC-VWM-029 | Closure |

---

## SECTION 8 — TASKCARD INDEX

| ID | Title | Phase | Req | Status |
|---|---|---|---|---|
| TC-VWM-001 | Bind Mission and Write Plan Lock | Bind | REQ-VWM-001..004 | PROPOSED |
| TC-VWM-002 | Discover Complete Machinery | Discover | REQ-VWM-005..009 | PROPOSED |
| TC-VWM-003 | Stage Review: Evidence Declaration | Stage Review | REQ-VWM-010 | PROPOSED |
| TC-VWM-004 | Stage Review: Declaration Inspection | Stage Review | REQ-VWM-011 | PROPOSED |
| TC-VWM-005 | Stage Review: Governance Validators | Stage Review | REQ-VWM-012 | PROPOSED |
| TC-VWM-006 | Stage Review: Work Item Grading | Stage Review | REQ-VWM-013 | PROPOSED |
| TC-VWM-007 | Stage Review: Sprint Planning | Stage Review | REQ-VWM-014 | PROPOSED |
| TC-VWM-008 | Stage Review: Continuation Checking | Stage Review | REQ-VWM-015 | PROPOSED |
| TC-VWM-009 | Stage Review: Plan Lock Management | Stage Review | REQ-VWM-016 | PROPOSED |
| TC-VWM-010 | Stage Review: Evidence Manifest | Stage Review | REQ-VWM-017 | PROPOSED |
| TC-VWM-011 | Stage Review: Gap Ledger | Stage Review | REQ-VWM-018 | PROPOSED |
| TC-VWM-012 | Stage Review: Anti-Skip & Stub Detection | Stage Review | REQ-VWM-019 | PROPOSED |
| TC-VWM-013 | Stage Review: Control Index | Stage Review | REQ-VWM-020 | PROPOSED |
| TC-VWM-014 | Stage Review: Skill Registry | Stage Review | REQ-VWM-021 | PROPOSED |
| TC-VWM-015 | Stage Review: Oracle Layer | Stage Review | REQ-VWM-022 | PROPOSED |
| TC-VWM-016 | Stage Review: Autonomous Loop Orchestration | Stage Review | REQ-VWM-023 | PROPOSED |
| TC-VWM-017 | Stage Review: Lifecycle Audit | Stage Review | REQ-VWM-024 | PROPOSED |
| TC-VWM-018 | Build Output-Class Inventory | Output Review | REQ-VWM-025 | PROPOSED |
| TC-VWM-019 | Score All Quality Dimensions | Quality | REQ-VWM-026 | PROPOSED |
| TC-VWM-020 | Claim-to-Evidence Reconciliation | Reconciliation | REQ-VWM-027 | PROPOSED |
| TC-VWM-021 | Build Canonical Gap Ledger | Gap Ledger | REQ-VWM-028 | PROPOSED |
| TC-VWM-022 | Harden the Plan | Hardening | REQ-VWM-029 | PROPOSED |
| TC-VWM-023 | Heal Machinery (per gap priorities) | Healing | REQ-VWM-030 | PROPOSED |
| TC-VWM-024 | Verify Healed Machinery | Verification | REQ-VWM-031 | PROPOSED |
| TC-VWM-025 | Regenerate and Heal Affected Outputs | Output Healing | REQ-VWM-032 | PROPOSED |
| TC-VWM-026 | Output Quality Revalidation | Revalidation | REQ-VWM-033 | PROPOSED |
| TC-VWM-027 | Run All Required Pilots (10+) | Pilots | REQ-VWM-034 | PROPOSED |
| TC-VWM-028 | Independent Final Review | Final Review | REQ-VWM-035 | PROPOSED |
| TC-VWM-029 | Idempotent Closure and Final Report | Closure | REQ-VWM-036..040 | PROPOSED |
| TC-VWM-030+ | (Reserved for hardening — added by TC-VWM-022) | Healing | TBD | DEFERRED |

---

## SECTION 9 — FULLY DECOMPOSED TASKCARDS

### Notation Key

```
[PARENT] status: PROPOSED|READY|IN_PROGRESS|CHILDREN_IN_PROGRESS|INTEGRATION_PENDING|VERIFIED|SCORED|CLOSED|BLOCKED|REROUTED
[CHILD]  status: TODO|READY|IN_PROGRESS|IMPLEMENTED|VERIFIED|SCORED|CLOSED|BLOCKED|REROUTED
[MS]     status: PENDING|READY|ACTIVE|COMPLETE|FAILED|BLOCKED|SKIPPED_NOT_APPLICABLE
```

---

## TC-VWM-001 [PARENT — PROPOSED]

**Title:** Bind Mission and Write Plan Lock
**Req:** REQ-VWM-001, REQ-VWM-002, REQ-VWM-003, REQ-VWM-004
**Phase:** Bind | **Priority:** P0 | **Owner:** Specialist Assurance Agent
**Deps:** None | **Successor:** TC-VWM-002

**Objective:** Establish the authoritative assurance session by writing the plan lock, recording all known state, and producing `assurance-mission.yaml` before any other work begins.

**Scope allowed:** `.local/supervisor/active-plan-lock.json` (write_plan_lock.py writes), `reports/machinery-assurance/assurance-mission.yaml`, `reports/machinery-assurance/vwm-analysis/*.md`
**Forbidden:** `src/python/`, `src/net/`, `tests/`, `tools/supervisor/`

**Children:** TC-VWM-001-01, TC-VWM-001-02, TC-VWM-001-03, TC-VWM-001-04, TC-VWM-001-05

**Parent acceptance:**
- All 5 children CLOSED
- Plan lock exists at `.local/supervisor/active-plan-lock.json` with `status: IN_PROGRESS` and `plan_path: plans/.claude/vast-wibbling-moon.md`
- `assurance-mission.yaml` written with all fields from Section 2
- All 7 known issues (I-001 through I-007) documented in assurance-mission.yaml
- `check_continuation.py` actual verdict recorded with evidence

**Rollback:** Delete `assurance-mission.yaml` and rerun write_plan_lock.py to reset
**Stop condition:** If write_plan_lock.py fails → escalate before proceeding

---

### TC-VWM-001-01 [CHILD — TODO]

**Parent:** TC-VWM-001 | **Req:** REQ-VWM-001
**Purpose:** Write the plan lock so this plan governs the current session and check_continuation.py cannot auto-continue prior plans.
**Files:** `.local/supervisor/active-plan-lock.json` (written by tool)
**Forbidden:** Any src/ or test/ files

**Micro-steps:**
- MS-VWM-001-01-01 [PENDING]: Action: Run `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/vast-wibbling-moon.md`. Target: `.local/supervisor/active-plan-lock.json`. Expected: File written with `status: IN_PROGRESS`, `plan_path: plans/.claude/vast-wibbling-moon.md`, `session_id: <current_session>`. Check: Read the lock file and confirm all 3 fields. Failure: If tool exits nonzero, record error and escalate before proceeding. Evidence: `.local/evidences/vwm-2026-07-10/plan-lock-write.log`

- MS-VWM-001-01-02 [PENDING]: Action: Read `.local/supervisor/active-plan-lock.json` and verify contents. Target: Plan lock file. Expected: `status == "IN_PROGRESS"`, `plan_path == "plans/.claude/vast-wibbling-moon.md"`. Check: File contents match expected. Failure: If status is not IN_PROGRESS, run write_plan_lock.py again. Evidence: Inline confirmation note.

**Evidence:** `.local/evidences/vwm-2026-07-10/tc-001-01-plan-lock.log`
**Accept:** Plan lock file exists with correct status and plan_path.
**Next:** TC-VWM-001-02

---

### TC-VWM-001-02 [CHILD — TODO]

**Parent:** TC-VWM-001 | **Req:** REQ-VWM-002
**Purpose:** Record the actual session state so the assurance mission has a verified baseline.
**Files (read-only):** `reports/supervisor/session-resume.md`, `reports/supervisor/approval-gates.md`, `.local/supervisor/continuation-signal.json`, `.local/supervisor/active-plan-lock.json`
**Forbidden:** Any writes except to evidence directory

**Micro-steps:**
- MS-VWM-001-02-01 [PENDING]: Action: Read `reports/supervisor/session-resume.md` fully. Expected: Last sprint name, test counts, autonomous continue flag. Check: Record: sprint=vast-weaving-lampson, tests=1169, continue=True. Evidence: Inline notes.

- MS-VWM-001-02-02 [PENDING]: Action: Read `reports/supervisor/approval-gates.md` fully. Expected: AUTONOMOUS_CONTINUE status, MODE, pending actions. Check: Record AUTONOMOUS_CONTINUE=YES, MODE=4. Evidence: Inline notes.

- MS-VWM-001-02-03 [PENDING]: Action: Read `.local/supervisor/continuation-signal.json` fully. Expected: Document stop_reason, rework_items, session_id, autonomous_continue, generated_at. Check: Confirm I-001 (stop_reason ≠ null with empty rework_items) and I-002 (session_id=null). Evidence: `.local/evidences/vwm-2026-07-10/tc-001-02-state-snapshot.json`

- MS-VWM-001-02-04 [PENDING]: Action: Run `python tools/supervisor/check_continuation.py`. Expected: JSON verdict with CONTINUE or STOP. Check: Record actual verdict, reason, and any blockers. Evidence: `.local/evidences/vwm-2026-07-10/tc-001-02-check-continuation.json`

**Accept:** All 4 files read, all values recorded in evidence.
**Next:** TC-VWM-001-03

---

### TC-VWM-001-03 [CHILD — TODO]

**Parent:** TC-VWM-001 | **Req:** REQ-VWM-003
**Purpose:** Carry forward all prior open gaps so they are not lost or rediscovered.
**Files (read-only):** `reports/machinery-assurance/gap-ledger.yaml`

**Micro-steps:**
- MS-VWM-001-03-01 [PENDING]: Action: Read `reports/machinery-assurance/gap-ledger.yaml` fully. Expected: Gap entries with status OPEN, ACCEPTED_RISK, DOCUMENTED. Check: List all gaps with their current status. Evidence: Inline list.

- MS-VWM-001-03-02 [PENDING]: Action: Identify gaps that are OPEN (not CLOSED): expected GAP-MA-001 (OPEN), GAP-MA-002 (ACCEPTED_RISK), GAP-MA-005 (ACCEPTED_RISK). Check: Confirm GAP-MA-006 is NOT in gap-ledger.yaml (it is only in MEMORY.md — this is I-004). Evidence: Inline note.

- MS-VWM-001-03-03 [PENDING]: Action: Write a running issue summary to `.local/evidences/vwm-2026-07-10/prior-gaps-carried-forward.yaml` listing each gap ID, status, and action required. Expected: YAML file with all prior gaps. Check: File exists and lists at minimum GAP-MA-001, GAP-MA-002, GAP-MA-005. Evidence: The file itself.

**Accept:** prior-gaps-carried-forward.yaml written with all prior gaps documented.
**Next:** TC-VWM-001-04

---

### TC-VWM-001-04 [CHILD — TODO]

**Parent:** TC-VWM-001 | **Req:** REQ-VWM-003
**Purpose:** Verify the Plan Agent's finding that governance validator count has drifted (I-005: MEMORY.md says 165 but runner may say 167).
**Files (read-only):** `tools/supervisor/governance_validator_runner.py` (search for expected_count only)

**Micro-steps:**
- MS-VWM-001-04-01 [PENDING]: Action: Read `tools/supervisor/governance_validator_runner.py` searching for the `expected_count` variable. Expected: Find the actual hardcoded count (165 or 167 or other). Check: Record the exact value and line number. Evidence: Inline note with file:line reference.

- MS-VWM-001-04-02 [PENDING]: Action: Document the finding as a confirmed or refuted issue. If actual count ≠ 165 → confirm I-005. If count = 165 → refute I-005. Check: I-005 status updated. Evidence: Inline note in assurance-mission.yaml (to be written in TC-VWM-001-05).

**Accept:** expected_count value confirmed from code, I-005 confirmed or refuted.
**Next:** TC-VWM-001-05

---

### TC-VWM-001-05 [CHILD — TODO]

**Parent:** TC-VWM-001 | **Req:** REQ-VWM-004
**Purpose:** Write the formal assurance-mission.yaml that becomes the authoritative binding record for this mission.
**Files (write):** `reports/machinery-assurance/assurance-mission.yaml`

**Micro-steps:**
- MS-VWM-001-05-01 [PENDING]: Action: Create directory `reports/machinery-assurance/vwm-analysis/` if it doesn't exist. Expected: Directory exists. Check: `ls reports/machinery-assurance/vwm-analysis/`. Evidence: Inline.

- MS-VWM-001-05-02 [PENDING]: Action: Write `reports/machinery-assurance/assurance-mission.yaml` using the template from Section 2 plus all collected evidence from TC-VWM-001-02 through -04. Include: all required fields, known_issues (I-001 through I-007 with I-005 confirmed/refuted), check_continuation verdict, prior gaps list. Expected: Valid YAML file with all fields. Check: Parse the YAML with `python -c "import yaml; yaml.safe_load(open('reports/machinery-assurance/assurance-mission.yaml'))"`. Evidence: The file itself.

- MS-VWM-001-05-03 [PENDING]: Action: Write `reports/machinery-assurance/vwm-analysis/active-plan-authority-verdict.md` with content confirming this plan is the sole authority. Expected: File declares `authoritative_plan: plans/.claude/vast-wibbling-moon.md` and `execution_authority: true` (this plan only). Evidence: The file itself.

**Accept:** assurance-mission.yaml parses as valid YAML, all required fields present, active-plan-authority-verdict.md written.
**Next:** TC-VWM-002 (after TC-VWM-001 integration check)

**TC-VWM-001 Integration check:** Read assurance-mission.yaml and verify all 7 known issues appear. Read plan lock and verify IN_PROGRESS. Then mark TC-VWM-001 CLOSED.

---

## TC-VWM-002 [PARENT — PROPOSED]

**Title:** Discover Complete Machinery
**Req:** REQ-VWM-005, REQ-VWM-006, REQ-VWM-007, REQ-VWM-008, REQ-VWM-009
**Phase:** Discover | **Priority:** P0 | **Owner:** Specialist Assurance Agent
**Deps:** TC-VWM-001 | **Successor:** TC-VWM-003 through TC-VWM-017 (parallel group)

**Objective:** Reconstruct the complete machinery workflow from REAL CODE — not documentation. Find all hidden paths, bypasses, legacy code, and alternate entry points. Produce machinery-stage-inventory.yaml.

**Scope allowed:** All read operations. Write only to `reports/machinery-assurance/machinery-stage-inventory.yaml` and `reports/machinery-assurance/vwm-analysis/`
**Forbidden:** Any src/, tests/ mutations

**Children:** TC-VWM-002-01, TC-VWM-002-02, TC-VWM-002-03, TC-VWM-002-04, TC-VWM-002-05, TC-VWM-002-06

**Parent acceptance:**
- All 6 children CLOSED
- machinery-stage-inventory.yaml written with ≥15 stage entries (S01-S15)
- UNINVENTORIED_MACHINERY_STAGES = 0
- UNCLASSIFIED_BYPASS_PATHS = 0
- All files in tools/supervisor/ classified by role

**Rollback:** Delete machinery-stage-inventory.yaml and re-run if incomplete

---

### TC-VWM-002-01 [CHILD — TODO]

**Parent:** TC-VWM-002 | **Req:** REQ-VWM-005
**Purpose:** Enumerate and classify every file in the machinery roots.

**Micro-steps:**
- MS-VWM-002-01-01 [PENDING]: Action: List all files in `tools/supervisor/` recursively. Expected: ≥242 files. Check: Count matches ≥242. Record total count. Evidence: `.local/evidences/vwm-2026-07-10/tc-002-01-file-list.txt`

- MS-VWM-002-01-02 [PENDING]: Action: Classify each file into one of: orchestration, validation, grading, evidence, state, AI-decision, gap-management, plan-management, control-index, legacy/deprecated, utility. Expected: Every file has exactly one classification. Check: No "unclassified" entries remain. Evidence: `.local/evidences/vwm-2026-07-10/tc-002-01-file-classification.yaml`

- MS-VWM-002-01-03 [PENDING]: Action: List all files in `tools/review/`, `tools/assurance/`, `tools/oracle/`, `.supervisor/`. Expected: All non-supervisor machinery files enumerated. Check: Each file classified. Evidence: Append to file-classification.yaml.

- MS-VWM-002-01-04 [PENDING]: Action: Identify any files dated significantly before the last sprint (vast-weaving-lampson, 2026-07-10) that write to output paths — potential stale producers. Expected: List of stale producer candidates. Check: List captured. Evidence: `.local/evidences/vwm-2026-07-10/tc-002-01-stale-producer-candidates.txt`

**Accept:** All files classified. file-classification.yaml written.
**Next:** TC-VWM-002-02

---

### TC-VWM-002-02 [CHILD — TODO]

**Parent:** TC-VWM-002 | **Req:** REQ-VWM-006
**Purpose:** Trace the complete import chain from the official entry points to understand all code executed per pipeline run.

**Micro-steps:**
- MS-VWM-002-02-01 [PENDING]: Action: Read `tools/supervisor/autonomous_cycle.py` first 200 lines. Map all `import` and `from X import Y` statements. Expected: List of directly imported modules. Check: Every module name recorded. Evidence: Notes captured inline.

- MS-VWM-002-02-02 [PENDING]: Action: For each directly imported module from MS-01, read its first 50 lines to find its imports. Expected: Second-level import map. Check: No module left unexamined. Evidence: `.local/evidences/vwm-2026-07-10/tc-002-02-import-chain.yaml`

- MS-VWM-002-02-03 [PENDING]: Action: Search for all `subprocess.run(` or `subprocess.Popen(` calls in tools/supervisor/ — these are alternate entry points (shell-out patterns). Expected: List of subprocess calls with their commands. Check: Every subprocess.run/Popen call found. Evidence: `.local/evidences/vwm-2026-07-10/tc-002-02-subprocess-calls.txt`

**Accept:** Import chain map and subprocess-call list written to evidence.
**Next:** TC-VWM-002-03

---

### TC-VWM-002-03 [CHILD — TODO]

**Parent:** TC-VWM-002 | **Req:** REQ-VWM-007
**Purpose:** Map all state write operations to identify who owns each state file.

**Micro-steps:**
- MS-VWM-002-03-01 [PENDING]: Action: Search all files in tools/supervisor/ for writes to `.local/supervisor/` paths using grep for pattern `\.local.supervisor`. Expected: List of (file, line, target_path) tuples. Check: Every write to .local/supervisor/ attributed to a file. Evidence: `.local/evidences/vwm-2026-07-10/tc-002-03-state-writes-local.txt`

- MS-VWM-002-03-02 [PENDING]: Action: Search all files in tools/supervisor/ for writes to `reports/supervisor/` paths. Expected: List of (file, line, target_path) tuples. Check: Every write to reports/supervisor/ attributed. Evidence: `.local/evidences/vwm-2026-07-10/tc-002-03-state-writes-reports.txt`

- MS-VWM-002-03-03 [PENDING]: Action: Identify any file that writes to BOTH `.local/supervisor/` AND `reports/supervisor/` — these are dual-state owners and higher risk for inconsistency. Expected: Short list of dual-state writers. Check: Each identified and noted in inventory. Evidence: Inline.

**Accept:** All state write operations mapped with file+line attribution.
**Next:** TC-VWM-002-04

---

### TC-VWM-002-04 [CHILD — TODO]

**Parent:** TC-VWM-002 | **Req:** REQ-VWM-008
**Purpose:** Find all bypass paths, emergency overrides, and legacy/deprecated code paths.

**Micro-steps:**
- MS-VWM-002-04-01 [PENDING]: Action: Search tools/supervisor/ for flags like `--skip`, `--force`, `--bypass`, `--override`, `--no-validate`. Expected: List of bypass flags with their files and effect. Check: Every flag captured. Evidence: `.local/evidences/vwm-2026-07-10/tc-002-04-bypass-flags.txt`

- MS-VWM-002-04-02 [PENDING]: Action: Search for `DEPRECATED`, `legacy`, `# TODO: remove`, `# old` comments in tools/supervisor/. Expected: List of deprecated paths. Check: All deprecated paths identified. Evidence: `.local/evidences/vwm-2026-07-10/tc-002-04-legacy-paths.txt`

- MS-VWM-002-04-03 [PENDING]: Action: Search for direct writes to `src/python/` or `src/net/` inside tools/supervisor/ (bypassing skill mediation). Expected: List of any such writes. Check: Any found = potential governance bypass → gap candidate. Evidence: `.local/evidences/vwm-2026-07-10/tc-002-04-src-direct-writes.txt`

- MS-VWM-002-04-04 [PENDING]: Action: Find producers-without-consumers: files in machinery that write outputs that are never imported or read by other machinery files. Search for unique output paths and verify each is consumed. Expected: Short list of orphan outputs. Check: Each confirmed as orphaned or as consumed. Evidence: `.local/evidences/vwm-2026-07-10/tc-002-04-orphan-outputs.txt`

**Accept:** All bypass flags, legacy paths, src-direct-writes, and orphan outputs documented.
**Next:** TC-VWM-002-05

---

### TC-VWM-002-05 [CHILD — TODO]

**Parent:** TC-VWM-002 | **Req:** REQ-VWM-007
**Purpose:** Map the dual-track continuation architecture (product/ vs machinery/ tracks) from real code, not documentation.

**Micro-steps:**
- MS-VWM-002-05-01 [PENDING]: Action: Read `tools/supervisor/continuation_selector.py` fully. Expected: Understand how product vs machinery track is selected. Check: Track selection logic documented. Evidence: Inline notes.

- MS-VWM-002-05-02 [PENDING]: Action: Check if `.local/supervisor/product/` and `.local/supervisor/machinery/` directories exist. Expected: One or both directories present with track-specific continuation files. Check: List directory contents for each. Evidence: `.local/evidences/vwm-2026-07-10/tc-002-05-dual-track.txt`

- MS-VWM-002-05-03 [PENDING]: Action: Map the full continuation signal lifecycle: who writes it, when, what fields, and how check_continuation.py reads it. Expected: State transition map for continuation signal. Check: Map captures all 7+ stop conditions referenced in CLAUDE.md. Evidence: `.local/evidences/vwm-2026-07-10/tc-002-05-continuation-lifecycle.yaml`

**Accept:** Dual-track architecture documented from real code. Continuation signal lifecycle mapped.
**Next:** TC-VWM-002-06

---

### TC-VWM-002-06 [CHILD — TODO]

**Parent:** TC-VWM-002 | **Req:** REQ-VWM-009
**Purpose:** Write the machinery-stage-inventory.yaml consolidating all findings.

**Micro-steps:**
- MS-VWM-002-06-01 [PENDING]: Action: Map findings from TC-VWM-002-01 through -05 to the 15 known stages (S01-S15 from Sections 3-17 of the stage reviews). For each stage, populate: stage_id, name, purpose, entry_points (from import chain), inputs, outputs (from state-writes), producers, consumers, state_read, state_written, bypass_paths, failure_modes. Expected: 15 stage entries minimum. Check: Every stage from S01 to S15 has an entry. Evidence: The file itself.

- MS-VWM-002-06-02 [PENDING]: Action: Add any stages discovered during TC-VWM-002-01 through -05 that were NOT in the original S01-S15 list. Expected: Additional stages if found. Check: If new stages found, add them and increment stage counter. Evidence: Inline note.

- MS-VWM-002-06-03 [PENDING]: Action: Write `reports/machinery-assurance/machinery-stage-inventory.yaml`. Expected: Valid YAML with ≥15 stage entries. Check: Parse with `python -c "import yaml; d=yaml.safe_load(open('reports/machinery-assurance/machinery-stage-inventory.yaml')); print(len(d['stages']))"` — expect ≥15. Verify UNINVENTORIED_MACHINERY_STAGES=0 and UNCLASSIFIED_BYPASS_PATHS=0. Evidence: The file itself + parse result.

- MS-VWM-002-06-04 [PENDING]: Action: Write `reports/machinery-assurance/vwm-analysis/complete-plan-read-confirmation.md` confirming all plan sections were read and analyzed. Evidence: The file itself.

**Accept:** machinery-stage-inventory.yaml written with ≥15 stages. UNINVENTORIED=0, UNCLASSIFIED_BYPASS=0.
**Next:** TC-VWM-003 through TC-VWM-017 (can run in parallel groups A and B per Section 5 DAG)

---

## STANDARD STAGE REVIEW TEMPLATE (TC-VWM-003 through TC-VWM-017)

All stage review taskcards use the same 4-child pattern. Stage-specific content is in each TC definition.

```
Child -01: Read and inspect all stage source files
  MS-01: Read file 1 fully (largest/most important first)
  MS-02: Read file 2 fully
  MS-03: Read file N fully (repeat per file list in TC)
  MS-04: Map the call flow through stage entry points
Child -02: Execute all checklist items with direct evidence
  MS-01: Execute each check (run command or inspect code for each [ ] item)
  MS-02: Record definitive Y/N answer and evidence for each check item
  MS-03: Identify any defect, unexpected behavior, or gap candidate
Child -03: Score quality and register gaps
  MS-01: Score 8 quality dimensions 1-5 for this stage
  MS-02: For any dimension < 4, write gap candidate record
  MS-03: If applicable, run negative path test (inject bad input, verify detection)
Child -04: Write stage_manual_review record
  MS-01: Append entry to reports/machinery-assurance/stage-reviews.yaml
  MS-02: Verify the YAML is valid (parse check)
  MS-03: Mark child -01, -02, -03 complete and advance to parent integration check
```

**Standard child acceptance criteria:**
- Child -01: All files in TC file list read. Call flow captured.
- Child -02: Every checklist item has a definitive Y/N answer from direct evidence (not assumptions).
- Child -03: All dimensions scored. Any gap candidates registered.
- Child -04: stage-reviews.yaml has valid entry for this stage.

**Standard parent acceptance:**
- All 4 children CLOSED
- stage-reviews.yaml has this stage's entry
- Any found defect has a corresponding gap candidate
- Quality scores ≥ 4/5 on all mandatory dimensions (or gap opened)

---

## TC-VWM-003 [PARENT — PROPOSED]

**Title:** Stage Review — Evidence Declaration Validation (S01)
**Req:** REQ-VWM-010 | **Stage ID:** S01-EVIDENCE-DECLARATION
**Phase:** Stage Review | **Priority:** P1 | **Owner:** Specialist Assurance Agent
**Deps:** TC-VWM-002 | **Parallel group:** A | **Successor:** TC-VWM-018 (after all stage reviews)

**Stage purpose:** Validate structure and completeness of evidence-declaration.yaml before it enters the supervisor pipeline. Must fail closed on schema errors.

**Files to read (child -01):**
1. `tools/supervisor/evidence_declaration.py` — full
2. `tools/supervisor/sprint_executor_validate.py` — full (focus on --repair mode)
3. `.local/evidences/vwl-20260710/evidence-declaration.yaml` — last real sprint declaration
4. `docs/automation/supervisor-worker-contract.md` — schema contract

**Checklist for child -02:**
- [ ] What schema fields are required vs optional? Does validation fail CLOSED on missing required fields?
- [ ] Does `--repair` correctly fix: markdown fences, type mismatches, banned fields?
- [ ] Is `provenance_chain` field enforced for PRODUCT_SOURCE items (Phase 12 in validator)?
- [ ] What is the failure mode when declared evidence paths don't exist on disk?
- [ ] Are evidence paths validated as relative or absolute? Both?
- [ ] Is WARN(TC-LA-005) for missing provenance_chain actually emitted or is it suppressed?
- [ ] Negative test: submit a minimal invalid declaration (missing `planned_work_items`); verify exit code > 0 and useful message.

**Children:** TC-VWM-003-01, TC-VWM-003-02, TC-VWM-003-03, TC-VWM-003-04

**Status:** PROPOSED

---

## TC-VWM-004 [PARENT — PROPOSED]

**Title:** Stage Review — Declaration Inspection & Materialization (S02)
**Req:** REQ-VWM-011 | **Stage ID:** S02-INSPECTION
**Phase:** Stage Review | **Priority:** P1 | **Deps:** TC-VWM-002 | **Parallel group:** A

**Stage purpose:** Walk declared evidence paths, verify files exist, and build evidence-manifest.yaml for the review package builder.

**Files to read (child -01):**
1. `tools/supervisor/inspect_declared_evidence.py` — full
2. `tools/supervisor/materialize_declared_evidence.py` — full

**Checklist for child -02:**
- [ ] Does inspection walk all declared evidence paths and report missing files (not silently skip)?
- [ ] Does materialization produce a correct evidence-manifest.yaml with all expected fields?
- [ ] Are symlinks or relative paths handled safely (no path traversal risk)?
- [ ] What happens with large evidence directories — is there a timeout or performance guard?
- [ ] Is there a retry if a file is being written concurrently?
- [ ] Negative test: declare an evidence path that doesn't exist; verify specific error message.

**Children:** TC-VWM-004-01, TC-VWM-004-02, TC-VWM-004-03, TC-VWM-004-04
**Status:** PROPOSED

---

## TC-VWM-005 [PARENT — PROPOSED]

**Title:** Stage Review — Governance Validation (S03 — 165+ validators)
**Req:** REQ-VWM-012 | **Stage ID:** S03-GOVERNANCE-VALIDATORS
**Phase:** Stage Review | **Priority:** P0 (highest risk) | **Deps:** TC-VWM-002 | **Parallel group:** B

**Stage purpose:** Run 165+ governance validators across product source to enforce architectural rules. Must fail closed, must report per-validator results.

**CRITICAL KNOWN ISSUE (I-005):** MEMORY.md claims 165 validators. Plan agent found `expected_count: 167` in runner (V149 added 2026-07-09). TC-VWM-001-04 will confirm the actual count. This TC must verify the count in code and resolve the discrepancy.

**Files to read (child -01):**
1. `tools/supervisor/governance_validator_runner.py` — full (find expected_count variable and runner loop)
2. `tools/supervisor/governance_validators.py` — count all `def validate_` functions
3. `tools/supervisor/governance_validators_ext.py` — count functions
4. `tools/supervisor/governance_validators_ext2.py` — count functions
5. `tools/supervisor/governance_validators_ext3.py` — count functions
6. `tools/supervisor/governance_validators_ext4.py` — count functions (V119/V120/V125/V126)
7. `tools/supervisor/governance_validators_contract.py` — how many registry validators added at runtime?
8. `tests/supervisor/test_governance_validators.py` — find expected_count assertion

**Execution (child -02):**
- Run: `python tools/supervisor/governance_validator_runner.py 2>&1 | tail -30`
- Count actual validators reported in output

**Checklist for child -02:**
- [ ] ACTUAL `expected_count` in runner code — exact value and line number
- [ ] Total `def validate_` function count across ALL validator files (manual count)
- [ ] How many validators from governance_validators_contract.py are added at runtime?
- [ ] V119/V120/V125/V126 API mismatch fix (TC-CQGA-FIX-001): search code for the fix — verify it's present
- [ ] V126 moved to per-file loop: verify this exists in current runner code
- [ ] GOV-WINDOW-FIX-001: V105/V106 windows 300→500/400→600: search for these constants in code (not just commit message)
- [ ] Are ALL validators from all files actually CALLED by the runner (grep for each file's validators in runner)?
- [ ] Exit codes: 0 = all pass, 3 = critical rework — verify in code
- [ ] `blocks_sprint` flag: is it consistently set per validator?
- [ ] Lazy import pattern: does each validator file use lazy imports inside function bodies?
- [ ] Bypass: is there a skip list, exemption flag, or emergency override in the runner?
- [ ] Negative test: introduce a deliberate LOC violation in a temp file; verify runner detects and reports it; restore file.

**Additional child -05 (unique to TC-VWM-005):**
- TC-VWM-005-05: Update MEMORY.md with confirmed validator count and update I-005 status in assurance-mission.yaml

**Children:** TC-VWM-005-01, TC-VWM-005-02, TC-VWM-005-03, TC-VWM-005-04, TC-VWM-005-05
**Status:** PROPOSED

---

### TC-VWM-005-05 [CHILD — TODO] (unique to TC-VWM-005)

**Parent:** TC-VWM-005 | **Req:** REQ-VWM-012
**Purpose:** Resolve the validator count discrepancy by updating MEMORY.md with the confirmed correct count.
**Precondition:** TC-VWM-005-02 (checklist verification) must be CLOSED with confirmed count.
**Files (write):** `C:\Users\prora\.claude\projects\c--Users-prora-OneDrive-Documents-GitHub-format-factory\memory\MEMORY.md`

**Micro-steps:**
- MS-VWM-005-05-01 [PENDING]: Action: Read MEMORY.md to find the line claiming "165 governance validators". Target: Line containing "165" or "expected_count". Expected: Line found. Check: Exact line number and content captured. Evidence: Inline.

- MS-VWM-005-05-02 [PENDING]: Action: Edit MEMORY.md to replace the stale count with the confirmed actual count (from TC-VWM-005-01 findings). Use surgical edit — change only the count number, preserve surrounding context. Expected: Count updated to confirmed value. Check: Re-read MEMORY.md and verify new count appears. Evidence: Inline confirmation.

- MS-VWM-005-05-03 [PENDING]: Action: Update assurance-mission.yaml `known_issues.I-005` to `RESOLVED` with the confirmed count and date. Expected: I-005 status updated. Check: Parse YAML and verify I-005 has status RESOLVED. Evidence: Inline.

**Accept:** MEMORY.md has correct validator count. I-005 marked RESOLVED.

---

## TC-VWM-006 [PARENT — PROPOSED]

**Title:** Stage Review — Work Item Grading (S04)
**Req:** REQ-VWM-013 | **Stage ID:** S04-GRADING
**Phase:** Stage Review | **Priority:** P1 | **Deps:** TC-VWM-002 | **Parallel group:** A

**Stage purpose:** Grade declared work items against a rubric to produce ACCEPTED/REWORK/REJECTED verdicts. Must prevent overclaiming.

**Files to read (child -01):**
1. `tools/supervisor/grade_declared_work.py` — full
2. `tools/supervisor/grade_to_quality_adapter.py` — full
3. `tools/supervisor/grade_intermediate_verify.py` — full
4. `reports/supervisor/work-item-grades.yaml` — last sprint output
5. `docs/automation/supervisor-grading-rubric.md` — criteria

**Checklist for child -02:**
- [ ] What grading classifications exist? Do they map to the 6-class audit taxonomy?
- [ ] Can a work item receive ACCEPTED with ZERO direct evidence (only self-report)?
- [ ] Is synthetic test evidence distinguished from real execution evidence?
- [ ] How is the LLM grader (`GPT_OSS_ENDPOINT`) used? Can it over-accept weak evidence?
- [ ] Can grading be bypassed by omitting work items from the declaration?
- [ ] What happens when evidence paths declared don't exist on disk?
- [ ] Negative test: declare a work item with no evidence paths; verify it is graded REWORK or REJECTED.

**Children:** TC-VWM-006-01, TC-VWM-006-02, TC-VWM-006-03, TC-VWM-006-04
**Status:** PROPOSED

---

## TC-VWM-007 [PARENT — PROPOSED]

**Title:** Stage Review — Sprint Planning & Next-Sprint Generation (S05)
**Req:** REQ-VWM-014 | **Stage ID:** S05-SPRINT-PLANNING
**Phase:** Stage Review | **Priority:** P1 | **Deps:** TC-VWM-002 | **Parallel group:** A

**Stage purpose:** Generate the next-sprint.md prompt and next-work-items.json from graded work, gap ledger, and AI planning. Must remain ADVISORY — must not claim gate authority.

**Files to read (child -01):**
1. `tools/supervisor/generate_next_worker_prompt.py` — full
2. `tools/supervisor/generate_next_work_items.py` — full
3. `tools/supervisor/ai_sprint_manager.py` — first 100 lines
4. `reports/supervisor/next-sprint.md` — last real output (inspect for ADVISORY ONLY label)
5. `.local/supervisor/next-work-items.json` — last structured output

**Checklist for child -02:**
- [ ] Are work items generated from REAL gap ledger entries (not fabricated by LLM)?
- [ ] Is "ADVISORY ONLY" correctly propagated to ALL output paths (md and json)?
- [ ] Does LLM grading create a circular dependency (grading influences next-sprint which influences grading)?
- [ ] Are task priorities correctly ordered (machinery gaps before product work)?
- [ ] Is output deterministic (same inputs → same next-sprint.md)?
- [ ] What happens when `selected-product-gaps.json` is missing?
- [ ] Negative test: remove selected-product-gaps.json; verify graceful fallback (not crash).

**Children:** TC-VWM-007-01, TC-VWM-007-02, TC-VWM-007-03, TC-VWM-007-04
**Status:** PROPOSED

---

## TC-VWM-008 [PARENT — PROPOSED]

**Title:** Stage Review — Continuation Checking & Session Identity (S06)
**Req:** REQ-VWM-015 | **Stage ID:** S06-CONTINUATION
**Phase:** Stage Review | **Priority:** P0 (controls the loop) | **Deps:** TC-VWM-002 | **Parallel group:** B

**Stage purpose:** Deterministically decide CONTINUE or STOP for the autonomous loop. Enforces non-overridable hard stops (POST_PLAN_TERMINAL, SESSION_MISMATCH, etc.).

**KNOWN ISSUES:**
- I-001: `stop_reason: "critical_rework_blocks_continuation"` with `rework_items: []` — contradictory
- I-002: `session_id: null` — CCI-MVP isolation not in effect
- Signal dated 2026-07-04 (stale)
- `global_repair_applied: true` present — what does this field do?

**Files to read (child -01) — read ALL fully:**
1. `tools/supervisor/check_continuation.py` — complete implementation
2. `tools/supervisor/continuation_identity.py` — session identity logic
3. `tools/supervisor/continuation_selector.py` — track selection
4. `tools/supervisor/stop_reason_adjudicator.py` — stop reason classification
5. `.local/supervisor/continuation-signal.json` — current state (already read in TC-VWM-001-02)

**Execution (child -02):**
- Run `python tools/supervisor/check_continuation.py` — capture full JSON stdout and exit code
- Run `python tools/supervisor/stop_reason_adjudicator.py "critical_rework_blocks_continuation"` if CLI supports string args; else read the function directly

**Checklist for child -02:**
- [ ] What is the ACTUAL exit code and verdict of check_continuation.py right now?
- [ ] Find the exact code path for: `stop_reason = "critical_rework_blocks_continuation"` with `rework_items = []` → does it CONTINUE or STOP? Why?
- [ ] What does `global_repair_applied: true` do? Find the code that reads this field.
- [ ] For `session_id: null` signals: does CCI-MVP allow or block consumption? Trace Check 2.
- [ ] POST_PLAN_TERMINAL (Check 1b): For vast-weaving-lampson lock (session 033f6a1ae2f3) with TERMINAL_CLOSED — does check_continuation correctly skip this because it belongs to a DIFFERENT session (not the current chat)?
- [ ] SESSION_MISMATCH: if session_id in signal ≠ current session, is it enforced or bypassable?
- [ ] MAX_ITERATIONS (iteration=0, max=12): confirmed not a stop condition?
- [ ] Are all 7+ CLAUDE.md-listed hard stop conditions actually implemented in code?
- [ ] Is there any code path where check_continuation.py exits 0 (CONTINUE) despite a hard stop condition being active?
- [ ] Negative test: manually set continuation-signal.json `autonomous_continue: false` and run check_continuation.py; verify STOP verdict. Restore file.

**Additional child -05 (unique to TC-VWM-008):**
- TC-VWM-008-05: Diagnose and propose fix for I-001 (stale/contradictory continuation signal)

**Children:** TC-VWM-008-01, TC-VWM-008-02, TC-VWM-008-03, TC-VWM-008-04, TC-VWM-008-05

---

### TC-VWM-008-05 [CHILD — TODO] (unique to TC-VWM-008)

**Parent:** TC-VWM-008 | **Req:** REQ-VWM-015
**Purpose:** Diagnose the root cause of I-001/I-002 in the continuation signal and record the exact fix needed.
**Precondition:** TC-VWM-008-02 CLOSED with root cause identified.

**Micro-steps:**
- MS-VWM-008-05-01 [PENDING]: Action: Based on TC-VWM-008-02 findings, document: WHICH code path produces the contradictory state (stop_reason non-null + empty rework_items). Target: Specific function in check_continuation.py or autonomous_cycle.py. Expected: Exact file:line where the state is written. Check: Reference is specific and from direct code reading. Evidence: `.local/evidences/vwm-2026-07-10/tc-008-05-root-cause.md`

- MS-VWM-008-05-02 [PENDING]: Action: Evaluate whether the fix is: (A) update the stale signal file directly, (B) fix the code that writes the signal, or (C) fix check_continuation.py to handle this state gracefully. Use solution options: Option A = minimal surgical (update JSON), Option B = structural (fix writer), Option C = defensive (fix reader). Expected: Recommendation with score. Check: Score recorded for all 3 options across key dimensions. Evidence: Inline in tc-008-05-root-cause.md.

- MS-VWM-008-05-03 [PENDING]: Action: Record the recommended fix as a GAP-VWM-001 entry candidate for TC-VWM-021 gap ledger. Include: category, severity, root_cause, permanent_solution, taskcard_ids referencing TC-VWM-023. Expected: Gap candidate recorded. Check: Gap candidate entry written. Evidence: `.local/evidences/vwm-2026-07-10/gap-candidates.yaml` (append).

**Accept:** Root cause documented. Fix option selected and scored. Gap candidate written for TC-VWM-021.

**Status:** PROPOSED

---

## TC-VWM-009 [PARENT — PROPOSED]

**Title:** Stage Review — Plan Lock Management (S07)
**Req:** REQ-VWM-016 | **Stage ID:** S07-PLAN-LOCK
**Phase:** Stage Review | **Priority:** P1 | **Deps:** TC-VWM-002 | **Parallel group:** A

**Stage purpose:** Manage plan lock lifecycle (IN_PROGRESS → COMPLETE | TERMINAL_CLOSED | ITERATION_REQUIRED | SUPERSEDED). Prevents cross-session contamination and spurious continuation.

**Files to read (child -01):**
1. `tools/supervisor/write_plan_lock.py` — full
2. `tools/supervisor/plan_lock_gc.py` — full
3. `.local/supervisor/active-plan-lock.json` — current state
4. List `.local/supervisor/plan-locks/` — identify all session-keyed locks
5. `docs/automation/terminal-closure-state-machine.md`

**Checklist for child -02:**
- [ ] State machine transitions: IN_PROGRESS → COMPLETE | TERMINAL_CLOSED | ITERATION_REQUIRED | SUPERSEDED — all implemented?
- [ ] Does GC correctly identify stale locks (>168 hours) and mark SUPERSEDED?
- [ ] Are test-artifact locks (AppData/Temp/pytest paths) caught by GC?
- [ ] Does `--terminal` correctly set TERMINAL_CLOSED (not COMPLETE)?
- [ ] Does `--complete` set COMPLETE (not TERMINAL_CLOSED)?
- [ ] How does `--audit-gate` interact with `--terminal`?
- [ ] Does SUPERSEDED allow check_continuation to proceed past an old lock?
- [ ] Can a test artifact lock create a false ACTIVE_PLAN_INCOMPLETE block?
- [ ] Is the `updated_at` date on vast-weaving-lampson lock within the 7-day stale window?
- [ ] ITERATION_REQUIRED: does check_continuation return CONTINUE (not STOP) when this is the lock status?
- [ ] Negative test: write a lock with `status: "IN_PROGRESS"` referencing a non-existent plan path; verify check_continuation handles correctly.

**Children:** TC-VWM-009-01, TC-VWM-009-02, TC-VWM-009-03, TC-VWM-009-04
**Status:** PROPOSED

---

## TC-VWM-010 [PARENT — PROPOSED]

**Title:** Stage Review — Evidence Manifest & Review Package (S08)
**Req:** REQ-VWM-017 | **Stage ID:** S08-REVIEW-PACKAGE
**Phase:** Stage Review | **Priority:** P1 | **Deps:** TC-VWM-002 | **Parallel group:** A

**Stage purpose:** Build evidence-manifest.yaml from declared paths and package everything into a deterministic ZIP with SHA-256.

**Files to read (child -01):**
1. `tools/supervisor/evidence_manifest.py` — full
2. `tools/supervisor/build_declaration_review_package.py` — full

**Execution (child -02):**
- `python -c "import zipfile; z=zipfile.ZipFile('.local/supervisor/reviews/vwl-20260710/declaration-review-package.zip'); print(len(z.namelist())); print(sorted(z.namelist())[:5])"` — verify entry count

**Checklist for child -02:**
- [ ] Is the ZIP archive deterministic (same content → same SHA-256)?
- [ ] Are all declared evidence paths verified before inclusion (not blindly zipped)?
- [ ] Is the SHA-256 printed as absolute Windows path in the output?
- [ ] Are stale entries from previous sprints excluded?
- [ ] Actual entry count vs 38 reported in session-resume.md?
- [ ] Can the review package be built without running a full supervisor cycle?
- [ ] Negative test: try to build a review package with a missing evidence directory; verify error message.

**Children:** TC-VWM-010-01, TC-VWM-010-02, TC-VWM-010-03, TC-VWM-010-04
**Status:** PROPOSED

---

## TC-VWM-011 [PARENT — PROPOSED]

**Title:** Stage Review — Gap Ledger & Work Item Selection (S09)
**Req:** REQ-VWM-018 | **Stage ID:** S09-GAP-LEDGER
**Phase:** Stage Review | **Priority:** P1 | **Deps:** TC-VWM-002 | **Parallel group:** A

**Stage purpose:** Maintain canonical gap ledger and convert open gaps into ranked work items for the next sprint.

**KNOWN ISSUE (I-004):** GAP-MA-006 appears in MEMORY.md but NOT in formal gap-ledger.yaml.

**Files to read (child -01):**
1. `tools/supervisor/gap_ledger_to_work_items.py` — full
2. `tools/supervisor/gap_ledger_hygiene.py` — full
3. `tools/supervisor/select_poc_gaps.py` — full
4. `reports/machinery-assurance/gap-ledger.yaml` — current gaps
5. `.local/supervisor/selected-product-gaps.json` — current selection

**Checklist for child -02:**
- [ ] GAP-MA-001 (site-packages sync): OPEN in gap-ledger.yaml — confirm still present
- [ ] GAP-MA-006 (concurrent writes / One-Mechanism Lock): NOT in gap-ledger.yaml — confirm MISSING
- [ ] Are machinery gaps separated from product gaps in work item selection?
- [ ] Does gap hygiene correctly identify and merge duplicate gaps?
- [ ] Are CLOSED gaps correctly excluded from work item generation?
- [ ] Is there a risk of gap IDs being reused or colliding?
- [ ] What is `related_capability_id` — product capability (thousands) or agent skill (120)?
- [ ] Negative test: manually add a gap entry with invalid status; verify hygiene detects and reports it.

**Children:** TC-VWM-011-01, TC-VWM-011-02, TC-VWM-011-03, TC-VWM-011-04
**Status:** PROPOSED

---

## TC-VWM-012 [PARENT — PROPOSED]

**Title:** Stage Review — Anti-Skip & Stub Detection (S10)
**Req:** REQ-VWM-019 | **Stage ID:** S10-ANTI-SKIP
**Phase:** Stage Review | **Priority:** P1 | **Deps:** TC-VWM-002 | **Parallel group:** A

**Stage purpose:** Prevent workers from skipping required work (anti-skip) and detect stubs/placeholders in product source (no-stub-scan).

**Files to read (child -01):**
1. `tools/supervisor/anti_skip_checker.py` — first 200 lines + key functions
2. `tools/review/no_stub_scan.py` — full (228 lines)
3. `tools/review/python_qname_reviewer.py` — first 100 lines

**Execution (child -02):**
- `python tools/review/no_stub_scan.py src/python --json 2>&1 | head -30`

**Checklist for child -02:**
- [ ] What triggers an anti-skip block — declared work items vs actual file changes?
- [ ] Can a worker bypass by declaring matching work items but doing nothing?
- [ ] All 11 forbidden terms enforced in no_stub_scan?
- [ ] All 8 allowlist patterns correctly applied? Any false positives on known-good patterns (ODF XML names, NamedTemporaryFile, etc.)?
- [ ] Does AST analysis correctly catch pass-only method bodies?
- [ ] Is `authority_only = True` correctly exempted from pass-only class check?
- [ ] Does python_qname_reviewer.py run standalone or is it wired into governance validators?
- [ ] Negative test: add `# TODO: fix this` to a temp Python file; run no_stub_scan; verify detection; delete temp file.

**Children:** TC-VWM-012-01, TC-VWM-012-02, TC-VWM-012-03, TC-VWM-012-04
**Status:** PROPOSED

---

## TC-VWM-013 [PARENT — PROPOSED]

**Title:** Stage Review — Control Index (S11)
**Req:** REQ-VWM-020 | **Stage ID:** S11-CONTROL-INDEX
**Phase:** Stage Review | **Priority:** P1 | **Deps:** TC-VWM-002 | **Parallel group:** A

**Stage purpose:** Provide an operational SQLite+FTS5 index over the machinery knowledge base (11K+ rows, 11 ingestors, 16 tables) for fast querying.

**Files to read (child -01):**
1. List `tools/supervisor/control_index/` — all files
2. `tools/supervisor/control_index/__main__.py` or main entry point
3. `docs/automation/operational-control-index.md`
4. `tests/supervisor/test_control_index_db.py` — first 80 lines
5. `tests/supervisor/test_control_index_sync.py` — first 80 lines

**Execution (child -02):**
- `python -m tools.supervisor.control_index status`
- `.venv/Scripts/pytest tests/supervisor/test_control_index_db.py tests/supervisor/test_control_index_sync.py -v 2>&1 | tail -20`

**Checklist for child -02:**
- [ ] Is the control index current (synced after vast-weaving-lampson sprint)?
- [ ] Are all 11 ingestors found in code and functional?
- [ ] Are all 16 tables present and populated?
- [ ] Does FTS5 full-text search return correct results for a known entity (e.g., "fods")?
- [ ] Is rebuild idempotent — second rebuild produces identical DB (hash-based skip)?
- [ ] Do 30/30 tests pass?
- [ ] Does `autonomous_cycle.py --sync-index` correctly call the sync?
- [ ] Negative test: delete one table manually; verify rebuild restores it.

**Children:** TC-VWM-013-01, TC-VWM-013-02, TC-VWM-013-03, TC-VWM-013-04
**Status:** PROPOSED

---

## TC-VWM-014 [PARENT — PROPOSED]

**Title:** Stage Review — Skill Registry & Skill-First Execution (S12)
**Req:** REQ-VWM-021 | **Stage ID:** S12-SKILLS
**Phase:** Stage Review | **Priority:** P1 | **Deps:** TC-VWM-002 | **Parallel group:** A

**Stage purpose:** Enforce that all product source changes go through registered skills with governed handoffs. Prevents ad-hoc edits.

**Files to read (child -01):**
1. `.supervisor/skill-registry.yaml` — first 200 lines (global controls + one skill example)
2. `tools/supervisor/skill_inventory.py` — full
3. `tools/supervisor/sync_skill_command_registry.py` — first 80 lines
4. `.supervisor/ad-hoc-execution-inventory.yaml` — current state
5. `.supervisor/skill-first-policy.md`

**Checklist for child -02:**
- [ ] Is `exact_path_scope_required: true` enforced (code vs config-only)?
- [ ] Is `product_code_ledger_required_before_source_edit: true` operative?
- [ ] Known skill gaps (capability_compiler, analytics separation) still open and documented?
- [ ] Does BLOCKED_SKILL_GAP workflow create taskcards correctly?
- [ ] Is analytics rotation SUSPENDED (2026-06-18) still enforced in registry?
- [ ] Is `source_edits_require_explicit_handoff: true` blocking ad-hoc src/ edits?
- [ ] Are all command bindings in registry pointing to existing CLI commands?
- [ ] Negative test: attempt to invoke a skill for which no registry entry exists; verify BLOCKED_SKILL_GAP response.

**Children:** TC-VWM-014-01, TC-VWM-014-02, TC-VWM-014-03, TC-VWM-014-04
**Status:** PROPOSED

---

## TC-VWM-015 [PARENT — PROPOSED]

**Title:** Stage Review — Oracle Layer (S13)
**Req:** REQ-VWM-022 | **Stage ID:** S13-ORACLE
**Phase:** Stage Review | **Priority:** P1 | **Deps:** TC-VWM-002 | **Parallel group:** B

**Stage purpose:** Execute oracle cases for each format and verify products meet spec contracts. Depth levels D0-D3 (load → properties → RelaxNG → external tool).

**Files to read (child -01):**
1. `tools/oracle/execute_oracle.py` — first 150 lines + last 50 lines
2. `tools/supervisor/governance_validators_oracle.py` — V143 validate_oracle_depth_minimum()
3. Verify `oracle/schemas/odf-1.3-relaxng/OpenDocument-v1.3-schema.rng` exists

**Execution (child -02):**
- `.venv/Scripts/python tools/oracle/execute_oracle.py --help 2>&1`
- `.venv/Scripts/python tools/oracle/execute_oracle.py fods 2>&1 | tail -20`
- List `oracle/` directory

**Checklist for child -02:**
- [ ] Are all 20 Python FOSS formats at VERIFIED (73/73 PASS)? Run oracle for 3 spot checks: fods, csv, zst.
- [ ] V143 `validate_oracle_depth_minimum()`: fires WARN (not FAIL) for D0-only formats?
- [ ] `make_verdict()` depth_level parameter: does every verdict dict have `depth_level` key?
- [ ] `loaded` property: computed as `result_val is not None` (synthetic, not a returned field)?
- [ ] D2 for FODS with RelaxNG: correctly returns SKIPPED_MISSING_PROVIDER when lxml unavailable?
- [ ] ZST oracle: uses `.venv/Scripts/python` (not system Python) to access zstandard package?
- [ ] ODF schema at `oracle/schemas/odf-1.3-relaxng/OpenDocument-v1.3-schema.rng` — file size >500KB?
- [ ] Negative test: oracle fods with an intentionally malformed FODS file; verify FAIL (not crash).

**Children:** TC-VWM-015-01, TC-VWM-015-02, TC-VWM-015-03, TC-VWM-015-04
**Status:** PROPOSED

---

## TC-VWM-016 [PARENT — PROPOSED]

**Title:** Stage Review — Autonomous Loop Orchestration (S14)
**Req:** REQ-VWM-023 | **Stage ID:** S14-ORCHESTRATION
**Phase:** Stage Review | **Priority:** P1 | **Deps:** TC-VWM-002 | **Parallel group:** B

**Stage purpose:** Orchestrate the complete evidence pipeline: validate → inspect → grade → plan → manifest. Enforce One-Mechanism Lock, best-effort closeout, and checkpoint policy.

**Files to read (child -01):**
1. `tools/supervisor/autonomous_cycle.py` — first 200 lines + main() function
2. `tools/supervisor/sprint_executor.py` — run-loop subcommand handling
3. `tools/supervisor/supervisor_loop.py` — first 80 lines
4. `.supervisor/policies.yaml` lines 231-300 (autonomous_continuation section)

**Checklist for child -02:**
- [ ] What is the exact step sequence in autonomous_cycle.py? (validate → inspect → grade → plan-next → manifest?)
- [ ] One-Mechanism Lock: is there code preventing sprint_executor run-loop and Claude CLI from running simultaneously?
- [ ] Does anti-skip checker run BEFORE inspection in the cycle (not after)?
- [ ] Exit codes: 0 (all pass), 3 (critical rework), 9 (error) — all implemented?
- [ ] Best-effort closeout: does a step-2 failure (inspection) allow step-5+ (manifest) to still run?
- [ ] Does `--sync-index` flag exist and run non-blockingly?
- [ ] Checkpoint mechanism: every 3 iterations OR max 75 dirty files OR max 12 src files — implemented in code?
- [ ] Negative test: pass an invalid declaration path to autonomous_cycle.py; verify exit 1 (not 0) with helpful message.

**Children:** TC-VWM-016-01, TC-VWM-016-02, TC-VWM-016-03, TC-VWM-016-04
**Status:** PROPOSED

---

## TC-VWM-017 [PARENT — PROPOSED]

**Title:** Stage Review — Lifecycle Audit (S15)
**Req:** REQ-VWM-024 | **Stage ID:** S15-LIFECYCLE-AUDIT
**Phase:** Stage Review | **Priority:** P1 | **Deps:** TC-VWM-002 | **Parallel group:** B

**Stage purpose:** Audit machinery_hardening plans at closure to verify all taskcards are CLOSED before allowing --terminal flag. Prevents premature plan closure.

**KNOWN QUIRK (from MEMORY.md):** `parse_plan_taskcards()` requires exactly 2-column table format (`| TC-ID | Status |`). Code-block Status: fields are NOT parsed. Multi-column tables are skipped → ITERATION_REQUIRED incorrect.

**Files to read (child -01):**
1. `tools/supervisor/lifecycle_audit.py` — full, focusing on `parse_plan_taskcards()`
2. `.local/supervisor/lifecycle-audit-results.json` — last audit results

**Checklist for child -02:**
- [ ] Confirm `parse_plan_taskcards()` REQUIRES exactly 2-column table (`| TC-ID | Status |`)
- [ ] Are code-block `Status:` fields (e.g., `**Status:** OPEN`) parsed? Expected: NO.
- [ ] Are multi-column tables (e.g., 4-column taskcard index) parsed? Expected: SKIPPED.
- [ ] What happens when a plan has NO 2-column table at all? Expected: audit fails or returns ITERATION_REQUIRED?
- [ ] Does this plan file (vast-wibbling-moon) have the correct 2-column table at the bottom?
- [ ] Does `--audit-gate` flag on write_plan_lock.py correctly invoke lifecycle_audit and pass `--mission-id` and `--sprint-id`?
- [ ] Is ITERATION_REQUIRED written to active-plan-lock.json when audit finds open taskcards?
- [ ] Negative test: pass a plan file with no 2-column table to lifecycle_audit.py; verify ITERATION_REQUIRED (not error).

**Critical action:** If the 2-column table in this plan lacks child taskcard IDs, the lifecycle audit cannot verify children are closed. The Taskcard Status Summary Table at the end of this plan must list both parent AND child TC IDs.

**Children:** TC-VWM-017-01, TC-VWM-017-02, TC-VWM-017-03, TC-VWM-017-04
**Status:** PROPOSED

---

## TC-VWM-018 [PARENT — PROPOSED]

**Title:** Build Output-Class Inventory and Review All Classes
**Req:** REQ-VWM-025
**Phase:** Output Review | **Priority:** P1 | **Owner:** Specialist Assurance Agent
**Deps:** TC-VWM-003 through TC-VWM-017 (all stage reviews) | **Successor:** TC-VWM-019 + TC-VWM-020

**Objective:** Produce output-class-inventory.yaml covering all 18 identified output classes. Manually inspect representative samples from each class.

**Children:** TC-VWM-018-01, TC-VWM-018-02, TC-VWM-018-03, TC-VWM-018-04, TC-VWM-018-05

**Parent acceptance:**
- All 5 children CLOSED
- output-class-inventory.yaml has exactly 18 entries (OC-01 through OC-18)
- Every entry has: producer, authoritative_source, expected_structure, freshness_rules, consumer, mutation_policy, failure_impact, acceptance_criteria
- UNREVIEWED_OUTPUT_CLASSES = 0

---

### TC-VWM-018-01 [CHILD — TODO]

**Purpose:** Manually inspect the 5 highest-risk output classes (OC-01 evidence declarations, OC-03 supervisor reports, OC-06 gap ledger, OC-07 plan locks, OC-16 continuation signal).

**Micro-steps:**
- MS-VWM-018-01-01 [PENDING]: Action: Read `.local/evidences/vwl-20260710/evidence-declaration.yaml` (OC-01). Expected: Valid schema, all required fields present. Check: List schema fields found; compare against supervisor-worker-contract.md. Evidence: Notes.

- MS-VWM-018-01-02 [PENDING]: Action: Read `reports/supervisor/session-resume.md` (OC-03). Expected: All required sections (Quick State, What Was Done, What To Do Next, Project Memory). Check: All 5 sections present. Evidence: Notes.

- MS-VWM-018-01-03 [PENDING]: Action: Read `reports/machinery-assurance/gap-ledger.yaml` (OC-06). Expected: All entries have gap_id, semantic_key, status, root_cause, exact_next_action. Check: GAP-MA-006 missing (known). Record discrepancy. Evidence: Notes.

- MS-VWM-018-01-04 [PENDING]: Action: Read `.local/supervisor/active-plan-lock.json` (OC-07). Expected: current_session plan is vast-wibbling-moon with IN_PROGRESS. Check: Match. Evidence: Notes.

- MS-VWM-018-01-05 [PENDING]: Action: Inspect OC-16 continuation signal — already captured in TC-VWM-001-02. Reference that evidence. Check: I-001 and I-002 confirmed from prior read. Evidence: Reference to tc-001-02-state-snapshot.json.

**Accept:** All 5 high-risk classes inspected with findings documented.

---

### TC-VWM-018-02 [CHILD — TODO]

**Purpose:** Review remaining output classes OC-02, OC-04, OC-05, OC-08, OC-09, OC-10.

**Micro-steps:**
- MS-VWM-018-02-01 [PENDING]: Action: Check that `.local/supervisor/reviews/vwl-20260710/declaration-review-package.zip` exists and has ≥38 entries (OC-04). Run: `python -c "import zipfile; z=zipfile.ZipFile('.local/supervisor/reviews/vwl-20260710/declaration-review-package.zip'); print(len(z.namelist()))"`. Check: count ≥ 38. Evidence: Count result.

- MS-VWM-018-02-02 [PENDING]: Action: Check `.local/supervisor/next-work-items.json` exists and has valid structure (OC-05). Run: `python -c "import json; d=json.load(open('.local/supervisor/next-work-items.json')); print(type(d), len(d) if isinstance(d, list) else 'dict')"`. Expected: list or dict with work items. Check: Parseable JSON. Evidence: Inline.

- MS-VWM-018-02-03 [PENDING]: Action: Spot-check OC-09 (Python product source). List `src/python/fods/` and read one file (e.g., `src/python/fods/parser.py` first 30 lines). Expected: Proper Python source, no stubs, spec_qname present. Check: No forbidden terms, proper structure. Evidence: Notes.

- MS-VWM-018-02-04 [PENDING]: Action: Spot-check OC-10 (.NET product source). List `src/net/fods/` and read first 30 lines of one .cs file. Expected: Proper C# source. Check: Source exists and has content. Evidence: Notes.

**Accept:** All 6 output classes inspected with findings captured.

---

### TC-VWM-018-03 [CHILD — TODO]

**Purpose:** Review output classes OC-11 through OC-14 (tests, oracle packages, registry, control index).

**Micro-steps:**
- MS-VWM-018-03-01 [PENDING]: Action: Check OC-11 (tests). List `tests/` top-level dirs. Count test files in one format (e.g., `tests/fods/`). Expected: Tests exist and appear complete. Evidence: Notes.

- MS-VWM-018-03-02 [PENDING]: Action: Check OC-12 (oracle packages). List `oracle/` and verify ≥20 format directories. Expected: All 20 active formats have oracle packages. Evidence: Notes.

- MS-VWM-018-03-03 [PENDING]: Action: Check OC-13 (registry). Read first 20 lines of `registry/format-registry.yaml`. Expected: Valid YAML, formats array present. Evidence: Notes.

- MS-VWM-018-03-04 [PENDING]: Action: Check OC-14 (control index). Run `python -m tools.supervisor.control_index status`. Expected: synced, 11K+ rows. Evidence: Status output captured.

**Accept:** All 4 output classes inspected.

---

### TC-VWM-018-04 [CHILD — TODO]

**Purpose:** Review output classes OC-15 through OC-18 (consumer proofs, skill registry, project memory).

**Micro-steps:**
- MS-VWM-018-04-01 [PENDING]: Action: List `.local/evidences/consumer-proof-*.txt` files (OC-15). Expected: ≥20 files (one per active format). Check: Count and verify at least fods, csv, zst present. Evidence: File list.

- MS-VWM-018-04-02 [PENDING]: Action: Read first 100 lines of `.supervisor/skill-registry.yaml` (OC-17). Expected: valid YAML with global controls and skill entries. Check: `exact_path_scope_required: true` present. Evidence: Notes.

- MS-VWM-018-04-03 [PENDING]: Action: Check `.supervisor/project-memory.md` exists (OC-18). Note file size in KB. Expected: File exists with significant content (~500KB+). Check: File size > 100KB. Evidence: Notes.

**Accept:** OC-15 through OC-18 inspected.

---

### TC-VWM-018-05 [CHILD — TODO]

**Purpose:** Write output-class-inventory.yaml with all 18 classes.

**Micro-steps:**
- MS-VWM-018-05-01 [PENDING]: Action: Write `reports/machinery-assurance/output-class-inventory.yaml` with all 18 OC entries using findings from children -01 through -04. Each entry must have: oc_id, class_name, producer, authoritative_source, expected_structure, freshness_rules, consumer, mutation_policy, failure_impact, acceptance_criteria, review_status, anomalies_found. Expected: Valid YAML with 18 entries. Check: Parse check + count. Evidence: The file itself.

- MS-VWM-018-05-02 [PENDING]: Action: Verify UNREVIEWED_OUTPUT_CLASSES = 0 by confirming every OC-01 through OC-18 has `review_status: REVIEWED`. Check: Count REVIEWED entries. Evidence: Inline.

**Accept:** output-class-inventory.yaml written, 18 entries, all REVIEWED.

---

## TC-VWM-019 [PARENT — PROPOSED]

**Title:** Score All Quality Dimensions
**Req:** REQ-VWM-026
**Phase:** Quality | **Priority:** P1
**Deps:** TC-VWM-018 | **Successor:** TC-VWM-021 (after TC-VWM-020)

**Objective:** Score every applicable stage (S01-S15) and output class (OC-01 to OC-18) against all 8 quality dimension groups. Flag any score < 4.

**Children:** TC-VWM-019-01, TC-VWM-019-02, TC-VWM-019-03

---

### TC-VWM-019-01 [CHILD — TODO]

**Purpose:** Score all 15 stages (S01-S15) across all 8 quality dimensions.

**Micro-steps:**
- MS-VWM-019-01-01 [PENDING]: Action: Create score sheet with rows=stages (S01-S15), columns=8 dimensions. For each cell, use evidence from TC-VWM-003 through TC-VWM-017 stage reviews. Score 1-5. Expected: 15×8=120 scores. Check: No cell is TBD. Evidence: `.local/evidences/vwm-2026-07-10/tc-019-01-stage-scores.yaml`

- MS-VWM-019-01-02 [PENDING]: Action: For every score < 4, create a gap candidate entry in `.local/evidences/vwm-2026-07-10/gap-candidates.yaml`. Record: stage_id, dimension, score, specific_weakness, proposed_fix. Expected: All sub-4 scores have gap candidates. Check: Count gap candidates ≥ count of sub-4 scores. Evidence: gap-candidates.yaml updated.

**Scoring dimensions:**
1. Functional quality (correctness, completeness, spec fidelity, negative behavior, boundary handling)
2. Data/artifact quality (structure, consistency, freshness, provenance, determinism, traceability)
3. Integration quality (producer-consumer, schema compat, state consistency, downstream consumption)
4. Engineering quality (maintainability, modularity, readability, duplication, extensibility)
5. Operational quality (reliability, retries, timeout, concurrency, observability, recovery, idempotency)
6. Safety/governance (path controls, authority boundaries, gate enforcement, bypass resistance)
7. Performance/scalability (latency, throughput, disk, DB contention, portfolio-scale)
8. User/consumer quality (usability, discoverability, clarity, actionable errors)

**Accept:** 120 scores written. All sub-4 scores have gap candidates.

---

### TC-VWM-019-02 [CHILD — TODO]

**Purpose:** Score all 18 output classes (OC-01 to OC-18) across applicable quality dimensions.

**Micro-steps:**
- MS-VWM-019-02-01 [PENDING]: Action: Score each OC against applicable dimensions (not all 8 apply to all OCs). Use output-class-inventory.yaml findings. Expected: ≥80 scores (not all dimensions apply to all OCs). Check: Every OC has ≥4 dimension scores. Evidence: `.local/evidences/vwm-2026-07-10/tc-019-02-output-scores.yaml`

- MS-VWM-019-02-02 [PENDING]: Action: For every OC score < 4, add gap candidate. Expected: All sub-4 OC scores have gap candidates. Evidence: gap-candidates.yaml updated.

**Accept:** All OC scores written. Sub-4 scores have gap candidates.

---

### TC-VWM-019-03 [CHILD — TODO]

**Purpose:** Write quality-scores.yaml consolidating all stage and output scores.

**Micro-steps:**
- MS-VWM-019-03-01 [PENDING]: Action: Write `reports/machinery-assurance/quality-scores.yaml` combining stage scores (from -01) and output class scores (from -02). Include summary statistics: worst_dimension, worst_stage, worst_output_class, count_sub4. Expected: Valid YAML file. Check: Parse check. Evidence: The file itself.

**Accept:** quality-scores.yaml written and parseable.

---

## TC-VWM-020 [PARENT — PROPOSED]

**Title:** Claim-to-Evidence Reconciliation
**Req:** REQ-VWM-027
**Phase:** Reconciliation | **Priority:** P1
**Deps:** TC-VWM-018 | **Successor:** TC-VWM-021

**Objective:** Verify every major claim in plans, reports, MEMORY.md against DIRECT evidence (not summaries). Assign disposition to each.

**Children:** TC-VWM-020-01, TC-VWM-020-02, TC-VWM-020-03

---

### TC-VWM-020-01 [CHILD — TODO]

**Purpose:** Verify claims CL-001 through CL-007 (test count, validator count, oracle status, plan lock, GOV-WINDOW-FIX, PQLM closure, GAP-MA-001).

**Micro-steps (one per claim):**
- MS-VWM-020-01-01 [PENDING]: CL-001 (1169 tests): Run `.venv/Scripts/pytest --co -q 2>&1 | tail -5`. Record actual count. Disposition: VERIFIED if count ≥ 1169, else CONTRADICTED.

- MS-VWM-020-01-02 [PENDING]: CL-002 (165 validators): Use TC-VWM-001-04 finding. Disposition: VERIFIED if runner code says 165, STALE if 167+.

- MS-VWM-020-01-03 [PENDING]: CL-003 (oracle 73/73 PASS): Run `.venv/Scripts/python tools/oracle/execute_oracle.py fods csv zst 2>&1 | grep -E 'PASS|FAIL'`. Disposition: VERIFIED if spot checks pass.

- MS-VWM-020-01-04 [PENDING]: CL-004 (TERMINAL_CLOSED for vwl): Read active-plan-lock.json. Already verified in TC-VWM-001-01. Disposition: VERIFIED.

- MS-VWM-020-01-05 [PENDING]: CL-005 (GOV-WINDOW-FIX-001): Search governance_validators.py for the values 300, 500, 400, 600 in the V105/V106 detection window context. Disposition: VERIFIED if new values (500/600) found, CONTRADICTED if old values (300/400) still present.

- MS-VWM-020-01-06 [PENDING]: CL-006 (PQLM taskcards CLOSED): Read `plans/.claude/vast-weaving-lampson.md` and find TC-PQLM-026 through TC-PQLM-029 statuses. Disposition: VERIFIED if all 4 show CLOSED in the plan file.

- MS-VWM-020-01-07 [PENDING]: CL-007 (GAP-MA-001 OPEN): Direct read of gap-ledger.yaml (done in TC-VWM-018-01). Disposition: VERIFIED.

**Evidence:** `.local/evidences/vwm-2026-07-10/tc-020-01-claims.yaml`
**Accept:** All 7 claims dispositioned.

---

### TC-VWM-020-02 [CHILD — TODO]

**Purpose:** Verify claims CL-008 through CL-013 (GAP-MA-006 missing, QName coverage, control index tests, bundle validation, continuation contradictions, lifecycle audit format).

**Micro-steps (one per claim):**
- MS-VWM-020-02-01 [PENDING]: CL-008 (GAP-MA-006 not in gap-ledger.yaml): Confirmed in TC-VWM-018-01. Disposition: CONTRADICTED — MEMORY.md claims it is documented but gap-ledger.yaml lacks it.

- MS-VWM-020-02-02 [PENDING]: CL-009 (QName coverage 99.4%): Search for QName coverage report in reports/ or run `python tools/supervisor/governance_validator_runner.py 2>&1 | grep -i qname`. Disposition: VERIFIED if recent report found, STALE if no recent evidence.

- MS-VWM-020-02-03 [PENDING]: CL-010 (control index 30/30 tests): Run `.venv/Scripts/pytest tests/supervisor/test_control_index_db.py tests/supervisor/test_control_index_sync.py -v 2>&1 | tail -5`. Disposition: VERIFIED if 30 passed 0 failed.

- MS-VWM-020-02-04 [PENDING]: CL-011 (bundle 38 entries): Use TC-VWM-010 findings. Disposition: VERIFIED or STALE.

- MS-VWM-020-02-05 [PENDING]: CL-012 (continuation contradictions): Confirmed I-001 from TC-VWM-001-02. Disposition: CONTRADICTED — stop_reason non-null with empty rework_items.

- MS-VWM-020-02-06 [PENDING]: CL-013 (lifecycle_audit 2-column table): From TC-VWM-017-02 checklist. Disposition: VERIFIED if code confirms this requirement.

**Evidence:** `.local/evidences/vwm-2026-07-10/tc-020-02-claims.yaml`
**Accept:** All 6 claims dispositioned.

---

### TC-VWM-020-03 [CHILD — TODO]

**Purpose:** Write claim-reconciliation.yaml with all 13 claims and their dispositions.

**Micro-steps:**
- MS-VWM-020-03-01 [PENDING]: Action: Write `reports/machinery-assurance/claim-reconciliation.yaml` combining TC-VWM-020-01 and -02 findings. Each entry: claim_id, source, claim, claimed_status, direct_evidence, disposition, action_required. Expected: 13 entries, all with dispositions. Check: Parse check + no "TBD" dispositions. Evidence: The file itself.

**Accept:** claim-reconciliation.yaml written, all 13 claims dispositioned.

---

## TC-VWM-021 [PARENT — PROPOSED]

**Title:** Build Canonical Gap Ledger
**Req:** REQ-VWM-028
**Phase:** Gap Ledger | **Priority:** P1
**Deps:** TC-VWM-019, TC-VWM-020 | **Successor:** TC-VWM-022

**Objective:** Update reports/machinery-assurance/gap-ledger.yaml to be the canonical, complete gap record for this mission. Carry forward all prior open gaps, add all new gaps from discovery and stage reviews.

**Children:** TC-VWM-021-01, TC-VWM-021-02, TC-VWM-021-03, TC-VWM-021-04

---

### TC-VWM-021-01 [CHILD — TODO]

**Purpose:** Collect all gap candidates from stage reviews and quality scoring.

**Micro-steps:**
- MS-VWM-021-01-01 [PENDING]: Action: Read `.local/evidences/vwm-2026-07-10/gap-candidates.yaml` (collected during TC-VWM-008-05, -011, -019-01, -019-02). Expected: All gap candidates from stage reviews and quality scores. Check: At minimum GAP-VWM-001 (continuation signal), GAP-VWM-002 (session_id null), GAP-VWM-003 (validator count). Evidence: Inline.

- MS-VWM-021-01-02 [PENDING]: Action: For each gap candidate, evaluate: is this a new gap or does it match an existing gap in gap-ledger.yaml? Mark duplicates. Expected: Deduplicated gap list. Check: DUPLICATE_ACTIVE_GAPS = 0. Evidence: gap-dedup.txt.

**Accept:** All gap candidates collected and deduplicated.

---

### TC-VWM-021-02 [CHILD — TODO]

**Purpose:** Evaluate solution options for the top-3 gaps (GAP-VWM-001, GAP-MA-001, GAP-VWM-003).

**Micro-steps:**
- MS-VWM-021-02-01 [PENDING]: Action: For GAP-VWM-001 (continuation signal inconsistency) — evaluate: Option A (update JSON file directly), Option B (fix the writer code that produces contradictory state), Option C (fix the reader to handle this state). Score each on: root-cause coverage (1-5), production durability (1-5), testability (1-5). Expected: Selected option with rationale. Evidence: `.local/evidences/vwm-2026-07-10/tc-021-02-gap-vwm-001-options.yaml`

- MS-VWM-021-02-02 [PENDING]: Action: For GAP-MA-001 (site-packages sync no enforcement) — evaluate: Option A (add governance validator for sync check), Option B (add pre-execution script check), Option C (document as accepted risk). Score each. Expected: Selected option. Evidence: `.local/evidences/vwm-2026-07-10/tc-021-02-gap-ma-001-options.yaml`

- MS-VWM-021-02-03 [PENDING]: Action: For GAP-VWM-003 (MEMORY.md stale count) — this is a simple correction already handled by TC-VWM-005-05. Mark as SIMPLE_CORRECTION, no options analysis needed. Evidence: Inline.

**Accept:** Solution options scored for GAP-VWM-001 and GAP-MA-001. Selected solutions documented.

---

### TC-VWM-021-03 [CHILD — TODO]

**Purpose:** Formally register GAP-MA-006 in gap-ledger.yaml (it was only in MEMORY.md).

**Micro-steps:**
- MS-VWM-021-03-01 [PENDING]: Action: Read MEMORY.md entry for GAP-MA-006 to understand the full description. Expected: Description of concurrent background writes violating One-Mechanism Lock. Evidence: Inline.

- MS-VWM-021-03-02 [PENDING]: Action: Prepare GAP-MA-006 entry in canonical gap schema format with: gap_id, semantic_key, category=GOVERNANCE_BYPASS, severity=MEDIUM, symptom, evidence=[MEMORY.md reference], root_cause, blast_radius, current_risk, permanent_solution, status=OPEN, exact_next_action. Expected: Complete gap entry. Evidence: `.local/evidences/vwm-2026-07-10/gap-ma-006-entry.yaml`

**Accept:** GAP-MA-006 formally prepared for inclusion in gap-ledger.yaml.

---

### TC-VWM-021-04 [CHILD — TODO]

**Purpose:** Write updated gap-ledger.yaml with all prior gaps carried forward plus all new gaps.

**Micro-steps:**
- MS-VWM-021-04-01 [PENDING]: Action: Read current `reports/machinery-assurance/gap-ledger.yaml`. Note which prior gaps exist. Expected: GAP-MA-001 through GAP-MA-005 (some CLOSED, some OPEN). Evidence: Prior entries captured.

- MS-VWM-021-04-02 [PENDING]: Action: Write updated `reports/machinery-assurance/gap-ledger.yaml` including: all prior gaps (preserved), GAP-MA-006 (new from TC-VWM-021-03), GAP-VWM-001 (continuation signal), GAP-VWM-002 (session_id null), GAP-VWM-003 (validator count — if not already fixed), and any additional gaps from quality scoring. Expected: Valid YAML. Check: MATERIAL_FINDINGS_WITHOUT_GAPS = 0, DUPLICATE_ACTIVE_GAPS = 0, GAPS_WITHOUT_ROOT_CAUSE_OR_NEXT_ACTION = 0. Evidence: The file itself.

- MS-VWM-021-04-03 [PENDING]: Action: Verify every gap in gap-ledger.yaml has: gap_id, status, root_cause, exact_next_action, taskcard_ids. Check: Parse all entries. Evidence: Parse result.

**Accept:** gap-ledger.yaml updated. All 3 counters = 0.

---

## TC-VWM-022 [PARENT — PROPOSED]

**Title:** Harden the Plan
**Req:** REQ-VWM-029
**Phase:** Hardening | **Priority:** P1
**Deps:** TC-VWM-021 | **Successor:** TC-VWM-023

**Objective:** Map every OPEN/ACTIVE gap to a bounded taskcard. Create TC-VWM-030+ for gaps that don't already have taskcards. Update this plan's index and status table.

**Children:** TC-VWM-022-01, TC-VWM-022-02, TC-VWM-022-03

---

### TC-VWM-022-01 [CHILD — TODO]

**Purpose:** Map all gaps to existing or new taskcards.

**Micro-steps:**
- MS-VWM-022-01-01 [PENDING]: Action: For each OPEN/ACTIVE gap in gap-ledger.yaml, check if a taskcard already references it (search TC-VWM-023 and TC-VWM-025 sections). If yes: add gap_id to taskcard's gap_ids field. If no: create TC-VWM-030+ entry for it. Expected: Every gap has ≥1 taskcard_id. Check: ACTIONABLE_GAPS_WITHOUT_TASKCARDS = 0. Evidence: `.local/evidences/vwm-2026-07-10/tc-022-01-gap-to-taskcard-map.yaml`

- MS-VWM-022-01-02 [PENDING]: Action: At minimum create TC-VWM-030 (Fix continuation signal inconsistency — GAP-VWM-001), TC-VWM-031 (Add site-packages sync enforcement — GAP-MA-001), TC-VWM-032 (Formalize One-Mechanism Lock gap — GAP-MA-006). Write these as taskcard entries in this plan file (add them after TC-VWM-029). Expected: TC-VWM-030, -031, -032 defined. Check: Taskcards exist in plan. Evidence: Updated plan file.

**Accept:** All gaps mapped to taskcards.

---

### TC-VWM-022-02 [CHILD — TODO]

**Purpose:** Write the 45 supporting analysis artifacts (traceability maps, DAG, state machine) to reports/machinery-assurance/vwm-analysis/.

**Micro-steps:**
- MS-VWM-022-02-01 [PENDING]: Action: Write `reports/machinery-assurance/vwm-analysis/execution-dag.yaml` representing the DAG from Section 5 as structured YAML. Include: nodes (taskcard_ids), edges (dependency pairs), parallel_groups, file_ownership_locks. Expected: Valid YAML. Check: Parse check. Evidence: The file.

- MS-VWM-022-02-02 [PENDING]: Action: Write `reports/machinery-assurance/vwm-analysis/taskcard-dependency-matrix.csv` as a 29×29 binary matrix (1=depends on, 0=independent). Expected: 29 rows, 29 columns. Check: CSV parseable with 29 rows. Evidence: The file.

- MS-VWM-022-02-03 [PENDING]: Action: Write `reports/machinery-assurance/vwm-analysis/normalized-requirements-inventory.yaml` from the Requirements Registry in Section 3. Expected: 40 entries, each with req_id, requirement, maps_to. Check: 40 entries. Evidence: The file.

- MS-VWM-022-02-04 [PENDING]: Action: Write `reports/machinery-assurance/vwm-analysis/file-ownership-and-locks.yaml` documenting which taskcard owns each machinery file during execution (to prevent concurrent modification). Expected: At minimum 10 ownership entries. Check: Every file in Section 5 parallel-safe groups has an entry. Evidence: The file.

**Accept:** Key supporting artifacts written. Parse checks pass.

---

### TC-VWM-022-03 [CHILD — TODO]

**Purpose:** Update this plan file's Taskcard Status Summary Table to include all parent + child + TC-VWM-030+ IDs.

**Micro-steps:**
- MS-VWM-022-03-01 [PENDING]: Action: Generate the complete TC-ID list: TC-VWM-001 through TC-VWM-029 (parents) + TC-VWM-001-01 through TC-VWM-029-05 (children) + TC-VWM-030+ (healing taskcards). Expected: Complete list with statuses. Check: No taskcard is missing from the list. Evidence: The updated Taskcard Status Summary Table at the bottom of this plan.

- MS-VWM-022-03-02 [PENDING]: Action: Edit this plan file's Taskcard Status Summary Table to add all children and new taskcards. Keep 2-column format required by lifecycle_audit.py. Expected: Table has all TC-IDs. Check: lifecycle_audit.py will parse all entries when run. Evidence: Updated plan file section.

**Accept:** Taskcard Status Summary Table updated with all IDs.

---

## TC-VWM-023 [PARENT — PROPOSED]

**Title:** Heal Machinery (per gap priorities)
**Req:** REQ-VWM-030
**Phase:** Healing | **Priority:** P1
**Deps:** TC-VWM-022 | **Successor:** TC-VWM-024

**Objective:** For each OPEN/ACTIVE machinery gap (in priority order): reproduce defect → find root cause → repair machinery → add regression tests → verify focused behavior.

**Constraint:** Do NOT manually patch output files while the producer is defective.
**Constraint:** Machinery-repair taskcards must complete before output-backfill taskcards.

**Children:** TC-VWM-023-01, TC-VWM-023-02, TC-VWM-023-03, TC-VWM-023-04

**Note:** TC-VWM-030, TC-VWM-031, TC-VWM-032 (created in TC-VWM-022) are the actual implementation taskcards for each gap. TC-VWM-023 is the ORCHESTRATOR that sequences them and verifies completion.

---

### TC-VWM-023-01 [CHILD — TODO]

**Purpose:** Execute GAP-VWM-001 fix (continuation signal inconsistency) via TC-VWM-030.

**Micro-steps:**
- MS-VWM-023-01-01 [PENDING]: Action: Confirm TC-VWM-030 exists with gap_ids=[GAP-VWM-001], allowed_paths, and acceptance_criteria. Expected: TC-VWM-030 is defined in plan. Check: TC-VWM-030 present in taskcard index. Evidence: Plan file.

- MS-VWM-023-01-02 [PENDING]: Action: Execute TC-VWM-030 (which implements the selected solution from TC-VWM-021-02: Option A/B/C for fixing continuation signal). Record before/after state of `.local/supervisor/continuation-signal.json`. Expected: Signal file has consistent stop_reason/rework_items after fix. Evidence: `.local/evidences/vwm-2026-07-10/tc-023-01-before.json` + `tc-023-01-after.json`.

- MS-VWM-023-01-03 [PENDING]: Action: Run regression test: `python tools/supervisor/check_continuation.py` — verify verdict is CONTINUE with correct reasoning. Check: No spurious STOP. Evidence: `tc-023-01-regression.log`.

**Accept:** GAP-VWM-001 fix applied and verified.

---

### TC-VWM-023-02 [CHILD — TODO]

**Purpose:** Execute GAP-MA-001 fix (site-packages sync enforcement) via TC-VWM-031.

**Micro-steps:**
- MS-VWM-023-02-01 [PENDING]: Action: Confirm TC-VWM-031 exists with gap_ids=[GAP-MA-001] and the selected enforcement mechanism. Expected: TC-VWM-031 defined. Check: Present in plan. Evidence: Plan file.

- MS-VWM-023-02-02 [PENDING]: Action: Execute TC-VWM-031 (implement automated site-packages sync check). Record what was added (validator/script/check). Evidence: `.local/evidences/vwm-2026-07-10/tc-023-02-site-packages-fix.log`.

- MS-VWM-023-02-03 [PENDING]: Action: Test: modify `src/python/fods/` then verify the new enforcement mechanism detects the sync gap. Restore. Evidence: `tc-023-02-enforcement-test.log`.

**Accept:** GAP-MA-001 enforcement mechanism implemented and tested.

---

### TC-VWM-023-03 [CHILD — TODO]

**Purpose:** Execute GAP-VWM-003 fix (MEMORY.md stale validator count) — should already be done by TC-VWM-005-05.

**Micro-steps:**
- MS-VWM-023-03-01 [PENDING]: Action: Verify TC-VWM-005-05 is CLOSED (MEMORY.md update was done). Check: Read MEMORY.md line claiming validator count — confirm it matches actual expected_count from runner. Evidence: Inline comparison.

- MS-VWM-023-03-02 [PENDING]: Action: If TC-VWM-005-05 is NOT yet closed, execute it now as part of healing. Otherwise mark this micro-step SKIPPED_NOT_APPLICABLE with reason. Evidence: Inline.

**Accept:** MEMORY.md validator count matches actual code.

---

### TC-VWM-023-04 [CHILD — TODO]

**Purpose:** Execute any additional TC-VWM-030+ taskcards created during TC-VWM-022 for gaps found in stage reviews.

**Micro-steps:**
- MS-VWM-023-04-01 [PENDING]: Action: List all TC-VWM-033+ taskcards created during hardening. For each, verify it has: gap_ids, objective, allowed_paths, acceptance_criteria. Expected: All TC-VWM-033+ are properly specified. Check: No taskcard is underspecified. Evidence: Inline list.

- MS-VWM-023-04-02 [PENDING]: Action: Execute each TC-VWM-033+ in dependency order. Record which gaps were healed. Evidence: `.local/evidences/vwm-2026-07-10/tc-023-04-additional-repairs.log`.

**Accept:** All additional gap repairs executed and documented.

---

## TC-VWM-024 [PARENT — PROPOSED]

**Title:** Verify Healed Machinery
**Req:** REQ-VWM-031
**Phase:** Verification | **Priority:** P1
**Deps:** TC-VWM-023 | **Successor:** TC-VWM-025

**Objective:** Run comprehensive verification of all healed machinery components against their proof-level targets. Do not proceed to output regeneration until all proof levels are met.

**Children:** TC-VWM-024-01, TC-VWM-024-02, TC-VWM-024-03, TC-VWM-024-04

---

### TC-VWM-024-01 [CHILD — TODO]

**Purpose:** Verify governance validators and continuation checking (highest-risk components).

**Micro-steps:**
- MS-VWM-024-01-01 [PENDING]: Action: Run `python tools/supervisor/governance_validator_runner.py 2>&1 | tail -30`. Expected: actual_count == expected_count (confirmed value), 0 FAIL results. Check: Both conditions. Evidence: `.local/evidences/vwm-2026-07-10/tc-024-01-governance-runners.log`

- MS-VWM-024-01-02 [PENDING]: Action: Run `python tools/supervisor/check_continuation.py`. Expected: CONTINUE verdict (after GAP-VWM-001 fix). Check: verdict==CONTINUE. Evidence: `tc-024-01-check-continuation.json`

- MS-VWM-024-01-03 [PENDING]: Action: Run `python tools/supervisor/plan_lock_gc.py --dry-run`. Expected: vast-weaving-lampson lock (last updated 2026-07-10) may or may not be stale (check date); new vast-wibbling-moon lock shows IN_PROGRESS. Check: GC behavior is correct. Evidence: `tc-024-01-plan-lock-gc.log`

**Accept:** Governance validators pass. Continuation checker returns CONTINUE. Plan lock GC behaves correctly.

---

### TC-VWM-024-02 [CHILD — TODO]

**Purpose:** Run full test suite and stub scan.

**Micro-steps:**
- MS-VWM-024-02-01 [PENDING]: Action: Run `.venv/Scripts/pytest --tb=short -q 2>&1 | tail -5`. Expected: ≥1169 passed, 0 failed. Check: Both conditions met. Evidence: `.local/evidences/vwm-2026-07-10/tc-024-02-pytest.log`

- MS-VWM-024-02-02 [PENDING]: Action: Run `python tools/review/no_stub_scan.py src/python --json`. Expected: `{"status": "CLEAN", "total_violations": 0}`. Check: CLEAN status. Evidence: `tc-024-02-no-stub-scan.json`

**Accept:** ≥1169 tests pass, 0 stubs found.

---

### TC-VWM-024-03 [CHILD — TODO]

**Purpose:** Run oracle spot checks and control index verification.

**Micro-steps:**
- MS-VWM-024-03-01 [PENDING]: Action: Run `.venv/Scripts/python tools/oracle/execute_oracle.py fods 2>&1 | tail -10`. Expected: All FODS cases PASS. Evidence: `tc-024-03-oracle-fods.log`

- MS-VWM-024-03-02 [PENDING]: Action: Run `.venv/Scripts/python tools/oracle/execute_oracle.py csv 2>&1 | tail -10`. Expected: All CSV cases PASS. Evidence: `tc-024-03-oracle-csv.log`

- MS-VWM-024-03-03 [PENDING]: Action: Run `.venv/Scripts/python tools/oracle/execute_oracle.py zst 2>&1 | tail -10`. Expected: All ZST cases PASS (requires .venv Python for zstandard). Evidence: `tc-024-03-oracle-zst.log`

- MS-VWM-024-03-04 [PENDING]: Action: Run `python -m tools.supervisor.control_index status`. Expected: synced, 11K+ rows. Evidence: `tc-024-03-control-index.log`

**Accept:** Oracle 3 spot checks all PASS. Control index synced.

---

### TC-VWM-024-04 [CHILD — TODO]

**Purpose:** Run supervisor-specific tests and verify proof levels.

**Micro-steps:**
- MS-VWM-024-04-01 [PENDING]: Action: Run `.venv/Scripts/pytest tests/supervisor/ -v --tb=short 2>&1 | tail -40`. Expected: All supervisor tests pass (including plan lock, continuation, control index). Evidence: `tc-024-04-supervisor-tests.log`

- MS-VWM-024-04-02 [PENDING]: Action: Record proof levels achieved vs targets (from the proof level table in original TC-VWM-024). For each stage, mark ACHIEVED or NOT_ACHIEVED. Expected: All mandatory targets met. Check: E2E_VERIFIED for evidence declaration, governance validators, continuation; INTEGRATION_VERIFIED for plan lock, gap ledger, oracle; FOCUSED_VERIFIED for anti-skip. Evidence: `tc-024-04-proof-levels.yaml`

**Accept:** All mandatory proof levels achieved. Supervisor tests pass.

---

## TC-VWM-025 [PARENT — PROPOSED]

**Title:** Regenerate and Heal Affected Outputs
**Req:** REQ-VWM-032
**Phase:** Output Healing | **Priority:** P1
**Deps:** TC-VWM-024 | **Successor:** TC-VWM-026

**Objective:** For each output class affected by healed machinery: regenerate through official entry points, compare before/after, verify consumer.

**Children:** TC-VWM-025-01, TC-VWM-025-02, TC-VWM-025-03

---

### TC-VWM-025-01 [CHILD — TODO]

**Purpose:** Identify which output classes are affected by healed machinery.

**Micro-steps:**
- MS-VWM-025-01-01 [PENDING]: Action: For each healed gap (GAP-VWM-001, GAP-MA-001, GAP-VWM-003, any TC-VWM-030+), determine which output class(es) the fix affected. Map: GAP-VWM-001 fix → OC-16 (continuation signal), OC-03 (supervisor reports); GAP-MA-001 fix → OC-09 (Python source, if sync gap); GAP-VWM-003 → OC-18 (MEMORY.md). Expected: List of (gap_id, affected_oc_ids). Check: Every healed gap maps to at least one OC. Evidence: `tc-025-01-affected-outputs.yaml`

- MS-VWM-025-01-02 [PENDING]: Action: Capture current "before" snapshot of each affected output for comparison. Save each file's hash or first 20 lines. Evidence: `tc-025-01-before-snapshots.yaml`

**Accept:** Affected outputs identified. Before snapshots captured.

---

### TC-VWM-025-02 [CHILD — TODO]

**Purpose:** Regenerate all affected outputs through official entry points ONLY.

**Micro-steps:**
- MS-VWM-025-02-01 [PENDING]: Action: For OC-16 (continuation signal), if healed by GAP-VWM-001 fix, the updated file already IS the regenerated output. Verify it's consistent. No additional regeneration needed. Evidence: Current continuation-signal.json verified.

- MS-VWM-025-02-02 [PENDING]: Action: For OC-18 (MEMORY.md), if updated by TC-VWM-005-05 (validator count fix), it is already regenerated. Verify count is correct. Evidence: MEMORY.md read, count confirmed.

- MS-VWM-025-02-03 [PENDING]: Action: Run `python tools/supervisor/gap_ledger_hygiene.py` to ensure gap-ledger.yaml is canonically regenerated (OC-06). Expected: Clean output, no duplicates. Evidence: `tc-025-02-gap-ledger-hygiene.log`

- MS-VWM-025-02-04 [PENDING]: Action: Run `python -m tools.supervisor.control_index sync` to ensure control index reflects healed state (OC-14). Expected: sync completes without error. Evidence: `tc-025-02-control-index-sync.log`

**Accept:** All affected outputs regenerated or confirmed current.

---

### TC-VWM-025-03 [CHILD — TODO]

**Purpose:** Compare before/after and write output-healing-run.yaml.

**Micro-steps:**
- MS-VWM-025-03-01 [PENDING]: Action: For each affected OC, compare current state vs before snapshot. Record: what changed, what stayed the same, any anomalies. Expected: Before/after comparison complete. Evidence: `tc-025-03-before-after-diff.yaml`

- MS-VWM-025-03-02 [PENDING]: Action: Write `reports/machinery-assurance/output-healing-run.yaml` with: run_id, repaired_machinery_revision, affected_outputs, regenerated_outputs, preserved_outputs, failed_outputs, anomalies, consumer_checks, verdict. Expected: Valid YAML. Check: AFFECTED_OUTPUTS_NOT_REGENERATED_OR_DISPOSITIONED = 0. Evidence: The file itself.

**Accept:** output-healing-run.yaml written. All affected outputs accounted for.

---

## TC-VWM-026 [PARENT — PROPOSED]

**Title:** Output Quality Revalidation
**Req:** REQ-VWM-033
**Phase:** Revalidation | **Priority:** P1
**Deps:** TC-VWM-025 | **Successor:** TC-VWM-027

**Objective:** Re-validate output quality after regeneration. Re-score any quality dimension that was < 4. Verify downstream consumers.

**Children:** TC-VWM-026-01, TC-VWM-026-02, TC-VWM-026-03

---

### TC-VWM-026-01 [CHILD — TODO]

**Purpose:** Re-run all automated quality checks.

**Micro-steps:**
- MS-VWM-026-01-01 [PENDING]: Action: Run `python tools/review/no_stub_scan.py src/python --json`. Expected: CLEAN. Evidence: `tc-026-01-no-stub-scan.json`

- MS-VWM-026-01-02 [PENDING]: Action: Run `python tools/supervisor/governance_validator_runner.py 2>&1 | tail -20`. Expected: All pass, 0 FAIL. Evidence: `tc-026-01-governance.log`

- MS-VWM-026-01-03 [PENDING]: Action: Run `.venv/Scripts/pytest --tb=short -q 2>&1 | tail -5`. Expected: ≥1169 passed, 0 failed. Evidence: `tc-026-01-pytest.log`

**Accept:** All 3 automated checks pass.

---

### TC-VWM-026-02 [CHILD — TODO]

**Purpose:** Manual review of anomalies and downstream consumer verification.

**Micro-steps:**
- MS-VWM-026-02-01 [PENDING]: Action: Review any anomalies recorded in output-healing-run.yaml. For each anomaly, inspect the actual output and determine if it is acceptable or a defect. Expected: All anomalies dispositioned. Evidence: `tc-026-02-anomaly-review.yaml`

- MS-VWM-026-02-02 [PENDING]: Action: Verify downstream consumers. Import one installed Python format package from .venv: `python -c "from fods.parser import parse_fods; print('fods OK')"`. Expected: Import succeeds. Evidence: `tc-026-02-consumer-check.log`

**Accept:** Anomalies reviewed. Consumer import verified.

---

### TC-VWM-026-03 [CHILD — TODO]

**Purpose:** Re-score quality dimensions that previously scored < 4.

**Micro-steps:**
- MS-VWM-026-03-01 [PENDING]: Action: Read quality-scores.yaml. Find all entries with score < 4. Re-score each based on healed state. Expected: All previously sub-4 scores now ≥ 4 OR a new gap opened for any that remain < 4. Check: OUTPUTS_WITH_UNRESOLVED_QUALITY_DEFECTS = 0. STALE_OUTPUTS_FROM_DEFECTIVE_MACHINERY = 0. Evidence: `tc-026-03-rescored.yaml`

**Accept:** All quality scores ≥ 4 or new gaps opened. Both counters = 0.

---

## TC-VWM-027 [PARENT — PROPOSED]

**Title:** Run All Required Pilots (10+)
**Req:** REQ-VWM-034
**Phase:** Pilots | **Priority:** P1
**Deps:** TC-VWM-026 | **Successor:** TC-VWM-028

**Objective:** Execute all 10 required pilots. Each pilot must produce evidence. FAILED_REQUIRED_PILOTS = 0.

**Evidence root:** `.local/evidences/vwm-pilots/`

**Children:** TC-VWM-027-01 through TC-VWM-027-05 (grouped pilots)

---

### TC-VWM-027-01 [CHILD — TODO]

**Pilots 1-2 (Normal and Complex paths)**

**Micro-steps:**
- MS-VWM-027-01-01 [PENDING]: **Pilot 1 — Simple normal path.** Action: Write a minimal valid evidence-declaration.yaml to `.local/evidences/vwm-pilot-p1/evidence-declaration.yaml` with 1 work item and valid evidence paths. Run `python tools/supervisor/autonomous_cycle.py --declaration .local/evidences/vwm-pilot-p1/evidence-declaration.yaml`. Expected: exit 0, next-sprint.md updated, continuation signal updated. Check: Exit code = 0. Evidence: `vwm-pilots/pilot-01-simple.log`

- MS-VWM-027-01-02 [PENDING]: **Pilot 2 — Complex/high-risk input.** Action: Run `python tools/supervisor/governance_validator_runner.py 2>&1 | grep -E 'PASS|FAIL|WARN' | head -20`. Verify governance validators report correct results for actual current repo state. Expected: All validators report correctly (no false negatives). Check: Output count matches expected_count. Evidence: `vwm-pilots/pilot-02-complex.log`

**Accept:** Pilots 1-2 PASS with evidence.

---

### TC-VWM-027-02 [CHILD — TODO]

**Pilots 3-4 (Negative and State-Interruption)**

**Micro-steps:**
- MS-VWM-027-02-01 [PENDING]: **Pilot 3 — Invalid/negative input.** Action: Create a malformed evidence-declaration.yaml (missing required `planned_work_items` key). Run `python tools/supervisor/sprint_executor_validate.py <malformed_path>`. Expected: Non-zero exit, useful error message, no partial state written. Check: Exit ≠ 0. Error message mentions missing field. `.local/supervisor/` state unchanged. Evidence: `vwm-pilots/pilot-03-negative.log`

- MS-VWM-027-02-02 [PENDING]: **Pilot 4 — State interruption.** Action: (a) Read current continuation-signal.json. (b) Write a corrupted version (e.g., invalid JSON or truncated file) to simulate crash. (c) Run `python tools/supervisor/check_continuation.py`. Expected: Graceful handling — either STOP with clear error or safe fallback. (d) Restore original continuation-signal.json. Check: check_continuation.py does not crash (exits 0 or 1, not exception). State is restored. Evidence: `vwm-pilots/pilot-04-interrupt.log`

**Accept:** Pilots 3-4 PASS. State restored after Pilot 4.

---

### TC-VWM-027-03 [CHILD — TODO]

**Pilots 5-6 (Regression and Output Regeneration)**

**Micro-steps:**
- MS-VWM-027-03-01 [PENDING]: **Pilot 5 — Machinery regression.** Action: (a) Create a temp Python file `src/python/fods/_vwm_pilot5_temp.py` with content containing "# TODO: temporary stub". (b) Run `python tools/review/no_stub_scan.py src/python/fods/_vwm_pilot5_temp.py --json`. Expected: violation detected. (c) Delete the temp file. (d) Verify no_stub_scan returns CLEAN after deletion. Check: Detection confirmed, file restored. Evidence: `vwm-pilots/pilot-05-regression.log`

- MS-VWM-027-03-02 [PENDING]: **Pilot 6 — Output regeneration.** Action: Read current `reports/supervisor/next-sprint.md` header (first 5 lines). Run `python tools/supervisor/generate_next_worker_prompt.py` if it can be run standalone (else use autonomous_cycle output from Pilot 1). Read new next-sprint.md header. Compare. Expected: Output regenerated and fresh (different generated_at timestamp). Evidence: `vwm-pilots/pilot-06-regeneration.log`

**Accept:** Pilots 5-6 PASS. Temp file from Pilot 5 deleted.

---

### TC-VWM-027-04 [CHILD — TODO]

**Pilots 7-8 (Consumer and Portfolio)**

**Micro-steps:**
- MS-VWM-027-04-01 [PENDING]: **Pilot 7 — Downstream consumer.** Action: Run `.venv/Scripts/python -c "from fods.parser import parse_fods; result = parse_fods('samples/by-format/fods/'); print('fods loaded OK, type:', type(result))"`. Expected: Import succeeds and parse_fods runs without exception. Check: No ImportError or AttributeError. Evidence: `vwm-pilots/pilot-07-consumer.log`

- MS-VWM-027-04-02 [PENDING]: **Pilot 8 — Portfolio/cross-track coverage.** Action: Run governance_validator_runner.py against at least 3 format source directories: fods, csv, zst. Collect total validator results. Expected: No false negatives (violations not caught) or false positives (clean files flagged incorrectly). For ZST and CSV (which are CLEAN), verify 0 FAIL. Evidence: `vwm-pilots/pilot-08-portfolio.log`

**Accept:** Pilots 7-8 PASS.

---

### TC-VWM-027-05 [CHILD — TODO]

**Pilots 9-10 (Rollback and Idempotency)**

**Micro-steps:**
- MS-VWM-027-05-01 [PENDING]: **Pilot 9 — Rollback/recovery.** Action: (a) Run `git status` to note current state. (b) If any machinery changes were made in TC-VWM-023, run `git diff --stat tools/supervisor/` to see what changed. (c) Verify that a `git stash` would safely preserve the changes and `git stash pop` would restore them (do NOT actually stash if changes should be kept). (d) Document the rollback path. Expected: All machinery changes are in tracked files that can be reverted safely. Check: git diff shows only expected files. Evidence: `vwm-pilots/pilot-09-rollback.log`

- MS-VWM-027-05-02 [PENDING]: **Pilot 10 — Idempotency.** Action: (a) Run `python tools/supervisor/governance_validator_runner.py 2>&1 | tail -5`. Record output. (b) Run again immediately. Record output. Expected: Identical results (same pass count, same fail count, no state mutation). (c) Run `python tools/supervisor/check_continuation.py` twice. Expected: Same verdict both times. Check: Output diff is empty (or timestamps differ only). Evidence: `vwm-pilots/pilot-10-idempotency.log`

**Accept:** Pilots 9-10 PASS. FAILED_REQUIRED_PILOTS = 0.

---

## TC-VWM-028 [PARENT — PROPOSED]

**Title:** Independent Final Review
**Req:** REQ-VWM-035
**Phase:** Final Review | **Priority:** P1
**Deps:** TC-VWM-027 | **Successor:** TC-VWM-029

**Objective:** Perform a FRESH specialist review after all healing — as if seeing the system for the first time. Independently compare intended contracts vs actual code.

**Children:** TC-VWM-028-01, TC-VWM-028-02, TC-VWM-028-03

---

### TC-VWM-028-01 [CHILD — TODO]

**Purpose:** Compare intended stage contracts vs actual code behavior.

**Micro-steps:**
- MS-VWM-028-01-01 [PENDING]: Action: Read CLAUDE.md "Sprint Closeout" section and "Autonomous Continuation" section. Record the documented pipeline steps and stop conditions. Expected: Documented pipeline captured. Evidence: Notes.

- MS-VWM-028-01-02 [PENDING]: Action: Compare documented pipeline steps (from CLAUDE.md) against actual autonomous_cycle.py step sequence (from TC-VWM-016 findings). Are they in sync? Expected: Documented and actual steps match. Check: Any discrepancy = gap candidate. Evidence: `tc-028-01-contract-vs-code.yaml`

- MS-VWM-028-01-03 [PENDING]: Action: Specifically look for hidden skips in autonomous_cycle.py (exception handlers that swallow errors silently, steps that run only conditionally without logging when skipped). Expected: All silent fallbacks are identified. Check: Any found = gap candidate. Evidence: Appended to tc-028-01 file.

**Accept:** Contract vs code comparison complete. All discrepancies documented.

---

### TC-VWM-028-02 [CHILD — TODO]

**Purpose:** Check for stale outputs, weak proof, and duplicate authority.

**Micro-steps:**
- MS-VWM-028-02-01 [PENDING]: Action: Check for STALE outputs — files whose modification dates predate the machinery repairs. For each affected output class, verify the file was regenerated or confirmed current. Expected: No stale outputs remain. Check: STALE_OUTPUTS_FROM_DEFECTIVE_MACHINERY = 0. Evidence: `tc-028-02-stale-check.log`

- MS-VWM-028-02-02 [PENDING]: Action: Check for SYNTHETIC-ONLY PROOF in grading results — evidence_paths that point to files created specifically to pass the grader (not real execution artifacts). Review work-item-grades.yaml from last sprint. Check: At least 3 evidence paths verified to point to real execution artifacts. Evidence: `tc-028-02-proof-quality.yaml`

- MS-VWM-028-02-03 [PENDING]: Action: Check for DUPLICATE AUTHORITY — two systems claiming to own the same state (e.g., both continuation-signal.json and some other file defining the CONTINUE/STOP decision). Expected: Each state file has exactly one owner. Check: Any dual-authority found = gap candidate. Evidence: `tc-028-02-duplicate-authority.yaml`

**Accept:** No stale outputs. Proof quality verified. No duplicate authority.

---

### TC-VWM-028-03 [CHILD — TODO]

**Purpose:** Score the overall assurance quality and determine if any gap needs reopening.

**Micro-steps:**
- MS-VWM-028-03-01 [PENDING]: Action: Re-score every quality dimension that was previously scored < 4/5 during TC-VWM-019. For each: is the issue now resolved? If yes, update score to ≥ 4. If not, reopen the gap and mark REROUTED. Expected: All dimensions ≥ 4/5 or explicitly reopened. Evidence: `tc-028-03-final-quality-scores.yaml`

- MS-VWM-028-03-02 [PENDING]: Action: Final independent check — read through the gap-ledger.yaml and verify every OPEN gap has: a taskcard_id, a permanent_solution, and a clear exact_next_action. Expected: All OPEN gaps are actionable. Check: No gap with status=OPEN has empty exact_next_action. Evidence: Inline.

**Accept:** All quality scores ≥ 4 or explicitly reopened. All OPEN gaps actionable.

---

## TC-VWM-029 [PARENT — PROPOSED]

**Title:** Idempotent Closure and Final Report
**Req:** REQ-VWM-036, REQ-VWM-037, REQ-VWM-038, REQ-VWM-039, REQ-VWM-040
**Phase:** Closure | **Priority:** P1
**Deps:** TC-VWM-028 | **Successor:** POST_PLAN_TERMINAL (stop)

**Objective:** Verify all completion gate counters = 0. Write final report. Run autonomous cycle. Execute lifecycle audit. Close the plan lock with --terminal --audit-gate. STOP.

**Children:** TC-VWM-029-01, TC-VWM-029-02, TC-VWM-029-03, TC-VWM-029-04, TC-VWM-029-05

---

### TC-VWM-029-01 [CHILD — TODO]

**Purpose:** Verify all 11 completion gate counters equal zero.

**Micro-steps:**
- MS-VWM-029-01-01 [PENDING]: Action: For each of the 11 completion gate counters (from TC-VWM-029 original section), measure the actual count from evidence and reports. Record result in a table. Expected: All 11 = 0. Check: Any counter > 0 → that work is not done → must return to the relevant taskcard before proceeding. Evidence: `tc-029-01-completion-gate-check.yaml`

| Counter | Expected | Source |
|---|---|---|
| UNINVENTORIED_MACHINERY_STAGES | 0 | machinery-stage-inventory.yaml entry count |
| UNCLASSIFIED_BYPASS_PATHS | 0 | TC-VWM-002-04 findings |
| UNREVIEWED_OUTPUT_CLASSES | 0 | output-class-inventory.yaml review_status |
| MATERIAL_FINDINGS_WITHOUT_GAPS | 0 | stage-reviews.yaml vs gap-ledger.yaml |
| ACTIONABLE_GAPS_WITHOUT_TASKCARDS | 0 | gap-ledger.yaml vs taskcard index |
| MACHINERY_GAPS_NOT_ROOT_CAUSE_REPAIRED | 0 | TC-VWM-023 children |
| AFFECTED_OUTPUTS_NOT_REGENERATED | 0 | output-healing-run.yaml |
| OUTPUTS_WITH_QUALITY_DEFECTS | 0 | quality-scores.yaml post-healing |
| STALE_OUTPUTS | 0 | TC-VWM-028-02-01 |
| FAILED_REQUIRED_PILOTS | 0 | TC-VWM-027 children |
| MATERIAL_SECOND_RUN_CHANGES | 0 | Pilot 10 result |

**Accept:** All 11 counters = 0 with evidence.

---

### TC-VWM-029-02 [CHILD — TODO]

**Purpose:** Write the final assurance report.

**Micro-steps:**
- MS-VWM-029-02-01 [PENDING]: Action: Write `reports/machinery-assurance/final-report-vwm-2026-07-10.md`. Required sections: (1) Mission scope, (2) Stage inventory summary, (3) Output classes reviewed, (4) Quality scores summary, (5) Claims reconciliation summary, (6) Gaps created/closed, (7) Machinery repairs, (8) Outputs regenerated, (9) Pilot results table, (10) Idempotency result, (11) Final verdict. Expected: Complete report. Check: File exists and has all 11 sections. Evidence: The file itself.

- MS-VWM-029-02-02 [PENDING]: Action: Determine the final verdict based on TC-VWM-029-01 results. Exactly one of: `MACHINERY_AND_OUTPUTS_PRODUCTION_READY_VERIFIED_AND_IDEMPOTENT` (all counters = 0, all pilots pass) | `MACHINERY_OR_OUTPUT_HEALING_REQUIRES_REWORK` (any counter > 0) | `BLOCKED_BY_TRUE_EXTERNAL_DEPENDENCY` (only if Gate 11 or publication required). Write verdict as first line of final report. Check: Verdict matches counter states. Evidence: Final report.

**Accept:** Final report written with correct verdict.

---

### TC-VWM-029-03 [CHILD — TODO]

**Purpose:** Write evidence declaration and run autonomous cycle.

**Micro-steps:**
- MS-VWM-029-03-01 [PENDING]: Action: Write `.local/evidences/vwm-2026-07-10/evidence-declaration.yaml` using the supervisor-worker-contract.md schema. Include all 29 (+ 30+) taskcards as work items with status CLOSED and evidence paths. Expected: Valid YAML. Check: `python tools/supervisor/sprint_executor_validate.py .local/evidences/vwm-2026-07-10/evidence-declaration.yaml --repair`. Evidence: The file + validate log.

- MS-VWM-029-03-02 [PENDING]: Action: Run `python tools/supervisor/autonomous_cycle.py --declaration .local/evidences/vwm-2026-07-10/evidence-declaration.yaml`. Expected: Exit 0 or 3. Record exit code. If exit 3: log rework items but continue (per Supreme Directive — closeout is best-effort). Evidence: `tc-029-03-autonomous-cycle.log`

**Accept:** Evidence declaration written and autonomous cycle run. Exit 0 or 3 accepted.

---

### TC-VWM-029-04 [CHILD — TODO]

**Purpose:** Build review package and record SHA-256.

**Micro-steps:**
- MS-VWM-029-04-01 [PENDING]: Action: Run `python tools/supervisor/build_declaration_review_package.py --declaration .local/evidences/vwm-2026-07-10/evidence-declaration.yaml`. Expected: ZIP created at absolute path. Check: Absolute path starts with `C:\Users\prora\OneDrive\Documents\GitHub\format-factory\`. SHA-256 printed. Evidence: Path and hash recorded in final report.

**Accept:** Review package created. Absolute path and SHA-256 recorded.

---

### TC-VWM-029-05 [CHILD — TODO]

**Purpose:** Execute lifecycle audit and close the plan lock.

**Micro-steps:**
- MS-VWM-029-05-01 [PENDING]: Action: Run `python tools/supervisor/lifecycle_audit.py --mission-id VWM-2026-07-10 --sprint-id TC-VWM-029`. Expected: Reads Taskcard Status Summary Table, confirms all CLOSED. If ITERATION_REQUIRED: continue with remaining taskcards. If audit passes: proceed to lock. Evidence: `tc-029-05-lifecycle-audit.log`

- MS-VWM-029-05-02 [PENDING]: Action: ONLY IF lifecycle_audit returns no ITERATION_REQUIRED: Run `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/vast-wibbling-moon.md --terminal --audit-gate`. Expected: `.local/supervisor/active-plan-lock.json` updated to `status: TERMINAL_CLOSED`. Check: Read file and verify. Evidence: `tc-029-05-terminal-lock.json`

- MS-VWM-029-05-03 [PENDING]: Action: **STOP.** Report to user: "Plan vast-wibbling-moon COMPLETE. All [N] taskcards closed. Final verdict: [VERDICT]. Review package: [PATH] (SHA-256: [HASH]). Awaiting your next instruction." Do NOT call check_continuation.py. Do NOT read next-sprint.md. POST_PLAN_TERMINAL applies. Evidence: User report.

**Accept:** Plan lock TERMINAL_CLOSED. User notified. Session ends.

---

## TC-VWM-030 [PARENT — PROPOSED] (Created by TC-VWM-022)

**Title:** Fix Continuation Signal Inconsistency (GAP-VWM-001)
**Req:** REQ-VWM-030 | **Gap:** GAP-VWM-001
**Phase:** Healing | **Priority:** P0 (HIGH severity)
**Deps:** TC-VWM-022, TC-VWM-008-05 (root cause identified)
**Scope allowed:** `.local/supervisor/continuation-signal.json` (Option A); OR `tools/supervisor/autonomous_cycle.py` (Option B); OR `tools/supervisor/check_continuation.py` (Option C)
**Scope forbidden:** `src/python/`, `src/net/`, `tests/`

**Objective:** Resolve the contradictory state where `stop_reason = "critical_rework_blocks_continuation"` with `rework_items = []`. Apply the solution option selected in TC-VWM-021-02.

**Children:** TC-VWM-030-01, TC-VWM-030-02

### TC-VWM-030-01 [CHILD — TODO]

**Purpose:** Apply the selected fix for GAP-VWM-001.

**Micro-steps:**
- MS-VWM-030-01-01 [PENDING]: Action: Read TC-VWM-021-02 evidence to determine selected option (A, B, or C). Apply the fix to the selected file. Expected: The contradictory state is resolved. Check: After fix, read continuation-signal.json — stop_reason should be null or consistent with rework_items. Evidence: `tc-030-01-fix-applied.log`

- MS-VWM-030-01-02 [PENDING]: Action: Add a regression test (if Option B or C — code changes) to `tests/supervisor/` that verifies check_continuation.py handles empty rework_items correctly regardless of stop_reason. If Option A (JSON fix only), document as ACCEPTED_RISK (no code regression). Expected: Test added or risk accepted. Evidence: `tc-030-01-regression-test.log` or acceptance note.

### TC-VWM-030-02 [CHILD — TODO]

**Purpose:** Verify the fix works end-to-end.

**Micro-steps:**
- MS-VWM-030-02-01 [PENDING]: Action: Run `python tools/supervisor/check_continuation.py`. Expected: CONTINUE verdict. Evidence: `tc-030-02-verify.json`

- MS-VWM-030-02-02 [PENDING]: Action: Update GAP-VWM-001 in gap-ledger.yaml to `status: CLOSED` with `closure_evidence` pointing to tc-030-02-verify.json. Evidence: Updated gap-ledger.yaml.

**Accept:** continuation-signal.json consistent. check_continuation returns CONTINUE. GAP-VWM-001 CLOSED.

---

## TC-VWM-031 [PARENT — PROPOSED] (Created by TC-VWM-022)

**Title:** Add Automated Site-Packages Sync Enforcement (GAP-MA-001)
**Req:** REQ-VWM-030 | **Gap:** GAP-MA-001
**Phase:** Healing | **Priority:** P1 (MEDIUM severity)
**Deps:** TC-VWM-022
**Scope allowed:** `tools/supervisor/` (new validator or script), `tools/assurance/`, `tests/supervisor/`

**Objective:** Add automated enforcement so that when non-editable packages (ABW/SYLK/ZST/DIF) have source changes, a check verifies the .venv/Lib/site-packages/ copy is current.

**Children:** TC-VWM-031-01, TC-VWM-031-02

### TC-VWM-031-01 [CHILD — TODO]

**Purpose:** Implement the selected enforcement mechanism.

**Micro-steps:**
- MS-VWM-031-01-01 [PENDING]: Action: Read TC-VWM-021-02 evidence for selected option (A=governance validator, B=pre-execution script, C=accepted risk). If Option A: implement a new governance validator function `validate_site_packages_sync()` in the appropriate governance_validators file. If Option B: implement a standalone script `tools/assurance/check_site_packages_sync.py`. If Option C: update gap-ledger.yaml status to ACCEPTED_RISK with rationale. Expected: Implementation or documented acceptance. Evidence: `tc-031-01-implementation.log`

- MS-VWM-031-01-02 [PENDING]: Action: Add a focused test for the enforcement mechanism. If validator: add test case to tests/supervisor/test_governance_validators.py. If script: add test to tests/. Expected: Test passes. Evidence: `tc-031-01-test.log`

### TC-VWM-031-02 [CHILD — TODO]

**Purpose:** Verify and close GAP-MA-001.

**Micro-steps:**
- MS-VWM-031-02-01 [PENDING]: Action: Test enforcement: modify `src/python/abw/__init__.py` (one trivial comment), verify enforcement mechanism detects the sync gap, then revert. Expected: Detection confirmed. Evidence: `tc-031-02-enforcement-test.log`

- MS-VWM-031-02-02 [PENDING]: Action: Update GAP-MA-001 in gap-ledger.yaml to `status: CLOSED` (or ACCEPTED_RISK if Option C). Evidence: Updated gap-ledger.yaml.

**Accept:** GAP-MA-001 enforcement implemented (or formally accepted). Gap closed.

---

## TC-VWM-032 [PARENT — PROPOSED] (Created by TC-VWM-022)

**Title:** Formally Register GAP-MA-006 in Gap Ledger (One-Mechanism Lock Violation)
**Req:** REQ-VWM-028 | **Gap:** GAP-MA-006
**Phase:** Gap Ledger (admin) | **Priority:** P1 (MEDIUM severity)
**Deps:** TC-VWM-021-03

**Objective:** Move GAP-MA-006 from MEMORY.md informal reference to formal gap-ledger.yaml entry. This is a registration task, not a code fix — the fix itself may require further taskcards.

**Children:** TC-VWM-032-01

### TC-VWM-032-01 [CHILD — TODO]

**Purpose:** Add GAP-MA-006 to gap-ledger.yaml.

**Micro-steps:**
- MS-VWM-032-01-01 [PENDING]: Action: Verify TC-VWM-021-03 produced a formal GAP-MA-006 entry in gap-candidates.yaml. Read it. Expected: Entry has all required fields. Evidence: Inline.

- MS-VWM-032-01-02 [PENDING]: Action: Append GAP-MA-006 to `reports/machinery-assurance/gap-ledger.yaml`. Set status=OPEN. Include exact_next_action: "Assess One-Mechanism Lock enforcement in autonomous_cycle.py and sprint_executor.py". Evidence: Updated gap-ledger.yaml.

- MS-VWM-032-01-03 [PENDING]: Action: Run `python -c "import yaml; yaml.safe_load(open('reports/machinery-assurance/gap-ledger.yaml'))"`. Expected: Parses without error. Evidence: Parse result.

**Accept:** GAP-MA-006 in gap-ledger.yaml. YAML valid.

---

## SECTION 10 — EXECUTION HANDOFF

**The future execution agent must follow this protocol:**

### Before Starting ANY Taskcard

1. Read `plans/.claude/vast-wibbling-moon.md` (this file) — it is the SOLE execution authority.
2. Run `python tools/supervisor/check_continuation.py` — verify CONTINUE verdict.
3. Identify the first PROPOSED or READY parent taskcard in the dependency order (Section 5 DAG).
4. Read that parent taskcard completely.
5. Identify the first TODO child taskcard under the parent.
6. Read that child taskcard completely.
7. Confirm: (a) What parent does this serve? (b) What REQ does this satisfy? (c) What files may be touched? (d) What must not change?

### Executing a Micro-Step

1. Confirm the micro-step status is PENDING or READY.
2. Confirm all preconditions are met (prior micro-steps COMPLETE).
3. Execute EXACTLY ONE micro-step action.
4. Capture evidence immediately (log file, inline note, or artifact).
5. Confirm the expected output matches actual output.
6. Update the micro-step status: PENDING → ACTIVE → COMPLETE (or FAILED).

### After Completing All Micro-Steps in a Child

1. Verify all micro-steps are COMPLETE (none FAILED or BLOCKED).
2. Run child acceptance checks.
3. Score child quality dimensions (1-5).
4. If any mandatory dimension < 4/5: mark child REROUTED, create repair micro-step.
5. If all ≥ 4/5: mark child SCORED → CLOSED.
6. Update Taskcard Status Summary Table (bottom of this plan).

### After Completing All Children in a Parent

1. Run parent integration checks.
2. Score parent quality dimensions.
3. If any mandatory dimension < 4/5: mark parent REROUTED.
4. If all ≥ 4/5: mark parent SCORED → CLOSED.
5. Update status table.
6. Per the DAG (Section 5), identify the next valid parent taskcard.
7. Continue.

### The Agent MUST NOT

- Choose unrelated work outside this plan.
- Skip micro-steps silently.
- Mark a child CLOSED before all its micro-steps are COMPLETE.
- Mark a parent CLOSED before all mandatory children are CLOSED.
- Treat code existence as validation (must run and verify).
- Treat evidence PATH existence as evidence (must inspect contents).
- Continue to the next sprint after TC-VWM-029 closes (POST_PLAN_TERMINAL applies).

---

## SECTION 11 — TASKCARD STATUS SUMMARY TABLE

This 2-column table is required by `lifecycle_audit.py parse_plan_taskcards()`.
It must list ALL taskcards (parents and children) in exactly 2-column format.

| TC-ID | Status |
|---|---|
| TC-VWM-001 | OPEN |
| TC-VWM-001-01 | OPEN |
| TC-VWM-001-02 | OPEN |
| TC-VWM-001-03 | OPEN |
| TC-VWM-001-04 | OPEN |
| TC-VWM-001-05 | OPEN |
| TC-VWM-002 | OPEN |
| TC-VWM-002-01 | OPEN |
| TC-VWM-002-02 | OPEN |
| TC-VWM-002-03 | OPEN |
| TC-VWM-002-04 | OPEN |
| TC-VWM-002-05 | OPEN |
| TC-VWM-002-06 | OPEN |
| TC-VWM-003 | OPEN |
| TC-VWM-003-01 | OPEN |
| TC-VWM-003-02 | OPEN |
| TC-VWM-003-03 | OPEN |
| TC-VWM-003-04 | OPEN |
| TC-VWM-004 | OPEN |
| TC-VWM-004-01 | OPEN |
| TC-VWM-004-02 | OPEN |
| TC-VWM-004-03 | OPEN |
| TC-VWM-004-04 | OPEN |
| TC-VWM-005 | OPEN |
| TC-VWM-005-01 | OPEN |
| TC-VWM-005-02 | OPEN |
| TC-VWM-005-03 | OPEN |
| TC-VWM-005-04 | OPEN |
| TC-VWM-005-05 | OPEN |
| TC-VWM-006 | OPEN |
| TC-VWM-006-01 | OPEN |
| TC-VWM-006-02 | OPEN |
| TC-VWM-006-03 | OPEN |
| TC-VWM-006-04 | OPEN |
| TC-VWM-007 | OPEN |
| TC-VWM-007-01 | OPEN |
| TC-VWM-007-02 | OPEN |
| TC-VWM-007-03 | OPEN |
| TC-VWM-007-04 | OPEN |
| TC-VWM-008 | OPEN |
| TC-VWM-008-01 | OPEN |
| TC-VWM-008-02 | OPEN |
| TC-VWM-008-03 | OPEN |
| TC-VWM-008-04 | OPEN |
| TC-VWM-008-05 | OPEN |
| TC-VWM-009 | OPEN |
| TC-VWM-009-01 | OPEN |
| TC-VWM-009-02 | OPEN |
| TC-VWM-009-03 | OPEN |
| TC-VWM-009-04 | OPEN |
| TC-VWM-010 | OPEN |
| TC-VWM-010-01 | OPEN |
| TC-VWM-010-02 | OPEN |
| TC-VWM-010-03 | OPEN |
| TC-VWM-010-04 | OPEN |
| TC-VWM-011 | OPEN |
| TC-VWM-011-01 | OPEN |
| TC-VWM-011-02 | OPEN |
| TC-VWM-011-03 | OPEN |
| TC-VWM-011-04 | OPEN |
| TC-VWM-012 | OPEN |
| TC-VWM-012-01 | OPEN |
| TC-VWM-012-02 | OPEN |
| TC-VWM-012-03 | OPEN |
| TC-VWM-012-04 | OPEN |
| TC-VWM-013 | OPEN |
| TC-VWM-013-01 | OPEN |
| TC-VWM-013-02 | OPEN |
| TC-VWM-013-03 | OPEN |
| TC-VWM-013-04 | OPEN |
| TC-VWM-014 | OPEN |
| TC-VWM-014-01 | OPEN |
| TC-VWM-014-02 | OPEN |
| TC-VWM-014-03 | OPEN |
| TC-VWM-014-04 | OPEN |
| TC-VWM-015 | OPEN |
| TC-VWM-015-01 | OPEN |
| TC-VWM-015-02 | OPEN |
| TC-VWM-015-03 | OPEN |
| TC-VWM-015-04 | OPEN |
| TC-VWM-016 | OPEN |
| TC-VWM-016-01 | OPEN |
| TC-VWM-016-02 | OPEN |
| TC-VWM-016-03 | OPEN |
| TC-VWM-016-04 | OPEN |
| TC-VWM-017 | OPEN |
| TC-VWM-017-01 | OPEN |
| TC-VWM-017-02 | OPEN |
| TC-VWM-017-03 | OPEN |
| TC-VWM-017-04 | OPEN |
| TC-VWM-018 | OPEN |
| TC-VWM-018-01 | OPEN |
| TC-VWM-018-02 | OPEN |
| TC-VWM-018-03 | OPEN |
| TC-VWM-018-04 | OPEN |
| TC-VWM-018-05 | OPEN |
| TC-VWM-019 | OPEN |
| TC-VWM-019-01 | OPEN |
| TC-VWM-019-02 | OPEN |
| TC-VWM-019-03 | OPEN |
| TC-VWM-020 | OPEN |
| TC-VWM-020-01 | OPEN |
| TC-VWM-020-02 | OPEN |
| TC-VWM-020-03 | OPEN |
| TC-VWM-021 | OPEN |
| TC-VWM-021-01 | OPEN |
| TC-VWM-021-02 | OPEN |
| TC-VWM-021-03 | OPEN |
| TC-VWM-021-04 | OPEN |
| TC-VWM-022 | OPEN |
| TC-VWM-022-01 | OPEN |
| TC-VWM-022-02 | OPEN |
| TC-VWM-022-03 | OPEN |
| TC-VWM-023 | OPEN |
| TC-VWM-023-01 | OPEN |
| TC-VWM-023-02 | OPEN |
| TC-VWM-023-03 | OPEN |
| TC-VWM-023-04 | OPEN |
| TC-VWM-024 | OPEN |
| TC-VWM-024-01 | OPEN |
| TC-VWM-024-02 | OPEN |
| TC-VWM-024-03 | OPEN |
| TC-VWM-024-04 | OPEN |
| TC-VWM-025 | OPEN |
| TC-VWM-025-01 | OPEN |
| TC-VWM-025-02 | OPEN |
| TC-VWM-025-03 | OPEN |
| TC-VWM-026 | OPEN |
| TC-VWM-026-01 | OPEN |
| TC-VWM-026-02 | OPEN |
| TC-VWM-026-03 | OPEN |
| TC-VWM-027 | OPEN |
| TC-VWM-027-01 | OPEN |
| TC-VWM-027-02 | OPEN |
| TC-VWM-027-03 | OPEN |
| TC-VWM-027-04 | OPEN |
| TC-VWM-027-05 | OPEN |
| TC-VWM-028 | OPEN |
| TC-VWM-028-01 | OPEN |
| TC-VWM-028-02 | OPEN |
| TC-VWM-028-03 | OPEN |
| TC-VWM-029 | OPEN |
| TC-VWM-029-01 | OPEN |
| TC-VWM-029-02 | OPEN |
| TC-VWM-029-03 | OPEN |
| TC-VWM-029-04 | OPEN |
| TC-VWM-029-05 | OPEN |
| TC-VWM-030 | OPEN |
| TC-VWM-030-01 | OPEN |
| TC-VWM-030-02 | OPEN |
| TC-VWM-031 | OPEN |
| TC-VWM-031-01 | OPEN |
| TC-VWM-031-02 | OPEN |
| TC-VWM-032 | OPEN |
| TC-VWM-032-01 | OPEN |

---

## SECTION 12 — VERIFICATION SUMMARY

```bash
# 1. Plan lock written for this session
python tools/supervisor/check_continuation.py
# Expected: CONTINUE verdict

# 2. Governance validators — actual count matches expected
python tools/supervisor/governance_validator_runner.py 2>&1 | tail -10
# Expected: 0 FAIL, actual_count == expected_count

# 3. Full test suite
.venv/Scripts/pytest --tb=short -q 2>&1 | tail -5
# Expected: ≥1169 passed, 0 failed

# 4. Stub scan
python tools/review/no_stub_scan.py src/python --json
# Expected: {"status": "CLEAN", "total_violations": 0}

# 5. Control index
python -m tools.supervisor.control_index status
# Expected: synced, 11K+ rows

# 6. Oracle spot check
.venv/Scripts/python tools/oracle/execute_oracle.py fods
# Expected: all cases PASS

# 7. Final report
python -c "open('reports/machinery-assurance/final-report-vwm-2026-07-10.md').readline()"
# Expected: starts with verdict line
```

---

## SECTION 13 — KEY FILES REFERENCE

| Purpose | Path |
|---|---|
| This plan (authoritative) | plans/.claude/vast-wibbling-moon.md |
| Prior gap ledger | reports/machinery-assurance/gap-ledger.yaml |
| Prior assurance report | reports/machinery-assurance/final-report.md |
| Assurance mission | reports/machinery-assurance/assurance-mission.yaml |
| Stage inventory | reports/machinery-assurance/machinery-stage-inventory.yaml |
| Stage reviews | reports/machinery-assurance/stage-reviews.yaml |
| Output class inventory | reports/machinery-assurance/output-class-inventory.yaml |
| Quality scores | reports/machinery-assurance/quality-scores.yaml |
| Claim reconciliation | reports/machinery-assurance/claim-reconciliation.yaml |
| Output healing run | reports/machinery-assurance/output-healing-run.yaml |
| Supporting analysis artifacts | reports/machinery-assurance/vwm-analysis/ |
| Final report | reports/machinery-assurance/final-report-vwm-2026-07-10.md |
| Evidence declaration | .local/evidences/vwm-2026-07-10/evidence-declaration.yaml |
| Gap candidates (running) | .local/evidences/vwm-2026-07-10/gap-candidates.yaml |
| Pilot evidence | .local/evidences/vwm-pilots/ |
| Plan lock (this session) | .local/supervisor/active-plan-lock.json |
| Continuation signal | .local/supervisor/continuation-signal.json |
| Governance validators | tools/supervisor/governance_validator_runner.py |
| Continuation checker | tools/supervisor/check_continuation.py |
| Plan lock writer | tools/supervisor/write_plan_lock.py |
| Lifecycle auditor | tools/supervisor/lifecycle_audit.py |
| Stub scanner | tools/review/no_stub_scan.py |
| Pytest binary | .venv/Scripts/pytest |
| MEMORY.md | C:\Users\prora\.claude\projects\c--Users-prora-OneDrive-Documents-GitHub-format-factory\memory\MEMORY.md |
