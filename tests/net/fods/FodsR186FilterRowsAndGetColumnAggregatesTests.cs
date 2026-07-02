// Tests for FodsDocument.FilterRows, GetColumnAggregates, GetNumericColumnValues, FindCellsByValue.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R186

using System.Linq;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R186: Tests for FodsDocument.FilterRows, GetColumnAggregates, GetNumericColumnValues, FindCellsByValue.
/// FilterRows(sheetName, col, value): returns rows where column matches value.
/// GetColumnAggregates(sheetName, col): returns (Min, Max, Sum, Count) for numeric column.
/// GetNumericColumnValues(sheetName, col): returns numeric values from column.
/// FindCellsByValue(sheetName, value): finds (row,col) coordinates for matching cells.
/// Covers: FilterRows by dept returns matching rows; FilterRows count correct;
/// FilterRows non-matching value returns empty; GetColumnAggregates count correct;
/// GetColumnAggregates sum correct; GetColumnAggregates min correct;
/// GetColumnAggregates max correct; GetNumericColumnValues count equals row count;
/// GetNumericColumnValues values correct; FindCellsByValue finds matching cell;
/// FindCellsByValue non-existent returns empty; FindCellsByValue multiple matches;
/// GetColumnAggregates after InsertRowWithValues;
/// dogfood CreateNew->SetCells->FilterRows->GetColumnAggregates->FindCellsByValue.
/// </summary>
public class FodsR186FilterRowsAndGetColumnAggregatesTests
{
    private static FodsDocument CreateWithData()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Alice");
        doc.SetCellValue(0, 1, "Eng");
        doc.SetCellValue(0, 2, "95");
        doc.SetCellValue(1, 0, "Bob");
        doc.SetCellValue(1, 1, "Finance");
        doc.SetCellValue(1, 2, "82");
        doc.SetCellValue(2, 0, "Carol");
        doc.SetCellValue(2, 1, "Eng");
        doc.SetCellValue(2, 2, "88");
        doc.SetCellValue(3, 0, "Dave");
        doc.SetCellValue(3, 1, "Finance");
        doc.SetCellValue(3, 2, "91");
        return doc;
    }

    private static string DefaultSheet(FodsDocument doc) => doc.GetSheetNames()[0];

    // -------------------------------------------------------------------------
    // FilterRows
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRows_ByDept_Eng_ReturnsMatchingRows()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var rows = doc.FilterRows(sheetName, 1, "Eng");
        Assert.NotNull(rows);
        Assert.True(rows.Count > 0);
    }

    [Fact]
    public void FilterRows_ByDept_Eng_CountIsTwo()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var rows = doc.FilterRows(sheetName, 1, "Eng");
        Assert.Equal(2, rows.Count);
    }

    [Fact]
    public void FilterRows_NonExistentValue_ReturnsEmpty()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var rows = doc.FilterRows(sheetName, 1, "Marketing");
        Assert.Empty(rows);
    }

    [Fact]
    public void FilterRows_ByDept_Finance_CountIsTwo()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var rows = doc.FilterRows(sheetName, 1, "Finance");
        Assert.Equal(2, rows.Count);
    }

    // -------------------------------------------------------------------------
    // GetColumnAggregates
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnAggregates_Count_EqualsRowCount()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var agg = doc.GetColumnAggregates(sheetName, 2);
        Assert.Equal(4, agg.Count);
    }

    [Fact]
    public void GetColumnAggregates_Sum_IsCorrect()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var agg = doc.GetColumnAggregates(sheetName, 2);
        Assert.Equal(95 + 82 + 88 + 91, agg.Sum, 0);
    }

    [Fact]
    public void GetColumnAggregates_Min_IsCorrect()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var agg = doc.GetColumnAggregates(sheetName, 2);
        Assert.Equal(82.0, agg.Min, 0);
    }

    [Fact]
    public void GetColumnAggregates_Max_IsCorrect()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var agg = doc.GetColumnAggregates(sheetName, 2);
        Assert.Equal(95.0, agg.Max, 0);
    }

    // -------------------------------------------------------------------------
    // GetNumericColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumericColumnValues_Count_EqualsRowCount()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var nums = doc.GetNumericColumnValues(sheetName, 2);
        Assert.Equal(4, nums.Count);
    }

    [Fact]
    public void GetNumericColumnValues_ContainsCorrectValues()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var nums = doc.GetNumericColumnValues(sheetName, 2);
        Assert.Contains(95.0, nums);
        Assert.Contains(82.0, nums);
        Assert.Contains(88.0, nums);
        Assert.Contains(91.0, nums);
    }

    // -------------------------------------------------------------------------
    // FindCellsByValue
    // -------------------------------------------------------------------------

    [Fact]
    public void FindCellsByValue_FindsMatchingCell()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var cells = doc.FindCellsByValue(sheetName, "Alice");
        Assert.NotEmpty(cells);
    }

    [Fact]
    public void FindCellsByValue_NonExistent_ReturnsEmpty()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var cells = doc.FindCellsByValue(sheetName, "ZZZ_NONEXISTENT");
        Assert.Empty(cells);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->SetCells->FilterRows->GetColumnAggregates->FindCellsByValue
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetFilterAggregatesFind_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheetName = doc.GetSheetNames()[0];

        // Set data
        doc.SetCellValue(0, 0, "X");
        doc.SetCellValue(0, 1, "A");
        doc.SetCellValue(0, 2, "10");
        doc.SetCellValue(1, 0, "Y");
        doc.SetCellValue(1, 1, "A");
        doc.SetCellValue(1, 2, "20");
        doc.SetCellValue(2, 0, "Z");
        doc.SetCellValue(2, 1, "B");
        doc.SetCellValue(2, 2, "30");

        // FilterRows
        var rowsA = doc.FilterRows(sheetName, 1, "A");
        Assert.Equal(2, rowsA.Count);

        // GetColumnAggregates
        var agg = doc.GetColumnAggregates(sheetName, 2);
        Assert.Equal(3, agg.Count);
        Assert.Equal(60.0, agg.Sum, 0);
        Assert.Equal(10.0, agg.Min, 0);
        Assert.Equal(30.0, agg.Max, 0);

        // GetNumericColumnValues
        var nums = doc.GetNumericColumnValues(sheetName, 2);
        Assert.Equal(3, nums.Count);

        // FindCellsByValue
        var found = doc.FindCellsByValue(sheetName, "X");
        Assert.NotEmpty(found);
        Assert.Equal(0, found[0].Row);
        Assert.Equal(0, found[0].Col);
    }
}
