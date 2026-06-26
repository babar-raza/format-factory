# Provenance and Artifact Identity Layer

```yaml
layer_metadata:
  layer_id: L26
  canonical_name: Provenance and Artifact Identity Layer
  canonical_slug: provenance-artifact-identity-layer
  permanent_plan_path: plans/layers/provenance-artifact-identity-layer.md
  schema_version: "1.0"
  plan_revision: "1"
  repository_revision: "a7744cf6"
  status: NOT_ASSESSED
  health: UNKNOWN
  maturity_current: 2
  maturity_target: 4
  current_stage: DISCOVERY
  current_owner: null
  session_id: "923e237958c1"
  dependencies: [L08]
  upstream_layers: [L08]
  downstream_layers: [L11]
  skill_ids: [build-evidence-bundle]
  command_ids: [build-evidence-bundle]
  last_updated_at: "2026-06-26"
  next_task_id: TC-PROV-001
  next_action: "Enforce provenance_chain field in all PRODUCT_SOURCE declarations (SAL-HEAL-B001)"
```

## 2. Authority and Purpose

Owns the traceability chain from product change to spec fact:
- `provenance_chain` field: fact_id + section_ref + page_ref + source_sha256
- SHA-256 tracking for review packages
- Artifact identity (review package ZIPs, evidence bundles)

## 9. Current Implementation

- `provenance_chain` field added to evidence-declaration.schema.json (TC-LA-005)
- V-NEW-002: WARN for READINESS items without provenance_chain
- SHA-256 printed in worker output for review packages
- Not widely used yet (SAL-HEAL-B001 advisory)

## 14. Gap Register

| Gap ID | Severity | Current | Target | Status |
|--------|----------|---------|--------|--------|
| PROV-GAP-001 | MEDIUM | provenance_chain not widely used | All PRODUCT_SOURCE items have it | SAL-HEAL-B001 advisory now |
| PROV-GAP-002 | LOW | No artifact identity registry | Artifacts tracked by SHA-256 | TODO |

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L26-001
  layer_id: L26
  permanent_layer_plan: plans/layers/provenance-artifact-identity-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  current_status: NOT_ASSESSED
  maturity_current: 2
  exact_next_task: TC-PROV-001
  important_decisions:
    - "provenance_chain: fact_id + section_ref + page_ref + source_sha256"
    - "SAL-HEAL-B001: advisory now; becomes required when workbench coverage ≥80%"
    - "V-NEW-002 fires WARN for READINESS items without provenance"
  resume_instructions: >
    Provenance layer partially implemented (schema field exists, advisory enforcement).
    Next: enforce provenance_chain for all new PRODUCT_SOURCE declarations.
    Coordinate with L01 (SAL) to ensure spec facts have section_ref and page_ref.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (stub) |
