// Tests for FodsDocument.DeleteRow dedicated coverage.
// Sprint: ff-sprint-s223-dotnet-deepening-20260629
// Ledger: PC-FODS-R241

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R241: Dedicated tests for FodsDocument.DeleteRow(sheetName, rowIndex).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Negative row index → throws exception.
/// Empty sheet delete → throws or no-exception.
/// Valid delete → no exception.
/// Row count decreases after delete.
/// SheetCount unchanged after delete.
/// Delete row zero: no exception.
/// Dogfood: add rows then delete, count decreases.
/// </summary>
public class FodsR241DeleteRowDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRow_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.DeleteRow(null!, 0));
    }

    [Fact]
    public void DeleteRow_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.DeleteRow("   ", 0));
    }

    [Fact]
    public void DeleteRow_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.DeleteRow("NoSheet", 0));
    }

    [Fact]
    public void DeleteRow_NegativeRowIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.DeleteRow(sheetName, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRow_ValidDelete_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "A", "B", "C" });
        var ex = Record.Exception(() => doc.DeleteRow(sheetName, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void DeleteRow_RowCountDecreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Row1A" });
        doc.AddRow(sheetName, new[] { "Row2A" });
        int before = doc.GetRowCount(sheetName);
        doc.DeleteRow(sheetName, 0);
        int after = doc.GetRowCount(sheetName);
        Assert.True(after < before);
    }

    [Fact]
    public void DeleteRow_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "X" });
        int before = doc.SheetCount;
        doc.DeleteRow(sheetName, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void DeleteRow_DeleteRowZero_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "FirstRow" });
        var ex = Record.Exception(() => doc.DeleteRow(sheetName, 0));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddThenDelete_CountDecreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Row1" });
        doc.AddRow(sheetName, new[] { "Row2" });
        doc.AddRow(sheetName, new[] { "Row3" });
        int before = doc.GetRowCount(sheetName);
        doc.DeleteRow(sheetName, 0);
        int after = doc.GetRowCount(sheetName);
        Assert.True(after < before);
    }
}
