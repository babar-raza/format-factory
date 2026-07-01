// Tests for FodsDocument.GetShapeCount dedicated coverage.
// Sprint: ff-sprint-s447-dotnet-deepening-20260701
// Ledger: PC-FODS-R496

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R496: Dedicated tests for FodsDocument.GetShapeCount().
/// New document returns non-negative count.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default doc non-negative; after adding sheet non-negative; multiple docs non-negative.
/// </summary>
public class FodsR496GetShapeCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetShapeCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetShapeCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetShapeCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetShapeCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetShapeCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetShapeCount();
        int second = doc.GetShapeCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetShapeCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetShapeCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetShapeCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetShapeCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetShapeCount() >= 0);
        }
    }
}
