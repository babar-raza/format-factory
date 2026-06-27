// Tests for FodsDocument.GetCellFontName dedicated coverage.
// Sprint: ff-sprint-s339-dotnet-deepening-20260630
// Ledger: PC-FODS-R377

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R377: Dedicated tests for FodsDocument.GetCellFontName().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellFontName.
/// Idempotent (called twice same result).
/// Dogfood: SetCellFontName then Get returns correct name.
/// Dogfood: Multiple cells with different font names all non-null.
/// </summary>
public class FodsR377GetCellFontNameDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontName_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontName(null!, 0, 0));
    }

    [Fact]
    public void GetCellFontName_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontName("   ", 0, 0));
    }

    [Fact]
    public void GetCellFontName_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontName("Nonexistent", 0, 0));
    }

    [Fact]
    public void GetCellFontName_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Fonts");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontName("Fonts", -1, 0));
    }

    [Fact]
    public void GetCellFontName_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Text");
        string? fontName = doc.GetCellFontName("Text", 0, 0);
        Assert.NotNull(fontName);
    }

    [Fact]
    public void GetCellFontName_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("FontSheet");
        int before = doc.SheetCount;
        _ = doc.GetCellFontName("FontSheet", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFontName_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        doc.SetCellFontName("Stable", 0, 0, "Arial");
        string? first = doc.GetCellFontName("Stable", 0, 0);
        string? second = doc.GetCellFontName("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellFontNameThenGet_ReturnsName()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellFontName("Report", 0, 0, "Calibri");
        string? fontName = doc.GetCellFontName("Report", 0, 0);
        Assert.NotNull(fontName);
        Assert.Equal("Calibri", fontName);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCellsDifferentFonts_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Design");
        doc.SetCellFontName("Design", 0, 0, "Arial");
        doc.SetCellFontName("Design", 0, 1, "Times New Roman");
        doc.SetCellFontName("Design", 0, 2, "Courier New");
        Assert.NotNull(doc.GetCellFontName("Design", 0, 0));
        Assert.NotNull(doc.GetCellFontName("Design", 0, 1));
        Assert.NotNull(doc.GetCellFontName("Design", 0, 2));
    }
}
