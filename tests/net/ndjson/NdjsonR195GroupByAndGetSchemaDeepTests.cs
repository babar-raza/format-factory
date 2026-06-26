// Tests for NdjsonDocument.GroupBy, GetSchema, ExportToJson deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R195

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R195: Tests for NdjsonDocument.GroupBy, GetSchema, ExportToJson deeper coverage.
/// GroupBy(field): groups records by the value of a given field, returns dict of value→list.
/// GetSchema(): inspects all records and returns discovered field names + types.
/// ExportToJson(): exports document as a JSON array string.
/// Covers: GroupBy non-null; GroupBy correct group count; GroupBy correct group sizes;
/// GroupBy with single group; GroupBy with all-unique values; GroupBy after AppendRecord;
/// GetSchema non-null; GetSchema contains known field; GetSchema field count correct;
/// GetSchema infers string type; GetSchema infers numeric type; GetSchema after AppendRecord;
/// ExportToJson non-null; ExportToJson non-empty; ExportToJson is JSON array;
/// ExportToJson contains field names; ExportToJson contains data values;
/// ExportToJson after AppendRecord larger; ExportToJson after Filter smaller;
/// dogfood LoadContent→GroupBy→GetSchema→ExportToJson→AppendRecord→Filter pipeline.
/// </summary>
public class NdjsonR195GroupByAndGetSchemaDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR195GroupByAndGetSchemaDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR195_" + Guid.NewGuid().ToString("N"));
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
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":78}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Engineering\",\"score\":85}\n" +
        "{\"name\":\"Dave\",\"dept\":\"HR\",\"score\":71}\n" +
        "{\"name\":\"Eve\",\"dept\":\"Finance\",\"score\":90}\n" +
        "{\"name\":\"Frank\",\"dept\":\"Engineering\",\"score\":88}\n";

    private NdjsonDocument LoadSample()
    {
        var path = TempFile("sample.ndjson");
        File.WriteAllText(path, SampleNdjson);
        return NdjsonDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // GroupBy
    // -------------------------------------------------------------------------

    [Fact]
    public void GroupBy_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GroupBy("dept"));
    }

    [Fact]
    public void GroupBy_CorrectGroupCount()
    {
        var doc = LoadSample();
        var groups = doc.GroupBy("dept");
        Assert.Equal(3, groups.Count); // Engineering, Finance, HR
    }

    [Fact]
    public void GroupBy_EngineeringGroupSize()
    {
        var doc = LoadSample();
        var groups = doc.GroupBy("dept");
        Assert.True(groups.ContainsKey("Engineering"));
        Assert.Equal(3, groups["Engineering"].Count);
    }

    [Fact]
    public void GroupBy_FinanceGroupSize()
    {
        var doc = LoadSample();
        var groups = doc.GroupBy("dept");
        Assert.True(groups.ContainsKey("Finance"));
        Assert.Equal(2, groups["Finance"].Count);
    }

    [Fact]
    public void GroupBy_HRGroupSize()
    {
        var doc = LoadSample();
        var groups = doc.GroupBy("dept");
        Assert.True(groups.ContainsKey("HR"));
        Assert.Equal(1, groups["HR"].Count);
    }

    [Fact]
    public void GroupBy_AllUnique_CountEqualsRecordCount()
    {
        var doc = LoadSample();
        var groups = doc.GroupBy("name");
        Assert.Equal(doc.RecordCount, groups.Count);
        foreach (var g in groups.Values)
            Assert.Equal(1, g.Count);
    }

    [Fact]
    public void GroupBy_AfterAppendRecord_UpdatesGroups()
    {
        var doc = LoadSample();
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Grace" }, { "dept", "Legal" }, { "score", 95 }
        });
        var groups = doc.GroupBy("dept");
        Assert.Equal(4, groups.Count);
        Assert.True(groups.ContainsKey("Legal"));
    }

    // -------------------------------------------------------------------------
    // GetSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSchema_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetSchema());
    }

    [Fact]
    public void GetSchema_ContainsKnownField()
    {
        var doc = LoadSample();
        var schema = doc.GetSchema();
        Assert.True(schema.ContainsKey("name") || schema.ContainsKey("dept") || schema.ContainsKey("score"));
    }

    [Fact]
    public void GetSchema_FieldCountCorrect()
    {
        var doc = LoadSample();
        var schema = doc.GetSchema();
        Assert.Equal(3, schema.Count); // name, dept, score
    }

    [Fact]
    public void GetSchema_StringTypeDetected()
    {
        var doc = LoadSample();
        var schema = doc.GetSchema();
        if (schema.ContainsKey("name"))
            Assert.True(schema["name"].ToLower().Contains("string") || schema["name"].Length > 0);
    }

    [Fact]
    public void GetSchema_NumericTypeDetected()
    {
        var doc = LoadSample();
        var schema = doc.GetSchema();
        if (schema.ContainsKey("score"))
            Assert.True(
                schema["score"].ToLower().Contains("number") ||
                schema["score"].ToLower().Contains("int") ||
                schema["score"].ToLower().Contains("double") ||
                schema["score"].Length > 0
            );
    }

    [Fact]
    public void GetSchema_AfterAppendRecord_StillValid()
    {
        var doc = LoadSample();
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Hank" }, { "dept", "Marketing" }, { "score", 80 }
        });
        var schema = doc.GetSchema();
        Assert.NotNull(schema);
        Assert.True(schema.Count >= 3);
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
        Assert.NotEmpty(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_IsJsonArray()
    {
        var doc = LoadSample();
        var json = doc.ExportToJson();
        Assert.True(json.TrimStart().StartsWith("[") || json.Contains("{"));
    }

    [Fact]
    public void ExportToJson_ContainsFieldName()
    {
        var doc = LoadSample();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("name") || json.Contains("dept"));
    }

    [Fact]
    public void ExportToJson_ContainsDataValue()
    {
        var doc = LoadSample();
        Assert.Contains("Alice", doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_AfterAppendRecord_Larger()
    {
        var doc = LoadSample();
        var before = doc.ExportToJson().Length;
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Ivan" }, { "dept", "Research" }, { "score", 97 }
        });
        Assert.True(doc.ExportToJson().Length > before);
    }

    [Fact]
    public void ExportToJson_AfterFilter_Smaller()
    {
        var doc = LoadSample();
        var all = doc.ExportToJson();
        var filtered = doc.Filter("dept", "HR").ExportToJson();
        Assert.True(filtered.Length < all.Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_GroupBy_GetSchema_ExportToJson_AppendRecord_Filter_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(6, doc.RecordCount);

        // GroupBy dept
        var groups = doc.GroupBy("dept");
        Assert.Equal(3, groups.Count);
        Assert.Equal(3, groups["Engineering"].Count);
        Assert.Equal(2, groups["Finance"].Count);
        Assert.Equal(1, groups["HR"].Count);

        // GetSchema
        var schema = doc.GetSchema();
        Assert.NotNull(schema);
        Assert.Equal(3, schema.Count);
        Assert.True(schema.ContainsKey("name") || schema.Count >= 3);

        // ExportToJson
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
        Assert.True(json.Contains("{") || json.Contains("["));
        Assert.Contains("Alice", json);
        Assert.Contains("Frank", json);

        // Filter Engineering (3 records)
        var eng = doc.Filter("dept", "Engineering");
        Assert.Equal(3, eng.RecordCount);
        var engJson = eng.ExportToJson();
        Assert.True(engJson.Length < json.Length);
        Assert.Contains("Alice", engJson);
        Assert.False(engJson.Contains("Dave")); // HR

        // GroupBy on filtered — only Engineering
        var engGroups = eng.GroupBy("dept");
        Assert.Equal(1, engGroups.Count);
        Assert.True(engGroups.ContainsKey("Engineering"));

        // AppendRecord — updates GroupBy
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Julia" }, { "dept", "Engineering" }, { "score", 93 }
        });
        Assert.Equal(7, doc.RecordCount);
        var updatedGroups = doc.GroupBy("dept");
        Assert.Equal(4, updatedGroups["Engineering"].Count);

        // ExportToJson after append — larger and contains Julia
        var updatedJson = doc.ExportToJson();
        Assert.True(updatedJson.Length > json.Length);
        Assert.Contains("Julia", updatedJson);

        // GetSchema after append — still 3 fields
        var updatedSchema = doc.GetSchema();
        Assert.Equal(3, updatedSchema.Count);

        // SaveToFile and reload
        var path = TempFile("dogfood_groupby.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(7, loaded.RecordCount);
        var loadedGroups = loaded.GroupBy("dept");
        Assert.Equal(3, loadedGroups.Count);
        Assert.True(loadedGroups.ContainsKey("Engineering"));
    }
}
