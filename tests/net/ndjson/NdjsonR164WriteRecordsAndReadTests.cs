// Tests for NdjsonWriter.WriteToFile and NdjsonDocument.LoadFile deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R164

using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R164: Tests for NdjsonWriter.WriteToFile and NdjsonDocument.LoadFile round-trips.
/// NdjsonWriter.WriteToFile(doc, path): writes NdjsonDocument to file.
/// NdjsonDocument.LoadFile(path): reads NDJSON from file.
/// Covers: WriteToFile creates file; WriteToFile->LoadFile count matches;
/// WriteToFile->LoadFile field values correct; WriteToFile then Filter->LoadFile;
/// NdjsonDocument.SaveToFile creates file; SaveToFile->LoadFile count matches;
/// SaveToFile then GetFieldValues matches; Filter->SaveToFile->LoadFile IsUniformSchema;
/// LoadFile->Filter->WriteToFile->LoadFile chain; Count on loaded doc;
/// Records list count matches Count; Records direct access field;
/// WriteToFile of empty doc; LoadFile of empty file;
/// dogfood NdjsonDocument->SaveToFile->LoadFile->NdjsonWriter->WriteToFile->LoadFile.
/// </summary>
public class NdjsonR164WriteRecordsAndReadTests : IDisposable
{
    private readonly string _tempDir;

    private const string ThreeRecordNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":88}";

    public NdjsonR164WriteRecordsAndReadTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR164_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // NdjsonWriter.WriteToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToFile_CreatesFile()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("wr.ndjson");
        NdjsonWriter.WriteToFile(doc, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_LoadFile_CountMatches()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("wl.ndjson");
        NdjsonWriter.WriteToFile(doc, path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(doc.Count, loaded.Count);
    }

    [Fact]
    public void WriteToFile_LoadFile_FieldValuesCorrect()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("wf.ndjson");
        NdjsonWriter.WriteToFile(doc, path);
        var loaded = NdjsonDocument.LoadFile(path);
        var names = loaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    // -------------------------------------------------------------------------
    // SaveToFile (alias)
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("sf.ndjson");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_LoadFile_CountMatches()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("sl.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, loaded.Count);
    }

    [Fact]
    public void SaveToFile_LoadFile_IsUniformSchema()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("us.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.True(loaded.IsUniformSchema());
    }

    // -------------------------------------------------------------------------
    // Records direct access
    // -------------------------------------------------------------------------

    [Fact]
    public void Records_Count_MatchesCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(doc.Count, doc.Records.Count);
    }

    [Fact]
    public void Records_DirectAccess_FirstElement()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var first = doc.Records[0];
        Assert.True(first.TryGetProperty("name", out var name));
        Assert.Equal("Alice", name.GetString());
    }

    // -------------------------------------------------------------------------
    // Empty doc
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToFile_EmptyDoc_CreatesFile()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        var path = TempFile("empty.ndjson");
        NdjsonWriter.WriteToFile(doc, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void LoadFile_EmptyFile_CountIsZero()
    {
        var path = TempFile("emptyload.ndjson");
        File.WriteAllText(path, string.Empty);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(0, doc.Count);
    }

    // -------------------------------------------------------------------------
    // Filter -> WriteToFile -> LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_WriteToFile_LoadFile_Chain()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var path = TempFile("eng.ndjson");
        NdjsonWriter.WriteToFile(eng, path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(2, loaded.Count);
        var names = loaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood: SaveToFile->LoadFile->Filter->NdjsonWriter->WriteToFile->LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SaveLoadFilterWriteLoadVerify_Pipeline()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(3, doc.Count);

        // SaveToFile
        var path1 = TempFile("dog1.ndjson");
        doc.SaveToFile(path1);

        // LoadFile
        var loaded1 = NdjsonDocument.LoadFile(path1);
        Assert.Equal(3, loaded1.Count);
        Assert.True(loaded1.IsUniformSchema());

        // Filter
        var eng = loaded1.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);

        // WriteToFile
        var path2 = TempFile("dog2.ndjson");
        NdjsonWriter.WriteToFile(eng, path2);

        // LoadFile again
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(2, loaded2.Count);
        var names = loaded2.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);

        // Records direct access
        Assert.Equal(2, loaded2.Records.Count);
    }
}
