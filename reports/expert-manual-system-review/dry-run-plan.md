# Dry Run Plan
# Format Factory — Expert Manual System Review
# Phase 8 output — Generated: 2026-06-25

## Purpose

Simulate review scoring on 3 representative products to verify the rubric works before applying it to all 30 products.

## Products Selected for Dry Run

### Product 1: FODS .NET — Expected: HIGH (commercial candidate)

**Why:** Pre-assessed as strongest .NET product. Gate 11 approved. Should score 3.5+.

| Dimension | Expected Score | Rationale |
|-----------|---------------|-----------|
| API Design | 4 | Full DOM, consistent naming, XML docs |
| Architecture | 4 | Parser/Model/Writer/Exporter layers |
| Object Model | 4 | Sheets/Rows/Cells with typed values |
| Error Handling | 3 | FodsParseException; DTD guard; 50MB guard |
| Roundtrip | 3 | Tested but not full edge cases |
| Export/Dogfood | 4 | 6 exporters; CSV/HTML use dogfood |
| Tests | 4 | 71 test files; mix of types |
| Commercial Polish | 3 | XML docs; NuGet metadata |
| **Expected Total** | **3.6/5** | Commercial candidate |

**Pass criteria:** Score >= 3.5 → rubric is calibrated correctly for strong products.

---

### Product 2: ZST .NET — Expected: VERY LOW (not a product)

**Why:** Probe-only, no decompression. Should score below 2.0.

| Dimension | Expected Score | Rationale |
|-----------|---------------|-----------|
| API Design | 1 | ZstDocument exposes metadata only; no content access |
| Architecture | 2 | ZstParser + ZstDocument separated |
| Object Model | 1 | Frame count, magic bytes — no content |
| Error Handling | 2 | Basic file not found; magic bytes check |
| Roundtrip | 0 | Cannot roundtrip — no decompression |
| Export/Dogfood | 0 | No export, no dogfood |
| Tests | 1 | 2 test files; probe-only smoke |
| Commercial Polish | 1 | Minimal docs; probe-only |
| **Expected Total** | **1.0/5** | Not a product |

**Pass criteria:** Score <= 1.5 → rubric catches critical gaps.

---

### Product 3: ODS Python — Expected: MEDIUM (useful scoped FOSS)

**Why:** Has writer (write_ods() confirmed), but thin. Should score 2.5–3.0.

| Dimension | Expected Score | Rationale |
|-----------|---------------|-----------|
| Package Import | 3 | Clean import; __all__ defined |
| Parser/Load | 3 | ods_parser returns structured data |
| Data Model | 3 | spec_qname on OdsRow |
| Writer/Save | 3 | write_ods() produces valid ZIP |
| Export | 3 | export_to_csv exists |
| Installed Workflow | 2 | Wheel existence to be confirmed |
| Tests | 2 | Limited test files visible |
| FOSS Polish | 1 | No README; no examples |
| **Expected Total** | **2.5/5** | Useful scoped FOSS |

**Pass criteria:** Score 2.0–3.5 → rubric positions ODS correctly between ZST and FODS.

---

## Dry Run Validation Criteria

The dry run PASSES if:
1. FODS score >= 3.5 (commercial candidate with known gaps) ✓
2. ZST score <= 1.5 (not a product)
3. ODS score is between ZST and FODS scores
4. Known PROB items (PDF Latin-1, no table traversal) appear as gap evidence in FODS score
5. ZST PROB-001 (no decompression) is the key driver of low ZST score

The dry run FAILS if:
- FODS scores very low (rubric too harsh)
- ZST scores above 2.5 (rubric too lenient)
- Known gaps are not reflected in scores

## Output

`phase-c-dry-run/rubric-results.json` — three products with dimension-by-dimension scores
`phase-c-dry-run/dry-run-methodology-proof.md` — confirms rubric detects known gaps
