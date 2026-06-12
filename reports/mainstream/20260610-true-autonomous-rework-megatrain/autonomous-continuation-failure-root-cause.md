# Autonomous Continuation Failure — Root Cause Analysis
# Sprint: TRUE-AUTONOMOUS-REWORK-MEGATRAIN
# Generated: 2026-06-10

## Executive Summary

The prior sprint (TRUE-AUTONOMOUS-MAINSTREAM-CONTINUATION-001) completed with supervisor
exit 0 and `AUTONOMOUS_CONTINUE: YES` in approval-gates.md, but the agent returned to
the human instead of auto-continuing. Three compounding root causes explain this failure.

## Root Cause 1: `autonomous_continue` type mismatch (PRIMARY)

**CLAUDE.md condition 3** states:
> `.local/supervisor/continuation-signal.json` exists with `"autonomous_continue": true`

**Actual signal value:** `"autonomous_continue": "true_with_rework"` (STRING, not boolean `true`)

The agent performed a strict equality check (`value === true`) which returns `false` for
the string `"true_with_rework"`. This is the **primary root cause** — the agent interpreted
a valid continuation state as a stop signal.

**autonomous_cycle.py** lines 696-697 intentionally set:
```python
elif rework_items and not overclaimed:
    auto_continue_value = "true_with_rework"
```

This is a valid continuation state (rework items exist but safe lanes can proceed), but
CLAUDE.md's instructions only accept boolean `true`, creating a mismatch between the
supervisor code and the agent instructions.

## Root Cause 2: `advisory_prompt_executable: false` misinterpreted

The continuation-signal.json included `"advisory_prompt_executable": false`. The prior
agent likely saw this and interpreted it as "the prompt cannot be executed autonomously."

**Reality:** `advisory_prompt_executable` is ALWAYS `false` by design.
- `continuation_state.py:99` — hardcoded `False`
- `evidence_continuation.py:124,225` — hardcoded `False`
- `continuation_state.py:136-137` — validator REJECTS `true`

This field means "the Markdown advisory prompt is not a machine-executable action" — it
does NOT mean "autonomous continuation is blocked." The agent misread this signal.

## Root Cause 3: CLAUDE.md lacks `"true_with_rework"` handling

CLAUDE.md's Autonomous Continuation section lists 5 conditions. Condition 3 requires
`"autonomous_continue": true` (exact boolean). There is no mention of:
- `"true_with_rework"` as a valid truthy value
- `continuation_state` field (which has the actual classified state)
- How to handle rework items during autonomous continuation

The agent had no instruction for the "rework but safe lanes available" case.

## Contributing Factor: Next-sprint.md had no rework section

The generated next-sprint.md (Section 2: Rework / Repair) contained "None" — but the
work-item-grades.yaml showed 3 items (TAC-W01, W03, W04) as REWORK_REQUIRED. The prompt
generator did not inject rework items into the next sprint prompt, so even if the agent
had continued, it would not have known what to fix.

## Fix Plan

| Fix | Type | Scope |
|-----|------|-------|
| Update CLAUDE.md condition 3 to accept truthy values | Documentation | CLAUDE.md |
| Add `"true_with_rework"` handling instructions | Documentation | CLAUDE.md |
| Add `continuation_state` checking to CLAUDE.md | Documentation | CLAUDE.md |
| Clarify `advisory_prompt_executable` is always false | Documentation | CLAUDE.md |
| Inject rework items into next-sprint.md Section 2 | Code | generate_next_worker_prompt.py |

## Evidence

- continuation-signal.json: `.local/supervisor/continuation-signal.json`
- approval-gates.md: `reports/supervisor/approval-gates.md`
- session-resume.md: `reports/supervisor/session-resume.md`
- work-item-grades.yaml: `reports/supervisor/work-item-grades.yaml`
- autonomous_cycle.py: `tools/supervisor/autonomous_cycle.py` (lines 696-697)
- continuation_state.py: `tools/supervisor/continuation_state.py` (line 99)
- evidence_continuation.py: `tools/supervisor/evidence_continuation.py` (lines 124, 225)
