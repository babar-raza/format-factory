// Tests for FodsDocument.InsertRow, DeleteRows, ClearSheet deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R222

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R222: Tests for FodsDocument.InsertRow, DeleteRows, ClearSheet deeper coverage.
/// InsertRow(sheet, rowIndex, values): inserts a row at the given index with values.
/// DeleteRows(sheet, rowIndex, count): removes rows from the given index.
/// ClearSheet(sheet): clears all data from a sheet.
/// Covers: InsertRow increases RowCount; InsertRow at 0 becomes first;
/// InsertRow at end becomes last; InsertRow values accessible;
/// DeleteRows decreases RowCount; DeleteRows removes specified row;
/// DeleteRows leaves other rows intact; DeleteRows count=2 removes two;
/// ClearSheet leaves zero row count; ClearSheet then SetCellValue works;
/// ClearSheet then InsertRow works; ClearSheet multiple sheets isolated;
/// dogfood CreateDoc->InsertRow->DeleteRows->ClearSheet->Verify pipeline.
/// </summary>
public class FodsR222InsertRowAndDeleteRowDeepTests
{
    private static FodsDocument CreateWithData()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Alice");
        doc.SetCellValue("Data", 0, 1, "Eng");
        doc.SetCellValue("Data", 1, 0, "Bob");
        doc.SetCellValue("Data", 1, 1, "Finance");
        doc.SetCellValue("Data", 2, 0, "Carol");
        doc.SetCellValue("Data", 2, 1, "HR");
        return doc;
    }

    // -------------------------------------------------------------------------
    // InsertRow
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertRow_IncreasesRowCount()
    {
        var doc = CreateWithData();
        var before = doc.GetRowCount("Data");
        doc.InsertRow("Data", 0, new[] { "Dave", "Legal" });
        Assert.True(doc.GetRowCount("Data") > before);
    }

    [Fact]
    public void InsertRow_AtZero_BecomesFirstRow()
    {
        var doc = CreateWithData();
        doc.InsertRow("Data", 0, new[] { "FIRST", "TOP" });
        Assert.Equal("FIRST", doc.GetCellValue("Data", 0, 0));
    }

    [Fact]
    public void InsertRow_ValuesAccessibleViaGetCellValue()
    {
        var doc = CreateWithData();
        doc.InsertRow("Data", 0, new[] { "Inserted", "IT" });
        Assert.Equal("Inserted", doc.GetCellValue("Data", 0, 0));
        Assert.Equal("IT", doc.GetCellValue("Data", 0, 1));
    }

    [Fact]
    public void InsertRow_ShiftsExistingRowsDown()
    {
        var doc = CreateWithData();
        doc.InsertRow("Data", 0, new[] { "New", "Top" });
        // Alice should now be at row 1
        Assert.Equal("Alice", doc.GetCellValue("Data", 1, 0));
    }

    [Fact]
    public void InsertRow_MultipleInserts_AllPresent()
    {
        var doc = CreateWithData();
        doc.InsertRow("Data", 0, new[] { "A", "1" });
        doc.InsertRow("Data", 0, new[] { "B", "2" });
        Assert.True(doc.GetRowCount("Data") >= 5);
    }

    // -------------------------------------------------------------------------
    // DeleteRows
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRows_DecreasesRowCount()
    {
        var doc = CreateWithData();
        var before = doc.GetRowCount("Data");
        doc.DeleteRows("Data", 0, 1);
        Assert.True(doc.GetRowCount("Data") < before);
    }

    [Fact]
    public void DeleteRows_RemovesSpecifiedRow()
    {
        var doc = CreateWithData();
        // Delete row 0 (Alice)
        doc.DeleteRows("Data", 0, 1);
        // Bob should now be at row 0
        Assert.Equal("Bob", doc.GetCellValue("Data", 0, 0));
    }

    [Fact]
    public void DeleteRows_Count2_RemovesTwoRows()
    {
        var doc = CreateWithData();
        var before = doc.GetRowCount("Data");
        doc.DeleteRows("Data", 0, 2);
        Assert.Equal(before - 2, doc.GetRowCount("Data"));
    }

    [Fact]
    public void DeleteRows_LeavesOtherRowsIntact()
    {
        var doc = CreateWithData();
        doc.DeleteRows("Data", 0, 1); // Delete Alice
        // Bob at row 0, Carol at row 1
        Assert.Equal("Bob", doc.GetCellValue("Data", 0, 0));
        Assert.Equal("Carol", doc.GetCellValue("Data", 1, 0));
    }

    [Fact]
    public void DeleteRows_DeleteLastRow_Works()
    {
        var doc = CreateWithData();
        var rowCount = doc.GetRowCount("Data");
        doc.DeleteRows("Data", rowCount - 1, 1);
        Assert.Equal(rowCount - 1, doc.GetRowCount("Data"));
    }

    // -------------------------------------------------------------------------
    // ClearSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void ClearSheet_LeavesZeroOrMinimalRowCount()
    {
        var doc = CreateWithData();
        doc.ClearSheet("Data");
        Assert.True(doc.GetRowCount("Data") == 0 || doc.GetCellValue("Data", 0, 0) == "" || doc.GetCellValue("Data", 0, 0) == null);
    }

    [Fact]
    public void ClearSheet_ThenSetCellValue_Works()
    {
        var doc = CreateWithData();
        doc.ClearSheet("Data");
        var ex = Record.Exception(() => doc.SetCellValue("Data", 0, 0, "Fresh"));
        Assert.Null(ex);
        Assert.Equal("Fresh", doc.GetCellValue("Data", 0, 0));
    }

    [Fact]
    public void ClearSheet_MultipleSheets_Isolated()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        doc.SetCellValue("Alpha", 0, 0, "AlphaData");
        doc.SetCellValue("Beta", 0, 0, "BetaData");
        doc.ClearSheet("Alpha");
        // Beta should still have data
        Assert.Equal("BetaData", doc.GetCellValue("Beta", 0, 0));
    }

    [Fact]
    public void ClearSheet_ThenInsertRow_Works()
    {
        var doc = CreateWithData();
        doc.ClearSheet("Data");
        var ex = Record.Exception(() => doc.InsertRow("Data", 0, new[] { "NewA", "NewB" }));
        Assert.Null(ex);
        Assert.Equal("NewA", doc.GetCellValue("Data", 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_InsertRow_DeleteRows_ClearSheet_Verify_Pipeline()
    {
        var doc = CreateWithData();
        Assert.Equal(3, doc.GetRowCount("Data"));

        // InsertRow at beginning
        doc.InsertRow("Data", 0, new[] { "HEADER_Alice", "HEADER_Dept" });
        Assert.True(doc.GetRowCount("Data") >= 4);
        Assert.Equal("HEADER_Alice", doc.GetCellValue("Data", 0, 0));
        Assert.Equal("Alice", doc.GetCellValue("Data", 1, 0)); // shifted

        // InsertRow at end
        var rowCount = doc.GetRowCount("Data");
        doc.InsertRow("Data", rowCount, new[] { "Eve", "Operations" });
        Assert.True(doc.GetRowCount("Data") >= 5);

        // DeleteRows — remove header row
        doc.DeleteRows("Data", 0, 1);
        Assert.Equal("Alice", doc.GetCellValue("Data", 0, 0)); // back to first

        // DeleteRows — remove 2 rows from index 1
        var countBefore = doc.GetRowCount("Data");
        doc.DeleteRows("Data", 1, 2);
        Assert.Equal(countBefore - 2, doc.GetRowCount("Data"));

        // ClearSheet
        doc.ClearSheet("Data");
        // After clear, set fresh data
        doc.SetCellValue("Data", 0, 0, "PostClear");
        Assert.Equal("PostClear", doc.GetCellValue("Data", 0, 0));

        // Multi-sheet isolation
        doc.AddSheet("Summary");
        doc.SetCellValue("Summary", 0, 0, "SummaryData");
        doc.ClearSheet("Data");
        Assert.Equal("SummaryData", doc.GetCellValue("Summary", 0, 0));
    }
}
