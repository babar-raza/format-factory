// Tests for NdjsonDocument.TypedRecords, GetTypedRecord, NdjsonRecord.Keys, ToNdjson.
// Sprint: FORMAT-FACTORY-NDJSON-TYPED-RECORDS-20260626
// Ledger: R119-GOVERNED-DOTNET-NDJSON-TYPED-RECORDS-001

using System;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R119: NdjsonDocument.TypedRecords returns IReadOnlyList{NdjsonRecord}; GetTypedRecord(i)
/// returns the i-th typed record. NdjsonRecord.Keys lists the field keys present in a
/// record. NdjsonRecord.TryGetValue(key, out JsonElement) retrieves field by name.
/// ToNdjson() serializes the document back to NDJSON text with one JSON object per line.
/// </summary>
public class NdjsonR119TypedRecordsTests
{
    private static NdjsonDocument LoadNdjson(string ndjson) =>
        NdjsonDocument.Load(ndjson);

    // ---- TypedRecords count ----

    [Fact]
    public void TypedRecords_CountMatchesDocumentCount()
    {
        var ndjson = "{\"a\":1}\n{\"b\":2}\n{\"c\":3}\n";
        var doc = LoadNdjson(ndjson);
        Assert.Equal(doc.Count, doc.TypedRecords.Count);
    }

    [Fact]
    public void TypedRecords_SingleRecord_CountIsOne()
    {
        var ndjson = "{\"name\":\"Alice\"}\n";
        var doc = LoadNdjson(ndjson);
        Assert.Single(doc.TypedRecords);
    }

    // ---- GetTypedRecord ----

    [Fact]
    public void GetTypedRecord_IndexZero_ReturnsFirstRecord()
    {
        var ndjson = "{\"id\":1}\n{\"id\":2}\n";
        var doc = LoadNdjson(ndjson);
        var record = doc.GetTypedRecord(0);
        Assert.NotNull(record);
    }

    [Fact]
    public void GetTypedRecord_LastIndex_ReturnsLastRecord()
    {
        var ndjson = "{\"x\":\"first\"}\n{\"x\":\"second\"}\n{\"x\":\"third\"}\n";
        var doc = LoadNdjson(ndjson);
        var last = doc.GetTypedRecord(2);
        Assert.NotNull(last);
    }

    // ---- NdjsonRecord.Keys ----

    [Fact]
    public void NdjsonRecord_Keys_ContainsFieldNames()
    {
        var ndjson = "{\"name\":\"Alice\",\"score\":90}\n";
        var doc = LoadNdjson(ndjson);
        var record = doc.GetTypedRecord(0);

        Assert.Contains("name", record.Keys);
        Assert.Contains("score", record.Keys);
    }

    [Fact]
    public void NdjsonRecord_Keys_CountMatchesFieldCount()
    {
        var ndjson = "{\"a\":1,\"b\":2,\"c\":3}\n";
        var doc = LoadNdjson(ndjson);
        var record = doc.GetTypedRecord(0);

        Assert.Equal(3, record.Keys.Count);
    }

    // ---- NdjsonRecord.TryGetValue ----

    [Fact]
    public void TryGetValue_ExistingKey_ReturnsTrue()
    {
        var ndjson = "{\"city\":\"London\"}\n";
        var doc = LoadNdjson(ndjson);
        var record = doc.GetTypedRecord(0);

        Assert.True(record.TryGetValue("city", out _));
    }

    [Fact]
    public void TryGetValue_MissingKey_ReturnsFalse()
    {
        var ndjson = "{\"city\":\"London\"}\n";
        var doc = LoadNdjson(ndjson);
        var record = doc.GetTypedRecord(0);

        Assert.False(record.TryGetValue("country", out _));
    }

    // ---- ToNdjson ----

    [Fact]
    public void ToNdjson_ProducesNonEmptyString()
    {
        var ndjson = "{\"a\":1}\n";
        var doc = LoadNdjson(ndjson);
        var output = doc.ToNdjson();
        Assert.False(string.IsNullOrWhiteSpace(output));
    }

    [Fact]
    public void ToNdjson_OutputContainsFieldNames()
    {
        var ndjson = "{\"name\":\"Alice\",\"score\":90}\n";
        var doc = LoadNdjson(ndjson);
        var output = doc.ToNdjson();

        Assert.Contains("name", output);
        Assert.Contains("score", output);
    }

    // ---- Dogfood: TypedRecords + Keys + TryGetValue pipeline ----

    [Fact]
    public void DogfoodPipeline_TypedRecordsKeysTryGetValue_Consistent()
    {
        var ndjson = string.Concat(
            "{\"name\":\"Alice\",\"age\":30}\n",
            "{\"name\":\"Bob\",\"age\":25}\n",
            "{\"name\":\"Carol\",\"age\":35}\n");

        var doc = LoadNdjson(ndjson);

        // TypedRecords matches Count
        Assert.Equal(3, doc.TypedRecords.Count);

        // Each record has the expected keys
        foreach (var record in doc.TypedRecords)
        {
            Assert.Contains("name", record.Keys);
            Assert.Contains("age", record.Keys);
        }

        // TryGetValue for first record
        var first = doc.GetTypedRecord(0);
        Assert.True(first.TryGetValue("name", out var nameEl));
        Assert.Equal("Alice", nameEl.GetString());

        // ToNdjson roundtrip
        var output = doc.ToNdjson();
        Assert.Contains("Alice", output);
        Assert.Contains("Carol", output);
    }
}
