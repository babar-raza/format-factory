---
artifact_id: FF-SIX-PYTHON-PRODUCTION-EXECUTION-PLAN-001
artifact_type: strategic_execution_plan
format_id: null
product_family: python_format_libraries
visibility: internal
publish_allowed: false
open_source_allowed: false
commercial_allowed: false
generated_by: codex
generated_at: 2026-08-02
skill_id: create-taskcard
skill_ids:
  - plan-control
  - plan-hardening
  - build-obligation-register
  - create-taskcard
  - product-source-task
  - format-feature-expansion
  - add-python-api
  - add-python-object-model-feature
  - add-roundtrip-test
  - run-oracle
  - package-install-proof
  - spec-parity-source-regeneration-and-migration
  - spec-parity-verification
  - certification-ci-gate
  - certification-mutation-tester
  - certification-performance-benchmark
  - build-evidence-bundle
  - post-sprint-audit
  - execution-handoff
status: HARDENED_AUTONOMOUS_EXECUTION_ACTIVE
plan_version: 6
goal_id: FF6-PRODUCTION-LIBRARIES-001
goal_status: ACTIVE
quality_target: production_ready
capability_target: comprehensive_developer_use
canonical_forge: GitLab
canonical_remote: origin
canonical_branch: main
execution_branch: main
baseline_ref: origin/main
baseline_commit: 2ec206edc0104e5f64441c6d043f8d9cd5186fd8
baseline_commit_policy: refresh_per_task_from_origin_main
execution_model: six_product_pull_queues_double_buffered_vertical_slices
logical_product_queues: 6
maximum_active_lanes: 4
maximum_active_write_lanes: 4
integration_model: serialized_fast_forward_to_gitlab_main
last_verified_execution_event: FF6-EVENT-000047
last_verified_semantic_commit: ea118ba39904b54517ba6bc5839c8d4fc36fa050
current_execution_focus: NRRD_R3_INDEPENDENT_CORPUS_AND_ORACLE_MATRIX
scope:
  - ipynb
  - openraster
  - nrrd
  - xliff
  - safetensors
  - ubl
---

# Autonomous Production Execution Plan: Six Python Format Libraries

## 0. Canonical GitLab mainline execution policy

The only forge and integration target for this mission is the GitLab repository
configured as `origin`. The only permitted integration branch is `main`
(`origin/main`). GitHub is not a source, remote, mirror, publication target, or
fallback for this mission.

- Do not create, use, push, merge, or retain a feature, Codex, or other
  non-`main` branch locally or remotely.
- Before each bounded task, fetch `origin/main`; base the task on that exact
  commit and fast-forward the completed commit directly to `origin/main`.
- A dirty local `main` worktree is preserved and never reset, cleaned, or
  overwritten. If it cannot safely advance, use a temporary **detached**
  worktree from `origin/main` solely to create the next mainline commit, push
  that commit directly to `origin/main`, and remove the detached worktree at
  task closeout. A detached worktree is an isolation mechanism, not a branch.
- If `origin/main` advances before push, fetch, rebase/reconcile the bounded
  change against the new `origin/main`, rerun affected verification, then push
  only the resulting fast-forward to `origin/main`.
- Do not leave additional worktrees, branch names, or uncommitted mission work
  as continuation state. Persist continuation through the controller journal,
  content-addressed proof, current-gap projection, and committed plan records.

### 0.1 Binding acceleration amendment and precedence

Plan version 6 retains the version-5 pull system and replaces its fixed
four-lane role assignment with six persistent product queues under a four-write
work-in-progress cap. Sections 0.1, 0.2, 0.3, 5.2, 5.5, 5.6, 7.1, 7.2, 8.4,
11, 11.2, and 12.4 are binding acceleration controls. Where older wave prose
implies that every format waits for another
format, every authority occurrence receives its own full checkpoint, every
task builds a wheel, or every accepted microstep rewrites the complete handover
packet, these acceleration controls take precedence.

The quality target, capability denominator, proof requirements, promotion
rules, main-only GitLab policy, release thresholds, and human-only release
boundaries do not change. Acceleration is obtained through safer work
aggregation, dependency-aware verification, generated projections, and
parallel disjoint lanes. It is never obtained by lowering a gate, accepting a
generated proposal as authority, omitting an obligation, weakening negative
tests, or treating deferred full verification as final proof.

The immutable planning baseline for version 6 is clean GitLab `origin/main`
commit `2ec206edc0104e5f64441c6d043f8d9cd5186fd8` and native controller Event 47.
The accepted semantic product/control checkpoint remains
`ea118ba39904b54517ba6bc5839c8d4fc36fa050`: acceleration controls A1-A3 are
executable, the six contracts compile deterministically, the canonical
denominator is 110 capabilities and 689 obligations, and NRRD R1-R2 are complete.
This progress does not change the six `UNASSESSED` products or the `0/6`
certification boundary. NRRD has 17 implemented, 39 partial, 6 missing, and 3
preservation-only obligation classifications; the 48 unresolved obligations,
R3 independent Teem/pynrrd evidence, XLIFF profile work, UBL-03, independent
IPYNB/SafeTensors readiness, and OpenRaster product source remain open.

The executor must update the native controller only through a normal
hash-chained event after evidence is committed to GitLab `main`. Event 46 is
superseded by Event 47, which is the executable authority for the current NRRD
R3 continuation; plan prose may
explain that state but cannot replace it.

### 0.2 Version-5 product-throughput amendment

Version 4 made parallel execution safe but left two sources of avoidable
latency: the prose queue still described an Event-40 bootstrap, and agents
could treat four scheduled lanes as a reason to wait for four simultaneous
writers. Version 5 makes the queue a pull system. Available executors claim the
highest-ranked ready disjoint work package; a single executor rotates to the
next ready lane at accepted batch boundaries, while multiple registered
executors may work concurrently under non-overlapping leases. Parallelism is a
capacity optimization, never a prerequisite for progress.

The following controls are binding:

1. **Product-first lane allocation.** Whenever ready work exists, at least
   three of the four scheduled lane slots are assigned to format contract,
   implementation, corpus/oracle, packaging, documentation, or certification
   closure. At most one slot performs control-plane work. A second machinery
   batch is allowed only when a critical/high machinery defect directly blocks
   safe product work or could create false proof.
2. **Complete homogeneous work packages.** Version 5 used a 5-15 obligation
   default; version 6 applies the adaptive risk bands in Section 0.3. Every
   package still shares source, invalidation, and rollback boundaries. A
   deterministic read-only classification or generated-schema
   package may exceed 15 when it processes the complete canonical set in one
   transaction and retains a row-level decision for every member. Do not create
   a checkpoint, taskcard, commit, or handover for each mechanically identical
   member.
3. **Pre-stage external evidence.** Authority downloads, licensed corpus
   acquisition, external implementation environments, dependency locks, and
   package-build environments are prepared as soon as their profile contract is
   stable enough to identify them. Late oracle/tool setup must not idle a ready
   implementation lane.
4. **One semantic commit, one projection checkpoint.** Integrate one coherent
   accepted batch per semantic commit. Append one controller event and refresh
   the generated four-file handover only when the accepted batch changes the
   route, controller transition, provider, or externally blocked terminal
   state. Row-level proof remains in the batch transaction and does not create
   documentation churn.
5. **Verification by impact with mandatory sentinels.** T1/T2 run on every
   member/batch; T3 runs only for its explicit triggers; T4/T5 remain scheduled
   and mandatory before their promotion boundaries. A selector false negative
   immediately disables selective verification for that component.
6. **No planning loop.** Once a task has an authority closure, obligation set,
   exact paths, registered skill, RED tests, and proof outputs, execute it.
   Additional plan, handover, registry, or machinery work is forbidden unless a
   current failed control shows that the existing representation cannot execute
   or prove the task safely.
7. **No quality conversion.** A faster batch may reduce duplicated setup,
   repeated serialization, and unrelated test execution. It may not convert
   missing proof into a deferral, reduce a threshold, merge heterogeneous
   semantics, weaken an oracle, or promote from cached/stale evidence.

### 0.3 Version-6 flow-efficiency amendment

Version 5 removed global serialization but retained fixed lane roles and a
single combined compact-product queue. That structure can still idle a format
while another task owns the role, start the next package only after the current
one closes, and apply the same batch size to low-risk generated work and
high-risk handwritten parser work. Version 6 removes those delays without
changing evidence or release criteria.

The following controls are binding:

1. **Six logical product queues, four active writes.** IPYNB, OpenRaster, NRRD,
   XLIFF, SafeTensors, and UBL each retain an independent queue, proof
   transaction, verification kit, and successor state. At most four canonical
   mutation packages may be active at once. Available executors pull the four
   highest-ranked non-overlapping packages; one executor rotates among the same
   queues without waiting for more workers.
2. **Double-buffer each unblocked product.** A product with an active write
   package also has at most one `READY` successor and one read-only `PREPARED`
   successor. Authority, corpus, oracle, RED-test, and environment work for the
   successor proceeds against committed inputs while the current package runs.
   The successor cannot mutate overlapping paths or claim proof before its
   baseline is refreshed after integration.
3. **Prefer vertical capability slices.** Once contract readiness exists, the
   normal product package closes a coherent developer capability across model,
   reader/writer or validator behavior, security limits, public API, tests,
   documentation, and installed-wheel proof. Separate horizontal taskcards are
   used only for shared generators, independent oracle acquisition, or a proven
   ownership boundary. This removes handoffs that produce no usable capability.
4. **Adapt batch size to rollback risk.** Generated or deterministic
   classification work may process a complete namespace, schema layer, or
   canonical set. Stable repeated product rules normally group 8-20 obligations.
   New parser state transitions, security boundaries, compatibility changes,
   and ambiguous authority start at 1-5. A batch grows only after two accepted
   predecessor batches with the same invariant and no split/rollback; any
   exception or rollback halves the next batch and creates a new stable group.
5. **Schedule long-lead verification first.** Licensed corpus acquisition,
   external tool installation, platform/dependency matrices, fuzz seed
   preparation, and generated-schema closure begin as soon as profile identity
   is stable. Their immutable artifacts are prepared ahead of implementation;
   their result nodes are still executed against the exact committed candidate.
6. **Reuse content-addressed verification kits, never verdicts.** Downloaded
   authorities, external binaries, wheels, locks, corpus bytes, and built base
   environments may be reused only when their full input digest matches. Test,
   oracle, performance, and certification verdicts are rerun whenever any proof
   input changes.
