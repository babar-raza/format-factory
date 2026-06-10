# Train H: MCP Truth

## MCP Status Classifications (R99 — complete set)
| Classification | When | Verified |
|---------------|------|----------|
| MCP_DISABLED | MODE < 4, no file | Yes (existing) |
| MCP_CONFIG_MISSING | MODE >= 4, no .vscode/mcp.json | Yes (existing) |
| MCP_CONFIG_PRESENT_NOT_ACTIVE | File present, MODE < 4 | Yes (existing) |
| MCP_CONFIG_PRESENT_MODE4_ACTIVE | File present, MODE >= 4 | Yes (existing) |
| MCP_MISCONFIGURED | File present but invalid JSON | Yes (existing) |
| MCP_BLOCKED_POLICY | Policies.yaml hard_prohibitions blocks MCP | Yes (R99: D99-MCP-01) |
| MCP_ACTIVE_VERIFIED | Runtime server responding | Aspirational (requires MCP runtime probe) |

## Fix (R99: D99-MCP-01)
Added `MCP_BLOCKED_POLICY` classification to `check_mcp_status.py`. When:
- policies.yaml hard_prohibitions includes `mcp_activation_beyond_mode_3`
- AND current mode < 4

The status is classified as `MCP_BLOCKED_POLICY` rather than `MCP_DISABLED`, making the reason explicit.

## MCP_ACTIVE_VERIFIED
This state would require runtime verification that MCP servers are actually responding. This is aspirational — it cannot be implemented without an MCP client probe. Documented as future work, not claimed.

## Current State
MCP status: `MCP_CONFIG_PRESENT_MODE4_ACTIVE`
- .vscode/mcp.json present with 2 servers
- MODE 4 (ACTIVE_MCP_ACTIVATION)
