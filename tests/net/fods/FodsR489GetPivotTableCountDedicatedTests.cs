// Tests for FodsDocument.GetPivotTableCount dedicated coverage.
// Sprint: ff-sprint-s440-dotnet-deepening-20260701
// Ledger: PC-FODS-R489

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R489: Dedicated tests for FodsDocument.GetPivotTableCount().
/// New document returns non-negative count.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default doc non-negative; after adding sheet non-negative; multiple docs non-negative.
/// </summary>
public class FodsR489GetPivotTableCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPivotTableCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetPivotTableCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetPivotTableCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetPivotTableCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetPivotTableCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetPivotTableCount();
        int second = doc.GetPivotTableCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPivotTableCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetPivotTableCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetPivotTableCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetPivotTableCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetPivotTableCount() >= 0);
        }
    }
}
