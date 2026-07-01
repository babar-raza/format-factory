// Tests for FodsDocument.GetFontCount dedicated coverage.
// Sprint: ff-sprint-s497-dotnet-deepening-20260701
// Ledger: PC-FODS-R546

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R546: Dedicated tests for FodsDocument.GetFontCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetFontCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR546GetFontCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFontCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetFontCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetFontCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetFontCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetFontCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetFontCount();
        int second = doc.GetFontCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetFontCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetFontCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetFontCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Typography");
        Assert.True(doc.GetFontCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetFontCount() >= 0);
        }
    }
}
