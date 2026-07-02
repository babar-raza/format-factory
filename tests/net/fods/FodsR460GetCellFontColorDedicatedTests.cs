// Tests for FodsDocument.GetCellFontColor dedicated coverage.
// Sprint: ff-sprint-s411-dotnet-deepening-20260701
// Ledger: PC-FODS-R460

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R460: Dedicated tests for FodsDocument.GetCellFontColor().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellFontColor.
/// Idempotent (called twice same result).
/// Is string type.
/// SetFontColor+GetCellFontColor round-trips.
/// Dogfood: default cell font color non-null.
/// Dogfood: multiple cells all non-null.
/// </summary>
public class FodsR460GetCellFontColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontColor_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontColor(null!, 0, 0));
    }

    [Fact]
    public void GetCellFontColor_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontColor("   ", 0, 0));
    }

    [Fact]
    public void GetCellFontColor_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontColor("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellFontColor_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontColor(sheetName, -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontColor_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        string color = doc.GetCellFontColor(sheetName, 0, 0);
        Assert.NotNull(color);
    }

    [Fact]
    public void GetCellFontColor_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetCellFontColor(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFontColor_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        string first = doc.GetCellFontColor(sheetName, 0, 0);
        string second = doc.GetCellFontColor(sheetName, 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellFontColor_IsString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        object color = doc.GetCellFontColor(sheetName, 0, 0);
        Assert.IsType<string>(color);
    }

    [Fact]
    public void GetCellFontColor_AfterSet_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetCellFontColor(sheetName, 0, 0, "#FF0000");
        string color = doc.GetCellFontColor(sheetName, 0, 0);
        Assert.Equal("#FF0000", color);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_FontColorNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        string color = doc.GetCellFontColor(sheetName, 0, 0);
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
                Assert.NotNull(doc.GetCellFontColor(sheetName, row, col));
            }
        }
    }
}
