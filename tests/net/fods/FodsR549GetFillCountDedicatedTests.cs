// Tests for FodsDocument.GetFillCount dedicated coverage.
// Sprint: ff-sprint-s500-dotnet-deepening-20260701
// Ledger: PC-FODS-R549

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R549: Dedicated tests for FodsDocument.GetFillCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetFillCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR549GetFillCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFillCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetFillCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetFillCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetFillCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetFillCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetFillCount();
        int second = doc.GetFillCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetFillCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetFillCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetFillCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Colors");
        Assert.True(doc.GetFillCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetFillCount() >= 0);
        }
    }
}
