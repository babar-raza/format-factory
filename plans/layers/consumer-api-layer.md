# Consumer API Layer

```yaml
layer_metadata:
  layer_id: L19
  canonical_name: Consumer API Layer
  canonical_slug: consumer-api-layer
  permanent_plan_path: plans/layers/consumer-api-layer.md
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
  dependencies: [L06, L18]
  upstream_layers: [L06, L18]
  downstream_layers: []
  skill_ids: []
  command_ids: []
  last_updated_at: "2026-06-26"
  next_task_id: TC-CAPI-001
  next_action: "Audit __init__.py exports for all formats; define public API surface contract"
```

## 2. Authority and Purpose

Owns the external consumer API surface: what external consumers (developers using
format packages) can call. Governed by `__init__.py` exports (≤100 LOC per production standard).

## 3. Scope

- `src/python/{format}/__init__.py` — public Python API (≤100 LOC)
- `src/net/{format}/*.cs` public API classes
- API surface documentation
- Consumer examples

## 9. Current Implementation

- 20 Python `__init__.py` files (≤100 LOC per V35)
- No formal API surface documentation
- No consumer example tests
- `/add-installed-package-example` skill registered

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L19-001
  layer_id: L19
  permanent_layer_plan: plans/layers/consumer-api-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  current_status: NOT_ASSESSED
  maturity_current: 1
  exact_next_task: TC-CAPI-001
  resume_instructions: >
    Consumer API layer not assessed. First: audit all __init__.py files.
    Define API surface contract. Create consumer example tests.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (stub) |
