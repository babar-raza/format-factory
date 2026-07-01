// Tests for FodsDocument.GetCellStyleCount dedicated coverage.
// Sprint: ff-sprint-s454-dotnet-deepening-20260701
// Ledger: PC-FODS-R503

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R503: Dedicated tests for FodsDocument.GetCellStyleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetCellStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR503GetCellStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetCellStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCellStyleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetCellStyleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellStyleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetCellStyleCount();
        int second = doc.GetCellStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellStyleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetCellStyleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetCellStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetCellStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetCellStyleCount() >= 0);
        }
    }
}
