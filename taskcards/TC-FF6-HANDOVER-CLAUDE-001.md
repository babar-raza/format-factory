---
artifact_id: TC-FF6-HANDOVER-CLAUDE-001
artifact_type: taskcard
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
goal_id: FF6-PRODUCTION-LIBRARIES-001
status: COMPLETE
skill_ids:
  - refresh-provider-neutral-handover
  - create-taskcard
  - plan-control
---

# Publish a Provider-Neutral Claude/Codex Shift Handover

Status: `COMPLETE`

## Objective

Create a single-entry, evidence-backed, machine-readable handover that lets
Claude and Codex resume the FF6 mission from GitLab main without conversation
memory, provider-local state, lost work, duplicate execution, or false product
promotion.

## Allowed paths

- `plans/codex/handover/**`
- `plans/strategic/ff6/controller-state.yaml`
- `plans/strategic/ff6/events.jsonl`
- `taskcards/TC-FF6-PROGRAM-CAPABILITIES-001.md`
- `taskcards/TC-FF6-AUTHORITY-CLOSURE-001.md`
- this taskcard
- `taskcards/index.yaml`
- local task transcript and evidence metadata

## Acceptance

- One start file links every handover artifact and canonical authority.
- Exact commit, tree, controller event, next task, and evidence limits are
  recorded.
- Symptoms, root causes, structural weaknesses, preservation requirements,
  redesign direction, risks, and uncertainty are separated.
- Start, execution, checkpoint, takeover, validation, integration, and release
  procedures are provider-neutral and executable.
- The absent next taskcard is materialized as `READY`.
- Known global plan-control and line-ending digest contradictions are explicit.
- All internal links, YAML, normalized hashes, event chain, task index, and
  focused regression checks pass.
- Files are committed and pushed to GitLab main with remote verification.
- No product implementation or promotion occurs.

## Initial closure

The packet was integrated and remote-verified at
`1f215cc7ba0ce36225ae8bbc49678b3ca0d5d8fd`. The closing controller event
records the final packet and task-index digests. This task changes no product
promotion state.

## Refresh checkpoint

The packet was refreshed after `TC-FF6-AUTHORITY-CLOSURE-001` passed.
Controller event 16 records 15 of 15 live authority matches, strict
six-contract compilation, clean online and offline replay, deterministic
six-format projections, and no product promotion. The exact successor is
`TC-FF6-ORA-PROFILE-SURFACE-001` in `READY`.

The packet remains a derived navigation and shift artifact. The fetched
GitLab `origin/main` commit, native FF6 journal, controller, task index,
current gaps, and taskcard supersede every earlier packet revision and the
initial integration commit above.

## Event-19 refresh checkpoint

The packet was rebuilt from the remote-verified NRRD source checkpoint
`865558bb88243acda08c2a8d58a0d5ec887dedeb`.

- Native journal head:
  `FF6-EVENT-000019` /
  `76b580d72f865428e92bc5b6089a89487356c69163aadf6b615b70c6867221f8`.
- `TC-FF6-NRRD-PROFILE-SURFACE-001` is `PASS`.
- The current planning denominator is 110 capabilities and 672 obligations;
  NRRD owns 21 capabilities and 65 exact-profile obligations.
- All 15 predecessor authority records match.
- No product, package, certification, promotion, release, or gate changed.
- The exact successor is `TC-FF6-XLIFF-PROFILE-SURFACE-001` in `READY`.
- The successor must first acquire a separately pinned official XLIFF 2.0
  Standard package; the existing XLIFF 2.1 authority cannot stand in for it.
- Core and all eight official XLIFF 2.1 modules must receive separate, exact
  normative capability ownership. The pinned bundle has nine module schema
  vocabularies because ITS uses both `its` and `itsm`; Format Style and ITS
  were missing from the earlier six-module wording. The Change Tracking
  extension is informative and cannot count as a normative module. XLIFF 2.2
  is preview-only and XLIFF 1.2 is outside the 2.x model.

## Event-19 standards correction

The prior event-19 packet was structurally valid but contained an incomplete
XLIFF module enumeration. This refresh corrects the task and every handover
projection without changing event 19, the controller, the capability
denominator, product source, certification, promotion, release, or gates.
The correction is proven from the hash-matched `SRC-XLF-002`/`SRC-XLIFF-001`
XLIFF 2.1 authority bytes, not from current product code.

This refresh replaces every event-18/NRRD-as-next statement in the packet,
recomputes normalized hashes, and preserves the same provider-neutral,
GitLab-main-only, atomic-shift contract.

