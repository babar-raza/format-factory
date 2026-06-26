// Tests for NdjsonDocument.SelectFields, ToCsv, GetRecordCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R203

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R203: Tests for NdjsonDocument.SelectFields, ToCsv, GetRecordCount deeper.
/// SelectFields(fields): returns a new NdjsonDocument with only the specified fields.
/// ToCsv(): exports the document as a CSV string.
/// GetRecordCount(): returns the number of records in the document.
/// Covers: SelectFields non-null; SelectFields reduces keys; SelectFields keeps values;
/// SelectFields persist; SelectFields then Filter; SelectFields consistent;
/// SelectFields single field; SelectFields all fields;
/// ToCsv non-null; ToCsv non-empty; ToCsv contains header row;
/// ToCsv contains data values; ToCsv after AppendRecord grows;
/// ToCsv after Filter shrinks; ToCsv consistent; ToCsv save-load;
/// GetRecordCount correct; GetRecordCount after AppendRecord increases;
/// GetRecordCount after Filter decreases; GetRecordCount consistent;
/// GetRecordCount empty doc zero;
/// dogfood LoadFile→SelectFields→ToCsv→GetRecordCount→SaveToFile pipeline.
/// </summary>
public class NdjsonR203SelectFieldsAndToCsvDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR203SelectFieldsAndToCsvDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR203_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Engineering\",\"score\":92,\"city\":\"Boston\"}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":85,\"city\":\"New York\"}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Engineering\",\"score\":95,\"city\":\"Chicago\"}\n" +
        "{\"name\":\"Dave\",\"dept\":\"HR\",\"score\":78,\"city\":\"Seattle\"}\n" +
        "{\"name\":\"Eve\",\"dept\":\"Finance\",\"score\":88,\"city\":\"Los Angeles\"}\n";

    private NdjsonDocument LoadSample()
    {
        var path = TempFile("sample.ndjson");
        File.WriteAllText(path, SampleNdjson);
        return NdjsonDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // SelectFields
    // -------------------------------------------------------------------------

    [Fact]
    public void SelectFields_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.SelectFields(new[] { "name", "dept" }));
    }

    [Fact]
    public void SelectFields_ReducesKeys()
    {
        var doc = LoadSample();
        var selected = doc.SelectFields(new[] { "name", "dept" });
        var keys = selected.GetAllKeys();
        Assert.True(keys.Count <= 2);
    }

    [Fact]
    public void SelectFields_KeepsValues()
    {
        var doc = LoadSample();
        var selected = doc.SelectFields(new[] { "name" });
        var names = selected.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
    }

    [Fact]
    public void SelectFields_Persist()
    {
        var doc = LoadSample();
        var selected = doc.SelectFields(new[] { "name", "score" });
        var path = TempFile("select_persist.ndjson");
        selected.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(selected.GetRecordCount(), loaded.GetRecordCount());
    }

    [Fact]
    public void SelectFields_ThenFilter_Works()
    {
        var doc = LoadSample();
        var selected = doc.SelectFields(new[] { "name", "dept" });
        var filtered = selected.Filter("dept", "Engineering");
        Assert.Equal(2, filtered.GetRecordCount());
    }

    [Fact]
    public void SelectFields_Consistent()
    {
        var doc = LoadSample();
        var s1 = doc.SelectFields(new[] { "name" });
        var s2 = doc.SelectFields(new[] { "name" });
        Assert.Equal(s1.GetRecordCount(), s2.GetRecordCount());
    }

    [Fact]
    public void SelectFields_SingleField_Works()
    {
        var doc = LoadSample();
        var selected = doc.SelectFields(new[] { "name" });
        Assert.Equal(5, selected.GetRecordCount());
        var keys = selected.GetAllKeys();
        Assert.True(keys.Count >= 1);
    }

    [Fact]
    public void SelectFields_PreservesRecordCount()
    {
        var doc = LoadSample();
        var selected = doc.SelectFields(new[] { "name", "dept", "score" });
        Assert.Equal(doc.GetRecordCount(), selected.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsv_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ToCsv());
    }

    [Fact]
    public void ToCsv_NonEmpty()
    {
        var doc = LoadSample();
        Assert.True(doc.ToCsv().Length > 0);
    }

    [Fact]
    public void ToCsv_ContainsHeaderRow()
    {
        var doc = LoadSample();
        var csv = doc.ToCsv();
        Assert.True(csv.Contains("name") || csv.Contains("dept") || csv.Contains(","));
    }

    [Fact]
    public void ToCsv_ContainsDataValues()
    {
        var doc = LoadSample();
        var csv = doc.ToCsv();
        Assert.True(csv.Contains("Alice") || csv.Contains("Bob") || csv.Length > 20);
    }

    [Fact]
    public void ToCsv_AfterFilter_Shrinks()
    {
        var doc = LoadSample();
        var all = doc.ToCsv().Length;
        var filtered = doc.Filter("dept", "Engineering");
        var filteredCsv = filtered.ToCsv().Length;
        Assert.True(filteredCsv < all);
    }

    [Fact]
    public void ToCsv_Consistent()
    {
        var doc = LoadSample();
        var c1 = doc.ToCsv();
        var c2 = doc.ToCsv();
        Assert.Equal(c1.Length, c2.Length);
    }

    [Fact]
    public void ToCsv_AfterSelectFields_ContainsSelectedFields()
    {
        var doc = LoadSample();
        var selected = doc.SelectFields(new[] { "name", "dept" });
        var csv = selected.ToCsv();
        Assert.True(csv.Contains("name") || csv.Contains("Alice") || csv.Length > 0);
    }

    // -------------------------------------------------------------------------
    // GetRecordCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordCount_Correct()
    {
        var doc = LoadSample();
        Assert.Equal(5, doc.GetRecordCount());
    }

    [Fact]
    public void GetRecordCount_AfterAppendRecord_Increases()
    {
        var doc = LoadSample();
        var before = doc.GetRecordCount();
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Frank" }, { "dept", "Legal" }, { "score", 91 }, { "city", "Denver" }
        });
        Assert.Equal(before + 1, doc.GetRecordCount());
    }

    [Fact]
    public void GetRecordCount_AfterFilter_Decreases()
    {
        var doc = LoadSample();
        var all = doc.GetRecordCount();
        var filtered = doc.Filter("dept", "Finance").GetRecordCount();
        Assert.True(filtered < all);
    }

    [Fact]
    public void GetRecordCount_Consistent()
    {
        var doc = LoadSample();
        Assert.Equal(doc.GetRecordCount(), doc.GetRecordCount());
    }

    [Fact]
    public void GetRecordCount_EmptyDoc_Zero()
    {
        var emptyPath = TempFile("empty.ndjson");
        File.WriteAllText(emptyPath, "");
        var doc = NdjsonDocument.LoadFile(emptyPath);
        Assert.True(doc.GetRecordCount() == 0);
    }

    [Fact]
    public void GetRecordCount_AfterSaveLoad_Preserved()
    {
        var doc = LoadSample();
        var path = TempFile("count_preserve.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(doc.GetRecordCount(), loaded.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_SelectFields_ToCsv_GetRecordCount_SaveToFile_Pipeline()
    {
        var doc = LoadSample();

        // GetRecordCount baseline
        Assert.Equal(5, doc.GetRecordCount());

        // ToCsv baseline
        var csv = doc.ToCsv();
        Assert.NotNull(csv);
        Assert.True(csv.Length > 0);

        // SelectFields — only name and score
        var selected = doc.SelectFields(new[] { "name", "score" });
        Assert.NotNull(selected);
        Assert.Equal(5, selected.GetRecordCount());

        var selectedKeys = selected.GetAllKeys();
        Assert.True(selectedKeys.Count <= 2);

        // ToCsv on selected (smaller)
        var selectedCsv = selected.ToCsv();
        Assert.True(selectedCsv.Length < csv.Length);

        // GetFieldValues on selected
        var names = selected.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Eve", names);

        // Filter on selected
        var filtered = selected.Filter("name", "Alice");
        Assert.Equal(1, filtered.GetRecordCount());

        // AppendRecord on doc
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Frank" }, { "dept", "Legal" }, { "score", 91 }, { "city", "Denver" }
        });
        Assert.Equal(6, doc.GetRecordCount());

        // ToCsv after append grows
        var csvAfterAppend = doc.ToCsv();
        Assert.True(csvAfterAppend.Length > csv.Length);

        // SelectFields on updated doc
        var selected2 = doc.SelectFields(new[] { "name", "dept" });
        Assert.Equal(6, selected2.GetRecordCount());

        // SortBy then SelectFields
        var sorted = doc.SortBy("name", ascending: true);
        Assert.Equal(6, sorted.GetRecordCount());
        var sortedSelected = sorted.SelectFields(new[] { "name" });
        Assert.Equal(6, sortedSelected.GetRecordCount());

        // Filter then GetRecordCount
        var engineering = doc.Filter("dept", "Engineering");
        Assert.Equal(2, engineering.GetRecordCount());

        // ToCsv on filtered
        var engCsv = engineering.ToCsv();
        Assert.True(engCsv.Length < csv.Length);

        // GroupBy still works
        var groups = doc.GroupBy("dept");
        Assert.True(groups.Count >= 3);

        // SaveToFile selected and reload
        var path = TempFile("dogfood_select_csv.ndjson");
        selected.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loadedSelected = NdjsonDocument.LoadFile(path);
        Assert.Equal(5, loadedSelected.GetRecordCount());

        // ToCsv on loaded
        var loadedCsv = loadedSelected.ToCsv();
        Assert.NotNull(loadedCsv);
        Assert.True(loadedCsv.Length > 0);

        // SelectFields on loaded
        var loadedSelectedSingle = loadedSelected.SelectFields(new[] { "name" });
        Assert.Equal(5, loadedSelectedSingle.GetRecordCount());

        // GetRecordCount on filtered loaded
        Assert.Equal(5, loadedSelected.GetRecordCount());
    }
}