7. **Drain integration before drift grows.** The integration queue may contain
   at most two accepted candidates. At two, the controller stops new overlapping
   mutations, drains the deterministic GitLab-main commit train, refreshes
   affected baselines, and then resumes. Disjoint read-only preparation
   continues.
8. **Keep control work exceptional.** Across every rolling six accepted
   batches, at least five must close product contract, corpus/oracle,
   implementation, documentation, package, compatibility, or certification
   evidence. A control-only batch requires a current critical/high defect that
   blocks safe product work or could create false proof. A user-requested plan
   amendment is recorded but does not create permission for another planning
   loop.
9. **Preserve independent validation.** No authoring executor can turn its own
   result into promotion evidence. Deterministic validators, external
   implementations, installed-package tests, and independent certification
   remain required exactly as before.

## 1. Purpose, authority, and non-negotiable outcome

This is the operational handoff for a successor agent. It is deliberately more
authoritative than prior plans, reports, status labels, and prose summaries for
this six-format program. Historical evidence remains useful input, but it is
not proof until replayed against the current commit and content-addressed
inputs.

Build independently publishable, production-grade Python distributions for:

1. Jupyter Notebook (`format-factory-ipynb`)
2. OpenRaster (`format-factory-openraster`)
3. NRRD (`format-factory-nrrd`)
4. XLIFF (`format-factory-xliff`)
5. SafeTensors (`format-factory-safetensors`)
6. OASIS UBL (`format-factory-ubl`)

### 1.1 Binding product goal

The goal is to deliver **six production-ready format libraries, one for each
selected format, with a comprehensive set of format-specific capabilities that
application developers can safely compose into their own production systems**.
The capability implementations are part of the product and must meet the same
correctness, security, performance, typing, documentation, compatibility, and
maintenance standard as the parser and writer. A broad API backed by shallow,
synthetic, incomplete, or unverified behavior fails this goal.

The program is not complete when six packages merely import, parse a minimal
sample, or expose many method names. It is complete only when every package is
independently publishable, its entire declared stable capability surface is
production-grade, and all six packages satisfy the computed certification
contract in this plan.

The supporting distribution is `format-factory-core`. The mission ends only
when all six have computed technical certification and extraction-ready source,
or every remaining path is a true external block after all safe alternatives
have been exhausted. Missing publication credentials or a required human-only
release authorization is an `EXTERNAL_RELEASE_BLOCKED` outcome, not a reason to
leave source, certification, packages, documentation, SBOMs, provenance, and
exports incomplete.

Do not ask a human to choose a format, approve a retry, or continue the work.
Do not self-approve human-only Gate 10 or impersonate an approver. Continue the
highest-priority unblocked obligation and allow a blocked format to run in
parallel with the other five.

## 2. Success definition and explicit non-claims

A library is technically certified only when live, digest-bound proof shows all
of the following from a fresh checkout/worktree:

- every mandatory normative obligation has executed positive evidence;
- every rejection/security obligation has executed negative evidence;
- semantic roundtrip, preservation, and independent interoperability evidence
  meet that format's contract;
- built-wheel tests import the installed wheel rather than source-tree code;
- typed, linted, documented, reproducibly built, dependency-locked artifacts
  pass their required platform and Python-version matrices;
- no critical/high unresolved security finding, proof-edge failure, mandatory
  gap, or unexplained oracle contradiction remains;
- extraction into a standalone repository preserves declared source/package
  digests and reruns the same certification.

Never substitute percentage coverage, a passing test filename, a hand-maintained
status label, or an LLM assessment for these conditions. Synthetic fixtures are
useful but cannot be the sole interoperability proof. Byte-for-byte output is
claimed only where the format profile explicitly supports it; otherwise claim
semantic fidelity and safe unknown-data preservation.

### 2.1 Bounded meaning of comprehensive capabilities

"All possible capabilities" is made finite and testable through a compiled
capability universe. For each format, the inventory must include and classify:

1. every normative requirement in every targeted stable specification profile;
2. every optional module in a targeted stable profile;
3. every read, write, edit, inspect, validate, transform, preserve, and repair
   workflow supported by the format and reasonably useful to developers;
4. security, resource-limit, streaming, random-access, lazy-access, and
   deterministic-output capabilities applicable to the representation;
5. interoperability behaviors exposed by official/reference implementations
   and at least two materially independent ecosystem implementations where they
   exist;
6. format-native developer utilities, diagnostics, and typed builders that do
   not require applications to manipulate untyped internal dictionaries;
7. optional adapters for major Python ecosystems where the adapter adds real
   developer value and can remain dependency-isolated;
8. known extensions, preview profiles, and unsupported behavior, without
   misrepresenting them as stable conformance.

Every inventory item has exactly one release classification:

- `STABLE_REQUIRED`: implemented and certified before 1.0;
- `OPTIONAL_ADAPTER_REQUIRED`: implemented and certified in an install extra;
- `PREVIEW_ISOLATED`: implemented behind an explicit preview API and excluded
  from stable compatibility promises;
- `EXCLUDED_WITH_AUTHORITY`: impossible, unsafe, legally unavailable, outside
  the selected profile, or intentionally delegated to a future package, with a
  primary-authority citation and user-visible documentation.

No capability may remain unclassified. A written deferral, low priority, or
large implementation cost cannot turn a feasible stable capability into an
exclusion. Generic analytics added only to increase method count are not format
capabilities and do not count toward breadth.

### 2.2 Canonical capability record

Compile one machine-readable record per capability with these required fields:

```text
capability_id, format_id, stable_name, classification, developer_use_cases,
spec_profiles, authority_fact_ids, normative_obligation_ids, public_symbols,
source_symbols, model_invariants, preservation_contract, error_contract,
security_contract, resource_limits, performance_budget, dependency_policy,
positive_tests, negative_tests, property_tests, roundtrip_tests, fixtures,
independent_oracles, documentation_examples, compatibility_status,
proof_node_ids, invalidation_inputs, taskcard_ids, release_state
```

Contract compilation fails on a missing field, duplicate identity, foreign
format fact, dangling source/test/proof reference, or mandatory capability with
no implementation task. The capability register, obligation graph, public API
snapshot, documentation inventory, task register, and proof graph must agree.

### 2.3 Production-grade capability definition

A capability is complete only when all applicable conditions pass:

- the public API is intentional, typed, documented, ergonomic, and exported;
- behavior is correct for every declared profile, including invalid and
  adversarial inputs;
- read/edit/write operations preserve all declared information and never
  silently discard unknown supported data;
- errors use the package hierarchy and carry actionable source locations or
  offsets where the representation permits;
- resource use is bounded, configurable, and tested at and beyond limits;
- large-input behavior meets its streaming, lazy, mmap, or allocation contract;
- deterministic behavior is byte-stable where promised and semantically stable
  otherwise;
- positive, negative, property, metamorphic, roundtrip, fuzz, and regression
  evidence covers the obligation decisions relevant to that capability;
- at least one official or independent external implementation validates
  interoperability when an external implementation exists;
- examples execute against the installed wheel, not the source tree;
- compatibility, deprecation, and optional-dependency behavior are tested;
- exact source, test, fixture, authority, dependency, tool, environment, and
  wheel digests are bound into live proof.

### 2.4 Six-library completion rule

Each package promotes independently, but the mission is `COMPLETE` only when all
six packages are at least `RELEASE_CANDIDATE`, every stable capability is
certified, every exclusion is authoritative and documented, standalone
repository extraction passes, and the complete six-package co-installation and
namespace test passes. One strong library cannot compensate for a shallow one.

## 3. Baseline and truth-recovery contract

The baseline below is the verified Event-47 controller checkpoint on 2026-08-02.
It is current only for planning commit
`2ec206edc0104e5f64441c6d043f8d9cd5186fd8` and accepted semantic commit
`ea118ba39904b54517ba6bc5839c8d4fc36fa050`. Every task captures fetched
`origin/main` and recomputes contracts, capabilities, gaps, source/API
inventory, installed-package proof, and invalidation state before selection.

### 3.1 Branch and workspace status

| Item | Status | Required treatment |
|---|---|---|
| GitLab mainline planning snapshot | `origin/main` at `2ec206edc0104e5f64441c6d043f8d9cd5186fd8` | Verified clean checkpoint input only; capture a fresh task baseline before every mutation. |
| Production controller | Event 47, `CONTRACT`, NRRD R3 active | Native journal and controller are executable authority; this plan cannot complete or reorder that task without a validated event. |
| Existing plans/statuses | Historical input only | Revalidate every claim against the canonical proof graph. |
| Shared root worktree | Clean at amendment baseline; concurrency may change it | Preserve unexplained later changes; never clean, stash, reset, restore, or broadly stage them. |
| Product queues | NRRD R3 `WORK_IN_PROGRESS`; XLIFF semantic batch, UBL schema generator, and compact readiness `READY`; OpenRaster preparation is schedulable | Pull up to four highest-ranked non-overlapping writes; maintain all six logical queues without waiting for simultaneous writers. |

The tracked, still non-promoting SafeTensors checkpoint remains historical
input and consists of:

- `tests/python/safetensors/test_official_interop.py`
- `reports/skills-rff6/skill-transcripts/add-roundtrip-test-safetensors-preservation-001.json`

Its focused differential test passed once only with an alias-loaded official
`safetensors` 0.8.0 distribution. A broader installed-wheel regression then
failed during collection because the installed wheel was stale and lacked
`PayloadAccessMode`. Therefore the checkpoint remains **IN_PROGRESS**, not evidence
for `SAL-SAFETENSORS-OBL-2E14EAEFAB630C7F`; do not discard it, stage it with
unrelated files, or claim it closes the obligation.

### 3.2 Verified machinery and contract baseline

The following work is usable but must continue to obey invalidation/replay:

- the canonical product-contract compiler now handles shared capability groups,
  explicit exclusions, required family defaults, content-stable SAL identifiers,
  and missing readiness categories;
- 17 registered authority records currently live-match their pinned digests;
- six draft contracts compile into 110 capabilities and 689 canonical
  obligations, but compilation proves contract integrity rather than
  implementation completion;
- XLIFF profile/module closure remains active with 142 compiled obligations;
  historical candidate counts and partial source-bound rows are non-promoting;
- UBL has a verified partial schema graph with 106 schema documents, 91 roots,
  6,001 local particle nodes, and 1,178 derivation edges, but UBL-03 remains
  incomplete;
- product source exists for IPYNB, NRRD, XLIFF, SafeTensors, and UBL;
  OpenRaster source does not exist;
- NRRD R1-R2 has an immutable source/install baseline, current authority/contract
  closure, and exact classifications for all 65 obligations; 48 partial,
  missing, or preservation-only rows and independent R3 proof remain open;
