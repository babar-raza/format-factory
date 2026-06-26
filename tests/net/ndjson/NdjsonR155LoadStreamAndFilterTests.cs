// Tests for NdjsonDocument.Load(Stream), Filter composition, and SaveToFile.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R155

using System;
using System.IO;
using System.Text;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R155: Tests for NdjsonDocument.Load(Stream), Filter composition, and multi-step pipelines.
/// Load(Stream): loads NDJSON from memory stream.
/// Filter: chains multiple filters for compound queries.
/// IsUniformSchema: consistency after filter composition.
/// ToNdjson + SaveToFile: double-write pattern.
/// Covers: Load(Stream) 3 records count; Load(Stream) GetAllKeys;
/// Load(Stream) GetFieldValues; Load(Stream) Filter works;
/// Filter(active=true) count; Filter(score>85) count;
/// Compound filter (active AND score>85) count; IsUniformSchema after compound filter;
/// GetFieldValues after compound filter; SaveToFile from compound filter;
/// LoadFile after SaveToFile count matches; ToNdjson then LoadContent round-trip;
/// dogfood Stream->CompoundFilter->SaveToFile->LoadFile pipeline.
/// </summary>
public class NdjsonR155LoadStreamAndFilterTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR155LoadStreamAndFilterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR155_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string FiveRecords =
        "{\"name\":\"Alice\",\"score\":92,\"active\":true,\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Bob\",\"score\":78,\"active\":false,\"dept\":\"Finance\"}\n" +
        "{\"name\":\"Carol\",\"score\":88,\"active\":true,\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Dave\",\"score\":65,\"active\":false,\"dept\":\"Finance\"}\n" +
        "{\"name\":\"Eve\",\"score\":95,\"active\":true,\"dept\":\"Eng\"}";

    private static NdjsonDocument LoadStream() =>
        NdjsonDocument.Load(new MemoryStream(Encoding.UTF8.GetBytes(FiveRecords)));

    // -------------------------------------------------------------------------
    // Load(Stream)
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_FiveRecords_CountIsFive()
    {
        var doc = LoadStream();
        Assert.Equal(5, doc.Count);
    }

    [Fact]
    public void LoadStream_GetAllKeys_HasFourKeys()
    {
        var doc = LoadStream();
        var keys = doc.GetAllKeys();
        Assert.Equal(4, keys.Count);
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
        Assert.Contains("active", keys);
        Assert.Contains("dept", keys);
    }

    [Fact]
    public void LoadStream_GetFieldValues_ContainsNames()
    {
        var doc = LoadStream();
        var names = doc.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Eve", names);
    }

    // -------------------------------------------------------------------------
    // Single filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_Active_CountIsThree()
    {
        var doc = LoadStream();
        var active = doc.Filter(el =>
            el.TryGetProperty("active", out var a) && a.ValueKind == JsonValueKind.True);
        Assert.Equal(3, active.Count); // Alice, Carol, Eve
    }

    [Fact]
    public void Filter_ScoreAbove85_CountIsThree()
    {
        var doc = LoadStream();
        var high = doc.Filter(el =>
            el.TryGetProperty("score", out var s) && s.GetDouble() > 85);
        Assert.Equal(3, high.Count); // Alice(92), Carol(88), Eve(95)
    }

    // -------------------------------------------------------------------------
    // Compound filter
    // -------------------------------------------------------------------------

    [Fact]
    public void CompoundFilter_ActiveAndScoreAbove85_CountIsThree()
    {
        var doc = LoadStream();
        var result = doc.Filter(el =>
            el.TryGetProperty("active", out var a) &&
            a.ValueKind == JsonValueKind.True &&
            el.TryGetProperty("score", out var s) &&
            s.GetDouble() > 85);
        Assert.Equal(3, result.Count); // Alice(92), Carol(88), Eve(95)
    }

    [Fact]
    public void CompoundFilter_EngAndActive_CountIsThree()
    {
        var doc = LoadStream();
        var result = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) &&
            d.GetString() == "Eng" &&
            el.TryGetProperty("active", out var a) &&
            a.ValueKind == JsonValueKind.True);
        Assert.Equal(3, result.Count); // Alice, Carol, Eve (all Eng active)
    }

    [Fact]
    public void CompoundFilter_IsUniformSchema()
    {
        var doc = LoadStream();
        var result = doc.Filter(el =>
            el.TryGetProperty("active", out var a) && a.ValueKind == JsonValueKind.True);
        Assert.True(result.IsUniformSchema());
    }

    [Fact]
    public void CompoundFilter_GetFieldValues()
    {
        var doc = LoadStream();
        var eng = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var names = eng.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Eve", names);
        Assert.DoesNotContain("Bob", names);
    }

    // -------------------------------------------------------------------------
    // SaveToFile from compound filter
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_AfterCompoundFilter_CountMatches()
    {
        var doc = LoadStream();
        var active = doc.Filter(el =>
            el.TryGetProperty("active", out var a) && a.ValueKind == JsonValueKind.True);

        var path = TempFile("active.ndjson");
        active.SaveToFile(path);

        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, reloaded.Count);
    }

    // -------------------------------------------------------------------------
    // ToNdjson then LoadContent round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void ToNdjson_LoadContent_RoundTrip()
    {
        var doc = LoadStream();
        var ndjson = doc.ToNdjson();
        var reloaded = NdjsonDocument.LoadContent(ndjson);
        Assert.Equal(doc.Count, reloaded.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Stream->CompoundFilter->SaveToFile->LoadFile pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_StreamCompoundFilterSaveLoadPipeline()
    {
        // Load from stream
        var doc = LoadStream();
        Assert.Equal(5, doc.Count);

        // Compound filter: Eng dept AND active AND score > 85
        var result = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng" &&
            el.TryGetProperty("active", out var a) && a.ValueKind == JsonValueKind.True &&
            el.TryGetProperty("score", out var s) && s.GetDouble() > 85);
        Assert.Equal(3, result.Count); // Alice(92), Carol(88), Eve(95) — all Eng+active+>85

        // Serialize and save
        var path = TempFile("eng_active.ndjson");
        result.SaveToFile(path);
        Assert.True(File.Exists(path));

        // Reload and verify
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, reloaded.Count);
        Assert.True(reloaded.IsUniformSchema());

        var names = reloaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Eve", names);
        Assert.DoesNotContain("Bob", names);
        Assert.DoesNotContain("Dave", names);
    }
}
