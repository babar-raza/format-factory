---
artifact_id: FF6-HANDOVER-STATE-AND-CAUSES-001
artifact_type: agent_handover_analysis
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
authoritative_state: false
historical_projection: false
---

# Current State, Root Causes, and Structural Weaknesses

## 2026-08-01 verified live overlay

GitLab `origin/main` is verified through controller checkpoint
`de569544eebc1fff011901e61d3574dcc48e5e08`. Native authority is
`FF6-EVENT-000040`; accepted and materialized XLIFF evidence agree at 9
verified and 1,121 open dispositions. Obligation coverage is 31/105 with 74
missing. The exact next task is `XLF-04-BATCH-005-PARTIAL-002-I`, an
independent authority-adjudication microstep for
`XLF-CAND-CORE-SCHEMATRON-60B596A00F7FA06A`.

The deeper replay investigation found that the visible stale-manifest error
was caused by workstation-dependent byte identity: mixed CRLF/LF manifest
bytes and CRLF proof-tool copies were hashed in the shared tree, while Git
materialized LF in a clean checkout. Commit `809cc18c` establishes declared LF
identity for proof/source text, preserves byte-sensitive fixture classes, adds
44 negative/positive checkout controls, and regenerates only invalidated
current descendants. A clean Windows/autocrlf replay passed 115 affected
tests, 69 production-program tests, and 94 format-contract tests with one exact
known stateful deselection. This closes the bounded replay defect but does not
certify a library.

Semantic commit `1b758c2e` independently adjudicates the unit-cardinality
report, `3fc939ad` adjudicates source-language compatibility, and `39b2e89f`
resolves target-language profile semantics. Semantic commit `d95af5ae` then
binds the stable start-code isolation biconditional to one direct obligation,
with source-side executable evidence. Event 40 projects that result without
changing product or promotion state.

The production-level lesson is that repeatability cannot be achieved by
refreshing a receipt in the current workspace. Durable state requires one
authority graph, explicit input identity, immutable replay before acceptance,
separate accepted/materialized projections, bounded transactional mutation,
and a hash-chained event that makes each transition auditable. Events 36-40
advance only independently proven semantic obligations and retain prior
failures as negative controls.

> **Current authority overlay: Event 40.** Native head
> `FF6-EVENT-000040`. Event 31 remains the negative
> control proving that deterministic mechanical evidence can encode the wrong
> semantic owner and profile. Event 36 accepts the repaired reciprocal XLIFF
> skeleton checkpoint at 28/105 obligations and 5/1,130 dispositions; Event 37
> accepts unit cardinality at 29/105 and 6/1,130; Event 38 accepts the XLIFF
> 2.1 source-language boundary at 30/105 and 7/1,130; Event 39 corrects
> target-language profile semantics at 30/105 and 8/1,130; Event 40 binds
> start-code isolation at 31/105 and 9/1,130. Event 34
> separately binds 6,001 UBL local particle nodes without changing promotion.
> This file explains causes and redesign
> direction; executable state comes only from
> [START-HERE.md](START-HERE.md),
> [CURRENT-MACHINE-STATE.yaml](CURRENT-MACHINE-STATE.yaml), the native
> journal, and [NEXT-MICROSTEP.yaml](NEXT-MICROSTEP.yaml).

The failure described by the historical text below is now repaired and kept as
a negative-control case. Current executable state comes from the live overlay,
[CLEAN-REPLAY-REPAIR.md](CLEAN-REPLAY-REPAIR.md), and
[NEXT-MICROSTEP.yaml](NEXT-MICROSTEP.yaml).

## Executive truth

The FF6 mission has a durable goal, deterministic contract compiler, locked
authority dependency plane, hash-chained controller, current gap projection,
and a provider-neutral resume protocol. Events 16-19 closed authority,
OpenRaster, IPYNB, and NRRD contract prerequisites. Events 20-30 advanced
XLIFF authority/profile work through a complete 1,130-candidate Core census
and advanced UBL through its first root/type graph primitive.

