# Ruflo — Supervisor Integration

## Overview

Ruflo (Layer 4) is the lane/swarm coordination engine.
The Local Supervisor Control Plane (Layer 2) generates Ruflo inputs from evidence.
Ruflo does NOT have authority over Format Factory gates or evidence.

## Integration Points

```
Supervisor (Layer 2)                    Ruflo (Layer 4)
─────────────────────────────────────   ──────────────────────────────
generate_supervisor_packet.py
  │
  └── writes next-ruflo-lanes.json
              │
              └── Ruflo import (MODE 3+) ─► lane coordination
```

## Data Flow

1. `generate_supervisor_packet.py` reads `evidence-review.json` + `contradictions.json`
2. Generates `next-ruflo-lanes.json` (schema-validated against next-ruflo-lanes.schema.json)
3. In MODE 3: dry run — validates schema, no daemon
4. In MODE 4+: Ruflo ingests lanes via `claude-flow` CLI

## next-ruflo-lanes.json Format

```json
{
  "sprint_id": "format-factory-RNNNN-...",
  "timestamp": "2026-05-30T00:00:00",
  "verdict": "SUPERVISOR_...",
  "coordinator_lane": "C0",
  "lanes": [
    {
      "lane_id": "C0",
      "owner_role": "Coordinator",
      "allowed_files": ["reports/**"],
      "forbidden_files": ["AGENTS.md", "GOVERNANCE.md"],
      "non_authoritative": true,
      "status": "pending"
    }
  ],
  "overlap_check_passed": true
}
```

All lanes must have `non_authoritative: true`.
`overlap_check_passed: true` required before supervisor activates lanes.

## Bridge Validation

`tools/taskmaster/validate_dual_orchestration_bridge.py` validates every Ruflo export:

- RULE-2: Completed lanes must have `non_authoritative: true`
- RULE-3: All lanes must have `non_authoritative: true`
- RULE-4: Lane fields must not contain gate closure keywords

Run: `python tools/taskmaster/validate_dual_orchestration_bridge.py --ruflo-file reports/supervisor/next-ruflo-lanes.json`

## CLI Note

The Ruflo CLI command is `claude-flow` (NOT `ruflo`).

```bash
claude-flow mcp start     # Start Ruflo MCP server (MODE 4+)
claude-flow mcp stop      # Stop Ruflo MCP server
claude-flow mcp status    # Check status
claude-flow mcp tools     # List available tools
claude-flow mcp toggle    # Toggle individual tools
```

## Mode Activation

- MODE 0-2: No Ruflo activation. No CLI calls.
- MODE 3: Dry run — `claude-flow mcp tools` (no daemon, temp dir only)
- MODE 4+: Active Ruflo with MCP registration (requires human approval)

## Safe Init Flags (MODE 3 dry run)

```bash
claude-flow init --minimal --only-claude --no-global
```

FORBIDDEN flags (never use without explicit approval):
- `--codex` — creates AGENTS.md (forbidden file)
- `--start-all` — starts daemon+memory+swarm (forbidden in MODE 0-2)
- `--with-embeddings` — starts ONNX embeddings (forbidden)
- `--all-agents` — installs ~89 agents (forbidden without approval)
