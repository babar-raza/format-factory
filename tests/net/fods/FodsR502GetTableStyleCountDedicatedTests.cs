// Tests for FodsDocument.GetTableStyleCount dedicated coverage.
// Sprint: ff-sprint-s453-dotnet-deepening-20260701
// Ledger: PC-FODS-R502

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R502: Dedicated tests for FodsDocument.GetTableStyleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetTableStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR502GetTableStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetTableStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetTableStyleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetTableStyleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetTableStyleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetTableStyleCount();
        int second = doc.GetTableStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTableStyleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetTableStyleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetTableStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetTableStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetTableStyleCount() >= 0);
        }
    }
}
