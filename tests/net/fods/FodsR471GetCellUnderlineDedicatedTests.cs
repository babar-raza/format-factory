// Tests for FodsDocument.GetCellUnderline dedicated coverage.
// Sprint: ff-sprint-s422-dotnet-deepening-20260701
// Ledger: PC-FODS-R471

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R471: Dedicated tests for FodsDocument.GetCellUnderline().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null string.
/// SheetCount unchanged after GetCellUnderline.
/// Idempotent (called twice same result).
/// Return type is string.
/// SetCellUnderline + GetCellUnderline round-trips.
/// Dogfood: default cell underline non-null.
/// Dogfood: multiple cells have non-null underline.
/// </summary>
public class FodsR471GetCellUnderlineDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellUnderline_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellUnderline(null!, 0, 0));
    }

    [Fact]
    public void GetCellUnderline_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellUnderline("   ", 0, 0));
    }

    [Fact]
    public void GetCellUnderline_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellUnderline("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellUnderline_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellUnderline("Sheet1", -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellUnderline_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string underline = doc.GetCellUnderline("Sheet1", 0, 0);
        Assert.NotNull(underline);
    }

    [Fact]
    public void GetCellUnderline_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellUnderline("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellUnderline_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string first = doc.GetCellUnderline("Sheet1", 0, 0);
        string second = doc.GetCellUnderline("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellUnderline_IsString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        object result = doc.GetCellUnderline("Sheet1", 0, 0);
        Assert.IsType<string>(result);
    }

    [Fact]
    public void GetCellUnderline_RoundTrip()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellUnderline("Data", 0, 0, "single");
        string underline = doc.GetCellUnderline("Data", 0, 0);
        Assert.Equal("single", underline);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_UnderlineNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        string underline = doc.GetCellUnderline("Report", 0, 0);
        Assert.NotNull(underline);
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
                Assert.NotNull(doc.GetCellUnderline("Data", row, col));
            }
        }
    }
}
