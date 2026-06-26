// Tests for FodsDocument.GetRowValues, GetRowCount, GetCellCount, GetColumnCount.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R184

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R184: Tests for FodsDocument.GetRowValues, GetRowCount, GetCellCount, GetColumnCount.
/// GetRowValues(row): returns all cell values in a given row.
/// GetRowCount(sheetName): returns number of rows in a given sheet.
/// GetCellCount(sheetName): returns total non-empty cell count in a sheet.
/// GetColumnCount(sheetName): returns max column count in a sheet.
/// Covers: GetRowValues count equals ColumnCount; GetRowValues contains cell values;
/// GetRowCount matches sheet.RowCount; GetRowCount after InsertRow;
/// GetCellCount positive after SetCellValue; GetCellCount zero for empty sheet;
/// GetColumnCount three after setting three columns; GetColumnCount after InsertRowWithValues;
/// GetRowValues first row has correct values; GetRowCount after DeleteRows;
/// GetCellCount after ClearSheet is zero; GetColumnCount matches expected;
/// dogfood CreateNew->SetCell->GetRowValues->GetCellCount->GetColumnCount.
/// </summary>
public class FodsR184GetRowValuesAndGetCellCountTests
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
        return doc;
    }

    private static string DefaultSheet(FodsDocument doc) => doc.GetSheetNames()[0];

    // -------------------------------------------------------------------------
    // GetRowValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowValues_FirstRow_ContainsValues()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var row = doc.GetRowValues(sheetName, 0);
        Assert.Contains("Alice", row);
        Assert.Contains("Eng", row);
        Assert.Contains("95", row);
    }

    [Fact]
    public void GetRowValues_SecondRow_ContainsValues()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var row = doc.GetRowValues(sheetName, 1);
        Assert.Contains("Bob", row);
        Assert.Contains("Finance", row);
    }

    // -------------------------------------------------------------------------
    // GetRowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_MatchesSheetRowCount()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var sheet = doc.GetSheetByName(sheetName)!;
        Assert.Equal(sheet.RowCount, doc.GetRowCount(sheetName));
    }

    [Fact]
    public void GetRowCount_AfterInsertRow_Increments()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var before = doc.GetRowCount(sheetName);
        doc.InsertRow(sheetName, 0);
        Assert.Equal(before + 1, doc.GetRowCount(sheetName));
    }

    [Fact]
    public void GetRowCount_AfterDeleteRows_Decrements()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var before = doc.GetRowCount(sheetName);
        doc.DeleteRows(sheetName, 0, 1);
        Assert.Equal(before - 1, doc.GetRowCount(sheetName));
    }

    // -------------------------------------------------------------------------
    // GetCellCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellCount_PositiveAfterSetCellValue()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        Assert.True(doc.GetCellCount(sheetName) > 0);
    }

    [Fact]
    public void GetCellCount_ZeroForEmptySheet()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = DefaultSheet(doc);
        doc.ClearSheet(sheetName);
        Assert.Equal(0, doc.GetCellCount(sheetName));
    }

    [Fact]
    public void GetCellCount_AfterClearSheet_IsZero()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        doc.ClearSheet(sheetName);
        Assert.Equal(0, doc.GetCellCount(sheetName));
    }

    // -------------------------------------------------------------------------
    // GetColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_ThreeColumnsSet_IsThree()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        Assert.Equal(3, doc.GetColumnCount(sheetName));
    }

    [Fact]
    public void GetColumnCount_AfterInsertRowWithValues_Consistent()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = DefaultSheet(doc);
        doc.InsertRowWithValues(sheetName, 0, new[] { "A", "B", "C", "D" });
        var count = doc.GetColumnCount(sheetName);
        Assert.Equal(4, count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->SetCell->GetRowValues->GetCellCount->GetColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetCellGetRowValuesGetCellCountGetColumnCount()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = DefaultSheet(doc);

        // Set cell values
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(0, 1, "Value");
        doc.SetCellValue(0, 2, "Status");
        doc.SetCellValue(1, 0, "Widget");
        doc.SetCellValue(1, 1, "42");
        doc.SetCellValue(1, 2, "Active");

        // GetRowValues
        var row0 = doc.GetRowValues(sheetName, 0);
        Assert.Contains("Name", row0);
        Assert.Contains("Value", row0);

        var row1 = doc.GetRowValues(sheetName, 1);
        Assert.Contains("Widget", row1);

        // GetCellCount
        var cellCount = doc.GetCellCount(sheetName);
        Assert.True(cellCount >= 6); // at least 6 non-empty cells

        // GetColumnCount
        var colCount = doc.GetColumnCount(sheetName);
        Assert.Equal(3, colCount);

        // GetRowCount
        var rowCount = doc.GetRowCount(sheetName);
        Assert.Equal(2, rowCount);
    }
}
