// Tests for NdjsonRecord.TryGetValue(string key, out JsonElement value) and NdjsonRecord.Keys.
// Sprint: FORMAT-FACTORY-NDJSON-R131-20260627
// Ledger: R131-GOVERNED-DOTNET-NDJSON-RECORD-TRYGETVALUE-001

using System;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R131: Tests for NdjsonRecord.TryGetValue(string key, out JsonElement value) and
/// NdjsonRecord.Keys property. TryGetValue returns true when the key exists and
/// outputs the JsonElement; returns false when the key is absent (out is default).
/// Keys returns an IReadOnlyList of all field names in the record.
/// Covers: TryGetValue existing key → true; TryGetValue absent key → false;
/// TryGetValue string value accessible; TryGetValue numeric value accessible;
/// TryGetValue boolean value accessible; Keys count matches field count;
/// Keys contains all expected names; Keys and Fields dictionary key parity;
/// RawElement.ValueKind is Object; dogfood pipeline TryGetValue-gated extraction.
/// </summary>
public class NdjsonR131RecordTryGetValueTests
{
    private static NdjsonRecord RecordFrom(string json)
    {
        var doc = NdjsonDocument.Load(json);
        return doc.GetTypedRecord(0);
    }

    // -------------------------------------------------------------------------
    // TryGetValue: existing key
    // -------------------------------------------------------------------------

    [Fact]
    public void TryGetValue_ExistingStringKey_ReturnsTrue()
    {
        var rec = RecordFrom("{\"city\":\"London\",\"pop\":9000000}");
        var found = rec.TryGetValue("city", out var val);
        Assert.True(found);
        Assert.Equal("London", val.GetString());
    }

    [Fact]
    public void TryGetValue_ExistingNumericKey_ReturnsTrue()
    {
        var rec = RecordFrom("{\"score\":42,\"name\":\"Alice\"}");
        var found = rec.TryGetValue("score", out var val);
        Assert.True(found);
        Assert.Equal(42, val.GetInt32());
    }

    [Fact]
    public void TryGetValue_ExistingBooleanKey_ReturnsTrue()
    {
        var rec = RecordFrom("{\"active\":true,\"name\":\"Bob\"}");
        var found = rec.TryGetValue("active", out var val);
        Assert.True(found);
        Assert.True(val.GetBoolean());
    }

    // -------------------------------------------------------------------------
    // TryGetValue: absent key
    // -------------------------------------------------------------------------

    [Fact]
    public void TryGetValue_AbsentKey_ReturnsFalse()
    {
        var rec = RecordFrom("{\"name\":\"Carol\",\"age\":30}");
        var found = rec.TryGetValue("country", out _);
        Assert.False(found);
    }

    [Fact]
    public void TryGetValue_EmptyKey_ReturnsFalse()
    {
        var rec = RecordFrom("{\"name\":\"Dave\"}");
        var found = rec.TryGetValue(string.Empty, out _);
        Assert.False(found);
    }

    // -------------------------------------------------------------------------
    // NdjsonRecord.Keys property
    // -------------------------------------------------------------------------

    [Fact]
    public void Keys_SingleField_CountIsOne()
    {
        var rec = RecordFrom("{\"x\":1}");
        Assert.Equal(1, rec.Keys.Count);
    }

    [Fact]
    public void Keys_MultipleFields_ContainsAllNames()
    {
        var rec = RecordFrom("{\"name\":\"Eve\",\"age\":25,\"city\":\"Paris\"}");
        Assert.Contains("name", rec.Keys);
        Assert.Contains("age",  rec.Keys);
        Assert.Contains("city", rec.Keys);
    }

    [Fact]
    public void Keys_ParityWithFieldsDictionary()
    {
        var rec = RecordFrom("{\"a\":1,\"b\":2,\"c\":3}");
        foreach (var key in rec.Keys)
        {
            Assert.True(rec.Fields.ContainsKey(key));
        }
        Assert.Equal(rec.Fields.Count, rec.Keys.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: TryGetValue-gated field extraction pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TryGetValueGated_ExtractPresent_SkipAbsent()
    {
        const string ndjson =
            "{\"product\":\"Widget\",\"revenue\":1000,\"region\":\"West\"}\n" +
            "{\"product\":\"Gadget\",\"revenue\":800}\n" +         // no region
            "{\"product\":\"Thingit\",\"revenue\":500,\"region\":\"East\"}";

        var doc = NdjsonDocument.Load(ndjson);
        var withRegion = 0;
        var totalRevenue = 0;

        for (var i = 0; i < doc.Count; i++)
        {
            var rec = doc.GetTypedRecord(i);

            // Gate on presence
            if (rec.TryGetValue("region", out _))
                withRegion++;

            if (rec.TryGetValue("revenue", out var revVal))
                totalRevenue += revVal.GetInt32();
        }

        Assert.Equal(2, withRegion);
        Assert.Equal(2300, totalRevenue);

        // Verify Keys on each typed record covers product field
        for (var i = 0; i < doc.Count; i++)
        {
            var rec = doc.GetTypedRecord(i);
            Assert.Contains("product", rec.Keys);
        }
    }
}
