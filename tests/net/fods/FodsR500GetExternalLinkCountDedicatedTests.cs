// Tests for FodsDocument.GetExternalLinkCount dedicated coverage.
// Sprint: ff-sprint-s451-dotnet-deepening-20260701
// Ledger: PC-FODS-R500

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R500: Dedicated tests for FodsDocument.GetExternalLinkCount().
/// New document returns non-negative count.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default doc non-negative; after adding sheet non-negative; multiple docs non-negative.
/// </summary>
public class FodsR500GetExternalLinkCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetExternalLinkCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetExternalLinkCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetExternalLinkCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetExternalLinkCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetExternalLinkCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetExternalLinkCount();
        int second = doc.GetExternalLinkCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetExternalLinkCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetExternalLinkCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetExternalLinkCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetExternalLinkCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetExternalLinkCount() >= 0);
        }
    }
}
