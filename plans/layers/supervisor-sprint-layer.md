# Supervisor Sprint Layer

```yaml
layer_metadata:
  layer_id: L11
  canonical_name: Supervisor Sprint Layer
  canonical_slug: supervisor-sprint-layer
  permanent_plan_path: plans/layers/supervisor-sprint-layer.md
  schema_version: "1.0"
  plan_revision: "1"
  repository_revision: "a7744cf6"
  status: GOVERNED_OPERATIONAL
  health: HEALTHY
  maturity_current: 5
  maturity_target: 5
  current_stage: GOVERNED_OPERATION
  current_owner: null
  agent_type: autonomous-supervisor
  session_id: "923e237958c1"
  active_sprint: "lp-bootstrap"
  active_taskcards: []
  ready_taskcards: [TC-SUP-001, TC-SUP-002]
  blocked_taskcards: []
  completed_taskcards: []
  dependencies: [L08, L09, L10, L12, L13]
  upstream_layers: [L08, L09, L10, L12, L13]
  downstream_layers: []
  skill_ids: [autonomous-loop, post-sprint-loop, post-sprint-audit]
  command_ids: [autonomous-loop, post-sprint-loop, post-sprint-audit]
  evidence_paths:
    - reports/supervisor/session-resume.md
    - reports/supervisor/next-sprint.md
    - .local/supervisor/continuation-signal.json
  last_started_at: "2026-06-26"
  last_progress_at: "2026-06-26"
  last_updated_at: "2026-06-26"
  last_verified_at: "2026-06-26"
  last_verified_revision: "a7744cf6"
  next_task_id: TC-SUP-001
  next_action: "Code-enforce lane ownership and DAG ordering; call overclaim detector on every cycle"
  handoff_id: null
```

---

## 1. Layer Metadata

See YAML block above.

## 2. Authority and Purpose

The Supervisor Sprint Layer is the **autonomous execution engine** of Format Factory.
It is responsible for:

- Orchestrating the full sprint cycle: validate → inspect → grade → plan-next → manifest
- Generating the next-worker prompt (8-section format)
- Managing continuation state (CONTINUE/STOP verdicts)
- Writing session-resume.md, approval-gates.md, next-sprint.md
- Running governance validators against every declaration
- Grading each work item on an 8-level rubric
- Detecting anti-skip patterns, stale state, and overclaims
- Enforcing the Supreme Directive (never stop except TRUE_EXTERNAL_GATEs)

**Authority:** Advisory only. The registry (format-registry.yaml), plans/master-plan.md,
and taskcards are authoritative. Supervisor output is advisory and input to next sprint.

## 3. Scope

- All files under `tools/supervisor/` (69 modules)
- Sprint cycle: autonomous_cycle.py, sprint_executor.py, sprint_executor_validate.py
- Grading: grade_declared_work.py, grade_to_quality_adapter.py
- Next-prompt generation: generate_next_worker_prompt.py
- Continuation: check_continuation.py, continuation_state.py
- Validator runner: governance_validator_runner.py
- Context pack: build_context_pack.py
- Anti-skip: anti_skip_checker.py

## 4. Explicit Non-Scope

- Does NOT own plan content (that is L10)
- Does NOT own governance validators (that is L12)
- Does NOT own skill registry (that is L13)
- Does NOT own continuation state storage (that is L09)
- Does NOT own evidence schema (that is L08)
- Does NOT own product source (that is L06)

## 5. Owned Decisions

- Sprint cycle step ordering
- Continuation verdict logic (CONTINUE/STOP and all sub-reasons)
- Grading rubric implementation
- Anti-skip detection patterns
- Next-worker prompt 8-section format
- Context pack assembly

## 6. Upstream Inputs

| Input | Source Layer | File | Description |
|-------|-------------|------|-------------|
| Evidence declaration | L08 | .local/evidences/<run_id>/evidence-declaration.yaml | Worker's claimed work |
| Continuation signal | L09 | .local/supervisor/continuation-signal.json | Session isolation, iteration |
| Plan authority | L10 | plans/master-plan.md, next-sprint.md | Strategic direction |
| Governance results | L12 | governance_validator_runner output | Blocking violations |
| Skill registry | L13 | .supervisor/skill-registry.yaml | Available skills |

## 7. Downstream Consumers

