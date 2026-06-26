// Tests for NdjsonWriter.WriteToFile, NdjsonCsvExporter deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R169

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R169: Tests for NdjsonWriter.WriteToFile, NdjsonCsvExporter deeper coverage.
/// NdjsonWriter.WriteToFile(doc, path): writes NDJSON doc to file.
/// NdjsonCsvExporter.ToCsvString(doc): converts doc to CSV string.
/// NdjsonCsvExporter.WriteToFile(doc, path): writes CSV to file.
/// NdjsonDocument.SaveToFile(path): alias for WriteToFile.
/// Covers: WriteToFile creates file; WriteToFile->LoadFile count matches;
/// WriteToFile->LoadFile values correct; WriteToFile empty doc creates file;
/// SaveToFile creates file; SaveToFile->LoadFile count; SaveToFile->LoadFile values;
/// CsvExporter ToCsvString after WriteToFile; CsvExporter WriteToFile creates file;
/// CsvExporter WriteToFile content has Alice; Filter->SaveToFile->LoadFile;
/// WriteToFile multiple documents same path overwrites; SaveToFile->LoadFile->Filter;
/// CsvExporter after Filter contains filtered rows;
/// dogfood Load->Filter->WriteToFile->LoadFile->SaveToFile->LoadFile->CsvExporter.
/// </summary>
public class NdjsonR169CsvExporterAndWriterDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string ThreeRecordNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":88}";

    public NdjsonR169CsvExporterAndWriterDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR169_" + Guid.NewGuid().ToString("N"));
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
        var path = TempFile("out.ndjson");
        NdjsonWriter.WriteToFile(doc, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_LoadFile_CountMatches()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("count.ndjson");
        NdjsonWriter.WriteToFile(doc, path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, loaded.Count);
    }

    [Fact]
    public void WriteToFile_LoadFile_ValuesCorrect()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("vals.ndjson");
        NdjsonWriter.WriteToFile(doc, path);
        var loaded = NdjsonDocument.LoadFile(path);
        var names = loaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void WriteToFile_EmptyDoc_CreatesFile()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        var path = TempFile("empty.ndjson");
        NdjsonWriter.WriteToFile(doc, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_OverwritesPreviousContent()
    {
        var doc1 = NdjsonDocument.Load("{\"id\":1}");
        var path = TempFile("overwrite.ndjson");
        NdjsonWriter.WriteToFile(doc1, path);

        var doc2 = NdjsonDocument.Load(ThreeRecordNdjson);
        NdjsonWriter.WriteToFile(doc2, path);

        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, loaded.Count);
    }

    // -------------------------------------------------------------------------
    // SaveToFile (alias)
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("save.ndjson");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_LoadFile_CountMatches()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("savecount.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, loaded.Count);
    }

    [Fact]
    public void SaveToFile_LoadFile_ThenFilter_Works()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("savefilter.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var eng = loaded.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);
    }

    // -------------------------------------------------------------------------
    // NdjsonCsvExporter
    // -------------------------------------------------------------------------

    [Fact]
    public void CsvExporter_ToCsvString_ContainsAlice()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var csv = NdjsonCsvExporter.ToCsvString(doc);
        Assert.Contains("Alice", csv);
    }

    [Fact]
    public void CsvExporter_WriteToFile_CreatesFile()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("export.csv");
        NdjsonCsvExporter.WriteToFile(doc, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void CsvExporter_AfterFilter_ContainsFilteredRows()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var csv = NdjsonCsvExporter.ToCsvString(eng);
        Assert.Contains("Alice", csv);
        Assert.DoesNotContain("Bob", csv);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->WriteToFile->LoadFile->SaveToFile->LoadFile->CsvExporter
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterWriteLoadSaveLoadCsvExport_Pipeline()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(3, doc.Count);

        // Filter
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);

        // WriteToFile
        var path1 = TempFile("eng1.ndjson");
        NdjsonWriter.WriteToFile(eng, path1);
        var loaded1 = NdjsonDocument.LoadFile(path1);
        Assert.Equal(2, loaded1.Count);

        // SaveToFile
        var path2 = TempFile("eng2.ndjson");
        loaded1.SaveToFile(path2);
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(2, loaded2.Count);

        // CsvExporter
        var csv = NdjsonCsvExporter.ToCsvString(loaded2);
        Assert.Contains("Alice", csv);
        Assert.Contains("Carol", csv);
        Assert.DoesNotContain("Bob", csv);

        // CsvExporter.WriteToFile
        var csvPath = TempFile("eng.csv");
        NdjsonCsvExporter.WriteToFile(loaded2, csvPath);
        Assert.True(File.Exists(csvPath));
        var csvContent = File.ReadAllText(csvPath);
        Assert.Contains("Alice", csvContent);
    }
}
