// Tests for FodsDocument.GetSpinnerCount dedicated coverage.
// Sprint: ff-sprint-s523-dotnet-deepening-20260701
// Ledger: PC-FODS-R572

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R572: Dedicated tests for FodsDocument.GetSpinnerCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetSpinnerCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR572GetSpinnerCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSpinnerCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetSpinnerCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSpinnerCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetSpinnerCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSpinnerCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetSpinnerCount();
        int second = doc.GetSpinnerCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSpinnerCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetSpinnerCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetSpinnerCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Controls");
        Assert.True(doc.GetSpinnerCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetSpinnerCount() >= 0);
        }
    }
}
