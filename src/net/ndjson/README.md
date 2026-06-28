# FormatFactory.Ndjson

Commercial .NET library for reading and writing NDJSON (Newline-Delimited JSON) files.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-06-28T08:14:30+00:00 source=package-metadata -->
```bash
dotnet add package FormatFactory.Ndjson
```
<!-- END:README-INSTALLATION -->

## Quick Start

```csharp
using FormatFactory.Ndjson;

// Load an NDJSON file
var doc = NdjsonDocument.LoadFile("records.ndjson");
Console.WriteLine($"Record count: {doc.RecordCount}");

// Load from content string
var doc2 = NdjsonDocument.LoadFromContent("{\"id\":1}\n{\"id\":2}");

// Query all keys
var keys = doc.GetAllKeys();
bool uniform = doc.IsUniformSchema();
```

## Features

- Parse NDJSON files (one JSON object per line)
- Query and filter records
- Uniform schema detection
- Field value extraction

## License

Commercial — Format Factory product. See root LICENSE for terms.

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-06-28T08:14:30+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Newline Delimited JSON |
| Track | dotnet |
| Package | FormatFactory.Ndjson |
| Version | 0.1.0-mwp |
| License | unknown |
| Python | unknown |
| .NET | net10.0 |
| Spec | Informal (ndjson.org) v1 |
| QName coverage | 2/2 implemented |
| Source files | 7 |
| Test files | 180 |
<!-- END:README-PACKAGE_INFO -->
