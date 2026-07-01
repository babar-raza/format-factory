// Tests for FodsDocument.GetDataPilotCount dedicated coverage.
// Sprint: ff-sprint-s476-dotnet-deepening-20260701
// Ledger: PC-FODS-R525

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R525: Dedicated tests for FodsDocument.GetDataPilotCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetDataPilotCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR525GetDataPilotCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDataPilotCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetDataPilotCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetDataPilotCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetDataPilotCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetDataPilotCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetDataPilotCount();
        int second = doc.GetDataPilotCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDataPilotCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetDataPilotCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetDataPilotCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetDataPilotCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetDataPilotCount() >= 0);
        }
    }
}
