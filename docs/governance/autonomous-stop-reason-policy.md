# Autonomous Stop Reason Policy

**Authority:** Format Factory Governance
**Sprint:** FORMAT-FACTORY-PERMANENT-AUTONOMY-STOP-REASON-HARDENING-001
**Date:** 2026-06-05

## Central Rule

No component in the Format Factory autonomous train may output STOP, approval-blocked,
human-required, or blocked as a final decision unless the Stop Reason Adjudicator
(`tools/supervisor/stop_reason_adjudicator.py`) classifies that item as:

- `TRUE_EXTERNAL_GATE`
- `UNSAFE_WORKSPACE`

Everything else must map to a continuation decision:
- `CONTINUE_NEXT_ITERATION`
- `LOCAL_REPAIR_CONTINUE`
- `AGENT_OWNED_REVIEW_CONTINUE`
- `AGENT_OWNED_RECOMMENDATION_CONTINUE`
- `RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER`
- `CHECKPOINT_ROLLOVER_CONTINUE`
- `RUFLO_FALLBACK_LOCAL_CONTINUE`
- `POC_READY_CANDIDATE`

## Permanent False Stops

The following signals are PERMANENTLY classified as false stops.
They must NEVER cause the implementation train to stop:

1. **Supervisor ACCEPTED** — continue to next iteration
2. **Evidence package built** — never stops train
3. **max_iterations reached** — checkpoint rollover, not stop
4. **Gate 11 pending (implementation incomplete)** — continue
5. **MODE 5 approval pending** — fall back to local coordinator
6. **Ruflo/claude-flow unavailable** — local coordinator fallback
7. **evidence_quality_zero (repairable)** — repair declaration, rerun
8. **prompt_quality_failure** — repair and continue
9. **missing_sample_outputs** — LOW severity, non-blocking
10. **DIF/SYLK/ZST promotion** — produce proposal, continue
11. **poc-targets proposed delta** — produce proposal, do not stop
12. **Generic "approval-blocked"/"blocked" labels** — always reclassify first

## Permanent TRUE_EXTERNAL_GATE Stops

Only these warrant a terminal stop:

1. git commit/push/merge (human must execute)
2. NuGet/PyPI publication (human must execute)
3. Credentials/secrets (no fallback)
4. Destructive cleanup (no non-destructive alternative)
5. Gate 11 approval EXECUTION (not preparation)
6. Gate 8 approval EXECUTION (not preparation)
7. Actual external MCP daemon activation (when governance requires it)

## Enforcement

- `tools/supervisor/stop_reason_adjudicator.py` — reference implementation
- `.supervisor/schemas/stop-reason-decision.schema.json` — output schema
- `tests/supervisor/test_stop_reason_adjudicator.py` — 91 regression tests
- `tools/supervisor/generate_next_worker_prompt.py` — must not emit false-stop labels
- `tools/supervisor/autonomous_poc_controller.py` — must use adjudicator for all terminal decisions
