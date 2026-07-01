// Tests for FodsDocument.GetCellComment dedicated coverage.
// Sprint: ff-sprint-s414-dotnet-deepening-20260701
// Ledger: PC-FODS-R463

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R463: Dedicated tests for FodsDocument.GetCellComment().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null string.
/// SheetCount unchanged after GetCellComment.
/// Idempotent (called twice same result).
/// Return type is string.
/// SetCellComment + GetCellComment round-trips.
/// Dogfood: default cell comment non-null.
/// Dogfood: multiple cells have non-null comment.
/// </summary>
public class FodsR463GetCellCommentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
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
    public void GetCellComment_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellComment("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellComment_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellComment("Sheet1", -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellComment_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string comment = doc.GetCellComment("Sheet1", 0, 0);
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
    public void GetCellComment_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string first = doc.GetCellComment("Sheet1", 0, 0);
        string second = doc.GetCellComment("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellComment_IsString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        object result = doc.GetCellComment("Sheet1", 0, 0);
        Assert.IsType<string>(result);
    }

    [Fact]
    public void GetCellComment_RoundTrip()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Notes");
        doc.SetCellComment("Notes", 0, 0, "Important note here");
        string comment = doc.GetCellComment("Notes", 0, 0);
        Assert.Equal("Important note here", comment);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_CommentNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        string comment = doc.GetCellComment("Report", 0, 0);
        Assert.NotNull(comment);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        for (int row = 0; row < 3; row++)
        {
            for (int col = 0; col < 3; col++)
            {
                string comment = doc.GetCellComment("Data", row, col);
                Assert.NotNull(comment);
            }
        }
    }
}
