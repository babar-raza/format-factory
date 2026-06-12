using System.Text.Json;
using FormatFactory.Ndjson;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

public class NdjsonWriterTests
{
    [Fact]
    public void WriteRecords_Roundtrip_PreservesData()
    {
        var records = new object[]
        {
            new { name = "Alice", age = 30 },
            new { name = "Bob", age = 25 },
        };

        string ndjson = NdjsonWriter.WriteRecords(records);

        // Verify it ends with newline
        Assert.EndsWith("\n", ndjson);

        // Parse back and verify
        var parsed = NdjsonReader.ReadRecords(ndjson);
        Assert.Equal(2, parsed.Count);
        Assert.Equal("Alice", parsed[0].GetProperty("name").GetString());
        Assert.Equal(25, parsed[1].GetProperty("age").GetInt32());
    }

    [Fact]
    public void WriteRecords_EmptyCollection_ReturnsEmpty()
    {
        string ndjson = NdjsonWriter.WriteRecords(Array.Empty<object>());
        Assert.Equal("", ndjson);
    }

    [Fact]
    public void WriteRecords_EachRecordOnSingleLine()
    {
        var records = new object[]
        {
            new { a = 1 },
            new { b = 2 },
        };

        string ndjson = NdjsonWriter.WriteRecords(records);
        var lines = ndjson.Split('\n', StringSplitOptions.RemoveEmptyEntries);

        Assert.Equal(2, lines.Length);
        // Each line should be valid JSON
        foreach (var line in lines)
        {
            using var doc = JsonDocument.Parse(line);
            Assert.NotNull(doc);
        }
    }

    [Fact]
    public void WriteRecordsToFile_WritesAndReadsBack()
    {
        var path = Path.Combine(Path.GetTempPath(), $"ndjson_writer_test_{Guid.NewGuid()}.ndjson");
        try
        {
            var records = new object[]
            {
                new { id = 1, value = "one" },
                new { id = 2, value = "two" },
            };

            NdjsonWriter.WriteRecordsToFile(records, path);

            Assert.True(File.Exists(path));

            var parsed = NdjsonReader.ReadRecordsFromFile(path);
            Assert.Equal(2, parsed.Count);
            Assert.Equal("one", parsed[0].GetProperty("value").GetString());
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void WriteRecordsToFile_EmptyPath_ThrowsNdjsonException()
    {
        Assert.Throws<NdjsonException>(() => NdjsonWriter.WriteRecordsToFile(new object[] { new { a = 1 } }, ""));
    }

    [Fact]
    public void WriteRecords_UsesLfLineEndings()
    {
        var records = new object[] { new { x = 1 } };
        string ndjson = NdjsonWriter.WriteRecords(records);

        Assert.DoesNotContain("\r\n", ndjson);
        Assert.Contains("\n", ndjson);
    }
}
