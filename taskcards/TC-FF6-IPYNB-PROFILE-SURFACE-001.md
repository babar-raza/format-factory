---
artifact_id: TC-FF6-IPYNB-PROFILE-SURFACE-001
artifact_type: taskcard
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-PROGRAM-CAPABILITIES-001
status: PASS
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

## Verified completion

Status: `PASS`

- Pinned nbformat 4.0-4.5 schemas were compared by JSON pointer. The retained
  matrix records 62 recursive leaf changes, grouped without losing canonical
  subtree digests, at
  `reports/ff6/ipynb-profile-delta-matrix.yaml`.
- Six new exact SAL facts bring IPYNB to 25/25 content-addressed passing facts.
  The evidence retains two official-schema peculiarities instead of silently
  strengthening them: `authors` uses `item`, and the Jupyter hidden-field
  declarations are not nested under `properties`.
- The executable-document family now has a valid applicability boundary and
  22 format domains. `fact_ownership: explicit_complete` requires every IPYNB
  SAL fact to have exactly one owner; unknown, duplicate, or unassigned facts
  fail compilation.
- IPYNB has 25 capabilities and 68 canonical obligations. Every capability and
  obligation has a non-empty exact subset of nbformat 4.0-4.5.
- Cell names apply to 4.0-4.5; notebook title/authors and cell-name uniqueness
  apply from 4.2; Jupyter hidden metadata from 4.3; execution timing from 4.4;
  cell IDs only to 4.5.
- `IPYNB-EXEC-001` remains `EXCLUDED_WITH_AUTHORITY` across all profiles. No
  notebook code execution, product source, product tests, certification,
  promotion, release, or gate state changed.
- Six-format strict compilation is byte-identical over three runs:
  aggregate `e0747efbf376f081fd6550afed48100c7e1872a055bf6155332ed9358ac05b5f`;
  three-run digest
  `dc33648ffa8f8b676de98f7b145dc2180630d5c470148ca0f46b13ec1492b554`.
- All 15 authority artifacts remain `MATCH`. Affected behavioral regression:
  126 passed, with the pre-existing stateful CSV idempotency test deselected
  and its three test-generated tracked artifacts restored exactly to `HEAD`.
- Ruff passes. Pyright 1.1.411 reports zero errors on all three changed
  compiler modules. Strict mypy passes on the new family-pack validator;
  repository-wide strict mypy remains outside this task because the legacy
  contract compiler/import graph is not strict-mypy-clean.

The remaining parent blockers are `FF6-NRRD-PROFILE-001`,
`FF6-XLIFF-PROFILE-001`, and `FF6-UBL-TYPING-001`.