It does not yet have a production-ready library. Five formats have existing
implementation footholds of uneven depth. OpenRaster has no product package.
All 672 compiled obligations are planning requirements, not verified behavior.
The XLIFF census has six independently verified semantic dispositions and
1,124 still open. All six promotion states are `UNASSESSED`.

## Product depth actually present

| Format | Existing foothold | Material depth still missing |
|---|---|---|
| IPYNB | Typed notebook/cell/output models, codec, validation, conversion, cleanup, trust inspection and editing; exact 4.0-4.5 contract surface now compiled | Independent oracle depth, installed-wheel and matrix proof, architecture cleanup, complete obligation execution |
| OpenRaster | Three locked authorities, 20 exact SAL facts, dedicated layered-raster family, 20 capabilities and 134 profile-scoped obligations | Entire product package, corpus, application interoperability, rendering implementation, security implementation, package and certification proof |
| NRRD | Header/payload codec, attached/detached entry points, encodings, preservation and limits; exact five-profile contract now compiled | Stronger typed spatial model, streaming/mmap proof, Teem and pynrrd differential depth, package/certification proof |
| XLIFF | Core model, inline editing, segmentation/state helpers and preservation; independently pinned 2.0/2.1 authorities and deterministic source-surface matrix | Fine-grained 2.0/2.1 Core semantics, all eight official 2.1 modules across nine module schema vocabularies, processing requirements, schemas/oracles, package/certification proof |
| SafeTensors | Typed descriptors, strict layout checks, mmap/region access, writer and adapters | Full dtype/edge/sharded coverage, upstream differential corpus, co-installation and multi-platform package proof |
| UBL | 91 root subclasses, ordered generic XML model, extensions and signature handling | Fully schema-typed common components, cardinality/order API, reproducible generator proof, all-root examples, independent XSD engine and package proof |

These statements describe observed code breadth, not certification.

## What events 16 through 22 added

- Event 16: one canonical 15-source authority lock; legal, locator, digest,
  cache, and materialization policy; content-addressed online/offline replay;
  strict ProductContract authority verification; complete authority
  invalidation closure; six regenerated contracts; and nonpromotion for
  diagnostic overrides.
- Event 17: current OpenRaster RST authority assertions, explicit draft
  uncertainty, the `layered_raster_archive` capability family, 20
  format-specific capabilities, 134 obligations, and exact 0.0.3/0.0.4/0.0.5
  applicability. Isolation is correctly limited to 0.0.4/0.0.5 and masks are
  treated as a product extension rather than a draft baseline claim.
- Event 18: exact nbformat 4.0-4.5 schema member hashes and a 62-leaf delta
  matrix; 25/25 exact SAL facts; explicit-complete fact ownership; 25
  profile-homogeneous capabilities and 68 obligations; exact introduction
  profiles for names, document metadata, hidden metadata, execution timing
  and cell IDs; retained no-execution exclusion; and deterministic
  six-format replay.
- Event 19: a source-located NRRD0001-NRRD0005 delta; 25/25 exact SAL facts;
  18 scientific-raster domains and 41 policy IDs with explicit-complete
  ownership; a governed repair to a requirement that mixed NRRD0004 transforms
  and NRRD0005 measurement frame; 21 profile-homogeneous capabilities; 65
  obligations; all five profiles claimed; and deterministic six-format
  replay. Teem's permissive later-field parsing under earlier magic is retained
  as an interoperability peculiarity rather than normalized into strict
  conformance.
- Events 20-21: independent XLIFF 2.0 authority acquisition, exact 42-member
  2.0/2.1 package inventory, 5/5 XLIFF authority closure, and the first tested
  digest-bound matrix compiler slice.
- Event 22: deterministic default source-surface anchors, CLI/check mode,
  bounded authority XML support, fail-closed archive/XML/matrix controls, 18
  tests, and a three-run identical real-authority matrix at
  `9f4ea4b8b71378217af26c0fb2b97a759817a0aca6c64255b8cd55170c60a090`.
  XLF-03 is complete, while fine-grained Core and module semantics remain
  XLF-04 and XLF-05.
