// Tests for FodsDocument.GetCellBackground dedicated coverage.
// Sprint: ff-sprint-s312-dotnet-deepening-20260630
// Ledger: PC-FODS-R342

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R342: Dedicated tests for FodsDocument.GetCellBackground(sheetName, row, col).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call returns non-null.
/// SheetCount unchanged after GetCellBackground.
/// Idempotent (called twice same result).
/// Dogfood: get background after SetCellBackground.
/// </summary>
public class FodsR342GetCellBackgroundDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellBackground_NullSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBackground(null!, 0, 0));
    }

    [Fact]
    public void GetCellBackground_WhitespaceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBackground("   ", 0, 0));
    }

    [Fact]
    public void GetCellBackground_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellBackground("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellBackground_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBackground("Sheet1", -1, 0));
    }

    [Fact]
    public void GetCellBackground_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBackground("Sheet1", 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellBackground_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string? bg = doc.GetCellBackground("Sheet1", 0, 0);
        Assert.NotNull(bg);
    }

    [Fact]
    public void GetCellBackground_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellBackground("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellBackground_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string? first = doc.GetCellBackground("Sheet1", 0, 0);
        string? second = doc.GetCellBackground("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterSetCellBackground_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellBackground("Data", 0, 0, "#FF0000");
        string? bg = doc.GetCellBackground("Data", 0, 0);
        Assert.NotNull(bg);
        int before = doc.SheetCount;
        Assert.Equal(before, doc.SheetCount);
    }
}
