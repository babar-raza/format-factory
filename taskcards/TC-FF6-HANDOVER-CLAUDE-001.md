---
artifact_id: TC-FF6-HANDOVER-CLAUDE-001
artifact_type: taskcard
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
goal_id: FF6-PRODUCTION-LIBRARIES-001
status: COMPLETE
skill_ids:
  - refresh-provider-neutral-handover
  - create-taskcard
  - plan-control
---

# Publish a Provider-Neutral Claude/Codex Shift Handover

Status: `COMPLETE`

## Objective

Create a single-entry, evidence-backed, machine-readable handover that lets
Claude and Codex resume the FF6 mission from GitLab main without conversation
memory, provider-local state, lost work, duplicate execution, or false product
promotion.

## Allowed paths

- `plans/codex/handover/**`
- `plans/strategic/ff6/controller-state.yaml`
- `plans/strategic/ff6/events.jsonl`
- `taskcards/TC-FF6-PROGRAM-CAPABILITIES-001.md`
- `taskcards/TC-FF6-AUTHORITY-CLOSURE-001.md`
- this taskcard
- `taskcards/index.yaml`
- local task transcript and evidence metadata

## Acceptance

- One start file links every handover artifact and canonical authority.
- Exact commit, tree, controller event, next task, and evidence limits are
  recorded.
- Symptoms, root causes, structural weaknesses, preservation requirements,
  redesign direction, risks, and uncertainty are separated.
- Start, execution, checkpoint, takeover, validation, integration, and release
  procedures are provider-neutral and executable.
- The absent next taskcard is materialized as `READY`.
- Known global plan-control and line-ending digest contradictions are explicit.
- All internal links, YAML, normalized hashes, event chain, task index, and
  focused regression checks pass.
- Files are committed and pushed to GitLab main with remote verification.
- No product implementation or promotion occurs.

## Initial closure

The packet was integrated and remote-verified at
`1f215cc7ba0ce36225ae8bbc49678b3ca0d5d8fd`. The closing controller event
records the final packet and task-index digests. This task changes no product
promotion state.

## Refresh checkpoint

The packet was refreshed after `TC-FF6-AUTHORITY-CLOSURE-001` passed.
Controller event 16 records 15 of 15 live authority matches, strict
six-contract compilation, clean online and offline replay, deterministic
six-format projections, and no product promotion. The exact successor is
`TC-FF6-ORA-PROFILE-SURFACE-001` in `READY`.

The packet remains a derived navigation and shift artifact. The fetched
GitLab `origin/main` commit, native FF6 journal, controller, task index,
current gaps, and taskcard supersede every earlier packet revision and the
initial integration commit above.

## Event-19 refresh checkpoint

The packet was rebuilt from the remote-verified NRRD source checkpoint
`865558bb88243acda08c2a8d58a0d5ec887dedeb`.

- Native journal head:
  `FF6-EVENT-000019` /
  `76b580d72f865428e92bc5b6089a89487356c69163aadf6b615b70c6867221f8`.
- `TC-FF6-NRRD-PROFILE-SURFACE-001` is `PASS`.
- The current planning denominator is 110 capabilities and 672 obligations;
  NRRD owns 21 capabilities and 65 exact-profile obligations.
- All 15 predecessor authority records match.
- No product, package, certification, promotion, release, or gate changed.
- The exact successor is `TC-FF6-XLIFF-PROFILE-SURFACE-001` in `READY`.
- The successor must first acquire a separately pinned official XLIFF 2.0
  Standard package; the existing XLIFF 2.1 authority cannot stand in for it.
- Core and all eight official XLIFF 2.1 modules must receive separate, exact
  normative capability ownership. The pinned bundle has nine module schema
  vocabularies because ITS uses both `its` and `itsm`; Format Style and ITS
  were missing from the earlier six-module wording. The Change Tracking
  extension is informative and cannot count as a normative module. XLIFF 2.2
  is preview-only and XLIFF 1.2 is outside the 2.x model.

## Event-19 standards correction

The prior event-19 packet was structurally valid but contained an incomplete
XLIFF module enumeration. This refresh corrects the task and every handover
projection without changing event 19, the controller, the capability
denominator, product source, certification, promotion, release, or gates.
The correction is proven from the hash-matched `SRC-XLF-002`/`SRC-XLIFF-001`
XLIFF 2.1 authority bytes, not from current product code.

This refresh replaces every event-18/NRRD-as-next statement in the packet,
recomputes normalized hashes, and preserves the same provider-neutral,
GitLab-main-only, atomic-shift contract.

## Event-21 XLF-03 microstep refresh

The packet was rebuilt after a tested XLF-03 implementation slice was committed
at `a1316b4fae21c20c71ccb6d60e4b9fe634dca573` and bound to
`FF6-EVENT-000021` /
`3e83a764c53da658cb1dd348ed20d041db850f1cef45bec5eaa5637ccafecc11`.

- The active task remains
  `TC-FF6-XLIFF-PROFILE-SURFACE-001` / `WORK_IN_PROGRESS`.
- `XLF-01` and `XLF-02` are complete; `XLF-03` is still first unmet.
- The nested XLF-03 microstate is `GREEN_VERIFIED_CHECKPOINTED`.
- The digest-bound authority reader, Core/module inventories, section delta,
  source-row validation, canonical YAML, atomic write, and drift check
  primitives are committed and covered by 3 passing tests.
- Ruff, strict Mypy, and bytecode compilation pass. Pyright was unavailable in
  the checkpoint shell and is not claimed.
- The exact next RED test is
  `test_cli_writes_and_checks_default_xliff_matrix`.
- The CLI/default curated seeds, complete negative suite, real matrix, and
  three-run real-authority replay remain.
