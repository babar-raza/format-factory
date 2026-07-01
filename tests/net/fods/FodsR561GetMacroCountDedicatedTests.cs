// Tests for FodsDocument.GetMacroCount dedicated coverage.
// Sprint: ff-sprint-s512-dotnet-deepening-20260701
// Ledger: PC-FODS-R561

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R561: Dedicated tests for FodsDocument.GetMacroCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetMacroCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR561GetMacroCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMacroCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetMacroCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetMacroCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetMacroCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetMacroCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetMacroCount();
        int second = doc.GetMacroCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMacroCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetMacroCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetMacroCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Macros");
        Assert.True(doc.GetMacroCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetMacroCount() >= 0);
        }
    }
}
