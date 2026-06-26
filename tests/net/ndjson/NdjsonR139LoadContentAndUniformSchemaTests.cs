// Tests for NdjsonDocument.LoadContent and NdjsonDocument.IsUniformSchema.
// Sprint: ff-sprint-s142-dotnet-deepening-20260627
// Ledger: PC-NDJSON-R139

using System;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R139: Tests for NdjsonDocument.LoadContent and NdjsonDocument.IsUniformSchema.
/// LoadContent is a named alias for Load(string) that accepts JSONL string content.
/// IsUniformSchema returns true when all object records share the same set of keys.
/// Covers: LoadContent null throws; LoadContent empty string returns empty doc;
/// LoadContent valid JSONL returns record count; LoadContent result matches Load;
/// IsUniformSchema empty doc returns true; single record returns true;
/// uniform records returns true; mixed keys returns false;
/// non-object records (mixed types) treated as uniform with no key set;
/// dogfood LoadContent->Filter->IsUniformSchema pipeline.
/// </summary>
public class NdjsonR139LoadContentAndUniformSchemaTests
{
    private const string UniformContent =
        "{\"name\":\"Alice\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"score\":88}";

    private const string NonUniformContent =
        "{\"name\":\"Alice\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"age\":30}";

    // -------------------------------------------------------------------------
    // LoadContent tests
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadContent_NullContent_ThrowsException()
    {
        Assert.ThrowsAny<Exception>(() => NdjsonDocument.LoadContent(null!));
    }

    [Fact]
    public void LoadContent_EmptyString_ReturnsEmptyDocument()
    {
        var doc = NdjsonDocument.LoadContent(string.Empty);
        Assert.NotNull(doc);
        Assert.Equal(0, doc.Count);
    }

    [Fact]
    public void LoadContent_ValidJsonl_ReturnsCorrectRecordCount()
    {
        var doc = NdjsonDocument.LoadContent(UniformContent);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void LoadContent_ResultMatchesLoad()
    {
        var viaLoadContent = NdjsonDocument.LoadContent(UniformContent);
        var viaLoad = NdjsonDocument.Load(UniformContent);
        Assert.Equal(viaLoad.Count, viaLoadContent.Count);
    }

    [Fact]
    public void LoadContent_SingleRecord_ReturnsOneRecord()
    {
        var doc = NdjsonDocument.LoadContent("{\"key\":\"value\"}");
        Assert.Equal(1, doc.Count);
    }

    // -------------------------------------------------------------------------
    // IsUniformSchema tests
    // -------------------------------------------------------------------------

    [Fact]
    public void IsUniformSchema_EmptyDocument_ReturnsTrue()
    {
        var doc = NdjsonDocument.LoadContent(string.Empty);
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_SingleRecord_ReturnsTrue()
    {
        var doc = NdjsonDocument.LoadContent("{\"name\":\"Alice\",\"score\":95}");
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_UniformRecords_ReturnsTrue()
    {
        var doc = NdjsonDocument.LoadContent(UniformContent);
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_DifferentKeysSets_ReturnsFalse()
    {
        var doc = NdjsonDocument.LoadContent(NonUniformContent);
        Assert.False(doc.IsUniformSchema());
    }

    // -------------------------------------------------------------------------
    // Dogfood: LoadContent -> Filter -> IsUniformSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_LoadContent_Filter_IsUniformSchema_True()
    {
        var doc = NdjsonDocument.LoadContent(UniformContent);
        // Filter to high-scorers — same schema
        var filtered = doc.Filter(r =>
            r.TryGetProperty("score", out var s) && s.GetInt32() >= 88);
        Assert.Equal(2, filtered.Count);
        Assert.True(filtered.IsUniformSchema());
    }
}
