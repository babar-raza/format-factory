# Task Master AI — MCP Tool Surface

## Overview

Task Master AI exposes tools via MCP (Model Context Protocol).
These tools are available to Claude Code after MCP activation (MODE 4+).
In MODE 0-3 no MCP tools are active.

## Default Tool Mode: core (7 tools)

The core tool set is active by default when the MCP server starts.

| Tool | Purpose |
|------|---------|
| `get_tasks` | List all tasks with status |
| `get_task` | Get details for a specific task |
| `set_task_status` | Update task status (pending/in_progress/done/blocked) |
| `add_task` | Add a new task to the graph |
| `get_next_task` | Get the next task to work on |
| `analyze_project_complexity` | Analyze task complexity |
| `generate_task_files` | Generate task implementation files |

Extended tools are available via MCP configuration.

## MCP Registration (MODE 4+)

After human approval, register via `.vscode/mcp.json`:

```json
{
  "servers": {
    "task-master-ai": {
      "type": "stdio",
      "command": "task-master-ai",
      "args": []
    }
  }
}
```

Template available at: `.vscode/mcp.dual-orchestration.provider-key.example.json`

## Tool Toggle (MODE 4+)

Individual tools can be enabled/disabled without restarting the server.
See Ruflo docs for `claude-flow mcp toggle` — the same toggle mechanism applies.

## Tool Surface Control Policy

In MODE 4+, only enable tools that are explicitly needed for the current sprint.
Disable tools that can cause unintended side effects:
- Tools that write to external systems
- Tools that modify git state
- Tools that execute shell commands

## No-Drift Enforcement at Tool Level

Claude Code must not use TM tools to:
- Mark a task done and imply a Format Factory gate is closed
- Skip evidence generation because TM shows a task as done
- Override supervisor contradiction detection with TM state

TM tools show task state. Evidence validators show reality.
When they disagree, evidence validators win.

## MCP Server Lifecycle

Start: happens automatically when VS Code detects `.vscode/mcp.json`
Stop: `claude-flow mcp stop` (if registered via Ruflo) or close VS Code
Status: `claude-flow mcp status`

In MODE 3 (dry run): version check only, no MCP registration.
In MODE 4+: full MCP server lifecycle with human-approved config.

## Version Management

TM version is obtained from npm registry (not the CLI):
```bash
npm show task-master-ai version
```

To install/upgrade:
```bash
npm install -g task-master-ai
```

Current confirmed version in this project: check `reports/dual-orchestration-supervisor-e2e/`
for the MODE 3 dry run output.
