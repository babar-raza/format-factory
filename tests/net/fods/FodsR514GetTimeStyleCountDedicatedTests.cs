// Tests for FodsDocument.GetTimeStyleCount dedicated coverage.
// Sprint: ff-sprint-s465-dotnet-deepening-20260701
// Ledger: PC-FODS-R514

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R514: Dedicated tests for FodsDocument.GetTimeStyleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetTimeStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR514GetTimeStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTimeStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetTimeStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetTimeStyleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetTimeStyleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetTimeStyleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetTimeStyleCount();
        int second = doc.GetTimeStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTimeStyleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetTimeStyleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetTimeStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetTimeStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetTimeStyleCount() >= 0);
        }
    }
}
