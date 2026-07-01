// Tests for FodsDocument.GetSortStateCount dedicated coverage.
// Sprint: ff-sprint-s491-dotnet-deepening-20260701
// Ledger: PC-FODS-R540

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R540: Dedicated tests for FodsDocument.GetSortStateCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetSortStateCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR540GetSortStateCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSortStateCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetSortStateCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSortStateCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetSortStateCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSortStateCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetSortStateCount();
        int second = doc.GetSortStateCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSortStateCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetSortStateCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetSortStateCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sorted");
        Assert.True(doc.GetSortStateCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetSortStateCount() >= 0);
        }
    }
}
