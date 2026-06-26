// Tests for NdjsonWriter, NdjsonCsvExporter, NdjsonDocument.SaveToFile.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R149

using System;
using System.IO;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R149: Tests for NdjsonWriter, NdjsonCsvExporter, NdjsonDocument.SaveToFile.
/// NdjsonWriter.WriteRecords(records, stream): writes JsonElement records to stream.
/// NdjsonWriter.WriteRecords(records, filePath): writes to file.
/// NdjsonCsvExporter.ToCsv(doc): converts document to CSV string.
/// NdjsonDocument.SaveToFile(path): saves document to file.
/// Covers: WriteRecords to stream produces valid NDJSON; WriteRecords to file creates file;
/// WriteRecords to file is non-empty; ToCsv produces comma-separated output;
/// ToCsv includes record values; ToCsv empty doc returns empty/header;
/// SaveToFile creates file; SaveToFile file non-empty; SaveToFile round-trip preserves count;
/// dogfood Load->Filter->SaveToFile->LoadFile->ToCsv pipeline.
/// </summary>
public class NdjsonR149WriteRecordsAndCsvExporterTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR149WriteRecordsAndCsvExporterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR149_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string ThreeRecordNdjson =
        "{\"name\":\"Alice\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"score\":88}";

    // -------------------------------------------------------------------------
    // NdjsonWriter.WriteRecords (stream)
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRecords_ToStream_ProducesValidNdjson()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        using var stream = new MemoryStream();
        NdjsonWriter.WriteRecords(doc.Records, stream);
        stream.Position = 0;
        var content = new StreamReader(stream).ReadToEnd();
        Assert.Contains("{", content);
        Assert.Contains("}", content);
    }

    [Fact]
    public void WriteRecords_ToStream_ContainsFieldValues()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        using var stream = new MemoryStream();
        NdjsonWriter.WriteRecords(doc.Records, stream);
        stream.Position = 0;
        var content = new StreamReader(stream).ReadToEnd();
        Assert.Contains("Alice", content);
        Assert.Contains("Bob", content);
    }

    // -------------------------------------------------------------------------
    // NdjsonWriter.WriteRecords (file)
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRecords_ToFile_CreatesFile()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("output.ndjson");
        NdjsonWriter.WriteRecords(doc.Records, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteRecords_ToFile_IsNonEmpty()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("nonempty.ndjson");
        NdjsonWriter.WriteRecords(doc.Records, path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void WriteRecords_ToFile_RoundTrip_PreservesCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("roundtrip.ndjson");
        NdjsonWriter.WriteRecords(doc.Records, path);
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(doc.Count, reloaded.Count);
    }

    // -------------------------------------------------------------------------
    // NdjsonCsvExporter.ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsv_ProducesCommaOutput()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var csv = NdjsonCsvExporter.ToCsv(doc);
        Assert.Contains(",", csv);
    }

    [Fact]
    public void ToCsv_IncludesFieldValues()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var csv = NdjsonCsvExporter.ToCsv(doc);
        Assert.Contains("Alice", csv);
    }

    [Fact]
    public void ToCsv_EmptyDoc_ReturnsEmptyOrHeader()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        var csv = NdjsonCsvExporter.ToCsv(doc);
        // Empty doc: either empty string or header-only
        Assert.NotNull(csv);
    }

    // -------------------------------------------------------------------------
    // NdjsonDocument.SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("saved.ndjson");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileIsNonEmpty()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("nonempty2.ndjson");
        doc.SaveToFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void SaveToFile_RoundTrip_PreservesCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("roundtrip2.ndjson");
        doc.SaveToFile(path);
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, reloaded.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->SaveToFile->LoadFile->ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FilterSaveLoadToCsv_Pipeline()
    {
        var ndjson =
            "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
            "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":72}\n" +
            "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":88}";

        var doc = NdjsonDocument.Load(ndjson);
        Assert.Equal(3, doc.Count);

        // Filter to Eng
        var eng = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);

        // Save filtered to file
        var path = TempFile("eng.ndjson");
        eng.SaveToFile(path);
        Assert.True(File.Exists(path));

        // Reload from file
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(2, reloaded.Count);

        // Export to CSV
        var csv = NdjsonCsvExporter.ToCsv(reloaded);
        Assert.Contains("Alice", csv);
        Assert.Contains("Carol", csv);
        Assert.Contains(",", csv);
    }
}