- Event 23: a typed fine-grained Core-obligation schema, exact
  source/member/section/paragraph digests, fail-closed profile and evidence
  declarations, seven real-authority obligations, and a tested rule that
  category presence cannot self-certify completeness. The report remains
  incomplete because its expected-obligation ID denominator is absent; five
  categories and canonical SAL reconciliation remain.

This removes a major rerun-consistency failure: `ACQUIRED` can no longer
survive as promoting evidence when the locked bytes are absent or changed.
It also removes the earlier generic-archive blind spot for OpenRaster. Neither
event implements product behavior.

## Current compiled denominator

The planning inventory contains 110 capabilities and 672 obligations:

- IPYNB: 68
- OpenRaster: 134
- NRRD: 65
- XLIFF: 125
- SafeTensors: 86
- UBL: 194

Assessment remains `NEEDS_PROFILE_OR_SURFACE_REPAIR`. The compiler currently
reports profile/surface follow-ups for XLIFF and UBL.
Counts cannot hide a mandatory missing profile or format surface.

The assessment file `current-state.yaml` predates event 20. Its product source
tree inventory is still useful because the five tracked product trees have not
changed at the source checkpoint, but its old contract hashes and 89/636
planning denominator are historical. This distinction is now machine-recorded
in `CURRENT-MACHINE-STATE.yaml`.

## Symptoms

1. Historical reports can say PASS after their input closure changed.
2. Public symbol and test counts are mistaken for format capability.
3. Generic format-family capabilities conceal omitted format behavior.
4. Shallow or implementation-derived oracles appear independent.
5. Source-tree imports can make package tests pass accidentally.
6. Generated class counts obscure untyped schemas or cardinality gaps.
7. Global queue selection can disagree with the FF6 task DAG.
8. Provider shifts can create two plausible resume points if work is not
   committed, journaled, and remote-verified.
9. Generic Plan Control rejects the FF6 event schema.
10. Shared worktrees and mutable ignored inputs can alter reruns.
11. XLIFF authority closure now exists, but the current SAL/capability
    projection still assigns only XLIFF 2.1 and collapses eight normative 2.1
    modules into one broad capability.
12. A coarse task step can remain unmet while several valid TDD microsteps have
    landed, so a journal that records only task-step completion cannot identify
    the exact provider resume point.

## Root causes

### Competing partial authorities

Contracts, SAL, registries, reports, package proof, oracle records, taskcards,
generic Plan Control, and FF6 controller each describe part of state. Without
a dependency-closed graph and one current projection, old outputs retain
unearned authority.

### Incomplete evidence identity

Legacy results do not consistently bind authority, source, tests, fixtures,
corpora, dependency locks, tools, environments, built packages, imports, and
oracles. Any unbound input can change while a result appears current.

### Presence substituted for behavior

Files, methods, exports, generated types, fixtures, and test names were allowed
to stand in for executed positive, negative, preservation, resource, and
interoperability behavior.

### Breadth compiled from underspecified contracts

Mechanical completeness cannot discover a capability never named. Generic
JSON, archive, binary, or XML templates therefore produce consistent but
shallow inventories unless each format first receives a source-located
semantic surface.

### Mutable execution context

Shared worktrees, source imports, editable fixtures, unlocked dependencies,
untracked authorities, and checkout line endings create different inputs
across apparently equivalent runs.

### Package architecture preceded final product contracts

Useful code grew before the stable public API, preservation semantics,
resource limits, optional dependency boundaries, performance budgets, and
compatibility policy were obligation-driven.

### Provider state existed outside durable state

Conversation memory and provider-local changes previously mattered. That made
handoffs depend on the outgoing agent. The correct resume key is remote commit
plus controller, journal, taskcard, proof digests, and coordination ownership.

The deeper consistency failure is a missing distinction between four kinds of
state:

