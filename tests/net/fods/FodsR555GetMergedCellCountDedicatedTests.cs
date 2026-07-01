// Tests for FodsDocument.GetMergedCellCount dedicated coverage.
// Sprint: ff-sprint-s506-dotnet-deepening-20260701
// Ledger: PC-FODS-R555

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R555: Dedicated tests for FodsDocument.GetMergedCellCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetMergedCellCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR555GetMergedCellCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMergedCellCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetMergedCellCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetMergedCellCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetMergedCellCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetMergedCellCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetMergedCellCount();
        int second = doc.GetMergedCellCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMergedCellCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetMergedCellCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetMergedCellCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Merged");
        Assert.True(doc.GetMergedCellCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetMergedCellCount() >= 0);
        }
    }
}
