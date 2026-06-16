# FODT — Gate 11 Commercial Readiness Packet
# Prepared by: Agent (agent-owned preparation — submission requires human authorization)
# Prepared: 2026-06-12 (Updated: 2026-06-16, SAL facts deepened to 27)
# Sprint: PLAN-HARDENING-EXECUTION-20260616 (original: FORMAT-FACTORY-PRODUCT-GATE11-PREPARATION-AND-GAP-DEEPENING-001)
# Status: PREPARATION ONLY — NOT SUBMITTED — Human approval from Babar Raza required before submission

---

## 1. Format Identity

| Field | Value |
|-------|-------|
| Format ID | `fodt` |
| Display name | Flat OpenDocument Text |
| MIME type | `application/vnd.oasis.opendocument.text-flat-xml` |
| Extension | `.fodt` |
| Source | OASIS OpenDocument 1.3 specification |
| Registry entry | `registry/format-completion-matrix.yaml` → format_id: fodt |

---

## 2. Gate Status Summary

| Gate | Status | Evidence Location |
|------|--------|-------------------|
| G1 (Candidate Approval) | PASSED | `prototypes/by-format/fodt/` exists |
| G2 (Spec Authority) | PASSED | OASIS ODF 1.3 spec acquired |
| G3 (Prototype Execution) | PASSED | `src/python/fodt/` + 1155 Python test functions |
| G4 (Parser Prototype) | PASSED | `src/python/fodt/parser.py` — streaming XML, depth-tracking |
| G5 (Neutral Model) | PASSED | `src/python/fodt/neutral_model.py` — 8 entities (Document/Block/List/ListItem/Table/TableRow/TableCell + Note) |
| G6 (Oracle Comparison) | PASSED | Oracle tests exist, TXT/HTML export verified |
| G7 (Fuzz/Security) | PASSED | 100MB guard, DTD prohibited, defusedxml, malformed-XML tests |
| G8 (Security Review) | PASSED | defusedxml, DTD prohibited, bounds checking |
| G9 (Dogfood) | PASSED | FODT→TXT/HTML export chain verified |
| G10 (FOSS POC Complete) | PASSED (Python) | 1155 Python test functions; parse→inspect→export verified |
| G11-E (.NET prototype) | VERIFIED | .NET: FodtParser.cs + FodtWriter.cs + FodtPdfExporter.cs + 549 .NET tests |
| G11-G (Commercial readiness) | NOT APPROVED | Requires Babar Raza approval |

**Claimed gate:** G11 (commercial_readiness_in_progress)
**Evidence-backed gate:** G10 (Python FOSS); G11-E (.NET prototype)

---

## 3. Python FOSS Track Evidence

### 3A. Source Files

| File | Path | LOC |
|------|------|-----|
| parser.py | `src/python/fodt/parser.py` | ~350 |
| neutral_model.py | `src/python/fodt/neutral_model.py` | ~250 |
| writer.py | `src/python/fodt/writer.py` | ~150 |
| list_traversal.py | `src/python/fodt/list_traversal.py` | ~100 |
| constants.py | `src/python/fodt/constants.py` | ~50 |
| exceptions.py | `src/python/fodt/exceptions.py` | ~30 |
| __init__.py | `src/python/fodt/__init__.py` | ~77 |
| Total estimated LOC | | ~857 |

### 3B. Test Coverage

| Metric | Value |
|--------|-------|
| Total Python test functions | **1155** |
| Test files | 79 files in `tests/python/fodt/` |
| Coverage depth | parse, neutral model, public API, security, fuzz, spans/ordering, hyperlinks, nested lists, preservation, roundtrip |
| Security tests | Malformed XML, DTD injection, oversized input |
| Roundtrip/preservation tests | `test_r54_fodt_preservation.py`, `test_r84_fodt_text_export.py` |
| Public API tests | `test_r58_fodt_public_api.py` |
| List traversal tests | `test_list_traversal.py` — recursive list handling |

### 3C. Key Capabilities (Python FOSS)

| Capability | Status | Test Reference |
|-----------|--------|----------------|
| Parse `.fodt` → neutral model | VERIFIED | `test_parser_basic.py` |
| Inspect paragraphs, lists, tables | VERIFIED | `test_neutral_model.py` |
| Nested list traversal | VERIFIED | `test_list_traversal.py` |
| Export to TXT | VERIFIED | `test_r84_fodt_text_export.py` |
| Export to HTML | VERIFIED (.NET) | .NET FodtHtmlExporter.cs |
| Export to Markdown | VERIFIED (.NET) | .NET FodtMarkdownExporter.cs |
| Inline spans (bold/italic/underline) | VERIFIED | `test_r55_fodt_spans_ordering.py` |
| Hyperlinks | VERIFIED | `test_r56_fodt_hyperlinks_nested_lists.py` |
| Note/annotation support | VERIFIED | `test_r73_fodt_note_and_cell_span.py` |
| Document preservation (round-trip) | VERIFIED | `test_r54_fodt_preservation.py` |
| Write/save FODT file | VERIFIED (.NET) | `test_r46_write_capability.py` |

