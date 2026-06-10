# Stop Reason Taxonomy

**Sprint:** FORMAT-FACTORY-PERMANENT-AUTONOMY-STOP-REASON-HARDENING-001

## Purpose

This taxonomy defines every stop signal that can appear in the Format Factory
autonomous train and maps it to the correct adjudicated decision.

## Rule Summary (18 Rules)

| # | Signal | Normalized | Decision | Terminal |
|---|--------|------------|----------|---------|
| 1 | supervisor_accepted | SUPERVISOR_VERDICT | CONTINUE_NEXT_ITERATION | No |
| 1 | supervisor_accepted + poc_ready | SUPERVISOR_VERDICT | RELEASE_APPROVAL_PENDING | Yes (release only) |
| 2 | accepted_with_rework | SUPERVISOR_VERDICT | LOCAL_REPAIR_CONTINUE | No |
| 3 | evidence_package_built | EVIDENCE_QUALITY | CONTINUE_NEXT_ITERATION | No |
| 4 | evidence_quality_zero (repairable) | EVIDENCE_QUALITY | LOCAL_REPAIR_CONTINUE | No |
| 4 | evidence_quality_zero (corrupted) | EVIDENCE_QUALITY | UNSAFE_WORKSPACE | Yes |
| 5 | prompt_quality_failure | PROMPT_QUALITY | LOCAL_REPAIR_CONTINUE | No |
| 5 | prompt_would_cause_unsafe_edit | PROMPT_QUALITY | UNSAFE_WORKSPACE | Yes |
| 6 | max_iterations_reached | MAX_ITERATION | CHECKPOINT_ROLLOVER_CONTINUE | No |
| 7 | mode_5_approval_pending | MCP_MODE | RUFLO_FALLBACK_LOCAL_CONTINUE | No |
| 7 | mode_5 + requires_external_daemon | MCP_MODE | TRUE_EXTERNAL_GATE | Yes |
| 8 | ruflo_unavailable | RUFLO_MODE | RUFLO_FALLBACK_LOCAL_CONTINUE | No |
| 9 | gate_11_pending + poc_ready | GATE_11 | RELEASE_APPROVAL_PENDING | Yes (release only) |
| 9 | gate_11_pending + poc NOT ready | GATE_11 | CONTINUE_NEXT_ITERATION | No |
| 10 | gate_8_pending + poc_ready | GATE_8 | RELEASE_APPROVAL_PENDING | Yes (release only) |
| 10 | gate_8_pending + poc NOT ready | GATE_8 | CONTINUE_NEXT_ITERATION | No |
| 11 | git_push_required | PUSH_COMMIT | TRUE_EXTERNAL_GATE | Yes |
| 12 | publication_required | PUBLICATION | TRUE_EXTERNAL_GATE | Yes |
| 13 | credentials_required | CREDENTIAL | TRUE_EXTERNAL_GATE | Yes |
| 13 | credentials + safe_fallback | CREDENTIAL | LOCAL_REPAIR_CONTINUE | No |
| 14 | destructive_cleanup | DESTRUCTIVE_OPERATION | TRUE_EXTERNAL_GATE | Yes |
| 14 | destructive + non_destructive_alt | DESTRUCTIVE_OPERATION | LOCAL_REPAIR_CONTINUE | No |
| 15 | business_decision + policy_can_infer | BUSINESS_DECISION | AGENT_OWNED_RECOMMENDATION | No |
| 15 | business_decision + cannot_infer | BUSINESS_DECISION | TRUE_EXTERNAL_GATE | Yes |
| 16 | dif_reconsideration | PRODUCT_GAP | AGENT_OWNED_RECOMMENDATION | No |
| 17 | poc_targets_proposed_delta | PRODUCT_GAP | AGENT_OWNED_RECOMMENDATION | No |
| 18 | dirty_git_state (classified) | WORKSPACE_SAFETY | CONTINUE_NEXT_ITERATION | No |
| 18 | dirty_git_state (unclassified) | WORKSPACE_SAFETY | LOCAL_REPAIR_CONTINUE | No |
| 18 | source_corruption | WORKSPACE_SAFETY | UNSAFE_WORKSPACE | Yes |

## Critical Classification: Things That Are NEVER Terminal

1. **Supervisor ACCEPTED** — always continue unless POC-ready + Gate 11
2. **Evidence package built** — never stops train
3. **max_iterations reached** — checkpoint rollover, not stop
4. **Gate 11 pending when POC not complete** — continue implementation
5. **MODE 5 approval pending** — fall back to local coordinator
6. **Ruflo/claude-flow unavailable** — local coordinator fallback
7. **evidence_quality_zero (repairable)** — repair declaration and rerun
8. **prompt_quality_failure** — repair and continue
9. **missing_sample_outputs** — LOW severity, non-blocking
10. **DIF/SYLK/ZST promotion** — produce proposal, continue
11. **poc-targets proposed delta** — produce proposal, do not stop
12. **Generic "approval-blocked"/"blocked" labels** — always reclassify first

## Critical Classification: TRUE_EXTERNAL_GATE (always terminal)

1. git commit/push/merge
2. NuGet/PyPI publication
3. Credentials/secrets (no fallback)
4. Destructive cleanup (no alternative)
5. Gate 11 approval execution (not preparation)
6. Gate 8 approval (formal execution)
7. Actual external MCP daemon activation

## Critical Classification: RELEASE_APPROVAL_PENDING (terminal for release, NOT for implementation)

1. Gate 11 pending + POC-ready candidate complete
2. Gate 8 pending + POC-ready candidate complete
3. Commercial release approval + POC-ready

Note: Agent prepares packet; human executes approval. These are two separate actions.
