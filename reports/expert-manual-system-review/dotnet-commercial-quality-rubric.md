# .NET Commercial Quality Rubric
# Format Factory — Expert Manual System Review
# Phase 3 output — Generated: 2026-06-25

## Rubric Overview

Each .NET product is scored on 8 dimensions, 0–5 each. Maximum score: 40 (converted to 0–5 band).

---

## Dimension 1: API Design (0–5)

Evaluates: namespace clarity, method naming, method signatures, stability of public surface.

| Score | Meaning |
|-------|---------|
| 0 | No public API / completely internal |
| 1 | Public API exists but naming is inconsistent, confusing, or undocumented |
| 2 | Adequate naming; some inconsistency; minimal docs |
| 3 | Good naming; consistent; XML comments on most public members |
| 4 | Professional naming; stable surface; full XML docs; no surprises |
| 5 | Best-in-class API design; versioning-ready; clean deprecation path |

**FODS expected**: 4 (full DOM, consistent naming)
**ZST expected**: 1 (probe-only API, no real contract)

---

## Dimension 2: Architecture Separation (0–5)

Evaluates: parser vs. model vs. writer vs. exporter separation; coupling between layers.

| Score | Meaning |
|-------|---------|
| 0 | Monolith — all in one class |
| 1 | Some separation but high coupling |
| 2 | Parser and model separated; writer mixed into model |
| 3 | Parser / model / writer separated; exporters may be coupled |
| 4 | Clean 4-layer separation (parser / model / writer / exporter) |
| 5 | Layers injectable; interfaces defined; no runtime coupling |

**FODS expected**: 4 (Fods*Parser / Fods*Document / internal writer / Fods*Exporter)
**HTML/Markdown/TXT expected**: N/A (target writers only — single-layer utility)

---

## Dimension 3: Object Model Depth (0–5)

Evaluates: depth of the object model, property accessibility, mutability where appropriate.

| Score | Meaning |
|-------|---------|
| 0 | No model — raw strings or byte arrays only |
| 1 | Flat model — document is a list of strings |
| 2 | Shallow model — document → rows → values (no column types) |
| 3 | Medium model — document → sheets → rows → cells with typed values |
| 4 | Rich model — all relevant structure accessible; types correct; metadata available |
| 5 | Spec-shaped model — every element has spec_qname, spec_fact_ref; full edit API |

**FODS expected**: 4 (sheets/rows/cells with types and coordinates)
**ZST expected**: 1 (probe metrics only — no content access)
**CSV expected**: 2 (rows + columns but no types, no edit)

---

## Dimension 4: Error Handling (0–5)

Evaluates: meaningful exceptions on bad input; null safety; culture-invariant parsing.

| Score | Meaning |
|-------|---------|
| 0 | No error handling — throws NullReferenceException on bad input |
| 1 | Minimal — catches some IOExceptions but propagates most raw |
| 2 | Format-specific exceptions exist but not consistently thrown |
| 3 | Custom exception hierarchy; most bad inputs produce meaningful errors |
| 4 | Full exception hierarchy; null-safe throughout; culture-invariant number/date parse |
| 5 | Exception hierarchy with error codes; streaming safe; no resource leaks |

**FODS expected**: 3-4 (FodsParseException exists; DTD guard; 50MB guard)
**CSV expected**: 1-2 (thin wrapper, limited guards)

---

## Dimension 5: Roundtrip Correctness (0–5)

Evaluates: load → edit → save → reload produces identical or semantically equivalent document.

| Score | Meaning |
|-------|---------|
| 0 | No roundtrip — parse-only |
| 1 | Writer exists but no test verifies roundtrip |
| 2 | Basic roundtrip test exists (smoke test only) |
| 3 | Roundtrip tested with representative content |
| 4 | Roundtrip tested for edge cases (empty doc, Unicode, formulas, styles) |
| 5 | Roundtrip proven for full spec coverage; diff-tested |

**FODS expected**: 3 (roundtrip tested, not full edge case coverage)
**ZST expected**: 0 (no roundtrip — parse-only; no decompression)

---

## Dimension 6: Export and Dogfood (0–5)

Evaluates: export to other formats; use of other FormatFactory libraries (dogfood); physical output tested.

| Score | Meaning |
|-------|---------|
| 0 | No export capability |
| 1 | Export exists in code but no test verifies output is valid |
| 2 | Export tested by smoke test (checks file exists, not content) |
| 3 | Export tested with content verification (CSV output matches input values) |
| 4 | Multiple export targets; dogfood to other FF libraries; output opens in real app |
| 5 | Physical output verified in real applications (LibreOffice, browser, PDF reader) |

**FODS expected**: 4 (6 exporters; CSV and HTML use dogfood; tests verify output)
**ODS exporter expected**: 2 (marked PROTOTYPE in source; test may not verify ZIP structure)
**ZST expected**: 0 (no export, no dogfood)

---

## Dimension 7: Test Meaningfulness (0–5)

Evaluates: test quality beyond smoke — behavior tests, edge cases, roundtrip, malformed input.

| Score | Meaning |
|-------|---------|
| 0 | No tests or 1 trivial smoke test |
| 1 | Smoke tests only (parser returns non-null) |
| 2 | Basic behavior tests (correct value returned) |
| 3 | Behavior + edge cases (empty input, Unicode, large files) |
| 4 | Behavior + edge cases + malformed input + roundtrip |
| 5 | Full spec-coverage test suite; property-based tests; performance tests |

**FODS expected**: 4 (71 test files; behavior and roundtrip tests)
**ZST expected**: 1 (2 test files; probe-only smoke)
**CSV expected**: 1-2 (6 test files; mostly behavior smoke)

---

## Dimension 8: Commercial Polish (0–5)

Evaluates: XML doc comments, examples in docs, streaming support, NuGet metadata, culture settings.

| Score | Meaning |
|-------|---------|
| 0 | No docs, no examples, no NuGet metadata |
| 1 | Partial XML docs on some public members |
| 2 | XML docs on all public members; basic NuGet metadata |
| 3 | Full XML docs; NuGet metadata complete; version set |
| 4 | Full docs + examples in XML; streaming-capable; culture-invariant |
| 5 | Full docs + quickstart example; streaming; culture-invariant; changelog |

**FODS expected**: 3-4 (GenerateDocumentationFile=true fixed; NuGet metadata added)
**ZST expected**: 1 (minimal docs; probe-only with no real feature to document)

---

## Scoring Bands

| Total (0–40) | Band | Meaning |
|-------------|------|---------|
| 0–11 | Not a product | Toy or stub |
| 12–19 | Demo or prototype | Illustrates intent, not useful |
| 20–27 | POC candidate | Proof of concept; not ship-ready |
| 28–33 | Commercial candidate with known gaps | Ship-ready with identified work remaining |
| 34–40 | Scoped commercial-ready | Ready for NuGet publication in defined scope |

## Per-Product Score Summary (from prior sprint scoring)

| Product | Scored | Band |
|---------|--------|------|
| FODS | 3.79/5 (~30.3/40) | Commercial candidate with known gaps |
| FODT | 3.67/5 (~29.4/40) | Commercial candidate with known gaps |
| NetPBM | Not fully scored | Estimated: 3.2/5 |
| CSV | Not fully scored | Estimated: 2.0/5 |
| TSV | Not fully scored | Estimated: 2.0/5 |
| NDJSON | Not fully scored | Estimated: 2.0/5 |
| ZST | Not scored | Estimated: 0.5/5 (Not a product) |
| HTML/Markdown/TXT | N/A | Target writers — not rated as format products |
