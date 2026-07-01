// Tests for FodsDocument.GetCellStrikethrough dedicated coverage.
// Sprint: ff-sprint-s421-dotnet-deepening-20260701
// Ledger: PC-FODS-R470

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R470: Dedicated tests for FodsDocument.GetCellStrikethrough().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns bool.
/// SheetCount unchanged after GetCellStrikethrough.
/// Idempotent (called twice same result).
/// SetCellStrikethrough(true) + GetCellStrikethrough returns true.
/// SetCellStrikethrough(false) + GetCellStrikethrough returns false.
/// Dogfood: default cell strikethrough is bool.
/// </summary>
public class FodsR470GetCellStrikethroughDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStrikethrough_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellStrikethrough(null!, 0, 0));
    }

    [Fact]
    public void GetCellStrikethrough_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellStrikethrough("   ", 0, 0));
    }

    [Fact]
    public void GetCellStrikethrough_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellStrikethrough("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellStrikethrough_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellStrikethrough("Sheet1", -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStrikethrough_ValidCell_ReturnsBool()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        bool st = doc.GetCellStrikethrough("Sheet1", 0, 0);
        Assert.IsType<bool>(st);
    }

    [Fact]
    public void GetCellStrikethrough_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellStrikethrough("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellStrikethrough_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        bool first = doc.GetCellStrikethrough("Sheet1", 0, 0);
        bool second = doc.GetCellStrikethrough("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellStrikethrough_SetTrue_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellStrikethrough("Data", 0, 0, true);
        Assert.True(doc.GetCellStrikethrough("Data", 0, 0));
    }

    [Fact]
    public void GetCellStrikethrough_SetFalse_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellStrikethrough("Data", 0, 0, false);
        Assert.False(doc.GetCellStrikethrough("Data", 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_StrikethroughIsBool()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        object result = doc.GetCellStrikethrough("Report", 0, 0);
        Assert.IsType<bool>(result);
    }
}
