// Tests for FodsDocument.GetFractionStyleCount dedicated coverage.
// Sprint: ff-sprint-s469-dotnet-deepening-20260701
// Ledger: PC-FODS-R518

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R518: Dedicated tests for FodsDocument.GetFractionStyleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetFractionStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR518GetFractionStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFractionStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetFractionStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetFractionStyleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetFractionStyleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetFractionStyleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetFractionStyleCount();
        int second = doc.GetFractionStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetFractionStyleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetFractionStyleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetFractionStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetFractionStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetFractionStyleCount() >= 0);
        }
    }
}
