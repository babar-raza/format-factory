// Tests for NdjsonRecord.Fields, Keys, TryGetValue, and RawElement.
// Sprint: ff-sprint-s148-dotnet-deepening-20260628
// Ledger: PC-NDJSON-R142

using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R142: Dedicated tests for NdjsonRecord.Fields, Keys, TryGetValue, and RawElement.
/// Fields returns a dict of field name→JsonElement for object records; empty for non-objects.
/// Keys returns list of top-level field names; empty for non-objects.
/// TryGetValue returns true+value for present keys; false+default for missing or non-objects.
/// RawElement returns the underlying JsonElement.
/// Covers: Fields non-object returns empty; Keys non-object returns empty;
/// TryGetValue non-object returns false; Fields object returns all fields;
/// Keys object returns all names; TryGetValue present key returns true;
/// TryGetValue absent key returns false; TryGetValue value correct;
/// RawElement is same element; dogfood TypedRecords->Fields->Keys pipeline;
/// dogfood TryGetValue chain across multiple records.
/// </summary>
public class NdjsonR142RecordFieldsAndTryGetValueTests
{
    private const string ThreeRecords =
        "{\"name\":\"Alice\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"score\":88}";

    // -------------------------------------------------------------------------
    // Non-object record tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Fields_NonObjectRecord_ReturnsEmptyDict()
    {
        var el = JsonDocument.Parse("42").RootElement;
        var rec = new NdjsonRecord(el);
        Assert.Empty(rec.Fields);
    }

    [Fact]
    public void Keys_NonObjectRecord_ReturnsEmptyList()
    {
        var el = JsonDocument.Parse("\"hello\"").RootElement;
        var rec = new NdjsonRecord(el);
        Assert.Empty(rec.Keys);
    }

    [Fact]
    public void TryGetValue_NonObjectRecord_ReturnsFalse()
    {
        var el = JsonDocument.Parse("true").RootElement;
        var rec = new NdjsonRecord(el);
        Assert.False(rec.TryGetValue("key", out _));
    }

    // -------------------------------------------------------------------------
    // Object record tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Fields_ObjectRecord_ReturnsAllFields()
    {
        var el = JsonDocument.Parse("{\"name\":\"Alice\",\"score\":95}").RootElement;
        var rec = new NdjsonRecord(el);
        Assert.Equal(2, rec.Fields.Count);
        Assert.True(rec.Fields.ContainsKey("name"));
        Assert.True(rec.Fields.ContainsKey("score"));
    }

    [Fact]
    public void Keys_ObjectRecord_ReturnsAllNames()
    {
        var el = JsonDocument.Parse("{\"a\":1,\"b\":2,\"c\":3}").RootElement;
        var rec = new NdjsonRecord(el);
        Assert.Equal(3, rec.Keys.Count);
        Assert.Contains("a", rec.Keys);
        Assert.Contains("b", rec.Keys);
        Assert.Contains("c", rec.Keys);
    }

    [Fact]
    public void TryGetValue_PresentKey_ReturnsTrue()
    {
        var el = JsonDocument.Parse("{\"name\":\"Alice\"}").RootElement;
        var rec = new NdjsonRecord(el);
        Assert.True(rec.TryGetValue("name", out _));
    }

    [Fact]
    public void TryGetValue_AbsentKey_ReturnsFalse()
    {
        var el = JsonDocument.Parse("{\"name\":\"Alice\"}").RootElement;
        var rec = new NdjsonRecord(el);
        Assert.False(rec.TryGetValue("missing", out _));
    }

    [Fact]
    public void TryGetValue_PresentKey_ValueCorrect()
    {
        var el = JsonDocument.Parse("{\"score\":42}").RootElement;
        var rec = new NdjsonRecord(el);
        Assert.True(rec.TryGetValue("score", out var val));
        Assert.Equal(42, val.GetInt32());
    }

    [Fact]
    public void RawElement_MatchesConstructorElement()
    {
        var doc = JsonDocument.Parse("{\"x\":1}");
        var el = doc.RootElement;
        var rec = new NdjsonRecord(el);
        Assert.Equal(JsonValueKind.Object, rec.RawElement.ValueKind);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TypedRecords_Fields_KeysCount()
    {
        var ndjsonDoc = NdjsonDocument.LoadContent(ThreeRecords);
        var typedRecords = ndjsonDoc.TypedRecords;
        Assert.Equal(3, typedRecords.Count);
        foreach (var rec in typedRecords)
        {
            Assert.Equal(2, rec.Keys.Count);
            Assert.Contains("name", rec.Keys);
            Assert.Contains("score", rec.Keys);
        }
    }

    [Fact]
    public void DogfoodPipeline_TryGetValue_ChainAcrossRecords_AllNamesExtracted()
    {
        var ndjsonDoc = NdjsonDocument.LoadContent(ThreeRecords);
        var names = new System.Collections.Generic.List<string>();
        foreach (var rec in ndjsonDoc.TypedRecords)
        {
            if (rec.TryGetValue("name", out var val))
                names.Add(val.GetString()!);
        }
        Assert.Equal(3, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }
}
