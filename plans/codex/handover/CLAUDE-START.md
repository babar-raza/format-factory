---
artifact_id: FF6-CLAUDE-START-809CC18
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Claude exact start and stop sequence

## 1. Reconstruct the immutable checkpoint

```powershell
Set-Location 'C:\Users\prora\OneDrive\Documents\GitHub\format-factory'
Get-Content -LiteralPath AGENTS.md
git fetch origin main --prune
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 809cc18cc6e62ae19f6ea5c11ed41ab9a7ec5956 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_committed_checkpoint.py --ref origin/main
git status --short --branch
.venv\Scripts\python.exe -m tools.supervisor.coordination --json status
```

Require local `HEAD` and `origin/main` to equal
`809cc18cc6e62ae19f6ea5c11ed41ab9a7ec5956` at initial resume. If GitLab has
advanced, do not reset it: validate the newer journal and rebuild this packet
from live authority. The expected native head at this checkpoint is
`FF6-EVENT-000035` /
`2866d7e70bd193f8aa7b60ca1f92f4f842d1cd470f97984c07f47d88ed2ea97d`.
Its accepted XLIFF implementation is
`591fcfe18808e5195c33570eaa9d334770e90166`.

If the shared tree is clean, also run:

```powershell
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --require-clean --self-test
```

If it is dirty, attribute every path through coordination. Preserve foreign
or unexplained bytes. Do not use restore, stash, reset, clean, checkout, or
broad staging.

## 2. Read authority before acting

Read, in order:

1. `plans/master-plan.md`
2. `docs/governance/codex-adapter.md` when the executor is Codex
3. `plans/strategic/ff6/product-goal.yaml`
4. `plans/strategic/ff6/controller-state.yaml`
5. the complete `plans/strategic/ff6/events.jsonl`
6. `taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md`
7. `plans/codex/handover/CLEAN-REPLAY-REPAIR.md`
8. `plans/codex/handover/NEXT-MICROSTEP.yaml`
9. `.claude/commands/plan-control.md` and every other selected skill contract

The semantic implementation commit `2dcb161e...`, accepted implementation
`591fcfe18808e5195c33570eaa9d334770e90166`, and proof-identity repair
commit `809cc18c...` already exist. Do not repeat either implementation.

## 3. Establish a new shift identity

```powershell
.venv\Scripts\python.exe -m tools.supervisor.coordination register `
  --provider claude-code --mode interactive `
  --task TC-FF6-XLIFF-PROFILE-SURFACE-001
```

Store the returned identity and token only for this shift. Claim the logical
transaction plus its exact controller/task/projection/handover paths.
Preflight before each write, record each write, heartbeat during long checks,
and never release another identity's lease.

## 4. Execute the exact next transaction

Run `XLF-04-BATCH-005-PARTIAL-002-D-REPLAY-REPAIR-001` in substate
`VERIFIED_PENDING_CONTROLLER_ACCEPTANCE`. Use `plan-control`, not a product
source skill. Reconfirm:

- Event 35 is the current journal head;
- `809cc18c` is on GitLab main;
- the adjudication has 5 verified and 1,125 unverified dispositions;
- the obligation inventory remains 28 resolved of 105, with 77 missing;
- all checkout-identity, affected XLIFF, static, and regression gates pass.

Append exactly one Event 36 accepting PARTIAL-002-D, binding both `2dcb161e`
and `809cc18c` plus current artifact hashes. Atomically update native controller,
taskcard/current projections, and derive the next candidate from the live
unverified set. Do not guess it from this packet. The accepted disposition
count becomes 5; obligation counts and all completion/promotion flags stay
unchanged.

## 5. Close the shift safely

1. Validate the event chain and projections.
2. Run focused and required regression gates in an isolated checkout.
3. Create zero-warning skill transcripts and receipts.
4. Stage only reviewed leased files and commit to `main`.
5. Push only `origin main` and prove `HEAD == origin/main`.
6. Replay the exact immutable commit.
7. Refresh every operational handover file and its LF-normalized manifest.
8. Run both handover validators with self-tests.
9. Record all writes, release only this shift's leases, and complete its
   coordination identity.

Never report any library production-ready. The program remains 0/6 certified
after this one-disposition controller acceptance.