- all six products remain `UNASSESSED` and production certification remains
  `0/6`.

Current Event-47 canonical denominator:

| Format | Canonical capability file | Capabilities | Canonical obligations | Current meaning |
|---|---|---:|---:|---|
| IPYNB | `plans/strategic/ff6/capabilities/ipynb.yaml` | 25 | 68 | Draft contract; existing source requires exact obligation-to-symbol characterization and production verification. |
| OpenRaster | `plans/strategic/ff6/capabilities/ora.yaml` | 20 | 134 | Draft contract; source absent and policy gate must be re-evaluated before creation. |
| NRRD | `plans/strategic/ff6/capabilities/nrrd.yaml` | 21 | 65 | R1-R2 complete; R3 independent Teem/pynrrd corpus and oracle evidence is first unmet. |
| XLIFF | `plans/strategic/ff6/capabilities/xliff.yaml` | 15 | 142 | Profile/module surface and semantic-batch adjudication remain incomplete. |
| SafeTensors | `plans/strategic/ff6/capabilities/safetensors.yaml` | 11 | 86 | Existing source and prior oracle results require fresh installed-wheel reconciliation. |
| UBL | `plans/strategic/ff6/capabilities/ubl.yaml` | 18 | 194 | Schema graph and generator remain incomplete. |

The aggregate capability-manifest digest at Event 47 remains
`eaf9d1e03611243d455b88a9c10d7513feedcb8264f6e3fee26eb8f45f804a62`.
Any later executor must recompute counts and digests from fetched
`origin/main`; this table must not override newer controller or proof state.

### 3.3 Known block

OpenRaster has a current high-severity package-chassis gap because
`src/python/openraster/` is absent. Repository policy permits creating it only
after Gates 1-9, recorded Gate 9 human approval, implementation taskcards, and
an explicit Phase 4 product implementation prompt. Record this as
`BLOCKED_POLICY_GATE`, do not bypass it, and continue OpenRaster authority,
corpus, contract, architecture, tests that do not create source, and all other
formats. Re-evaluate the exact gate record every run; do not rely on this
paragraph if the registry changes.

## 4. Root causes this plan fixes

The prior system's inconsistency was structural, not a missing test or prompt:

| Symptom | Root cause | Required durable control |
|---|---|---|
| Status says ready after source or fixture changes | Status and evidence are separate mutable authorities | Compute readiness solely from a content-addressed proof graph. |
| Different reruns report different coverage | Digests omitted inputs; fixtures/worktrees were mutable | Bind full dependency closure and use immutable fixtures plus isolated worktrees. |
| Tests exist but mandatory behavior is absent | Presence checks and small hand-maintained lists substitute for obligations | Compile complete contract obligations and require executed positive/negative results per obligation. |
| Oracles appear independent but agree too easily | Synthetic or implementation-derived fixtures/oracles share faults | Require named independent corpus and external reference results; record contradictions. |
| Old gaps keep being scheduled | Append-only history is treated as current queue | Materialize a current-state projection keyed by obligation/format. |
| Promotion is editable | Promotion is stored as a label | Derive promotion from live proof; invalidate descendants automatically. |
| Contract work advances too slowly | A single authority occurrence is treated as a full sprint, checkpoint, replay, handover refresh, and event | Group semantically equivalent occurrences, retain per-occurrence decisions, and accept or roll back one evidence-bound semantic batch. |
| One difficult format stalls the portfolio | Program state is interpreted as one global phase rather than six product lifecycles plus shared prerequisites | Schedule up to four disjoint lanes and compute readiness independently per product. |
| Verification cost dominates semantic work | Release-shaped regression and detached replay are repeated after changes that cannot affect packages or unrelated formats | Select tests from the proof dependency graph and run full sentinel/release tiers at explicit checkpoints. |
| Handover projections become work products | The same controller facts are manually repeated across many Markdown and YAML files after every microstep | Generate four operational handover files from canonical state only at shift or transition checkpoints. |
| Existing code does not shorten delivery | Source presence is not mapped mechanically to obligations, public symbols, and executed behavior | Characterize once, classify `KEEP/REPAIR/REPLACE/REMOVE`, and generate implementation tasks only for the residual gap. |

Preserve existing characterization tests, legal authority records, valid corpus,
and working public behavior. Redesign only the competing-status authority,
proof closure, task selection, promotion, and isolation mechanisms.

## 5. Mandatory operating protocol for the successor

### 5.1 Read and reconcile before every bounded task

1. Read `AGENTS.md`, `plans/master-plan.md`, the Codex adapter, the skill-only
   policy, the relevant registered skill, the format contract, and the current
   controller state.
2. Use the format-first source authority: `src/python/<format>/`; never create
   `src/python/open-source/`, `src/dotnet/`, a top-level `nrrd`, or a top-level
   `safetensors` package.
3. Register with coordination, claim only the exact paths, preflight before
   every write, record every write, and use audited takeover only for a confirmed
   stale lease. Treat unrelated dirty files as preserved foreign work.
4. Capture git commit/tree digest; authority, contract, corpus, generator,
   lockfile, tool, interpreter, OS, architecture, and adapter digests before a
   proof-producing run.
5. Select the highest-severity *current* unmet obligation. Priority order is:
   referential integrity; security/data loss; mandatory read/write; external
   interoperability; installed packaging; public API/docs; optional utility;
   analytics. A blocked format does not stop another format.

### 5.2 One bounded semantic batch

The default unit of work is one coherent semantic batch, not one authority
occurrence and not an entire format. A batch may contain multiple obligations
or candidate occurrences only when they share the same format, compatible
profiles, authority closure, semantic rule family, ownership boundary,
invalidation set, and rollback boundary. Heterogeneous members and every
exception are split into another batch.

For each batch:

1. Resolve the capability route and registered production skill. No direct
   mutation of product, tests, tools, plans, or ledgers without a valid skill
   authorization and receipt.
2. Capture the pinned `origin/main` revision, target-path baselines, authority
   closure, semantic-group identity, all member IDs, predecessor counts, and
   expected proof descendants before mutation.
3. Create or use a separately leased execution scope with its own environment,
   artifact directory, and proof transaction. A detached worktree may be used
   for isolation or immutable verification but never becomes a retained branch.
4. Begin with a representative RED test plus group-invariant and exception
   tests. Execute the rule for every member and retain an explicit decision for
   every occurrence. Generated group membership and mappings are proposals;
   an independent validator must reproduce the authority-to-obligation result.
5. Apply one rollback-safe change set. Generated source must be checked in and
   reproducible; model code must not perform I/O; adapters own optional
   dependencies; analytics never live in codecs.
6. Run verification tier T1 for every member and T2 for the accepted batch.
   Run T3 only at a checkpoint or when source, package metadata, public API,
   runtime dependencies, fixtures, generators, or environment contracts change.
   Contract-only adjudication does not rebuild an unrelated wheel.
7. If any member violates the group invariant, quarantine that member without
   accepting it, restore the entire unaccepted batch transaction, split the
   group, and rerun. Partial batch acceptance is forbidden unless the accepted
   subgroup has a new stable identity and complete proof closure.
8. On failure, minimize, classify the changed proof inputs, repair, and rerun.
   After three materially distinct repairs for the same root cause, mark only
   the affected obligation technically blocked and release its lane for other
   work.
9. Emit one immutable batch manifest containing every member decision and proof
   node. Append one native event per accepted semantic batch, not per mechanically
   identical occurrence. Commit successful owned files explicitly; never use
   `git add .` or `git add -A`.
10. Build and install sdists/wheels whenever runtime or package inputs change,
    and at checkpoint/release tiers. Installed-package proof always asserts the
    import location is inside the installed distribution.

### 5.3 Controller transitions

Use the controller state machine exactly:

`DISCOVER -> SNAPSHOT -> CONTRACT -> IMPLEMENT -> VERIFY -> REPAIR -> CERTIFY -> EXTRACT -> RELEASE_PREP -> COMPLETE`

Journal every transition atomically. A restart resumes the last verified
transition. Any changed source, test, fixture, contract, authority, generator,
dependency lock, tool, or execution environment invalidates descendants and
forces evidence replay. Manual status edits must have no promotion effect.

### 5.4 Bounded task scope, ownership, and evidence paths

The program taskcards compile exact file allowlists before any product write.
Permitted product roots are only `src/python/<format>/` for the selected six
formats plus explicitly named shared-core, test, authority, corpus, registry,
taskcard, proof, plan, report, and documentation files in that taskcard.
Forbidden paths include `src/dotnet/`, `src/python/open-source/`, unrelated
formats, another agent's leased files, and every path not in the allowlist.

Before staging, each changed file is classified as this taskcard's main sprint,
an independently leased secondary sprint, memory-only work, another live
agent's work, or unexplained preserved state. Only reviewed main-sprint files
are staged. Secondary, memory, other-agent, and unexplained files remain
untouched and are recorded in the run manifest.

Every task writes its machine-readable run record under
`.local/run-records/ff6/<taskcard-id>/`, proof transaction under
`.local/proof/ff6/<taskcard-id>/`, and evidence contract under
`.local/evidence-contracts/ff6/<taskcard-id>.yaml`. Successful gate transitions
produce `.local/evidence-bundles/ff6-<taskcard-id>.zip`, update
`.local/artifact-index.yaml`, and record a minimum metadata count defined by the
taskcard. Committed continuation state is materialized under
`plans/programs/ff6/` and `taskcards/ff6/`; local evidence is referenced by
digest and never confused with committed product proof.

### 5.5 Six product queues, four-write WIP cap, and serialized integration

The controller maintains six independent product lifecycles. Queue identity is
per format and never moves between formats; the four-slot cap applies only to
simultaneous canonical mutation packages whose leases, proof transactions,
generated outputs, and taskcard allowlists do not overlap:

| Product queue | Current critical path | Exclusive authority |
|---|---|---|
| NRRD | R3 immutable Teem/pynrrd corpus and differential matrix, then risk-ranked R4 vertical slices | NRRD authority/corpus/oracle/report paths; product paths only after R4 taskcard compilation |
| XLIFF | Core denominator adjudication, 2.0/2.1 module obligations, processing semantics, then vertical implementation slices | XLIFF authority/contract/report/test/product paths named by the claimed package |
| UBL | attributes/groups/wildcards/substitutions/facets, reproducible schema graph and generated typed surface for all 91 roots | UBL schema/generator/report/test/product paths named by the claimed package |
| IPYNB | independent readiness, official `nbformat` differential kit, version conversion and stable API slices | IPYNB-only source/test/corpus/package paths plus explicitly leased shared core |
| SafeTensors | independent readiness, upstream differential kit, layout/security and lazy-access slices | SafeTensors-only source/test/corpus/package paths plus explicitly leased shared core |
| OpenRaster | authority/legal/two-application corpus and policy preparation; source only when live prerequisites permit | OpenRaster preparation paths; product source remains policy-gated |

