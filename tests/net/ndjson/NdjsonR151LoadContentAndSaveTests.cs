// Tests for NdjsonDocument.LoadContent, Load(stream), SaveToFile, ToNdjson round-trip.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R151

using System;
using System.IO;
using System.Text;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R151: Tests for NdjsonDocument.LoadContent, Load(stream), SaveToFile, ToNdjson round-trip.
/// LoadContent(jsonlContent): alias for Load(string) — loads NDJSON from string.
/// Load(Stream stream): loads NDJSON from stream.
/// SaveToFile(path): persists records to file.
/// ToNdjson(): serializes to NDJSON string.
/// Covers: LoadContent count correct; LoadContent records accessible;
/// Load(stream) count equals Load(string); Load(stream) records have correct keys;
/// SaveToFile creates file; SaveToFile content contains records;
/// LoadFile after SaveToFile round-trip count; ToNdjson non-empty;
/// ToNdjson contains field values; Filter->ToNdjson excludes filtered records;
/// dogfood LoadContent->Filter->SaveToFile->LoadFile pipeline.
/// </summary>
public class NdjsonR151LoadContentAndSaveTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR151LoadContentAndSaveTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR151_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string ThreeRecords =
        "{\"name\":\"Alice\",\"score\":95,\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Bob\",\"score\":82,\"dept\":\"Finance\"}\n" +
        "{\"name\":\"Carol\",\"score\":88,\"dept\":\"Eng\"}";

    // -------------------------------------------------------------------------
    // LoadContent
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadContent_CountIsThree()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecords);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void LoadContent_RecordsAreAccessible()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecords);
        var first = doc.Records[0];
        Assert.True(first.TryGetProperty("name", out var name));
        Assert.Equal("Alice", name.GetString());
    }

    [Fact]
    public void LoadContent_AllKeysPresent()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecords);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
        Assert.Contains("dept", keys);
    }

    // -------------------------------------------------------------------------
    // Load(Stream)
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_CountMatchesString()
    {
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(ThreeRecords));
        var doc = NdjsonDocument.Load(stream);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void LoadStream_RecordsHaveCorrectKeys()
    {
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(ThreeRecords));
        var doc = NdjsonDocument.Load(stream);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
    }

    [Fact]
    public void LoadStream_FieldValuesCorrect()
    {
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(ThreeRecords));
        var doc = NdjsonDocument.Load(stream);
        var names = doc.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
    }

    // -------------------------------------------------------------------------
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecords);
        var path = TempFile("out.ndjson");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_ContentContainsRecords()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecords);
        var path = TempFile("content.ndjson");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("Bob", content);
    }

    [Fact]
    public void SaveToFile_ThenLoadFile_CountMatches()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecords);
        var path = TempFile("roundtrip.ndjson");
        doc.SaveToFile(path);
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, reloaded.Count);
    }

    // -------------------------------------------------------------------------
    // ToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ToNdjson_IsNonEmpty()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecords);
        var ndjson = doc.ToNdjson();
        Assert.False(string.IsNullOrEmpty(ndjson));
    }

    [Fact]
    public void ToNdjson_ContainsFieldValues()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecords);
        var ndjson = doc.ToNdjson();
        Assert.Contains("Alice", ndjson);
        Assert.Contains("Carol", ndjson);
    }

    [Fact]
    public void FilterThenToNdjson_ExcludesFiltered()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecords);
        var engOnly = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var ndjson = engOnly.ToNdjson();
        Assert.Contains("Alice", ndjson);
        Assert.Contains("Carol", ndjson);
        Assert.DoesNotContain("Bob", ndjson);
    }

    // -------------------------------------------------------------------------
    // Dogfood: LoadContent->Filter->SaveToFile->LoadFile pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterSaveLoadPipeline()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecords);
        Assert.Equal(3, doc.Count);

        // Filter Eng only
        var eng = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);

        // Save to file
        var path = TempFile("eng.ndjson");
        eng.SaveToFile(path);
        Assert.True(File.Exists(path));

        // Reload
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(2, reloaded.Count);

        // Verify content
        var names = reloaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);

        // Verify schema
        Assert.True(reloaded.IsUniformSchema());
    }
}
