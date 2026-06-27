// Tests for FodsDocument.GetCellFontSize dedicated coverage.
// Sprint: ff-sprint-s338-dotnet-deepening-20260630
// Ledger: PC-FODS-R376

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R376: Dedicated tests for FodsDocument.GetCellFontSize().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-negative.
/// SheetCount unchanged after GetCellFontSize.
/// Idempotent (called twice same result).
/// Dogfood: SetCellFontSize then Get returns correct size.
/// Dogfood: Multiple cells with different font sizes.
/// </summary>
public class FodsR376GetCellFontSizeDedicatedTests
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
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontSize("Missing", 0, 0));
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
        doc.AddSheet("Text");
        double fontSize = doc.GetCellFontSize("Text", 0, 0);
        Assert.True(fontSize >= 0);
    }

    [Fact]
    public void GetCellFontSize_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("SizeSheet");
        int before = doc.SheetCount;
        _ = doc.GetCellFontSize("SizeSheet", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFontSize_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        doc.SetCellFontSize("Stable", 0, 0, 14.0);
        double first = doc.GetCellFontSize("Stable", 0, 0);
        double second = doc.GetCellFontSize("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellFontSizeThenGet_ReturnsSize()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Headers");
        doc.SetCellFontSize("Headers", 0, 0, 18.0);
        double fontSize = doc.GetCellFontSize("Headers", 0, 0);
        Assert.Equal(18.0, fontSize, precision: 5);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCellsDifferentSizes_AllNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Mixed");
        doc.SetCellFontSize("Mixed", 0, 0, 10.0);
        doc.SetCellFontSize("Mixed", 0, 1, 12.0);
        doc.SetCellFontSize("Mixed", 0, 2, 24.0);
        Assert.True(doc.GetCellFontSize("Mixed", 0, 0) >= 0);
        Assert.True(doc.GetCellFontSize("Mixed", 0, 1) >= 0);
        Assert.True(doc.GetCellFontSize("Mixed", 0, 2) >= 0);
    }
}
