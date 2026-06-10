# GhidraMCP Compliance Gate

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## Current Status

GhidraMCP: ABSENT — not registered in `.vscode/mcp.json`.

## 4 Verdicts

| Verdict | Condition |
|---------|-----------|
| ABSENT | Not in mcp.json, no Ghidra installation |
| DISABLED_DEFAULT | Disabled explicitly or not configured |
| ALLOWED_AUTHORIZED_FIXTURE_ONLY | Authorized binary + hash provided, fixture-only mode |
| BLOCKED_NEEDS_AUTHORIZATION | Registered but no authorized binary |

## Authorization Requirements

1. Authorized binary required before any activation
2. Input hash (SHA-256) required for each binary analyzed
3. No proprietary decompiled code in source tree
4. No capability matrix updates from reverse engineering alone

## Current Sprint Verdict: GHIDRA_MCP_DISABLED_DEFAULT
