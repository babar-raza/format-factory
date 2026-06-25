# Product Quality Problem Matrix

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Problem Categories

| Category | Code | Description |
|----------|------|-------------|
| Product Code | PRODUCT_CODE | Source code quality issues |
| Public API | PUBLIC_API | API surface quality issues |
| API Naming | API_NAMING | Method/property naming issues |
| API Usability | API_USABILITY | Developer usability issues |
| Class Segregation | CLASS_SEGREGATION | Responsibility division issues |
| Object Model | OBJECT_MODEL | Domain model depth/typing |
| Parser | PARSER | Parse/load implementation issues |
| Writer | WRITER | Serialize/save implementation issues |
| Edit Workflow | EDIT_WORKFLOW | Mutation API issues |
| Save Roundtrip | SAVE_ROUNDTRIP | Roundtrip fidelity issues |
| Export Dogfood | EXPORT_DOGFOOD | Cross-format export issues |
| Feature Availability | FEATURE_AVAILABILITY | Missing features |
| Feature Complexity | FEATURE_COMPLEXITY | Implementation depth |
| Feature Comprehensiveness | FEATURE_COMPREHENSIVENESS | Domain coverage gaps |
| Error Handling | ERROR_HANDLING | Exception model issues |
| Edge Cases | EDGE_CASES | Edge case coverage gaps |
| Test Coverage | TEST_COVERAGE | Test breadth gaps |
| Test Meaningfulness | TEST_MEANINGFULNESS | Test quality issues |
| Examples/Docs | EXAMPLES_DOCS | Documentation and example gaps |
| Packaging | PACKAGING | Package metadata issues |
| End User Workflow | END_USER_WORKFLOW | User experience gaps |
| Claim Overreach | CLAIM_OVERREACH | False or inflated claims |
| Commercial Readiness | COMMERCIAL_READINESS | .NET commercial product gaps |
| FOSS Readiness | FOSS_READINESS | Python FOSS product gaps |

---

## Severity Levels

| Level | Meaning |
|-------|---------|
| CRITICAL | Blocks product use; fundamental gap or contradiction |
| HIGH | Significant negative impact; must fix before release |
| MEDIUM | Noticeable quality gap; should fix before release |
| LOW | Minor issue; can defer |

---

## Confidence Levels

| Level | Meaning |
|-------|---------|
| VERIFIED | Confirmed by direct source inspection |
| LIKELY | Strongly suggested by available evidence |
| NEEDS_CONFIRMATION | Requires additional source inspection to confirm |

---

## Pre-Identified Problems (PQ-001 through PQ-020)

