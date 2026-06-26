// Tests for NdjsonDocument.GetAllKeys, GetFieldValues, IsUniformSchema, Filter.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R147

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R147: Tests for NdjsonDocument.GetAllKeys, GetFieldValues, IsUniformSchema, Filter.
/// GetAllKeys(): returns distinct keys across all records.
/// GetFieldValues(key): returns all values for the given key across records.
/// IsUniformSchema(): true if all records have the same set of keys.
/// Filter(predicate): returns new NdjsonDocument with records matching predicate.
/// Covers: GetAllKeys with uniform records; GetAllKeys distinct across varying records;
/// GetAllKeys empty doc returns empty; GetFieldValues returns all values;
/// GetFieldValues missing key returns empty; GetFieldValues count matches record count;
/// IsUniformSchema true for uniform; IsUniformSchema false for varying;
/// IsUniformSchema true for single record; Filter count correct;
/// Filter result is independent; dogfood Load->GetAllKeys->Filter->GetFieldValues pipeline.
/// </summary>
public class NdjsonR147GetAllKeysAndIsUniformSchemaTests
{
    private const string UniformNdjson =
        "{\"name\":\"Alice\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"score\":88}";

    private const string VaryingNdjson =
        "{\"name\":\"Alice\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\"}\n" +
        "{\"city\":\"London\"}";

    // -------------------------------------------------------------------------
    // GetAllKeys
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAllKeys_UniformRecords_ReturnsExpectedKeys()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
    }

    [Fact]
    public void GetAllKeys_VaryingRecords_ReturnsDistinctKeys()
    {
        var doc = NdjsonDocument.Load(VaryingNdjson);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
        Assert.Contains("city", keys);
        // No duplicates
        Assert.Equal(keys.Count, keys.Distinct().Count());
    }

    [Fact]
    public void GetAllKeys_EmptyDoc_ReturnsEmpty()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        var keys = doc.GetAllKeys();
        Assert.Empty(keys);
    }

    [Fact]
    public void GetAllKeys_SingleRecord_ReturnsItsKeys()
    {
        var doc = NdjsonDocument.Load("{\"x\":1,\"y\":2,\"z\":3}");
        var keys = doc.GetAllKeys();
        Assert.Equal(3, keys.Count);
        Assert.Contains("x", keys);
    }

    // -------------------------------------------------------------------------
    // GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValues_ExistingKey_ReturnsAllValues()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var values = doc.GetFieldValues("name");
        Assert.Contains("Alice", values);
        Assert.Contains("Bob", values);
        Assert.Contains("Carol", values);
    }

    [Fact]
    public void GetFieldValues_MissingKey_ReturnsEmpty()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var values = doc.GetFieldValues("nonexistent");
        Assert.Empty(values);
    }

    [Fact]
    public void GetFieldValues_CountMatchesRecordCount()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var values = doc.GetFieldValues("score");
        Assert.Equal(doc.Count, values.Count);
    }

    [Fact]
    public void GetFieldValues_VaryingSchema_SkipsMissingRecords()
    {
        var doc = NdjsonDocument.Load(VaryingNdjson);
        var nameValues = doc.GetFieldValues("name");
        // Only 2 records have "name"
        Assert.Equal(2, nameValues.Count);
    }

    // -------------------------------------------------------------------------
    // IsUniformSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void IsUniformSchema_AllSameKeys_IsTrue()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_VaryingKeys_IsFalse()
    {
        var doc = NdjsonDocument.Load(VaryingNdjson);
        Assert.False(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_SingleRecord_IsTrue()
    {
        var doc = NdjsonDocument.Load("{\"a\":1}");
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_EmptyDoc_IsTrue()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        Assert.True(doc.IsUniformSchema());
    }

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_ByFieldValue_CountCorrect()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var filtered = doc.Filter(el =>
            el.TryGetProperty("score", out var s) && s.GetInt32() > 85);
        Assert.Equal(2, filtered.Count); // Alice(95) and Carol(88)
    }

    [Fact]
    public void Filter_KeepAll_SameCount()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var filtered = doc.Filter(_ => true);
        Assert.Equal(doc.Count, filtered.Count);
    }

    [Fact]
    public void Filter_KeepNone_EmptyResult()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var filtered = doc.Filter(_ => false);
        Assert.Equal(0, filtered.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->GetAllKeys->Filter->GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadKeysFilterFieldValues_Pipeline()
    {
        var ndjson =
            "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
            "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":72}\n" +
            "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":88}\n" +
            "{\"name\":\"Dave\",\"dept\":\"Finance\",\"score\":91}";

        var doc = NdjsonDocument.Load(ndjson);
        Assert.True(doc.IsUniformSchema());

        // All keys present
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
        Assert.Contains("score", keys);

        // Filter Eng dept
        var eng = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);

        // Get names of Eng dept members
        var engNames = eng.GetFieldValues("name");
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);

        // Verify uniform schema preserved
        Assert.True(eng.IsUniformSchema());
    }
}
