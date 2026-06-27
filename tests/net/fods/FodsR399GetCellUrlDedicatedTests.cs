// Tests for FodsDocument.GetCellUrl dedicated coverage.
// Sprint: ff-sprint-s358-dotnet-deepening-20260630
// Ledger: PC-FODS-R399

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R399: Dedicated tests for FodsDocument.GetCellUrl().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellUrl.
/// Idempotent (called twice same result).
/// Dogfood: SetCellUrl then GetCellUrl returns expected URL.
/// Dogfood: multiple cells with different URLs each non-null.
/// </summary>
public class FodsR399GetCellUrlDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellUrl_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellUrl(null!, 0, 0));
    }

    [Fact]
    public void GetCellUrl_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellUrl("   ", 0, 0));
    }

    [Fact]
    public void GetCellUrl_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellUrl("NoSheet", 0, 0));
    }

    [Fact]
    public void GetCellUrl_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Links");
        Assert.ThrowsAny<Exception>(() => doc.GetCellUrl("Links", -1, 0));
    }

    [Fact]
    public void GetCellUrl_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        string? url = doc.GetCellUrl("Data", 0, 0);
        Assert.NotNull(url);
    }

    [Fact]
    public void GetCellUrl_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Hyperlinks");
        int before = doc.SheetCount;
        _ = doc.GetCellUrl("Hyperlinks", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellUrl_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string? first = doc.GetCellUrl("Stable", 0, 0);
        string? second = doc.GetCellUrl("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterSetCellUrl_ReturnsExpectedUrl()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("References");
        doc.SetCellUrl("References", 0, 0, "https://example.com/report");
        string? url = doc.GetCellUrl("References", 0, 0);
        Assert.NotNull(url);
        Assert.Equal("https://example.com/report", url);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_DifferentUrls()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Nav");
        doc.SetCellUrl("Nav", 0, 0, "https://example.com/page1");
        doc.SetCellUrl("Nav", 1, 0, "https://example.com/page2");
        doc.SetCellUrl("Nav", 2, 0, "https://example.com/page3");
        Assert.NotNull(doc.GetCellUrl("Nav", 0, 0));
        Assert.NotNull(doc.GetCellUrl("Nav", 1, 0));
        Assert.NotNull(doc.GetCellUrl("Nav", 2, 0));
    }
}
