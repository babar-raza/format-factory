# FormatFactory.Csv

Commercial .NET library for reading and writing CSV (comma-separated values) files.

## Installation

```
dotnet add package FormatFactory.Csv
```

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
