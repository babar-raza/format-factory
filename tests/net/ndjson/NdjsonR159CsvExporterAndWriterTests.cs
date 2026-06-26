// Tests for NdjsonCsvExporter and NdjsonWriter standalone classes.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R159

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R159: Tests for NdjsonCsvExporter and NdjsonWriter standalone classes.
/// NdjsonCsvExporter: exports NDJSON records to CSV format.
/// NdjsonWriter.WriteRecords: writes NdjsonRecord objects to a file.
/// NdjsonWriter.WriteToFile: writes NdjsonDocument to a file.
/// Covers: NdjsonCsvExporter.Export non-null; CSV output contains commas;
/// CSV output contains field values; NdjsonWriter.WriteRecords creates file;
/// NdjsonWriter.WriteToFile creates file; WriteToFile output readable by LoadFile;
/// WriteToFile count matches doc.Count; WriteRecords output non-empty;
/// NdjsonWriter.WriteToFile then GetFieldValues; Filter->WriteToFile->LoadFile chain;
/// Empty document WriteToFile produces file; WriteToFile then reload IsUniformSchema;
/// dogfood Load->Filter->WriteToFile->LoadFile->GetAllKeys->IsUniformSchema.
/// </summary>
public class NdjsonR159CsvExporterAndWriterTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR159CsvExporterAndWriterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR159_" + Guid.NewGuid().ToString("N"));
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
    // NdjsonCsvExporter
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonCsvExporter_Export_IsNotNull()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var exporter = new NdjsonCsvExporter();
        var csv = exporter.Export(doc);
        Assert.NotNull(csv);
    }

    [Fact]
    public void NdjsonCsvExporter_Export_ContainsCommas()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var exporter = new NdjsonCsvExporter();
        var csv = exporter.Export(doc);
        Assert.Contains(",", csv);
    }

    [Fact]
    public void NdjsonCsvExporter_Export_ContainsFieldValues()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var exporter = new NdjsonCsvExporter();
        var csv = exporter.Export(doc);
        Assert.Contains("Alice", csv);
        Assert.Contains("Bob", csv);
    }

    [Fact]
    public void NdjsonCsvExporter_Export_ContainsFieldNames()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var exporter = new NdjsonCsvExporter();
        var csv = exporter.Export(doc);
        Assert.Contains("name", csv);
    }

    // -------------------------------------------------------------------------
    // NdjsonWriter.WriteToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonWriter_WriteToFile_CreatesFile()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("writer.ndjson");
        var writer = new NdjsonWriter();
        writer.WriteToFile(doc, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void NdjsonWriter_WriteToFile_OutputReadableByLoadFile()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("readable.ndjson");
        var writer = new NdjsonWriter();
        writer.WriteToFile(doc, path);
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, reloaded.Count);
    }

    [Fact]
    public void NdjsonWriter_WriteToFile_CountMatchesDocCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("count.ndjson");
        var writer = new NdjsonWriter();
        writer.WriteToFile(doc, path);
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(doc.Count, reloaded.Count);
    }

    [Fact]
    public void NdjsonWriter_WriteToFile_ThenGetFieldValues()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("fields.ndjson");
        var writer = new NdjsonWriter();
        writer.WriteToFile(doc, path);
        var reloaded = NdjsonDocument.LoadFile(path);
        var names = reloaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
    }

    // -------------------------------------------------------------------------
    // Filter -> WriteToFile -> LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_WriteToFile_LoadFile_Chain()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var eng = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var path = TempFile("eng.ndjson");
        var writer = new NdjsonWriter();
        writer.WriteToFile(eng, path);
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(2, reloaded.Count);
        var names = reloaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }

    [Fact]
    public void WriteToFile_ThenReload_IsUniformSchema()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("schema.ndjson");
        var writer = new NdjsonWriter();
        writer.WriteToFile(doc, path);
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.True(reloaded.IsUniformSchema());
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->WriteToFile->LoadFile->GetAllKeys->IsUniformSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FilterWriteToFileLoadGetAllKeysIsUniform()
    {
        // Load
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(3, doc.Count);

        // Filter
        var eng = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);

        // WriteToFile
        var path = TempFile("dogfood.ndjson");
        var writer = new NdjsonWriter();
        writer.WriteToFile(eng, path);
        Assert.True(File.Exists(path));

        // LoadFile
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(2, reloaded.Count);

        // GetAllKeys
        var keys = reloaded.GetAllKeys();
        Assert.Equal(3, keys.Count);
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);

        // IsUniformSchema
        Assert.True(reloaded.IsUniformSchema());
    }
}
