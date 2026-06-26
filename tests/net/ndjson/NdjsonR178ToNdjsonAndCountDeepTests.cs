// Tests for NdjsonDocument.ToNdjson, Count, NdjsonWriter.WriteToFile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R178

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R178: Tests for NdjsonDocument.ToNdjson, Count, NdjsonWriter.WriteToFile deeper.
/// ToNdjson(): serializes the document back to NDJSON string.
/// Count: total record count.
/// NdjsonWriter.WriteToFile(doc, path): writes NDJSON document to a file.
/// Covers: ToNdjson non-null; ToNdjson non-empty; ToNdjson contains record data;
/// ToNdjson has newlines separating records; ToNdjson->Load round-trip count correct;
/// ToNdjson->Load values correct; Count after filter; Count after LoadContent;
/// WriteToFile creates file; WriteToFile file non-empty; WriteToFile then LoadFile count correct;
/// WriteToFile content contains record data;
/// dogfood Load->ToNdjson->Load->Filter->ToNdjson->WriteToFile->LoadFile verify pipeline.
/// </summary>
public class NdjsonR178ToNdjsonAndCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string FourRecordNdjson =
        "{\"id\":1,\"name\":\"Alice\",\"score\":95}\n" +
        "{\"id\":2,\"name\":\"Bob\",\"score\":82}\n" +
        "{\"id\":3,\"name\":\"Carol\",\"score\":91}\n" +
        "{\"id\":4,\"name\":\"Dave\",\"score\":78}";

    public NdjsonR178ToNdjsonAndCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR178_" + Guid.NewGuid().ToString("N"));
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
        var doc = NdjsonDocument.LoadContent(FourRecordNdjson);
        Assert.NotNull(doc.ToNdjson());
    }

    [Fact]
    public void ToNdjson_NonEmpty()
    {
        var doc = NdjsonDocument.LoadContent(FourRecordNdjson);
        Assert.False(string.IsNullOrWhiteSpace(doc.ToNdjson()));
    }

    [Fact]
    public void ToNdjson_ContainsRecordData()
    {
        var doc = NdjsonDocument.LoadContent(FourRecordNdjson);
        var ndjson = doc.ToNdjson();
        Assert.Contains("Alice", ndjson);
        Assert.Contains("Bob", ndjson);
    }

    [Fact]
    public void ToNdjson_HasNewlines()
    {
        var doc = NdjsonDocument.LoadContent(FourRecordNdjson);
        var ndjson = doc.ToNdjson();
        Assert.Contains("\n", ndjson);
    }

    [Fact]
    public void ToNdjson_RoundTrip_CountCorrect()
    {
        var doc = NdjsonDocument.LoadContent(FourRecordNdjson);
        var ndjson = doc.ToNdjson();
        var reloaded = NdjsonDocument.LoadContent(ndjson);
        Assert.Equal(4, reloaded.Count);
    }

    [Fact]
    public void ToNdjson_RoundTrip_ValuesCorrect()
    {
        var doc = NdjsonDocument.LoadContent(FourRecordNdjson);
        var ndjson = doc.ToNdjson();
        var reloaded = NdjsonDocument.LoadContent(ndjson);
        var names = reloaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }

    // -------------------------------------------------------------------------
    // Count
    // -------------------------------------------------------------------------

    [Fact]
    public void Count_AfterLoadContent_Correct()
    {
        var doc = NdjsonDocument.LoadContent(FourRecordNdjson);
        Assert.Equal(4, doc.Count);
    }

    [Fact]
    public void Count_AfterFilter_ReducedCorrectly()
    {
        var doc = NdjsonDocument.LoadContent(FourRecordNdjson);
        var high = doc.Filter(r => r.TryGetValue("score", out var s) &&
            int.TryParse(s, out var v) && v >= 90);
        Assert.Equal(2, high.Count); // Alice(95), Carol(91)
    }

    [Fact]
    public void Count_SingleRecord_IsOne()
    {
        var doc = NdjsonDocument.LoadContent("{\"x\":1}");
        Assert.Equal(1, doc.Count);
    }

    // -------------------------------------------------------------------------
    // NdjsonWriter.WriteToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToFile_CreatesFile()
    {
        var doc = NdjsonDocument.LoadContent(FourRecordNdjson);
        var path = TempFile("out.ndjson");
        NdjsonWriter.WriteToFile(doc, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_FileNonEmpty()
    {
        var doc = NdjsonDocument.LoadContent(FourRecordNdjson);
        var path = TempFile("nonempty.ndjson");
        NdjsonWriter.WriteToFile(doc, path);
        Assert.False(string.IsNullOrWhiteSpace(File.ReadAllText(path)));
    }

    [Fact]
    public void WriteToFile_ThenLoadFile_CountCorrect()
    {
        var doc = NdjsonDocument.LoadContent(FourRecordNdjson);
        var path = TempFile("roundtrip.ndjson");
        NdjsonWriter.WriteToFile(doc, path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(4, loaded.Count);
    }

    [Fact]
    public void WriteToFile_FileContainsRecordData()
    {
        var doc = NdjsonDocument.LoadContent(FourRecordNdjson);
        var path = TempFile("data.ndjson");
        NdjsonWriter.WriteToFile(doc, path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("Dave", content);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadToNdjsonLoadFilterToNdjsonWriteToFileLoadFileVerify_Pipeline()
    {
        // Load
        var doc = NdjsonDocument.LoadContent(FourRecordNdjson);
        Assert.Equal(4, doc.Count);

        // ToNdjson round-trip
        var ndjson = doc.ToNdjson();
        var reloaded = NdjsonDocument.LoadContent(ndjson);
        Assert.Equal(4, reloaded.Count);

        // Filter high scorers
        var high = reloaded.Filter(r =>
            r.TryGetValue("score", out var s) &&
            int.TryParse(s, out var v) && v >= 90);
        Assert.Equal(2, high.Count);

        // ToNdjson on filtered
        var filteredNdjson = high.ToNdjson();
        Assert.Contains("Alice", filteredNdjson);
        Assert.Contains("Carol", filteredNdjson);
        Assert.DoesNotContain("Bob", filteredNdjson);
        Assert.DoesNotContain("Dave", filteredNdjson);

        // WriteToFile
        var path = TempFile("dogfood.ndjson");
        NdjsonWriter.WriteToFile(high, path);
        Assert.True(File.Exists(path));

        // LoadFile verify
        var fromFile = NdjsonDocument.LoadFile(path);
        Assert.Equal(2, fromFile.Count);
        var names = fromFile.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }
}
