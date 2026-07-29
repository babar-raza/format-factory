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
