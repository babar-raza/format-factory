// Tests for FodsDocument.GetSheetByIndex, GetColumnValues, GetNumericColumnValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R188

using System.Linq;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R188: Tests for FodsDocument.GetSheetByIndex, GetColumnValues, GetNumericColumnValues deeper.
/// GetSheetByIndex(index): returns a sheet by index.
/// GetColumnValues(sheetName, col): returns all values in a column.
/// GetNumericColumnValues(sheetName, col): returns parsed numeric values.
/// Covers: GetSheetByIndex 0 returns first sheet; GetSheetByIndex name matches GetSheetNames[0];
/// GetColumnValues col0 count equals row count; GetColumnValues col0 contains values;
/// GetColumnValues col1 matches expected dept values; GetColumnValues non-numeric col;
/// GetNumericColumnValues skips non-numeric; GetNumericColumnValues count for all-numeric col;
/// GetColumnValues after InsertRowWithValues contains new value;
/// GetColumnValues after DeleteRows decrements; GetSheetByIndex after AddSheet;
/// GetColumnValues on multiple sheets; GetNumericColumnValues empty for text column;
/// dogfood CreateNew->SetCells->GetColumnValues->GetNumericColumnValues->GetSheetByIndex.
/// </summary>
public class FodsR188GetSheetByIndexAndColumnValuesTests
{
    private static FodsDocument CreateWithData()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, "Alice");
        doc.SetCellValue(0, 1, "Eng");
        doc.SetCellValue(0, 2, "95");
        doc.SetCellValue(1, 0, "Bob");
        doc.SetCellValue(1, 1, "Finance");
        doc.SetCellValue(1, 2, "82");
        doc.SetCellValue(2, 0, "Carol");
        doc.SetCellValue(2, 1, "Eng");
        doc.SetCellValue(2, 2, "88");
        return doc;
    }

    private static string DefaultSheet(FodsDocument doc) => doc.GetSheetNames()[0];

    // -------------------------------------------------------------------------
    // GetSheetByIndex
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetByIndex_Zero_ReturnsFirstSheet()
    {
        var doc = CreateWithData();
        var sheet = doc.GetSheetByIndex(0);
        Assert.NotNull(sheet);
    }

    [Fact]
    public void GetSheetByIndex_Zero_NameMatchesGetSheetNames()
    {
        var doc = CreateWithData();
        var sheet = doc.GetSheetByIndex(0);
        var expected = doc.GetSheetNames()[0];
        Assert.Equal(expected, sheet!.Name);
    }

    [Fact]
    public void GetSheetByIndex_AfterAddSheet_IndexOneReturnsNewSheet()
    {
        var doc = CreateWithData();
        doc.AddSheet("SecondSheet");
        var sheet = doc.GetSheetByIndex(1);
        Assert.NotNull(sheet);
        Assert.Equal("SecondSheet", sheet!.Name);
    }

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_Col0_CountEqualsRowCount()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var col = doc.GetColumnValues(sheetName, 0);
        Assert.Equal(3, col.Count);
    }

    [Fact]
    public void GetColumnValues_Col0_ContainsValues()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var col = doc.GetColumnValues(sheetName, 0);
        Assert.Contains("Alice", col);
        Assert.Contains("Bob", col);
        Assert.Contains("Carol", col);
    }

    [Fact]
    public void GetColumnValues_Col1_MatchesDeptValues()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var col = doc.GetColumnValues(sheetName, 1);
        Assert.Contains("Eng", col);
        Assert.Contains("Finance", col);
    }

    [Fact]
    public void GetColumnValues_AfterInsertRowWithValues_ContainsNewValue()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        doc.InsertRowWithValues(sheetName, 3, new[] { "Dave", "Finance", "91" });
        var col = doc.GetColumnValues(sheetName, 0);
        Assert.Contains("Dave", col);
    }

    [Fact]
    public void GetColumnValues_AfterDeleteRows_CountDecreases()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        doc.DeleteRows(sheetName, 0, 1);
        var col = doc.GetColumnValues(sheetName, 0);
        Assert.Equal(2, col.Count);
    }

    // -------------------------------------------------------------------------
    // GetNumericColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumericColumnValues_AllNumericCol_CountEqualsRowCount()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var nums = doc.GetNumericColumnValues(sheetName, 2);
        Assert.Equal(3, nums.Count);
    }

    [Fact]
    public void GetNumericColumnValues_Values_Correct()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var nums = doc.GetNumericColumnValues(sheetName, 2);
        Assert.Contains(95.0, nums);
        Assert.Contains(82.0, nums);
        Assert.Contains(88.0, nums);
    }

    [Fact]
    public void GetNumericColumnValues_TextColumn_ReturnsEmpty()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        // Column 0 is text (names) — all non-numeric
        var nums = doc.GetNumericColumnValues(sheetName, 0);
        Assert.Empty(nums);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->SetCells->GetColumnValues->GetNumericColumnValues->GetSheetByIndex
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetGetColumnValuesGetNumericGetSheetByIndex_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.GetSheetNames()[0];

        // Set cells
        doc.SetCellValue(0, 0, "X");
        doc.SetCellValue(0, 1, "10");
        doc.SetCellValue(1, 0, "Y");
        doc.SetCellValue(1, 1, "20");
        doc.SetCellValue(2, 0, "Z");
        doc.SetCellValue(2, 1, "30");

        // GetColumnValues col0
        var names = doc.GetColumnValues(sheetName, 0);
        Assert.Equal(3, names.Count);
        Assert.Contains("X", names);

        // GetColumnValues col1
        var scores = doc.GetColumnValues(sheetName, 1);
        Assert.Equal(3, scores.Count);
        Assert.Contains("10", scores);

        // GetNumericColumnValues col1
        var nums = doc.GetNumericColumnValues(sheetName, 1);
        Assert.Equal(3, nums.Count);
        Assert.Equal(60.0, nums.Sum(), 0);

        // GetSheetByIndex
        var sheet = doc.GetSheetByIndex(0);
        Assert.NotNull(sheet);
        Assert.Equal(sheetName, sheet!.Name);
    }
}
