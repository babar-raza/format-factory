---
artifact_id: FF6-CLAUDE-START-EVENT-40
artifact_type: executor_start_instructions
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Claude start instructions: Event 40

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
git merge-base --is-ancestor de569544eebc1fff011901e61d3574dcc48e5e08 origin/main
git merge-base --is-ancestor d95af5aeb248907b4d23457ecd288723fc9c2050 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_committed_checkpoint.py --ref origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --self-test
```

`origin` must be the GitLab URL and the active branch must be `main`. If
`origin/main` is newer, validate its newest native event and regenerate this
derived packet. Never reset GitLab to the packet, use GitHub, or create another
branch.

Expected checkpoint:

- event: `FF6-EVENT-000040`
- event hash:
  `c9c7167d447fbe0945c7a65c288f3cece78c64090e09c1ce2d674fdbf9bf2d63`
- controller state: `CONTRACT`
- control checkpoint: `de569544eebc1fff011901e61d3574dcc48e5e08`
- accepted semantic commit:
  `d95af5aeb248907b4d23457ecd288723fc9c2050`
- selected task: `TC-FF6-XLIFF-PROFILE-SURFACE-001`
- first unmet step: `XLF-04`
- exact microstep: `XLF-04-BATCH-005-PARTIAL-002-I`

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

- all 40 event hashes, sequences, and predecessor edges;
- controller head and taskcard agreement;
- exactly 1,130 candidate identities;
- exactly 9 verified and 1,121 unverified dispositions;
- exactly 105 expected obligations, 31 source-bound, and 74 missing;
- exact denominator, census, adjudication, inventory, and ProductContract
  digests;
- all 34 XLIFF SAL facts and all five authority records;
- the fresh XLIFF contract is `DRAFT` with 15 capabilities;
- all promotions remain `UNASSESSED` and certification remains `0/6`.

The immutable replay must restore the complete five-record XLIFF authority
closure: ignored external files `src-xlf-001.bin`, `src-xlf-002.bin`,
`src-xliff-001.bin`, and `src-xliff-003.bin`, plus the tracked
product-requirement authority. Restoring only the two packages can pass focused
tests and SAL verification but cannot prove ProductContract check-mode
identity.

## 4. Execute the exact TDD microstep

Run `XLF-04-BATCH-005-PARTIAL-002-I` for
`XLF-CAND-CORE-SCHEMATRON-60B596A00F7FA06A`.

Pinned identity:

- profile: `xliff_2.1`
- source member: `schemas/xliff_core_2.1.sch`
- occurrence: `schematron/rule[16]/report[1]`
- content SHA-256:
  `41719598a09ae47886c9d146932117abc74da0c2c6f51482d1e2a94c109dd900`
- requirement SHA-256:
  `823cd7fb987463c882d783105487f3463a316392accad13d3be184487c2c4959`
- occurrence SHA-256:
  `90c4965db1a12842770b7212cddaa078a48f48848896387093ad56cf4cdcf1a6`
- normalized rule:
  `sc[isolated='yes']` in target content reports when a same-unit
  `ec[@startRef=$id]` exists.

Required sequence:

1. Independently read the exact Schematron occurrence and relevant Core prose.
2. Add a genuine pre-change failing test for the direct semantic obligation.
3. Treat all eight generated mappings in `NEXT-MICROSTEP.yaml` as proposals.
4. Determine whether the report supplies reciprocal evidence for existing
   `SAL-XLIFF-CORE-INLINE-ISOLATION-001`; do not duplicate the obligation.
5. Explicitly reject generic validator behavior, hierarchy/cardinality trigger
   context, and element-name surfaces that do not directly own the constraint.
6. Bind candidate, occurrence, authority, fact, decision, obligation, and
   compiled contract with role-specific digests.
7. Add positive, rejection, tamper, profile, selected-seed, transactional, and
   predecessor-preservation tests.
8. Preserve all 31 accepted rows, all 9 decisions, and all 1,130 candidate identities.
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
