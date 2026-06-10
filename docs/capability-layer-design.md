# Capability & Feature Understanding Layer — Design

Sprint: FORMAT-FACTORY-CAPABILITY-FEATURE-UNDERSTANDING-LAYER-INVESTIGATIVE-HEALING-001
Run ID: capability-feature-understanding-layer-healing-20260608-e382e5f
Generated: 2026-06-08

---

## Purpose

The Capability & Feature Understanding Layer (CAP) answers the question:

> "Can the system reliably convert Spec Authority, Requirement Authority, repo-local product goals,
> existing implementation, tests, examples, packages, and evidence into verified commercial/FOSS
> product capability maps that drive product implementation tasks?"

It extends the existing Format Understanding Layer (FUL) without replacing it.

---

## Scope Boundary

| Layer | Responsibility | Schemas Namespace |
|-------|---------------|-------------------|
| FUL (existing) | Format-level understanding — structure, probe, parse | `schemas/format-understanding/` |
| CAP (this layer) | Capability-level understanding — what operations exist and how verified | `schemas/capability/` |

---

## Key Files

| File | Purpose |
|------|---------|
| `schemas/capability/capability_status_taxonomy.schema.json` | 18-state taxonomy with verification rules |
| `schemas/capability/capability_record.schema.json` | Per-capability record (35+ fields) |
| `schemas/capability/capability_map.schema.json` | Map container (commercial or foss_reduced) |
| `schemas/capability/capability_gap.schema.json` | Gap ledger entry |
| `schemas/capability/pilot_report.schema.json` | Pilot report structure |
| `tools/capability_layer/__init__.py` | Package declaration |
| `tools/capability_layer/capability_map_generator.py` | Main generator |
| `tools/capability_layer/validate_capability_map.py` | Validator (VAL-001..010) |
| `reports/capability-layer/commercial-capability-map.json` | Commercial .NET records |
| `reports/capability-layer/foss-reduced-capability-map.json` | Python FOSS records |
| `reports/capability-layer/unified-capability-map.json` | All records (commercial + FOSS) |
| `reports/capability-layer/gap-ledger.json` | Gaps derived from missing/unverified records |
| `reports/capability-layer/action-queue.json` | Advisory action queue (never auto-executable) |
| `reports/capability-layer/pilots/` | Per-pilot reports (.md + .json) |
| `reports/capability-layer-plan-healing/` | Plan review, vocabulary, status taxonomy |

---

## Generator Input Sources

The generator (`capability_map_generator.py`) reads from multiple authority sources:

1. **`product-capability-matrix/poc-targets.yaml`** — primary authority source (one input, not final truth)
2. **`src/python/{format}/`** — Python FOSS source introspection (AST scan for exported functions)
3. **`tests/python/{format}/`** — test file detection (count test files)
4. **`examples/python/{format}/`** — example detection
5. **`acquisition-packs/{format}/pack.yaml`** — FUL acquisition pack authority state

Commercial records come from `poc-targets.yaml → commercial_net_products → dotnet_status`.
FOSS records come from `poc-targets.yaml → foss_reduced_products → python_status` plus source introspection of `src/python/`.

---

## Capability Status Taxonomy (18 states)

States in ascending order of evidence:

| State | Counts as Verified | Requires |
|-------|--------------------|---------|
| `missing` | No | — |
| `planned` | No | Taskcard |
| `ai_draft` | No | — |
| `human_goal` | No | Product goal statement |
| `inferred_unverified` | No | — |
| `spec_verified` | Yes | Spec fact ref |
| `requirement_verified` | Yes | Requirement ref |
| `capability_verified` | Yes | Independent validation |
| `implementation_partial` | Yes | Source ref (partial) |
| `implementation_verified` | Yes | Source ref (complete) |
| `test_verified` | Yes | Test ref + passing tests |
| `example_verified` | Yes | Example output + tests |
| `package_verified` | Yes | Package artifact |
| `dogfood_verified` | Yes | Dogfood output validated |
| `blocked` | No | External constraint |
| `unsupported` | No | — |
| `out_of_scope` | No | — |
| `future` | No | — |

**Critical rule**: `ai_draft`, `inferred_unverified`, and `human_goal` are NEVER counted as verified in summary statistics or task selection.

---

