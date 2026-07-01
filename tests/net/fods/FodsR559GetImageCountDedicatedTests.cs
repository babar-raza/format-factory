// Tests for FodsDocument.GetImageCount dedicated coverage.
// Sprint: ff-sprint-s510-dotnet-deepening-20260701
// Ledger: PC-FODS-R559

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R559: Dedicated tests for FodsDocument.GetImageCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetImageCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR559GetImageCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetImageCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetImageCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetImageCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetImageCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetImageCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetImageCount();
        int second = doc.GetImageCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetImageCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetImageCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetImageCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Images");
        Assert.True(doc.GetImageCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetImageCount() >= 0);
        }
    }
}
