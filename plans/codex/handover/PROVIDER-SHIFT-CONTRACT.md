---
artifact_id: FF6-PROVIDER-SHIFT-CONTRACT
artifact_type: provider_neutral_execution_contract
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# FF6 Provider-Shift and Clean-Checkpoint Contract

This contract governs every transfer of the six-library production mission
between Claude, Codex, or another registered executor. It exists because a
chat summary, provider identity, lease token, dirty worktree, or passing
focused test is not a durable checkpoint.

The goal, phase order, task semantics, evidence standard, and terminal
condition do not change when the provider changes. Only the current executor
identity and its leased files change.

> **Current authority overlay: Event 33.** The native head is
> `FF6-EVENT-000033`; the latest implementation checkpoint is `a79dad74`;
> the accepted XLIFF boundary remains `ff8f7d9f` at 27/105 source-bound
> obligations and 3/1,130 independently verified dispositions; UBL now has
> 6,001 content-addressed local particle nodes and remains non-promoting.
> The exact canonical successor is
> `XLF-04-BATCH-005-PARTIAL-002-C`. Use
> [CURRENT-MACHINE-STATE.yaml](CURRENT-MACHINE-STATE.yaml) and
> [NEXT-MICROSTEP.yaml](NEXT-MICROSTEP.yaml) for executable state.
>
> Event 29-31 routes and counts below are retained only as failure and recovery
> history. They are non-operative. In particular, `d99fc6bf` remains a useful
> negative control, not an accepted checkpoint or resume target.

## 1. Locked mission

Mission: `FF6-PRODUCTION-LIBRARIES-001`.

Produce six independently publishable Python libraries:

1. `format-factory-ipynb`
2. `format-factory-openraster`
3. `format-factory-nrrd`
4. `format-factory-xliff`
5. `format-factory-safetensors`
6. `format-factory-ubl`

Each library must provide the complete, explicitly supported format-specific
capability surface that production developers need. Every capability must be
implemented, secure, typed, documented, tested against built and installed
packages, validated against primary authority, and supported by independent
interoperability evidence. Professional package structure and maintainability
are part of the product, not cleanup deferred until release.

The mission is not complete until all six libraries are technically certified
and repository-extraction-ready. Publication can remain externally blocked by
credentials or a human-only release gate, but source, packages, documentation,
SBOM, provenance, signatures, and certification evidence must still be
complete.

Current truth: `0/6` libraries are certified and all six promotions are
`UNASSESSED`.

## 2. Authority order

When records disagree, use this order:

1. fetched GitLab `origin/main`;
2. `AGENTS.md` and the canonical skill-only policy;
3. `plans/strategic/ff6/product-goal.yaml`;
4. the complete native journal
   `plans/strategic/ff6/events.jsonl`;
5. `plans/strategic/ff6/controller-state.yaml`;
6. registered taskcard and `taskcards/index.yaml`;
7. current digest-bound proof artifacts;
8. this derived handover packet;
9. conversation memory or provider summaries.

Never rewrite a higher authority to match a lower one. If the journal is newer
than this packet, validate the journal, rebuild projections, and refresh this
packet.

## 3. Three states that must remain separate

Every shift records three independent state axes:

| Axis | Question | Current answer |
|---|---|---|
| Mission state | What does the native journal authorize next? | `CONTRACT`, `FF6-EVENT-000033`, XLIFF `XLF-04-BATCH-005-PARTIAL-002-C`; UBL partial 004 is the disjoint fallback |
| Immutable evidence state | What committed work can be replayed? | Event 33 binds `a79dad74` and 6,001 UBL particle nodes; Event 32 accepts XLIFF `ff8f7d9f` at 27/105 obligations and 3/1,130 dispositions; Event 31 remains a rejected-attempt negative control |
| Workspace transfer state | Which current local bytes can the incoming executor own? | Seven attributed XLIFF occurrence paths are preserved outside the checkpoint and require governed takeover plus independent replay; all accepted proof is reconstructible from GitLab `origin/main` |

An immutable evidence commit without a journal transition is not a task-state
transition. A dirty worktree with a passing test is not a committed checkpoint.
An `ACTIVE` lease is not transferable authority. These distinctions prevent
duplicate work, status inflation, and cross-provider data loss.

## 4. Current clean checkpoint

At the immutable Event 30 boundary:

- The bounded XLIFF implementation commit is
  `e13e103de0bb789ff51a8e931af0fb649474be20`.
- Native journal head is `FF6-EVENT-000030`, hash
  `2d365d013b94c386014d7e75813114de6d7a225e2a9e16d21a485a38cd2d9398`.
- Canonical active task is
  `TC-FF6-XLIFF-PROFILE-SURFACE-001`.
- Canonical exact next microstep is
  `XLF-04-BATCH-005-PARTIAL-002-B`.