Shared controller, proof, or generator work is an on-demand service package, not
a permanent product slot. It consumes one of the four write slots only when a
current critical/high control defect blocks safe product work or could create a
false result. A blocked product releases its active slot immediately while its
queue and evidence remain intact. Ready work in another product never waits for
wave numbering, a fixed lane role, or simultaneous worker availability.

Only one live identity may own `logical:FF6-CONTROLLER-WRITE` and only one may
own `logical:FF6-MAINLINE-INTEGRATION`. Product lanes never edit controller or
promotion state directly. They produce a digest-bound closure candidate; the
controller owner validates it and appends the event. Commits and pushes to
GitLab `main` are serialized through the integration lease, use explicit file
lists, and must be fast-forwards. Other lanes may continue read/compute/test
work while integration is occupied, but may not stage or modify the integration
candidate's paths.

Before integration, compare every leased target baseline and proof input with
current `origin/main`. If an upstream change affects the batch dependency
closure, replay T1/T2 against the new commit. If it is disjoint, retain the
already computed proof inputs and run the integration smoke controls. Never
resolve concurrency by stash, reset, clean, broad restore, broad staging, an
unreviewed merge, or a side branch.

The scheduler is deterministic: security/data-loss and broken-authority work
first; then mandatory read/write and contract closure; then interoperability,
packaging, and developer surface. Within equal severity it prefers the batch
that unlocks the greatest number of ready downstream obligations, then the
oldest ready task ID. Throughput or convenience cannot outrank a higher-risk
obligation.

### 5.6 Pull scheduling, work-package readiness, and commit trains

The controller exposes a ready queue rather than assigning work to a specific
provider. An executor may claim a package only when all of these fields are
materialized: obligation/member IDs, authority closure, exact read/write paths,
registered skill and command, RED/negative controls, expected proof descendants,
verification tiers, rollback boundary, and deterministic successor rule.
Missing fields keep that package `NOT_READY`; they do not block a different
ready package.

The queue operates as follows:

1. Recompute ready packages after every accepted batch or invalidation.
2. Exclude packages whose paths, generated outputs, logical resources, or proof
   transactions overlap a live lease.
3. Rank the rest by severity, downstream unlock count, existing environment or
   corpus readiness, then oldest stable task ID.
4. Claim one write package per executor, never more than one active mutation
   package per product. Long-running external-oracle,
   build-matrix, fuzz, or mutation jobs may execute concurrently only in their
   own immutable environment and only when their inputs are already committed.
5. Keep ready depth at least `min(4, unblocked_product_count)`. Every product
   with an active write package has at most one `READY` successor and one
   read-only `PREPARED` successor. If portfolio depth falls below the formula,
   the scheduler compiles the next vertical product packages before optional
   machinery, status, analytics, or convenience work.
6. When a package passes T2, enqueue it for the single integration writer.
   Integration rebases/replays only the affected closure against the current
   `origin/main`; a disjoint upstream commit does not force unrelated full
   verification.
7. After integration, immediately pull the next ready product package. Generate
   a handover only at the Section 12 transition boundary, not merely because a
   commit occurred.

Environment and corpus preparation are explicit queue items but have no product
promotion effect. Each format maintains a reusable, digest-pinned verification
kit containing locked dependencies, official/reference tool versions, licensed
corpus inventory, build commands, and expected import boundaries. The kit is
rebuilt only when one of its inputs changes. Cached bytes may reduce network and
setup latency; results still bind the current task's exact inputs and execute in
a fresh isolated environment.

Preparation is double-buffered but never speculative proof. A `PREPARED`
successor may inventory committed authority, acquire licensed bytes, build a
digest-pinned tool environment, and write RED-test design under its own lease.
It may not modify the current package's paths, reuse an old verdict, or become
`READY` until the current integration commit is fetched and its baseline and
invalidation closure are recomputed.

The integration writer consumes a commit train of independently accepted,
path-disjoint candidates. It performs an ancestry and overlap check for each
candidate, integrates in deterministic priority order, and stops only the
affected candidate on failure. It never combines unverified changes into one
commit, rewrites another executor's commit, or turns several task states into
one optimistic controller transition.

## 6. Target distribution architecture

Create independently buildable packages:

- `format-factory-core`
- `format-factory-ipynb`
- `format-factory-openraster`
- `format-factory-nrrd`
- `format-factory-xliff`
- `format-factory-safetensors`
- `format-factory-ubl`

Use PEP 420 implicit namespace packages, e.g.
`format_factory.ipynb`, `format_factory.nrrd`, and
`format_factory.safetensors`. No `format_factory/__init__.py` is allowed.
`format-factory-core` contains only common errors, diagnostics/source locations,
resource limits, and shared path/stream protocols—no format models, registries,
plugins, codecs, analytics, or governance machinery.

Each format package has independent build metadata, lock files, docs, changelog,
security policy, release manifest, test suite, extraction boundary, and layers:

`model/`, `codec/reader/`, `codec/writer/`, `validation/`, `security/`,
`adapters/`, `analytics/`, `cli/`.

Where meaningful, expose `probe`, `load`, `loads`, `dump`, `dumps`, and
`validate`; strict mode rejects invalid input and preservation mode retains safe
unknown data without claiming to understand it. Recovery mode is prohibited
unless deterministic and documented. Support Python 3.11–3.14 only.

### 6.1 Required professional package structure

Each format distribution must converge on this reviewable structure:

```text
src/python/<format>/
  pyproject.toml
  README.md
  CHANGELOG.md
  SECURITY.md
  LICENSE
  src/format_factory/<format>/
    __init__.py
    py.typed
    api.py
    constants.py
    exceptions.py
    model/
    codec/reader/
    codec/writer/
    validation/
    security/
    workflows/
    adapters/
    analytics/
    cli/
  tests/
    unit/
    behavior/
    conformance/
    roundtrip/
    interoperability/
    security/
    property/
    fuzz/
    performance/
    installed/
  docs/
  examples/
```

Small modules may be consolidated only when they retain one responsibility and
remain within the limits in Section 6.3. Compatibility modules exist only for
documented migrations. The typed `format_factory.<format>` namespace is the
canonical 1.0 API; unsafe top-level aliases are not retained indefinitely.

### 6.2 Enforced dependency direction

The import graph is binding:

```text
model        -> core types only
codec.reader -> model, constants, core protocols, security limits
codec.writer -> model, constants, core protocols, security limits
validation   -> model, constants, core diagnostics
security     -> core policies only
workflows    -> public reader, writer, validation, and model APIs
analytics    -> model only
adapters     -> public API plus one isolated optional dependency
cli          -> public API and workflows
api          -> model, codec, validation, and workflows
```

Models perform no I/O. Circular and upward imports fail certification. Optional
dependency types cannot leak into the base public API. Product code cannot
import agent, governance, registry, supervisor, or proof-runtime modules.
Architecture and import-lint checks enforce these rules fail-closed.

### 6.3 Code-quality and maintainability contract

- New handwritten production modules target at most 600 logical lines and fail
  at 800; a module may expose at most 60 top-level functions.
- `__init__.py` and exception modules target 100 lines; constants modules target
  200. Oversized legacy files require an explicit decomposition taskcard.
- Cyclomatic complexity is at most 10 per function, except a documented and
  mutation-tested parser state machine with a taskcard-approved justification.
- Public APIs and model fields are completely typed and documented. Ruff has
  zero findings; mypy and pyright run in strict mode over public production code.
- Wildcard imports, mutable module-global runtime state, debug output, ambiguous
  `utils`/`helpers` dumping grounds, and agent-facing references are prohibited.
- Complex formats use typed domain models. Untyped dictionaries are confined to
  explicitly preserved extension/metadata boundaries or a migration adapter;
  they are never the primary document model.
- Parser, writer, validation, security, workflow, and analytics decisions remain
  separable and independently testable. No monolithic codec may own all layers.
- Public compatibility follows Semantic Versioning. A documented deprecation
  remains for at least two minor releases unless retaining it creates a security
  or correctness defect.

### 6.4 Generated-source contract

UBL and schema-derived XLIFF source must separate generated and handwritten
code. The generator records authority version and digest, configuration digest,
naming and collision rules, generator/tool digest, and a complete output
manifest. Three clean runs must be byte-identical. Generated files are never
hand-edited; a generator or schema change invalidates all dependent source,
tests, packages, and proof.

### 6.5 Format-specific capability breadth floors

These are minimum breadth floors, not substitutes for the compiled normative
obligation inventory:

| Library | Mandatory developer-capability families |
|---|---|
| IPYNB | nbformat 4.0-4.5 parse/write/convert; typed notebook, cell, output, attachment, MIME, and metadata models; cell-ID rules; schema and semantic validation; deterministic serialization; unknown metadata preservation; trust inspection without execution; output clearing, metadata filtering, ID normalization, structural inspection and transformation; size/depth limits; official `nbformat` interoperability |
| OpenRaster | secure and deterministic archive read/write; versioned profiles; typed stack/group/layer/mask trees; offsets, opacity, visibility, nesting, isolation and documented compositing; PNG assets, thumbnail and merged image; rendering adapter; extension preservation; archive-bomb/path/duplicate defenses; roundtrips with at least two independent applications |
| NRRD | NRRD0001-0005; every type/endian/encoding combination; attached and detached single/list/pattern payloads; full dimensional and spatial metadata; lossless raw-header plus normalized access; streaming, memory mapping and lazy payload access where legal; NumPy adapter; overflow/decompression/path/truncation defenses; Teem and pynrrd interoperability |
| XLIFF | 2.0/2.1 Core and every official 2.1 module; typed vocabulary; inline-code-safe editing; segment split/join and state workflows; original data, skeleton, extensions, matches, glossary, metadata, resource data, size restriction, validation and ITS; schema plus processing validation; canonical XML; preview isolation; independent-tool interoperability |
| SafeTensors | every defined dtype and descriptor edge case; lazy mmap, random tensor access and slicing; deterministic write; strict header/layout validation; NumPy and PyTorch adapters; sharded-index workflows; upstream co-installation and differential tests; duplicate/offset/overlap/hole/truncation/resource defenses |
| OASIS UBL | all 91 UBL 2.3 roots; all common components, simple types, attributes, namespaces, order and cardinality; typed parse/build/edit/write for every root; XSD validation; extension and code-list hooks; streaming; typed signatures and invalidation-on-edit; curated Invoice/CreditNote/Order workflows; official examples and independent schema-engine cross-validation |

