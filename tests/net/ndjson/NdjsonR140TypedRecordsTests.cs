// Tests for NdjsonDocument.TypedRecords and GetTypedRecord.
// Sprint: ff-sprint-oracle-all-verified-20260626
// Ledger: PC-NDJSON-R140

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R140: Tests for NdjsonDocument.TypedRecords and GetTypedRecord.
/// TypedRecords returns all records wrapped in NdjsonRecord.
/// GetTypedRecord(index) returns a single NdjsonRecord by index.
/// NdjsonRecord exposes Fields, Keys, TryGetValue, and RawElement.
/// Covers: TypedRecords empty doc returns empty list; TypedRecords count matches Records.Count;
/// TypedRecords first item is NdjsonRecord; GetTypedRecord(0) returns first record;
/// GetTypedRecord out-of-range throws; NdjsonRecord.Keys contains expected key;
/// NdjsonRecord.TryGetValue returns true for existing key; false for missing;
/// NdjsonRecord.Fields.Count matches key count; RawElement.ValueKind is Object;
/// dogfood Load->TypedRecords->TryGetValue pipeline.
/// </summary>
public class NdjsonR140TypedRecordsTests
{
    private const string ThreeRecords =
        "{\"name\":\"Alice\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"score\":88}";

    private const string MixedContent =
        "{\"id\":1,\"tag\":\"alpha\"}\n" +
        "{\"id\":2,\"tag\":\"beta\",\"extra\":true}";

    // -------------------------------------------------------------------------
    // TypedRecords basic
    // -------------------------------------------------------------------------

    [Fact]
    public void TypedRecords_EmptyDocument_ReturnsEmptyList()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        Assert.Empty(doc.TypedRecords);
    }

    [Fact]
    public void TypedRecords_CountMatchesRecordsCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        Assert.Equal(doc.Records.Count, doc.TypedRecords.Count);
    }

    [Fact]
    public void TypedRecords_FirstItemIsNdjsonRecord()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var typed = doc.TypedRecords;
        Assert.NotNull(typed[0]);
        Assert.IsType<NdjsonRecord>(typed[0]);
    }

    [Fact]
    public void TypedRecords_AllItemsAreNdjsonRecord()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        Assert.All(doc.TypedRecords, r => Assert.IsType<NdjsonRecord>(r));
    }

    // -------------------------------------------------------------------------
    // GetTypedRecord
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTypedRecord_Index0_ReturnsFirstRecord()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var rec = doc.GetTypedRecord(0);
        Assert.NotNull(rec);
        Assert.True(rec.TryGetValue("name", out var nameEl));
        Assert.Equal("Alice", nameEl.GetString());
    }

    [Fact]
    public void GetTypedRecord_OutOfRange_Throws()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        Assert.ThrowsAny<Exception>(() => doc.GetTypedRecord(99));
    }

    // -------------------------------------------------------------------------
    // NdjsonRecord.Keys
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonRecord_Keys_ContainsExpectedKey()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var rec = doc.GetTypedRecord(0);
        Assert.Contains("name", rec.Keys);
        Assert.Contains("score", rec.Keys);
    }

    [Fact]
    public void NdjsonRecord_Keys_CountMatchesFieldCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var rec = doc.GetTypedRecord(0);
        Assert.Equal(2, rec.Keys.Count); // name, score
    }

    // -------------------------------------------------------------------------
    // NdjsonRecord.TryGetValue
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonRecord_TryGetValue_ExistingKey_ReturnsTrue()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var rec = doc.GetTypedRecord(1); // Bob
        Assert.True(rec.TryGetValue("name", out var val));
        Assert.Equal("Bob", val.GetString());
    }

    [Fact]
    public void NdjsonRecord_TryGetValue_MissingKey_ReturnsFalse()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var rec = doc.GetTypedRecord(0);
        Assert.False(rec.TryGetValue("nonexistent", out _));
    }

    // -------------------------------------------------------------------------
    // NdjsonRecord.Fields
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonRecord_Fields_CountMatchesKeyCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var rec = doc.GetTypedRecord(0);
        Assert.Equal(rec.Keys.Count, rec.Fields.Count);
    }

    [Fact]
    public void NdjsonRecord_Fields_ContainsExpectedEntry()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var rec = doc.GetTypedRecord(2); // Carol
        Assert.True(rec.Fields.ContainsKey("name"));
        Assert.Equal("Carol", rec.Fields["name"].GetString());
    }

    // -------------------------------------------------------------------------
    // NdjsonRecord.RawElement
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonRecord_RawElement_ValueKindIsObject()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var rec = doc.GetTypedRecord(0);
        Assert.Equal(JsonValueKind.Object, rec.RawElement.ValueKind);
    }

    // -------------------------------------------------------------------------
    // Mixed schema scenarios
    // -------------------------------------------------------------------------

    [Fact]
    public void TypedRecords_MixedSchema_SecondRecordHasExtraKey()
    {
        var doc = NdjsonDocument.Load(MixedContent);
        Assert.Equal(2, doc.TypedRecords.Count);
        var rec2 = doc.GetTypedRecord(1);
        Assert.Contains("extra", rec2.Keys);
    }

    // -------------------------------------------------------------------------
    // Dogfood: full pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadTypedRecordsTryGetValue_Pipeline()
    {
        var content =
            "{\"product\":\"Widget\",\"qty\":10,\"price\":2.99}\n" +
            "{\"product\":\"Gadget\",\"qty\":5,\"price\":49.99}\n" +
            "{\"product\":\"Doohickey\",\"qty\":100,\"price\":0.50}";

        var doc = NdjsonDocument.Load(content);
        var typed = doc.TypedRecords;

        Assert.Equal(3, typed.Count);

        // Verify each record has product key
        foreach (var rec in typed)
        {
            Assert.True(rec.TryGetValue("product", out var prod));
            Assert.Equal(JsonValueKind.String, prod.ValueKind);
        }

        // Spot-check second record
        var gadget = typed[1];
        Assert.True(gadget.TryGetValue("qty", out var qty));
        Assert.Equal(5, qty.GetInt32());
    }
}
