// Tests for FodsDocument.GetCellBorderStyle dedicated coverage.
// Sprint: ff-sprint-s374-dotnet-deepening-20260630
// Ledger: PC-FODS-R417

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R417: Dedicated tests for FodsDocument.GetCellBorderStyle().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellBorderStyle.
/// Idempotent (called twice same result).
/// Dogfood: SetBorderStyle thin+Get.
/// Dogfood: multiple cells distinct border styles.
/// </summary>
public class FodsR417GetCellBorderStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellBorderStyle_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellBorderStyle(null!, 0, 0));
    }

    [Fact]
    public void GetCellBorderStyle_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellBorderStyle("   ", 0, 0));
    }

    [Fact]
    public void GetCellBorderStyle_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellBorderStyle("Missing", 0, 0));
    }

    [Fact]
    public void GetCellBorderStyle_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBorderStyle("Data", -1, 0));
    }

    [Fact]
    public void GetCellBorderStyle_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Layout");
        string style = doc.GetCellBorderStyle("Layout", 0, 0);
        Assert.NotNull(style);
    }

    [Fact]
    public void GetCellBorderStyle_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        _ = doc.GetCellBorderStyle("Data", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellBorderStyle_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string first = doc.GetCellBorderStyle("Stable", 0, 0);
        string second = doc.GetCellBorderStyle("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetBorderStyleThinThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellBorderStyle("Report", 0, 0, "thin");
        string style = doc.GetCellBorderStyle("Report", 0, 0);
        Assert.Equal("thin", style);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_DistinctStyles()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Grid");
        doc.SetCellBorderStyle("Grid", 0, 0, "thin");
        doc.SetCellBorderStyle("Grid", 1, 0, "medium");
        doc.SetCellBorderStyle("Grid", 2, 0, "thick");
        Assert.Equal("thin", doc.GetCellBorderStyle("Grid", 0, 0));
        Assert.Equal("medium", doc.GetCellBorderStyle("Grid", 1, 0));
        Assert.Equal("thick", doc.GetCellBorderStyle("Grid", 2, 0));
    }
}
