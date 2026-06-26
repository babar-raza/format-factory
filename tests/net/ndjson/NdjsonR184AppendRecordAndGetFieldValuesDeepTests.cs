// Tests for NdjsonDocument.AppendRecord, GetFieldValues, Select/Project deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R184

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R184: Tests for NdjsonDocument.AppendRecord, GetFieldValues, Select/Project deeper.
/// AppendRecord(dict): appends a new record to the document.
/// GetFieldValues(field): returns all values for a given field across all records.
/// Select(fields): returns a new document with only the specified fields per record.
/// Covers: AppendRecord increases Count; AppendRecord data accessible via RecordAt;
/// AppendRecord multiple records; GetFieldValues after AppendRecord includes new values;
/// GetFieldValues count equals Count; Select non-null; Select reduces fields;
/// Select correct Count; Select GetAllKeys contains only selected fields;
/// GetFieldValues after Select correct; Filter then AppendRecord on filtered copy;
/// dogfood LoadContent->AppendRecord->GetFieldValues->Select->Filter->Count->Verify pipeline.
/// </summary>
public class NdjsonR184AppendRecordAndGetFieldValuesDeepTests
{
    private const string BaseNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":92}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":85}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":78}";

    // -------------------------------------------------------------------------
    // AppendRecord
    // -------------------------------------------------------------------------

    [Fact]
    public void AppendRecord_IncreasesCount()
    {
        var doc = NdjsonDocument.LoadContent(BaseNdjson);
        var before = doc.Count;
        doc.AppendRecord(new Dictionary<string, string> { ["name"] = "Dave", ["dept"] = "HR", ["score"] = "91" });
        Assert.Equal(before + 1, doc.Count);
    }

    [Fact]
    public void AppendRecord_DataAccessibleViaRecordAt()
    {
        var doc = NdjsonDocument.LoadContent(BaseNdjson);
        doc.AppendRecord(new Dictionary<string, string> { ["name"] = "Dave", ["dept"] = "HR", ["score"] = "91" });
        var last = doc.RecordAt(doc.Count - 1);
        Assert.True(last.TryGetValue("name", out var name));
        Assert.Equal("Dave", name);
    }

    [Fact]
    public void AppendRecord_MultipleRecords_CountCorrect()
    {
        var doc = NdjsonDocument.LoadContent(BaseNdjson);
        doc.AppendRecord(new Dictionary<string, string> { ["name"] = "Dave", ["dept"] = "HR", ["score"] = "91" });
        doc.AppendRecord(new Dictionary<string, string> { ["name"] = "Eve", ["dept"] = "Finance", ["score"] = "88" });
        Assert.Equal(5, doc.Count);
    }

    [Fact]
    public void AppendRecord_NewDept_GetFieldValuesIncludesNewValue()
    {
        var doc = NdjsonDocument.LoadContent(BaseNdjson);
        doc.AppendRecord(new Dictionary<string, string> { ["name"] = "Dave", ["dept"] = "HR", ["score"] = "91" });
        var depts = doc.GetFieldValues("dept");
        Assert.Contains("HR", depts);
    }

    [Fact]
    public void AppendRecord_PreservesExistingRecords()
    {
        var doc = NdjsonDocument.LoadContent(BaseNdjson);
        doc.AppendRecord(new Dictionary<string, string> { ["name"] = "Dave", ["dept"] = "HR", ["score"] = "91" });
        var alice = doc.RecordAt(0);
        Assert.True(alice.TryGetValue("name", out var name));
        Assert.Equal("Alice", name);
    }

    // -------------------------------------------------------------------------
    // GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValues_CountEqualsDocumentCount()
    {
        var doc = NdjsonDocument.LoadContent(BaseNdjson);
        var names = doc.GetFieldValues("name");
        Assert.Equal(doc.Count, names.Count);
    }

    [Fact]
    public void GetFieldValues_AllNamesPresent()
    {
        var doc = NdjsonDocument.LoadContent(BaseNdjson);
        var names = doc.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void GetFieldValues_AfterAppendRecord_IncludesNewValue()
    {
        var doc = NdjsonDocument.LoadContent(BaseNdjson);
        doc.AppendRecord(new Dictionary<string, string> { ["name"] = "Zara", ["dept"] = "Legal", ["score"] = "77" });
        var names = doc.GetFieldValues("name");
        Assert.Contains("Zara", names);
        Assert.Equal(4, names.Count);
    }

    [Fact]
    public void GetFieldValues_MissingField_EmptyOrNull()
    {
        var doc = NdjsonDocument.LoadContent(BaseNdjson);
        var result = doc.GetFieldValues("nonexistent");
        Assert.True(result == null || result.Count == 0);
    }

    // -------------------------------------------------------------------------
    // Select
    // -------------------------------------------------------------------------

    [Fact]
    public void Select_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(BaseNdjson);
        Assert.NotNull(doc.Select(new[] { "name", "dept" }));
    }

    [Fact]
    public void Select_PreservesCount()
    {
        var doc = NdjsonDocument.LoadContent(BaseNdjson);
        var projected = doc.Select(new[] { "name" });
        Assert.Equal(doc.Count, projected.Count);
    }

    [Fact]
    public void Select_ReducedFields_GetAllKeysHasOnlySelected()
    {
        var doc = NdjsonDocument.LoadContent(BaseNdjson);
        var projected = doc.Select(new[] { "name", "dept" });
        var keys = projected.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
        Assert.DoesNotContain("score", keys);
    }

    [Fact]
    public void Select_SingleField_AccessibleViaGetFieldValues()
    {
        var doc = NdjsonDocument.LoadContent(BaseNdjson);
        var projected = doc.Select(new[] { "name" });
        var names = projected.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_AppendRecord_GetFieldValues_Select_Filter_Count_Verify_Pipeline()
    {
        // Load
        var doc = NdjsonDocument.LoadContent(BaseNdjson);
        Assert.Equal(3, doc.Count);

        // AppendRecord
        doc.AppendRecord(new Dictionary<string, string> { ["name"] = "Dave", ["dept"] = "HR", ["score"] = "91" });
        doc.AppendRecord(new Dictionary<string, string> { ["name"] = "Eve", ["dept"] = "Finance", ["score"] = "88" });
        Assert.Equal(5, doc.Count);

        // GetFieldValues
        var names = doc.GetFieldValues("name");
        Assert.Equal(5, names.Count);
        Assert.Contains("Dave", names);
        Assert.Contains("Eve", names);

        var depts = doc.GetFieldValues("dept");
        Assert.Contains("HR", depts);
        Assert.Contains("Finance", depts);
        Assert.Contains("Eng", depts);

        // Select name and dept only
        var projected = doc.Select(new[] { "name", "dept" });
        Assert.Equal(5, projected.Count);
        var keys = projected.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
        Assert.DoesNotContain("score", keys);

        // Filter on projected
        var engProjected = projected.Filter(r => r.TryGetValue("dept", out var d) && d == "Eng");
        Assert.Equal(2, engProjected.Count);

        // Filter original and GetFieldValues
        var eng = doc.Filter(r => r.TryGetValue("dept", out var d) && d == "Eng");
        Assert.Equal(2, eng.Count);
        var engNames = eng.GetFieldValues("name");
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);
        Assert.DoesNotContain("Dave", engNames);
    }
}
