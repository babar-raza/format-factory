// Tests for FodsDocument.SetCellFont dedicated coverage.
// Sprint: ff-sprint-s271-dotnet-deepening-20260630
// Ledger: PC-FODS-R297

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R297: Dedicated tests for FodsDocument.SetCellFont(sheetName, row, col, fontName, fontSize).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call no exception.
/// SheetCount unchanged after SetCellFont.
/// Set twice no exception.
/// Dogfood: set font on multiple cells no exception.
/// Dogfood: set font then set value, both succeed.
/// </summary>
public class FodsR297SetCellFontDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFont_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellFont(null!, 0, 0, "Arial", 12));
    }

    [Fact]
    public void SetCellFont_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellFont("   ", 0, 0, "Arial", 12));
    }

    [Fact]
    public void SetCellFont_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellFont("NoSuchSheet", 0, 0, "Arial", 12));
    }

    [Fact]
    public void SetCellFont_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFont("Sheet1", -1, 0, "Arial", 12));
    }

    [Fact]
    public void SetCellFont_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFont("Sheet1", 0, -1, "Arial", 12));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFont_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetCellFont("Sheet1", 0, 0, "Arial", 12));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellFont_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.SetCellFont("Sheet1", 0, 0, "Times New Roman", 14);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellFont_SetTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellFont("Sheet1", 0, 0, "Arial", 12);
        var ex = Record.Exception(() => doc.SetCellFont("Sheet1", 0, 0, "Helvetica", 16));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetFontOnMultipleCells_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Styled");
        var ex = Record.Exception(() =>
        {
            doc.SetCellFont("Styled", 0, 0, "Arial", 10);
            doc.SetCellFont("Styled", 0, 1, "Courier New", 12);
            doc.SetCellFont("Styled", 1, 0, "Verdana", 14);
            doc.SetCellFont("Styled", 1, 1, "Georgia", 16);
        });
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_SetFontThenSetValue_BothSucceed()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        var ex = Record.Exception(() =>
        {
            doc.SetCellFont("Report", 0, 0, "Arial", 12);
            doc.SetCellValue("Report", 0, 0, "Header");
        });
        Assert.Null(ex);
    }
}
