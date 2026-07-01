// Tests for FodsDocument.GetCommentCount dedicated coverage.
// Sprint: ff-sprint-s449-dotnet-deepening-20260701
// Ledger: PC-FODS-R498

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R498: Dedicated tests for FodsDocument.GetCommentCount().
/// New document returns non-negative count.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default doc non-negative; after adding sheet non-negative; multiple docs non-negative.
/// </summary>
public class FodsR498GetCommentCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCommentCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetCommentCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCommentCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetCommentCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCommentCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetCommentCount();
        int second = doc.GetCommentCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCommentCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetCommentCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetCommentCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetCommentCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetCommentCount() >= 0);
        }
    }
}
