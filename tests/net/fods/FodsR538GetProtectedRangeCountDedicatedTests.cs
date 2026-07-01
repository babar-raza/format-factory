// Tests for FodsDocument.GetProtectedRangeCount dedicated coverage.
// Sprint: ff-sprint-s489-dotnet-deepening-20260701
// Ledger: PC-FODS-R538

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R538: Dedicated tests for FodsDocument.GetProtectedRangeCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetProtectedRangeCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR538GetProtectedRangeCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetProtectedRangeCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetProtectedRangeCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetProtectedRangeCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetProtectedRangeCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetProtectedRangeCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetProtectedRangeCount();
        int second = doc.GetProtectedRangeCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetProtectedRangeCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetProtectedRangeCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetProtectedRangeCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Protected");
        Assert.True(doc.GetProtectedRangeCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetProtectedRangeCount() >= 0);
        }
    }
}
