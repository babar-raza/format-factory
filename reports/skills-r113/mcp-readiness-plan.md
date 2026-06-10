# MCP Readiness Plan

## Current State
- `check-mcp-status` is the only deferred skill (1 of 25)
- Deferred reason: "No command file exists. MCP status is checked ad-hoc during preflight."
- MCP status is currently checked informally during session start

## Assessment
check-mcp-status should NOT be promoted to active in R113 because:
1. No MCP server is currently configured for autonomous use
2. The skill would need a real MCP endpoint to validate against
3. Promoting without a real backend creates a "hollow skill" anti-pattern

## Readiness Gate
Instead of promoting, R113 will:
1. Create a readiness gate document defining promotion criteria
2. Create a taskcard for future promotion
3. Verify the command file stub exists at `.claude/commands/check-mcp-status.md`

## Promotion Criteria (for future sprint)
- [ ] MCP server configured and accessible
- [ ] 5-state health model implemented (CONNECTED, DEGRADED, DISCONNECTED, UNKNOWN, NOT_CONFIGURED)
- [ ] At least 5 tests covering each state
- [ ] Command file meets R106 validator requirements
