---
artifact_id: FF6-CURRENT-SHIFT-HANDOVER-EVENT-30
artifact_type: provider_shift_handover
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Codex to Claude shift handover — Event 30

## Outcome

Codex completed the inherited Partial-002-A RED cycle, committed the bounded
implementation as `e13e103de0bb789ff51a8e931af0fb649474be20`, pushed it to
GitLab `origin/main`, replayed its generated artifacts from the immutable
commit, and appended native Event 30. The current task remains
`WORK_IN_PROGRESS`.

## Implemented changes

- New `xliff_core_candidate_adjudication.py` compiler and validator.
- Separate durable decision source and generated adjudication projection.
- Exact dependency closure across candidate, occurrence, authority,
  denominator, SAL evidence, decisions, and adjudicator implementation.
- Batch 005 compiler now fails closed without validated adjudication proof.
- One exact `trgLang` obligation added after independent adjudication.
- Batch 003 output remains byte-identical.
- Nine proof-drift classes and malformed-decision controls.

## Evidence

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

## Exact next task

Execute Partial-002-B for
`XLF-CAND-CORE-SCHEMATRON-00C4A041AF12C8A1`. Its direct rule requires paired
`subFlowsStart` and `subFlowsEnd` attributes on `pc`. Independently adjudicate
the direct semantic owner; reject incidental ancestor and generic-validator
overmapping; write RED controls first.

See [NEXT-MICROSTEP.yaml](NEXT-MICROSTEP.yaml) and
[event-30/RUNBOOK.md](event-30/RUNBOOK.md).

## Provider transfer rules

- Claude registers a new identity and fresh manifests.
- Codex leases and tokens are not transferable.
- No branch or GitHub workflow is authorized.
- Explicit staging only.
- No reset, clean, restore, broad stash, or unexplained overwrite.
- One bounded implementation commit precedes immutable replay and one new
  native event.
- A later provider resumes from the latest valid event, never this prose alone.

The shift ends at a clean, machine-reconstructible product boundary. Handover
projection files are committed separately from implementation so a failure in
packet generation cannot corrupt product evidence.
