# Python FOSS Readiness Rubric
# Format Factory — Expert Manual System Review
# Phase 9 output — Generated: 2026-06-25

## Rubric Overview

8 dimensions, each scored 0–5. Maximum: 40 points.
Final score = total / 8 (normalized to 0–5 scale).

---

## Dimension 1: Package Import (0–5)

Clean import; no pollution; __all__ defined.

| Score | Criteria |
|-------|---------|
| 0 | Import fails |
| 1 | Import succeeds but pollutes namespace |
| 2 | Import succeeds; minimal pollution |
| 3 | __all__ defined; no unintended exports |
| 4 | Clean __all__; no module/type leaks; dynamic filter |
| 5 | Clean __all__ + lazy imports for performance |

---

## Dimension 2: Parser / Load API (0–5)

Returns structured data from file path.

| Score | Criteria |
|-------|---------|
| 0 | No load function |
| 1 | load() returns raw bytes or string only |
| 2 | load() returns dict with some structure |
| 3 | load() returns typed object with meaningful properties |
| 4 | from_file() factory + multiple load modes |
| 5 | Full load + streaming + partial load + error recovery |

---

## Dimension 3: Data Model (0–5)

Typed, meaningful, spec-traced with spec_qname.

| Score | Criteria |
|-------|---------|
| 0 | No model class |
| 1 | Model class exists but is just a dict wrapper |
| 2 | Model class with typed properties |
| 3 | Model class + spec_qname class attribute |
| 4 | Model class + spec_qname + spec_fact_ref + to_dict() |
| 5 | Fully spec-shaped model with all Compat/ facades |

---

## Dimension 4: Writer / Save (0–5)

Produces valid output file.

| Score | Criteria |
|-------|---------|
| 0 | No write function (N/A formats: XCF acceptable) |
| 1 | write() exists but output is malformed |
| 2 | write() produces syntactically valid output |
| 3 | write() + roundtrip test (load → write → load → same) |
| 4 | write() + roundtrip + edge cases |
| 5 | write() + full spec coverage + LibreOffice verifiable |

---

## Dimension 5: Export (0–5)

Export to CSV, JSON, or text where applicable.

| Score | Criteria |
|-------|---------|
| 0 | No export |
| 1 | Export function exists but no test |
| 2 | Export with smoke test |
| 3 | Export verified (content matches input) |
| 4 | Multiple export targets |
| 5 | Export + installed workflow proof |

---

## Dimension 6: Installed Workflow (0–5)

Works from wheel install, not just editable.

| Score | Criteria |
|-------|---------|
| 0 | No wheel; only works as editable install |
| 1 | Wheel builds but not verified |
| 2 | Wheel installs; basic import works |
| 3 | Wheel + API functions verified from installed package |
| 4 | Wheel + full roundtrip from installed |
| 5 | Wheel + all examples work from installed |

---

## Dimension 7: Tests (0–5)

Parser, writer, roundtrip, error, edge cases.

| Score | Criteria |
|-------|---------|
| 0 | No tests |
| 1 | One smoke test |
| 2 | Unit tests for parser |
| 3 | Parser + writer + basic roundtrip |
| 4 | Full: parser + writer + roundtrip + error + edge |
| 5 | Full + malformed input + property-based |

---

## Dimension 8: FOSS Polish (0–5)

README, examples, dependency docs, community-usable.

| Score | Criteria |
|-------|---------|
| 0 | No README; no examples |
| 1 | Minimal README (package name only) |
| 2 | README with install instructions |
| 3 | README + quickstart code example |
| 4 | README + quickstart + API reference |
| 5 | Full docs + CHANGELOG + examples/ directory |

---

## Scoring Bands

| Score (0–5 average) | Band |
|--------------------|------|
| 0.0–1.4 | Not usable |
| 1.5–2.4 | Toy or demo |
| 2.5–3.4 | Useful scoped FOSS |
| 3.5–4.2 | Release candidate |
| 4.3–5.0 | Strong FOSS product |

## FOSS Gate Criteria (P1–P8 for PyPI publication)

| Criterion | Minimum Score |
|-----------|--------------|
| P1: Package Import | >= 3 |
| P2: Parser/Load API | >= 3 |
| P3: Data Model | >= 2 |
| P4: Writer/Save | >= 2 (or N/A with doc) |
| P5: Export | >= 1 |
| P6: Installed Workflow | >= 3 |
| P7: Tests | >= 3 |
| P8: FOSS Polish | >= 2 |
| **Overall Average** | >= 2.5 |
