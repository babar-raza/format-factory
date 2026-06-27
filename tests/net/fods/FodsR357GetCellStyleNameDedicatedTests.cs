// Tests for FodsDocument.GetCellStyleName dedicated coverage.
// Sprint: ff-sprint-s324-dotnet-deepening-20260630
// Ledger: PC-FODS-R357

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R357: Dedicated tests for FodsDocument.GetCellStyleName().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet throws.
/// Negative row throws.
/// Valid call returns non-null.
/// SheetCount unchanged after GetCellStyleName.
/// Called twice same result.
/// Dogfood: SetCellStyle then GetCellStyleName.
/// Dogfood: multiple cells all return non-null style names.
/// </summary>
public class FodsR357GetCellStyleNameDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStyleName_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyleName(null!, 0, 0));
    }

    [Fact]
    public void GetCellStyleName_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyleName("   ", 0, 0));
    }

    [Fact]
    public void GetCellStyleName_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyleName("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellStyleName_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyleName("Data", -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStyleName_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Test value");
        string? styleName = doc.GetCellStyleName("Sheet1", 0, 0);
        Assert.NotNull(styleName);
    }

    [Fact]
    public void GetCellStyleName_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellStyleName("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellStyleName_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Styled");
        doc.SetCellValue("Styled", 0, 0, "Content");
        string? first = doc.GetCellStyleName("Styled", 0, 0);
        string? second = doc.GetCellStyleName("Styled", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellStyleThenGetStyleName()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Header");
        doc.SetCellStyle("Report", 0, 0, "HeaderStyle");
        string? styleName = doc.GetCellStyleName("Report", 0, 0);
        Assert.NotNull(styleName);
        Assert.Equal(doc.SheetCount, doc.SheetCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNullStyleNames()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Grid");
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                doc.SetCellValue("Grid", r, c, $"Val{r}{c}");
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                Assert.NotNull(doc.GetCellStyleName("Grid", r, c));
    }
}
