---
artifact_id: TC-FF6-NRRD-PROFILE-SURFACE-001
artifact_type: taskcard
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-PROGRAM-CAPABILITIES-001
status: PASS
format_id: nrrd
skill_ids:
  - ingest-spec-sal
  - sal-pipeline-heal
  - create-format-family-pack
  - research-format-contract-sources
  - compile-format-contract
  - compile-production-capability-universe
  - plan-control
---

# Repair NRRD0001-NRRD0005 Profile Applicability

## Boundary

Contract and obligation work only. Product source, product tests, packages,
certification, promotion, release, and gates remain prohibited.

## Objective

Compile exact capability and obligation applicability for NRRD0001,
NRRD0002, NRRD0003, NRRD0004, and NRRD0005 from the two pinned Teem NRRD
authority artifacts. Preserve every current scientific-array capability while
separating features introduced by later magic/version identifiers.

## Required execution

1. Revalidate event 18, all 15 authority artifacts, and both NRRD authority
   declarations (`SRC-NRRD-001`, `SRC-NRRD-002`).
2. Parse the pinned specification and examples into a source-located
   NRRD0001-NRRD0005 delta matrix. Record exact sections/lines or structural
   members, source digests, interpretation confidence, and every version
   introduction or semantic change.
3. Determine, rather than assume, applicability for header fields, attached
   and detached data, scalar/block types, endian rules, dimensional/spatial
   metadata, orientation, measurement frames, axis metadata, comments,
   key/value pairs, raw/ASCII/hex/gzip/bzip2 encodings, data-file lists, and
   filename patterns.
4. Audit NRRD SAL facts and declarative evidence against the matrix. Add or
   heal facts only through registered SAL skills. Preserve exact authority
   contradictions and do not infer a version from the newest specification
   merely because it documents older behavior.
5. Apply `fact_ownership: explicit_complete` to the NRRD family only after
   every live SAL fact has one exact capability owner. Split capabilities
   whenever one current capability mixes rules with different version
   applicability.
6. Preserve the intended production surface: attached/detached resources,
   streaming and memory mapping where encoding permits, high-fidelity raw
   header preservation, normalized typed access, deterministic writing, and
   allocation/overflow/decompression/traversal/truncation/payload-size
   protections.
7. Require every NRRD capability and obligation to declare a non-empty subset
   of the five selected profiles. Reject duplicate, unassigned, foreign, and
   dangling fact or profile edges.
8. Remove `FF6-NRRD-PROFILE-001` only when the strict projection claims all
   five profiles from evidence. Regenerate all six projections, prove three
   byte-identical runs, retain 15/15 authority matches, reconcile controller
   state, and select XLIFF profile repair next.

## Acceptance

- Exact NRRD0001-NRRD0005 delta evidence with authority locations,
  peculiarities, contradictions, and uncertainty.
- No missing NRRD target profile or known NRRD profile gap.
- Every mandatory NRRD rule has one canonical `SAL-NRRD-OBL-*` owner and an
  exact profile subset.
- Teem and pynrrd differential expectations are explicit future
  implementation proofs, not contract-completion evidence.
- Three identical strict six-format runs; all 15 authorities `MATCH`;
  affected tests, Ruff, and Pyright pass. Mypy results retain their precise
  checked boundary.
- No product or promotion state changes.

## Verified completion checkpoint

Status: `PASS` at native FF6 event `FF6-EVENT-000019`.

### Authority and profile evidence

- The pinned Teem HTML specification and Teem 1.9.0 `formatNRRD.c` member were
  independently checked at SHA-256
  `43ca6102...`, `e0b34337...`, and `c75ebbf2...` respectively; full values
  remain in the authority lock, SAL receipts, and delta report.
- `reports/ff6/nrrd-profile-delta-matrix.yaml` separates the five magic
  profiles without treating the newest prose as proof of older behavior:
  - NRRD0001: baseline header, attached/single detached payload, scalar/block
    types, encodings, endian, shape, and baseline metadata;
  - NRRD0002: key/value metadata;
  - NRRD0003: axis kinds;
  - NRRD0004: thickness/sample units, space/orientation metadata, multi-file
    resources, and changed path semantics;
  - NRRD0005: measurement frame.
- The report records an interoperability peculiarity rather than hiding it:
  Teem's reader accepts later fields under older magic identifiers. Strict
  conformance remains version-aware; tolerant interoperability behavior is a
  future explicit product policy.
