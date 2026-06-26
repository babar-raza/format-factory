// Tests for NdjsonDocument.ToNdjson, LoadStream, NdjsonWriter deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R188

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R188: Tests for NdjsonDocument.ToNdjson, LoadStream, NdjsonWriter deeper coverage.
/// ToNdjson(): serializes the document back to NDJSON string format.
/// LoadStream(stream): loads a document from a stream.
/// NdjsonWriter.WriteRecords(records, path): writes records to NDJSON file.
/// Covers: ToNdjson non-null; ToNdjson non-empty; ToNdjson contains field names;
/// ToNdjson line count equals record count; ToNdjson after Filter smaller;
/// ToNdjson after AppendRecord contains new record;
/// LoadStream non-null; LoadStream count matches; LoadStream data accessible;
/// LoadStream after ToNdjson bytes round-trip;
/// NdjsonWriter.WriteRecords creates file; WriteRecords file parseable;
/// NdjsonWriter.WriteToString non-null and parseable;
/// dogfood LoadContent->ToNdjson->WriteRecords->LoadFile->LoadStream->Verify pipeline.
/// </summary>
public class NdjsonR188ToNdjsonAndLoadStreamDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string Content =
        "{\"Name\":\"Alice\",\"Dept\":\"Eng\",\"Score\":92}\n" +
        "{\"Name\":\"Bob\",\"Dept\":\"Finance\",\"Score\":85}\n" +
        "{\"Name\":\"Carol\",\"Dept\":\"Eng\",\"Score\":78}";

    public NdjsonR188ToNdjsonAndLoadStreamDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR188_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // ToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ToNdjson_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        Assert.NotNull(doc.ToNdjson());
    }

    [Fact]
    public void ToNdjson_NonEmpty()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        Assert.NotEmpty(doc.ToNdjson());
    }

    [Fact]
    public void ToNdjson_ContainsFieldNames()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var ndjson = doc.ToNdjson();
        Assert.Contains("Name", ndjson);
        Assert.Contains("Dept", ndjson);
    }

    [Fact]
    public void ToNdjson_ContainsDataValues()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var ndjson = doc.ToNdjson();
        Assert.Contains("Alice", ndjson);
        Assert.Contains("Finance", ndjson);
    }

    [Fact]
    public void ToNdjson_LineCountEqualsRecordCount()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var ndjson = doc.ToNdjson().TrimEnd('\n');
        var lines = ndjson.Split('\n');
        Assert.Equal(doc.Count, lines.Length);
    }

    [Fact]
    public void ToNdjson_AfterFilter_Smaller()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var full = doc.ToNdjson();
        var engOnly = doc.Filter(r => r.GetField("Dept")?.ToString() == "Eng");
        var filtered = engOnly.ToNdjson();
        Assert.True(filtered.Length < full.Length);
    }

    [Fact]
    public void ToNdjson_AfterAppendRecord_ContainsNewRecord()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var newRecord = new Dictionary<string, object?> { ["Name"] = "Dave", ["Dept"] = "HR", ["Score"] = 91 };
        var updated = doc.AppendRecord(newRecord);
        var ndjson = updated.ToNdjson();
        Assert.Contains("Dave", ndjson);
        Assert.Contains("HR", ndjson);
    }

    [Fact]
    public void ToNdjson_RoundTrip_SameCount()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var ndjson = doc.ToNdjson();
        var reloaded = NdjsonDocument.LoadContent(ndjson);
        Assert.Equal(doc.Count, reloaded.Count);
    }

    // -------------------------------------------------------------------------
    // LoadStream
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_NonNull()
    {
        using var ms = new MemoryStream(System.Text.Encoding.UTF8.GetBytes(Content));
        Assert.NotNull(NdjsonDocument.LoadStream(ms));
    }

    [Fact]
    public void LoadStream_CountMatches()
    {
        using var ms = new MemoryStream(System.Text.Encoding.UTF8.GetBytes(Content));
        var doc = NdjsonDocument.LoadStream(ms);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void LoadStream_DataAccessible()
    {
        using var ms = new MemoryStream(System.Text.Encoding.UTF8.GetBytes(Content));
        var doc = NdjsonDocument.LoadStream(ms);
        Assert.Equal("Alice", doc.RecordAt(0).GetField("Name")?.ToString());
    }

    [Fact]
    public void LoadStream_MatchesLoadContent()
    {
        var doc1 = NdjsonDocument.LoadContent(Content);
        using var ms = new MemoryStream(System.Text.Encoding.UTF8.GetBytes(Content));
        var doc2 = NdjsonDocument.LoadStream(ms);
        Assert.Equal(doc1.Count, doc2.Count);
    }

    [Fact]
    public void LoadStream_FromToNdjsonBytes_RoundTrip()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var ndjson = doc.ToNdjson();
        using var ms = new MemoryStream(System.Text.Encoding.UTF8.GetBytes(ndjson));
        var reloaded = NdjsonDocument.LoadStream(ms);
        Assert.Equal(doc.Count, reloaded.Count);
    }

    // -------------------------------------------------------------------------
    // NdjsonWriter
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonWriter_WriteToString_NonNull()
    {
        var records = new[]
        {
            new Dictionary<string, object?> { ["A"] = 1, ["B"] = "x" },
            new Dictionary<string, object?> { ["A"] = 2, ["B"] = "y" }
        };
        var result = NdjsonWriter.WriteToString(records);
        Assert.NotNull(result);
    }

    [Fact]
    public void NdjsonWriter_WriteToString_Parseable()
    {
        var records = new[]
        {
            new Dictionary<string, object?> { ["Name"] = "Test", ["Value"] = 42 }
        };
        var result = NdjsonWriter.WriteToString(records);
        var doc = NdjsonDocument.LoadContent(result);
        Assert.Equal(1, doc.Count);
    }

    [Fact]
    public void NdjsonWriter_WriteRecords_CreatesFile()
    {
        var records = new[]
        {
            new Dictionary<string, object?> { ["Name"] = "Alice", ["Score"] = 92 }
        };
        var path = TempFile("writer.ndjson");
        NdjsonWriter.WriteRecords(records, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void NdjsonWriter_WriteRecords_FileParseable()
    {
        var records = new[]
        {
            new Dictionary<string, object?> { ["Name"] = "Bob", ["Score"] = 85 },
            new Dictionary<string, object?> { ["Name"] = "Carol", ["Score"] = 78 }
        };
        var path = TempFile("writer2.ndjson");
        NdjsonWriter.WriteRecords(records, path);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(2, doc.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_ToNdjson_WriteRecords_LoadFile_LoadStream_Verify_Pipeline()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        Assert.Equal(3, doc.Count);

        // ToNdjson
        var ndjson = doc.ToNdjson();
        Assert.NotEmpty(ndjson);
        Assert.Contains("Alice", ndjson);

        // LoadContent from ToNdjson (round-trip)
        var roundTripped = NdjsonDocument.LoadContent(ndjson);
        Assert.Equal(3, roundTripped.Count);

        // WriteRecords to file
        var records = new List<Dictionary<string, object?>>();
        for (var i = 0; i < doc.Count; i++)
        {
            var rec = doc.RecordAt(i);
            records.Add(new Dictionary<string, object?>
            {
                ["Name"] = rec.GetField("Name"),
                ["Dept"] = rec.GetField("Dept"),
                ["Score"] = rec.GetField("Score")
            });
        }
        var path = TempFile("dogfood.ndjson");
        NdjsonWriter.WriteRecords(records, path);
        Assert.True(File.Exists(path));

        // LoadFile
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, loaded.Count);
        Assert.Equal("Alice", loaded.RecordAt(0).GetField("Name")?.ToString());

        // LoadStream
        using var ms = new MemoryStream(File.ReadAllBytes(path));
        var fromStream = NdjsonDocument.LoadStream(ms);
        Assert.Equal(3, fromStream.Count);

        // Filter and ToNdjson
        var engOnly = loaded.Filter(r => r.GetField("Dept")?.ToString() == "Eng");
        Assert.Equal(2, engOnly.Count);
        var engNdjson = engOnly.ToNdjson();
        Assert.Contains("Alice", engNdjson);
        Assert.DoesNotContain("Finance", engNdjson);
    }
}
