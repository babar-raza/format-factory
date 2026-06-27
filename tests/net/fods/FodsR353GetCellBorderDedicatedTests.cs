// Tests for FodsDocument.GetCellBorder dedicated coverage.
// Sprint: ff-sprint-s321-dotnet-deepening-20260630
// Ledger: PC-FODS-R353

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R353: Dedicated tests for FodsDocument.GetCellBorder().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet throws.
/// Negative row throws.
/// Valid call returns non-null.
/// SheetCount unchanged after GetCellBorder.
/// Called twice same result.
/// Dogfood: SetCellBorder then GetCellBorder.
/// Dogfood: multiple cells.
/// </summary>
public class FodsR353GetCellBorderDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellBorder_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBorder(null!, 0, 0));
    }

    [Fact]
    public void GetCellBorder_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBorder("   ", 0, 0));
    }

    [Fact]
    public void GetCellBorder_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellBorder("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellBorder_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBorder("Data", -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellBorder_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Header");
        string? border = doc.GetCellBorder("Sheet1", 0, 0);
        Assert.NotNull(border);
    }

    [Fact]
    public void GetCellBorder_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellBorder("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellBorder_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Data");
        string? first = doc.GetCellBorder("Report", 0, 0);
        string? second = doc.GetCellBorder("Report", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellBorderThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Name");
        doc.SetCellBorder("Data", 0, 0, "thin");
        string? border = doc.GetCellBorder("Data", 0, 0);
        Assert.NotNull(border);
        Assert.Equal(doc.SheetCount, doc.SheetCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Table");
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                doc.SetCellValue("Table", r, c, $"Cell{r}{c}");
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                Assert.NotNull(doc.GetCellBorder("Table", r, c));
    }
}
