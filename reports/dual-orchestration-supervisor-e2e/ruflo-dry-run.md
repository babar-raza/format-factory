# Ruflo Dry Run — MODE 3

## Sprint Identity
dual-orchestration-supervisor-e2e-20260530-165603

## Version Check

**Registry version:** `npm show claude-flow version` → 3.10.13
**Local installation:** Not installed globally
**npx availability:** `npx claude-flow` downloads and runs v3.10.13 on demand (confirmed)

```
$ npm list -g claude-flow --depth=0
(empty)

$ npm show claude-flow version
3.10.13
```

`claude-flow` is available via `npx claude-flow` (downloads v3.10.13 on demand) even without global install.
Global install not required for MODE 4 — `npx claude-flow mcp start` works directly.
Activation deferred to MODE 4.

## Installation Notes

Version 3.10.13 includes orphan-process watchdog (added in v3.10.11).
The watchdog automatically terminates Ruflo processes when the parent Claude Code session ends.

## Safe Init Flags (documented for MODE 4)

When installing in MODE 4:
```bash
claude-flow init --minimal --only-claude --no-global
```

FORBIDDEN flags:
- `--codex` — creates AGENTS.md (forbidden file)
- `--start-all` — starts daemon+memory+swarm (forbidden in MODE 0-3)
- `--with-embeddings` — starts ONNX embeddings (forbidden)
- `--all-agents` — installs ~89 agents (forbidden without approval)

## MCP Subcommands (documented for MODE 4)

```bash
claude-flow mcp start    # Start Ruflo MCP server
claude-flow mcp stop     # Stop server
claude-flow mcp status   # Check status
claude-flow mcp tools    # List available tools
claude-flow mcp toggle   # Toggle individual tool
```

## Schema Validation

`reports/supervisor/next-ruflo-lanes.json` validated against:
`.supervisor/schemas/next-ruflo-lanes.schema.json`

**Result:** SCHEMA VALID

## No-Drift Validation

```
python tools/taskmaster/validate_dual_orchestration_bridge.py \
  --ruflo-lanes reports/supervisor/next-ruflo-lanes.json
```

**Result:** NO_DRIFT_CONTRACT: NO_DRIFT (Violations: 0, Warnings: 0)

All lanes have `non_authoritative: true`, no gate closure keywords detected.

## Mode 3 Assessment

| Check | Result |
|-------|--------|
| Ruflo version obtainable from registry | PASS (3.10.13) |
| Ruflo CLI available locally | NOT INSTALLED globally; available via npx |
| next-ruflo-lanes.json schema-validates | PASS |
| No-drift contract: no violations | PASS |
| No daemon started | PASS |
| No .ruflo/ directory created | PASS |
| No .swarm/ directory created | PASS |
| No .vscode/mcp.json created | PASS |
| Safe init flags documented | PASS |
| Forbidden flags documented | PASS |

## Process Hygiene

No claude-flow processes running.
No .ruflo/ or .swarm/ directories exist.
No Ruflo ports or sockets open.

## Next Step (MODE 4)

Requires explicit human approval:
1. Use `npx claude-flow` (no global install required) or `npm install -g claude-flow`
2. `npx claude-flow init --minimal --only-claude --no-global` (in temp directory)
3. `claude-flow mcp tools` — capture tool list
4. Create `.vscode/mcp.json` from template
5. Validate daemon lifecycle + rollback procedure
6. Verify orphan-process watchdog active (v3.10.11+)
