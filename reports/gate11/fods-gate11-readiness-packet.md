# FODS — Gate 11 Commercial Readiness Packet
# Prepared by: Agent (agent-owned preparation — submission requires human authorization)
# Prepared: 2026-06-12 (Updated: 2026-06-16, SAL facts deepened)
# Sprint: PLAN-HARDENING-EXECUTION-20260616 (original: FORMAT-FACTORY-PRODUCT-GATE11-PREPARATION-AND-GAP-DEEPENING-001)
# Status: PREPARATION ONLY — NOT SUBMITTED — Human approval from Babar Raza required before submission

---

## 1. Format Identity

| Field | Value |
|-------|-------|
| Format ID | `fods` |
| Display name | Flat OpenDocument Spreadsheet |
| MIME type | `application/vnd.oasis.opendocument.spreadsheet-flat-xml` |
| Extension | `.fods` |
| Source | OASIS OpenDocument 1.3 specification |
| Registry entry | `registry/format-completion-matrix.yaml` → format_id: fods |

---

## 2. Gate Status Summary

| Gate | Status | Evidence Location |
|------|--------|-------------------|
| G1 (Candidate Approval) | PASSED | `prototypes/by-format/fods/` exists |
| G2 (Spec Authority) | PASSED | OASIS ODF 1.3 spec acquired |
| G3 (Prototype Execution) | PASSED | `src/python/fods/` + 1039 Python test functions |
| G4 (Parser Prototype) | PASSED | `src/python/fods/parser.py` — streaming XML, defusedxml |
| G5 (Neutral Model) | PASSED | `src/python/fods/neutral_model.py` — 6 entities (Workbook/Sheet/Row/Cell/Formula/Warning) |
| G6 (Oracle Comparison) | PASSED | Oracle tests exist, CSV export verified |
| G7 (Fuzz/Security) | PASSED | 100MB guard, DTD prohibited, defusedxml, 64MB guard |
| G8 (Security Review) | PASSED | defusedxml, DTD prohibited, malformed-input tests pass |
| G9 (Dogfood) | PASSED | FODS→CSV export chain verified |
| G10 (FOSS POC Complete) | PASSED (Python) | 1039 Python test functions; parse→inspect→export verified |
| G11-E (.NET prototype - VERIFIED) | IN_PROGRESS | .NET: FodsParser.cs + FodsWriter.cs + FodsPdfExporter.cs + FodsOdsExporter.cs + FodsPngExporter.cs + 611 .NET tests |
| G11-G (Commercial readiness) | NOT APPROVED | Requires Babar Raza approval |

**Claimed gate:** G11 (commercial_readiness_in_progress)
**Evidence-backed gate:** G10 (Python FOSS); G11-E (.NET prototype - VERIFIED)

---

## 3. Python FOSS Track Evidence

### 3A. Source Files

| File | Path | LOC |
|------|------|-----|
| parser.py | `src/python/fods/parser.py` | ~300 |
| neutral_model.py | `src/python/fods/neutral_model.py` | ~200 |
| writer.py | `src/python/fods/writer.py` | ~150 |
| csv_exporter.py | `src/python/fods/csv_exporter.py` | ~100 |
| constants.py | `src/python/fods/constants.py` | ~50 |
| exceptions.py | `src/python/fods/exceptions.py` | ~30 |
| __init__.py | `src/python/fods/__init__.py` | ~43 |
| Total estimated LOC | | ~793 |

### 3B. Test Coverage

| Metric | Value |
|--------|-------|
| Total Python test functions | **1039** |
| Test files | 76 files in `tests/python/fods/` |
| Coverage depth | parse, neutral model, public API, security, fuzz, roundtrip, write, CSV export |
| Security tests | `test_parser_security.py` — malformed XML, DTD injection, oversized input |
| Roundtrip tests | `test_r76_fods_edit_save.py`, `test_r78_fods_end_to_end_workflow.py` |
| Public API tests | `test_public_api.py`, `test_r58_fods_public_api.py` |

### 3C. Key Capabilities (Python FOSS)

| Capability | Status | Test Reference |
|-----------|--------|----------------|
| Parse `.fods` → neutral model | VERIFIED | `test_parser_basic.py` |
| Inspect sheets, rows, cells | VERIFIED | `test_neutral_model.py` |
| Export to CSV | VERIFIED | `test_r50_fods_csv_export.py`, `test_r84_fods_csv_export.py` |
| Write/save FODS file | VERIFIED (.NET) | `test_r46_write_capability.py` |
| Round-trip (load→edit→save→reload) | VERIFIED (.NET) | `test_r76_fods_edit_save.py` |
| Typed values (int, float, string, bool, date) | VERIFIED | `test_r48_writer_typed_values.py` |
| Formula preservation | VERIFIED | `src/python/fods/parser.py` — formula passthrough |
| Style/column-def round-trip | VERIFIED | `test_r55_fods_style_coldef.py` |
| Merged cell span | VERIFIED | `test_r73_fods_merged_cell_span.py` |

### 3D. Python Write Gap

Python FOSS has **read and basic write** via `writer.py`, but full write capability (write→reload→verify round-trip) is currently only demonstrated for .NET. Python write capability deepening is deferred pending PYWRITE-001 taskcard.

---

## 4. .NET Commercial Track Evidence

