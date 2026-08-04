---
artifact_id: TC-FF6-SUPERVISOR-PLAN-REVIEW-001
artifact_type: taskcard
path: taskcards/TC-FF6-SUPERVISOR-PLAN-REVIEW-001.md
format_id: null
product_family: six-python-production
visibility: internal
publish_allowed: false
license: null
provenance_required: true
provenance_status: pending-independent-review
source_hash: null
generated_by: codex
generated_at: 2026-08-02
reusable: false
refresh_policy:
  trigger: review-input-or-plan-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-PROGRAM-CAPABILITIES-001
status: SUPERSEDED_BY_OPERATOR_RECOVERY_DIRECTIVE
lane: INDEPENDENT_REVIEW
skill_ids:
  - plan-hardening
  - post-sprint-audit
  - execution-handoff
release_blockers: []
notes: Full-supervisor review is superseded for routing; independent review now evaluates the minimal-control-then-product recovery package.
---

# TC-FF6-SUPERVISOR-PLAN-REVIEW-001: Independently challenge plan version 7

## Supersession record

**Status:** `SUPERSEDED_BY_OPERATOR_RECOVERY_DIRECTIVE`.

This card is retained for audit and is not marked complete. The operator's
2026-08-03 directive rejected a full-supervisor-first critical path. Independent
review must now inspect the execution-recovery ZIP and answer whether Stage 1
is truly minimal, whether it immediately unlocks NRRD, and whether the NRRD and
SafeTensors slice contracts preserve final production quality. It may not
restore the full six-lane runtime ahead of tangible product evidence.

## Objective

Determine whether plan version 7 and its taskcards are sufficient, internally
consistent, safe to implement, and capable of delivering six deep
production-grade Python libraries. The reviewer must challenge the design from
the supplied immutable ZIP and current GitLab main, not trust plan claims.

## Required review questions

1. Does the plan separate present evidence, target design, and product claims?
2. Can the supervisor recover atomically without duplicate work or promotion?
3. Are lane, path, logical-resource, capacity, validator, and integration
   isolation complete and fail-closed?
4. Can any mutable global file still be written by two lanes?
5. Do taskcards preserve Event 47 and the 0/6 certification boundary?
6. Does each format have a credible route from current state to complete
   obligation coverage, independent interoperability, installed-wheel proof,
   and professional package quality?
7. Are capability breadth, security, resource limits, typing, API stability,
   documentation, fuzz/mutation/performance, cross-platform, extraction,
   supply-chain, and release controls measurable rather than aspirational?
8. Which assumptions are unproved, and what discriminating tests would resolve
   them?

## Review procedure

1. Verify ZIP SHA-256 and bundle-contract validation result.
2. Recompute Git, controller-event, plan, taskcard, and referenced-source
   digests; list drift before analysis.
3. Trace current orchestrator, continuation state, queue, projection priority,
   action guard, coordination, and integration code rather than relying on the
   findings summary.
4. Score all 22 hardening criteria with file/line evidence and counterexamples.
5. Model crash/concurrency/adversarial scenarios and identify missing state,
   transaction, or invalidation edges.
6. Audit every new taskcard for exact inputs, writable outputs, skills,
   prerequisites, acceptance criteria, verification, rollback, successor, and
   non-claim.
7. Classify each finding `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, or `NOTE`, with
   root cause and a durable remediation. Avoid prompt-only or local patches.
8. Produce one verdict: `ACCEPT_FOR_IMPLEMENTATION`,
   `ACCEPT_WITH_PREIMPLEMENTATION_REPAIRS`, or `REJECT_AND_REDESIGN`.

## Mandatory outputs

- Input/digest verification report.
- Evidence-backed architecture and consistency findings.
- 22-item hardening score with gaps.
- Threat/failure/concurrency model.
- Taskcard completeness matrix.
- Proposed exact plan/taskcard patches or unambiguous repair instructions.
- Activation preconditions and regression suite.
- Verdict and unresolved uncertainties.

## Acceptance criteria

- [ ] Every material claim cites an inspected file, executed check, or marked uncertainty.
- [ ] Symptoms, root causes, and structural weaknesses are separated.
- [ ] Current product progress is not inferred from taskcard/test presence.
- [ ] All critical/high findings have a concrete testable disposition.
- [ ] The reviewer does not approve product certification or Gate 10.
- [ ] The runtime remains inactive until a later evidence-backed activation event.

## Successor rule

If accepted, generate bounded implementation taskcards from
`TC-FF6-SUPERVISOR-RUNTIME-001` without changing Event 47 product truth. If
repairs are required, update the plan/taskcards, rebuild the review ZIP, and
repeat this independent review. Product NRRD R3 may continue through the safe
fallback when disjoint from review work.