## 7. Execution waves and exact exit tests

### 7.0 Taskcard compilation gate

No executor may implement a broad wave directly. Before product mutation, the
current contract and gap projection compile into bounded taskcards. One taskcard
owns one coherent vertical capability slice or the adaptive homogeneous
obligation batch defined in Section 0.3. IDs are
deterministic:
`TC-FF6-<FORMAT>-<CAPABILITY-ID>-<IMPLEMENT|VERIFY|CERTIFY>`.

Every taskcard records the program goal, capability and obligation IDs,
authority and evidence digests, exact allowed paths, public API delta, source
symbols, fixtures and external oracle, registered skill, exact commands and
expected results, security/resource/performance/compatibility acceptance,
proof-node and invalidation outputs, repair policy, dependencies, final states,
and deterministic next-task rule. Compilation fails if any mandatory obligation
is unowned, multiply owned without an integration card, missing authority, or
assigned only presence-based/synthetic evidence.

The first program taskcards execute in this order:

1. `TC-FF6-PROGRAM-TRUTH-001` — refresh mainline, source, package, test,
   authority, corpus, and proof truth.
2. `TC-FF6-PROGRAM-CAPABILITIES-001` — compile and classify the complete
   six-format capability and obligation universe.
3. `TC-FF6-PROGRAM-ARCHITECTURE-001` — establish package boundaries,
   dependency rules, and migration characterization.
4. `TC-FF6-PROGRAM-TASKCARDS-001` — generate and validate all unblocked
   implementation/verification/certification cards.
5. `TC-FF6-PROGRAM-QUALITY-GATES-001` — install executable quality,
   architecture, coverage, mutation, performance, and packaging gates.
6. `TC-FF6-PROGRAM-REPLAY-001` — prove invalidation, isolation, deterministic
   replay, and current-gap scheduling.

Each format then receives separate contract, architecture/migration, capability
implementation, independent verification, installed-package certification, and
extraction task families. Work may run in isolated detached worktrees, but
successful reviewed taskcards integrate serially to GitLab `main`.

### 7.1 Acceleration bootstrap and wave reinterpretation

The numbered waves are dependency groups, not portfolio-wide barriers. A
format advances when its own prerequisite proof is current even if another
format remains in an earlier wave. Shared machinery and package-chassis changes
still block only their actual proof descendants.

At the first execution after this amendment, compile these acceleration cards
without marking the Event-40 XLIFF task complete:

1. `TC-FF6-ACCEL-CONTROL-001`: repair immediate authority fail-closed behavior;
   implement proof-impact selection, semantic-batch manifests, generated
   operational handovers, per-product scheduling, and the serialized mainline
   integration lease.
2. `TC-FF6-XLIFF-SEMANTIC-BATCH-001`: use
   `XLF-CAND-CORE-SCHEMATRON-60B596A00F7FA06A` as the first regression case;
   compile semantic equivalence groups and exception queues without accepting
   generated mappings as proof.
3. `TC-FF6-UBL-SCHEMA-GENERATOR-001`: continue UBL-03 at attributes and
   attribute groups, then groups/wildcards/substitutions/facets, under one
   reproducible schema-graph lane.
4. `TC-FF6-COMPACT-READINESS-001`: independently characterize IPYNB and
   SafeTensors source, APIs, tests, installed packages, and obligation gaps;
   emit `KEEP`, `REPAIR`, `REPLACE`, or `REMOVE` decisions before source
   restructuring.

The acceleration bootstrap exits only when:

- a missing required authority fails before digest computation, contract
  emission, or proof-node creation;
- three identical semantic-group compilations have identical group/member IDs,
  exception queues, and canonical bytes;
- seeded dependency mutations prove that the impact selector includes every
  affected test/proof descendant, while a scheduled full-suite sentinel reports
  zero missed dependencies;
- a failed member rolls back the unaccepted batch without changing predecessor
  decisions, counts, or candidate identities;
- four simulated disjoint lanes cannot consume each other's leases, artifacts,
  environments, controller transaction, or staged files;
- three generated handover runs from identical controller/proof inputs are
  byte-identical and stale manual values fail validation;
- mainline integration is single-writer, explicit-path, fast-forward-only, and
  retains no branch or temporary worktree continuation state.

Failure of one bootstrap control blocks that mechanism, not safe work in a
different lane. The executor records the gap and uses the conservative existing
verification path for affected work until the mechanism is repaired.

### 7.2 Event-47 fast execution packages

The acceleration bootstrap is complete. The current task queue must now produce
format evidence rather than more bootstrap machinery. These packages are the
minimum next execution sequence; the native controller determines their exact
interleaving from leases and readiness.

#### NRRD queue: readiness to implementation

1. Preserve the accepted R2 deterministic 65-row classification from Event 47.
   It is exact and conservative but non-promoting: 17 obligations are
   implemented, 39 partial, 6 missing, and 3 preservation-only. Do not replay or
   rewrite it unless an input digest invalidates it.
2. Execute R3 now that profile/tool identities are known: acquire
   license-recorded Teem and pynrrd corpora, create pinned isolated oracle
   environments, and run the read/write/contradiction matrix against committed
   inputs. Acquisition and execution are separate proof nodes so a transient
   download does not discard validated local classification work.
3. Double-buffer R4 while R3 runs: draft vertical implementation cards from the
   48 unresolved rows, but keep them `PREPARED` until R3 evidence finalizes their
   proof requirements. Apply the Section 0.3 adaptive batch bands, then start the
   highest security/data-loss or mandatory read/write package immediately after
   its RED controls, exact paths, and R3 inputs are ready.

#### XLIFF queue: contract and module closure

1. Execute the registered semantic-batch pilot, then group only genuinely
   equivalent candidates by profile, namespace/module, authority role, QName,
   processing category, and normalized rule.
2. Accept complete groups with row-level decisions and discriminating boundary
   tests. Quarantine exceptions without reverting accepted predecessor groups.
3. Maintain at least one ready Core/module implementation or verification card
   while contract compilation continues, provided its authority closure is
   complete and paths do not overlap the generator.

#### UBL queue: schema graph and reproducible generator

1. Finish attributes and attribute groups as one schema-graph layer, then
   groups/wildcards/substitutions/facets as bounded layers. Do not checkpoint per
   QName or generate product code from an incomplete layer.
2. For every layer, run three canonical graph generations, collision/naming
   negative controls, and an independent schema-engine comparison.
3. Once a layer is complete, generate and verify its affected checked-in types
   while the next read-only schema layer is analyzed in a disjoint transaction.

#### IPYNB and SafeTensors queues: independent compact-product readiness

1. Characterize IPYNB and SafeTensors in one read-only inventory package with
   separate per-product digests and `KEEP/REPAIR/REPLACE/REMOVE` decisions.
2. Pre-build their official/reference oracle environments and installed-wheel
   matrices while residual implementation cards are compiled.
3. Split `TC-FF6-COMPACT-READINESS-001` into one IPYNB child queue and one
   SafeTensors child queue before either product mutation. Each child has its
   own exact-path taskcard, verification kit, proof transaction, successor
   buffer, and semantic commits; neither waits for the other after the shared
   read-only inventory is accepted.

#### OpenRaster queue: policy-safe preparation

Use the first released slot for OpenRaster authority/profile, legal corpus,
two-application interoperability, package architecture, and RED-test design.
Do not create product source until the live policy prerequisites permit it.
Completing all non-source preparation early prevents the policy gate from
becoming an avoidable setup delay after authorization exists.

Exit from this fast-execution stage requires each of the six product queues to
have an accepted readiness/contract package or an obligation-specific truthful
block, at least two vertical implementation packages ready, verification kits
prepared for every unblocked product, and no stale Event-40/Event-46 queue used
as scheduling authority. It does not require any product promotion.

### Wave 0 — Recover, snapshot, and quarantine

Status: **PARTIALLY COMPLETE; REPLAY REQUIRED BEFORE PROMOTION**.

1. Import all older ledgers, reports, status files, and proof graphs as
   historical inputs. Do not delete them and do not let them promote work.
2. Recompile all six product contracts; fail on foreign/missing/duplicate SAL
   fact references, stale authority digests, or mandatory deferrals.
3. Capture public API and behavior characterization tests for any existing
   product before changing its import path or architecture.
4. Hash and license-classify every corpus fixture. Quarantine invalid fixtures
   without deleting their historical digest or origin record.
5. Rebuild current-gap projection from live proof. The historical append-only
   gap ledger must never be scheduled directly.

Exit: three clean same-input replays produce byte-identical canonical contracts,
obligation graphs, generated source, run-manifest canonical portions, and built
package digests; old evidence is non-promoting until replayed.

### Wave 1 — Finish machinery consolidation

Status: **IN PROGRESS**.

1. Make one product contract compiler and one content-addressed proof graph the
   only promotion authority. Migrate legacy graphs/ledgers as read-only
   projections.
2. Ensure proof edges are exactly: authority -> obligation -> capability ->
   source symbol; source+test+fixture+environment -> executed result; executed
   results+package -> certification; certification -> promotion -> release.
3. Record direct input digests for every node. Ensure source/test deletion,
   fixture mutation, lockfile/tool/authority changes, and changed environment
   invalidate the correct descendants.
4. Materialize current operational gaps keyed by format/obligation with severity,
   root cause, retry count, invalidation reason, owner, and block status.
5. Enforce atomic, computed promotion; remove presence-only evidence and written
   deferrals as mechanisms for satisfying mandatory work.

Exit: all 12 machinery regression controls in Section 11 pass three times from
clean worktrees, including cross-run isolation and installed-wheel/source-tree
confusion detection.

### Wave 2 — Package chassis and reproducible generators

Status: **NOT CERTIFIED**.

1. Build the core wheel and each package chassis in the namespace layout.
2. Add deterministic diagnostics, configurable resource limits, lifecycle API,
   explicit public exports, typing, API snapshots, docs template, security
   policy, SBOM/provenance/signing hooks, and extraction manifests.
3. Establish reproducible generation contract for XLIFF/UBL (input schema
   digests, naming/collision rules, deterministic order, checked-in output).
4. Prove chassis with minimal representative fixtures only; label it chassis
   evidence and never format completion.

Exit: independently built wheels co-install with each other and, specifically,
the SafeTensors package co-installs with upstream `safetensors`; three builds
match digests and installed-wheel smoke tests pass on supported environments.

