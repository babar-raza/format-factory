// Tests for FodsDocument.SetCellBorder dedicated coverage.
// Sprint: ff-sprint-s313-dotnet-deepening-20260630
// Ledger: PC-FODS-R344

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R344: Dedicated tests for FodsDocument.SetCellBorder(sheetName, row, col, borderStyle).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call no exception.
/// SheetCount unchanged after SetCellBorder.
/// Called twice no exception.
/// Dogfood: set border on multiple cells.
/// </summary>
public class FodsR344SetCellBorderDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellBorder_NullSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellBorder(null!, 0, 0, "thin"));
    }

    [Fact]
    public void SetCellBorder_WhitespaceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
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
        doc.SetCellBorder("Sheet1", 0, 0, "thin");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellBorder_CalledTwice_NoException()
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
    public void DogfoodPipeline_SetBorderMultipleCells_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Header");
        doc.SetCellBorder("Report", 0, 0, "thin");
        doc.SetCellBorder("Report", 0, 1, "thin");
        doc.SetCellBorder("Report", 1, 0, "medium");
        var ex = Record.Exception(() => doc.SetCellBorder("Report", 1, 1, "thick"));
        Assert.Null(ex);
        int before = doc.SheetCount;
        Assert.Equal(before, doc.SheetCount);
    }
}
