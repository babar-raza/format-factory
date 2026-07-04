# /check-mcp-status

Check and classify the MCP server connection status using a 5-state model.

## What This Command Does

1. **Identify the target MCP server** — from `mcp_server_name` handoff field.
2. **Probe connection** — attempt a lightweight status call to the MCP server endpoint.
3. **Classify state** using the 5-state model:
   - `CONNECTED` — server reachable and responding normally
   - `DEGRADED` — server reachable but returning errors or partial responses
   - `TIMEOUT` — server not responding within the configured timeout
   - `AUTH_FAILED` — server reachable but authentication rejected
   - `UNREACHABLE` — server not reachable (DNS failure, port closed, network error)
4. **Report** — print state classification with timestamp and diagnostic details.
5. **Exit** — exit 0 for CONNECTED, exit 1 for any other state.

## When to Use

- Before any workflow that depends on an active MCP server connection
- When diagnosing MCP connectivity issues in CI or development environments
- After environment changes that may affect MCP server availability

## Steps

```
1. Read mcp_server_name from handoff fields.
2. Look up server endpoint from MCP configuration (usually .claude/mcp-config.yaml or environment).
3. Probe the server with a lightweight status/ping call (max 10s timeout).
4. Classify result into one of the 5 states.
5. Print: "MCP server <name>: <STATE> — <details>"
6. Exit 0 if CONNECTED, exit 1 otherwise.
```

## Source Files

- MCP configuration: `.claude/mcp-config.yaml` or environment variables
- MCP client library: provided by the Claude Code SDK

## Notes

- This skill is **DEFERRED** until MCP server integration is active in production.
- When active, it should be run before any skill that requires live MCP tool access.
- The 5-state model is defined in `docs/automation/mcp-status-model.md` (planned).

## skill_id

check-mcp-status

## Required Inputs

- `mcp_server_name` — name of the MCP server to check (e.g., `filesystem`, `github`, `gitlab`)

## Allowed Paths

- `.claude/` — read-only configuration access

## Forbidden Paths

- `src/net/**` — no product source mutation
- `src/python/**` — no product source mutation
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop immediately if `mcp_server_name` is not provided
- Stop if the server state is AUTH_FAILED (do not retry authentication)

## Output Format

- Print: `MCP server <name>: <STATE> — <timestamp> — <details>`
- Exit 0 for CONNECTED, exit 1 for all other states
