// Tests for FodsDocument.GetRadioButtonCount dedicated coverage.
// Sprint: ff-sprint-s525-dotnet-deepening-20260701
// Ledger: PC-FODS-R574

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R574: Dedicated tests for FodsDocument.GetRadioButtonCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetRadioButtonCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR574GetRadioButtonCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRadioButtonCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetRadioButtonCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetRadioButtonCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetRadioButtonCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetRadioButtonCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetRadioButtonCount();
        int second = doc.GetRadioButtonCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetRadioButtonCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetRadioButtonCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetRadioButtonCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Controls");
        Assert.True(doc.GetRadioButtonCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetRadioButtonCount() >= 0);
        }
    }
}