| Problem ID | Category | Severity | Confidence | Product(s) | Description |
|------------|----------|----------|------------|------------|-------------|
| PQ-001 | PUBLIC_API | HIGH | VERIFIED | All Python packages | Wildcard star-imports in `__init__.py` — uncontrolled namespace surface. `from .parser import *` exposes ~50+ names per package. |
| PQ-002 | API_USABILITY | HIGH | VERIFIED | FODS Python | Dual API: dict-function API (`parse_fods()`, `workbook_set_cell_value()`) AND class-based API (`FodsDocument`) both exported. No guidance on which to use. |
| PQ-003 | EXAMPLES_DOCS | MEDIUM | VERIFIED | All Python packages | All examples use dev-path imports (`sys.path.insert` + `from src.python.fods import ...`), not installed-package imports (`from fods import ...`). |
| PQ-004 | PACKAGING | HIGH | VERIFIED | All Python packages (20) | `pyproject.toml` missing: `authors`, `[project.urls]`, `keywords`, `classifiers`, `readme`. All 20 packages affected. |
| PQ-005 | PACKAGING | HIGH | VERIFIED | All .NET packages (10) | `README.md` missing at `src/net/{format}/`. csproj files reference it via `PackageReadmeFile = README.md`. |
| PQ-006 | CLAIM_OVERREACH | HIGH | VERIFIED | FODS .NET | `FormatFactory.Fods.csproj` PackageDescription says "Gate 11 approved 2026-06-05" but `FodsDocument.cs` header says "Gate 11 status: commercial_readiness_in_progress (NOT approved)". |
| PQ-007 | FEATURE_AVAILABILITY | CRITICAL | VERIFIED | ZST .NET | `ZstDocument` is a pure read-only DTO. No `ZstWriter.cs` exists. No compress, decompress, or roundtrip capability. `ZstParser.Parse()` is the only entry point. |
| PQ-008 | PUBLIC_API | HIGH | VERIFIED | FODS .NET, FODT .NET | No `Load(Stream)` overload. `NdjsonDocument` and `NetpbmDocument` have stream load; FODS and FODT don't. Inconsistent family API. |
| PQ-009 | FEATURE_AVAILABILITY | HIGH | VERIFIED | FODP Python | Read-only product with no `write_fodp()`. Limitation not documented for users. `consumer_roundtrip.py` example title is misleading. |
| PQ-010 | OBJECT_MODEL | MEDIUM | VERIFIED | NDJSON .NET | `NdjsonDocument` holds raw `List<JsonElement>`. No typed domain object (e.g., `NdjsonRecord`). `JsonElement` leaks into public API. |
| PQ-011 | API_NAMING | MEDIUM | VERIFIED | NDJSON .NET | `NdjsonDocument.Load(string content)` — parameter name `content` is ambiguous (content string or file path?). Compare: `LoadFile(string path)`. |
| PQ-012 | FEATURE_AVAILABILITY | MEDIUM | NEEDS_CONFIRMATION | FODT .NET | `Spec/Table/Table.cs`, `TableCell.cs`, `TableRow.cs` exist but are architecture-only stubs. Table operations may NOT be wired in `FodtDocument` public API. |
| PQ-013 | FEATURE_COMPREHENSIVENESS | LOW | VERIFIED | NetPBM .NET | `NetpbmExporter` is within-family only (PBM→PGM, PBM→PPM). Scope not documented in public API. Users expecting external format export are surprised. |
| PQ-014 | EXAMPLES_DOCS | HIGH | VERIFIED | All products (30) | No `README.md` for any Python or .NET product. Only PBM/PGM/PPM have `docs/api/*.md` files. |
| PQ-015 | COMMERCIAL_READINESS | HIGH | VERIFIED | HTML/Markdown/TXT .NET | These are internal writer helpers used by FODS/FODT exporters. Not standalone commercial products. Listed in product registry as products. |
| PQ-016 | CLASS_SEGREGATION | MEDIUM | VERIFIED | All Python packages | `src/python/_shared/_base_codec.py` and `_base_parser.py` exist but are not used by most format packages. Dead abstraction. |
| PQ-017 | TEST_MEANINGFULNESS | MEDIUM | VERIFIED | FODS .NET, FODT .NET, NetPBM .NET | Tests named by sprint (`FodsR87ProductDeepening.cs`, `FodsR100AddSheetTests.cs`). 60-80% sprint-named. Makes feature coverage discovery difficult. |
| PQ-018 | API_USABILITY | MEDIUM | VERIFIED | FODS .NET | `FodsDocument.GetColumnHeaders()` has 3 overloads including a `static` variant. No other FodsDocument methods are static. Inconsistent overload design. |
| PQ-019 | FOSS_READINESS | HIGH | VERIFIED | All Python packages (20) | No `[project.scripts]` CLI entry points in any Python package's `pyproject.toml`. Users cannot run `fods --help` or `pbm --convert` from command line. |
| PQ-020 | FOSS_READINESS | MEDIUM | VERIFIED | All Python packages (20) | No type stubs (`.pyi` files) for any package. Poor IDE support and type checking integration. |

---

## Additional Problems (PQ-021 through PQ-030)

| Problem ID | Category | Severity | Confidence | Product(s) | Description |
|------------|----------|----------|------------|------------|-------------|
| PQ-021 | API_USABILITY | MEDIUM | VERIFIED | SYLK Python | `set_cell_value(src, dest, row, col, value)` is file-based (takes src+dest paths). Edit operations should be model-based. |
| PQ-022 | FEATURE_AVAILABILITY | MEDIUM | VERIFIED | XCF Python | No write or export capability. GIMP XCF format is read-only in Format Factory Python. No documentation of this limitation. |
| PQ-023 | OBJECT_MODEL | MEDIUM | VERIFIED | FODG Python, FODP Python, GNUMERIC Python | Dict-only model — no typed class with named properties for shapes, pages, or cells. |
| PQ-024 | TEST_COVERAGE | HIGH | VERIFIED | ZST .NET | Only 2 test files. No roundtrip test possible (no write). Cannot meaningfully test the compression library without compress/decompress. |
| PQ-025 | PACKAGING | MEDIUM | VERIFIED | FODS .NET | `csproj` has `TargetFramework = net10.0` and `Version = 0.1.0-tier0`. Version suffix `tier0` is not a standard semver pre-release format. |
| PQ-026 | CLAIM_OVERREACH | MEDIUM | VERIFIED | Python FODP | `consumer_roundtrip.py` example name suggests true roundtrip but FODP is read-only. Misleading example name. |
| PQ-027 | FOSS_READINESS | MEDIUM | NEEDS_CONFIRMATION | All Python packages | No docstrings confirmed on all public functions. Need audit per package. |
| PQ-028 | API_NAMING | LOW | VERIFIED | Multiple Python packages | Inconsistent primary function naming: `parse_fods` vs `load_ods` vs `load` (ABW, FODG, FODP) vs `parse_pbm_strict` — no family convention. |
| PQ-029 | EDIT_WORKFLOW | MEDIUM | VERIFIED | NDJSON .NET | No `AddRecord()` method in `NdjsonDocument`. Can Filter/query but cannot add new records to an existing document. |
| PQ-030 | COMMERCIAL_READINESS | HIGH | VERIFIED | All .NET products | No code examples for any .NET product in `examples/` directory. Only Python examples exist. |
