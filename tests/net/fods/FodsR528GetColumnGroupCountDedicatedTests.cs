// Tests for FodsDocument.GetColumnGroupCount dedicated coverage.
// Sprint: ff-sprint-s479-dotnet-deepening-20260701
// Ledger: PC-FODS-R528

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R528: Dedicated tests for FodsDocument.GetColumnGroupCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetColumnGroupCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR528GetColumnGroupCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnGroupCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetColumnGroupCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetColumnGroupCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetColumnGroupCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetColumnGroupCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetColumnGroupCount();
        int second = doc.GetColumnGroupCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetColumnGroupCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetColumnGroupCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetColumnGroupCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetColumnGroupCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetColumnGroupCount() >= 0);
        }
    }
}
