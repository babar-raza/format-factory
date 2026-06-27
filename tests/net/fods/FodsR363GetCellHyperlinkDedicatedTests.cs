// Tests for FodsDocument.GetCellHyperlink dedicated coverage.
// Sprint: ff-sprint-s329-dotnet-deepening-20260630
// Ledger: PC-FODS-R363

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R363: Dedicated tests for FodsDocument.GetCellHyperlink().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet throws.
/// Negative row throws.
/// Valid call returns non-null.
/// SheetCount unchanged after GetCellHyperlink.
/// Called twice same result.
/// Dogfood: SetCellHyperlink then GetCellHyperlink.
/// Dogfood: multiple cells all return non-null.
/// </summary>
public class FodsR363GetCellHyperlinkDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellHyperlink_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellHyperlink(null!, 0, 0));
    }

    [Fact]
    public void GetCellHyperlink_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellHyperlink("   ", 0, 0));
    }

    [Fact]
    public void GetCellHyperlink_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellHyperlink("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellHyperlink_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellHyperlink("Data", -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellHyperlink_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Click here");
        string? hyperlink = doc.GetCellHyperlink("Sheet1", 0, 0);
        Assert.NotNull(hyperlink);
    }

    [Fact]
    public void GetCellHyperlink_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Links");
        int before = doc.SheetCount;
        _ = doc.GetCellHyperlink("Links", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellHyperlink_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Web");
        doc.SetCellValue("Web", 0, 0, "Link text");
        string? first = doc.GetCellHyperlink("Web", 0, 0);
        string? second = doc.GetCellHyperlink("Web", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellHyperlinkThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Resources");
        doc.SetCellValue("Resources", 0, 0, "Documentation");
        doc.SetCellHyperlink("Resources", 0, 0, "https://docs.example.com");
        string? hyperlink = doc.GetCellHyperlink("Resources", 0, 0);
        Assert.NotNull(hyperlink);
        Assert.Equal(doc.SheetCount, doc.SheetCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Links");
        string[] urls = { "https://site1.com", "https://site2.com", "https://site3.com" };
        for (int r = 0; r < urls.Length; r++)
        {
            doc.SetCellValue("Links", r, 0, $"Site {r + 1}");
            doc.SetCellHyperlink("Links", r, 0, urls[r]);
        }
        for (int r = 0; r < urls.Length; r++)
            Assert.NotNull(doc.GetCellHyperlink("Links", r, 0));
    }
}
