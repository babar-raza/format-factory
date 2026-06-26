// Tests for NdjsonDocument.Select, GetTypedRecord, typed record access deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R187

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R187: Tests for NdjsonDocument.Select, GetTypedRecord, typed record access deeper coverage.
/// Select(fields): returns new document with records containing only the selected fields.
/// GetTypedRecord&lt;T&gt;(index): returns record deserialized to typed object.
/// Covers: Select non-null; Select preserves record count; Select reduces keys;
/// Select with single field; Select with all fields; Select after Filter;
/// Select then GetAllKeys has only selected fields;
/// GetTypedRecord non-null; GetTypedRecord count gives correct number;
/// GetTypedRecord fields accessible; GetTypedRecord after AppendRecord includes new;
/// RecordAt non-null; RecordAt correct index; RecordAt GetField returns value;
/// dogfood LoadContent->Select->GetTypedRecord->RecordAt->Verify pipeline.
/// </summary>
public class NdjsonR187SelectAndTypedRecordsDeepTests
{
    private const string Content =
        "{\"Name\":\"Alice\",\"Dept\":\"Eng\",\"Score\":92,\"Active\":true}\n" +
        "{\"Name\":\"Bob\",\"Dept\":\"Finance\",\"Score\":85,\"Active\":false}\n" +
        "{\"Name\":\"Carol\",\"Dept\":\"Eng\",\"Score\":78,\"Active\":true}\n" +
        "{\"Name\":\"Dave\",\"Dept\":\"HR\",\"Score\":91,\"Active\":false}\n" +
        "{\"Name\":\"Eve\",\"Dept\":\"Finance\",\"Score\":88,\"Active\":true}";

    // -------------------------------------------------------------------------
    // Select
    // -------------------------------------------------------------------------

