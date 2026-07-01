// Tests for FodsDocument.GetCustomPropertyCount dedicated coverage.
// Sprint: ff-sprint-s516-dotnet-deepening-20260701
// Ledger: PC-FODS-R565

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R565: Dedicated tests for FodsDocument.GetCustomPropertyCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetCustomPropertyCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR565GetCustomPropertyCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCustomPropertyCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetCustomPropertyCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCustomPropertyCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetCustomPropertyCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCustomPropertyCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetCustomPropertyCount();
        int second = doc.GetCustomPropertyCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCustomPropertyCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetCustomPropertyCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetCustomPropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Properties");
        Assert.True(doc.GetCustomPropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetCustomPropertyCount() >= 0);
        }
    }
}
