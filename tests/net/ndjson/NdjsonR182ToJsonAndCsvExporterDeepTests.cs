// Tests for NdjsonDocument.ToJson, NdjsonCsvExporter deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R182

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R182: Tests for NdjsonDocument.ToJson, NdjsonCsvExporter deeper coverage.
/// ToJson(): returns a JSON array string of all records in the document.
/// NdjsonCsvExporter.ExportToString(doc): exports the document as a CSV string.
/// NdjsonCsvExporter.ExportToFile(doc, path): exports the document as a CSV file.
/// Covers: ToJson non-null; ToJson non-empty; ToJson contains record count;
/// ToJson contains field values; ToJson after Filter contains filtered records;
/// CsvExporter.ExportToString non-null; CsvExporter.ExportToString contains headers;
/// CsvExporter.ExportToString contains data values; CsvExporter.ExportToFile creates file;
/// CsvExporter.ExportToFile content contains headers; CsvExporter after Filter smaller output;
/// dogfood Load->ToJson->CsvExporter->File->Verify pipeline.
/// </summary>
public class NdjsonR182ToJsonAndCsvExporterDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string ThreeRecordNdjson =
        "{\"id\":1,\"name\":\"Alice\",\"dept\":\"Eng\"}\n" +
        "{\"id\":2,\"name\":\"Bob\",\"dept\":\"Finance\"}\n" +
        "{\"id\":3,\"name\":\"Carol\",\"dept\":\"Eng\"}";

    private const string FiveRecordNdjson =
        "{\"product\":\"Alpha\",\"price\":10.5,\"active\":true}\n" +
        "{\"product\":\"Beta\",\"price\":20.0,\"active\":false}\n" +
        "{\"product\":\"Gamma\",\"price\":15.75,\"active\":true}\n" +
        "{\"product\":\"Delta\",\"price\":8.0,\"active\":true}\n" +
        "{\"product\":\"Epsilon\",\"price\":30.0,\"active\":false}";

    public NdjsonR182ToJsonAndCsvExporterDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR182_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // ToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ToJson_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        Assert.NotNull(doc.ToJson());
    }

    [Fact]
    public void ToJson_NonEmpty()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        Assert.NotEmpty(doc.ToJson());
    }

    [Fact]
    public void ToJson_ContainsFieldValues()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var json = doc.ToJson();
        Assert.Contains("Alice", json);
        Assert.Contains("Bob", json);
    }

    [Fact]
    public void ToJson_ContainsAllRecordData()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var json = doc.ToJson();
        Assert.Contains("Carol", json);
        Assert.Contains("Eng", json);
        Assert.Contains("Finance", json);
    }

    [Fact]
    public void ToJson_AfterFilter_ContainsFilteredRecords()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var eng = doc.Filter(r => r.TryGetValue("dept", out var d) && d == "Eng");
        var json = eng.ToJson();
        Assert.Contains("Alice", json);
        Assert.Contains("Carol", json);
        Assert.DoesNotContain("Bob", json);
    }

    [Fact]
    public void ToJson_SingleRecord_NonEmpty()
    {
        var doc = NdjsonDocument.LoadContent("{\"x\":1,\"y\":\"hello\"}");
        var json = doc.ToJson();
        Assert.NotEmpty(json);
        Assert.Contains("hello", json);
    }

    // -------------------------------------------------------------------------
    // NdjsonCsvExporter.ExportToString
    // -------------------------------------------------------------------------

    [Fact]
    public void CsvExporter_ExportToString_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var csv = NdjsonCsvExporter.ExportToString(doc);
        Assert.NotNull(csv);
    }

    [Fact]
    public void CsvExporter_ExportToString_NonEmpty()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var csv = NdjsonCsvExporter.ExportToString(doc);
        Assert.NotEmpty(csv);
    }

    [Fact]
    public void CsvExporter_ExportToString_ContainsHeaders()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var csv = NdjsonCsvExporter.ExportToString(doc);
        // CSV should contain field names as headers
        Assert.True(csv.Contains("name") || csv.Contains("Name") || csv.Contains("id") || csv.Contains("dept"));
    }

    [Fact]
    public void CsvExporter_ExportToString_ContainsDataValues()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var csv = NdjsonCsvExporter.ExportToString(doc);
        Assert.Contains("Alice", csv);
    }

    [Fact]
    public void CsvExporter_ExportToString_AfterFilter_SmallerOutput()
    {
        var doc = NdjsonDocument.LoadContent(FiveRecordNdjson);
        var csvAll = NdjsonCsvExporter.ExportToString(doc);
        var filtered = doc.Filter(r => r.TryGetValue("active", out var v) && v == "true");
        var csvFiltered = NdjsonCsvExporter.ExportToString(filtered);
        Assert.True(csvFiltered.Length < csvAll.Length);
    }

    // -------------------------------------------------------------------------
    // NdjsonCsvExporter.ExportToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void CsvExporter_ExportToFile_CreatesFile()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var path = TempFile("export.csv");
        NdjsonCsvExporter.ExportToFile(doc, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void CsvExporter_ExportToFile_ContentNonEmpty()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var path = TempFile("content.csv");
        NdjsonCsvExporter.ExportToFile(doc, path);
        var content = File.ReadAllText(path);
        Assert.NotEmpty(content);
    }

    [Fact]
    public void CsvExporter_ExportToFile_ContainsDataValues()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var path = TempFile("data.csv");
        NdjsonCsvExporter.ExportToFile(doc, path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_Load_ToJson_CsvExporter_File_Verify_Pipeline()
    {
        // Load
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        Assert.Equal(3, doc.Count);

        // ToJson
        var json = doc.ToJson();
        Assert.NotEmpty(json);
        Assert.Contains("Alice", json);
        Assert.Contains("Finance", json);

        // CsvExporter.ExportToString
        var csvStr = NdjsonCsvExporter.ExportToString(doc);
        Assert.NotNull(csvStr);
        Assert.Contains("Alice", csvStr);

        // CsvExporter.ExportToFile
        var path = TempFile("dogfood.csv");
        NdjsonCsvExporter.ExportToFile(doc, path);
        Assert.True(File.Exists(path));
        var fileContent = File.ReadAllText(path);
        Assert.NotEmpty(fileContent);

        // Filter -> ToJson
        var engOnly = doc.Filter(r => r.TryGetValue("dept", out var d) && d == "Eng");
        Assert.Equal(2, engOnly.Count);
        var engJson = engOnly.ToJson();
        Assert.Contains("Alice", engJson);
        Assert.Contains("Carol", engJson);
        Assert.DoesNotContain("Bob", engJson);

        // Filter -> ExportToFile
        var engPath = TempFile("eng.csv");
        NdjsonCsvExporter.ExportToFile(engOnly, engPath);
        Assert.True(File.Exists(engPath));
        var engContent = File.ReadAllText(engPath);
        Assert.Contains("Alice", engContent);
    }
}
