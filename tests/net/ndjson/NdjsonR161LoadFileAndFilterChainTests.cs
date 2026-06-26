// Tests for NdjsonDocument.LoadFile, Filter chain, and GetAllKeys analysis.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R161

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R161: Tests for NdjsonDocument.LoadFile, Filter chain, and GetAllKeys analysis.
/// LoadFile(path): loads NDJSON from disk.
/// Filter chaining: apply multiple filters in sequence.
/// GetAllKeys(): returns all distinct field names across records.
/// Covers: LoadFile creates doc; LoadFile->Count matches written count;
/// LoadFile->GetAllKeys has expected keys; Filter->Filter count correct;
/// Filter->Filter->GetFieldValues subset; GetAllKeys non-empty;
/// GetAllKeys contains expected field names; GetAllKeys on filtered still has all keys;
/// Filter->GetAllKeys matches original keys; IsUniformSchema on uniform doc;
/// IsUniformSchema on non-uniform doc; Filter none->Count is zero;
/// Filter all->Count unchanged;
/// dogfood SaveToFile->LoadFile->GetAllKeys->Filter->Filter->GetFieldValues.
/// </summary>
public class NdjsonR161LoadFileAndFilterChainTests : IDisposable
{
    private readonly string _tempDir;

    private const string FiveRecordNdjson =
        "{\"name\":\"Alice\",\"score\":95,\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Bob\",\"score\":82,\"dept\":\"Finance\"}\n" +
        "{\"name\":\"Carol\",\"score\":88,\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Dave\",\"score\":91,\"dept\":\"Finance\"}\n" +
        "{\"name\":\"Eve\",\"score\":79,\"dept\":\"Eng\"}";

    public NdjsonR161LoadFileAndFilterChainTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR161_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private NdjsonDocument WriteAndLoad(string content)
    {
        var path = TempFile("data.ndjson");
        File.WriteAllText(path, content);
        return NdjsonDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_CreatesDoc()
    {
        var doc = WriteAndLoad(FiveRecordNdjson);
        Assert.NotNull(doc);
    }

    [Fact]
    public void LoadFile_CountMatchesWritten()
    {
        var doc = WriteAndLoad(FiveRecordNdjson);
        Assert.Equal(5, doc.Count);
    }

    [Fact]
    public void LoadFile_GetAllKeys_HasExpectedKeys()
    {
        var doc = WriteAndLoad(FiveRecordNdjson);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
        Assert.Contains("dept", keys);
    }

    // -------------------------------------------------------------------------
    // GetAllKeys
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAllKeys_NonEmpty()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var keys = doc.GetAllKeys();
        Assert.NotEmpty(keys);
    }

    [Fact]
    public void GetAllKeys_ContainsAllFields()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
        Assert.Contains("dept", keys);
    }

    [Fact]
    public void GetAllKeys_OnFiltered_StillHasAllOriginalKeys()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var keys = eng.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
    }

    // -------------------------------------------------------------------------
    // Filter chaining
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_Filter_ChainCountCorrect()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        // First: Eng (Alice=95, Carol=88, Eve=79)
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        // Second: score >= 85 (Alice=95, Carol=88)
        var highEng = eng.Filter(el => el.TryGetProperty("score", out var s) && s.GetDouble() >= 85);
        Assert.Equal(2, highEng.Count);
    }

    [Fact]
    public void Filter_Filter_GetFieldValues_Subset()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var highEng = eng.Filter(el => el.TryGetProperty("score", out var s) && s.GetDouble() >= 85);
        var names = highEng.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Eve", names);
    }

    [Fact]
    public void Filter_None_CountIsZero()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var none = doc.Filter(_ => false);
        Assert.Equal(0, none.Count);
    }

    [Fact]
    public void Filter_All_CountUnchanged()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var all = doc.Filter(_ => true);
        Assert.Equal(5, all.Count);
    }

    // -------------------------------------------------------------------------
    // IsUniformSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void IsUniformSchema_UniformDoc_ReturnsTrue()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_NonUniformDoc_ReturnsFalse()
    {
        var mixed = "{\"a\":1}\n{\"b\":2}";
        var doc = NdjsonDocument.Load(mixed);
        Assert.False(doc.IsUniformSchema());
    }

    // -------------------------------------------------------------------------
    // Dogfood: SaveToFile->LoadFile->GetAllKeys->Filter->Filter->GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SaveLoadGetAllKeysFilterFilterGetFieldValues_Pipeline()
    {
        // Save to file
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var path = TempFile("dogfood.ndjson");
        doc.SaveToFile(path);

        // LoadFile
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(5, loaded.Count);

        // GetAllKeys
        var keys = loaded.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
        Assert.Contains("dept", keys);

        // Filter Eng
        var eng = loaded.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(3, eng.Count);

        // Filter high score
        var highEng = eng.Filter(el => el.TryGetProperty("score", out var s) && s.GetDouble() >= 85);
        Assert.Equal(2, highEng.Count);

        // GetFieldValues
        var names = highEng.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Eve", names);

        // IsUniformSchema check on final subset
        Assert.True(highEng.IsUniformSchema());
    }
}
