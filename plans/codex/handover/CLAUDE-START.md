---
artifact_id: FF6-CLAUDE-START-EVENT-35
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Claude exact start sequence

Run from:

```powershell
Set-Location 'C:\Users\prora\OneDrive\Documents\GitHub\format-factory'
git fetch origin main --prune
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 2dcb161ed8e53bfc55e5be81374f5f7ddea3bb17 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_committed_checkpoint.py --ref origin/main
.venv\Scripts\python.exe -m tools.supervisor.coordination --json status
git status --short
```

Expected before work: `HEAD` equals the fetched `origin/main`; the merge-base
command proves repository checkpoint
`2dcb161ed8e53bfc55e5be81374f5f7ddea3bb17` is an ancestor; packet validation
passes; accepted XLIFF implementation
`591fcfe18808e5195c33570eaa9d334770e90166` is an ancestor; journal head is `FF6-EVENT-000035` /
`2866d7e70bd193f8aa7b60ca1f92f4f842d1cd470f97984c07f47d88ed2ea97d`.

Do not expect the XLIFF affected suite to pass in a fresh Windows checkout
before the repair. Commit `2dcb161e` is intentionally recorded as
non-promoting after 5/71 tests failed on LF/CRLF-sensitive SAL manifest
hashes. Read `plans/codex/handover/CLEAN-REPLAY-REPAIR.md` before selecting
skills or paths.

Then classify the shared worktree:

- If clean, run
  `.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --require-clean --self-test`
  and require PASS.
- If dirty only under a current foreign agent's live leases, preserve those
  bytes, do not touch or stage them, and use the detached validation result.
- The seven inherited XLIFF paths were independently replayed and are committed
  at `591fcfe1`; no local XLIFF overlay is required.
- At packet creation, UBL partial-005 was committed and its executor remained
  active. Re-query coordination. Do not enter partial-006 if it is still live.
- Any other unattributed dirty path fails the transfer. Never clean, restore,
  stash, reset, or silently absorb it.

Then read, in order:

1. `AGENTS.md`
2. `docs/governance/codex-adapter.md` if running Codex
3. `plans/strategic/ff6/product-goal.yaml`
4. `plans/strategic/ff6/controller-state.yaml`
5. `taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md`
6. `plans/codex/handover/CLEAN-REPLAY-REPAIR.md`
7. `plans/codex/handover/NEXT-MICROSTEP.yaml`
8. the complete command files for every selected registered skill

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

Execute only `XLF-04-BATCH-005-PARTIAL-002-D-REPLAY-REPAIR-001` unless the
live lease check shows that lane is owned. Start with a clean-checkout RED
control. The reciprocal semantic implementation already exists at `2dcb161e`;
do not duplicate it or refresh receipts locally. Existing XLIFF skills do not
authorize `.gitattributes` or repository-wide digest policy, so route through
the governed missing-skill workflow before such a mutation.

If XLIFF is live-owned, select only an unleased disjoint obligation after
re-querying coordination. `UBL-03-PARTIAL-005-DERIVATION-AND-INHERITANCE-EDGES`
is committed at `d8c10680`, its checkpoint is `ae31baed`, and that executor
completed its coordination session before this packet was sealed. Partial-006
is therefore an eligible fallback only after fresh coordination confirms it
is still unleased and replay of both commits passes. Any fallback does not
change the controller-selected XLIFF task.

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
