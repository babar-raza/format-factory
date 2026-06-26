// Tests for NdjsonReader.ReadRecords(Stream stream) stream-based NDJSON reading.
// Sprint: FORMAT-FACTORY-NDJSON-R133-20260627
// Ledger: R133-GOVERNED-DOTNET-NDJSON-STREAM-READRECORDS-001

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R133: Tests for NdjsonReader.ReadRecords(Stream stream) — stream-based NDJSON parsing.
/// Returns a List of JsonElement where each element is one parsed JSON object.
/// Null stream throws ArgumentNullException. Empty stream returns empty list.
/// Each record is a valid JSON object (ValueKind=Object). Stream result count
/// matches string-based ReadRecords(string) for the same content. Multi-record
/// stream returns all records. Field values accessible from stream-parsed records.
/// Covers: non-null result; non-empty result; record count matches string parity;
/// null stream throws ArgumentNullException; empty stream returns empty list;
/// records have ValueKind=Object; name field accessible; multi-record stream;
/// dogfood WriteRecords → Stream → ReadRecords(Stream) roundtrip.
/// </summary>
public class NdjsonR133StreamReadRecordsTests
{
    private static Stream ToStream(string content) =>
        new MemoryStream(Encoding.UTF8.GetBytes(content));

    // -------------------------------------------------------------------------
    // Basic stream reading
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRecords_ValidStream_ReturnsNonNull()
    {
        using var stream = ToStream("{\"name\":\"Alice\"}");
        var records = NdjsonReader.ReadRecords(stream);
        Assert.NotNull(records);
    }

    [Fact]
    public void ReadRecords_ValidStream_ReturnsNonEmptyList()
    {
        using var stream = ToStream("{\"name\":\"Alice\"}\n{\"name\":\"Bob\"}");
        var records = NdjsonReader.ReadRecords(stream);
        Assert.NotEmpty(records);
    }

    [Fact]
    public void ReadRecords_MultipleRecords_CountCorrect()
    {
        const string ndjson =
            "{\"name\":\"Alice\",\"score\":95}\n" +
            "{\"name\":\"Bob\",\"score\":80}\n" +
            "{\"name\":\"Carol\",\"score\":88}";
        using var stream = ToStream(ndjson);
        var records = NdjsonReader.ReadRecords(stream);
        Assert.Equal(3, records.Count);
    }

    [Fact]
    public void ReadRecords_EachRecord_IsJsonObject()
    {
        const string ndjson = "{\"x\":1}\n{\"y\":2}";
        using var stream = ToStream(ndjson);
        var records = NdjsonReader.ReadRecords(stream);
        foreach (var rec in records)
        {
            Assert.Equal(JsonValueKind.Object, rec.ValueKind);
        }
    }

    [Fact]
    public void ReadRecords_FieldValues_Accessible()
    {
        using var stream = ToStream("{\"city\":\"London\",\"pop\":9000000}");
        var records = NdjsonReader.ReadRecords(stream);
        Assert.Equal(1, records.Count);
        Assert.Equal("London",  records[0].GetProperty("city").GetString());
        Assert.Equal(9000000,   records[0].GetProperty("pop").GetInt32());
    }

    // -------------------------------------------------------------------------
    // Error guards
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRecords_NullStream_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            NdjsonReader.ReadRecords((Stream)null!));
    }

    [Fact]
    public void ReadRecords_EmptyStream_ReturnsEmptyList()
    {
        using var stream = ToStream(string.Empty);
        var records = NdjsonReader.ReadRecords(stream);
        Assert.Empty(records);
    }

    // -------------------------------------------------------------------------
    // Parity with ReadRecords(string)
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRecords_Stream_ParityWithStringOverload()
    {
        const string ndjson =
            "{\"product\":\"Widget\",\"revenue\":1000}\n" +
            "{\"product\":\"Gadget\",\"revenue\":800}";

        var fromString = NdjsonReader.ReadRecords(ndjson);
        using var stream = ToStream(ndjson);
        var fromStream = NdjsonReader.ReadRecords(stream);

        Assert.Equal(fromString.Count, fromStream.Count);
        for (var i = 0; i < fromString.Count; i++)
        {
            var strProduct    = fromString[i].GetProperty("product").GetString();
            var streamProduct = fromStream[i].GetProperty("product").GetString();
            Assert.Equal(strProduct, streamProduct);
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood: NdjsonWriter.WriteRecords → MemoryStream → ReadRecords(Stream) roundtrip
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_WriteRecords_ThenStreamReadRecords_Roundtrip()
    {
        var records = new object[]
        {
            new { name = "Alice", score = 95, active = true },
            new { name = "Bob",   score = 80, active = false },
            new { name = "Carol", score = 88, active = true },
        };

        // Serialize to NDJSON string
        var ndjson = NdjsonWriter.WriteRecords(records);

        // Parse via stream overload
        using var stream = ToStream(ndjson);
        var parsed = NdjsonReader.ReadRecords(stream);

        Assert.Equal(records.Length, parsed.Count);
        Assert.Equal("Alice", parsed[0].GetProperty("name").GetString());
        Assert.Equal(80,      parsed[1].GetProperty("score").GetInt32());
        Assert.True(parsed[2].GetProperty("active").GetBoolean());
    }
}
