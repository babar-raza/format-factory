// FormatFactory.Csv — .NET Consumer Roundtrip Proof
// Demonstrates behavioral query methods: IsEmpty, GetCellValue, Filter, HasColumn, GetColumn
//
// Run with: dotnet-script examples/dotnet/csv/consumer_roundtrip.csx
// Or compile via project referencing FormatFactory.Csv

// This script is a specification-by-example for CsvDocument behavioral methods.
// All assertions verify real semantic results from sample data.

#r "src/net/csv/bin/Debug/net10.0/FormatFactory.Csv.dll"

using FormatFactory.Csv;
using System;
using System.IO;
using System.Linq;

var samplePath = Path.Combine(AppContext.BaseDirectory, "../../../samples/by-format/csv/minimal-2x2.csv");
if (!File.Exists(samplePath))
    samplePath = "samples/by-format/csv/minimal-2x2.csv";

Console.WriteLine($"Source: {samplePath}");
Console.WriteLine();

// Step 1: Load
var doc = CsvDocument.LoadFile(samplePath, hasHeaders: true);
Console.WriteLine($"[LOAD] RowCount={doc.RowCount}, ColumnCount={doc.ColumnCount}, HasHeaders={doc.HasHeaders}");
if (doc.RowCount < 1) throw new Exception("Expected at least 1 data row");
if (!doc.HasHeaders) throw new Exception("Expected headers");

// Step 2: IsEmpty
var isEmpty = doc.IsEmpty;
Console.WriteLine($"[INSPECT] IsEmpty={isEmpty}");
if (isEmpty) throw new Exception("Expected non-empty document");

// Step 3: HasColumn
var hasName = doc.HasColumn("Name");
var hasAge = doc.HasColumn("Age");
var hasMissing = doc.HasColumn("Salary");
Console.WriteLine($"[INSPECT] HasColumn(Name)={hasName}, HasColumn(Age)={hasAge}, HasColumn(Salary)={hasMissing}");
if (!hasName || !hasAge) throw new Exception("Expected Name and Age columns");
if (hasMissing) throw new Exception("Did not expect Salary column");

// Step 4: GetCellValue
var cell00 = doc.GetCellValue(0, 0);  // First row, first col
var cell01 = doc.GetCellValue(0, 1);  // First row, second col
Console.WriteLine($"[GET_CELL] [0,0]={cell00!.Trim()}, [0,1]={cell01!.Trim()}");
if (cell00!.Trim() != "Alice") throw new Exception($"Expected 'Alice', got '{cell00}'");
if (cell01!.Trim() != "30") throw new Exception($"Expected '30', got '{cell01}'");

// Step 5: GetColumn by name
var nameCol = doc.GetColumn("Name");
Console.WriteLine($"[GET_COL] Name column: [{string.Join(", ", nameCol.Select(v => v.Trim()))}]");
if (!nameCol.Any(v => v.Trim() == "Alice")) throw new Exception("Alice not found in Name column");
if (!nameCol.Any(v => v.Trim() == "Bob")) throw new Exception("Bob not found in Name column");

// Step 6: Filter
var adults = doc.Filter(row => {
    var ageStr = row.Length > 1 ? row[1].Trim() : "";
    return int.TryParse(ageStr, out var age) && age >= 30;
});
Console.WriteLine($"[FILTER] Rows with Age>=30: {adults.RowCount}");
if (adults.RowCount < 1) throw new Exception("Expected at least 1 adult row (Alice=30)");
if (adults.IsEmpty) throw new Exception("Filtered result should not be empty");

// Step 7: Empty CSV
var emptyDoc = CsvDocument.Load("Name,Value\n", hasHeaders: true);
Console.WriteLine($"[EMPTY] IsEmpty={emptyDoc.IsEmpty}, RowCount={emptyDoc.RowCount}");
if (!emptyDoc.IsEmpty) throw new Exception("Expected empty document");

Console.WriteLine();
Console.WriteLine("CONSUMER_PROOF: PASS -- load -> IsEmpty -> HasColumn -> GetCellValue -> GetColumn -> Filter");
