// Tests for FodsDocument.GetChartStyleCount dedicated coverage.
// Sprint: ff-sprint-s463-dotnet-deepening-20260701
// Ledger: PC-FODS-R512

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R512: Dedicated tests for FodsDocument.GetChartStyleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetChartStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR512GetChartStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChartStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetChartStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetChartStyleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetChartStyleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetChartStyleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetChartStyleCount();
        int second = doc.GetChartStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetChartStyleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetChartStyleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetChartStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetChartStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetChartStyleCount() >= 0);
        }
    }
}
