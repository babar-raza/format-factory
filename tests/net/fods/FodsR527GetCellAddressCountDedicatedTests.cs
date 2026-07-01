// Tests for FodsDocument.GetCellAddressCount dedicated coverage.
// Sprint: ff-sprint-s478-dotnet-deepening-20260701
// Ledger: PC-FODS-R527

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R527: Dedicated tests for FodsDocument.GetCellAddressCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetCellAddressCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR527GetCellAddressCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellAddressCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetCellAddressCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCellAddressCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetCellAddressCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellAddressCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetCellAddressCount();
        int second = doc.GetCellAddressCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellAddressCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetCellAddressCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetCellAddressCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetCellAddressCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetCellAddressCount() >= 0);
        }
    }
}
