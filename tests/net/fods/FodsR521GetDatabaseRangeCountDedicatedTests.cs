// Tests for FodsDocument.GetDatabaseRangeCount dedicated coverage.
// Sprint: ff-sprint-s472-dotnet-deepening-20260701
// Ledger: PC-FODS-R521

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R521: Dedicated tests for FodsDocument.GetDatabaseRangeCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetDatabaseRangeCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR521GetDatabaseRangeCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDatabaseRangeCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetDatabaseRangeCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetDatabaseRangeCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetDatabaseRangeCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetDatabaseRangeCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetDatabaseRangeCount();
        int second = doc.GetDatabaseRangeCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDatabaseRangeCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetDatabaseRangeCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetDatabaseRangeCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetDatabaseRangeCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetDatabaseRangeCount() >= 0);
        }
    }
}
