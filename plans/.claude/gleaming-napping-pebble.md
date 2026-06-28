# Dual-Lane Product Deepening: Forensics, Governance, and DOM Deepening Plan

**Mission:** Formalize Format Factory's product deepening into two governed lanes — preserving all useful existing work (Lane A) while adding systematic DOM development (Lane B) for document-oriented formats.

**Plan type:** machinery_hardening
**Mission ID:** DUAL-LANE-DEEPENING-001
**Authoritative plan path:** `plans/.claude/gleaming-napping-pebble.md`

---

## Context

Product deepening in Format Factory currently means "expanding gate-checked format products with capabilities from the gap ledger." This is enforced by `product_deepening_gate.py` (4 gates), selected by `capability_feature_compiler.py`, and tracked in `product-deepening-ledger.yaml`.

**What works well:** Gate-checked readiness, gap-driven work selection, spec_qname tracing, analytics rotation suspension.

**What's missing:** No distinction between feature work and DOM/object-model work. Python formats have dict-based read-only wrappers (D1) while .NET has real editable DOM. No tracking of DOM maturity. No mechanism to prevent all sprints going to features while DOM stagnates. Zero consumer proof progress.

**Intended outcome:** A governed dual-lane system where feature depth (Lane A) and DOM depth (Lane B) are tracked, selected, and balanced independently — without replacing any working infrastructure. After machinery is proven, the system must autonomously backfill missing .NET DOM models across the complete active .NET portfolio, proving the dual-lane system works at portfolio scale.

**Terminal completion requires:** Every active .NET product under `src/net/` has a verified final disposition (DOM_NOT_APPLICABLE_VERIFIED, DOM_CEILING_ALREADY_MET_VERIFIED, DOM_BACKFILL_COMPLETED_VERIFIED, VALIDLY_DEFERRED_EXTERNAL_AUTHORITY, or PRODUCT_DEPRECATED_VERIFIED). No UNKNOWN, NOT_AUDITED, PLANNED, or TASK_CREATED dispositions accepted.

---

## Preflight Record

```yaml
preflight:
  repository_root: c:\Users\prora\OneDrive\Documents\GitHub\format-factory
  branch: main
  active_plan_path: plans/.claude/gleaming-napping-pebble.md
  active_plan_title: "Dual-Lane Product Deepening"
  plan_authority_source: per-chat plan mode
  major_section_count: 12 phases
  existing_taskcard_format: "TC-{AREA}-{NNN}"
  existing_lanes: product | machinery (in capability_feature_compiler.py)
  existing_gates: qname, src_layout, spec_mapping, sal, forbidden_bucket, taskcard, evidence
  existing_state_vocabulary: continuation_allowed (bool), qname_compliance_status, etc.
  existing_evidence_model: evidence-declaration.yaml per sprint
  existing_naming_conventions: TC-{LAYER_SLUG}-{SEQUENCE} (e.g., TC-CAP-001)
  duplicate_plan_risk: none — no competing dual-lane plans exist
```

---

## Forensic Findings (preserved from exploration — DO NOT EDIT without evidence)

### Current Product-Deepening Definitions

| Source File | Role | Key Integration |
|---|---|---|
| `registry/product-deepening-ledger.yaml` | Per-format readiness (20 entries, schema v2.0) | `continuation_allowed` bool from 4 gates |
| `tools/supervisor/product_deepening_gate.py` (235 LOC) | Gate evaluator: `check_product_readiness()`, `check_formats_in_gaps()` | Returns `{format, allowed, reason, 7 gate fields}` |
| `tools/supervisor/capability_feature_compiler.py` (289 LOC) | Gap-to-work-item compiler, scoring, `_lane()` returns "product"/"machinery" | Produces `next-work-items.json` with 17-field items |
| `tools/supervisor/check_continuation.py` Check 9 (lines 528-563) | Blocks continuation for non-compliant formats | Imports `check_formats_in_gaps()`, returns STOP if any `allowed=False` |
| `.supervisor/policies.yaml` (331 LOC, 9 sections) | Continuation, approval, product factory policies | `autonomous_continuation` section (lines 231-300) |

### Historical Work Classification

| Classification | Examples | Keep/Repair |
|---|---|---|
| CORE_PRODUCT_VALUE | .NET FODS/FODT DOM, Python parsers, roundtrip tests | KEEP |
| VALID_FORMAT_FEATURE | Sheet/cell access, metadata extraction | KEEP |
| VALID_ARCHITECTURE | QName compliance, spec class creation | KEEP |
| ANALYTICS_ONLY | Suspended mod_prime rotation | DEPRECATED |
| TEST_INFRASTRUCTURE | Batch 117-121 .NET test files (7/batch) | KEEP (useful coverage) |
| BLOCKED_PROGRESS | 9 formats with domain_model_missing | Lane B work needed |

### DOM State Per Format (verified against source)

| Format | Category | Python DOM | .NET DOM | Lane B Ceiling |
|---|---|---|---|---|
| FODS | SPREADSHEET | D2 (models.py 236 LOC: FodsDocument, FodsSheet, FodsCell — spec_qname as plain attr, NOT ClassVar) | D4 (editable XDocument) | D5 |
| FODT | TEXT_DOC | D2 (paragraph/heading classes) | D4 (extensive mutation) | D5 |
| ODS | SPREADSHEET | D1 (models.py 74 LOC: OdsModelDocument only — BUT parser has OdsSheet/OdsRow/OdsCell dataclasses + Compat facades exist) | N/A | D5 |
| ODT | TEXT_DOC | D1 (83 LOC wrapper) | N/A | D5 |
| ABW | TEXT_DOC | D1 (74 LOC wrapper) | N/A | D4 |
| FODG | DRAWING | D1 (68 LOC wrapper) | N/A | D4 |
| FODP | PRESENTATION | D1 (68 LOC wrapper) | N/A | D4 |
| GNUMERIC | SPREADSHEET | D1 (86 LOC wrapper) | N/A | D4 |
| DIF | TABULAR | D1 (82 LOC wrapper) | N/A | D3 |
| SYLK | TABULAR | D1 (90 LOC wrapper) | N/A | D3 |
| XCF | IMAGE | D1 (93 LOC wrapper) | N/A | D3 |
| TOML | CONFIG | D1 (91 LOC wrapper) | N/A | D3 |
| CSV | TABULAR_STREAM | D1 (90 LOC wrapper) | D2 (mutation API) | D1 |
| TSV | TABULAR_STREAM | D1 (85 LOC wrapper) | N/A | D1 |
| NDJSON | RECORD_STREAM | D1 (66 LOC wrapper) | N/A | D1 |
| ZST | CODEC | D1 (108 LOC wrapper) | N/A | D1 |
| PBM/PGM/PPM | IMAGE | D1 (80-89 LOC) | N/A | D1 |
| QOI | IMAGE | D1 (90 LOC wrapper) | N/A | D1 |

**Critical correction from source inspection:** ODS parser (`ods_parser.py` lines 104-128) ALREADY defines `OdsCell`, `OdsRow`, `OdsSheet`, `OdsDocument` as dataclasses with `spec_qname: ClassVar[str]`. Compat facades also exist in `src/python/ods/Compat/`. The D1→D2 upgrade for ODS is a WIRING task (expose parser types through models.py), NOT a class-creation task.

### .NET Product Universe (verified from repository)

**Critical finding:** The product-deepening ledger (`registry/product-deepening-ledger.yaml`) contains ONLY Python entries (20 entries, all `runtime: python`). NO .NET entries exist. The .NET backfill requires ledger schema migration to support `product_id: {FORMAT}-NET` entries.

| Product | Source Root | LOC | Model/ Classes | QName Entries | Tests | DOM Estimate | Category |
|---|---|---|---|---|---|---|---|
| FODS | `src/net/fods/` | 7,571 | 3 (Sheet/Row/Cell) | 12 | 519 | D4 (editable XDocument) | SPREADSHEET |
| FODT | `src/net/fodt/` | 4,896 | 5 (Body/Para/Table/Row/Cell) | 9 | 514 | D4 (editable XDocument) | TEXT_DOC |
| NetPBM | `src/net/netpbm/` | 829 | 5 (Format/Image/Analyzer/Filters/Transforms) | 0 | 488 | D2 (raster model) | IMAGE |
| CSV | `src/net/csv/` | 442 | 4 (Document/Reader/Writer/Record) | 3 | 178 | D1 (record stream) | TABULAR_STREAM |
| TSV | `src/net/tsv/` | 410 | 6 (Document/Reader/Writer/Record) | 3 | 179 | D1 (record stream) | TABULAR_STREAM |
| NDJSON | `src/net/ndjson/` | 505 | 7 (Document/Reader/Writer/Record) | 2 | 186 | D1 (record stream) | RECORD_STREAM |
| ZST | `src/net/zst/` | 418 | 4 (Document/Parser/Writer/Exception) | 3 | 174 | D0 (archive handler) | CODEC |
| HTML | `src/net/html/` | 118 | 1 (HtmlWriter) | 0 | 11 | D0 (export-only writer) | EXPORT_TARGET |
| Markdown | `src/net/markdown/` | 84 | 1 (MarkdownWriter) | 0 | 11 | D0 (export-only writer) | EXPORT_TARGET |
| TXT | `src/net/txt/` | 70 | 1 (TxtWriter) | 0 | 11 | D0 (export-only writer) | EXPORT_TARGET |

**Total:** 10 .NET products, ~15,343 LOC, 2,271 tests.

**.NET DOM Applicability Assessment:**
- **FULL:** FODS (hierarchical spreadsheet DOM), FODT (hierarchical text DOM)
- **PARTIAL:** NetPBM (raster model, not hierarchical document)
- **FLAT:** CSV, TSV, NDJSON (record-stream models)
- **METRICS_ONLY:** ZST (archive/compression handler)
- **NOT_APPLICABLE:** HTML, Markdown, TXT (export-only writers — no input parsing, no document model)

**Gate 11 Status:** FODS and FODT both G11-G APPROVED by Babar Raza (2026-06-05). Publication blocked on remaining gate sub-steps.

### QName Registry State

| Format | QNames Registered | Key Entries |
|---|---|---|
| FODS | 12 | office:document, table:table, table:table-row, table:table-cell, text:p, text:span, etc. |
| FODT | 9+ | office:document, text:p, text:h, text:list, table:table, etc. |
| ODS | 4 | office:document, table:table, table:table-cell, table:table-row |
| Others | 1-3 each | office:document typically |

---

## Lane Definitions

### Lane A — Capability and Feature Deepening

**Purpose:** Expand and harden meaningful product behavior derived from authoritative specifications, capabilities, and approved scope.

**Includes:** Parser support, loaders, validators, inspection APIs, mutation features, same-format save, writers, roundtrip, export/conversion, stream APIs, error handling, package hardening, consumer proof, security/performance, spec-derived features.

**Excludes:** Arbitrary analytics, trivial getters, repeated aliases, test-count inflation, speculative features, generated stubs.

### Lane B — Format DOM and Document Model Deepening

**Purpose:** Build and harden professional, specification-aligned, editable, traversable, serializable, preservation-aware object models for document-oriented formats.

**A valid Format DOM is:** A typed, specification-aligned, editable in-memory representation supporting parsing, navigation, inspection, mutation, validation, serialization, roundtrip preservation, and extension.

