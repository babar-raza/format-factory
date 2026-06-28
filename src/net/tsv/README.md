# FormatFactory.Tsv

Commercial .NET library for reading and writing TSV (tab-separated values) files.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-06-28T08:14:30+00:00 source=package-metadata -->
```bash
dotnet add package FormatFactory.Tsv
```
<!-- END:README-INSTALLATION -->

## Quick Start

```csharp
using FormatFactory.Tsv;

// Load a TSV file
var doc = TsvDocument.Load("data.tsv");
Console.WriteLine($"Rows: {doc.RowCount}, Columns: {doc.ColumnCount}");

// Query
bool hasCol = doc.HasColumn("Name");
string? value = doc.GetCellValue(0, 0);
var filtered = doc.Filter(row => row["Status"] == "active");
```

## Features

- Parse TSV files with tab delimiter
- Query rows, columns, and cells
- Filter rows by predicate
- Header-aware access

## License

Commercial — Format Factory product. See root LICENSE for terms.

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-06-28T08:14:30+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Tab-Separated Values (TSV) |
| Track | dotnet |
| Package | FormatFactory.Tsv |
| Version | 0.1.0-mwp |
| License | unknown |
| Python | unknown |
| .NET | net10.0 |
| Spec | IANA IANA registration (1993) |
| QName coverage | 3/3 implemented |
| Source files | 6 |
| Test files | 173 |
<!-- END:README-PACKAGE_INFO -->
