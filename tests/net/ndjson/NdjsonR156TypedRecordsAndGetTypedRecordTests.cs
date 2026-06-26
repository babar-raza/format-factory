// Tests for NdjsonDocument.TypedRecords, GetTypedRecord, and NdjsonRecord field access.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R156

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R156: Tests for NdjsonDocument.TypedRecords, GetTypedRecord, and NdjsonRecord field access.
/// TypedRecords: returns all records as IReadOnlyList&lt;NdjsonRecord&gt;.
/// GetTypedRecord(index): returns a specific NdjsonRecord by index.
/// NdjsonRecord.TryGetValue: typed field access.
/// Covers: TypedRecords count equals Count; TypedRecords[0] has Keys;
/// GetTypedRecord(0) returns NdjsonRecord; GetTypedRecord name field value;
/// TypedRecords all have non-empty Keys; NdjsonRecord.Keys contains field names;
/// TryGetValue found returns true; TryGetValue not found returns false;
/// TypedRecords on filtered doc; GetTypedRecord out-of-range throws;
/// TypedRecords on single-record doc; NdjsonRecord contains score;
/// dogfood Load->TypedRecords->TryGetValue->Filter->GetFieldValues pipeline.
/// </summary>
public class NdjsonR156TypedRecordsAndGetTypedRecordTests
{
    private const string ThreeRecordNdjson =
        "{\"name\":\"Alice\",\"score\":95,\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Bob\",\"score\":82,\"dept\":\"Finance\"}\n" +
        "{\"name\":\"Carol\",\"score\":88,\"dept\":\"Eng\"}";

    private const string SingleRecordNdjson =
        "{\"x\":42,\"y\":\"hello\"}";

    // -------------------------------------------------------------------------
    // TypedRecords
    // -------------------------------------------------------------------------

    [Fact]
    public void TypedRecords_CountEqualsDocumentCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(doc.Count, doc.TypedRecords.Count);
    }

    [Fact]
    public void TypedRecords_FirstRecord_HasKeys()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var first = doc.TypedRecords[0];
        Assert.NotNull(first.Keys);
        Assert.NotEmpty(first.Keys);
    }

    [Fact]
    public void TypedRecords_AllRecords_HaveNonEmptyKeys()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        foreach (var record in doc.TypedRecords)
        {
            Assert.NotEmpty(record.Keys);
        }
    }

    [Fact]
    public void TypedRecords_FirstRecord_KeysContainName()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var first = doc.TypedRecords[0];
        Assert.Contains("name", first.Keys);
    }

    [Fact]
    public void TypedRecords_SingleRecord_CountIsOne()
    {
        var doc = NdjsonDocument.Load(SingleRecordNdjson);
        Assert.Single(doc.TypedRecords);
    }

    // -------------------------------------------------------------------------
    // GetTypedRecord
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTypedRecord_Index0_ReturnsNdjsonRecord()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var record = doc.GetTypedRecord(0);
        Assert.NotNull(record);
    }

    [Fact]
    public void GetTypedRecord_Index0_NameFieldIsAlice()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var record = doc.GetTypedRecord(0);
        var found = record.TryGetValue("name", out var value);
        Assert.True(found);
        Assert.Equal("Alice", value);
    }

    [Fact]
    public void GetTypedRecord_Index1_NameFieldIsBob()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var record = doc.GetTypedRecord(1);
        var found = record.TryGetValue("name", out var value);
        Assert.True(found);
        Assert.Equal("Bob", value);
    }

    [Fact]
    public void GetTypedRecord_OutOfRange_Throws()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.ThrowsAny<Exception>(() => doc.GetTypedRecord(99));
    }

    // -------------------------------------------------------------------------
    // NdjsonRecord.TryGetValue
    // -------------------------------------------------------------------------

    [Fact]
    public void TryGetValue_ExistingField_ReturnsTrue()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var record = doc.GetTypedRecord(0);
        Assert.True(record.TryGetValue("dept", out _));
    }

    [Fact]
    public void TryGetValue_MissingField_ReturnsFalse()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var record = doc.GetTypedRecord(0);
        Assert.False(record.TryGetValue("nonexistent_field_xyz", out _));
    }

    [Fact]
    public void TryGetValue_ScoreField_ReturnsStringRepresentation()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var record = doc.GetTypedRecord(0);
        var found = record.TryGetValue("score", out var value);
        Assert.True(found);
        Assert.NotNull(value);
        // Score 95 should have some numeric representation
        Assert.Contains("95", value);
    }

    // -------------------------------------------------------------------------
    // TypedRecords on filtered document
    // -------------------------------------------------------------------------

    [Fact]
    public void TypedRecords_OnFilteredDoc_CountMatchesFilter()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var eng = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(eng.Count, eng.TypedRecords.Count);
        Assert.Equal(2, eng.TypedRecords.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->TypedRecords->TryGetValue->Filter->GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_TypedRecordsTryGetValueFilterFieldValues_Pipeline()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(3, doc.Count);

        // Check all TypedRecords have dept field
        foreach (var record in doc.TypedRecords)
        {
            var found = record.TryGetValue("dept", out _);
            Assert.True(found);
        }

        // Get typed record and verify value
        var first = doc.GetTypedRecord(0);
        first.TryGetValue("name", out var firstName);
        Assert.Equal("Alice", firstName);

        // Filter Eng department
        var eng = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);

        // GetFieldValues on filtered
        var names = eng.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);

        // TypedRecords on filtered
        Assert.Equal(2, eng.TypedRecords.Count);
    }
}
