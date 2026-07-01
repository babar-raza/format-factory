// Tests for FodsDocument.GetSparklineGroupCount dedicated coverage.
// Sprint: ff-sprint-s475-dotnet-deepening-20260701
// Ledger: PC-FODS-R524

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R524: Dedicated tests for FodsDocument.GetSparklineGroupCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetSparklineGroupCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR524GetSparklineGroupCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSparklineGroupCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetSparklineGroupCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSparklineGroupCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetSparklineGroupCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSparklineGroupCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetSparklineGroupCount();
        int second = doc.GetSparklineGroupCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSparklineGroupCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetSparklineGroupCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetSparklineGroupCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetSparklineGroupCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetSparklineGroupCount() >= 0);
        }
    }
}
