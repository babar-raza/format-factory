// Tests for FodsDocument.GetDataValidationCount dedicated coverage.
// Sprint: ff-sprint-s437-dotnet-deepening-20260701
// Ledger: PC-FODS-R486

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R486: Dedicated tests for FodsDocument.GetDataValidationCount().
/// New document returns non-negative count.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default doc non-negative; after adding sheet non-negative; multiple docs non-negative.
/// </summary>
public class FodsR486GetDataValidationCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDataValidationCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetDataValidationCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetDataValidationCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetDataValidationCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetDataValidationCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetDataValidationCount();
        int second = doc.GetDataValidationCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDataValidationCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetDataValidationCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetDataValidationCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetDataValidationCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetDataValidationCount() >= 0);
        }
    }
}
