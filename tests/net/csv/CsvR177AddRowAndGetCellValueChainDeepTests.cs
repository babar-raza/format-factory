// Tests for CsvDocument.AddRow, GetCellValue, SetCellValue chain deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R177

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R177: Tests for CsvDocument.AddRow, GetCellValue, SetCellValue chain deeper.
/// AddRow(values): appends a new row to the document.
/// GetCellValue(row, colName): returns the cell value at the given row by column name.
/// GetCellValue(row, colIndex): returns the cell value at the given row and column index.
/// SetCellValue(row, colName, value): sets the cell value at the given row and column name.
/// Covers: AddRow increments RowCount; AddRow value accessible via GetCellValue;
/// AddRow multiple rows; GetCellValue by name correct; GetCellValue by index correct;
/// GetCellValue last row correct; SetCellValue changes value; SetCellValue by name correct;
/// SetCellValue GetCellValue reflects change; SetCellValue multiple times LastWins;
/// AddRow then SetCellValue on new row;
/// dogfood CreateEmpty->AddRows->GetCellValue->SetCellValue->SaveLoad->Verify pipeline.
/// </summary>
public class CsvR177AddRowAndGetCellValueChainDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR177AddRowAndGetCellValueChainDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR177_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // AddRow
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_IncrementsRowCount()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "Name", "Score" });
        var before = doc.RowCount;
        doc.AddRow(new[] { "Alice", "95" });
        Assert.Equal(before + 1, doc.RowCount);
    }

    [Fact]
    public void AddRow_ValueAccessibleViaGetCellValue()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "Name", "Score" });
        doc.AddRow(new[] { "Alice", "95" });
        Assert.Equal("Alice", doc.GetCellValue(0, "Name"));
    }

    [Fact]
    public void AddRow_MultipleRows_CountCorrect()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "A", "B" });
        doc.AddRow(new[] { "1", "2" });
        doc.AddRow(new[] { "3", "4" });
        doc.AddRow(new[] { "5", "6" });
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void AddRow_LastRow_Accessible()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "X", "Y" });
        doc.AddRow(new[] { "first", "row" });
        doc.AddRow(new[] { "last", "entry" });
        Assert.Equal("last", doc.GetCellValue(1, "X"));
    }

    // -------------------------------------------------------------------------
    // GetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_ByName_Correct()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "Name", "City", "Age" });
        doc.AddRow(new[] { "Bob", "London", "30" });
        Assert.Equal("London", doc.GetCellValue(0, "City"));
    }

    [Fact]
    public void GetCellValue_ByIndex_Correct()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "Name", "City", "Age" });
        doc.AddRow(new[] { "Bob", "London", "30" });
        Assert.Equal("30", doc.GetCellValue(0, 2));
    }

    [Fact]
    public void GetCellValue_FirstColumn_Correct()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "ID", "Value" });
        doc.AddRow(new[] { "001", "Alpha" });
        Assert.Equal("001", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void GetCellValue_LastColumn_Correct()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "A", "B", "C" });
        doc.AddRow(new[] { "x", "y", "z" });
        Assert.Equal("z", doc.GetCellValue(0, "C"));
    }

    // -------------------------------------------------------------------------
    // SetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellValue_ChangesValue()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "Name", "Score" });
        doc.AddRow(new[] { "Alice", "90" });
        doc.SetCellValue(0, "Score", "95");
        Assert.Equal("95", doc.GetCellValue(0, "Score"));
    }

    [Fact]
    public void SetCellValue_GetCellValue_ReflectsChange()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "Status" });
        doc.AddRow(new[] { "pending" });
        doc.SetCellValue(0, "Status", "approved");
        Assert.Equal("approved", doc.GetCellValue(0, "Status"));
    }

    [Fact]
    public void SetCellValue_MultipleTimes_LastWins()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "Val" });
        doc.AddRow(new[] { "original" });
        doc.SetCellValue(0, "Val", "first");
        doc.SetCellValue(0, "Val", "second");
        doc.SetCellValue(0, "Val", "final");
        Assert.Equal("final", doc.GetCellValue(0, "Val"));
    }

    [Fact]
    public void SetCellValue_DoesNotChangeRowCount()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "Name" });
        doc.AddRow(new[] { "Alice" });
        doc.AddRow(new[] { "Bob" });
        var before = doc.RowCount;
        doc.SetCellValue(0, "Name", "Alicia");
        Assert.Equal(before, doc.RowCount);
    }

    [Fact]
    public void SetCellValue_ByIndex_ChangesValue()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "A", "B", "C" });
        doc.AddRow(new[] { "1", "2", "3" });
        doc.SetCellValue(0, 1, "updated");
        Assert.Equal("updated", doc.GetCellValue(0, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmpty_AddRows_GetCellValue_SetCellValue_SaveLoad_Verify_Pipeline()
    {
        // CreateEmpty
        var doc = CsvDocument.CreateEmpty(new[] { "Product", "Category", "Price", "Stock" });
        Assert.Equal(0, doc.RowCount);

        // AddRows
        doc.AddRow(new[] { "Widget", "Hardware", "9.99", "100" });
        doc.AddRow(new[] { "Gadget", "Electronics", "24.99", "50" });
        doc.AddRow(new[] { "Gizmo", "Hardware", "14.99", "75" });
        Assert.Equal(3, doc.RowCount);

        // GetCellValue checks
        Assert.Equal("Widget", doc.GetCellValue(0, "Product"));
        Assert.Equal("Electronics", doc.GetCellValue(1, "Category"));
        Assert.Equal("14.99", doc.GetCellValue(2, "Price"));
        Assert.Equal("75", doc.GetCellValue(2, 3));

        // SetCellValue mutations
        doc.SetCellValue(0, "Stock", "120");
        Assert.Equal("120", doc.GetCellValue(0, "Stock"));

        doc.SetCellValue(1, "Price", "22.99");
        Assert.Equal("22.99", doc.GetCellValue(1, "Price"));

        // RowCount unchanged
        Assert.Equal(3, doc.RowCount);

        // AddRow after SetCellValue
        doc.AddRow(new[] { "Thingamajig", "Hardware", "7.50", "200" });
        Assert.Equal(4, doc.RowCount);
        Assert.Equal("Thingamajig", doc.GetCellValue(3, "Product"));

        // SaveToFile and reload
        var path = TempFile("products.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(4, loaded.RowCount);
        Assert.Equal("Widget", loaded.GetCellValue(0, "Product"));
        Assert.Equal("120", loaded.GetCellValue(0, "Stock"));
    }
}
