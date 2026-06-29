// FormatFactory.Tsv — .NET Consumer Roundtrip Proof
// Demonstrates behavioral query methods: IsEmpty, GetCellValue, GetColumnValues, Filter
//
// Run with: dotnet-script examples/dotnet/tsv/consumer_roundtrip.csx

#r "src/net/tsv/bin/Debug/net10.0/FormatFactory.Tsv.dll"

using FormatFactory.Tsv;
using System;
using System.IO;
using System.Linq;

var samplePath = "samples/by-format/tsv/minimal-2x2.tsv";
Console.WriteLine($"Source: {samplePath}");
Console.WriteLine();

// Step 1: Load
var doc = TsvDocument.LoadFile(samplePath, hasHeaders: true);
Console.WriteLine($"[LOAD] RowCount={doc.RowCount}, ColumnCount={doc.ColumnCount}, HasHeaders={doc.HasHeaders}");
if (doc.RowCount < 1) throw new Exception("Expected at least 1 data row");
if (!doc.HasHeaders) throw new Exception("Expected headers");

// Step 2: IsEmpty
var isEmpty = doc.IsEmpty;
Console.WriteLine($"[INSPECT] IsEmpty={isEmpty}");
if (isEmpty) throw new Exception("Expected non-empty document");

// Step 3: GetCellValue
var cell00 = doc.GetCellValue(0, 0);
var cell01 = doc.GetCellValue(0, 1);
Console.WriteLine($"[GET_CELL] [0,0]={cell00?.Trim()}, [0,1]={cell01?.Trim()}");
if (cell00?.Trim() != "Alice") throw new Exception($"Expected 'Alice', got '{cell00}'");
if (cell01?.Trim() != "30") throw new Exception($"Expected '30', got '{cell01}'");

// Step 4: GetColumnValues
var nameColValues = doc.GetColumnValues(0);
Console.WriteLine($"[COLUMN] Name column: [{string.Join(", ", nameColValues.Select(v => v?.Trim()))}]");
if (!nameColValues.Any(v => v?.Trim() == "Alice")) throw new Exception("Alice not found");
if (!nameColValues.Any(v => v?.Trim() == "Bob")) throw new Exception("Bob not found");

// Step 5: Filter — rows where age >= 30
var adults = doc.Filter(row => {
    var ageStr = row.Length > 1 ? row[1].Trim() : "";
    return int.TryParse(ageStr, out var age) && age >= 30;
});
Console.WriteLine($"[FILTER] Rows with Age>=30: {adults.RowCount}");
if (adults.RowCount < 1) throw new Exception("Expected at least 1 adult (Alice=30)");
if (adults.IsEmpty) throw new Exception("Filtered result should not be empty");

// Step 6: Empty TSV
var emptyDoc = TsvDocument.Load("Name\tValue\n", hasHeaders: true);
Console.WriteLine($"[EMPTY] IsEmpty={emptyDoc.IsEmpty}, RowCount={emptyDoc.RowCount}");
if (!emptyDoc.IsEmpty) throw new Exception("Expected empty document");

Console.WriteLine();
Console.WriteLine("CONSUMER_PROOF: PASS -- load -> IsEmpty -> GetCellValue -> GetColumnValues -> Filter");
