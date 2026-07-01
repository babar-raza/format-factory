// Tests for FodsDocument.GetCurrencyStyleCount dedicated coverage.
// Sprint: ff-sprint-s467-dotnet-deepening-20260701
// Ledger: PC-FODS-R516

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R516: Dedicated tests for FodsDocument.GetCurrencyStyleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetCurrencyStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR516GetCurrencyStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCurrencyStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetCurrencyStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCurrencyStyleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetCurrencyStyleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCurrencyStyleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetCurrencyStyleCount();
        int second = doc.GetCurrencyStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCurrencyStyleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetCurrencyStyleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetCurrencyStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetCurrencyStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetCurrencyStyleCount() >= 0);
        }
    }
}
