// Tests for FodsDocument.GetAlignmentCount dedicated coverage.
// Sprint: ff-sprint-s501-dotnet-deepening-20260701
// Ledger: PC-FODS-R550

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R550: Dedicated tests for FodsDocument.GetAlignmentCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetAlignmentCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR550GetAlignmentCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAlignmentCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetAlignmentCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetAlignmentCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetAlignmentCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetAlignmentCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetAlignmentCount();
        int second = doc.GetAlignmentCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetAlignmentCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetAlignmentCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetAlignmentCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Layout");
        Assert.True(doc.GetAlignmentCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetAlignmentCount() >= 0);
        }
    }
}
