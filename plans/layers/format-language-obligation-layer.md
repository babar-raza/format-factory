# Format Language Obligation Layer

```yaml
layer_metadata:
  layer_id: L27
  canonical_name: Format Language Obligation Layer
  canonical_slug: format-language-obligation-layer
  permanent_plan_path: plans/layers/format-language-obligation-layer.md
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
  dependencies: [L01, L05]
  upstream_layers: [L01, L05]
  downstream_layers: [L06]
  skill_ids: [build-obligation-register, update-obligation-entry, verify-obligation-entry]
  command_ids: [build-obligation-register, update-obligation-entry, verify-obligation-entry]
  last_updated_at: "2026-06-26"
  next_task_id: TC-OBL-001
  next_action: "Define per-format language obligation registry; link V82 oracle obligations to this layer"
```

## 2. Authority and Purpose

Owns per-format specification obligations: what MUST be implemented per spec
for each format. This is distinct from L01 (raw facts) and L05 (conformance testing).

**Key artifacts:**
- `oracle/registry/format-oracle-registry.yaml` — current oracle obligation tracking
- V82: `validate_oracle_obligations` — enforces OBLIGATION_CREATED lifecycle

## 3. Scope

- Per-format obligation registry (to be formalized)
- V82 oracle obligation enforcement
- `/build-obligation-register`, `/update-obligation-entry`, `/verify-obligation-entry` skills

## 9. Current Implementation

- Oracle lifecycle (OBLIGATION_CREATED → VERIFIED) tracks conformance obligations
- V82 validator enforces oracle obligations per format
- `/build-obligation-register` and related skills registered
- No formal obligation register document (beyond oracle-package.yaml)

## 14. Gap Register

| Gap ID | Severity | Current | Target | Status |
|--------|----------|---------|--------|--------|
| OBL-GAP-001 | MEDIUM | No formal obligation register | registry/obligation-register.yaml | TC-OBL-001 |
| OBL-GAP-002 | MEDIUM | 4 formats at OBLIGATION_CREATED (no products) | All formats at VERIFIED | Waiting for products |

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L27-001
  layer_id: L27
  permanent_layer_plan: plans/layers/format-language-obligation-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  current_status: NOT_ASSESSED
  maturity_current: 1
  exact_next_task: TC-OBL-001
  important_decisions:
    - "V82 oracle obligations validator enforces OBLIGATION_CREATED lifecycle"
    - "ora/pam/xpm/zpaq: OBLIGATION_CREATED but no products yet"
    - "Oracle lifecycle: OBLIGATION_CREATED → SCAFFOLDED → AUTHORITY_MAPPED → CASES_DEFINED → VERIFIED"
  resume_instructions: >
    Format obligation layer not assessed. Start by reading oracle/registry/format-oracle-registry.yaml.
    Map V82 obligation enforcement to this layer formally.
    Create /build-obligation-register skill invocation to generate obligation register.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (stub) |
