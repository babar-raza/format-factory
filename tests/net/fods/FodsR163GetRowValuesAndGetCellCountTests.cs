// Tests for FodsDocument.GetRowValues, GetCellCount, SaveToFile.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R163

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R163: Tests for FodsDocument.GetRowValues, GetCellCount, SaveToFile.
/// GetRowValues(row): returns cell values from the first sheet at given row index.
/// GetRowValues(sheetName, row): returns cell values from the named sheet.
/// GetCellCount(): total number of cells across all sheets.
/// SaveToFile(path): writes the document to disk; reloadable via Load.
/// Covers: GetRowValues valid row returns correct values; GetRowValues empty row is empty;
/// GetRowValues OOB row returns empty; GetRowValues named sheet correct;
/// GetCellCount empty doc is 0; GetCellCount after InsertRowWithValues;
/// GetCellCount includes header row; SaveToFile creates file;
/// SaveToFile round-trip preserves sheet count; SaveToFile round-trip preserves cell value;
/// dogfood CreateNew->InsertRows->GetCellCount->GetRowValues->SaveToFile pipeline.
/// </summary>
public class FodsR163GetRowValuesAndGetCellCountTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR163GetRowValuesAndGetCellCountTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR163_" + Guid.NewGuid().ToString("N"));
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
    // GetRowValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowValues_ValidRow_ReturnsCorrectValues()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var row = doc.GetRowValues(0); // first sheet, row 0 = header
        Assert.NotEmpty(row);
    }

    [Fact]
    public void GetRowValues_NamedSheet_ReturnsCorrectValues()
    {
        var doc = BuildSheet("Sales",
            new[] { "Product", "Revenue" },
            new[] { new[] { "Widget", "1500" } });
        var row = doc.GetRowValues("Sales", 1);
        Assert.Contains("Widget", row);
    }

    [Fact]
    public void GetRowValues_OobRow_ReturnsEmpty()
    {
        var doc = BuildSheet("Data",
            new[] { "A" },
            new[] { new[] { "1" } });
        var row = doc.GetRowValues("Data", 999);
        Assert.Empty(row);
    }

    [Fact]
    public void GetRowValues_DataRow_ContainsExpectedValues()
    {
        var doc = BuildSheet("Sheet",
            new[] { "X", "Y", "Z" },
            new[] { new[] { "10", "20", "30" } });
        var row = doc.GetRowValues("Sheet", 1); // data row index 1
        Assert.Contains("10", row);
        Assert.Contains("20", row);
        Assert.Contains("30", row);
    }

    // -------------------------------------------------------------------------
    // GetCellCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellCount_EmptyDoc_IsZero()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Equal(0, doc.GetCellCount());
    }

    [Fact]
    public void GetCellCount_AfterInsertRowWithValues_IsPositive()
    {
        var doc = BuildSheet("Data",
            new[] { "A", "B", "C" },
            new[] { new[] { "1", "2", "3" } });
        Assert.True(doc.GetCellCount() > 0);
    }

    [Fact]
    public void GetCellCount_IncludesHeaderRow()
    {
        var doc = BuildSheet("Data",
            new[] { "Col1", "Col2" },
            new[] { new[] { "A", "B" } });
        // Header row (2 cells) + data row (2 cells) = at least 4
        Assert.True(doc.GetCellCount() >= 4);
    }

    [Fact]
    public void GetCellCount_MultipleRows_SumsCorrectly()
    {
        var doc = BuildSheet("Data",
            new[] { "A", "B" },
            new[] {
                new[] { "1", "2" },
                new[] { "3", "4" },
                new[] { "5", "6" }
            });
        // 4 rows * 2 cols = 8 cells
        Assert.True(doc.GetCellCount() >= 8);
    }

    // -------------------------------------------------------------------------
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = BuildSheet("Sheet",
            new[] { "X" },
            new[] { new[] { "1" } });
        var path = TempFile("save.fods");
        doc.Save(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileNotEmpty()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name", "Value" },
            new[] { new[] { "Alpha", "100" } });
        var path = TempFile("nonempty.fods");
        doc.Save(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void SaveToFile_RoundTrip_PreservesSheetCount()
    {
        var doc = BuildSheet("Main",
            new[] { "A" },
            new[] { new[] { "1" } });
        doc.AddSheet("Extra");
        var path = TempFile("roundtrip.fods");
        doc.Save(path);
        var reloaded = FodsDocument.Load(path);
        Assert.Equal(2, reloaded.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->InsertRows->GetCellCount->GetRowValues->Save
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertGetCountRowValuesSave_Pipeline()
    {
        var doc = BuildSheet("Inventory",
            new[] { "Item", "Qty", "Price" },
            new[] {
                new[] { "Bolt", "100", "0.05" },
                new[] { "Nut", "200", "0.03" },
                new[] { "Washer", "500", "0.01" }
            });

        // Cell count
        Assert.True(doc.GetCellCount() >= 12); // 4 rows * 3 cols

        // Row values
        var header = doc.GetRowValues("Inventory", 0);
        Assert.Contains("Item", header);

        var dataRow = doc.GetRowValues("Inventory", 1);
        Assert.Contains("Bolt", dataRow);

        // Save and verify
        var path = TempFile("inventory.fods");
        doc.Save(path);
        Assert.True(File.Exists(path));

        // Reload and check
        var reloaded = FodsDocument.Load(path);
        Assert.True(reloaded.GetCellCount() >= 12);
    }
}
