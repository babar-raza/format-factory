---
artifact_id: TC-FF6-NRRD-PROFILE-SURFACE-001
artifact_type: taskcard
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-PROGRAM-CAPABILITIES-001
status: READY
format_id: nrrd
skill_ids:
  - ingest-spec-sal
  - sal-pipeline-heal
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
