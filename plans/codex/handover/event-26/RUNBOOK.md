---
artifact_id: FF6-EVENT-26-HANDOVER-RUNBOOK
artifact_type: immutable_handover_runbook
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
---

# Event 26 Resume Runbook

## 1. Establish canonical state

From the repository root:

```powershell
git fetch origin
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 18bb295f94e43338611ef88caff073eed17411c9 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --self-test
```

If `origin/main` advanced, recompute from the latest journal event and
controller. Never force this Event 26 packet onto a newer state.

## 2. Rehydrate governance

1. Read `AGENTS.md`.
2. Read the provider adapter and canonical skill policy.
3. Read the product goal, execution plan, full FF6 journal, controller,
   current gaps, task index, and active XLIFF taskcard.
4. Register a fresh coordination identity.
5. Claim only exact Batch 005 files.
6. Resolve the registered skill route; create a live execution manifest.
7. Run the mutation guard and preflight before each write.

No provider-local identity or lease is part of this packet.

## 3. Revalidate Batch 004

Confirm:

- source commit `1fef79b9...` is on `origin/main`;
- source, test, matrix, denominator, inventory, census, and three receipts
  match Event 26 digests;
- 34 focused tests and affected regressions still pass;
- all four artifact check modes pass;
- XLIFF authority audit is 5/5 MATCH;
- three census generations are byte-identical;
- non-modal prose remains false, coarse count remains 78, and obligation
  closure remains 25/105 with 80 missing.

Input drift invalidates downstream evidence. Do not reuse a stale receipt.

## 4. Execute XLF-04-BATCH-005 with TDD

Write RED tests for exhaustive non-modal prose classification, exact
replacement of every coarse disposition, denominator expansion, preservation
of all 25 existing rows, source-bound compilation of remaining IDs, and
fail-closed tamper cases.

Begin with the independent post-commit failures: forged normalized requirement
text, member digest, source digest, and occurrence location must be rejected.
Add explicit candidate classes and a content-sensitive digest that binds every
occurrence without making stable candidate identity depend on output order.

Implement deterministic classification and compilation against exact pinned
OASIS bytes. Every authority item must have exactly one disposition. A
non-obligation needs a stable reason code and source location. A new normative
semantic needs an expected ID and source-bound obligation. Do not count a
candidate mapping as an obligation row.

Keep these states distinct:

```text
SOURCE_LOCATED_RULE_DISPOSITION_UNVERIFIED
SOURCE_BOUND_UNVERIFIED
CANONICAL_SAL_VERIFIED
```

Only the last can support XLF-04 closure, and only after the denominator is
exhaustive with zero missing IDs.

## 5. Verify

Run focused tests, format-contract and production-program regressions, Ruff,
strict Mypy, Pyright, bytecode compilation, every artifact check mode, XLIFF
authority audit, three clean generations, and transcript validation. Record
exact commands, versions, outcomes, digests, known baseline conditions, and
truth limits.

## 6. Integrate atomically

1. Commit and push the bounded implementation/evidence set to GitLab `main`.
2. From that immutable commit, append one native FF6 event and update derived
   controller/task projections through `plan-control`.
3. Validate the event chain and current-state consistency.
4. Commit/push the control projection.
5. Refresh the provider-neutral handover through its registered skill.
6. Commit/push the packet and verify `origin/main`.
7. Release only this identity's leases and mark it complete.

Use explicit staging. Never use GitHub, another branch, broad staging, reset,
clean, restore, or stash.

## 7. Stop boundary

Stop a planned shift only after the state is `RESUMABLE`. If work is RED-only,
local-only, unjournaled, or dirty, record it as a recovery state and do not
claim a clean checkpoint.
