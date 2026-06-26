# Product Output Dogfood Layer

```yaml
layer_metadata:
  layer_id: L16
  canonical_name: Product Output Dogfood Layer
  canonical_slug: product-output-dogfood-layer
  permanent_plan_path: plans/layers/product-output-dogfood-layer.md
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
  dependencies: [L06]
  upstream_layers: [L06]
  downstream_layers: [L19]
  skill_ids: [add-dogfood-export, verify-dogfood-path]
  command_ids: [add-dogfood-export, verify-dogfood-path]
  last_updated_at: "2026-06-26"
  next_task_id: TC-DOG-001
  next_action: "Audit dogfood export pipeline; verify /add-dogfood-export skill coverage for all formats"
```

## 2. Authority and Purpose

Owns the dogfood export pipeline: format package → export transformation → dogfood artifact.
The `/add-dogfood-export` skill (advisory_only=true) and `/verify-dogfood-path` skill govern this.

## 3. Scope

- `{format}_to_{target}.py` export files in `src/python/{format}/export/`
- `/add-dogfood-export` skill
- `/verify-dogfood-path` skill
- Dogfood output directory (to be determined)

## 9. Current Implementation

- `/add-dogfood-export` skill registered (advisory_only=true)
- `/verify-dogfood-path` skill registered
- Export files exist for some formats in `src/python/{format}/export/`
- No formal dogfood output directory or governance

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L16-001
  layer_id: L16
  permanent_layer_plan: plans/layers/product-output-dogfood-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  current_status: NOT_ASSESSED
  maturity_current: 1
  exact_next_task: TC-DOG-001
  resume_instructions: >
    Dogfood layer not assessed. Start with /verify-dogfood-path to see current state.
    Then audit which formats have export/ files.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (stub) |
