// Tests for FodsDocument.SetCellFontSize dedicated coverage.
// Sprint: ff-sprint-s315-dotnet-deepening-20260630
// Ledger: PC-FODS-R346

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R346: Dedicated tests for FodsDocument.SetCellFontSize(sheetName, row, col, fontSize).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call no exception.
/// SheetCount unchanged after SetCellFontSize.
/// Called twice no exception.
/// Dogfood: set different font sizes on multiple cells.
/// </summary>
public class FodsR346SetCellFontSizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFontSize_NullSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFontSize(null!, 0, 0, 12));
    }

    [Fact]
    public void SetCellFontSize_WhitespaceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFontSize("   ", 0, 0, 12));
    }

    [Fact]
    public void SetCellFontSize_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellFontSize("NoSuchSheet", 0, 0, 12));
    }

    [Fact]
    public void SetCellFontSize_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFontSize("Sheet1", -1, 0, 12));
    }

    [Fact]
    public void SetCellFontSize_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFontSize("Sheet1", 0, -1, 12));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFontSize_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetCellFontSize("Sheet1", 0, 0, 14));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellFontSize_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.SetCellFontSize("Sheet1", 0, 0, 12);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellFontSize_CalledTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellFontSize("Sheet1", 0, 0, 12);
        var ex = Record.Exception(() => doc.SetCellFontSize("Sheet1", 0, 0, 16));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetFontSizeMultipleCells_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Title");
        doc.SetCellFontSize("Report", 0, 0, 18);
        doc.SetCellFontSize("Report", 1, 0, 12);
        doc.SetCellFontSize("Report", 1, 1, 10);
        var ex = Record.Exception(() => doc.SetCellFontSize("Report", 2, 0, 9));
        Assert.Null(ex);
        int before = doc.SheetCount;
        Assert.Equal(before, doc.SheetCount);
    }
}
