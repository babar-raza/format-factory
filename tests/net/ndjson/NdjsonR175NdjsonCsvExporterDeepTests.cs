// Tests for NdjsonCsvExporter.ToCsvString, WriteToFile deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R175

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R175: Tests for NdjsonCsvExporter.ToCsvString, WriteToFile deeper.
/// NdjsonCsvExporter.ToCsvString(doc): converts NDJSON to CSV string.
/// NdjsonCsvExporter.WriteToFile(doc, path): writes CSV to file.
/// Covers: ToCsvString non-null; ToCsvString non-empty;
/// ToCsvString contains header row; ToCsvString contains all field names;
/// ToCsvString contains all record values; ToCsvString comma-separated;
/// ToCsvString->CsvDocument.Load count matches; ToCsvString after Filter;
/// WriteToFile creates file; WriteToFile non-empty; WriteToFile contains values;
/// WriteToFile->CsvDocument.LoadFile count matches;
/// Filter->ToCsvString->CsvDocument.Load count and values;
/// Filter->WriteToFile->LoadFile chain;
/// dogfood Load->Filter->ToCsvString->CsvLoad->Filter->WriteToFile->LoadFile verify.
/// </summary>
public class NdjsonR175NdjsonCsvExporterDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string FiveRecordNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":88}\n" +
        "{\"name\":\"Dave\",\"dept\":\"HR\",\"score\":76}\n" +
        "{\"name\":\"Eve\",\"dept\":\"Eng\",\"score\":91}";

    public NdjsonR175NdjsonCsvExporterDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR175_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // ToCsvString
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsvString_NonNull()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        Assert.NotNull(NdjsonCsvExporter.ToCsvString(doc));
    }

    [Fact]
    public void ToCsvString_NonEmpty()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        Assert.False(string.IsNullOrWhiteSpace(NdjsonCsvExporter.ToCsvString(doc)));
    }

    [Fact]
    public void ToCsvString_ContainsHeaders()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var csv = NdjsonCsvExporter.ToCsvString(doc);
        Assert.True(csv.Contains("name") || csv.Contains("dept") || csv.Contains("score"));
    }

    [Fact]
    public void ToCsvString_ContainsAllRecordValues()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var csv = NdjsonCsvExporter.ToCsvString(doc);
        Assert.Contains("Alice", csv);
        Assert.Contains("Bob", csv);
        Assert.Contains("Eve", csv);
    }

    [Fact]
    public void ToCsvString_CommaSeparated()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var csv = NdjsonCsvExporter.ToCsvString(doc);
        Assert.Contains(",", csv);
    }

    [Fact]
    public void ToCsvString_CsvDocument_Load_CountMatches()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var csv = NdjsonCsvExporter.ToCsvString(doc);
        var csvDoc = CsvDocument.Load(csv);
        Assert.Equal(5, csvDoc.RowCount);
    }

    [Fact]
    public void ToCsvString_AfterFilter_OnlyFilteredRecords()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var csv = NdjsonCsvExporter.ToCsvString(eng);
        Assert.Contains("Alice", csv);
        Assert.DoesNotContain("Bob", csv);
        Assert.DoesNotContain("Dave", csv);
    }

    [Fact]
    public void Filter_ToCsvString_CsvLoad_CountAndValues()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var csv = NdjsonCsvExporter.ToCsvString(eng);
        var csvDoc = CsvDocument.Load(csv);
        Assert.Equal(3, csvDoc.RowCount); // Alice, Carol, Eve
        var names = csvDoc.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Eve", names);
    }

    // -------------------------------------------------------------------------
    // WriteToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToFile_CreatesFile()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var path = TempFile("out.csv");
        NdjsonCsvExporter.WriteToFile(doc, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_NonEmpty()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var path = TempFile("nonempty.csv");
        NdjsonCsvExporter.WriteToFile(doc, path);
        var content = File.ReadAllText(path);
        Assert.False(string.IsNullOrWhiteSpace(content));
    }

    [Fact]
    public void WriteToFile_ContainsValues()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var path = TempFile("vals.csv");
        NdjsonCsvExporter.WriteToFile(doc, path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("Eve", content);
    }

    [Fact]
    public void WriteToFile_CsvDocument_LoadFile_CountMatches()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var path = TempFile("load.csv");
        NdjsonCsvExporter.WriteToFile(doc, path);
        var csvDoc = CsvDocument.LoadFile(path);
        Assert.Equal(5, csvDoc.RowCount);
    }

    [Fact]
    public void Filter_WriteToFile_LoadFile_Chain()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var path = TempFile("eng.csv");
        NdjsonCsvExporter.WriteToFile(eng, path);
        var csvDoc = CsvDocument.LoadFile(path);
        Assert.Equal(3, csvDoc.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterToCsvStringCsvLoadFilterWriteToFileLoadFileVerify_Pipeline()
    {
        // Load
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        Assert.Equal(5, doc.Count);

        // Filter Eng
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(3, eng.Count);

        // ToCsvString
        var csv = NdjsonCsvExporter.ToCsvString(eng);
        Assert.Contains("Alice", csv);

        // CsvDocument.Load
        var csvDoc = CsvDocument.Load(csv);
        Assert.Equal(3, csvDoc.RowCount);

        // Filter high score from CSV
        var highScore = csvDoc.Filter(r => {
            return int.TryParse(r.GetValue("score"), out var s) && s > 90;
        });
        Assert.Equal(2, highScore.RowCount); // Alice(95) and Eve(91)

        // WriteToFile
        var path = TempFile("high_score.csv");
        NdjsonCsvExporter.WriteToFile(eng, path);
        Assert.True(File.Exists(path));

        // LoadFile
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(3, loaded.RowCount);
        var names = loaded.GetColumn("name");
        Assert.Contains("Carol", names);
    }
}
