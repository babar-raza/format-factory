// Tests for FodsDocument.GetConnectionCount dedicated coverage.
// Sprint: ff-sprint-s514-dotnet-deepening-20260701
// Ledger: PC-FODS-R563

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R563: Dedicated tests for FodsDocument.GetConnectionCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetConnectionCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR563GetConnectionCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetConnectionCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetConnectionCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetConnectionCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetConnectionCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetConnectionCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetConnectionCount();
        int second = doc.GetConnectionCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetConnectionCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetConnectionCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetConnectionCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.True(doc.GetConnectionCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetConnectionCount() >= 0);
        }
    }
}
