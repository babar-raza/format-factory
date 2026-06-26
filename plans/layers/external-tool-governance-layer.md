# External Tool Governance Layer

```yaml
layer_metadata:
  layer_id: L22
  canonical_name: External Tool Governance Layer
  canonical_slug: external-tool-governance-layer
  permanent_plan_path: plans/layers/external-tool-governance-layer.md
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
  downstream_layers: [L11, L13]
  skill_ids: []
  command_ids: []
  last_updated_at: "2026-06-26"
  next_task_id: TC-EXT-001
  next_action: "Audit .vscode/mcp.json; inventory MCP server dependencies; define governance contract"
```

## 2. Authority and Purpose

Owns governance of external tools: MCP servers, IDE integrations, external APIs.
MCP server activation changes require explicit policy per CLAUDE.md.

## 3. Scope

- `.vscode/mcp.json` — MCP server configuration
- MCP server inventory and dependency tracking
- External API credentials policy

## 9. Current Implementation

- `.vscode/mcp.json` present (MCP ACTIVE per session-resume.md)
- No formal MCP governance contract
- MCP activation changes require explicit policy per CLAUDE.md

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L22-001
  layer_id: L22
  permanent_layer_plan: plans/layers/external-tool-governance-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  current_status: NOT_ASSESSED
  maturity_current: 1
  exact_next_task: TC-EXT-001
  resume_instructions: >
    External tool governance not assessed. First: read .vscode/mcp.json.
    Inventory MCP servers and their capabilities. Define governance contract.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (stub) |
