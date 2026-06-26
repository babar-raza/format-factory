# Regression Compatibility Layer

```yaml
layer_metadata:
  layer_id: L17
  canonical_name: Regression Compatibility Layer
  canonical_slug: regression-compatibility-layer
  permanent_plan_path: plans/layers/regression-compatibility-layer.md
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
  dependencies: [L06, L07]
  upstream_layers: [L06, L07]
  downstream_layers: [L18]
  skill_ids: []
  command_ids: []
  last_updated_at: "2026-06-26"
  next_task_id: TC-REG-001
  next_action: "Define compatibility matrix per format; audit existing regression test coverage"
```

## 2. Authority and Purpose

Owns backward compatibility guarantees and regression testing: ensuring format packages
don't break existing consumer code across versions.

## 9. Current Implementation

- No formal compatibility matrix exists
- Regression tests co-located with unit tests in tests/python/{format}/
- No semver policy for format packages

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L17-001
  layer_id: L17
  permanent_layer_plan: plans/layers/regression-compatibility-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  current_status: NOT_ASSESSED
  maturity_current: 1
  exact_next_task: TC-REG-001
  resume_instructions: >
    Regression layer not assessed. First: audit tests/ for regression-specific tests.
    Define compatibility matrix. Create semver policy for format packages.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (stub) |
