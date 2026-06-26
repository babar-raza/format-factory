# Security and Legal Layer

```yaml
layer_metadata:
  layer_id: L20
  canonical_name: Security and Legal Layer
  canonical_slug: security-legal-layer
  permanent_plan_path: plans/layers/security-legal-layer.md
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
  downstream_layers: [L18, L21]
  skill_ids: []
  command_ids: []
  last_updated_at: "2026-06-26"
  next_task_id: TC-SEC-001
  next_action: "Audit legal_category in format-registry.yaml; ensure all formats score legal_safety 30/30"
```

## 2. Authority and Purpose

Owns legal category classification and security analysis for all formats.
The `registry/format-registry.yaml` contains `legal_safety` scores (max 30/30).
Gate 8 requires legal safety clearance before commercial release.

## 9. Current Implementation

- `registry/format-registry.yaml`: legal_category, legal_safety, spec_availability per format
- FODS: legal_safety 30/30 (OASIS royalty-free, legal_category 1)
- No formal security audit process for format parsers
- OWASP considerations: format parsers (XXE, zip bomb, etc.) not systematically assessed

## 14. Gap Register

| Gap ID | Severity | Current | Target | Status |
|--------|----------|---------|--------|--------|
| SEC-GAP-001 | MEDIUM | No formal security audit of format parsers | Security audit complete | TODO |
| SEC-GAP-002 | LOW | Legal categories not assessed for all 24 formats | All 24 formats scored | TODO |

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L20-001
  layer_id: L20
  permanent_layer_plan: plans/layers/security-legal-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  current_status: NOT_ASSESSED
  maturity_current: 1
  exact_next_task: TC-SEC-001
  resume_instructions: >
    Security/legal layer not assessed. Start with registry/format-registry.yaml audit.
    Check legal_safety scores for all formats. Identify any missing or low scores.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (stub) |
