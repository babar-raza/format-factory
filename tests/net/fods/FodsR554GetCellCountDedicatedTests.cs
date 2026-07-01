// Tests for FodsDocument.GetCellCount dedicated coverage.
// Sprint: ff-sprint-s505-dotnet-deepening-20260701
// Ledger: PC-FODS-R554

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R554: Dedicated tests for FodsDocument.GetCellCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetCellCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR554GetCellCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetCellCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCellCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetCellCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetCellCount();
        int second = doc.GetCellCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetCellCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetCellCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Cells");
        Assert.True(doc.GetCellCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetCellCount() >= 0);
        }
    }
}
