# R25 FODS/FODT G11-F Hardening Report
# Sprint: FORMAT-FACTORY-R25-AI-PHASE1-GATE4-FORWARD-TRAIN-AND-R24-METADATA-SYNC-001
# Date: 2026-05-18
# Gate: 5 — FODS/FODT G11-F hardening continuation
# Lane: E

## Baseline Confirmation (R24)

| Suite | R24 Baseline |
|-------|-------------|
| FODS | 112/112 PASS |
| FODT | 100/100 PASS |

## FODS G11-F Hardening: Malformed XML Guard

**Hardening slice:** Malformed/adversarial XML input resilience

### New Test File
`tests/net/fods/FodsG11fMalformedXmlGuardTests.cs` — 8 tests

| Test | Validates |
|------|-----------|
| Parser_NullPath_ReturnsErrorNotThrow | Null path → error result, no exception |
| Parser_EmptyPath_ReturnsError | Empty string path → error |
| Parser_NonExistentFile_ReturnsError | Missing file → error |
| Parser_EmptyFile_ReturnsError | 0-byte file → error |
| Parser_TruncatedXml_ReturnsError | Truncated XML → error |
| Parser_NonXmlContent_ReturnsError | Binary/non-XML → error |
| Parser_WrongRootElement_ReturnsErrorOrEmptyDocument | Wrong root → no data |
| Parser_FileSizeGuard_RejectsOversized | MaxFileSizeBytes=1 → error |

### FODS Test Results Post-Hardening

| Suite | Tests | Status |
|-------|-------|--------|
| FodsParserTests | (existing) | PASS |
| FodsJsonExporterTests | (existing) | PASS |
| FodsHtmlExporterTests | (existing) | PASS |
| FodsCsvExporterTests | (existing) | PASS |
| FodsMultiSheetHardeningTests (R24) | 10 | PASS |
| **FodsG11fMalformedXmlGuardTests (NEW)** | **8** | **PASS** |
| Other FODS tests | (existing) | PASS |
| **TOTAL** | **120** | **120/120 PASS** |

## FODT G11-F Hardening: Heading Detection and Malformed XML Guard

**Hardening slices:** Heading detection (ATX Markdown rendering) + malformed XML guard

### New Fixture
`tests/net/fodt/Fixtures/fodt-headings-and-list.fodt`
ODF 1.3 FODT with 4 headings (H1, H2, H3, H1) and 4 paragraphs.

### New Test File
`tests/net/fodt/FodtG11fHeadingAndGuardTests.cs` — 8 tests

| Test | Validates |
|------|-----------|
| MarkdownExporter_Headings_H1ProducesHashPrefix | H1 → `# Chapter One` |
| MarkdownExporter_Headings_H2ProducesTwoHashPrefix | H2 → `## Section 1.1` |
| MarkdownExporter_Headings_H3ProducesThreeHashPrefix | H3 → `### Subsection 1.1.1` |
| MarkdownExporter_Headings_MultipleH1BothPresent | Both H1 headings preserved |
| MarkdownExporter_Headings_ParagraphTextPreserved | Paragraph text intact |
| Document_Load_EmptyFile_ThrowsException | Empty file → throws |
| Document_Load_TruncatedXml_ThrowsException | Truncated XML → throws |
| Document_Load_FileSizeGuard_ThrowsException | MaxFileSizeBytes=1 → throws |

### FODT Test Results Post-Hardening

| Suite | Tests | Status |
|-------|-------|--------|
| FodtParserTests | (existing) | PASS |
| FodtMarkdownExporterTests | (existing) | PASS |
| FodtHtmlExporterTests | (existing) | PASS |
| FodtTxtExporterTests | (existing) | PASS |
| FodtUnicodeHardeningTests (R24) | 8 | PASS |
| **FodtG11fHeadingAndGuardTests (NEW)** | **8** | **PASS** |
| Other FODT tests | (existing) | PASS |
| **TOTAL** | **108** | **108/108 PASS** |

## Gate 11 Status (Unchanged)

| Field | FODS | FODT |
|-------|------|------|
| G11-E | g11e_hardening_pass | g11e_hardening_pass |
| G11-F | g11f_hardening_in_progress | g11f_hardening_in_progress |
| G11-G | NOT_STARTED | NOT_STARTED |
| commercial_product_ready | false | false |
| G11-G approval | Requires Babar Raza human approval | Same |

**Gate 5 — PASS**
**Lane E — G11-F Hardening: COMPLETE (+8 FODS, +8 FODT)**
