// Tests for FodsDocument.GetListBoxCount dedicated coverage.
// Sprint: ff-sprint-s521-dotnet-deepening-20260701
// Ledger: PC-FODS-R570

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R570: Dedicated tests for FodsDocument.GetListBoxCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetListBoxCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR570GetListBoxCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListBoxCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetListBoxCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetListBoxCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetListBoxCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetListBoxCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetListBoxCount();
        int second = doc.GetListBoxCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetListBoxCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetListBoxCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetListBoxCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Controls");
        Assert.True(doc.GetListBoxCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetListBoxCount() >= 0);
        }
    }
}
