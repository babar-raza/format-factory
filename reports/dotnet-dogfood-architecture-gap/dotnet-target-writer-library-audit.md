# .NET Target Writer Library Audit
Sprint: FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001
Lane: B — Target Writer Library Existence Audit
Date: 2026-06-05

---

## Architecture Distinction

### Product-Local Exporter Stub (what FODS/FODT have)

A product-local exporter stub is a static class that lives inside the source format's own namespace
(`FormatFactory.Fods` or `FormatFactory.Fodt`) and contains its own inline serialization logic. It
does NOT call into any separate Format Factory writer library. The conversion logic — CSV field
escaping, HTML encoding, Markdown ATX prefix generation, plain-text joining — is written directly
inside the exporter class. There is no external Format Factory dependency for the target format.

Examples:
- `FodsCsvExporter.cs` — namespace `FormatFactory.Fods`; implements RFC 4180 escaping inline via
  `EscapeCsvField()`; no `target_ff_library` declaration present
- `FodsHtmlExporter.cs` — namespace `FormatFactory.Fods`; uses `System.Net.WebUtility.HtmlEncode`
  (BCL, not a FF library) directly; no `target_ff_library` declaration present
- `FodtMarkdownExporter.cs` — namespace `FormatFactory.Fodt`; generates ATX headings inline with
  `new string('#', level)`; no `target_ff_library` declaration present
- `FodtTxtExporter.cs` — namespace `FormatFactory.Fodt`; joins paragraph texts with
  `string.Join("\n", lines)`; no `target_ff_library` declaration present

### Standalone FF Writer Library (what Netpbm has — the IMPLEMENTED pattern)

A standalone FF writer library is a separate Format Factory product library for the TARGET format.
The exporter class invokes that library's writer to produce the output. This makes the export a
genuine "dogfood" path: Format Factory uses its own product to write the target format.

Example:
- `NetpbmExporter.cs` — carries the explicit declaration `target_ff_library: FormatFactory.Netpbm.NetpbmWriter`
  in its class-level XML doc comment (line 21). The exporter operates on `NetpbmImage` model objects
  (the FF product model) and returns converted `NetpbmImage` objects ready to be serialized by
  `NetpbmWriter` — the FF library for the target format. The dogfood loop is closed: FF reads via
  `NetpbmParser`, transforms via `NetpbmExporter`, and writes via `NetpbmWriter`.

### Why This Matters for Dogfood Status

Dogfood status `IMPLEMENTED` is valid only when the export path traverses the Format Factory library
for the target format (`target_ff_library` is declared and invoked). When serialization is inlined into
the source-format exporter, the export is functional but does NOT exercise any Format Factory
target-format library. There is no `FormatFactory.Csv`, `FormatFactory.Html`, `FormatFactory.Markdown`,
or `FormatFactory.Txt` library anywhere in `src/net/`, so FODS/FODT dogfood export status for these
four target formats cannot be claimed as IMPLEMENTED. The architecture gap must be closed first.

---

## Evidence Citations

### FodsCsvExporter.cs — src/net/fods/FodsCsvExporter.cs

File header (lines 1-9, verbatim):
```
// FormatFactory.Fods -- Commercial .NET FODS -> CSV Exporter (G11-E Prototype)
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: g11e_prototype_complete -- G11-G NOT approved
// Sprint: FORMAT-FACTORY-R22-FULL-THROTTLE-RELEASE-CANDIDATE-AND-GATE11-PROTOTYPE-TRAIN-001
//
// PROTOTYPE STATUS: design_complete_in_progress
// This is a G11-E conversion/export prototype only.
// commercial_product_ready: false
// Do NOT package or publish.
```

Namespace declaration (line 16): `namespace FormatFactory.Fods;`

Observation: No `target_ff_library` comment exists anywhere in this file. No reference to
`FormatFactory.Csv`, `CsvWriter`, or any external FF library. Serialization is fully inline
(`EscapeCsvField` method at line 260, `File.WriteAllText` at line 147).

### FodsHtmlExporter.cs — src/net/fods/FodsHtmlExporter.cs

File header (lines 1-8, verbatim):
```
// FormatFactory.Fods -- Commercial .NET FODS -> HTML Table Exporter (G11-E Expanded Prototype)
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: g11e_prototype_complete -- G11-G NOT approved
// Sprint: FORMAT-FACTORY-R23-MEGA-TRAIN-001
//
// PROTOTYPE STATUS: design_complete_in_progress
// commercial_product_ready: false
// Do NOT package or publish.
```

Namespace declaration (line 16): `namespace FormatFactory.Fods;`

Observation: No `target_ff_library` comment. No reference to `FormatFactory.Html` or `HtmlWriter`.
Serialization uses `System.Net.WebUtility.HtmlEncode` (BCL, not FF) and StringBuilder directly in
`FodsHtmlExporter.ExportToHtml()`.

### FodtMarkdownExporter.cs — src/net/fodt/FodtMarkdownExporter.cs

