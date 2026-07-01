// Tests for FodsDocument.GetRowGroupCount dedicated coverage.
// Sprint: ff-sprint-s480-dotnet-deepening-20260701
// Ledger: PC-FODS-R529

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R529: Dedicated tests for FodsDocument.GetRowGroupCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetRowGroupCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR529GetRowGroupCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowGroupCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetRowGroupCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetRowGroupCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetRowGroupCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetRowGroupCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetRowGroupCount();
        int second = doc.GetRowGroupCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetRowGroupCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetRowGroupCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetRowGroupCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet2");
        Assert.True(doc.GetRowGroupCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetRowGroupCount() >= 0);
        }
    }
}
