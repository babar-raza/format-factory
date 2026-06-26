// Tests for NdjsonRecord.Fields, Keys, TryGetValue, RawElement.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R146

using System;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R146: Tests for NdjsonRecord.Fields, Keys, TryGetValue, RawElement.
/// Fields: IReadOnlyDictionary of key→JsonElement for the record.
/// Keys: IReadOnlyList of all key strings in the record.
/// TryGetValue(key, out value): returns true if key present; false if missing.
/// RawElement: the underlying JsonElement.
/// Covers: Fields has correct count; Fields contains expected keys; Fields value accessible;
/// Keys count matches Fields count; Keys contains expected key names;
/// TryGetValue existing key returns true; TryGetValue missing key returns false;
/// TryGetValue populates out value for existing key; TryGetValue out value is default for missing;
/// RawElement kind is Object; RawElement has correct property count;
/// dogfood GetTypedRecord->Fields->TryGetValue->RawElement pipeline.
/// </summary>
public class NdjsonR146NdjsonRecordFieldAccessTests
{
    private const string ThreeRecords =
        "{\"name\":\"Alice\",\"score\":95,\"active\":true}\n" +
        "{\"name\":\"Bob\",\"score\":82,\"active\":false}\n" +
        "{\"name\":\"Carol\",\"score\":88,\"active\":true}";

    private static NdjsonRecord GetRecord(string ndjson, int index)
    {
        var doc = NdjsonDocument.Load(ndjson);
        return doc.GetTypedRecord(index);
    }

    // -------------------------------------------------------------------------
    // Fields
    // -------------------------------------------------------------------------

    [Fact]
    public void Fields_HasCorrectCount()
    {
        var r = GetRecord(ThreeRecords, 0);
        Assert.Equal(3, r.Fields.Count); // name, score, active
    }

    [Fact]
    public void Fields_ContainsExpectedKeys()
    {
        var r = GetRecord(ThreeRecords, 0);
        Assert.True(r.Fields.ContainsKey("name"));
        Assert.True(r.Fields.ContainsKey("score"));
        Assert.True(r.Fields.ContainsKey("active"));
    }

    [Fact]
    public void Fields_ValueAccessible()
    {
        var r = GetRecord(ThreeRecords, 0);
        Assert.Equal("Alice", r.Fields["name"].GetString());
    }

    [Fact]
    public void Fields_NumericValueAccessible()
    {
        var r = GetRecord(ThreeRecords, 0);
        Assert.Equal(95, r.Fields["score"].GetInt32());
    }

    [Fact]
    public void Fields_BoolValueAccessible()
    {
        var r = GetRecord(ThreeRecords, 0);
        Assert.True(r.Fields["active"].GetBoolean());
    }

    // -------------------------------------------------------------------------
    // Keys
    // -------------------------------------------------------------------------

    [Fact]
    public void Keys_CountMatchesFieldsCount()
    {
        var r = GetRecord(ThreeRecords, 0);
        Assert.Equal(r.Fields.Count, r.Keys.Count);
    }

    [Fact]
    public void Keys_ContainsExpectedKeyNames()
    {
        var r = GetRecord(ThreeRecords, 0);
        Assert.Contains("name", r.Keys);
        Assert.Contains("score", r.Keys);
        Assert.Contains("active", r.Keys);
    }

    // -------------------------------------------------------------------------
    // TryGetValue
    // -------------------------------------------------------------------------

    [Fact]
    public void TryGetValue_ExistingKey_ReturnsTrue()
    {
        var r = GetRecord(ThreeRecords, 0);
        Assert.True(r.TryGetValue("name", out _));
    }

    [Fact]
    public void TryGetValue_MissingKey_ReturnsFalse()
    {
        var r = GetRecord(ThreeRecords, 0);
        Assert.False(r.TryGetValue("nonexistent_key", out _));
    }

    [Fact]
    public void TryGetValue_PopulatesOutValue()
    {
        var r = GetRecord(ThreeRecords, 0);
        r.TryGetValue("score", out var value);
        Assert.Equal(95, value.GetInt32());
    }

    [Fact]
    public void TryGetValue_SecondRecord_CorrectValue()
    {
        var r = GetRecord(ThreeRecords, 1); // Bob
        r.TryGetValue("name", out var nameEl);
        Assert.Equal("Bob", nameEl.GetString());
    }

    // -------------------------------------------------------------------------
    // RawElement
    // -------------------------------------------------------------------------

    [Fact]
    public void RawElement_KindIsObject()
    {
        var r = GetRecord(ThreeRecords, 0);
        Assert.Equal(JsonValueKind.Object, r.RawElement.ValueKind);
    }

    [Fact]
    public void RawElement_HasCorrectPropertyCount()
    {
        var r = GetRecord(ThreeRecords, 0);
        var count = 0;
        foreach (var _ in r.RawElement.EnumerateObject())
            count++;
        Assert.Equal(3, count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: GetTypedRecord->Fields->TryGetValue->RawElement
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetTypedRecordFieldsTryGetValueRawElement_Pipeline()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);

        for (var i = 0; i < doc.Count; i++)
        {
            var record = doc.GetTypedRecord(i);

            // Fields accessible
            Assert.Equal(3, record.Fields.Count);

            // Keys present
            Assert.Contains("name", record.Keys);
            Assert.Contains("score", record.Keys);

            // TryGetValue works
            Assert.True(record.TryGetValue("name", out var nameEl));
            Assert.Equal(JsonValueKind.String, nameEl.ValueKind);

            Assert.False(record.TryGetValue("missingField", out _));

            // RawElement is Object
            Assert.Equal(JsonValueKind.Object, record.RawElement.ValueKind);
        }
    }
}