**A valid Format DOM is NOT:** A generic dictionary, raw XML wrapper, parsed token list, monolithic document class, metadata-only model, class shells without behavior, parser-internal tree exposed publicly.

### Lane B Maturity Scale

- **D0:** No typed model (raw dict/primitive/opaque data only)
- **D1:** Single Document class wrapping dict or XML (Python: dict wrapper; .NET: XDocument wrapper or parser output container)
- **D2:** Document + typed child classes matching qname registry, with factory method, child accessors, behavioral methods, serializable projection
- **D3:** Navigation/traversal API (find_by, iterate typed children, parent access, deterministic iteration, no public parser-internal leakage)
- **D4:** Mutation API (set_value, add_child, remove_child, ownership invariants, validity checks, writer consumes mutated DOM, unrelated content preserved)
- **D5:** Full roundtrip (parse→DOM→inspect→mutate→serialize→reparse→semantic compare, unknown-content policy, package and clean-consumer proof, no material silent data loss)

**.NET-specific behavioral criteria (do NOT infer maturity from):**
- Class count alone
- Source LOC
- XDocument presence (wrapping XDocument without typed children = D1, not D4)
- Tests existing (tests prove claims; existence is not the claim)
- A method named Save (save without roundtrip proof ≠ D5)
- README or ledger status alone

### Lane A Maturity Scale

- **A0:** No features beyond parse
- **A1:** Load + basic query (from_file, properties)
- **A2:** Load + save same format (roundtrip)
- **A3:** Load + export to another format
- **A4:** Consumer proof (installed package example passes)
- **A5:** Full approved feature scope

### DOM Applicability Tiers

- **FULL:** Hierarchical structure warranting multi-class DOM (FODS, FODT, ODS, ODT, ABW, FODG, FODP, GNUMERIC)
- **PARTIAL:** Some structure, limited hierarchy (DIF, SYLK, XCF, TOML)
- **FLAT:** Tabular/sequential; DOM is just the Document wrapper (CSV, TSV, NDJSON)
- **METRICS_ONLY:** Binary/opaque; model exposes metrics only (ZST, PBM, PGM, PPM, QOI)

---

## Machine State Model

### Parent Taskcard States

```
PROPOSED → READY → IN_PROGRESS → CHILDREN_IN_PROGRESS → INTEGRATION_PENDING → VERIFIED → CLOSED
Any non-closed → BLOCKED | BLOCKED_EXTERNAL | DEFERRED_WITH_REASON
BLOCKED → READY (on unblock)
```

### Child Taskcard States

```
TODO → READY → IN_PROGRESS → IMPLEMENTED → VERIFIED → CLOSED
VERIFIED → REROUTED (quality < 4/5) → IN_PROGRESS (rework)
Any non-closed → BLOCKED | BLOCKED_EXTERNAL
```

### Invalid Transitions (blocked)

- TODO → CLOSED, READY → CLOSED, IMPLEMENTED → CLOSED (must pass VERIFIED)
- Parent CLOSED while mandatory children incomplete
- Child CLOSED without evidence at declared paths

---

## Requirement Inventory

```yaml
REQ-DL-001: Document current product-deepening meaning with evidence
REQ-DL-002: Add lane maturity fields to product-deepening-ledger.yaml (additive, backward-compatible)
REQ-DL-003: Add dual-lane policy to .supervisor/policies.yaml
REQ-DL-004: Add advisory DOM readiness gate (never blocks continuation)
REQ-DL-005: Tag compiled work items with deepening_lane field
REQ-DL-006: Apply lane-balance scoring penalty in work-item compiler
REQ-DL-007: Create format DOM applicability register
REQ-DL-008: Prove dual-lane system works end-to-end (FODS pilot)
REQ-DL-009: Prove Lane B creates real behavioral DOM (ODS pilot)
REQ-DL-010: Prove non-DOM formats correctly skip Lane B
REQ-DL-011: Classify historical product-deepening work into lanes
REQ-DL-012: Update master plan with dual-lane section
REQ-DL-013: Wire lane tracking into sprint closeout
REQ-DL-014: Prove idempotent rerun stability
REQ-DL-015: Discover the complete active .NET product universe from repository truth (src/net/*, registries, .csproj, qname, tests)
REQ-DL-016: Resolve .NET DOM applicability, required ceiling, and current maturity per product with evidence
REQ-DL-017: Build spec/qname/capability-to-.NET-DOM coverage model per applicable product
REQ-DL-018: Compile missing .NET DOM obligations into governed, dependency-aware, idempotent taskcards
REQ-DL-019: Implement missing .NET document roots, typed children, hierarchy, traversal, mutation, serialization, roundtrip up to approved ceiling
REQ-DL-020: Preserve existing .NET public APIs and consumer compatibility during DOM backfill
REQ-DL-021: Prove parser-to-DOM and DOM-to-writer mappings for every applicable .NET product
REQ-DL-022: Prove .NET DOM through focused, integration, negative, roundtrip, package, and clean-consumer tests
REQ-DL-023: Heal all machinery and product defects exposed during .NET portfolio backfill
REQ-DL-024: Reconcile ledgers, qname mappings, capabilities, gaps, READMEs, plans, evidence after each .NET product backfill
REQ-DL-025: Run complete second .NET portfolio pass and prove stable zero-change idempotency
REQ-DL-026: Block terminal plan closure until every active .NET product has verified DOM disposition and full audit is green
```

---

## Dependency DAG

```
TC-DL-001 (forensic report)
  ↓
TC-DL-002 (ledger + policy) ← no code deps, can start after TC-DL-001
  ↓
TC-DL-003 (gate extension) ← depends on TC-DL-002 (reads new ledger fields)
  ↓
TC-DL-004 (compiler lane tagging) ← depends on TC-DL-002 (reads lane fields)
  ↓
TC-DL-005 (applicability register) ← depends on TC-DL-002 (uses lane fields)
  ↓
TC-DL-006 (FODS pilot) ← depends on TC-DL-003 + TC-DL-004 (needs gate + compiler)
  ↓
TC-DL-007 (ODS DOM sprint) ← depends on TC-DL-006 (proves system first)
  ↓
TC-DL-008 (non-DOM proof) ← depends on TC-DL-003 + TC-DL-004
  ↓
TC-DL-009 (historical reclassification) ← independent, can run after TC-DL-002
  ↓
TC-DL-010 (plan + README integration) ← depends on TC-DL-006 results
  ↓
TC-DL-011 (supervisor integration) ← depends on TC-DL-006 (needs proven counters)
  ↓
TC-DL-012 (idempotency + audit) ← depends on ALL above
  ↓
TC-DL-013 (.NET product + DOM inventory) ← depends on TC-DL-012 accepted
  ↓
TC-DL-014 (.NET DOM coverage + gap compilation) ← depends on TC-DL-013
  ↓
TC-DL-015 (.NET backfill machinery pilot) ← depends on TC-DL-014
  ↓
TC-DL-016 (full .NET DOM portfolio backfill) ← depends on TC-DL-015
  ↓
TC-DL-017 (.NET portfolio reconciliation) ← depends on TC-DL-016
  ↓
TC-DL-018 (full .NET portfolio verification) ← depends on TC-DL-017
  ↓
TC-DL-019 (.NET backfill idempotency rerun) ← depends on TC-DL-018
  ↓
TC-DL-020 (terminal dual-lane + .NET portfolio audit) ← depends on ALL prior
```

**Parallel-safe pairs (machinery phase TC-DL-001–012):**
- TC-DL-003 + TC-DL-004 (different files: gate.py vs compiler.py)
- TC-DL-005 + TC-DL-009 (different outputs: register vs classification report)
- TC-DL-008 + TC-DL-009 (different scopes: verification vs reporting)

**Parallel-safe pairs (.NET backfill phase TC-DL-016 children):**
- Per-product backfill children may run in parallel ONLY when different product roots are owned, shared registries have one writer, and no shared namespace project is modified concurrently. Default mode: sequential.

**File ownership locks (machinery phase TC-DL-001–012):**
- `registry/product-deepening-ledger.yaml`: TC-DL-002 (initial), TC-DL-006/007/008 (updates), TC-DL-011 (counter wiring)
- `tools/supervisor/product_deepening_gate.py`: TC-DL-003 exclusively
- `tools/supervisor/capability_feature_compiler.py`: TC-DL-004 exclusively
- `.supervisor/policies.yaml`: TC-DL-002 exclusively
- `src/python/ods/models.py`: TC-DL-007 exclusively
- `src/python/fods/models.py`: TC-DL-006 exclusively

**File ownership locks (.NET backfill phase TC-DL-013–020):**
- `src/net/{format}/**`: owned by the per-product backfill child task for that format
- `tests/net/{format}/**`: owned by same per-product child task
- `registry/product-deepening-ledger.yaml`: single-writer (TC-DL-013 for .NET entries, then per-product updates)
- `shared/qname-registry/{format}.yaml`: single-writer per format
- `plans/master-plan.md`: TC-DL-017 (reconciliation)
- Shared .NET props/targets/solution files: single-writer, sequenced

---

## TC-DL-001: Forensic Discovery Report

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-001
**Owner:** Worker agent
**Objective:** Document what "product deepening" currently means with evidence from repository files.
**Outcome:** `reports/dual-lane-deepening/forensic-discovery-report.md` exists with validated findings.

### TC-DL-001-01: Create forensic report directory and file
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-001
**Purpose:** Produce the forensic report from findings already validated during plan exploration.

**Micro-steps:**

- **MS-DL-001-01-01:** Create directory `reports/dual-lane-deepening/`.
  - Action: `mkdir -p reports/dual-lane-deepening`
  - Completion check: directory exists
  - Next: MS-DL-001-01-02

- **MS-DL-001-01-02:** Write `reports/dual-lane-deepening/forensic-discovery-report.md` containing:
  - Current definitions table (5 source files with paths, roles, integration points)
  - Historical work classification table (6 categories with keep/repair verdict)
  - DOM state per format table (18 rows with verified Python/NET state and ceiling)
  - Product-deepening interpretation analysis (gate-driven, gap-driven, spec-traced)
  - Contradictions found (none material — analytics rotation already suspended)
  - Completion check: file exists, contains all 5 sections, no placeholder text
  - Evidence: the file itself
  - Next: MS-DL-001-01-03

- **MS-DL-001-01-03:** Write `reports/dual-lane-deepening/format-dom-applicability.yaml` with 20 entries, each containing: format_id, product_id, language, format_category, hierarchical_structure, dom_applicability, current_lane_b_maturity, lane_b_ceiling, decision_evidence.
  - Completion check: YAML is valid, 20 entries present, every dom_applicability value is one of FULL/PARTIAL/FLAT/METRICS_ONLY
  - Evidence: the file itself
  - Next: parent acceptance

**Acceptance criteria:**
- [ ] forensic-discovery-report.md exists with all 5 sections
- [ ] format-dom-applicability.yaml has 20 valid entries
- [ ] No placeholder text or TBD markers

**Allowed files:** `reports/dual-lane-deepening/*`
**Forbidden files:** Any source code, any existing registry files

**Rollback:** Delete `reports/dual-lane-deepening/` directory.

---

