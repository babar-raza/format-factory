# Initial Product Quality Risk Register

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Risk Register Summary

| Total Risks | CRITICAL | HIGH | MEDIUM | LOW |
|-------------|----------|------|--------|-----|
| 18 | 2 | 8 | 6 | 2 |

---

## Critical Risks

### RISK-001 — ZST .NET Missing Write Capability

| Field | Value |
|-------|-------|
| **ID** | RISK-001 |
| **Severity** | CRITICAL |
| **PQ-ID** | PQ-007 |
| **Product** | ZST .NET |
| **Risk** | ZstDocument is a pure read-only DTO. No ZstWriter exists. A .NET Zstandard library that cannot compress data is functionally useless as a product. |
| **Impact** | ZST .NET cannot be published as a commercial product. Any user who installs it expecting to compress files will be unable to do so. |
| **Mitigation** | Implement ZstWriter with Compress(byte[]) and Decompress(byte[]) methods. See pilot-product-quality-fix-plan.md. |
| **Status** | OPEN |
| **Fix Sprint** | QF-1 |

### RISK-002 — Gate 11 Approval Contradiction

| Field | Value |
|-------|-------|
| **ID** | RISK-002 |
| **Severity** | CRITICAL |
| **PQ-ID** | PQ-006 |
| **Product** | FODS .NET |
| **Risk** | FormatFactory.Fods.csproj PackageDescription says "Gate 11 approved 2026-06-05". FodsDocument.cs line 2-3 says "Gate 11 status: commercial_readiness_in_progress (NOT approved)". A NuGet consumer would believe the package is commercially approved when it is not. |
| **Impact** | Legal risk; false product claim; potential customer complaint when product does not meet expected quality bar. |
| **Mitigation** | Update csproj PackageDescription to remove the approval claim. Replace with: "commercial_readiness_in_progress — Gate 11 pending". |
| **Status** | OPEN |
| **Fix Sprint** | QF-1 (XS effort) |

---

## High Risks

### RISK-003 — Python Wildcard Namespace Pollution

| Field | Value |
|-------|-------|
| **ID** | RISK-003 |
| **Severity** | HIGH |
| **PQ-ID** | PQ-001 |
| **Products** | All 20 Python packages |
| **Risk** | All Python __init__.py files use wildcard star-imports. 50+ names appear in `from fods import *`. Internal implementation details are exposed as public API. |
| **Impact** | Breaking changes become invisible (any internal rename breaks users). IDE autocomplete is cluttered. Name collisions with user code are possible. |
| **Mitigation** | Replace all wildcard imports with explicit curated __all__ lists. |
| **Status** | OPEN |
| **Fix Sprint** | QF-3 |

### RISK-004 — Python Dual API Confusion (FODS)

| Field | Value |
|-------|-------|
| **ID** | RISK-004 |
| **Severity** | HIGH |
| **PQ-ID** | PQ-002 |
| **Products** | FODS Python |
| **Risk** | FODS Python exports both a dict-function API (`parse_fods`, `workbook_set_cell_value`) and a class-based API (`FodsDocument`) with equal prominence and no guidance. |
| **Impact** | Developer confusion. A user choosing the dict API will have a different (worse) experience than one choosing the class API. API surface is effectively doubled. |
| **Mitigation** | Designate FodsDocument as the primary API. Mark dict functions as internal or deprecated. |
| **Status** | OPEN |
| **Fix Sprint** | QF-1 |

### RISK-005 — All Python Packaging Incomplete

| Field | Value |
|-------|-------|
| **ID** | RISK-005 |
| **Severity** | HIGH |
| **PQ-ID** | PQ-004 |
| **Products** | All 20 Python packages |
| **Risk** | pyproject.toml for all 20 packages missing: authors, [project.urls], keywords, classifiers, readme. |
| **Impact** | PyPI listing will show incomplete metadata. Users cannot find packages by keyword. Package credibility is low. |
| **Mitigation** | Enrich all 20 pyproject.toml files with complete metadata. |
| **Status** | OPEN |
| **Fix Sprint** | QF-2 |

