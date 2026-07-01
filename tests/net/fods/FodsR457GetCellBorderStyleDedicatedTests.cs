// Tests for FodsDocument.GetCellBorderStyle dedicated coverage.
// Sprint: ff-sprint-s408-dotnet-deepening-20260701
// Ledger: PC-FODS-R457

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R457: Dedicated tests for FodsDocument.GetCellBorderStyle().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellBorderStyle.
/// Idempotent (called twice same result).
/// Is string type.
/// SetBorderStyle+Get round-trips.
/// Dogfood: default cell border style non-null.
/// Dogfood: multiple cells all non-null.
/// </summary>
public class FodsR457GetCellBorderStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellBorderStyle_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellBorderStyle(null!, 0, 0));
    }

    [Fact]
    public void GetCellBorderStyle_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellBorderStyle("   ", 0, 0));
    }

    [Fact]
    public void GetCellBorderStyle_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellBorderStyle("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellBorderStyle_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetCellBorderStyle(sheetName, -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellBorderStyle_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        string style = doc.GetCellBorderStyle(sheetName, 0, 0);
        Assert.NotNull(style);
    }

    [Fact]
    public void GetCellBorderStyle_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetCellBorderStyle(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellBorderStyle_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        string first = doc.GetCellBorderStyle(sheetName, 0, 0);
        string second = doc.GetCellBorderStyle(sheetName, 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellBorderStyle_IsString()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        object style = doc.GetCellBorderStyle(sheetName, 0, 0);
        Assert.IsType<string>(style);
    }

    [Fact]
    public void GetCellBorderStyle_AfterSet_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        doc.SetCellBorderStyle(sheetName, 0, 0, "solid");
        string style = doc.GetCellBorderStyle(sheetName, 0, 0);
        Assert.Equal("solid", style);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_BorderStyleNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        string style = doc.GetCellBorderStyle(sheetName, 0, 0);
        Assert.NotNull(style);
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
                Assert.NotNull(doc.GetCellBorderStyle(sheetName, row, col));
            }
        }
    }
}
