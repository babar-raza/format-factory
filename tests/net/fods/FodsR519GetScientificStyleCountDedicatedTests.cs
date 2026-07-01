// Tests for FodsDocument.GetScientificStyleCount dedicated coverage.
// Sprint: ff-sprint-s470-dotnet-deepening-20260701
// Ledger: PC-FODS-R519

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R519: Dedicated tests for FodsDocument.GetScientificStyleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetScientificStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR519GetScientificStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetScientificStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetScientificStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetScientificStyleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetScientificStyleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetScientificStyleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetScientificStyleCount();
        int second = doc.GetScientificStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetScientificStyleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetScientificStyleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetScientificStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetScientificStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetScientificStyleCount() >= 0);
        }
    }
}
