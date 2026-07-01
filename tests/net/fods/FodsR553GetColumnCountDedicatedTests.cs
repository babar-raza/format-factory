// Tests for FodsDocument.GetColumnCount dedicated coverage.
// Sprint: ff-sprint-s504-dotnet-deepening-20260701
// Ledger: PC-FODS-R553

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R553: Dedicated tests for FodsDocument.GetColumnCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetColumnCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR553GetColumnCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetColumnCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetColumnCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetColumnCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetColumnCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetColumnCount();
        int second = doc.GetColumnCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetColumnCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetColumnCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetColumnCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Grid");
        Assert.True(doc.GetColumnCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetColumnCount() >= 0);
        }
    }
}
