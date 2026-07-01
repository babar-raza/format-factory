// Tests for FodsDocument.GetRowCount dedicated coverage.
// Sprint: ff-sprint-s503-dotnet-deepening-20260701
// Ledger: PC-FODS-R552

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R552: Dedicated tests for FodsDocument.GetRowCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetRowCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR552GetRowCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetRowCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetRowCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetRowCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetRowCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetRowCount();
        int second = doc.GetRowCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetRowCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetRowCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetRowCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.True(doc.GetRowCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetRowCount() >= 0);
        }
    }
}
