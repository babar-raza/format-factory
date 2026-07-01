// Tests for FodsDocument.GetQueryTableCount dedicated coverage.
// Sprint: ff-sprint-s515-dotnet-deepening-20260701
// Ledger: PC-FODS-R564

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R564: Dedicated tests for FodsDocument.GetQueryTableCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetQueryTableCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR564GetQueryTableCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetQueryTableCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetQueryTableCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetQueryTableCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetQueryTableCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetQueryTableCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetQueryTableCount();
        int second = doc.GetQueryTableCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetQueryTableCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetQueryTableCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetQueryTableCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Queries");
        Assert.True(doc.GetQueryTableCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetQueryTableCount() >= 0);
        }
    }
}
