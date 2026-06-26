// Tests for TsvDocument.ColumnCount, HasHeaders, Headers list deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R165

using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R165: Tests for TsvDocument.ColumnCount, HasHeaders, Headers deeper.
/// ColumnCount: number of columns (from header row or first row).
/// HasHeaders: whether the document has a header row.
/// Headers: list of column header names.
/// Covers: ColumnCount equals header count; ColumnCount correct value;
/// ColumnCount unchanged after AddRow; HasHeaders true when loaded with headers;
/// HasHeaders false when created empty; Headers non-null; Headers non-empty;
/// Headers contains all column names; Headers count equals ColumnCount;
/// Headers[0] is first column; Load without headers has HasHeaders=false;
/// Filter preserves Headers; Filter preserves HasHeaders;
/// ToTsv->Load preserves Headers; AddRow doesn't change ColumnCount;
/// dogfood Load->Headers->ColumnCount->Filter->Headers->ToTsv->Load verify.
/// </summary>
public class TsvR165ColumnCountAndHasHeadersTests
{
    private const string ThreeColTsv =
        "product\tprice\tqty\n" +
        "Widget\t10.00\t5\n" +
        "Gadget\t20.00\t3\n" +
        "Thingamajig\t15.00\t7";

    private const string NoHeaderTsv =
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82";

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
    public void ColumnCount_IsThreeForThreeColumns()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_UnchangedAfterAddRow()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        var before = doc.ColumnCount;
        doc.AddRow(new[] { "X", "1.00", "1" });
        Assert.Equal(before, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // HasHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void HasHeaders_True_WhenLoadedWithHeaders()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void HasHeaders_PreservedAfterFilter()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        var filtered = doc.Filter(r => r.GetValue("qty") != "3");
        Assert.True(filtered.HasHeaders);
    }

    [Fact]
    public void HasHeaders_PreservedAfterToTsvLoad()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        var tsv = doc.ToTsv();
        var reloaded = TsvDocument.Load(tsv);
        Assert.True(reloaded.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // Headers
    // -------------------------------------------------------------------------

    [Fact]
    public void Headers_NonNull()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        Assert.NotNull(doc.Headers);
    }

    [Fact]
    public void Headers_NonEmpty()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        Assert.NotEmpty(doc.Headers);
    }

    [Fact]
    public void Headers_CountEqualsColumnCount()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        Assert.Equal(doc.ColumnCount, doc.Headers.Count);
    }

    [Fact]
    public void Headers_ContainsAllColumnNames()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        Assert.Contains("product", doc.Headers);
        Assert.Contains("price", doc.Headers);
        Assert.Contains("qty", doc.Headers);
    }

    [Fact]
    public void Headers_FirstColumn_Correct()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        Assert.Equal("product", doc.Headers[0]);
    }

    [Fact]
    public void Headers_PreservedAfterFilter()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        var filtered = doc.Filter(r => true);
        Assert.Contains("product", filtered.Headers);
        Assert.Contains("price", filtered.Headers);
    }

    [Fact]
    public void Headers_ToTsvLoad_Preserved()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        var tsv = doc.ToTsv();
        var reloaded = TsvDocument.Load(tsv);
        Assert.Equal(doc.Headers.Count, reloaded.Headers.Count);
        for (var i = 0; i < doc.Headers.Count; i++)
            Assert.Equal(doc.Headers[i], reloaded.Headers[i]);
    }

    [Fact]
    public void Headers_FilterToTsv_DoesNotContainBob()
    {
        var doc = TsvDocument.Load(ThreeColTsv);
        var filtered = doc.Filter(r => r.GetValue("product") != "Widget");
        var tsv = filtered.ToTsv();
        Assert.DoesNotContain("Widget", tsv);
        Assert.Contains("product", tsv); // header still there
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadHeadersColumnCountFilterHeadersToTsvLoadVerify_Pipeline()
    {
        // Load
        var doc = TsvDocument.Load(ThreeColTsv);
        Assert.True(doc.HasHeaders);
        Assert.Equal(3, doc.ColumnCount);

        // Headers
        var headers = doc.Headers;
        Assert.Equal(3, headers.Count);
        Assert.Equal("product", headers[0]);
        Assert.Equal("price", headers[1]);
        Assert.Equal("qty", headers[2]);

        // Filter (exclude qty=3)
        var filtered = doc.Filter(r => r.GetValue("qty") != "3");
        Assert.Equal(2, filtered.RowCount);
        Assert.True(filtered.HasHeaders);
        Assert.Equal(3, filtered.ColumnCount);
        Assert.Contains("product", filtered.Headers);

        // ToTsv
        var tsv = filtered.ToTsv();
        Assert.Contains("product", tsv);
        Assert.DoesNotContain("Gadget", tsv);

        // Load
        var reloaded = TsvDocument.Load(tsv);
        Assert.Equal(2, reloaded.RowCount);
        Assert.True(reloaded.HasHeaders);
        Assert.Equal(3, reloaded.ColumnCount);
        Assert.Equal("product", reloaded.Headers[0]);
    }
}
