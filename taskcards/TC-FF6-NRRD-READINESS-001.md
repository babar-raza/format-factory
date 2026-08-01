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
status: WORK_IN_PROGRESS
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
notes: NRRD production-readiness characterization and executable gap compilation; no optimistic certification.
---

# TC-FF6-NRRD-READINESS-001: Establish NRRD Production Readiness

**Phase:** CONTRACT to IMPLEMENTATION_IN_PROGRESS
**Status:** WORK_IN_PROGRESS
**Owner:** deterministic FF6 Lane A scheduler
**Created:** 2026-08-01
**Last updated:** 2026-08-01
**Blocking:** NRRD production implementation and certification batches
**Blocked by:** none for read-only characterization and contract reconciliation
**Format:** nrrd
**Gate:** no gate transition; certification remains evidence-computed

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

The exact next action is R2 per-obligation classification, followed by R3
independent Teem/pynrrd corpus and oracle acquisition. Product source remains
read-only until R4 compiles bounded implementation taskcards.

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

The existing `src/python/nrrd/**` and `tests/python/nrrd/**` trees are read-only
for R1-R4. Any source mutation requires a separate generated implementation
taskcard with an exact path allowlist, obligation IDs, RED tests, and rollback
boundary.

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

### R3 - independent corpus and oracle matrix

8. Inventory official, Teem-produced, pynrrd-produced, and independently
   licensed corpus items by digest and legal status. Synthetic fixtures may
   test invariants but cannot be the only interoperability evidence.
9. Execute read and write differential tests against Teem and pynrrd. Record
   contradictions without selecting whichever result improves coverage.
10. Establish positive, negative, preservation, semantic-roundtrip, property,
    metamorphic, fuzz, mutation, security/resource, and performance evidence
    required for every obligation class.

### R4 - architecture and production batch compilation

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
- [ ] All 65 canonical obligations have exact current classifications and proof
      requirements; no mandatory item is hidden by percentage coverage.
- [ ] Teem and pynrrd matrices use immutable independent corpus evidence and
      preserve contradictions explicitly.
- [ ] Architecture/API/security/package gaps are root-caused and prioritized.
- [ ] Three same-input readiness generations are byte-identical.
- [ ] Stale source/test/fixture/authority/tool/lock/environment/package inputs
      invalidate the correct descendants.
- [ ] Executable production implementation taskcards cover every open mandatory
      obligation and name exact RED tests and owned paths.
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
- Successful closure selects the highest-risk NRRD implementation batch. It
  does not self-approve certification or release.

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
