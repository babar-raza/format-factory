// Tests for NdjsonRecord.Fields dictionary and RawElement JSON access.
// Sprint: FORMAT-FACTORY-NDJSON-RECORD-FIELDS-R123-20260627
// Ledger: R123-GOVERNED-DOTNET-NDJSON-RECORD-FIELDS-001

using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R123: NdjsonRecord.Fields returns an IReadOnlyDictionary&lt;string, JsonElement&gt; — all keys
/// present, values accessible by key, numeric and string types preserved. RawElement is
/// the underlying JsonElement whose ValueKind is Object. Fields dictionary contains
/// the same keys as NdjsonRecord.Keys. Accessing a missing key via Fields throws KeyNotFoundException.
/// </summary>
public class NdjsonR123RecordFieldsTests
{
    private static NdjsonRecord FirstRecord(string ndjson)
    {
        var doc = NdjsonDocument.Load(ndjson);
        return doc.GetTypedRecord(0);
    }

    // ---- Fields dictionary: basic access ----

    [Fact]
    public void Fields_StringField_AccessibleByKey()
    {
        var rec = FirstRecord("{\"city\":\"London\"}");
        Assert.True(rec.Fields.ContainsKey("city"));
    }

    [Fact]
    public void Fields_StringField_ValueIsString()
    {
        var rec = FirstRecord("{\"city\":\"London\"}");
        var el  = rec.Fields["city"];
        Assert.Equal(JsonValueKind.String, el.ValueKind);
    }

    [Fact]
    public void Fields_StringField_ValueCorrect()
    {
        var rec = FirstRecord("{\"city\":\"London\"}");
        Assert.Equal("London", rec.Fields["city"].GetString());
    }

    [Fact]
    public void Fields_NumericField_AccessibleByKey()
    {
        var rec = FirstRecord("{\"score\":42}");
        Assert.True(rec.Fields.ContainsKey("score"));
    }

    [Fact]
    public void Fields_NumericField_ValueIsNumber()
    {
        var rec = FirstRecord("{\"score\":42}");
        var el  = rec.Fields["score"];
        Assert.Equal(JsonValueKind.Number, el.ValueKind);
    }

    [Fact]
    public void Fields_NumericField_ValueCorrect()
    {
        var rec = FirstRecord("{\"score\":42}");
        Assert.Equal(42, rec.Fields["score"].GetInt32());
    }

    // ---- Fields: count and key alignment ----

    [Fact]
    public void Fields_Count_MatchesKeysCount()
    {
        var rec = FirstRecord("{\"a\":1,\"b\":2,\"c\":3}");
        Assert.Equal(rec.Keys.Count, rec.Fields.Count);
    }

    [Fact]
    public void Fields_ContainsAllKeysFromKeys()
    {
        var rec = FirstRecord("{\"name\":\"Alice\",\"age\":30,\"active\":true}");
        foreach (var key in rec.Keys)
            Assert.True(rec.Fields.ContainsKey(key));
    }

    // ---- RawElement ----

    [Fact]
    public void RawElement_ValueKind_IsObject()
    {
        var rec = FirstRecord("{\"x\":1}");
        Assert.Equal(JsonValueKind.Object, rec.RawElement.ValueKind);
    }

    [Fact]
    public void RawElement_ContainsExpectedField()
    {
        var rec = FirstRecord("{\"product\":\"Widget\"}");
        Assert.True(rec.RawElement.TryGetProperty("product", out var el));
        Assert.Equal("Widget", el.GetString());
    }

    // ---- Dogfood: multi-field analytics record ----

    [Fact]
    public void DogfoodPipeline_AnalyticsRecord_AllFieldsAccessible()
    {
        var ndjson =
            "{\"id\":\"T-001\",\"format\":\"FODS\",\"tests\":120,\"pass_rate\":0.98,\"enabled\":true}\n" +
            "{\"id\":\"T-002\",\"format\":\"ZST\",\"tests\":85,\"pass_rate\":0.94,\"enabled\":false}\n";

        var doc = NdjsonDocument.Load(ndjson);
        var r1  = doc.GetTypedRecord(0);
        var r2  = doc.GetTypedRecord(1);

        // Record 1 fields
        Assert.Equal("T-001", r1.Fields["id"].GetString());
        Assert.Equal("FODS",  r1.Fields["format"].GetString());
        Assert.Equal(120,     r1.Fields["tests"].GetInt32());
        Assert.Equal(JsonValueKind.True, r1.Fields["enabled"].ValueKind);

        // Record 2 fields
        Assert.Equal("T-002", r2.Fields["id"].GetString());
        Assert.Equal(JsonValueKind.False, r2.Fields["enabled"].ValueKind);

        // RawElement is Object for both
        Assert.Equal(JsonValueKind.Object, r1.RawElement.ValueKind);
        Assert.Equal(JsonValueKind.Object, r2.RawElement.ValueKind);

        // Fields.Count == Keys.Count for both
        Assert.Equal(r1.Keys.Count, r1.Fields.Count);
        Assert.Equal(r2.Keys.Count, r2.Fields.Count);
    }
}
