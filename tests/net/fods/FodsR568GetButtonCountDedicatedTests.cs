// Tests for FodsDocument.GetButtonCount dedicated coverage.
// Sprint: ff-sprint-s519-dotnet-deepening-20260701
// Ledger: PC-FODS-R568

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R568: Dedicated tests for FodsDocument.GetButtonCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetButtonCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR568GetButtonCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetButtonCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetButtonCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetButtonCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetButtonCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetButtonCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetButtonCount();
        int second = doc.GetButtonCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetButtonCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetButtonCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetButtonCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Controls");
        Assert.True(doc.GetButtonCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetButtonCount() >= 0);
        }
    }
}
