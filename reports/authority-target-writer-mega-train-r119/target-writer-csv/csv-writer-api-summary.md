# CSV Writer API Summary
Library: FormatFactory.Csv
Sprint: FORMAT-FACTORY-AUTHORITY-LAYERS-AND-TARGET-WRITER-MEGA-TRAIN-R119-001

## Namespace
`FormatFactory.Csv`

## Public API

### `CsvWriter` (static class)

#### `WriteRows(IEnumerable<IEnumerable<string?>> rows) : string`
Serializes rows of string fields to a CSV string.
- Input: rows where each row is a sequence of nullable string fields
- Output: CSV content with LF line endings
- Encoding: UTF-8 (returned as string)
- Null fields treated as empty strings

#### `WriteRowsToFile(IEnumerable<IEnumerable<string?>> rows, string path) : void`
Serializes rows and writes to file.
- Creates parent directories if needed
- UTF-8, no BOM
- LF line endings (normalizes CRLF→LF)
- Throws `CsvWriterException` on I/O error

#### `EscapeField(string? value) : string`
Escapes a single CSV field per RFC 4180.
- null/empty → empty string (no quotes)
- Contains comma, double-quote, CR, or LF → wrap in double-quotes
- Embedded double-quotes → doubled ("")

### `CsvWriterException` (sealed class)
Thrown when output cannot be written.
- `CsvWriterException(string message)`
- `CsvWriterException(string message, Exception inner)`

## Behavior Specification
- RFC 4180 compatible quoting
- Deterministic output (same input → same output)
- No runtime dependencies beyond System.*
- Works on net10.0, compatible with standard .NET

## Reusability
This library is designed for reuse by any Format Factory .NET product.
Current consumers:
- `FormatFactory.Fods` (via ProjectReference) — FODS → CSV export

## Not Included (future work)
- Custom delimiter support
- BOM output option
- Streaming/large file optimizations
- Header row abstraction
