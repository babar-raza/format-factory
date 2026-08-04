---
artifact_id: TC-FF6-NRRD-READINESS-001
artifact_type: taskcard
path: taskcards/TC-FF6-NRRD-READINESS-001.md
format_id: nrrd
product_family: six-python-production
visibility: internal
publish_allowed: false
license: null
provenance_required: true
provenance_status: pending-execution
source_hash: null
generated_by: codex
generated_at: 2026-08-01
reusable: false
refresh_policy:
  trigger: input-digest-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-PROGRAM-CAPABILITIES-001
status: NARROWED_TO_SLICE_SUPPORT_PENDING_REVIEW
lane: A
skill_ids:
  - test-driven-development
  - compile-format-contract
  - reconcile-contract-capabilities
  - build-obligation-register
  - product-source-task
  - package-install-proof
  - plan-control
release_blockers: []
notes: Event-47 work is preserved; recovery revision narrows R3 to inputs required by the golden slice and removes full R3/R4 as a source-mutation prerequisite.
---

# TC-FF6-NRRD-READINESS-001: Establish NRRD Production Readiness

**Phase:** CONTRACT to IMPLEMENTATION_IN_PROGRESS
**Status:** NARROWED_TO_SLICE_SUPPORT_PENDING_REVIEW
**Owner:** deterministic FF6 Lane A scheduler
**Created:** 2026-08-01
**Last updated:** 2026-08-02
**Blocking:** NRRD production implementation and certification batches
**Blocked by:** none for read-only characterization and contract reconciliation
**Format:** nrrd
**Gate:** no gate transition; certification remains evidence-computed

**Capability inspiration backlog (added 2026-08-04):** while gathering
independent oracle evidence for TC-FF6-NRRD-GOLDEN-SLICE-001, pynrrd's API
surfaced four capabilities format_factory.nrrd doesn't yet have — a numpy
adapter, writer compression-level control, detached-header write
convenience, and typed custom-field parsing — each verified against current
source, not assumed. Logged as a non-binding backlog, not a taskcard, in
`plans/strategic/ff6/execution-recovery-directive.yaml`'s
`capability_inspiration_backlog` section. When NRRD readiness work resumes
beyond the golden slice, run each idea through the normal obligation/
capability process there before any implementation.

## Objective

Turn the existing NRRD package from an untrusted partial implementation into a
digest-bound, executable readiness baseline. Reconcile NRRD0001-NRRD0005
authority, the 65 canonical obligations, public APIs, existing source/tests,
security limits, packaging, and external-oracle coverage; then compile bounded
implementation taskcards in risk order. This task does not call the library
production-ready and cannot promote it.

## Event 46 execution checkpoint

R1 is complete and the authority/contract portion of R2 is accepted at GitLab
`main` commit `767e7006a19a118e4a16d72db0a15e2f387b44af`:

- source-tree characterization: 17 production-namespace Python files, 1,290
  lines, 40 public definitions, and 277 passing NRRD tests;
- installed-wheel characterization: `format-factory-nrrd` 0.2.0.dev0, wheel
  SHA-256 `caced0c989552415db6db963d821646b15b3aa198b17510389d37927f8b7fea5`,
  proof ID `PACKAGE-PROOF-AEC9B51D141841330327C084E506E50CFED3EC1D4A0304810AEAAE0A3C8F7964`;
- strict NRRD contract: 21 capabilities and 65 obligations, with all six FF6
  contracts passing check and idempotency;
- current limitation: the reconciliation report is heuristic and
  non-promoting. Exact classification and proof requirements for every one of
  the 65 obligations remain the first unmet R2 work;
- no product source, promotion, certification, release, or gate state changed.

The Event 46 next action was R2 per-obligation classification, followed by R3
independent Teem/pynrrd corpus and oracle acquisition. Event 47 records R2 as
complete. Product source remains read-only until R4 compiles bounded
implementation taskcards.

## Event 47 execution checkpoint

R2 exact obligation classification is complete at GitLab `main` semantic commit
`ea118ba39904b54517ba6bc5839c8d4fc36fa050`:

