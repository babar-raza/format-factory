// Tests for FodsDocument.GetSheetViewCount dedicated coverage.
// Sprint: ff-sprint-s494-dotnet-deepening-20260701
// Ledger: PC-FODS-R543

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R543: Dedicated tests for FodsDocument.GetSheetViewCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetSheetViewCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR543GetSheetViewCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetViewCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetSheetViewCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSheetViewCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetSheetViewCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetViewCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetSheetViewCount();
        int second = doc.GetSheetViewCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetViewCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetSheetViewCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetSheetViewCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("View2");
        Assert.True(doc.GetSheetViewCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetSheetViewCount() >= 0);
        }
    }
}
