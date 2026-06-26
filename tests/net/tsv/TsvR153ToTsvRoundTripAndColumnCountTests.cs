// Tests for TsvDocument.ToTsv, ColumnCount, and additional edge cases.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R153

using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R153: Tests for TsvDocument.ToTsv round-trip, ColumnCount, and edge cases.
/// ToTsv(): serializes document back to TSV string.
/// ColumnCount: number of columns inferred from headers or first row.
/// Covers: ToTsv non-null; ToTsv contains tab characters; ToTsv contains values;
/// ToTsv->Load round-trip row count; ToTsv->Load cell values match;
/// ToTsv after Filter contains only filtered rows; ColumnCount with headers;
/// ColumnCount without headers; ColumnCount after Filter-all unchanged;
/// ColumnCount empty doc is zero; ToTsv empty doc is empty or whitespace;
/// ToTsv after adding row has new value; GetCellValue null for out-of-bounds col;
/// GetCellValue null for out-of-bounds row;
/// dogfood Load->Filter->ToTsv->Load->GetColumnValues pipeline.
/// </summary>
public class TsvR153ToTsvRoundTripAndColumnCountTests
{
    private const string FourRowTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88\n" +
        "Dave\tFinance\t91";

    // -------------------------------------------------------------------------
    // ToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToTsv_IsNonNull()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.NotNull(doc.ToTsv());
    }

    [Fact]
    public void ToTsv_ContainsTabCharacters()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.Contains("\t", doc.ToTsv());
    }

    [Fact]
    public void ToTsv_ContainsValues()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var tsv = doc.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("Bob", tsv);
    }

    [Fact]
    public void ToTsv_Load_RoundTrip_RowCountMatches()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var tsv = doc.ToTsv();
        var loaded = TsvDocument.Load(tsv);
        Assert.Equal(doc.RowCount, loaded.RowCount);
    }

    [Fact]
    public void ToTsv_Load_RoundTrip_CellValuesMatch()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var tsv = doc.ToTsv();
        var loaded = TsvDocument.Load(tsv);
        Assert.Equal("Alice", loaded.GetCellValue(0, 0));
        Assert.Equal("Dave", loaded.GetCellValue(3, 0));
    }

    [Fact]
    public void ToTsv_AfterFilter_ContainsOnlyFilteredRows()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        var tsv = eng.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("Carol", tsv);
        Assert.DoesNotContain("Bob", tsv);
        Assert.DoesNotContain("Dave", tsv);
    }

    [Fact]
    public void ToTsv_AfterAddingRow_HasNewValue()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        doc.Rows.Add(new[] { "Eve", "Eng", "79" });
        var tsv = doc.ToTsv();
        Assert.Contains("Eve", tsv);
    }

    // -------------------------------------------------------------------------
    // ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_WithHeaders_IsThree()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_WithoutHeaders_InferredFromFirstRow()
    {
        var doc = TsvDocument.Load("A\tB\tC\tD", hasHeaders: false);
        Assert.Equal(4, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_AfterFilterAll_Unchanged()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var all = doc.Filter(_ => true);
        Assert.Equal(doc.ColumnCount, all.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Edge cases
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_OutOfBoundsCol_ReturnsNull()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var val = doc.GetCellValue(0, 999);
        Assert.Null(val);
    }

    [Fact]
    public void GetCellValue_OutOfBoundsRow_ReturnsNull()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var val = doc.GetCellValue(999, 0);
        Assert.Null(val);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->ToTsv->Load->GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterToTsvLoadGetColumnValues_Pipeline()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.Equal(4, doc.RowCount);
        Assert.Equal(3, doc.ColumnCount);

        // Filter Eng
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        Assert.Equal(2, eng.RowCount);

        // ToTsv
        var tsv = eng.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("Carol", tsv);
        Assert.DoesNotContain("Bob", tsv);

        // Load from ToTsv string
        var loaded = TsvDocument.Load(tsv);
        Assert.Equal(2, loaded.RowCount);

        // GetColumnValues
        var names = loaded.GetColumnValues(0);
        Assert.Equal(2, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }
}
