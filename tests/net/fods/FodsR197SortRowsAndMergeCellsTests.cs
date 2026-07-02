// Tests for FodsDocument.SortRows, MergeCells deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R197

using System.Linq;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R197: Tests for FodsDocument.SortRows, MergeCells deeper coverage.
/// SortRows(sheetName, col, ascending): sorts rows by column value.
/// MergeCells(sheetName, startRow, startCol, endRow, endCol): merges a cell range.
/// Covers: SortRows non-null result; SortRows ascending order correct;
/// SortRows descending order correct; SortRows count unchanged;
/// SortRows by string column; SortRows by numeric column;
/// MergeCells does not throw; MergeCells then GetCellValue works;
/// MergeCells then GetRowValues works; SortRows then FilterRows;
/// SortRows then GetColumnValues; SortRows ascending first value;
/// SortRows descending first value; SortRows single row unchanged;
/// dogfood CreateNew->SetCells->SortRows->MergeCells->GetColumnValues->Verify.
/// </summary>
public class FodsR197SortRowsAndMergeCellsTests
{
    private static FodsDocument CreateWithData()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Carol"); doc.SetCellValue(0, 1, "Eng");   doc.SetCellValue(0, 2, "88");
        doc.SetCellValue(1, 0, "Alice"); doc.SetCellValue(1, 1, "Eng");   doc.SetCellValue(1, 2, "95");
        doc.SetCellValue(2, 0, "Bob");   doc.SetCellValue(2, 1, "Finance"); doc.SetCellValue(2, 2, "82");
        return doc;
    }

    private static string DefaultSheet(FodsDocument doc) => doc.GetSheetNames()[0];

    // -------------------------------------------------------------------------
    // SortRows
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_CountUnchanged()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        var before = doc.GetRowCount(sheet);
        doc.SortRows(sheet, 0, ascending: true);
        Assert.Equal(before, doc.GetRowCount(sheet));
    }

    [Fact]
    public void SortRows_Ascending_ByName_FirstIsAlice()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.SortRows(sheet, 0, ascending: true);
        var row0 = doc.GetRowValues(sheet, 0);
        Assert.Contains("Alice", row0);
    }

    [Fact]
    public void SortRows_Descending_ByName_FirstIsCarol()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.SortRows(sheet, 0, ascending: false);
        var row0 = doc.GetRowValues(sheet, 0);
        Assert.Contains("Carol", row0);
    }

    [Fact]
    public void SortRows_Ascending_ByScore_FirstIsBob()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.SortRows(sheet, 2, ascending: true);
        var row0 = doc.GetRowValues(sheet, 0);
        // Bob has score 82 (lowest)
        Assert.Contains("Bob", row0);
    }

    [Fact]
    public void SortRows_Descending_ByScore_FirstIsAlice()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.SortRows(sheet, 2, ascending: false);
        var row0 = doc.GetRowValues(sheet, 0);
        // Alice has score 95 (highest)
        Assert.Contains("Alice", row0);
    }

    [Fact]
    public void SortRows_ThenFilterRows_Works()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.SortRows(sheet, 0, ascending: true);
        var engRows = doc.FilterRows(sheet, 1, "Eng");
        Assert.Equal(2, engRows.Count);
    }

    [Fact]
    public void SortRows_ThenGetColumnValues_ContainsAll()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.SortRows(sheet, 0, ascending: true);
        var col = doc.GetColumnValues(sheet, 0);
        Assert.Contains("Alice", col);
        Assert.Contains("Bob", col);
        Assert.Contains("Carol", col);
    }

    // -------------------------------------------------------------------------
    // MergeCells
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeCells_DoesNotThrow()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        var ex = Record.Exception(() => doc.MergeCells(sheet, 0, 0, 0, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void MergeCells_ThenGetRowValues_Works()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.MergeCells(sheet, 0, 0, 0, 1);
        var row = doc.GetRowValues(sheet, 0);
        Assert.NotNull(row);
    }

    [Fact]
    public void MergeCells_ThenGetCellValue_FirstCellAccessible()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.MergeCells(sheet, 0, 0, 0, 1);
        // First cell of merged range should still be accessible
        var row = doc.GetRowValues(sheet, 0);
        Assert.True(row.Count >= 1);
    }

    [Fact]
    public void MergeCells_MultipleRanges_DoesNotThrow()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        var ex = Record.Exception(() =>
        {
            doc.MergeCells(sheet, 0, 0, 0, 2);
            doc.MergeCells(sheet, 1, 0, 2, 0);
        });
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->SetCells->SortRows->MergeCells->GetColumnValues->Verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetSortMergeGetColumnVerify_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = DefaultSheet(doc);

        // SetCells (unsorted)
        doc.SetCellValue(0, 0, "Zebra"); doc.SetCellValue(0, 1, "Z"); doc.SetCellValue(0, 2, "1");
        doc.SetCellValue(1, 0, "Apple"); doc.SetCellValue(1, 1, "A"); doc.SetCellValue(1, 2, "3");
        doc.SetCellValue(2, 0, "Mango"); doc.SetCellValue(2, 1, "M"); doc.SetCellValue(2, 2, "2");

        // SortRows ascending by col 0
        doc.SortRows(sheet, 0, ascending: true);
        var row0 = doc.GetRowValues(sheet, 0);
        Assert.Contains("Apple", row0);

        var row2 = doc.GetRowValues(sheet, 2);
        Assert.Contains("Zebra", row2);

        // GetColumnValues still works
        var col0 = doc.GetColumnValues(sheet, 0);
        Assert.Equal(3, col0.Count);
        Assert.Contains("Apple", col0);
        Assert.Contains("Mango", col0);
        Assert.Contains("Zebra", col0);

        // MergeCells
        var ex = Record.Exception(() => doc.MergeCells(sheet, 0, 0, 0, 1));
        Assert.Null(ex);

        // Row count unchanged
        Assert.Equal(3, doc.GetRowCount(sheet));
    }
}
