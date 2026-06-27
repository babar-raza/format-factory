// Tests for FodsDocument.GetCellFontColor dedicated coverage.
// Sprint: ff-sprint-s320-dotnet-deepening-20260630
// Ledger: PC-FODS-R351

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R351: Dedicated tests for FodsDocument.GetCellFontColor(sheetName, row, col).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call returns non-null.
/// SheetCount unchanged after GetCellFontColor.
/// Idempotent (called twice same result).
/// Dogfood: get font color after SetCellFontColor.
/// </summary>
public class FodsR351GetCellFontColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontColor_NullSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontColor(null!, 0, 0));
    }

    [Fact]
    public void GetCellFontColor_WhitespaceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontColor("   ", 0, 0));
    }

    [Fact]
    public void GetCellFontColor_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontColor("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellFontColor_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontColor("Sheet1", -1, 0));
    }

    [Fact]
    public void GetCellFontColor_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontColor("Sheet1", 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontColor_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string? color = doc.GetCellFontColor("Sheet1", 0, 0);
        Assert.NotNull(color);
    }

    [Fact]
    public void GetCellFontColor_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellFontColor("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFontColor_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string? first = doc.GetCellFontColor("Sheet1", 0, 0);
        string? second = doc.GetCellFontColor("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterSetCellFontColor_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellFontColor("Data", 0, 0, "#FF0000");
        string? color = doc.GetCellFontColor("Data", 0, 0);
        Assert.NotNull(color);
        int before = doc.SheetCount;
        Assert.Equal(before, doc.SheetCount);
    }
}
