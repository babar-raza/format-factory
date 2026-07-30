---
artifact_id: FF6-CLAUDE-START-EVENT-32
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Claude exact start sequence

Run from:

```powershell
Set-Location 'C:\Users\prora\OneDrive\Documents\GitHub\format-factory'
git fetch origin main --prune
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 530f18fe89a6875276e8f4442351445564df80e9 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_committed_checkpoint.py --ref origin/main
.venv\Scripts\python.exe -m tools.supervisor.coordination --json status
git status --short
```

Expected before work: `HEAD` equals the fetched `origin/main`; the merge-base
command proves Event 32 control commit
`530f18fe89a6875276e8f4442351445564df80e9` is an ancestor; detached validation
passes; accepted implementation
`ff8f7d9f9ff1ff613be376e1361b0dd8304566e3` is an ancestor; journal head is
`FF6-EVENT-000032` /
`1b04941583c0015b42115b8d07ca748a744561a000833b38fc64412531164054`.

Then classify the shared worktree:

- If clean, run
  `.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --require-clean --self-test`
  and require PASS.
- If dirty only under a current foreign agent's live leases, preserve those
  bytes, do not touch or stage them, and use the detached validation result.
  Select only a disjoint fallback described below.
- If any dirty path is unattributed, or its owner is stale without a governed
  takeover, do not mutate it. Reconcile ownership first. Never clean, restore,
  stash, reset, or silently absorb it.

Then read, in order:

1. `AGENTS.md`
2. `docs/governance/codex-adapter.md` if running Codex
3. `plans/strategic/ff6/product-goal.yaml`
4. `plans/strategic/ff6/controller-state.yaml`
5. `taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md`
6. `plans/codex/handover/NEXT-MICROSTEP.yaml`
7. the complete command files for every selected registered skill

Register a new provider identity:

```powershell
.venv\Scripts\python.exe -m tools.supervisor.coordination register `
  --provider claude-code --mode interactive `
  --task TC-FF6-XLIFF-PROFILE-SURFACE-001
```

Persist the returned ID/token only for this shift. Query `status`, claim the
logical microstep and exact file set, preflight before every write, record
every write, and use a fresh execution manifest plus mutation authorization.
Do not release or take over an active foreign lease.

Execute only `XLF-04-BATCH-005-PARTIAL-002-C` unless the live lease check
shows that lane is owned. The exact candidate is
`XLF-CAND-CORE-SCHEMATRON-04053F3F140BDD92`. Start with a RED control; do not
accept the generated mappings as authority.

If XLIFF is live-owned, continue only the disjoint UBL-03 schema-graph task
described in `PARALLEL-UBL-CHECKPOINT.yaml`, after registering the UBL task,
claiming exact non-overlapping files, and revalidating its current commits.
The fallback does not change the controller-selected XLIFF task.

Required closing sequence:

1. focused tests;
2. check modes and three deterministic generations;
3. SAL and authority replay;
4. Ruff, strict Mypy, pinned Pyright, and bytecode compilation;
5. format-contract and production-program regressions;
6. zero-warning skill transcripts;
7. explicit-file commit and GitLab push;
8. immutable replay;
9. native event append and projection update;
10. handover refresh, clean validator pass, and release of only this shift's
    leases.

Never claim product completion. The next microstep can advance one contract
obligation or disposition; it cannot certify XLIFF or any other library.
