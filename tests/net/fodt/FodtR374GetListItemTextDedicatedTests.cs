// Tests for FodtDocument.GetListItemText dedicated coverage.
// Sprint: ff-sprint-s356-dotnet-deepening-20260630
// Ledger: PC-FODT-R374

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R374: Dedicated tests for FodtDocument.GetListItemText().
/// Negative list index throws.
/// Out-of-range list index throws.
/// Negative item index throws.
/// Out-of-range item index throws.
/// Valid item returns non-null.
/// ListCount unchanged after GetListItemText.
/// Idempotent (called twice same result).
/// Dogfood: AddList then GetListItemText returns exact text.
/// Dogfood: multiple items in list each returns correct text.
/// </summary>
public class FodtR374GetListItemTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListItemText_NegativeListIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "Item A", "Item B" });
        Assert.ThrowsAny<Exception>(() => doc.GetListItemText(-1, 0));
    }

    [Fact]
    public void GetListItemText_OutOfRangeListIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "Item A" });
        Assert.ThrowsAny<Exception>(() => doc.GetListItemText(99, 0));
    }

    [Fact]
    public void GetListItemText_NegativeItemIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "Item A", "Item B" });
        Assert.ThrowsAny<Exception>(() => doc.GetListItemText(0, -1));
    }

    [Fact]
    public void GetListItemText_OutOfRangeItemIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "Item A" });
        Assert.ThrowsAny<Exception>(() => doc.GetListItemText(0, 99));
    }

    [Fact]
    public void GetListItemText_ValidItem_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "Alpha", "Beta" });
        string? text = doc.GetListItemText(0, 0);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetListItemText_ListCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "X", "Y", "Z" });
        int before = doc.ListCount;
        _ = doc.GetListItemText(0, 0);
        Assert.Equal(before, doc.ListCount);
    }

    [Fact]
    public void GetListItemText_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "Stable Item" });
        string? first = doc.GetListItemText(0, 0);
        string? second = doc.GetListItemText(0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddListThenGet_ReturnsExactText()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "Revenue", "Expenses", "Net Profit" });
        string? text = doc.GetListItemText(0, 1);
        Assert.NotNull(text);
        Assert.Equal("Expenses", text);
    }

    [Fact]
    public void DogfoodPipeline_MultipleItems_EachCorrectText()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "First", "Second", "Third" });
        Assert.Equal("First", doc.GetListItemText(0, 0));
        Assert.Equal("Second", doc.GetListItemText(0, 1));
        Assert.Equal("Third", doc.GetListItemText(0, 2));
    }
}
