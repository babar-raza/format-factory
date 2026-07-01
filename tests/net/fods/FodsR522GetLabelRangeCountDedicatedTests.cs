// Tests for FodsDocument.GetLabelRangeCount dedicated coverage.
// Sprint: ff-sprint-s473-dotnet-deepening-20260701
// Ledger: PC-FODS-R522

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R522: Dedicated tests for FodsDocument.GetLabelRangeCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetLabelRangeCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR522GetLabelRangeCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLabelRangeCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetLabelRangeCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetLabelRangeCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetLabelRangeCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetLabelRangeCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetLabelRangeCount();
        int second = doc.GetLabelRangeCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetLabelRangeCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetLabelRangeCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetLabelRangeCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetLabelRangeCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetLabelRangeCount() >= 0);
        }
    }
}
