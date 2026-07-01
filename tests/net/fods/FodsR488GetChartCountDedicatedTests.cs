// Tests for FodsDocument.GetChartCount dedicated coverage.
// Sprint: ff-sprint-s439-dotnet-deepening-20260701
// Ledger: PC-FODS-R488

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R488: Dedicated tests for FodsDocument.GetChartCount().
/// New document returns non-negative count.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default doc non-negative; after adding sheet non-negative; multiple docs non-negative.
/// </summary>
public class FodsR488GetChartCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChartCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetChartCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetChartCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetChartCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetChartCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetChartCount();
        int second = doc.GetChartCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetChartCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetChartCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetChartCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetChartCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetChartCount() >= 0);
        }
    }
}