- all 65 canonical obligations have exactly one schema-valid current row;
- conservative classifications are 17 implemented, 39 partial, 6 missing, and
  3 preservation-only, leaving 48 unresolved obligations;
- every claimed behavior row resolves exact source and test references, while
  every missing behavior states required positive and negative proof;
- eight fail-closed negative controls cover incomplete/duplicate/foreign rows,
  unresolved source/tests, invalid execution evidence, status invariants, and
  source-digest invalidation;
- the exact report was byte-identical across three runs with SHA-256
  `f0e05101e78c3836452f9a5a4a826af9443f0190a97cf6657f60cf2b98b81395`;
- existing execution evidence is suite-level supporting evidence only. It is
  not selector-bound independent interoperability proof and has no promotion
  effect.

Event 47 still records R3 as the accepted continuation until the recovery plan
is reviewed and a later execution transition is validly recorded. Under the
2026-08-03 recovery route, R3 is narrowed to the immutable official, Teem, and
pynrrd inputs required by `TC-FF6-NRRD-GOLDEN-SLICE-001`. A complete 65-row
oracle matrix and full-tree architecture classification remain certification
backlog; they are no longer prerequisites to the first bounded source slice.

## Locked truth and invariants

- GitLab `origin/main` is the only integration authority; no branches or GitHub.
- The existing NRRD source and tests are preserved and characterized before
  restructuring.
- Every authority, fixture, source, test, tool, dependency lock, environment,
  package, and proof input is digest-bound.
- Teem and pynrrd evidence is independent only when produced by those actual
  implementations against immutable corpus items.
- A test name, fixture presence, source symbol, generated report, or local
  source-tree import is not behavior proof.
- The known stateful CSV idempotency test remains exactly deselected in shared
  broad runs until its separately registered repair closes; its three tracked
  outputs must remain byte-identical to Git.
- No product, promotion, release, Gate 10, or publication state changes here.

## Exact owned outputs

- NRRD readiness/characterization reports under `reports/ff6/nrrd-*`.
- NRRD contract/obligation reconciliation outputs already named by the
  registered contract skills.
- Bounded NRRD follow-on taskcards and their `taskcards/index.yaml` entries.
- Skill transcripts and run/proof records under the FF6 task identity.

This readiness card cannot mutate `src/python/nrrd/**` or
`tests/python/nrrd/**`. `TC-FF6-NRRD-GOLDEN-SLICE-001` is the separate exact
implementation authority after Stage 1 passes; it may mutate only its declared
paths, obligations, and RED tests.

## Ordered task slices

### R1 - immutable baseline and import truth

1. Capture Git commit/tree, NRRD authority/contract digests, dependency locks,
   Python/OS/tool identities, public symbols, source/test/fixture digests, and
   current proof descendants.
2. Build the existing wheel from a clean checkout and test imports from an
   isolated environment outside the source tree. Record actual import paths.
3. Run current focused tests without modifying fixtures. Classify every failure
   as current defect, environment defect, invalid fixture, or stale evidence.
4. Snapshot behavior for every currently working public reader, writer, model,
   validation, metadata, compression, detached-file, stream, and mmap surface.

### R2 - authority and obligation closure

5. Strictly compile the NRRD ProductContract from NRRD0001-NRRD0005 authority.
   Missing/mismatched/unsafe authority must stop before digest or proof emission.
6. Reconcile all 65 canonical NRRD obligations to exact authority facts and
   classify each as implemented, partial, missing, rejected, unsupported,
   preservation-only, or preview. Duplicate/foreign/unresolved IDs fail closed.
7. Expand obligations where broad buckets hide distinct behavior: attached vs
   detached payloads; single/list/pattern data files; scalar/block types;
   endian; raw/ASCII/hex/gzip/bzip2; spatial/orientation/measurement frame;
   comments/key-values; header preservation; streaming/mmap; path, allocation,
   overflow, truncation, decompression, and payload-size defenses.

### R3 - slice-required independent corpus and oracle inputs

8. Acquire and hash the smallest licensed official/Teem/pynrrd corpus that
   discriminates multi-byte raw endian behavior and hostile declared-size
   handling for the three golden-slice obligations. Synthetic fixtures may
   supplement but cannot be the only interoperability evidence.
