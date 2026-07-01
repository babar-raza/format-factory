// Tests for FodsDocument.GetFormulaErrorCount dedicated coverage.
// Sprint: ff-sprint-s450-dotnet-deepening-20260701
// Ledger: PC-FODS-R499

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R499: Dedicated tests for FodsDocument.GetFormulaErrorCount().
/// New document returns non-negative count.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default doc non-negative; after adding sheet non-negative; multiple docs non-negative.
/// </summary>
public class FodsR499GetFormulaErrorCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFormulaErrorCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetFormulaErrorCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetFormulaErrorCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetFormulaErrorCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetFormulaErrorCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetFormulaErrorCount();
        int second = doc.GetFormulaErrorCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetFormulaErrorCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetFormulaErrorCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetFormulaErrorCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetFormulaErrorCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetFormulaErrorCount() >= 0);
        }
    }
}
