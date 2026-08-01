---
artifact_id: FF6-CLEAN-REPLAY-REPAIR-EVENT-38
artifact_type: machinery_repair_history
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Clean replay repair and current invariant

## Historical defect

The reciprocal skeleton attempt at
`2dcb161ed8e53bfc55e5be81374f5f7ddea3bb17` passed in the shared worktree but
failed from a clean Windows checkout because tracked text received different
LF/CRLF raw-byte digests. Proof consumers bound mutable worktree bytes while the
repository lacked a single canonical text-digest rule. A local GREEN result
therefore did not prove checkout-reproducible evidence.

## Accepted repair

Commit `809cc18cc6e62ae19f6ea5c11ed41ab9a7ec5956` established digest-verified CAS
hydration for the affected proof closure and passed an immutable Windows replay.
Event 36 accepted the repaired reciprocal-skeleton slice. Event 37 later
accepted unit-cardinality semantics at `1b758c2e`; Event 38 now accepts the
source-language compatibility slice at
`3fc939ad70ec6caac9e0699041076e02de00c5d2`.

The current native head is `FF6-EVENT-000038`. The exact continuation is
`XLF-04-BATCH-005-PARTIAL-002-G`.

## Current invariant

For every accepted semantic slice:

1. bind authorities, candidate occurrence, decision, source, tests, generated
   artifacts, and environment through explicit role-specific digests;
2. run focused verification in the working tree;
3. commit only explicit owned files to GitLab `main`;
4. create a detached worktree at the exact commit;
5. hydrate only digest-pinned external authority bytes;
6. rerun the affected suite and deterministic check modes there;
7. accept the semantic commit only if checkout identity and proof pass;
8. append the native event after immutable replay, never before;
9. regenerate this handover from the event and committed artifacts.

Line-ending normalization in this packet is only for packet manifest hashing.
It does not authorize arbitrary proof consumers to normalize format payloads or
binary authorities. Canonicalization must be role- and artifact-specific.

## Event 38 replay evidence

The Event 38 semantic commit passed 90 affected tests both in the shared
worktree and in a fresh detached checkout. Four generated artifacts reproduced
exact expected digests. All 32 XLIFF SAL facts and five authority locks passed.
The selected SAL seed rerun preserved canonical store, alias, and cache bytes.

This closes the replay risk for that bounded input closure only. It does not
prove every repository generator or future platform matrix deterministic.

## Required successor controls

For `XLF-04-BATCH-005-PARTIAL-002-G`, preserve the same immutable replay ladder
and add discriminating tests for:

- exact target-language candidate identity;
- source-language symmetry not being treated as an oracle;
- proposal accountability versus independent semantic ownership;
- role-swapped content/requirement/occurrence digest rejection;
- XLIFF 2.0 versus 2.1 profile scope;
- predecessor semantic equality for all 30 accepted rows;
- identity of all 1,130 candidate records;
- selected-seed missing, duplicate, unrelated-row, transaction, and
  idempotency behavior if another fact is ingested.

If the detached replay disagrees with the working tree, preserve the semantic
commit as a non-promoting attempt, record the differing input closure, and
repair machinery. Never edit the event or promotion label to accept a failing
checkout.