## Event-21 XLF-03 microstep refresh

The packet was rebuilt after a tested XLF-03 implementation slice was committed
at `a1316b4fae21c20c71ccb6d60e4b9fe634dca573` and bound to
`FF6-EVENT-000021` /
`3e83a764c53da658cb1dd348ed20d041db850f1cef45bec5eaa5637ccafecc11`.

- The active task remains
  `TC-FF6-XLIFF-PROFILE-SURFACE-001` / `WORK_IN_PROGRESS`.
- `XLF-01` and `XLF-02` are complete; `XLF-03` is still first unmet.
- The nested XLF-03 microstate is `GREEN_VERIFIED_CHECKPOINTED`.
- The digest-bound authority reader, Core/module inventories, section delta,
  source-row validation, canonical YAML, atomic write, and drift check
  primitives are committed and covered by 3 passing tests.
- Ruff, strict Mypy, and bytecode compilation pass. Pyright was unavailable in
  the checkpoint shell and is not claimed.
- The exact next RED test is
  `test_cli_writes_and_checks_default_xliff_matrix`.
- The CLI/default curated seeds, complete negative suite, real matrix, and
  three-run real-authority replay remain.
- The packet now defines a nested TDD/provider-shift state machine and a
  two-commit checkpoint protocol so a provider switch never depends on chat or
  an unjournaled source commit.
- No product source, certification, promotion, release, or gate changed.

## Cross-provider shift hardening refresh

The packet was re-audited from clean, fetched GitLab `main` at
`b6aef60c12368753939e75f88951a6f4d3533e76` without changing the FF6
controller or product task.

- The provider transfer is now explicitly one-writer-at-a-time for the active
  task. The outgoing identity completes after remote verification; the
  incoming provider registers a new identity and never inherits a token or
  lease.
- Planned token exhaustion is handled only at a `RESUMABLE` boundary. RED-only,
  unjournaled, and local-only states are not clean checkpoints.
- Crash recovery now distinguishes implementation-only commits, journaled but
  stale projections, owned GREEN/RED worktrees, unattributed dirt, and remote
  overlap.
- The XLIFF evidence denominator is disambiguated: the official 2.0/2.1 prose
  contains 293/420 total DocBook sections, of which 197/312 have direct IDs.
  ID-less sections remain in the matrix through deterministic title paths.
- The exact continuation remains the same XLF-03 RED test. No canonical
  taskcard, source, test, authority, contract, controller, promotion, gate, or
  release state changed.

## Event-24 XLF-04 batch-002 checkpoint refresh

The packet was rebuilt from immutable implementation commit
`78660ae1a310ab06cf00d977bbc26fb65914f1c9` and native event
`FF6-EVENT-000024` /
`10d96a6729d250fecb89f5f082682f583b5b8053fd620702dcd837dfaf541434`.

- `XLF-01`, `XLF-02`, `XLF-03`, `XLF-04-BATCH-001`, and
  `XLF-04-BATCH-002` are complete; `XLF-04` remains first unmet.
- XLF-03 now includes deterministic default anchors, CLI/check mode, declared
  archive/XML/matrix negative controls, and a real pinned-authority matrix.
- The matrix has 36 unique source-surface anchors, 293/420 sections, 8/8
  modules, and 8/9 schema vocabularies for XLIFF 2.0/2.1.
- Three real-authority generations are byte-identical at SHA-256
  `9f4ea4b8b71378217af26c0fb2b97a759817a0aca6c64255b8cd55170c60a090`.
- Eighteen focused tests, Ruff, strict Mypy, Pyright 1.1.411, bytecode
  compilation, and zero-warning receipt validation pass.
- The 36 rows are coarse source-surface anchors, not complete semantic
  obligations. XLF-04 must compile full Core semantics; XLF-05 must compile
  every module as a first-class capability family.
- Batches 001-002 add 19 source-bound obligations covering ten categories,
  but they remain `SOURCE_BOUND_UNVERIFIED`; two categories and the explicit
  expected-obligation ID denominator remain. Category presence cannot close
  XLF-04.
- The mission remains in `CONTRACT`, the active task remains
  `WORK_IN_PROGRESS`, the parent remains `NEEDS_REPAIR`, product certification
  remains 0/6, and every promotion remains `UNASSESSED`.
