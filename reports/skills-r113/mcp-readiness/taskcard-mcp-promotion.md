# TC-MCP-READINESS-001: Promote check-mcp-status to Active

## Summary
Promote the deferred `check-mcp-status` skill to active status when an MCP server is configured for autonomous use.

## Prerequisites
- MCP server must be configured and accessible
- Connection health monitoring endpoint available
- Authentication/authorization model defined

## Implementation
1. Create `.claude/commands/check-mcp-status.md` with all R106-required sections
2. Implement 5-state health model: CONNECTED, DEGRADED, DISCONNECTED, UNKNOWN, NOT_CONFIGURED
3. Add at least 5 tests (one per state)
4. Pass R106 command validator
5. Run dry-run execution proof
6. Update skill-registry.yaml: status → active, remove deferred_reason

## Acceptance Criteria
- [ ] Command file passes R106 validator
- [ ] 5+ tests pass
- [ ] Dry-run transcript validates
- [ ] Registry updated
- [ ] All existing tests still pass

## Priority
Low — no MCP server is currently configured for autonomous workflows.

## Blocked By
MCP server configuration and availability.