| Output | Consumer | File |
|--------|----------|------|
| session-resume.md | Worker (next session) | reports/supervisor/session-resume.md |
| approval-gates.md | Worker | reports/supervisor/approval-gates.md |
| next-sprint.md | Worker | reports/supervisor/next-sprint.md |
| next-work-items.json | Automated continuation | .local/supervisor/next-work-items.json |
| evidence-review.json | Audit trail | reports/supervisor/evidence-review.json |
| grading-history.jsonl | L24 Metrics | reports/supervisor/grading-history.jsonl |
| context-pack.yaml | Multiple | .supervisor/context-pack.yaml |

## 8. Ideal Production Design

The ideal supervisor:

1. **Consumes declarations** via `autonomous_cycle.py --declaration <path>` (single entry point)
2. **Validates** schema + path existence + governance validators (all 85+ validators)
3. **Inspects** each declared evidence artifact exists and is non-empty
4. **Grades** each item against 8-level rubric + acceptance criteria
5. **Anti-skip checks** detect patterns that indicate work was skipped
6. **Overclaim detection** (10 patterns) runs on every item
7. **Lane ownership enforcement** in code (not just prompts) — each item's files must belong to declared lane
8. **DAG ordering** validated — items cannot claim work on downstream layers before upstream layers
9. **Generates** next-worker prompt using current gap-ledger, maturity signal, and layer index
10. **Selects** next work from plans/layers/index.yaml (ready, dependency-valid tasks)
11. **Writes** outputs atomically with rollback on failure
12. **Updates** session-resume.md with full context for cross-session resume

## 9. Verified Current Implementation

```yaml
current_layer_implementation:
  implementation_paths:
    - tools/supervisor/autonomous_cycle.py  # 2500+ LOC, main orchestrator
    - tools/supervisor/sprint_executor.py   # headless run-loop wrapper
    - tools/supervisor/sprint_executor_validate.py  # declaration validator
    - tools/supervisor/check_continuation.py  # CONTINUE/STOP verdict
    - tools/supervisor/governance_validator_runner.py  # validator runner
    - tools/supervisor/grade_declared_work.py  # 8-level grading
    - tools/supervisor/generate_next_worker_prompt.py  # next prompt
    - tools/supervisor/anti_skip_checker.py  # anti-skip patterns
    - tools/supervisor/build_context_pack.py  # context assembly
  schema_paths:
    - .supervisor/schemas/supervisor-cycle-manifest.schema.json
    - .supervisor/schemas/supervisor-review.schema.json
    - .supervisor/schemas/next-sprint-taskmaster.schema.json
  registry_paths:
    - .supervisor/policies.yaml
    - .supervisor/context-pack.yaml
  active_components:
    - autonomous_cycle (declaration-driven)
    - check_continuation (CCI-MVP with session_id)
    - governance_validator_runner (85 validators)
    - grade_declared_work (8-level rubric)
    - generate_next_worker_prompt (8-section format)
    - anti_skip_checker (10 patterns)
  partially_implemented_components:
    - overclaim_detector: defined (10 patterns) but NEVER CALLED per forensic audit
    - lane_ownership_enforcement: only in prompts, not in code
    - dag_ordering_enforcement: only in prompts, not in code
  missing_components:
    - layer_control_plane_consumer: supervisor does not read plans/layers/index.yaml
    - failure_memory: zero durable learning (static decision rules)
  bypass_paths:
    - sprint_executor_validate.py can be skipped (best-effort per CLAUDE.md)
  contradictions: []
```

## 10. Current Execution Stage

**GOVERNED_OPERATION** — The supervisor is production-grade and runs every sprint.
Key capability gaps (SUP-GAP-001 through SUP-GAP-008) exist in enforcement depth
but do not prevent operation.

## 11. Current Maturity Assessment

**LEVEL 5 — PRODUCTION AUTHORITY** (operational assessment)

Justification:
- 69 modules, 6,500+ LOC validators
- Every sprint uses it without exception
- CCI-MVP isolation working
- 8-level grading + anti-skip + 85 validators operational
- Session resume proven across multiple sessions
- Exit codes correctly signal CONTINUE/STOP

Ceiling gaps (preventing ideal state):
- Overclaim detector never called (prompt-only)
- Lane ownership not code-enforced (prompt-only)
- Layer index not consumed by supervisor

## 12. Target Maturity

**LEVEL 5 — PRODUCTION AUTHORITY** (maintained with gap closure)

Gap closure needed:
- Call overclaim_detector on every cycle (SUP-GAP-001)
- Code-enforce lane ownership in autonomous_cycle.py (SUP-GAP-002)
- Consume plans/layers/index.yaml for work selection (SUP-GAP-003)
- Add failure_memory.json (SUP-GAP-004)

