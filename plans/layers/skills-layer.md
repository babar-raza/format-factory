# Skills Layer

```yaml
layer_metadata:
  layer_id: L13
  canonical_name: Skills Layer
  canonical_slug: skills-layer
  permanent_plan_path: plans/layers/skills-layer.md
  schema_version: "1.0"
  plan_revision: "1"
  repository_revision: "a7744cf6"
  status: GOVERNED_OPERATIONAL
  health: HEALTHY
  maturity_current: 4
  maturity_target: 5
  current_stage: GOVERNED_OPERATION
  current_owner: null
  agent_type: null
  session_id: "923e237958c1"
  active_sprint: "lp-bootstrap"
  active_taskcards: []
  ready_taskcards: [TC-SKILL-001]
  blocked_taskcards: []
  completed_taskcards: []
  dependencies: []
  upstream_layers: []
  downstream_layers: [L11]
  skill_ids:
    - check-skill-coverage
    - sync-skill-command-registry
    - normalize-skill-registry
    - inventory-skills
    - enforce-skill-first-execution
    - validate-skill-transcript
    - collect-skill-execution-receipts
    - preflight-skill-entry
    - detect-duplicate-skills
    - run-skill-idempotency
  command_ids:
    - check-skill-coverage
    - sync-skill-command-registry
    - normalize-skill-registry
    - inventory-skills
    - enforce-skill-first-execution
    - validate-skill-transcript
  evidence_paths:
    - .supervisor/skill-registry.yaml
    - .supervisor/skill-inventory.yaml
    - .supervisor/skill-quality-matrix.yaml
  last_started_at: null
  last_progress_at: "2026-06-26"
  last_updated_at: "2026-06-26"
  last_verified_at: "2026-06-26"
  last_verified_revision: "a7744cf6"
  next_task_id: TC-SKILL-001
  next_action: "Register 19 layer-maintenance micro-skills in .supervisor/skill-registry.yaml"
  handoff_id: null
```

---

## 1. Layer Metadata

See YAML block above.

## 2. Authority and Purpose

The Skills Layer governs **how work is executed** in Format Factory. It owns:

- The skill registry (`.supervisor/skill-registry.yaml`, 74 registered skills)
- The command inventory (`.supervisor/command-inventory.yaml`, 72 commands)
- The skill-first execution policy (`.supervisor/skill-first-policy.md`)
- The skill quality matrix (`.supervisor/skill-quality-matrix.yaml`)
- All `.claude/commands/*.md` command definition files
- Skill gap tracking (5 open gaps: SKILL-GAP-003, 008, 009, 010, 011)
- 19 layer-maintenance micro-skills (pending TC-SKILL-001)

**Key principle:** Every governed task must be executed through a registered skill.
Direct mutation is prohibited. No skill = no execution.

## 3. Scope

- `.supervisor/skill-registry.yaml`
- `.supervisor/skill-inventory.yaml`
- `.supervisor/skill-quality-matrix.yaml`
- `.supervisor/skill-execution-receipt-index.yaml`
- `.supervisor/skill-command-registry-sync-report.yaml`
- `.supervisor/skill-contract-validation-results.yaml`
- `.supervisor/skill-system-baseline.yaml`
- `.supervisor/command-inventory.yaml`
- `.supervisor/skill-first-policy.md`
- `.claude/commands/*.md` (all command definition files)

## 4. Explicit Non-Scope

- Does NOT execute the sprint cycle (L11)
- Does NOT define validators (L12)
- Does NOT govern plan content (L10)
- Does NOT contain product source (L06)

## 5. Owned Decisions

- Which skills are canonical vs. deprecated
- Skill gap tracking (SKILL-GAP-NNN)
- Skill idempotency requirements
- Skill-first enforcement policy
- Analytics rotation suspension (2026-06-18)

## 6. Upstream Inputs

- Task definitions from L10 (plan authority) — determine what capabilities are needed
- L12 (validation policy) — V46 skill_transcript_present enforcement

## 7. Downstream Consumers

- L11 (supervisor) — reads skill registry to verify skill invocations
- Every product sprint — must invoke registered skills before mutating source

## 8. Ideal Production Design

The ideal skills layer:

