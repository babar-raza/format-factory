// Tests for FodsDocument.GetProtectionCount dedicated coverage.
// Sprint: ff-sprint-s502-dotnet-deepening-20260701
// Ledger: PC-FODS-R551

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R551: Dedicated tests for FodsDocument.GetProtectionCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetProtectionCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR551GetProtectionCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetProtectionCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetProtectionCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetProtectionCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetProtectionCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetProtectionCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetProtectionCount();
        int second = doc.GetProtectionCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetProtectionCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetProtectionCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetProtectionCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Locked");
        Assert.True(doc.GetProtectionCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetProtectionCount() >= 0);
        }
    }
}