### RISK-006 — All .NET README Missing

| Field | Value |
|-------|-------|
| **ID** | RISK-006 |
| **Severity** | HIGH |
| **PQ-ID** | PQ-005 |
| **Products** | All 10 .NET packages |
| **Risk** | All .NET csproj files reference `<PackageReadmeFile>README.md</PackageReadmeFile>` but no README.md exists at src/net/{format}/. |
| **Impact** | NuGet packaging will fail or warn. NuGet.org listing will show no README. |
| **Mitigation** | Create README.md at each src/net/{format}/ directory. |
| **Status** | OPEN |
| **Fix Sprint** | QF-2 |

### RISK-007 — FODP Undocumented Read-Only Limitation

| Field | Value |
|-------|-------|
| **ID** | RISK-007 |
| **Severity** | HIGH |
| **PQ-ID** | PQ-009 |
| **Products** | FODP Python |
| **Risk** | FODP Python has no write_fodp() function. The `consumer_roundtrip.py` example name implies roundtrip (load → edit → save) which is impossible. No user-facing docs state the limitation. |
| **Impact** | User installs FODP expecting to create/modify presentations; discovers it's read-only only after exploration. Poor developer experience. |
| **Mitigation** | Add write_fodp() raising NotImplementedError("FODP write not yet supported. Use read/inspect API only."). Rename consumer_roundtrip.py to consumer_inspect.py. |
| **Status** | OPEN |
| **Fix Sprint** | QF-1 (XS effort) |

### RISK-008 — No Product README for 30 Products