1. **Complete registry:** Every governed capability has exactly one registered skill
2. **Zero gaps:** All SKILL-GAP-NNN are closed
3. **Transcript verification:** V46 FAIL-level (not WARN) — all skill invocations logged
4. **Layer-maintenance skills:** 19 micro-skills for layer plan management
5. **Idempotency proofs:** Every skill proven idempotent
6. **Command synchronization:** skill-registry.yaml and command-inventory.yaml always in sync
7. **Coverage metrics:** skill-quality-matrix.yaml current with all skills rated

## 9. Verified Current Implementation

```yaml
current_layer_implementation:
  registry_paths:
    - .supervisor/skill-registry.yaml  # 74 skills, registry_id: r98-governed-skills-expanded
    - .supervisor/skill-inventory.yaml
    - .supervisor/command-inventory.yaml  # 72 commands
    - .supervisor/skill-quality-matrix.yaml
  active_components:
    - 74 skill registrations (71 active, 3 deprecated)
    - 72 command entries
    - Skill-first execution policy (skill-first-policy.md)
    - V46 skill_transcript_present (WARN-only)
  partially_implemented_components:
    - transcript_verification: installed but V46 is WARN-only (TC-SKILL-GOV-002)
    - skill_invocation_receipt: infrastructure exists but not consistently used
  missing_components:
    - SKILL-GAP-003: capability_compiler (Lane 3, no skill yet)
    - SKILL-GAP-008: pre_sprint_governance_hook (GOV_BLOCK pre-check)
    - SKILL-GAP-009: ci_transcript_verification (CI enforcement)
    - SKILL-GAP-010: supervision_audit (Lane 14)
    - SKILL-GAP-011: rollback_and_recovery (recovery protocol)
    - SKILL-GAP-012: 19 layer-maintenance micro-skills (TC-SKILL-001)
  deprecated_skills:
    - add-analytics-function (SUSPENDED 2026-06-18, rotation permanently suspended)
  bypass_paths:
    - V46 WARN means skill invocations can be skipped without FAIL
```

## 10. Current Execution Stage

**GOVERNED_OPERATION** — 74 skills registered, 72 commands, skill-first policy active.
Key gap: 19 layer-maintenance micro-skills missing, 5 SKILL-GAPs open.

## 11. Current Maturity Assessment

**LEVEL 4 — GOVERNED**

Justification:
- 74 skills registered
- Skill-first policy documented
- skill-quality-matrix.yaml maintained
- Command-registry sync reports

Gap preventing L5:
- V46 WARN (not FAIL) — transcript enforcement incomplete
- SKILL-GAP-003/008/009/010/011 open
- 19 layer-maintenance micro-skills missing

## 12. Target Maturity

**LEVEL 5 — PRODUCTION AUTHORITY**

Required:
- All SKILL-GAPs closed
- V46 upgraded to FAIL
- 19 layer-maintenance micro-skills registered and proven idempotent

## 13. Current Strengths

- 74 skills covering all major product operations
- Skill quality matrix for ongoing assessment
- Analytics rotation correctly suspended with governance record
- Idempotency proofs for core skills

## 14. Gap Register

| Gap ID | Severity | Current State | Target State | Root Cause | Taskcards |
|--------|----------|---------------|--------------|------------|-----------|
| SKILL-GAP-003 | CRITICAL | capability_compiler not implemented | /capability-compiler skill | Lane 3 not started | TC-FEAT-001 |
| SKILL-GAP-008 | HIGH | pre_sprint_governance_hook missing | Pre-sprint GOV_BLOCK check | GOV_BLOCK added after skill design | TBD |
| SKILL-GAP-009 | HIGH | ci_transcript_verification missing | CI verifies skill transcripts | CI not integrated | TBD |
| SKILL-GAP-010 | HIGH | supervision_audit missing | Lane 14 audit skill | Lane 14 not started | TBD |
| SKILL-GAP-011 | MEDIUM | rollback_and_recovery missing | /rollback-and-recovery skill | Recovery protocol informal | TBD |
| SKILL-GAP-012 | HIGH | 19 layer-maintenance micro-skills missing | All 19 registered | Layer control plane just created | TC-SKILL-001 |

## 15. Root-Cause Register

- **SKILL-GAP-012:** plans/layers/ did not exist before this bootstrap session. Layer maintenance operations (identify-primary-layer, update-layer-current-state, etc.) had no canonical targets. All 19 skills can now be designed against the permanent layer plan files.

