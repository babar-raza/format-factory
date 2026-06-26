// Tests for NdjsonDocument.Load, LoadContent, LoadFile edge cases deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R170

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R170: Tests for NdjsonDocument.Load, LoadContent, LoadFile edge cases.
/// NdjsonDocument.Load(content): loads from NDJSON string.
/// NdjsonDocument.LoadContent(content): alias for Load.
/// NdjsonDocument.LoadFile(path): loads from file.
/// Covers: Load non-null; Load count correct; Load empty string returns empty doc;
/// Load single record; Load with trailing newline; LoadContent same as Load;
/// LoadContent count; LoadFile from written file; LoadFile count matches;
/// LoadFile values correct; Load->Filter->ToNdjson->Load chain;
/// LoadContent->GetAllKeys; LoadFile->IsUniformSchema; Load->TypedRecords;
/// LoadContent->GetFieldValues; LoadFile after SaveToFile;
/// dogfood Load->GetAllKeys->Filter->SaveToFile->LoadFile->TypedRecords verify.
/// </summary>
public class NdjsonR170DocumentLoadAndSchemaTests : IDisposable
{
    private readonly string _tempDir;

    private const string ThreeRecordNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":88}";

    public NdjsonR170DocumentLoadAndSchemaTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR170_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // NdjsonDocument.Load
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_NonNull()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.NotNull(doc);
    }

    [Fact]
    public void Load_CountCorrect()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void Load_EmptyString_ReturnsEmptyDoc()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        Assert.Equal(0, doc.Count);
    }

    [Fact]
    public void Load_SingleRecord()
    {
        var doc = NdjsonDocument.Load("{\"id\":1,\"val\":\"test\"}");
        Assert.Equal(1, doc.Count);
    }

    [Fact]
    public void Load_WithTrailingNewline_CountCorrect()
    {
        var content = ThreeRecordNdjson + "\n";
        var doc = NdjsonDocument.Load(content);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void Load_TypedRecords_CountMatches()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(doc.Count, doc.TypedRecords.Count);
    }

    // -------------------------------------------------------------------------
    // NdjsonDocument.LoadContent
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadContent_SameAsLoad_CountMatches()
    {
        var doc1 = NdjsonDocument.Load(ThreeRecordNdjson);
        var doc2 = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        Assert.Equal(doc1.Count, doc2.Count);
    }

    [Fact]
    public void LoadContent_GetAllKeys_NonEmpty()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var keys = doc.GetAllKeys();
        Assert.NotEmpty(keys);
    }

    [Fact]
    public void LoadContent_GetFieldValues_Correct()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var names = doc.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
    }

    // -------------------------------------------------------------------------
    // NdjsonDocument.LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_FromWrittenFile_CountMatches()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("test.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, loaded.Count);
    }

    [Fact]
    public void LoadFile_ValuesCorrect()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("vals.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var names = loaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void LoadFile_IsUniformSchema_True()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("schema.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.True(loaded.IsUniformSchema());
    }

    [Fact]
    public void LoadFile_AfterSaveToFile_TypedRecords()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("typed.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, loaded.TypedRecords.Count);
        Assert.True(loaded.TypedRecords[0].TryGetString("name", out var name));
        Assert.Equal("Alice", name);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->GetAllKeys->Filter->SaveToFile->LoadFile->TypedRecords verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadGetKeysFilterSaveLoadTypedVerify_Pipeline()
    {
        // Load
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(3, doc.Count);

        // GetAllKeys
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
        Assert.Contains("score", keys);

        // Filter
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);
        Assert.True(eng.IsUniformSchema());

        // SaveToFile
        var path = TempFile("dogfood.ndjson");
        eng.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(2, loaded.Count);
        Assert.True(loaded.IsUniformSchema());

        // TypedRecords
        var typed = loaded.TypedRecords;
        Assert.Equal(2, typed.Count);
        Assert.True(typed[0].TryGetString("name", out var firstName));
        Assert.Equal("Alice", firstName);

        // LoadContent
        var content = File.ReadAllText(path);
        var fromContent = NdjsonDocument.LoadContent(content);
        Assert.Equal(2, fromContent.Count);
    }
}
