# Commercial Readiness Rubric (.NET)
# Format Factory — Expert Manual System Review
# Phase 9 output — Generated: 2026-06-25

## Rubric Overview

8 dimensions, each scored 0–5. Maximum: 40 points.
Final score = total / 8 (normalized to 0–5 scale).

---

## Dimension 1: API Design (0–5)

Professional naming, stable surface, namespacing.

| Score | Criteria |
|-------|---------|
| 0 | No public API |
| 1 | API exists but confusing or unstable |
| 2 | Adequate naming; some inconsistency |
| 3 | Good naming; consistent; XML comments |
| 4 | Professional naming; stable; full XML docs |
| 5 | Best-in-class; versioning-ready |

---

## Dimension 2: Architecture Separation (0–5)

Parser / Model / Writer / Exporter layer separation.

| Score | Criteria |
|-------|---------|
| 0 | Monolith |
| 1 | Minimal separation |
| 2 | Parser and model separated |
| 3 | Parser / model / writer separated |
| 4 | Clean 4-layer separation |
| 5 | Injectable layers with interfaces |

---

## Dimension 3: Object Model Depth (0–5)

Access to all document structure, correct types, mutability.

| Score | Criteria |
|-------|---------|
| 0 | No model |
| 1 | Flat string model |
| 2 | Shallow model (rows/values only) |
| 3 | Medium model (typed values, coordinates) |
| 4 | Rich model (all structure accessible, typed) |
| 5 | Spec-shaped model with spec_qname and full edit API |

---

## Dimension 4: Error Handling (0–5)

Meaningful exceptions, null safety, culture-invariant.

| Score | Criteria |
|-------|---------|
| 0 | No error handling |
| 1 | Minimal catch |
| 2 | Format-specific exceptions (inconsistent) |
| 3 | Custom exception hierarchy (consistent) |
| 4 | Full exceptions + null-safe + culture-invariant |
| 5 | Full exceptions + error codes + recovery |

---

## Dimension 5: Roundtrip Correctness (0–5)

Load → edit → save → reload = identical content.

| Score | Criteria |
|-------|---------|
| 0 | No roundtrip |
| 1 | Writer exists; no roundtrip test |
| 2 | Basic roundtrip (smoke) |
| 3 | Roundtrip with representative content |
| 4 | Roundtrip with edge cases |
| 5 | Full spec coverage roundtrip |

---

## Dimension 6: Export and Dogfood (0–5)

Export to other formats; use of other FF libraries.

| Score | Criteria |
|-------|---------|
| 0 | No export |
| 1 | Export exists; no test |
| 2 | Export smoke test |
| 3 | Export with content verification |
| 4 | Multiple exporters; FF dogfood |
| 5 | Physical output verified in real apps |

---

## Dimension 7: Test Meaningfulness (0–5)

Test type distribution: smoke vs. behavioral vs. roundtrip vs. malformed.

| Score | Criteria |
|-------|---------|
| 0 | No tests |
| 1 | Smoke only |
| 2 | Unit behavioral |
| 3 | Unit + edge cases |
| 4 | Unit + edge + malformed + roundtrip |
| 5 | Full spec coverage + property-based |

---

## Dimension 8: Commercial Polish (0–5)

XML docs, examples, streaming, NuGet metadata.

| Score | Criteria |
|-------|---------|
| 0 | No docs, no NuGet metadata |
| 1 | Partial XML comments |
| 2 | All public members documented; NuGet metadata |
| 3 | Full XML docs; version; README |
| 4 | Full docs + examples + streaming + culture-invariant |
| 5 | Full docs + quickstart + changelog |

---

## Scoring Bands

| Score (0–5 average) | Band |
|--------------------|------|
| 0.0–1.4 | Not a product |
| 1.5–2.4 | Demo or prototype |
| 2.5–3.4 | POC candidate |
| 3.5–4.2 | Commercial candidate with known gaps |
| 4.3–5.0 | Scoped commercial-ready |

## Commercial Gate Criteria (C1–C8 for NuGet publication)

| Criterion | Minimum Score |
|-----------|--------------|
| C1: API Design | >= 3 |
| C2: Architecture | >= 3 |
| C3: Object Model | >= 3 |
| C4: Error Handling | >= 3 |
| C5: Roundtrip | >= 2 |
| C6: Export | >= 2 |
| C7: Tests | >= 3 |
| C8: Polish | >= 2 |
| **Overall Average** | >= 3.0 |
