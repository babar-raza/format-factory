// Tests for NdjsonDocument.Load(stream), MaxFileSizeBytes deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R180

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R180: Tests for NdjsonDocument.Load(stream), MaxFileSizeBytes deeper coverage.
/// NdjsonDocument.Load(stream): loads document from a Stream.
/// NdjsonDocument.MaxFileSizeBytes: configurable limit for maximum file size.
/// Covers: Load(stream) non-null; Load(stream) Count correct;
/// Load(stream) records accessible; Load(stream) IsUniformSchema;
/// Load(stream) then GetFieldValues; Load(stream) from FileStream;
/// Load(stream) from MemoryStream; MaxFileSizeBytes default positive;
/// MaxFileSizeBytes settable; Load(stream) from file bytes;
/// multiple Load(stream) calls independent;
/// dogfood LoadContent->ToNdjson->MemoryStream->Load(stream)->verify round-trip.
/// </summary>
public class NdjsonR180LoadStreamAndMaxSizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string ThreeRecordNdjson =
        "{\"id\":1,\"name\":\"Alice\",\"dept\":\"Eng\"}\n" +
        "{\"id\":2,\"name\":\"Bob\",\"dept\":\"Finance\"}\n" +
        "{\"id\":3,\"name\":\"Carol\",\"dept\":\"Eng\"}";

    public NdjsonR180LoadStreamAndMaxSizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR180_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private MemoryStream ToMemoryStream(string content) =>
        new MemoryStream(Encoding.UTF8.GetBytes(content));

    // -------------------------------------------------------------------------
    // Load(stream) from MemoryStream
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_NonNull()
    {
        using var ms = ToMemoryStream(ThreeRecordNdjson);
        var doc = NdjsonDocument.Load(ms);
        Assert.NotNull(doc);
    }

    [Fact]
    public void LoadStream_Count_Correct()
    {
        using var ms = ToMemoryStream(ThreeRecordNdjson);
        var doc = NdjsonDocument.Load(ms);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void LoadStream_Records_Accessible()
    {
        using var ms = ToMemoryStream(ThreeRecordNdjson);
        var doc = NdjsonDocument.Load(ms);
        Assert.NotNull(doc.RecordAt(0));
    }

    [Fact]
    public void LoadStream_IsUniformSchema_True()
    {
        using var ms = ToMemoryStream(ThreeRecordNdjson);
        var doc = NdjsonDocument.Load(ms);
        Assert.True(doc.IsUniformSchema);
    }

    [Fact]
    public void LoadStream_GetFieldValues_Correct()
    {
        using var ms = ToMemoryStream(ThreeRecordNdjson);
        var doc = NdjsonDocument.Load(ms);
        var names = doc.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void LoadStream_TryGetValue_FirstRecord_Correct()
    {
        using var ms = ToMemoryStream(ThreeRecordNdjson);
        var doc = NdjsonDocument.Load(ms);
        Assert.True(doc.RecordAt(0).TryGetValue("name", out var val));
        Assert.Equal("Alice", val);
    }

    [Fact]
    public void LoadStream_MultipleIndependent_CorrectCounts()
    {
        using var ms1 = ToMemoryStream(ThreeRecordNdjson);
        using var ms2 = ToMemoryStream("{\"x\":1}\n{\"x\":2}");
        var doc1 = NdjsonDocument.Load(ms1);
        var doc2 = NdjsonDocument.Load(ms2);
        Assert.Equal(3, doc1.Count);
        Assert.Equal(2, doc2.Count);
    }

    // -------------------------------------------------------------------------
    // Load(stream) from FileStream
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_FromFileStream_NonNull()
    {
        var path = TempFile("stream.ndjson");
        File.WriteAllText(path, ThreeRecordNdjson, Encoding.UTF8);
        using var fs = File.OpenRead(path);
        var doc = NdjsonDocument.Load(fs);
        Assert.NotNull(doc);
    }

    [Fact]
    public void LoadStream_FromFileStream_CountCorrect()
    {
        var path = TempFile("fs_count.ndjson");
        File.WriteAllText(path, ThreeRecordNdjson, Encoding.UTF8);
        using var fs = File.OpenRead(path);
        var doc = NdjsonDocument.Load(fs);
        Assert.Equal(3, doc.Count);
    }

    // -------------------------------------------------------------------------
    // MaxFileSizeBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void MaxFileSizeBytes_Default_Positive()
    {
        Assert.True(NdjsonDocument.MaxFileSizeBytes > 0);
    }

    [Fact]
    public void MaxFileSizeBytes_Settable()
    {
        var original = NdjsonDocument.MaxFileSizeBytes;
        NdjsonDocument.MaxFileSizeBytes = original * 2;
        Assert.Equal(original * 2, NdjsonDocument.MaxFileSizeBytes);
        NdjsonDocument.MaxFileSizeBytes = original; // restore
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_ToNdjson_MemoryStream_Load_VerifyRoundTrip_Pipeline()
    {
        // LoadContent
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        Assert.Equal(3, doc.Count);

        // ToNdjson
        var ndjson = doc.ToNdjson();
        Assert.NotNull(ndjson);
        Assert.Contains("Alice", ndjson);

        // MemoryStream from ToNdjson output
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(ndjson));
        var fromStream = NdjsonDocument.Load(ms);
        Assert.Equal(3, fromStream.Count);

        // GetFieldValues from stream-loaded doc
        var names = fromStream.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);

        // IsUniformSchema
        Assert.True(fromStream.IsUniformSchema);

        // GetAllKeys
        var keys = fromStream.GetAllKeys();
        Assert.Contains("id", keys);
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);

        // Filter from stream-loaded doc
        var eng = fromStream.Filter(r => r.TryGetValue("dept", out var d) && d == "Eng");
        Assert.Equal(2, eng.Count);

        // FileStream round-trip
        var path = TempFile("dogfood.ndjson");
        File.WriteAllText(path, ndjson, Encoding.UTF8);
        using var fs = File.OpenRead(path);
        var fromFile = NdjsonDocument.Load(fs);
        Assert.Equal(3, fromFile.Count);
    }
}
