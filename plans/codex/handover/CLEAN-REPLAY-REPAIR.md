---
artifact_id: FF6-CLEAN-REPLAY-REPAIR-EVENT-40
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
different LF/CRLF raw-byte digests. Commit `809cc18c` established the accepted
checkout-identity repair. Events 37-40 then accepted later bounded XLIFF
contract slices under that policy.

## Event 40 replay evidence

Event 40 accepts source-side start-code isolation semantics at semantic commit
`d95af5aeb248907b4d23457ecd288723fc9c2050`. The current native head is
`FF6-EVENT-000040`; the exact continuation is
`XLF-04-BATCH-005-PARTIAL-002-I`.

The semantic commit passed 113 affected tests in the working tree. Three runs
reproduced byte-identical adjudication and obligation inventory artifacts. All
34 XLIFF SAL facts passed, as did format-contract and production-program
regressions, Ruff, strict Mypy, Pyright 1.1.411, py_compile, and four semantic
transcripts.

## Event 40 detached replay attempts

The first attempt is excluded: the command remained in the primary checkout
and one long selector used the wrong suffix, so pytest collected no tests.

The second attempt is excluded: it restored `src-xlf-001.bin`,
`src-xlf-002.bin`, and `src-xliff-001.bin` but omitted
`src-xliff-003.bin`. Focused tests, SAL, adjudication, and inventory checks
passed, but ProductContract check mode differed. This was a valid rejection,
not an accepted replay.

The accepted attempt recreated the detached worktree at `d95af5ae`, restored
all four cached binary authorities, and used the tracked product-requirement
authority as the fifth record. It passed:

1. the three focused candidate/obligation tests;
2. exact SAL verification;
3. candidate adjudication check mode;
4. obligation inventory check mode;
5. ProductContract check mode and idempotency; and
6. complete authority digest audit.

## Structural weakness exposed

The contract compiler currently represents a missing cached authority by the
SHA-256 of empty bytes and continues compilation. The subsequent contract
check detected drift, so no false acceptance occurred, but this is still a
fail-late design. A durable repair must require every declared input before
compilation and distinguish `MISSING` from a legitimate empty authority.

This gap is recorded in the handover; Event 40 does not claim it is fixed. It
does not block the next bounded candidate because the complete five-record
closure is available and digest-verified.

## Current invariant

For every accepted semantic slice:

1. bind every authority, candidate occurrence, decision, source, test,
   generated artifact, lock, environment, and package through role-specific
   digests;
2. start with an independently meaningful RED test;
3. run focused verification in the owned worktree;
4. commit only explicit leased files to GitLab `main`;
5. create a detached worktree at the exact semantic commit;
6. derive and hydrate the complete content-addressed dependency closure;
7. rerun affected suites and every changed descendant in check mode;
8. reject every incomplete or divergent replay;
9. append the native event after immutable replay, never before; and
10. regenerate status projections and this handover from the event.

Line-ending normalization in the packet manifest applies only to handover
hashing. It does not authorize generic normalization of binary authorities or
format payloads.

## Required successor controls

For `XLF-04-BATCH-005-PARTIAL-002-I`, preserve the replay ladder and add:

- exact target-side isolation candidate identity;
- independent reciprocal-owner reasoning;
- rejection of duplicate obligation creation;
- generated proposal accountability and explicit rejections;
- role-swapped candidate/requirement/occurrence/authority tamper controls;
- profile and source/target-context controls;
- equality of all 31 predecessor obligations and all 9 decisions;
- identity of all 1,130 candidates; and
- full five-record authority restoration before ProductContract check mode.

If detached replay disagrees with the working tree, preserve the semantic
commit as a non-promoting attempt, record divergent inputs, and repair the
machinery. Never edit an event or promotion label to accept a failing checkout.