## 13. Current Strengths

- Production-grade declaration-driven pipeline
- 85 governance validators with GOV_BLOCK structural exception
- CCI-MVP prevents cross-session state contamination
- Supreme Directive implemented: closeout failures never block next sprint
- POST_PLAN_TERMINAL correctly handled
- MAX_ITERATIONS correctly handled (rollover, not stop)
- Per-chat plan precedence enforced mechanically via plan-lock files

## 14. Gap Register

| Gap ID | Severity | Current State | Target State | Root Cause | Taskcards |
|--------|----------|---------------|--------------|------------|-----------|
| SUP-GAP-001 | HIGH | overclaim_detector defined but never called | Called on every cycle | prompt-only enforcement | TC-SUP-001 |
| SUP-GAP-002 | HIGH | Lane ownership in prompts only | Code-enforced DAG ordering | No code implementation | TC-SUP-001 |
| SUP-GAP-003 | MEDIUM | Supervisor does not read layer index | Reads plans/layers/index.yaml | Layer index didn't exist | TC-SUP-002 |
| SUP-GAP-004 | MEDIUM | Zero durable learning | failure_memory.json auto-propagation | Architecture decision (static rules) | TBD |
| SUP-GAP-005 | LOW | generate_supervisor_packet.py: AttributeError on list | Fixed | Pre-existing bug | TBD |
| SUP-GAP-006 | MEDIUM | Shared file mutation ownership in prompts only | Code-enforced via source-change-handoff | No implementation | TC-SCH-001 |

## 15. Root-Cause Register

- **SUP-GAP-001/002:** The supervisor was designed as advisory-only (policies.yaml). Enforcement of lane ordering and overclaim detection was left to prompt text rather than code, creating a gap where the Supreme Directive "log and continue" could bypass structural checks.
- **SUP-GAP-003:** plans/layers/ directory did not exist before this bootstrap session.
- **SUP-GAP-004:** Architecture decision: all decision rules are static. Failure-memory auto-propagation requires a persistent learning loop (Lane 15 of spec-to-feature plan).

## 16. Repair Architecture

1. **TC-SUP-001:** Add `call_overclaim_detector()` in `autonomous_cycle.py` after validation phase. Add DAG ordering check that reads `plans/layers/dependency-register.yaml` to verify upstream layers have adequate maturity before downstream work is selected.
2. **TC-SUP-002:** Update `autonomous_task_generator.py` to read `plans/layers/index.yaml` and return ready, dependency-valid tasks.
3. **SUP-GAP-004:** Phase 1: Add append-only failure_memory.json in `.local/supervisor/`. Phase 2: Loader reads it at cycle start. Phase 3: Auto-propagation to CLAUDE.md (future).

## 17. Schemas and Contracts

- `.supervisor/schemas/supervisor-cycle-manifest.schema.json` — cycle output manifest
- `.supervisor/schemas/supervisor-review.schema.json` — grading output
- `.supervisor/schemas/next-sprint-taskmaster.schema.json` — next-sprint format
- `.supervisor/schemas/stop-reason-decision.schema.json` — continuation verdicts
- `.supervisor/policies.yaml` — authority model and no-drift contract

## 18. Producers

- Worker writes evidence declaration → supervisor consumes
- Plan authority provides strategic direction → supervisor reads

## 19. Consumers

- Worker reads session-resume.md, next-sprint.md, approval-gates.md
- L24 (Metrics) reads grading-history.jsonl, maturity-trend.json
- L09 (State) writes continuation-signal.json that supervisor reads

## 20. Skills and Commands

| Skill | Command | Purpose |
|-------|---------|---------|
| autonomous-loop | /autonomous-loop | Interactive VSCode supervised loop |
| post-sprint-loop | /post-sprint-loop | Post-sprint cleanup and continuation |
| post-sprint-audit | /post-sprint-audit | Audit sprint results |

## 21. Validators and Enforcement

All 85 governance validators (V1-V82 + SAL validators) run via
`governance_validator_runner.py` on every declaration. Key validators that
affect supervisor operation:

- V74: ledger_continuation_gate — blocks formats with continuation_allowed=false
- V48: architecture_only_stub_gate — blocks RELEASE_GATE with stubs
- GOV_BLOCK validators (V66, V67, V69, monolith_detection) — structural failures

