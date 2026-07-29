---
artifact_id: FF6-AGENT-HANDOVER-START-001
artifact_type: agent_handover_entrypoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
canonical_state_path: plans/strategic/ff6/controller-state.yaml
---

# Start Here: Six Python Production Libraries

This is the single entry point for Claude, Codex, or another governed executor
continuing mission `FF6-PRODUCTION-LIBRARIES-001`.

The handover is a derived, commit-bound navigation packet. It does not replace
the product goal, controller journal, current-state snapshot, taskcards, Git
history, coordination database, or executed proof.

## Exact checkpoint

- Canonical forge: GitLab.
- Canonical remote and branch: `origin/main`.
- Last pre-shift durable source commit:
  `2129ad278c5d7a8b7f81559388489e6231def550`.
- Last pre-shift durable tree:
  `44714dc4d74b784ab7b09d6735eae3ebc1482743`.
- FF6 controller state: `CONTRACT`.
- Last verified event: `FF6-EVENT-000014`.
- Completed repair subtask: `TC-FF6-CAPABILITY-COMPILER-001` (`PASS`).
- Parent task: `TC-FF6-PROGRAM-CAPABILITIES-001` (`NEEDS_REPAIR`).
- Active resumable task: `TC-FF6-AUTHORITY-CLOSURE-001`
  (`WORK_IN_PROGRESS`).
- Canonical planning inventory: 89 capabilities and 636 obligations.
- Product certifications: zero.
- Product promotion states: all six `UNASSESSED`.

The GitLab commit containing this packet and event 14 is the clean provider
shift checkpoint. The pre-shift commit above is recorded to make ancestry
verifiable without embedding a self-referential hash in this packet.

Do not resume from a conversation summary, old branch, local transcript, stale
worktree, test count, package-smoke report, or `tools.plan_control next`.
Reconstruct the checkpoint from GitLab and the canonical files below.

## Read in this order

1. Repository operating contract: [`AGENTS.md`](../../../AGENTS.md).
2. Immutable mission goal:
   [`product-goal.yaml`](../../strategic/ff6/product-goal.yaml).
3. Executable production plan:
   [`autonomous-six-python-production-execution-plan.md`](../../strategic/autonomous-six-python-production-execution-plan.md).
4. Canonical controller:
   [`controller-state.yaml`](../../strategic/ff6/controller-state.yaml).
5. Append-only FF6 events:
   [`events.jsonl`](../../strategic/ff6/events.jsonl).
6. Evidence-backed product snapshot:
   [`current-state.yaml`](../../strategic/ff6/current-state.yaml).
7. Parent taskcard:
   [`TC-FF6-PROGRAM-CAPABILITIES-001.md`](../../../taskcards/TC-FF6-PROGRAM-CAPABILITIES-001.md).
8. Exact next executable taskcard:
   [`TC-FF6-AUTHORITY-CLOSURE-001.md`](../../../taskcards/TC-FF6-AUTHORITY-CLOSURE-001.md).
9. Exact in-progress implementation checkpoint:
   [`ACTIVE-WORK-CHECKPOINT.md`](ACTIVE-WORK-CHECKPOINT.md).
10. Canonical capability manifest:
   [`capability-manifest.json`](../../strategic/ff6/capability-manifest.json).
11. Machine-readable handover checkpoint:
   [`checkpoint.yaml`](checkpoint.yaml).
12. Current findings and causal assessment:
   [`CURRENT-STATE-AND-ROOT-CAUSES.md`](CURRENT-STATE-AND-ROOT-CAUSES.md).
13. Provider-neutral execution and checkpoint protocol:
    [`SHIFT-AND-RESUME-PROTOCOL.md`](SHIFT-AND-RESUME-PROTOCOL.md).
14. Exact execution sequence and task DAG:
    [`EXECUTION-RUNBOOK.md`](EXECUTION-RUNBOOK.md).
15. Quality, evidence, regression, and release rules:
    [`VALIDATION-AND-RELEASE.md`](VALIDATION-AND-RELEASE.md).
16. Ready-to-use Claude instruction:
    [`CLAUDE-START.md`](CLAUDE-START.md).
17. Packet file hashes:
    [`manifest.yaml`](manifest.yaml).

## Mandatory preflight

Run from the repository root in PowerShell:

```powershell
git fetch origin main
git status --short
git rev-parse HEAD
git rev-parse origin/main
python tools/evidence/check_current_state_consistency.py
python -m pytest tests/plan_control -q
python -m tools.supervisor.coordination --json status
```