## 16. Repair Architecture

**TC-SKILL-001 — Register 19 layer-maintenance micro-skills:**

Each skill block in `.supervisor/skill-registry.yaml` needs:
```yaml
- skill_id: identify-primary-layer
  command: /identify-primary-layer
  description: "Given a task description, return the primary layer_id and permanent plan path"
  scope: [L10, L11, L12, L13]
  capability: layer_classification
  idempotent: true
  advisory_only: false
  spec_qname_required: false
  ...
```

19 skills to register:
1. identify-primary-layer
2. create-permanent-layer-plan
3. update-layer-current-state
4. update-layer-target-design
5. update-layer-stage
6. update-layer-maturity
7. register-layer-gap
8. register-layer-task
9. append-layer-work-log
10. append-layer-verification-log
11. update-layer-session-handoff
12. update-layer-master-index
13. reconcile-layer-index
14. reconcile-layer-task-register
15. create-cross-layer-handoff
16. detect-unlogged-work
17. detect-stale-layer-state
18. migrate-temporary-agent-plan
19. validate-permanent-layer-plans
20. select-next-layer-task (bonus: 20th)

## 17. Schemas and Contracts

- `.supervisor/schemas/skill-registry.schema.json` — skill entry schema
- `.supervisor/skill-first-policy.md` — mandatory skill-first execution rules
- `.supervisor/skill-system-baseline.yaml` — skill system baseline metrics

## 18. Producers

- Sprint workers register new skills when capabilities are needed
- Skill registry sync tool keeps command-inventory.yaml in sync

## 19. Consumers

- L11 (supervisor) reads skill-registry.yaml to verify skill invocations in declarations
- V46 checks for skill transcript presence

## 20. Skills and Commands

Self-referential: this layer's own micro-skills are the gap (TC-SKILL-001).

Core governance skills currently registered:
- `/check-skill-coverage` — audit skill coverage
- `/sync-skill-command-registry` — sync registry and command inventory
- `/normalize-skill-registry` — clean up registry format
- `/inventory-skills` — list all skills
- `/enforce-skill-first-execution` — verify skill-first policy
- `/validate-skill-transcript` — verify skill invocation logs

## 21. Validators and Enforcement

- V46: `skill_transcript_present` — WARN if skill invocation not logged
- Skill-first policy: every mutation must have a skill invocation receipt

## 22. Tests and Negative Controls

- `.supervisor/skill-idempotency-proof.yaml` — idempotency proofs
- `.supervisor/skill-contract-validation-results.yaml` — contract results
- Test: running same skill twice produces same result (idempotency)
- Negative: attempt mutation without skill invocation → V46 WARN fires

## 23. Evidence and Observability

- `.supervisor/skill-execution-receipt-index.yaml` — indexed receipts
- `.supervisor/skill-quality-matrix.yaml` — quality ratings
- `.supervisor/skill-command-registry-sync-report.yaml` — sync status
- `.supervisor/ad-hoc-execution-inventory.yaml` — detected bypasses

## 24. Recovery and Rollback

- Deprecated skills remain in registry with `status: deprecated` — never deleted
- SKILL-GAP entries are never closed without a registered skill + tests + idempotency proof
- Analytics rotation suspension is permanent and recorded in decision log

## 25. Security and Compliance

- Skill-first policy prevents ad-hoc mutations that bypass governance
- `.supervisor/residual-bypass-report.yaml` tracks known bypasses

## 26. Cross-Layer Handoffs

| Handoff | From | To | Artifact |
|---------|------|----|---------|
| HO-007 | L13 | L11 | 19 new layer maintenance skills in skill-registry.yaml |

## 27. Migration and Backfill

When TC-SKILL-001 registers 19 new skills, corresponding `.claude/commands/*.md`
files must be created for each. Pattern: copy an existing command file and adapt.
No migration of existing skills required (append-only).

## 28. Effort and Dependencies

- TC-SKILL-001: ~6 hours. Depends on TC-LP-001 (layer files must exist to write skills against).
- SKILL-GAP-003 (capability_compiler): depends on TC-FEAT-001 (L14 design first).

## 29. Active Taskcards

| Task ID | Title | Status | Priority |
|---------|-------|--------|---------|
| TC-SKILL-001 | Register 19 layer-maintenance micro-skills | TODO | P1 |

## 30. Ready Taskcards

