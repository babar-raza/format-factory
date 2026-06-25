// Tests for NdjsonDocument.IsUniformSchema, GetAllKeys, GetFieldValues, Filter.
// Sprint: FORMAT-FACTORY-NDJSON-SCHEMA-ANALYTICS-20260626
// Ledger: R118-GOVERNED-DOTNET-NDJSON-SCHEMA-ANALYTICS-001

using System;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R118: NdjsonDocument schema analytics — IsUniformSchema() returns true when all records
/// share the same set of keys; false when schemas diverge. GetAllKeys() returns the union
/// of all keys across records. GetFieldValues(key) collects all values for a given key.
/// Filter(predicate) returns a subset document with matching records.
/// </summary>
public class NdjsonR118SchemaAnalyticsTests
{
    private static NdjsonDocument LoadNdjson(string ndjson) =>
        NdjsonDocument.Load(ndjson);

    // ---- IsUniformSchema ----

    [Fact]
    public void IsUniformSchema_AllSameKeys_IsTrue()
    {
        var ndjson = "{\"name\":\"Alice\",\"age\":30}\n{\"name\":\"Bob\",\"age\":25}\n";
        var doc = LoadNdjson(ndjson);
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_DifferentKeys_IsFalse()
    {
        var ndjson = "{\"name\":\"Alice\",\"age\":30}\n{\"name\":\"Bob\",\"city\":\"NY\"}\n";
        var doc = LoadNdjson(ndjson);
        Assert.False(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_SingleRecord_IsTrue()
    {
        var ndjson = "{\"x\":1,\"y\":2}\n";
        var doc = LoadNdjson(ndjson);
        Assert.True(doc.IsUniformSchema());
    }

    // ---- GetAllKeys ----

    [Fact]
    public void GetAllKeys_UniformSchema_ContainsAllExpectedKeys()
    {
        var ndjson = "{\"name\":\"Alice\",\"score\":90}\n{\"name\":\"Bob\",\"score\":80}\n";
        var doc = LoadNdjson(ndjson);
        var keys = doc.GetAllKeys();

        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
    }

    [Fact]
    public void GetAllKeys_MixedSchema_UnionOfAllKeys()
    {
        var ndjson = "{\"a\":1}\n{\"b\":2}\n{\"c\":3}\n";
        var doc = LoadNdjson(ndjson);
        var keys = doc.GetAllKeys();

        Assert.Contains("a", keys);
        Assert.Contains("b", keys);
        Assert.Contains("c", keys);
    }

    [Fact]
    public void GetAllKeys_NoDuplicates()
    {
        var ndjson = "{\"x\":1,\"y\":2}\n{\"x\":3,\"y\":4}\n";
        var doc = LoadNdjson(ndjson);
        var keys = doc.GetAllKeys();

        // "x" and "y" each appear once even though present in both records
        var xCount = 0;
        foreach (var k in keys) if (k == "x") xCount++;
        Assert.Equal(1, xCount);
    }

    // ---- GetFieldValues ----

    [Fact]
    public void GetFieldValues_ExistingKey_ReturnsAllValues()
    {
        var ndjson = "{\"name\":\"Alice\"}\n{\"name\":\"Bob\"}\n{\"name\":\"Carol\"}\n";
        var doc = LoadNdjson(ndjson);
        var values = doc.GetFieldValues("name");

        Assert.Equal(3, values.Count);
    }

    [Fact]
    public void GetFieldValues_ValuesMatchRecordContent()
    {
        var ndjson = "{\"city\":\"London\"}\n{\"city\":\"Paris\"}\n";
        var doc = LoadNdjson(ndjson);
        var values = doc.GetFieldValues("city");

        Assert.Contains("London", values);
        Assert.Contains("Paris", values);
    }

    // ---- Filter ----

    [Fact]
    public void Filter_PredicateMatchesSomeRecords_CorrectCount()
    {
        var ndjson = "{\"score\":90}\n{\"score\":70}\n{\"score\":85}\n";
        var doc = LoadNdjson(ndjson);

        var filtered = doc.Filter(el =>
            el.TryGetProperty("score", out var s) && s.GetInt32() >= 80);

        Assert.Equal(2, filtered.Count);
    }

    [Fact]
    public void Filter_NoMatchingRecords_EmptyDocument()
    {
        var ndjson = "{\"x\":1}\n{\"x\":2}\n";
        var doc = LoadNdjson(ndjson);

        var filtered = doc.Filter(_ => false);

        Assert.Equal(0, filtered.Count);
    }

    // ---- Dogfood: schema analytics pipeline ----

    [Fact]
    public void DogfoodPipeline_UniformSchemaFilterKeys_Consistent()
    {
        var ndjson = string.Concat(
            "{\"name\":\"Alice\",\"score\":92,\"pass\":true}\n",
            "{\"name\":\"Bob\",\"score\":68,\"pass\":false}\n",
            "{\"name\":\"Carol\",\"score\":85,\"pass\":true}\n");

        var doc = LoadNdjson(ndjson);

        // Uniform schema
        Assert.True(doc.IsUniformSchema());

        // All keys present
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
        Assert.Contains("pass", keys);

        // Field values for "name"
        var names = doc.GetFieldValues("name");
        Assert.Equal(3, names.Count);

        // Filter to passing students
        var passing = doc.Filter(el =>
            el.TryGetProperty("pass", out var p) && p.GetBoolean());
        Assert.Equal(2, passing.Count);
    }
}
