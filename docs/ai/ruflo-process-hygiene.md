# Ruflo — Process Hygiene

## Overview

Ruflo (claude-flow) can leave orphaned processes if not properly shut down.
This document defines process hygiene rules for all modes.

## v3.10.11+ Orphan Watchdog

Ruflo v3.10.11 and later include an orphan-process watchdog.
The watchdog automatically terminates Ruflo processes when the parent Claude Code session ends.

Current version: v3.10.13 (watchdog active).

## Process Rules by Mode

### MODE 0-2: No Ruflo Processes

No `claude-flow` processes should be running.
No `.ruflo/` or `.swarm/` directories should exist.
No Ruflo daemon should be running.

Verification: `tasklist | findstr claude-flow` should return empty.

### MODE 3: Temp Directory Dry Run Only

```bash
# Create temp dir
mkdir -p /tmp/ruflo-dry-run

# Run in temp dir only
cd /tmp/ruflo-dry-run
claude-flow mcp tools
cd -

# Clean up
rm -rf /tmp/ruflo-dry-run
```

No files created in repo root.
No daemon started.
Check: `claude-flow mcp status` should show not-running after cleanup.

### MODE 4+: Managed Lifecycle

```bash
# Start with watchdog (v3.10.11+)
claude-flow mcp start

# Verify running
claude-flow mcp status

# After sprint: stop cleanly
claude-flow mcp stop

# Verify stopped
claude-flow mcp status
```

## Process Hygiene Checklist

Before each sprint (all modes):
- [ ] `claude-flow mcp status` returns "not running" or equivalent
- [ ] No `.ruflo/` directory in repo root (MODE 0-3)
- [ ] No `.swarm/` directory in repo root (MODE 0-3)
- [ ] No `.taskmaster/` directory in repo root (MODE 0-3)
- [ ] No `.vscode/mcp.json` (MODE 0-3)

After each sprint (MODE 4+):
- [ ] `claude-flow mcp stop` executed
- [ ] `claude-flow mcp status` confirms stopped
- [ ] No orphaned processes via watchdog check

## Emergency Process Cleanup

If a Ruflo process is found running unexpectedly in MODE 0-3:

1. Log in `reports/dual-orchestration-supervisor-e2e/stop-gate-log.md`
2. Run `claude-flow mcp stop`
3. Verify stopped with `claude-flow mcp status`
4. If process persists: identify PID and terminate manually
5. Report to user — this is an emergency stop condition

## Port and Socket Cleanup

After `claude-flow mcp stop`:
- Verify no Ruflo ports remain open (check with `netstat` if needed)
- Verify no Ruflo socket files remain in temp directories
- The v3.10.11+ watchdog handles most cleanup automatically

## Daemon vs Non-Daemon Usage

Non-daemon usage (safe in MODE 3 dry run):
- `claude-flow mcp tools` — list tools without starting daemon
- `claude-flow mcp status` — check status
- `claude-flow init check` — check initialization state

Daemon usage (MODE 4+ only, human-approved):
- `claude-flow mcp start` — starts daemon
- `claude-flow mcp restart` — restarts daemon
- Any long-running `claude-flow` process

## Logging

Process lifecycle events are logged in:
- `reports/dual-orchestration-supervisor-e2e/ruflo-dry-run.md` (MODE 3 evidence)
- `.supervisor/state/current-run.json` (runtime state)
- `reports/dual-orchestration-supervisor-e2e/stop-gate-log.md` (emergency events)
