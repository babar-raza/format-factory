# Autonomous Supervisor Audit — ff-arch-20260621-001

## Summary

**Status: FUNCTIONAL with significant infrastructure. Key lane separation NOT enforced by code.**

The autonomous supervisor has extensive machinery: continuation logic, evidence declaration,
governance validators (38), sprint grading, lane routing, and plan locking. However,
machinery and product lanes are NOT separated by a hard enforcement mechanism — only by
prompt/governance rules.

---

## Continuation Logic Assessment

### check_continuation.py
- EXISTS and functional
- Returns CONTINUE/STOP verdict with reason
- Enforces: SESSION_MISMATCH, CHAT_ID_MISMATCH (non-overridable per CLAUDE.md)
- Enforces: plan lock (ACTIVE_PLAN_INCOMPLETE)
- Enforces: MAX_ITERATIONS (with governed rollover)
- Autonomous continue: currently False (requires reset or plan completion signal)

### Plan Lock
- `write_plan_lock.py` — creates `.local/supervisor/plan-locks/{plan-id}.json`
- `--terminal` flag: writes `status: TERMINAL_CLOSED` → blocks sprint loop
- `--complete` flag: marks done for future sessions
- CCI-MVP enforcement: session_id matching prevents cross-chat signal consumption

---

## Lane Separation Assessment

### Current Lane Separation (from plans/strategic/spec-to-feature-radical-correction-plan.md)

The plan defines Lanes 1-15:
- Lanes 1-6, 14, 15: System healing (MUST complete first)
- Lanes 7-13: Product regeneration (BLOCKED until healing lanes complete)
- Lane P6: Product deepening (runs IN PARALLEL with healing)

### Is Lane Separation Enforced by Code?

**NO.** The spec-to-feature correction plan documents the lane structure but:
1. `check_continuation.py` does NOT check which lane is active
2. Governance validators check declaration content but not lane assignment
3. An agent can start a product deepening sprint when a healing lane should be running
4. The lane routing (`autonomous_route_decider.py`, `autonomy_route_ledger.py`) exists
   but its enforcement is PROMPT-based, not code-enforced

### Can Lane Contamination Happen?

**YES.** Evidence of contamination in recent history:
- MEMORY.md notes: "Root cause of prior failure: after TC-C3-001/TC-C3-003, fell back to
  next-sprint.md product deepening instead of continuing to TC-DIAG-001"
- The plan precedence rule requires per-chat plan > ledger, but this was violated in the past

---

## GOV_BLOCK Enforcement

**TC-GUARD-001 (BLOCK mode):** Unconditional BLOCK for PRODUCT_SOURCE/PRODUCT_TEST items
without gap_ledger_ref, capability_ref, or spec_fact_refs. Added to rework_items post-grade.

**V42 deepening_suspension_validator:** Rejects PRODUCT_SOURCE items with `_mod_\d+_times_\d+`
in evidence_paths.

**GOV_BLOCK:monolith_detection_validator:** Triggers when source files exceed LOC caps.
- ZST codec: healed (1558/4210 LOC)
- XCF parser: healed (1301/3997 LOC)
- FODG codec: healed (3176/3176 LOC)

---

## Gate 11 Stop Behavior

Is there a mechanism to stop at Gate 11 and wait for Babar Raza?

**YES — via task classification.** In next-sprint.md:
```
[external-gate] TASK-005: Submit FODS Gate 11 for Babar Raza approval
```

`stop_reason_adjudicator.py` classifies this as a TRUE_EXTERNAL_GATE.
The check_continuation.py returns STOP for TRUE_EXTERNAL_GATE reasons.

**However:** The current code has Gate 11 PREPARATION as agent-owned.
The gate stop only triggers when the task is explicitly classified as external-gate
in the sprint prompt. If a sprint prompt doesn't classify it that way, the agent
may try to self-approve.

---

## Evidence Declaration Quality

Evidence declarations have:
- Required fields: evidence_root, start_time, end_time, git_head_start, git_head_end,
  git_status_final, declared_scope, incomplete_work_items, changed_files, tests_run,
  test_results, reports_created, worker_self_verdict, next_recommended_work
- Validation: `sprint_executor_validate.py --repair` available
- Schema: `additionalProperties: false` — strict

Sprint grading: AI + governance validators combined verdict
Known gap: `evidence_quality_zero` false stop when LLM grader unavailable

---

## Supervisor Readiness for Spec-to-Feature Pipeline

| Requirement | Present? | Quality |
|---|---|---|
| Sprint evidence tracking | YES | Good |
| Governance validators | YES | 38 validators |
| Lane routing | PARTIAL | Prompt-enforced only |
| Gate 11 stop | YES | Classification-based |
| SAL fact validation | NO | Not integrated |
| QName compliance check | NO | Not a validator |
| Source generation gate | NO | Not present |
| Cross-session state isolation | YES (CCI-MVP) | Good |
| Plan precedence enforcement | YES (plan lock) | Good |
