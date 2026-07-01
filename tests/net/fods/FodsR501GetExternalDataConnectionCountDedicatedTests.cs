// Tests for FodsDocument.GetExternalDataConnectionCount dedicated coverage.
// Sprint: ff-sprint-s452-dotnet-deepening-20260701
// Ledger: PC-FODS-R501

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R501: Dedicated tests for FodsDocument.GetExternalDataConnectionCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetExternalDataConnectionCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR501GetExternalDataConnectionCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetExternalDataConnectionCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetExternalDataConnectionCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetExternalDataConnectionCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetExternalDataConnectionCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetExternalDataConnectionCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetExternalDataConnectionCount();
        int second = doc.GetExternalDataConnectionCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetExternalDataConnectionCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetExternalDataConnectionCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetExternalDataConnectionCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetExternalDataConnectionCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetExternalDataConnectionCount() >= 0);
        }
    }
}
