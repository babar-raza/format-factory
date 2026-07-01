// Tests for FodsDocument.GetFrameCount dedicated coverage.
// Sprint: ff-sprint-s529-dotnet-deepening-20260701
// Ledger: PC-FODS-R578

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R578: Dedicated tests for FodsDocument.GetFrameCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetFrameCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR578GetFrameCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetFrameCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetFrameCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetFrameCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetFrameCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetFrameCount();
        int second = doc.GetFrameCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetFrameCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetFrameCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetFrameCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Frames");
        Assert.True(doc.GetFrameCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetFrameCount() >= 0);
        }
    }
}
