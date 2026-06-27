// Tests for FodsDocument.GetCellHyperlink dedicated coverage.
// Sprint: ff-sprint-s360-dotnet-deepening-20260630
// Ledger: PC-FODS-R402

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R402: Dedicated tests for FodsDocument.GetCellHyperlink().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellHyperlink.
/// Idempotent (called twice same result).
/// Dogfood: SetCellHyperlink then GetCellHyperlink returns expected.
/// Dogfood: multiple cells each with different hyperlinks.
/// </summary>
public class FodsR402GetCellHyperlinkDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellHyperlink_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellHyperlink(null!, 0, 0));
    }

    [Fact]
    public void GetCellHyperlink_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellHyperlink("   ", 0, 0));
    }

    [Fact]
    public void GetCellHyperlink_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellHyperlink("Ghost", 0, 0));
    }

    [Fact]
    public void GetCellHyperlink_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Links");
        Assert.ThrowsAny<Exception>(() => doc.GetCellHyperlink("Links", -1, 0));
    }

    [Fact]
    public void GetCellHyperlink_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        string? link = doc.GetCellHyperlink("Data", 0, 0);
        Assert.NotNull(link);
    }

    [Fact]
    public void GetCellHyperlink_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Refs");
        int before = doc.SheetCount;
        _ = doc.GetCellHyperlink("Refs", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellHyperlink_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string? first = doc.GetCellHyperlink("Stable", 0, 0);
        string? second = doc.GetCellHyperlink("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterSetCellHyperlink_ReturnsExpected()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Resources");
        doc.SetCellHyperlink("Resources", 0, 0, "https://example.com/docs");
        string? link = doc.GetCellHyperlink("Resources", 0, 0);
        Assert.NotNull(link);
        Assert.Equal("https://example.com/docs", link);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_DifferentHyperlinks()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Nav");
        doc.SetCellHyperlink("Nav", 0, 0, "https://example.com/home");
        doc.SetCellHyperlink("Nav", 1, 0, "https://example.com/about");
        doc.SetCellHyperlink("Nav", 2, 0, "https://example.com/contact");
        string? l0 = doc.GetCellHyperlink("Nav", 0, 0);
        string? l1 = doc.GetCellHyperlink("Nav", 1, 0);
        string? l2 = doc.GetCellHyperlink("Nav", 2, 0);
        Assert.NotNull(l0);
        Assert.NotNull(l1);
        Assert.NotNull(l2);
    }
}
