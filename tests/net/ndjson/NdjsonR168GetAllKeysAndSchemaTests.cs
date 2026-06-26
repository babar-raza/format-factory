// Tests for NdjsonDocument.GetAllKeys, IsUniformSchema deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R168

using System.Linq;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R168: Tests for NdjsonDocument.GetAllKeys, IsUniformSchema deeper coverage.
/// GetAllKeys(): returns set of all distinct field names across all records.
/// IsUniformSchema(): returns true if all records have exactly the same keys.
/// Covers: GetAllKeys non-null; GetAllKeys non-empty for data;
/// GetAllKeys contains expected field names; GetAllKeys count matches schema;
/// GetAllKeys union for non-uniform; IsUniformSchema true for uniform doc;
/// IsUniformSchema false for non-uniform doc; IsUniformSchema empty doc;
/// IsUniformSchema single record always true; GetAllKeys single record;
/// GetAllKeys after Filter; IsUniformSchema after Filter;
/// GetAllKeys superset for mixed doc; IsUniformSchema for all-same-keys;
/// GetAllKeys does not duplicate keys;
/// dogfood Load->GetAllKeys->IsUniformSchema->Filter->GetAllKeys->IsUniformSchema chain.
/// </summary>
public class NdjsonR168GetAllKeysAndSchemaTests
{
    private const string UniformNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":88}";

    private const string NonUniformNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Bob\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Eng\",\"extra\":true}";

    // -------------------------------------------------------------------------
    // GetAllKeys
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAllKeys_NonNull()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        Assert.NotNull(doc.GetAllKeys());
    }

    [Fact]
    public void GetAllKeys_NonEmpty()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        Assert.NotEmpty(doc.GetAllKeys());
    }

    [Fact]
    public void GetAllKeys_ContainsExpectedFieldNames()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
        Assert.Contains("score", keys);
    }

    [Fact]
    public void GetAllKeys_CountMatchesSchemaForUniform()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var keys = doc.GetAllKeys();
        Assert.Equal(3, keys.Count);
    }

    [Fact]
    public void GetAllKeys_EmptyDoc_EmptySet()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        var keys = doc.GetAllKeys();
        Assert.Empty(keys);
    }

    [Fact]
    public void GetAllKeys_SingleRecord()
    {
        var doc = NdjsonDocument.Load("{\"id\":1,\"value\":\"test\"}");
        var keys = doc.GetAllKeys();
        Assert.Equal(2, keys.Count);
        Assert.Contains("id", keys);
        Assert.Contains("value", keys);
    }

    [Fact]
    public void GetAllKeys_NonUniform_IsSupersetOfAllKeys()
    {
        var doc = NdjsonDocument.Load(NonUniformNdjson);
        var keys = doc.GetAllKeys();
        // Should contain all distinct keys across all records
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
        Assert.Contains("score", keys);
        Assert.Contains("extra", keys);
    }

    [Fact]
    public void GetAllKeys_NoDuplicates()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var keys = doc.GetAllKeys().ToList();
        Assert.Equal(keys.Count, keys.Distinct().Count());
    }

    [Fact]
    public void GetAllKeys_AfterFilter_CorrectKeys()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var keys = eng.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
        Assert.Contains("score", keys);
    }

    // -------------------------------------------------------------------------
    // IsUniformSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void IsUniformSchema_TrueForUniformDoc()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_FalseForNonUniform()
    {
        var doc = NdjsonDocument.Load(NonUniformNdjson);
        Assert.False(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_TrueForEmptyDoc()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_TrueForSingleRecord()
    {
        var doc = NdjsonDocument.Load("{\"id\":1,\"val\":\"x\"}");
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_AfterFilter_StillTrue()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.True(eng.IsUniformSchema());
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->GetAllKeys->IsUniformSchema->Filter->GetAllKeys->IsUniformSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadGetKeysIsUniformFilterGetKeysIsUniform_Chain()
    {
        // Uniform doc
        var doc = NdjsonDocument.Load(UniformNdjson);
        Assert.Equal(3, doc.Count);

        var keys = doc.GetAllKeys();
        Assert.Equal(3, keys.Count);
        Assert.Contains("name", keys);
        Assert.True(doc.IsUniformSchema());

        // Filter
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);

        var engKeys = eng.GetAllKeys();
        Assert.Equal(3, engKeys.Count);
        Assert.True(eng.IsUniformSchema());

        // Non-uniform doc
        var mixed = NdjsonDocument.Load(NonUniformNdjson);
        Assert.False(mixed.IsUniformSchema());

        var mixedKeys = mixed.GetAllKeys();
        Assert.True(mixedKeys.Count >= 4);
        Assert.Contains("extra", mixedKeys);
    }
}
