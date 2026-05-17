---
artifact_id: fodt-gate11-conversion-export-technical-design
artifact_type: acquisition-pack
path: acquisition-packs/fodt/gate11-conversion-export-technical-design.md
format_id: fodt
gate: "G11-E"
sprint: FORMAT-FACTORY-R21-FOSS-RELEASE-READINESS-AND-GATE11-COMMERCIAL-PREEXECUTION-TRAIN-001
date: "2026-05-17"
status: design_complete_not_implemented
visibility: internal
---

# FODT Gate 11 G11-E — Conversion and Export Technical Design

## Status

**G11-E: design_complete_not_implemented**

This document is design only. No .NET source has been written or modified.
No `src/net/` mutation. G11-E implementation requires a separate explicit authorization prompt.

## Current Capability Baseline

Capability: C4-C6 (load/parse/save/round-trip for .fodt files)
Source: `src/net/fodt/`
Tests: 43/43 PASS

## C7 Target: Format Conversion/Export

### Option 1: FODT → TXT (Plain Text, Simplest)

- **Approach:** Extract paragraph text from section/paragraph model (C4 already does this).
- **Difficulty:** Very low — paragraph text already available.
- **Value:** Plain text extraction covers common use case.
- **Output:** `document.ExportToText(outputPath)` method.

### Option 2: FODT → DOCX (OOXML Word Document)

- **Approach:** Map ODF text model (Document/Section/Paragraph/Span) to OOXML (Document/Body/Paragraph/Run).
- **Difficulty:** Medium — ODF→OOXML text mapping is established (LibreOffice does this).
- **Library option:** `DocumentFormat.OpenXml` (NuGet, MIT). Adds a dependency.
- **Value:** DOCX is the dominant word processing format.
- **Output:** `document.ExportToDocx(outputPath)` method.

### Option 3: FODT → HTML (Web-Friendly)

- **Approach:** Emit styled HTML from paragraph/span model. No external library needed.
- **Difficulty:** Low-medium — requires CSS style mapping for text properties.
- **Value:** HTML is universally viewable without installed software.
- **Output:** `document.ExportToHtml(outputPath)` method.

### Option 4: FODT → PDF

- **Difficulty:** High. Deferred to C8+.

## Recommended C7 Implementation Order

1. **TXT export** — implement first (direct from C4 extraction)
2. **HTML export** — implement second (no new dependencies)
3. **DOCX export** — implement third (OpenXml dependency, high value)
4. **PDF** — deferred

## Design API

```csharp
// Proposed (C7):
public class FodtDocument {
    // ... existing Load/Save/Edit ...
    public void ExportToText(string outputPath);
    public void ExportToHtml(string outputPath);
    public void ExportToDocx(string outputPath);  // requires OpenXml
}
```

## Dependencies for C7

- TXT/HTML: no new dependency
- DOCX: `DocumentFormat.OpenXml` (MIT, NuGet)

## What Is NOT Authorized by This Design

- No src/net/ code written in this sprint
- No NuGet package created
- No commercial_product_ready=true
- Implementation requires explicit G11-E execution prompt
