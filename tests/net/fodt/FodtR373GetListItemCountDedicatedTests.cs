// Tests for FodtDocument.GetListItemCount dedicated coverage.
// Sprint: ff-sprint-s355-dotnet-deepening-20260630
// Ledger: PC-FODT-R373

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R373: Dedicated tests for FodtDocument.GetListItemCount().
/// Negative list index throws.
/// Out-of-range list index throws.
/// Empty document (no lists) throws.
/// Valid list returns non-negative count.
/// ParagraphCount unchanged after GetListItemCount.
/// ListCount unchanged after GetListItemCount.
/// Idempotent (called twice same result).
/// Dogfood: AddList with items returns correct item count.
/// Dogfood: multiple lists each returns correct count.
/// </summary>
public class FodtR373GetListItemCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListItemCount_NegativeListIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "Item 1", "Item 2" });
        Assert.ThrowsAny<Exception>(() => doc.GetListItemCount(-1));
    }

    [Fact]
    public void GetListItemCount_OutOfRangeListIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "Item 1" });
        Assert.ThrowsAny<Exception>(() => doc.GetListItemCount(99));
    }

    [Fact]
    public void GetListItemCount_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetListItemCount(0));
    }

    [Fact]
    public void GetListItemCount_ValidList_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "Alpha", "Beta", "Gamma" });
        int count = doc.GetListItemCount(0);
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetListItemCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction");
        doc.AddList(new[] { "Point A", "Point B" });
        int before = doc.ParagraphCount;
        _ = doc.GetListItemCount(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetListItemCount_ListCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "A", "B", "C" });
        int before = doc.ListCount;
        _ = doc.GetListItemCount(0);
        Assert.Equal(before, doc.ListCount);
    }

    [Fact]
    public void GetListItemCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "X", "Y", "Z" });
        int first = doc.GetListItemCount(0);
        int second = doc.GetListItemCount(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddListWithThreeItems_ReturnsThree()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "Revenue", "Expenses", "Net Profit" });
        int count = doc.GetListItemCount(0);
        Assert.Equal(3, count);
    }

    [Fact]
    public void DogfoodPipeline_MultipleLists_EachCorrectCount()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "A", "B" });
        doc.AddList(new[] { "X", "Y", "Z", "W" });
        Assert.Equal(2, doc.GetListItemCount(0));
        Assert.Equal(4, doc.GetListItemCount(1));
    }
}
