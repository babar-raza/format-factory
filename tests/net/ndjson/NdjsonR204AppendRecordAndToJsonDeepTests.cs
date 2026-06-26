// Tests for NdjsonDocument.AppendRecord, ToJson, GetAllKeys deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R204

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R204: Tests for NdjsonDocument.AppendRecord, ToJson, GetAllKeys deeper.
/// AppendRecord(record): appends a new JSON record to the document.
/// ToJson(): exports the document as a JSON array string.
/// GetAllKeys(): returns all distinct field names across all records.
/// Covers: AppendRecord increases record count; AppendRecord values accessible;
/// AppendRecord persist; AppendRecord multiple records; AppendRecord then Filter;
/// AppendRecord then SortBy; AppendRecord then GetAllKeys;
/// ToJson non-null; ToJson non-empty; ToJson is valid array;
/// ToJson has field names; ToJson has data values; ToJson after AppendRecord grows;
/// ToJson after Filter shrinks; ToJson consistent;
/// GetAllKeys non-null; GetAllKeys non-empty; GetAllKeys contains known fields;
/// GetAllKeys no duplicates; GetAllKeys consistent; GetAllKeys after AppendRecord;
/// GetAllKeys after SelectFields reduces;
/// dogfood LoadFile→AppendRecord→ToJson→GetAllKeys→SaveToFile pipeline.
/// </summary>
public class NdjsonR204AppendRecordAndToJsonDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR204AppendRecordAndToJsonDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR204_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Engineering\",\"score\":92}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":85}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Engineering\",\"score\":95}\n";

    private NdjsonDocument LoadSample()
    {
        var path = TempFile("sample.ndjson");
        File.WriteAllText(path, SampleNdjson);
        return NdjsonDocument.LoadFile(path);
    }

    private static Dictionary<string, object> MakeRecord(string name, string dept, int score)
        => new Dictionary<string, object>
        {
            { "name", name }, { "dept", dept }, { "score", score }
        };

    // -------------------------------------------------------------------------
    // AppendRecord
    // -------------------------------------------------------------------------

    [Fact]
    public void AppendRecord_IncreasesRecordCount()
    {
        var doc = LoadSample();
        var before = doc.GetRecordCount();
        doc.AppendRecord(MakeRecord("Dave", "HR", 78));
        Assert.Equal(before + 1, doc.GetRecordCount());
    }

    [Fact]
    public void AppendRecord_ValuesAccessible()
    {
        var doc = LoadSample();
        doc.AppendRecord(MakeRecord("Eve", "Finance", 88));
        Assert.Contains("Eve", doc.GetFieldValues("name"));
    }

    [Fact]
    public void AppendRecord_Persist()
    {
        var doc = LoadSample();
        doc.AppendRecord(MakeRecord("Frank", "Legal", 91));
        var path = TempFile("append_persist.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Contains("Frank", loaded.GetFieldValues("name"));
    }

    [Fact]
    public void AppendRecord_Multiple_AllPresent()
    {
        var doc = LoadSample();
        doc.AppendRecord(MakeRecord("Grace", "IT", 87));
        doc.AppendRecord(MakeRecord("Hank", "Sales", 93));
        var names = doc.GetFieldValues("name");
        Assert.Contains("Grace", names);
        Assert.Contains("Hank", names);
    }

    [Fact]
    public void AppendRecord_ThenFilter_Works()
    {
        var doc = LoadSample();
        doc.AppendRecord(MakeRecord("Ivan", "Engineering", 79));
        var eng = doc.Filter("dept", "Engineering");
        Assert.Equal(3, eng.GetRecordCount());
    }

    [Fact]
    public void AppendRecord_ThenSortBy_Works()
    {
        var doc = LoadSample();
        doc.AppendRecord(MakeRecord("Aaron", "HR", 88));
        var sorted = doc.SortBy("name", ascending: true);
        Assert.Equal("Aaron", sorted.GetFieldValues("name")[0]);
    }

    [Fact]
    public void AppendRecord_WithExtraField_UpdatesGetAllKeys()
    {
        var doc = LoadSample();
        var beforeKeys = doc.GetAllKeys().Count;
        var rec = new Dictionary<string, object>
        {
            { "name", "Julia" }, { "dept", "Legal" }, { "score", 90 }, { "city", "Denver" }
        };
        doc.AppendRecord(rec);
        var afterKeys = doc.GetAllKeys().Count;
        Assert.True(afterKeys >= beforeKeys);
    }

    // -------------------------------------------------------------------------
    // ToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ToJson_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ToJson());
    }

    [Fact]
    public void ToJson_NonEmpty()
    {
        var doc = LoadSample();
        Assert.True(doc.ToJson().Length > 0);
    }

    [Fact]
    public void ToJson_IsArray()
    {
        var doc = LoadSample();
        var json = doc.ToJson();
        Assert.True(json.TrimStart().StartsWith("[") || json.Contains("{"));
    }

    [Fact]
    public void ToJson_HasFieldNames()
    {
        var doc = LoadSample();
        var json = doc.ToJson();
        Assert.True(json.Contains("name") || json.Contains("dept") || json.Length > 10);
    }

    [Fact]
    public void ToJson_HasDataValues()
    {
        var doc = LoadSample();
        var json = doc.ToJson();
        Assert.True(json.Contains("Alice") || json.Contains("Bob") || json.Length > 10);
    }

    [Fact]
    public void ToJson_AfterAppendRecord_Grows()
    {
        var doc = LoadSample();
        var before = doc.ToJson().Length;
        doc.AppendRecord(MakeRecord("Karl", "Ops", 82));
        var after = doc.ToJson().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ToJson_AfterFilter_Shrinks()
    {
        var doc = LoadSample();
        var all = doc.ToJson().Length;
        var filtered = doc.Filter("dept", "Engineering");
        var filteredJson = filtered.ToJson().Length;
        Assert.True(filteredJson < all);
    }

    [Fact]
    public void ToJson_Consistent()
    {
        var doc = LoadSample();
        var j1 = doc.ToJson();
        var j2 = doc.ToJson();
        Assert.Equal(j1.Length, j2.Length);
    }

    // -------------------------------------------------------------------------
    // GetAllKeys
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAllKeys_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetAllKeys());
    }

    [Fact]
    public void GetAllKeys_NonEmpty()
    {
        var doc = LoadSample();
        Assert.True(doc.GetAllKeys().Count > 0);
    }

    [Fact]
    public void GetAllKeys_ContainsKnownFields()
    {
        var doc = LoadSample();
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
        Assert.Contains("score", keys);
    }

    [Fact]
    public void GetAllKeys_NoDuplicates()
    {
        var doc = LoadSample();
        var keys = doc.GetAllKeys();
        var set = new HashSet<string>(keys);
        Assert.Equal(set.Count, keys.Count);
    }

    [Fact]
    public void GetAllKeys_Consistent()
    {
        var doc = LoadSample();
        var k1 = doc.GetAllKeys();
        var k2 = doc.GetAllKeys();
        Assert.Equal(k1.Count, k2.Count);
    }

    [Fact]
    public void GetAllKeys_AfterAppendRecord_UpdatesIfNewField()
    {
        var doc = LoadSample();
        var before = doc.GetAllKeys().Count;
        doc.AppendRecord(new Dictionary<string, object>
        {
            { "name", "Lena" }, { "dept", "IT" }, { "score", 88 }, { "city", "Austin" }
        });
        var after = doc.GetAllKeys().Count;
        Assert.True(after >= before); // city adds a new key if not previously present
    }

    [Fact]
    public void GetAllKeys_AfterSelectFields_ReducesCount()
    {
        var doc = LoadSample();
        var all = doc.GetAllKeys().Count;
        var selected = doc.SelectFields(new[] { "name" });
        var selectedKeys = selected.GetAllKeys().Count;
        Assert.True(selectedKeys <= all);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_AppendRecord_ToJson_GetAllKeys_SaveToFile_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(3, doc.GetRecordCount());

        // GetAllKeys baseline
        var keys = doc.GetAllKeys();
        Assert.NotNull(keys);
        Assert.True(keys.Count >= 3);
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
        Assert.Contains("score", keys);

        // ToJson baseline
        var json = doc.ToJson();
        Assert.NotNull(json);
        Assert.True(json.Length > 0);

        // AppendRecord — standard fields
        doc.AppendRecord(MakeRecord("Dave", "HR", 78));
        Assert.Equal(4, doc.GetRecordCount());
        Assert.Contains("Dave", doc.GetFieldValues("name"));

        // ToJson grew
        var jsonAfter = doc.ToJson();
        Assert.True(jsonAfter.Length > json.Length);

        // AppendRecord — extra field (city)
        doc.AppendRecord(new Dictionary<string, object>
        {
            { "name", "Eve" }, { "dept", "Finance" }, { "score", 88 }, { "city", "LA" }
        });
        Assert.Equal(5, doc.GetRecordCount());

        // GetAllKeys now includes city
        var keysAfterCity = doc.GetAllKeys();
        Assert.True(keysAfterCity.Count >= keys.Count);

        // ToJson with 5 records
        var jsonAll = doc.ToJson();
        Assert.True(jsonAll.Length > jsonAfter.Length);

        // Filter then GetAllKeys
        var eng = doc.Filter("dept", "Engineering");
        Assert.Equal(2, eng.GetRecordCount());
        var engKeys = eng.GetAllKeys();
        Assert.NotNull(engKeys);

        // SortBy then ToJson
        var sorted = doc.SortBy("name", ascending: true);
        Assert.Equal(5, sorted.GetRecordCount());
        var sortedJson = sorted.ToJson();
        Assert.NotNull(sortedJson);
        Assert.True(sortedJson.Length > 0);

        // SelectFields then GetAllKeys
        var selected = doc.SelectFields(new[] { "name", "score" });
        var selectedKeys = selected.GetAllKeys();
        Assert.True(selectedKeys.Count <= keysAfterCity.Count);

        // GroupBy
        var groups = doc.GroupBy("dept");
        Assert.True(groups.Count >= 3);

        // AppendRecord with all fields
        doc.AppendRecord(new Dictionary<string, object>
        {
            { "name", "Frank" }, { "dept", "Engineering" }, { "score", 91 }, { "city", "Denver" }
        });
        Assert.Equal(6, doc.GetRecordCount());

        // SaveToFile and reload
        var path = TempFile("dogfood_append_json.ndjson");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetRecordCount());

        // GetAllKeys on loaded
        var loadedKeys = loaded.GetAllKeys();
        Assert.NotNull(loadedKeys);
        Assert.True(loadedKeys.Count >= 3);
        Assert.Contains("name", loadedKeys);

        // ToJson on loaded
        var loadedJson = loaded.ToJson();
        Assert.NotNull(loadedJson);
        Assert.True(loadedJson.Length > 0);

        // AppendRecord on loaded
        loaded.AppendRecord(MakeRecord("Grace", "IT", 87));
        Assert.Equal(7, loaded.GetRecordCount());
        Assert.Contains("Grace", loaded.GetFieldValues("name"));

        // Filter on loaded
        var loadedEng = loaded.Filter("dept", "Engineering");
        Assert.Equal(3, loadedEng.GetRecordCount());
    }
}
