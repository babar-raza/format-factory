// Tests for FodsDocument.GetSheetTabColor dedicated coverage.
// Sprint: ff-sprint-s370-dotnet-deepening-20260630
// Ledger: PC-FODS-R412

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R412: Dedicated tests for FodsDocument.GetSheetTabColor().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// New sheet returns non-null.
/// SheetCount unchanged after GetSheetTabColor.
/// Idempotent (called twice same result).
/// Dogfood: SetSheetTabColor "#FF0000" then GetSheetTabColor returns "#FF0000".
/// Dogfood: multiple sheets each returns non-null tab color.
/// </summary>
public class FodsR412GetSheetTabColorDedicatedTests
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
        Assert.ThrowsAny<Exception>(() => doc.GetSheetTabColor("NoSheet"));
    }

    [Fact]
    public void GetSheetTabColor_NewSheet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Colorful");
        string? color = doc.GetSheetTabColor("Colorful");
        Assert.NotNull(color);
    }

    [Fact]
    public void GetSheetTabColor_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Track");
        int before = doc.SheetCount;
        _ = doc.GetSheetTabColor("Track");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetTabColor_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string? first = doc.GetSheetTabColor("Stable");
        string? second = doc.GetSheetTabColor("Stable");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetTabColorRed_ReturnsExpected()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alerts");
        doc.SetSheetTabColor("Alerts", "#FF0000");
        string? color = doc.GetSheetTabColor("Alerts");
        Assert.NotNull(color);
        Assert.Equal("#FF0000", color);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_EachNonNull()
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
