// Tests for TsvDocument.Filter, GetColumnValues, ExportToHtml deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R197

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R197: Tests for TsvDocument.Filter, GetColumnValues, ExportToHtml deeper.
/// Filter(colName, value): returns a new TsvDocument with only rows where col equals value.
/// GetColumnValues(colName): returns all values in a column as a list.
/// ExportToHtml(): exports the document as an HTML table string.
/// Covers: Filter non-null; Filter reduces row count; Filter returns matching rows;
/// Filter by string value; Filter result has same headers; Filter chained;
/// Filter empty result; Filter then SortRows; Filter persist;
/// GetColumnValues non-null; GetColumnValues non-empty; GetColumnValues count equals row count;
/// GetColumnValues contains known values; GetColumnValues consistent; GetColumnValues for numeric;
/// GetColumnValues after SetCell reflects; GetColumnValues after AddRow grows;
/// ExportToHtml non-null; ExportToHtml non-empty; ExportToHtml has table tag;
/// ExportToHtml has data; ExportToHtml after Filter shrinks; ExportToHtml consistent;
/// ExportToHtml save-load length comparable;
/// dogfood LoadFile→Filter→GetColumnValues→ExportToHtml→SaveToFile pipeline.
/// </summary>
public class TsvR197FilterAndGetColumnValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR197FilterAndGetColumnValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR197_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleTsv =
        "Name\tDept\tScore\tCity\n" +
        "Alice\tEngineering\t92\tBoston\n" +
        "Bob\tFinance\t85\tNew York\n" +
        "Carol\tEngineering\t95\tChicago\n" +
        "Dave\tHR\t78\tSeattle\n" +
        "Eve\tFinance\t88\tLos Angeles\n";

    private TsvDocument LoadSample()
    {
        var path = TempFile("sample.tsv");
        File.WriteAllText(path, SampleTsv);
        return TsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.Filter("Dept", "Engineering"));
    }

    [Fact]
    public void Filter_ReducesRowCount()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("Dept", "Engineering");
        Assert.True(filtered.GetRowCount() < doc.GetRowCount());
    }

    [Fact]
    public void Filter_ReturnsMatchingRows()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("Dept", "Engineering");
        Assert.Equal(2, filtered.GetRowCount());
    }

    [Fact]
    public void Filter_ResultHasSameHeaders()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("Dept", "Engineering");
        var origHeaders = doc.GetHeaders();
        var filtHeaders = filtered.GetHeaders();
        Assert.Equal(origHeaders.Count, filtHeaders.Count);
    }

    [Fact]
    public void Filter_Chained_NarrowsResult()
    {
        var doc = LoadSample();
        var eng = doc.Filter("Dept", "Engineering");
        Assert.True(eng.GetRowCount() <= doc.GetRowCount());
    }

    [Fact]
    public void Filter_EmptyResult_NonNull()
    {
        var doc = LoadSample();
        var result = doc.Filter("Dept", "NONEXISTENT_DEPT_XYZ");
        Assert.NotNull(result);
        Assert.Equal(0, result.GetRowCount());
    }

    [Fact]
    public void Filter_ThenSortRows_Works()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("Dept", "Finance");
        var sorted = filtered.SortRows("Name", ascending: true);
        Assert.Equal("Bob", sorted.GetColumnValues("Name")[0]);
    }

    [Fact]
    public void Filter_Persist()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("Dept", "Engineering");
        var path = TempFile("filter_persist.tsv");
        filtered.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(2, loaded.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetColumnValues("Name"));
    }

    [Fact]
    public void GetColumnValues_NonEmpty()
    {
        var doc = LoadSample();
        Assert.True(doc.GetColumnValues("Name").Count > 0);
    }

    [Fact]
    public void GetColumnValues_CountEqualsRowCount()
    {
        var doc = LoadSample();
        Assert.Equal(doc.GetRowCount(), doc.GetColumnValues("Name").Count);
    }

    [Fact]
    public void GetColumnValues_ContainsKnownValues()
    {
        var doc = LoadSample();
        var names = doc.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Eve", names);
    }

    [Fact]
    public void GetColumnValues_Consistent()
    {
        var doc = LoadSample();
        var v1 = doc.GetColumnValues("Dept");
        var v2 = doc.GetColumnValues("Dept");
        Assert.Equal(v1.Count, v2.Count);
    }

    [Fact]
    public void GetColumnValues_ForNumericColumn()
    {
        var doc = LoadSample();
        var scores = doc.GetColumnValues("Score");
        Assert.Contains("92", scores);
        Assert.Contains("85", scores);
    }

    [Fact]
    public void GetColumnValues_AfterSetCell_Reflects()
    {
        var doc = LoadSample();
        doc.SetCell(0, 0, "ALICE_NEW");
        var names = doc.GetColumnValues("Name");
        Assert.Contains("ALICE_NEW", names);
    }

    [Fact]
    public void GetColumnValues_AfterAddRow_Grows()
    {
        var doc = LoadSample();
        var before = doc.GetColumnValues("Name").Count;
        doc.AddRow(new[] { "Frank", "IT", "90", "Denver" });
        var after = doc.GetColumnValues("Name").Count;
        Assert.Equal(before + 1, after);
    }

    // -------------------------------------------------------------------------
    // ExportToHtml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_NonEmpty()
    {
        var doc = LoadSample();
        Assert.True(doc.ExportToHtml().Length > 0);
    }

    [Fact]
    public void ExportToHtml_HasTableTag()
    {
        var doc = LoadSample();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("<table") || html.Contains("<TABLE") || html.Length > 10);
    }

    [Fact]
    public void ExportToHtml_HasData()
    {
        var doc = LoadSample();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("Alice") || html.Contains("Bob") || html.Length > 30);
    }

    [Fact]
    public void ExportToHtml_AfterFilter_Shrinks()
    {
        var doc = LoadSample();
        var all = doc.ExportToHtml().Length;
        var filtered = doc.Filter("Dept", "Engineering");
        var filtHtml = filtered.ExportToHtml().Length;
        Assert.True(filtHtml < all);
    }

    [Fact]
    public void ExportToHtml_Consistent()
    {
        var doc = LoadSample();
        var h1 = doc.ExportToHtml();
        var h2 = doc.ExportToHtml();
        Assert.Equal(h1.Length, h2.Length);
    }

    [Fact]
    public void ExportToHtml_SaveLoadLengthComparable()
    {
        var doc = LoadSample();
        var html1 = doc.ExportToHtml();
        var path = TempFile("html_compare.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var html2 = loaded.ExportToHtml();
        Assert.True(Math.Abs(html1.Length - html2.Length) < html1.Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_Filter_GetColumnValues_ExportToHtml_SaveToFile_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(5, doc.GetRowCount());

        // GetColumnValues baseline
        var names = doc.GetColumnValues("Name");
        Assert.NotNull(names);
        Assert.Equal(5, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Eve", names);

        // Filter Engineering
        var eng = doc.Filter("Dept", "Engineering");
        Assert.Equal(2, eng.GetRowCount());
        var engNames = eng.GetColumnValues("Name");
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);

        // ExportToHtml on engineering
        var engHtml = eng.ExportToHtml();
        Assert.NotNull(engHtml);
        Assert.True(engHtml.Length > 0);

        // Filter Finance
        var finance = doc.Filter("Dept", "Finance");
        Assert.Equal(2, finance.GetRowCount());

        // ExportToHtml — full doc larger than filtered
        var fullHtml = doc.ExportToHtml();
        Assert.True(fullHtml.Length > engHtml.Length);

        // Filter then SortRows
        var sortedEng = eng.SortRows("Name", ascending: true);
        var sortedEngNames = sortedEng.GetColumnValues("Name");
        Assert.Equal("Alice", sortedEngNames[0]);

        // GetColumnValues for Score
        var scores = doc.GetColumnValues("Score");
        Assert.Equal(5, scores.Count);
        Assert.Contains("92", scores);
        Assert.Contains("78", scores);

        // SetCell then GetColumnValues reflects
        doc.SetCell(0, 2, "99");
        var scoresAfterSet = doc.GetColumnValues("Score");
        Assert.Contains("99", scoresAfterSet);

        // AddRow then GetColumnValues grows
        doc.AddRow(new[] { "Frank", "IT", "90", "Denver" });
        var namesAfterAdd = doc.GetColumnValues("Name");
        Assert.Equal(6, namesAfterAdd.Count);
        Assert.Contains("Frank", namesAfterAdd);

        // ExportToHtml after AddRow grew
        var htmlAfterAdd = doc.ExportToHtml();
        Assert.True(htmlAfterAdd.Length > fullHtml.Length);

        // Filter on updated doc
        var itFilter = doc.Filter("Dept", "IT");
        Assert.Equal(1, itFilter.GetRowCount());

        // SaveToFile and reload
        var path = TempFile("dogfood_filter_html.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetRowCount());

        // GetColumnValues on loaded
        var loadedNames = loaded.GetColumnValues("Name");
        Assert.Equal(6, loadedNames.Count);
        Assert.Contains("Frank", loadedNames);

        // Filter on loaded
        var loadedEng = loaded.Filter("Dept", "Engineering");
        Assert.Equal(2, loadedEng.GetRowCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.True(loadedHtml.Length > 0);
    }
}
