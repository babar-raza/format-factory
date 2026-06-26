# Knowledge Discoverability Layer

```yaml
layer_metadata:
  layer_id: L23
  canonical_name: Knowledge Discoverability Layer
  canonical_slug: knowledge-discoverability-layer
  permanent_plan_path: plans/layers/knowledge-discoverability-layer.md
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
  downstream_layers: [L10, L11]
  skill_ids: [sync-memory, build-context-pack]
  command_ids: [sync-memory, build-context-pack]
  last_updated_at: "2026-06-26"
  next_task_id: TC-KNOW-001
  next_action: "Audit MEMORY.md and project-memory.md (591KB); define structured discoverability contracts"
```

## 2. Authority and Purpose

Owns structured knowledge management: MEMORY.md, project-memory.md, documentation
discoverability, and context pack construction.

**MEMORY.md size issue:** `.supervisor/project-memory.md` is 591KB — very large,
difficult to search. Needs structured organization.

## 9. Current Implementation

- `C:\Users\prora\.claude\projects\...\memory\MEMORY.md` — cross-session memory (200 line truncation)
- `.supervisor/project-memory.md` (591KB) — supervisor memory
- `/sync-memory` skill registered
- `/build-context-pack` skill registered
- Context pack: `.supervisor/context-pack.yaml`

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L23-001
  layer_id: L23
  permanent_layer_plan: plans/layers/knowledge-discoverability-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  current_status: NOT_ASSESSED
  maturity_current: 1
  exact_next_task: TC-KNOW-001
  important_decisions:
    - "MEMORY.md: lines after 200 truncated — must stay concise"
    - "project-memory.md at 591KB is unsearchable — needs restructuring"
  resume_instructions: >
    Knowledge layer not assessed. Start with /sync-memory to check current state.
    Audit project-memory.md structure. Define discoverability taxonomy.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (stub) |
