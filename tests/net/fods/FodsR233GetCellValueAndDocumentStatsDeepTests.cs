// Tests for FodsDocument.GetCellValue, GetDocumentStats, GetSheetCount deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R233

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R233: Tests for FodsDocument.GetCellValue, GetDocumentStats, GetSheetCount deeper coverage.
/// GetCellValue(row, col): returns the cell value at the given position.
/// GetDocumentStats(): returns stats like RowCount, ColumnCount, SheetCount.
/// GetSheetCount(): returns the number of sheets in the document.
/// Covers: GetCellValue returns correct value; GetCellValue after SetCellValue reflects;
/// GetCellValue first row first col; GetCellValue last row; GetCellValue after AddRow;
/// GetCellValue string value correct; GetCellValue numeric value correct;
/// GetDocumentStats non-null; GetDocumentStats RowCount equals GetRowCount;
/// GetDocumentStats ColumnCount positive; GetDocumentStats SheetCount positive;
/// GetDocumentStats after AddRow increases RowCount; GetDocumentStats after AddSheet increases;
/// GetSheetCount positive; GetSheetCount increases after AddSheet; GetSheetCount matches stats;
/// dogfood CreateDoc→SetCellValues→GetCellValue×6→GetDocumentStats→AddSheet→verify pipeline.
/// </summary>
public class FodsR233GetCellValueAndDocumentStatsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR233GetCellValueAndDocumentStatsDeepTests()
    {
        _tempDir = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "FodsR233_" + Guid.NewGuid().ToString("N"));
        System.IO.Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (System.IO.Directory.Exists(_tempDir))
            System.IO.Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => System.IO.Path.Combine(_tempDir, name);

    private static FodsDocument CreateDataDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(0, 1, "Score");
        doc.SetCellValue(0, 2, "Dept");
        doc.AddRow(new List<string> { "Alice", "92", "Engineering" });
        doc.AddRow(new List<string> { "Bob", "78", "Finance" });
        doc.AddRow(new List<string> { "Carol", "85", "Engineering" });
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_FirstRowFirstCol_Correct()
    {
        var doc = CreateDataDoc();
        Assert.Equal("Alice", doc.GetCellValue(1, 0));
    }

    [Fact]
    public void GetCellValue_AfterSetCellValue_Reflects()
    {
        var doc = CreateDataDoc();
        doc.SetCellValue(1, 0, "ALICE_MOD");
        Assert.Equal("ALICE_MOD", doc.GetCellValue(1, 0));
    }

    [Fact]
    public void GetCellValue_NumericColumn_Correct()
    {
        var doc = CreateDataDoc();
        Assert.Equal("92", doc.GetCellValue(1, 1));
    }

    [Fact]
    public void GetCellValue_LastRow_Correct()
    {
        var doc = CreateDataDoc();
        Assert.Equal("Carol", doc.GetCellValue(3, 0));
    }

    [Fact]
    public void GetCellValue_AfterAddRow_Accessible()
    {
        var doc = CreateDataDoc();
        doc.AddRow(new List<string> { "Dave", "71", "HR" });
        Assert.Equal("Dave", doc.GetCellValue(4, 0));
    }

    [Fact]
    public void GetCellValue_DeptColumn_Correct()
    {
        var doc = CreateDataDoc();
        Assert.Equal("Engineering", doc.GetCellValue(1, 2));
        Assert.Equal("Finance", doc.GetCellValue(2, 2));
    }

    [Fact]
    public void GetCellValue_HeaderRow_Correct()
    {
        var doc = CreateDataDoc();
        Assert.Equal("Name", doc.GetCellValue(0, 0));
        Assert.Equal("Score", doc.GetCellValue(0, 1));
    }

    // -------------------------------------------------------------------------
    // GetDocumentStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentStats_NonNull()
    {
        var doc = CreateDataDoc();
        Assert.NotNull(doc.GetDocumentStats());
    }

    [Fact]
    public void GetDocumentStats_RowCountEqualsGetRowCount()
    {
        var doc = CreateDataDoc();
        Assert.Equal(doc.GetRowCount(), doc.GetDocumentStats().RowCount);
    }

    [Fact]
    public void GetDocumentStats_ColumnCountPositive()
    {
        var doc = CreateDataDoc();
        Assert.True(doc.GetDocumentStats().ColumnCount > 0);
    }

    [Fact]
    public void GetDocumentStats_SheetCountPositive()
    {
        var doc = CreateDataDoc();
        Assert.True(doc.GetDocumentStats().SheetCount > 0);
    }

    [Fact]
    public void GetDocumentStats_AfterAddRow_RowCountIncreases()
    {
        var doc = CreateDataDoc();
        var before = doc.GetDocumentStats().RowCount;
        doc.AddRow(new List<string> { "Dave", "71", "HR" });
        var after = doc.GetDocumentStats().RowCount;
        Assert.True(after > before);
    }

    [Fact]
    public void GetDocumentStats_AfterAddSheet_SheetCountIncreases()
    {
        var doc = CreateDataDoc();
        var before = doc.GetDocumentStats().SheetCount;
        doc.AddSheet("NewSheet");
        var after = doc.GetDocumentStats().SheetCount;
        Assert.True(after > before);
    }

    // -------------------------------------------------------------------------
    // GetSheetCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetCount_Positive()
    {
        var doc = CreateDataDoc();
        Assert.True(doc.GetSheetCount() > 0);
    }

    [Fact]
    public void GetSheetCount_IncreasesAfterAddSheet()
    {
        var doc = CreateDataDoc();
        var before = doc.GetSheetCount();
        doc.AddSheet("Extra");
        Assert.Equal(before + 1, doc.GetSheetCount());
    }

    [Fact]
    public void GetSheetCount_MatchesDocumentStats()
    {
        var doc = CreateDataDoc();
        Assert.Equal(doc.GetDocumentStats().SheetCount, doc.GetSheetCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_SetCellValues_GetCellValue_GetDocumentStats_AddSheet_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Inventory");
        doc.SetCellValue(0, 0, "Item");
        doc.SetCellValue(0, 1, "Quantity");
        doc.SetCellValue(0, 2, "Price");
        doc.AddRow(new List<string> { "Widget A", "100", "9.99" });
        doc.AddRow(new List<string> { "Widget B", "250", "4.99" });
        doc.AddRow(new List<string> { "Widget C", "75", "19.99" });
        doc.AddRow(new List<string> { "Widget D", "500", "2.99" });

        // GetCellValue × 6
        Assert.Equal("Item", doc.GetCellValue(0, 0));
        Assert.Equal("Widget A", doc.GetCellValue(1, 0));
        Assert.Equal("100", doc.GetCellValue(1, 1));
        Assert.Equal("Widget D", doc.GetCellValue(4, 0));
        Assert.Equal("2.99", doc.GetCellValue(4, 2));
        Assert.Equal("250", doc.GetCellValue(2, 1));

        // SetCellValue and re-verify
        doc.SetCellValue(1, 1, "150");
        Assert.Equal("150", doc.GetCellValue(1, 1));

        // GetDocumentStats
        var stats = doc.GetDocumentStats();
        Assert.NotNull(stats);
        Assert.Equal(4, stats.RowCount); // 4 data rows
        Assert.True(stats.ColumnCount >= 3);
        Assert.Equal(1, stats.SheetCount);

        // AddSheet and verify stats increase
        doc.AddSheet("Orders");
        var updatedStats = doc.GetDocumentStats();
        Assert.Equal(2, updatedStats.SheetCount);
        Assert.Equal(2, doc.GetSheetCount());

        // SwitchSheet to Orders and add data
        doc.SwitchSheet("Orders");
        doc.SetCellValue(0, 0, "OrderID");
        doc.SetCellValue(0, 1, "Amount");
        doc.AddRow(new List<string> { "ORD001", "1500" });
        doc.AddRow(new List<string> { "ORD002", "2300" });

        // GetCellValue on Orders sheet
        Assert.Equal("OrderID", doc.GetCellValue(0, 0));
        Assert.Equal("ORD001", doc.GetCellValue(1, 0));

        // SaveToFile
        var path = TempFile("inventory.fods");
        doc.SaveToFile(path);
        Assert.True(System.IO.File.Exists(path));

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);
        Assert.Equal(2, loaded.GetSheetCount());

        // Switch to Inventory sheet and check data
        loaded.SwitchSheet("Inventory");
        Assert.Equal("Widget A", loaded.GetCellValue(1, 0));
        Assert.Equal("150", loaded.GetCellValue(1, 1)); // Updated value persisted
    }
}
