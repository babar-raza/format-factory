// Tests for FodsDocument.GetSheetTabColor dedicated coverage.
// Sprint: ff-sprint-s333-dotnet-deepening-20260630
// Ledger: PC-FODS-R368

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R368: Dedicated tests for FodsDocument.GetSheetTabColor().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Valid sheet returns non-null.
/// SheetCount unchanged after GetSheetTabColor.
/// Idempotent (called twice same result).
/// Dogfood: SetSheetTabColor then Get returns correct color.
/// Dogfood: Multiple sheets each have a color.
/// </summary>
public class FodsR368GetSheetTabColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetTabColor_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetTabColor(null!));
    }

    [Fact]
    public void GetSheetTabColor_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetTabColor("   "));
    }

    [Fact]
    public void GetSheetTabColor_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetTabColor("NoSuchSheet"));
    }

    [Fact]
    public void GetSheetTabColor_ValidSheet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Palette");
        string? color = doc.GetSheetTabColor("Palette");
        Assert.NotNull(color);
    }

    [Fact]
    public void GetSheetTabColor_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Colors");
        int before = doc.SheetCount;
        _ = doc.GetSheetTabColor("Colors");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetTabColor_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Tabs");
        doc.SetSheetTabColor("Tabs", "#FF5733");
        string? first = doc.GetSheetTabColor("Tabs");
        string? second = doc.GetSheetTabColor("Tabs");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetSheetTabColorThenGet_ReturnsColor()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Dashboard");
        doc.SetSheetTabColor("Dashboard", "#4A90D9");
        string? color = doc.GetSheetTabColor("Dashboard");
        Assert.NotNull(color);
        Assert.Equal("#4A90D9", color);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_EachHasColor()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Red");
        doc.AddSheet("Green");
        doc.AddSheet("Blue");
        doc.SetSheetTabColor("Red", "#FF0000");
        doc.SetSheetTabColor("Green", "#00FF00");
        doc.SetSheetTabColor("Blue", "#0000FF");
        Assert.NotNull(doc.GetSheetTabColor("Red"));
        Assert.NotNull(doc.GetSheetTabColor("Green"));
        Assert.NotNull(doc.GetSheetTabColor("Blue"));
    }
}
