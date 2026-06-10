# Host Live Invocation Proof
Sprint: FORMAT-FACTORY-HOST-PROOFED-AUTONOMOUS-FORMAT-PILOT-001
Date: 2026-06-05

## Classification: HOST_RUNNER_LIVE_INVOCATION_BLOCKED_BY_CLAUDECODE

Live host invocation is NOT proven in this sprint. CLAUDECODE=1 environment variable
is present, indicating this agent is running inside a Claude Code session. Per policy,
nested invocation is not attempted.

## Environment Checks

| Check | Result |
|---|---|
| CLAUDECODE env var | PRESENT (value=1) |
| Nested session | DETECTED |
| CLI path | C:/Users/prora/AppData/Roaming/npm/claude.cmd |
| CLI version | 2.1.62 (Claude Code) |
| CLI detected | YES |
| Dry-run safe | YES |

## Why Not Attempted

Phase 1 requirement 2 states: "If CLAUDECODE is present, do not attempt nested invocation
unless policy explicitly allows it." Policy does not explicitly allow nested sessions.
Attempting it would produce: "Claude Code cannot be launched inside another Claude Code session."

## Wiring Instructions (for external terminal proof)

Run from a terminal outside Claude Code:

```
cd c:/Users/prora/OneDrive/Documents/GitHub/format-factory
claude --print -p "Respond with exactly: HOST_RUNNER_NOOP_OK. Do not modify files. Do not run commands."
```

Expected output: `HOST_RUNNER_NOOP_OK`

After running:
1. Confirm output contains `HOST_RUNNER_NOOP_OK`
2. Run `git status` — confirm unchanged
3. Write result to `reports/host-proofed-format-pilot/host-runner-external-proof.json`

## Impact

Pilot runs in **SUPERVISED_AUTONOMOUS_PILOT_ONLY** mode.
No claim of unattended autonomy. Babar manually starts each Claude Code session.
This is a runtime environment constraint, not a tool defect.

Gate A verdict: **NOT_PROVEN_BLOCKED_BY_CLAUDECODE**
