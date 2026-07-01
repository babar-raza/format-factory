// Tests for FodsDocument.GetGroupCount dedicated coverage.
// Sprint: ff-sprint-s443-dotnet-deepening-20260701
// Ledger: PC-FODS-R492

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R492: Dedicated tests for FodsDocument.GetGroupCount().
/// New document returns non-negative count.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default doc non-negative; after adding sheet non-negative; multiple docs non-negative.
/// </summary>
public class FodsR492GetGroupCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGroupCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetGroupCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetGroupCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetGroupCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetGroupCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetGroupCount();
        int second = doc.GetGroupCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetGroupCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetGroupCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetGroupCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetGroupCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetGroupCount() >= 0);
        }
    }
}