- At the historical event-24 boundary, the exact continuation was
  `XLF-04-BATCH-003`: RED tests for source-located
  semantic roundtrip/canonical output and XML security/resource limits plus an
  explicit expected-ID denominator after replaying event 24 and its bound evidence.

## Event-24 provider-shift truth refresh

The provider-neutral packet was re-audited from clean GitLab `origin/main` at
`df727a916ffac7ff028cd087adea7f1055652b8d`.

- All 50 LF-normalized manifest hashes, 24 native FF6 event links/hashes, and
  packet-internal links were recomputed successfully before this refresh.
- Two derived machine records and this taskcard still carried isolated
  batch-001-only wording even though the controller, journal, active
  checkpoint, and manifest correctly recorded batch 002. Those stale
  statements are corrected without changing the native event head, task
  state, product source, proof, certification, gate, or promotion.
- Coordination completion is now modeled as a resume-time off-repo
  precondition, not a durable boolean that this tracked packet could continue
  to prove after commit. Provider identities, tokens, and leases are never
  transferred.
- At that historical refresh, the exact continuation remained
  `XLF-04-BATCH-003`; event 25 below supersedes that continuation.

## Event-25 clean checkpoint refresh

The batch-003 recovery boundary has been reconciled without loss:

- GitLab `origin/main` contains READY UBL taskcard commit `210c1383`,
  XLIFF implementation commit `25227527`, and event/controller checkpoint
  commit `220ee7f5`.
- Event `FF6-EVENT-000025`, controller sequence 25, active taskcard, and
  plan-control receipt agree.
- Batch 003 contains six exact implementation/evidence paths, two valid skill
  transcripts, 25 cumulative source-bound obligations, and a 105-ID open
  denominator with 80 unresolved IDs.
- Independent replay in the handover refresh observed 27 focused tests,
  94 format-contract tests with the baseline-known CSV test deselected,
  69 production-program tests, Ruff, strict Mypy, bytecode compilation, and
  5/5 XLIFF authority matches. Pyright was unavailable in the refresh shell;
  the batch receipt records Pyright 1.1.411 passing.
- XLF-04 remains incomplete, 0/6 products are certified, and all promotions
  remain `UNASSESSED`.

The exact continuation is `XLF-04-BATCH-004`: compile a deterministic Core
authority-candidate census across direct/leaf normative prose, Core XSD
constraints, Core Schematron assertions, and exact 2.0/2.1 deltas. Map every
candidate exactly once to an expected obligation ID or a reasoned
non-obligation disposition. Reject unmapped and duplicate candidates; retain
`complete=false`. Exact hashes and the resolved recovery history are retained
in `plans/codex/handover/INFLIGHT-RECOVERY.yaml`.

## Event-26 provider shift

The current compact resume packet is
`plans/codex/handover/event-26/START-HERE.md`, bound to GitLab checkpoint
`15ab7d04`, event 26, and implementation `1fef79b9`. Historical event-25
packets remain immutable. The semantic validator now loads the versioned
event-26 checkpoint and derives the expected batch from the native event.

Independent negative controls found that the standalone census validator
accepts forged normalized requirement text, member/source digests, and
occurrence location. The packet makes those bindings plus explicit candidate
class and content-sensitive candidate digest the first RED controls of batch
005. XLF-04 remains open, certification remains 0/6, and all promotions remain
`UNASSESSED`.

## Event-25 semantic consistency repair

The event-25 packet's 61 LF-normalized file digests and links were valid, but
that structural check did not detect four semantic projection defects:

- the active checkpoint and starting-defect projection omitted completed
  `XLF-04-BATCH-003`;
- historical event-24/24-test evidence was described as current;
- the Claude instruction named an immutable batch-002 RED receipt as the
  destination for new batch-004 evidence;
- “six files plus two transcripts” ambiguously double-counted a six-file set
  that already contains the two transcripts.

The repair preserves all historical evidence and adds the read-only
`plans/codex/handover/validate_handover.py` control. It derives active
semantics from the latest native event, checks every handover projection,
validates the event hash chain, manifest digests, local links, and GitLab
ancestry, and carries negative controls for a missing batch, stale next batch,
wrong event head, and predecessor-as-current wording. This repair changes no
product, controller, task, gate, certification, or promotion state.

## Event-26 provider-neutral refresh

The hardened packet is refreshed from GitLab `origin/main` handover source
checkpoint `18bb295f94e43338611ef88caff073eed17411c9`; native Event 26 remains
bound to controller commit `15ab7d0455e109bd88289e16d73c0835324a21ab`.

