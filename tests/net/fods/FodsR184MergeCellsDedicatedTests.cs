// Tests for FodsDocument.MergeCells dedicated coverage.
// Sprint: ff-sprint-s177-dotnet-deepening-20260628
// Ledger: PC-FODS-R184

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R184: Dedicated tests for FodsDocument.MergeCells(sheetName, startRow, startCol, rowSpan, colSpan).
/// Sets ODF span attributes on the anchor cell and marks covered cells.
/// null/whitespace sheetName throws ArgumentException.
/// rowSpan &lt; 1 throws ArgumentOutOfRangeException.
/// colSpan &lt; 1 throws ArgumentOutOfRangeException.
/// Nonexistent sheet throws InvalidOperationException.
/// startRow out-of-range throws ArgumentOutOfRangeException.
/// startCol out-of-range throws ArgumentOutOfRangeException.
/// Valid merge: anchor cell has span attributes; does not throw.
/// Covers: null/whitespace guard; rowSpan=0 guard; colSpan=0 guard;
/// nonexistent sheet; startRow negative; valid 1x1 (no-op anchor); valid 1x2;
/// valid 2x1; dogfood pipeline add-rows-then-merge.
/// </summary>
public class FodsR184MergeCellsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void MergeCells_NullOrWhitespaceSheetName_ThrowsArgumentException(string sheetName)
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.MergeCells(sheetName, 0, 0, 1, 1));
    }

    [Fact]
    public void MergeCells_RowSpanZero_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.MergeCells("Data", 0, 0, 0, 1));
    }

    [Fact]
    public void MergeCells_ColSpanZero_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.MergeCells("Data", 0, 0, 1, 0));
    }

    [Fact]
    public void MergeCells_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() => doc.MergeCells("NoSheet", 0, 0, 1, 1));
    }

    [Fact]
    public void MergeCells_NegativeStartRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "A");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.MergeCells("Data", -1, 0, 1, 1));
    }

    // -------------------------------------------------------------------------
    // Valid merge tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeCells_ValidSingleCell_DoesNotThrow()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "Anchor");
        // 1x1 merge is a no-op but should not throw
        doc.MergeCells("Data", 0, 0, 1, 1);
    }

    [Fact]
    public void MergeCells_ValidHorizontalMerge_DoesNotThrow()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "A");
        doc.SetCellValue(0, 1, "B");
        // merge row 0, col 0..1 (1 row, 2 cols)
        doc.MergeCells("Data", 0, 0, 1, 2);
    }

    [Fact]
    public void MergeCells_ValidVerticalMerge_DoesNotThrow()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "Top");
        doc.SetCellValue(1, 0, "Bottom");
        // merge rows 0..1, col 0 (2 rows, 1 col)
        doc.MergeCells("Data", 0, 0, 2, 1);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddRows_ThenMerge_CellDataPreserved()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue(0, 0, "Header");
        doc.SetCellValue(0, 1, "Value");
        doc.SetCellValue(1, 0, "Row1A");
        doc.SetCellValue(1, 1, "Row1B");
        // Merge the header row (row 0, cols 0-1)
        doc.MergeCells("Report", 0, 0, 1, 2);
        // Anchor cell retains its value
        Assert.Equal("Header", doc.GetCellValue("Report", 0, 0));
    }
}