TC-SKILL-001 — READY (TC-LP-001 near completion; layer files being created).

## 31. Completed Taskcards

(None in this session)

## 32. Blocked and Waiting Work

- SKILL-GAP-003: blocked on TC-FEAT-001 (feature compiler design)
- SKILL-GAP-009: blocked on CI integration

## 33. Decision Log

| Decision | Date | Rationale |
|----------|------|-----------|
| Analytics rotation SUSPENDED | 2026-06-18 | keen-dancing-hopper plan; no new mod_prime functions |
| V46 remains WARN | Pre-existing | Transcript infrastructure incomplete |
| Deprecated skills kept in registry | Pre-existing | Audit trail, prevent re-creation |
| add-analytics-function DEPRECATED | 2026-06-18 | Rotation permanently suspended |

## 34. Work Log

```yaml
- log_id: WL-L13-001
  layer_id: L13
  task_id: TC-LP-001
  session_id: "923e237958c1"
  sprint_id: lp-bootstrap
  timestamp: "2026-06-26T00:00:00Z"
  event_type: LAYER_FILE_CREATED
  summary: "Created skills-layer.md permanent plan file"
  repository_revision: a7744cf6
  changed_paths: [plans/layers/skills-layer.md]
  current_stage: GOVERNED_OPERATION
  status: IN_PROGRESS
  next_action: "Execute TC-SKILL-001 to register 19 layer-maintenance micro-skills"
```

## 35. Verification Log

```yaml
- verification_id: VER-L13-001
  layer_id: L13
  task_id: null
  repository_revision: a7744cf6
  contracts_verified:
    - "74 skills registered in skill-registry.yaml"
    - "72 commands in command-inventory.yaml"
    - "skill-first-policy.md exists"
    - "skill-quality-matrix.yaml maintained"
    - "ad-hoc-execution-inventory.yaml tracks bypasses"
  focused_result: PASS
  verdict: VERIFIED
  verified_at: "2026-06-26"
  verifier: forensic-layer-discovery-report.md
```

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L13-001
  layer_id: L13
  permanent_layer_plan: plans/layers/skills-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  repository_revision: a7744cf6
  current_status: GOVERNED_OPERATIONAL
  current_stage: GOVERNED_OPERATION
  maturity_current: 4
  exact_next_task: TC-SKILL-001
  why_this_is_next: >
    19 layer-maintenance micro-skills are the primary gap. Without them, layer
    plan maintenance (update-layer-current-state, append-layer-work-log, etc.)
    has no canonical skill execution path — violating the skill-first policy.
  ready_tasks: [TC-SKILL-001]
  blocked_tasks: [SKILL-GAP-003, SKILL-GAP-009]
  allowed_paths:
    - .supervisor/skill-registry.yaml
    - .claude/commands/
  forbidden_paths:
    - src/python/
    - src/net/
  required_verification:
    - "All 19 skills appear in .supervisor/skill-registry.yaml"
    - "Corresponding .claude/commands/*.md files exist"
    - "sync-skill-command-registry runs clean"
  unresolved_findings:
    - "SKILL-GAP-003 through SKILL-GAP-012: 6 open gaps"
  resume_instructions: >
    READ this file §14 Gap Register for SKILL-GAP details.
    Execute TC-SKILL-001: append 19 skill blocks to .supervisor/skill-registry.yaml.
    Create corresponding .claude/commands/*.md files.
    Run /sync-skill-command-registry to verify sync.
```

## 37. Exact Next Actions

1. Append 19 skill blocks to `.supervisor/skill-registry.yaml` (append only, never replace)
2. Create `.claude/commands/identify-primary-layer.md` (and 18 others)
3. Run `/sync-skill-command-registry` to verify registry and command inventory are in sync
4. Update this file §9 `active_components` and §29 `completed_taskcards`

## 38. Layer Completion Gate

```yaml
skills_layer_completion_gate:
  permanent_plan_exists: true
  all_skill_gaps_closed: false  # 6 open SKILL-GAPs
  19_layer_maintenance_skills_registered: false  # TC-SKILL-001 pending
  v46_upgraded_to_fail: false  # pending transcript infrastructure
  idempotency_proven: false  # pending TC-SKILL-001
  overall: GOVERNED_OPERATIONAL_GAPS_KNOWN
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (bootstrap TC-LP-001) |
