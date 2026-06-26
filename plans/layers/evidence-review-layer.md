# Evidence and Review Layer

```yaml
layer_metadata:
  layer_id: L08
  canonical_name: Evidence and Review Layer
  canonical_slug: evidence-review-layer
  permanent_plan_path: plans/layers/evidence-review-layer.md
  schema_version: "1.0"
  plan_revision: "1"
  repository_revision: "a7744cf6"
  status: GOVERNED_OPERATIONAL
  health: HEALTHY
  maturity_current: 4
  maturity_target: 4
  current_stage: GOVERNED_OPERATION
  current_owner: null
  session_id: "923e237958c1"
  active_taskcards: []
  ready_taskcards: [TC-EV-001]
  blocked_taskcards: []
  completed_taskcards: []
  dependencies: [L09, L11, L12]
  upstream_layers: [L09, L11, L12]
  downstream_layers: [L11]
  skill_ids: [build-evidence-bundle, materialize-declaration-review, evidence-review-next-prompt]
  command_ids: [build-evidence-bundle, materialize-declaration-review]
  evidence_paths:
    - .supervisor/schemas/evidence-declaration.schema.json
  last_updated_at: "2026-06-26"
  last_verified_at: "2026-06-26"
  last_verified_revision: "a7744cf6"
  next_task_id: TC-EV-001
  next_action: "Enforce provenance_chain field in all PRODUCT_SOURCE declarations (SAL-HEAL-B001)"
```

---

## 2. Authority and Purpose

Owns the evidence declaration pipeline: declaration schema, artifact inspection,
review package generation, and ZIP archival.

## 3. Scope

- `.local/evidences/<run_id>/evidence-declaration.yaml` — per-sprint declarations
- `.supervisor/schemas/evidence-declaration.schema.json` — declaration schema
- `tools/supervisor/evidence_declaration.py` — schema validation
- `tools/supervisor/inspect_declared_evidence.py` — artifact inspection
- `tools/supervisor/build_declaration_review_package.py` — review package builder
- `reports/supervisor/evidence-review.json` — grading output
- `reports/supervisor/materialized-evidence-review.md` — human summary

## 8. Ideal Production Design

1. Worker writes evidence-declaration.yaml with all required fields
2. `sprint_executor_validate.py --repair` validates and auto-fixes
3. `autonomous_cycle.py` validates schema, inspects artifacts, grades items
4. Review package built with SHA-256 for external transfer
5. `provenance_chain` field on all PRODUCT_SOURCE items (SAL-HEAL-B001)
6. `primary_layer_id` field on all PRODUCT_SOURCE items (V83 pending)

## 9. Verified Current Implementation

- Evidence declaration schema: 14 required fields
- `provenance_chain` field added (TC-LA-005) — WARN for PRODUCT_SOURCE without it
- Review packages: `.local/supervisor/reviews/<run_id>/declaration-review-package.zip`
- SHA-256 printed in worker output
- `sprint_executor_validate.py --repair` auto-corrects markdown fences, type mismatches

## 14. Gap Register

| Gap ID | Severity | Current | Target | Taskcards |
|--------|----------|---------|--------|-----------|
| EV-GAP-001 | MEDIUM | provenance_chain not widely used | All PRODUCT_SOURCE items have it | TC-EV-001 |
| EV-GAP-002 | LOW | primary_layer_id not in schema yet | V83 WARN for missing field | TC-VAL-001 |

## 29. Active Taskcards

| Task ID | Title | Status |
|---------|-------|--------|
| TC-EV-001 | Enforce provenance_chain in PRODUCT_SOURCE declarations | TODO |

## 34. Work Log

```yaml
- log_id: WL-L08-001
  layer_id: L08
  task_id: TC-LP-001
  session_id: "923e237958c1"
  timestamp: "2026-06-26T00:00:00Z"
  event_type: LAYER_FILE_CREATED
  summary: "Created evidence-review-layer.md"
```

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L08-001
  layer_id: L08
  permanent_layer_plan: plans/layers/evidence-review-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  repository_revision: a7744cf6
  current_status: GOVERNED_OPERATIONAL
  maturity_current: 4
  exact_next_task: TC-EV-001
  allowed_paths: [.local/evidences/, .supervisor/schemas/evidence-declaration.schema.json]
  forbidden_paths: [src/python/, src/net/]
  important_decisions:
    - "Always print absolute path + SHA-256 for review packages"
    - "Use --repair flag with sprint_executor_validate.py"
    - "ZIP not required for local use (only for external transfer)"
  resume_instructions: >
    Evidence layer is healthy. Declarations validated every sprint.
    Next: enforce provenance_chain field (SAL-HEAL-B001) in PRODUCT_SOURCE items.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file |
