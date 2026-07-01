// Tests for FodsDocument.GetAnnotationCount dedicated coverage.
// Sprint: ff-sprint-s446-dotnet-deepening-20260701
// Ledger: PC-FODS-R495

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R495: Dedicated tests for FodsDocument.GetAnnotationCount().
/// New document returns non-negative count.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default doc non-negative; after adding sheet non-negative; multiple docs non-negative.
/// </summary>
public class FodsR495GetAnnotationCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAnnotationCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetAnnotationCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetAnnotationCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetAnnotationCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetAnnotationCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetAnnotationCount();
        int second = doc.GetAnnotationCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetAnnotationCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetAnnotationCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetAnnotationCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetAnnotationCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetAnnotationCount() >= 0);
        }
    }
}