- Native event `FF6-EVENT-000026` and controller sequence 26 agree.
- XLIFF implementation checkpoint `1fef79b9` and Batch 004 are committed,
  pushed, and journaled.
- Batch 004 reconciles 542 candidates in its declared modal-prose, Core XSD,
  and Core Schematron selector with zero unmapped or multiply dispositioned
  candidates.
- Non-modal prose remains unclassified; 78 dispositions remain coarse; only
  25 of 105 expected IDs have source-bound obligations and 80 remain missing.
- All current obligation rows remain `SOURCE_BOUND_UNVERIFIED`.
- The exact successor is `XLF-04-BATCH-005`; XLF-04 remains incomplete.
- The root packet and immutable `event-26/` packet are provider-neutral and
  require no local identity, lease, branch, or conversation memory.
- Product source, product proof, certification, promotion, release, and gate
  state are unchanged. Production certification remains 0/6.

## Event-27 cross-provider checkpoint

The current root packet and immutable `event-27/` packet are rebuilt from
GitLab checkpoint `59ef8ee2e1b4e37168e4c7094687fac0a6098a79`.

- Native Event 27 and the controller agree at hash
  `9a1783b0705468fec1e9f9fda96f61ab4b1da32a161d128a3120a8bf689686c2`.
- XLIFF remains canonical-active at `XLF-04-BATCH-005`.
- UBL-01 and UBL-02 are serialized as `PACKAGE_CENSUS_COMPLETE`;
  `UBL-03` is first unmet.
- The UBL evidence binds three matching authorities, 34 verified SAL facts,
  890 package members, and exactly 91 document roots.
- The capability aggregate is
  `e199e84e9f7ee0579959db28283ecb89e014077cdd1605fbf0c82aee553d9960`;
  the three-run digest is
  `eafd6f8657ed83b73dbd5975046698d24fda6d8fd58c3d6aea962e6b6a85cf7c`.
- If the foreign XLIFF working set is still live-owned, the safe disjoint
  fallback is UBL-03. Event 27 must not be appended again.
- The handover validator understands parallel-task events, binds 69 current
  packet files, verifies the complete native chain, and rejects eleven
  semantic corruptions.
- Five dirty XLIFF Batch 005 paths remain foreign work and are excluded from
  every handover/controller commit.
- Product source, certification, promotion, release, and gate state are
  unchanged. Production certification remains 0/6.

## Final Codex-to-Claude shift refresh

At `2026-07-29T21:08:29Z`, GitLab `origin/main` and local `HEAD` matched at
`0b69bddb8faab010d9d064d75655564a67ddca4a`. The 70-file handover validator,
complete Event 27 chain, and eleven semantic negative controls passed.

No product or controller work advanced. Five XLIFF Batch 005 paths remained
foreign dirty state; their owner and eleven leases were still reported
`ACTIVE`, while the recorded process was absent and the observation was close
to the lease TTL boundary. Claude must register a new identity and requery
coordination. It resumes XLIFF only after safe release or governed stale
takeover; otherwise it executes UBL-03 under disjoint leases. Certification
remains 0/6 and all promotions remain `UNASSESSED`.

## Event-30 clean provider-neutral checkpoint

Event 30 supersedes all earlier operational resume paragraphs while preserving
them as history. XLIFF Partial-002-A is committed and pushed to GitLab `main`
at `e13e103de0bb789ff51a8e931af0fb649474be20`; there is no local-only product
overlay.

- Native journal head: `FF6-EVENT-000030`.
- Controller remains `CONTRACT`.
- Active task remains `TC-FF6-XLIFF-PROFILE-SURFACE-001` /
  `WORK_IN_PROGRESS`.
- Exactly 1 of 1,130 candidate dispositions is independently verified.
- Exactly 26 of 105 expected Core obligation rows are source-bound; 79 remain
  missing.
- XLF-04, all product implementations, certification, promotion, release, and
  gates remain incomplete or unchanged.
- Exact next microstep:
  `XLF-04-BATCH-005-PARTIAL-002-B`.
- Exact next candidate:
  `XLF-CAND-CORE-SCHEMATRON-00C4A041AF12C8A1`.

The incoming provider must start at
`plans/codex/handover/START-HERE.md`, validate the Event 30 packet, register a
fresh coordination identity, replay immutable check modes, and begin the new
candidate with a failing independent-adjudication test. Provider credentials,
leases, manifests, and uncommitted assumptions are never transferred.

## Event-30 deep resume audit

