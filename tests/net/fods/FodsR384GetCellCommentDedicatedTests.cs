// Tests for FodsDocument.GetCellComment dedicated coverage.
// Sprint: ff-sprint-s346-dotnet-deepening-20260630
// Ledger: PC-FODS-R384

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R384: Dedicated tests for FodsDocument.GetCellComment().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellComment.
/// Idempotent (called twice same result).
/// Dogfood: SetCellComment then GetCellComment returns expected.
/// Dogfood: multiple cells each with different comments.
/// </summary>
public class FodsR384GetCellCommentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellComment_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellComment(null!, 0, 0));
    }

    [Fact]
    public void GetCellComment_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellComment("   ", 0, 0));
    }

    [Fact]
    public void GetCellComment_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellComment("Missing", 0, 0));
    }

    [Fact]
    public void GetCellComment_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Notes");
        Assert.ThrowsAny<Exception>(() => doc.GetCellComment("Notes", -1, 0));
    }

    [Fact]
    public void GetCellComment_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        string? comment = doc.GetCellComment("Data", 0, 0);
        Assert.NotNull(comment);
    }

    [Fact]
    public void GetCellComment_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Comments");
        int before = doc.SheetCount;
        _ = doc.GetCellComment("Comments", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellComment_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string? first = doc.GetCellComment("Stable", 0, 0);
        string? second = doc.GetCellComment("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterSetCellComment_ReturnsExpected()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Annotations");
        doc.SetCellComment("Annotations", 0, 0, "Please review this value");
        string? comment = doc.GetCellComment("Annotations", 0, 0);
        Assert.NotNull(comment);
        Assert.Equal("Please review this value", comment);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_DifferentComments()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Review");
        doc.SetCellComment("Review", 0, 0, "Header comment");
        doc.SetCellComment("Review", 1, 0, "Data comment");
        doc.SetCellComment("Review", 2, 0, "Total comment");
        string? c0 = doc.GetCellComment("Review", 0, 0);
        string? c1 = doc.GetCellComment("Review", 1, 0);
        string? c2 = doc.GetCellComment("Review", 2, 0);
        Assert.NotNull(c0);
        Assert.NotNull(c1);
        Assert.NotNull(c2);
    }
}
