# MCP Status Report
# Format Factory — Supervisor-Generated
# Generated: 2026-06-02T18:59:55.428100

## Classification

**MCP_CONFIG_PRESENT_MODE4_ACTIVE**

MODE 4 — MCP authorized and config present. 2 server(s) configured: task-master-ai, claude-flow.

## Details

| Item | Value |
|------|-------|
| .vscode/mcp.json present | True |
| Supervisor mode | MODE 4 |
| Server count | 2 |

## Configured Servers

| Name | Type | Command |
|------|------|---------|
| task-master-ai | stdio | npx |
| claude-flow | stdio | npx |

## Interpretation

| Classification | Meaning |
|---------------|---------|
| MCP_CONFIG_PRESENT_MODE4_ACTIVE | MCP authorized (MODE 4+) and config file present — servers can be used |
| MCP_CONFIG_PRESENT_NOT_ACTIVE | Config file exists but MODE < 4 — MCP not yet authorized |
| MCP_CONFIG_MISSING | MODE 4+ authorized but file missing — restore .vscode/mcp.json |
| MCP_DISABLED | MODE < 4 and no config — MCP not authorized |
| MCP_MISCONFIGURED | Config file present but malformed JSON |

## Important Note

MCP active = servers CAN be invoked by MCP-aware tools if the IDE is configured.
This script only checks configuration presence, NOT whether servers are running.
Actual server startup requires IDE/client integration.
