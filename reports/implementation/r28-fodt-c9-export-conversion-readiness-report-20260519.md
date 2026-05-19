# R28 FODT C9 Export/Conversion Readiness Report

**Date:** 2026-05-19
**Sprint:** R28 Lane J
**Format:** FODT (Flat OpenDocument Text)
**Gate 11 Status:** commercial_readiness_in_progress (G11-G NOT_STARTED)
**commercial_product_ready:** false

---

## Summary

C9 export/conversion readiness has been verified for FODT across all three exporters (TXT, Markdown, HTML). The full pipeline -- load, edit, save, reload, export -- produces correct output for all export formats, and the export operation does not mutate the in-memory document model.

## Exporters Tested

| Exporter | Source File | Format | C9 Tests Added |
|---|---|---|---|
| FodtTxtExporter | `src/net/fodt/FodtTxtExporter.cs` | Plain text (UTF-8, LF) | 5 |
| FodtMarkdownExporter | `src/net/fodt/FodtMarkdownExporter.cs` | Markdown (CommonMark ATX headings) | 4 |
| FodtHtmlExporter | `src/net/fodt/FodtHtmlExporter.cs` | HTML5 (semantic h1-h6, p) | 5 |

**Governance tests:** 2 (commercial_product_ready=false invariant; static class assertion)

**Total C9 tests added:** 16

## Test Results

```
Passed!  - Failed: 0, Passed: 140, Skipped: 0, Total: 140
```

Prior baseline: 124/124. New total: 140/140 (all pass).

## C9 Test Matrix

### TXT (5 tests)
- C9-TXT-01: Export after edit+save+reload contains edited paragraph text
- C9-TXT-02: Export after edit+save+reload preserves unedited paragraph ("Second paragraph.")
- C9-TXT-03: Export does not mutate the in-memory document model
- C9-TXT-04: Export paragraph count matches document paragraph count
- C9-TXT-05: Export preserves heading text ("A Heading") after edit pipeline

### Markdown (4 tests)
- C9-MD-01: Export after edit+save+reload contains edited paragraph
- C9-MD-02: Export after edit+save+reload preserves unedited paragraph
- C9-MD-03: Export does not mutate the in-memory document model
- C9-MD-04: Export preserves heading with ATX format ("# A Heading") after edit pipeline

### HTML (5 tests)
- C9-HTML-01: Export after edit+save+reload contains edited paragraph
- C9-HTML-02: Export after edit+save+reload preserves unedited paragraph
- C9-HTML-03: Export does not mutate the in-memory document model
- C9-HTML-04: Export output is valid HTML5 with correct structure
- C9-HTML-05: Heading appears in correct `<h1>` tag after edit pipeline

### Governance (2 tests)
- C9-GOV-01: commercial_product_ready = false invariant
- C9-GOV-02: All three exporters exist as static classes

## Capability Evidence Chain

| Capability | Status | Evidence |
|---|---|---|
| C4 (Load) | PASS | FodtParserTests, FodtDocumentRoundtripTests |
| C5 (Edit) | PASS | FodtDocumentEditTests, FodtEditSaveTests |
| C6 (Save) | PASS | FodtEditSaveTests, FodtDocumentRoundtripTests |
| C7 (Round-trip fidelity) | PASS | FodtC7C8RoundtripPreservationTests (9 tests) |
| C8 (Opaque node preservation) | PASS | FodtC7C8RoundtripPreservationTests (7 tests) |
| C9 (Export/conversion readiness) | PASS | FodtC9ExportConversionReadinessTests (16 tests) |

## Test File

`tests/net/fodt/FodtC9ExportConversionReadinessTests.cs`

## Constraints Observed

- G11-G status: NOT_STARTED (unchanged)
- commercial_product_ready: false (enforced by governance test)
- No AI files modified
- No gate self-approval
