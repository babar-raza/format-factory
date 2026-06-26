// Tests for NdjsonDocument.ExportToJson, GetFieldNames, ToNdjsonString deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R209

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R209: Tests for NdjsonDocument.ExportToJson, GetFieldNames, ToNdjsonString deeper.
/// ExportToJson(): exports the document as a formatted JSON array string.
/// GetFieldNames(): returns all unique field names across all records.
/// ToNdjsonString(): exports the document as newline-delimited JSON string.
/// Covers: ExportToJson non-null; ExportToJson non-empty; ExportToJson has brackets;
/// ExportToJson has field names; ExportToJson has data values; ExportToJson after AppendRecord grows;
/// ExportToJson after Filter shrinks; ExportToJson consistent; ExportToJson no-throw;
/// ExportToJson save-load consistent;
/// GetFieldNames non-null; GetFieldNames non-empty; GetFieldNames count correct;
/// GetFieldNames contains known; GetFieldNames no duplicates; GetFieldNames consistent;
/// GetFieldNames after AppendRecord with new field grows; GetFieldNames after Filter same;
/// GetFieldNames no-throw; GetFieldNames empty doc empty;
/// ToNdjsonString non-null; ToNdjsonString non-empty; ToNdjsonString has braces;
/// ToNdjsonString has field names; ToNdjsonString after AppendRecord grows;
/// ToNdjsonString consistent; ToNdjsonString newline per record;
/// dogfood CreateDoc→GetFieldNames→ExportToJson→ToNdjsonString→WriteToFile pipeline.
/// </summary>
public class NdjsonR209ExportToJsonAndGetFieldNamesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR209ExportToJsonAndGetFieldNamesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR209_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NdjsonDocument CreateBaseDoc()
    {
        var doc = NdjsonDocument.CreateNew();
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 1, ["name"] = "Alice", ["dept"] = "Engineering", ["score"] = 92 });
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 2, ["name"] = "Bob", ["dept"] = "Marketing", ["score"] = 78 });
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 3, ["name"] = "Carol", ["dept"] = "Engineering", ["score"] = 88 });
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 4, ["name"] = "Dave", ["dept"] = "Finance", ["score"] = 85 });
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 5, ["name"] = "Eve", ["dept"] = "Engineering", ["score"] = 95 });
        return doc;
    }

    // -------------------------------------------------------------------------
    // ExportToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToJson_NonNull()
    {
        var doc = CreateBaseDoc();
        Assert.NotNull(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_NonEmpty()
    {
        var doc = CreateBaseDoc();
        Assert.NotEmpty(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_HasBrackets()
    {
        var doc = CreateBaseDoc();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("[") || json.Contains("{"));
    }

    [Fact]
    public void ExportToJson_HasFieldNames()
    {
        var doc = CreateBaseDoc();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("name") || json.Contains("dept") || json.Contains("score"));
    }

    [Fact]
    public void ExportToJson_HasDataValues()
    {
        var doc = CreateBaseDoc();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("Alice") || json.Contains("Bob") || json.Contains("Carol"));
    }

    [Fact]
    public void ExportToJson_AfterAppendRecord_Grows()
    {
        var doc = CreateBaseDoc();
        var before = doc.ExportToJson().Length;
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 6, ["name"] = "Frank", ["dept"] = "HR", ["score"] = 80 });
        var after = doc.ExportToJson().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToJson_AfterFilter_Shrinks()
    {
        var doc = CreateBaseDoc();
        var before = doc.ExportToJson().Length;
        var filtered = doc.Filter("dept", "Engineering");
        var after = filtered.ExportToJson().Length;
        Assert.True(after < before);
    }

    [Fact]
    public void ExportToJson_Consistent()
    {
        var doc = CreateBaseDoc();
        var j1 = doc.ExportToJson();
        var j2 = doc.ExportToJson();
        Assert.Equal(j1.Length, j2.Length);
    }

    [Fact]
    public void ExportToJson_NoThrow()
    {
        var doc = CreateBaseDoc();
        var ex = Record.Exception(() => doc.ExportToJson());
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToJson_SaveLoadConsistent()
    {
        var doc = CreateBaseDoc();
        var json1 = doc.ExportToJson();
        var path = TempFile("export_json_saveload.ndjson");
        doc.WriteToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var json2 = loaded.ExportToJson();
        Assert.True(Math.Abs(json1.Length - json2.Length) <= 10);
    }

    // -------------------------------------------------------------------------
    // GetFieldNames
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldNames_NonNull()
    {
        var doc = CreateBaseDoc();
        Assert.NotNull(doc.GetFieldNames());
    }

    [Fact]
    public void GetFieldNames_NonEmpty()
    {
        var doc = CreateBaseDoc();
        Assert.True(doc.GetFieldNames().Count > 0);
    }

    [Fact]
    public void GetFieldNames_CountCorrect()
    {
        var doc = CreateBaseDoc();
        // id, name, dept, score = 4
        Assert.Equal(4, doc.GetFieldNames().Count);
    }

    [Fact]
    public void GetFieldNames_ContainsKnown()
    {
        var doc = CreateBaseDoc();
        var fields = doc.GetFieldNames();
        Assert.Contains("id", fields);
        Assert.Contains("name", fields);
        Assert.Contains("dept", fields);
        Assert.Contains("score", fields);
    }

    [Fact]
    public void GetFieldNames_NoDuplicates()
    {
        var doc = CreateBaseDoc();
        var fields = doc.GetFieldNames();
        var set = new HashSet<string>(fields);
        Assert.Equal(set.Count, fields.Count);
    }

    [Fact]
    public void GetFieldNames_Consistent()
    {
        var doc = CreateBaseDoc();
        var f1 = doc.GetFieldNames();
        var f2 = doc.GetFieldNames();
        Assert.Equal(f1.Count, f2.Count);
    }

    [Fact]
    public void GetFieldNames_AfterAppendRecord_WithNewField_Grows()
    {
        var doc = CreateBaseDoc();
        var before = doc.GetFieldNames().Count;
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 6, ["name"] = "Frank", ["dept"] = "HR", ["score"] = 80, ["email"] = "frank@example.com" });
        var after = doc.GetFieldNames().Count;
        Assert.True(after > before);
    }

    [Fact]
    public void GetFieldNames_AfterFilter_SameFields()
    {
        var doc = CreateBaseDoc();
        var all = doc.GetFieldNames();
        var filtered = doc.Filter("dept", "Engineering");
        var filtFields = filtered.GetFieldNames();
        // Fields should be same or subset
        Assert.True(filtFields.Count <= all.Count);
    }

    [Fact]
    public void GetFieldNames_NoThrow()
    {
        var doc = CreateBaseDoc();
        var ex = Record.Exception(() => doc.GetFieldNames());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldNames_EmptyDoc_EmptyOrNull()
    {
        var doc = NdjsonDocument.CreateNew();
        var fields = doc.GetFieldNames();
        Assert.True(fields == null || fields.Count == 0);
    }

    // -------------------------------------------------------------------------
    // ToNdjsonString
    // -------------------------------------------------------------------------

    [Fact]
    public void ToNdjsonString_NonNull()
    {
        var doc = CreateBaseDoc();
        Assert.NotNull(doc.ToNdjsonString());
    }

    [Fact]
    public void ToNdjsonString_NonEmpty()
    {
        var doc = CreateBaseDoc();
        Assert.NotEmpty(doc.ToNdjsonString());
    }

    [Fact]
    public void ToNdjsonString_HasBraces()
    {
        var doc = CreateBaseDoc();
        var ndjson = doc.ToNdjsonString();
        Assert.Contains("{", ndjson);
    }

    [Fact]
    public void ToNdjsonString_HasFieldNames()
    {
        var doc = CreateBaseDoc();
        var ndjson = doc.ToNdjsonString();
        Assert.True(ndjson.Contains("name") || ndjson.Contains("dept"));
    }

    [Fact]
    public void ToNdjsonString_AfterAppendRecord_Grows()
    {
        var doc = CreateBaseDoc();
        var before = doc.ToNdjsonString().Length;
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 6, ["name"] = "Frank", ["dept"] = "HR", ["score"] = 80 });
        var after = doc.ToNdjsonString().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ToNdjsonString_Consistent()
    {
        var doc = CreateBaseDoc();
        var n1 = doc.ToNdjsonString();
        var n2 = doc.ToNdjsonString();
        Assert.Equal(n1.Length, n2.Length);
    }

    [Fact]
    public void ToNdjsonString_NewlinePerRecord()
    {
        var doc = CreateBaseDoc();
        var ndjson = doc.ToNdjsonString();
        var lines = ndjson.Trim().Split('\n');
        Assert.True(lines.Length >= doc.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldNames_ExportToJson_ToNdjsonString_WriteToFile_Pipeline()
    {
        // Build multi-field document
        var doc = NdjsonDocument.CreateNew();
        var records = new[]
        {
            new Dictionary<string, object> { ["id"] = 1, ["product"] = "Widget A", ["category"] = "Electronics", ["price"] = 29.99, ["inStock"] = true },
            new Dictionary<string, object> { ["id"] = 2, ["product"] = "Gadget B", ["category"] = "Electronics", ["price"] = 49.99, ["inStock"] = true },
            new Dictionary<string, object> { ["id"] = 3, ["product"] = "Tool C", ["category"] = "Hardware", ["price"] = 19.99, ["inStock"] = false },
            new Dictionary<string, object> { ["id"] = 4, ["product"] = "Device D", ["category"] = "Electronics", ["price"] = 99.99, ["inStock"] = true },
            new Dictionary<string, object> { ["id"] = 5, ["product"] = "Part E", ["category"] = "Hardware", ["price"] = 9.99, ["inStock"] = true },
            new Dictionary<string, object> { ["id"] = 6, ["product"] = "Kit F", ["category"] = "Hardware", ["price"] = 39.99, ["inStock"] = false },
        };
        foreach (var r in records) doc.AppendRecord(r);
        Assert.Equal(6, doc.GetRecordCount());

        // GetFieldNames baseline
        var fields = doc.GetFieldNames();
        Assert.NotNull(fields);
        Assert.Equal(5, fields.Count);
        Assert.Contains("id", fields);
        Assert.Contains("product", fields);
        Assert.Contains("category", fields);
        Assert.Contains("price", fields);
        Assert.Contains("inStock", fields);

        // ExportToJson baseline
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
        Assert.True(json.Contains("[") || json.Contains("{"));
        Assert.True(json.Contains("Widget") || json.Contains("product"));

        // ToNdjsonString baseline
        var ndjson = doc.ToNdjsonString();
        Assert.NotNull(ndjson);
        Assert.NotEmpty(ndjson);
        Assert.Contains("{", ndjson);

        // AppendRecord with new field
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 7, ["product"] = "Module G", ["category"] = "Electronics", ["price"] = 149.99, ["inStock"] = true, ["rating"] = 4.8 });
        Assert.Equal(7, doc.GetRecordCount());

        var fieldsAfterAppend = doc.GetFieldNames();
        Assert.True(fieldsAfterAppend.Count > fields.Count);
        Assert.Contains("rating", fieldsAfterAppend);

        // ExportToJson grows after AppendRecord
        var jsonAfterAppend = doc.ExportToJson();
        Assert.True(jsonAfterAppend.Length > json.Length);

        // ToNdjsonString grows
        var ndjsonAfterAppend = doc.ToNdjsonString();
        Assert.True(ndjsonAfterAppend.Length > ndjson.Length);

        // Filter Electronics
        var electronics = doc.Filter("category", "Electronics");
        var elecFields = electronics.GetFieldNames();
        Assert.NotNull(elecFields);

        // ExportToJson on filtered
        var elecJson = electronics.ExportToJson();
        Assert.True(elecJson.Length < jsonAfterAppend.Length);

        // GetFieldNames after Filter same or subset
        Assert.True(elecFields.Count <= fieldsAfterAppend.Count);

        // Count by category
        var elecCount = doc.Count("category", "Electronics");
        Assert.Equal(4, elecCount);
        var hwCount = doc.Count("category", "Hardware");
        Assert.Equal(3, hwCount);

        // GetRecordCount consistent
        Assert.Equal(doc.GetRecordCount(), doc.GetRecordCount());

        // ExportToJson consistent
        var j1 = doc.ExportToJson();
        var j2 = doc.ExportToJson();
        Assert.Equal(j1.Length, j2.Length);

        // ToNdjsonString consistent
        var n1 = doc.ToNdjsonString();
        var n2 = doc.ToNdjsonString();
        Assert.Equal(n1.Length, n2.Length);

        // GetFieldNames no duplicates
        var finalFields = doc.GetFieldNames();
        var fieldSet = new HashSet<string>(finalFields);
        Assert.Equal(fieldSet.Count, finalFields.Count);

        // WriteToFile
        var path = TempFile("dogfood_export_fields.ndjson");
        doc.WriteToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(doc.GetRecordCount(), loaded.GetRecordCount());

        var loadedFields = loaded.GetFieldNames();
        Assert.NotNull(loadedFields);
        Assert.True(loadedFields.Count >= fields.Count);

        // ExportToJson on loaded
        var loadedJson = loaded.ExportToJson();
        Assert.NotNull(loadedJson);
        Assert.NotEmpty(loadedJson);

        // ToNdjsonString on loaded
        var loadedNdjson = loaded.ToNdjsonString();
        Assert.NotNull(loadedNdjson);
        Assert.NotEmpty(loadedNdjson);

        // AppendRecord on loaded
        loaded.AppendRecord(new Dictionary<string, object>
            { ["id"] = 8, ["product"] = "Sensor H", ["category"] = "Electronics", ["price"] = 24.99, ["inStock"] = true });
        Assert.Equal(doc.GetRecordCount() + 1, loaded.GetRecordCount());

        // Final GetFieldNames
        var finalLoadedFields = loaded.GetFieldNames();
        Assert.NotNull(finalLoadedFields);

        // Final WriteToFile
        var path2 = TempFile("dogfood_loaded_fields.ndjson");
        loaded.WriteToFile(path2);
        Assert.True(File.Exists(path2));
        var final = NdjsonDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRecordCount(), final.GetRecordCount());
    }
}
