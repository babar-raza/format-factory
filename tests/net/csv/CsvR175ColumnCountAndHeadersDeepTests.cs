// Tests for CsvDocument.ColumnCount, Headers deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R175

using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R175: Tests for CsvDocument.ColumnCount, Headers deeper coverage.
/// ColumnCount: number of columns in the document.
/// Headers: IReadOnlyList of column header strings.
/// HasHeaders: true when headers are present.
/// Covers: ColumnCount equals header count after Load; ColumnCount after CreateEmpty(headers);
/// ColumnCount preserved after AddRow; ColumnCount preserved after Filter;
/// ColumnCount preserved after SetCellValue; Headers non-null when HasHeaders;
/// Headers order preserved; Headers count equals ColumnCount;
/// Headers contains all expected values; Headers after CreateEmpty(headers);
/// HasHeaders true after Load with header row; HasHeaders preserved after Filter;
/// HasHeaders preserved after AddRow;
/// dogfood Load->ColumnCount->Headers->Filter->ColumnCount->Headers->verify pipeline.
/// </summary>
public class CsvR175ColumnCountAndHeadersDeepTests
{
    private const string FourColCsv =
        "id,name,dept,score\n" +
        "1,Alice,Eng,95\n" +
        "2,Bob,Finance,82\n" +
        "3,Carol,Eng,88";

    // -------------------------------------------------------------------------
    // ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_EqualsHeaderCount_AfterLoad()
    {
        var doc = CsvDocument.Load(FourColCsv);
        Assert.Equal(doc.Headers.Length, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_FourCol_Correct()
    {
        var doc = CsvDocument.Load(FourColCsv);
        Assert.Equal(4, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_AfterCreateEmpty_Correct()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "a", "b", "c" });
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_PreservedAfterAddRow()
    {
        var doc = CsvDocument.Load(FourColCsv);
        doc.AddRow(new[] { "4", "Dave", "HR", "76" });
        Assert.Equal(4, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_PreservedAfterFilter()
    {
        var doc = CsvDocument.Load(FourColCsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(4, eng.ColumnCount);
    }

    [Fact]
    public void ColumnCount_PreservedAfterSetCellValue()
    {
        var doc = CsvDocument.Load(FourColCsv);
        doc.SetCellValue(0, 0, "99");
        Assert.Equal(4, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_TwoCol_Correct()
    {
        var doc = CsvDocument.Load("x,y\n1,2\n3,4");
        Assert.Equal(2, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Headers
    // -------------------------------------------------------------------------

    [Fact]
    public void Headers_NonNull_WhenHasHeaders()
    {
        var doc = CsvDocument.Load(FourColCsv);
        Assert.NotNull(doc.Headers);
    }

    [Fact]
    public void Headers_Count_EqualsFourCols()
    {
        var doc = CsvDocument.Load(FourColCsv);
        Assert.Equal(4, doc.Headers.Length);
    }

    [Fact]
    public void Headers_ContainsAllExpectedValues()
    {
        var doc = CsvDocument.Load(FourColCsv);
        Assert.Contains("id", doc.Headers);
        Assert.Contains("name", doc.Headers);
        Assert.Contains("dept", doc.Headers);
        Assert.Contains("score", doc.Headers);
    }

    [Fact]
    public void Headers_OrderPreserved()
    {
        var doc = CsvDocument.Load(FourColCsv);
        Assert.Equal("id", doc.Headers[0]);
        Assert.Equal("name", doc.Headers[1]);
        Assert.Equal("dept", doc.Headers[2]);
        Assert.Equal("score", doc.Headers[3]);
    }

    [Fact]
    public void Headers_AfterCreateEmpty_Correct()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "p", "q", "r" });
        Assert.Contains("p", doc.Headers);
        Assert.Contains("q", doc.Headers);
        Assert.Contains("r", doc.Headers);
    }

    // -------------------------------------------------------------------------
    // HasHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void HasHeaders_True_AfterLoad()
    {
        var doc = CsvDocument.Load(FourColCsv);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void HasHeaders_Preserved_AfterFilter()
    {
        var doc = CsvDocument.Load(FourColCsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.True(eng.HasHeaders);
    }

    [Fact]
    public void HasHeaders_Preserved_AfterAddRow()
    {
        var doc = CsvDocument.Load(FourColCsv);
        doc.AddRow(new[] { "4", "Dave", "HR", "76" });
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void HasHeaders_True_CreateEmptyWithHeaders()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "x", "y" });
        Assert.True(doc.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadColumnCountHeadersFilterColumnCountHeadersVerify_Pipeline()
    {
        // Load
        var doc = CsvDocument.Load(FourColCsv);
        Assert.Equal(3, doc.RowCount);

        // ColumnCount
        Assert.Equal(4, doc.ColumnCount);

        // Headers
        var headers = doc.Headers;
        Assert.Equal(4, headers!.Length);
        Assert.Equal("id", headers[0]);
        Assert.Equal("score", headers[3]);

        // HasHeaders
        Assert.True(doc.HasHeaders);

        // AddRow — ColumnCount and Headers unchanged
        doc.AddRow(new[] { "4", "Dave", "HR", "76" });
        Assert.Equal(4, doc.ColumnCount);
        Assert.Equal(4, doc.Headers.Length);
        Assert.Equal(4, doc.RowCount);

        // Filter Eng — ColumnCount and Headers preserved
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);
        Assert.Equal(4, eng.ColumnCount);
        Assert.True(eng.HasHeaders);
        Assert.Contains("score", eng.Headers);

        // Filter with zero match — still has columns and headers
        var mkt = doc.Filter(r => r.GetValue("dept") == "Marketing");
        Assert.Equal(0, mkt.RowCount);
        Assert.Equal(4, mkt.ColumnCount);
        Assert.True(mkt.HasHeaders);
    }
}