## TC-DL-002: Ledger + Policy Extension

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-002, REQ-DL-003
**Owner:** Worker agent
**Objective:** Add lane maturity fields to all 20 ledger entries and dual-lane policy to policies.yaml.
**Outcome:** Ledger has 9 new fields per entry; policies.yaml has `dual_lane_deepening` section.

**Preserved behavior:** All existing ledger fields unchanged. All existing policy sections unchanged. `check_product_readiness()` continues to work (new fields are optional).

### TC-DL-002-01: Add lane fields to product-deepening-ledger.yaml
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-002

**Scope:**
- Allowed files: `registry/product-deepening-ledger.yaml`
- Forbidden files: all others

**Micro-steps:**

- **MS-DL-002-01-01:** Read `registry/product-deepening-ledger.yaml` completely. Record current field count per entry, total entry count (expect 20), schema_version (expect "2.0").
  - Completion check: 20 entries confirmed, field list documented
  - Next: MS-DL-002-01-02

- **MS-DL-002-01-02:** For EACH of the 20 entries, add these 9 fields AFTER `pilot_proof` (last existing field):
  ```yaml
  dom_applicability: <FULL|PARTIAL|FLAT|METRICS_ONLY per applicability table>
  lane_a_maturity: <A0-A5 per current feature state>
  lane_b_maturity: <D0-D5 per DOM state table>
  lane_b_ceiling: <D1-D5 per applicability tier>
  execution_mode: AUTO
  last_lane_a_sprint: null
  last_lane_b_sprint: null
  lane_starvation_threshold: 3
  lane_a_consecutive: 0
  lane_b_consecutive: 0
  ```
  - Values per format (from forensic findings):
    - FODS: FULL, A1, D2, D5
    - FODT: FULL, A1, D2, D5
    - ODS: FULL, A1, D1, D5 (parser has typed classes but models.py doesn't expose them → D1)
    - ODT: FULL, A1, D1, D5
    - ABW: FULL, A1, D1, D4
    - FODG: FULL, A0, D1, D4
    - FODP: FULL, A0, D1, D4
    - GNUMERIC: FULL, A1, D1, D4
    - DIF: PARTIAL, A1, D1, D3
    - SYLK: PARTIAL, A1, D1, D3
    - XCF: PARTIAL, A1, D1, D3
    - TOML: PARTIAL, A1, D1, D3
    - CSV: FLAT, A1, D1, D1
    - TSV: FLAT, A1, D1, D1
    - NDJSON: FLAT, A1, D1, D1
    - ZST: METRICS_ONLY, A1, D1, D1
    - PBM: METRICS_ONLY, A1, D1, D1
    - PGM: METRICS_ONLY, A1, D1, D1
    - PPM: METRICS_ONLY, A1, D1, D1
    - QOI: METRICS_ONLY, A1, D1, D1
  - Completion check: `python -c "import yaml; d=yaml.safe_load(open('registry/product-deepening-ledger.yaml')); assert len(d)==20; assert all('dom_applicability' in e for e in d)"`
  - Next: MS-DL-002-01-03

- **MS-DL-002-01-03:** Validate no existing fields were modified. Diff against git HEAD; only additions should appear.
  - Completion check: `git diff registry/product-deepening-ledger.yaml` shows only additions (+ lines), no deletions (- lines) of existing content
  - Evidence: git diff output
  - Next: parent acceptance

**Acceptance criteria:**
- [ ] All 20 entries have 9 new fields
- [ ] YAML parses without errors
- [ ] No existing field values changed
- [ ] dom_applicability values match applicability table
- [ ] lane_b_maturity values match DOM state table

**Rollback:** `git checkout registry/product-deepening-ledger.yaml`

### TC-DL-002-02: Add dual_lane_deepening section to policies.yaml
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-002

**Scope:**
- Allowed files: `.supervisor/policies.yaml`
- Forbidden files: all others

**Micro-steps:**

- **MS-DL-002-02-01:** Read `.supervisor/policies.yaml`. Identify last section (expect `product_factory_gates` ending around line 331). Record section count (expect 9).
  - Completion check: 9 existing sections confirmed
  - Next: MS-DL-002-02-02

- **MS-DL-002-02-02:** Append new section after `product_factory_gates`:
  ```yaml
  # ============================================================
  # Section 10: Dual-Lane Product Deepening
  # ============================================================
  dual_lane_deepening:
    enabled: true
    default_execution_mode: AUTO
    default_starvation_threshold: 3
    dom_classification:
      full: [fods, fodt, ods, odt, abw, fodg, fodp, gnumeric]
      partial: [dif, sylk, xcf, toml]
      flat: [csv, tsv, ndjson]
      metrics_only: [zst, pbm, pgm, ppm, qoi]
    dom_ceiling_by_tier:
      full: D5
      partial: D3
      flat: D1
      metrics_only: D1
    dom_d2_contract:
      required_classes_minimum: 2
      spec_qname_required: true
      from_file_factory_required: true
      child_accessor_required: true
      to_dict_required: true
      behavioral_method_minimum: 1
  ```
  - Completion check: `python -c "import yaml; d=yaml.safe_load(open('.supervisor/policies.yaml')); assert 'dual_lane_deepening' in d; assert d['dual_lane_deepening']['enabled']==True"`
  - Next: MS-DL-002-02-03

- **MS-DL-002-02-03:** Validate no existing sections were modified. Diff should show only additions at end of file.
  - Completion check: git diff shows only + lines after existing content
  - Evidence: git diff output
  - Next: parent acceptance

**Acceptance criteria:**
- [ ] `dual_lane_deepening` section parses correctly
- [ ] 20 formats classified across 4 tiers (8 full + 4 partial + 3 flat + 5 metrics_only = 20)
- [ ] No existing policy sections changed

**Rollback:** `git checkout .supervisor/policies.yaml`

---

## TC-DL-003: Gate Extension — Advisory DOM Readiness

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-004
**Dependencies:** TC-DL-002 (needs lane fields in ledger)
**Owner:** Worker agent
**Objective:** Add `check_dom_readiness()` to product_deepening_gate.py as advisory-only gate.
**Outcome:** Gate evaluator reports DOM readiness without ever blocking continuation.

**Preserved behavior:** `check_product_readiness()` return structure unchanged. `allowed` boolean logic unchanged. Check 9 in check_continuation.py unaffected.

### TC-DL-003-01: Add check_dom_readiness() function
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-003

**Scope:**
- Allowed files: `tools/supervisor/product_deepening_gate.py`
- Forbidden files: all others (especially check_continuation.py)

**Micro-steps:**

- **MS-DL-003-01-01:** Read `tools/supervisor/product_deepening_gate.py` completely (235 LOC). Identify insertion point (after `emit_continuation_signal_gates()`, before `main()`).
  - Completion check: insertion point line number recorded
  - Next: MS-DL-003-01-02

- **MS-DL-003-01-02:** Add function `check_dom_readiness(format_name: str, ledger_path: Path | None = None) -> dict`:
  ```python
  def check_dom_readiness(format_name: str, ledger_path=None):
      """Advisory DOM readiness check. Never blocks continuation."""
      entry = load_ledger(ledger_path).get(format_name.lower(), {})
      dom_app = entry.get("dom_applicability", "FLAT")
      lane_b = entry.get("lane_b_maturity", "D0")
      ceiling = entry.get("lane_b_ceiling", "D1")
      # Count qnames from registry
      qname_path = Path("shared/qname-registry") / f"{format_name.lower()}.yaml"
      qname_count = 0
      if qname_path.exists():
          import yaml as _y
          qname_count = len(_y.safe_load(qname_path.read_text()) or [])
      return {
          "dom_applicability": dom_app,
          "current_maturity": lane_b,
          "ceiling": ceiling,
          "qname_count": qname_count,
          "ready_for_dom_sprint": dom_app in ("FULL", "PARTIAL") and lane_b < ceiling,
          "dom_lane_at_ceiling": lane_b >= ceiling,
          "advisory": True,
      }
  ```
  - Completion check: function exists, returns dict with 7 fields, contains `advisory: True`
  - Next: MS-DL-003-01-03

- **MS-DL-003-01-03:** In `check_product_readiness()`, after the existing `evidence_gate` assignment, add one line:
  ```python
  dom_readiness = check_dom_readiness(format_name, ledger_path)
  ```
  And include `"dom_readiness_gate": dom_readiness` in the return dict.
  - Completion check: return dict has new `dom_readiness_gate` key
  - **CRITICAL:** Do NOT modify `allowed` boolean calculation
  - Next: MS-DL-003-01-04

- **MS-DL-003-01-04:** Test manually: `python tools/supervisor/product_deepening_gate.py --check fods`
  - Expected: output contains `dom_readiness_gate` with `dom_applicability: FULL`, `ready_for_dom_sprint: True`
  - Expected: `allowed` value unchanged from before this change
  - Evidence: command output captured
  - Next: parent acceptance

**Acceptance criteria:**
- [ ] `check_dom_readiness()` exists and returns 7-field dict
- [ ] `check_product_readiness()` result includes `dom_readiness_gate`
- [ ] `allowed` boolean unchanged for all formats
- [ ] `--check fods` returns FULL applicability
- [ ] `--check zst` returns METRICS_ONLY with `dom_lane_at_ceiling: True`

**Rollback:** `git checkout tools/supervisor/product_deepening_gate.py`

---

## TC-DL-004: Lane-Aware Work Selection

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-005, REQ-DL-006
**Dependencies:** TC-DL-002 (needs lane fields in ledger)
**Owner:** Worker agent
**Objective:** Tag compiled work items with `deepening_lane` and apply balance scoring.
**Outcome:** `next-work-items.json` items include lane tags; overrepresented lanes get scoring penalty.

**Preserved behavior:** Existing work item fields unchanged. Existing scoring logic unchanged (additive penalty only). Items without lane classification default to "feature".

### TC-DL-004-01: Add lane classification to capability_feature_compiler.py
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-004

**Scope:**
- Allowed files: `tools/supervisor/capability_feature_compiler.py`
- Forbidden files: all others

**Micro-steps:**

- **MS-DL-004-01-01:** Read `tools/supervisor/capability_feature_compiler.py` (289 LOC). Record: function list, `_gap_to_work_item()` line number, `_score()` line number, work item field list (17 fields).
  - Completion check: function list and line numbers documented
  - Next: MS-DL-004-01-02

- **MS-DL-004-01-02:** Add `_classify_deepening_lane(gap: dict) -> str` function (after existing `_lane()` function):
  ```python
  def _classify_deepening_lane(gap: dict) -> str:
      """Classify gap as feature or dom deepening work."""
      gap_type = gap.get("gap_type", "")
      cap = gap.get("capability_name", "").lower()
      if gap_type in ("spec_parity_gap", "architecture_only", "missing_qname_registration"):
          return "dom"
      if any(kw in cap for kw in ("object_model", "dom_", "navigation", "mutation", "spec_class")):
          return "dom"
      return "feature"
  ```
  - Completion check: function exists, returns "feature" or "dom"
  - Next: MS-DL-004-01-03

- **MS-DL-004-01-03:** In `_gap_to_work_item()`, add `"deepening_lane": _classify_deepening_lane(gap)` to the returned dict (after existing `"spec_facts"` field).
  - Completion check: work item dict now has 18 fields (was 17)
  - Next: MS-DL-004-01-04

- **MS-DL-004-01-04:** Add `_lane_balance_penalty(lane: str, format_name: str) -> int` function:
  ```python
  def _lane_balance_penalty(lane: str, format_name: str) -> int:
      """Soft penalty for overrepresented lane (starvation prevention)."""
      import yaml
      ledger_path = Path("registry/product-deepening-ledger.yaml")
      if not ledger_path.exists():
          return 0
      ledger = yaml.safe_load(ledger_path.read_text()) or []
      entry = next((e for e in ledger if e.get("format") == format_name.lower()), {})
      mode = entry.get("execution_mode", "AUTO")
      if mode == "FEATURE_ONLY" and lane == "dom":
          return 999
      if mode == "DOM_ONLY" and lane == "feature":
          return 999
      a = entry.get("lane_a_consecutive", 0)
      b = entry.get("lane_b_consecutive", 0)
      threshold = entry.get("lane_starvation_threshold", 3)
      if lane == "feature" and a - b >= threshold:
          return 15
      if lane == "dom" and b - a >= threshold:
          return 15
      return 0
  ```
  - Completion check: function exists, returns int
  - Next: MS-DL-004-01-05

- **MS-DL-004-01-05:** In `_score()`, after existing scoring, add:
  ```python
  fmt = gap.get("format", gap.get("product_id", "")).split("-")[0].lower()
  dl = _classify_deepening_lane(gap)
  score += _lane_balance_penalty(dl, fmt)
  ```
  - Completion check: `_score()` includes balance penalty
  - Next: MS-DL-004-01-06

- **MS-DL-004-01-06:** Test: run compiler in dry-run mode and verify `deepening_lane` appears in output items.
  - Command: `python tools/supervisor/capability_feature_compiler.py --dry-run` (or equivalent)
  - Expected: each item in output has `deepening_lane: "feature"` or `deepening_lane: "dom"`
  - Evidence: command output
  - Next: parent acceptance

**Acceptance criteria:**
- [ ] `_classify_deepening_lane()` exists
- [ ] `_lane_balance_penalty()` exists
- [ ] Work items have `deepening_lane` field
- [ ] Scoring includes balance penalty
- [ ] Dry-run shows lane tags in output

**Rollback:** `git checkout tools/supervisor/capability_feature_compiler.py`

---

## TC-DL-005: Format DOM Applicability Register

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-007
**Dependencies:** TC-DL-002 (uses lane fields as source)
**Owner:** Worker agent
**Objective:** Create the definitive applicability register with evidence per format.
**Outcome:** `reports/dual-lane-deepening/format-dom-applicability.yaml` with 20 validated entries.

**Note:** This overlaps with MS-DL-001-01-03. If TC-DL-001-01 is already completed, this taskcard validates and enriches that file. If not, this taskcard creates it.

### TC-DL-005-01: Write applicability register
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-005

**Micro-steps:**

- **MS-DL-005-01-01:** If `reports/dual-lane-deepening/format-dom-applicability.yaml` already exists (from TC-DL-001), read it and verify 20 entries. If not, create it.
  - Each entry: format_id, product_id, language, format_category, hierarchical_structure (bool), dom_applicability, decision_evidence (string citing spec or structure), current_lane_b_maturity, lane_b_ceiling
  - Completion check: YAML valid, 20 entries, all fields present
  - Next: parent acceptance

**Acceptance criteria:**
- [ ] 20 entries, each with 9 fields
- [ ] dom_applicability matches ledger entries
- [ ] decision_evidence is non-empty for each entry

**Rollback:** Delete file.

---

## TC-DL-006: FODS Python Pilot — Validate Dual-Lane System

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-008
**Dependencies:** TC-DL-003 (gate), TC-DL-004 (compiler)
**Owner:** Worker agent
**Objective:** Prove dual-lane tracking works end-to-end using FODS (already at D2+).
**Outcome:** Gate reports DOM readiness for FODS; compiler tags FODS items with lane; lane counters track correctly.

### TC-DL-006-01: Verify FODS gate reports DOM readiness
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-006

**Micro-steps:**

- **MS-DL-006-01-01:** Run `python tools/supervisor/product_deepening_gate.py --check fods`.
  - Expected output includes: `dom_readiness_gate: {dom_applicability: FULL, current_maturity: D2, ceiling: D5, ready_for_dom_sprint: True}`
  - Expected: `allowed: True` (existing gates all pass for FODS)
  - Evidence: command output
  - Next: MS-DL-006-01-02

- **MS-DL-006-01-02:** Run compiler and verify FODS work items have `deepening_lane` tag.
  - Evidence: work item JSON showing lane field
  - Next: parent acceptance

**Acceptance criteria:**
- [ ] Gate reports FODS as dom_applicability=FULL, ready_for_dom_sprint=True
- [ ] Compiler tags FODS items with deepening_lane

### TC-DL-006-02: Advance FODS Python DOM to D3 (traversal)
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-006

**Purpose:** Prove a Lane B sprint produces real behavioral DOM improvement.

**Scope:**
- Allowed files: `src/python/fods/models.py`, `tests/python/fods/test_*.py`
- Forbidden files: parser, codec, __init__.py, .NET source

**Micro-steps:**

- **MS-DL-006-02-01:** Read `src/python/fods/models.py` (236 LOC). Identify current behavioral methods on FodsSheet: `cells()` iterator, `cell_at(row, col)`. These are D2 methods.
  - Completion check: current method list documented
  - Next: MS-DL-006-02-02

- **MS-DL-006-02-02:** Add D3 traversal methods to `FodsSheet`:
  ```python
  def find_cells_by_value(self, value: Any) -> list[FodsCell]:
      """Find all cells whose value matches the given value."""
      return [c for c in self.cells() if c.value == value]

  def iter_rows(self) -> Iterator[list[FodsCell]]:
      """Iterate rows, yielding each as a list of typed FodsCell objects."""
      for row in self.rows:
          row_cells = row.get("cells", []) if isinstance(row, dict) else row
          yield [FodsCell(c) for c in row_cells]
  ```
  - Completion check: 2 new methods added, file parses without errors
  - Next: MS-DL-006-02-03

- **MS-DL-006-02-03:** Add D3 traversal method to `FodsDocument`:
  ```python
  def find_sheet_by_index(self, index: int) -> FodsSheet | None:
      """Get sheet by zero-based index, or None if out of range."""
      sheets = self._data.get("sheets", [])
      if 0 <= index < len(sheets):
          return FodsSheet(sheets[index])
      return None
  ```
  - Completion check: method added
  - Next: MS-DL-006-02-04

- **MS-DL-006-02-04:** Write test file `tests/python/fods/test_fods_dom_d3_traversal.py`:
  - Test `find_cells_by_value()` returns correct FodsCell list
  - Test `iter_rows()` returns typed FodsCell rows
  - Test `find_sheet_by_index()` returns FodsSheet or None
  - Use existing sample: `samples/by-format/fods/valid/` (or create minimal dict fixture)
  - Completion check: test file exists, imports correctly
  - Next: MS-DL-006-02-05

- **MS-DL-006-02-05:** Run tests: `.venv/Scripts/pytest tests/python/fods/test_fods_dom_d3_traversal.py -v`
  - Expected: all tests PASS
  - Evidence: test output
  - Next: MS-DL-006-02-06

- **MS-DL-006-02-06:** Update FODS ledger entry: `lane_b_maturity: D3`, `last_lane_b_sprint: <sprint_id>`, `lane_b_consecutive: 1`
  - Completion check: ledger entry updated, YAML valid
  - Next: parent acceptance

**Acceptance criteria:**
- [ ] 3 new traversal methods (find_cells_by_value, iter_rows, find_sheet_by_index)
- [ ] All tests pass
- [ ] Ledger updated to D3
- [ ] No existing methods/tests broken

**Rollback:** `git checkout src/python/fods/models.py registry/product-deepening-ledger.yaml`; delete test file.

---

## TC-DL-007: ODS DOM Sprint — Wire Existing Types to D2

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-009
**Dependencies:** TC-DL-006 (proves system first)
**Owner:** Worker agent
**Objective:** Advance ODS from D1 to D2 by exposing existing parser types through models.py.
**Outcome:** `OdsModelDocument.sheets` returns typed `OdsSheet` objects with cell access.

**Critical finding:** ODS parser (`ods_parser.py` lines 104-128) ALREADY has `OdsCell`, `OdsRow`, `OdsSheet`, `OdsDocument` dataclasses with `spec_qname: ClassVar[str]`. Compat facades exist in `Compat/`. This is a WIRING task, not class creation.

### TC-DL-007-01: Wire parser types into models.py
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-007

**Scope:**
- Allowed files: `src/python/ods/models.py`, `tests/python/ods/test_*.py`
- Forbidden files: `src/python/ods/ods_parser.py` (do not modify parser), Compat/ files

**Micro-steps:**

- **MS-DL-007-01-01:** Read `src/python/ods/ods_parser.py` lines 104-128. Confirm `OdsCell`, `OdsRow`, `OdsSheet`, `OdsDocument` are dataclasses with spec_qname.
  - Record: OdsSheet has `name: str`, `rows: list[OdsRow]`. OdsRow has `cells: list[OdsCell]`. OdsCell has `value`, `value_type`, `text`.
  - Completion check: parser type structure documented
  - Next: MS-DL-007-01-02

- **MS-DL-007-01-02:** In `src/python/ods/models.py`, modify `get_sheet(index)` to return typed wrapper:
  ```python
  def get_sheet(self, index: int) -> "OdsSheetModel | None":
      """Return typed OdsSheetModel at index, or None."""
      if 0 <= index < len(self._parsed.sheets):
          return OdsSheetModel(self._parsed.sheets[index])
      return None

  def sheets(self) -> list["OdsSheetModel"]:
      """Return all sheets as typed OdsSheetModel objects."""
      return [OdsSheetModel(s) for s in self._parsed.sheets]
  ```
  - Completion check: `sheets()` method exists returning typed list
  - Next: MS-DL-007-01-03

- **MS-DL-007-01-03:** Add `OdsSheetModel` class to models.py (wrapping parser's OdsSheet):
  ```python
  class OdsSheetModel:
      """Typed wrapper for ODS sheet with cell access."""
      spec_qname: ClassVar[str] = "table:table"
      spec_fact_ref: ClassVar[str] = "FACT-FODS-004"

      def __init__(self, sheet) -> None:
          self._sheet = sheet

      @property
      def name(self) -> str:
          return self._sheet.name

      @property
      def row_count(self) -> int:
          return len(self._sheet.rows)

      def cells(self) -> Iterator:
          """Iterate all cells as OdsCellModel objects."""
          for row in self._sheet.rows:
              for cell in row.cells:
                  yield OdsCellModel(cell)

      def cell_at(self, row: int, col: int):
          """Get cell at (row, col) or None."""
          if 0 <= row < len(self._sheet.rows):
              cells = self._sheet.rows[row].cells
              if 0 <= col < len(cells):
                  return OdsCellModel(cells[col])
          return None

      def to_dict(self) -> dict:
          return {"name": self.name, "row_count": self.row_count}
  ```
  - Completion check: class exists with spec_qname, name, cells(), cell_at(), to_dict()
  - Next: MS-DL-007-01-04

- **MS-DL-007-01-04:** Add `OdsCellModel` class to models.py:
  ```python
  class OdsCellModel:
      """Typed wrapper for ODS cell."""
      spec_qname: ClassVar[str] = "table:table-cell"
      spec_fact_ref: ClassVar[str] = "FACT-FODS-006"

      def __init__(self, cell) -> None:
          self._cell = cell

      @property
      def value(self):
          return self._cell.value

      @property
      def value_type(self) -> str:
          return self._cell.value_type

      @property
      def text(self) -> str:
          return self._cell.text

      def to_dict(self) -> dict:
          return {"value": self.value, "value_type": self.value_type, "text": self.text}
  ```
  - Completion check: class exists with spec_qname, value, value_type, text, to_dict()
  - Next: MS-DL-007-01-05

- **MS-DL-007-01-05:** Add necessary imports to models.py: `from typing import Iterator, ClassVar`
  - Completion check: imports present, file parses without errors
  - Next: MS-DL-007-01-06

- **MS-DL-007-01-06:** Write test file `tests/python/ods/test_ods_dom_d2.py`:
  - Test `OdsModelDocument.sheets()` returns `list[OdsSheetModel]`
  - Test `OdsSheetModel.name` returns string
  - Test `OdsSheetModel.cells()` yields `OdsCellModel` objects
  - Test `OdsCellModel.value` returns correct value
  - Test `OdsCellModel.spec_qname == "table:table-cell"`
  - Test `OdsSheetModel.to_dict()` returns dict with name and row_count
  - Use existing ODS sample file from `samples/by-format/ods/` or oracle test fixtures
  - Completion check: test file exists
  - Next: MS-DL-007-01-07

- **MS-DL-007-01-07:** Run tests: `.venv/Scripts/pytest tests/python/ods/test_ods_dom_d2.py -v`
  - Expected: all tests PASS
  - Evidence: test output
  - Next: MS-DL-007-01-08

- **MS-DL-007-01-08:** Run existing ODS tests to verify no regression: `.venv/Scripts/pytest tests/python/ods/ -v`
  - Expected: all existing tests still PASS
  - Evidence: test output
  - Next: MS-DL-007-01-09

- **MS-DL-007-01-09:** Update ODS ledger entry: `lane_b_maturity: D2`, `last_lane_b_sprint: <sprint_id>`, `lane_b_consecutive: 1`
  - Completion check: ledger entry updated, YAML valid
  - Next: parent acceptance

**D2 contract verification:**
- [ ] Document class (OdsModelDocument) has spec_qname
- [ ] At least one child class (OdsSheetModel) with spec_qname
- [ ] Typed child accessor (sheets()) on Document
- [ ] At least one behavioral method (cells(), cell_at()) on child
- [ ] to_dict() serialization on all classes

**Acceptance criteria:**
- [ ] OdsSheetModel and OdsCellModel classes exist with spec_qname
- [ ] OdsModelDocument.sheets() returns typed objects
- [ ] All new tests pass
- [ ] All existing ODS tests pass (regression)
- [ ] Ledger updated to D2

**Rollback:** `git checkout src/python/ods/models.py registry/product-deepening-ledger.yaml`; delete test file.

---

## TC-DL-008: Non-Document Format Proof

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-010
**Dependencies:** TC-DL-003 (gate), TC-DL-004 (compiler)
**Owner:** Worker agent
**Objective:** Prove METRICS_ONLY and FLAT formats correctly skip Lane B.
**Outcome:** Gate reports "DOM lane at ceiling" for ZST/CSV; compiler routes all work to Lane A.

### TC-DL-008-01: Verify non-DOM gate and compiler behavior
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-008

**Micro-steps:**

- **MS-DL-008-01-01:** Run `python tools/supervisor/product_deepening_gate.py --check zst`.
  - Expected: `dom_readiness_gate: {dom_applicability: METRICS_ONLY, current_maturity: D1, ceiling: D1, dom_lane_at_ceiling: True, ready_for_dom_sprint: False}`
  - Evidence: command output
  - Next: MS-DL-008-01-02

- **MS-DL-008-01-02:** Run `python tools/supervisor/product_deepening_gate.py --check csv`.
  - Expected: `dom_readiness_gate: {dom_applicability: FLAT, dom_lane_at_ceiling: True, ready_for_dom_sprint: False}`
  - Evidence: command output
  - Next: MS-DL-008-01-03

- **MS-DL-008-01-03:** Verify compiler does not apply starvation penalty for ceiling-at-D1 formats (no `lane_b_consecutive` matters when ceiling reached).
  - Evidence: dry-run output showing no penalty applied to ZST/CSV items
  - Next: parent acceptance

**Acceptance criteria:**
- [ ] ZST: dom_lane_at_ceiling=True, ready_for_dom_sprint=False
- [ ] CSV: dom_lane_at_ceiling=True, ready_for_dom_sprint=False
- [ ] No false starvation warnings for ceiling-met formats

---

## TC-DL-009: Historical Task Reclassification

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-011
**Dependencies:** TC-DL-002 (needs lane definitions)
**Owner:** Worker agent
**Objective:** Classify prior product-deepening work into lanes without rewriting history.
**Outcome:** `reports/dual-lane-deepening/historical-task-classification.yaml`

### TC-DL-009-01: Classify recent sprints
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-009

**Micro-steps:**

- **MS-DL-009-01-01:** Scan `.local/evidences/` for the 10 most recent evidence declarations. For each, extract: sprint_id, format(s), work items, changed files.
  - Completion check: 10 sprints cataloged
  - Next: MS-DL-009-01-02

- **MS-DL-009-01-02:** For each work item, classify: `lane: feature | dom | shared | non_deepening`, `value_classification`, `keep_or_repair`.
  - Classification rules:
    - .NET test files → feature (test coverage)
    - Python iterator/workflow files → feature (test infrastructure)
    - spec class creation → dom
    - qname compliance → dom
    - parser features → feature
    - analytics functions → non_deepening (deprecated)
  - Completion check: all items classified
  - Next: MS-DL-009-01-03

- **MS-DL-009-01-03:** Write `reports/dual-lane-deepening/historical-task-classification.yaml`.
  - Completion check: YAML valid, all sprints represented
  - Next: parent acceptance

**Acceptance criteria:**
- [ ] 10 recent sprints classified
- [ ] Every work item has lane and value_classification
- [ ] No source code changes (reporting only)

---

## TC-DL-010: Plan Integration + README Updates

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-012
**Dependencies:** TC-DL-006 (needs pilot results)
**Owner:** Worker agent
**Objective:** Update master plan and format READMEs with dual-lane status.

### TC-DL-010-01: Add dual-lane section to master plan
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-010

**Scope:**
- Allowed files: `plans/master-plan.md`, `src/net/fods/README.md`
- Forbidden files: source code, registry files

**Micro-steps:**

- **MS-DL-010-01-01:** Read `plans/master-plan.md` and identify insertion point for dual-lane section (after existing product-deepening references).
  - Next: MS-DL-010-01-02

- **MS-DL-010-01-02:** Add concise dual-lane section (max 30 lines):
  ```markdown
  ## Dual-Lane Product Deepening

  Product deepening operates in two governed lanes:
  - **Lane A (Features):** Capability expansion, export, consumer proof
  - **Lane B (DOM):** Specification-aligned typed object model

  Lane maturity tracked independently (A0-A5, D0-D5).
  DOM applicable for FULL/PARTIAL formats only.
  Policy: `.supervisor/policies.yaml` → `dual_lane_deepening`
  Ledger: `registry/product-deepening-ledger.yaml` (dom_applicability, lane_*_maturity fields)
  ```
  - Next: MS-DL-010-01-03

- **MS-DL-010-01-03:** Add dual-lane status to `src/net/fods/README.md` (after "What Remains for Gate 11"):
  ```markdown
  ## Product Maturity (Dual-Lane)
  - **Lane A (Features):** A1 — Load + basic query
  - **Lane B (DOM):** D4 — Editable XDocument DOM with mutation
  - **DOM Applicable:** Yes (FULL — hierarchical XML spreadsheet)
  ```
  - Next: parent acceptance

**Acceptance criteria:**
- [ ] Master plan has dual-lane section
- [ ] FODS README has maturity status
- [ ] No existing content overwritten

---

## TC-DL-011: Supervisor Integration — Lane Counter Updates

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-013
**Dependencies:** TC-DL-006 (needs proven system)
**Owner:** Worker agent
**Objective:** Wire lane tracking into sprint closeout in autonomous_cycle.py.

### TC-DL-011-01: Add lane counter update to autonomous_cycle.py
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-011

**Scope:**
- Allowed files: `tools/supervisor/autonomous_cycle.py`
- Forbidden files: check_continuation.py, product_deepening_gate.py

**Micro-steps:**

- **MS-DL-011-01-01:** Read `tools/supervisor/autonomous_cycle.py`. Find the sprint acceptance point (where exit code 0 is determined after grading).
  - Completion check: insertion point identified
  - Next: MS-DL-011-01-02

- **MS-DL-011-01-02:** After sprint acceptance, add ~20 lines:
  ```python
  # Update dual-lane counters in product-deepening ledger
  def _update_lane_counters(declaration, ledger_path):
      """Increment lane counters after accepted sprint."""
      import yaml
      if not ledger_path.exists():
          return
      items = declaration.get("planned_work_items", [])
      lanes_by_format = {}
      for item in items:
          if item.get("status") != "completed":
              continue
          dl = item.get("deepening_lane", "feature")
          fmt = item.get("format", "").lower()
          if fmt:
              lanes_by_format.setdefault(fmt, set()).add(dl)
      if not lanes_by_format:
          return
      ledger = yaml.safe_load(ledger_path.read_text()) or []
      for entry in ledger:
          fmt = entry.get("format", "").lower()
          if fmt in lanes_by_format:
              for lane in lanes_by_format[fmt]:
                  if lane == "dom":
                      entry["lane_b_consecutive"] = entry.get("lane_b_consecutive", 0) + 1
                      entry["lane_a_consecutive"] = 0
                      entry["last_lane_b_sprint"] = declaration.get("sprint_id")
                  else:
                      entry["lane_a_consecutive"] = entry.get("lane_a_consecutive", 0) + 1
                      entry["lane_b_consecutive"] = 0
                      entry["last_lane_a_sprint"] = declaration.get("sprint_id")
      ledger_path.write_text(yaml.dump(ledger, default_flow_style=False, allow_unicode=True))
  ```
  - Completion check: function exists, wired at acceptance point
  - Next: MS-DL-011-01-03

- **MS-DL-011-01-03:** Add evidence declaration schema note: `deepening_lane` is optional field on work items. No schema enforcement (advisory).
  - Next: parent acceptance

**Acceptance criteria:**
- [ ] `_update_lane_counters()` function exists
- [ ] Called after sprint acceptance (exit code 0)
- [ ] Increments correct counter, resets other
- [ ] Handles missing fields gracefully (`.get()` with defaults)

**Rollback:** `git checkout tools/supervisor/autonomous_cycle.py`

---

## TC-DL-012: Idempotency + Final Audit

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-014
**Dependencies:** ALL previous taskcards
**Owner:** Worker agent
**Objective:** Prove rerun stability and audit completeness.

### TC-DL-012-01: Idempotency verification
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-012

**Micro-steps:**

- **MS-DL-012-01-01:** Run gate evaluator for FODS, ODS, ZST. Record outputs. Run again. Compare. Must be identical.
  - Evidence: two runs' outputs compared
  - Next: MS-DL-012-01-02

- **MS-DL-012-01-02:** Run compiler in dry-run. Record output. Run again. Compare. Must be identical.
  - Evidence: two runs' outputs compared
  - Next: MS-DL-012-01-03

- **MS-DL-012-01-03:** Re-read ledger. Verify no duplicate fields on any entry.
  - Evidence: validation script output
  - Next: MS-DL-012-01-04

- **MS-DL-012-01-04:** Verify all FULL formats have lane fields. Verify all METRICS_ONLY formats have `lane_b_maturity == lane_b_ceiling`.
  - Evidence: validation output
  - Next: MS-DL-012-01-05

- **MS-DL-012-01-05:** Write `reports/dual-lane-deepening/idempotency-verdict.md` with PASS/FAIL per check.
  - Next: parent acceptance

**Acceptance criteria:**
- [ ] Gate evaluator produces identical output on rerun
- [ ] Compiler produces identical output on rerun
- [ ] No duplicate fields in ledger
- [ ] All METRICS_ONLY formats at ceiling
- [ ] Idempotency verdict: PASS

---

## .NET DOM Portfolio Backfill Program (Lane B — .NET Execution Phase)

This is NOT a third product-deepening lane. It is a mandatory portfolio execution phase of Lane B that uses the completed dual-lane machinery to bring every applicable active .NET product to its evidence-backed DOM maturity ceiling.

### .NET DOM Applicability Values

- **FULL:** Hierarchically structured document/spreadsheet/presentation/drawing (evaluated independently from Python)
- **PARTIAL:** Meaningful typed structure exists but large DOM hierarchy would be artificial
- **FLAT:** Typed document + records/rows is the meaningful ceiling
- **METRICS_ONLY:** Public model exposes bounded metadata or codec state, not a document tree
- **NOT_APPLICABLE:** Export-only writers with no input parsing or document model (evidence required)

### .NET Portfolio Required Terminal Conditions

```yaml
net_portfolio_terminal_conditions:
  UNACCOUNTED_ACTIVE_NET_PRODUCTS: 0
  UNVERIFIED_NET_DOM_OBLIGATIONS: 0
  UNRESOLVED_LOCALLY_ACTIONABLE_NET_DOM_GAPS: 0
```

Every active .NET product must reach exactly one verified final disposition:
- `DOM_NOT_APPLICABLE_VERIFIED` — export-only or no document model warranted
- `DOM_CEILING_ALREADY_MET_VERIFIED` — already at target maturity with proof
- `DOM_BACKFILL_COMPLETED_VERIFIED` — backfill implemented and proven
- `VALIDLY_DEFERRED_EXTERNAL_AUTHORITY` — requires Gate 11 or similar external decision
- `PRODUCT_DEPRECATED_VERIFIED` — product is deprecated with evidence

### Backfill Execution Waves

```
WAVE NET-0: Inventory + ledger schema migration (TC-DL-013)
WAVE NET-1: Coverage model + gap compilation (TC-DL-014)
WAVE NET-2: Backfill machinery pilots (TC-DL-015)
WAVE NET-3: Full portfolio backfill — FULL products first (TC-DL-016)
WAVE NET-4: Full portfolio backfill — PARTIAL products (TC-DL-016)
WAVE NET-5: FLAT/METRICS_ONLY/NOT_APPLICABLE validation (TC-DL-016)
WAVE NET-6: Package + clean-consumer proof (TC-DL-016)
WAVE NET-7: Reconciliation (TC-DL-017)
WAVE NET-8: Full verification (TC-DL-018)
WAVE NET-9: Idempotency rerun (TC-DL-019)
WAVE NET-10: Terminal audit (TC-DL-020)
```

Product membership in waves is determined by discovery, NOT hard-coded.

---

## TC-DL-013: .NET Product and DOM Inventory

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-015, REQ-DL-016
**Dependencies:** TC-DL-012 accepted (machinery audit green)
**Owner:** Worker agent
**Objective:** Discover every active `src/net/{format}` product and determine its evidence-backed DOM applicability, current maturity, target ceiling, and architecture state.
**Outcome:** Complete .NET product inventory with zero unaccounted source roots.

### TC-DL-013-01: Discover .NET product universe from repository truth
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-013

**Scope:**
- Allowed: READ all `src/net/`, `tests/net/`, `shared/qname-registry/`, `registry/`, `.csproj` files
- Forbidden: modifying any source code

**Micro-steps:**

- **MS-DL-013-01-01:** Enumerate all directories under `src/net/`. For each, record: path, .csproj existence, target framework, source file count, Model/ subdirectory, key classes (Document/Parser/Writer), test root existence.
  - Completion check: every `src/net/*/` directory accounted for
  - Next: MS-DL-013-01-02

- **MS-DL-013-01-02:** Cross-reference with registries: format-registry.yaml, product-deepening-ledger.yaml (note: currently Python-only), qname registries (dotnet_file entries), gap-ledger.json, Gate records.
  - Completion check: registry coverage documented per product
  - Next: MS-DL-013-01-03

- **MS-DL-013-01-03:** Classify each product: `active`, `export_only`, `deprecated`, `unknown`. Evidence required for each classification.
  - Completion check: zero UNKNOWN classifications remain
  - Next: MS-DL-013-01-04

- **MS-DL-013-01-04:** For each active product, determine DOM applicability (FULL/PARTIAL/FLAT/METRICS_ONLY/NOT_APPLICABLE) based on format category, source structure, and specification hierarchy — NOT by copying Python classification.
  - Evidence: cite format specification, source structure, existing typed classes
  - Completion check: every active product has applicability with evidence
  - Next: MS-DL-013-01-05

- **MS-DL-013-01-05:** Calculate current .NET DOM maturity (D0-D5) per product based on behavioral criteria (not class count or LOC). Record: document root, typed children, collections, traversal, mutation, writer mapping, roundtrip proof.
  - Completion check: every product has maturity assessment with behavioral evidence
  - Next: MS-DL-013-01-06

- **MS-DL-013-01-06:** Write `reports/dual-lane-deepening/net-dom-product-inventory.yaml` with per-product records containing: product_id, format_id, source_root, project_paths, test_roots, package_identity, target_frameworks, active (bool), format_category, dom_applicability, required_dom_ceiling, current_dom_maturity, existing_document_roots, existing_public_dom_types, parser_paths, writer_paths, qname_registry, gap_records, current_gate, final_disposition (initially null for applicable products).
  - Completion check: YAML valid, count matches enumerated products, `ACTIVE_NET_SOURCE_DIRECTORIES == INVENTORIED_NET_PRODUCTS + VALID_EXCLUSIONS`
  - Next: parent acceptance

### TC-DL-013-02: Migrate ledger schema for .NET entries
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-013

**Scope:**
- Allowed files: `registry/product-deepening-ledger.yaml`
- Forbidden: modifying existing Python entries' values

**Micro-steps:**

- **MS-DL-013-02-01:** Determine ledger identity model. Current: `product_id: {FORMAT}-PYTHON`. Required: add `{FORMAT}-NET` entries for each active .NET product. Confirm no field collisions.
  - Completion check: identity model documented
  - Next: MS-DL-013-02-02

- **MS-DL-013-02-02:** Add .NET product entries to ledger for each active product (FODS-NET, FODT-NET, NETPBM-NET, CSV-NET, TSV-NET, NDJSON-NET, ZST-NET). Use `runtime: dotnet`. Set lane fields from inventory. Export-only products (HTML, Markdown, TXT) get entries with `dom_applicability: NOT_APPLICABLE`, `continuation_allowed: false`, `blockers: ["export_only_no_document_model"]`.
  - Completion check: .NET entries present, YAML valid, existing Python entries unchanged
  - Next: MS-DL-013-02-03

- **MS-DL-013-02-03:** Validate: `git diff registry/product-deepening-ledger.yaml` shows only additions, no modifications to existing Python entries.
  - Evidence: git diff output
  - Next: parent acceptance

**Acceptance criteria:**
- [ ] All `src/net/*/` directories accounted for (10 products)
- [ ] Net-dom-product-inventory.yaml has 10 entries with all required fields
- [ ] Zero UNKNOWN classifications
- [ ] DOM applicability decided from evidence (not copied from Python)
- [ ] Current maturity based on behavioral criteria
- [ ] Ledger has .NET entries with correct runtime and lane fields
- [ ] No existing Python ledger entries modified

**Rollback:** Delete net-dom-product-inventory.yaml; `git checkout registry/product-deepening-ledger.yaml`

---

## TC-DL-014: .NET DOM Coverage and Gap Compilation

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-017, REQ-DL-018
**Dependencies:** TC-DL-013
**Owner:** Worker agent
**Objective:** Build per-product coverage model and compile missing DOM obligations into taskcards.
**Outcome:** Coverage model, gap ledger, and generated backfill taskcards for every applicable .NET product.

### TC-DL-014-01: Build .NET DOM coverage model
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-014

**Micro-steps:**

- **MS-DL-014-01-01:** For each applicable .NET product, analyze: specification concepts in scope, qnames total, qnames mapped to types, required DOM types, implemented DOM types, parser mappings (required vs implemented), writer mappings, typed collections, traversal contracts, mutation contracts, roundtrip contracts, package proof, consumer proof.
  - Completion check: coverage data collected per product
  - Next: MS-DL-014-01-02

- **MS-DL-014-01-02:** Write `reports/dual-lane-deepening/net-dom-coverage.yaml` with per-product coverage records.
  - Completion check: YAML valid, every applicable product has coverage entry
  - Next: parent acceptance

### TC-DL-014-02: Compile .NET DOM gaps into taskcards
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-014

**Micro-steps:**

- **MS-DL-014-02-01:** For each coverage gap (missing type, missing parser mapping, missing traversal, missing mutation, missing writer mapping, missing roundtrip proof, missing package/consumer proof), create a gap record with: gap_id (stable, reusable on rerun), product_id, format_id, gap_type, specification_refs, qname_refs, expected_namespace, expected_type, dependency_gaps, severity, status.
  - Stable ID format: `GAP-NET-{FORMAT}-{GAP_TYPE}-{SEQ}`
  - Completion check: every coverage shortfall has a gap
  - Next: MS-DL-014-02-02

- **MS-DL-014-02-02:** Write `reports/dual-lane-deepening/net-dom-gap-ledger.yaml` with all compiled gaps.
  - Completion check: YAML valid, no duplicate semantic gaps, every gap traces to coverage model
  - Next: MS-DL-014-02-03

- **MS-DL-014-02-03:** Generate per-product parent taskcards and child taskcards from gaps. Write to plan or to `reports/dual-lane-deepening/net-dom-backfill-taskcards.yaml`. Each parent: product_id, format_id, source_root, applicability, current_maturity, target_maturity, child_tasks, dependencies, allowed_paths. Each child: gap_ids, title, objective, specification_refs, qname_refs, expected_types, parser_mappings, writer_mappings, tests, evidence, rollback.
  - Completion check: every applicable gap is represented in a taskcard
  - Next: MS-DL-014-02-04

- **MS-DL-014-02-04:** Build dependency graph across per-product backfill tasks. Document file ownership. Assign execution waves.
  - Completion check: dependency graph valid, no circular dependencies
  - Next: parent acceptance

**Acceptance criteria:**
- [ ] Coverage model exists for every applicable .NET product
- [ ] Every coverage shortfall has a gap record
- [ ] No duplicate semantic gaps
- [ ] Taskcards map to gaps
- [ ] Gap closure requirements are behavioral (not class-existence)
- [ ] Dependency graph is acyclic

---

## TC-DL-015: .NET Backfill Machinery Pilot

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-018, REQ-DL-019, REQ-DL-021, REQ-DL-022
**Dependencies:** TC-DL-014
**Owner:** Worker agent
**Objective:** Prove backfill machinery works on 3 representative .NET products.

### TC-DL-015-01: Pilot A — Mature hierarchical product (FODS or FODT)
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-015
**Purpose:** Prove system correctly identifies ceiling-met product, audits it, and assigns DOM_CEILING_ALREADY_MET_VERIFIED (or identifies remaining gaps if ceiling is NOT actually met).

**Micro-steps:**

- **MS-DL-015-01-01:** Run coverage model against FODS-NET (or FODT-NET). Record: current maturity, target ceiling, gaps found (if any).
  - Next: MS-DL-015-01-02

- **MS-DL-015-01-02:** If no gaps: verify with focused tests (parser mapping, traversal, mutation, writer, roundtrip). Assign `DOM_CEILING_ALREADY_MET_VERIFIED` if all pass. If gaps found: generate child tasks, execute smallest one, verify.
  - Evidence: test output, coverage assessment
  - Next: parent acceptance

### TC-DL-015-02: Pilot B — Missing/partial DOM product
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-015
**Purpose:** Prove backfill can implement actual behavioral DOM progress for a product below its ceiling.

Select a product with gap between current maturity and ceiling (e.g., NetPBM at D2 with ceiling D2 — or a product where ceiling exceeds current). Selection must be evidence-based from TC-DL-014 gaps.

**Micro-steps:**

- **MS-DL-015-02-01:** Select product. Load its gaps. Select smallest ready child task.
  - Next: MS-DL-015-02-02

- **MS-DL-015-02-02:** Implement the child task (add typed class, parser mapping, or behavioral method). Build. Run focused tests. Run negative tests. Run regression.
  - Next: MS-DL-015-02-03

- **MS-DL-015-02-03:** Update coverage model and maturity (only after proof). Verify maturity change is evidence-backed.
  - Evidence: test results, source diff, coverage model update
  - Next: parent acceptance

### TC-DL-015-03: Pilot C — NOT_APPLICABLE or ceiling-met product
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-015
**Purpose:** Prove system correctly assigns DOM_NOT_APPLICABLE_VERIFIED (e.g., HTML export-only writer) with no artificial DOM work generated.

**Micro-steps:**

- **MS-DL-015-03-01:** Select an export-only product (HTML, Markdown, or TXT). Run coverage model. Verify zero DOM gaps generated.
  - Next: MS-DL-015-03-02

- **MS-DL-015-03-02:** Verify no taskcards generated for this product. Assign `DOM_NOT_APPLICABLE_VERIFIED`. Record evidence.
  - Evidence: empty gap list, applicability decision with rationale
  - Next: parent acceptance

**Acceptance criteria:**
- [ ] Mature control: system correctly audits ceiling-met product
- [ ] Missing/partial: actual behavioral progress implemented and proven
- [ ] Non-applicable: no artificial DOM imposed, correct disposition assigned
- [ ] Pilot rerun is idempotent (second run produces zero changes)

---

## TC-DL-016: Full .NET DOM Portfolio Backfill

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-019, REQ-DL-020, REQ-DL-021, REQ-DL-022, REQ-DL-023
**Dependencies:** TC-DL-015 (pilots accepted)
**Owner:** Worker agent
**Objective:** Execute ALL generated .NET DOM backfill taskcards for every applicable active product.

**This task is NOT complete until every product reaches a verified terminal disposition.**

### Per-product autonomous loop:

```
LOAD PRODUCT CONTEXT
→ VERIFY APPLICABILITY
→ LOAD GAPS
→ SELECT FIRST READY GAP
→ CLAIM FILES
→ IMPLEMENT
→ BUILD (dotnet build)
→ RUN FOCUSED TESTS (dotnet test --filter)
→ RUN NEGATIVE TESTS
→ RUN PRODUCT REGRESSION
→ VERIFY PARSER MAPPING
→ VERIFY WRITER MAPPING
→ VERIFY ROUNDTRIP (where applicable)
→ BUILD PROOF
→ HEAL OR ACCEPT
→ UPDATE MATURITY (only after proof)
→ UPDATE README
→ SELECT NEXT GAP
→ CONTINUE UNTIL PRODUCT CEILING
→ ASSIGN FINAL DISPOSITION
```

### Per-product child taskcard contract:

One child taskcard per product is created during TC-DL-016 execution. Each child:
- Scope: `src/net/{format}/**`, `tests/net/{format}/**`
- Forbidden: modifying other products' source
- Required: preserve existing public API (REQ-DL-020)
- Required: focused tests, negative tests, regression tests
- Required: parser-to-DOM mapping proof (REQ-DL-021)
- Required: writer-to-DOM mapping proof where writer exists
- Evidence: build log, test output, coverage model update, source diff

### Healing protocol:

When any product reveals a machinery defect (invalid qname mapping, parser/model disconnect, source organization defect, etc.):
1. CAPTURE — document the defect
2. CLASSIFY — machinery vs product-specific
3. If machinery: create healing task, repair the shared tool, add regression test, rerun affected products
4. If product-specific: repair within product scope
5. Do NOT patch each product separately when root cause is shared machinery

### Product completion gate (per product):

```yaml
net_dom_product_completion:
  applicability_verified: true
  target_maturity_verified: true
  required_types_accounted_for: true
  parser_mapping_proven: true
  typed_access_proven: true
  traversal_proven_or_not_applicable: true
  mutation_proven_or_not_applicable: true
  writer_mapping_proven_or_not_applicable: true
  roundtrip_proven_or_not_applicable: true
  no_material_stubs: true
  no_silent_data_loss: true
  existing_api_compatibility_proven: true
  focused_tests_pass: true
  regression_tests_pass: true
  gaps_reconciled: true
  readme_current: true
  final_disposition: <one of 5 valid values>
```

### Expected dispositions per product (from inventory):

| Product | Expected Disposition | Rationale |
|---|---|---|
| FODS-NET | DOM_CEILING_ALREADY_MET_VERIFIED or DOM_BACKFILL_COMPLETED_VERIFIED | Already D4, ceiling D5 — may need roundtrip proof |
| FODT-NET | DOM_CEILING_ALREADY_MET_VERIFIED or DOM_BACKFILL_COMPLETED_VERIFIED | Already D4, ceiling D5 — may need roundtrip proof |
| NETPBM-NET | DOM_CEILING_ALREADY_MET_VERIFIED or DOM_BACKFILL_COMPLETED_VERIFIED | D2 raster model, ceiling D2-D3 |
| CSV-NET | DOM_CEILING_ALREADY_MET_VERIFIED | D1 record stream, ceiling D1 |
| TSV-NET | DOM_CEILING_ALREADY_MET_VERIFIED | D1 record stream, ceiling D1 |
| NDJSON-NET | DOM_CEILING_ALREADY_MET_VERIFIED | D1 record stream, ceiling D1 |
| ZST-NET | DOM_NOT_APPLICABLE_VERIFIED or DOM_CEILING_ALREADY_MET_VERIFIED | D0 archive handler, ceiling D0-D1 |
| HTML-NET | DOM_NOT_APPLICABLE_VERIFIED | Export-only writer, no parsing |
| MARKDOWN-NET | DOM_NOT_APPLICABLE_VERIFIED | Export-only writer, no parsing |
| TXT-NET | DOM_NOT_APPLICABLE_VERIFIED | Export-only writer, no parsing |

**Acceptance criteria:**
- [ ] Every active .NET product has a verified final disposition
- [ ] Zero UNKNOWN, NOT_AUDITED, PLANNED, or TASK_CREATED dispositions
- [ ] All focused tests pass
- [ ] All regression tests pass
- [ ] All existing public APIs preserved
- [ ] All machinery defects healed

---

## TC-DL-017: .NET Portfolio Reconciliation

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-024
**Dependencies:** TC-DL-016
**Owner:** Worker agent
**Objective:** Reconcile all state after .NET backfill.

### TC-DL-017-01: Reconcile registries and state
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-017

**Micro-steps:**

- **MS-DL-017-01-01:** Reconcile product-deepening-ledger.yaml: all .NET entries have correct lane_b_maturity, disposition, proof paths.
- **MS-DL-017-01-02:** Reconcile qname registries: dotnet_file entries match actual source paths.
- **MS-DL-017-01-03:** Reconcile coverage model: net-dom-coverage.yaml reflects final state.
- **MS-DL-017-01-04:** Reconcile gap ledger: all locally-actionable gaps closed or have governed rework.
- **MS-DL-017-01-05:** Reconcile product READMEs: each `src/net/{format}/README.md` has current DOM status.
- **MS-DL-017-01-06:** Reconcile master plan: dual-lane section reflects .NET portfolio state.
- **MS-DL-017-01-07:** Reconcile evidence declarations: all proof paths valid.

**Acceptance criteria:**
- [ ] No stale maturity claims
- [ ] No falsely closed gaps
- [ ] No unsupported README claims
- [ ] No missing proof links

---

## TC-DL-018: Full .NET Portfolio Verification

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-022, REQ-DL-026
**Dependencies:** TC-DL-017
**Owner:** Worker agent
**Objective:** Run complete .NET DOM verification matrix for every active product.

### Verification matrix per applicable product:

- **Build:** `dotnet build` succeeds, no new warnings
- **Unit tests:** focused DOM tests pass
- **Integration tests:** parser→DOM→writer chain works
- **Negative tests:** malformed input, invalid mutations, unsupported elements handled explicitly
- **Parser mapping:** valid constructs map to correct typed objects
- **Traversal:** deterministic typed iteration works
- **Mutation:** property changes persist through writer (where applicable)
- **Roundtrip:** parse→DOM→serialize→reparse→semantic compare (where applicable)
- **Package:** package builds, contains required assemblies, public DOM types exported
- **Clean consumer:** new project references package, compiles, creates/loads/inspects document
- **Source quality:** no monolithic god objects, no stubs, no silent data loss, namespace/qname alignment
- **API compatibility:** existing public APIs unchanged

**Acceptance criteria:**
- [ ] Every applicable product passes all applicable verification checks
- [ ] Every non-applicable product has verified exclusion evidence
- [ ] No happy-path-only proof (negative controls required)

---

## TC-DL-019: .NET Backfill Idempotency and Healing Rerun

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-023, REQ-DL-025
**Dependencies:** TC-DL-018
**Owner:** Worker agent
**Objective:** Prove complete pipeline rerun produces zero material changes.

### TC-DL-019-01: Full pipeline rerun
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-DL-019

**Micro-steps:**

- **MS-DL-019-01-01:** Rerun .NET product inventory. Compare with TC-DL-013 output. Must match (or add newly discovered products only).
- **MS-DL-019-01-02:** Rerun coverage model. Compare with TC-DL-014 output. Must match.
- **MS-DL-019-01-03:** Rerun gap compilation. Must produce no new locally-actionable gaps.
- **MS-DL-019-01-04:** Rerun taskcard generation. Must produce no new taskcards (all gaps closed).
- **MS-DL-019-01-05:** Verify zero material source changes needed.
- **MS-DL-019-01-06:** Write `reports/dual-lane-deepening/net-backfill-idempotency-verdict.md`.

**Acceptance criteria:**
- [ ] No duplicate gaps, taskcards, classes, or qname mappings
- [ ] No maturity churn (values stable)
- [ ] No README churn
- [ ] Zero new locally-actionable gaps
- [ ] Zero material source changes
- [ ] Idempotency verdict: PASS

---

## TC-DL-020: Terminal Dual-Lane and .NET Portfolio Audit

**Type:** PARENT
**Status:** CLOSED
**Requirements:** REQ-DL-026
**Dependencies:** ALL prior taskcards (TC-DL-001 through TC-DL-019)
**Owner:** Worker agent
**Objective:** Final independent audit. Close the mission only if both machinery and .NET portfolio are green.

### Terminal audit questions:

1. Were all `src/net/*` products discovered?
2. Were non-products and deprecated products explicitly classified?
3. Was applicability decided from evidence?
4. Is language-specific maturity represented correctly in the ledger?
5. Does every applicable product have a typed document model?
6. Do namespaces and types follow authoritative qnames?
7. Are parser mappings complete for approved scope?
8. Are writers connected to the typed DOM?
9. Is mutation behavior real (where applicable)?
10. Is roundtrip proven where applicable?
11. Are source files professionally organized?
12. Do packages expose the expected public DOM?
13. Do clean consumers compile and run?
14. Were existing APIs preserved?
15. Are all maturity claims supported by proof?
16. Did the second full pass produce zero material changes?
17. Were machinery weaknesses exposed during backfill repaired?

### Portfolio completion gate:

```yaml
net_dom_portfolio_completion:
  active_net_products_discovered: <count>
  applicable_products: <count>
  ceiling_complete_products: <count>
  backfilled_products: <count>
  valid_exclusions: <count>
  unknown_products: 0
  unverified_applicability: 0
  unexecuted_ready_taskcards: 0
  unresolved_local_gaps: 0
  products_missing_package_proof: 0
  products_missing_consumer_proof: 0
  full_regression_green: true
  second_pass_idempotent: true
  final_audit_green: true
```

### Required proof artifacts:

```
reports/dual-lane-deepening/net-dom-product-inventory.yaml
reports/dual-lane-deepening/net-dom-coverage.yaml
reports/dual-lane-deepening/net-dom-gap-ledger.yaml
reports/dual-lane-deepening/net-dom-backfill-taskcards.yaml
reports/dual-lane-deepening/net-backfill-idempotency-verdict.md
reports/dual-lane-deepening/net-dom-portfolio-audit.md
reports/dual-lane-deepening/net-dom-portfolio-completion.yaml
.local/evidences/dual-lane-deepening-001/net-dom/<product-id>/ (per product proof)
```

**Acceptance criteria:**
- [ ] All 17 audit questions answered affirmatively with evidence
- [ ] Portfolio completion gate all-green
- [ ] Zero unresolved locally-actionable gaps
- [ ] Idempotency rerun passed

---

## Plan-Hardening Change Log

```yaml
changes:
  - id: HC-001
    section: Context
    action: EXPANDED
    detail: "Added terminal completion requirement (verified disposition for every .NET product)"
  - id: HC-002
    section: Forensic Findings
    action: EXPANDED
    detail: "Added .NET Product Universe table (10 products from src/net/), .NET DOM applicability assessment, Gate 11 status, ledger schema gap (no .NET entries)"
  - id: HC-003
    section: Lane B Maturity Scale
    action: ENHANCED
    detail: "Added .NET-specific behavioral criteria and anti-inference rules"
  - id: HC-004
    section: Requirement Inventory
    action: EXPANDED
    detail: "Added REQ-DL-015 through REQ-DL-026 (12 new requirements for .NET portfolio backfill)"
  - id: HC-005
    section: Dependency DAG
    action: EXPANDED
    detail: "Extended with TC-DL-013 through TC-DL-020 chain, .NET parallel-safety rules"
  - id: HC-006
    section: File Ownership
    action: EXPANDED
    detail: "Added .NET backfill file ownership rules"
  - id: HC-007
    section: New Taskcards
    action: INSERTED
    detail: "Added TC-DL-013 through TC-DL-020 (8 parent taskcards with children and micro-steps)"
  - id: HC-008
    section: Final Verdict Target
    action: CORRECTED
    detail: "Changed terminal verdict from PORTFOLIO_BACKFILL_ACTIVE to PORTFOLIO_BACKFILLED_VERIFIED"
  - id: HC-009
    section: .NET Portfolio Backfill Program
    action: INSERTED
    detail: "Added complete section: applicability values, terminal conditions, execution waves, healing protocol, completion gates"
  - id: HC-010
    section: Execution Handoff
    action: EXPANDED
    detail: "Extended execution order with TC-DL-013–020, added .NET backfill execution mode and 7 verification items"
  - id: HC-011
    section: What This Plan Does NOT Do
    action: EXPANDED
    detail: "Added 4 .NET-specific exclusion items (no cross-language DOM copy, no artificial DOM for exporters, API compat, discovery-driven)"
  - id: HC-012
    section: Final Verdict Target
    action: CORRECTED
    detail: "Changed from 12 to 20 taskcards, changed verdict to DUAL_LANE_SYSTEM_ESTABLISHED_NET_DOM_PORTFOLIO_BACKFILLED_VERIFIED_AND_GOVERNED, added .NET portfolio completion criteria"
```

---

## Execution Handoff

### Execution Agent Instructions

1. Read this plan completely before starting.
2. Execute taskcards in dependency order:
   - **Machinery phase:** TC-DL-001 → TC-DL-002 → TC-DL-003 + TC-DL-004 (parallel-safe) → TC-DL-005 → TC-DL-006 → TC-DL-007 → TC-DL-008 → TC-DL-009 → TC-DL-010 → TC-DL-011 → TC-DL-012
   - **.NET backfill phase:** TC-DL-013 → TC-DL-014 → TC-DL-015 → TC-DL-016 → TC-DL-017 → TC-DL-018 → TC-DL-019 → TC-DL-020
   - TC-DL-013 MUST NOT start until TC-DL-012 is accepted (machinery audit green)
3. For each child taskcard, execute micro-steps in order.
4. Mark each micro-step COMPLETE immediately after verifying.
5. Do NOT close a parent until ALL children are CLOSED.
6. Run validation commands at each checkpoint.
7. If any micro-step FAILS, investigate root cause before proceeding.
8. Capture evidence at every checkpoint.
9. Do NOT modify files outside the allowed scope for each taskcard.
10. Rollback on critical failure using documented rollback commands.
11. For .NET backfill (TC-DL-016), follow the per-product autonomous loop documented in that taskcard.
12. When TC-DL-016 reveals machinery defects, follow the healing protocol before continuing.

### Execution Mode

```
SEQUENTIAL_DOM_THEN_FEATURE for pilots (TC-DL-006, TC-DL-007)
PARALLEL for TC-DL-003 + TC-DL-004 (different files)
PARALLEL for TC-DL-005 + TC-DL-009 (different outputs)
SEQUENTIAL for TC-DL-013 through TC-DL-020 (strict chain)
SEQUENTIAL for all other taskcards
```

### Verification Plan

**Machinery phase (TC-DL-001–012):**
1. **Unit:** Gate `check_dom_readiness()`, compiler `_classify_deepening_lane()`, `_lane_balance_penalty()` — validated by manual runs
2. **Integration:** Gate + compiler end-to-end with FODS/ODS/ZST
3. **Pilot positive:** FODS D3 traversal tests pass; ODS D2 wiring tests pass
4. **Pilot negative:** ZST/CSV dom_lane_at_ceiling=True, ready_for_dom_sprint=False
5. **Regression:** All existing FODS/ODS tests still pass
6. **Idempotency:** TC-DL-012 rerun stability

**.NET backfill phase (TC-DL-013–020):**
7. **Inventory completeness:** Every `src/net/*/` directory accounted for with zero UNKNOWN classifications
8. **Coverage model:** Every applicable product has coverage entry with gap records
9. **Pilot proof:** 3 representative .NET products (mature, partial, non-applicable) proven in TC-DL-015
10. **Per-product verification matrix:** Build, unit tests, integration tests, negative tests, parser mapping, traversal, mutation, roundtrip, package, clean consumer, source quality, API compatibility (TC-DL-018)
11. **Portfolio completeness:** Every active .NET product at verified terminal disposition
12. **Idempotency rerun:** Full pipeline rerun produces zero material changes (TC-DL-019)
13. **Terminal audit:** All 17 audit questions answered affirmatively with evidence (TC-DL-020)

---

## What This Plan Does NOT Do

- Does NOT replace existing gate system — extends with advisory DOM readiness
- Does NOT delete any existing tests, features, or workflows
- Does NOT force DOM on simple formats (ZST, CSV, PBM, etc.)
- Does NOT create empty class shells — D2 requires behavioral methods
- Does NOT change check_continuation.py — lane balance is work-selection, not continuation-gating
- Does NOT create new skills — extends existing workflows
- Does NOT block feature work while DOM incomplete — Lane A always available
- Does NOT modify parser source (ods_parser.py, parser.py) — DOM wires to existing parser output
- Does NOT impose Python DOM classifications on .NET products — each language evaluated independently
- Does NOT create artificial DOM work for export-only .NET writers (HTML, Markdown, TXT)
- Does NOT modify existing .NET public APIs during backfill — backward compatibility required
- Does NOT hard-code product membership in execution waves — discovery-driven

---

## Final Verdict Target

After all 20 parent taskcards CLOSED (TC-DL-001 through TC-DL-020):

`DUAL_LANE_SYSTEM_ESTABLISHED_NET_DOM_PORTFOLIO_BACKFILLED_VERIFIED_AND_GOVERNED`

This means:

**Machinery (TC-DL-001–012):**
- Lane definitions formalized and governed
- Ledger tracks both lanes independently
- Gate reports DOM readiness (advisory)
- Compiler tags and balances lane work
- FODS pilot proves D3 traversal
- ODS pilot proves D2 wiring
- Non-DOM formats correctly skip Lane B
- Historical work classified
- Plans and READMEs updated
- Supervisor integration wired
- Machinery idempotency proven

**.NET Portfolio Backfill (TC-DL-013–020):**
- Every active `src/net/*/` product discovered and inventoried
- DOM applicability decided from evidence (not copied from Python)
- Coverage model and gap ledger compiled for every applicable product
- Backfill machinery proven on 3 representative pilots
- Every applicable product backfilled to its verified DOM ceiling
- All existing .NET public APIs preserved
- All machinery defects exposed during backfill healed
- All registries, qnames, READMEs, and plans reconciled
- Full verification matrix passed for every applicable product
- Idempotency rerun produces zero material changes
- Terminal audit green with all 17 questions answered affirmatively
- Every active .NET product at one of 5 verified final dispositions
- Zero UNKNOWN, NOT_AUDITED, PLANNED, or TASK_CREATED dispositions remain


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-06-28T16:16:02.100946+00:00"
  locked_by: "b42c05efe582"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
