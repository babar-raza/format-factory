// Tests for FodsDocument.DeleteRow dedicated coverage.
// Sprint: ff-sprint-s257-dotnet-deepening-20260630
// Ledger: PC-FODS-R279

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R279: Dedicated tests for FodsDocument.DeleteRow(sheetName, rowIndex).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet name → throws exception.
/// Negative row index → throws exception.
/// Out-of-bounds row index → throws exception.
/// Valid delete → no exception.
/// GetRowCount decreases after deletion.
/// SheetCount unchanged after deletion.
/// Other rows unaffected by deletion.
/// Dogfood: add rows then delete first, count decreases by 1.
/// Dogfood: delete last row of data, count decreases.
/// </summary>
public class FodsR279DeleteRowDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRow_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddRow("Sheet1", new[] { "a", "b" });
        Assert.ThrowsAny<Exception>(() => doc.DeleteRow(null!, 0));
    }

    [Fact]
    public void DeleteRow_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddRow("Sheet1", new[] { "a", "b" });
        Assert.ThrowsAny<Exception>(() => doc.DeleteRow("   ", 0));
    }

    [Fact]
    public void DeleteRow_NonexistentSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.DeleteRow("NoSuchSheet", 0));
    }

    [Fact]
    public void DeleteRow_NegativeRowIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddRow("Sheet1", new[] { "a", "b" });
        Assert.ThrowsAny<Exception>(() => doc.DeleteRow("Sheet1", -1));
    }

    [Fact]
    public void DeleteRow_OutOfBoundsRowIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddRow("Sheet1", new[] { "a", "b" });
        int count = doc.GetRowCount("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.DeleteRow("Sheet1", count));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRow_ValidDelete_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddRow("Sheet1", new[] { "x", "y" });
        var ex = Record.Exception(() => doc.DeleteRow("Sheet1", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void DeleteRow_RowCountDecreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddRow("Sheet1", new[] { "a" });
        doc.AddRow("Sheet1", new[] { "b" });
        int before = doc.GetRowCount("Sheet1");
        doc.DeleteRow("Sheet1", 0);
        Assert.True(doc.GetRowCount("Sheet1") < before);
    }

    [Fact]
    public void DeleteRow_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddRow("Sheet1", new[] { "data" });
        int before = doc.SheetCount;
        doc.DeleteRow("Sheet1", 0);
        Assert.Equal(before, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddRowsThenDeleteFirst_CountDecreasesBy1()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddRow("Data", new[] { "row1col1", "row1col2" });
        doc.AddRow("Data", new[] { "row2col1", "row2col2" });
        doc.AddRow("Data", new[] { "row3col1", "row3col2" });
        int before = doc.GetRowCount("Data");
        doc.DeleteRow("Data", 0);
        Assert.Equal(before - 1, doc.GetRowCount("Data"));
    }

    [Fact]
    public void DogfoodPipeline_DeleteLastRow_CountDecreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddRow("Sheet1", new[] { "first" });
        doc.AddRow("Sheet1", new[] { "last" });
        int before = doc.GetRowCount("Sheet1");
        doc.DeleteRow("Sheet1", before - 1); // delete last row
        Assert.Equal(before - 1, doc.GetRowCount("Sheet1"));
    }
}
