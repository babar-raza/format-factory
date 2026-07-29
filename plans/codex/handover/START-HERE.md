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
- Source checkpoint commit: `a585a9e67c6f5ee55922c6cf356f600de3b4c751`.
- Source checkpoint tree: `aaa4e437607d1078cad01b13d37be681142565f8`.
- FF6 controller state: `SNAPSHOT`.
- Last completed program task: `TC-FF6-PROGRAM-TRUTH-001`.
- Exact next task: `TC-FF6-PROGRAM-CAPABILITIES-001`.
- Product certifications: zero.
- Product promotion states: all six `UNASSESSED`.

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
7. Next executable taskcard:
   [`TC-FF6-PROGRAM-CAPABILITIES-001.md`](../../../taskcards/TC-FF6-PROGRAM-CAPABILITIES-001.md).
8. Machine-readable handover checkpoint:
   [`checkpoint.yaml`](checkpoint.yaml).
9. Current findings and causal assessment:
   [`CURRENT-STATE-AND-ROOT-CAUSES.md`](CURRENT-STATE-AND-ROOT-CAUSES.md).
10. Provider-neutral execution and checkpoint protocol:
    [`SHIFT-AND-RESUME-PROTOCOL.md`](SHIFT-AND-RESUME-PROTOCOL.md).
11. Exact execution sequence and task DAG:
    [`EXECUTION-RUNBOOK.md`](EXECUTION-RUNBOOK.md).
12. Quality, evidence, regression, and release rules:
    [`VALIDATION-AND-RELEASE.md`](VALIDATION-AND-RELEASE.md).
13. Ready-to-use Claude instruction:
    [`CLAUDE-START.md`](CLAUDE-START.md).
14. Packet file hashes:
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

- `origin/main` contains the handover integration commit and descends from
  `a585a9e67c6f5ee55922c6cf356f600de3b4c751`.
- the chosen execution worktree is clean before mutation;
- current-state consistency prints `CURRENT_STATE_CONSISTENCY: PASS`;
- plan-control tests report `40 passed`;
- no fresh agent owns the FF6 capability scope.

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
  `TC-FF6-PROGRAM-CAPABILITIES-001`.

Until machinery consolidation repairs and tests that split, use
`plans/strategic/ff6/controller-state.yaml` plus `events.jsonl` for this
mission. Record the contradiction as a machinery gap. Do not silently edit a
status to make the two authorities agree.

## First allowed action

Execute only `TC-FF6-PROGRAM-CAPABILITIES-001`. It is a contract and obligation
compilation task. It must not modify product source.

The task closes only when all six stable-profile capability universes and
normative obligation inventories exist, reconcile without omissions, carry
authority references, classify every item, and generate deterministic next
tasks. A capability inventory is planning evidence, not implementation proof.

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
