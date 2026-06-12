using System.Text.Json;
using FormatFactory.Ndjson;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

public class NdjsonCsvExporterTests
{
    [Fact]
    public void Export_SimpleRecords_ProducesValidCsv()
    {
        var doc = NdjsonDocument.Load(
            "{\"name\":\"Alice\",\"age\":30}\n" +
            "{\"name\":\"Bob\",\"age\":25}\n");

        string csv = NdjsonCsvExporter.Export(doc);

        var lines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(3, lines.Length); // header + 2 data rows

        Assert.Equal("name,age", lines[0]);
        Assert.Equal("Alice,30", lines[1]);
        Assert.Equal("Bob,25", lines[2]);
    }

    [Fact]
    public void Export_MissingKeys_ProducesEmptyFields()
    {
        var doc = NdjsonDocument.Load(
            "{\"name\":\"Alice\",\"age\":30}\n" +
            "{\"name\":\"Bob\",\"city\":\"NYC\"}\n");

        string csv = NdjsonCsvExporter.Export(doc);

        var lines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(3, lines.Length);

        // Header should have all three keys
        Assert.Equal("name,age,city", lines[0]);

        // Alice has no city
        Assert.Equal("Alice,30,", lines[1]);

        // Bob has no age
        Assert.Equal("Bob,,NYC", lines[2]);
    }

    [Fact]
    public void Export_EmptyDocument_ReturnsEmpty()
    {
        var doc = NdjsonDocument.Load("");
        string csv = NdjsonCsvExporter.Export(doc);
        Assert.Equal(string.Empty, csv);
    }

    [Fact]
    public void Export_ValuesWithCommas_AreQuoted()
    {
        var doc = NdjsonDocument.Load("{\"desc\":\"hello, world\"}\n");
        string csv = NdjsonCsvExporter.Export(doc);

        var lines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(2, lines.Length);
        Assert.Equal("desc", lines[0]);
        Assert.Equal("\"hello, world\"", lines[1]);
    }

    [Fact]
    public void Export_NullValues_ProduceEmptyFields()
    {
        var doc = NdjsonDocument.Load("{\"a\":null,\"b\":\"ok\"}\n");
        string csv = NdjsonCsvExporter.Export(doc);

        var lines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal("a,b", lines[0]);
        Assert.Equal(",ok", lines[1]);
    }

    [Fact]
    public void Export_BooleanAndNumericValues_UseRawText()
    {
        var doc = NdjsonDocument.Load("{\"flag\":true,\"count\":42}\n");
        string csv = NdjsonCsvExporter.Export(doc);

        var lines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal("flag,count", lines[0]);
        Assert.Equal("true,42", lines[1]);
    }
}
