// Tests for FodsDocument.GetProgressBarCount dedicated coverage.
// Sprint: ff-sprint-s527-dotnet-deepening-20260701
// Ledger: PC-FODS-R576

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R576: Dedicated tests for FodsDocument.GetProgressBarCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetProgressBarCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR576GetProgressBarCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetProgressBarCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetProgressBarCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetProgressBarCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetProgressBarCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetProgressBarCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetProgressBarCount();
        int second = doc.GetProgressBarCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetProgressBarCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetProgressBarCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetProgressBarCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Controls");
        Assert.True(doc.GetProgressBarCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetProgressBarCount() >= 0);
        }
    }
}
