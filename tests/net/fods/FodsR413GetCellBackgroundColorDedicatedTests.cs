// Tests for FodsDocument.GetCellBackgroundColor dedicated coverage.
// Sprint: ff-sprint-s371-dotnet-deepening-20260630
// Ledger: PC-FODS-R413

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R413: Dedicated tests for FodsDocument.GetCellBackgroundColor().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellBackgroundColor.
/// Idempotent (called twice same result).
/// Dogfood: SetCellBackgroundColor "#FFFF00" then Get returns "#FFFF00".
/// Dogfood: multiple cells each returns non-null color.
/// </summary>
public class FodsR413GetCellBackgroundColorDedicatedTests
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
        Assert.ThrowsAny<Exception>(() => doc.GetCellBackgroundColor("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellBackgroundColor_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Colors");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBackgroundColor("Colors", -1, 0));
    }

    [Fact]
    public void GetCellBackgroundColor_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Data");
        string? color = doc.GetCellBackgroundColor("Data", 0, 0);
        Assert.NotNull(color);
    }

    [Fact]
    public void GetCellBackgroundColor_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Style");
        int before = doc.SheetCount;
        _ = doc.GetCellBackgroundColor("Style", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellBackgroundColor_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Stable");
        string? first = doc.GetCellBackgroundColor("Stable", 0, 0);
        string? second = doc.GetCellBackgroundColor("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetYellowBackground_ReturnsExpected()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Highlights");
        doc.SetCellBackgroundColor("Highlights", 0, 0, "#FFFF00");
        string? color = doc.GetCellBackgroundColor("Highlights", 0, 0);
        Assert.NotNull(color);
        Assert.Equal("#FFFF00", color);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_EachNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Traffic");
        doc.SetCellBackgroundColor("Traffic", 0, 0, "#FF0000");
        doc.SetCellBackgroundColor("Traffic", 1, 0, "#FFFF00");
        doc.SetCellBackgroundColor("Traffic", 2, 0, "#00FF00");
        Assert.NotNull(doc.GetCellBackgroundColor("Traffic", 0, 0));
        Assert.NotNull(doc.GetCellBackgroundColor("Traffic", 1, 0));
        Assert.NotNull(doc.GetCellBackgroundColor("Traffic", 2, 0));
    }
}
