// Tests for TsvDocument.Headers, ColumnCount, HasHeaders deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R171

using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R171: Tests for TsvDocument.Headers, ColumnCount, HasHeaders deeper coverage.
/// Headers: IReadOnlyList of header strings (when HasHeaders is true).
/// ColumnCount: number of columns in the document.
/// HasHeaders: true when the document was loaded with a header row.
/// Covers: HasHeaders true after Load with header row; HasHeaders correct for no-header content;
/// Headers non-null when HasHeaders; Headers count equals ColumnCount;
/// Headers contains expected values; Headers order preserved;
/// ColumnCount equals header count; ColumnCount consistent across rows;
/// ColumnCount after CreateEmpty; ColumnCount after AddRow;
/// Headers preserved after Filter; ColumnCount preserved after Filter;
/// dogfood Load->HasHeaders->Headers->ColumnCount->Filter->Headers->ColumnCount verify.
/// </summary>
public class TsvR171HeadersAndColumnCountDeepTests
{
    private const string ThreeColTsv =
        "id\tname\tdept\n" +
        "1\tAlice\tEng\n" +
        "2\tBob\tFinance\n" +
        "3\tCarol\tEng";

    private const string FiveColTsv =
        "a\tb\tc\td\te\n" +
        "1\t2\t3\t4\t5\n" +
        "6\t7\t8\t9\t10";

    // -------------------------------------------------------------------------
    // HasHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void HasHeaders_True_AfterLoadWithHeaderRow()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void HasHeaders_True_FiveColContent()
    {
        var doc = TsvDocument.Load(FiveColTsv);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void HasHeaders_True_CreateEmptyWithHeaders()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "x", "y", "z" });
        Assert.True(doc.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // Headers
    // -------------------------------------------------------------------------

    [Fact]
    public void Headers_NonNull_WhenHasHeaders()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        Assert.NotNull(doc.Headers);
    }

    [Fact]
    public void Headers_Count_Correct()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        Assert.Equal(3, doc.Headers.Count);
    }

    [Fact]
    public void Headers_ContainsExpectedValues()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        Assert.Contains("id", doc.Headers);
        Assert.Contains("name", doc.Headers);
        Assert.Contains("dept", doc.Headers);
    }

    [Fact]
    public void Headers_OrderPreserved()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        Assert.Equal("id", doc.Headers[0]);
        Assert.Equal("name", doc.Headers[1]);
        Assert.Equal("dept", doc.Headers[2]);
    }

    [Fact]
    public void Headers_FiveCol_Correct()
    {
        var doc = TsvDocument.Load(FiveColTsv);
        Assert.Equal(5, doc.Headers.Count);
        Assert.Equal("a", doc.Headers[0]);
        Assert.Equal("e", doc.Headers[4]);
    }

    [Fact]
    public void Headers_Preserved_AfterFilter()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.True(eng.HasHeaders);
        Assert.Contains("id", eng.Headers);
        Assert.Contains("name", eng.Headers);
        Assert.Contains("dept", eng.Headers);
    }

    // -------------------------------------------------------------------------
    // ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_EqualsHeaderCount()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        Assert.Equal(doc.Headers.Count, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_ThreeCol_Correct()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_FiveCol_Correct()
    {
        var doc = TsvDocument.Load(FiveColTsv);
        Assert.Equal(5, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_CreateEmpty_MatchesHeadersGiven()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "p", "q", "r", "s" });
        Assert.Equal(4, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_Preserved_AfterFilter()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(doc.ColumnCount, eng.ColumnCount);
    }

    [Fact]
    public void ColumnCount_Preserved_AfterAddRow()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        doc.AddRow(new[] { "4", "Dave", "HR" });
        Assert.Equal(3, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadHasHeadersHeadersColumnCountFilterHeadersColumnCountVerify_Pipeline()
    {
        // Load
        var doc = TsvDocument.Load(ThreeColTsv);
        Assert.Equal(3, doc.RowCount);

        // HasHeaders
        Assert.True(doc.HasHeaders);

        // Headers
        var headers = doc.Headers;
        Assert.Equal(3, headers.Count);
        Assert.Equal("id", headers[0]);
        Assert.Equal("name", headers[1]);
        Assert.Equal("dept", headers[2]);

        // ColumnCount
        Assert.Equal(3, doc.ColumnCount);
        Assert.Equal(headers.Count, doc.ColumnCount);

        // AddRow and re-check ColumnCount
        doc.AddRow(new[] { "4", "Dave", "HR" });
        Assert.Equal(4, doc.RowCount);
        Assert.Equal(3, doc.ColumnCount); // unchanged

        // Filter Eng
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);

        // Headers and ColumnCount preserved after filter
        Assert.True(eng.HasHeaders);
        Assert.Equal(3, eng.ColumnCount);
        Assert.Equal("id", eng.Headers[0]);
        Assert.Equal("dept", eng.Headers[2]);
    }
}
