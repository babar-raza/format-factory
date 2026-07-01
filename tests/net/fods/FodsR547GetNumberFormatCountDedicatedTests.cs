// Tests for FodsDocument.GetNumberFormatCount dedicated coverage.
// Sprint: ff-sprint-s498-dotnet-deepening-20260701
// Ledger: PC-FODS-R547

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R547: Dedicated tests for FodsDocument.GetNumberFormatCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetNumberFormatCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document returns non-negative.
/// Dogfood: after adding sheet returns non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodsR547GetNumberFormatCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumberFormatCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetNumberFormatCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetNumberFormatCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetNumberFormatCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetNumberFormatCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetNumberFormatCount();
        int second = doc.GetNumberFormatCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetNumberFormatCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetNumberFormatCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetNumberFormatCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Numbers");
        Assert.True(doc.GetNumberFormatCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i + 2}");
            Assert.True(doc.GetNumberFormatCount() >= 0);
        }
    }
}
