# Commercial Readiness Rubric

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Purpose

Scores .NET products for commercial release readiness. Commercial products must meet a higher
bar than POC or FOSS products: they must be professionally packaged, have stable APIs, be
backed by documentation, and not carry contradictions or false claims.

---

## Commercial Readiness Gate 11 Criteria (C1–C20)

These criteria come from `plans/strategic/spec-to-feature-radical-correction-plan.md`. Gate 11 requires
ALL C1–C20 to pass. Status: NOT approved. Approver: Babar Raza only.

| Criterion | Description | Required |
|-----------|-------------|---------|
| C1 | Spec-conformant namespace and class names | YES |
| C2 | All public APIs have XML documentation | YES |
| C3 | Exception hierarchy: product base + subtypes | YES |
| C4 | Stream load overload for all document types | YES |
| C5 | Save(string path) or equivalent for all writable products | YES |
| C6 | Export to at least one alternate format | YES |
| C7 | README.md at src/net/{format}/ | YES |
| C8 | NuGet metadata complete (authors, urls, keywords, classifiers) | YES |
| C9 | Roundtrip test (load → edit → save → reload → compare) | YES |
| C10 | Malformed input test (parser does not crash on bad input) | YES |
| C11 | No Gate 11 approval claim contradictions | YES |
| C12 | No architecture-only stubs in public API surface | YES |
| C13 | Test suite organized by feature (not sprint) | REQUIRED |
| C14 | Version consistency (csproj vs NuGet metadata) | YES |
| C15 | No internal implementation details in public namespace | YES |
| C16 | Culture-invariant number parsing in parser and writer | YES |
| C17 | Thread-safe read operations | YES |
| C18 | CI pipeline passes | YES |
| C19 | Sample file present for format | YES |
| C20 | At least one usage example (installed, not dev-path) | YES |

---

## Commercial Readiness Scoring (18 Dimensions)

Each dimension scored 0–5.

### Dimension 1: Namespace and Class Quality

| Score | Criteria |
|-------|---------|
| 0 | Random naming; no namespace |
| 1 | Generic namespace (e.g. `Library`) |
| 2 | Format-prefixed names but not brand-consistent |
| 3 | `FormatFactory.{Format}` namespace; classes named for domain |
| 4 | Consistent naming across all product classes |
| 5 | Spec-conformant class names per C1 criterion |

### Dimension 2: XML Documentation

| Score | Criteria |
|-------|---------|
| 0 | No XML docs |
| 1 | < 25% of public members documented |
| 2 | 25–50% documented |
| 3 | 50–75% documented |
| 4 | 75–90% documented; all constructors and key methods |
| 5 | 100% documented including examples and exceptions |

### Dimension 3: Exception Handling

| Score | Criteria |
|-------|---------|
| 0 | Raw framework exceptions |
| 1 | Single generic product exception |
| 2 | Base + 1 subtype |
| 3 | Base + 2-3 subtypes; meaningful messages |
| 4 | Full hierarchy; inner exception; diagnostic context |
| 5 | Full hierarchy; recovery hints; serializable exceptions |

### Dimension 4: Load API Completeness

| Score | Criteria |
|-------|---------|
| 0 | No load capability |
| 1 | Load(string path) only |
| 2 | Load(string path) + handles file not found |
| 3 | Load(string path) + Load(Stream) |
| 4 | Load(string path) + Load(Stream) + Load(byte[]) |
| 5 | All overloads + async variants + cancellation token |

### Dimension 5: Edit API Completeness

| Score | Criteria |
|-------|---------|
| 0 | No edit capability |
| 1 | Single edit operation |
| 2 | Basic CRUD on primary object |
| 3 | Full CRUD on all model objects |
| 4 | CRUD + bulk operations + sort/filter |
| 5 | CRUD + bulk + transactions + undo |

### Dimension 6: Save API Completeness

| Score | Criteria |
|-------|---------|
| 0 | No save capability |
| 1 | Save overwrites input only |
| 2 | Save(string path) to any path |
| 3 | Save(string path) + Save(Stream) |
| 4 | Save + optional format parameters |
| 5 | Save + async + cancellation + atomic write |

