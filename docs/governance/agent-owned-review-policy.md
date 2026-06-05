# Agent-Owned Review Policy

**Authority:** Format Factory Governance
**Sprint:** FORMAT-FACTORY-PERMANENT-AUTONOMY-STOP-REASON-HARDENING-001
**Date:** 2026-06-05

## Core Principle

The autonomous train agent acts as Babar Raza's delegate for all implementation,
review, classification, and continuation work. The agent does not impersonate
Babar's release approval authority, but it does own the preparation and classification
of every gate state.

## What "Agent-Owned Review" Means

When the Stop Reason Adjudicator returns `AGENT_OWNED_REVIEW_CONTINUE`, it means:

1. The agent must NOT stop
2. The agent must classify the ambiguous item more specifically
3. After classification, the agent either continues or escalates to the correct gate
4. The agent documents the classification result

## What "Agent-Owned Recommendation" Means

When the adjudicator returns `AGENT_OWNED_RECOMMENDATION_CONTINUE`, it means:

1. The agent produces a proposed delta/recommendation document
2. The agent does NOT directly mutate authority files
3. The proposed delta is advisory — it is not applied automatically
4. The agent continues implementation work while the recommendation is pending

## DIF/SYLK/ZST Reconsideration Policy

When DIF, SYLK, or ZST promotion/reconsideration is flagged:

1. Agent produces `proposed-delta.yaml` in the sprint report directory
2. Agent classifies current status based on existing project policy
3. Agent does NOT stop for this classification
4. Agent continues next implementation lanes

The proposed delta is a file, not an action. The agent can always produce a file.

## poc-targets.yaml Policy

1. Agent may read `product-capability-matrix/poc-targets.yaml` freely
2. Agent produces proposed changes as `proposed-poc-targets-delta.yaml`
3. Direct mutation requires explicit user instruction to proceed
4. Proposed delta production is always agent-owned, never requires human approval

## Next-Sprint Prompt Advisory Requirement

Every generated next-sprint prompt MUST include:

```
ADVISORY ONLY — Read Stop Reason Adjudicator Before Treating Any Task As Blocked

For any task marked [approval-blocked], [blocked], or [human-required]:
1. Run: python tools/supervisor/stop_reason_adjudicator.py "<signal>"
2. If decision is not TRUE_EXTERNAL_GATE or UNSAFE_WORKSPACE: repair/continue
3. If decision is RUFLO_FALLBACK: use local coordinator
4. If decision is CHECKPOINT_ROLLOVER: increment iteration and continue
```

## Fallback Chain

When an external tool or daemon is unavailable:

1. Check if local coordinator can proceed (almost always YES)
2. Use `tools/supervisor/stop_reason_adjudicator.py` to adjudicate
3. If adjudicator says RUFLO_FALLBACK: proceed as local coordinator
4. If adjudicator says TRUE_EXTERNAL_GATE: report to user and wait
5. If adjudicator says CONTINUE_NEXT_ITERATION: continue immediately

The fallback chain never results in a spurious stop.
