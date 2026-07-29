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

## TDD microstep and provider-shift state machine

A task step such as XLF-03 is too coarse to identify an interrupted TDD cycle.
Every code-producing substep therefore uses this provider-neutral microstate:

```text
PLANNED
  -> RED_OBSERVED
  -> GREEN_VERIFIED
  -> CHECKPOINT_COMMITTED
  -> JOURNALED
  -> PACKET_REFRESHED
  -> REMOTE_VERIFIED
  -> RESUMABLE
```

- `RED_OBSERVED` proves the test detects the missing behavior. It is not a
  shift boundary and must not be promoted or pushed as a clean checkpoint.
- `GREEN_VERIFIED` requires the focused test plus the declared regression and
  static tiers.
- `CHECKPOINT_COMMITTED` binds coherent source, tests, and a skill receipt to
  one Git commit. A commit alone is not a durable resume instruction.
- `JOURNALED` records that commit, file digests, exact validation, unfinished
  parent criterion, and exact next test in the native FF6 chain.
- `PACKET_REFRESHED` makes the journaled state discoverable without relying on
  provider memory.
- `REMOTE_VERIFIED` requires the GitLab `origin/main` ref to contain both the
  implementation commit and the packet/controller commit.
- `RESUMABLE` additionally requires prior coordination ownership to be
  completed or safely taken over.

A crash may leave an uncommitted `RED_OBSERVED` tree. The incoming executor
must classify and preserve it through coordination takeover, then continue to
`GREEN_VERIFIED`; it must not call that state a clean checkpoint. Planned
token exhaustion is handled before starting a microstep or after
`REMOTE_VERIFIED`, never between RED and GREEN.

## Current task decomposition

Task: `TC-FF6-XLIFF-PROFILE-SURFACE-001`.

| Step | Required output | Exit test |
|---|---|---|
| XLF-01 — PASS at event 20 | event 19, task/index/controller, authority and worktree preflight | native chain, exact READY task, clean or classified tree, 15/15 predecessor authority match |
| XLF-02 — PASS at event 20 | official XLIFF 2.0 authority record, five-source XLIFF closure, and 42-member 2.0/2.1 inventory | independent digest plus published SHA-1 cross-check, legal record, 5/5 clean offline reconstruction, no 2.1-as-2.0 proxy |
| XLF-03 — FIRST UNMET; event-21 microstate `GREEN_VERIFIED_CHECKPOINTED` | source-located 2.0/2.1 Core and module delta matrix | first compiler slice is committed and tested; next RED test is `test_cli_writes_and_checks_default_xliff_matrix`; XLF-03 passes only when every requirement has source/member/location, profile set, Core/module owner, confidence, and contradiction note |
| XLF-04 | complete Core SAL and processing-requirement map | exact verifier passes; inline, segmentation, state, extension, skeleton, ITS, and agent rules are not reduced to XSD validity |
| XLF-05 | separately owned Translation Candidates/Matches, Glossary, Format Style, Metadata, Resource Data, Size/Length, Validation, and ITS families | all eight official modules and all nine module schema vocabularies are accounted for; each module has typed-model, read/write, validation, preservation, rejection, and proof obligations |
| XLF-06 | repaired research/family/enrichment layers | mixed-profile requirements split; explicit-complete ownership; no keyword duplication |
| XLF-07 | exact stable and preview projections | both stable profiles claimed; 2.1-only rules excluded from 2.0; 2.2 preview isolated; 1.2 outside model |
| XLF-08 | replay, close, and remote checkpoint | negative controls, three identical runs, all authorities match, event/controller/task/handover committed and remote-verified |

Product source and product tests are forbidden in XLF-01 through XLF-08.

XLF-03 through XLF-07 must explicitly cover files, groups, units, segments,
ignorable content, notes, original data, skeleton references, extension
points, inline identity/pairing/nesting/order/isolation, language and direction
inheritance, state/sub-state, segmentation and re-segmentation, Core and module
processing requirements, namespace-aware preservation, deterministic
canonical XML, downgrade-loss reporting, XML security, resource limits, and
all eight official 2.1 modules. The nine module schema vocabularies
(`matches`, `glossary`, `fs`, `metadata`, `resource_data`,
`size_restriction`, `validation`, `its`, `itsm`) must map to those eight
owners because `its` and `itsm` are one ITS module. The informative Change
Tracking extension is inventoried without normative conformance credit.
Preservation-only content is not modeled module support. Schema validity is
necessary but cannot satisfy semantic or agent processing obligations.

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
- A shift event for partial code must bind the implementation commit, source
  and test digests, validation boundary, first unmet task criterion, and exact
  next RED test.
- The outgoing provider commits the coherent implementation slice first,
  journals that immutable commit second, refreshes projections/packet third,
  and verifies the two-commit descendant on GitLab main last.
- If remote main moved, classify overlap and rerun affected proof before
  integrating.
- A blocked format does not stop another ready format.
- Human-only release authority never blocks technical release preparation.
