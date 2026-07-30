---
artifact_id: FF6-CLAUDE-START-EVENT-33
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
git merge-base --is-ancestor a79dad747a5305b24c41f42437f1824b3d92ec67 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_committed_checkpoint.py --ref origin/main
.venv\Scripts\python.exe -m tools.supervisor.coordination --json status
git status --short
```

Expected before work: `HEAD` equals the fetched `origin/main`; the merge-base
command proves Event 33 source implementation
`a79dad747a5305b24c41f42437f1824b3d92ec67` is an ancestor; detached validation
passes; accepted XLIFF implementation
`ff8f7d9f9ff1ff613be376e1361b0dd8304566e3` is also an ancestor; journal head is
`FF6-EVENT-000033` /
`eae356bca531c8cec38f57b012444d1032884b61eb5ef986018d7dd57c474988`.

Then classify the shared worktree:

- If clean, run
  `.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --require-clean --self-test`
  and require PASS.
- If dirty only under a current foreign agent's live leases, preserve those
  bytes, do not touch or stage them, and use the detached validation result.
- The seven XLIFF paths in `INFLIGHT-RECOVERY.yaml` are a stable, hash-bound,
  non-promoting occurrence from an absent process. Do not mutate them until a
  governed takeover revalidates every byte and independently replays its
  claims. Use the disjoint UBL fallback meanwhile.
- Any other unattributed dirty path fails the transfer. Never clean, restore,
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

If XLIFF is live-owned or its preserved occurrence is not yet safely adopted,
continue only the disjoint UBL-03 schema-graph task
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
