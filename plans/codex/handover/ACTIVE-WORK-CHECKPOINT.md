---
artifact_id: FF6-ACTIVE-WORK-CHECKPOINT-EVENT-40
artifact_type: active_work_checkpoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Active work checkpoint: Event 40

## Immutable accepted boundary

- GitLab control checkpoint: `de569544eebc1fff011901e61d3574dcc48e5e08`
- XLIFF semantic commit: `d95af5aeb248907b4d23457ecd288723fc9c2050`
- Native event: `FF6-EVENT-000040`
- Event hash: `c9c7167d447fbe0945c7a65c288f3cece78c64090e09c1ce2d674fdbf9bf2d63`
- Controller state: `CONTRACT`
- Active task: `TC-FF6-XLIFF-PROFILE-SURFACE-001`
- Task state: `WORK_IN_PROGRESS`
- First unmet task step: `XLF-04`
- Completed microstep: `XLF-04-BATCH-005-PARTIAL-002-H`
- Exact next microstep: `XLF-04-BATCH-005-PARTIAL-002-I`

## What the outgoing shift achieved

The accepted slice independently resolved the source-side start-code isolation
rule without treating generated token matches as authority.

- Decision `XLF-ADJ-CORE-SCHEMATRON-0009` accepts only direct owner
  `SAL-XLIFF-CORE-INLINE-ISOLATION-001`.
- Exact fact `SAL-XLIFF-D5C1325C047A7CB0` has six passing assertions and proof
  SHA-256 `c584c795046953ff73f4de7db941bdbae9abd35fc0d838bf9cc297b9790a3085`.
- Identical normative XLIFF 2.0 and 2.1 prose establishes the full `isolated`
  biconditional; XLIFF 2.1 F5S Schematron supplies source-side rejection proof.
- Validator, hierarchy, complete `sc`/`ec` surface, `startRef`, and source
  cardinality proposals were rejected as direct owners.
- All 30 predecessor obligation objects, all 8 predecessor decision objects,
  and all 1,130 candidate identities are preserved.
- Exactly one obligation and one decision were appended.
- The freshly compiled XLIFF ProductContract remains `DRAFT` with 15
  capabilities.

Accepted counts are `9/1,130` dispositions and `31/105` source-bound
obligations. This is partial contract evidence only; 1,121 dispositions and 74
expected obligations remain open.

## Verification achieved

- 113 affected adjudication, extraction, seed, and merge tests passed.
- 94 format-contract tests passed with the exact stateful CSV writer test
  deselected; 69 production-program tests passed.
- All 34 XLIFF SAL facts pass exact proof verification.
- Three runs reproduced byte-identical adjudication and inventory artifacts.
- Ruff, strict Mypy, Pyright 1.1.411, py_compile, and four semantic transcripts
  passed.
- Detached replay from `d95af5ae` passed three focused tests, SAL,
  adjudication, inventory, ProductContract check/idempotency, and the complete
  five-record authority closure.

Two earlier detached attempts are non-promoting: one failed collection due to
the replay harness working directory/selector; one omitted `src-xliff-003.bin`
and correctly exposed ProductContract drift. The accepted replay recreated the
worktree and materialized all four cached binary authorities plus the tracked
product-requirement authority.

## Exact successor

Adjudicate `XLF-CAND-CORE-SCHEMATRON-60B596A00F7FA06A` at XLIFF 2.1
`schematron/rule[16]/report[1]`. It is the target-side analogue of the accepted
source-side isolation report.

Do not add a duplicate obligation. Determine independently whether the target
report completes reciprocal proof for `SAL-XLIFF-CORE-INLINE-ISOLATION-001`.
Treat all eight generated mappings as proposals, explicitly reject incidental
and downstream surfaces, and preserve all 31 obligations, 9 decisions, and
1,130 candidate identities.

## Transfer status

The semantic and control state is reconstructible from GitLab. No uncommitted
product overlay belongs to this handover. Provider identities, tokens, leases,
execution manifests, mutation authorizations, and ignored local files do not
transfer. The next provider creates fresh state after validating this packet.

All six products remain `UNASSESSED`; certification remains `0/6`.
