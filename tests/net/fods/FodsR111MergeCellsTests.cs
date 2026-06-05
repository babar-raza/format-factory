// R111 Wave 5: FODS MergeCells tests
// Ledger: R111-GOVERNED-DOTNET-FODS-MERGECELLS-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR111MergeCellsTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void MergeCells_SingleCell_SetsMergeAttributes()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        int rows = doc.GetRowCount(name);
        int cols = doc.GetColumnCount(name);
        if (rows >= 2 && cols >= 2)
        {
            doc.MergeCells(name, 0, 0, 2, 2);
            // After merge, cell (0,1) should be covered
            var val = FodsDocument.GetCellValue(doc.Sheets[0], 0, 1);
            // Covered cells return null
            Assert.Null(val);
        }
    }

    [Fact]
    public void MergeCells_SingleRowSpan_SetsColumnSpan()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        int cols = doc.GetColumnCount(name);
        if (cols >= 3)
        {
            doc.MergeCells(name, 0, 0, 1, 3);
            // Cells (0,1) and (0,2) should be covered
            Assert.Null(FodsDocument.GetCellValue(doc.Sheets[0], 0, 1));
            Assert.Null(FodsDocument.GetCellValue(doc.Sheets[0], 0, 2));
        }
    }

    [Fact]
    public void MergeCells_InvalidSheetName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<InvalidOperationException>(() =>
            doc.MergeCells("nonexistent_sheet_xyz", 0, 0, 1, 1));
    }

    [Fact]
    public void MergeCells_EmptySheetName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() =>
            doc.MergeCells("", 0, 0, 1, 1));
    }

    [Fact]
    public void MergeCells_ZeroRowSpan_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.MergeCells(name, 0, 0, 0, 1));
    }

    [Fact]
    public void MergeCells_ZeroColSpan_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.MergeCells(name, 0, 0, 1, 0));
    }

    [Fact]
    public void MergeCells_OutOfRangeRow_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        int rows = doc.GetRowCount(name);
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.MergeCells(name, 0, 0, rows + 10, 1));
    }

    [Fact]
    public void MergeCells_PreservesAnchorValue()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        int rows = doc.GetRowCount(name);
        int cols = doc.GetColumnCount(name);
        if (rows >= 2 && cols >= 2)
        {
            var originalVal = FodsDocument.GetCellValue(doc.Sheets[0], 0, 0);
            doc.MergeCells(name, 0, 0, 2, 2);
            // Anchor cell value is preserved
            Assert.Equal(originalVal, FodsDocument.GetCellValue(doc.Sheets[0], 0, 0));
        }
    }
}