A later read-only authority and source audit hardened the successor
instructions without advancing the native controller or product state.

- The selected rule's direct denominator owner is
  `SAL-XLIFF-CORE-INLINE-PAIRING-001`; the generated proposal omits it.
- The current adjudicator incorrectly makes the generated proposal set an
  upper bound on accepted truth. It must separate proposal accountability from
  independently discovered denominator ownership.
- The reverse pair direction is separately pinned as
  `XLF-CAND-CORE-SCHEMATRON-4BE479DD3F5875EF`, digest
  `246f6e9e4c64fe142760045dbca69070405ae50f552b34387ce8709c3c7226e3`,
  at `schematron/rule[46]/assert[2]`.
- `SAL-XLIFF-00005` does not yet bind either exact pair assertion in its
  evidence manifest.
- The exact pair assertions were found in the pinned XLIFF 2.1 Schematron.
  The pinned XLIFF 2.0 XSD and prose define both attributes, but this audit did
  not find the same must-be-used-in-pair rule. The implementation must locate
  separate 2.0 authority or narrow this obligation to 2.1.
- The extractor must retain candidate-to-obligation provenance and require
  both reciprocal candidates before compiling a bidirectional pairing row.

These are `READ_ONLY_FINDING_NOT_YET_IMPLEMENTED`. They do not change the
Event 30 counts, hashes, task state, promotion state, or certification state.
The executable details and negative controls are in
`plans/codex/handover/NEXT-MICROSTEP.yaml`.

## Event-34 provider-neutral shift checkpoint

The packet is refreshed from immutable GitLab implementation commit
`8e61ee11e7598b22093d397f4006d4f189b681d4` and native
`FF6-EVENT-000034` /
`7cab150d9d49deeba140c6a0ce56e619ae560f8b0abc7510e555ca54d6f307da`.

- The selected task is still XLIFF
  `XLF-04-BATCH-005-PARTIAL-002-C`; the accepted boundary remains 27/105
  obligations and 3/1,130 candidate dispositions.
- Seven XLIFF occurrence paths remain preserved, hash-bound, and
  non-promoting. The attempted governed takeover was denied because the lease
  was still `ACTIVE`; no path was overwritten or released.
- The disjoint UBL fallback completed
  `UBL-03-PARTIAL-004-ANONYMOUS-TYPE-IDENTITY`.
- Stable anonymous simple and complex type identities are derived from exact
  authority paths. Invalid explicit-plus-anonymous and multiple-anonymous
  declarations fail closed.
- The official UBL 2.3 package contains zero anonymous declarations. The
  implementation is therefore proved with adversarial schemas and a
  zero-count authority census, not a false claim of official-corpus coverage.
- Twenty-eight focused tests, 69 production-program regressions, Ruff, strict
  Mypy, Pyright 1.1.411, bytecode compilation, and three identical graph runs
  pass.
- The next disjoint UBL fallback is
  `UBL-03-PARTIAL-005-DERIVATION-AND-INHERITANCE-EDGES`.
- UBL-03, XLF-04, all six production certifications, promotion, release, and
  gates remain open or unchanged.

The packet remains derived. Every incoming Claude or Codex shift starts at
`plans/codex/handover/START-HERE.md`, validates fetched GitLab main in a
detached worktree, registers a fresh coordination identity, and never
inherits prior leases, tokens, manifests, or uncommitted claims.

## Event-35 provider-neutral shift checkpoint

Event 35 supersedes the Event 34 operational routing while retaining Event 34
as verified UBL history.

- The seven inherited XLIFF paths were governed-taken-over, independently
  replayed, committed, and pushed without discarding any bytes.
- Immutable XLIFF implementation:
  `591fcfe18808e5195c33570eaa9d334770e90166`.
- Native head: `FF6-EVENT-000035` /
  `2866d7e70bd193f8aa7b60ca1f92f4f842d1cd470f97984c07f47d88ed2ea97d`.
- Accepted XLIFF boundary: 28/105 Core obligations, 77 missing; 4/1,130
  candidate dispositions verified, 1,126 open.
- Completed microstep: `XLF-04-BATCH-005-PARTIAL-002-C`.
- Exact successor: `XLF-04-BATCH-005-PARTIAL-002-D`, candidate
  `XLF-CAND-CORE-SCHEMATRON-8D50B407E90E354E`.
- The successor must independently adjudicate the reciprocal skeleton report,
  start with a genuine RED test, preserve all 28 accepted rows, and must not
  duplicate the already compiled biconditional obligation.
