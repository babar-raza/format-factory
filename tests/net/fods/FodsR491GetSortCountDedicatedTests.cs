// Tests for FodsDocument.GetSortCount dedicated coverage.
// Sprint: ff-sprint-s442-dotnet-deepening-20260701
// Ledger: PC-FODS-R491

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R491: Dedicated tests for FodsDocument.GetSortCount().
/// New document returns non-negative count.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default doc non-negative; after adding sheet non-negative; multiple docs non-negative.
/// </summary>
public class FodsR491GetSortCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSortCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetSortCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSortCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetSortCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSortCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetSortCount();
        int second = doc.GetSortCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSortCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetSortCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetSortCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetSortCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetSortCount() >= 0);
        }
    }
}
