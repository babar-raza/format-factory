// Tests for NdjsonDocument.Load(Stream) and LoadContent (alias).
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R145

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R145: Tests for NdjsonDocument.Load(Stream) and LoadContent(string).
/// Load(Stream): reads UTF-8 encoded NDJSON from a stream; returns NdjsonDocument.
/// LoadContent(string): alias for Load(string) — parses string content directly.
/// Covers: Load(Stream) valid stream returns correct count; Load(Stream) empty stream returns empty;
/// Load(Stream) preserves field values; Load(Stream) null stream throws;
/// LoadContent empty string returns empty; LoadContent single record returns count=1;
/// LoadContent multiple records returns correct count; LoadContent preserves field values;
/// LoadContent round-trips through ToNdjson; LoadContent whitespace-only is empty;
/// dogfood LoadContent->Filter->ToNdjson->Load(Stream) pipeline.
/// </summary>
public class NdjsonR145LoadStreamAndLoadContentTests
{
    private const string ThreeRecords =
        "{\"name\":\"Alice\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"score\":88}";

    private static Stream ToStream(string content) =>
        new MemoryStream(Encoding.UTF8.GetBytes(content));

    // -------------------------------------------------------------------------
    // Load(Stream)
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_ValidStream_CorrectCount()
    {
        using var stream = ToStream(ThreeRecords);
        var doc = NdjsonDocument.Load(stream);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void LoadStream_EmptyStream_ReturnsEmpty()
    {
        using var stream = ToStream(string.Empty);
        var doc = NdjsonDocument.Load(stream);
        Assert.Equal(0, doc.Count);
    }

    [Fact]
    public void LoadStream_PreservesFieldValues()
    {
        using var stream = ToStream(ThreeRecords);
        var doc = NdjsonDocument.Load(stream);
        var names = doc.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void LoadStream_SingleRecord_CountIsOne()
    {
        using var stream = ToStream("{\"x\":1}");
        var doc = NdjsonDocument.Load(stream);
        Assert.Equal(1, doc.Count);
    }

    [Fact]
    public void LoadStream_NullStream_Throws()
    {
        Assert.ThrowsAny<Exception>(() => NdjsonDocument.Load((Stream)null!));
    }

    // -------------------------------------------------------------------------
    // LoadContent (alias for Load(string))
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadContent_EmptyString_ReturnsEmpty()
    {
        var doc = NdjsonDocument.LoadContent(string.Empty);
        Assert.Equal(0, doc.Count);
    }

    [Fact]
    public void LoadContent_SingleRecord_CountIsOne()
    {
        var doc = NdjsonDocument.LoadContent("{\"a\":1}");
        Assert.Equal(1, doc.Count);
    }

    [Fact]
    public void LoadContent_MultipleRecords_CorrectCount()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecords);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void LoadContent_PreservesFieldValues()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecords);
        var names = doc.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void LoadContent_WhitespaceOnly_ReturnsEmpty()
    {
        var doc = NdjsonDocument.LoadContent("   \n  \n  ");
        Assert.Equal(0, doc.Count);
    }

    [Fact]
    public void LoadContent_RoundTripThroughToNdjson()
    {
        var doc1 = NdjsonDocument.LoadContent(ThreeRecords);
        var ndjson = doc1.ToNdjson();
        var doc2 = NdjsonDocument.LoadContent(ndjson);
        Assert.Equal(doc1.Count, doc2.Count);
    }

    [Fact]
    public void LoadContent_SameResultAsLoad()
    {
        var doc1 = NdjsonDocument.Load(ThreeRecords);
        var doc2 = NdjsonDocument.LoadContent(ThreeRecords);
        Assert.Equal(doc1.Count, doc2.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: LoadContent->Filter->ToNdjson->Load(Stream)
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContentFilterToNdjsonLoadStream_Pipeline()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecords);

        // Filter high scorers
        var high = doc.Filter(el =>
            el.TryGetProperty("score", out var s) && s.GetInt32() >= 88);
        Assert.Equal(2, high.Count); // Alice(95), Carol(88)

        // Serialize
        var ndjson = high.ToNdjson();

        // Load from stream
        using var stream = ToStream(ndjson);
        var reloaded = NdjsonDocument.Load(stream);
        Assert.Equal(2, reloaded.Count);

        var names = reloaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }
}
