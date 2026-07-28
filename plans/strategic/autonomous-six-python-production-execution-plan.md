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
generated_at: 2026-07-24
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
status: HARDENED_READY_FOR_AUTONOMOUS_EXECUTION
plan_version: 3
goal_id: FF6-PRODUCTION-LIBRARIES-001
goal_status: ACTIVE
quality_target: production_ready
capability_target: comprehensive_developer_use
canonical_forge: GitLab
canonical_remote: origin
canonical_branch: main
execution_branch: main
baseline_ref: origin/main
baseline_commit: 54c4dacb2ed6ef8b89258db2d3f0d1ec00ab92fb
baseline_commit_policy: refresh_per_task_from_origin_main
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

The tables below retain the 2026-07-24 recovery snapshot as historical input.
They are not current readiness evidence. Every task captures the fetched
`origin/main` commit and recomputes contracts, capabilities, gaps, source/API
inventory, installed-package proof, and invalidation state before selection.

### 3.1 Branch and workspace status

| Item | Status | Required treatment |
|---|---|---|
| GitLab mainline planning snapshot | `origin/main` at `54c4dacb2ed6ef8b89258db2d3f0d1ec00ab92fb` | Historical planning input only; capture a fresh task baseline before every mutation. |
| Production controller | Historical/partial state for all six formats | Recompute current state from committed contracts, proof, and current-gap projection; do not treat a prior worktree-local controller state as authoritative. |
| Existing plans/statuses | Historical input only | Revalidate every claim against the canonical proof graph. |
| Shared root worktree | Potentially dirty/concurrent | Preserve; never clean, stash, reset, restore, or broadly stage it. |
| Current SafeTensors checkpoint | Uncommitted / unpromoted | Preserve and review; it is not certification evidence until rebuilt-wheel replay. |

The uncommitted SafeTensors checkpoint consists of:

- `tests/python/safetensors/test_official_interop.py`
- `reports/skills-rff6/skill-transcripts/add-roundtrip-test-safetensors-preservation-001.json`

Its focused differential test passed once only with an alias-loaded official
`safetensors` 0.8.0 distribution. A broader installed-wheel regression then
failed during collection because the installed wheel was stale and lacked
`PayloadAccessMode`. Therefore the checkpoint is **IN_PROGRESS**, not evidence
for `SAL-SAFETENSORS-OBL-2E14EAEFAB630C7F`; do not discard it, stage it with
unrelated files, or claim it closes the obligation.

### 3.2 Verified machinery and contract baseline

The following work is usable but must continue to obey invalidation/replay:

- the canonical product-contract compiler now handles shared capability groups,
  explicit exclusions, required family defaults, content-stable SAL identifiers,
  and missing readiness categories;
- SafeTensors is mapped to the binary-tensor family with 11 capabilities and
  86 strict-profile obligations, contract digest
  `a60f33fd57d8ac98ada72b5a1ea8d03e0dc0852ae1e936e46fefb8ae38809574`;
- XLIFF and UBL authority facts and XSD evidence manifests were added and
  replayed; their facts are promotion-valid only while digests remain current;
- all six strict contracts compile, but compilation proves contract integrity,
  not implementation completion.

Current controller contract digests:

| Format | Contract digest | Controller state | Meaning |
|---|---|---|---|
| IPYNB | `3cfd3362ad167a7e7d6e7054813779f96c483c9dda2156dd07e7f135bc676be6` | IMPLEMENT | Contract ready; implementation/certification proof incomplete. |
| OpenRaster | `2ecf3c51da0443e1d68a82d528dce020b877fe5bb0a9070c629fa338ff785fcf` | IMPLEMENT | Contract ready; product source is policy-blocked. |
| NRRD | `dec661f33cff0eeddb15996022f4b4502eff095605eb11e237eb963d0e0e5aaa` | IMPLEMENT | Contract ready; implementation/certification proof incomplete. |
| XLIFF | `a8f20ae84167690d27130ad0c24076e66d538e14f48a7f6f75eb1b4fb11deaf3` | IMPLEMENT | Contract and authority proof ready; implementation incomplete. |
| SafeTensors | `a60f33fd57d8ac98ada72b5a1ea8d03e0dc0852ae1e936e46fefb8ae38809574` | IMPLEMENT | Highest known unblocked obligation is preservation/interoperability. |
| UBL | `81ca59edbd396364fc89c5d12154b0f53a7b7d693f8fd21d4e6f337c2b8804f7` | IMPLEMENT | Contract and authority proof ready; generator/product evidence incomplete. |

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

### 5.2 One bounded change set

For each task:

1. Resolve the capability route and registered production skill. No direct
   mutation of product, tests, tools, plans, or ledgers without a valid skill
   authorization and receipt.
2. Create/use a clean, isolated worktree from the pinned integration commit;
   separate environment, artifact directory, and proof transaction per format.
