# Feature Compilation Layer

```yaml
layer_metadata:
  layer_id: L14
  canonical_name: Feature Compilation Layer
  canonical_slug: feature-compilation-layer
  permanent_plan_path: plans/layers/feature-compilation-layer.md
  schema_version: "1.0"
  plan_revision: "1"
  repository_revision: "a7744cf6"
  status: NOT_ASSESSED
  health: ABSENT
  maturity_current: 0
  maturity_target: 4
  current_stage: DISCOVERY
  current_owner: null
  session_id: "923e237958c1"
  active_taskcards: []
  ready_taskcards: []
  blocked_taskcards: [TC-FEAT-001]
  completed_taskcards: []
  dependencies: [L03]
  upstream_layers: [L03]
  downstream_layers: [L06]
  skill_ids: []
  command_ids: []
  evidence_paths:
    - plans/strategic/spec-to-feature-radical-correction-plan.md
  last_updated_at: "2026-06-26"
  last_verified_at: null
  next_task_id: TC-FEAT-001
  next_action: "Design 9-phase feature compiler per spec-to-feature plan Lane 3; close SKILL-GAP-003"
```

---

## 2. Authority and Purpose

The Feature Compilation Layer is the **missing bridge** between capability records (L03)
and product source generation (L06). It is Lane 3 of the spec-to-feature radical
correction plan.

**Current state: NOT IMPLEMENTED (SKILL-GAP-003)**

The 9-phase compiler should:
1. Read gap-ledger.json from L03
2. Map capabilities to feature specifications
3. Generate feature contracts (API signature, spec_qname, test requirements)
4. Output taskcard definitions for L06 implementation
5. Wire back to spec facts from L01

## 3. Scope

- `tools/` (to be created): `tools/feature_compilation/` directory
- Compiler: `tools/feature_compilation/feature_compiler.py` (9 phases)
- Output: feature specifications consumed by /add-python-api, /add-dotnet-api

**NOT to be confused with:**
- `tools/capability_layer/capability_to_feature_compiler.py` — PLANNING TOOL (stubs only)
- `tools/supervisor/capability_feature_compiler.py` — PIPELINE TOOL (next-work-items.json)

## 8. Ideal Production Design (9 Phases)

Phase 1: Load gap-ledger.json (open gaps only)
Phase 2: Map gap → spec QName (via L02 qname-registry)
Phase 3: Resolve spec facts (via L01 sal-facts-latest.json)
Phase 4: Generate feature signature (API method name, parameters, return type)
Phase 5: Validate canonical naming (Compat/ facade if needed)
Phase 6: Generate test requirements
Phase 7: Generate taskcard definition
Phase 8: Write feature spec to .local/feature-specs/{format}/{feature}.yaml
Phase 9: Update task-register.yaml with new taskcards

## 14. Gap Register

| Gap ID | Severity | Current | Target | Taskcards |
|--------|----------|---------|--------|-----------|
| FEAT-GAP-001 | CRITICAL | Feature compiler does not exist | 9-phase compiler implemented | TC-FEAT-001 |

## 29. Active Taskcards

| Task ID | Title | Status |
|---------|-------|--------|
| TC-FEAT-001 | Design and implement 9-phase feature compiler | TODO (BLOCKED on TC-CAP-001) |

## 34. Work Log

```yaml
- log_id: WL-L14-001
  layer_id: L14
  task_id: TC-LP-001
  session_id: "923e237958c1"
  timestamp: "2026-06-26T00:00:00Z"
  event_type: LAYER_FILE_CREATED
  summary: "Created feature-compilation-layer.md"
```

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L14-001
  layer_id: L14
  permanent_layer_plan: plans/layers/feature-compilation-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  repository_revision: a7744cf6
  current_status: NOT_ASSESSED
  maturity_current: 0
  exact_next_task: TC-FEAT-001
  why_this_is_next: >
    This layer does not exist yet. It is the missing link between capability records
    and product implementation. Lane 3 of spec-to-feature plan defines the architecture.
    SKILL-GAP-003 is the open gap.
  blocked_tasks: [TC-FEAT-001]
  allowed_paths: [tools/, plans/layers/feature-compilation-layer.md]
  forbidden_paths: [src/python/, src/net/]
  important_decisions:
    - "Do NOT confuse with tools/capability_layer/capability_to_feature_compiler.py (planning tool)"
    - "Do NOT confuse with tools/supervisor/capability_feature_compiler.py (pipeline tool)"
    - "This layer creates a NEW tools/feature_compilation/ directory"
  resume_instructions: >
    Feature compiler does not exist. BLOCKED until TC-CAP-001 wires gap-ledger to task generator.
    READ plans/strategic/spec-to-feature-radical-correction-plan.md Lane 3 for full design spec.
    DESIGN the 9-phase compiler architecture first. Then implement.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (stub — NOT IMPLEMENTED) |
