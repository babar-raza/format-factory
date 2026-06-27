// Tests for FodsDocument.GetCellFontName dedicated coverage.
// Sprint: ff-sprint-s361-dotnet-deepening-20260630
// Ledger: PC-FODS-R403

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R403: Dedicated tests for FodsDocument.GetCellFontName().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellFontName.
/// Idempotent (called twice same result).
/// Dogfood: SetCellFontName then GetCellFontName returns expected.
/// Dogfood: multiple cells each returns non-null font name.
/// </summary>
public class FodsR403GetCellFontNameDedicatedTests
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
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontName("Missing", 0, 0));
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
        doc.AddSheet("Data");
        string? fontName = doc.GetCellFontName("Data", 0, 0);
        Assert.NotNull(fontName);
    }

    [Fact]
    public void GetCellFontName_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Style");
        int before = doc.SheetCount;
        _ = doc.GetCellFontName("Style", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFontName_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string? first = doc.GetCellFontName("Stable", 0, 0);
        string? second = doc.GetCellFontName("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterSetCellFontName_ReturnsExpected()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellFontName("Report", 0, 0, "Arial");
        string? fontName = doc.GetCellFontName("Report", 0, 0);
        Assert.NotNull(fontName);
        Assert.Equal("Arial", fontName);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_EachNonNullFontName()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Typography");
        doc.SetCellFontName("Typography", 0, 0, "Arial");
        doc.SetCellFontName("Typography", 1, 0, "Times New Roman");
        doc.SetCellFontName("Typography", 2, 0, "Courier New");
        Assert.NotNull(doc.GetCellFontName("Typography", 0, 0));
        Assert.NotNull(doc.GetCellFontName("Typography", 1, 0));
        Assert.NotNull(doc.GetCellFontName("Typography", 2, 0));
    }
}
