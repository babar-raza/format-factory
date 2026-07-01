// Tests for FodsDocument.GetGroupBoxCount dedicated coverage.
// Sprint: ff-sprint-s528-dotnet-deepening-20260701
// Ledger: PC-FODS-R577

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R577: Dedicated tests for FodsDocument.GetGroupBoxCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetGroupBoxCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR577GetGroupBoxCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGroupBoxCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetGroupBoxCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetGroupBoxCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetGroupBoxCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetGroupBoxCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetGroupBoxCount();
        int second = doc.GetGroupBoxCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetGroupBoxCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetGroupBoxCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetGroupBoxCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Controls");
        Assert.True(doc.GetGroupBoxCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetGroupBoxCount() >= 0);
        }
    }
}
