---
artifact_id: TC-FF6-PROGRAM-CAPABILITIES-001
artifact_type: taskcard
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
goal_id: FF6-PRODUCTION-LIBRARIES-001
status: NEEDS_REPAIR
skill_ids:
  - build-obligation-register
  - compile-format-contract
  - reconcile-contract-capabilities
  - create-taskcard
  - plan-control
---

# Compile the Six-Format Capability and Obligation Universe

## State

- Status: `NEEDS_REPAIR`
- Controller predecessor: `TC-FF6-PROGRAM-TRUTH-001`
- Controller successor: `TC-FF6-PROGRAM-ARCHITECTURE-001`
- Product source mutation: prohibited
- Product promotion effect: none

## Objective

Compile a complete, authority-backed, deterministic inventory of stable,
optional-adapter, preview, and excluded capabilities plus every normative
obligation for IPYNB, OpenRaster, NRRD, XLIFF, SafeTensors, and UBL.

This task establishes what must be built and proven. It does not count any
capability as implemented merely because source, a public symbol, a test, or a
fixture exists.

## Inputs

- `plans/strategic/ff6/product-goal.yaml`
- `plans/strategic/ff6/current-state.yaml`
- `plans/strategic/autonomous-six-python-production-execution-plan.md`
- `registry/format-contract-registry.yaml`
- `shared/format-contracts/{ipynb,ora,nrrd,xliff,safetensors,ubl}.yaml`
- `shared/sal-facts/{ipynb,ora,nrrd,xliff,safetensors,ubl}.yaml`
- corresponding SAL evidence and verification reports
- pinned primary specifications and schemas
- current source, tests, samples, oracle, package, and proof inventories

## Allowed tracked outputs

- `plans/strategic/ff6/capability-taxonomy.yaml`
- `plans/strategic/ff6/capabilities/*.yaml`
- `plans/strategic/ff6/obligations/*.yaml`
- `plans/strategic/ff6/capability-coverage.yaml`
- `plans/strategic/ff6/current-gaps.yaml`
- `plans/strategic/ff6/controller-state.yaml`
- `plans/strategic/ff6/events.jsonl`
- this taskcard and `taskcards/index.yaml`
- the successor architecture taskcard

All `src/**`, product test trees, packaging metadata, release registries, and
gate approvals are forbidden.

## Required capability record fields

Each record must contain:

```text
capability_id, format_id, stable_name, classification, developer_use_cases,
spec_profiles, authority_fact_ids, normative_obligation_ids, public_symbols,
source_symbols, model_invariants, preservation_contract, error_contract,
security_contract, resource_limits, performance_budget, dependency_policy,
positive_tests, negative_tests, property_tests, roundtrip_tests, fixtures,
independent_oracles, documentation_examples, compatibility_status,
proof_node_ids, invalidation_inputs, taskcard_ids, release_state
```

Unknown future implementation references are explicit `PLANNED`, never omitted.

## Acceptance

- All six targeted stable profile surfaces are accounted for.
- Every normative requirement has one stable ID and authority reference.
- Every capability has exactly one allowed classification.
- No capability or obligation remains unclassified or unowned.
- Exclusions contain a primary-authority basis and user-visible disposition.
- Capability, obligation, fact, format, and profile references have zero
  duplicates, zero foreign edges, and zero dangling edges.
- Counts reconcile from authority inventory to obligations to capabilities.
- Three clean compilations produce byte-identical canonical outputs.
- Existing source symbols are observations only and do not close obligations.
- The controller event chain validates and selects the architecture task.
- No product is promoted.

## Failure handling

Missing or contradictory authority creates a named current gap and blocks only
the affected obligation/profile. It does not permit invention, omission, or
synthetic authority and does not stop safe compilation for other formats.

## Independent checkpoint audit

Event `FF6-EVENT-000009` invalidates the submitted close without discarding its
draft work. The submitted artifacts contain 89 useful capability descriptions
but only 128 parallel `OBL-*` records. The canonical product-contract compiler
produces 636 obligations from the same contracts, with zero ID overlap:

| Format | Submitted | Canonical compiler |
|---|---:|---:|
| IPYNB | 19 | 105 |
| OpenRaster | 7 | 32 |
| NRRD | 18 | 94 |
| XLIFF | 31 | 125 |
| SafeTensors | 19 | 86 |
| UBL | 34 | 194 |

Additional failures are recorded as `FF6-GAP-013` through `FF6-GAP-015`:
classification/scope contradictions, missing repository-local authority bytes,
and absent three-run deterministic proof. Architecture remains locked. Repair
must preserve useful descriptions, replace the incomplete identity/projection,
and satisfy every original acceptance criterion before a new close event.

## Repair checkpoint — deterministic compiler

`TC-FF6-CAPABILITY-COMPILER-001` replaces the incomplete hand-written
projection with a registered, schema-validated compiler:

- 89 canonical capability identities are retained.
- 636 canonical `SAL-<FORMAT>-OBL-*` obligations are emitted and owned once:
  IPYNB 105, OpenRaster 32, NRRD 94, XLIFF 125, SafeTensors 86, UBL 194.
- Locked classification results are 80 stable, 4 optional-adapter, 4 preview,
  and 1 authority-backed exclusion.
- IPYNB execution is excluded; SafeTensors framework adapters are optional.
- Every contract, SAL store, SAL evidence store, policy, family pack, research
  record, enrichment, compiler module, product-contract runtime, and schema is
  bound into `capability-manifest.json`.
- Expected and observed authority-artifact digests are explicit. All six
  formats remain authority-blocked because 11 expected artifacts are missing
  and 4 source declarations lack reproducible local paths/digests.
- Three clean compiles are byte-identical. Manifest aggregate:
  `26cbe9d21cedafe70653bfaa8134ffa4e481080278e954546cf9710c97a5b00a`;
  three-run digest:
  `018c26be67ea91fe86aeb65374365b5e917eb8c0058235f999d59909bfd08943`.

This closes `FF6-GAP-012` and `FF6-GAP-015`, but not the parent task.
`FF6-GAP-013` remains open for OpenRaster profile/surface depth and
`FF6-GAP-014` remains open for authority-artifact closure. Architecture and
product promotion therefore remain locked.

## Repair checkpoint — authority closure

`TC-FF6-AUTHORITY-CLOSURE-001` is `PASS`:

- all 15 canonical authority records and six contract declaration sets are
  live `MATCH` results;
- clean online and offline reconstructions pass;
- strict ProductContract and three-run capability compilation pass;
- the complete dependency closure includes lock, schemas, authority runtime,
  materializer, research tools, contract generator tools, source bytes, SAL,
  evidence, policy, and enrichment inputs;
- capability aggregate is
  `667cd4cb69773e6746ad46173b53de39c18ef44d39ef7db91c6337d8a3761a73`.

This resolves `FF6-GAP-014` without changing product or promotion state. The
parent remains `NEEDS_REPAIR`: the next deterministic repair is
`TC-FF6-ORA-PROFILE-SURFACE-001` for `FF6-GAP-013`. Compiler-reported profile
applicability gaps for IPYNB, NRRD, XLIFF, and UBL typing remain visible and
must be scheduled after the higher-severity OpenRaster defect; they are not
implicitly closed by authority readiness.
