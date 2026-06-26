# AI Acceleration Boundary Layer

```yaml
layer_metadata:
  layer_id: L21
  canonical_name: AI Acceleration Boundary Layer
  canonical_slug: ai-acceleration-boundary-layer
  permanent_plan_path: plans/layers/ai-acceleration-boundary-layer.md
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
  dependencies: []
  upstream_layers: []
  downstream_layers: [L18]
  skill_ids: [check-gate, check-release-boundary]
  command_ids: [check-gate, check-release-boundary]
  last_updated_at: "2026-06-26"
  next_task_id: TC-AIB-001
  next_action: "BLOCKED_EXTERNAL: Gate 11 G11-G execution requires Babar Raza commercial sign-off"
```

## 2. Authority and Purpose

Owns the boundary between agent-executable work and human authority:
- AGENTS.md §AG1-AG2: Human Task Conversion Rule
- TRUE_EXTERNAL_GATE classification (git push credentials, Gate 11, package publication)
- Supreme Directive exceptions (named legitimate stop conditions)
- POST_PLAN_TERMINAL handling

**Key document:** `AGENTS.md` (governance) + `CLAUDE.md` §Supreme Directive

## 9. Current Implementation

- `AGENTS.md`: comprehensive agent governance (§AG1-AG4)
- `CLAUDE.md`: Supreme Directive with TRUE_EXTERNAL_GATE definition
- 3 TRUE_EXTERNAL_GATEs defined: git push credentials, Gate 11 execution, package publication credentials
- 4 named legitimate stops: POST_PLAN_TERMINAL, PLAN_COMPLETED_IN_SESSION, SESSION_MISMATCH, CHAT_ID_MISMATCH
- `/check-gate` and `/check-release-boundary` skills registered
- Gate 11 G11-G APPROVED for FODS/FODT/Netpbm (G11 EXECUTION still pending)

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L21-001
  layer_id: L21
  permanent_layer_plan: plans/layers/ai-acceleration-boundary-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  current_status: NOT_ASSESSED
  maturity_current: 2
  exact_next_task: TC-AIB-001
  important_decisions:
    - "TRUE_EXTERNAL_GATE = git push credentials, Gate 11 execution, package publication"
    - "Named legitimate stops (NOT TRUE_EXTERNAL_GATE but valid): POST_PLAN_TERMINAL etc."
    - "Supreme Directive: never stop except TRUE_EXTERNAL_GATEs or context exhaustion"
    - "Gate 11 PREPARATION is always agent-owned; EXECUTION (commercial) needs Babar Raza"
  resume_instructions: >
    AI boundary layer partially documented in AGENTS.md and CLAUDE.md.
    Next: formalize TRUE_EXTERNAL_GATE taxonomy into machine-readable registry.
    Create .supervisor/schemas/true-external-gate.schema.json.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (stub) |
