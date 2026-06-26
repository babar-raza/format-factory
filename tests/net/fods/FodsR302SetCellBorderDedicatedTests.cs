// Tests for FodsDocument.SetCellBorder dedicated coverage.
// Sprint: ff-sprint-s274-dotnet-deepening-20260630
// Ledger: PC-FODS-R302

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R302: Dedicated tests for FodsDocument.SetCellBorder(sheetName, row, col, borderStyle).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call no exception.
/// SheetCount unchanged after SetCellBorder.
/// Set twice no exception.
/// Dogfood: set border on multiple cells no exception.
/// Dogfood: set border then set value, both succeed.
/// </summary>
public class FodsR302SetCellBorderDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellBorder_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellBorder(null!, 0, 0, "thin"));
    }

    [Fact]
    public void SetCellBorder_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellBorder("   ", 0, 0, "thin"));
    }

    [Fact]
    public void SetCellBorder_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellBorder("NoSuchSheet", 0, 0, "thin"));
    }

    [Fact]
    public void SetCellBorder_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellBorder("Sheet1", -1, 0, "thin"));
    }

    [Fact]
    public void SetCellBorder_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellBorder("Sheet1", 0, -1, "thin"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellBorder_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetCellBorder("Sheet1", 0, 0, "thin"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellBorder_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.SetCellBorder("Sheet1", 0, 0, "thick");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellBorder_SetTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellBorder("Sheet1", 0, 0, "thin");
        var ex = Record.Exception(() => doc.SetCellBorder("Sheet1", 0, 0, "thick"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetBorderOnMultipleCells_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Styled");
        var ex = Record.Exception(() =>
        {
            doc.SetCellBorder("Styled", 0, 0, "thin");
            doc.SetCellBorder("Styled", 0, 1, "thick");
            doc.SetCellBorder("Styled", 1, 0, "thin");
            doc.SetCellBorder("Styled", 1, 1, "thick");
        });
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_SetBorderThenSetValue_BothSucceed()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        var ex = Record.Exception(() =>
        {
            doc.SetCellBorder("Report", 0, 0, "thin");
            doc.SetCellValue("Report", 0, 0, "Header");
        });
        Assert.Null(ex);
    }
}
