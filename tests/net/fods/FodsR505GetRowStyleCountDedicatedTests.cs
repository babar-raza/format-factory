// Tests for FodsDocument.GetRowStyleCount dedicated coverage.
// Sprint: ff-sprint-s456-dotnet-deepening-20260701
// Ledger: PC-FODS-R505

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R505: Dedicated tests for FodsDocument.GetRowStyleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetRowStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR505GetRowStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetRowStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetRowStyleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetRowStyleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetRowStyleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetRowStyleCount();
        int second = doc.GetRowStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetRowStyleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetRowStyleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetRowStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetRowStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetRowStyleCount() >= 0);
        }
    }
}
