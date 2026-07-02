// Tests for FodsDocument.GetCellMergeInfo dedicated coverage.
// Sprint: ff-sprint-s396-dotnet-deepening-20260701
// Ledger: PC-FODS-R445

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R445: Dedicated tests for FodsDocument.GetCellMergeInfo().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellMergeInfo.
/// Idempotent (called twice same result).
/// Dogfood: default cell non-null merge info.
/// Dogfood: multiple cells return non-null merge info.
/// </summary>
public class FodsR445GetCellMergeInfoDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellMergeInfo_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellMergeInfo(null!, 0, 0));
    }

    [Fact]
    public void GetCellMergeInfo_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellMergeInfo("   ", 0, 0));
    }

    [Fact]
    public void GetCellMergeInfo_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellMergeInfo("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellMergeInfo_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetCellMergeInfo(sheetName, -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellMergeInfo_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        var info = doc.GetCellMergeInfo(sheetName, 0, 0);
        Assert.NotNull(info);
    }

    [Fact]
    public void GetCellMergeInfo_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetCellMergeInfo(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellMergeInfo_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        var first = doc.GetCellMergeInfo(sheetName, 0, 0);
        var second = doc.GetCellMergeInfo(sheetName, 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_NonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        var info = doc.GetCellMergeInfo(sheetName, 0, 0);
        Assert.NotNull(info);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        Assert.NotNull(doc.GetCellMergeInfo(sheetName, 0, 0));
        Assert.NotNull(doc.GetCellMergeInfo(sheetName, 1, 0));
        Assert.NotNull(doc.GetCellMergeInfo(sheetName, 2, 0));
    }
}