- XLIFF Event 30 proves 1,130 source-authentic candidates, one independently
  verified disposition, 26 source-bound obligation rows, and 79 missing rows.
  It does not close XLF-04.
- UBL commits `7b5cce4f` and `7fc49c29` prove UBL-02 and UBL-01;
  `f98d220a` proves the first UBL-03 root/type graph primitive. Events 27 and
  28 record those task-state effects.
- The current capability compiler replay is:
  aggregate
  `e199e84e9f7ee0579959db28283ecb89e014077cdd1605fbf0c82aee553d9960`;
  three-run digest
  `eafd6f8657ed83b73dbd5975046698d24fda6d8fd58c3d6aea962e6b6a85cf7c`.
- The controller contains those capability digests and the Event 30 XLIFF
  adjudication and inventory digests.
- No product overlay or provider-local recovery asset is required. The packet
  commit must descend from the implementation commit, but cannot hash itself.

## 5. Exact start algorithm for every incoming executor

Run this algorithm before any mutation:

1. Read `AGENTS.md` completely. Codex also reads
   `docs/governance/codex-adapter.md` and
   `docs/governance/skill-only-policy.yaml`.
2. Read this contract, `START-HERE.md`, `INFLIGHT-RECOVERY.yaml`,
   `CLAUDE-START.md`, `CURRENT-SHIFT-HANDOVER.md`, `checkpoint.yaml`, and
   `CURRENT-MACHINE-STATE.yaml`.
3. Fetch GitLab `origin`; do not fetch or push GitHub for this mission.
4. Compare `HEAD`, `origin/main`, the required packet ancestor, the controller
   event, the journal tail, and every recorded recovery-path hash.
5. Run `validate_handover.py --self-test`.
6. Query coordination status, live leases, stale candidates, open conflicts,
   Git status, and relevant process state. Coordination status may be nonzero
   because historical open conflicts exist; classify scope rather than
   pretending the database is clean.
7. Register a new provider identity. Never reuse an outgoing identity or
   token.
8. Select the exact registered skill route, claim only paths demonstrated by
   the next RED test, create a fresh execution manifest, run the mutation
   guard, preflight before every write, and record every write.
9. Recompute the next action from the decision table below.

If any higher authority advanced, stop following the old exact-next text,
rebuild the state projection, and refresh the packet before product work.

## 6. Deterministic work-selection decision

Use this decision order:

```text
new native event after Event 30?
  yes -> validate the complete chain and execute the newly computed task
  no  -> product overlay or unexplained dirty state exists?
           yes -> preserve and reconcile; continue only disjoint safe work
           no  -> exact XLIFF Partial-002-B scope live-owned?
                    yes -> preserve XLIFF; execute serialized UBL fallback
                    no  -> replay Event 30 and start the fixed RED candidate
```

Canonical priority and operationally safe priority are different:

- The controller-selected product-contract task remains XLIFF Batch 005.
- While that scope is live-owned, the first safe disjoint action is UBL-03.
  It does not replace XLIFF as active task.
- The machine action ID is `UBL-03`.
- After Event 30, if XLIFF remains live-owned, UBL-03 may continue only if the
  serialized projections agree and its exact source/report paths are
  independently leased.

Never select work by scanning historical gap ledgers, copying an old prompt,
or choosing the easiest passing test.

## 7. Recorded UBL checkpoint contract (Events 27 and 28)

This completed checkpoint binds already committed evidence. It does not
implement new UBL format behavior.

Required immutable inputs:

- package/root census commit `7b5cce4f`;
- authority/SAL closure commit `7fc49c29`;
- UBL package report SHA-256
  `787c8d9258dc25a8662ee934b9b0b14096de790db87826dab970792b9494976d`;
- SAL receipt SHA-256
  `2cc0f2cac163b7f42ab18bbe5220837d1f49a808904ac964c536085ca6d111a0`;
- 890 package members;
- 91 unique document roots;
- three of three authority artifacts `MATCH`;
- 34 of 34 SAL facts verified;
- capability aggregate and three-run digests recorded in section 4.

Required serialized result:

- Event 27 exists exactly once after Event 26;
- Event 28 exists exactly once after Event 27 and binds the root/type graph
  primitive at `f98d220a`;
- Event 29 exists exactly once after Event 28 and preserves UBL as a disjoint
  partial checkpoint while returning the journal head to XLIFF work;
- preserve controller state `CONTRACT`;
- represent UBL task progress as `WORK_IN_PROGRESS`;
- record completed UBL steps `UBL-01` and `UBL-02`;
- record first unmet step `UBL-03`;
- keep canonical active/next task XLIFF
  `TC-FF6-XLIFF-PROFILE-SURFACE-001`;
