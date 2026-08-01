---
artifact_id: FF6-CLAUDE-START-EVENT-39
artifact_type: executor_start_instructions
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Claude start instructions: Event 39

These instructions are provider-neutral in substance. Claude must use its
ambient governance hooks; Codex must explicitly follow
`docs/governance/codex-adapter.md`. Neither provider inherits the outgoing
execution identity.

## 1. Establish immutable GitLab state

From the repository root:

```powershell
git fetch origin main
git remote get-url origin
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor c421940ae70a3dc949318eee00cbfc5e3cf8b9a3 origin/main
git merge-base --is-ancestor 39b2e89fde0f7dd5e1acebc424f4d700dfe74765 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_committed_checkpoint.py --ref origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --self-test
```

`origin` must be the GitLab URL and the active branch must be `main`. If
`origin/main` is newer, validate its newest native event and regenerate this
derived packet. Never reset GitLab to the packet, use GitHub, or create another
branch.

Expected checkpoint:

- event: `FF6-EVENT-000039`
- event hash:
  `5f76c75ca4f7bc0845b22dccd38a195e962fb49b5f4161651737ab23d560cd36`
- controller state: `CONTRACT`
- control checkpoint: `c421940ae70a3dc949318eee00cbfc5e3cf8b9a3`
- accepted semantic commit:
  `39b2e89fde0f7dd5e1acebc424f4d700dfe74765`
- selected task: `TC-FF6-XLIFF-PROFILE-SURFACE-001`
- first unmet step: `XLF-04`
- exact microstep: `XLF-04-BATCH-005-PARTIAL-002-H`

## 2. Re-establish coordination

Run the provider's governed registration flow, then query:

```powershell
.venv\Scripts\python.exe -m tools.supervisor.coordination status
.venv\Scripts\python.exe -m tools.supervisor.coordination conflicts list
```

Register a new identity for `TC-FF6-XLIFF-PROFILE-SURFACE-001`. Never copy a
prior agent ID or token. Claim the exact candidate work set and a logical
microstep resource, preflight before every write, record every write, heartbeat
during long verification, and release only leases owned by the new identity.
Open conflicts are not authorization to resolve unrelated paths.

Use registered skills in this order:

1. `test-driven-development`;
2. `ingest-spec-sal` only if exact authority requires a new fact;
3. `sal-pipeline-heal` for fact/store/proof reconciliation;
4. `compile-format-contract` if contract inputs change;
5. `plan-control` only after the semantic commit passes immutable replay;
6. `refresh-provider-neutral-handover` after the new event is committed.

Create new execution manifests and mutation authorizations. Local state from a
previous shift is evidence to inspect, never authority to reuse.

## 3. Revalidate the accepted boundary

Before editing, recompute:

- all 39 event hashes, sequences, and predecessor edges;
- controller head and taskcard agreement;
- exactly 1,130 candidate identities;
- exactly 8 verified and 1,122 unverified dispositions;
- exactly 105 expected obligations, 30 source-bound, and 75 missing;
- exact denominator, census, adjudication, inventory, and ProductContract
  digests;
- all 33 XLIFF SAL facts and all five authority records;
- the fresh XLIFF contract is `DRAFT` with 15 capabilities;
- all promotions remain `UNASSESSED` and certification remains `0/6`.

The immutable replay must restore the complete five-record XLIFF authority
closure: ignored external files `src-xlf-001.bin`, `src-xlf-002.bin`,
`src-xliff-001.bin`, and `src-xliff-003.bin`, plus the tracked
product-requirement authority. Restoring only the two packages can pass focused
tests and SAL verification but cannot prove ProductContract check-mode
identity.

## 4. Execute the exact TDD microstep

Run `XLF-04-BATCH-005-PARTIAL-002-H` for
`XLF-CAND-CORE-SCHEMATRON-E891C4DEC555F165`.

Pinned identity:

- profile: `xliff_2.1`
- source member: `schemas/xliff_core_2.1.sch`
- occurrence: `schematron/rule[15]/report[1]`
- content SHA-256:
  `04aeb46e7eeaa854cf9554005a11476334fa8f41f6db9a45ca2f0e38b8d6d0e6`
- requirement SHA-256:
  `d7daf659d3b7ad1388c42203d845b452afe12e8e05134d35d36a26cb9cc5e60c`
- occurrence SHA-256:
  `cb57d9e386c6274b0aa0aedca3e2b4bab1dbaafb41ff2e66a884681485d6c84f`
- normalized rule:
  `sc[isolated='yes']` in source content reports when a same-unit
  `ec[@startRef=$id]` exists.

Required sequence:

1. Independently read the exact Schematron occurrence and relevant Core prose.
2. Add a genuine pre-change failing test for the direct semantic obligation.
3. Treat all eight generated mappings in `NEXT-MICROSTEP.yaml` as proposals.
4. Decide the exact owner, or add an expected obligation only if authority
   proves a distinct missing semantic rule.
5. Explicitly reject generic validator behavior, hierarchy/cardinality trigger
   context, and element-name surfaces that do not directly own the constraint.
6. Bind candidate, occurrence, authority, fact, decision, obligation, and
   compiled contract with role-specific digests.
7. Add positive, rejection, tamper, profile, selected-seed, transactional, and
   predecessor-preservation tests.
8. Preserve all 30 accepted rows and all 1,130 candidate identities.
9. Rebuild deterministic descendants three times and compare canonical bytes.
10. Run affected tests, SAL and authority verification, contract and
    production-program regressions, Ruff, strict Mypy, Pyright 1.1.411,
    py_compile, transcript validation, and immutable detached replay.
11. Commit and push only the bounded semantic files to GitLab `main`.
12. Append the next native event only after immutable proof passes.
13. Derive controller/taskcard/handover projections from that event, commit and
    push them, validate the remote checkpoint, and release the shift.

## 5. Forbidden shortcuts

- Do not accept generated mappings, neighboring implementation behavior, or
  naming similarity as authority.
- Do not count an element mention, XPath ancestor, or validator report as a
  separate capability unless the normative semantic owner is distinct.
- Do not weaken source/digest validation, tamper rejection, checkout identity,
  selected-candidate seeding, or predecessor equality.
- Do not claim XLF-04 complete from a single disposition.
- Do not edit product source, gates, certification, promotion, or release state.
- Do not clean, stash, reset, restore, broadly stage, use `--no-verify`, use
  GitHub, create a branch, or release another agent's lease.

## 6. Clean shift exit

A provider-neutral checkpoint requires: semantic commit on GitLab; immutable
replay from all required inputs; next event appended only after proof;
controller/taskcard/receipts consistent; handover refreshed and pushed; remote
validator passing; no unexplained owned dirt; and only the current identity's
leases released. RED-only, local-only, or unjournaled GREEN work is not a clean
handover.