| State kind | Durable authority | Transfer rule |
|---|---|---|
| Product/mission truth | GitLab commit, native event journal, controller, proof graph | Recompute; never copy from chat |
| Task progress | Taskcard, task index, first unmet criterion, immutable evidence | Resume the first unmet criterion |
| In-flight mutation | Coordination identity, leases, write journal, working-tree bytes | Finish, complete, or governably take over; never inherit credentials |
| Provider context | Chat history, model memory, token budget | Non-authoritative and disposable |

Prior handoffs sometimes preserved the fourth layer while underspecifying the
first three. The durable design does the opposite. The outgoing provider
publishes a remote-verifiable state transition and ends its ownership; the
incoming provider reconstructs from canonical bytes and obtains new
ownership. This is what allows Claude and Codex to alternate without merging
their internal narratives.

### Task and TDD state used different granularity

`XLF-03` describes a complete normative-matrix outcome, while implementing it
requires multiple RED/GREEN cycles. Recording only `XLF-03 incomplete` loses
which cycles are safely reusable; recording only a source commit loses the
governed task meaning and next acceptance criterion. This is why the previous
packet could truthfully say “start XLF-03” while the worktree already contained
a partially working extractor.

The durable correction is a nested microstate. A shift-safe event binds:

- the immutable implementation commit;
- exact source, test, and receipt digests;
- the focused/regression/static results;
- the unfinished parent criterion;
- the exact next RED test;
- no-promotion and unsupported/unavailable boundaries.

That event is followed by a derived packet commit and remote verification.
Neither chat memory nor an unjournaled Git commit is enough.

### Missing registered implementation paths hid machinery debt

The `ingest-spec-sal` registry and command named
`tools/spec/extract_sal_facts.py`, but the file did not exist. The visible
symptom was “XLF-03 has no matrix”; the underlying cause was that governance
could declare an execution path without verifying the implementation path,
entry point, tests, or idempotent behavior as one referential-integrity unit.
Event 21 repairs the first implementation slice, but the wider machinery still
needs a validator that fails any active registered skill whose implementation
path or executable contract is absent.

### Evidence denominators can be semantically ambiguous

The XLIFF prose exposes a concrete example. It contains 293/420 DocBook
`section` elements, but only 197/312 have direct IDs. A tool or agent that
labels the ID-bearing count as the section count can produce deterministic yet
incomplete output. The durable control is to name the denominator precisely,
retain ID-less sections through deterministic title-path locations, and test
both total and directly identified counts. More generally, every coverage
metric must state what population it counts; reproducibility alone cannot make
an underspecified denominator correct.

### Agent liveness and lease liveness can disagree

The batch-003 worker reached GREEN and committed, then its recorded PID
disappeared before the event/projection closeout initially became durable. A
separate governed worker later completed and pushed event 25 without rewriting
the implementation. During the gap, the coordination plane
moved the short agent heartbeat toward `STALE_SUSPECT`, but explicit file
leases use a much longer TTL and can remain `ACTIVE`. The visible symptom is
an apparently dead worker whose files still cannot be governably taken over.
The root cause is two independently expiring liveness models without a
dead-PID transition that makes explicit leases takeover-eligible while
preserving audit history.

Do not repair this by editing SQLite, transferring tokens, releasing another
identity's lease, or weakening preflight. The durable redesign is an audited
`OWNER_DEAD_LEASE_QUARANTINED` state: prove PID/session death, freeze the
write-journal and file hashes, require successor recapture, then atomically
transfer leases through `takeover --reason`. Until that machinery exists,
continue disjoint work and preserve all bytes. This incident is now closed at
GitLab checkpoint `220ee7f5`, but the machinery weakness remains.

### Content integrity does not prove semantic projection integrity

The event-25 handover manifest correctly rehashed every tracked packet file,
yet several derived sentences still described batch 002 or event 24 as the
current boundary. The visible symptom was a packet that passed content and
link checks while giving a successor conflicting instructions. The root cause
was that the validator proved byte identity, not agreement between the latest
native event and every active-state projection.