- The packet now defines a nested TDD/provider-shift state machine and a
  two-commit checkpoint protocol so a provider switch never depends on chat or
  an unjournaled source commit.
- No product source, certification, promotion, release, or gate changed.

## Cross-provider shift hardening refresh

The packet was re-audited from clean, fetched GitLab `main` at
`b6aef60c12368753939e75f88951a6f4d3533e76` without changing the FF6
controller or product task.

- The provider transfer is now explicitly one-writer-at-a-time for the active
  task. The outgoing identity completes after remote verification; the
  incoming provider registers a new identity and never inherits a token or
  lease.
- Planned token exhaustion is handled only at a `RESUMABLE` boundary. RED-only,
  unjournaled, and local-only states are not clean checkpoints.
- Crash recovery now distinguishes implementation-only commits, journaled but
  stale projections, owned GREEN/RED worktrees, unattributed dirt, and remote
  overlap.
- The XLIFF evidence denominator is disambiguated: the official 2.0/2.1 prose
  contains 293/420 total DocBook sections, of which 197/312 have direct IDs.
  ID-less sections remain in the matrix through deterministic title paths.
- The exact continuation remains the same XLF-03 RED test. No canonical
  taskcard, source, test, authority, contract, controller, promotion, gate, or
  release state changed.

## Event-24 XLF-04 batch-002 checkpoint refresh

The packet was rebuilt from immutable implementation commit
`78660ae1a310ab06cf00d977bbc26fb65914f1c9` and native event
`FF6-EVENT-000024` /
`10d96a6729d250fecb89f5f082682f583b5b8053fd620702dcd837dfaf541434`.

- `XLF-01`, `XLF-02`, `XLF-03`, `XLF-04-BATCH-001`, and
  `XLF-04-BATCH-002` are complete; `XLF-04` remains first unmet.
- XLF-03 now includes deterministic default anchors, CLI/check mode, declared
  archive/XML/matrix negative controls, and a real pinned-authority matrix.
- The matrix has 36 unique source-surface anchors, 293/420 sections, 8/8
  modules, and 8/9 schema vocabularies for XLIFF 2.0/2.1.
- Three real-authority generations are byte-identical at SHA-256
  `9f4ea4b8b71378217af26c0fb2b97a759817a0aca6c64255b8cd55170c60a090`.
- Eighteen focused tests, Ruff, strict Mypy, Pyright 1.1.411, bytecode
  compilation, and zero-warning receipt validation pass.
- The 36 rows are coarse source-surface anchors, not complete semantic
  obligations. XLF-04 must compile full Core semantics; XLF-05 must compile
  every module as a first-class capability family.
- Batches 001-002 add 19 source-bound obligations covering ten categories,
  but they remain `SOURCE_BOUND_UNVERIFIED`; two categories and the explicit
  expected-obligation ID denominator remain. Category presence cannot close
  XLF-04.
- The mission remains in `CONTRACT`, the active task remains
  `WORK_IN_PROGRESS`, the parent remains `NEEDS_REPAIR`, product certification
  remains 0/6, and every promotion remains `UNASSESSED`.
- At the historical event-24 boundary, the exact continuation was
  `XLF-04-BATCH-003`: RED tests for source-located
  semantic roundtrip/canonical output and XML security/resource limits plus an
  explicit expected-ID denominator after replaying event 24 and its bound evidence.

## Event-24 provider-shift truth refresh

The provider-neutral packet was re-audited from clean GitLab `origin/main` at
`df727a916ffac7ff028cd087adea7f1055652b8d`.

- All 50 LF-normalized manifest hashes, 24 native FF6 event links/hashes, and
  packet-internal links were recomputed successfully before this refresh.
- Two derived machine records and this taskcard still carried isolated
  batch-001-only wording even though the controller, journal, active
  checkpoint, and manifest correctly recorded batch 002. Those stale
  statements are corrected without changing the native event head, task
  state, product source, proof, certification, gate, or promotion.
- Coordination completion is now modeled as a resume-time off-repo
  precondition, not a durable boolean that this tracked packet could continue
  to prove after commit. Provider identities, tokens, and leases are never
  transferred.
- At that historical refresh, the exact continuation remained
  `XLF-04-BATCH-003`; event 25 below supersedes that continuation.

## Event-25 clean checkpoint refresh

The batch-003 recovery boundary has been reconciled without loss:

- GitLab `origin/main` contains READY UBL taskcard commit `210c1383`,
  XLIFF implementation commit `25227527`, and event/controller checkpoint
  commit `220ee7f5`.
- Event `FF6-EVENT-000025`, controller sequence 25, active taskcard, and
  plan-control receipt agree.
- Batch 003 contains six exact implementation/evidence paths, two valid skill
  transcripts, 25 cumulative source-bound obligations, and a 105-ID open
  denominator with 80 unresolved IDs.
- Independent replay in the handover refresh observed 27 focused tests,
  94 format-contract tests with the baseline-known CSV test deselected,
  69 production-program tests, Ruff, strict Mypy, bytecode compilation, and
  5/5 XLIFF authority matches. Pyright was unavailable in the refresh shell;
  the batch receipt records Pyright 1.1.411 passing.
- XLF-04 remains incomplete, 0/6 products are certified, and all promotions
  remain `UNASSESSED`.

The exact continuation is `XLF-04-BATCH-004`: compile a deterministic Core
authority-candidate census across direct/leaf normative prose, Core XSD
constraints, Core Schematron assertions, and exact 2.0/2.1 deltas. Map every
candidate exactly once to an expected obligation ID or a reasoned
non-obligation disposition. Reject unmapped and duplicate candidates; retain
`complete=false`. Exact hashes and the resolved recovery history are retained
in `plans/codex/handover/INFLIGHT-RECOVERY.yaml`.