- All 25 NRRD SAL facts have exact passing declarative receipts.

### Contract depth and ownership

- The scientific-raster family pack contains 18 domains and 41 policy IDs.
- `fact_ownership: explicit_complete` assigns every one of the 25 live NRRD
  facts exactly once, with no duplicate, foreign, missing, or dangling owner.
- A validator negative control rejected the malformed
  `NRRD-V4META-001` identifier; the canonical source was corrected to
  `NRRD-PHYSICALMETA-001` and the policy to
  `POL-SCR-PHYSICALMETA-01`.
- The governed research source was repaired where one requirement mixed
  NRRD0004 coordinate transforms with NRRD0005 measurement-frame semantics.
  The research store, deterministic product requirement, authority lock, and
  compiled contract were resynchronized rather than patching the projection.
- The compiled NRRD contract has 21 professional capability records. The
  deterministic six-format projection owns 65 NRRD obligations, with 20
  stable required capabilities and one isolated preview capability.
- All five selected profiles are claimed; missing profiles and known NRRD
  surface gaps are empty; every obligation has a non-empty profile subset;
  duplicate canonical obligation IDs are zero.

### Deterministic proof

- NRRD contract SHA-256:
  `a5de17bfd0d6f978b07d0e00b109b6fc4e16257c6299444081e356fc9b1b693b`.
- NRRD capability projection SHA-256:
  `36fd53d95ae006c5709f4e44285c8c1edd554be992f1dc99ef6db1453a92116a`.
- NRRD obligation projection SHA-256:
  `12dfc9adffc69c0762756972f6de2552c1a721cccad51d020d1e08c130d4cef9`.
- Six-format manifest aggregate:
  `4d17d8c8c0ef3de74d59e1d5b16884c0210fd0836e0593591871f10d0af2efd2`.
- Three-run digest:
  `389be84634941d3f244387bbc488c2303dcdb3add74b7d1edfb5def85710d3fc`.
- All 15 locked authority artifacts remain live `MATCH`.

### Verification boundary

- SAL exact verification: 25/25 `PASS`.
- Family-pack validation and idempotency: `PASS`.
- ProductContract schema, provenance, depth, shallow-language, duplicate-ID,
  test-gate, freshness, and family-adequacy checks: 8/8 `PASS`.
- Six-format check mode and three-run idempotency: `PASS`.
- Format-contract tests: 92 passed, 1 baseline-known stateful CSV
  idempotency test deselected.
- Affected verification/compiler/controller tests: 96 passed.
- Authority dependency-closure tests: 119 passed.
- Ruff on affected machinery and tests: `PASS`.
- Pyright 1.1.411: zero errors, warnings, or information diagnostics.
- Strict Mypy passed for the touched family-pack validator after installing
  `types-PyYAML 6.0.12.20260724` in the ignored local virtual environment.
  This is not a repository-wide Mypy claim.
- The global SAL merge command still exits non-zero on pre-existing ODS/ODT
  alias contradictions. Its derived cache contains all 25 valid NRRD facts,
  and all attempted global alias side effects were removed. This NRRD task
  did not conceal or broaden into those unrelated defects.

### Self-challenge

1. All required NRRD task steps were performed: yes.
2. Required evidence is present: yes.
3. Evidence is sufficient for contract/profile completion: yes; it is not
   presented as product implementation evidence.
4. A secondary source was used where primary authority was required: no.
5. A phase-forbidden file was created or modified: no.
6. A gate was self-approved: no.
7. Phase N+1 work was performed: no.
8. An unauthorized commit or push occurred: no.
9. The next executor has an inspectable checkpoint: yes.
10. A discovered gap was left unlogged: no.
11. Relevant memory/context was read: yes.
12. Memory was treated only as context, not authority: yes.
13. Memory was checked against canonical Git/controller evidence: yes; no
    unlogged contradiction remains.
14. Memory-update trigger: not applicable; no memory update was requested.
15. Human review is being requested: not applicable; no human review is
    requested.

### Truth boundary and successor

This checkpoint proves the NRRD normative work denominator and deterministic
contract projection. It does not prove that the existing NRRD source is
production-ready, does not certify a package, and changes no promotion or
gate.

The parent task remains `NEEDS_REPAIR`. The exact successor is
`TC-FF6-XLIFF-PROFILE-SURFACE-001`; UBL all-root typing remains queued after
XLIFF.
