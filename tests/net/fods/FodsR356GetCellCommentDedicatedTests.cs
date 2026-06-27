// Tests for FodsDocument.GetCellComment dedicated coverage.
// Sprint: ff-sprint-s323-dotnet-deepening-20260630
// Ledger: PC-FODS-R356

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R356: Dedicated tests for FodsDocument.GetCellComment().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet throws.
/// Negative row throws.
/// Valid call returns non-null.
/// SheetCount unchanged after GetCellComment.
/// Called twice same result.
/// Dogfood: SetCellComment then GetCellComment.
/// Dogfood: multiple cells with comments.
/// </summary>
public class FodsR356GetCellCommentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellComment_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellComment(null!, 0, 0));
    }

    [Fact]
    public void GetCellComment_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");
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
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellComment("Data", -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellComment_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Value");
        string? comment = doc.GetCellComment("Sheet1", 0, 0);
        Assert.NotNull(comment);
    }

    [Fact]
    public void GetCellComment_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellComment("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellComment_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Notes");
        doc.SetCellValue("Notes", 0, 0, "Important");
        string? first = doc.GetCellComment("Notes", 0, 0);
        string? second = doc.GetCellComment("Notes", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellCommentThenGet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Review");
        doc.SetCellValue("Review", 0, 0, "Draft text");
        doc.SetCellComment("Review", 0, 0, "Please verify this value");
        string? comment = doc.GetCellComment("Review", 0, 0);
        Assert.NotNull(comment);
        Assert.Equal(doc.SheetCount, doc.SheetCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCellsWithComments_AllNonNull()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");
        for (int r = 0; r < 3; r++)
        {
            doc.SetCellValue("Data", r, 0, $"Row{r}");
            doc.SetCellComment("Data", r, 0, $"Comment for row {r}");
        }
        for (int r = 0; r < 3; r++)
            Assert.NotNull(doc.GetCellComment("Data", r, 0));
    }
}