3. Apply one bounded change only. Generated source must be checked in and
   reproducible; model code must not perform I/O; adapters own optional
   dependencies; analytics never live in codecs.
4. Run the smallest relevant test first, then the contract-required affected
   regression tier. On failure, minimize, classify the changed proof inputs,
   repair, and rerun. After three materially distinct repairs for the same root
   cause, mark that obligation technically blocked and continue other work.
5. Build an sdist and wheel from the worktree; install it into a fresh test
   environment and assert imported module locations are inside the installed
   distribution. Never accept a source-tree import as package proof.
6. Emit immutable run manifest and proof nodes; update only the materialized
   current-gap projection. Commit successful owned files explicitly; never use
   `git add .` or `git add -A`.

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
owns one coherent capability or 5-15 tightly related obligations. IDs are
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

Exit: all 105 strict obligations pass with official schema, differential,
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

Exit: all 94 strict obligations, binary/text encoding roundtrips, detached-file
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

Exit: the policy gate is documented, then all strict obligations and two-application
interoperability/re-rendering tests pass from installed wheels.

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

Exit: all 125 strict obligations have current schema, semantic, preservation,
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

Exit: all 194 strict obligations, all 91 roots, reproducible generator output,
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
API snapshot, invalidation checks, built-wheel tests, coordination precommit
check, and skill receipt pass. A failed candidate remains isolated and is never
pushed as partial product progress. After a successful push, verify the exact
remote SHA before removing the detached worktree.

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

The successor must first execute the six `TC-FF6-PROGRAM-*` taskcards in Section
7.0. Those cards recompute truth and compile the bounded per-capability queue
from the current-gap projection. If the resulting product priorities are
unchanged, perform in this order:

1. `RFF6-ST-001`: rebuild core + SafeTensors wheel in a clean environment;
   inspect/preserve the uncommitted checkpoint; run the official differential
   test and existing SafeTensors regression through installed packages; emit
   digest-bound proof or retain the gap.
2. `RFF6-ST-002`: implement and prove SafeTensors preservation, lazy/mmap,
   malformed-layout rejection, dtype edge cases, and oracle corpus obligations.
3. `RFF6-IPYNB-001`: establish package chassis/import migration characterization
   and installed-wheel baseline; then implement contract-selected mandatory
   notebook behavior.
4. `RFF6-NRRD-001`: establish NRRD package chassis and first mandatory
   attached/detached payload contract task with Teem/pynrrd oracle harness.
5. `RFF6-XLIFF-001`: reproduce XML models from pinned XSD inputs and prove
   generation determinism before extending module semantics.
6. `RFF6-UBL-001`: reproduce all-91-root generator baseline from pinned XSD
   inputs, validate naming/collisions, and generate test instances.
7. `RFF6-ORA-001`: maintain the policy-blocked record and perform only allowed
   contract/corpus/interoperability planning until source authorization exists.

The controller may reorder only when its current severity/root-cause projection
shows a higher-priority unblocked obligation. It must journal the reason.

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
write a successor handoff pointing at this plan and the exact state/manifest
paths. Do not leave a prose-only memory as the resume mechanism.

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

Status: **HARDENED_READY_FOR_AUTONOMOUS_EXECUTION**. This means the executor has
a durable operational sequence, a bounded definition of comprehensive
capabilities, professional package and code contracts, taskcard compilation,
numeric quality gates, failure rules, and honest policy blocks. It does **not**
mean any of the six libraries is production-certified or release-ready.

## 15. Plan hardening assessment

This version passes the repository plan-hardening checklist at the plan-design
level (22/22 items). That is a statement about executable planning quality, not
product evidence:

- **Goals and outcomes:** one immutable six-library production goal, explicit
  non-claims, format breadth floors, and measurable program completion.
- **Scope and completeness:** normative and developer-use capability universes
  are classified; no mandatory behavior can disappear into a percentage or
  prose deferral.
- **Execution clarity:** the controller, six program taskcards, deterministic
  per-capability taskcard schema, state transitions, and mainline integration
  rule remove reliance on agent memory or broad wave interpretation.
- **Validation:** obligation proof, independent corpora/oracles, installed-wheel
  matrices, numeric coverage/mutation/performance thresholds, reproducibility,
  extraction, and security/supply-chain controls are explicit.
- **Failure handling:** invalidation, bounded repair, technical/policy/external
  block states, current-gap scheduling, and no-push-on-failure behavior preserve
  truthful state.
- **Maintainability:** professional source layout, dependency direction, module
  and complexity limits, typed domain models, optional-adapter isolation,
  generated-source reproducibility, SemVer, and compatibility controls are
  binding.

The first executor action is therefore not ad hoc feature implementation. It is
`TC-FF6-PROGRAM-TRUTH-001`, followed by capability compilation and taskcard
generation. Only evidence from those tasks may replace the historical baseline
or promote a library.
