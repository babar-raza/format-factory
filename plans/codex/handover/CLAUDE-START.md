---
artifact_id: FF6-CLAUDE-START-EVENT-38
artifact_type: executor_start_instructions
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Claude start instructions: Event 38

These instructions are provider-neutral in substance. Claude must apply its
ambient hooks; Codex must apply `docs/governance/codex-adapter.md` explicitly.
Neither provider inherits the outgoing execution identity.

## 1. Establish immutable GitLab state

From the repository root:

```powershell
git fetch origin
git remote get-url origin
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor d1f8b3229bf3be32675e047b1469259ad7375500 origin/main
git merge-base --is-ancestor 3fc939ad70ec6caac9e0699041076e02de00c5d2 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_committed_checkpoint.py
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --self-test
```

`origin` must be the GitLab URL. If `origin/main` is newer, validate the newer
native event and rebuild this derived packet; never reset GitLab to this packet.
Do not switch to or create another branch. Do not contact the GitHub remote.

Expected controller head:

- event: `FF6-EVENT-000038`
- event hash: `13db4cceafcefb86d9c964d7c3e20e7d63092977faf50002ef0c88ea4f6b5603`
- state: `CONTRACT`
- control checkpoint: `d1f8b3229bf3be32675e047b1469259ad7375500`
- accepted semantic commit: `3fc939ad70ec6caac9e0699041076e02de00c5d2`

## 2. Re-establish coordination

Run the provider's governed registration flow and query:

```powershell
.venv\Scripts\python.exe -m tools.supervisor.coordination status
.venv\Scripts\python.exe -m tools.supervisor.coordination conflicts list
```

Register a new identity for `TC-FF6-XLIFF-PROFILE-SURFACE-001`. Never copy the
outgoing agent ID or token. Claim the exact candidate work set plus a logical
microstep resource, then run preflight before every write and record-write
after every write. Existing open conflicts are not authorization to resolve or
take over unrelated paths.

Before product/source work, follow AGENTS.md B2a/B2b and load the verified
knowledge contracts. For this current contract microstep, use the registered
skills in this order:

1. `test-driven-development`
2. `ingest-spec-sal` if a new exact fact is required
3. `sal-pipeline-heal` for proof/store reconciliation
4. `plan-control` only after semantic proof is immutable

Create fresh execution manifests and mutation authorizations. Local manifests
from this shift are intentionally non-transferable.

## 3. Revalidate the accepted boundary

Before editing, prove:

- the complete 38-event native chain and controller projection agree;
- candidate count is 1,130;
- accepted candidate dispositions are 7 and open dispositions are 1,123;
- expected obligations are 105, source-bound obligations are 30, and 75 are
  missing;
- the four current generated artifacts reproduce their recorded digests;
- all 32 XLIFF SAL facts pass and all five authority locks match;
- the source-language semantic commit replays 90 affected tests;
- product certification remains `0/6` and all promotions remain `UNASSESSED`.

Do not accept this packet's statements as proof; the validator and immutable
checkout must recompute them.

## 4. Execute the exact TDD microstep

Run `XLF-04-BATCH-005-PARTIAL-002-G` for
`XLF-CAND-CORE-SCHEMATRON-5D563A565DC6DCFE`.

Pinned identity:

- profile: XLIFF 2.1 only
- source member: `schemas/xliff_core_2.1.sch`
- occurrence: `schematron/rule[14]/report[1]`
- content SHA-256: `2f48f02786ace40f8e45306a2622fb031a0650a1004e6d4b316f3dd5ec44ee4d`
- requirement SHA-256: `85279eddf8546a96b332e7a7b5388cb4639d886f2a6a0f7168048ec3e7e483ec`
- occurrence SHA-256: `639468d347a85cb3843f43bba0d0bdc9065beda22aee96021cb10f37374137fe`

Required sequence:

1. Read the exact pinned report and relevant Core prose independently.
2. Add a pre-change RED test for the semantic owner and proof binding.
3. Treat every generated proposal as a hypothesis, never as authority.
4. Decide whether target-language compatibility maps to one existing direct
   obligation or requires a new exact denominator obligation.
5. Account for every proposal and materially implicated obligation as accepted
   or rejected with evidence-bound reasoning.
6. Add positive, negative, tamper, profile-boundary, selected-seed, and
   predecessor-preservation tests.
7. Preserve semantic equality of all 30 accepted rows and identity of all
   1,130 candidates.
8. Generate deterministic artifacts three times and compare canonical bytes.
9. Run focused, SAL, authority, format-contract, production-program, Ruff,
   Mypy, Pyright, py_compile, transcript, and immutable-checkout verification.
10. Commit the bounded semantic slice to GitLab `main`.
11. Only after immutable replay passes, append the next hash-chained event and
    project controller/taskcard state through `plan-control`.
12. Refresh this packet and complete the shift only after GitLab remote proof.

## 5. Forbidden shortcuts

- Do not infer target compatibility from source-language symmetry alone.
- Do not accept `AGENT-VALIDATOR`, segment, or ignorable context as direct
  obligations without primary authority.
- Do not weaken exact source/digest validation or selected-candidate seeding.
- Do not rewrite, delete, stash, restore, or broadly stage foreign work.
- Do not claim XLF-04 complete from one row or one disposition.
- Do not edit gate, certification, promotion, or release state.
- Do not use `git add .`, `git add -A`, `--no-verify`, GitHub, or another branch.

## 6. Clean shift exit

A resumable checkpoint requires: semantic commit pushed to GitLab; immutable
replay; native event appended only if proof passes; controller/taskcard and
receipts consistent; refreshed handover committed and pushed; no owned dirty
paths; and release/completion of only the current identity's leases. RED-only,
local-only, or unjournaled GREEN state is not a clean transfer.