### Dimension 7: Export Coverage

| Score | Criteria |
|-------|---------|
| 0 | No export |
| 1 | One export format |
| 2 | 2-3 export formats |
| 3 | 4-5 export formats including at least CSV/JSON |
| 4 | 5+ export formats; all with stream overloads |
| 5 | All export formats + conversion API + pipeline support |

### Dimension 8: Packaging

| Score | Criteria |
|-------|---------|
| 0 | No NuGet package |
| 1 | NuGet package exists; minimal metadata |
| 2 | NuGet + version + description |
| 3 | NuGet + version + description + README |
| 4 | Full metadata: authors, urls, keywords, classifiers, readme, tags |
| 5 | Full metadata + icon + release notes + changelog |

### Dimension 9: Documentation

| Score | Criteria |
|-------|---------|
| 0 | No documentation |
| 1 | README stub only |
| 2 | README with overview and installation |
| 3 | README + quickstart code example |
| 4 | README + quickstart + API reference |
| 5 | README + quickstart + API reference + tutorials + troubleshooting |

### Dimension 10: Test Completeness

| Score | Criteria |
|-------|---------|
| 0 | No tests |
| 1 | Smoke tests only |
| 2 | Happy path tests |
| 3 | Behavior tests + roundtrip test |
| 4 | Behavior + roundtrip + edge cases + malformed input |
| 5 | Full product-confidence suite; performance tests; regression suite |

---

## Commercial Readiness Scores — .NET Products

| Product | Namespace | XmlDoc | Except | Load | Edit | Save | Export | Package | Docs | Tests | Avg |
|---------|-----------|--------|--------|------|------|------|--------|---------|------|-------|-----|
| FODS | 4 | 3 | 4 | 3 | 5 | 4 | 4 | 2 | 1 | 4 | 3.4 |
| FODT | 4 | 3 | 4 | 3 | 4 | 4 | 4 | 2 | 1 | 4 | 3.3 |
| NetPBM | 4 | 3 | 4 | 4 | 4 | 4 | 3 | 2 | 2 | 4 | 3.4 |
| NDJSON | 4 | 2 | 4 | 4 | 2 | 3 | 3 | 2 | 1 | 3 | 2.8 |
| CSV | 4 | 2 | 1 | 3 | 2 | 2 | 1 | 2 | 1 | 2 | 2.0 |
| TSV | 4 | 2 | 3 | 2 | 1 | 2 | 3 | 2 | 1 | 2 | 2.2 |
| ZST | 3 | 2 | 3 | 2 | 0 | 0 | 0 | 2 | 1 | 2 | 1.5 |
| HTML | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0.5 |
| Markdown | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0.5 |
| TXT | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0.5 |

---

## Commercial Readiness Bands

| Score | Band | Verdict |
|-------|------|---------|
| 0.0 – 1.4 | NOT_PRODUCT | Internal helper only |
| 1.5 – 2.4 | DEMO_PROTOTYPE | Not publishable |
| 2.5 – 3.4 | POC_CANDIDATE | Fix P1 issues before release |
| 3.5 – 4.2 | COMMERCIAL_CANDIDATE | Minor fixes; P0 blockers must close |
| 4.3 – 5.0 | COMMERCIALLY_READY | Gate 11 eligible |

**Current verdicts:**
- FODS .NET: POC_CANDIDATE (3.4) — close to COMMERCIAL_CANDIDATE
- FODT .NET: POC_CANDIDATE (3.3) — same
- NetPBM .NET: POC_CANDIDATE (3.4) — same
- NDJSON .NET: POC_CANDIDATE (2.8) — NdjsonRecord model needed
- CSV/TSV .NET: DEMO_PROTOTYPE — thin products
- ZST .NET: DEMO_PROTOTYPE (1.5) — no write capability
- HTML/Markdown/TXT .NET: NOT_PRODUCT — writer helpers only