- UBL partial-005 was independently committed as `d8c10680` and checkpointed
  as `ae31baed`: 1,178 exact derivation edges and identity `783506c4...`.
  Its executor completed cleanly before packet seal. The next provider still
  registers a fresh identity, re-queries coordination, and replays both
  commits before entering partial-006.
- XLF-04, UBL-03, all six product certifications, promotion, release, and
  gates remain incomplete or unchanged.

This taskcard, the packet, and the refresh receipt record a transfer
checkpoint only. They do not certify any product or authorize publication.

## 2026-08-01 clean-replay repair handover

GitLab `main` now contains reciprocal skeleton implementation attempt
`2dcb161ed8e53bfc55e5be81374f5f7ddea3bb17`. The shared worktree passed 71
affected tests, 43 production-program tests, 94 format-contract tests with the
one documented stateful CSV deselection, three deterministic generations,
predecessor preservation, static checks, SAL verification, five authority
matches, and zero-warning implementation transcripts.

The attempt is non-promoting. A clean detached Windows checkout failed 5/71
affected tests at `canonical SAL manifest digest is stale`. The same tracked
proof files received different raw SHA-256 values after LF/CRLF checkout
conversion because `.gitattributes` has no EOL rule while SAL proof consumers
bind raw worktree bytes. This is a live manifestation of
`FF6-GAP-011/FF6-HO-GAP-003`.

The provider-neutral packet was refreshed without changing the native
controller. Event 35 remains the last accepted event; accepted XLIFF state
remains 28/105 obligations, 77 missing, 4/1,130 dispositions, XLF-04
incomplete, and 0/6 certified.

The exact successor is
`XLF-04-BATCH-005-PARTIAL-002-D-REPLAY-REPAIR-001`. The incoming provider must
start at `plans/codex/handover/START-HERE.md`, read
`plans/codex/handover/CLEAN-REPLAY-REPAIR.md`, register a fresh identity, add a
clean-checkout RED regression, and establish one repository-wide tracked-text
digest invariant through a registered machinery skill or the governed
missing-skill workflow. It must preserve `2dcb161e` and may accept
PARTIAL-002-D only after the committed clean Windows replay passes.

## Event-38 cross-provider checkpoint refresh

This refresh supersedes every earlier operational resume paragraph while
retaining them as audit history.

- Accepted XLIFF semantic commit:
  `3fc939ad70ec6caac9e0699041076e02de00c5d2`.
- Accepted controller checkpoint:
  `d1f8b3229bf3be32675e047b1469259ad7375500`.
- Native authority: `FF6-EVENT-000038` /
  `13db4cceafcefb86d9c964d7c3e20e7d63092977faf50002ef0c88ea4f6b5603`.
- Accepted XLIFF boundary: 7/1,130 independently verified candidate
  dispositions and 30/105 source-bound Core obligations; 1,123 dispositions
  and 75 obligations remain open.
- The semantic slice accepts only the XLIFF 2.1 source-language compatibility
  owner, excludes XLIFF 2.0, and includes a tested transactional exact-ID SAL
  seeding repair.
- Ninety affected tests passed in the shared worktree and immutable detached
  checkout; 69 production-program and 94 format-contract tests passed with the
  one exact baseline-known stateful CSV deselection.
- All 32 XLIFF SAL facts, five authority locks, four deterministic artifact
  checks, Ruff, strict Mypy, Pyright 1.1.411, py_compile, semantic transcripts,
  and native plan-control tests passed.
- Product source, certification, promotion, release, and gates did not change.
  Every product remains `UNASSESSED`; certification remains `0/6`.

The exact successor is `XLF-04-BATCH-005-PARTIAL-002-G`, candidate
`XLF-CAND-CORE-SCHEMATRON-5D563A565DC6DCFE`. The incoming provider starts from
`plans/codex/handover/START-HERE.md`, validates fetched GitLab `origin/main`,
registers a fresh coordination identity, obtains new leases and mutation
authorizations, and independently adjudicates target `xml:lang` versus root
`trgLang`. It must preserve all 30 predecessor rows and all 1,130 candidate
identities. Source-language symmetry and generated proposals are context, not
proof.

The outgoing provider identity, token, leases, local execution manifests, and
mutation authorizations are deliberately not transferable. A shift is complete
only after the refreshed packet is validated, committed, pushed to GitLab
`main`, remote equality is proved, and the outgoing provider releases only its
own leases.
