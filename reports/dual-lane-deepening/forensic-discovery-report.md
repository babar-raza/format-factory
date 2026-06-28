# Forensic Discovery Report — Dual-Lane Product Deepening

**Generated:** 2026-06-28
**Mission:** DUAL-LANE-DEEPENING-001

---

## 1. Current Product-Deepening Definitions

| Source File | Role | Key Integration |
|---|---|---|
| `registry/product-deepening-ledger.yaml` | Per-format readiness (20 entries, schema v2.0) | `continuation_allowed` bool from 4 gates |
| `tools/supervisor/product_deepening_gate.py` (235 LOC) | Gate evaluator: `check_product_readiness()`, `check_formats_in_gaps()` | Returns `{format, allowed, reason, 7 gate fields}` |
| `tools/supervisor/capability_feature_compiler.py` (289 LOC) | Gap-to-work-item compiler, scoring, `_lane()` returns "product"/"machinery" | Produces `next-work-items.json` with 17-field items |
| `tools/supervisor/check_continuation.py` Check 9 (lines 528-563) | Blocks continuation for non-compliant formats | Imports `check_formats_in_gaps()`, returns STOP if any `allowed=False` |
| `.supervisor/policies.yaml` (331 LOC, 9 sections) | Continuation, approval, product factory policies | `autonomous_continuation` section (lines 231-300) |

**Interpretation:** "Product deepening" currently means expanding gate-checked format products with capabilities selected from the gap ledger. The system is gate-driven (4 gates in product_deepening_gate.py), gap-driven (capability_feature_compiler.py selects work items from gap-ledger.json), and spec-traced (qname compliance required). There is no distinction between feature work and DOM/object-model work — everything routes through a single "product" lane.

---

## 2. Historical Work Classification

| Classification | Examples | Keep/Repair |
|---|---|---|
| CORE_PRODUCT_VALUE | .NET FODS/FODT DOM, Python parsers, roundtrip tests | KEEP |
| VALID_FORMAT_FEATURE | Sheet/cell access, metadata extraction, export APIs | KEEP |
| VALID_ARCHITECTURE | QName compliance, spec class creation, SAL facts | KEEP |
| ANALYTICS_ONLY | Suspended mod_prime rotation (ZST/XCF/FODG) | DEPRECATED |
| TEST_INFRASTRUCTURE | Batch 117-121 .NET test files (7/batch) | KEEP (useful coverage) |
| BLOCKED_PROGRESS | 9 formats with domain_model_missing classification | Lane B work needed |

---

## 3. DOM State Per Format

| Format | Category | Python DOM | .NET DOM | Lane B Ceiling |
|---|---|---|---|---|
| FODS | SPREADSHEET | D2 (models.py 236 LOC: FodsDocument, FodsSheet, FodsCell) | D4 (editable XDocument) | D5 |
| FODT | TEXT_DOC | D2 (paragraph/heading classes) | D4 (extensive mutation) | D5 |
| ODS | SPREADSHEET | D1 (models.py 74 LOC — but parser has OdsSheet/OdsRow/OdsCell dataclasses) | N/A | D5 |
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
| PBM | IMAGE | D1 (80 LOC wrapper) | N/A | D1 |
| PGM | IMAGE | D1 (85 LOC wrapper) | N/A | D1 |
| PPM | IMAGE | D1 (89 LOC wrapper) | N/A | D1 |
| QOI | IMAGE | D1 (90 LOC wrapper) | N/A | D1 |

**Critical correction:** ODS parser (`ods_parser.py` lines 104-128) ALREADY defines `OdsCell`, `OdsRow`, `OdsSheet`, `OdsDocument` as dataclasses with `spec_qname: ClassVar[str]`. Compat facades also exist. The D1 to D2 upgrade is a WIRING task, not class creation.

---

## 4. Product-Deepening Interpretation Analysis

The current product-deepening system operates through three mechanisms:

1. **Gate-driven readiness:** `product_deepening_gate.py` evaluates 4 gates (qname, src_layout, spec_mapping, sal) per format. All must pass for `continuation_allowed=True`.

2. **Gap-driven work selection:** `capability_feature_compiler.py` reads gap-ledger.json, scores items, and compiles `next-work-items.json`. The `_lane()` function returns "product" or "machinery" but does NOT distinguish between feature work and DOM work.

3. **Spec-traced compliance:** QName registry entries (`shared/qname-registry/*.yaml`) must exist for each format's key specification concepts. This is enforced at the gate level.

**What is missing:**
- No Lane A vs Lane B distinction (features vs DOM maturity)
- No starvation prevention (all sprints can go to one lane indefinitely)
- No DOM applicability classification (FULL/PARTIAL/FLAT/METRICS_ONLY)
- No DOM maturity tracking independent of feature maturity
- No advisory DOM readiness gate

---

## 5. Contradictions Found

No material contradictions found. The analytics rotation (mod_prime) was already suspended (2026-06-18) and is correctly classified as DEPRECATED. The product-deepening system works correctly for its current scope; this plan extends it without replacing existing functionality.
