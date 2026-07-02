// Tests for FodsDocument.GetCellFontSize dedicated coverage.
// Sprint: ff-sprint-s409-dotnet-deepening-20260701
// Ledger: PC-FODS-R458

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R458: Dedicated tests for FodsDocument.GetCellFontSize().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns positive value.
/// SheetCount unchanged after GetCellFontSize.
/// Idempotent (called twice same result).
/// Is int (or double) type.
/// SetFontSize+GetCellFontSize round-trips.
/// Dogfood: default cell font size positive.
/// Dogfood: multiple cells all positive.
/// </summary>
public class FodsR458GetCellFontSizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontSize_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontSize(null!, 0, 0));
    }

    [Fact]
    public void GetCellFontSize_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontSize("   ", 0, 0));
    }

    [Fact]
    public void GetCellFontSize_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontSize("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellFontSize_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontSize(sheetName, -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontSize_ValidCell_ReturnsPositive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        double size = doc.GetCellFontSize(sheetName, 0, 0);
        Assert.True(size > 0);
    }

    [Fact]
    public void GetCellFontSize_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetCellFontSize(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFontSize_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        double first = doc.GetCellFontSize(sheetName, 0, 0);
        double second = doc.GetCellFontSize(sheetName, 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellFontSize_AfterSet_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetCellFontSize(sheetName, 0, 0, 14.0);
        double size = doc.GetCellFontSize(sheetName, 0, 0);
        Assert.Equal(14.0, size, precision: 5);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_FontSizePositive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        double size = doc.GetCellFontSize(sheetName, 0, 0);
        Assert.True(size > 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllPositive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        for (int row = 0; row < 3; row++)
        {
            for (int col = 0; col < 3; col++)
            {
                Assert.True(doc.GetCellFontSize(sheetName, row, col) > 0);
            }
        }
    }
}
