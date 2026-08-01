---
artifact_id: FF6-CLAUDE-START-41BFAEF
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Claude exact start and stop sequence

## 1. Reconstruct authority without changing state

```powershell
Set-Location 'C:\Users\prora\OneDrive\Documents\GitHub\format-factory'
Get-Content -LiteralPath AGENTS.md
git fetch origin main --prune
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 41bfaef73992f69313226543dff81d3a11e232bb origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_committed_checkpoint.py --ref origin/main
git status --short --branch
.venv\Scripts\python.exe -m tools.supervisor.coordination --json status
```

At this packet, the expected native head is `FF6-EVENT-000036` /
`d4a05e36bbae4d3ab5f05a4968045552f79ae45dd7b38f6ba3bc39840f684924`.
If GitLab has advanced, validate the newer chain and regenerate this packet;
do not reset or force-push. If the shared tree is clean, also run:

```powershell
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --require-clean --self-test
```

If it is dirty, attribute every path through coordination. Never use restore,
stash, reset, clean, checkout, or broad staging on unexplained state.

## 2. Read the binding execution context

Read, in order:

1. `plans/master-plan.md`
2. `plans/strategic/ff6/product-goal.yaml`
3. `plans/strategic/ff6/controller-state.yaml`
4. the complete `plans/strategic/ff6/events.jsonl`
5. `taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md`
6. `plans/codex/handover/NEXT-MICROSTEP.yaml`
7. `.supervisor/knowledge/registry.yaml` and every applicable verified contract
8. every selected `.claude/commands/<skill>.md` contract
9. `docs/governance/codex-adapter.md` if the next provider is Codex

Do not reimplement the accepted reciprocal skeleton change or its checkout
repair. They are immutable history at `2dcb161e`, repair commit
`809cc18cc6e62ae19f6ea5c11ed41ab9a7ec5956`, and Event 36.

## 3. Establish a fresh shift identity

```powershell
.venv\Scripts\python.exe -m tools.supervisor.coordination register `
  --provider claude-code --mode interactive `
  --task TC-FF6-XLIFF-PROFILE-SURFACE-001
```

Use only the returned identity/token for this shift. Claim the logical
microstep and exact files, preflight every write, record every write, heartbeat
during long validation, and never release another provider's lease.

## 4. Execute the exact next microstep

Run `XLF-04-BATCH-005-PARTIAL-002-E` for
`XLF-CAND-CORE-SCHEMATRON-100732DB0BBED389`.

Before mutation, reconfirm:

- controller Event 36 and GitLab checkpoint `41bfaef7`;
- 5 verified / 1,125 open candidate dispositions;
- 28 resolved / 77 missing of 105 obligations;
- candidate content digest `7564733d...`, requirement digest `51c4d1ac...`,
  and occurrence digest `903d76dd...`;
- exact authority occurrence `schematron/rule[12]/report[1]` in the pinned
  XLIFF 2.1 Core Schematron member;
- checkout identity and all predecessor proof hashes.

Execution order is RED test, independent authority adjudication, SAL/proof
repair if required, deterministic artifact compilation, complete focused and
regression validation, immutable checkout replay, then native controller
projection. Generated owner mappings are proposals only. If no existing
denominator row is the direct owner, record and schedule the gap; never force a
mapping to make coverage rise.

## 5. Required proof before the next event

- positive, rejection, tamper, and predecessor-preservation tests;
- exact candidate/occurrence/authority/SAL/decision digest closure;
- all 28 accepted predecessor rows semantically equal;
- all 1,130 candidate identities unchanged;
- three byte-identical clean generations;
- Ruff, strict Mypy, Pyright 1.1.411, and bytecode compilation on touched code;
- SAL verification and 5/5 XLIFF authority matches;
- affected tool tests plus format-contract and production-program regressions;
- zero-warning skill transcripts;
- detached checkout replay from the candidate commit;
- native event chain and controller/task/handover agreement.

## 6. Close the shift safely

1. Stage only reviewed leased files.
2. Commit to `main`; push only `origin main`; prove `HEAD == origin/main`.
3. Replay the exact immutable commit with digest-pinned authority inputs.
4. Refresh every operational handover file and LF-normalized manifest from the
   new native journal head.
5. Run both handover validators and their negative controls.
6. Record writes, release only this shift's leases, and complete the identity.

Never report a production-ready library unless the full product certification
graph—not a focused contract microstep—proves it. Current status is 0/6.
