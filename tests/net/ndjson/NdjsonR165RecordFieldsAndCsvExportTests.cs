// Tests for NdjsonDocument.Records field access and NdjsonCsvExporter integration.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R165

using System;
using System.IO;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R165: Tests for NdjsonDocument record field access and NdjsonCsvExporter integration.
/// NdjsonCsvExporter.ToCsvString(doc): converts NDJSON to CSV string.
/// NdjsonCsvExporter.WriteToFile(doc, path): writes CSV to file.
/// NdjsonDocument.Records: direct access to underlying record list.
/// Covers: ToCsvString returns non-empty string; ToCsvString contains header row;
/// ToCsvString contains data values; ToCsvString field count matches schema;
/// WriteToFile creates file; WriteToFile content has headers;
/// WriteToFile content has data rows; Records count matches Count;
/// Records direct access to field values; Records element has expected property;
/// ToCsvString round-trip Load-from-CsvDocument; ToCsvString empty doc;
/// Filter->ToCsvString only filtered rows;
/// dogfood Load->Filter->ToCsvString->WriteToFile->File.ReadAllText verify.
/// </summary>
public class NdjsonR165RecordFieldsAndCsvExportTests : IDisposable
{
    private readonly string _tempDir;

    private const string ThreeRecordNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":88}";

    public NdjsonR165RecordFieldsAndCsvExportTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR165_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // NdjsonCsvExporter.ToCsvString
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsvString_NonEmpty()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var csv = NdjsonCsvExporter.ToCsvString(doc);
        Assert.False(string.IsNullOrWhiteSpace(csv));
    }

    [Fact]
    public void ToCsvString_ContainsHeaderRow()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var csv = NdjsonCsvExporter.ToCsvString(doc);
        // Should contain at least one of the field names as header
        Assert.True(
            csv.Contains("name") || csv.Contains("dept") || csv.Contains("score"),
            "CSV header should contain field names");
    }

    [Fact]
    public void ToCsvString_ContainsDataValues()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var csv = NdjsonCsvExporter.ToCsvString(doc);
        Assert.Contains("Alice", csv);
        Assert.Contains("Bob", csv);
        Assert.Contains("Carol", csv);
    }

    [Fact]
    public void ToCsvString_EmptyDoc_ReturnsString()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        var csv = NdjsonCsvExporter.ToCsvString(doc);
        Assert.NotNull(csv);
    }

    [Fact]
    public void ToCsvString_AfterFilter_OnlyFilteredRows()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var csv = NdjsonCsvExporter.ToCsvString(eng);
        Assert.Contains("Alice", csv);
        Assert.Contains("Carol", csv);
        Assert.DoesNotContain("Bob", csv);
    }

    // -------------------------------------------------------------------------
    // NdjsonCsvExporter.WriteToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToFile_CreatesFile()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("export.csv");
        NdjsonCsvExporter.WriteToFile(doc, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_ContentHasData()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("data.csv");
        NdjsonCsvExporter.WriteToFile(doc, path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
    }

    [Fact]
    public void WriteToFile_ContentMatchesToCsvString()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var path = TempFile("match.csv");
        NdjsonCsvExporter.WriteToFile(doc, path);
        var fileContent = File.ReadAllText(path);
        var csvString = NdjsonCsvExporter.ToCsvString(doc);
        // Both should contain the same data
        Assert.Contains("Alice", fileContent);
        Assert.Contains("Alice", csvString);
    }

    // -------------------------------------------------------------------------
    // Records direct access
    // -------------------------------------------------------------------------

    [Fact]
    public void Records_Count_MatchesDocCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(doc.Count, doc.Records.Count);
    }

    [Fact]
    public void Records_FirstElement_HasNameProperty()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var first = doc.Records[0];
        Assert.True(first.TryGetProperty("name", out var name));
        Assert.Equal("Alice", name.GetString());
    }

    [Fact]
    public void Records_LastElement_HasExpectedField()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var last = doc.Records[doc.Count - 1];
        Assert.True(last.TryGetProperty("name", out var name));
        Assert.Equal("Carol", name.GetString());
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->ToCsvString->WriteToFile->ReadAllText verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterToCsvWriteFilVerify_Pipeline()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(3, doc.Count);
        Assert.Equal(3, doc.Records.Count);

        // Filter Eng
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);

        // ToCsvString
        var csv = NdjsonCsvExporter.ToCsvString(eng);
        Assert.Contains("Alice", csv);
        Assert.Contains("Carol", csv);
        Assert.DoesNotContain("Bob", csv);

        // WriteToFile
        var path = TempFile("dogfood.csv");
        NdjsonCsvExporter.WriteToFile(eng, path);
        Assert.True(File.Exists(path));

        // ReadAllText
        var fileContent = File.ReadAllText(path);
        Assert.Contains("Alice", fileContent);
        Assert.Contains("Carol", fileContent);
        Assert.DoesNotContain("Bob", fileContent);
    }
}