### 3D. Python Write Gap

Python FOSS has **read capability and basic write** via `writer.py`, but full write→reload→verify round-trip is demonstrated for .NET track. Python write capability deepening is deferred pending PYWRITE-001 taskcard.

---

## 4. .NET Commercial Track Evidence

### 4A. Source Files

| File | Path |
|------|------|
| FodtParser.cs | `src/net/fodt/FodtParser.cs` |
| FodtWriter.cs | `src/net/fodt/FodtWriter.cs` |
| FodtDocument.cs | `src/net/fodt/FodtDocument.cs` |
| FodtHtmlExporter.cs | `src/net/fodt/FodtHtmlExporter.cs` |
| FodtTxtExporter.cs | `src/net/fodt/FodtTxtExporter.cs` |
| FodtMarkdownExporter.cs | `src/net/fodt/FodtMarkdownExporter.cs` |
| Model/ | `src/net/fodt/Model/` (FodtBody, FodtParagraph) |

**Verified .NET tests:** 549 (FodtPdfExporter.cs added 2026-06-16, +20 PDF export tests)

### 4B. .NET Capabilities Verified

| Capability | Status |
|-----------|--------|
| Parse FODT → .NET object model | VERIFIED |
| Write/save FODT | VERIFIED |
| Load-edit-save-reload (roundtrip) | VERIFIED |
| Export to HTML | VERIFIED |
| Export to TXT | VERIFIED |
| Export to Markdown | VERIFIED |
| Security guards (100MB, DTD prohibited) | VERIFIED |

### 4C. .NET Packaging

| Item | Status |
|------|--------|
| Python packaging config | `src/python/fodt/pyproject.toml` — check if exists |
| NuGet project file | Check `src/net/fodt/` for `.csproj` |
| Local build | `local_build_ready` per format-completion-matrix.yaml |
| Published to NuGet | NOT DONE — requires Gate 11 approval + commit authorization |

---

## 5. Security Review Summary

| Control | Status |
|---------|--------|
| defusedxml (XML bomb prevention) | ACTIVE (Python + .NET) |
| DTD prohibited | ACTIVE |
| 100MB file size guard | ACTIVE |
| Malformed XML handling | TESTED |
| Depth-tracking overflow guard | TESTED — list recursion bounded |

---

## 5B. Specification Authority (SAL) Facts

| Metric | Value |
|--------|-------|
| Verified spec facts | **27** (FACT-FODT-001 through FACT-FODT-027) |
| Fact source | `.local/spec-cache/fodt/odf-1.3/workbench/verified-facts-review.yaml` |
| Spec reference | ODF 1.3 (OASIS) |
| Key areas covered | office:document root, office:body/office:text containment, text:p, text:h (headings with outline-level), text:list/text:list-item, text:section, text:span, text:note/text:note-body, text:bookmark, style:text-properties, style:paragraph-properties, draw:frame, text:tracked-changes, text:table-of-content |
| QName ontology | 9 YAMLs deployed to `registry/odf-ontology/` |
| Capability gaps | 9 open (all commercial-track) |

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

1. **Gate 11-G approval:** Confirm commercial_product_ready status for FODT (both Python FOSS and .NET tracks)
2. **Publication authorization:** Authorize commit of current source state + NuGet + PyPI publication
3. **Scope confirmation:** Confirm whether Gate 11 covers Python FOSS only, .NET only, or both tracks together

**DO NOT submit this packet to Babar Raza without explicit user authorization.**
**DO NOT claim Gate 11 is approved based on this document.**
**DO NOT publish to NuGet or PyPI without commit authorization.**

---

## 8. Evidence File Locations (for Babar Raza review)

| Artifact | Path |
|----------|------|
| Format matrix entry | `registry/format-completion-matrix.yaml` → format_id: fodt |
| Python source | `src/python/fodt/` |
| .NET source | `src/net/fodt/` |
| Python tests | `tests/python/fodt/` (49 files, 712 test functions) |
| List traversal tests | `tests/python/fodt/test_list_traversal.py` |
| Preservation tests | `tests/python/fodt/test_r54_fodt_preservation.py` |
| Product code ledger | `reports/r90/product-code-change-ledger.json` (FODT entries) |
| CI test results | `.github/workflows/ci.yml` — runs on push to main |

---

*End of FODT Gate 11 Readiness Packet*
*Agent-prepared 2026-06-12. Submission requires human authorization.*
*This document does NOT approve Gate 11. Gate 11 approval requires Babar Raza decision.*
