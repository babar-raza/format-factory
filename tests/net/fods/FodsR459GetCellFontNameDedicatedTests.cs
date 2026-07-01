// Tests for FodsDocument.GetCellFontName dedicated coverage.
// Sprint: ff-sprint-s410-dotnet-deepening-20260701
// Ledger: PC-FODS-R459

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R459: Dedicated tests for FodsDocument.GetCellFontName().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellFontName.
/// Idempotent (called twice same result).
/// Is string type.
/// SetFontName+GetCellFontName round-trips.
/// Dogfood: default cell font name non-null.
/// Dogfood: multiple cells all return non-null.
/// </summary>
public class FodsR459GetCellFontNameDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
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
    public void GetCellFontName_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontName("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellFontName_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontName(sheetName, -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontName_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        string fontName = doc.GetCellFontName(sheetName, 0, 0);
        Assert.NotNull(fontName);
    }

    [Fact]
    public void GetCellFontName_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetCellFontName(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFontName_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        string first = doc.GetCellFontName(sheetName, 0, 0);
        string second = doc.GetCellFontName(sheetName, 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellFontName_IsString()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        object fontName = doc.GetCellFontName(sheetName, 0, 0);
        Assert.IsType<string>(fontName);
    }

    [Fact]
    public void GetCellFontName_AfterSet_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        doc.SetCellFontName(sheetName, 0, 0, "Arial");
        string fontName = doc.GetCellFontName(sheetName, 0, 0);
        Assert.Equal("Arial", fontName);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_FontNameNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        string fontName = doc.GetCellFontName(sheetName, 0, 0);
        Assert.NotNull(fontName);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        for (int row = 0; row < 3; row++)
        {
            for (int col = 0; col < 3; col++)
            {
                Assert.NotNull(doc.GetCellFontName(sheetName, row, col));
            }
        }
    }
}
