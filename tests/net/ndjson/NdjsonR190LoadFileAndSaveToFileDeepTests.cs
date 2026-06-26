// Tests for NdjsonDocument.LoadFile, SaveToFile, Filter chain deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R190

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R190: Tests for NdjsonDocument.LoadFile, SaveToFile, Filter chain deeper coverage.
/// LoadFile(path): loads a document from a file.
/// SaveToFile(path): saves the document to a file.
/// Filter(predicate) chain: applies multiple filters in sequence.
/// Covers: LoadFile non-null; LoadFile count correct; LoadFile data accessible;
/// SaveToFile creates file; SaveToFile file non-empty; SaveToFile parseable;
/// SaveToFile then LoadFile count matches; SaveToFile then LoadFile data correct;
/// Filter chain three conditions; Filter then SaveToFile; Filter then ToNdjson;
/// Filter preserves record structure; Filter chain empty result;
/// dogfood LoadFile->AppendRecord->Filter->SaveToFile->LoadFile->Verify pipeline.
/// </summary>
public class NdjsonR190LoadFileAndSaveToFileDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string Content =
        "{\"Name\":\"Alice\",\"Dept\":\"Eng\",\"Score\":92,\"Active\":true}\n" +
        "{\"Name\":\"Bob\",\"Dept\":\"Finance\",\"Score\":85,\"Active\":false}\n" +
        "{\"Name\":\"Carol\",\"Dept\":\"Eng\",\"Score\":78,\"Active\":true}\n" +
        "{\"Name\":\"Dave\",\"Dept\":\"HR\",\"Score\":91,\"Active\":false}\n" +
        "{\"Name\":\"Eve\",\"Dept\":\"Finance\",\"Score\":88,\"Active\":true}";

    public NdjsonR190LoadFileAndSaveToFileDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR190_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string WriteSampleFile(string name = "sample.ndjson")
    {
        var path = TempFile(name);
        File.WriteAllText(path, Content);
        return path;
    }

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_NonNull()
    {
        var path = WriteSampleFile();
        Assert.NotNull(NdjsonDocument.LoadFile(path));
    }

    [Fact]
    public void LoadFile_CountCorrect()
    {
        var path = WriteSampleFile();
        Assert.Equal(5, NdjsonDocument.LoadFile(path).Count);
    }

    [Fact]
    public void LoadFile_DataAccessible()
    {
        var path = WriteSampleFile();
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal("Alice", doc.RecordAt(0).GetField("Name")?.ToString());
    }

    [Fact]
    public void LoadFile_AllRecordsNonNull()
    {
        var path = WriteSampleFile();
        var doc = NdjsonDocument.LoadFile(path);
        for (var i = 0; i < doc.Count; i++)
            Assert.NotNull(doc.RecordAt(i));
    }

    [Fact]
    public void LoadFile_LastRecord_Correct()
    {
        var path = WriteSampleFile();
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal("Eve", doc.RecordAt(4).GetField("Name")?.ToString());
    }

    // -------------------------------------------------------------------------
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var path = TempFile("saved.ndjson");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileIsNonEmpty()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var path = TempFile("nonempty.ndjson");
        doc.SaveToFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void SaveToFile_FileParseable()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var path = TempFile("parseable.ndjson");
        doc.SaveToFile(path);
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(doc.Count, reloaded.Count);
    }

    [Fact]
    public void SaveToFile_ThenLoadFile_DataCorrect()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var path = TempFile("data.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal("Alice", loaded.RecordAt(0).GetField("Name")?.ToString());
    }

    [Fact]
    public void SaveToFile_AfterAppendRecord_IncludesNew()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var record = new Dictionary<string, object?> { ["Name"] = "Frank", ["Dept"] = "Legal", ["Score"] = 97, ["Active"] = true };
        var extended = doc.AppendRecord(record);
        var path = TempFile("extended.ndjson");
        extended.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(6, loaded.Count);
        Assert.Equal("Frank", loaded.RecordAt(5).GetField("Name")?.ToString());
    }

    // -------------------------------------------------------------------------
    // Filter chain
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_Chain_ThreeConditions()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var result = doc
            .Filter(r => r.GetField("Dept")?.ToString() == "Eng")
            .Filter(r => Convert.ToBoolean(r.GetField("Active")))
            .Filter(r => Convert.ToDouble(r.GetField("Score")) >= 90);
        // Eng AND Active AND Score>=90: only Alice (Eng, Active, 92)
        Assert.Equal(1, result.Count);
        Assert.Equal("Alice", result.RecordAt(0).GetField("Name")?.ToString());
    }

    [Fact]
    public void Filter_Chain_EmptyResult()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var result = doc
            .Filter(r => r.GetField("Dept")?.ToString() == "Eng")
            .Filter(r => r.GetField("Dept")?.ToString() == "Finance");
        Assert.Equal(0, result.Count);
    }

    [Fact]
    public void Filter_ThenSaveToFile_CreatesFile()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var filtered = doc.Filter(r => r.GetField("Dept")?.ToString() == "Eng");
        var path = TempFile("filtered.ndjson");
        filtered.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void Filter_ThenSaveToFile_CorrectCount()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var engOnly = doc.Filter(r => r.GetField("Dept")?.ToString() == "Eng");
        var path = TempFile("eng_only.ndjson");
        engOnly.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(2, loaded.Count); // Alice and Carol
    }

    [Fact]
    public void Filter_PreservesRecordStructure()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var filtered = doc.Filter(r => r.GetField("Dept")?.ToString() == "Eng");
        var keys = filtered.GetAllKeys();
        Assert.Contains("Name", keys);
        Assert.Contains("Dept", keys);
        Assert.Contains("Score", keys);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_AppendRecord_Filter_SaveToFile_LoadFile_Verify_Pipeline()
    {
        // Write and LoadFile
        var path = WriteSampleFile("dogfood_input.ndjson");
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(5, doc.Count);

        // AppendRecord
        var newRecord = new Dictionary<string, object?> { ["Name"] = "Frank", ["Dept"] = "Eng", ["Score"] = 95, ["Active"] = true };
        var extended = doc.AppendRecord(newRecord);
        Assert.Equal(6, extended.Count);

        // Filter by Eng
        var engOnly = extended.Filter(r => r.GetField("Dept")?.ToString() == "Eng");
        Assert.Equal(3, engOnly.Count); // Alice, Carol, Frank

        // SaveToFile filtered result
        var savedPath = TempFile("dogfood_eng.ndjson");
        engOnly.SaveToFile(savedPath);
        Assert.True(File.Exists(savedPath));

        // LoadFile from saved
        var loaded = NdjsonDocument.LoadFile(savedPath);
        Assert.Equal(3, loaded.Count);

        // Verify data
        var names = loaded.GetFieldValues("Name");
        Assert.Contains("Alice", names.ConvertAll(v => v?.ToString() ?? ""));
        Assert.Contains("Frank", names.ConvertAll(v => v?.ToString() ?? ""));

        // Filter chain on loaded
        var activeHighScore = loaded.Filter(r =>
            Convert.ToBoolean(r.GetField("Active")) &&
            Convert.ToDouble(r.GetField("Score")) >= 90);
        Assert.Equal(2, activeHighScore.Count); // Alice (92, active) and Frank (95, active)

        // ToNdjson and verify
        var ndjson = activeHighScore.ToNdjson();
        Assert.Contains("Alice", ndjson);
        Assert.Contains("Frank", ndjson);
        Assert.DoesNotContain("Carol", ndjson);
    }
}