## 22. Tests and Negative Controls

- `tests/supervisor/test_governance_validators.py` — 138 tests (2026-06-26)
- `tests/supervisor/test_lane_guard.py` — lane enforcement tests
- `tests/supervisor/test_governance_validators.py` — V83-V86 (pending TC-VAL-001)

## 23. Evidence and Observability

- `reports/supervisor/session-resume.md` — human-readable sprint summary
- `reports/supervisor/evidence-review.json` — machine-readable grading
- `reports/supervisor/grading-history.jsonl` — append-only audit trail
- `.supervisor/context-pack.yaml` — current execution context
- `reports/supervisor/maturity-signal.json` — format maturity tracking

## 24. Recovery and Rollback

Per CLAUDE.md Supreme Directive:
- Any closeout step failure → log and continue to next sprint immediately
- Exit 3 (rework) → log rework items, continue
- Exit 1 (declaration error) → log error, continue
- Exit 9 (unexpected) → log error, continue

GOV_BLOCK exception overrides Supreme Directive for structural failures
(monolith_detection, source_architecture, multi_responsibility, analytics_naming).

## 25. Security and Compliance

- Supervisor output is advisory only (policies.yaml)
- Never overwrites: AGENTS.md, GOVERNANCE.md, plans/master-plan.md, tools/evidence/, tests/evidence/
- Gate 11 execution requires Babar Raza's business authority

## 26. Cross-Layer Handoffs

| Handoff | From | To | Artifact |
|---------|------|----|---------|
| HO-005 | L10 | L11 | plans/layers/index.yaml consumed by supervisor |
| HO-006 | L12 | L08 | V83 enforces primary_layer_id in declarations |

## 27. Migration and Backfill

No migration needed. Supervisor is operational. Gap closure (TC-SUP-001, TC-SUP-002)
is additive enhancement to existing codebase.

## 28. Effort and Dependencies

- TC-SUP-001: ~4 hours. Depends on TC-LP-001 (layer control plane must exist).
- TC-SUP-002: ~2 hours. Depends on TC-LP-001 (index.yaml must exist).
- No product source changes required.

## 29. Active Taskcards

| Task ID | Title | Status | Priority |
|---------|-------|--------|---------|
| TC-SUP-001 | Code-enforce lane ownership and DAG ordering | TODO | P1 |
| TC-SUP-002 | Update supervisor to consume plans/layers/index.yaml | TODO | P2 |

## 30. Ready Taskcards

TC-SUP-001 and TC-SUP-002 are READY (depends on TC-LP-001 which is IN_PROGRESS).

## 31. Completed Taskcards

(None in this bootstrap session)

## 32. Blocked and Waiting Work

- SUP-GAP-004 (failure_memory.json) — requires Lane 15 design decision. WAITING.

## 33. Decision Log

| Decision | Date | Rationale |
|----------|------|-----------|
| Supervisor is advisory only | Pre-existing | policies.yaml authority model |
| Closeout failures skip (not block) | Pre-existing | Supreme Directive |
| Lane ownership in prompts only | Pre-existing | Implementation debt (SUP-GAP-002) |
| Layer index not consumed | Pre-existing | Layer index didn't exist |

## 34. Work Log

```yaml
- log_id: WL-L11-001
  layer_id: L11
  permanent_layer_plan: plans/layers/supervisor-sprint-layer.md
  task_id: TC-LP-001
  session_id: "923e237958c1"
  sprint_id: lp-bootstrap
  timestamp: "2026-06-26T00:00:00Z"
  event_type: LAYER_FILE_CREATED
  summary: "Created supervisor-sprint-layer.md permanent plan file with full 39-section content"
  repository_revision: a7744cf6
  changed_paths:
    - plans/layers/supervisor-sprint-layer.md
  current_stage: GOVERNED_OPERATION
  status: IN_PROGRESS
  next_action: "Continue with TC-LP-001 remaining layer files"
```

## 35. Verification Log