9. Record tool versions, commands, exit codes, source/license/digest, and any
   Teem/pynrrd contradiction. Do not execute the complete format matrix here.
10. Hand these immutable inputs to `TC-FF6-NRRD-GOLDEN-SLICE-001` and stop
    readiness-report expansion until the slice produces a real implementation
    result.

### R4 - deferred certification backlog, not first-slice prerequisite

11. Map the current package into professional layers: `model/`,
    `codec/reader/`, `codec/writer/`, `validation/`, `security/`, `adapters/`,
    optional `analytics/`, and `cli/`. Models perform no I/O; optional NumPy or
    ecosystem integration remains in adapters.
12. Define the public lifecycle API, explicit exports, typing snapshot,
    compatibility policy, resource-limit defaults, strict/preservation modes,
    and deterministic serialization profile.
13. Compile the gap projection into bounded implementation taskcards ordered by
    security/data loss, mandatory read/write, interoperability, packaging,
    public API/docs, then optional capabilities. Each card names exact
    obligations, paths, proof descendants, negative controls, and rollback.
14. Recompute the four-lane schedule. If NRRD becomes blocked, release the slot
    to OpenRaster preparation without fabricating NRRD progress.

## Verification tiers

- **T0:** every write - coordination lease/preflight/write journal, input
  digests, source checkpoint, task/skill manifest, and predicted invalidation.
- **T1:** focused characterization, contract edge, obligation mapping, corpus
  item, oracle comparison, and rejection/resource test.
- **T2:** complete NRRD contract/readiness suite, Ruff, strict Mypy, Pyright,
  py_compile, architecture/API checks, and installed-wheel smoke tests.
- **T3:** clean detached GitLab replay with immutable authority/corpus closure,
  three deterministic report runs, package build/install isolation, and
  current controller/handover consistency.
- **T4:** affected portfolio regression plus selector/full-sentinel comparison;
  zero false negatives.
- **T5:** not satisfied by this readiness task and never claimed.

## Acceptance criteria

- [x] Clean source and installed-wheel baselines are captured separately.
- [x] Existing working behavior has executable characterization coverage.
- [x] NRRD0001-NRRD0005 authority closure passes fail-closed validation.
- [x] All 65 canonical obligations have exact current classifications and proof
      requirements; no mandatory item is hidden by percentage coverage.
- [ ] Slice-required Teem and pynrrd inputs are immutable, licensed, and bind
      the exact golden-slice oracle commands.
- [ ] Full architecture/API/security/package classification is deferred to
      evidence-triggered vertical slices and certification milestones.
- [ ] Three same-input readiness generations are byte-identical.
- [ ] Stale source/test/fixture/authority/tool/lock/environment/package inputs
      invalidate the correct descendants.
- [x] The first executable implementation taskcard names exact obligations,
      RED tests, owned paths, and rollback; later mandatory work remains in the
      current gap projection and is not represented as closed.
- [ ] Focused, regression, static, installed-wheel, receipt, event-chain, and
      detached checks pass.
- [ ] NRRD remains non-certified and `UNASSESSED` unless a later independent
      certification task satisfies the full release-candidate gate.

## Failure and continuation policy

- Invalid fixtures are quarantined by digest; never silently edited in place.
- Oracle disagreements create discriminating tests and contradiction records.
- Missing external optional tools do not stop authority/contract/source/test
  analysis; they create explicit oracle tasks and the lane continues safely.
- After three materially different failed repairs of one root cause, mark only
  that obligation technically blocked and release the lane slot.
- Successful slice-input acquisition transfers directly to
  `TC-FF6-NRRD-GOLDEN-SLICE-001`. It does not self-approve certification or
  release.

## Evidence required

- T0 input manifest and current GitLab commit.
- Exact public API/source/test/corpus inventory with hashes.
- Contract and 65-obligation reconciliation reports.
- Installed-wheel/source-tree isolation proof.
- Teem/pynrrd oracle matrix and contradiction register.
- Determinism/invalidation results and negative controls.
- Generated implementation taskcards with no uncovered mandatory obligation.
- Valid skill transcripts, detached replay, native event ID/hash, and explicit
  statement that product certification/promotion remains unchanged.
