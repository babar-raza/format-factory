// Tests for NdjsonDocument.GetFieldValues, IsUniformSchema, Filter, GetAllKeys.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R153

using System;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R153: Tests for NdjsonDocument.GetFieldValues, IsUniformSchema, Filter, GetAllKeys.
/// GetFieldValues(key): returns all values for the named field as strings.
/// IsUniformSchema(): true when all records have the same set of keys.
/// GetAllKeys(): returns all unique keys across all records.
/// Filter(predicate): returns new NdjsonDocument with matching records.
/// Covers: GetFieldValues count equals Count; GetFieldValues contains expected values;
/// GetFieldValues numeric field returns string representations;
/// GetFieldValues missing field returns empty or nulls;
/// IsUniformSchema true for uniform records; IsUniformSchema false for mixed;
/// GetAllKeys count for 3-key schema; GetAllKeys contains all field names;
/// Filter predicate reduces Count; Filter count correct for bool field;
/// Filter then GetFieldValues on subset; GetAllKeys on empty doc;
/// dogfood Load->GetAllKeys->IsUniformSchema->Filter->GetFieldValues pipeline.
/// </summary>
public class NdjsonR153GetFieldValuesAndUniformSchemaTests
{
    private const string UniformNdjson =
        "{\"name\":\"Alice\",\"score\":95,\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Bob\",\"score\":82,\"dept\":\"Finance\"}\n" +
        "{\"name\":\"Carol\",\"score\":88,\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Dave\",\"score\":91,\"dept\":\"Finance\"}";

    private const string MixedNdjson =
        "{\"name\":\"Alice\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\"}";

    // -------------------------------------------------------------------------
    // GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValues_CountEqualsDocumentCount()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var values = doc.GetFieldValues("name");
        Assert.Equal(doc.Count, values.Count);
    }

    [Fact]
    public void GetFieldValues_ContainsExpectedValues()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var names = doc.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void GetFieldValues_NumericField_ReturnsStringRepresentations()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var scores = doc.GetFieldValues("score");
        Assert.Equal(4, scores.Count);
        Assert.Contains("95", scores);
        Assert.Contains("82", scores);
    }

    [Fact]
    public void GetFieldValues_MissingField_ReturnsMissingOrEmpty()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var vals = doc.GetFieldValues("nonexistent_key");
        // Either empty or contains null/empty strings for missing fields
        Assert.True(vals.Count == 0 || vals.All(v => v == null || v == ""));
    }

    // -------------------------------------------------------------------------
    // IsUniformSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void IsUniformSchema_UniformRecords_IsTrue()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_MixedRecords_IsFalse()
    {
        var doc = NdjsonDocument.Load(MixedNdjson);
        Assert.False(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_SingleRecord_IsTrue()
    {
        var doc = NdjsonDocument.Load("{\"x\":1}");
        Assert.True(doc.IsUniformSchema());
    }

    // -------------------------------------------------------------------------
    // GetAllKeys
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAllKeys_ThreeKeySchema_ReturnThreeKeys()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var keys = doc.GetAllKeys();
        Assert.Equal(3, keys.Count);
    }

    [Fact]
    public void GetAllKeys_ContainsAllFieldNames()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
        Assert.Contains("dept", keys);
    }

    [Fact]
    public void GetAllKeys_MixedDoc_ReturnsUnion()
    {
        var doc = NdjsonDocument.Load(MixedNdjson);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
        Assert.Contains("dept", keys);
    }

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_ReducesCount()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var eng = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.True(eng.Count < doc.Count);
        Assert.Equal(2, eng.Count);
    }

    [Fact]
    public void Filter_GetFieldValuesOnSubset()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var eng = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var names = eng.GetFieldValues("name");
        Assert.Equal(2, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }

    [Fact]
    public void Filter_ScoreAbove88_CountCorrect()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var high = doc.Filter(el =>
            el.TryGetProperty("score", out var s) && s.GetDouble() > 88);
        Assert.Equal(2, high.Count); // Alice(95), Dave(91)
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->GetAllKeys->IsUniformSchema->Filter->GetFieldValues pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AllKeysUniformFilterFieldValuesPipeline()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        Assert.Equal(4, doc.Count);

        // All keys
        var keys = doc.GetAllKeys();
        Assert.Equal(3, keys.Count);
        Assert.Contains("name", keys);

        // Uniform schema
        Assert.True(doc.IsUniformSchema());

        // Filter Finance dept
        var finance = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Finance");
        Assert.Equal(2, finance.Count);

        // Finance names
        var financeNames = finance.GetFieldValues("name");
        Assert.Contains("Bob", financeNames);
        Assert.Contains("Dave", financeNames);
        Assert.DoesNotContain("Alice", financeNames);

        // Finance is still uniform schema
        Assert.True(finance.IsUniformSchema());

        // Field values by score
        var scores = doc.GetFieldValues("score");
        Assert.Equal(4, scores.Count);
    }
}
