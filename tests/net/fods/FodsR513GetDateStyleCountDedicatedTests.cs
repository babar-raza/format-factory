// Tests for FodsDocument.GetDateStyleCount dedicated coverage.
// Sprint: ff-sprint-s464-dotnet-deepening-20260701
// Ledger: PC-FODS-R513

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R513: Dedicated tests for FodsDocument.GetDateStyleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetDateStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR513GetDateStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDateStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetDateStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetDateStyleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetDateStyleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetDateStyleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetDateStyleCount();
        int second = doc.GetDateStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDateStyleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetDateStyleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetDateStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetDateStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetDateStyleCount() >= 0);
        }
    }
}