- keep exact XLIFF next action `XLF-04-BATCH-005-PARTIAL-002-B`;
- update the controller capability digests only from a fresh identical replay;
- update the UBL taskcard and task index consistently;
- keep the broad UBL typing gap open;
- preserve `0/6` certification and all `UNASSESSED` promotions.

Recorded write order:

1. independently replay evidence;
2. claim/take over only stale plan-control leases through the governed verb;
3. append the hash-chained event first;
4. record the journal write;
5. update controller and task projections from that event;
6. validate the chain and projections;
7. commit and push the exact plan-control files;
8. refresh this handover in a separate bounded commit.

Forbidden shortcuts:

- manually changing the UBL status without a journal event;
- appending more than one event for the two committed steps;
- changing the XLIFF active task;
- restarting UBL-03 before Events 27-29 projections agree;
- replaying `--apply` to manufacture fresh-looking evidence;
- treating 91 named roots as a reachable typed schema graph;
- treating current source classes as certification.

## 8. XLIFF Batch 005 partial-002 contract

When its paths are safely ownable, resume the same task rather than starting a
replacement. The exact first candidate and RED controls are locked in
`NEXT-MICROSTEP.yaml`:

1. preserve the 26 existing source-bound obligation rows;
2. retain generated dispositions as proposals, never as proof;
3. preserve and revalidate the committed content-addressed adjudication record
   binding candidate,
   occurrence, authority, denominator, decision, accepted IDs, rejected IDs,
   and reasons;
4. replay Event 30 check modes and its three immutable smoke tests, then write
   the new failing decision test for
   `XLF-CAND-CORE-SCHEMATRON-00C4A041AF12C8A1`;
5. increment verified counts only from valid independent adjudications;
6. reuse an exact canonical obligation only if its semantics own the rule;
   otherwise add a new stable denominator ID with exact authority evidence;
7. compile source-bound obligations only after their adjudications validate;
8. retain `complete: false` until authority census, expected-ID closure, and
   canonical SAL verification are all complete.

Event 30 facts that must not be weakened:

- 1,130 candidates: 182 normative prose, 588 non-modal prose, 264 XSD, and 96
  Schematron;
- every candidate is bound to pinned authority replay;
- one disposition is independently verified and 1,129 remain unverified;
- 26 source-bound rows exist and 79 expected IDs remain missing;
- every existing row remains `SOURCE_BOUND_UNVERIFIED`.

## 9. Per-task execution transaction

Every taskcard or bounded microstep uses this transaction:

```text
DISCOVER
-> RECONCILE
-> CLAIM
-> RED
-> GREEN
-> REFACTOR
-> FOCUSED_VERIFY
-> AFFECTED_REGRESSION
-> IMMUTABLE_SOURCE_COMMIT
-> NATIVE_JOURNAL_CHECKPOINT
-> PROJECTION_REBUILD
-> HANDOVER_REFRESH
-> GITLAB_REMOTE_VERIFY
-> RELEASE_LEASES
-> RESUMABLE
```

Failure transitions:

- test failure -> `REPAIR`, retain exact failure and changed proof inputs;
- foreign mutation -> `PRESERVE_AND_RECONCILE`;
- lost provider -> `RECOVERY_REQUIRED`, never optimistic completion;
- authority contradiction -> `CONTRADICTION_OPEN`, add a discriminating test;
- publication credential or business gate -> `EXTERNAL_RELEASE_BLOCKED` only
  after all technical artifacts are complete.

No executor may call its own implementation production-valid. Independent
validators, installed-wheel tests, external implementations, and immutable
proof determine promotion.

## 10. Clean checkpoint definition

A shift may call its state `RESUMABLE` only when all applicable conditions
hold:

- bounded source/evidence changes are committed;
- the commit is pushed to GitLab `origin/main`;
- required native event is appended exactly once;
- controller, taskcard, task index, gap projection, and handover agree;
- proof commands pass against the committed or staged snapshot;
- root manifest hashes match LF-normalized bytes;
- no unexplained dirty path is included;
- foreign dirty paths are separately classified and untouched;
- coordination writes are recorded;
- the outgoing identity releases only its own leases and completes.

A RED-only worktree, implementation-only commit, unjournaled GREEN result,
stale projection, local transcript, or unpushed commit is a recovery state,
not a clean checkpoint.

## 11. Handover at token or shift boundary

Before ending a provider shift:

1. stop at the smallest safe transaction boundary;
2. run the bounded verification and affected regression tier;
3. commit/push finished immutable work if valid;
4. journal it if its task state changes;
5. refresh this packet from live state;
6. record every dirty path with owner, Git status, digest policy, test state,
   and safe recovery action;
7. record the exact first unmet task step and first command;
8. run the handover validator and semantic negative controls;
9. explicitly stage only owned files;
10. push to GitLab and verify remote ancestry;
11. release only the outgoing executor's leases and complete its identity.