    [Fact]
    public void Select_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        Assert.NotNull(doc.Select(new[] { "Name", "Score" }));
    }

    [Fact]
    public void Select_PreservesRecordCount()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var selected = doc.Select(new[] { "Name", "Score" });
        Assert.Equal(doc.Count, selected.Count);
    }

    [Fact]
    public void Select_ReducesKeys_ToSelectedFields()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var selected = doc.Select(new[] { "Name", "Score" });
        var keys = selected.GetAllKeys();
        Assert.Equal(2, keys.Count);
        Assert.Contains("Name", keys);
        Assert.Contains("Score", keys);
        Assert.DoesNotContain("Dept", keys);
        Assert.DoesNotContain("Active", keys);
    }

    [Fact]
    public void Select_SingleField_AllRecordsHaveThatField()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var selected = doc.Select(new[] { "Name" });
        Assert.Equal(5, selected.Count);
        var keys = selected.GetAllKeys();
        Assert.Equal(1, keys.Count);
        Assert.Contains("Name", keys);
    }

    [Fact]
    public void Select_AllFields_SameAsOriginal()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var selected = doc.Select(new[] { "Name", "Dept", "Score", "Active" });
        Assert.Equal(doc.Count, selected.Count);
        var keys = selected.GetAllKeys();
        Assert.Equal(4, keys.Count);
    }

    [Fact]
    public void Select_AfterFilter_ReducedRecords()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var engOnly = doc.Filter(r => r.GetField("Dept")?.ToString() == "Eng");
        var selected = engOnly.Select(new[] { "Name" });
        Assert.Equal(engOnly.Count, selected.Count);
        Assert.Equal(2, selected.Count);
    }

    [Fact]
    public void Select_GetAllKeys_HasOnlySelectedFields()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var selected = doc.Select(new[] { "Name", "Dept" });
        var allKeys = selected.GetAllKeys();
        Assert.Equal(2, allKeys.Count);
        Assert.DoesNotContain("Score", allKeys);
    }

    // -------------------------------------------------------------------------
    // RecordAt
    // -------------------------------------------------------------------------

    [Fact]
    public void RecordAt_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        Assert.NotNull(doc.RecordAt(0));
    }

    [Fact]
    public void RecordAt_CorrectFirstRecord()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var record = doc.RecordAt(0);
        Assert.Equal("Alice", record.GetField("Name")?.ToString());
    }

    [Fact]
    public void RecordAt_CorrectLastRecord()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var record = doc.RecordAt(4);
        Assert.Equal("Eve", record.GetField("Name")?.ToString());
    }

    [Fact]
    public void RecordAt_MiddleRecord_Correct()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var record = doc.RecordAt(2);
        Assert.Equal("Carol", record.GetField("Name")?.ToString());
    }

    [Fact]
    public void RecordAt_GetField_ReturnsValue()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var record = doc.RecordAt(0);
        Assert.NotNull(record.GetField("Dept"));
        Assert.Equal("Eng", record.GetField("Dept")?.ToString());
    }

    [Fact]
    public void RecordAt_AllRecords_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        for (var i = 0; i < doc.Count; i++)
            Assert.NotNull(doc.RecordAt(i));
    }

    // -------------------------------------------------------------------------
    // GetTypedRecord
    // -------------------------------------------------------------------------

    private record EmployeeRecord(string Name, string Dept, int Score);

    [Fact]
    public void GetTypedRecord_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var typed = doc.GetTypedRecord<Dictionary<string, object?>>(0);
        Assert.NotNull(typed);
    }

    [Fact]
    public void GetTypedRecord_AsDict_ContainsExpectedKey()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var typed = doc.GetTypedRecord<Dictionary<string, object?>>(0);
        Assert.True(typed.ContainsKey("Name"));
    }

    [Fact]
    public void GetTypedRecord_AllIndices_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        for (var i = 0; i < doc.Count; i++)
            Assert.NotNull(doc.GetTypedRecord<Dictionary<string, object?>>(i));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_Select_GetTypedRecord_RecordAt_Verify_Pipeline()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        Assert.Equal(5, doc.Count);

        // RecordAt all records
        for (var i = 0; i < doc.Count; i++)
        {
            var rec = doc.RecordAt(i);
            Assert.NotNull(rec);
            Assert.NotNull(rec.GetField("Name"));
        }

        // Select subset
        var nameOnly = doc.Select(new[] { "Name" });
        Assert.Equal(5, nameOnly.Count);
        Assert.Equal(1, nameOnly.GetAllKeys().Count);

        // After select, RecordAt still works
        var firstSelected = nameOnly.RecordAt(0);
        Assert.NotNull(firstSelected);
        Assert.Equal("Alice", firstSelected.GetField("Name")?.ToString());

        // GetTypedRecord as dict
        var typed = doc.GetTypedRecord<Dictionary<string, object?>>(1);
        Assert.NotNull(typed);
        Assert.True(typed.ContainsKey("Name"));

        // Filter then Select
        var activeOnly = doc.Filter(r =>
        {
            var active = r.GetField("Active");
            if (active == null) return false;
            if (active is bool b) return b;
            return active.ToString()?.ToLower() == "true";
        });
        Assert.Equal(3, activeOnly.Count); // Alice, Carol, Eve

        var activeNames = activeOnly.Select(new[] { "Name" });
        Assert.Equal(3, activeNames.Count);
        var keys = activeNames.GetAllKeys();
        Assert.Equal(1, keys.Count);
        Assert.Contains("Name", keys);

        // AppendRecord then GetTypedRecord
        var newRecord = new Dictionary<string, object?> { ["Name"] = "Frank", ["Dept"] = "Legal", ["Score"] = 95, ["Active"] = true };
        var extended = doc.AppendRecord(newRecord);
        Assert.Equal(6, extended.Count);
        var lastTyped = extended.GetTypedRecord<Dictionary<string, object?>>(5);
        Assert.NotNull(lastTyped);
    }
}
