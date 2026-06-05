# Human Gate Classification Policy

**Authority:** Format Factory Governance
**Sprint:** FORMAT-FACTORY-PERMANENT-AUTONOMY-STOP-REASON-HARDENING-001
**Date:** 2026-06-05

## Policy Statement

The agent acts on Babar Raza's behalf for review, classification, recommendation,
local implementation, validation, and continuation. The agent does NOT impersonate
Babar's release approval, push authorization, publication authorization, or
credential authority.

The key distinction is between **preparation** (always agent-owned) and **execution**
(human-only when it is a true external gate).

## Agent-Owned Actions (never require human to proceed)

The agent may independently perform all of these without waiting for human approval:

### Evidence and Review
- Review evidence declarations and grade quality
- Classify gate states and human-gate items
- Prepare Gate 11 readiness packet
- Prepare Gate 8 readiness assessment
- Prepare release recommendation
- Prepare commit candidate summary and changed-file manifest
- Prepare publication packet and release checklist
- Prepare proposed poc-targets delta
- Prepare DIF/SYLK/ZST promotion recommendation

### Implementation
- Choose local coordinator fallback (when Ruflo/claude-flow unavailable)
- Continue without external daemon (MODE 5 / Ruflo pending)
- Repair evidence declarations
- Run tests
- Repair failing tests
- Choose next product gaps from poc-targets.yaml
- Generate next sprint prompt
- Mark false stops as false stops
- Implement any product capability in allowed paths
- Implement target writer libraries for dogfood routes
- Build and rebuild packages locally
- Update state and memory files

### Classification and Analysis
- Classify whether a gate is agent-owned vs human-only
- Classify whether a stop reason is false
- Produce proposed deltas (poc-targets, capability matrix)
- Classify terminal vs non-terminal states
- Analyze proof graphs, evidence quality, test results

## Human-Only Actions (require explicit authorization)

These require the human (Babar Raza) to explicitly act:

### Release Execution
- Actual Gate 11 release approval (sign-off that commercial product is ready)
- Actual Gate 8 approval (if governance requires formal sign-off)
- Actual git commit (explicit user authorization)
- Actual git push (explicit user authorization)
- Actual git merge (explicit user authorization)
- Actual NuGet/PyPI/GitHub publication

### Security and Infrastructure
- Credentials / API keys / secrets
- Destructive git operations (reset --hard, clean -f, stash drop)
- Activating new MCP servers
- Enabling paid external AI APIs

### Business Decisions
- Business decisions where project policy cannot infer a safe default
- Official poc-targets.yaml authority changes (not proposed deltas)

## The Separation Principle

For every action that involves human-only execution, the agent first prepares:

| Human-Only Execution | Agent Preparation (first) |
|---------------------|--------------------------|
| Gate 11 approval | Prepare Gate 11 readiness packet |
| Git commit | Prepare commit candidate summary |
| Git push | Prepare push checklist and diff |
| Publication | Prepare publication packet |
| Credentials | Identify what credential is needed; provide safe fallback if possible |

The agent never bypasses the human-only step for execution.
The agent never stops implementation because the human-only step is pending.

## Label Enforcement

In next-sprint prompts, task labels must be one of:
- `[agent-owned]` — agent executes this task
- `[external-gate]` — human must execute (TRUE_EXTERNAL_GATE only)
- `[release-approval-pending]` — POC-ready; human approves release when ready
- `[unsafe-stop]` — UNSAFE_WORKSPACE; report and stop

Forbidden labels for agent-owned work:
- `[approval-blocked]`
- `[blocked]`
- `[human-required]`
- `[stop]`

These labels must not appear unless Stop Reason Adjudicator returns
`TRUE_EXTERNAL_GATE` or `UNSAFE_WORKSPACE` for that specific task.
