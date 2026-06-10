# FormatFactory.Csv — .NET Minimum Viable Writer Outline

## Namespace
FormatFactory.Csv

## Minimum API
```csharp
public static class CsvWriter {
    // Write rows as RFC 4180 CSV string
    public static string WriteRows(IEnumerable<IEnumerable<string?>> rows) { ... }
    // Write rows to file
    public static void WriteToFile(IEnumerable<IEnumerable<string?>> rows, string filePath) { ... }
    // Escape a single field (RFC 4180)
    public static string EscapeField(string? field) { ... }
}
```

## Extraction Path

The logic to build this library already exists in `src/net/fods/FodsCsvExporter.cs` (316 lines).
No new algorithms are required — this is primarily an extraction and namespace move:

- `EscapeCsvField(string? value)` (lines 260–274) → becomes `CsvWriter.EscapeField(string? field)`
  - Already RFC 4180 compliant: null/empty → empty string; commas/quotes/newlines → double-quoted; embedded quotes → doubled (`""`)
- Row serialization loop from `ExportSheetToCsvString(FodsSheet sheet)` (lines 218–235) → becomes `CsvWriter.WriteRows(IEnumerable<IEnumerable<string?>> rows)`
  - Loop: for each row, map cells to escaped fields, join with `,`, append `\n`
- File write path from `ExportSheetToCsv(FodsSheet, string, string)` (lines 101–156) → becomes `CsvWriter.WriteToFile(...)`
  - UTF-8 without BOM, normalize `\r\n` → `\n`, `File.WriteAllText` with `new UTF8Encoding(false)`
- After extraction: `FodsCsvExporter.cs` calls `CsvWriter.WriteRows()` and `CsvWriter.EscapeField()` instead of its own internal loop and `EscapeCsvField()`. The `FodsCsvExporter` becomes a thin FODS-to-rows adapter over `FormatFactory.Csv`.

## Extraction Boundary

`FodsCsvExporter` retains FODS-specific concerns:
- Loading `FodsDocument` from file
- Iterating `FodsSheet.Rows` and `FodsRow.Cells`
- Handling `IsCovered` (merged cells → null value)
- `SanitizeFileName()` for multi-sheet export
- `FodsCsvExportResult` / `FodsCsvExportException` result and exception types

`CsvWriter` is format-agnostic: it accepts any `IEnumerable<IEnumerable<string?>>` and knows nothing about FODS.

## Test Fixtures Required

| Fixture | Description | Assertion |
|---------|-------------|-----------|
| Round-trip | Header + data rows → `WriteRows()` → parse back | Values match exactly |
| RFC 4180 quoting — comma | Field containing `,` | Output field is double-quoted |
| RFC 4180 quoting — quote | Field containing `"` | Embedded quote doubled to `""` |
| RFC 4180 quoting — newline | Field containing `\n` or `\r` | Output field is double-quoted |
| Empty cell (null) | null input | Empty CSV field (no quotes) |
| Empty cell (empty string) | `""` input | Empty CSV field (no quotes) |
| Multi-row | Multiple rows | Correct LF-terminated lines |
| `WriteToFile` | Write to temp file | File content matches `WriteRows()` output |

## Package Strategy

- NuGet package ID: `format-factory-csv`
- Assembly: `FormatFactory.Csv.dll`
- Consumed by: `FormatFactory.Fods` (`FodsCsvExporter`) after refactor
- Gate 11 status: `g11_prototype` — follow same gate progression as other FF exporters
- No external NuGet dependencies required (BCL only: `System.IO`, `System.Text`)

## Implementation Complexity: 2/5 (LOW)

Logic already exists in `FodsCsvExporter.cs` — this is primarily an extraction and namespace move.
The core escaping (`EscapeCsvField`) and row serialization loop (`ExportSheetToCsvString`) are already correct and tested. Risk is low.

## Blocker It Resolves

Unblocks dogfood gap: `fods_to_csv_dotnet` ONLY.
Does NOT unblock `fods_to_html_dotnet` — that requires a separate `FormatFactory.Html` library.
