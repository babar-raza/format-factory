// Tests for TsvDocument.HasHeaders, GetCellValue, and headers-false loading.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R154

using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R154: Tests for TsvDocument.HasHeaders, GetCellValue, and no-header loading.
/// HasHeaders: indicates whether first row was parsed as headers.
/// GetCellValue(row, col): returns string cell value or null.
/// Load(content, hasHeaders=false): treats all rows as data rows.
/// Covers: HasHeaders true after Load with headers; HasHeaders false when loaded no-headers;
/// GetCellValue valid coordinates returns value; GetCellValue col out-of-bounds returns null;
/// GetCellValue row out-of-bounds returns null; GetCellValue first cell;
/// GetCellValue last cell; GetCellValue middle cell;
/// Load hasHeaders=false RowCount includes all rows; Load hasHeaders=false cell [0,0];
/// ColumnCount with hasHeaders=false; GetColumnValues hasHeaders=false;
/// Filter then GetCellValue; Filter then RowCount;
/// dogfood Load->GetCellValue->Filter->GetCellValue pipeline.
/// </summary>
public class TsvR154HasHeadersAndGetCellValueTests
{
    private const string ThreeRowTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88";

    // -------------------------------------------------------------------------
    // HasHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void HasHeaders_TrueAfterLoadWithHeaders()
    {
        var doc = TsvDocument.Load(ThreeRowTsv, hasHeaders: true);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void HasHeaders_FalseWhenLoadedNoHeaders()
    {
        var doc = TsvDocument.Load(ThreeRowTsv, hasHeaders: false);
        Assert.False(doc.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // GetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_ValidCoordinates_ReturnsValue()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void GetCellValue_ColOutOfBounds_ReturnsNull()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Null(doc.GetCellValue(0, 100));
    }

    [Fact]
    public void GetCellValue_RowOutOfBounds_ReturnsNull()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Null(doc.GetCellValue(100, 0));
    }

    [Fact]
    public void GetCellValue_FirstCell_Correct()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void GetCellValue_LastCell_Correct()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("88", doc.GetCellValue(2, 2));
    }

    [Fact]
    public void GetCellValue_MiddleCell_Correct()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("Finance", doc.GetCellValue(1, 1));
    }

    // -------------------------------------------------------------------------
    // Load hasHeaders=false
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_HasHeadersFalse_RowCountIncludesAllRows()
    {
        // ThreeRowTsv has 4 lines total (1 header + 3 data)
        // With hasHeaders=false, all 4 lines become data rows
        var doc = TsvDocument.Load(ThreeRowTsv, hasHeaders: false);
        Assert.Equal(4, doc.RowCount);
    }

    [Fact]
    public void Load_HasHeadersFalse_FirstCell_IsHeaderValue()
    {
        var doc = TsvDocument.Load(ThreeRowTsv, hasHeaders: false);
        // First row is "Name\tDept\tScore"
        Assert.Equal("Name", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void Load_HasHeadersFalse_ColumnCount_InferredFromFirstRow()
    {
        var doc = TsvDocument.Load(ThreeRowTsv, hasHeaders: false);
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void GetColumnValues_HasHeadersFalse_IncludesHeaderAsData()
    {
        var doc = TsvDocument.Load(ThreeRowTsv, hasHeaders: false);
        var col = doc.GetColumnValues(0);
        Assert.Contains("Name", col); // header treated as data
        Assert.Contains("Alice", col);
    }

    // -------------------------------------------------------------------------
    // Filter then GetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_ThenGetCellValue_ReturnsFilteredValue()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        Assert.Equal("Alice", eng.GetCellValue(0, 0));
    }

    [Fact]
    public void Filter_ThenRowCount_IsCorrect()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        Assert.Equal(2, eng.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->GetCellValue->Filter->GetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadGetCellValueFilterGetCellValue_Pipeline()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.True(doc.HasHeaders);
        Assert.Equal(3, doc.RowCount);

        // GetCellValue for each row
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
        Assert.Equal("Eng", doc.GetCellValue(0, 1));
        Assert.Equal("95", doc.GetCellValue(0, 2));
        Assert.Equal("Bob", doc.GetCellValue(1, 0));
        Assert.Equal("Carol", doc.GetCellValue(2, 0));

        // GetCellValue edge cases
        Assert.Null(doc.GetCellValue(0, 99));
        Assert.Null(doc.GetCellValue(99, 0));

        // Filter
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        Assert.Equal(2, eng.RowCount);
        Assert.Equal("Alice", eng.GetCellValue(0, 0));
        Assert.Equal("Carol", eng.GetCellValue(1, 0));

        // GetColumnValues on filtered
        var col = eng.GetColumnValues(0);
        Assert.Contains("Alice", col);
        Assert.Contains("Carol", col);
        Assert.DoesNotContain("Bob", col);
    }
}
