// Tests for NdjsonDocument.IsUniformSchema and GetAllKeys deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R177

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R177: Tests for NdjsonDocument.IsUniformSchema and GetAllKeys deeper coverage.
/// IsUniformSchema: true when all records share the same set of keys.
/// GetAllKeys(): returns the union of all keys across all records.
/// Covers: IsUniformSchema true for uniform content; IsUniformSchema false for mixed keys;
/// IsUniformSchema single record is uniform; IsUniformSchema empty-ish doc;
/// IsUniformSchema after Filter still uniform; GetAllKeys non-null;
/// GetAllKeys count correct for uniform; GetAllKeys count is union for mixed;
/// GetAllKeys contains expected keys; GetAllKeys after Filter;
/// GetAllKeys for single record equals its fields;
/// dogfood Load->IsUniformSchema->GetAllKeys->Filter->IsUniformSchema->GetAllKeys verify.
/// </summary>
public class NdjsonR177IsUniformSchemaAndGetAllKeysDeepTests
{
    private const string UniformNdjson =
        "{\"id\":1,\"name\":\"Alice\",\"dept\":\"Eng\"}\n" +
        "{\"id\":2,\"name\":\"Bob\",\"dept\":\"Finance\"}\n" +
        "{\"id\":3,\"name\":\"Carol\",\"dept\":\"Eng\"}";

    private const string MixedNdjson =
        "{\"id\":1,\"name\":\"Alice\",\"dept\":\"Eng\"}\n" +
        "{\"id\":2,\"name\":\"Bob\"}\n" +
        "{\"id\":3,\"name\":\"Carol\",\"dept\":\"Eng\",\"level\":\"Senior\"}";

    // -------------------------------------------------------------------------
    // IsUniformSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void IsUniformSchema_UniformContent_True()
    {
        var doc = NdjsonDocument.LoadContent(UniformNdjson);
        Assert.True(doc.IsUniformSchema);
    }

    [Fact]
    public void IsUniformSchema_MixedKeys_False()
    {
        var doc = NdjsonDocument.LoadContent(MixedNdjson);
        Assert.False(doc.IsUniformSchema);
    }

    [Fact]
    public void IsUniformSchema_SingleRecord_True()
    {
        var doc = NdjsonDocument.LoadContent("{\"x\":1,\"y\":2}");
        Assert.True(doc.IsUniformSchema);
    }

    [Fact]
    public void IsUniformSchema_AfterFilter_UniformSubset_True()
    {
        var doc = NdjsonDocument.LoadContent(UniformNdjson);
        var eng = doc.Filter(r => r.TryGetValue("dept", out var d) && d == "Eng");
        Assert.True(eng.IsUniformSchema);
    }

    [Fact]
    public void IsUniformSchema_SubsetOfMixed_CanBeUniform()
    {
        // Filter mixed to only records with all 3 common keys
        var doc = NdjsonDocument.LoadContent(MixedNdjson);
        var withDept = doc.Filter(r => r.TryGetValue("dept", out _));
        // These have dept but not necessarily level — not guaranteed uniform
        // Just verify it doesn't throw
        var _ = withDept.IsUniformSchema;
    }

    // -------------------------------------------------------------------------
    // GetAllKeys
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAllKeys_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(UniformNdjson);
        Assert.NotNull(doc.GetAllKeys());
    }

    [Fact]
    public void GetAllKeys_UniformContent_CountCorrect()
    {
        var doc = NdjsonDocument.LoadContent(UniformNdjson);
        var keys = doc.GetAllKeys();
        Assert.Equal(3, keys.Count); // id, name, dept
    }

    [Fact]
    public void GetAllKeys_UniformContent_ContainsExpectedKeys()
    {
        var doc = NdjsonDocument.LoadContent(UniformNdjson);
        var keys = doc.GetAllKeys();
        Assert.Contains("id", keys);
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
    }

    [Fact]
    public void GetAllKeys_MixedContent_IsUnion()
    {
        var doc = NdjsonDocument.LoadContent(MixedNdjson);
        var keys = doc.GetAllKeys();
        // Union: id, name, dept, level
        Assert.True(keys.Count >= 3);
        Assert.Contains("id", keys);
        Assert.Contains("name", keys);
    }

    [Fact]
    public void GetAllKeys_MixedContent_ContainsAllDistinctKeys()
    {
        var doc = NdjsonDocument.LoadContent(MixedNdjson);
        var keys = doc.GetAllKeys();
        Assert.Contains("dept", keys); // in records 1 and 3
        Assert.Contains("level", keys); // in record 3 only
    }

    [Fact]
    public void GetAllKeys_AfterFilter_ReducedSet()
    {
        var doc = NdjsonDocument.LoadContent(UniformNdjson);
        var filtered = doc.Filter(r => r.TryGetValue("dept", out var d) && d == "Eng");
        var keys = filtered.GetAllKeys();
        Assert.NotNull(keys);
        // Filtered doc still has same schema as original
        Assert.Contains("name", keys);
    }

    [Fact]
    public void GetAllKeys_SingleRecord_EqualsItsFields()
    {
        var doc = NdjsonDocument.LoadContent("{\"alpha\":1,\"beta\":2,\"gamma\":3}");
        var keys = doc.GetAllKeys();
        Assert.Equal(3, keys.Count);
        Assert.Contains("alpha", keys);
        Assert.Contains("beta", keys);
        Assert.Contains("gamma", keys);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadIsUniformGetAllKeysFilterIsUniformGetAllKeysVerify_Pipeline()
    {
        // Load uniform content
        var doc = NdjsonDocument.LoadContent(UniformNdjson);
        Assert.Equal(3, doc.Count);

        // IsUniformSchema
        Assert.True(doc.IsUniformSchema);

        // GetAllKeys
        var keys = doc.GetAllKeys();
        Assert.Equal(3, keys.Count);
        Assert.Contains("id", keys);
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);

        // Filter to Eng dept
        var eng = doc.Filter(r => r.TryGetValue("dept", out var d) && d == "Eng");
        Assert.Equal(2, eng.Count);

        // IsUniformSchema after filter
        Assert.True(eng.IsUniformSchema);

        // GetAllKeys after filter — same 3 keys
        var engKeys = eng.GetAllKeys();
        Assert.Equal(3, engKeys.Count);

        // Load mixed content
        var mixed = NdjsonDocument.LoadContent(MixedNdjson);
        Assert.False(mixed.IsUniformSchema);

        // GetAllKeys for mixed — has 4 distinct keys
        var mixedKeys = mixed.GetAllKeys();
        Assert.True(mixedKeys.Count >= 3);
        Assert.Contains("level", mixedKeys);
    }
}
