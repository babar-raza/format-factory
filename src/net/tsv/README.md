# FormatFactory.Tsv

Commercial .NET library for reading and writing TSV (tab-separated values) files.

## Installation

```
dotnet add package FormatFactory.Tsv
```

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
