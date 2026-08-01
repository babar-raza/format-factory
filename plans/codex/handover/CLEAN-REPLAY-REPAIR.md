---
artifact_id: FF6-CLEAN-REPLAY-REPAIR-EVENT-39
artifact_type: machinery_repair_history
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Clean replay repair and current invariant

## Historical defect

The reciprocal skeleton attempt at
`2dcb161ed8e53bfc55e5be81374f5f7ddea3bb17` passed in a shared worktree but
failed from a clean Windows checkout because tracked proof text received
different LF/CRLF raw-byte digests. A local GREEN result therefore did not prove
checkout-reproducible evidence.

Commit `809cc18cc6e62ae19f6ea5c11ed41ab9a7ec5956` established the accepted
checkout-identity repair for that proof closure. Event 36 accepted the repaired
slice; Events 37 and 38 accepted unit-cardinality and source-language slices.

## Event 39 replay evidence

Event 39 accepts target-language profile semantics at semantic commit
`39b2e89fde0f7dd5e1acebc424f4d700dfe74765`. The current native head is
`FF6-EVENT-000039`; the exact continuation is
`XLF-04-BATCH-005-PARTIAL-002-H`.

The semantic commit passed 77 affected tests in the working tree and in an
immutable detached checkout. Three runs reproduced denominator, census,
adjudication, inventory, and ProductContract bytes. All 33 XLIFF SAL facts and
all five authority records passed. Ruff, strict Mypy, Pyright 1.1.411,
py_compile, and four semantic transcripts passed.

## Newly exposed dependency-closure defect

A detached replay initially restored only the two official XLIFF packages. The
77 focused tests and SAL verification passed, but ProductContract check mode
differed. The replay was not valid because the contract dependency closure
contains five authority records, not two.

The accepted replay restored:

1. ignored `src-xlf-001.bin`;
2. ignored `src-xlf-002.bin`;
3. ignored `src-xliff-001.bin`;
4. ignored `src-xliff-003.bin`; and
5. the tracked product-requirement authority.

After full restoration, tests, SAL, contract check, and the 5/5 authority audit
passed. This is a structural lesson: a test suite can be GREEN while a
downstream proof node is invalid because its complete authority closure was not
materialized. Future automation must derive replay inputs from the proof graph,
not from a provider-maintained list.

## Current invariant

For every accepted semantic slice:

1. bind every authority, candidate occurrence, decision, source, test,
   generated artifact, lock, environment, and package through role-specific
   digests;
2. start with an independently meaningful RED test;
3. run focused verification in the owned worktree;
4. commit only explicit leased files to GitLab `main`;
5. create a detached worktree at the exact semantic commit;
6. compute and hydrate the complete content-addressed dependency closure;
7. rerun affected suites and every changed descendant in check mode;
8. accept the semantic commit only if checkout identity and the full proof
   closure pass;
9. append the native event after immutable replay, never before; and
10. regenerate all status projections and this handover from the event.

Line-ending normalization in the packet manifest applies only to handover
hashing. It does not authorize generic normalization of binary authorities or
format payloads.

## Required successor controls

For `XLF-04-BATCH-005-PARTIAL-002-H`, preserve the replay ladder and add
controls for:

- exact isolated-start-code candidate identity;
- generated proposal accountability versus independent ownership;
- rejection of ancestor context and downstream validation as direct semantics;
- role-swapped candidate/requirement/occurrence/authority digests;
- profile scope;
- all 30 accepted obligation identities and all 1,130 candidate identities;
- selected-seed missing, duplicate, unrelated-row, transactional, QName, and
  idempotency behavior if a fact is ingested;
- full five-record authority restoration before ProductContract check mode.

If detached replay disagrees with the working tree, preserve the semantic commit
as a non-promoting attempt, record the divergent inputs, and repair machinery.
Never edit an event or promotion label to accept a failing checkout.
