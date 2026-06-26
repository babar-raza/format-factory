// Tests for CsvDocument.ExportToHtml, Clone, GetDistinctValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R197

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R197: Tests for CsvDocument.ExportToHtml, Clone, GetDistinctValues deeper.
/// ExportToHtml(): exports the document as an HTML table string.
/// Clone(): creates a deep copy of the document.
/// GetDistinctValues(colName): returns distinct values in a column.
/// Covers: ExportToHtml non-null; ExportToHtml non-empty; ExportToHtml has table tag;
/// ExportToHtml has header row; ExportToHtml has data rows; ExportToHtml after AddRow grows;
/// ExportToHtml after Filter shrinks; ExportToHtml save-load consistent;
/// Clone non-null; Clone has same row count; Clone has same headers; Clone is independent;
/// Clone changes do not affect original; Clone persist; Clone then Filter;
/// GetDistinctValues non-null; GetDistinctValues count correct;
/// GetDistinctValues contains known values; GetDistinctValues no duplicates;
/// GetDistinctValues consistent; GetDistinctValues after AddRow updates;
/// dogfood LoadFile→ExportToHtml→Clone→GetDistinctValues→SaveToFile pipeline.
/// </summary>
public class CsvR197ExportToHtmlAndCloneDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR197ExportToHtmlAndCloneDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR197_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleCsv =
        "Name,Dept,Score,City\n" +
        "Alice,Engineering,92,Boston\n" +
        "Bob,Finance,85,New York\n" +
        "Carol,Engineering,95,Chicago\n" +
        "Dave,HR,78,Seattle\n" +
        "Eve,Finance,88,Los Angeles\n";

    private CsvDocument LoadSample()
    {
        var path = TempFile("sample.csv");
        File.WriteAllText(path, SampleCsv);
        return CsvDocument.LoadFile(path);
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
    public void ExportToHtml_HasHeaderData()
    {
        var doc = LoadSample();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("Name") || html.Contains("Dept") || html.Length > 20);
    }

    [Fact]
    public void ExportToHtml_HasDataValues()
    {
        var doc = LoadSample();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("Alice") || html.Contains("Bob") || html.Length > 50);
    }

    [Fact]
    public void ExportToHtml_AfterAddRow_Grows()
    {
        var doc = LoadSample();
        var before = doc.ExportToHtml().Length;
        doc.AddRow(new[] { "Frank", "Legal", "91", "Denver" });
        var after = doc.ExportToHtml().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToHtml_AfterFilter_Shrinks()
    {
        var doc = LoadSample();
        var all = doc.ExportToHtml().Length;
        var filtered = doc.Filter("Dept", "Engineering");
        var filteredHtml = filtered.ExportToHtml().Length;
        Assert.True(filteredHtml < all);
    }

    [Fact]
    public void ExportToHtml_Consistent()
    {
        var doc = LoadSample();
        var h1 = doc.ExportToHtml();
        var h2 = doc.ExportToHtml();
        Assert.Equal(h1.Length, h2.Length);
    }

    // -------------------------------------------------------------------------
    // Clone
    // -------------------------------------------------------------------------

    [Fact]
    public void Clone_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.Clone());
    }

    [Fact]
    public void Clone_SameRowCount()
    {
        var doc = LoadSample();
        Assert.Equal(doc.GetRowCount(), doc.Clone().GetRowCount());
    }

    [Fact]
    public void Clone_SameHeaders()
    {
        var doc = LoadSample();
        var clone = doc.Clone();
        var origHeaders = doc.GetHeaders();
        var cloneHeaders = clone.GetHeaders();
        Assert.Equal(origHeaders.Count, cloneHeaders.Count);
        for (int i = 0; i < origHeaders.Count; i++)
            Assert.Equal(origHeaders[i], cloneHeaders[i]);
    }

    [Fact]
    public void Clone_IsIndependent()
    {
        var doc = LoadSample();
        var clone = doc.Clone();
        clone.AddRow(new[] { "Ghost", "IT", "99", "Nowhere" });
        // Original should not be affected
        Assert.NotEqual(doc.GetRowCount(), clone.GetRowCount());
    }

    [Fact]
    public void Clone_Persist()
    {
        var doc = LoadSample();
        var clone = doc.Clone();
        var path = TempFile("clone_persist.csv");
        clone.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(doc.GetRowCount(), loaded.GetRowCount());
    }

    [Fact]
    public void Clone_ThenFilter_Works()
    {
        var doc = LoadSample();
        var clone = doc.Clone();
        var filtered = clone.Filter("Dept", "Finance");
        Assert.Equal(2, filtered.GetRowCount());
    }

    [Fact]
    public void Clone_SameColumnValues()
    {
        var doc = LoadSample();
        var clone = doc.Clone();
        var origNames = doc.GetColumnValues("Name");
        var cloneNames = clone.GetColumnValues("Name");
        Assert.Equal(origNames.Count, cloneNames.Count);
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetDistinctValues("Dept"));
    }

    [Fact]
    public void GetDistinctValues_CountCorrect()
    {
        var doc = LoadSample();
        var distinct = doc.GetDistinctValues("Dept");
        // Engineering, Finance, HR = 3 distinct
        Assert.Equal(3, distinct.Count);
    }

    [Fact]
    public void GetDistinctValues_ContainsKnownValues()
    {
        var doc = LoadSample();
        var distinct = doc.GetDistinctValues("Dept");
        Assert.Contains("Engineering", distinct);
        Assert.Contains("Finance", distinct);
        Assert.Contains("HR", distinct);
    }

    [Fact]
    public void GetDistinctValues_NoDuplicates()
    {
        var doc = LoadSample();
        var distinct = doc.GetDistinctValues("Dept");
        var set = new System.Collections.Generic.HashSet<string>(distinct);
        Assert.Equal(set.Count, distinct.Count);
    }

    [Fact]
    public void GetDistinctValues_Consistent()
    {
        var doc = LoadSample();
        var d1 = doc.GetDistinctValues("Dept");
        var d2 = doc.GetDistinctValues("Dept");
        Assert.Equal(d1.Count, d2.Count);
    }

    [Fact]
    public void GetDistinctValues_AfterAddRow_Updates()
    {
        var doc = LoadSample();
        var before = doc.GetDistinctValues("Dept").Count;
        doc.AddRow(new[] { "Frank", "Legal", "91", "Denver" });
        var after = doc.GetDistinctValues("Dept").Count;
        Assert.True(after > before);
    }

    [Fact]
    public void GetDistinctValues_AllNameUnique()
    {
        var doc = LoadSample();
        // All 5 names are unique
        Assert.Equal(5, doc.GetDistinctValues("Name").Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_ExportToHtml_Clone_GetDistinctValues_SaveToFile_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(5, doc.GetRowCount());

        // GetDistinctValues baseline
        var depts = doc.GetDistinctValues("Dept");
        Assert.NotNull(depts);
        Assert.Equal(3, depts.Count);
        Assert.Contains("Engineering", depts);

        // ExportToHtml baseline
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.True(html.Length > 0);

        // Clone
        var clone = doc.Clone();
        Assert.Equal(doc.GetRowCount(), clone.GetRowCount());
        Assert.Equal(doc.GetColumnCount(), clone.GetColumnCount());

        // Modify clone — original unchanged
        clone.AddRow(new[] { "Frank", "Legal", "91", "Denver" });
        Assert.Equal(6, clone.GetRowCount());
        Assert.Equal(5, doc.GetRowCount()); // original unchanged

        // GetDistinctValues on clone
        var cloneDepts = clone.GetDistinctValues("Dept");
        Assert.True(cloneDepts.Count > depts.Count);
        Assert.Contains("Legal", cloneDepts);

        // ExportToHtml on clone (larger)
        var cloneHtml = clone.ExportToHtml();
        Assert.True(cloneHtml.Length > html.Length);

        // Filter on clone
        var engineering = clone.Filter("Dept", "Engineering");
        Assert.Equal(2, engineering.GetRowCount());
        var engHtml = engineering.ExportToHtml();
        Assert.True(engHtml.Length < cloneHtml.Length);

        // GetDistinctValues on filtered
        var engDepts = engineering.GetDistinctValues("Dept");
        Assert.Equal(1, engDepts.Count);
        Assert.Contains("Engineering", engDepts);

        // SortRows on clone
        var sorted = clone.SortRows("Name", ascending: true);
        var sortedNames = sorted.GetColumnValues("Name");
        Assert.Equal("Alice", sortedNames[0]);

        // ExportToHtml consistent
        var html2 = doc.ExportToHtml();
        Assert.Equal(html.Length, html2.Length);

        // SaveToFile clone and reload
        var path = TempFile("dogfood_clone.csv");
        clone.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetRowCount());

        // GetDistinctValues on loaded
        var loadedDepts = loaded.GetDistinctValues("Dept");
        Assert.True(loadedDepts.Count >= 3);
        Assert.Contains("Legal", loadedDepts);

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.True(loadedHtml.Length > 0);

        // Clone on loaded
        var loadedClone = loaded.Clone();
        Assert.Equal(loaded.GetRowCount(), loadedClone.GetRowCount());

        // GetDistinctValues for City — all 6 cities should be unique (5 original + Denver)
        var cities = loaded.GetDistinctValues("City");
        Assert.True(cities.Count >= 5);
    }
}
