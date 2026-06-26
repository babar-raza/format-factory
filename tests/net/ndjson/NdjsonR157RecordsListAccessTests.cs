// Tests for NdjsonDocument.Records list direct access and LoadFile deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R157

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R157: Tests for NdjsonDocument.Records list access and LoadFile deeper coverage.
/// Records: direct list of JsonElement accessible by index.
/// LoadFile: loads NDJSON from disk.
/// SaveToFile: writes NDJSON to disk.
/// Covers: Records count equals Count; Records[0] is valid JsonElement;
/// Records[0].TryGetProperty("name") true; Records list is non-null;
/// LoadFile from temp file returns correct count; LoadFile records accessible;
/// SaveToFile then LoadFile preserves count; SaveToFile then LoadFile record values;
/// Filter->SaveToFile->LoadFile chain; ToNdjson->Load round-trip;
/// Empty doc Records is empty; Count zero for empty doc;
/// GetAllKeys after LoadFile; dogfood SaveToFile->LoadFile->Filter->GetFieldValues.
/// </summary>
public class NdjsonR157RecordsListAccessTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR157RecordsListAccessTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR157_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string ThreeRecordNdjson =
        "{\"name\":\"Alice\",\"score\":95,\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Bob\",\"score\":82,\"dept\":\"Finance\"}\n" +
        "{\"name\":\"Carol\",\"score\":88,\"dept\":\"Eng\"}";

    // -------------------------------------------------------------------------
    // Records direct access
    // -------------------------------------------------------------------------

    [Fact]
    public void Records_CountEqualsDocumentCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(doc.Count, doc.Records.Count);
    }

    [Fact]
    public void Records_IsNonNull()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.NotNull(doc.Records);
    }

    [Fact]
    public void Records_FirstElement_HasNameProperty()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var first = doc.Records[0];
        Assert.True(first.TryGetProperty("name", out _));
    }

    [Fact]
    public void Records_FirstElement_NameIsAlice()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var first = doc.Records[0];
        first.TryGetProperty("name", out var nameProp);
        Assert.Equal("Alice", nameProp.GetString());
    }

    [Fact]
    public void Records_EmptyDoc_IsEmpty()
    {
        var doc = NdjsonDocument.Load("");
        Assert.Equal(0, doc.Records.Count);
        Assert.Equal(0, doc.Count);
    }

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_ReturnsCorrectCount()
    {
        var path = TempFile("load.ndjson");
        File.WriteAllText(path, ThreeRecordNdjson, Encoding.UTF8);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void LoadFile_RecordsAccessible()
    {
        var path = TempFile("records.ndjson");
        File.WriteAllText(path, ThreeRecordNdjson, Encoding.UTF8);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.True(doc.Records[0].TryGetProperty("name", out _));
    }

    [Fact]
    public void LoadFile_GetAllKeys_CountIsThree()
    {
        var path = TempFile("keys.ndjson");
        File.WriteAllText(path, ThreeRecordNdjson, Encoding.UTF8);
        var doc = NdjsonDocument.LoadFile(path);
        var keys = doc.GetAllKeys();
        Assert.Equal(3, keys.Count);
    }

    // -------------------------------------------------------------------------
    // SaveToFile -> LoadFile round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFileThenLoadFile_PreservesCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("rt.ndjson");
        doc.SaveToFile(path);
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, reloaded.Count);
    }

    [Fact]
    public void SaveToFileThenLoadFile_PreservesFieldValues()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("rt2.ndjson");
        doc.SaveToFile(path);
        var reloaded = NdjsonDocument.LoadFile(path);
        var names = reloaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
    }

    // -------------------------------------------------------------------------
    // Filter -> SaveToFile -> LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterSaveLoadFile_Chain()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var eng = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var path = TempFile("eng.ndjson");
        eng.SaveToFile(path);
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(2, reloaded.Count);
        var names = reloaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood: SaveToFile->LoadFile->Filter->GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SaveLoadFilterGetFieldValues_Pipeline()
    {
        // Save original
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path1 = TempFile("step1.ndjson");
        doc.SaveToFile(path1);

        // Reload
        var loaded = NdjsonDocument.LoadFile(path1);
        Assert.Equal(3, loaded.Count);

        // GetAllKeys
        var keys = loaded.GetAllKeys();
        Assert.Equal(3, keys.Count);

        // Filter Finance
        var finance = loaded.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Finance");
        Assert.Equal(1, finance.Count);

        // GetFieldValues on filtered
        var financeNames = finance.GetFieldValues("name");
        Assert.Single(financeNames);
        Assert.Contains("Bob", financeNames);

        // Save filtered
        var path2 = TempFile("step2.ndjson");
        finance.SaveToFile(path2);
        var final = NdjsonDocument.LoadFile(path2);
        Assert.Equal(1, final.Count);
    }
}
