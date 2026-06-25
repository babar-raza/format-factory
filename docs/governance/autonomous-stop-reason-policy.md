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

Only these warrant a terminal stop. Apply the Human Task Conversion Rule (AGENTS.md §AG1) before
classifying. Use the exact blocker category, not "human must":

1. **git push** — classified as `EXTERNAL_BLOCKER: git_push_credentials_unavailable` when credentials
   or branch protection are unavailable for the agent identity. When available, this is an SCM Agent
   task (AGENTS.md §AG4.2), not a terminal stop.
   **git commit** — SCM Agent task (AGENTS.md §AG4.1) when sprint policy authorizes. Only a terminal
   stop when sprint policy and explicit user authorization are both absent.
   **git merge** — requires explicit policy authority. Classify: `BLOCKED: merge_no_policy_authority`.
2. **NuGet/PyPI publication** — agent prepares release packet. Actual registry push classified as
   `EXTERNAL_BLOCKER: publication_credentials_unavailable` when registry credentials unavailable.
3. **Credentials/secrets (no fallback)** — `EXTERNAL_BLOCKER: credentials_unavailable`.
4. **Destructive cleanup (no non-destructive alternative)** — `BLOCKED: destructive_no_safe_alternative`.
5. **Gate 11 approval EXECUTION** — commercial business decision by project lead (Babar Raza). Preparation
   is always agent-owned: evidence packet, readiness assessment, recommendation. Only the final
   commercial sign-off requires business authority.
6. **Gate 8 approval EXECUTION** — formal sign-off where governance requires it. Preparation is
   always agent-owned.
7. **Actual external MCP daemon activation (when governance requires it)** — `BLOCKED: mcp_activation_requires_policy`.

## Enforcement

- `tools/supervisor/stop_reason_adjudicator.py` — reference implementation
- `.supervisor/schemas/stop-reason-decision.schema.json` — output schema
- `tests/supervisor/test_stop_reason_adjudicator.py` — 91 regression tests
- `tools/supervisor/generate_next_worker_prompt.py` — must not emit false-stop labels
- `tools/supervisor/autonomous_poc_controller.py` — must use adjudicator for all terminal decisions
- `docs/governance/authorization-policy-v1.yaml` — canonical authorization policy contract (FORMAT_FACTORY_GATE_AUTHORIZATION_V1)