### Wave 3 — SafeTensors and IPYNB

#### SafeTensors

Status: **IMPLEMENT; first required task is rebuild-wheel replay**.

1. Rebuild `format-factory-core` and the SafeTensors wheel from current source
   into a fresh isolated environment. Prove the import location before tests.
2. Review the uncommitted official-interop checkpoint. Keep it only if its test
   invokes the upstream distribution without source alias collisions and its
   receipt contains exact source/test/package/corpus/environment digests.
3. Implement/verify framework-neutral descriptors, lazy memory-mapped payload
   access, all defined dtypes including scalar/empty/sub-byte cases, strict
   validation for UTF-8/shape/size/offset/overlap/hole/truncation, deterministic
   writing, optional NumPy/PyTorch adapters, and separately documented sharded
   indexes.
4. Differentially verify against an exact pinned upstream release and run
   rejection/property/fuzz/resource-limit tests. Prove unknown descriptor fields,
   metadata absence/empty metadata/string-map roundtrip through independent
   parsing before closing `SAL-SAFETENSORS-OBL-2E14EAEFAB630C7F`.

Exit: all 86 mandatory strict obligations have live evidence; upstream
co-install/differential tests and installed-wheel matrix are green.

#### IPYNB

Status: **IMPLEMENT**.

1. Support nbformat 4.0–4.5 and write 4.5 by default; pin official schemas.
2. Implement typed notebooks/cells/outputs/attachments/MIME bundles/metadata,
   official schema validation, explicit version conversion, unknown metadata
   preservation, unique cell IDs, deterministic serialization, safe output
   clearing/metadata filtering/ID normalization, and structural inspection.
3. Differentially compare against `nbformat` on official and independent
   notebooks. Never execute notebook code.

Exit: all 68 current canonical obligations pass with official schema, differential,
preservation, security, built-wheel, and API compatibility proof.

### Wave 4 — NRRD and OpenRaster

#### NRRD

Status: **IMPLEMENT**.

1. Implement NRRD0001–0005 attached/detached files; scalar/block types,
endianness, dimensional/spatial/orientation/measurement/axis/comments/key-value
metadata; raw/ASCII/hex/gzip/bzip2; detached payload lists/patterns; streaming
and mmap where legal; raw-header preservation plus normalized model access.
2. Defend allocation/overflow/decompression/traversal/truncation/payload-size
limits. Differentially validate against Teem and pynrrd with independently
licensed corpora.

Exit: all 65 current canonical obligations, binary/text encoding roundtrips, detached-file
security cases, and differential installed-wheel tests pass.

#### OpenRaster

Status: **BLOCKED_POLICY_GATE for source; otherwise PREPARE**.

1. Continue authoritative draft/corpus/interoperability preparation without
   product source until policy prerequisites are actually recorded.
2. Once unblocked, implement named 0.0.3/0.0.4/0.0.5 profiles and default 0.0.5:
   secure ZIP/mimetype/duplicate/path/decompression controls; typed image/stack/
   group/layer/mask/thumbnail/merged-image models; ordering/opacity/visibility/
   offsets/nesting/isolation/compositing; PNG validation; deterministic archive;
   safe extension preservation; pinned Pillow adapter.
3. Obtain and hash corpora from at least two independent ORA-producing
   applications. Certify interoperability, not universal conformance, because
   the authority is an early draft.

Exit: the policy gate is documented, then all 134 current canonical obligations
and two-application interoperability/re-rendering tests pass from installed
wheels.

### Wave 5 — XLIFF 2.0/2.1

Status: **IMPLEMENT**.

1. Use the official 2.1 schema bundle as the complete authority and support 2.0
   and 2.1; isolate 2.2 as preview and exclude XLIFF 1.2 from this model.
2. Generate/implement typed Core and every module: inline-code pairing/order,
   segmentation/state semantics, files/groups/units/segments/ignorable/note/
   original-data/skeleton/extensions/matches/glossary/metadata/resource-data/
   size restriction/validation/ITS.
3. Enforce schemas plus processing requirements; preserve namespace-aware
   extensions; provide semantic roundtrip and canonical XML output. Use
   independent corpus/reference results and discriminate any oracle conflict.

Exit: all 142 current canonical obligations have current schema, semantic, preservation,
security, differential, and installed-package evidence.

### Wave 6 — UBL 2.3 schema family

Status: **IMPLEMENT**.

1. Treat official UBL 2.3 XSD as normative. Generate deterministically,
   check in, and reproduce types for all 91 document roots and all common
   components/simple types/attributes/namespaces/cardinalities.
2. Provide public typed builders/serializers for all roots, curated Invoice,
   CreditNote, and Order workflows, order/cardinality-correct parse/serialize,
   XSD validation, extension preservation, code-list hooks, streaming parse,
   typed signatures and optional crypto support. Editing signed content must
   invalidate signature state.
3. Test official examples plus schema-valid generated minimal instances where
   examples are absent. Cross-validate with an independent schema engine.
   National invoicing business profiles are explicitly out of scope.

Exit: all 194 current canonical obligations, all 91 roots, reproducible generator output,
schema-engine cross-validation, installed-wheel tests, and signature-invalidated
on-edit proof pass.

### Wave 7 — Certification, extraction, and release preparation

Status: **NOT STARTED** until each package is individually verified.

1. Run full certification in fresh per-format worktrees/containers using locked
   dependencies and immutable fixtures.
2. Extract each distribution from its manifest into a standalone repository,
   verify source and package digests, and rerun certification there.
3. Build two reproducible sdists/wheels; generate SBOM, provenance, signatures,
   license/vulnerability reports, docs site, changelog, and release notes.
4. Publish automatically only if credentials and external authorization already
   exist. Otherwise record `EXTERNAL_RELEASE_BLOCKED` with complete technical
   release artifacts and no question to a human.

## 8. Format-independent validation matrix

Every package must pass contract/referential integrity; unit/behavior/rejection/
model-invariant tests; semantic roundtrip; unknown-data preservation; official
and independent corpus; external-reference differential tests; property and
metamorphic tests; coverage-guided fuzzing; security/resource-exhaustion tests;
Ruff/mypy/pyright/architecture/docs checks; mutation testing of parser,
validator, and writer decisions; public API snapshot; Linux/Windows/macOS and
Python 3.11–3.14 installed-wheel matrices with minimum/latest supported
dependencies; reproducible build, SBOM, provenance, signature, license, and
vulnerability checks.

PR runs: contract/proof integrity, changed-format tests, static checks,
generation check, build/install smoke. Merge/nightly: full corpus, property,
fuzz, mutation, differential, compatibility, performance, replay/invalidation,
cross-platform/dependency matrices. Release: fresh checkout, full graph rebuild,
two reproducible builds, namespace and third-party co-installation, docs examples
against installed wheels, and computed promotion.

### 8.1 Numeric release thresholds

A format reaches `RELEASE_CANDIDATE` only when all thresholds hold:

- 100% of `STABLE_REQUIRED` and `OPTIONAL_ADAPTER_REQUIRED` capabilities have
  current digest-bound proof; every mandatory positive obligation and every
  rejection obligation has executed positive or negative evidence respectively.
- Handwritten production source has at least 95% statement and 90% branch
  coverage, with no uncovered security, preservation, dispatch, or parser/writer
  decision. Coverage never substitutes for obligation proof.
- Mutation score is at least 90% over parser, writer, validator, security, and
  preservation decisions, with zero surviving critical-behavior mutants.
- Ruff, strict mypy, strict pyright, import architecture, API documentation, and
  executable documentation examples are clean; every public symbol is typed and
  documented.
- Deterministic property, metamorphic, rejection, and coverage-guided fuzz suites
  cover every public reader/writer/validator entrypoint with zero crash, hang,
  unbounded allocation, or silent data-loss result.
- Per-format small/medium/large performance budgets record wall time, peak
  memory, throughput, and lazy/streaming behavior where promised. An unexplained
  regression greater than 10% blocks promotion.
- Built-wheel tests pass on Linux, Windows, and macOS for Python 3.11-3.14,
  minimum and latest dependency sets, all optional extras, six-package
  co-installation, upstream-name co-installation, and every published example.
- Two fresh builds are byte-identical and have SBOM, license, provenance,
  signature, and vulnerability evidence. Critical/high vulnerabilities are zero;
  each medium finding has a current technical disposition.
- Public API compatibility matches the approved snapshot or has a versioned,
  tested migration and deprecation record.

A threshold may be `NOT_APPLICABLE` only when the product contract cites the
authority or architectural reason and the proof graph records that decision.

### 8.2 Corpus and oracle minimums

Each format corpus must cover valid minimum, representative, maximum-practical,
boundary, malformed, adversarial, unknown-extension, version/profile,
independently-produced, and writer-generated cases. Every item records origin,
license, digest, format profile, expected semantics, and covered obligations.
Adequacy is measured by the capability/obligation matrix, not a raw file count.

Every mandatory positive obligation needs a valid corpus path; every rejection
obligation needs a negative case; every stable profile needs independently
produced interoperability evidence. Synthetic fixtures cannot be the sole
evidence for interoperability or preservation. External oracles execute in a
separate process or environment against their own installed implementation and
record version and package digests.

### 8.3 Mainline commit gate

Because GitLab `main` is the only integration branch, a taskcard candidate is
pushed only after its affected behavior tests, static and architecture gates,
applicable API snapshot, invalidation checks, the T3 built-wheel controls
required by Section 8.4, coordination precommit check, and skill receipt pass.
A failed candidate remains isolated and is never pushed as partial product
progress. After a successful push, verify the exact remote SHA before removing
the detached worktree.

### 8.4 Verification tiers and impact-selection safety

Verification cost is proportional to the changed proof closure while release
confidence remains cumulative:

| Tier | Trigger | Required work |
|---|---|---|
| T0: pre-write | every mutation | authority/contract identity, lease, skill manifest, target baseline, and expected invalidation check |
| T1: member | every semantic-batch member | genuine RED/GREEN behavior or adjudication test, group invariant, exception handling, and direct proof edges |
| T2: batch | before batch closure | all affected-format tests selected by the proof graph, changed static/architecture checks, deterministic artifacts, predecessor equality, and independent batch validation |
| T3: checkpoint | controller transition, runtime/package/API/generator/fixture/dependency change, or provider shift | fresh detached replay, installed-wheel proof when applicable, affected dependency closure, event-chain validation, and generated handover validation |
| T4: sentinel/nightly | scheduled full audit and before implementation verification | full-format corpus/oracles/property/fuzz/mutation/performance plus dependency and platform matrices appropriate to the schedule |
| T5: certification/release | promotion, extraction, or release candidate | every Section 8 and 8.1 requirement from fresh independent repositories |

