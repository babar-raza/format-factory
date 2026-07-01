// Tests for FodsDocument.GetFilterCount dedicated coverage.
// Sprint: ff-sprint-s441-dotnet-deepening-20260701
// Ledger: PC-FODS-R490

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R490: Dedicated tests for FodsDocument.GetFilterCount().
/// New document returns non-negative count.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default doc non-negative; after adding sheet non-negative; multiple docs non-negative.
/// </summary>
public class FodsR490GetFilterCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFilterCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetFilterCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetFilterCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetFilterCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetFilterCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetFilterCount();
        int second = doc.GetFilterCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetFilterCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetFilterCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetFilterCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetFilterCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetFilterCount() >= 0);
        }
    }
}
