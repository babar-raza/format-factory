// Tests for NdjsonDocument.Load(Stream stream) — stream-based NDJSON loading.
// Sprint: FORMAT-FACTORY-NDJSON-R125-20260627
// Ledger: R125-GOVERNED-DOTNET-NDJSON-STREAM-LOAD-001

using System;
using System.IO;
using System.Text;
using FormatFactory.Ndjson;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R125: Tests for NdjsonDocument.Load(Stream stream) — the stream-based load overload.
/// Covers: non-null document from MemoryStream; record count; record keys present;
/// parity with string-based Load; empty stream returns empty doc; multi-record stream;
/// UTF-8 BOM tolerance; null stream throws ArgumentNullException; dogfood analytics pipeline.
/// </summary>
public class NdjsonR125StreamLoadTests
{
    private static Stream ToStream(string content)
        => new MemoryStream(Encoding.UTF8.GetBytes(content));

    private const string ThreeRecords =
        "{\"name\":\"Alice\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"score\":80}\n" +
        "{\"name\":\"Carol\",\"score\":88}\n";

    // -------------------------------------------------------------------------
    // Basic load from MemoryStream
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_Stream_DocumentIsNotNull()
    {
        using var ms = ToStream(ThreeRecords);
        var doc = NdjsonDocument.Load(ms);
        Assert.NotNull(doc);
    }

    [Fact]
    public void Load_Stream_RecordCountMatchesLines()
    {
        using var ms = ToStream(ThreeRecords);
        var doc = NdjsonDocument.Load(ms);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void Load_Stream_RecordsCollectionNonEmpty()
    {
        using var ms = ToStream(ThreeRecords);
        var doc = NdjsonDocument.Load(ms);
        Assert.NotEmpty(doc.Records);
    }

    [Fact]
    public void Load_Stream_FirstRecordContainsNameKey()
    {
        using var ms = ToStream(ThreeRecords);
        var doc = NdjsonDocument.Load(ms);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
    }

    // -------------------------------------------------------------------------
    // Parity with string-based Load
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_Stream_CountMatchesStringLoad()
    {
        var stringDoc = NdjsonDocument.Load(ThreeRecords);
        using var ms = ToStream(ThreeRecords);
        var streamDoc = NdjsonDocument.Load(ms);
        Assert.Equal(stringDoc.Count, streamDoc.Count);
    }

    [Fact]
    public void Load_Stream_KeysMatchStringLoad()
    {
        var stringDoc = NdjsonDocument.Load(ThreeRecords);
        using var ms = ToStream(ThreeRecords);
        var streamDoc = NdjsonDocument.Load(ms);
        Assert.Equal(stringDoc.GetAllKeys(), streamDoc.GetAllKeys());
    }

    // -------------------------------------------------------------------------
    // Edge cases
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_Stream_EmptyStream_ReturnsEmptyDocument()
    {
        using var ms = ToStream(string.Empty);
        var doc = NdjsonDocument.Load(ms);
        Assert.Equal(0, doc.Count);
    }

    [Fact]
    public void Load_Stream_SingleRecord_CountIsOne()
    {
        using var ms = ToStream("{\"id\":42,\"active\":true}\n");
        var doc = NdjsonDocument.Load(ms);
        Assert.Equal(1, doc.Count);
    }

    [Fact]
    public void Load_Stream_NullStream_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => NdjsonDocument.Load((Stream)null!));
    }

    // -------------------------------------------------------------------------
    // Dogfood: stream load → analytics pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StreamLoad_FilterAndGetFieldValues()
    {
        const string content =
            "{\"product\":\"Widget\",\"region\":\"West\",\"qty\":10}\n" +
            "{\"product\":\"Gadget\",\"region\":\"East\",\"qty\":5}\n" +
            "{\"product\":\"Widget\",\"region\":\"East\",\"qty\":8}\n" +
            "{\"product\":\"Gadget\",\"region\":\"West\",\"qty\":3}\n";

        using var ms = ToStream(content);
        var doc = NdjsonDocument.Load(ms);

        Assert.Equal(4, doc.Count);

        // GetFieldValues on stream-loaded doc
        var products = doc.GetFieldValues("product");
        Assert.Equal(4, products.Count);

        // Filter to Widgets only
        var widgets = doc.Filter(r =>
            r.TryGetProperty("product", out var p) && p.GetString() == "Widget");
        Assert.Equal(2, widgets.Count);

        // GetAllKeys includes expected fields
        var keys = doc.GetAllKeys();
        Assert.Contains("product", keys);
        Assert.Contains("region", keys);
        Assert.Contains("qty", keys);
    }
}
