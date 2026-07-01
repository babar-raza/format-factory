// Tests for FodsDocument.GetEventHandlerCount dedicated coverage.
// Sprint: ff-sprint-s513-dotnet-deepening-20260701
// Ledger: PC-FODS-R562

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R562: Dedicated tests for FodsDocument.GetEventHandlerCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetEventHandlerCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR562GetEventHandlerCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEventHandlerCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetEventHandlerCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetEventHandlerCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetEventHandlerCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetEventHandlerCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetEventHandlerCount();
        int second = doc.GetEventHandlerCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetEventHandlerCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetEventHandlerCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetEventHandlerCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Events");
        Assert.True(doc.GetEventHandlerCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetEventHandlerCount() >= 0);
        }
    }
}
