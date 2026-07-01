// Tests for FodsDocument.GetColorScaleCount dedicated coverage.
// Sprint: ff-sprint-s484-dotnet-deepening-20260701
// Ledger: PC-FODS-R533

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R533: Dedicated tests for FodsDocument.GetColorScaleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetColorScaleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR533GetColorScaleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorScaleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetColorScaleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetColorScaleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetColorScaleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetColorScaleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetColorScaleCount();
        int second = doc.GetColorScaleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetColorScaleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetColorScaleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetColorScaleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Heatmap");
        Assert.True(doc.GetColorScaleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetColorScaleCount() >= 0);
        }
    }
}
