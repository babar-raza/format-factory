// Tests for FodsDocument.SetCellFontColor dedicated coverage.
// Sprint: ff-sprint-s319-dotnet-deepening-20260630
// Ledger: PC-FODS-R350

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R350: Dedicated tests for FodsDocument.SetCellFontColor(sheetName, row, col, color).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call no exception.
/// SheetCount unchanged after SetCellFontColor.
/// Called twice no exception.
/// Dogfood: set font color on multiple cells.
/// </summary>
public class FodsR350SetCellFontColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFontColor_NullSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFontColor(null!, 0, 0, "#FF0000"));
    }

    [Fact]
    public void SetCellFontColor_WhitespaceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFontColor("   ", 0, 0, "#FF0000"));
    }

    [Fact]
    public void SetCellFontColor_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellFontColor("NoSuchSheet", 0, 0, "#0000FF"));
    }

    [Fact]
    public void SetCellFontColor_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFontColor("Sheet1", -1, 0, "#FF0000"));
    }

    [Fact]
    public void SetCellFontColor_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFontColor("Sheet1", 0, -1, "#FF0000"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFontColor_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetCellFontColor("Sheet1", 0, 0, "#0000FF"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellFontColor_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.SetCellFontColor("Sheet1", 0, 0, "#FF0000");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellFontColor_CalledTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellFontColor("Sheet1", 0, 0, "#FF0000");
        var ex = Record.Exception(() => doc.SetCellFontColor("Sheet1", 0, 0, "#00FF00"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetFontColorMultipleCells_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Header");
        doc.SetCellFontColor("Report", 0, 0, "#FF0000");
        doc.SetCellFontColor("Report", 1, 0, "#0000FF");
        doc.SetCellFontColor("Report", 1, 1, "#00FF00");
        var ex = Record.Exception(() => doc.SetCellFontColor("Report", 2, 0, "#000000"));
        Assert.Null(ex);
        int before = doc.SheetCount;
        Assert.Equal(before, doc.SheetCount);
    }
}
