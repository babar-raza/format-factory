---
artifact_id: FF6-STATE-TASKCARD-PROTOCOL-001
artifact_type: provider_neutral_execution_protocol
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
---

# State Machine and Taskcard Execution Protocol

## Purpose

This protocol makes execution identity-independent. The same input commit,
taskcard, authority bytes, tools, and proof must lead Claude and Codex to the
same next action and the same acceptance decision.

## Program state machine

```text
DISCOVER
  -> SNAPSHOT
  -> CONTRACT
  -> IMPLEMENT
  -> VERIFY
  -> REPAIR
  -> CERTIFY
  -> EXTRACT
  -> RELEASE_PREP
  -> COMPLETE
```

Current state: `CONTRACT`.

Transition rules:

| From | To | Required evidence |
|---|---|---|
| `DISCOVER` | `SNAPSHOT` | repositories, formats, source, tests and evidence inventoried from a pinned commit |
| `SNAPSHOT` | `CONTRACT` | truth baseline and active gaps materialized |
| `CONTRACT` | `IMPLEMENT` | every mandatory profile/surface obligation compiled, authority-current, classified, and taskcarded |
| `IMPLEMENT` | `VERIFY` | bounded source change complete with local behavior, rejection, preservation and installed-wheel smoke proof |
| `VERIFY` | `REPAIR` | an executed gate exposes a reproducible unmet obligation |
| `REPAIR` | `VERIFY` | repair lands and invalidated proof is replayed |
| `VERIFY` | `CERTIFY` | implementation-verified proof graph is complete for the format |
| `CERTIFY` | `EXTRACT` | all mandatory certification gates pass from clean environments |
| `EXTRACT` | `RELEASE_PREP` | independent repository reproduces canonical source/package digests and recertifies |
| `RELEASE_PREP` | `COMPLETE` | all six are technically release-ready; external publication blocks may remain recorded |

No conversation, provider change, elapsed time, test count, or status edit can
cause a transition.

## Task state machine

```text
UNREGISTERED
  -> READY
  -> CLAIMED
  -> WORK_IN_PROGRESS
  -> VERIFYING
  -> CLOSE_INTENT
  -> PASS
  -> COMPLETE
```

Failure branches:

```text
WORK_IN_PROGRESS or VERIFYING
  -> NEEDS_REPAIR -> READY
  -> TECHNICALLY_BLOCKED
  -> EXTERNAL_RELEASE_BLOCKED
```

Meanings:

- `READY`: dependencies, scope, required skills, inputs, outputs, tests, and
  acceptance are explicit.
- `CLAIMED`: temporary coordination ownership only; it is not persisted
  product progress.
- `WORK_IN_PROGRESS`: tracked checkpoint states exactly which atomic substeps
  passed and which is first unmet.
- `VERIFYING`: mutation is frozen while required checks run.
- `CLOSE_INTENT`: write-ahead close record; projections are not yet allowed to
  claim completion.
- `PASS`: task acceptance is independently verified. It does not imply product
  certification.
- `COMPLETE`: close projection and successor selection are journaled.
- `NEEDS_REPAIR`: a reproducible technical defect and repair acceptance are
  recorded.
- `TECHNICALLY_BLOCKED`: same root cause remains after three materially
  different repair attempts and safe alternatives are exhausted.
- `EXTERNAL_RELEASE_BLOCKED`: technical work is complete but credentials,
  legal authority, or human-only publication authority is unavailable.

## Definition of an executable taskcard

An agent must not start mutation unless the taskcard defines:

1. stable task ID, mission ID, parent and dependencies;
2. current state;
3. scope and explicit forbidden scope;
4. registered skill IDs and command IDs;
5. canonical input paths and expected digests or digest-producing commands;
6. exact output paths;
7. ordered atomic substeps;
8. positive, negative and invalidation acceptance criteria;
9. focused, regression, static and replay commands;
10. close event and projection updates;
11. rollback or repair routing;
12. successor selection rule;
13. product/gate/promotion effect;
14. shift-safe checkpoint boundaries.

If any field is absent, create or repair the taskcard through the registered
planning skill before product mutation. Do not infer it from nearby code.

## Atomic substep contract

Every substep must leave the tracked tree integration-safe:

1. declare input hashes and intended paths;
2. resolve registered skill/command;
3. create execution manifest;
4. acquire exact leases;
5. run mutation guard and per-file preflight;
6. apply one coherent change;
7. record every write;
8. run the smallest decisive check;
9. run the taskcard regression tier;
10. record evidence and first unmet criterion;
11. either proceed to the next substep or create a WIP checkpoint.

A substep is not checkpointable if the source fails to import, generated output
is inconsistent with its generator, required tests newly fail, or projections
claim evidence not yet executed.

## Current task decomposition

Task: `TC-FF6-IPYNB-PROFILE-SURFACE-001`.

| Step | Required output | Exit test |
|---|---|---|
| IPY-01 | event 17, task, authority and worktree preflight | native chain, controller/task agreement, 15/15 authority match |
| IPY-02 | source-located schema/document delta matrix for 4.0–4.5 | every delta has source ID, location, confidence and profile set |
| IPY-03 | audited SAL fact/evidence map | exact verifier passes; no dangling, duplicate or foreign edge |
| IPY-04 | profile-homogeneous capability model | mixed-version capabilities split; all six target profiles covered |
| IPY-05 | regenerated IPYNB contract and obligation projection | every capability/obligation has non-empty profile subset |
| IPY-06 | strict six-format replay | three byte-identical runs; aggregate recomputed; 15/15 authorities match |
| IPY-07 | close projection | IPYNB gap removed by evidence; remaining NRRD/XLIFF/UBL gaps retained |
| IPY-08 | remote checkpoint | explicit files committed and pushed to GitLab main; remote hash verified |

Product source and product tests are forbidden in IPY-01 through IPY-08.

## Shift checkpoint state

A shift checkpoint must record:

- source commit and fetched remote relationship;
- program state and event head;
- task state;
- completed atomic substeps;
- first unmet substep;
- changed paths and their hashes;
- validation commands and exact outcomes;
- known failures separated into introduced, inherited, and unavailable;
- current gaps and promotion effect;
- coordination session disposition;
- exact next command or taskcard step.

The incoming agent recomputes these facts. It never accepts the outgoing
agent’s self-verdict without replay.

## Consistency and recovery rules

- Event append precedes mutable projection replacement.
- A crash after event append is recovered by replay; never append a duplicate.
- A changed input invalidates descendants, even when output bytes happen to
  match.
- A deleted test revokes its obligation evidence.
- A WIP event may be committed only when the partial tree passes its declared
  integration-safe gate.
- Uncommitted work is never advertised as a clean checkpoint.
- If remote main moved, classify overlap and rerun affected proof before
  integrating.
- A blocked format does not stop another ready format.
- Human-only release authority never blocks technical release preparation.
