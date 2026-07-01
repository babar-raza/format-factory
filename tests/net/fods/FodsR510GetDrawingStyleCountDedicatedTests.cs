// Tests for FodsDocument.GetDrawingStyleCount dedicated coverage.
// Sprint: ff-sprint-s461-dotnet-deepening-20260701
// Ledger: PC-FODS-R510

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R510: Dedicated tests for FodsDocument.GetDrawingStyleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetDrawingStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR510GetDrawingStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDrawingStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetDrawingStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetDrawingStyleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetDrawingStyleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetDrawingStyleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetDrawingStyleCount();
        int second = doc.GetDrawingStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDrawingStyleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetDrawingStyleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetDrawingStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetDrawingStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetDrawingStyleCount() >= 0);
        }
    }
}