The impact selector is optimization machinery, never proof authority. It must
map every source, test, fixture, authority, contract, generator, dependency,
tool, environment, and public-API input to descendants. Seeded mutation tests
must cover all input categories. T4 compares the selector's prediction with
the full observed failure set. Any false negative disables selective promotion
for the affected component, records a high-severity machinery gap, expands the
dependency graph, and replays impacted proof. There is no allowed false-negative
budget.

A contract-only semantic batch does not require an installed-wheel rebuild
unless it changes a runtime-consumed generated artifact. A runtime, packaging,
public-API, dependency, generator, or fixture change always runs the applicable
T3 installed-package controls before integration. Deferred T4/T5 checks can
delay promotion but can never be cited as already-passing evidence.

## 9. Machinery regression controls

Before certifying any product, prove all of these:

1. Three equivalent reruns produce identical canonical outputs.
2. Every input category invalidates the correct descendants.
3. Deleted/renamed tests revoke obligation evidence.
4. Modified fixtures cannot reuse old results.
5. Stale authority digests block contract compilation.
6. Broken/foreign format facts fail closed.
7. Written deferrals cannot satisfy mandatory work.
8. Concurrent runs cannot share mutable state.
9. Source-tree and installed-wheel imports cannot be confused.
10. Manual promotion changes cannot override computed readiness.
11. Legacy evidence cannot become current without replay.
12. Independent repository extraction preserves canonical digests.

## 10. Promotion, failure, and blocking rules

Allowed state progression is:

`UNASSESSED -> CONTRACT_READY -> IMPLEMENTATION_IN_PROGRESS -> IMPLEMENTATION_VERIFIED -> RELEASE_CANDIDATE -> RELEASED`

Any affected digest change yields `INVALIDATED`. Rebuild proof; never edit state
to recover. Failure handling is deterministic:

- transient network/process failure: bounded exponential retry, then cached
  authority or alternate official endpoint;
- invalid fixture: quarantine with digest/history and replace only from a
  licensed independent source;
- specification contradiction: prefer normative machine-readable artifacts when
  authority defines them, otherwise create distinct named profiles;
- oracle disagreement: record it, add a discriminating test, consult primary
  authority, and do not select the convenient result;
- nondeterministic generation: block promotion, isolate input, repair generator,
  and replay from snapshot;
- repeated same root cause after three materially different repairs: mark that
  obligation technically blocked, retain proof, and continue other formats.

## 11. Concrete first task queue

The version-6 queue starts from Event 47. The acceleration bootstrap, control
repair, and NRRD R1-R2 are already complete and must not be repeated. Pull work in this
order, subject to live leases and the deterministic priority rule:

1. Revalidate Event 47, `origin/main`, the capability-manifest aggregate digest,
   110 capabilities, the six obligation totals summing to 689, current leases,
   source presence, and `0/6` certification. Reconcile any difference before a
   proof-producing write; do not regenerate current inputs merely because they
   were produced by another provider.
2. Continue `TC-FF6-NRRD-READINESS-001` at R3. Acquire immutable licensed
   official, Teem, and pynrrd corpus inputs; execute read/write differential and
   contradiction matrices; and double-buffer draft R4 vertical slices from the
   48 unresolved R2 rows without mutating product source early.
3. Keep `TC-FF6-XLIFF-SEMANTIC-BATCH-001`,
   `TC-FF6-UBL-SCHEMA-GENERATOR-001`, and
   `TC-FF6-COMPACT-READINESS-001` ready. Complete the compact read-only inventory,
   then immediately compile separate IPYNB and SafeTensors readiness successors.
   Any available executor claims the highest-ranked non-overlapping product
   package; a single executor rotates among queues at accepted batch boundaries.
4. Use the next free preparation capacity for OpenRaster authority/profile,
   legal corpus, two-application interoperability, architecture, and RED-test
   preparation. Respect its live source-creation policy gate while ensuring the
   non-source kit is ready before the gate can become the critical path.
5. While implementation/code review occupies a write slot, run already-ready
   read-only corpus acquisition validation, external-tool environment builds,
   or committed-input oracle jobs in isolated environments. Never run a proof
   job against uncommitted mutable source.
6. When NRRD R3 closes, finalize and start the highest-risk R4 vertical slice
   immediately. For every active product, maintain at most one `READY` successor
   and one `PREPARED` successor. Keep portfolio ready depth at
   `min(4, unblocked_product_count)`; compile missing product taskcards before
   optional reports, dashboards, convenience exports, or control layers.
7. Apply adaptive batch sizing: complete deterministic schema/classification
   sets, 8-20 stable repeated obligations, and 1-5 high-risk parser/security or
   ambiguous-authority obligations. Grow only after two clean predecessor
   batches; halve after an exception, split, or rollback.
8. Integrate accepted semantic commits through the single GitLab-main writer.
   Refresh the controller/handover only when the accepted batch changes the
   route or transition. Resume the next ready package immediately after the
   remote SHA is verified.
9. Promote each product independently only from its current proof graph. The
   aggregate program remains incomplete until all six release-candidate gates
   pass.

Deterministic scheduling within each lane uses current severity, downstream
unlock count, then oldest stable task ID. A lane blocked by external authority,
policy, or three failed repair approaches yields its worker slot to the next
ready disjoint task. It never keeps the portfolio idle.

### 11.2 Automatic throughput safeguards

The controller applies these checks at every batch boundary:

- **product-work ratio:** over any rolling six accepted batches, at least five
  must close format obligation, corpus/oracle, implementation, package,
  documentation, compatibility, or certification work. A lower ratio is
  allowed only while a recorded critical/high control defect blocks those
  product batches.
- **queue starvation:** ready depth below `min(4, unblocked_product_count)` while
  open mandatory obligations exist triggers vertical taskcard compilation, not
  another status report, handover rewrite, or optional control artifact.
- **integration pressure:** two accepted candidates waiting for the
  integration lease pauses new writes that touch their dependency closures and
  drains the deterministic commit train first. Disjoint read-only work may
  continue.
- **verification waste:** repeated execution of an unchanged expensive tier
  without a trigger records a scheduling defect. Cached artifacts may be reused
  only when their complete input closure matches; executed proof is never
  inferred from cache presence.
- **planning churn:** a plan/handover-only batch after version 5 must name the
  current product task it unblocks and the failing control that necessitated it.
  Otherwise it is rejected as non-goal work.
- **late external setup:** reaching an implementation-complete package without
  its already-identifiable oracle, corpus, or platform kit creates a high
  scheduling gap and immediately schedules that kit without invalidating valid
  implementation proof.
- **successor starvation:** an active product package with no `READY` or
  `PREPARED` successor records a scheduling defect unless the product is
  technically blocked or at certification. Prepare exactly one successor; do
  not create a speculative backlog that will become stale.
- **batch-risk drift:** two consecutive clean homogeneous batches permit the
  next batch to grow within its risk band. Any exception, split, rollback, or
  oracle contradiction halves the next batch and forbids growth until two new
  clean predecessors exist.
- **verification-kit reuse:** cached authorities, tools, corpora, wheels, and
  base environments must match complete input digests. A cached verdict or a
  kit with a missing digest is rejected and cannot satisfy executed evidence.

Historical `RFF6-ST-001` through `RFF6-ORA-001` labels are planning aliases,
not executable priority authority. The taskcard compiler may reuse them only
after binding them to the current contracts, proof graph, path leases, and
version-6 verification tiers.

### 11.1 Per-format release-candidate gates

Each format independently reaches `RELEASE_CANDIDATE` only after:

1. its complete capability inventory has no unclassified or unowned stable
   obligation;
2. its architecture, public API, typing, documentation, and installed-wheel
   quality contracts pass;
3. every capability has digest-bound behavior, rejection, preservation,
   security/resource, and applicable performance proof;
4. its official and independent corpus, external oracle, and contradiction
   register are complete and current;
5. its standalone extraction reproduces source and package digests and passes
   certification; and
6. its SBOM, provenance, signatures, license, vulnerability, compatibility, and
   release documentation artifacts are complete.

The program reaches `RELEASE_CANDIDATE` only after all six formats pass these
gates and the aggregate six-package co-installation and namespace tests pass.

## 12. Required run record and handoff closeout

Each bounded task records exact commands/selectors/exit codes; target-tree and
input digests; built artifact digests; installed import locations; tool/runtime
versions; clean-worktree assertion; coordination identity; proof nodes;
invalidation decisions; change list; skill receipt; test result; next task; and
an honest status (`PASS`, `NEEDS_REPAIR`, `PARTIAL`, `BLOCKED_POLICY_GATE`,
`EXTERNAL_RELEASE_BLOCKED`, or `COMPLETE`). Canonical content excludes
timestamps, absolute paths, random IDs, and ordering noise.

Before ending a session, journal the last verified controller transition,
materialize current gaps, retain all failures, release coordination leases, and
generate the operational successor handoff from canonical inputs. The required
generated surface is `START-HERE.md`, `CURRENT-MACHINE-STATE.yaml`,
`NEXT-MICROSTEP.yaml`, and `manifest.yaml`. Stable architecture, runbook, root
cause, validation, and provider-shift documents are referenced rather than
rewritten after each semantic batch. Refresh them only when their durable
contract changes. Do not leave prose-only memory as the resume mechanism.

A handover refresh is mandatory at a provider shift, controller-state
transition, accepted batch whose next route changes, external-block terminal
checkpoint, or user-requested pause. Per-member and same-route batch progress is
already resumable from the journal and proof transaction and does not require a
20-file documentation rewrite.

### 12.1 Required current-state artifacts

The controller must materialize and validate a product-goal record; per-format
capability and obligation inventories; public-API/source-symbol map;
architecture/dependency report; corpus/license/oracle inventory; current-gap
projection; bounded task register; canonical proof graph and invalidation index;
package certification records; and extraction/release manifests. The program
taskcards must select existing repository schemas where adequate and record
their canonical paths in a governed plan update. Legacy ledgers remain
read-only historical inputs and cannot be current state.

The first six program taskcards must create or adopt these canonical committed
paths:

- `plans/programs/ff6/product-goal.yaml`
- `plans/programs/ff6/controller-state.yaml`
- `plans/programs/ff6/current-state.yaml`
- `plans/programs/ff6/capabilities/<format>.yaml`
- `plans/programs/ff6/obligations/<format>.yaml`
- `plans/programs/ff6/api-source-map/<format>.yaml`
- `plans/programs/ff6/architecture/<format>.yaml`
- `plans/programs/ff6/corpus-oracles/<format>.yaml`
- `plans/programs/ff6/current-gaps.yaml`
- `plans/programs/ff6/task-register.yaml`
- `plans/programs/ff6/proof-index.yaml`
- `plans/programs/ff6/certification/<format>.yaml`
- `plans/programs/ff6/extraction/<format>.yaml`
- `taskcards/ff6/`

