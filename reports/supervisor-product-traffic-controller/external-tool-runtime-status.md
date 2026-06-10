# External Tool Runtime Status

## Sprint
`FORMAT-FACTORY-SUPERVISOR-PRODUCT-TRAFFIC-CONTROLLER-INTEGRATION-001`

## Detection Summary

| Tool | Detected | Mode | Invoked This Sprint |
|------|----------|------|---------------------|
| claude-flow (Ruflo) | YES | DETECTED_NOT_CONFIGURED | NO |
| task-master-ai | YES | DETECTED_NOT_CONFIGURED | NO |
| Superpowers | NO | ABSENT | NO |
| GhidraMCP | NO | ABSENT | NO |

## Ruflo/claude-flow Status

- **MCP registration:** `claude-flow` in `.vscode/mcp.json` via `npx -y claude-flow@3.10.14 mcp start`
- **State directory:** `.claude-flow/` — ABSENT
- **Hooks:** ABSENT
- **Daemon:** ABSENT
- **Auto-install risk:** YES — `npx -y` will install package on first invocation
- **Invoked this sprint:** NO
- **Verdict:** `RUFLO_DETECTED_NOT_CONFIGURED_APPROVAL_REQUIRED_FOR_INVOCATION`

## task-master-ai Status

- **MCP registration:** `task-master-ai` in `.vscode/mcp.json` via `npx -y task-master-ai@0.43.1`
- **Invoked this sprint:** NO
- **Verdict:** `TASKMASTER_DETECTED_NOT_CONFIGURED_APPROVAL_REQUIRED_FOR_INVOCATION`

## Superpowers Status

- **Plugin directory:** `.claude-plugin/` — ABSENT
- **Verdict:** `SUPERPOWERS_NOT_INSTALLED_EVALUATE_ONLY`

## GhidraMCP Status

- **Not in mcp.json.** Disabled by default.
- **Verdict:** `GHIDRA_MCP_DISABLED_DEFAULT`

## Overall Governance Verdict

**`EXTERNAL_TOOLS_GOVERNED_LOCAL_COORDINATOR_ACTIVE`**

Deterministic Supervisor retains all authority. No external tool invoked. No workspace mutations.
No MCP server activation. Local coordinator is the sole orchestration authority.
