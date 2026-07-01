// Tests for FodsDocument.GetColumnStyleCount dedicated coverage.
// Sprint: ff-sprint-s455-dotnet-deepening-20260701
// Ledger: PC-FODS-R504

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R504: Dedicated tests for FodsDocument.GetColumnStyleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetColumnStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR504GetColumnStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetColumnStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetColumnStyleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetColumnStyleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetColumnStyleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetColumnStyleCount();
        int second = doc.GetColumnStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetColumnStyleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetColumnStyleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetColumnStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetColumnStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetColumnStyleCount() >= 0);
        }
    }
}