## Generator Logic

```
for each commercial format in poc-targets.yaml:
    build commercial records from dotnet_status
    mark test_verified if tests > 0, implementation_verified if implemented, missing otherwise
    emit to commercial-capability-map.json

for each FOSS format in poc-targets.yaml:
    introspect src/python/{format}/ with AST scanner
    compare against python_status from poc-targets.yaml
    mark test_verified if tests > 0 and function found
    emit to foss-reduced-capability-map.json

scan src/python/ for formats NOT in poc-targets.yaml:
    emit as inferred_unverified records with gap "not_in_poc_targets_yaml"

merge → unified-capability-map.json
derive gap ledger from records in (missing, planned, inferred_unverified, ai_draft, blocked) states
derive action queue from gap ledger (all advisory_only: true)
```

---

## Validator Checks (VAL-001..010)

| Check | Type | What it verifies |
|-------|------|-----------------|
| VAL-001 | Hard | Required fields present in all records |
| VAL-002 | Hard | ai_draft/inferred_unverified/human_goal not overclaimed as verified |
| VAL-003 | Hard | Verified records have at least one provenance ref |
| VAL-004 | Hard | implementation_refs path components exist on disk |
| VAL-005 | Hard | test_refs exist on disk for test_verified records |
| VAL-006 | Hard | Commercial and FOSS records never mixed |
| VAL-007 | Advisory | Pilot report files exist |
| VAL-008 | Advisory | Gap ledger entries link to taskcard IDs |
| VAL-009 | Hard | All action queue items have advisory_only=true |
| VAL-010 | Advisory | Evidence declaration includes capability artifacts |

Exit codes: 0=PASS, 1=hard errors, 2=advisory warnings only

---

## Commercial / FOSS Separation

**Rule**: Commercial (.NET) and FOSS/reduced (Python) records are NEVER mixed.

- `commercial-capability-map.json` → only `product_type: "commercial"` records
- `foss-reduced-capability-map.json` → only `product_type: "foss_reduced"` records
- `unified-capability-map.json` → both, distinguished by `product_type` field

The validator (VAL-006) enforces this separation and fails hard if violated.

---

## Action Queue Safety

All items in `action-queue.json` carry `advisory_only: true`. This field must never be removed.
The action queue is advisory only — it suggests next tasks but is not an authoritative execution source.
The authoritative execution source is the supervisor loop (`reports/supervisor/next-sprint.md`).

---

## Known Limitations (as of R126 sprint)

1. **poc-targets.yaml staleness**: FODG, TSV, NDJSON not yet in `foss_reduced_products`. These are
   discovered via source scan and marked `inferred_unverified` / discovered (not in poc-targets).
   Fix: CAP-PROD-005 — update poc-targets.yaml.

2. **Netpbm logical/physical mismatch**: poc-targets.yaml lists "Netpbm" but Python source is split
   into `pbm`, `pgm`, `ppm` packages. Generator correctly omits implementation_refs for the Netpbm
   logical group since `src/python/netpbm/` doesn't exist.

3. **Gap ledger**: Currently 0 gaps because generator only creates records for functions that ARE
   present in source. Missing capabilities (e.g., `write_fodg`) get no record and no gap entry.
   This will be improved by adding expected-capability declarations to per-format matrix files.

4. **Spec/requirement refs**: All records have empty `spec_refs` and `requirement_refs`. The
   requirement authority outputs exist at `requirements-authority/` but are not yet wired into
   the generator (CAP-GEN-006 pending).

---

## Layered Authority Model

```
Format Factory Authority (FINAL)
  └─ Gate registry: registry/format-registry.yaml
  └─ Ledger: reports/r90/product-code-change-ledger.json

Capability Layer (ADVISORY)
  └─ Generator: tools/capability_layer/capability_map_generator.py
  └─ Maps: reports/capability-layer/*.json
  └─ Validator: tools/capability_layer/validate_capability_map.py

Spec/Requirement Authority (ADVISORY)
  └─ tools/specification-authority-layer/
  └─ tools/requirements_authority/

Format Understanding Layer (ADVISORY)
  └─ schemas/format-understanding/
  └─ acquisition-packs/{format}/pack.yaml
```

Supervisor output is always advisory. No gate can be self-approved by the agent.
