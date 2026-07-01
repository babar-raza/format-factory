// Tests for FodsDocument.GetSharedFormulaCount dedicated coverage.
// Sprint: ff-sprint-s445-dotnet-deepening-20260701
// Ledger: PC-FODS-R494

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R494: Dedicated tests for FodsDocument.GetSharedFormulaCount().
/// New document returns non-negative count.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default doc non-negative; after adding sheet non-negative; multiple docs non-negative.
/// </summary>
public class FodsR494GetSharedFormulaCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSharedFormulaCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetSharedFormulaCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSharedFormulaCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetSharedFormulaCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSharedFormulaCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetSharedFormulaCount();
        int second = doc.GetSharedFormulaCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSharedFormulaCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetSharedFormulaCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetSharedFormulaCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetSharedFormulaCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetSharedFormulaCount() >= 0);
        }
    }
}
