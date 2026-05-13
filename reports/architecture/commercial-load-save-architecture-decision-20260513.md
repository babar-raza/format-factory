# Architecture Decision: Commercial Load-Save Vertical Slice
# COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001
# Date: 2026-05-13

## Decision
FORMAT-LOCAL IMPLEMENTATION — no shared FormatFactory.Core in this sprint.

## Rationale
1. Reduces cross-lane conflicts — FODS and FODT lanes operate independently.
2. Keeps FODS/FODT source separate; allows later extraction of shared abstractions after real patterns emerge.
3. First vertical slice must be minimal and unblocked; shared core would require extra design and testing.
4. Aligns with DEC-033 Option B: .NET Commercial only, format-first layout.

## Source Layout
- FODS model: src/net/fods/Model/ (FodsSheet.cs, FodsRow.cs, FodsCell.cs)
- FODT model: src/net/fodt/Model/ (FodtBody.cs, FodtParagraph.cs)
- FODS document: src/net/fods/FodsDocument.cs
- FODS writer: src/net/fods/FodsWriter.cs
- FODT document: src/net/fodt/FodtDocument.cs
- FODT writer: src/net/fodt/FodtWriter.cs

## Namespace Conventions
- FODS: FormatFactory.Fods (existing namespace, preserved)
- FODT: FormatFactory.Fodt (existing namespace, preserved)

## Public API Surface

### FODS
```csharp
FodsDocument.Load(string path)        // Load FODS file into DOM
FodsDocument.Save(string path)        // Save DOM to FODS file
FodsDocument.Sheets                   // IReadOnlyList<FodsSheet>
FodsSheet.Name                        // get/set — table:name attribute
FodsSheet.Rows                        // IReadOnlyList<FodsRow>
FodsRow.Cells                         // IReadOnlyList<FodsCell>
FodsCell.Value                        // string? — text:p text content (read)
FodsCell.SetText(string value)        // update text:p text node in XML
```

### FODT
```csharp
FodtDocument.Load(string path)        // Load FODT file into DOM
FodtDocument.Save(string path)        // Save DOM to FODT file
FodtDocument.Body                     // FodtBody — office:body wrapper
FodtDocument.Paragraphs               // IReadOnlyList<FodtParagraph> (convenience)
FodtParagraph.Text                    // string — text content (read)
FodtParagraph.SetText(string value)  // update text:p text node in XML
```

## DOM-Backed Preservation Strategy
- Load XML into XDocument (System.Xml.Linq)
- Typed wrappers (FodsSheet, FodsRow, FodsCell, FodtParagraph) hold XElement references
- Unknown nodes preserved automatically by XDocument — wrapper only accesses known children
- Save writes XDocument as-is (with modifications from SetText/SetName calls)

## Security Posture (carried over from existing FodsParser/FodtParser)
- DtdProcessing.Prohibit
- XmlResolver = null
- File size guard: 50 MB default
- No unsafe blocks
- XML output uses XmlWriterSettings: Encoding=UTF-8, Indent=true

## Future Shared-Core Extraction Criteria
Extract shared core only when:
1. At least 3 format parsers share >50% of the same model patterns
2. Shared abstractions are confirmed by real implementations (not speculative)
3. Coordinator approves extraction in a new sprint
4. DEC-033 Option B remains in force

## Lane B Verdict
LANE_B_PASS_FORMAT_LOCAL
