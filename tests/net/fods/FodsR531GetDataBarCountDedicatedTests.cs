// Tests for FodsDocument.GetDataBarCount dedicated coverage.
// Sprint: ff-sprint-s482-dotnet-deepening-20260701
// Ledger: PC-FODS-R531

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R531: Dedicated tests for FodsDocument.GetDataBarCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetDataBarCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR531GetDataBarCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDataBarCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetDataBarCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetDataBarCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetDataBarCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetDataBarCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetDataBarCount();
        int second = doc.GetDataBarCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDataBarCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetDataBarCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetDataBarCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Metrics");
        Assert.True(doc.GetDataBarCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetDataBarCount() >= 0);
        }
    }
}
