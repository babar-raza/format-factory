# Capability Layer

```yaml
layer_metadata:
  layer_id: L03
  canonical_name: Capability Layer
  canonical_slug: capability-layer
  permanent_plan_path: plans/layers/capability-layer.md
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
  ready_taskcards: [TC-CAP-001]
  blocked_taskcards: []
  completed_taskcards: []
  dependencies: [L01, L02]
  upstream_layers: [L01, L02]
  downstream_layers: [L14, L06]
  skill_ids: [build-capability-routes, update-capability-matrix]
  command_ids: [build-capability-routes, update-capability-matrix]
  evidence_paths:
    - reports/capability-layer/gap-ledger.json
    - reports/capability-layer/gap-sal-traceability-20260626.json
  last_updated_at: "2026-06-26"
  last_verified_at: null
  next_task_id: TC-CAP-001
  next_action: "Wire gap-ledger.json to autonomous task generator; replace hardcoded _EXPANSION_GOALS"
```

---

## 1-4. Identity, Authority, Scope, Non-Scope

**Authority:** The canonical map of format capabilities (what each format can do)
and the gap ledger (which capabilities are missing or incomplete).

**Scope:**
- `tools/capability_layer/capability_map_generator.py`
- `tools/capability_layer/capability_to_feature_compiler.py` (planning tool only)
- `tools/capability_layer/validate_capability_map.py`
- `reports/capability-layer/gap-ledger.json` (1,242 entries, 96.8% closed)
- `reports/capability-layer/gap-sal-traceability-20260626.json`

**Non-Scope:** Does NOT own the feature compiler pipeline (L14), does NOT own product source (L06).

**CRITICAL NOTE:** `tools/capability_layer/capability_to_feature_compiler.py` is a
PLANNING TOOL (produces taskcard stubs). The canonical PIPELINE tool is
`tools/supervisor/capability_feature_compiler.py`. These are NOT interchangeable.

## 5. Owned Decisions

- Gap severity classifications
- Capability taxonomy per format family
- Gap closure criteria

## 8. Ideal Production Design

1. `capability_map_generator.py` generates capability records from QName registry
2. Each capability record cites spec_fact_refs from L01 SAL
3. `gap-ledger.json` is the authoritative gap register — read by autonomous task generator
4. Task generator reads gap-ledger.json instead of hardcoded _EXPANSION_GOALS
5. Gap closure drives product deepening work selection

## 9. Verified Current Implementation

- 1,242 gap entries in gap-ledger.json (1,203 closed = 96.8%)
- 39 open gaps
- **CRITICAL DISCONNECT:** capabilities generated but task generator uses hardcoded
  `_EXPANSION_GOALS` (~100 entries) instead of reading gap-ledger.json
- `capability_to_feature_compiler.py` produces taskcard stubs (advisory, not pipeline)

## 10-11. Stage / Maturity

**PLAN_HARDENING** / **LEVEL 3 — OPERATIONAL**

Critical gap: capability pipeline generates output that nobody consumes.
The task generator bypass (hardcoded _EXPANSION_GOALS) is a systemic root cause.

## 14. Gap Register

| Gap ID | Severity | Current | Target | Root Cause | Taskcards |
|--------|----------|---------|--------|------------|-----------|
| CAP-GAP-001 | CRITICAL | Task generator uses hardcoded goals, ignores gap-ledger.json | gap-ledger.json drives all task selection | Autonomous task generator pre-dates gap ledger | TC-CAP-001 |
| CAP-GAP-002 | HIGH | Many capabilities lack spec_fact_refs | All capabilities cite FACT-* entries | SAL facts missing for 14 formats | TC-SAL-001 |

## 16. Repair Architecture

**TC-CAP-001:**
1. Read `tools/supervisor/autonomous_task_generator.py` — find `_EXPANSION_GOALS`
2. Replace hardcoded list with dynamic reader that loads gap-ledger.json
3. Filter for open gaps (status != CLOSED) ordered by severity
4. Map gap entries to task generation format
5. Test: verify task generator returns gaps from gap-ledger.json

## 29. Active Taskcards

| Task ID | Title | Status |
|---------|-------|--------|
| TC-CAP-001 | Wire gap-ledger.json to autonomous task generator | TODO |

## 34. Work Log

```yaml
- log_id: WL-L03-001
  layer_id: L03
  task_id: TC-LP-001
  session_id: "923e237958c1"
  timestamp: "2026-06-26T00:00:00Z"
  event_type: LAYER_FILE_CREATED
  summary: "Created capability-layer.md"
```

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L03-001
  layer_id: L03
  permanent_layer_plan: plans/layers/capability-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  repository_revision: a7744cf6
  current_status: HARDENING_REQUIRED
  maturity_current: 3
  exact_next_task: TC-CAP-001
  why_this_is_next: >
    The capability layer generates 1,242 entries but NONE drive task selection.
    The autonomous task generator uses hardcoded _EXPANSION_GOALS instead of reading
    gap-ledger.json. This is the most impactful system healing gap below L01-SAL.
  allowed_paths: [tools/supervisor/autonomous_task_generator.py, tools/capability_layer/]
  forbidden_paths: [src/python/, src/net/]
  required_verification:
    - "Task generator returns gap entries from gap-ledger.json (not hardcoded)"
    - "open gaps from gap-ledger.json appear in next-sprint.md"
  important_decisions:
    - "capability_to_feature_compiler.py is PLANNING tool (not pipeline) — do not confuse"
    - "canonical pipeline: tools/supervisor/capability_feature_compiler.py"
  unresolved_findings:
    - "CAP-GAP-001: task generator bypass (most impactful)"
    - "CAP-GAP-002: many capabilities lack spec_fact_refs"
  resume_instructions: >
    READ tools/supervisor/autonomous_task_generator.py.
    FIND _EXPANSION_GOALS. REPLACE with gap-ledger.json reader.
    VERIFY task generator selects from open gap entries.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file |
