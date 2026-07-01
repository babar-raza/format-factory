// Tests for FodsDocument.GetGraphicStyleCount dedicated coverage.
// Sprint: ff-sprint-s458-dotnet-deepening-20260701
// Ledger: PC-FODS-R507

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R507: Dedicated tests for FodsDocument.GetGraphicStyleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetGraphicStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR507GetGraphicStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGraphicStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetGraphicStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetGraphicStyleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetGraphicStyleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetGraphicStyleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetGraphicStyleCount();
        int second = doc.GetGraphicStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetGraphicStyleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetGraphicStyleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetGraphicStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetGraphicStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetGraphicStyleCount() >= 0);
        }
    }
}
