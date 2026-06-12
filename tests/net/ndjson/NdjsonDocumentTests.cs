using System.Text;
using System.Text.Json;
using FormatFactory.Ndjson;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

public class NdjsonDocumentTests
{
    [Fact]
    public void Load_CountsRecords()
    {
        var doc = NdjsonDocument.Load("{\"a\":1}\n{\"b\":2}\n{\"c\":3}\n");

        Assert.Equal(3, doc.Count);
        Assert.Equal(3, doc.Records.Count);
    }

    [Fact]
    public void Load_EmptyInput_ZeroCount()
    {
        var doc = NdjsonDocument.Load("");

        Assert.Equal(0, doc.Count);
        Assert.Empty(doc.Records);
    }

    [Fact]
    public void Roundtrip_LoadToNdjsonLoad()
    {
        var original = "{\"name\":\"Alice\",\"age\":30}\n{\"name\":\"Bob\",\"age\":25}\n";
        var doc1 = NdjsonDocument.Load(original);
        string serialized = doc1.ToNdjson();
        var doc2 = NdjsonDocument.Load(serialized);

        Assert.Equal(doc1.Count, doc2.Count);
        for (int i = 0; i < doc1.Count; i++)
        {
            Assert.Equal(
                doc1.Records[i].GetProperty("name").GetString(),
                doc2.Records[i].GetProperty("name").GetString());
            Assert.Equal(
                doc1.Records[i].GetProperty("age").GetInt32(),
                doc2.Records[i].GetProperty("age").GetInt32());
        }
    }

    [Fact]
    public void Load_FromStream()
    {
        var input = "{\"x\":42}\n";
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(input));

        var doc = NdjsonDocument.Load(stream);
        Assert.Equal(1, doc.Count);
        Assert.Equal(42, doc.Records[0].GetProperty("x").GetInt32());
    }

    [Fact]
    public void FileIO_SaveAndLoadFile()
    {
        var path = Path.Combine(Path.GetTempPath(), $"ndjson_doc_test_{Guid.NewGuid()}.ndjson");
        try
        {
            var doc1 = NdjsonDocument.Load("{\"id\":1}\n{\"id\":2}\n");
            doc1.SaveToFile(path);

            Assert.True(File.Exists(path));

            var doc2 = NdjsonDocument.LoadFile(path);
            Assert.Equal(2, doc2.Count);
            Assert.Equal(1, doc2.Records[0].GetProperty("id").GetInt32());
            Assert.Equal(2, doc2.Records[1].GetProperty("id").GetInt32());
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ToNdjson_EachRecordOnOwnLine()
    {
        var doc = NdjsonDocument.Load("{\"a\":1}\n{\"b\":2}\n");
        string output = doc.ToNdjson();

        var lines = output.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(2, lines.Length);
    }

    [Fact]
    public void SaveToFile_EmptyPath_Throws()
    {
        var doc = NdjsonDocument.Load("{\"a\":1}\n");
        Assert.Throws<NdjsonException>(() => doc.SaveToFile(""));
    }
}
