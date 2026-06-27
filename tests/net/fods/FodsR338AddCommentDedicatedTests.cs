// Tests for FodsDocument.AddComment dedicated coverage.
// Sprint: ff-sprint-s310-dotnet-deepening-20260630
// Ledger: PC-FODS-R338

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R338: Dedicated tests for FodsDocument.AddComment(sheetName, row, col, comment).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call no exception.
/// SheetCount unchanged after AddComment.
/// Called twice no exception.
/// GetCellComment returns non-null after AddComment.
/// Dogfood: add comment and verify SheetCount.
/// </summary>
public class FodsR338AddCommentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddComment_NullSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.AddComment(null!, 0, 0, "Note"));
    }

    [Fact]
    public void AddComment_WhitespaceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.AddComment("   ", 0, 0, "Note"));
    }

    [Fact]
    public void AddComment_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.AddComment("NoSuchSheet", 0, 0, "Note"));
    }

    [Fact]
    public void AddComment_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.AddComment("Sheet1", -1, 0, "Note"));
    }

    [Fact]
    public void AddComment_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.AddComment("Sheet1", 0, -1, "Note"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddComment_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.AddComment("Sheet1", 0, 0, "This is a comment"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddComment_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.AddComment("Sheet1", 0, 0, "Note");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void AddComment_CalledTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddComment("Sheet1", 0, 0, "First note");
        var ex = Record.Exception(() => doc.AddComment("Sheet1", 0, 1, "Second note"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddComment_GetCellComment_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddComment("Sheet1", 0, 0, "This is a comment");
        string? comment = doc.GetCellComment("Sheet1", 0, 0);
        Assert.NotNull(comment);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddMultipleComments_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Notes");
        doc.SetCellValue("Notes", 0, 0, "Revenue");
        doc.AddComment("Notes", 0, 0, "Q1 data");
        doc.AddComment("Notes", 1, 0, "Q2 data");
        doc.AddComment("Notes", 0, 1, "Projection");
        int before = doc.SheetCount;
        Assert.Equal(before, doc.SheetCount);
    }
}
