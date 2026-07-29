---
artifact_id: TC-FF6-IPYNB-PROFILE-SURFACE-001
artifact_type: taskcard
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-PROGRAM-CAPABILITIES-001
status: READY
format_id: ipynb
skill_ids:
  - ingest-spec-sal
  - sal-pipeline-heal
  - compile-format-contract
  - compile-production-capability-universe
  - plan-control
---

# Repair IPYNB nbformat 4.0-4.5 Profile Applicability

## Boundary

Contract and obligation work only. Product source, product tests, packages,
certification, promotion, release, and gates remain prohibited.

## Objective

Compile exact capability and obligation applicability for nbformat 4.0, 4.1,
4.2, 4.3, 4.4, and 4.5 from the pinned official schemas and documentation.
Preserve the no-execution boundary and do not treat conversion support as
permission to execute notebook code.

## Required execution

1. Revalidate event 17, all 15 authority artifacts, and the IPYNB authority
   declaration.
2. Produce a source-located 4.0-4.5 delta matrix. In particular distinguish
   cell IDs and every minor-version schema change rather than assigning 4.5 to
   all rules.
3. Audit IPYNB SAL facts and exact evidence against the matrix; add facts only
   through registered SAL skills.
4. Split capabilities when obligations within one current capability have
   different version applicability.
5. Preserve typed notebook/cell/output/attachment/MIME/metadata, schema
   validation, conversion, deterministic serialization, safe clearing and
   filtering, ID validation/normalization, structural inspection, unknown
   metadata preservation, and explicit no-execution behavior.
6. Require every capability and obligation to declare a non-empty subset of
   the six selected profiles.
7. Remove `FF6-IPYNB-PROFILE-001` only when compiled evidence claims all six
   profiles with no dangling or foreign fact edge.
8. Regenerate all six projections, prove three identical runs, reconcile the
   parent/current gaps/controller/event/handover, and select the next live
   profile or typing gap.

## Acceptance

- Exact 4.0-4.5 delta evidence with uncertainties.
- No missing IPYNB target profile or known IPYNB profile gap.
- Every mandatory rule has one canonical `SAL-IPYNB-OBL-*` owner and exact
  profile applicability.
- Official schema validation and differential `nbformat` expectations are
  explicit, but remain future implementation proofs.
- Three identical strict runs; all 15 authorities `MATCH`; affected tests and
  static checks pass.
- No product or promotion state changes.
