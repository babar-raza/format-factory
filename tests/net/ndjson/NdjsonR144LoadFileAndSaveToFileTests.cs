// Tests for NdjsonDocument.LoadFile, SaveToFile, TypedRecords, GetTypedRecord.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R144

using System;
using System.IO;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R144: Tests for NdjsonDocument.LoadFile, SaveToFile, TypedRecords, GetTypedRecord.
/// LoadFile reads from disk; SaveToFile writes to disk; round-trip preserves records.
/// TypedRecords is a lazy view of Records as NdjsonRecord wrappers.
/// GetTypedRecord(index) wraps the record at that index; throws on OOB.
/// Covers: LoadFile missing path throws; LoadFile content matches Load content;
/// SaveToFile writes valid NDJSON; SaveToFile round-trip preserves count;
/// SaveToFile round-trip preserves field values; TypedRecords count matches Records;
/// TypedRecords elements are NdjsonRecord; GetTypedRecord valid index succeeds;
/// GetTypedRecord OOB throws; GetTypedRecord negative throws;
/// dogfood Load->Filter->SaveToFile->LoadFile pipeline.
/// </summary>
public class NdjsonR144LoadFileAndSaveToFileTests : IDisposable
{
    private const string ThreeRecords =
        "{\"name\":\"Alice\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"score\":88}";

    private readonly string _tempDir;

    public NdjsonR144LoadFileAndSaveToFileTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR144_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_MissingPath_Throws()
    {
        Assert.ThrowsAny<Exception>(() =>
            NdjsonDocument.LoadFile(Path.Combine(_tempDir, "nonexistent.ndjson")));
    }

    [Fact]
    public void LoadFile_ValidFile_SameCountAsLoad()
    {
        var path = TempFile("three.ndjson");
        File.WriteAllText(path, ThreeRecords);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void LoadFile_ValidFile_SameFieldsAsLoad()
    {
        var path = TempFile("three2.ndjson");
        File.WriteAllText(path, ThreeRecords);
        var docFile = NdjsonDocument.LoadFile(path);
        var docMem = NdjsonDocument.Load(ThreeRecords);
        var namesFile = docFile.GetFieldValues("name");
        var namesMem = docMem.GetFieldValues("name");
        Assert.Equal(namesMem, namesFile);
    }

    // -------------------------------------------------------------------------
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_WritesFile()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var path = TempFile("saved.ndjson");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void SaveToFile_RoundTrip_SameCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var path = TempFile("roundtrip.ndjson");
        doc.SaveToFile(path);
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(doc.Count, reloaded.Count);
    }

    [Fact]
    public void SaveToFile_RoundTrip_PreservesFieldValues()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var path = TempFile("roundtrip2.ndjson");
        doc.SaveToFile(path);
        var reloaded = NdjsonDocument.LoadFile(path);
        var names = reloaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void SaveToFile_OutputIsValidNdjson()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var path = TempFile("valid.ndjson");
        doc.SaveToFile(path);
        var lines = File.ReadAllLines(path);
        foreach (var line in lines)
        {
            if (string.IsNullOrWhiteSpace(line)) continue;
            var el = JsonDocument.Parse(line).RootElement;
            Assert.Equal(JsonValueKind.Object, el.ValueKind);
        }
    }

    // -------------------------------------------------------------------------
    // TypedRecords
    // -------------------------------------------------------------------------

    [Fact]
    public void TypedRecords_CountMatchesRecordsCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        Assert.Equal(doc.Records.Count, doc.TypedRecords.Count);
    }

    [Fact]
    public void TypedRecords_ElementsAreNdjsonRecord()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        foreach (var r in doc.TypedRecords)
            Assert.IsType<NdjsonRecord>(r);
    }

    // -------------------------------------------------------------------------
    // GetTypedRecord
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTypedRecord_ValidIndex_ReturnsNdjsonRecord()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var r = doc.GetTypedRecord(0);
        Assert.IsType<NdjsonRecord>(r);
    }

    [Fact]
    public void GetTypedRecord_OobIndex_Throws()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        Assert.ThrowsAny<Exception>(() => doc.GetTypedRecord(doc.Count));
    }

    [Fact]
    public void GetTypedRecord_NegativeIndex_Throws()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        Assert.ThrowsAny<Exception>(() => doc.GetTypedRecord(-1));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->SaveToFile->LoadFile pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterSaveLoadFile_Pipeline()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);

        // Keep only high scorers
        var high = doc.Filter(el =>
            el.TryGetProperty("score", out var s) && s.GetInt32() >= 88);
        Assert.Equal(2, high.Count); // Alice(95), Carol(88)

        // Write to file and reload
        var path = TempFile("dogfood.ndjson");
        high.SaveToFile(path);
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(2, reloaded.Count);

        var names = reloaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }
}
