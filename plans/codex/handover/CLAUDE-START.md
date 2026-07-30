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

The deeper read-only reassessment completed after Event 30 identifies the
direct owner as `SAL-XLIFF-CORE-INLINE-PAIRING-001`. This is a finding to test,
not a completed implementation. The current adjudicator contains a structural
defect at `tools/spec/xliff_core_candidate_adjudication.py`: it requires the
union of accepted and rejected IDs to equal the generated proposal set. That
means an independent decision cannot accept a valid denominator obligation
that the generator omitted. Repair that invariant before adding the decision;
otherwise the new evidence would still be generator-constrained.

The reverse direction is a separate candidate and must be proven separately:

```text
candidate: XLF-CAND-CORE-SCHEMATRON-4BE479DD3F5875EF
digest:    246f6e9e4c64fe142760045dbca69070405ae50f552b34387ce8709c3c7226e3
location:  schematron/rule[46]/assert[2]
context:   xlf:pc[@subFlowsEnd][ancestor::xlf:segment|ancestor::xlf:ignorable]
test:      @subFlowsStart
occurrence:
1443b1090a3a0f118c4c478fbabe27a2fef549a4c3ad0168d7b6ef0d95d8b80f
```

`SAL-XLIFF-00005` currently has no exact manifest assertion for either mutual
presence rule. Repair its claim/evidence/receipt through `ingest-spec-sal` and
`sal-pipeline-heal`; do not hand-edit only downstream hashes. The pair
assertions are present in the pinned 2.1 Schematron. The pinned 2.0 package
defines both attributes but the reassessment did not find the equivalent
must-be-used-in-pair requirement. Therefore either find and bind separate 2.0
normative authority or narrow this exact pairing obligation to `xliff_2.1`.
Never project the 2.1 rule into 2.0 merely to preserve the current denominator.

Required RED controls:

1. Generated proposal alone cannot increment `verified_disposition_count`.
2. A valid denominator obligation omitted by the proposal can be independently
   accepted, and the normalized artifact exposes it as unproposed.
3. Every generated proposal ID is accepted or reasoned-rejected.
4. `segment` and `ignorable` context tokens cannot create independent
   hierarchy obligations.
5. `subFlowsStart` without `subFlowsEnd` is rejected.
6. `subFlowsEnd` without `subFlowsStart` is rejected from its exact authority
   occurrence, not inferred.
7. One reciprocal decision cannot compile a bidirectional pairing obligation;
   both exact candidates are required.
8. Any candidate, occurrence, member, denominator, decision, SAL, or
   adjudicator drift invalidates the projection.
9. Duplicate, unknown, foreign-format, missing, or unreasoned decisions fail
   closed.

## Expected execution sequence

1. Reproduce current green from immutable commit.
2. Write focused failing tests for generator-omitted acceptance, reciprocal
   proof, and one-sided compilation rejection.
3. Inspect both exact authority occurrences and canonical `SAL-XLIFF-00005`.
4. Repair the independent-adjudication invariant.
5. Add two reasoned decisions that accept only the direct pairing owner and
   explicitly reject every incidental proposal.
6. Repair the canonical SAL proof and profile claim, then regenerate only
   affected artifacts.
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
