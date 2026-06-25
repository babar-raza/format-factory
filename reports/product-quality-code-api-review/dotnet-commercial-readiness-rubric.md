# .NET Commercial Readiness Rubric

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Commercial Readiness Scale (0–5)

| Score | Band | Meaning |
|-------|------|---------|
| 0–1.4 | Not product | Demo/spike; not suitable for any customer |
| 1.5–2.4 | Demo/prototype | Works for one path; significant gaps; not production |
| 2.5–3.4 | POC candidate | Usable for PoC/evaluation; production gaps known |
| 3.5–4.2 | Commercial candidate | Strong product; documented gaps; addressable issues |
| 4.3–5.0 | Scoped commercial-ready | Ready for commercial release within stated scope |

---

## Gate 11 Commercial Readiness Criteria (C1–C20)

Per `plans/spec-to-feature-radical-correction-plan.md`:

| Criterion | Category | Description |
|-----------|----------|-------------|
| C1 | API | All public classes have XML documentation |
| C2 | API | No ambiguous method overloads |
| C3 | API | All load paths accept Stream overload |
| C4 | API | Custom exception types with meaningful hierarchy |
| C5 | Architecture | Parser, model, writer, exporter are distinct classes |
| C6 | Architecture | No partial class with > 3 files |
| C7 | Architecture | No God class (no single class > 600 LOC with all responsibilities) |
| C8 | Features | Core load/edit/save roundtrip verified |
| C9 | Features | Export to at least 2 target formats verified |
| C10 | Features | Malformed input handled with custom exception |
| C11 | Testing | Feature-organized test names (not sprint-named) |
| C12 | Testing | Edge/error/roundtrip tests present |
| C13 | Testing | Test count >= 50 for primary products |
| C14 | Packaging | README.md at src/net/{format}/ |
| C15 | Packaging | NuGet metadata complete (authors, urls, keywords) |
| C16 | Packaging | Version is 1.0.0 or higher (not 0.x pre-release) |
| C17 | Docs | At least one code example in README |
| C18 | Docs | XML doc on all public members |
| C19 | Quality | No `TODO` or `FIXME` in public API methods |
| C20 | Quality | Gate 11 status in csproj consistent with source header |

---

## Scoring Dimensions (12 dimensions, each 0–5)

1. **Public API Score** — Namespace quality + naming + discoverability
2. **Namespace Score** — Clean namespace, version strategy
3. **Naming Score** — Methods, properties, parameters idiomatic PascalCase
4. **Object Model Score** — Typed domain objects, not raw collections
5. **Class Segregation Score** — Parser/model/writer/exporter distinct
6. **Parser Quality Score** — Security guards, encoding, error handling
7. **Writer Quality Score** — Format-valid output, atomic write
8. **Edit Score** — Rich mutation API on typed objects
9. **Save Score** — Roundtrip verified
10. **Export Score** — Cross-format export with verified output
11. **Feature Availability Score** — FA levels averaged across domain
12. **Feature Complexity Score** — C levels averaged across domain
13. **Feature Comprehensiveness Score** — Domain coverage percentage
14. **Error Handling Score** — Custom exception hierarchy
15. **Test Meaningfulness Score** — Feature-organized, edge cases, roundtrip
16. **Examples/Docs Score** — README, XML docs, code examples
17. **Packaging Score** — NuGet metadata completeness
18. **Maintainability Score** — Architecture clean, no God classes

**Commercial Readiness Score = weighted average of all 18 dimensions**

---

## Product Commercial Readiness Estimates

### FODS .NET — Estimated Score: 3.8/5

**Strong:** Core CRUD operations, 5 exporters, DTD security, custom exceptions, 73+ tests, SortRows/FilterRows with InvariantCulture
**Gaps:**
- C3 FAIL: No `Load(Stream)` overload
- C14 FAIL: No README.md at `src/net/fods/`
- C15 PARTIAL: NuGet metadata incomplete
- C20 FAIL: Gate 11 contradiction in csproj vs source header
- C11 PARTIAL: Tests named by sprint (R87/R100) not by feature

**Verdict:** COMMERCIAL_CANDIDATE_WITH_GAPS

---

### FODT .NET — Estimated Score: 3.7/5

**Strong:** Paragraph/heading CRUD, 5 exporters, DTD security, full roundtrip
**Gaps:**
- C3 FAIL: No `Load(Stream)` overload
- C12 NEEDS_CONFIRMATION: Table ops (Spec/Table/*) wiring status unknown
- C14 FAIL: No README.md
- C20 FAIL: Gate 11 contradiction

**Verdict:** COMMERCIAL_CANDIDATE_WITH_GAPS

---

### NetPBM .NET — Estimated Score: 3.9/5

**Strong:** Stream load (only .NET product with it!), transforms/filters, 4-way partial class split, 65+ tests
**Gaps:**
- C14 FAIL: No README.md
- C9 PARTIAL: NetpbmExporter is within-family only (not documented)
- C16 FAIL: Version is 0.x pre-release

**Verdict:** COMMERCIAL_CANDIDATE_WITH_GAPS

---

### NDJSON .NET — Estimated Score: 2.9/5

**Strong:** Has stream load, filter/query API, has CsvExporter
**Gaps:**
- C8 PARTIAL: Raw JsonElement model, no typed domain object
- No AddRecord() method
- C10 PARTIAL: Limited custom exception depth
- C14 FAIL: No README.md

**Verdict:** POC_CANDIDATE

---

### CSV .NET — Estimated Score: 2.0/5

**Strong:** Clean separation, simple model
**Gaps:** Target writer role; no edit API; no custom exceptions; no examples; no docs
**Verdict:** DEMO_PROTOTYPE (as standalone product)

---

### TSV .NET — Estimated Score: 2.2/5

**Strong:** Has TsvCsvExporter; custom exception; clean code
**Gaps:** No primary facade (requires TsvReader); no edit API
**Verdict:** DEMO_PROTOTYPE (as standalone product)

---

### ZST .NET — Estimated Score: 1.3/5

**Strong:** Clean DTO; good magic byte inspection; exception type
**Gaps:**
- C8 FAIL: No roundtrip (can't compress/decompress)
- No write/compress capability whatsoever
- ZstDocument is pure DTO — not a usable product without ZstWriter

**Verdict:** DEMO_PROTOTYPE → CRITICAL GAPS (PQ-007)

---

### HTML/Markdown/TXT .NET — Estimated Score: 0.8/5

**Assessment:** Internal helpers. Not standalone products.
**Verdict:** NOT_PRODUCT
