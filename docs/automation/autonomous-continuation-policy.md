# Autonomous Continuation Policy

## Decision Rule

The supervisor decides whether the loop can continue autonomously after each cycle:

```
autonomous_continue = (critical_rework_count == 0)
```

Where critical rework = items graded OVERCLAIMED or REJECTED.

## When Autonomous Continue = True

- Exit code: 0
- The combined-next-worker-prompt.md is generated with forward work
- The loop may continue without human intervention
- Non-critical rework items (REWORK_REQUIRED, ACCEPTED_WITH_WARNINGS) are included in the next prompt's rework lane
- Product-factory forward work is always included

## When Autonomous Continue = False

- Exit code: 3
- The loop pauses
- Human must review the overclaimed/rejected items
- The next-worker prompt still exists but requires human approval before execution
- The stop_reason field in the review explains why

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success, autonomous continue possible |
| 1 | Declaration not found or schema invalid |
| 3 | Critical rework exists (OVERCLAIMED/REJECTED items) |
| 9 | Unexpected error |

## External Gates

External gates (Gate 11 commercial approval, git push authorization) are NOT treated as autonomous-continue blockers. They are tracked as BLOCKED_EXTERNAL_GATE items and carried forward in each prompt cycle.

## Hard Prohibitions (Never Autonomous)

These actions always require explicit human authorization:
- git push
- Package publication (PyPI, NuGet)
- Gate 8 or Gate 11 approval
- MCP activation beyond MODE 3
- Destructive git operations (reset --hard, force push)

## Loop Continuation Model

```
Worker executes -> writes evidence-declaration.yaml
Supervisor validates -> inspects -> grades -> generates next prompt
  If autonomous_continue == True:
    Next worker picks up combined-next-worker-prompt.md
    Loop continues
  If autonomous_continue == False:
    Loop pauses
    Human reviews rework items
    Human approves or modifies next prompt
    Worker resumes
```
