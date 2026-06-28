# FormatFactory.Csv

Commercial .NET library for reading and writing CSV (comma-separated values) files.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-06-28T08:14:28+00:00 source=package-metadata -->
```bash
dotnet add package FormatFactory.Csv
```
<!-- END:README-INSTALLATION -->

## Quick Start

```csharp
using FormatFactory.Csv;

// Load a CSV file
var doc = CsvDocument.Load("data.csv");
Console.WriteLine($"Rows: {doc.RowCount}, Columns: {doc.ColumnCount}");

// Query
bool hasCol = doc.HasColumn("Name");
string? value = doc.GetCellValue(0, 0);
```

## Features

- Parse CSV files with automatic delimiter detection
- Query rows, columns, and cells
- Filter rows by predicate
- Robust header handling

## License

Commercial — Format Factory product. See root LICENSE for terms.

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-06-28T08:14:28+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Comma-Separated Values (CSV) |
| Track | dotnet |
| Package | FormatFactory.Csv |
| Version | 0.1.0-mwp |
| License | unknown |
| Python | unknown |
| .NET | net10.0 |
| Spec | IETF (RFC 4180) RFC 4180 (2005) |
| QName coverage | 3/3 implemented |
| Source files | 4 |
| Test files | 173 |
<!-- END:README-PACKAGE_INFO -->
