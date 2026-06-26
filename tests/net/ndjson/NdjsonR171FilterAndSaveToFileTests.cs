// Tests for NdjsonDocument.Filter, SaveToFile, and NdjsonWriter deep coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R171

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R171: Tests for NdjsonDocument.Filter, SaveToFile, NdjsonWriter deeper coverage.
/// Filter(predicate): returns new NdjsonDocument with matching records.
/// SaveToFile(path): writes NDJSON content to file.
/// NdjsonWriter.WriteToFile(doc, path): writes document to file.
/// Covers: Filter non-null; Filter count correct; Filter non-matching empty;
/// Filter chain narrows result; Filter preserves TypedRecords;
/// SaveToFile creates file; SaveToFile non-empty; SaveToFile values correct;
/// SaveToFile->LoadFile round-trip; Filter->SaveToFile->LoadFile chain;
/// NdjsonWriter.WriteToFile creates file; NdjsonWriter count preserved;
/// Filter->NdjsonWriter.WriteToFile->LoadFile verify;
/// dogfood Load->Filter->SaveToFile->LoadFile->Filter->NdjsonWriter.WriteToFile->LoadFile verify.
/// </summary>
public class NdjsonR171FilterAndSaveToFileTests : IDisposable
{
    private readonly string _tempDir;

    private const string FourRecordNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":88}\n" +
        "{\"name\":\"Dave\",\"dept\":\"HR\",\"score\":76}";

    public NdjsonR171FilterAndSaveToFileTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR171_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_NonNull()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var result = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.NotNull(result);
    }

    [Fact]
    public void Filter_ByDept_Eng_CountIsTwo()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);
    }

    [Fact]
    public void Filter_NonMatching_ReturnsEmpty()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var none = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Marketing");
        Assert.Equal(0, none.Count);
    }

    [Fact]
    public void Filter_Chain_NarrowsResult()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var highScore = eng.Filter(el =>
            el.TryGetProperty("score", out var s) && s.GetInt32() > 90);
        Assert.Equal(1, highScore.Count);
    }

    [Fact]
    public void Filter_PreservesTypedRecords()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(eng.Count, eng.TypedRecords.Count);
    }

    // -------------------------------------------------------------------------
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var path = TempFile("out.ndjson");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileNonEmpty()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var path = TempFile("nonempty.ndjson");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.False(string.IsNullOrWhiteSpace(content));
    }

    [Fact]
    public void SaveToFile_ValuesPreserved()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var path = TempFile("vals.ndjson");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("Dave", content);
    }

    [Fact]
    public void SaveToFile_LoadFile_RoundTrip_CountMatches()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var path = TempFile("rt.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(4, loaded.Count);
    }

    [Fact]
    public void Filter_SaveToFile_LoadFile_ChainCount()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var path = TempFile("eng.ndjson");
        eng.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(2, loaded.Count);
    }

    // -------------------------------------------------------------------------
    // NdjsonWriter.WriteToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonWriter_WriteToFile_CreatesFile()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var path = TempFile("writer.ndjson");
        NdjsonWriter.WriteToFile(doc, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void NdjsonWriter_WriteToFile_LoadFile_CountPreserved()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var path = TempFile("writer2.ndjson");
        NdjsonWriter.WriteToFile(doc, path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(4, loaded.Count);
    }

    [Fact]
    public void Filter_NdjsonWriter_WriteToFile_LoadFile_Verify()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var path = TempFile("eng_writer.ndjson");
        NdjsonWriter.WriteToFile(eng, path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(2, loaded.Count);
        var names = loaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterSaveLoadFilterWriterLoadVerify_Pipeline()
    {
        // Load
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        Assert.Equal(4, doc.Count);

        // Filter Eng
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);

        // SaveToFile
        var path1 = TempFile("step1.ndjson");
        eng.SaveToFile(path1);

        // LoadFile
        var loaded1 = NdjsonDocument.LoadFile(path1);
        Assert.Equal(2, loaded1.Count);

        // Filter by score > 90
        var highScore = loaded1.Filter(el =>
            el.TryGetProperty("score", out var s) && s.GetInt32() > 90);
        Assert.Equal(1, highScore.Count);

        // NdjsonWriter.WriteToFile
        var path2 = TempFile("step2.ndjson");
        NdjsonWriter.WriteToFile(highScore, path2);

        // LoadFile final
        var final = NdjsonDocument.LoadFile(path2);
        Assert.Equal(1, final.Count);
        var names = final.GetFieldValues("name");
        Assert.Contains("Alice", names);
    }
}
