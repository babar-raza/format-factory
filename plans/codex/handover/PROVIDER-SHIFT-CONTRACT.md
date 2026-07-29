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
| Mission state | What does the native journal authorize next? | `CONTRACT`, Event 27, XLIFF `XLF-04-BATCH-005` |
| Immutable evidence state | What committed work can be replayed? | XLIFF Batch 004 and UBL-01/UBL-02 are journaled; UBL-03 is open |
| Workspace transfer state | Which current local bytes can the incoming executor own? | Five dirty XLIFF paths are foreign and under an `ACTIVE` Batch 005 lease |

An immutable evidence commit without a journal transition is not a task-state
transition. A dirty worktree with a passing test is not a committed checkpoint.
An `ACTIVE` lease is not transferable authority. These distinctions prevent
duplicate work, status inflation, and cross-provider data loss.

## 4. Current clean checkpoint

At this packet refresh:

- GitLab `origin/main` and local `HEAD` are
  `59ef8ee2e1b4e37168e4c7094687fac0a6098a79`.
- Native journal head is `FF6-EVENT-000027`,
  hash
  `9a1783b0705468fec1e9f9fda96f61ab4b1da32a161d128a3120a8bf689686c2`.
- Canonical active task is
  `TC-FF6-XLIFF-PROFILE-SURFACE-001`.
- Canonical exact next microstep is `XLF-04-BATCH-005`.
- UBL commits `7b5cce4f` and `7fc49c29` prove UBL-02 and UBL-01,
  respectively; Event 27 records their task-state effect.
- The current capability compiler replay is:
  aggregate
  `e199e84e9f7ee0579959db28283ecb89e014077cdd1605fbf0c82aee553d9960`;
  three-run digest
  `eafd6f8657ed83b73dbd5975046698d24fda6d8fd58c3d6aea962e6b6a85cf7c`.
- The controller contains the fresh capability aggregate and three-run
  digests recorded by Event 27.

The packet is derived from `59ef8ee2`. The commit containing a future refresh
must descend from that commit; the packet cannot embed its own final commit
hash.

## 5. Exact start algorithm for every incoming executor

Run this algorithm before any mutation:

1. Read `AGENTS.md` completely. Codex also reads
   `docs/governance/codex-adapter.md` and
   `docs/governance/skill-only-policy.yaml`.
2. Read this contract, `START-HERE.md`, `CURRENT-SHIFT-HANDOVER.md`,
   `checkpoint.yaml`, `CURRENT-MACHINE-STATE.yaml`, and
   `INFLIGHT-RECOVERY.yaml`.
3. Fetch GitLab `origin`; do not fetch or push GitHub for this mission.
4. Compare `HEAD`, `origin/main`, the required packet ancestor, the controller
   event, and the journal tail.
5. Run `validate_handover.py --self-test`.
6. Query coordination status, live leases, stale candidates, open conflicts,
   Git status, and relevant process state. Coordination status may be nonzero
   because historical open conflicts exist; classify scope rather than
   pretending the database is clean.
7. Register a new provider identity. Never reuse an outgoing identity or
   token.
8. Select the exact registered skill route, claim only required paths, create
   an execution manifest, run the mutation guard, preflight before every
   write, and record every write.
9. Recompute the next action from the decision table below.

If any higher authority advanced, stop following the old exact-next text,
rebuild the state projection, and refresh the packet before product work.

## 6. Deterministic work-selection decision

Use this decision order:

```text
new native event after Event 27?
  yes -> validate the complete chain and execute the newly computed task
  no  -> XLIFF Batch 005 scope owned by another ACTIVE lease?
           yes -> preserve all XLIFF bytes; execute UBL-03 under disjoint
                  leases; do not repeat Event 27
           no  -> Batch 005 implementation commit on origin/main?
                    yes -> replay it independently and journal it once
                    no  -> stale owner with attributable bytes?
                             yes -> governed takeover, rebaseline, continue
                             no  -> claim exact paths and start Batch 005
```

Canonical priority and operationally safe priority are different:

- The controller-selected product-contract task remains XLIFF Batch 005.
- While that scope is live-owned, the first safe disjoint action is UBL-03.
  It does not replace XLIFF as active task.
- The machine action ID is `UBL-03`.
- After Event 27, if XLIFF remains live-owned, UBL-03 may start only if the
  serialized projections agree and its exact source/report paths are
  independently leased.

Never select work by scanning historical gap ledgers, copying an old prompt,
or choosing the easiest passing test.

## 7. Recorded Event 27 checkpoint contract

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
- preserve controller state `CONTRACT`;
- represent UBL task progress as `WORK_IN_PROGRESS`;
- record completed UBL steps `UBL-01` and `UBL-02`;
- record first unmet step `UBL-03`;
- keep canonical active/next task XLIFF
  `TC-FF6-XLIFF-PROFILE-SURFACE-001`;
- keep exact XLIFF next action `XLF-04-BATCH-005`;
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
- starting UBL-03 before Event 27 projections agree;
- replaying `--apply` to manufacture fresh-looking evidence;
- treating 91 named roots as a reachable typed schema graph;
- treating current source classes as certification.

## 8. XLIFF Batch 005 contract

When its paths become safely ownable, resume the same task rather than
starting a replacement:

1. preserve the 25 existing source-bound obligation rows;
2. add rejection controls for forged normalized text, source/member digests,
   and occurrence locations;
3. bind explicit candidate classes and content-sensitive occurrence digests;
4. classify all non-modal Core prose excluded by Batch 004;
5. replace all 78 coarse structural dispositions with exact mappings or
   source-located reasoned non-obligations;
6. expand the 105-ID denominator for newly exposed semantics;
7. compile source-bound obligations for every resolved expected ID;
8. retain `complete: false` until authority census, expected-ID closure, and
   canonical SAL verification are all complete.

Batch 004 facts that must not be weakened:

- 542 selected candidates;
- 182 prose, 264 XSD, and 96 Schematron candidates;
- zero unmapped or multiply dispositioned candidates within its declared
  selector;
- 25 source-bound rows, 80 expected IDs still missing;
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
- duplicate Event 27 serialization;
- a provider reusing another provider's identity;
- a packet that cites GitHub or a non-main branch;
- a packet that labels historical open conflicts as a clean coordination
  plane.

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