If an established repository authority already serves one of these purposes,
the truth taskcard records the replacement path, schema, and migration mapping
before later taskcards rely on it; it must not create a competing authority.

### 12.2 Task final states and repair control

Allowed taskcard final states are `PASS`, `NEEDS_REPAIR`, `PARTIAL`,
`TECHNICALLY_BLOCKED`, `BLOCKED_POLICY_GATE`, `EXTERNAL_RELEASE_BLOCKED`, and
`COMPLETE`. `PASS` closes only the taskcard; it never implies format completion.
Any non-pass state records the failing obligation, root cause, exact evidence,
attempt history, safe work that remains, and deterministic next task. Three
materially different failed repairs may establish a technical block, but cannot
satisfy, exclude, or promote the obligation.

### 12.3 Taskcard self-challenge

Before closing any taskcard, its independent verifier answers and records:

1. Is this executed behavior rather than a file, method, or test count?
2. Does every changed public symbol map to a classified capability and authority?
3. Do positive, rejection, preservation, and resource cases have current proof?
4. Can any valid supported input lose information silently?
5. Was the built wheel, rather than a source-tree import, exercised?
6. Is the claimed oracle truly independent and version/digest bound?
7. Did the change preserve package boundaries and dependency direction?
8. Are optional dependencies isolated and absent from the base API?
9. Are public API, typing, documentation, examples, and compatibility complete?
10. Do all changed inputs invalidate the correct descendants?
11. Are performance and memory behavior bounded for the claimed scale?
12. Are every discovered gap and contradiction retained in current state?
13. Were all writes, staging, and generation confined to the exact task allowlist?
14. Were current-state, taskcard, artifact-index, and evidence outputs updated?
15. Did governance, phase, authority, visibility, and release boundaries remain
    satisfied without self-approval?
16. Were unapproved LLM calls, embeddings, hidden manual work, and synthetic
    substitutes avoided?
17. Does the evidence bundle validate with its required metadata count, and is
    the claimed final state no stronger than its live proof?

A missing or unfavorable answer prevents closure and generates a repair or gap
task automatically.

Every gate-transition response ends with exactly:
`EVIDENCE_BUNDLE: <absolute Windows path to validated zip>`.

### 12.4 Throughput, reliability, and anti-gaming metrics

The controller records these metrics per product queue and per checkpoint:

- accepted product-evidence batches versus machinery/plan-only batches, with
  the Section 11.2 five-of-six product-work floor;
- ready product-package depth, queue-starvation events, and time-equivalent
  idle checkpoints represented as deterministic event counts rather than human
  estimates;
- accepted candidates waiting for integration, overlap/rebase replays, and
  batches drained per commit train;
- formats whose corpus/oracle/tool/platform kits were ready before their first
  implementation-complete batch, plus late-setup gaps;
- independently accepted mandatory obligations and dispositions per semantic
  batch and per verification compute-hour;
- median and tail T1, T2, and T3 duration by change class;
- batch split, rejection, rollback, retry, and repeated-root-cause rates;
- ready-queue idle events caused by shared dependencies, integration contention,
  missing authority, or policy gates;
- proof invalidation fan-out and replay duration;
- impact-selector predicted descendants versus full-sentinel observed
  descendants, with false negatives required to remain zero;
- generated handover determinism and manual operational-projection edits, with
  manual edits required to reach zero after generator acceptance;
- installed-wheel, external-oracle, corpus, and mandatory-obligation burn-down
  per product;
- certification progress as fully proven capabilities, never raw files, lines
  of code, methods, test names, or passing-test counts.

Metrics are diagnostic and scheduling inputs. No throughput target can waive a
failed obligation, security issue, oracle contradiction, proof edge, or release
gate. A faster batch with increased rollback, escaped dependencies, or weaker
proof is a regression.

### 12.5 Acceleration risks and mandatory mitigations

| Risk | Failure mode | Mandatory mitigation |
|---|---|---|
| Semantic grouping | superficially similar authority rules hide profile or processing differences | include profile, normalized expression, authority role, QName, and processing category in group identity; split every exception |
| Parallel lanes | overlapping files, generators, or controller writes corrupt state | exact path/logical leases, separate transactions/environments, single controller writer, serialized integration |
| Impact selection | an omitted descendant lets a regression escape | seeded mutation coverage, periodic T4 comparison, zero-tolerance false-negative disable-and-repair policy |
| Larger batches | failure localization or rollback becomes ambiguous | stable member IDs, representative and boundary RED tests, atomic transaction, subgroup re-identification before partial acceptance |
| Less frequent handovers | an interruption loses uncommitted reasoning | per-member decision journal and content-addressed batch transaction; generated handover at every actual shift/pause |
| Deferred full matrices | incompatibility appears later | T3 triggers for runtime inputs, scheduled T4 sentinels, mandatory T5 before promotion |
| Existing-code reuse | legacy behavior is preserved without proving correctness | characterize behavior separately from acceptance, map to obligations, and require `KEEP/REPAIR/REPLACE/REMOVE` evidence |
| Planning/control churn | safe machinery becomes the product and consumes the execution budget | five-of-six product-work floor, plan-only unblock citation, queue-starvation task compilation, no repeated bootstrap |
| Double buffering | a successor is prepared against a baseline invalidated by current integration | allow only one READY and one PREPARED successor; refresh baseline and invalidation closure after integration before readiness |
| Adaptive batches | throughput pressure grows a batch beyond safe rollback or semantic boundaries | risk bands, two-clean-predecessor growth rule, automatic halving after split/rollback/contradiction |
| Verification-kit caching | cached environment or corpus is mistaken for an executed current verdict | bind complete kit inputs, reuse bytes only, rerun result nodes for changed proof closure |
| Single-executor operation | four active slots are mistaken for a four-worker prerequisite | pull one ready package, rotate among six product queues at batch boundaries, and keep concurrency optional |
| Integration backlog | many accepted candidates drift from current main before integration | deterministic commit train, queue-pressure drain rule, affected-closure replay, serialized fast-forward writer |
| Late oracle/corpus setup | implementation finishes before independent verification can start | pre-stage licensed corpora, pinned external tools, dependency locks, and platform kits as soon as profiles stabilize |

## 13. Hard prohibitions

- Do not delete, reset, restore, stash, clean, or overwrite unexplained work.
- Do not use broad staging, broad generators, or repository-wide formatters
  while agents may be live.
- Do not create prohibited source roots or top-level compatibility packages.
- Do not execute notebook code.
- Do not call a synthetic fixture or own implementation an independent oracle.
- Do not claim OpenRaster universal conformance, XLIFF 2.2 stable support, UBL
  national-profile correctness, or SafeTensors upstream replacement without the
  stated proof.
- Do not count generic analytics, aliases, stubs, taskcards, schemas, or
  synthetic-only fixtures as implemented capability breadth.
- Do not wrap an external library thinly and claim that library's behavior as a
  Format Factory implementation without explicit adapter classification.
- Do not use an untyped dictionary as the canonical model for these six
  libraries or consolidate format behavior into a monolithic codec.
- Do not call production LLM endpoints, create embeddings/vector stores, or use
  model output as authority, oracle, corpus, acceptance evidence, or promotion
  proof unless a separately authorized taskcard and endpoint policy permit it.
- Do not lower coverage, mutation, typing, architecture, security, corpus,
  oracle, packaging, or reproducibility gates to make a task pass.
- Do not create release/promotion claims from labels, test presence, or old
  reports; do not bypass Gate 10 or business authorization.

## 14. Plan acceptance status

Status: **HARDENED_AUTONOMOUS_EXECUTION_ACTIVE**. This means the executor has
a durable operational sequence, a bounded definition of comprehensive
capabilities, professional package and code contracts, taskcard compilation,
numeric quality gates, failure rules, honest policy blocks, semantic batching,
six logical product queues under a four-write WIP cap, double-buffered
successors, adaptive risk-bounded batches, vertical capability slices,
product-first pull scheduling, pre-staged content-addressed verification kits,
tiered verification, commit trains, and serialized mainline integration.
Acceleration controls A1-A3 are implemented and verified through Event 45;
Event 47 records NRRD R2 completion; version 6 improves flow without changing
controller promotion or product state.
This does **not** mean that any of the six libraries is production-certified or
release-ready.

## 15. Plan hardening assessment

This version passes the repository plan-hardening checklist at the plan-design
level (22/22 items). That is a statement about executable planning quality, not
product evidence:

- **Goals and outcomes:** one immutable six-library production goal, explicit
  non-claims, format breadth floors, and measurable program completion.
- **Scope and completeness:** normative and developer-use capability universes
  are classified; no mandatory behavior can disappear into a percentage or
  prose deferral.
- **Execution clarity:** the controller, completed acceleration bootstrap,
  deterministic semantic-batch taskcards, Event-47 pull queue, six independent
  product lifecycles, four-write WIP cap, double-buffered successors, adaptive
  batch rules, work-package readiness contract, state transitions, generated
  handover boundary, and serialized commit train remove reliance on agent
  memory, simultaneous-worker assumptions, or broad wave interpretation.
- **Validation:** T0-T5 impact-aware tiers preserve obligation proof,
  independent corpora/oracles, installed-wheel matrices, numeric
  coverage/mutation/performance thresholds, reproducibility, extraction, and
  security/supply-chain controls; zero selector false negatives is binding.
- **Failure handling:** invalidation, bounded repair, technical/policy/external
  block states, current-gap scheduling, and no-push-on-failure behavior preserve
  truthful state.
- **Maintainability:** professional source layout, dependency direction, module
  and complexity limits, typed domain models, optional-adapter isolation,
  generated-source reproducibility, SemVer, and compatibility controls are
  binding.

The next executor action remains the exact Event 47 continuation: execute NRRD
R3 independent Teem/pynrrd corpus and oracle work from immutable committed
inputs while double-buffering draft R4 vertical slices for the 48 unresolved
rows. It must not restructure NRRD product source before R4 finalizes bounded
implementation taskcards. XLIFF, UBL, IPYNB, SafeTensors, and policy-safe
OpenRaster preparation retain independent pull queues; they do not wait for
NRRD when a disjoint executor is available. Only executed, digest-bound
evidence may advance the controller or promote a library.
