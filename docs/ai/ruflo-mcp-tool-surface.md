# Ruflo — MCP Tool Surface

## Overview

Ruflo exposes coordination tools via MCP (Model Context Protocol).
These tools are available to Claude Code after MCP activation (MODE 4+).
In MODE 0-3 no Ruflo MCP tools are active.

## MCP Subcommands

```bash
claude-flow mcp start      # Start Ruflo MCP server
claude-flow mcp stop       # Stop Ruflo MCP server
claude-flow mcp status     # Check server status + health
claude-flow mcp health     # Health check
claude-flow mcp restart    # Restart server
claude-flow mcp tools      # List available tools
claude-flow mcp toggle     # Toggle individual tool on/off
claude-flow mcp exec       # Execute a specific tool
claude-flow mcp logs       # View server logs
```

## Init Subcommands (MODE 3 dry run)

```bash
claude-flow init wizard    # Interactive setup
claude-flow init check     # Check current state
claude-flow init skills    # Show available skills
claude-flow init hooks     # Configure hooks
claude-flow init upgrade   # Upgrade configuration
```

Safe flags for dry run:
```bash
claude-flow init --minimal --only-claude --no-global
```

## Tool Toggle Policy

Before activating MCP in MODE 4+:

1. Run `claude-flow mcp tools` to see all available tools
2. Disable tools not needed for current sprint: `claude-flow mcp toggle <tool_name>`
3. Document which tools are enabled in the sprint evidence
4. Verify no tools exist that can modify AGENTS.md, GOVERNANCE.md, registry

Minimum required tools for lane coordination:
- Lane assignment tools
- Status update tools
- File ownership enforcement tools

## Forbidden Tool Patterns

Do NOT enable tools that can:
- Write to governance files (AGENTS.md, GOVERNANCE.md, master-plan.md, registry)
- Execute git push or merge
- Activate paid external APIs
- Modify Format Factory evidence artifacts
- Override evidence validators

## MCP Registration (MODE 4+)

Template: `.vscode/mcp.dual-orchestration.provider-key.example.json`

After human approval, register via `.vscode/mcp.json`:
```json
{
  "servers": {
    "claude-flow": {
      "type": "stdio",
      "command": "claude-flow",
      "args": ["mcp", "start"]
    }
  }
}
```

IMPORTANT: `.vscode/mcp.json` must NOT exist in MODE 0-3.
Its presence in MODE 0-3 is an emergency stop condition.

## Tool Discovery (MODE 3 Dry Run)

In MODE 3, tool discovery is safe:

```bash
# In a temp directory
mkdir -p /tmp/ruflo-dry-run
cd /tmp/ruflo-dry-run
claude-flow mcp tools   # Lists tools without starting daemon
cd -                    # Return to repo
```

This does not create any files in the repo root.
Results are captured in `reports/dual-orchestration-supervisor-e2e/ruflo-dry-run.md`.

## Process Hygiene

After any Ruflo session:
1. Verify no daemon remains: `claude-flow mcp status`
2. Verify no orphaned processes (v3.10.11+ watchdog handles this automatically)
3. Verify `.ruflo/` and `.swarm/` exist only if MODE 4+ authorized
4. Log any unexpected processes in the stop-gate log
