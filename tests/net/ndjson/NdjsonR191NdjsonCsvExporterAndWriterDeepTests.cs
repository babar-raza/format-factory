// Tests for NdjsonCsvExporter and NdjsonWriter deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R191

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R191: Tests for NdjsonCsvExporter and NdjsonWriter deeper coverage.
/// NdjsonCsvExporter.ExportToCsv(doc, path): exports NDJSON document as CSV file.
/// NdjsonCsvExporter.ExportToCsvString(doc): returns CSV as string.
/// NdjsonWriter.WriteToFile(records, path): writes list of records to NDJSON file.
/// NdjsonWriter.WriteToString(records): returns NDJSON string.
/// Covers: ExportToCsv creates file; ExportToCsv file non-empty; ExportToCsv has comma;
/// ExportToCsv has headers; ExportToCsv has data; ExportToCsvString non-null;
/// ExportToCsvString has comma; ExportToCsvString has headers/data;
/// ExportToCsvString after Filter smaller; ExportToCsvString after AppendRecord includes new;
/// WriteToFile creates file; WriteToFile non-empty; WriteToFile parseable;
/// WriteToString non-null; WriteToString non-empty; WriteToString parseable;
/// WriteToString after LoadContent round-trip;
/// dogfood LoadContent→Filter→ExportToCsv→ExportToCsvString→WriteToFile→WriteToString pipeline.
/// </summary>
public class NdjsonR191NdjsonCsvExporterAndWriterDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR191NdjsonCsvExporterAndWriterDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR191_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleNdjson =
        "{\"Name\":\"Alice\",\"Score\":92,\"Dept\":\"Engineering\",\"Active\":true}\n" +
        "{\"Name\":\"Bob\",\"Score\":78,\"Dept\":\"Finance\",\"Active\":false}\n" +
        "{\"Name\":\"Carol\",\"Score\":85,\"Dept\":\"Engineering\",\"Active\":true}\n" +
        "{\"Name\":\"Dave\",\"Score\":71,\"Dept\":\"HR\",\"Active\":false}\n" +
        "{\"Name\":\"Eve\",\"Score\":90,\"Dept\":\"Finance\",\"Active\":true}\n";

    private NdjsonDocument LoadSample()
    {
        var path = TempFile("sample.ndjson");
        File.WriteAllText(path, SampleNdjson);
        return NdjsonDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // NdjsonCsvExporter.ExportToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToCsv_CreatesFile()
    {
        var doc = LoadSample();
        var path = TempFile("export.csv");
        NdjsonCsvExporter.ExportToCsv(doc, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToCsv_FileNonEmpty()
    {
        var doc = LoadSample();
        var path = TempFile("nonempty.csv");
        NdjsonCsvExporter.ExportToCsv(doc, path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void ExportToCsv_HasCommaChar()
    {
        var doc = LoadSample();
        var path = TempFile("comma.csv");
        NdjsonCsvExporter.ExportToCsv(doc, path);
        var content = File.ReadAllText(path);
        Assert.Contains(",", content);
    }

    [Fact]
    public void ExportToCsv_HasHeaderData()
    {
        var doc = LoadSample();
        var path = TempFile("headers.csv");
        NdjsonCsvExporter.ExportToCsv(doc, path);
        var content = File.ReadAllText(path);
        Assert.True(content.Contains("Name") || content.Contains("Score"));
    }

    [Fact]
    public void ExportToCsv_HasDataValues()
    {
        var doc = LoadSample();
        var path = TempFile("data.csv");
        NdjsonCsvExporter.ExportToCsv(doc, path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
    }

    // -------------------------------------------------------------------------
    // NdjsonCsvExporter.ExportToCsvString
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToCsvString_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(NdjsonCsvExporter.ExportToCsvString(doc));
    }

    [Fact]
    public void ExportToCsvString_HasComma()
    {
        var doc = LoadSample();
        Assert.Contains(",", NdjsonCsvExporter.ExportToCsvString(doc));
    }

    [Fact]
    public void ExportToCsvString_HasHeaderData()
    {
        var doc = LoadSample();
        var csv = NdjsonCsvExporter.ExportToCsvString(doc);
        Assert.True(csv.Contains("Name") || csv.Contains("Score"));
    }

    [Fact]
    public void ExportToCsvString_ContainsDataValue()
    {
        var doc = LoadSample();
        var csv = NdjsonCsvExporter.ExportToCsvString(doc);
        Assert.Contains("Alice", csv);
    }

    [Fact]
    public void ExportToCsvString_AfterFilter_Smaller()
    {
        var doc = LoadSample();
        var all = NdjsonCsvExporter.ExportToCsvString(doc);
        var filtered = doc.Filter("Dept", "HR");
        var fCsv = NdjsonCsvExporter.ExportToCsvString(filtered);
        Assert.True(fCsv.Length < all.Length);
    }

    [Fact]
    public void ExportToCsvString_AfterAppendRecord_IncludesNew()
    {
        var doc = LoadSample();
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["Name"] = "Frank", ["Score"] = 95, ["Dept"] = "Research", ["Active"] = true
        });
        var csv = NdjsonCsvExporter.ExportToCsvString(doc);
        Assert.Contains("Frank", csv);
    }

    // -------------------------------------------------------------------------
    // NdjsonWriter.WriteToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToFile_CreatesFile()
    {
        var doc = LoadSample();
        var path = TempFile("writer.ndjson");
        NdjsonWriter.WriteRecords(doc, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_NonEmpty()
    {
        var doc = LoadSample();
        var path = TempFile("nonempty_writer.ndjson");
        NdjsonWriter.WriteRecords(doc, path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void WriteToFile_Parseable()
    {
        var doc = LoadSample();
        var path = TempFile("parseable.ndjson");
        NdjsonWriter.WriteRecords(doc, path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.NotNull(loaded);
        Assert.Equal(doc.Count, loaded.Count);
    }

    // -------------------------------------------------------------------------
    // NdjsonWriter.WriteToString
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToString_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(NdjsonWriter.WriteToString(doc));
    }

    [Fact]
    public void WriteToString_NonEmpty()
    {
        var doc = LoadSample();
        Assert.NotEmpty(NdjsonWriter.WriteToString(doc));
    }

    [Fact]
    public void WriteToString_ContainsData()
    {
        var doc = LoadSample();
        var ndjson = NdjsonWriter.WriteToString(doc);
        Assert.Contains("Alice", ndjson);
    }

    [Fact]
    public void WriteToString_Parseable()
    {
        var doc = LoadSample();
        var ndjson = NdjsonWriter.WriteToString(doc);
        var loaded = NdjsonDocument.LoadContent(ndjson);
        Assert.Equal(doc.Count, loaded.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_Filter_ExportToCsv_WriteToFile_WriteToString_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(5, doc.Count);

        // ExportToCsvString
        var csv = NdjsonCsvExporter.ExportToCsvString(doc);
        Assert.NotNull(csv);
        Assert.Contains(",", csv);
        Assert.Contains("Alice", csv);
        Assert.Contains("Engineering", csv);

        // ExportToCsv to file
        var csvPath = TempFile("dogfood.csv");
        NdjsonCsvExporter.ExportToCsv(doc, csvPath);
        Assert.True(File.Exists(csvPath));
        Assert.True(new FileInfo(csvPath).Length > 0);

        // Filter Engineering (3 records)
        var eng = doc.Filter("Dept", "Engineering");
        Assert.Equal(3, eng.Count);

        // ExportToCsvString from filtered — smaller
        var engCsv = NdjsonCsvExporter.ExportToCsvString(eng);
        Assert.True(engCsv.Length < csv.Length);
        Assert.Contains("Alice", engCsv);
        Assert.False(engCsv.Contains("Dave")); // HR

        // WriteToFile
        var ndjsonPath = TempFile("dogfood.ndjson");
        NdjsonWriter.WriteRecords(doc, ndjsonPath);
        Assert.True(File.Exists(ndjsonPath));
        var reloaded = NdjsonDocument.LoadFile(ndjsonPath);
        Assert.Equal(5, reloaded.Count);

        // WriteToString
        var ndjsonStr = NdjsonWriter.WriteToString(doc);
        Assert.NotNull(ndjsonStr);
        Assert.Contains("Alice", ndjsonStr);

        // AppendRecord and re-export
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["Name"] = "Grace", ["Score"] = 91, ["Dept"] = "Engineering", ["Active"] = true
        });
        Assert.Equal(6, doc.Count);

        // ExportToCsvString after append includes Grace
        var updatedCsv = NdjsonCsvExporter.ExportToCsvString(doc);
        Assert.Contains("Grace", updatedCsv);

        // WriteToString after append
        var updatedNdjson = NdjsonWriter.WriteToString(doc);
        Assert.Contains("Grace", updatedNdjson);
    }
}
