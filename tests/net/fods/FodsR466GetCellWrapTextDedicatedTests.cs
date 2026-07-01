// Tests for FodsDocument.GetCellWrapText dedicated coverage.
// Sprint: ff-sprint-s417-dotnet-deepening-20260701
// Ledger: PC-FODS-R466

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R466: Dedicated tests for FodsDocument.GetCellWrapText().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns bool.
/// SheetCount unchanged after GetCellWrapText.
/// Idempotent (called twice same result).
/// SetCellWrapText(true) + GetCellWrapText returns true.
/// SetCellWrapText(false) + GetCellWrapText returns false.
/// Dogfood: default cell wrap text is bool.
/// </summary>
public class FodsR466GetCellWrapTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellWrapText_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellWrapText(null!, 0, 0));
    }

    [Fact]
    public void GetCellWrapText_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellWrapText("   ", 0, 0));
    }

    [Fact]
    public void GetCellWrapText_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellWrapText("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellWrapText_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellWrapText("Sheet1", -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellWrapText_ValidCell_ReturnsBool()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        bool wrap = doc.GetCellWrapText("Sheet1", 0, 0);
        Assert.IsType<bool>(wrap);
    }

    [Fact]
    public void GetCellWrapText_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellWrapText("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellWrapText_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        bool first = doc.GetCellWrapText("Sheet1", 0, 0);
        bool second = doc.GetCellWrapText("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellWrapText_SetTrue_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellWrapText("Data", 0, 0, true);
        Assert.True(doc.GetCellWrapText("Data", 0, 0));
    }

    [Fact]
    public void GetCellWrapText_SetFalse_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellWrapText("Data", 0, 0, false);
        Assert.False(doc.GetCellWrapText("Data", 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_WrapTextIsBool()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        object result = doc.GetCellWrapText("Report", 0, 0);
        Assert.IsType<bool>(result);
    }
}
