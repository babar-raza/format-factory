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
status: READY_FOR_AUTONOMOUS_EXECUTION
plan_version: 1
execution_branch: codex/ff-six-python-production
baseline_commit: 2f54fbcd57b631736b1a187c5a6cfd3d082cf168
scope:
  - ipynb
  - openraster
  - nrrd
  - xliff
  - safetensors
  - ubl
---

# Autonomous Production Execution Plan: Six Python Format Libraries

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

## 3. Baseline recovered on 2026-07-24

### 3.1 Branch and workspace status

| Item | Status | Required treatment |
|---|---|---|
| Isolated branch | `codex/ff-six-python-production` at `2f54fbcd57b631736b1a187c5a6cfd3d082cf168` | Use as the pinned baseline until a successful bounded change is committed. |
| Production controller | `IMPLEMENT` for all six formats | Resume from `.local/production-program/state.json` in this worktree; do not reconstruct state from prose. |
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

## 7. Execution waves and exact exit tests

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

The successor must recompute this queue from the current-gap projection before
executing. If unchanged, perform in this order:

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
- Do not create release/promotion claims from labels, test presence, or old
  reports; do not bypass Gate 10 or business authorization.

## 14. Plan acceptance status

Status: **READY_FOR_AUTONOMOUS_EXECUTION**. This means the successor has a
durable operational sequence, known baseline, known checkpoint caveat, explicit
format scopes, validation gates, failure rules, and true policy block. It does
**not** mean any of the six libraries is production-certified or release-ready.
