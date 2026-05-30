# Ruflo — Format Factory Operating Profile

## Role in Architecture

Ruflo is Layer 4 in the 5-layer architecture:

```
Layer 1: Format Factory Repo (AUTHORITY)
Layer 2: Local Supervisor Control Plane
Layer 3: Task Master AI
Layer 4: Ruflo  ← HERE (lane/swarm coordination)
Layer 5: Claude Code (executor)
```

Ruflo is the **lane and swarm coordination** layer.
It does NOT have authority over Format Factory gates or evidence.

## What Ruflo Is Allowed to Do

- Coordinate parallel work across lanes (C0-C10)
- Assign Claude Code instances to lanes
- Track which lanes are active, pending, completed
- Consume supervisor-generated lane configurations
- Provide lane context to Claude Code sessions
- Enforce file ownership and overlap restrictions per lane

## What Ruflo Is NOT Allowed to Do

- Close Format Factory gates (gate closure requires human approval)
- Override evidence validators
- Mark lanes complete in a way that implies gate approval
- Generate sprint prompts (supervisor's role)
- Push or merge code
- Modify AGENTS.md, GOVERNANCE.md, master-plan.md, registry
- Start daemon without human authorization (MODE 4+ only)

## Version and Installation

| Item | Value |
|------|-------|
| CLI command | `claude-flow` (NOT `ruflo`) |
| Version | v3.10.13 |
| Orphan-process watchdog | Available since v3.10.11 |

Check version: `claude-flow --version`

## Activation by Mode

| Mode | Ruflo Usage |
|------|-------------|
| MODE 0-2 | None — no CLI calls |
| MODE 3 | Dry run — `claude-flow mcp tools` (temp dir, no daemon) |
| MODE 4+ | Active — MCP server registered (requires human approval) |

## .ruflo/ and .swarm/ Directory Policy

These directories must NOT exist in MODE 0-3 (in repo root).
If found unexpectedly: halt all lanes, quarantine, report to user.

In MODE 3: temp directory only (cleaned up after dry run).
In MODE 4+: `.ruflo/` and `.swarm/` are created under `.gitignore` policy.

## Daemon Policy

Ruflo daemon must NOT start in MODE 0-2.
In MODE 3: no daemon (schema validation and tool discovery only).
In MODE 4+: daemon lifecycle managed with explicit human authorization.

The daemon starts the process watchdog. In v3.10.11+, this watchdog prevents
orphaned Ruflo processes from persisting after Claude Code sessions end.
Always use the watchdog when the daemon is active.

## Lane Model

Ruflo manages lanes C0-C10 as defined in `next-ruflo-lanes.json`.
Each lane has:
- `allowed_files`: file globs this lane may create/modify
- `forbidden_files`: file globs this lane must never touch
- `non_authoritative: true`: required on all lanes

File ownership is enforced — no two lanes may write the same file.
Overlap check must pass before lane activation.

## Failure Recovery

If Ruflo state is inconsistent:
1. Run `claude-flow mcp stop` (stop any active daemon)
2. Check for orphaned processes: `claude-flow mcp status`
3. Regenerate lane config: `supervisor_loop.py export-ruflo`
4. Re-initialize from new `next-ruflo-lanes.json`

Ruflo state is always recoverable from the supervisor-generated export.
