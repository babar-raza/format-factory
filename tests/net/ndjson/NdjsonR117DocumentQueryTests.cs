// Tests for NdjsonDocument inspection APIs: GetAllKeys, Filter, GetFieldValues, IsUniformSchema
// Sprint: FORMAT-FACTORY-NDJSON-DOCUMENT-QUERY-20260624

using System;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

public class NdjsonR117DocumentQueryTests
{
    private const string _sample = """
        {"name":"Alice","age":30,"city":"Boston"}
        {"name":"Bob","age":25}
        {"name":"Carol","age":35,"city":"Denver"}
        """;

    private static NdjsonDocument Load(string content) => NdjsonDocument.Load(content);

    // ---- GetAllKeys ----

    [Fact]
    public void GetAllKeys_ReturnsAllTopLevelKeys()
    {
        var doc = Load(_sample);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("age", keys);
        Assert.Contains("city", keys);
    }

    [Fact]
    public void GetAllKeys_IsSorted()
    {
        var doc = Load(_sample);
        var keys = doc.GetAllKeys();
        for (int i = 1; i < keys.Count; i++)
            Assert.True(string.Compare(keys[i - 1], keys[i], StringComparison.Ordinal) < 0,
                $"Keys not sorted at index {i}");
    }

    [Fact]
    public void GetAllKeys_EmptyDocument_ReturnsEmpty()
    {
        var doc = Load("");
        Assert.Empty(doc.GetAllKeys());
    }

    [Fact]
    public void GetAllKeys_UniqueKeys_NoDuplicates()
    {
        var doc = Load(_sample);
        var keys = doc.GetAllKeys();
        Assert.Equal(keys.Count, new System.Collections.Generic.HashSet<string>(keys).Count);
    }

    // ---- Filter ----

    [Fact]
    public void Filter_ByStringField_ReturnsMatchingRecords()
    {
        var doc = Load(_sample);
        var filtered = doc.Filter(r =>
            r.ValueKind == JsonValueKind.Object
            && r.TryGetProperty("name", out var v)
            && v.GetString() == "Alice");
        Assert.Equal(1, filtered.Count);
    }

    [Fact]
    public void Filter_NoMatchReturnsEmptyDocument()
    {
        var doc = Load(_sample);
        var filtered = doc.Filter(r =>
            r.ValueKind == JsonValueKind.Object
            && r.TryGetProperty("name", out var v)
            && v.GetString() == "Zara");
        Assert.Equal(0, filtered.Count);
    }

    [Fact]
    public void Filter_AllMatchReturnsAllRecords()
    {
        var doc = Load(_sample);
        var filtered = doc.Filter(_ => true);
        Assert.Equal(doc.Count, filtered.Count);
    }

    [Fact]
    public void Filter_NullPredicateThrows()
    {
        var doc = Load(_sample);
        Assert.Throws<ArgumentNullException>(() => doc.Filter(null!));
    }

    // ---- GetFieldValues ----

    [Fact]
    public void GetFieldValues_ReturnsValuesForPresentKey()
    {
        var doc = Load(_sample);
        var names = doc.GetFieldValues("name");
        Assert.Equal(3, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void GetFieldValues_MissingKeyRecordsSkipped()
    {
        var doc = Load(_sample);
        // "city" is missing from Bob's record
        var cities = doc.GetFieldValues("city");
        Assert.Equal(2, cities.Count);
    }

    [Fact]
    public void GetFieldValues_NonexistentKeyReturnsEmpty()
    {
        var doc = Load(_sample);
        var vals = doc.GetFieldValues("zipcode");
        Assert.Empty(vals);
    }

    [Fact]
    public void GetFieldValues_NullKeyThrows()
    {
        var doc = Load(_sample);
        Assert.Throws<ArgumentNullException>(() => doc.GetFieldValues(null!));
    }

    // ---- IsUniformSchema ----

    [Fact]
    public void IsUniformSchema_UniformReturnsTrue()
    {
        var doc = Load("""
            {"a":1,"b":2}
            {"a":3,"b":4}
            """);
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_NonUniformReturnsFalse()
    {
        var doc = Load(_sample);  // Bob missing "city"
        Assert.False(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_EmptyDocumentReturnsTrue()
    {
        Assert.True(Load("").IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_SingleRecordReturnsTrue()
    {
        Assert.True(Load("{\"x\":1}").IsUniformSchema());
    }
}
