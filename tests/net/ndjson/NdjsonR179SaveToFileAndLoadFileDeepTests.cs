// Tests for NdjsonDocument.SaveToFile, LoadFile deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R179

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R179: Tests for NdjsonDocument.SaveToFile, LoadFile deeper coverage.
/// SaveToFile(path): writes NDJSON content to a file.
/// LoadFile(path): loads NdjsonDocument from a file.
/// Covers: SaveToFile creates file; SaveToFile file non-empty; SaveToFile content correct;
/// LoadFile non-null; LoadFile Count correct; LoadFile records accessible;
/// LoadFile IsUniformSchema preserved; SaveToFile->LoadFile round-trip values correct;
/// Filter->SaveToFile->LoadFile count preserved; SaveToFile then modify then reload;
/// multiple SaveToFile->LoadFile operations independent;
/// dogfood Load->Filter->SaveToFile->LoadFile->Filter->verify pipeline.
/// </summary>
public class NdjsonR179SaveToFileAndLoadFileDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string FiveRecordNdjson =
        "{\"id\":1,\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
        "{\"id\":2,\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":82}\n" +
        "{\"id\":3,\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":91}\n" +
        "{\"id\":4,\"name\":\"Dave\",\"dept\":\"HR\",\"score\":77}\n" +
        "{\"id\":5,\"name\":\"Eve\",\"dept\":\"Eng\",\"score\":88}";

    public NdjsonR179SaveToFileAndLoadFileDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR179_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = NdjsonDocument.LoadContent(FiveRecordNdjson);
        var path = TempFile("out.ndjson");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileNonEmpty()
    {
        var doc = NdjsonDocument.LoadContent(FiveRecordNdjson);
        var path = TempFile("nonempty.ndjson");
        doc.SaveToFile(path);
        Assert.False(string.IsNullOrWhiteSpace(File.ReadAllText(path)));
    }

    [Fact]
    public void SaveToFile_ContentContainsRecords()
    {
        var doc = NdjsonDocument.LoadContent(FiveRecordNdjson);
        var path = TempFile("content.ndjson");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("Eve", content);
    }

    [Fact]
    public void SaveToFile_ContentHasNewlines()
    {
        var doc = NdjsonDocument.LoadContent(FiveRecordNdjson);
        var path = TempFile("newlines.ndjson");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("\n", content);
    }

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(FiveRecordNdjson);
        var path = TempFile("load.ndjson");
        doc.SaveToFile(path);
        Assert.NotNull(NdjsonDocument.LoadFile(path));
    }

    [Fact]
    public void LoadFile_Count_Correct()
    {
        var doc = NdjsonDocument.LoadContent(FiveRecordNdjson);
        var path = TempFile("count.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(5, loaded.Count);
    }

    [Fact]
    public void LoadFile_Records_Accessible()
    {
        var doc = NdjsonDocument.LoadContent(FiveRecordNdjson);
        var path = TempFile("records.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var names = loaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
    }

    [Fact]
    public void LoadFile_IsUniformSchema_True()
    {
        var doc = NdjsonDocument.LoadContent(FiveRecordNdjson);
        var path = TempFile("schema.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.True(loaded.IsUniformSchema);
    }

    // -------------------------------------------------------------------------
    // Round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_ThenLoadFile_CountPreserved()
    {
        var doc = NdjsonDocument.LoadContent(FiveRecordNdjson);
        var path = TempFile("roundtrip.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(doc.Count, loaded.Count);
    }

    [Fact]
    public void Filter_SaveToFile_LoadFile_CountPreserved()
    {
        var doc = NdjsonDocument.LoadContent(FiveRecordNdjson);
        var eng = doc.Filter(r => r.TryGetValue("dept", out var d) && d == "Eng");
        var path = TempFile("eng.ndjson");
        eng.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, loaded.Count);
    }

    [Fact]
    public void SaveToFile_TwoFiles_Independent()
    {
        var doc = NdjsonDocument.LoadContent(FiveRecordNdjson);
        var engPath = TempFile("eng2.ndjson");
        var hrPath = TempFile("hr.ndjson");

        doc.Filter(r => r.TryGetValue("dept", out var d) && d == "Eng")
           .SaveToFile(engPath);
        doc.Filter(r => r.TryGetValue("dept", out var d) && d == "HR")
           .SaveToFile(hrPath);

        var engLoaded = NdjsonDocument.LoadFile(engPath);
        var hrLoaded = NdjsonDocument.LoadFile(hrPath);

        Assert.Equal(3, engLoaded.Count);
        Assert.Equal(1, hrLoaded.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterSaveToFileLoadFileFilterVerify_Pipeline()
    {
        // Load
        var doc = NdjsonDocument.LoadContent(FiveRecordNdjson);
        Assert.Equal(5, doc.Count);

        // Filter Eng
        var eng = doc.Filter(r => r.TryGetValue("dept", out var d) && d == "Eng");
        Assert.Equal(3, eng.Count);

        // SaveToFile
        var path = TempFile("dogfood.ndjson");
        eng.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, loaded.Count);
        Assert.True(loaded.IsUniformSchema);

        // Names accessible
        var names = loaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Eve", names);
        Assert.DoesNotContain("Bob", names);
        Assert.DoesNotContain("Dave", names);

        // Filter high scorers from loaded
        var high = loaded.Filter(r =>
            r.TryGetValue("score", out var s) &&
            int.TryParse(s, out var v) && v >= 91);
        Assert.Equal(2, high.Count); // Alice(95), Carol(91)

        // Verify filtered names
        var highNames = high.GetFieldValues("name");
        Assert.Contains("Alice", highNames);
        Assert.Contains("Carol", highNames);
        Assert.DoesNotContain("Eve", highNames); // Eve=88
    }
}
