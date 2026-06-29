# Plan and Prompt Authority Layer

```yaml
layer_metadata:
  layer_id: L10
  canonical_name: Plan and Prompt Authority Layer
  canonical_slug: plan-prompt-authority-layer
  permanent_plan_path: plans/layers/plan-prompt-authority-layer.md
  schema_version: "1.0"
  plan_revision: "1"
  repository_revision: "a7744cf6"
  status: HARDENING_REQUIRED
  health: DEGRADED
  maturity_current: 3
  maturity_target: 4
  current_stage: PLAN_HARDENING
  current_owner: null
  session_id: "923e237958c1"
  active_taskcards: []
  ready_taskcards: [TC-PLAN-001]
  blocked_taskcards: []
  completed_taskcards: []
  dependencies: []
  upstream_layers: []
  downstream_layers: [L11, L12, L13]
  skill_ids: [plan-hardening, build-context-pack, export-plan-context]
  command_ids: [plan-hardening, build-context-pack, export-plan-context]
  evidence_paths:
    - plans/master-plan.md
    - plans/strategic/spec-to-feature-radical-correction-plan.md
  last_updated_at: "2026-06-26"
  last_verified_at: null
  next_task_id: TC-PLAN-001
  next_action: "Consolidate 6 hardening addenda into canonical plan files; create plans/layers/ as permanent authority"
```

---

## 2. Authority and Purpose

Owns all plan files and prompt authority:
- `plans/master-plan.md` (v6.0) — strategic authority
- `plans/strategic/spec-to-feature-radical-correction-plan.md` — lane architecture (27 sections, ~3200 lines)
- `plans/.claude/` — per-chat plan files (migrated from external)
- `CLAUDE.md` — session instructions (highest authority)
- `AGENTS.md` — agent governance
- `plans/layers/` — permanent layer control plane (NEW, this bootstrap)

## 3. Scope

- `plans/` root — all plan files
- `plans/.claude/` — per-chat plans (locked with write_plan_lock.py)
- `CLAUDE.md` — session instructions
- `AGENTS.md` — agent governance
- `.claude/commands/` — command definitions
- `plans/layers/` — permanent layer control plane (this layer owns it)

## 8. Ideal Production Design

1. **Single authority per topic:** No duplicate plans for same concern
2. **No hardening addenda fragmentation:** addenda merged into canonical files after 30 days
3. **Per-chat plans in-repo:** plans/.claude/ with plan lock
4. **Layer control plane:** plans/layers/ (created this session)
5. **Task register drives work selection:** plans/layers/task-register.yaml consulted by supervisor

## 9. Verified Current Implementation

- 16+ plan files in plans/ root
- 6 hardening addenda (authority fragmentation — PLAN-GAP-001)
- `plans/.claude/.gitkeep` + `glistening-leaping-chipmunk.md` in per-chat directory
- CLAUDE.md: comprehensive session instructions (Step 0 through §39)
- AGENTS.md: agent governance (§AG1-AG4)
- `plans/strategic/spec-to-feature-radical-correction-plan.md`: master correction authority
- `plans/master-plan.md` v6.0: project master plan
- `plans/layers/` — NEW (this session)

## 14. Gap Register

| Gap ID | Severity | Current | Target | Taskcards |
|--------|----------|---------|--------|-----------|
| PLAN-GAP-001 | MEDIUM | 6 hardening addenda create authority fragmentation | Addenda merged into canonical plans | TC-PLAN-001 |
| PLAN-GAP-002 | LOW | Supervisor doesn't read plans/layers/task-register.yaml | Supervisor consumes layer task register | TC-SUP-002 |

## 17. Schemas and Contracts

Per-chat plan lifecycle:
1. External plan at `~/.claude/plans/<name>.md` → copy to `plans/.claude/<name>.md`
2. Lock: `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/<name>.md`
3. Work through all taskcards
4. Close: `write_plan_lock.py --terminal` → status=TERMINAL_CLOSED → STOP
5. `--complete` is NOT equivalent to `--terminal` for in-session use

## 20. Skills and Commands

| Skill | Purpose |
|-------|---------|
| /plan-hardening | Harden a plan against gaps found in audit |
| /build-context-pack | Build supervisor context pack |
| /export-plan-context | Export plan context for handoff |

## 29. Active Taskcards

| Task ID | Title | Status |
|---------|-------|--------|
| TC-PLAN-001 | Consolidate 6 hardening addenda into canonical plan files | TODO |

## 34. Work Log

```yaml
- log_id: WL-L10-001
  layer_id: L10
  task_id: TC-LP-001
  session_id: "923e237958c1"
  timestamp: "2026-06-26T00:00:00Z"
  event_type: LAYER_FILE_CREATED
  summary: "Created plan-prompt-authority-layer.md; plans/layers/ bootstrap completed"
```

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L10-001
  layer_id: L10
  permanent_layer_plan: plans/layers/plan-prompt-authority-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  repository_revision: a7744cf6
  current_status: HARDENING_REQUIRED
  maturity_current: 3
  exact_next_task: TC-PLAN-001
  why_this_is_next: >
    6 hardening addenda create authority fragmentation. When content is spread
    across addenda, assistants may read only the canonical plan and miss critical
    decisions in addenda.
  allowed_paths: [plans/]
  forbidden_paths: [src/python/, src/net/]
  important_decisions:
    - "plans/strategic/snoopy-juggling-seal.md is SAL FORENSICS PLAN — do NOT use for general amendments"
    - "Per-chat plans: use --terminal (NOT --complete) for in-session closure"
    - "plans/layers/ is now the permanent layer control plane — owned by this layer (L10)"
    - "taskcard-work-queue-layer MERGED into this layer (DEC-015)"
  unresolved_findings:
    - "PLAN-GAP-001: 6 hardening addenda not merged"
    - "PLAN-GAP-002: supervisor doesn't read task-register.yaml"
  resume_instructions: >
    Plan authority layer is functional. 16+ plans operational.
    Next: TC-PLAN-001 — audit and merge 6 hardening addenda.
    Read each addendum, identify durable content, migrate to canonical plans.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file; plans/layers/ bootstrap |
