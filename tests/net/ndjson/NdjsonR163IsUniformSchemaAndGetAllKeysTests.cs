// Tests for NdjsonDocument.IsUniformSchema and GetAllKeys deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R163

using System.Linq;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R163: Tests for NdjsonDocument.IsUniformSchema and GetAllKeys deeper coverage.
/// IsUniformSchema(): true when all records have exactly the same keys.
/// GetAllKeys(): returns union of all field names across all records.
/// Covers: IsUniformSchema uniform doc true; IsUniformSchema mixed doc false;
/// IsUniformSchema single record true; IsUniformSchema empty doc true;
/// GetAllKeys uniform doc has all fields; GetAllKeys mixed doc has union;
/// GetAllKeys empty doc is empty; GetAllKeys on filtered keeps all original keys;
/// IsUniformSchema after Filter (uniform subset) true;
/// IsUniformSchema doc with extra fields false;
/// GetAllKeys count equals distinct field names; GetAllKeys no duplicates;
/// IsUniformSchema on single-field doc; GetAllKeys single-field count is one;
/// dogfood Load->GetAllKeys->IsUniformSchema->Filter->GetAllKeys pipeline.
/// </summary>
public class NdjsonR163IsUniformSchemaAndGetAllKeysTests
{
    private const string UniformNdjson =
        "{\"a\":1,\"b\":2,\"c\":3}\n" +
        "{\"a\":4,\"b\":5,\"c\":6}\n" +
        "{\"a\":7,\"b\":8,\"c\":9}";

    private const string MixedNdjson =
        "{\"a\":1,\"b\":2}\n" +
        "{\"a\":3,\"c\":4}\n" +
        "{\"d\":5}";

    // -------------------------------------------------------------------------
    // IsUniformSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void IsUniformSchema_UniformDoc_ReturnsTrue()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_MixedDoc_ReturnsFalse()
    {
        var doc = NdjsonDocument.Load(MixedNdjson);
        Assert.False(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_SingleRecord_ReturnsTrue()
    {
        var doc = NdjsonDocument.Load("{\"x\":1,\"y\":2}");
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_EmptyDoc_ReturnsTrue()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        Assert.True(doc.IsUniformSchema()); // vacuously uniform
    }

    [Fact]
    public void IsUniformSchema_SingleFieldDoc_ReturnsTrue()
    {
        var doc = NdjsonDocument.Load("{\"k\":1}\n{\"k\":2}\n{\"k\":3}");
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_ExtraFieldDoc_ReturnsFalse()
    {
        var ndjson = "{\"a\":1,\"b\":2}\n{\"a\":3,\"b\":4,\"c\":5}";
        var doc = NdjsonDocument.Load(ndjson);
        Assert.False(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_AfterFilter_UniformSubset_ReturnsTrue()
    {
        var doc = NdjsonDocument.Load(MixedNdjson);
        // Filter to records with key "a"
        var sub = doc.Filter(el => el.TryGetProperty("a", out _));
        Assert.True(sub.IsUniformSchema());
    }

    // -------------------------------------------------------------------------
    // GetAllKeys
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAllKeys_UniformDoc_HasAllFields()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var keys = doc.GetAllKeys();
        Assert.Contains("a", keys);
        Assert.Contains("b", keys);
        Assert.Contains("c", keys);
    }

    [Fact]
    public void GetAllKeys_MixedDoc_HasUnionOfFields()
    {
        var doc = NdjsonDocument.Load(MixedNdjson);
        var keys = doc.GetAllKeys();
        Assert.Contains("a", keys);
        Assert.Contains("b", keys);
        Assert.Contains("c", keys);
        Assert.Contains("d", keys);
    }

    [Fact]
    public void GetAllKeys_EmptyDoc_IsEmpty()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        var keys = doc.GetAllKeys();
        Assert.Empty(keys);
    }

    [Fact]
    public void GetAllKeys_NoDuplicates()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var keys = doc.GetAllKeys();
        Assert.Equal(keys.Count, keys.Distinct().Count());
    }

    [Fact]
    public void GetAllKeys_SingleFieldDoc_CountIsOne()
    {
        var doc = NdjsonDocument.Load("{\"k\":1}\n{\"k\":2}");
        var keys = doc.GetAllKeys();
        Assert.Single(keys);
        Assert.Contains("k", keys);
    }

    [Fact]
    public void GetAllKeys_OnFiltered_KeepsOriginalKeys()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var sub = doc.Filter(el => el.TryGetProperty("a", out var v) && v.GetInt32() > 3);
        var keys = sub.GetAllKeys();
        Assert.Contains("a", keys);
        Assert.Contains("b", keys);
        Assert.Contains("c", keys);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->GetAllKeys->IsUniformSchema->Filter->GetAllKeys
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetAllKeysIsUniformSchemaFilterGetAllKeys_Pipeline()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        Assert.Equal(3, doc.Count);

        // GetAllKeys
        var allKeys = doc.GetAllKeys();
        Assert.Equal(3, allKeys.Count);
        Assert.Contains("a", allKeys);

        // IsUniformSchema
        Assert.True(doc.IsUniformSchema());

        // Filter: records where a > 3
        var high = doc.Filter(el => el.TryGetProperty("a", out var v) && v.GetDouble() > 3);
        Assert.Equal(2, high.Count);

        // GetAllKeys on filtered
        var filteredKeys = high.GetAllKeys();
        Assert.Contains("a", filteredKeys);
        Assert.Contains("b", filteredKeys);
        Assert.Contains("c", filteredKeys);

        // IsUniformSchema on filtered
        Assert.True(high.IsUniformSchema());

        // GetFieldValues
        var aVals = high.GetFieldValues("a");
        Assert.Equal(2, aVals.Count);
    }
}
