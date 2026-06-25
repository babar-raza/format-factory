# FormatFactory.Ndjson

Commercial .NET library for reading and writing NDJSON (Newline-Delimited JSON) files.

## Installation

```
dotnet add package FormatFactory.Ndjson
```

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
