// Tests for NdjsonDocument.GetAllKeys, Filter, GetFieldValues, and IsUniformSchema.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R141

using System;
using System.Linq;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R141: Tests for NdjsonDocument.GetAllKeys, Filter, GetFieldValues, IsUniformSchema.
/// GetAllKeys returns a sorted union of all top-level keys across all object records.
/// Filter(predicate) returns a new NdjsonDocument with matching records only.
/// GetFieldValues(key) returns string representations of each record's value for that key.
/// IsUniformSchema returns true when all object records share the same keys; false if divergent.
/// Covers: GetAllKeys empty doc returns empty; GetAllKeys single record; GetAllKeys union across records;
/// Filter all match; Filter none match; Filter null predicate throws; Filter result count correct;
/// GetFieldValues missing key returns empty; GetFieldValues existing key returns all values;
/// IsUniformSchema empty returns true; IsUniformSchema uniform returns true;
/// IsUniformSchema divergent returns false;
/// dogfood Load->GetAllKeys->Filter->GetFieldValues pipeline.
/// </summary>
public class NdjsonR141GetAllKeysFilterFieldValuesTests
{
    private const string ThreeRecords =
        "{\"name\":\"Alice\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"score\":88}";

    private const string MixedSchema =
        "{\"id\":1,\"tag\":\"alpha\"}\n" +
        "{\"id\":2,\"tag\":\"beta\",\"extra\":true}";

    // -------------------------------------------------------------------------
    // GetAllKeys
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAllKeys_EmptyDocument_ReturnsEmpty()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        Assert.Empty(doc.GetAllKeys());
    }

    [Fact]
    public void GetAllKeys_SingleRecord_ReturnsItsKeys()
    {
        var doc = NdjsonDocument.Load("{\"x\":1,\"y\":2}");
        var keys = doc.GetAllKeys();
        Assert.Contains("x", keys);
        Assert.Contains("y", keys);
        Assert.Equal(2, keys.Count);
    }

    [Fact]
    public void GetAllKeys_MultipleRecords_ReturnsUnion()
    {
        var doc = NdjsonDocument.Load(MixedSchema);
        var keys = doc.GetAllKeys();
        Assert.Contains("id", keys);
        Assert.Contains("tag", keys);
        Assert.Contains("extra", keys);
        Assert.Equal(3, keys.Count);
    }

    [Fact]
    public void GetAllKeys_UniformRecords_NoDuplicates()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var keys = doc.GetAllKeys();
        Assert.Equal(2, keys.Count); // name, score only
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
    }

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_AllMatch_SameCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var filtered = doc.Filter(_ => true);
        Assert.Equal(doc.Records.Count, filtered.Records.Count);
    }

    [Fact]
    public void Filter_NoneMatch_ReturnsEmpty()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var filtered = doc.Filter(_ => false);
        Assert.Empty(filtered.Records);
    }

    [Fact]
    public void Filter_ByProperty_ReturnsMatchingCount()
    {
        // Filter records where score > 90
        var doc = NdjsonDocument.Load(ThreeRecords);
        var filtered = doc.Filter(el =>
            el.TryGetProperty("score", out var s) && s.GetInt32() > 90);
        Assert.Equal(1, filtered.Records.Count); // Alice (95)
    }

    [Fact]
    public void Filter_NullPredicate_Throws()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        Assert.Throws<ArgumentNullException>(() => doc.Filter(null!));
    }

    [Fact]
    public void Filter_ReturnsNewInstance()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var filtered = doc.Filter(_ => true);
        Assert.NotSame(doc, filtered);
    }

    // -------------------------------------------------------------------------
    // GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValues_ExistingKey_ReturnsAllValues()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var names = doc.GetFieldValues("name");
        Assert.Equal(3, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void GetFieldValues_MissingKey_ReturnsEmpty()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var vals = doc.GetFieldValues("nonexistent");
        Assert.Empty(vals);
    }

    [Fact]
    public void GetFieldValues_PartialKey_ReturnsOnlyPresent()
    {
        // MixedSchema: only second record has "extra"
        var doc = NdjsonDocument.Load(MixedSchema);
        var extras = doc.GetFieldValues("extra");
        Assert.Single(extras);
    }

    // -------------------------------------------------------------------------
    // IsUniformSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void IsUniformSchema_EmptyDocument_ReturnsTrue()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_UniformRecords_ReturnsTrue()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_DivergentSchema_ReturnsFalse()
    {
        var doc = NdjsonDocument.Load(MixedSchema);
        Assert.False(doc.IsUniformSchema());
    }

    // -------------------------------------------------------------------------
    // Dogfood: pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetAllKeys_Filter_GetFieldValues_Pipeline()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);

        // All keys present
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);

        // Filter high scorers (>= 88)
        var highScorers = doc.Filter(el =>
            el.TryGetProperty("score", out var s) && s.GetInt32() >= 88);
        Assert.Equal(2, highScorers.Records.Count); // Alice(95) + Carol(88)

        // Get their names
        var names = highScorers.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }
}
