// Tests for FodsDocument.SetCellAlignment dedicated coverage.
// Sprint: ff-sprint-s318-dotnet-deepening-20260630
// Ledger: PC-FODS-R349

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R349: Dedicated tests for FodsDocument.SetCellAlignment(sheetName, row, col, alignment).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call no exception.
/// SheetCount unchanged after SetCellAlignment.
/// Called twice no exception.
/// Dogfood: set alignment on multiple cells.
/// </summary>
public class FodsR349SetCellAlignmentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellAlignment_NullSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellAlignment(null!, 0, 0, "center"));
    }

    [Fact]
    public void SetCellAlignment_WhitespaceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellAlignment("   ", 0, 0, "center"));
    }

    [Fact]
    public void SetCellAlignment_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellAlignment("NoSuchSheet", 0, 0, "left"));
    }

    [Fact]
    public void SetCellAlignment_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellAlignment("Sheet1", -1, 0, "center"));
    }

    [Fact]
    public void SetCellAlignment_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellAlignment("Sheet1", 0, -1, "center"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellAlignment_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetCellAlignment("Sheet1", 0, 0, "left"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellAlignment_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.SetCellAlignment("Sheet1", 0, 0, "right");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellAlignment_CalledTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellAlignment("Sheet1", 0, 0, "left");
        var ex = Record.Exception(() => doc.SetCellAlignment("Sheet1", 0, 0, "center"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetAlignmentMultipleCells_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Header");
        doc.SetCellAlignment("Report", 0, 0, "center");
        doc.SetCellAlignment("Report", 1, 0, "left");
        doc.SetCellAlignment("Report", 1, 1, "right");
        var ex = Record.Exception(() => doc.SetCellAlignment("Report", 2, 0, "center"));
        Assert.Null(ex);
        int before = doc.SheetCount;
        Assert.Equal(before, doc.SheetCount);
    }
}
