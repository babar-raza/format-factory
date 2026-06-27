// Tests for FodsDocument.GetCellFont dedicated coverage.
// Sprint: ff-sprint-s314-dotnet-deepening-20260630
// Ledger: PC-FODS-R345

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R345: Dedicated tests for FodsDocument.GetCellFont(sheetName, row, col).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call returns non-null.
/// SheetCount unchanged after GetCellFont.
/// Idempotent (called twice same result).
/// Dogfood: get font after SetCellFont.
/// </summary>
public class FodsR345GetCellFontDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFont_NullSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFont(null!, 0, 0));
    }

    [Fact]
    public void GetCellFont_WhitespaceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFont("   ", 0, 0));
    }

    [Fact]
    public void GetCellFont_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFont("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellFont_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFont("Sheet1", -1, 0));
    }

    [Fact]
    public void GetCellFont_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFont("Sheet1", 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFont_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string? font = doc.GetCellFont("Sheet1", 0, 0);
        Assert.NotNull(font);
    }

    [Fact]
    public void GetCellFont_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellFont("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFont_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string? first = doc.GetCellFont("Sheet1", 0, 0);
        string? second = doc.GetCellFont("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterSetCellFont_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellFont("Data", 0, 0, "Arial");
        string? font = doc.GetCellFont("Data", 0, 0);
        Assert.NotNull(font);
        int before = doc.SheetCount;
        Assert.Equal(before, doc.SheetCount);
    }
}
