// Pilot A: NdjsonDocument.AddRecord() roundtrip tests
// Verifies PQ-029 fix: AddRecord(string) and AddRecord(JsonElement) mutate the document
// and the mutation is preserved after save+reload.

using System;
using System.IO;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

public class NdjsonAddRecordRoundtripTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonAddRecordRoundtripTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonAddRecord_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // AddRecord(string jsonString)
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRecord_String_IncreasesCount()
    {
        var doc = NdjsonDocument.LoadFromContent("{\"id\":1}");
        Assert.Equal(1, doc.Count);
        doc.AddRecord("{\"id\":2}");
        Assert.Equal(2, doc.Count);
    }

    [Fact]
    public void AddRecord_String_ValueAccessible()
    {
        var doc = NdjsonDocument.LoadFromContent("{\"x\":10}");
        doc.AddRecord("{\"x\":99}");
        var values = doc.GetFieldValues("x");
        Assert.Contains("10", values);
        Assert.Contains("99", values);
    }

    [Fact]
    public void AddRecord_NullString_Throws()
    {
        var doc = NdjsonDocument.LoadFromContent("{\"a\":1}");
        Assert.Throws<NdjsonException>(() => doc.AddRecord((string)null!));
    }

    [Fact]
    public void AddRecord_EmptyString_Throws()
    {
        var doc = NdjsonDocument.LoadFromContent("{\"a\":1}");
        Assert.Throws<NdjsonException>(() => doc.AddRecord(""));
    }

    [Fact]
    public void AddRecord_InvalidJson_Throws()
    {
        var doc = NdjsonDocument.LoadFromContent("{\"a\":1}");
        Assert.Throws<NdjsonException>(() => doc.AddRecord("{not valid json"));
    }

    // -------------------------------------------------------------------------
    // AddRecord(JsonElement)
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRecord_Element_IncreasesCount()
    {
        var doc = NdjsonDocument.LoadFromContent("{\"name\":\"Alice\"}");
        using var parsed = JsonDocument.Parse("{\"name\":\"Bob\"}");
        doc.AddRecord(parsed.RootElement.Clone());
        Assert.Equal(2, doc.Count);
    }

    // -------------------------------------------------------------------------
    // Roundtrip: AddRecord → SaveToFile → LoadFile → Assert
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRecord_Roundtrip_SaveAndReload_PreservesNewRecord()
    {
        // Load initial document
        var doc = NdjsonDocument.LoadFromContent("{\"name\":\"Alice\",\"score\":90}");

        // Add a new record via the new API
        doc.AddRecord("{\"name\":\"Bob\",\"score\":75}");
        Assert.Equal(2, doc.Count);

        // Save to temp file
        var path = TempFile("addrecord_roundtrip.ndjson");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // Reload from file
        var doc2 = NdjsonDocument.LoadFile(path);

        // Verify both records are present
        Assert.Equal(2, doc2.Count);
        var names = doc2.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        var scores = doc2.GetFieldValues("score");
        Assert.Contains("90", scores);
        Assert.Contains("75", scores);
    }

    [Fact]
    public void AddRecord_MultipleRecords_AllPersistedInRoundtrip()
    {
        var doc = NdjsonDocument.LoadFromContent("");
        doc.AddRecord("{\"k\":\"v1\"}");
        doc.AddRecord("{\"k\":\"v2\"}");
        doc.AddRecord("{\"k\":\"v3\"}");
        Assert.Equal(3, doc.Count);

        var path = TempFile("multi_roundtrip.ndjson");
        doc.SaveToFile(path);

        var doc2 = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, doc2.Count);
        var vals = doc2.GetFieldValues("k");
        Assert.Equal(new[] { "v1", "v2", "v3" }, vals);
    }
}
