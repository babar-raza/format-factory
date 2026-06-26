// Tests for FodsDocument export methods: ExportSheetToCsv, ExportSheetToJson, ExportSheetToMarkdown.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R179

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R179: Tests for FodsDocument export methods: CSV, JSON, Markdown, TSV, HTML.
/// ExportSheetToCsv(sheetName): exports named sheet to CSV string.
/// ExportSheetToJson(sheetName): exports named sheet to JSON string.
/// ExportSheetToMarkdown(sheetName): exports named sheet to Markdown table string.
/// ExportSheetToCsvFile(sheetName, filePath): writes CSV to disk.
/// Covers: ExportSheetToCsv is non-empty; ExportSheetToCsv contains values;
/// ExportSheetToCsv has commas; ExportSheetToJson is non-empty;
/// ExportSheetToJson contains values; ExportSheetToMarkdown is non-empty;
/// ExportSheetToMarkdown has pipes; ExportSheetToHtml is non-empty;
/// ExportSheetToHtml contains table tags; ExportSheetToCsvFile creates file;
/// ExportSheetToCsvFile content contains values; ExportSheetToCsv() overload;
/// dogfood Build->Export CSV+JSON+Markdown+HTML pipeline.
/// </summary>
public class FodsR179ExportSheetCsvTsvJsonTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR179ExportSheetCsvTsvJsonTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR179_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument BuildDoc()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.GetSheetNames()[0];
        doc.InsertRowWithValues(sheetName, 0, new[] { "Name", "Dept", "Score" });
        doc.InsertRowWithValues(sheetName, 1, new[] { "Alice", "Eng", "95" });
        doc.InsertRowWithValues(sheetName, 2, new[] { "Bob", "Finance", "82" });
        doc.InsertRowWithValues(sheetName, 3, new[] { "Carol", "Eng", "88" });
        return doc;
    }

    private static string GetSheetName(FodsDocument doc) => doc.GetSheetNames()[0];

    // -------------------------------------------------------------------------
    // ExportSheetToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToCsv_IsNonEmpty()
    {
        var doc = BuildDoc();
        var csv = doc.ExportSheetToCsv(GetSheetName(doc));
        Assert.False(string.IsNullOrEmpty(csv));
    }

    [Fact]
    public void ExportSheetToCsv_ContainsValues()
    {
        var doc = BuildDoc();
        var csv = doc.ExportSheetToCsv(GetSheetName(doc));
        Assert.Contains("Alice", csv);
        Assert.Contains("Bob", csv);
    }

    [Fact]
    public void ExportSheetToCsv_HasCommas()
    {
        var doc = BuildDoc();
        var csv = doc.ExportSheetToCsv(GetSheetName(doc));
        Assert.Contains(",", csv);
    }

    [Fact]
    public void ExportSheetToCsv_DefaultOverload_IsNonEmpty()
    {
        var doc = BuildDoc();
        var csv = doc.ExportSheetToCsv();
        Assert.False(string.IsNullOrEmpty(csv));
    }

    // -------------------------------------------------------------------------
    // ExportSheetToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToJson_IsNonEmpty()
    {
        var doc = BuildDoc();
        var json = doc.ExportSheetToJson(GetSheetName(doc));
        Assert.False(string.IsNullOrEmpty(json));
    }

    [Fact]
    public void ExportSheetToJson_ContainsValues()
    {
        var doc = BuildDoc();
        var json = doc.ExportSheetToJson(GetSheetName(doc));
        Assert.Contains("Alice", json);
    }

    [Fact]
    public void ExportSheetToJson_DefaultOverload_IsNonEmpty()
    {
        var doc = BuildDoc();
        var json = doc.ExportSheetToJson();
        Assert.False(string.IsNullOrEmpty(json));
    }

    // -------------------------------------------------------------------------
    // ExportSheetToMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToMarkdown_IsNonEmpty()
    {
        var doc = BuildDoc();
        var md = doc.ExportSheetToMarkdown(GetSheetName(doc));
        Assert.False(string.IsNullOrEmpty(md));
    }

    [Fact]
    public void ExportSheetToMarkdown_HasPipes()
    {
        var doc = BuildDoc();
        var md = doc.ExportSheetToMarkdown(GetSheetName(doc));
        Assert.Contains("|", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_ContainsHeaders()
    {
        var doc = BuildDoc();
        var md = doc.ExportSheetToMarkdown(GetSheetName(doc));
        Assert.Contains("Name", md);
        Assert.Contains("Dept", md);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToHtml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToHtml_IsNonEmpty()
    {
        var doc = BuildDoc();
        var html = doc.ExportSheetToHtml(GetSheetName(doc));
        Assert.False(string.IsNullOrEmpty(html));
    }

    [Fact]
    public void ExportSheetToHtml_ContainsTableTags()
    {
        var doc = BuildDoc();
        var html = doc.ExportSheetToHtml(GetSheetName(doc));
        Assert.Contains("table", html, StringComparison.OrdinalIgnoreCase);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToCsvFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToCsvFile_CreatesFile()
    {
        var doc = BuildDoc();
        var path = TempFile("export.csv");
        doc.ExportSheetToCsvFile(GetSheetName(doc), path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportSheetToCsvFile_ContentContainsValues()
    {
        var doc = BuildDoc();
        var path = TempFile("values.csv");
        doc.ExportSheetToCsvFile(GetSheetName(doc), path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Build->Export CSV+JSON+Markdown+HTML pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ExportAllFormatsPipeline()
    {
        var doc = BuildDoc();
        var sheet = GetSheetName(doc);

        // CSV
        var csv = doc.ExportSheetToCsv(sheet);
        Assert.Contains("Alice", csv);
        Assert.Contains(",", csv);

        // JSON
        var json = doc.ExportSheetToJson(sheet);
        Assert.Contains("Alice", json);

        // Markdown
        var md = doc.ExportSheetToMarkdown(sheet);
        Assert.Contains("|", md);
        Assert.Contains("Name", md);

        // HTML
        var html = doc.ExportSheetToHtml(sheet);
        Assert.Contains("table", html, StringComparison.OrdinalIgnoreCase);

        // File export
        var path = TempFile("all-export.csv");
        doc.ExportSheetToCsvFile(sheet, path);
        Assert.True(File.Exists(path));
        var fileContent = File.ReadAllText(path);
        Assert.Contains("Carol", fileContent);
    }
}
