// Tests for NdjsonRecord typed wrapper (QF-3-003, TC-QF-R-008)

using System;
using System.IO;
using System.Text.Json;
using FormatFactory.Ndjson;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

public class NdjsonRecordTypedTests
{
    private const string SampleNdjson =
        "{\"id\":1,\"name\":\"Alice\",\"active\":true}\n" +
        "{\"id\":2,\"name\":\"Bob\",\"active\":false}\n" +
        "{\"id\":3,\"name\":\"Carol\",\"active\":true}\n";

    [Fact]
    public void TypedRecords_ReturnsCorrectCount()
    {
        var doc = NdjsonDocument.LoadFromContent(SampleNdjson);
        var typed = doc.TypedRecords;
        Assert.Equal(3, typed.Count);
    }

    [Fact]
    public void TypedRecord_Fields_ContainsExpectedKeys()
    {
        var doc = NdjsonDocument.LoadFromContent(SampleNdjson);
        var record = doc.TypedRecords[0];
        Assert.Contains("id", record.Keys);
        Assert.Contains("name", record.Keys);
        Assert.Contains("active", record.Keys);
    }

    [Fact]
    public void TypedRecord_TryGetValue_ReturnsFieldValue()
    {
        var doc = NdjsonDocument.LoadFromContent(SampleNdjson);
        var record = doc.TypedRecords[0];
        Assert.True(record.TryGetValue("name", out var nameElement));
        Assert.Equal("Alice", nameElement.GetString());
    }

    [Fact]
    public void TypedRecord_Fields_IndexByKey_ReturnsJsonElement()
    {
        var doc = NdjsonDocument.LoadFromContent(SampleNdjson);
        var record = doc.TypedRecords[1];
        var idElement = record.Fields["id"];
        Assert.Equal(2, idElement.GetInt32());
    }

    [Fact]
    public void TypedRecord_RawElement_IsJsonElement()
    {
        var doc = NdjsonDocument.LoadFromContent(SampleNdjson);
        var record = doc.TypedRecords[0];
        Assert.Equal(JsonValueKind.Object, record.RawElement.ValueKind);
    }

    [Fact]
    public void NdjsonRecord_Constructor_DirectFromJsonElement()
    {
        using var jsonDoc = JsonDocument.Parse("{\"x\":42}");
        var record = new NdjsonRecord(jsonDoc.RootElement.Clone());
        Assert.True(record.TryGetValue("x", out var xElem));
        Assert.Equal(42, xElem.GetInt32());
    }
}
