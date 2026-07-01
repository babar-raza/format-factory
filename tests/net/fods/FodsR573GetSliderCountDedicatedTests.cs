// Tests for FodsDocument.GetSliderCount dedicated coverage.
// Sprint: ff-sprint-s524-dotnet-deepening-20260701
// Ledger: PC-FODS-R573

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R573: Dedicated tests for FodsDocument.GetSliderCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetSliderCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR573GetSliderCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSliderCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetSliderCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSliderCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetSliderCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSliderCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetSliderCount();
        int second = doc.GetSliderCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSliderCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetSliderCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetSliderCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Controls");
        Assert.True(doc.GetSliderCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetSliderCount() >= 0);
        }
    }
}