The durable control is `plans/codex/handover/validate_handover.py`. It derives
the event head, controller sequence, completed steps, next batch, and
26/105/79 denominator counts from the native journal; compares those semantics
with the manifest, checkpoint, and machine-state projections; verifies the
complete event hash chain, local links, LF-normalized manifest digests, and
GitLab ancestry; and rejects known predecessor-as-current language. Its
embedded negative controls prove that a missing batch, stale next batch,
wrong event head, or stale current-state phrase fails closed. Historical
predecessor evidence remains preserved and is relabelled rather than deleted.

Event 29 exposed a second instance of the same weakness: the handover
validator passed while two live-root documents still described Event 27 and a
foreign dirty XLIFF workspace as current. Their bytes matched the manifest;
their meaning did not match the journal. The validator must therefore bind
every live-root projection to the machine state and reject known stale-state
sentences, not merely validate the small set of primary projections.

The Event 30 transfer audit found the same structural class again: several
current operational documents still routed through the predecessor event,
obsolete commits, and a closed uncommitted-overlay recovery procedure. The
packet hash validator passed because it proved the stale bytes faithfully.
The Event 30 hardening adds a current-operational-document set, required
current markers, forbidden predecessor tokens, a seventh tamper control, and
a working `--self-test` interface. Historical event directories remain
immutable; only root instructions are required to describe the live boundary.

### Deterministic mapping is not independent semantic verification

The XLIFF candidate census is now source-authentic and reproducible, but its
disposition algorithm scans the complete semantic location and normalized
requirement with keyword rules. For Schematron candidate
`XLF-CAND-CORE-SCHEMATRON-B109E9507A685F90`, the actual assertion is that
root `trgLang` is required when target content exists. The generated proposal
also assigns hierarchy/cardinality obligations because `segment`,
`ignorable`, and `target` appear in the XPath context.

The visible symptom is over-broad obligation ownership. The root cause is
that proposal generation and validation share the same algorithm and there is
no separate, content-addressed adjudication authority. Replaying the proposal
three times cannot make it independent evidence.

The durable design is:

- retain generated dispositions as proposals;
- store independent adjudications separately, keyed by candidate, content,
  occurrence, authority, denominator, decision, and tool digests;
- record accepted and rejected obligation IDs with source-located reasons;
- derive verified counts only from valid adjudications;
- invalidate downstream obligation rows when any adjudication input changes;
- require discriminating tests for every contradiction class.

The first bounded implementation cycle is fixed in
`NEXT-MICROSTEP.yaml`. Mechanical copying into canonical SAL is prohibited.

### Independent adjudication is still constrained by generator recall

The deeper Event 30 handover audit found a second-order defect in the otherwise
correctly separated adjudication layer. The validator currently enforces:

```text
accepted IDs union rejected IDs == generated proposal IDs
```

The visible symptom is that the selected sub-flow pair assertion can only
accept one of the four IDs proposed by the keyword mapper. The direct
denominator owner, `SAL-XLIFF-CORE-INLINE-PAIRING-001`, is absent from that
proposal. The current code therefore rejects a semantically correct independent
decision.

The root cause is not the individual mapping. The proof model conflates two
different completeness conditions:

- proposal accountability: every proposed ID must be accepted or rejected;
- semantic correction: a reviewer may identify a valid denominator ID that
  the proposal missed.

The structural weakness is generator recall acting as a hidden upper bound on
verified truth. A deterministic proposal omission becomes impossible to repair,
so reruns are consistent but consistently incomplete. This is precisely the
kind of false stability that the proof graph is intended to prevent.

The durable invariant is:

- accepted IDs may be any current denominator IDs with valid SAL proof;
- every generated proposal ID is accepted or explicitly reasoned-rejected;
- accepted and rejected IDs do not overlap;
- the normalized artifact exposes accepted-but-unproposed IDs;
- candidate-family requirements can demand more than one exact authority
  occurrence before a bidirectional obligation compiles.

