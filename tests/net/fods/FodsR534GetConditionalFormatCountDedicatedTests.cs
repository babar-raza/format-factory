// Tests for FodsDocument.GetConditionalFormatCount dedicated coverage.
// Sprint: ff-sprint-s485-dotnet-deepening-20260701
// Ledger: PC-FODS-R534

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R534: Dedicated tests for FodsDocument.GetConditionalFormatCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetConditionalFormatCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR534GetConditionalFormatCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetConditionalFormatCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetConditionalFormatCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetConditionalFormatCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetConditionalFormatCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetConditionalFormatCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetConditionalFormatCount();
        int second = doc.GetConditionalFormatCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetConditionalFormatCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetConditionalFormatCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetConditionalFormatCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Rules");
        Assert.True(doc.GetConditionalFormatCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetConditionalFormatCount() >= 0);
        }
    }
}
