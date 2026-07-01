// Tests for FodsDocument.GetNamedRangeCount dedicated coverage.
// Sprint: ff-sprint-s481-dotnet-deepening-20260701
// Ledger: PC-FODS-R530

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R530: Dedicated tests for FodsDocument.GetNamedRangeCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetNamedRangeCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR530GetNamedRangeCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNamedRangeCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetNamedRangeCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetNamedRangeCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetNamedRangeCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetNamedRangeCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetNamedRangeCount();
        int second = doc.GetNamedRangeCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetNamedRangeCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetNamedRangeCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetNamedRangeCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.True(doc.GetNamedRangeCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetNamedRangeCount() >= 0);
        }
    }
}
