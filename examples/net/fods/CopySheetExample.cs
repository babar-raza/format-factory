// Example: Copy a sheet in a FODS spreadsheet, edit the copy, and save
// Requires: FormatFactory.Fods NuGet package (commercial .NET track)
//
// Usage:
//   var doc = FodsDocument.Load("spreadsheet.fods");
//   var copy = doc.CopySheet("Sheet1", "Sheet1_Backup");
//   FodsDocument.SetCellValue(copy, 0, 0, "Modified");
//   doc.Save("output.fods");

using System;
using FormatFactory.Fods;

// Load a FODS spreadsheet
var doc = FodsDocument.Load("samples/by-format/fods/minimal-spreadsheet.fods");

// List existing sheets
Console.WriteLine("Sheets before copy:");
foreach (var name in doc.GetSheetNames())
    Console.WriteLine($"  - {name}");

// Copy the first sheet
var sourceName = doc.GetSheetNames()[0];
var copy = doc.CopySheet(sourceName, "Backup");
Console.WriteLine($"\nCopied '{sourceName}' → 'Backup'");

// Access by index
var sheet0 = doc.GetSheetByIndex(0);
Console.WriteLine($"Sheet at index 0: {sheet0?.Name}");

// Edit the copy independently
FodsDocument.SetCellValue(copy, 0, 0, "Edited in backup");

// Verify original is unchanged
var originalSheet = doc.GetSheetByName(sourceName)!;
var originalVal = FodsDocument.GetCellValue(originalSheet, 0, 0);
Console.WriteLine($"Original cell (0,0): {originalVal}");

// Save
doc.Save("output-with-backup.fods");
Console.WriteLine("\nSaved to output-with-backup.fods");
Console.WriteLine($"Total sheets: {doc.SheetCount}");