If a clean checkpoint cannot be completed, mark the workspace
`RECOVERY_REQUIRED` and preserve the bytes. Never claim a clean transfer for
convenience.

### Two-phase provider transfer

Provider transfer is a two-phase transaction; it is not a lease-token handoff.

`OUTBOUND_FREEZE`

1. stop new product mutations;
2. finish or explicitly classify the current bounded transaction;
3. push every completed immutable checkpoint and journal transition;
4. capture Git, controller, journal, proof, dirty-path, and coordination state;
5. refresh and validate this packet;
6. release only the outgoing identity's leases and complete that identity.

`INBOUND_ADOPT`

1. fetch GitLab and validate the packet against current higher authorities;
2. register a new provider identity;
3. requery the off-repo coordination plane;
4. classify every dirty path as committed, foreign-live, stale-attributable,
   or unexplained;
5. select work from the journal and decision table;
6. claim only the exact selected scope;
7. create a new execution manifest and mutation authorization;
8. rerun the smallest discriminating verification before writing.

There is deliberately no state in which an incoming provider inherits the
outgoing provider's identity, token, lease, local manifest, uncommitted bytes,
or self-reported test result. This removes provider memory from the correctness
boundary.

## 12. Minimum handback record

Every future handback must contain:

- goal ID and unchanged terminal condition;
- GitLab remote/branch and immutable source commit;
- journal event ID/hash and controller state;
- active task, completed steps, first unmet step, and exact next command;
- source/test/report/receipt paths and digests;
- exact tests, exit codes, pass/fail counts, and known baseline failures;
- current product certification and promotion states;
- live/stale lease ownership and all dirty paths;
- implementation-only or journal-only recovery cases;
- open contradictions, gaps, risks, and unsupported claims;
- exact validation and rollback/recovery commands.

The receiving executor must be able to resume from these files alone.

## 13. Regression controls for the handover machinery

The packet validator must continue to reject:

1. omission of a completed batch;
2. selection of a completed batch as next;
3. a controller/event-head mismatch;
4. any false product certification;
5. any false claim that foreign dirty bytes are transferable;
6. invalid recovery-asset identity;
7. any false regression of committed UBL authority evidence;
8. freezing active XLIFF bytes as immutable proof.

Future hardening should add negative controls for:

- an implementation commit without a journal event;
- a journal event without corresponding immutable evidence;
- a changed capability digest left stale in the controller;
- duplicate event serialization;
- a provider reusing another provider's identity;
- a packet that cites GitHub or a non-main branch;
- a packet that labels historical open conflicts as a clean coordination
  plane.

The current handover validator additionally rejects stale Event 27/dirty
workspace text in live projections and binds the exact first XLIFF candidate
batch. Content hashes alone are not accepted as semantic currency proof.

## 14. Production limits and honest claims

- Contract completeness is not product completeness.
- Source and test counts do not establish capability depth.
- Synthetic fixtures cannot be the only interoperability evidence.
- OpenRaster certification must remain a named interoperability claim because
  its authority is an early draft.
- Jupyter notebooks are never executed.
- UBL national profiles are separate packages.
- XLIFF 2.2 remains preview-only and XLIFF 1.2 requires a separate model.
- Exact byte reproduction is promised only where explicitly supported.
- Python 3.11 through 3.14 is the production matrix.
- Human-only publication authority is not bypassed, but it does not stop
  technical completion.

## 15. Navigation

- [Start file](START-HERE.md)
- [Current shift handover](CURRENT-SHIFT-HANDOVER.md)
- [Claude/Codex execution instructions](CLAUDE-START.md)
- [Machine checkpoint](checkpoint.yaml)
- [Complete machine state](CURRENT-MACHINE-STATE.yaml)
- [In-flight recovery](INFLIGHT-RECOVERY.yaml)
- [UBL checkpoint](PARALLEL-UBL-CHECKPOINT.yaml)
- [Validation and release controls](VALIDATION-AND-RELEASE.md)
- [Canonical execution plan](../../strategic/autonomous-six-python-production-execution-plan.md)
- [Canonical product goal](../../strategic/ff6/product-goal.yaml)

## Current authority overlay: Event 34

`FF6-EVENT-000034` is the current native head. The selected task remains
XLIFF `XLF-04-BATCH-005-PARTIAL-002-C` at 27/105 accepted obligations and
3/1,130 verified dispositions. Seven hash-bound XLIFF occurrence paths must
be adopted through governed takeover and independent replay before mutation.
When that lane remains live-owned, the disjoint fallback is UBL
`UBL-03-PARTIAL-005-DERIVATION-AND-INHERITANCE-EDGES` from `8e61ee11`.
The UBL graph retains 6,001 particle nodes and stable anonymous-type identity
machinery, but UBL-03 is incomplete. Certification remains 0/6.