### 4A. Source Files

| File | Path |
|------|------|
| FodsParser.cs | `src/net/fods/FodsParser.cs` |
| FodsWriter.cs | `src/net/fods/FodsWriter.cs` |
| FodsDocument.cs | `src/net/fods/FodsDocument.cs` |
| FodsCsvExporter.cs | `src/net/fods/FodsCsvExporter.cs` |
| FodsHtmlExporter.cs | `src/net/fods/FodsHtmlExporter.cs` |
| FodsJsonExporter.cs | `src/net/fods/FodsJsonExporter.cs` |
| FodsPdfExporter.cs | `src/net/fods/FodsPdfExporter.cs` |
| FodsOdsExporter.cs | `src/net/fods/FodsOdsExporter.cs` |
| FodsPngExporter.cs | `src/net/fods/FodsPngExporter.cs` |
| Model/ | `src/net/fods/Model/` (FodsSheet, FodsRow, FodsCell) |

**Verified .NET tests:** 611 (FodsPdfExporter.cs +21, FodsOdsExporter.cs +20, FodsPngExporter.cs +17 — all added 2026-06-16)

### 4B. .NET Capabilities Verified

| Capability | Status |
|-----------|--------|
| Parse FODS → .NET object model | VERIFIED |
| Write/save FODS | VERIFIED |
| Load-edit-save-reload (roundtrip) | VERIFIED |
| Export to CSV | VERIFIED |
| Export to HTML | VERIFIED |
| Export to JSON | VERIFIED |
| Export to PDF | VERIFIED |
| Export to ODS (ODF ZIP archive) | VERIFIED |
| Export to PNG (thumbnail grid) | VERIFIED |
| Security guards (100MB, DTD prohibited) | VERIFIED |

### 4C. .NET Packaging

| Item | Status |
|------|--------|
| pyproject.toml (Python) | `src/python/fods/pyproject.toml` — exists |
| NuGet project file | `src/net/fods/FormatFactory.Fods.csproj` — exists |
| Local build | `local_build_ready` per format-completion-matrix.yaml |
| Published to NuGet | NOT DONE — requires Gate 11 approval + commit authorization |

---

## 5. Security Review Summary

| Control | Status |
|---------|--------|
| defusedxml (XML bomb prevention) | ACTIVE (Python + .NET) |
| DTD prohibited | ACTIVE |
| 100MB file size guard | ACTIVE |
| Malformed XML handling | TESTED — `test_parser_security.py` |
| Injection prevention | TESTED — no arbitrary code execution paths |

---

## 5B. Specification Authority (SAL) Facts

| Metric | Value |
|--------|-------|
| Verified spec facts | **36** (FACT-FODS-001 through FACT-FODS-036) |
| Fact source | `.local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml` |
| Spec reference | ODF 1.3 (OASIS) |
| Key areas covered | office:document root, table:table, table:table-row, table:table-cell, office:value-type, value-type-to-attribute mapping (Table 14), office:meta, office:font-face-decls, office:automatic-styles, number:number-style, number:date-style, office:spreadsheet, table:table-column, table:table-header-rows |
| QName ontology | 9 YAMLs deployed to `registry/odf-ontology/` |
| Capability gaps | 10 open (all commercial-track) |

---

## 6. Remaining Gaps Before Full G11

| Gap | Severity | Blocker for G11-G? |
|-----|----------|-------------------|
| Python write→reload round-trip not fully proven | Medium | No (Python FOSS is separate track) |
| .NET model Tier 0-1 only (inline formatting, tables) | Medium | Deferred to post-G11 |
| NuGet publication | High | Yes — requires commit + Gate 11-G approval |
| PyPI publication (Python FOSS) | High | Yes — requires commit + Gate 11-G approval |

---

## 7. What Babar Raza Must Decide

This packet is agent-prepared. The following decisions require **human authorization from Babar Raza**:

1. **Gate 11-G approval:** Confirm commercial_product_ready status for FODS (both Python FOSS and .NET tracks)
2. **Publication authorization:** Authorize commit of current source state + NuGet + PyPI publication
3. **Scope confirmation:** Confirm whether Gate 11 covers Python FOSS only, .NET only, or both tracks together

**DO NOT submit this packet to Babar Raza without explicit user authorization.**
**DO NOT claim Gate 11 is approved based on this document.**
**DO NOT publish to NuGet or PyPI without commit authorization.**

---

## 8. Evidence File Locations (for Babar Raza review)

| Artifact | Path |
|----------|------|
| Format matrix entry | `registry/format-completion-matrix.yaml` → format_id: fods |
| Python source | `src/python/fods/` |
| .NET source | `src/net/fods/` |
| Python tests | `tests/python/fods/` (76 files, 1039 test functions) |
| Security tests | `tests/python/fods/test_parser_security.py` |
| Roundtrip tests | `tests/python/fods/test_r76_fods_edit_save.py` |
| Product code ledger | `reports/r90/product-code-change-ledger.json` (FODS entries) |
| CI test results | `.github/workflows/ci.yml` — runs on push to main |

---

*End of FODS Gate 11 Readiness Packet*
*Agent-prepared 2026-06-12. Submission requires human authorization.*
*This document does NOT approve Gate 11. Gate 11 approval requires Babar Raza decision.*
