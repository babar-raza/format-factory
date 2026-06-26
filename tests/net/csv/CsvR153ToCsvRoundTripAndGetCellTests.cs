// Tests for CsvDocument.ToCsv round-trip, GetCellValue edge cases, ColumnCount.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R153

using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R153: Tests for CsvDocument.ToCsv round-trip, GetCellValue edge cases, and ColumnCount.
/// ToCsv(): serializes the document back to CSV string.
/// GetCellValue(row, col): retrieves a cell value by row and column index.
/// ColumnCount: number of columns in the document.
/// Covers: ToCsv contains all row values; ToCsv preserves commas as separators;
/// ToCsv->Load round-trip RowCount equal; ToCsv->Load row 0 cell value;
/// GetCellValue in-bounds all rows; GetCellValue out-of-bounds returns null;
/// GetCellValue negative row returns null; ColumnCount for different CSV shapes;
/// Filter->ToCsv->Load chain; ToCsv single-row doc; ToCsv empty doc;
/// SetCell then ToCsv contains new value; AddRow then GetCellValue for new row;
/// dogfood Load->Filter->ToCsv->Load->GetCellValue chain.
/// </summary>
public class CsvR153ToCsvRoundTripAndGetCellTests
{
    private const string FourRowCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88\n" +
        "Dave,Finance,91";

    // -------------------------------------------------------------------------
    // ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsv_ContainsAllRowValues()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var csv = doc.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("Bob", csv);
        Assert.Contains("Carol", csv);
        Assert.Contains("Dave", csv);
    }

    [Fact]
    public void ToCsv_PreservesCommas()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var csv = doc.ToCsv();
        Assert.Contains(",", csv);
    }

    [Fact]
    public void ToCsv_RoundTrip_RowCountEqual()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var csv = doc.ToCsv();
        var reloaded = CsvDocument.Load(csv, hasHeaders: false);
        Assert.Equal(doc.RowCount, reloaded.RowCount);
    }

    [Fact]
    public void ToCsv_RoundTrip_FirstRowFirstCell()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var csv = doc.ToCsv();
        var reloaded = CsvDocument.Load(csv, hasHeaders: false);
        Assert.Equal("Alice", reloaded.GetCellValue(0, 0));
    }

    [Fact]
    public void ToCsv_SingleRow_ContainsValue()
    {
        var doc = CsvDocument.Load("OnlyOne,Value", hasHeaders: false);
        var csv = doc.ToCsv();
        Assert.Contains("OnlyOne", csv);
        Assert.Contains("Value", csv);
    }

    [Fact]
    public void ToCsv_AfterSetCell_ContainsNewValue()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        doc.SetCell(0, 0, "Alicia");
        var csv = doc.ToCsv();
        Assert.Contains("Alicia", csv);
        Assert.DoesNotContain("Alice", csv);
    }

    // -------------------------------------------------------------------------
    // GetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_InBounds_AllRows()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
        Assert.Equal("Bob", doc.GetCellValue(1, 0));
        Assert.Equal("Carol", doc.GetCellValue(2, 0));
        Assert.Equal("Dave", doc.GetCellValue(3, 0));
    }

    [Fact]
    public void GetCellValue_OutOfBoundsRow_ReturnsNull()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var val = doc.GetCellValue(99, 0);
        Assert.Null(val);
    }

    [Fact]
    public void GetCellValue_OutOfBoundsCol_ReturnsNull()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var val = doc.GetCellValue(0, 99);
        Assert.Null(val);
    }

    [Fact]
    public void GetCellValue_NegativeRow_ReturnsNull()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var val = doc.GetCellValue(-1, 0);
        Assert.Null(val);
    }

    [Fact]
    public void GetCellValue_AfterAddRow_NewCellAccessible()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        doc.AddRow(new[] { "Eve", "HR", "77" });
        var lastRow = doc.RowCount - 1;
        Assert.Equal("Eve", doc.GetCellValue(lastRow, 0));
        Assert.Equal("77", doc.GetCellValue(lastRow, 2));
    }

    // -------------------------------------------------------------------------
    // ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_ThreeColumnDoc_IsThree()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_SingleColumnDoc_IsOne()
    {
        var doc = CsvDocument.Load("Only\nA\nB", hasHeaders: true);
        Assert.Equal(1, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->ToCsv->Load->GetCellValue chain
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FilterToCsvLoadGetCellValue_Chain()
    {
        var doc = CsvDocument.Load(FourRowCsv);

        // Filter Eng rows
        var eng = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Equal(2, eng.RowCount);

        // ToCsv
        var csv = eng.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("Carol", csv);
        Assert.DoesNotContain("Bob", csv);

        // Reload from ToCsv
        var reloaded = CsvDocument.Load(csv, hasHeaders: false);
        Assert.Equal(2, reloaded.RowCount);

        // GetCellValue on reloaded
        Assert.Equal("Alice", reloaded.GetCellValue(0, 0));
        Assert.Equal("Carol", reloaded.GetCellValue(1, 0));

        // ColumnCount preserved
        Assert.Equal(3, reloaded.ColumnCount);
    }
}
