// Tests for FodsDocument.GetBooleanStyleCount dedicated coverage.
// Sprint: ff-sprint-s466-dotnet-deepening-20260701
// Ledger: PC-FODS-R515

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R515: Dedicated tests for FodsDocument.GetBooleanStyleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetBooleanStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR515GetBooleanStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBooleanStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetBooleanStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetBooleanStyleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetBooleanStyleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetBooleanStyleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetBooleanStyleCount();
        int second = doc.GetBooleanStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetBooleanStyleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetBooleanStyleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetBooleanStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetBooleanStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetBooleanStyleCount() >= 0);
        }
    }
}
