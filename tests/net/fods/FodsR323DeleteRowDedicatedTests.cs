// Tests for FodsDocument.DeleteRow dedicated coverage.
// Sprint: ff-sprint-s295-dotnet-deepening-20260630
// Ledger: PC-FODS-R323

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R323: Dedicated tests for FodsDocument.DeleteRow(sheetName, rowIndex).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative row index throws exception.
/// Valid call no exception.
/// Row count decreases after DeleteRow.
/// SheetCount unchanged after DeleteRow.
/// Delete last row no exception.
/// Dogfood: add rows then delete, row count matches.
/// Dogfood: two sheets delete row from first, second unchanged.
/// </summary>
public class FodsR323DeleteRowDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRow_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddRow("Sheet1", new[] { "A" });
        Assert.ThrowsAny<Exception>(() => doc.DeleteRow(null!, 0));
    }

    [Fact]
    public void DeleteRow_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddRow("Sheet1", new[] { "A" });
        Assert.ThrowsAny<Exception>(() => doc.DeleteRow("   ", 0));
    }

    [Fact]
    public void DeleteRow_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.DeleteRow("DoesNotExist", 0));
    }

    [Fact]
    public void DeleteRow_NegativeRowIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddRow("Sheet1", new[] { "A" });
        Assert.ThrowsAny<Exception>(() => doc.DeleteRow("Sheet1", -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRow_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddRow("Data", new[] { "Value1", "Value2" });
        int before = doc.GetRowCount("Data");
        var ex = Record.Exception(() => doc.DeleteRow("Data", before - 1));
        Assert.Null(ex);
    }

    [Fact]
    public void DeleteRow_RowCountDecreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddRow("Data", new[] { "Row1" });
        doc.AddRow("Data", new[] { "Row2" });
        int before = doc.GetRowCount("Data");
        doc.DeleteRow("Data", before - 1);
        int after = doc.GetRowCount("Data");
        Assert.True(after < before);
    }

    [Fact]
    public void DeleteRow_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddRow("Data", new[] { "A" });
        int sheetsBefore = doc.SheetCount;
        int row = doc.GetRowCount("Data") - 1;
        doc.DeleteRow("Data", row);
        Assert.Equal(sheetsBefore, doc.SheetCount);
    }

    [Fact]
    public void DeleteRow_DeleteLastRow_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddRow("Data", new[] { "Only" });
        int lastRow = doc.GetRowCount("Data") - 1;
        var ex = Record.Exception(() => doc.DeleteRow("Data", lastRow));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddRowsThenDelete_RowCountMatches()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.AddRow("Report", new[] { "H1", "H2" });
        doc.AddRow("Report", new[] { "D1", "D2" });
        doc.AddRow("Report", new[] { "D3", "D4" });
        int before = doc.GetRowCount("Report");
        doc.DeleteRow("Report", before - 1);
        int after = doc.GetRowCount("Report");
        Assert.Equal(before - 1, after);
    }

    [Fact]
    public void DogfoodPipeline_TwoSheets_DeleteFromFirst_SecondUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        doc.AddRow("Sheet1", new[] { "A" });
        doc.AddRow("Sheet2", new[] { "X" });
        int sheet2Before = doc.GetRowCount("Sheet2");
        doc.DeleteRow("Sheet1", doc.GetRowCount("Sheet1") - 1);
        int sheet2After = doc.GetRowCount("Sheet2");
        Assert.Equal(sheet2Before, sheet2After);
    }
}
