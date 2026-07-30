---
artifact_id: FF6-CLAUDE-EXECUTION-HANDOFF-EVENT-30
artifact_type: provider_execution_handoff
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Claude execution handoff — Event 30

Continue the active mission without asking for continuation. Use the same
controller, taskcard, skills, evidence rules, and checkpoint protocol that
Codex used. Provider identity changes; mission state and acceptance criteria do
not.

## Locked scope

- Repository: `C:\Users\prora\OneDrive\Documents\GitHub\format-factory`
- Canonical SCM: GitLab remote `origin`, branch `main`
- Goal: `FF6-PRODUCTION-LIBRARIES-001`
- Controller state: `CONTRACT`
- Journal head: `FF6-EVENT-000030`
- Active task: `TC-FF6-XLIFF-PROFILE-SURFACE-001`
- Exact microstep: `XLF-04-BATCH-005-PARTIAL-002-B`
- Implementation ancestor:
  `e13e103de0bb789ff51a8e931af0fb649474be20`

Do not create a branch, use GitHub, move work to an isolated stale worktree,
or reinterpret old provider notes as current authority.

## First actions

1. Fetch and verify GitLab main.
2. Read `AGENTS.md`, `docs/governance/codex-adapter.md` or the Claude
   equivalent, `docs/governance/skill-only-policy.yaml`,
   `plans/master-plan.md`, and the applicable skill contracts.
3. Run the handover validator before mutation.
4. Register a fresh coordination identity.
5. Inspect live agents, leases, conflicts, and exact path status.
6. If Event 31 or later exists, validate and follow it. Do not duplicate Event
   30.
7. Replay current artifact checks and the three immutable smoke tests.
8. Create fresh execution manifests for:
   - test-driven-development;
   - ingest-spec-sal;
   - sal-pipeline-heal.
9. Start the next candidate with a RED test. Do not edit the decision source
   first.

## Current proof and non-proof

Proven:

- the 1,130-row census is bound to pinned authority bytes;
- one candidate decision is independently reasoned and content-addressed;
- the real Batch 005 compiler requires complete adjudication proof;
- every relevant proof dependency has a negative drift control;
- 26 source-bound rows exist and the exact current inventory is reproducible;
- the implementation commit is pushed to GitLab main.

Not proven:

- the remaining 1,129 candidate dispositions;
- the remaining 79 expected obligation rows;
- complete Core semantics or any XLIFF module surface;
- XLF-04 completion;
- a production XLIFF parser/writer;
- any product certification, promotion, release, or gate.

## Partial-002-B TDD target

Candidate:

```text
XLF-CAND-CORE-SCHEMATRON-00C4A041AF12C8A1
candidate_content_sha256:
0a37761215603eb4db3f9602f6e979869b4f1f44c124c1f5ca2183cba1d7578a
```

Authority:

```text
source:   SRC-XLF-002
member:   schemas/xliff_core_2.1.sch
location: schematron/rule[47]/assert[2]
context:  xlf:pc[@subFlowsStart][ancestor::xlf:segment|ancestor::xlf:ignorable]
test:     @subFlowsEnd
message:  'subFlowsStart' and 'subFlowsEnd' must be used in pair.
```

Generated proposal:

- `SAL-XLIFF-CORE-AGENT-VALIDATOR-001`
- `SAL-XLIFF-CORE-HIERARCHY-IGNORABLE-001`
- `SAL-XLIFF-CORE-HIERARCHY-SEGMENT-001`
- `SAL-XLIFF-CORE-INLINE-PC-001`

Do not copy this list into the verified decision. Independently determine the
direct semantic owner. The ancestor names limit rule applicability; they do
not automatically establish hierarchy behavior. The generic validator ID is a
downstream capability, not necessarily the direct rule owner.

Required RED controls:

1. Generated proposal alone cannot increment `verified_disposition_count`.
2. `segment` and `ignorable` context tokens cannot create independent
   hierarchy obligations.
3. `subFlowsStart` without `subFlowsEnd` is rejected.
4. The reciprocal `subFlowsEnd` rule is handled from its own exact authority
   occurrence, not inferred.
5. Any candidate, occurrence, member, denominator, decision, SAL, or
   adjudicator drift invalidates the projection.
6. Duplicate, unknown, foreign-format, missing, or unreasoned decisions fail
   closed.

## Expected execution sequence

1. Reproduce current green from immutable commit.
2. Write a focused failing test for the new candidate decision.
3. Inspect exact authority and canonical SAL facts.
4. Add one reasoned decision, separating accepted and rejected mappings.
5. Make the smallest reusable adjudication/compiler change.
6. Regenerate only affected artifacts.
7. Preserve all 26 existing obligation IDs and all 1,130 candidate IDs.
8. Run focused tests, nine dependency drift classes, static checks,
   format-contract and production-program regression, SAL verification,
   authority audit, transcript checks, and three clean generations.
9. Record the honest boundary. Counts may remain unchanged if the authority
   supports no new denominator obligation.
10. Explicitly stage reviewed paths, run coordination precommit, commit, and
    push GitLab `main`.
11. Replay from the immutable commit.
12. Append one new native event and update projections before handover.

## Failure handling

- A test regression creates a repair task; it does not weaken the test.
- An oracle contradiction requires a discriminating test and authority review.
- A dirty workspace is preserved and attributed.
- A live XLIFF owner triggers the already-serialized UBL fallback only.
- A stale digest invalidates descendants.
- Three materially different failed repair attempts may mark only that
  obligation technically blocked; other safe work continues.
- Missing publication credentials never blocks completing release-ready
  artifacts.

## Completion rules

Partial-002-B is complete only when its exact decision and negative controls
are committed, pushed, independently replayed, journaled, and projected.
XLF-04 remains incomplete unless all Core and module obligation exit criteria
pass. The overall mission remains active until six libraries are technically
certified and extraction-ready.

Use [NEXT-MICROSTEP.yaml](NEXT-MICROSTEP.yaml) for machine-readable steps and
[event-30/RUNBOOK.md](event-30/RUNBOOK.md) for exact replay commands.
