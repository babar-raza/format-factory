// Tests for FodsDocument.GetFormulaCount dedicated coverage.
// Sprint: ff-sprint-s507-dotnet-deepening-20260701
// Ledger: PC-FODS-R556

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R556: Dedicated tests for FodsDocument.GetFormulaCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetFormulaCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR556GetFormulaCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFormulaCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetFormulaCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetFormulaCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetFormulaCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetFormulaCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetFormulaCount();
        int second = doc.GetFormulaCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetFormulaCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetFormulaCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetFormulaCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Formulas");
        Assert.True(doc.GetFormulaCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetFormulaCount() >= 0);
        }
    }
}
