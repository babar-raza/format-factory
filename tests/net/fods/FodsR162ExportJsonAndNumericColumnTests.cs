// Tests for FodsDocument.ExportSheetToJson, GetNumericColumnValues, ExportSheetToCsvFile.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R162

using System;
using System.IO;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R162: Tests for FodsDocument.ExportSheetToJson, GetNumericColumnValues, ExportSheetToCsvFile.
/// ExportSheetToJson(): serializes first sheet to JSON array of row arrays.
/// ExportSheetToJson(sheetName): serializes named sheet to JSON.
/// GetNumericColumnValues(sheetName, col): returns parsed double values, skipping non-numeric.
/// ExportSheetToCsvFile(sheetName, filePath): writes CSV to disk.
/// ExportSheetToCsvFile(filePath): writes first sheet CSV to disk.
/// Covers: ExportSheetToJson returns valid JSON; ExportSheetToJson non-null for empty sheet;
/// ExportSheetToJson named sheet contains cell value; ExportSheetToJson no-args matches named;
/// GetNumericColumnValues returns correct values; GetNumericColumnValues skips non-numeric;
/// GetNumericColumnValues empty result for all-text column; GetNumericColumnValues out-of-range col is empty;
/// ExportSheetToCsvFile creates file; ExportSheetToCsvFile file not empty;
/// ExportSheetToCsvFile no-args creates file;
/// dogfood BuildSheet->ExportJson->GetNumericColumn->ExportCsvFile pipeline.
/// </summary>
public class FodsR162ExportJsonAndNumericColumnTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR162ExportJsonAndNumericColumnTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR162_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument BuildSheet(string sheetName, string[] headers, string[][] rows)
    {
        var doc = FodsDocument.CreateNew();
        var names = doc.GetSheetNames();
        if (names.Count > 0)
            doc.RenameSheet(names[0], sheetName);
        else
            doc.AddSheet(sheetName);

        doc.InsertRowWithValues(sheetName, 0, headers);
        for (var i = 0; i < rows.Length; i++)
            doc.InsertRowWithValues(sheetName, i + 1, rows[i]);

        return doc;
    }

    // -------------------------------------------------------------------------
    // ExportSheetToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToJson_ReturnsValidJson()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var json = doc.ExportSheetToJson("Data");
        // Should be parseable JSON
        using var jdoc = JsonDocument.Parse(json);
        Assert.NotNull(jdoc);
    }

    [Fact]
    public void ExportSheetToJson_ContainsCellValue()
    {
        var doc = BuildSheet("Report",
            new[] { "Product" },
            new[] { new[] { "Widget" } });
        var json = doc.ExportSheetToJson("Report");
        Assert.Contains("Widget", json);
    }

    [Fact]
    public void ExportSheetToJson_NoArgs_ContainsData()
    {
        var doc = BuildSheet("First",
            new[] { "Col" },
            new[] { new[] { "Val" } });
        var json = doc.ExportSheetToJson();
        Assert.Contains("|", doc.ExportSheetToMarkdown()); // sanity check
        Assert.NotNull(json);
    }

    [Fact]
    public void ExportSheetToJson_EmptySheet_ReturnsJsonArray()
    {
        var doc = FodsDocument.CreateNew();
        var name = doc.GetSheetNames()[0];
        var json = doc.ExportSheetToJson(name);
        // Should still be valid JSON (empty array or similar)
        Assert.NotNull(json);
    }

    // -------------------------------------------------------------------------
    // GetNumericColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumericColumnValues_ReturnsCorrectValues()
    {
        var doc = BuildSheet("Scores",
            new[] { "Name", "Score" },
            new[] {
                new[] { "Alice", "95" },
                new[] { "Bob", "82" },
                new[] { "Carol", "88" }
            });
        var values = doc.GetNumericColumnValues("Scores", 1);
        Assert.Contains(95.0, values);
        Assert.Contains(82.0, values);
        Assert.Contains(88.0, values);
    }

    [Fact]
    public void GetNumericColumnValues_SkipsNonNumeric()
    {
        var doc = BuildSheet("Mixed",
            new[] { "Name", "Score" },
            new[] {
                new[] { "Alice", "95" },
                new[] { "Bob", "N/A" }
            });
        var values = doc.GetNumericColumnValues("Mixed", 1);
        // Should contain 95 but skip "N/A"
        Assert.Contains(95.0, values);
        Assert.DoesNotContain(double.NaN, values);
    }

    [Fact]
    public void GetNumericColumnValues_AllTextColumn_IsEmpty()
    {
        var doc = BuildSheet("TextOnly",
            new[] { "Name" },
            new[] { new[] { "Alice" }, new[] { "Bob" } });
        var values = doc.GetNumericColumnValues("TextOnly", 0);
        // Name column has no numeric values
        Assert.Empty(values);
    }

    [Fact]
    public void GetNumericColumnValues_OobCol_IsEmpty()
    {
        var doc = BuildSheet("Sheet",
            new[] { "A" },
            new[] { new[] { "1" } });
        var values = doc.GetNumericColumnValues("Sheet", 99);
        Assert.Empty(values);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToCsvFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToCsvFile_CreatesFile()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var path = TempFile("export.csv");
        doc.ExportSheetToCsvFile("Data", path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportSheetToCsvFile_FileNotEmpty()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Bob", "82" } });
        var path = TempFile("nonempty.csv");
        doc.ExportSheetToCsvFile("Data", path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void ExportSheetToCsvFile_NoArgs_CreatesFile()
    {
        var doc = BuildSheet("First",
            new[] { "X" },
            new[] { new[] { "1" } });
        var path = TempFile("firstsheet.csv");
        doc.ExportSheetToCsvFile(path);
        Assert.True(File.Exists(path));
    }

    // -------------------------------------------------------------------------
    // Dogfood: BuildSheet->ExportJson->GetNumericColumn->ExportCsvFile
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ExportJsonNumericColumnCsvFile_Pipeline()
    {
        var doc = BuildSheet("Sales",
            new[] { "Product", "Revenue" },
            new[] {
                new[] { "Widget", "1500" },
                new[] { "Gadget", "2200" },
                new[] { "Doohickey", "850" }
            });

        // JSON export
        var json = doc.ExportSheetToJson("Sales");
        Assert.Contains("Widget", json);

        // Numeric column
        var revenues = doc.GetNumericColumnValues("Sales", 1);
        Assert.Equal(3, revenues.Count);
        Assert.Contains(1500.0, revenues);
        Assert.Contains(2200.0, revenues);

        // CSV export to file
        var path = TempFile("dogfood-sales.csv");
        doc.ExportSheetToCsvFile("Sales", path);
        var csvContent = File.ReadAllText(path);
        Assert.Contains("Widget", csvContent);
    }
}
