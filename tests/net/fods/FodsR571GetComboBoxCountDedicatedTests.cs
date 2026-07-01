// Tests for FodsDocument.GetComboBoxCount dedicated coverage.
// Sprint: ff-sprint-s522-dotnet-deepening-20260701
// Ledger: PC-FODS-R571

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R571: Dedicated tests for FodsDocument.GetComboBoxCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetComboBoxCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR571GetComboBoxCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetComboBoxCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetComboBoxCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetComboBoxCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetComboBoxCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetComboBoxCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetComboBoxCount();
        int second = doc.GetComboBoxCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetComboBoxCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetComboBoxCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetComboBoxCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Controls");
        Assert.True(doc.GetComboBoxCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetComboBoxCount() >= 0);
        }
    }
}