For this pair rule, candidate
`XLF-CAND-CORE-SCHEMATRON-00C4A041AF12C8A1` proves start-to-end presence and
candidate `XLF-CAND-CORE-SCHEMATRON-4BE479DD3F5875EF` proves end-to-start
presence. A set of verified obligation IDs loses that distinction, so the
extractor must retain candidate-to-obligation provenance and require both exact
candidate IDs.

### Profile claims currently outrun the exact pair authority

The denominator currently marks `SAL-XLIFF-CORE-INLINE-PAIRING-001` for both
XLIFF 2.0 and 2.1. The pinned 2.1 Schematron contains the two exact
mutual-presence assertions. A read-only scan of the pinned 2.0 package found
both attribute definitions in the XSD and prose, but no equivalent
must-be-used-in-pair assertion. This is evidence of a current proof gap, not
proof that 2.0 permits or forbids the combination.

The durable response is fail-closed: locate a separate pinned 2.0 normative
rule or narrow this exact obligation to 2.1. Reusing the 2.1 assertion for a
2.0 profile would make a cross-profile evidence edge that survives reruns but
has no authority basis.

`SAL-XLIFF-00005` also describes Schematron pairing without exact evidence
assertions for these two rules. Its claim, manifest predicates, receipt, fact
proof, and dependent adjudication digests must move together through the
registered SAL pipeline. Updating only the claim or only the downstream
inventory would recreate the competing-authority problem.

## What must be preserved

- All working source and tests, including characterization behavior.
- Correct stable IDs and source-located SAL facts.
- Official schemas, acquisition history, and authority legal records.
- Security limits, strict validation, preservation behavior, and useful
  optional adapters.
- Append-only event, gap, rollback, and coordination history.
- GitLab-main-only integration.
- PEP 420 namespace and independent package boundaries.
- Explicit unsupported, preview, and interoperability profiles.
- The tested event-21 extractor primitives and their RED/GREEN history; later
  work extends them rather than rewriting them without evidence.

## What must be redesigned

- Make the ProductContract and proof graph canonical; other status is derived.
- Derive task selection from current mandatory obligations and dependencies.
- Replace family-generic capability surfaces with format-specific surfaces.
- Bind every executed result to its complete input closure.
- Test built wheels in isolated environments, not source trees.
- Require licensed independent corpora and genuinely external oracles.
- Separate generated schema models from handwritten workflows and adapters.
- Compute promotion from live proof and revoke it on dependency change.
- Use fresh worktrees/containers for certification.
- Make provider shifts atomic, remote-verifiable checkpoints.
- Separate durable mission/task state from ephemeral coordination and provider
  context; never transfer provider credentials or leases.
- Add TDD microstates below task steps and bind them to immutable commits in
  the native journal.
- Validate active skill registry entries against implementation paths, command
  contracts, focused tests, and executable smoke checks.
- Give each inventory count a named semantic denominator and negative controls
  against silently dropping unlabelled or unknown content.
- Validate handover semantics against the latest native event, not only file
  presence, links, and content hashes; reject stale active-state projections.
- Separate generated semantic proposals from independently verified
  adjudications and make that separation part of the proof graph.

## Immediate repair order

1. Execute `XLF-04-BATCH-005-PARTIAL-002-B` from the exact candidate and RED
   controls in `NEXT-MICROSTEP.yaml`. Extend the independent adjudication
   layer, reject incidental hierarchy overmapping, and retain XLF-04
   incomplete until all 1,130 dispositions, 105 expected IDs, and source-bound
   obligations close through canonical SAL.
2. Compile exact per-module applicability with isolated
   2.2 preview semantics.
3. UBL all-root/common-component typing contract.
4. Production package chassis and architecture only after contract readiness.
5. SafeTensors and IPYNB implementation/certification waves.
6. NRRD and OpenRaster implementation/certification waves.
7. XLIFF full vocabulary and processing semantics.
8. UBL generator and all-root typed certification.
9. Repository extraction, reproducible packaging, SBOM, provenance, and
   release preparation.

