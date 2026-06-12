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
- The Autonomous Supervisor reviews overclaimed/rejected items (supervisor_loop.py output)
- Human review of rework items is an OPTIONAL external audit, not a required production gate
- The agent should attempt self-repair of OVERCLAIMED items before concluding human review is needed
- Apply AGENTS.md §AG1 decision loop: classify whether any stop item can be agent-repaired
- The stop_reason field in the review explains why — use Stop Reason Adjudicator to adjudicate

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success, autonomous continue possible |
| 1 | Declaration not found or schema invalid |
| 3 | Critical rework exists (OVERCLAIMED/REJECTED items) |
| 9 | Unexpected error |

## External Gates

External gates (Gate 11 commercial approval, git push authorization) are NOT treated as autonomous-continue blockers. They are tracked as BLOCKED_EXTERNAL_GATE items and carried forward in each prompt cycle.

## Hard Prohibitions (Apply Human Task Conversion Rule First)

Apply AGENTS.md §AG1-AG4 before classifying any action as prohibited. The accurate classifications:

- **git push:** SCM Agent task (AGENTS.md §AG4.2) when credentials and branch policy allow + sprint
  policy authorizes. When credentials unavailable: `EXTERNAL_BLOCKER: git_push_credentials_unavailable`.
  Not an unconditional human-only prohibition.
- **git commit:** SCM Agent task (AGENTS.md §AG4.1) when sprint policy authorizes (exit 0, clean diff,
  validators pass). Not an unconditional human-only prohibition.
- **Package publication (PyPI, NuGet):** Agent prepares release packet; registry push requires
  `EXTERNAL_BLOCKER: publication_credentials_unavailable` classification when credentials are absent.
- **Gate 8 or Gate 11 approval EXECUTION:** Legitimate external gate — commercial/business decision.
  Preparation (packet, readiness, recommendation) is always agent-owned and never prohibited.
- **MCP activation beyond MODE 3:** Requires explicit policy authorization. Classify specifically.
- **Destructive git operations (reset --hard, force push):** Require explicit policy authority +
  documented rollback. Classify: `BLOCKED: destructive_operation_no_policy_authority`.

## Loop Continuation Model

```
Worker executes -> writes evidence-declaration.yaml
Supervisor validates -> inspects -> grades -> generates next prompt
  If autonomous_continue == True:
    Next worker picks up combined-next-worker-prompt.md
    Loop continues
  If autonomous_continue == False:
    Loop pauses
    Autonomous Supervisor classifies stop items (stop_reason_adjudicator.py)
    Agent attempts self-repair for OVERCLAIMED/REJECTED items where possible
    Human reviews only when Stop Reason Adjudicator returns TRUE_EXTERNAL_GATE
    Worker resumes after repair or after human unblocks TRUE_EXTERNAL_GATE items
```

## Cross-Window Recovery

When a Claude Code window exhausts context or crashes mid-sprint:

1. Open a new window in the same repository
2. `CLAUDE.md` is loaded automatically — it instructs the agent to read `session-resume.md`
3. `session-resume.md` reflects the last **completed** sprint (not the crashed one)
4. The agent checks `approval-gates.md` and resumes from the last known-good state
5. Any in-progress work from the crashed sprint remains in the working tree

**No conversation history is needed.** State is carried entirely by files:
- `reports/supervisor/session-resume.md` — last sprint outcome
- `reports/supervisor/approval-gates.md` — YES/NO continuation
- `reports/supervisor/next-sprint.md` — work items
- `.local/supervisor/continuation-signal.json` — iteration counter

## Iteration Limits

Default: 5 sprints per autonomous loop (configurable in `.supervisor/policies.yaml`).
After `max_iterations`, the system stops with `stop_reason: max_iterations_reached`.
The user can restart with a new limit.

## Replication

For a complete guide on how this system works and how to replicate it for another project, see:
[Autonomous Supervision — Replication Guide](autonomous-supervision-replication-guide.md)
