// Tests for FodsDocument.GetCellTooltip dedicated coverage.
// Sprint: ff-sprint-s347-dotnet-deepening-20260630
// Ledger: PC-FODS-R385

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R385: Dedicated tests for FodsDocument.GetCellTooltip().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellTooltip.
/// Idempotent (called twice same result).
/// Dogfood: SetCellTooltip then GetCellTooltip returns expected text.
/// Dogfood: multiple cells with different tooltips each non-null.
/// </summary>
public class FodsR385GetCellTooltipDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellTooltip_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellTooltip(null!, 0, 0));
    }

    [Fact]
    public void GetCellTooltip_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellTooltip("   ", 0, 0));
    }

    [Fact]
    public void GetCellTooltip_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellTooltip("Ghost", 0, 0));
    }

    [Fact]
    public void GetCellTooltip_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Tips");
        Assert.ThrowsAny<Exception>(() => doc.GetCellTooltip("Tips", -1, 0));
    }

    [Fact]
    public void GetCellTooltip_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string? tooltip = doc.GetCellTooltip("Sheet1", 0, 0);
        Assert.NotNull(tooltip);
    }

    [Fact]
    public void GetCellTooltip_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Tooltips");
        int before = doc.SheetCount;
        _ = doc.GetCellTooltip("Tooltips", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellTooltip_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string? first = doc.GetCellTooltip("Stable", 0, 0);
        string? second = doc.GetCellTooltip("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterSetCellTooltip_ReturnsExpectedText()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Help");
        doc.SetCellTooltip("Help", 0, 0, "Enter a value between 0 and 100");
        string? tooltip = doc.GetCellTooltip("Help", 0, 0);
        Assert.NotNull(tooltip);
        Assert.Equal("Enter a value between 0 and 100", tooltip);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_DifferentTooltips()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Guide");
        doc.SetCellTooltip("Guide", 0, 0, "Column header tooltip");
        doc.SetCellTooltip("Guide", 1, 0, "First data row tooltip");
        doc.SetCellTooltip("Guide", 2, 0, "Summary row tooltip");
        Assert.NotNull(doc.GetCellTooltip("Guide", 0, 0));
        Assert.NotNull(doc.GetCellTooltip("Guide", 1, 0));
        Assert.NotNull(doc.GetCellTooltip("Guide", 2, 0));
    }
}
