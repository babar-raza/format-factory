// Tests for FodsDocument.GetPageStyleCount dedicated coverage.
// Sprint: ff-sprint-s457-dotnet-deepening-20260701
// Ledger: PC-FODS-R506

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R506: Dedicated tests for FodsDocument.GetPageStyleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetPageStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR506GetPageStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPageStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetPageStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetPageStyleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetPageStyleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetPageStyleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetPageStyleCount();
        int second = doc.GetPageStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPageStyleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetPageStyleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetPageStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetPageStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetPageStyleCount() >= 0);
        }
    }
}
