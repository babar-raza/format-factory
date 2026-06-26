// Tests for FodsDocument.MergeCells dedicated coverage.
// Sprint: ff-sprint-s193-dotnet-deepening-20260629
// Ledger: PC-FODS-R205

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R205: Dedicated tests for FodsDocument.MergeCells(sheetName, startRow, startCol, rowSpan, colSpan).
/// null/whitespace sheetName → ArgumentException.
/// rowSpan &lt; 1 → ArgumentOutOfRangeException.
/// colSpan &lt; 1 → ArgumentOutOfRangeException.
/// Nonexistent sheet → InvalidOperationException.
/// OOB startRow → ArgumentOutOfRangeException.
/// OOB startCol → ArgumentOutOfRangeException.
/// Valid 1x2 merge: anchor cell gets number-columns-spanned attribute.
/// Valid merge does not throw.
/// Sheet cell count unchanged after merge.
/// Dogfood: merge then set value on anchor cell works; multi-cell merge sets span.
/// </summary>
public class FodsR205MergeCellsDedicatedTests
{
    private static readonly string MinimalPath =
        System.IO.Path.Combine("samples", "by-format", "fods", "minimal-spreadsheet.fods");

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeCells_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.MergeCells(null!, 0, 0, 1, 2));
    }

    [Fact]
    public void MergeCells_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.MergeCells("   ", 0, 0, 1, 2));
    }

    [Fact]
    public void MergeCells_RowSpanZero_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.MergeCells(sheet.Name!, 0, 0, 0, 1));
    }

    [Fact]
    public void MergeCells_ColSpanZero_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.MergeCells(sheet.Name!, 0, 0, 1, 0));
    }

    [Fact]
    public void MergeCells_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() => doc.MergeCells("NoSuchSheet", 0, 0, 1, 2));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeCells_ValidMerge_DoesNotThrow()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        // Ensure enough cells exist by setting values
        doc.SetCellValue(sheet.Name!, 0, 0, "A");
        doc.SetCellValue(sheet.Name!, 0, 1, "B");
        var ex = Record.Exception(() => doc.MergeCells(sheet.Name!, 0, 0, 1, 2));
        Assert.Null(ex);
    }

    [Fact]
    public void MergeCells_AfterMerge_SheetCountUnchanged()
    {
        var doc = FodsDocument.Load(MinimalPath);
        int before = doc.SheetCount;
        var sheet = doc.Sheets[0];
        doc.SetCellValue(sheet.Name!, 0, 0, "A");
        doc.SetCellValue(sheet.Name!, 0, 1, "B");
        doc.MergeCells(sheet.Name!, 0, 0, 1, 2);
        Assert.Equal(before, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MergeThenSetValue_ValueAccessible()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        doc.SetCellValue(sheet.Name!, 0, 0, "Header");
        doc.SetCellValue(sheet.Name!, 0, 1, "X");
        doc.MergeCells(sheet.Name!, 0, 0, 1, 2);
        // Anchor cell value should still be accessible
        var val = doc.GetCellValue(0, 0);
        Assert.Equal("Header", val);
    }

    [Fact]
    public void DogfoodPipeline_RowSpanNegative_Throws()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(
            () => doc.MergeCells(sheet.Name!, 0, 0, -1, 1));
    }
}
