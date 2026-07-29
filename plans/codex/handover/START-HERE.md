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

This is the single provider-neutral entry point for mission
`FF6-PRODUCTION-LIBRARIES-001`. Claude, Codex, or another governed executor
must reconstruct state from GitLab and the tracked machine records. Chat
history, model memory, old branches, ignored worktrees, and this prose packet
are not state authorities.

Absolute Windows path:

```text
C:\Users\prora\OneDrive\Documents\GitHub\format-factory\plans\codex\handover\START-HERE.md
```

## Current clean checkpoint

| Field | Verified value |
|---|---|
| Forge | GitLab only |
| Remote and branch | `origin/main` |
| Source commit | `17aece4e5301af958b21e4ffc9db878494f3b89c` |
| Controller state | `CONTRACT` |
| Journal head | `FF6-EVENT-000017` |
| Event hash | `44cb90a67aec8fff244de05d84c047f1d31077d694eda1ff1e27ee0aaa0f3015` |
| Parent task | `TC-FF6-PROGRAM-CAPABILITIES-001` — `NEEDS_REPAIR` |
| Last completed child | `TC-FF6-ORA-PROFILE-SURFACE-001` — `PASS` |
| Exact next task | `TC-FF6-IPYNB-PROFILE-SURFACE-001` — `READY` |
| Current compiled denominator | 99 capabilities / 738 obligations |
| Authority closure | 15/15 `MATCH` |
| Certified products | 0/6 |
| Promotion | all six `UNASSESSED` |

The packet commit necessarily comes after the source commit above. The incoming
executor must fetch `origin/main`, require the source commit to be an ancestor
of the fetched packet commit, and validate packet hashes. Never require the
packet to contain its own final commit hash.

## Read in this order

1. [`AGENTS.md`](../../../AGENTS.md)
2. [`skill-only-policy.yaml`](../../../docs/governance/skill-only-policy.yaml)
   and, for Codex, [`codex-adapter.md`](../../../docs/governance/codex-adapter.md);
   Claude uses the ambient hooks and `AGENTS.md` coordination contract because
   no separate Claude adapter is currently tracked
3. [`CURRENT-MACHINE-STATE.yaml`](CURRENT-MACHINE-STATE.yaml)
4. [`product-goal.yaml`](../../strategic/ff6/product-goal.yaml)
5. [`autonomous-six-python-production-execution-plan.md`](../../strategic/autonomous-six-python-production-execution-plan.md)
6. [`controller-state.yaml`](../../strategic/ff6/controller-state.yaml)
7. all records in [`events.jsonl`](../../strategic/ff6/events.jsonl)
8. [`current-gaps.yaml`](../../strategic/ff6/current-gaps.yaml)
9. [`capability-coverage.yaml`](../../strategic/ff6/capability-coverage.yaml)
10. [`TC-FF6-PROGRAM-CAPABILITIES-001.md`](../../../taskcards/TC-FF6-PROGRAM-CAPABILITIES-001.md)
11. [`TC-FF6-IPYNB-PROFILE-SURFACE-001.md`](../../../taskcards/TC-FF6-IPYNB-PROFILE-SURFACE-001.md)
12. [`ACTIVE-WORK-CHECKPOINT.md`](ACTIVE-WORK-CHECKPOINT.md)
13. [`STATE-MACHINE-AND-TASKCARD-PROTOCOL.md`](STATE-MACHINE-AND-TASKCARD-PROTOCOL.md)
14. [`SHIFT-AND-RESUME-PROTOCOL.md`](SHIFT-AND-RESUME-PROTOCOL.md)
15. [`EXECUTION-RUNBOOK.md`](EXECUTION-RUNBOOK.md)
16. [`CURRENT-STATE-AND-ROOT-CAUSES.md`](CURRENT-STATE-AND-ROOT-CAUSES.md)
17. [`VALIDATION-AND-RELEASE.md`](VALIDATION-AND-RELEASE.md)
18. [`CLAUDE-START.md`](CLAUDE-START.md)
19. [`checkpoint.yaml`](checkpoint.yaml)
20. [`manifest.yaml`](manifest.yaml)

## Authority precedence

If two records disagree, stop trusting the lower record and use this order:

1. fetched GitLab `origin/main` tracked bytes;
2. valid native FF6 journal;
3. controller projection;
4. current taskcard plus task index;
5. current gap and capability projections;
6. digest-bound contracts and proof;
7. this derived packet;
8. conversation or provider memory.

The assessment snapshot `current-state.yaml` remains valuable for product-tree
inventory, but it was captured at baseline commit `e4f8f5f…`. Its contract
hashes and pre-OpenRaster capability totals are historical where they disagree
with event 17 and `capability-coverage.yaml`.

## Mechanical resume preflight

Run from the repository root:

```powershell
git fetch origin main --prune
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 17aece4e5301af958b21e4ffc9db878494f3b89c origin/main
python tools/evidence/check_current_state_consistency.py
python -m tools.supervisor.coordination --json status
```

Then run the native FF6 journal check in
[`SHIFT-AND-RESUME-PROTOCOL.md`](SHIFT-AND-RESUME-PROTOCOL.md). Do not use
`tools.plan_control doctor` as an FF6 chain validator: it expects a different
event schema. That integration defect is tracked as `FF6-GAP-011`.

Resume only if:

- the worktree is clean or every dirty path is classified and outside scope;
- event 17 and controller state agree;
- the exact READY task exists in `taskcards/index.yaml`;
- the capability aggregate equals
  `de6a38a86aa7a82cc50dc7dc6ebfa0066c811d8de782a37684fd26d20a89272a`;
- all 15 authority artifacts still match;
- no live lease owns the intended files.

## Exact continuation

Execute only `TC-FF6-IPYNB-PROFILE-SURFACE-001`.

The first technical action is to revalidate the pinned IPYNB authorities and
produce a source-located nbformat 4.0–4.5 delta matrix. This task is contract
and obligation work only. Product source, product tests, packaging,
certification, gate movement, and promotion are prohibited.

The executor must not:

- repeat the completed OpenRaster repair;
- assign every notebook rule to 4.5;
- weaken the notebook no-execution boundary;
- hide `FF6-IPYNB-PROFILE-001` by editing policy;
- close the parent while NRRD, XLIFF, or UBL mandatory gaps remain;
- create a branch, use GitHub, or ask whether to continue.

## Shift invariant

Every provider shift ends at a GitLab-main checkpoint that contains:

- a valid task state and event head;
- explicit completed and remaining acceptance criteria;
- current proof and failure boundaries;
- a deterministic exact next action;
- refreshed packet hashes;
- no unexplained or required uncommitted work.

If a provider cannot finish the whole taskcard, it must finish the current
atomic substep to an integration-safe state, run the substep gates, append a
truthful `WORK_IN_PROGRESS` checkpoint event, refresh this packet, commit, push,
and remote-verify. A token boundary is never a reason to commit broken code or
to leave operational state only in chat.
