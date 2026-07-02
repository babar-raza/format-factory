// Tests for FodsDocument.GetCellShrinkToFit dedicated coverage.
// Sprint: ff-sprint-s401-dotnet-deepening-20260701
// Ledger: PC-FODS-R450

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R450: Dedicated tests for FodsDocument.GetCellShrinkToFit().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns bool.
/// SheetCount unchanged after GetCellShrinkToFit.
/// Idempotent (called twice same result).
/// SetShrinkToFit(true)+Get returns true.
/// SetShrinkToFit(false)+Get returns false.
/// Dogfood: default cell shrink-to-fit is bool.
/// Dogfood: multiple cells all return bool.
/// </summary>
public class FodsR450GetCellShrinkToFitDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellShrinkToFit_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellShrinkToFit(null!, 0, 0));
    }

    [Fact]
    public void GetCellShrinkToFit_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellShrinkToFit("   ", 0, 0));
    }

    [Fact]
    public void GetCellShrinkToFit_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellShrinkToFit("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellShrinkToFit_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetCellShrinkToFit(sheetName, -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellShrinkToFit_ValidCell_ReturnsBool()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        bool result = doc.GetCellShrinkToFit(sheetName, 0, 0);
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void GetCellShrinkToFit_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetCellShrinkToFit(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellShrinkToFit_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        bool first = doc.GetCellShrinkToFit(sheetName, 0, 0);
        bool second = doc.GetCellShrinkToFit(sheetName, 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellShrinkToFit_SetTrue_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetCellShrinkToFit(sheetName, 0, 0, true);
        Assert.True(doc.GetCellShrinkToFit(sheetName, 0, 0));
    }

    [Fact]
    public void GetCellShrinkToFit_SetFalse_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetCellShrinkToFit(sheetName, 0, 0, false);
        Assert.False(doc.GetCellShrinkToFit(sheetName, 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_IsBool()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        object result = doc.GetCellShrinkToFit(sheetName, 0, 0);
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllBool()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        for (int row = 0; row < 3; row++)
        {
            for (int col = 0; col < 3; col++)
            {
                object result = doc.GetCellShrinkToFit(sheetName, row, col);
                Assert.IsType<bool>(result);
            }
        }
    }
}
