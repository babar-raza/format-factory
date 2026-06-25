// Tests for NdjsonWriter.WriteRecords(IEnumerable<object>) serialization.
// Sprint: FORMAT-FACTORY-NDJSON-WRITE-RECORDS-20260626
// Ledger: R121-GOVERNED-DOTNET-NDJSON-WRITE-RECORDS-001

using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R121: NdjsonWriter.WriteRecords(IEnumerable{object}) serializes objects to NDJSON
/// text with one JSON object per line. The output is valid NDJSON — each line is
/// parseable JSON. WriteRecordsToFile(objects, path) persists to disk and can be
/// reloaded by NdjsonDocument.LoadFile. Property names and values are preserved.
/// </summary>
public class NdjsonR121WriteRecordsTests
{
    // ---- WriteRecords: basic output ----

    [Fact]
    public void WriteRecords_SingleObject_ProducesOutput()
    {
        var records = new object[] { new { name = "Alice", score = 90 } };
        var output  = NdjsonWriter.WriteRecords(records);
        Assert.False(string.IsNullOrWhiteSpace(output));
    }

    [Fact]
    public void WriteRecords_OutputContainsPropertyName()
    {
        var records = new object[] { new { city = "London" } };
        var output  = NdjsonWriter.WriteRecords(records);
        Assert.Contains("city", output);
    }

    [Fact]
    public void WriteRecords_OutputContainsPropertyValue()
    {
        var records = new object[] { new { city = "London" } };
        var output  = NdjsonWriter.WriteRecords(records);
        Assert.Contains("London", output);
    }

    [Fact]
    public void WriteRecords_MultipleObjects_AllValuesPresent()
    {
        var records = new object[]
        {
            new { name = "Alice" },
            new { name = "Bob" },
            new { name = "Carol" }
        };
        var output = NdjsonWriter.WriteRecords(records);
        Assert.Contains("Alice", output);
        Assert.Contains("Bob", output);
        Assert.Contains("Carol", output);
    }

    [Fact]
    public void WriteRecords_MultipleObjects_MultipleLines()
    {
        var records = new object[]
        {
            new { x = 1 },
            new { x = 2 },
            new { x = 3 }
        };
        var output = NdjsonWriter.WriteRecords(records);
        var lines  = output.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(3, lines.Length);
    }

    // ---- WriteRecords: each line is valid JSON ----

    [Fact]
    public void WriteRecords_EachLine_IsValidJson()
    {
        var records = new object[] { new { a = 1, b = "hello" }, new { a = 2, b = "world" } };
        var output  = NdjsonWriter.WriteRecords(records);
        foreach (var line in output.Split('\n', StringSplitOptions.RemoveEmptyEntries))
        {
            // Each line should parse as JSON without exception
            using var doc = JsonDocument.Parse(line);
            Assert.Equal(JsonValueKind.Object, doc.RootElement.ValueKind);
        }
    }

    // ---- WriteRecords: empty list ----

    [Fact]
    public void WriteRecords_EmptyList_DoesNotThrow()
    {
        var output = NdjsonWriter.WriteRecords(Array.Empty<object>());
        Assert.NotNull(output);
    }

    // ---- WriteRecordsToFile: round-trip ----

    [Fact]
    public void WriteRecordsToFile_CanReloadWithLoadFile()
    {
        var path = Path.GetTempFileName();
        try
        {
            var records = new object[]
            {
                new { product = "Widget", price = 9.99 },
                new { product = "Gadget", price = 24.99 }
            };
            NdjsonWriter.WriteRecordsToFile(records, path);

            var doc = NdjsonDocument.LoadFile(path);
            Assert.Equal(2, doc.Count);
        }
        finally
        {
            File.Delete(path);
        }
    }

    // ---- Dogfood: WriteRecords + reload + verify ----

    [Fact]
    public void DogfoodPipeline_WriteRecordsThenLoad_DataIntact()
    {
        var records = new object[]
        {
            new { name = "Alice", score = 92, pass = true },
            new { name = "Bob",   score = 68, pass = false },
            new { name = "Carol", score = 85, pass = true }
        };

        var ndjson = NdjsonWriter.WriteRecords(records);

        // Reload as NdjsonDocument
        var doc = NdjsonDocument.Load(ndjson);
        Assert.Equal(3, doc.Count);

        // Verify schema is uniform
        Assert.True(doc.IsUniformSchema());

        // Verify field values
        var names = doc.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }
}
