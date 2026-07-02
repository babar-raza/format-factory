// Tests for FodsDocument.GetCellBackgroundColor dedicated coverage.
// Sprint: ff-sprint-s412-dotnet-deepening-20260701
// Ledger: PC-FODS-R461

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R461: Dedicated tests for FodsDocument.GetCellBackgroundColor().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellBackgroundColor.
/// Idempotent (called twice same result).
/// Is string type.
/// SetBackgroundColor+GetCellBackgroundColor round-trips.
/// Dogfood: default cell background color non-null.
/// Dogfood: multiple cells all non-null.
/// </summary>
public class FodsR461GetCellBackgroundColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellBackgroundColor_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBackgroundColor(null!, 0, 0));
    }

    [Fact]
    public void GetCellBackgroundColor_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBackgroundColor("   ", 0, 0));
    }

    [Fact]
    public void GetCellBackgroundColor_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBackgroundColor("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellBackgroundColor_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetCellBackgroundColor(sheetName, -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellBackgroundColor_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        string color = doc.GetCellBackgroundColor(sheetName, 0, 0);
        Assert.NotNull(color);
    }

    [Fact]
    public void GetCellBackgroundColor_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetCellBackgroundColor(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellBackgroundColor_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        string first = doc.GetCellBackgroundColor(sheetName, 0, 0);
        string second = doc.GetCellBackgroundColor(sheetName, 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellBackgroundColor_IsString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        object color = doc.GetCellBackgroundColor(sheetName, 0, 0);
        Assert.IsType<string>(color);
    }

    [Fact]
    public void GetCellBackgroundColor_AfterSet_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetCellBackgroundColor(sheetName, 0, 0, "#FFFFFF");
        string color = doc.GetCellBackgroundColor(sheetName, 0, 0);
        Assert.Equal("#FFFFFF", color);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_BackgroundColorNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        string color = doc.GetCellBackgroundColor(sheetName, 0, 0);
        Assert.NotNull(color);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        for (int row = 0; row < 3; row++)
        {
            for (int col = 0; col < 3; col++)
            {
                Assert.NotNull(doc.GetCellBackgroundColor(sheetName, row, col));
            }
        }
    }
}
