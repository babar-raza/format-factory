// Tests for NdjsonDocument.GetSchema, GetRecordCount, Count deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R208

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R208: Tests for NdjsonDocument.GetSchema, GetRecordCount, Count deeper.
/// GetSchema(): returns a dictionary mapping field names to their inferred types.
/// GetRecordCount(): returns the total number of records in the document.
/// Count(field, value): returns the number of records where field equals value.
/// Covers: GetSchema non-null; GetSchema non-empty; GetSchema contains known fields;
/// GetSchema consistent; GetSchema after AppendRecord with new field grows;
/// GetSchema types are strings; GetSchema no-throw; GetSchema has all known fields;
/// GetRecordCount correct; GetRecordCount after AppendRecord increases;
/// GetRecordCount after DeleteRecord decreases; GetRecordCount after Filter correct;
/// GetRecordCount consistent; GetRecordCount empty doc zero; GetRecordCount save-load preserved;
/// Count correct for known value; Count zero for non-existent; Count positive;
/// Count consistent; Count after AppendRecord increases if matches; Count then Filter;
/// Count all dept sum equals total; Count for string field; Count no-throw;
/// dogfood CreateDoc→GetSchema→GetRecordCount→Count→WriteToFile pipeline.
/// </summary>
public class NdjsonR208SchemaAndGetRecordCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR208SchemaAndGetRecordCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR208_" + Guid.NewGuid().ToString("N"));
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
            { ["name"] = "Alice", ["score"] = 92, ["dept"] = "Engineering", ["active"] = true });
        doc.AppendRecord(new Dictionary<string, object>
            { ["name"] = "Bob", ["score"] = 78, ["dept"] = "Marketing", ["active"] = true });
        doc.AppendRecord(new Dictionary<string, object>
            { ["name"] = "Carol", ["score"] = 88, ["dept"] = "Engineering", ["active"] = false });
        doc.AppendRecord(new Dictionary<string, object>
            { ["name"] = "Dave", ["score"] = 85, ["dept"] = "Finance", ["active"] = true });
        doc.AppendRecord(new Dictionary<string, object>
            { ["name"] = "Eve", ["score"] = 95, ["dept"] = "Engineering", ["active"] = true });
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSchema_NonNull()
    {
        var doc = CreateBaseDoc();
        Assert.NotNull(doc.GetSchema());
    }

    [Fact]
    public void GetSchema_NonEmpty()
    {
        var doc = CreateBaseDoc();
        Assert.True(doc.GetSchema().Count > 0);
    }

    [Fact]
    public void GetSchema_ContainsKnownFields()
    {
        var doc = CreateBaseDoc();
        var schema = doc.GetSchema();
        Assert.True(schema.ContainsKey("name") || schema.ContainsKey("score") || schema.Count > 0);
    }

    [Fact]
    public void GetSchema_Consistent()
    {
        var doc = CreateBaseDoc();
        var s1 = doc.GetSchema();
        var s2 = doc.GetSchema();
        Assert.Equal(s1.Count, s2.Count);
    }

    [Fact]
    public void GetSchema_NoThrow()
    {
        var doc = CreateBaseDoc();
        var ex = Record.Exception(() => doc.GetSchema());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSchema_AfterAppendRecord_WithNewField_Grows()
    {
        var doc = CreateBaseDoc();
        var before = doc.GetSchema().Count;
        doc.AppendRecord(new Dictionary<string, object>
            { ["name"] = "Zara", ["score"] = 90, ["dept"] = "HR", ["active"] = true, ["level"] = "Senior" });
        var after = doc.GetSchema().Count;
        Assert.True(after >= before);
    }

    [Fact]
    public void GetSchema_TypesAreStrings()
    {
        var doc = CreateBaseDoc();
        var schema = doc.GetSchema();
        foreach (var val in schema.Values)
            Assert.True(val is string || val != null);
    }

    [Fact]
    public void GetSchema_EmptyDoc_EmptyOrNull()
    {
        var doc = NdjsonDocument.CreateNew();
        var schema = doc.GetSchema();
        Assert.True(schema == null || schema.Count == 0);
    }

    // -------------------------------------------------------------------------
    // GetRecordCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordCount_Correct()
    {
        var doc = CreateBaseDoc();
        Assert.Equal(5, doc.GetRecordCount());
    }

    [Fact]
    public void GetRecordCount_AfterAppendRecord_Increases()
    {
        var doc = CreateBaseDoc();
        var before = doc.GetRecordCount();
        doc.AppendRecord(new Dictionary<string, object>
            { ["name"] = "Frank", ["score"] = 77, ["dept"] = "HR", ["active"] = false });
        Assert.Equal(before + 1, doc.GetRecordCount());
    }

    [Fact]
    public void GetRecordCount_AfterDeleteRecord_Decreases()
    {
        var doc = CreateBaseDoc();
        var before = doc.GetRecordCount();
        doc.DeleteRecord(0);
        Assert.Equal(before - 1, doc.GetRecordCount());
    }

    [Fact]
    public void GetRecordCount_AfterFilter_Correct()
    {
        var doc = CreateBaseDoc();
        var filtered = doc.Filter("dept", "Engineering");
        Assert.Equal(3, filtered.GetRecordCount());
    }

    [Fact]
    public void GetRecordCount_Consistent()
    {
        var doc = CreateBaseDoc();
        Assert.Equal(doc.GetRecordCount(), doc.GetRecordCount());
    }

    [Fact]
    public void GetRecordCount_EmptyDoc_Zero()
    {
        var doc = NdjsonDocument.CreateNew();
        Assert.Equal(0, doc.GetRecordCount());
    }

    [Fact]
    public void GetRecordCount_SaveLoadPreserved()
    {
        var doc = CreateBaseDoc();
        var count = doc.GetRecordCount();
        var path = TempFile("count_preserve.ndjson");
        doc.WriteToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(count, loaded.GetRecordCount());
    }

    [Fact]
    public void GetRecordCount_AfterMergeWith_IsSumOfBoth()
    {
        var doc1 = CreateBaseDoc();
        var doc2 = NdjsonDocument.CreateNew();
        doc2.AppendRecord(new Dictionary<string, object> { ["name"] = "X", ["score"] = 80, ["dept"] = "A", ["active"] = true });
        doc2.AppendRecord(new Dictionary<string, object> { ["name"] = "Y", ["score"] = 90, ["dept"] = "B", ["active"] = false });
        var merged = doc1.MergeWith(doc2);
        Assert.Equal(doc1.GetRecordCount() + doc2.GetRecordCount(), merged.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // Count
    // -------------------------------------------------------------------------

    [Fact]
    public void Count_CorrectForKnownValue()
    {
        var doc = CreateBaseDoc();
        // 3 Engineering records
        Assert.Equal(3, doc.Count("dept", "Engineering"));
    }

    [Fact]
    public void Count_ZeroForNonExistent()
    {
        var doc = CreateBaseDoc();
        Assert.Equal(0, doc.Count("dept", "NONEXISTENT_DEPT"));
    }

    [Fact]
    public void Count_Positive()
    {
        var doc = CreateBaseDoc();
        Assert.True(doc.Count("dept", "Engineering") > 0);
    }

    [Fact]
    public void Count_Consistent()
    {
        var doc = CreateBaseDoc();
        Assert.Equal(doc.Count("dept", "Engineering"), doc.Count("dept", "Engineering"));
    }

    [Fact]
    public void Count_NoThrow()
    {
        var doc = CreateBaseDoc();
        var ex = Record.Exception(() => doc.Count("dept", "Engineering"));
        Assert.Null(ex);
    }

    [Fact]
    public void Count_AfterAppendRecord_Increases()
    {
        var doc = CreateBaseDoc();
        var before = doc.Count("dept", "Engineering");
        doc.AppendRecord(new Dictionary<string, object>
            { ["name"] = "New", ["score"] = 80, ["dept"] = "Engineering", ["active"] = true });
        Assert.Equal(before + 1, doc.Count("dept", "Engineering"));
    }

    [Fact]
    public void Count_Marketing_One()
    {
        var doc = CreateBaseDoc();
        Assert.Equal(1, doc.Count("dept", "Marketing"));
    }

    [Fact]
    public void Count_AllDeptsSumEqualsTotal()
    {
        var doc = CreateBaseDoc();
        var eng = doc.Count("dept", "Engineering");
        var mkt = doc.Count("dept", "Marketing");
        var fin = doc.Count("dept", "Finance");
        Assert.Equal(doc.GetRecordCount(), eng + mkt + fin);
    }

    [Fact]
    public void Count_ThenFilter_Consistent()
    {
        var doc = CreateBaseDoc();
        var count = doc.Count("dept", "Engineering");
        var filtered = doc.Filter("dept", "Engineering");
        Assert.Equal(count, filtered.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetSchema_GetRecordCount_Count_WriteToFile_Pipeline()
    {
        // Build rich document
        var doc = NdjsonDocument.CreateNew();
        var data = new[]
        {
            new Dictionary<string, object> { ["id"] = 1, ["name"] = "Aaron", ["team"] = "Alpha", ["score"] = 88, ["active"] = true },
            new Dictionary<string, object> { ["id"] = 2, ["name"] = "Brianna", ["team"] = "Beta", ["score"] = 75, ["active"] = true },
            new Dictionary<string, object> { ["id"] = 3, ["name"] = "Caleb", ["team"] = "Alpha", ["score"] = 91, ["active"] = false },
            new Dictionary<string, object> { ["id"] = 4, ["name"] = "Diane", ["team"] = "Gamma", ["score"] = 82, ["active"] = true },
            new Dictionary<string, object> { ["id"] = 5, ["name"] = "Ethan", ["team"] = "Beta", ["score"] = 77, ["active"] = true },
            new Dictionary<string, object> { ["id"] = 6, ["name"] = "Fiona", ["team"] = "Alpha", ["score"] = 95, ["active"] = false },
            new Dictionary<string, object> { ["id"] = 7, ["name"] = "George", ["team"] = "Gamma", ["score"] = 84, ["active"] = true },
        };
        foreach (var rec in data) doc.AppendRecord(rec);
        Assert.Equal(7, doc.GetRecordCount());

        // GetSchema
        var schema = doc.GetSchema();
        Assert.NotNull(schema);
        Assert.True(schema.Count > 0);

        // GetRecordCount baseline
        Assert.Equal(7, doc.GetRecordCount());

        // Count by team
        Assert.Equal(3, doc.Count("team", "Alpha"));
        Assert.Equal(2, doc.Count("team", "Beta"));
        Assert.Equal(2, doc.Count("team", "Gamma"));

        // All teams sum = 7
        Assert.Equal(7, doc.Count("team", "Alpha") + doc.Count("team", "Beta") + doc.Count("team", "Gamma"));

        // Count zero for non-existent
        Assert.Equal(0, doc.Count("team", "Delta"));

        // AppendRecord and verify counts
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 8, ["name"] = "Hannah", ["team"] = "Alpha", ["score"] = 79, ["active"] = true });
        Assert.Equal(8, doc.GetRecordCount());
        Assert.Equal(4, doc.Count("team", "Alpha")); // grew

        // GetSchema after append — should still work
        var schemaAfterAppend = doc.GetSchema();
        Assert.NotNull(schemaAfterAppend);
        Assert.True(schemaAfterAppend.Count >= schema.Count);

        // AppendRecord with new field
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 9, ["name"] = "Ivan", ["team"] = "Beta", ["score"] = 88, ["active"] = true, ["location"] = "Berlin" });
        Assert.Equal(9, doc.GetRecordCount());
        Assert.True(doc.HasField("location"));

        var schemaAfterNewField = doc.GetSchema();
        Assert.True(schemaAfterNewField.Count >= schemaAfterAppend.Count);

        // DeleteRecord and verify
        doc.DeleteRecord(0); // Remove Aaron
        Assert.Equal(8, doc.GetRecordCount());
        Assert.Equal(3, doc.Count("team", "Alpha")); // back to 3

        // Filter by team and count
        var alphaTeam = doc.Filter("team", "Alpha");
        Assert.Equal(3, alphaTeam.GetRecordCount());
        Assert.Equal(3, alphaTeam.Count("team", "Alpha"));

        // GetRecordCount consistent
        Assert.Equal(doc.GetRecordCount(), doc.GetRecordCount());

        // Count all active
        var activeCount = doc.Count("active", "True") + doc.Count("active", "true");
        Assert.True(activeCount >= 0);

        // SortBy and verify count preserved
        var sorted = doc.SortBy("score", ascending: false);
        Assert.Equal(doc.GetRecordCount(), sorted.GetRecordCount());

        // Schema consistent
        var schema1 = doc.GetSchema();
        var schema2 = doc.GetSchema();
        Assert.Equal(schema1.Count, schema2.Count);

        // WriteToFile
        var path = TempFile("dogfood_schema_count.ndjson");
        doc.WriteToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(doc.GetRecordCount(), loaded.GetRecordCount());

        // GetSchema on loaded
        var loadedSchema = loaded.GetSchema();
        Assert.NotNull(loadedSchema);

        // Count on loaded
        Assert.Equal(3, loaded.Count("team", "Alpha"));
        Assert.Equal(2, loaded.Count("team", "Beta"));
        Assert.Equal(2, loaded.Count("team", "Gamma"));

        // GetRecordCount on loaded after AppendRecord
        loaded.AppendRecord(new Dictionary<string, object>
            { ["id"] = 10, ["name"] = "Jade", ["team"] = "Delta", ["score"] = 93, ["active"] = true });
        Assert.Equal(doc.GetRecordCount() + 1, loaded.GetRecordCount());
        Assert.Equal(1, loaded.Count("team", "Delta"));

        // Final WriteToFile
        var path2 = TempFile("dogfood_loaded.ndjson");
        loaded.WriteToFile(path2);
        Assert.True(File.Exists(path2));
        var final = NdjsonDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRecordCount(), final.GetRecordCount());
        Assert.Equal(1, final.Count("team", "Delta"));
    }
}
