# Recovery and Rollback Layer

```yaml
layer_metadata:
  layer_id: L25
  canonical_name: Recovery and Rollback Layer
  canonical_slug: recovery-rollback-layer
  permanent_plan_path: plans/layers/recovery-rollback-layer.md
  schema_version: "1.0"
  plan_revision: "1"
  repository_revision: "a7744cf6"
  status: NOT_ASSESSED
  health: UNKNOWN
  maturity_current: 1
  maturity_target: 3
  current_stage: DISCOVERY
  current_owner: null
  session_id: "923e237958c1"
  dependencies: []
  upstream_layers: []
  downstream_layers: [L11]
  skill_ids: [rollback-and-recovery]
  command_ids: [rollback-and-recovery]
  last_updated_at: "2026-06-26"
  next_task_id: TC-REC-001
  next_action: "Define rollback protocol per CLAUDE.md §GOV_BLOCK; close SKILL-GAP-011"
```

## 2. Authority and Purpose

Owns recovery and rollback protocols: GOV_BLOCK recovery, stale plan lock recovery,
context exhaustion recovery, destructive operation safeguards.

## 9. Current Implementation

- `CLAUDE.md §GOV_BLOCK Exception` defines structural failure recovery
- `/rollback-and-recovery` skill registered but SKILL-GAP-011 (no implementation)
- Stale plan lock recovery: supersede with SUPERSEDED status
- Cross-window recovery: read session-resume.md and continue
- No formal rollback protocol document

## 14. Gap Register

| Gap ID | Severity | Current | Target | Status |
|--------|----------|---------|--------|--------|
| REC-GAP-001 | HIGH | SKILL-GAP-011: rollback-and-recovery skill has no implementation | /rollback-and-recovery implemented | TODO |
| REC-GAP-002 | MEDIUM | No formal rollback protocol document | docs/automation/rollback-protocol.md | TODO |

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L25-001
  layer_id: L25
  permanent_layer_plan: plans/layers/recovery-rollback-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  current_status: NOT_ASSESSED
  maturity_current: 1
  exact_next_task: TC-REC-001
  important_decisions:
    - "GOV_BLOCK: analytics separation required; do NOT skip (binding override of Supreme Directive)"
    - "Stale lock recovery: set status=SUPERSEDED (not delete, not re-lock)"
    - "Destructive operations require explicit policy authority + rollback path"
  resume_instructions: >
    Recovery layer not assessed. First: close SKILL-GAP-011 by implementing /rollback-and-recovery.
    Write docs/automation/rollback-protocol.md documenting all recovery scenarios.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (stub) |
