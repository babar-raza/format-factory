// Tests for FodsDocument.GetSparklineCount dedicated coverage.
// Sprint: ff-sprint-s487-dotnet-deepening-20260701
// Ledger: PC-FODS-R536

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R536: Dedicated tests for FodsDocument.GetSparklineCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetSparklineCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR536GetSparklineCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSparklineCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetSparklineCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSparklineCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetSparklineCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSparklineCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetSparklineCount();
        int second = doc.GetSparklineCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSparklineCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetSparklineCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetSparklineCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Trends");
        Assert.True(doc.GetSparklineCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetSparklineCount() >= 0);
        }
    }
}
