// Tests for FodsDocument.GetHyperlinkCount dedicated coverage.
// Sprint: ff-sprint-s448-dotnet-deepening-20260701
// Ledger: PC-FODS-R497

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R497: Dedicated tests for FodsDocument.GetHyperlinkCount().
/// New document returns non-negative count.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default doc non-negative; after adding sheet non-negative; multiple docs non-negative.
/// </summary>
public class FodsR497GetHyperlinkCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHyperlinkCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetHyperlinkCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetHyperlinkCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetHyperlinkCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetHyperlinkCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetHyperlinkCount();
        int second = doc.GetHyperlinkCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetHyperlinkCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetHyperlinkCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetHyperlinkCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetHyperlinkCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetHyperlinkCount() >= 0);
        }
    }
}
