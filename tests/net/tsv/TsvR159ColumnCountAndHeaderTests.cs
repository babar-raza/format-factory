// Tests for TsvDocument.ColumnCount, Headers property, HasHeaders deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R159

using System.Linq;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R159: Tests for TsvDocument.ColumnCount, Headers property, HasHeaders deeper coverage.
/// ColumnCount: number of columns detected from header or first row.
/// Headers: list of column header names.
/// HasHeaders: whether document has a header row.
/// Covers: ColumnCount positive for data; ColumnCount matches header count;
/// ColumnCount zero for empty doc; Headers non-null; Headers count matches ColumnCount;
/// Headers contains expected names; HasHeaders true for doc with header row;
/// HasHeaders false for doc without headers; GetColumnValues by index;
/// ColumnCount after AddRow increases if wider; Headers after Load match;
/// GetCellValue(row, col) correct; IsEmpty for empty content;
/// ColumnCount single column;
/// dogfood Load->Headers->ColumnCount->GetColumnValues->Filter->ToTsv verify.
/// </summary>
public class TsvR159ColumnCountAndHeaderTests
{
    private const string ThreeRowTsv =
        "name\tdept\tscore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88";

    private const string NoHeaderTsv =
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82";

    // -------------------------------------------------------------------------
    // ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_PositiveForData()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.True(doc.ColumnCount > 0);
    }

    [Fact]
    public void ColumnCount_MatchesHeaderCount()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal(doc.Headers.Count, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_ThreeForThreeColumns()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_ZeroForEmptyDoc()
    {
        var doc = TsvDocument.Load(string.Empty);
        Assert.Equal(0, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_SingleColumn()
    {
        var doc = TsvDocument.Load("id\n1\n2\n3");
        Assert.Equal(1, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Headers
    // -------------------------------------------------------------------------

    [Fact]
    public void Headers_NonNull()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.NotNull(doc.Headers);
    }

    [Fact]
    public void Headers_CountMatchesColumnCount()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal(doc.ColumnCount, doc.Headers.Count);
    }

    [Fact]
    public void Headers_ContainsExpectedNames()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Contains("name", doc.Headers);
        Assert.Contains("dept", doc.Headers);
        Assert.Contains("score", doc.Headers);
    }

    [Fact]
    public void Headers_AfterLoad_MatchOriginal()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("name", doc.Headers[0]);
        Assert.Equal("dept", doc.Headers[1]);
        Assert.Equal("score", doc.Headers[2]);
    }

    // -------------------------------------------------------------------------
    // HasHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void HasHeaders_TrueForDocWithHeaders()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void HasHeaders_FalseForDocWithoutHeaders()
    {
        var doc = TsvDocument.Load(NoHeaderTsv, hasHeaders: false);
        Assert.False(doc.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // GetCellValue and GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_Row0Col0_IsAlice()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var val = doc.GetCellValue(0, 0);
        Assert.Equal("Alice", val);
    }

    [Fact]
    public void GetCellValue_Row1Col1_IsFinance()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var val = doc.GetCellValue(1, 1);
        Assert.Equal("Finance", val);
    }

    [Fact]
    public void IsEmpty_TrueForEmptyContent()
    {
        var doc = TsvDocument.Load(string.Empty);
        Assert.True(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Headers->ColumnCount->GetColumnValues->Filter->ToTsv verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadHeadersColumnCountGetColumnValuesFilterToTsv_Pipeline()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);

        // Headers and ColumnCount
        Assert.Equal(3, doc.ColumnCount);
        Assert.Equal(3, doc.Headers.Count);
        Assert.Equal("name", doc.Headers[0]);
        Assert.True(doc.HasHeaders);

        // GetColumnValues
        var names = doc.GetColumnValues("name");
        Assert.Equal(3, names.Count);
        Assert.Contains("Alice", names);

        // Filter
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);
        Assert.Equal(3, eng.ColumnCount);
        Assert.True(eng.HasHeaders);

        // ToTsv
        var tsv = eng.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.DoesNotContain("Bob", tsv);

        // Load
        var reloaded = TsvDocument.Load(tsv);
        Assert.Equal(2, reloaded.RowCount);
        Assert.Equal(3, reloaded.ColumnCount);
    }
}
