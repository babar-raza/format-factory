// Tests for FodsDocument.GetNamedRangeCount dedicated coverage.
// Sprint: ff-sprint-s287-dotnet-deepening-20260630
// Ledger: PC-FODS-R315

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R315: Dedicated tests for FodsDocument.GetNamedRangeCount().
/// Returns non-negative int.
/// Increases after AddNamedRange.
/// SheetCount unchanged after GetNamedRangeCount.
/// Called twice returns same result.
/// Adding two ranges increases count by at least 2.
/// New document count at least zero.
/// Dogfood: add named range, count increases.
/// Dogfood: multiple named ranges accumulated correctly.
/// </summary>
public class FodsR315GetNamedRangeCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNamedRangeCount_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int count = doc.GetNamedRangeCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetNamedRangeCount_IncreasesAfterAddNamedRange()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        int before = doc.GetNamedRangeCount();
        doc.AddNamedRange("TestRange", sheet, 0, 0, 5, 5);
        int after = doc.GetNamedRangeCount();
        Assert.True(after > before);
    }

    [Fact]
    public void GetNamedRangeCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetNamedRangeCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetNamedRangeCount_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.AddNamedRange("Range1", sheet, 0, 0, 2, 2);
        int first = doc.GetNamedRangeCount();
        int second = doc.GetNamedRangeCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetNamedRangeCount_AddTwoRanges_IncreasedByAtLeastTwo()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        int before = doc.GetNamedRangeCount();
        doc.AddNamedRange("RangeA", sheet, 0, 0, 2, 2);
        doc.AddNamedRange("RangeB", sheet, 3, 0, 5, 2);
        int after = doc.GetNamedRangeCount();
        Assert.True(after >= before + 2);
    }

    [Fact]
    public void GetNamedRangeCount_NewDocument_AtLeastZero()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.True(doc.GetNamedRangeCount() >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddNamedRange_CountIncreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        int before = doc.GetNamedRangeCount();
        doc.AddNamedRange("DataRange", sheet, 1, 0, 10, 4);
        int after = doc.GetNamedRangeCount();
        Assert.True(after > before);
    }

    [Fact]
    public void DogfoodPipeline_MultipleRanges_AccumulatedCorrectly()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        int before = doc.GetNamedRangeCount();
        doc.AddNamedRange("R1", sheet, 0, 0, 1, 1);
        doc.AddNamedRange("R2", sheet, 2, 0, 3, 1);
        doc.AddNamedRange("R3", sheet, 4, 0, 5, 1);
        Assert.True(doc.GetNamedRangeCount() >= before + 3);
    }
}
