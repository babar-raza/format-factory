// Tests for FodsDocument.GetCellAlignment dedicated coverage.
// Sprint: ff-sprint-s317-dotnet-deepening-20260630
// Ledger: PC-FODS-R348

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R348: Dedicated tests for FodsDocument.GetCellAlignment(sheetName, row, col).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call returns non-null.
/// SheetCount unchanged after GetCellAlignment.
/// Idempotent (called twice same result).
/// Dogfood: get alignment after SetCellAlignment.
/// </summary>
public class FodsR348GetCellAlignmentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellAlignment_NullSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellAlignment(null!, 0, 0));
    }

    [Fact]
    public void GetCellAlignment_WhitespaceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellAlignment("   ", 0, 0));
    }

    [Fact]
    public void GetCellAlignment_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateEmpty();
        Assert.ThrowsAny<Exception>(() => doc.GetCellAlignment("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellAlignment_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellAlignment("Sheet1", -1, 0));
    }

    [Fact]
    public void GetCellAlignment_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellAlignment("Sheet1", 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellAlignment_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        string? alignment = doc.GetCellAlignment("Sheet1", 0, 0);
        Assert.NotNull(alignment);
    }

    [Fact]
    public void GetCellAlignment_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellAlignment("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellAlignment_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        string? first = doc.GetCellAlignment("Sheet1", 0, 0);
        string? second = doc.GetCellAlignment("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterSetCellAlignment_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");
        doc.SetCellAlignment("Data", 0, 0, "center");
        string? alignment = doc.GetCellAlignment("Data", 0, 0);
        Assert.NotNull(alignment);
        int before = doc.SheetCount;
        Assert.Equal(before, doc.SheetCount);
    }
}
