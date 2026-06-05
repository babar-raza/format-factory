// FODS CSV Export Example — FormatFactory.Fods
// Demonstrates: Load a FODS spreadsheet, edit cells, export a sheet as RFC 4180 CSV.

#r "../../../src/net/fods/bin/Debug/net10.0/FormatFactory.Fods.dll"
using FormatFactory.Fods;

// 1. Load a minimal FODS spreadsheet
var samplesDir = Path.GetFullPath(Path.Combine(
    AppContext.BaseDirectory, "../../../samples/by-format/fods"));
var doc = FodsDocument.Load(Path.Combine(samplesDir, "minimal-spreadsheet.fods"));

// 2. Get the first sheet name and clear it
var sheet = doc.GetSheetNames()[0];
doc.ClearSheet(sheet);

// 3. Insert header + data rows
doc.InsertRowWithValues(sheet, 0, new[] { "Name", "Age", "City" });
doc.InsertRowWithValues(sheet, 1, new[] { "Alice", "30", "New York" });
doc.InsertRowWithValues(sheet, 2, new[] { "Bob", "25", "London" });
doc.InsertRowWithValues(sheet, 3, new[] { "Charlie", "35", "Tokyo" });

// 4. Export to CSV string
var csv = doc.ExportSheetToCsv(sheet);
Console.WriteLine("--- CSV Output ---");
Console.WriteLine(csv);

// 5. Values with commas are automatically quoted (RFC 4180)
doc.SetCellValue(0, 3, "has,comma");
var csvQuoted = doc.ExportSheetToCsv(sheet);
Console.WriteLine("--- With quoted value ---");
Console.WriteLine(csvQuoted);
