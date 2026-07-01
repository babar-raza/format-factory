// Tests for FodsDocument.GetCellFontStyle dedicated coverage.
// Sprint: ff-sprint-s423-dotnet-deepening-20260701
// Ledger: PC-FODS-R472

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R472: Dedicated tests for FodsDocument.GetCellFontStyle().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null string.
/// SheetCount unchanged after GetCellFontStyle.
/// Idempotent (called twice same result).
/// Return type is string.
/// SetCellFontStyle + GetCellFontStyle round-trips.
/// Dogfood: default cell font style non-null.
/// Dogfood: multiple cells have non-null font style.
/// </summary>
public class FodsR472GetCellFontStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontStyle_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontStyle(null!, 0, 0));
    }

    [Fact]
    public void GetCellFontStyle_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontStyle("   ", 0, 0));
    }

    [Fact]
    public void GetCellFontStyle_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontStyle("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellFontStyle_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontStyle("Sheet1", -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontStyle_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string style = doc.GetCellFontStyle("Sheet1", 0, 0);
        Assert.NotNull(style);
    }

    [Fact]
    public void GetCellFontStyle_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellFontStyle("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFontStyle_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string first = doc.GetCellFontStyle("Sheet1", 0, 0);
        string second = doc.GetCellFontStyle("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellFontStyle_IsString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        object result = doc.GetCellFontStyle("Sheet1", 0, 0);
        Assert.IsType<string>(result);
    }

    [Fact]
    public void GetCellFontStyle_RoundTrip()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellFontStyle("Data", 0, 0, "italic");
        string style = doc.GetCellFontStyle("Data", 0, 0);
        Assert.Equal("italic", style);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_FontStyleNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        string style = doc.GetCellFontStyle("Report", 0, 0);
        Assert.NotNull(style);
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
                Assert.NotNull(doc.GetCellFontStyle("Data", row, col));
            }
        }
    }
}
