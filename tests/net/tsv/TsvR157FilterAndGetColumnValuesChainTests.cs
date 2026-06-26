// Tests for TsvDocument.Filter chain with GetColumnValues and ToTsv serialization.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R157

using System.Linq;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R157: Tests for TsvDocument.Filter chain with GetColumnValues and ToTsv.
/// Filter(predicate): returns a new TsvDocument with matching rows.
/// GetColumnValues(headerName): returns all values for the named column.
/// ToTsv(): serializes document to TSV string.
/// Covers: Filter by dept returns matching rows; Filter count correct;
/// Filter non-matching returns empty; Filter->Filter chain narrows result;
/// GetColumnValues after Filter; ToTsv after Filter contains expected rows;
/// Filter->ToTsv->Load round-trip count matches; Filter preserves headers;
/// GetColumnValues returns all values; GetColumnValues count matches row count;
/// Filter->GetColumnValues correct values; ToTsv non-empty for non-empty doc;
/// Filter chain: dept AND score range;
/// dogfood Load->Filter->GetColumnValues->ToTsv->Load verify pipeline.
/// </summary>
public class TsvR157FilterAndGetColumnValuesChainTests
{
    private const string ThreeRowTsv =
        "name\tdept\tscore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88";

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_ByDept_Eng_ReturnsMatchingRows()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.NotNull(eng);
        Assert.True(eng.RowCount > 0);
    }

    [Fact]
    public void Filter_ByDept_Eng_CountIsTwo()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);
    }

    [Fact]
    public void Filter_NonMatching_ReturnsEmpty()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var none = doc.Filter(r => r.GetValue("dept") == "Marketing");
        Assert.Equal(0, none.RowCount);
    }

    [Fact]
    public void Filter_PreservesHeaders()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.True(eng.HasHeaders);
        Assert.Contains("name", eng.Headers);
        Assert.Contains("dept", eng.Headers);
    }

    [Fact]
    public void Filter_Chain_NarrowsResult()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        // Filter Eng then score > 90
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        var highScoring = eng.Filter(r =>
            int.TryParse(r.GetValue("score"), out var s) && s > 90);
        Assert.Equal(1, highScoring.RowCount);
    }

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_AllNames_CountIsThree()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var names = doc.GetColumnValues("name");
        Assert.Equal(3, names.Count);
    }

    [Fact]
    public void GetColumnValues_ContainsAllValues()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var names = doc.GetColumnValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void GetColumnValues_AfterFilter_CorrectValues()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        var names = eng.GetColumnValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }

    // -------------------------------------------------------------------------
    // ToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToTsv_AfterFilter_ContainsEngRows()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        var tsv = eng.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("Carol", tsv);
        Assert.DoesNotContain("Bob", tsv);
    }

    [Fact]
    public void ToTsv_NonEmpty_ForNonEmptyDoc()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var tsv = doc.ToTsv();
        Assert.False(string.IsNullOrWhiteSpace(tsv));
    }

    [Fact]
    public void Filter_ToTsv_Load_RoundTrip_CountMatches()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        var tsv = eng.ToTsv();
        var loaded = TsvDocument.Load(tsv);
        Assert.Equal(2, loaded.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->GetColumnValues->ToTsv->Load verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterGetColumnValuesToTsvLoadVerify_Pipeline()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal(3, doc.RowCount);

        // Filter Eng
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);

        // GetColumnValues
        var names = eng.GetColumnValues("name");
        Assert.Equal(2, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);

        // ToTsv
        var tsv = eng.ToTsv();
        Assert.NotNull(tsv);
        Assert.Contains("Eng", tsv);

        // Load
        var loaded = TsvDocument.Load(tsv);
        Assert.Equal(2, loaded.RowCount);
        Assert.True(loaded.HasHeaders);

        // Verify names
        var loadedNames = loaded.GetColumnValues("name");
        Assert.Contains("Alice", loadedNames);
        Assert.Contains("Carol", loadedNames);
    }
}
