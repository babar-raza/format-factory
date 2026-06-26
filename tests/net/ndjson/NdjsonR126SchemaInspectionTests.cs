// Tests for NdjsonDocument schema inspection: GetAllKeys() and IsUniformSchema().
// Sprint: FORMAT-FACTORY-NDJSON-R126-20260626
// Ledger: R126-GOVERNED-DOTNET-NDJSON-SCHEMA-INSPECTION-001

using System;
using System.Collections.Generic;
using System.Linq;
using FormatFactory.Ndjson;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R126: Tests for NdjsonDocument schema inspection methods.
/// GetAllKeys() returns the union of all keys across all records.
/// IsUniformSchema() returns true only when every record has the same set of keys.
/// Covers: uniform schema, non-uniform schema, empty document, single-record document,
/// key ordering not guaranteed (set semantics), dogfood analytics pipeline.
/// </summary>
public class NdjsonR126SchemaInspectionTests
{
    private static NdjsonDocument Uniform() =>
        NdjsonDocument.Load(
            "{\"name\":\"Alice\",\"score\":95,\"active\":true}\n" +
            "{\"name\":\"Bob\",\"score\":80,\"active\":false}\n" +
            "{\"name\":\"Carol\",\"score\":88,\"active\":true}\n");

    private static NdjsonDocument NonUniform() =>
        NdjsonDocument.Load(
            "{\"name\":\"Alice\",\"score\":95}\n" +
            "{\"name\":\"Bob\",\"city\":\"London\"}\n" +
            "{\"name\":\"Carol\",\"score\":88,\"active\":true}\n");

    private static NdjsonDocument Empty() =>
        NdjsonDocument.Load(string.Empty);

    // -------------------------------------------------------------------------
    // GetAllKeys — uniform schema
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAllKeys_UniformSchema_ContainsAllExpectedKeys()
    {
        var doc = Uniform();
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
        Assert.Contains("active", keys);
    }

    [Fact]
    public void GetAllKeys_UniformSchema_ExactKeyCount()
    {
        var doc = Uniform();
        var keys = doc.GetAllKeys();
        Assert.Equal(3, keys.Count);
    }

    [Fact]
    public void GetAllKeys_UniformSchema_NoDuplicates()
    {
        var doc = Uniform();
        var keys = doc.GetAllKeys();
        Assert.Equal(keys.Count, keys.Distinct().Count());
    }

    // -------------------------------------------------------------------------
    // GetAllKeys — non-uniform schema
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAllKeys_NonUniform_ContainsUnionOfAllKeys()
    {
        var doc = NonUniform();
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
        Assert.Contains("city", keys);
        Assert.Contains("active", keys);
    }

    [Fact]
    public void GetAllKeys_NonUniform_KeyCountIsUnion()
    {
        var doc = NonUniform();
        var keys = doc.GetAllKeys();
        Assert.Equal(4, keys.Count);
    }

    // -------------------------------------------------------------------------
    // GetAllKeys — edge cases
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAllKeys_EmptyDocument_ReturnsEmpty()
    {
        var doc = Empty();
        var keys = doc.GetAllKeys();
        Assert.Empty(keys);
    }

    [Fact]
    public void GetAllKeys_SingleRecord_MatchesThatRecord()
    {
        var doc = NdjsonDocument.Load("{\"x\":1,\"y\":2}");
        var keys = doc.GetAllKeys();
        Assert.Contains("x", keys);
        Assert.Contains("y", keys);
        Assert.Equal(2, keys.Count);
    }

    // -------------------------------------------------------------------------
    // IsUniformSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void IsUniformSchema_AllSameKeys_ReturnsTrue()
    {
        var doc = Uniform();
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_DifferentKeys_ReturnsFalse()
    {
        var doc = NonUniform();
        Assert.False(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_EmptyDocument_ReturnsTrue()
    {
        var doc = Empty();
        // Vacuously uniform: no records to violate uniformity
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_SingleRecord_ReturnsTrue()
    {
        var doc = NdjsonDocument.Load("{\"a\":1,\"b\":2}");
        Assert.True(doc.IsUniformSchema());
    }

    // -------------------------------------------------------------------------
    // Dogfood: schema inspection analytics pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void SchemaInspection_DogfoodPipeline_UniformSchemaEnablesFieldAccess()
    {
        var doc = Uniform();
        Assert.True(doc.IsUniformSchema());
        var keys = doc.GetAllKeys();
        foreach (var key in keys)
        {
            var values = doc.GetFieldValues(key);
            Assert.Equal(doc.Count, values.Count);
        }
    }

    [Fact]
    public void SchemaInspection_NonUniform_GetAllKeysAlwaysSucceeds()
    {
        var doc = NonUniform();
        var keys = doc.GetAllKeys();
        // GetAllKeys should never throw, even for non-uniform schemas
        Assert.NotNull(keys);
        Assert.True(keys.Count >= 0);
    }
}