Expected at this checkpoint:

- `origin/main` contains the event-14 handover checkpoint and descends from
  `2129ad278c5d7a8b7f81559388489e6231def550`.
- the chosen execution worktree is clean before mutation;
- current-state consistency prints `CURRENT_STATE_CONSISTENCY: PASS`;
- plan-control tests report `40 passed`;
- the previous provider has completed its coordination session, or the
  receiving provider performs a governed takeover after digest comparison.

The coordination command currently exits nonzero because 15 historical OPEN
conflicts exist. That is not permission to resolve or discard them. Four point
to obsolete FF6 local worktrees. Use a fresh detached worktree and new leases.

## Known authority contradiction

The global `tools.plan_control` projection is not the current FF6 task
authority:

- `python -m tools.plan_control reconcile` fails because
  `plans/.control/config.json` still names deleted branch
  `codex/ff-six-python-production`.
- `python -m tools.plan_control next` selects legacy broad task
  `TC-FF6-NRRD-ORA-001`.
- the digest-bound FF6 controller and its last verified event select
  `TC-FF6-AUTHORITY-CLOSURE-001`.

Until machinery consolidation repairs and tests that split, use
`plans/strategic/ff6/controller-state.yaml` plus `events.jsonl` for this
mission. Record the contradiction as a machinery gap. Do not silently edit a
status to make the two authorities agree.

## Verified work completed since the original handover

The prior hand-written checkpoint claimed 128 obligations. Independent audit
proved the canonical contract runtime generated 636 obligations with zero ID
overlap. That false close was invalidated without deleting the draft detail.

The completed compiler repair now provides:

- one registered deterministic compiler and versioned schema;
- exactly 89 canonical capability identities;
- 636 canonical obligations: IPYNB 105, ORA 32, NRRD 94, XLIFF 125,
  SafeTensors 86, and UBL 194;
- classifications: 80 stable, 4 optional-adapter, 4 preview, 1 excluded;
- full compiler/schema/contract/SAL/policy/enrichment input closure;
- explicit expected-versus-observed authority artifacts;
- manifest aggregate
  `26cbe9d21cedafe70653bfaa8134ffa4e481080278e954546cf9710c97a5b00a`;
- three-run digest
  `018c26be67ea91fe86aeb65374365b5e917eb8c0058235f999d59909bfd08943`;
- 14 focused, 43 production-program, and 76 unaffected format-contract tests
  passing.

This is planning/contract machinery, not product implementation or
certification. `FF6-GAP-012` and `FF6-GAP-015` are resolved. The parent remains
open for `FF6-GAP-013` (OpenRaster profile/surface depth) and `FF6-GAP-014`
(authority dependency closure).

## Exact continuation action

Resume only `TC-FF6-AUTHORITY-CLOSURE-001` from
[`ACTIVE-WORK-CHECKPOINT.md`](ACTIVE-WORK-CHECKPOINT.md). The shared
lock/runtime, materializer, schema, four internal requirement documents, and
six focused tests already exist and are valid bounded WIP. Do not recreate
them.

Finish the immutable source/legal matrix beginning at the unresolved NRRD
authority decision, create the canonical 15-source lock, harden the known
materializer gaps, integrate the registered acquisition skill and strict
compiler closure, and complete the taskcard acceptance suite. The promoting
baseline remains 11 `MISSING`, 4 `UNDECLARED`, 0 `MATCH` until a real
lock/materialization/audit run proves otherwise.

Do not hide the baseline with `--allow-blocked-authority`, edit expected
digests to whatever downloaded, commit specification bytes without
redistribution evidence, modify product source, or promote a format.

## How to stop safely

At a shift boundary:

1. finish or roll back only your bounded change set;
2. run the taskcard's focused and regression validations;
3. append a write-ahead close intent and then a verified close or checkpoint
   event;
4. update the controller projection and current taskcard truthfully;
5. stage only the explicit owned file list;
6. run the coordination precommit check as the owning agent;
7. commit and push to GitLab `main` only after verifying `origin/main` has not
   advanced unexpectedly;
8. verify the remote commit;
9. complete or abandon the coordination session truthfully and release leases;
10. update this handover packet only when its checkpoint facts changed.

Never leave the next agent dependent on uncommitted files, an unpushed commit,
an ignored transcript, or conversation memory.
