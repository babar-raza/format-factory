// Tests for FodsDocument.GetScenarioCount dedicated coverage.
// Sprint: ff-sprint-s492-dotnet-deepening-20260701
// Ledger: PC-FODS-R541

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R541: Dedicated tests for FodsDocument.GetScenarioCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetScenarioCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR541GetScenarioCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetScenarioCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetScenarioCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetScenarioCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetScenarioCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetScenarioCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetScenarioCount();
        int second = doc.GetScenarioCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetScenarioCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetScenarioCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetScenarioCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Scenarios");
        Assert.True(doc.GetScenarioCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetScenarioCount() >= 0);
        }
    }
}
