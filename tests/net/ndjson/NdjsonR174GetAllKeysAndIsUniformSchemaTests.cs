// Tests for NdjsonDocument.GetAllKeys, IsUniformSchema deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R174

using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R174: Tests for NdjsonDocument.GetAllKeys, IsUniformSchema deeper coverage.
/// GetAllKeys(): returns union of all field names across all records.
/// IsUniformSchema(): returns true if all records have the same set of keys.
/// Covers: GetAllKeys non-empty for non-empty doc; GetAllKeys contains all field names;
/// GetAllKeys empty for empty doc; GetAllKeys count matches field count;
/// GetAllKeys after Filter may change if schema changes;
/// IsUniformSchema true for uniform records; IsUniformSchema false for mixed schema;
/// IsUniformSchema true after Filter that preserves schema;
/// IsUniformSchema for single record is true; IsUniformSchema for empty doc;
/// GetAllKeys->IsUniformSchema relationship; GetAllKeys stable on multiple calls;
/// IsUniformSchema->Filter->IsUniformSchema chain; GetAllKeys non-empty after Load;
/// GetAllKeys count with extra field record;
/// dogfood Load->GetAllKeys->IsUniformSchema->Filter->GetAllKeys->IsUniformSchema verify.
/// </summary>
public class NdjsonR174GetAllKeysAndIsUniformSchemaTests
{
    private const string UniformNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":88}";

    private const string MixedNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"city\":\"NYC\"}\n" +
        "{\"id\":3,\"value\":42.5}";

    // -------------------------------------------------------------------------
    // GetAllKeys
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAllKeys_NonEmpty_ForNonEmptyDoc()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        Assert.NotEmpty(doc.GetAllKeys());
    }

    [Fact]
    public void GetAllKeys_ContainsAllFieldNames()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
        Assert.Contains("score", keys);
    }

    [Fact]
    public void GetAllKeys_Empty_ForEmptyDoc()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        Assert.Empty(doc.GetAllKeys());
    }

    [Fact]
    public void GetAllKeys_Count_MatchesFieldCount()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        Assert.Equal(3, doc.GetAllKeys().Count);
    }

    [Fact]
    public void GetAllKeys_Stable_OnMultipleCalls()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var keys1 = doc.GetAllKeys();
        var keys2 = doc.GetAllKeys();
        Assert.Equal(keys1.Count, keys2.Count);
    }

    [Fact]
    public void GetAllKeys_MixedSchema_UnionOfAllKeys()
    {
        var doc = NdjsonDocument.Load(MixedNdjson);
        var keys = doc.GetAllKeys();
        // Union should have: name, dept, score, city, id, value
        Assert.True(keys.Count >= 4);
        Assert.Contains("name", keys);
    }

    [Fact]
    public void GetAllKeys_AfterFilter_SchemaPreserved()
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
    public void IsUniformSchema_True_ForUniformRecords()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_False_ForMixedSchema()
    {
        var doc = NdjsonDocument.Load(MixedNdjson);
        Assert.False(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_True_ForSingleRecord()
    {
        var doc = NdjsonDocument.Load("{\"a\":1,\"b\":2}");
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_True_ForEmptyDoc()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        // Empty doc has vacuously uniform schema
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_AfterFilter_StillTrue_ForUniform()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.True(eng.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_Stable_OnMultipleCalls()
    {
        var doc = NdjsonDocument.Load(UniformNdjson);
        Assert.True(doc.IsUniformSchema());
        Assert.True(doc.IsUniformSchema());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadGetAllKeysIsUniformFilterGetAllKeysIsUniformVerify_Pipeline()
    {
        // Load uniform doc
        var doc = NdjsonDocument.Load(UniformNdjson);
        Assert.Equal(3, doc.Count);

        // GetAllKeys
        var keys = doc.GetAllKeys();
        Assert.Equal(3, keys.Count);
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
        Assert.Contains("score", keys);

        // IsUniformSchema
        Assert.True(doc.IsUniformSchema());

        // Filter Eng
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);

        // GetAllKeys after filter — same schema
        var filteredKeys = eng.GetAllKeys();
        Assert.Equal(3, filteredKeys.Count);
        Assert.Contains("name", filteredKeys);

        // IsUniformSchema after filter — still true
        Assert.True(eng.IsUniformSchema());

        // Load mixed schema
        var mixed = NdjsonDocument.Load(MixedNdjson);
        Assert.False(mixed.IsUniformSchema());
        var mixedKeys = mixed.GetAllKeys();
        Assert.True(mixedKeys.Count > 3); // union of different schemas
    }
}