| Field | Value |
|-------|-------|
| **ID** | RISK-008 |
| **Severity** | HIGH |
| **PQ-ID** | PQ-014 |
| **Products** | All 30 |
| **Risk** | No README.md exists for any Python or .NET product (except PBM/PGM/PPM which have docs/api/*.md, not product-level READMEs). |
| **Impact** | Developers who find the package via PyPI/NuGet have no quickstart guidance. First-use experience is blind navigation. |
| **Mitigation** | Create README.md for all 30 products. |
| **Status** | OPEN |
| **Fix Sprint** | QF-2 |

### RISK-009 — HTML/Markdown/TXT Listed as Standalone Products

| Field | Value |
|-------|-------|
| **ID** | RISK-009 |
| **Severity** | HIGH |
| **PQ-ID** | PQ-015 |
| **Products** | HTML .NET, Markdown .NET, TXT .NET |
| **Risk** | These are single-file writer helpers used internally by FODS and FODT exporters. They are listed in the registry as standalone products. |
| **Impact** | Marketing these as products dilutes the product story. Installing them independently provides no useful API. |
| **Mitigation** | Reclassify as internal helpers in registry and documentation. |
| **Status** | OPEN |
| **Fix Sprint** | QF-4 (XS effort — registry doc change only) |

---

## Medium Risks

### RISK-010 — No Stream Load for Most .NET Products

| Field | Value |
|-------|-------|
| **ID** | RISK-010 |
| **PQ-ID** | PQ-008 |
| **Severity** | MEDIUM |
| **Products** | FODS .NET, FODT .NET (and CSV, TSV) |
| **Risk** | Most .NET products only support Load(string filePath). Cannot use with MemoryStream, HttpResponseStream, or other in-memory workflows. |
| **Mitigation** | Add Load(Stream stream) overloads to FODS and FODT at minimum. |
| **Fix Sprint** | QF-3 |
| **Status** | OPEN |

### RISK-011 — NdjsonDocument Exposes Raw JsonElement

| Field | Value |
|-------|-------|
| **ID** | RISK-011 |
| **PQ-ID** | PQ-010 |
| **Severity** | MEDIUM |
| **Products** | NDJSON .NET |
| **Risk** | NdjsonDocument.Records returns IReadOnlyList<JsonElement>. JsonElement is a System.Text.Json internal type — leaks framework dependency into public API. |
| **Mitigation** | Introduce NdjsonRecord typed wrapper. |
| **Fix Sprint** | QF-3 |
| **Status** | OPEN |

### RISK-012 — No CLI Entry Points for Any Python Package

| Field | Value |
|-------|-------|
| **ID** | RISK-012 |
| **PQ-ID** | PQ-019 |
| **Severity** | MEDIUM |
| **Products** | All 20 Python packages |
| **Risk** | FOSS libraries benefit from CLI tools. None of the 20 packages provide any [project.scripts] entry points. |
| **Mitigation** | Add minimal CLI tools to key packages (fods, fodt, pbm, zst). |
| **Fix Sprint** | QF-4 |
| **Status** | OPEN |

### RISK-013 — Examples Use Dev-Path Imports

| Field | Value |
|-------|-------|
| **ID** | RISK-013 |
| **PQ-ID** | PQ-003 |
| **Severity** | MEDIUM |
| **Products** | All Python examples |
| **Risk** | All examples use sys.path.insert + from src.python.{format} import. A pip-installed user cannot run these examples. |
| **Mitigation** | Update examples to use installed-package imports with dev fallback. |
| **Fix Sprint** | QF-4 |
| **Status** | OPEN |

### RISK-014 — Sprint-Named Test Files

| Field | Value |
|-------|-------|
| **ID** | RISK-014 |
| **PQ-ID** | PQ-017 |
| **Severity** | MEDIUM |
| **Products** | FODS .NET, FODT .NET, NetPBM .NET |
| **Risk** | ~70% of test files named R87, R100, etc. — not discoverable by feature. |
| **Mitigation** | Rename test files to feature-based names. Low urgency. |
| **Fix Sprint** | QF-5 |
| **Status** | OPEN |

### RISK-015 — _shared/ Dead Abstraction

| Field | Value |
|-------|-------|
| **ID** | RISK-015 |
| **PQ-ID** | PQ-016 |
| **Severity** | MEDIUM |
| **Products** | All Python packages |
| **Risk** | _shared/_base_codec.py, _base_parser.py exist but are not used by any format package. Dead code with no value. |
| **Mitigation** | Delete _shared/ or wire to all packages. |
| **Fix Sprint** | QF-5 |
| **Status** | OPEN |

---

## Low Risks

### RISK-016 — NetpbmExporter Scope Undocumented

| Field | Value |
|-------|-------|
| **ID** | RISK-016 |
| **PQ-ID** | PQ-013 |
| **Severity** | LOW |
| **Products** | NetPBM .NET |
| **Risk** | NetpbmExporter only converts within the Netpbm family (PBM→PGM, PBM→PPM). Not documented as such. Users might expect external format export (e.g. to JPEG). |
| **Mitigation** | Add XML doc comment to NetpbmExporter explaining within-family scope. |
| **Fix Sprint** | QF-5 (XS effort) |
| **Status** | OPEN |

### RISK-017 — No Type Stubs for Python Packages

| Field | Value |
|-------|-------|
| **ID** | RISK-017 |
| **PQ-ID** | PQ-020 |
| **Severity** | LOW |
| **Products** | All 20 Python packages |
| **Risk** | Without .pyi stub files, IDE autocomplete and mypy type checking don't work for installed packages. |
| **Mitigation** | Generate .pyi files via stubgen or manual authoring. |
| **Fix Sprint** | QF-5 |
| **Status** | OPEN |

---

## Risk Mitigation Timeline

| Sprint | Risks Resolved |
|--------|---------------|
| QF-1 (P0) | RISK-001, RISK-002, RISK-004, RISK-007 |
| QF-2 (P1) | RISK-005, RISK-006, RISK-008 |
| QF-3 (P1-P2) | RISK-003, RISK-010, RISK-011 |
| QF-4 (P2) | RISK-009, RISK-012, RISK-013 |
| QF-5 (P3) | RISK-014, RISK-015, RISK-016, RISK-017 |
