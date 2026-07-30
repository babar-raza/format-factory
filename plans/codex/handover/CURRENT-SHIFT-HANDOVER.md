---
artifact_id: FF6-CURRENT-SHIFT-HANDOVER-EVENT-31
artifact_type: provider_shift_handover
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Codex to Claude shift handover — Event 31

## Live transfer condition

The durable remote checkpoint is clean Event 31 at control commit
`240474babf868fa141850d4ed4792d3a8269ef28`. The prior executor committed
attempt `d99fc6bf3679cd39396afbf5621847e3009ddf31`, then correctly recorded
that its mechanical green result failed the hardened semantic acceptance
contract. The attempt is preserved, not promoted.

The executor still held XLIFF leases at the last observation even though its
bytes were committed. Claude must requery coordination and GitLab. If the
owner remains live, do not overlap XLIFF; use only the serialized UBL
fallback. If it is no longer live, acquire fresh leases and baselines. A clean
checkout reconstructs Event 31 without provider-local state.

## Outcome

Codex preserved both sides of the truth:

- Event 30 and `e13e103d` remain the last accepted XLIFF boundary.
- `d99fc6bf` remains an auditable, mechanically passing but semantically
  rejected attempt.
- Event 31 records the contradiction and exact repair.

The current task remains `WORK_IN_PROGRESS`.

## Accepted changes through Event 30

- New `xliff_core_candidate_adjudication.py` compiler and validator.
- Separate durable decision source and generated adjudication projection.
- Exact dependency closure across candidate, occurrence, authority,
  denominator, SAL evidence, decisions, and adjudicator implementation.
- Batch 005 compiler now fails closed without validated adjudication proof.
- One exact `trgLang` obligation added after independent adjudication.
- Batch 003 output remains byte-identical.
- Nine proof-drift classes and malformed-decision controls.

## Accepted evidence

```text
implementation commit: e13e103de0bb789ff51a8e931af0fb649474be20
adjudication digest:   28399664d50afdd15e9f8b5ab2824a9566aa478fd0fcb18c97ce1451fd90d521
inventory digest:      83b9f2da44b33a93cea6740e7510b32b961dda80791f9f148c163e913922f5e0
candidate count:       1,130
verified/open:          1 / 1,129
obligations:            26 / 105
missing:                79
```

Focused and regression evidence is recorded in the three production-skill
transcripts committed with the implementation. A post-commit replay confirmed
both check modes and three exact smoke tests.

## What remains

XLF-04 still requires:

- 1,129 independent candidate adjudications;
- 79 missing source-bound expected rows;
- resolution of expected IDs without reliable candidate mappings;
- complete Core processing semantics;
- all official 2.1 module obligations;
- canonical SAL reconciliation and complete contract compilation.

The broader mission then still requires production implementations,
interoperability, packaging, cross-platform installed-wheel proof,
certification, extraction, and release preparation for all six libraries.

## Rejected attempt and exact next task

The rejected attempt reported 27/105 rows and two verified dispositions, but
those numbers are non-promoting. It selected generic `INLINE-PC`, omitted the
reciprocal decision, and overclaimed XLIFF 2.0.

Execute `XLF-04-BATCH-005-PARTIAL-002-B-REPAIR-001` for
`XLF-CAND-CORE-SCHEMATRON-00C4A041AF12C8A1`. Its direct rule requires paired
`subFlowsStart` and `subFlowsEnd` attributes on `pc`. Independently adjudicate
the direct semantic owner; reject incidental ancestor and generic-validator
overmapping; write RED controls first.

See [EVENT-31-DELTA.md](EVENT-31-DELTA.md),
[NEXT-MICROSTEP.yaml](NEXT-MICROSTEP.yaml), and
[event-31/RUNBOOK.md](event-31/RUNBOOK.md).

## Provider transfer rules

- Claude registers a new identity and fresh manifests.
- Codex leases and tokens are not transferable.
- No branch or GitHub workflow is authorized.
- Explicit staging only.
- No reset, clean, restore, broad stash, or unexplained overwrite.
- One bounded implementation commit precedes immutable replay and one new
  native event.
- A later provider resumes from the latest valid event, never this prose alone.

The remote shift boundary is clean and machine-reconstructible. Provider
leases remain off-repo and non-transferable. Handover projection files remain
separate from implementation.

## Two independent validation questions

Do not collapse repository proof and worktree ownership into one verdict:

1. Run `validate_committed_checkpoint.py --ref origin/main`. It uses a
   temporary detached worktree, creates no branch, and proves the immutable
   GitLab checkpoint without reading the foreign overlay.
2. Run `validate_handover.py` in the shared checkout. Before this packet is
   committed, it may fail on these handover-only mutations. After the packet
   commit, any failure must be classified and cannot be hidden by cleanup.

Claude must record both results. Execution may proceed only on paths not owned
by another live agent. If XLIFF remains owned, continue
`UBL-03-PARTIAL-002` exactly as defined in
[PARALLEL-UBL-CHECKPOINT.yaml](PARALLEL-UBL-CHECKPOINT.yaml).
