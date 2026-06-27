// Tests for FodsDocument.GetCellFontSize dedicated coverage.
// Sprint: ff-sprint-s362-dotnet-deepening-20260630
// Ledger: PC-FODS-R404

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R404: Dedicated tests for FodsDocument.GetCellFontSize().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-negative.
/// SheetCount unchanged after GetCellFontSize.
/// Idempotent (called twice same result).
/// Dogfood: SetCellFontSize 14 then GetCellFontSize returns 14.
/// Dogfood: multiple cells each returns non-negative font size.
/// </summary>
public class FodsR404GetCellFontSizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontSize_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontSize(null!, 0, 0));
    }

    [Fact]
    public void GetCellFontSize_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontSize("   ", 0, 0));
    }

    [Fact]
    public void GetCellFontSize_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontSize("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellFontSize_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sizes");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontSize("Sizes", -1, 0));
    }

    [Fact]
    public void GetCellFontSize_ValidCell_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        double size = doc.GetCellFontSize("Data", 0, 0);
        Assert.True(size >= 0);
    }

    [Fact]
    public void GetCellFontSize_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Style");
        int before = doc.SheetCount;
        _ = doc.GetCellFontSize("Style", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFontSize_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        double first = doc.GetCellFontSize("Stable", 0, 0);
        double second = doc.GetCellFontSize("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetFontSize14_ReturnsExpected()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellFontSize("Report", 0, 0, 14.0);
        double size = doc.GetCellFontSize("Report", 0, 0);
        Assert.Equal(14.0, size, 1);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_EachNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Typography");
        doc.SetCellFontSize("Typography", 0, 0, 10.0);
        doc.SetCellFontSize("Typography", 1, 0, 12.0);
        doc.SetCellFontSize("Typography", 2, 0, 16.0);
        Assert.True(doc.GetCellFontSize("Typography", 0, 0) >= 0);
        Assert.True(doc.GetCellFontSize("Typography", 1, 0) >= 0);
        Assert.True(doc.GetCellFontSize("Typography", 2, 0) >= 0);
    }
}
