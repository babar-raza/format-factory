// Tests for FodsDocument.GetConsolidationCount dedicated coverage.
// Sprint: ff-sprint-s493-dotnet-deepening-20260701
// Ledger: PC-FODS-R542

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R542: Dedicated tests for FodsDocument.GetConsolidationCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetConsolidationCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR542GetConsolidationCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetConsolidationCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetConsolidationCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetConsolidationCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetConsolidationCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetConsolidationCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetConsolidationCount();
        int second = doc.GetConsolidationCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetConsolidationCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetConsolidationCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetConsolidationCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Consolidated");
        Assert.True(doc.GetConsolidationCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetConsolidationCount() >= 0);
        }
    }
}
