// Tests for FodsDocument.GetCellBackgroundColor dedicated coverage.
// Sprint: ff-sprint-s344-dotnet-deepening-20260630
// Ledger: PC-FODS-R382

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R382: Dedicated tests for FodsDocument.GetCellBackgroundColor().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellBackgroundColor.
/// Idempotent (called twice same result).
/// Dogfood: SetCellBackgroundColor then Get returns color.
/// Dogfood: Multiple cells with different background colors all non-null.
/// </summary>
public class FodsR382GetCellBackgroundColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellBackgroundColor_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBackgroundColor(null!, 0, 0));
    }

    [Fact]
    public void GetCellBackgroundColor_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBackgroundColor("   ", 0, 0));
    }

    [Fact]
    public void GetCellBackgroundColor_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBackgroundColor("Void", 0, 0));
    }

    [Fact]
    public void GetCellBackgroundColor_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Background");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBackgroundColor("Background", -1, 0));
    }

    [Fact]
    public void GetCellBackgroundColor_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Colors");
        string? color = doc.GetCellBackgroundColor("Colors", 0, 0);
        Assert.NotNull(color);
    }

    [Fact]
    public void GetCellBackgroundColor_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("BgSheet");
        int before = doc.SheetCount;
        _ = doc.GetCellBackgroundColor("BgSheet", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellBackgroundColor_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Repeat");
        doc.SetCellBackgroundColor("Repeat", 0, 0, "#FFFFCC");
        string? first = doc.GetCellBackgroundColor("Repeat", 0, 0);
        string? second = doc.GetCellBackgroundColor("Repeat", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellBackgroundColorThenGet_ReturnsColor()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Highlights");
        doc.SetCellBackgroundColor("Highlights", 0, 0, "#FFE4B5");
        string? color = doc.GetCellBackgroundColor("Highlights", 0, 0);
        Assert.NotNull(color);
        Assert.Equal("#FFE4B5", color);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCellsDifferentColors_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Spectrum");
        doc.SetCellBackgroundColor("Spectrum", 0, 0, "#FFCCCC");
        doc.SetCellBackgroundColor("Spectrum", 0, 1, "#CCFFCC");
        doc.SetCellBackgroundColor("Spectrum", 0, 2, "#CCCCFF");
        Assert.NotNull(doc.GetCellBackgroundColor("Spectrum", 0, 0));
        Assert.NotNull(doc.GetCellBackgroundColor("Spectrum", 0, 1));
        Assert.NotNull(doc.GetCellBackgroundColor("Spectrum", 0, 2));
    }
}
