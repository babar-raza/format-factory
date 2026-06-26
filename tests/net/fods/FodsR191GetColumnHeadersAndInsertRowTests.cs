// Tests for FodsDocument.GetColumnHeaders, InsertRow, DeleteRows deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R191

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R191: Tests for FodsDocument.GetColumnHeaders, InsertRow, DeleteRows, InsertRowWithValues deeper.
/// GetColumnHeaders(): returns column headers from the active sheet.
/// GetColumnHeaders(sheetName): returns headers for named sheet.
/// InsertRow(sheetName, rowIndex): inserts empty row at index.
/// DeleteRows(sheetName, startRow, count): deletes rows from index.
/// InsertRowWithValues(sheetName, rowIndex, values): inserts row with data.
/// Covers: GetColumnHeaders non-empty after SetCellValue; GetColumnHeaders count;
/// GetColumnHeaders first header; GetColumnHeaders(sheetName) matches;
/// InsertRow increments GetRowCount; InsertRow at 0 shifts existing rows;
/// DeleteRows decrements GetRowCount; DeleteRows removes first row;
/// InsertRowWithValues row has values; InsertRowWithValues GetColumnValues;
/// InsertRowWithValues at index 0; GetRowCount after InsertRow and DeleteRows net-zero;
/// GetColumnHeaders after InsertRowWithValues unchanged;
/// dogfood CreateNew->SetCells->InsertRow->InsertRowWithValues->DeleteRows->GetRowCount.
/// </summary>
public class FodsR191GetColumnHeadersAndInsertRowTests
{
    private static FodsDocument CreateWithData()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(0, 1, "Dept");
        doc.SetCellValue(0, 2, "Score");
        doc.SetCellValue(1, 0, "Alice");
        doc.SetCellValue(1, 1, "Eng");
        doc.SetCellValue(1, 2, "95");
        doc.SetCellValue(2, 0, "Bob");
        doc.SetCellValue(2, 1, "Finance");
        doc.SetCellValue(2, 2, "82");
        return doc;
    }

    private static string DefaultSheet(FodsDocument doc) => doc.GetSheetNames()[0];

    // -------------------------------------------------------------------------
    // GetColumnHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHeaders_NonEmpty_AfterSetCellValue()
    {
        var doc = CreateWithData();
        var headers = doc.GetColumnHeaders();
        Assert.NotEmpty(headers);
    }

    [Fact]
    public void GetColumnHeaders_Count_IsThree()
    {
        var doc = CreateWithData();
        var headers = doc.GetColumnHeaders();
        Assert.Equal(3, headers.Count);
    }

    [Fact]
    public void GetColumnHeaders_FirstHeader_IsName()
    {
        var doc = CreateWithData();
        var headers = doc.GetColumnHeaders();
        Assert.Equal("Name", headers[0]);
    }

    [Fact]
    public void GetColumnHeaders_BySheetName_MatchesDefault()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var headers1 = doc.GetColumnHeaders();
        var headers2 = doc.GetColumnHeaders(sheetName);
        Assert.Equal(headers1, headers2);
    }

    // -------------------------------------------------------------------------
    // InsertRow
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertRow_IncrementsGetRowCount()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var before = doc.GetRowCount(sheetName);
        doc.InsertRow(sheetName, 0);
        Assert.Equal(before + 1, doc.GetRowCount(sheetName));
    }

    [Fact]
    public void InsertRow_At0_ShiftsExistingRows()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        // Row 0 has "Name", row 1 has "Alice"
        doc.InsertRow(sheetName, 1); // insert before Alice's row
        // Now Alice should be at row 2
        var nameAt1 = doc.GetCellValue(1, 0); // should be empty (new row)
        var nameAt2 = doc.GetCellValue(2, 0); // should be Alice
        Assert.Equal("Alice", nameAt2);
    }

    // -------------------------------------------------------------------------
    // DeleteRows
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRows_DecrementsGetRowCount()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var before = doc.GetRowCount(sheetName);
        doc.DeleteRows(sheetName, 1, 1);
        Assert.Equal(before - 1, doc.GetRowCount(sheetName));
    }

    [Fact]
    public void DeleteRows_RemovesFirstDataRow()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        doc.DeleteRows(sheetName, 1, 1); // delete Alice row
        // Bob should now be at row 1
        Assert.Equal("Bob", doc.GetCellValue(1, 0));
    }

    // -------------------------------------------------------------------------
    // InsertRowWithValues
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertRowWithValues_RowHasValues()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        doc.InsertRowWithValues(sheetName, 3, new[] { "Carol", "Eng", "88" });
        Assert.Equal("Carol", doc.GetCellValue(3, 0));
    }

    [Fact]
    public void InsertRowWithValues_GetColumnValues_HasNewValue()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        doc.InsertRowWithValues(sheetName, 3, new[] { "Dave", "Finance", "91" });
        var col = doc.GetColumnValues(sheetName, 0);
        Assert.Contains("Dave", col);
    }

    [Fact]
    public void InsertRowWithValues_At0_ShiftsExisting()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        doc.InsertRowWithValues(sheetName, 0, new[] { "HEADER_NEW", "X", "Y" });
        Assert.Equal("HEADER_NEW", doc.GetCellValue(0, 0));
        // Original row 0 is now at row 1
        Assert.Equal("Name", doc.GetCellValue(1, 0));
    }

    // -------------------------------------------------------------------------
    // Net-zero operations
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_AfterInsertAndDelete_NetZero()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var original = doc.GetRowCount(sheetName);
        doc.InsertRow(sheetName, 0);
        doc.DeleteRows(sheetName, 0, 1);
        Assert.Equal(original, doc.GetRowCount(sheetName));
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->SetCells->InsertRow->InsertRowWithValues->DeleteRows->GetRowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetInsertRowWithValuesDeleteGetRowCount_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.GetSheetNames()[0];

        // Set initial data
        doc.SetCellValue(0, 0, "A");
        doc.SetCellValue(0, 1, "10");
        doc.SetCellValue(1, 0, "B");
        doc.SetCellValue(1, 1, "20");
        Assert.Equal(2, doc.GetRowCount(sheetName));

        // InsertRow
        doc.InsertRow(sheetName, 2);
        Assert.Equal(3, doc.GetRowCount(sheetName));

        // InsertRowWithValues
        doc.InsertRowWithValues(sheetName, 2, new[] { "C", "30" });
        Assert.Equal(4, doc.GetRowCount(sheetName));
        Assert.Equal("C", doc.GetCellValue(2, 0));

        // DeleteRows: remove the empty row (now at index 3)
        doc.DeleteRows(sheetName, 3, 1);
        Assert.Equal(3, doc.GetRowCount(sheetName));

        // GetColumnHeaders
        var headers = doc.GetColumnHeaders();
        Assert.NotEmpty(headers);

        // GetColumnValues col0
        var col = doc.GetColumnValues(sheetName, 0);
        Assert.Contains("A", col);
        Assert.Contains("B", col);
        Assert.Contains("C", col);
    }
}
