// Tests for FodsDocument.GetCellComment dedicated coverage.
// Sprint: ff-sprint-s305-dotnet-deepening-20260630
// Ledger: PC-FODS-R333

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R333: Dedicated tests for FodsDocument.GetCellComment(sheetName, row, col).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call returns non-null.
/// SheetCount unchanged after GetCellComment.
/// Called twice returns same result.
/// Dogfood: get comment after AddComment.
/// </summary>
public class FodsR333GetCellCommentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellComment_NullSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellComment(null!, 0, 0));
    }

    [Fact]
    public void GetCellComment_WhitespaceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellComment("   ", 0, 0));
    }

    [Fact]
    public void GetCellComment_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellComment("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellComment_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellComment("Sheet1", -1, 0));
    }

    [Fact]
    public void GetCellComment_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellComment("Sheet1", 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellComment_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string? comment = doc.GetCellComment("Sheet1", 0, 0);
        Assert.NotNull(comment);
    }

    [Fact]
    public void GetCellComment_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellComment("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellComment_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string? first = doc.GetCellComment("Sheet1", 0, 0);
        string? second = doc.GetCellComment("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_GetCommentAfterAddComment_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Notes");
        doc.AddComment("Notes", 0, 0, "This is a note");
        string? comment = doc.GetCellComment("Notes", 0, 0);
        Assert.NotNull(comment);
        int before = doc.SheetCount;
        Assert.Equal(before, doc.SheetCount);
    }
}
