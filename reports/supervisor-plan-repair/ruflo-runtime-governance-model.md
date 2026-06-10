# Ruflo Runtime Governance Model

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## Ruflo Modes (6)

| Mode | Condition | Verdict |
|------|-----------|---------|
| ABSENT | Not in mcp.json, no state dir | RUFLO_ABSENT_CONTINUE_WITH_LOCAL_COORDINATOR |
| DETECTED_NOT_CONFIGURED | In mcp.json, no state dir | RUFLO_DETECTED_NOT_CONFIGURED_APPROVAL_REQUIRED |
| PLUGIN_LITE | State dir present, not in mcp.json | RUFLO_LITE_AVAILABLE_NOT_REQUIRED |
| FULL_LOOP_PRESENT_NOT_APPROVED | Both present, no approval signal | RUFLO_FULL_LOOP_BLOCKED_PENDING_APPROVAL |
| FULL_LOOP_APPROVED | Both present + explicit approval | RUFLO_FULL_LOOP_ALLOWED_AS_RUNTIME_ONLY |
| DISABLED_DUE_RISK | Explicitly disabled | RUFLO_DISABLED_DUE_RISK |

## Detection Checks

1. Read `.vscode/mcp.json` — is `claude-flow` registered?
2. Check `.claude-flow/` — does state directory exist?
3. Check for hooks configuration
4. Check for daemon process (informational)

## Authority Rules

- Ruflo MAY coordinate lanes (runtime)
- Ruflo MAY NOT close taskcards
- Ruflo MAY NOT approve continuation
- Ruflo output = `runtime_advisory`, NOT `authoritative`
- `npx -y` invocation = activation risk → requires human approval

## Current Sprint

Mode: DETECTED_NOT_CONFIGURED → not invoked this sprint.
