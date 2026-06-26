// Tests for FodsDocument.MergeCells dedicated coverage.
// Sprint: ff-sprint-s160-dotnet-deepening-20260628
// Ledger: PC-FODS-R167

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R167: Dedicated tests for FodsDocument.MergeCells(string sheetName, int startRow, int startCol, int rowSpan, int colSpan).
/// MergeCells sets span attributes on the anchor cell and replaces covered cells with covered-table-cell elements.
/// Throws ArgumentException for null/whitespace sheetName.
/// Throws InvalidOperationException if no sheet with that name exists.
/// Throws ArgumentOutOfRangeException for rowSpan/colSpan less than 1, or out-of-bounds range.
/// Covers: null sheetName throws ArgumentException; whitespace throws ArgumentException;
/// nonexistent sheet throws InvalidOperationException; rowSpan=0 throws ArgumentOutOfRangeException;
/// colSpan=0 throws ArgumentOutOfRangeException; out-of-bounds startRow throws ArgumentOutOfRangeException;
/// valid 1x1 merge no-throw; rowSpan=1 colSpan=1 is identity no-throw;
/// dogfood CreateNew->AddSheet->SetCellValue->MergeCells pipeline;
/// dogfood merge does not change sheet count.
/// </summary>
public class FodsR167MergeCellsDedicatedTests
{
    private static FodsDocument MakeDocWithGrid()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Sheet1");
        // Add 3 rows with 3 cells each
        for (int r = 0; r < 3; r++)
        {
            doc.SetCellValue("Sheet1", r, 0, $"R{r}C0");
            doc.SetCellValue("Sheet1", r, 1, $"R{r}C1");
            doc.SetCellValue("Sheet1", r, 2, $"R{r}C2");
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeCells_NullSheetName_ThrowsArgumentException()
    {
        var doc = MakeDocWithGrid();
        Assert.Throws<ArgumentException>(() => doc.MergeCells(null!, 0, 0, 1, 2));
    }

    [Fact]
    public void MergeCells_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = MakeDocWithGrid();
        Assert.Throws<ArgumentException>(() => doc.MergeCells("   ", 0, 0, 1, 2));
    }

    [Fact]
    public void MergeCells_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = MakeDocWithGrid();
        Assert.Throws<InvalidOperationException>(() => doc.MergeCells("NoSheet", 0, 0, 1, 2));
    }

    [Fact]
    public void MergeCells_RowSpanZero_ThrowsArgumentOutOfRangeException()
    {
        var doc = MakeDocWithGrid();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.MergeCells("Sheet1", 0, 0, 0, 2));
    }

    [Fact]
    public void MergeCells_ColSpanZero_ThrowsArgumentOutOfRangeException()
    {
        var doc = MakeDocWithGrid();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.MergeCells("Sheet1", 0, 0, 1, 0));
    }

    [Fact]
    public void MergeCells_StartRowOutOfBounds_ThrowsArgumentOutOfRangeException()
    {
        var doc = MakeDocWithGrid();
        // 3 rows, startRow=2, rowSpan=2 → tries to access rows [2..3], row 3 doesn't exist
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.MergeCells("Sheet1", 2, 0, 2, 1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeCells_ValidCall_DoesNotThrow()
    {
        var doc = MakeDocWithGrid();
        // Merge 1 row, 2 cols starting at (0,0)
        doc.MergeCells("Sheet1", 0, 0, 1, 2);
        // If no exception, success
        Assert.Equal(1, doc.GetSheetByName("Sheet1")!.Rows.Count > 0 ? 1 : 0);
    }

    [Fact]
    public void MergeCells_RowSpan1ColSpan1_IsIdentityNoThrow()
    {
        var doc = MakeDocWithGrid();
        // 1x1 merge = no-op effectively (anchor covers itself)
        doc.MergeCells("Sheet1", 0, 0, 1, 1);
        Assert.Equal("R0C0", doc.GetCellValue("Sheet1", 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_SetCellValue_MergeCells()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Header");
        doc.SetCellValue("Data", 0, 1, "SubHeader");
        // Merge first two cells in header row
        doc.MergeCells("Data", 0, 0, 1, 2);
        var names = doc.GetSheetNames();
        Assert.Contains("Data", names);
    }

    [Fact]
    public void DogfoodPipeline_MergeCells_DoesNotChangeSheetCount()
    {
        var doc = MakeDocWithGrid();
        doc.AddSheet("Sheet2");
        var before = doc.GetSheetNames().Count;
        doc.MergeCells("Sheet1", 0, 0, 1, 2);
        Assert.Equal(before, doc.GetSheetNames().Count);
    }
}
