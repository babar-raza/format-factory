// Tests for FodsDocument.GetCellComment dedicated coverage.
// Sprint: ff-sprint-s372-dotnet-deepening-20260630
// Ledger: PC-FODS-R414

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R414: Dedicated tests for FodsDocument.GetCellComment().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellComment.
/// Idempotent (called twice same result).
/// Dogfood: SetComment then Get returns matching value.
/// Dogfood: multiple cells each has distinct comment.
/// </summary>
public class FodsR414GetCellCommentDedicatedTests
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
    public void GetCellComment_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellComment("Data", -1, 0));
    }

    [Fact]
    public void GetCellComment_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Notes");
        string comment = doc.GetCellComment("Notes", 0, 0);
        Assert.NotNull(comment);
    }

    [Fact]
    public void GetCellComment_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        _ = doc.GetCellComment("Data", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellComment_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string first = doc.GetCellComment("Stable", 0, 0);
        string second = doc.GetCellComment("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCommentThenGet_ReturnsComment()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sales");
        doc.SetCellComment("Sales", 0, 0, "Review this value");
        string comment = doc.GetCellComment("Sales", 0, 0);
        Assert.Equal("Review this value", comment);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_DistinctComments()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Audit");
        doc.SetCellComment("Audit", 0, 0, "First note");
        doc.SetCellComment("Audit", 1, 0, "Second note");
        doc.SetCellComment("Audit", 2, 0, "Third note");
        Assert.Equal("First note", doc.GetCellComment("Audit", 0, 0));
        Assert.Equal("Second note", doc.GetCellComment("Audit", 1, 0));
        Assert.Equal("Third note", doc.GetCellComment("Audit", 2, 0));
    }
}