File header (lines 1-8, verbatim):
```
// FormatFactory.Fodt -- Commercial .NET FODT -> Markdown Exporter (G11-E Expanded Prototype)
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: g11e_prototype_complete -- G11-G NOT approved
// Sprint: FORMAT-FACTORY-R23-MEGA-TRAIN-001
//
// PROTOTYPE STATUS: design_complete_in_progress
// commercial_product_ready: false
// Do NOT package or publish.
```

Namespace declaration (line 15): `namespace FormatFactory.Fodt;`

Observation: No `target_ff_library` comment. No reference to `FormatFactory.Markdown` or
`MarkdownWriter`. Markdown serialization is inline (`new string('#', level)` at line 116,
`string.Join("\n", lines)` at line 127).

### FodtTxtExporter.cs — src/net/fodt/FodtTxtExporter.cs

File header (lines 1-9, verbatim):
```
// FormatFactory.Fodt -- Commercial .NET FODT -> TXT Exporter (G11-E Prototype)
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: g11e_prototype_complete -- G11-G NOT approved
// Sprint: FORMAT-FACTORY-R22-FULL-THROTTLE-RELEASE-CANDIDATE-AND-GATE11-PROTOTYPE-TRAIN-001
//
// PROTOTYPE STATUS: design_complete_in_progress
// This is a G11-E conversion/export prototype only.
// commercial_product_ready: false
// Do NOT package or publish.
```

Namespace declaration (line 16): `namespace FormatFactory.Fodt;`

Observation: No `target_ff_library` comment. No reference to `FormatFactory.Txt` or `TxtWriter`.
Serialization is inline (`string.Join("\n", lines)` at line 119, `File.WriteAllText` at line 125).

### NetpbmExporter.cs — src/net/netpbm/NetpbmExporter.cs (reference IMPLEMENTED pattern)

File header dogfood comment (lines 6-9, verbatim):
```
// Dogfooding strategy:
//   PBM -> PGM: Expand 1-bit bitmap to 8-bit grayscale using Format Factory Netpbm model
//   (Uses Format Factory's own NetpbmImage model -- no external library)
```

Verbatim `target_ff_library` declaration (line 21):
```
/// target_ff_library: FormatFactory.Netpbm.NetpbmWriter
```

Full class doc comment context (lines 14-22, verbatim):
```
/// <summary>
/// Cross-format export within the Netpbm family.
///
/// Dogfooding: all exports use Format Factory's own NetpbmImage model.
/// No external image libraries.
///
/// dogfood_status: IMPLEMENTED (PBM->PGM, PBM->PPM grayscale)
/// target_ff_library: FormatFactory.Netpbm.NetpbmWriter
/// </summary>
```

### Grep Search Results — All Target Format Strings in src/net/

| Search Pattern | Scope | Result |
|---|---|---|
| `FormatFactory\.Csv` | src/**/*.cs | No matches |
| `class CsvWriter` | src/**/*.cs | No matches |
| `FormatFactory\.Html` | src/**/*.cs | No matches |
| `class HtmlWriter` | src/**/*.cs | No matches |
| `FormatFactory\.Markdown` | src/**/*.cs | No matches |
| `class MarkdownWriter` | src/**/*.cs | No matches |
| `FormatFactory\.Txt` | src/**/*.cs | No matches |
| `class TxtWriter` | src/**/*.cs | No matches |
| `target_ff_library` | src/**/*.cs | 1 match: src/net/netpbm/NetpbmExporter.cs line 21 only |

---

## Audit Matrix

| Target Writer | Expected Package | Exists | Evidence | Product-Local Stub | Status | Blocker |
|---|---|---|---|---|---|---|
| format-factory-csv-dotnet | FormatFactory.Csv | NO | No grep matches in src/net/ | src/net/fods/FodsCsvExporter.cs | NOT_STARTED | ARCHITECTURE_GAP |
| format-factory-html-dotnet | FormatFactory.Html | NO | No grep matches in src/net/ | src/net/fods/FodsHtmlExporter.cs | NOT_STARTED | ARCHITECTURE_GAP |
| format-factory-markdown-dotnet | FormatFactory.Markdown | NO | No grep matches in src/net/ | src/net/fodt/FodtMarkdownExporter.cs | NOT_STARTED | ARCHITECTURE_GAP |
| format-factory-txt-dotnet | FormatFactory.Txt | NO | No grep matches in src/net/ | src/net/fodt/FodtTxtExporter.cs | NOT_STARTED | ARCHITECTURE_GAP |

---

## Local Verdict

ARCHITECTURE_GAP_CONFIRMED

No standalone Format Factory .NET writer libraries exist for CSV, HTML, Markdown, or TXT. All four
product-local exporter stubs (FodsCsvExporter, FodsHtmlExporter, FodtMarkdownExporter, FodtTxtExporter)
serialize their respective target formats inline, without invoking any separate FormatFactory.* target
library. This is architecturally distinct from the Netpbm dogfood pattern, where `NetpbmExporter`
carries the explicit declaration `target_ff_library: FormatFactory.Netpbm.NetpbmWriter` and operates
on the FF product model. Until FormatFactory.Csv, FormatFactory.Html, FormatFactory.Markdown, and
FormatFactory.Txt libraries are built and integrated, FODS and FODT dogfood export status for these
target formats cannot be claimed as IMPLEMENTED.