The controller, not this prose ordering alone, selects each exact task.

## Tradeoffs and limits

- Strong authority locking increases cache size and maintenance when upstream
  standards move; it is necessary for replay.
- Exhaustive format contracts take longer before code writing, but prevent
  repeated shallow rewrites.
- OpenRaster can earn named interoperability certification, not a defensible
  universal-conformance claim.
- UBL schema typing will generate substantial checked-in source; generator
  determinism and reviewable layering are mandatory.
- Independent corpora can be legally or operationally difficult to obtain.
  Synthetic fixtures may supplement but never replace them.
- Cross-platform Python 3.11-3.14 proof is expensive and belongs to nightly and
  release tiers, not every small contract task.
- Gate 10 and business/legal publication authority remain external boundaries;
  technical release preparation must still finish autonomously.
- The generic Plan Control compatibility gap remains open. Native FF6 chain
  validation is the safe interim authority, not a permanent second truth.
- Microstep journaling creates more commits, events, hashes, and receipts. The
  cost is additional integration ceremony; the benefit is exact crash/token
  recovery and removal of provider-memory dependence. It should be applied to
  code-producing substeps, not every read-only command.
- A two-commit shift checkpoint briefly leaves local main ahead between the
  implementation and packet commits. Coordination leases and a final atomic
  GitLab push reduce, but do not eliminate, remote-race risk; every shift must
  fetch before both commits and before push.

## Confidence boundary

Confidence is high in the predecessor authority closure, OpenRaster, IPYNB,
and NRRD contract repairs, and deterministic projections because clean replay
and digest-bound tests exist.
Confidence is moderate in the observed implementation footholds because the
product source trees are unchanged from the baseline snapshot but no current
production certification binds their complete package/environment closure.
Confidence is low that the 672-obligation denominator is final until XLIFF and
UBL repairs pass. XLIFF 2.0/2.1 candidate coverage is deeper and
source-authentic, but only 7 of 1,130 candidate dispositions are independently
verified, 75 expected IDs lack source-bound rows, and module ownership is still
open. Events 30 through 38 prove a durable adjudication mechanism and seven
bounded decisions, not broad XLIFF semantic coverage. No stronger claim is
justified.

## Current authority overlay: Event 40

`FF6-EVENT-000040` is the current native head. The selected task remains
XLIFF, with exact microstep `XLF-04-BATCH-005-PARTIAL-002-I`, 31/105 accepted
obligations, and 9/1,130 verified dispositions. UBL retains 6,001 particle
nodes, stable anonymous-type identities, and 1,178 derivation edges, but
UBL-03 is incomplete. Certification remains 0/6.

### Event 38 pre-RED contradiction found during handover replay

The next target-language candidate exposes a deeper production risk than a
missing mapping. The pinned 2.0 and 2.1 Core prose use identical normative text
requiring the explicit or inherited target language to equal `trgLang`.
XLIFF 2.1's F4T Schematron, however, documents and implements a one-way
subcategory allowance through XPath `lang()`. A library that collapses those
authorities into a single unqualified boolean rule will be deterministic but
may be consistently wrong for one profile or one validation mode.

The visible symptom would be rerun-stable disagreement between prose-derived
tests, Schematron differential tests, and user expectations. The root cause is
that the current obligation model has no explicit field separating normative
semantic intent from the effective behavior of an official executable
artifact. The structural weakness is not fixed by choosing one authority ad
hoc. The durable resolution is a profile-aware decision that records both
authority roles, adds discriminating equal/subcategory/reverse-subcategory
tests, and either defines separate strict-prose and official-Schematron
validation modes or records a justified precedence rule. Until then, the
candidate remains unadjudicated and cannot increase coverage.

Tradeoff: exposing two validation modes is more honest and interoperable but
expands API and regression surface; choosing normative prose alone is simpler
but will diverge from the official 2.1 Schematron. Evidence is currently
sufficient to prove the contradiction, not to claim which public API policy
production users will prefer.
