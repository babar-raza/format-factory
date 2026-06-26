// Tests for FodsDocument.SetCellColor dedicated coverage.
// Sprint: ff-sprint-s270-dotnet-deepening-20260630
// Ledger: PC-FODS-R296

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R296: Dedicated tests for FodsDocument.SetCellColor(sheetName, row, col, color).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call no exception.
/// SheetCount unchanged after SetCellColor.
/// Set twice no exception.
/// Dogfood: set color on multiple cells no exception.
/// Dogfood: set color then set value, both succeed.
/// </summary>
public class FodsR296SetCellColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellColor_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellColor(null!, 0, 0, "#FF0000"));
    }

    [Fact]
    public void SetCellColor_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellColor("   ", 0, 0, "#FF0000"));
    }

    [Fact]
    public void SetCellColor_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellColor("NoSuchSheet", 0, 0, "#FF0000"));
    }

    [Fact]
    public void SetCellColor_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellColor("Sheet1", -1, 0, "#FF0000"));
    }

    [Fact]
    public void SetCellColor_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellColor("Sheet1", 0, -1, "#FF0000"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellColor_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetCellColor("Sheet1", 0, 0, "#FF0000"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellColor_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.SetCellColor("Sheet1", 0, 0, "#00FF00");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellColor_SetTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellColor("Sheet1", 0, 0, "#FF0000");
        var ex = Record.Exception(() => doc.SetCellColor("Sheet1", 0, 0, "#0000FF"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetColorOnMultipleCells_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        var ex = Record.Exception(() =>
        {
            doc.SetCellColor("Data", 0, 0, "#FF0000");
            doc.SetCellColor("Data", 0, 1, "#00FF00");
            doc.SetCellColor("Data", 1, 0, "#0000FF");
            doc.SetCellColor("Data", 1, 1, "#FFFF00");
        });
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_SetColorThenSetValue_BothSucceed()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Styled");
        var ex = Record.Exception(() =>
        {
            doc.SetCellColor("Styled", 0, 0, "#FF0000");
            doc.SetCellValue("Styled", 0, 0, "Red cell");
        });
        Assert.Null(ex);
    }
}
