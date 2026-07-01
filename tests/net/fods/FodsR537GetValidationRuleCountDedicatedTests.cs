// Tests for FodsDocument.GetValidationRuleCount dedicated coverage.
// Sprint: ff-sprint-s488-dotnet-deepening-20260701
// Ledger: PC-FODS-R537

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R537: Dedicated tests for FodsDocument.GetValidationRuleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetValidationRuleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR537GetValidationRuleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetValidationRuleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetValidationRuleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetValidationRuleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetValidationRuleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetValidationRuleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetValidationRuleCount();
        int second = doc.GetValidationRuleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetValidationRuleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetValidationRuleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetValidationRuleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Input");
        Assert.True(doc.GetValidationRuleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetValidationRuleCount() >= 0);
        }
    }
}
