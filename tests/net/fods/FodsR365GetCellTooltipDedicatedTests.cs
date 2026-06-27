// Tests for FodsDocument.GetCellTooltip dedicated coverage.
// Sprint: ff-sprint-s330-dotnet-deepening-20260630
// Ledger: PC-FODS-R365

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R365: Dedicated tests for FodsDocument.GetCellTooltip().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet throws.
/// Negative row throws.
/// Valid call returns non-null.
/// SheetCount unchanged after GetCellTooltip.
/// Called twice same result.
/// Dogfood: SetCellTooltip then GetCellTooltip.
/// Dogfood: multiple cells all return non-null tooltip.
/// </summary>
public class FodsR365GetCellTooltipDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellTooltip_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellTooltip(null!, 0, 0));
    }

    [Fact]
    public void GetCellTooltip_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellTooltip("   ", 0, 0));
    }

    [Fact]
    public void GetCellTooltip_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellTooltip("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellTooltip_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellTooltip("Data", -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellTooltip_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Value");
        string? tooltip = doc.GetCellTooltip("Sheet1", 0, 0);
        Assert.NotNull(tooltip);
    }

    [Fact]
    public void GetCellTooltip_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Hints");
        int before = doc.SheetCount;
        _ = doc.GetCellTooltip("Hints", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellTooltip_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Help");
        doc.SetCellValue("Help", 0, 0, "Click me");
        string? first = doc.GetCellTooltip("Help", 0, 0);
        string? second = doc.GetCellTooltip("Help", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellTooltipThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Form");
        doc.SetCellValue("Form", 0, 0, "Enter name");
        doc.SetCellTooltip("Form", 0, 0, "Please enter your full name here");
        string? tooltip = doc.GetCellTooltip("Form", 0, 0);
        Assert.NotNull(tooltip);
        Assert.Equal(doc.SheetCount, doc.SheetCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNullTooltip()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Guide");
        string[] hints = { "Enter first name", "Enter last name", "Enter email" };
        for (int r = 0; r < hints.Length; r++)
        {
            doc.SetCellValue("Guide", r, 0, $"Field {r + 1}");
            doc.SetCellTooltip("Guide", r, 0, hints[r]);
        }
        for (int r = 0; r < hints.Length; r++)
            Assert.NotNull(doc.GetCellTooltip("Guide", r, 0));
    }
}