```yaml
- verification_id: VER-L11-001
  layer_id: L11
  task_id: null
  repository_revision: a7744cf6
  contracts_verified:
    - "autonomous_cycle.py exists and is callable"
    - "check_continuation.py returns CONTINUE/STOP with session_id"
    - "85 validators registered in governance_validator_runner.py"
    - "session-resume.md current at 2026-06-25T17:41:06"
  tests_run:
    - "tests/supervisor/test_governance_validators.py — 138 PASS"
    - "tests/supervisor/test_lane_guard.py"
  focused_result: PASS
  integration_result: PASS (1609 tests passing total)
  negative_control_result: PASS (POST_PLAN_TERMINAL stops correctly)
  regression_result: PASS
  package_or_consumer_result: N/A
  idempotency_result: PASS (approval-gates.md MD5 unchanged after 2 runs)
  evidence_paths:
    - reports/supervisor/session-resume.md
  verified_at: "2026-06-26"
  verifier: "forensic-layer-discovery-report.md"
  verdict: VERIFIED
```

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L11-001
  layer_id: L11
  permanent_layer_plan: plans/layers/supervisor-sprint-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  repository_revision: a7744cf6
  current_status: GOVERNED_OPERATIONAL
  current_stage: GOVERNED_OPERATION
  maturity_current: 5
  last_completed_task: null
  active_task: TC-LP-001 (bootstrap, not L11-specific)
  current_checkpoint: "Layer file created with full content"
  exact_next_task: TC-SUP-001
  why_this_is_next: >
    Lane ownership is not code-enforced (SUP-GAP-001/002). The overclaim detector
    (10 patterns) is never called. These are the most impactful gaps for
    supervisor correctness.
  ready_tasks: [TC-SUP-001, TC-SUP-002]
  blocked_tasks: []
  required_skills: []
  required_commands: []
  allowed_paths:
    - tools/supervisor/autonomous_cycle.py
    - tools/supervisor/autonomous_cycle_extensions/
    - tools/supervisor/autonomous_task_generator.py
    - plans/layers/
  forbidden_paths:
    - src/python/
    - src/net/
  required_verification:
    - "tests/supervisor/test_governance_validators.py passes"
    - "check_continuation.py exits 0 with CONTINUE after successful sprint"
  important_decisions:
    - "Supervisor is advisory only per policies.yaml"
    - "Closeout failures skip, not block (Supreme Directive)"
  unresolved_findings:
    - "SUP-GAP-001: overclaim_detector never called"
    - "SUP-GAP-002: lane ownership in prompts only"
    - "SUP-GAP-003: supervisor does not read layer index"
  known_risks:
    - "Overclaim detection failure means false ACCEPTED_VERIFIED verdicts are possible"
    - "No DAG ordering means downstream work can start before upstream is complete"
  evidence_paths:
    - reports/supervisor/session-resume.md
    - reports/supervisor/evidence-review.json
  recovery_steps:
    - "If autonomous_cycle.py fails: check declaration schema with sprint_executor_validate.py"
    - "If check_continuation.py returns SESSION_MISMATCH: reset_track_signal.py --track product"
    - "If stale plan lock: python -c 'import json,glob; [...]' to supersede old locks"
  resume_instructions: >
    READ plans/layers/supervisor-sprint-layer.md §36 (this section).
    The supervisor is operational. Next work is TC-SUP-001 (code-enforce lane ownership).
    Run autonomous sprint cycle normally; this layer file documents the gaps.
```

## 37. Exact Next Actions

1. **TC-SUP-001:** Add `call_overclaim_detector()` in `tools/supervisor/autonomous_cycle.py`
   after the validation phase. Uses existing `overclaim_detector.py`.
2. **TC-SUP-002:** Update `tools/supervisor/autonomous_task_generator.py` to read
   `plans/layers/index.yaml` and return `ready, dependency-valid tasks.
3. After TC-SUP-001/002: run `tests/supervisor/test_governance_validators.py` to verify.

## 38. Layer Completion Gate

```yaml
supervisor_sprint_layer_completion_gate:
  permanent_plan_exists: true
  ideal_design_complete: true
  current_state_verified: true
  current_stage_recorded: true
  maturity_justified: true
  gaps_accounted_for: true
  contracts_defined: true
  producers_verified: true
  consumers_verified: true
  skills_registered: true
  commands_registered: true
  validators_enforced: true
  tests_passed: true  # 138 governance validator tests
  negative_controls_passed: true
  handoffs_verified: false  # HO-005 pending TC-SUP-002
  recovery_verified: true
  observability_active: true
  supervisor_consumption_proven: false  # TC-SUP-002 not done yet
  cross_session_resume_proven: true
  work_logs_complete: true
  verification_current: true
  idempotency_passed: true
  audit_clean: false  # SUP-GAP-001 through SUP-GAP-004 open
  overall: GOVERNED_OPERATIONAL_GAPS_KNOWN
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (bootstrap TC-LP-001) |
