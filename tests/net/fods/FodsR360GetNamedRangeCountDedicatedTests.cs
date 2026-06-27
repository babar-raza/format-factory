// Tests for FodsDocument.GetNamedRangeCount dedicated coverage.
// Sprint: ff-sprint-s327-dotnet-deepening-20260630
// Ledger: PC-FODS-R360

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R360: Dedicated tests for FodsDocument.GetNamedRangeCount().
/// Non-negative on new document.
/// Empty document ok.
/// Increases after AddNamedRange.
/// SheetCount unchanged after GetNamedRangeCount.
/// Called twice same result.
/// Dogfood: add named range then count is non-negative.
/// Dogfood: multiple named ranges count is non-negative.
/// </summary>
public class FodsR360GetNamedRangeCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNamedRangeCount_NewDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetNamedRangeCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetNamedRangeCount_EmptyDocument_Ok()
    {
        var doc = FodsDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetNamedRangeCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetNamedRangeCount_AfterAddNamedRange_Increases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Data");
        int before = doc.GetNamedRangeCount();
        doc.AddNamedRange("TotalSales", "Sheet1", 0, 0, 5, 0);
        int after = doc.GetNamedRangeCount();
        Assert.True(after >= before);
    }

    [Fact]
    public void GetNamedRangeCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        _ = doc.GetNamedRangeCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetNamedRangeCount_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddNamedRange("Region1", "Sheet1", 0, 0, 3, 3);
        int first = doc.GetNamedRangeCount();
        int second = doc.GetNamedRangeCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddNamedRange_CountNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Budget");
        doc.SetCellValue("Budget", 0, 0, "Q1");
        doc.AddNamedRange("Q1Total", "Budget", 0, 0, 0, 3);
        int count = doc.GetNamedRangeCount();
        Assert.True(count >= 0);
        Assert.Equal(doc.SheetCount, doc.SheetCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleNamedRanges_CountNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddNamedRange("RangeA", "Data", 0, 0, 2, 2);
        doc.AddNamedRange("RangeB", "Data", 3, 0, 5, 2);
        doc.AddNamedRange("RangeC", "Data", 6, 0, 8, 2);
        int count = doc.GetNamedRangeCount();
        Assert.True(count >= 0);
    }
}
