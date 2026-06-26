// Tests for CsvDocument.ToCsv, ColumnCount, Headers, IsEmpty deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R162

using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R162: Tests for CsvDocument.ToCsv, ColumnCount, Headers, IsEmpty deeper coverage.
/// ToCsv(): serializes document to CSV string.
/// ColumnCount: number of columns.
/// Headers: list of header names.
/// IsEmpty: whether document has no rows.
/// Covers: ToCsv non-null for non-empty doc; ToCsv non-empty string;
/// ToCsv contains all headers; ToCsv contains all data values;
/// ToCsv->Load round-trip count; ToCsv->Load field values;
/// ColumnCount positive; ColumnCount matches headers count;
/// ColumnCount single column; Headers non-null; Headers contains names;
/// Headers order preserved; IsEmpty true for empty; IsEmpty false for data;
/// ToCsv after mutation; ColumnCount after AddRow unchanged;
/// dogfood Load->ToCsv->Load->GetColumn->Filter->ToCsv->Load verify.
/// </summary>
public class CsvR162ToCsvAndColumnCountTests
{
    private const string ThreeRowCsv =
        "name,dept,score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88";

    // -------------------------------------------------------------------------
    // ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsv_NonNull()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.NotNull(doc.ToCsv());
    }

    [Fact]
    public void ToCsv_NonEmpty()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.False(string.IsNullOrWhiteSpace(doc.ToCsv()));
    }

    [Fact]
    public void ToCsv_ContainsHeaders()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var csv = doc.ToCsv();
        Assert.Contains("name", csv);
        Assert.Contains("dept", csv);
        Assert.Contains("score", csv);
    }

    [Fact]
    public void ToCsv_ContainsDataValues()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var csv = doc.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("Bob", csv);
        Assert.Contains("Carol", csv);
    }

    [Fact]
    public void ToCsv_Load_RoundTrip_CountMatches()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var csv = doc.ToCsv();
        var loaded = CsvDocument.Load(csv);
        Assert.Equal(3, loaded.RowCount);
    }

    [Fact]
    public void ToCsv_Load_RoundTrip_FieldValues()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var csv = doc.ToCsv();
        var loaded = CsvDocument.Load(csv);
        var names = loaded.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void ToCsv_AfterMutation_ContainsNewValue()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.SetCellValue(0, 0, "Alicia");
        var csv = doc.ToCsv();
        Assert.Contains("Alicia", csv);
    }

    // -------------------------------------------------------------------------
    // ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_PositiveForData()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.True(doc.ColumnCount > 0);
    }

    [Fact]
    public void ColumnCount_ThreeForThreeColumns()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_MatchesHeadersCount()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal(doc.Headers.Count, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_SingleColumn()
    {
        var doc = CsvDocument.Load("id\n1\n2\n3");
        Assert.Equal(1, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_AfterAddRow_Unchanged()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var before = doc.ColumnCount;
        doc.AddRow(new[] { "Dave", "HR", "77" });
        Assert.Equal(before, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Headers
    // -------------------------------------------------------------------------

    [Fact]
    public void Headers_NonNull()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.NotNull(doc.Headers);
    }

    [Fact]
    public void Headers_ContainsExpectedNames()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Contains("name", doc.Headers);
        Assert.Contains("dept", doc.Headers);
        Assert.Contains("score", doc.Headers);
    }

    [Fact]
    public void Headers_OrderPreserved()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal("name", doc.Headers[0]);
        Assert.Equal("dept", doc.Headers[1]);
        Assert.Equal("score", doc.Headers[2]);
    }

    // -------------------------------------------------------------------------
    // IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmpty_TrueForEmptyDoc()
    {
        var doc = CsvDocument.Load("name,dept\n");
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_FalseForDataDoc()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.False(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->ToCsv->Load->GetColumn->Filter->ToCsv->Load verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadToCsvLoadGetColumnFilterToCsvLoad_Verify()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal(3, doc.ColumnCount);
        Assert.Equal(3, doc.Headers.Count);
        Assert.False(doc.IsEmpty);

        // ToCsv -> Load
        var csv1 = doc.ToCsv();
        var doc2 = CsvDocument.Load(csv1);
        Assert.Equal(3, doc2.RowCount);
        Assert.Equal(3, doc2.ColumnCount);

        // GetColumn
        var names = doc2.GetColumn("name");
        Assert.Equal(3, names.Count);

        // Filter
        var eng = doc2.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);

        // ToCsv -> Load
        var csv2 = eng.ToCsv();
        var doc3 = CsvDocument.Load(csv2);
        Assert.Equal(2, doc3.RowCount);
        Assert.False(doc3.IsEmpty);
        var engNames = doc3.GetColumn("name");
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);
    }
}
