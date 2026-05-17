---
artifact_id: fods-gate11-conversion-export-technical-design
artifact_type: acquisition-pack
path: acquisition-packs/fods/gate11-conversion-export-technical-design.md
format_id: fods
gate: "G11-E"
sprint: FORMAT-FACTORY-R21-FOSS-RELEASE-READINESS-AND-GATE11-COMMERCIAL-PREEXECUTION-TRAIN-001
date: "2026-05-17"
status: design_complete_not_implemented
visibility: internal
---

# FODS Gate 11 G11-E — Conversion and Export Technical Design

## Status

**G11-E: design_complete_not_implemented**

This document is design only. No .NET source has been written or modified.
No `src/net/` mutation authorized by this sprint or this document.
G11-E implementation requires a separate explicit authorization prompt.

## Current Capability Baseline

Capability: C4-C6 (load/parse/save/round-trip for .fods files)
Source: `src/net/fods/`
Tests: 42/42 PASS

## C7 Target: Format Conversion/Export

C7 = format conversion capability.
For FODS, the primary C7 targets are:

### Option 1: FODS → CSV (Simplest Path)

- **Approach:** Extract cell values from the loaded FODS model and serialize as comma-separated values.
- **Difficulty:** Low — cell model is already available from C4 extraction.
- **Value:** CSV is the universal spreadsheet interchange format.
- **Output:** `document.ExportToCsv(outputPath)` method.
- **No external library required.**

### Option 2: FODS → XLSX (OOXML)

- **Approach:** Map ODF spreadsheet model (Spreadsheet/Table/Row/Cell) to OOXML structure (Workbook/Worksheet/Row/Cell).
- **Difficulty:** Medium — requires understanding of OOXML Open Packaging Convention.
- **Library option:** Use `DocumentFormat.OpenXml` (NuGet, MIT license). No commercial library needed.
- **Value:** XLSX is the dominant spreadsheet format.
- **Output:** `document.ExportToXlsx(outputPath)` method.

### Option 3: FODS → PDF (Print-Quality)

- **Approach:** Either embed a PDF generation library (.NET PdfSharpCore, MIT) or invoke LibreOffice headless.
- **Difficulty:** High — requires layout engine for grid rendering.
- **Not recommended for alpha milestone.**

## Recommended C7 Implementation Order

1. **CSV export** — implement first (C4 model → CSV serialization, minimal code)
2. **XLSX export** — implement second (requires DocumentFormat.OpenXml dependency)
3. **PDF** — deferred to C8+

## Design API

```csharp
// Proposed (C7):
public class FodsDocument {
    // ... existing Load/Save/Edit ...
    public void ExportToCsv(string outputPath, int sheetIndex = 0);
    public void ExportToXlsx(string outputPath);  // requires OpenXml
}
```

## Dependencies for C7

- CSV: no new dependency
- XLSX: `DocumentFormat.OpenXml` (MIT, NuGet) — must be evaluated for commercial compatibility

## What Is NOT Authorized by This Design

- No src/net/ code written in this sprint
- No NuGet package created
- No commercial_product_ready=true
- Implementation requires explicit G11-E execution prompt
