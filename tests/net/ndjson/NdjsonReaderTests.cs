using System.Text;
using System.Text.Json;
using FormatFactory.Ndjson;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

public class NdjsonReaderTests
{
    [Fact]
    public void ReadRecords_ValidNdjson_ParsesAllRecords()
    {
        var input = "{\"name\":\"Alice\",\"age\":30}\n{\"name\":\"Bob\",\"age\":25}\n";
        var records = NdjsonReader.ReadRecords(input);

        Assert.Equal(2, records.Count);
        Assert.Equal("Alice", records[0].GetProperty("name").GetString());
        Assert.Equal(30, records[0].GetProperty("age").GetInt32());
        Assert.Equal("Bob", records[1].GetProperty("name").GetString());
        Assert.Equal(25, records[1].GetProperty("age").GetInt32());
    }

    [Fact]
    public void ReadRecords_EmptyInput_ReturnsEmptyList()
    {
        var records = NdjsonReader.ReadRecords("");
        Assert.Empty(records);
    }

    [Fact]
    public void ReadRecords_BlankLines_AreSkipped()
    {
        var input = "{\"a\":1}\n\n\n{\"b\":2}\n\n";
        var records = NdjsonReader.ReadRecords(input);

        Assert.Equal(2, records.Count);
        Assert.Equal(1, records[0].GetProperty("a").GetInt32());
        Assert.Equal(2, records[1].GetProperty("b").GetInt32());
    }

    [Fact]
    public void ReadRecords_SingleRecord_Works()
    {
        var input = "{\"key\":\"value\"}\n";
        var records = NdjsonReader.ReadRecords(input);

        Assert.Single(records);
        Assert.Equal("value", records[0].GetProperty("key").GetString());
    }

    [Fact]
    public void ReadRecords_InvalidJsonLine_ThrowsNdjsonException()
    {
        var input = "{\"valid\":true}\nnot json\n";

        var ex = Assert.Throws<NdjsonException>(() => NdjsonReader.ReadRecords(input));
        Assert.Contains("line 2", ex.Message);
    }

    [Fact]
    public void ReadRecords_ExceedsSizeGuard_ThrowsNdjsonException()
    {
        // Create a string that exceeds 64 MB
        var huge = new string('x', (int)(NdjsonReader.MaxSize + 1));

        var ex = Assert.Throws<NdjsonException>(() => NdjsonReader.ReadRecords(huge));
        Assert.Contains("exceeds maximum", ex.Message);
    }

    [Fact]
    public void ReadRecords_FromStream_Works()
    {
        var input = "{\"x\":1}\n{\"y\":2}\n";
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(input));

        var records = NdjsonReader.ReadRecords(stream);
        Assert.Equal(2, records.Count);
    }

    [Fact]
    public void ReadRecordsFromFile_ValidFile_Works()
    {
        var path = Path.Combine(Path.GetTempPath(), $"ndjson_reader_test_{Guid.NewGuid()}.ndjson");
        try
        {
            File.WriteAllText(path, "{\"id\":1}\n{\"id\":2}\n", new UTF8Encoding(false));
            var records = NdjsonReader.ReadRecordsFromFile(path);

            Assert.Equal(2, records.Count);
            Assert.Equal(1, records[0].GetProperty("id").GetInt32());
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ReadRecordsFromFile_MissingFile_ThrowsNdjsonException()
    {
        var ex = Assert.Throws<NdjsonException>(() => NdjsonReader.ReadRecordsFromFile("/nonexistent/file.ndjson"));
        Assert.Contains("not found", ex.Message);
    }

    [Fact]
    public void ReadRecords_SingleRecordNoTrailingNewline_Works()
    {
        var input = "{\"key\":\"value\"}";
        var records = NdjsonReader.ReadRecords(input);
        Assert.Single(records);
    }
}
