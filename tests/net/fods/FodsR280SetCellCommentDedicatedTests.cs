// Tests for FodsDocument.SetCellComment dedicated coverage.
// Sprint: ff-sprint-s258-dotnet-deepening-20260630
// Ledger: PC-FODS-R280

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R280: Dedicated tests for FodsDocument.SetCellComment(sheetName, row, col, comment).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet name → throws exception.
/// Negative row → throws exception.
/// Negative col → throws exception.
/// Valid set → no exception.
/// GetCellComment returns the set comment.
/// SheetCount unchanged after set.
/// Set comment twice → second comment wins.
/// Dogfood: set comment and retrieve it.
/// Dogfood: two cells with different comments are independent.
/// </summary>
public class FodsR280SetCellCommentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellComment_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellComment(null!, 0, 0, "note"));
    }

    [Fact]
    public void SetCellComment_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellComment("   ", 0, 0, "note"));
    }

    [Fact]
    public void SetCellComment_NonexistentSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellComment("NoSheet", 0, 0, "note"));
    }

    [Fact]
    public void SetCellComment_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellComment("Sheet1", -1, 0, "note"));
    }

    [Fact]
    public void SetCellComment_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellComment("Sheet1", 0, -1, "note"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellComment_ValidArgs_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetCellComment("Sheet1", 0, 0, "my comment"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellComment_GetCellComment_ReturnsSetComment()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellComment("Sheet1", 0, 0, "review needed");
        string comment = doc.GetCellComment("Sheet1", 0, 0);
        Assert.Equal("review needed", comment);
    }

    [Fact]
    public void SetCellComment_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.SetCellComment("Sheet1", 0, 0, "note");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellComment_SetTwice_SecondCommentWins()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellComment("Sheet1", 0, 0, "first");
        doc.SetCellComment("Sheet1", 0, 0, "second");
        string comment = doc.GetCellComment("Sheet1", 0, 0);
        Assert.Equal("second", comment);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetAndRetrieveComment_RoundTrip()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Notes");
        doc.SetCellComment("Notes", 2, 3, "important annotation");
        string result = doc.GetCellComment("Notes", 2, 3);
        Assert.Equal("important annotation", result);
    }

    [Fact]
    public void DogfoodPipeline_TwoCellsWithComments_Independent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellComment("Sheet1", 0, 0, "alpha comment");
        doc.SetCellComment("Sheet1", 1, 1, "beta comment");
        Assert.Equal("alpha comment", doc.GetCellComment("Sheet1", 0, 0));
        Assert.Equal("beta comment", doc.GetCellComment("Sheet1", 1, 1));
    }
}
