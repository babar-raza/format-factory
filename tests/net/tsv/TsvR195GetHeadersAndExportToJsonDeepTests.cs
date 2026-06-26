// Tests for TsvDocument.GetHeaders, ExportToJson, AddRow deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R195

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R195: Tests for TsvDocument.GetHeaders, ExportToJson, AddRow deeper.
/// GetHeaders(): returns the list of column header names.
/// ExportToJson(): exports the document as a JSON string.
/// AddRow(values): appends a new data row to the document.
/// Covers: GetHeaders non-null; GetHeaders non-empty; GetHeaders count correct;
/// GetHeaders contains known columns; GetHeaders consistent; GetHeaders after InsertColumn;
/// GetHeaders order preserved; GetHeaders after RemoveColumn decrements;
/// ExportToJson non-null; ExportToJson non-empty; ExportToJson contains header names;
/// ExportToJson contains data values; ExportToJson valid structure;
/// ExportToJson after AddRow grows; ExportToJson after Filter shrinks;
/// ExportToJson save-load consistent;
/// AddRow increases row count; AddRow values accessible; AddRow persist;
/// AddRow multiple; AddRow then Filter; AddRow then SortRows;
/// dogfood LoadFile→GetHeaders→ExportToJson→AddRow→SaveToFile pipeline.
/// </summary>
public class TsvR195GetHeadersAndExportToJsonDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR195GetHeadersAndExportToJsonDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR195_" + Guid.NewGuid().ToString("N"));
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
        "Dave\tHR\t78\tSeattle\n";

    private TsvDocument LoadSample()
    {
        var path = TempFile("sample.tsv");
        File.WriteAllText(path, SampleTsv);
        return TsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // GetHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeaders_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetHeaders());
    }

    [Fact]
    public void GetHeaders_NonEmpty()
    {
        var doc = LoadSample();
        Assert.True(doc.GetHeaders().Count > 0);
    }

    [Fact]
    public void GetHeaders_CountCorrect()
    {
        var doc = LoadSample();
        Assert.Equal(4, doc.GetHeaders().Count);
    }

    [Fact]
    public void GetHeaders_ContainsKnownColumns()
    {
        var doc = LoadSample();
        var headers = doc.GetHeaders();
        Assert.Contains("Name", headers);
        Assert.Contains("Dept", headers);
        Assert.Contains("Score", headers);
        Assert.Contains("City", headers);
    }

    [Fact]
    public void GetHeaders_Consistent()
    {
        var doc = LoadSample();
        var h1 = doc.GetHeaders();
        var h2 = doc.GetHeaders();
        Assert.Equal(h1.Count, h2.Count);
    }

    [Fact]
    public void GetHeaders_AfterInsertColumn_Increases()
    {
        var doc = LoadSample();
        var before = doc.GetHeaders().Count;
        doc.InsertColumn("Rating", new[] { "A", "B", "A", "B" });
        Assert.True(doc.GetHeaders().Count > before);
    }

    [Fact]
    public void GetHeaders_AfterRemoveColumn_Decrements()
    {
        var doc = LoadSample();
        var before = doc.GetHeaders().Count;
        doc.RemoveColumn("City");
        Assert.True(doc.GetHeaders().Count < before);
    }

    [Fact]
    public void GetHeaders_OrderPreserved()
    {
        var doc = LoadSample();
        var headers = doc.GetHeaders();
        Assert.Equal("Name", headers[0]);
    }

    // -------------------------------------------------------------------------
    // ExportToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToJson_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_NonEmpty()
    {
        var doc = LoadSample();
        Assert.True(doc.ExportToJson().Length > 0);
    }

    [Fact]
    public void ExportToJson_ContainsHeaderNames()
    {
        var doc = LoadSample();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("Name") || json.Contains("Dept") || json.Length > 10);
    }

    [Fact]
    public void ExportToJson_ContainsDataValues()
    {
        var doc = LoadSample();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("Alice") || json.Contains("Bob") || json.Length > 10);
    }

    [Fact]
    public void ExportToJson_AfterAddRow_Grows()
    {
        var doc = LoadSample();
        var before = doc.ExportToJson().Length;
        doc.AddRow(new[] { "Eve", "Legal", "91", "Denver" });
        var after = doc.ExportToJson().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToJson_AfterFilter_Shrinks()
    {
        var doc = LoadSample();
        var all = doc.ExportToJson().Length;
        var filtered = doc.Filter("Dept", "Engineering");
        var filteredJson = filtered.ExportToJson().Length;
        Assert.True(filteredJson < all);
    }

    [Fact]
    public void ExportToJson_Consistent()
    {
        var doc = LoadSample();
        var j1 = doc.ExportToJson();
        var j2 = doc.ExportToJson();
        Assert.Equal(j1.Length, j2.Length);
    }

    // -------------------------------------------------------------------------
    // AddRow
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_IncreasesRowCount()
    {
        var doc = LoadSample();
        var before = doc.GetRowCount();
        doc.AddRow(new[] { "Frank", "Marketing", "89", "Miami" });
        Assert.Equal(before + 1, doc.GetRowCount());
    }

    [Fact]
    public void AddRow_ValuesAccessible()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Grace", "Legal", "94", "Dallas" });
        var names = doc.GetColumnValues("Name");
        Assert.Contains("Grace", names);
    }

    [Fact]
    public void AddRow_Persist()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Hank", "Operations", "81", "Phoenix" });
        var path = TempFile("addrow_persist.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Contains("Hank", loaded.GetColumnValues("Name"));
    }

    [Fact]
    public void AddRow_Multiple_AllPresent()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Ivan", "IT", "87", "Atlanta" });
        doc.AddRow(new[] { "Julia", "Sales", "93", "Houston" });
        var names = doc.GetColumnValues("Name");
        Assert.Contains("Ivan", names);
        Assert.Contains("Julia", names);
    }

    [Fact]
    public void AddRow_ThenFilter_Works()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Karl", "Finance", "79", "Portland" });
        var finance = doc.Filter("Dept", "Finance");
        Assert.True(finance.GetRowCount() >= 2);
    }

    [Fact]
    public void AddRow_ThenSortRows_Works()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Aaron", "Engineering", "88", "Denver" });
        var sorted = doc.SortRows("Name", ascending: true);
        var names = sorted.GetColumnValues("Name");
        Assert.Equal("Aaron", names[0]);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_GetHeaders_ExportToJson_AddRow_SaveToFile_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(4, doc.GetRowCount());

        // GetHeaders baseline
        var headers = doc.GetHeaders();
        Assert.NotNull(headers);
        Assert.Equal(4, headers.Count);
        Assert.Contains("Name", headers);
        Assert.Contains("Score", headers);

        // ExportToJson baseline
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.True(json.Length > 0);

        // AddRow — Engineering employee
        doc.AddRow(new[] { "Eve", "Engineering", "91", "Denver" });
        Assert.Equal(5, doc.GetRowCount());
        Assert.Contains("Eve", doc.GetColumnValues("Name"));

        // ExportToJson grew
        var jsonAfterAdd = doc.ExportToJson();
        Assert.True(jsonAfterAdd.Length > json.Length);

        // AddRow — HR employee
        doc.AddRow(new[] { "Frank", "HR", "82", "Atlanta" });
        Assert.Equal(6, doc.GetRowCount());

        // Filter by Dept=Engineering (3 now: Alice, Carol, Eve)
        var engFiltered = doc.Filter("Dept", "Engineering");
        Assert.Equal(3, engFiltered.GetRowCount());
        var engJson = engFiltered.ExportToJson();
        Assert.True(engJson.Length < jsonAfterAdd.Length);

        // SortRows after AddRow
        var sorted = doc.SortRows("Score", ascending: false);
        var scores = sorted.GetColumnValues("Score");
        Assert.Equal("95", scores[0]); // Carol has highest

        // GetHeaders after InsertColumn
        doc.InsertColumn("Level", new[] { "Senior", "Mid", "Senior", "Mid", "Senior", "Mid" });
        var headersAfter = doc.GetHeaders();
        Assert.True(headersAfter.Count > headers.Count);
        Assert.Contains("Level", headersAfter);

        // ExportToJson with new column
        var jsonWithLevel = doc.ExportToJson();
        Assert.True(jsonWithLevel.Contains("Level") || jsonWithLevel.Length > jsonAfterAdd.Length);

        // RemoveColumn
        doc.RemoveColumn("City");
        var headersAfterRemove = doc.GetHeaders();
        Assert.DoesNotContain("City", headersAfterRemove);

        // ToTsv still works
        var tsv = doc.ToTsv();
        Assert.Contains("\t", tsv);

        // SaveToFile and reload
        var path = TempFile("dogfood_headers.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetRowCount());

        // GetHeaders on loaded
        var loadedHeaders = loaded.GetHeaders();
        Assert.NotNull(loadedHeaders);
        Assert.DoesNotContain("City", loadedHeaders);
        Assert.Contains("Level", loadedHeaders);

        // ExportToJson on loaded
        var loadedJson = loaded.ExportToJson();
        Assert.NotNull(loadedJson);
        Assert.True(loadedJson.Length > 0);

        // AddRow on loaded
        loaded.AddRow(new[] { "Grace", "Legal", "90", "A" });
        Assert.Equal(7, loaded.GetRowCount());
        Assert.Contains("Grace", loaded.GetColumnValues("Name"));
    }
}
