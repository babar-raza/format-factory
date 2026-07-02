// Tests for FodsDocument.ExportSheetToHtml, FodsCsvExporter, MimeType, OdfVersion.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R183

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R183: Tests for FodsDocument.ExportSheetToHtml, FodsCsvExporter, MimeType, OdfVersion.
/// ExportSheetToHtml(): returns HTML string for first sheet.
/// ExportSheetToHtml(sheetName): returns HTML string for named sheet.
/// FodsCsvExporter.ExportSheetToCsvString(sheet): returns CSV string.
/// MimeType: returns spreadsheet MIME type.
/// OdfVersion: returns ODF version string.
/// Covers: ExportSheetToHtml is non-null; ExportSheetToHtml contains html;
/// ExportSheetToHtml(sheetName) non-null; ExportSheetToHtml(sheetName) contains html;
/// FodsCsvExporter.ExportSheetToCsvString non-null; CSV string contains commas;
/// CSV string contains cell values; MimeType is non-null;
/// MimeType contains spreadsheet; OdfVersion is non-null;
/// OdfVersion is non-empty; GetColumnHeaders returns list;
/// GetColumnHeaders non-null; dogfood CreateNew->SetCell->ExportHtml->CsvExport.
/// </summary>
public class FodsR183ExportSheetToCsvFileAndHtmlTests : IDisposable
{
    private readonly string _tempDir;
    private static readonly string FodsFixturePath =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "..",
            "samples", "by-format", "fods", "valid", "simple.fods");

    public FodsR183ExportSheetToCsvFileAndHtmlTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR183_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private FodsDocument LoadFixture()
    {
        var path = Path.GetFullPath(FodsFixturePath);
        return FodsDocument.Load(path);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToHtml (string return)
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToHtml_IsNotNull()
    {
        var doc = LoadFixture();
        Assert.NotNull(doc.ExportSheetToHtml());
    }

    [Fact]
    public void ExportSheetToHtml_ContainsHtmlTag()
    {
        var doc = LoadFixture();
        var html = doc.ExportSheetToHtml();
        Assert.Contains("html", html, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void ExportSheetToHtml_ByName_IsNotNull()
    {
        var doc = LoadFixture();
        var sheetName = doc.GetSheetNames()[0];
        Assert.NotNull(doc.ExportSheetToHtml(sheetName));
    }

    [Fact]
    public void ExportSheetToHtml_ByName_ContainsHtmlTag()
    {
        var doc = LoadFixture();
        var sheetName = doc.GetSheetNames()[0];
        var html = doc.ExportSheetToHtml(sheetName);
        Assert.Contains("html", html, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void ExportSheetToHtml_StaticMethod_IsNotNull()
    {
        var doc = LoadFixture();
        var sheet = doc.Sheets[0];
        var html = FodsDocument.ExportSheetToHtml(sheet);
        Assert.NotNull(html);
    }

    // -------------------------------------------------------------------------
    // FodsCsvExporter.ExportSheetToCsvString
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsCsvExporter_ExportSheetToCsvString_IsNotNull()
    {
        var doc = LoadFixture();
        var sheet = doc.Sheets[0];
        var csv = FodsCsvExporter.ExportSheetToCsvString(sheet);
        Assert.NotNull(csv);
    }

    [Fact]
    public void FodsCsvExporter_ExportSheetToCsvString_ContainsCommas()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(0, 0, "A");
        doc.SetCellValue(0, 1, "B");
        var sheet = doc.GetSheetByName(sheetName)!;
        var csv = FodsCsvExporter.ExportSheetToCsvString(sheet);
        Assert.Contains(",", csv);
    }

    [Fact]
    public void FodsCsvExporter_ExportSheetToCsvString_ContainsCellValues()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(0, 0, "TestAlpha");
        doc.SetCellValue(0, 1, "TestBeta");
        var sheet = doc.GetSheetByName(sheetName)!;
        var csv = FodsCsvExporter.ExportSheetToCsvString(sheet);
        Assert.Contains("TestAlpha", csv);
        Assert.Contains("TestBeta", csv);
    }

    // -------------------------------------------------------------------------
    // MimeType / OdfVersion
    // -------------------------------------------------------------------------

    [Fact]
    public void MimeType_IsNotNull()
    {
        var doc = LoadFixture();
        Assert.NotNull(doc.MimeType);
    }

    [Fact]
    public void MimeType_ContainsSpreadsheet()
    {
        var doc = LoadFixture();
        Assert.Contains("spreadsheet", doc.MimeType!, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void OdfVersion_IsNotNull()
    {
        var doc = LoadFixture();
        Assert.NotNull(doc.OdfVersion);
    }

    [Fact]
    public void OdfVersion_IsNonEmpty()
    {
        var doc = LoadFixture();
        Assert.False(string.IsNullOrEmpty(doc.OdfVersion));
    }

    // -------------------------------------------------------------------------
    // GetColumnHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHeaders_IsNotNull()
    {
        var doc = LoadFixture();
        Assert.NotNull(doc.GetColumnHeaders());
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->SetCell->ExportHtml->CsvExport
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetCellExportHtmlCsvExport_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheetName = doc.GetSheetNames()[0];

        // Set some cell values
        doc.SetCellValue(0, 0, "Product");
        doc.SetCellValue(0, 1, "Price");
        doc.SetCellValue(1, 0, "Widget");
        doc.SetCellValue(1, 1, "9.99");

        // Export to HTML
        var html = doc.ExportSheetToHtml();
        Assert.False(string.IsNullOrEmpty(html));
        Assert.Contains("html", html, StringComparison.OrdinalIgnoreCase);

        // Export to CSV string via exporter
        var sheet = doc.GetSheetByName(sheetName)!;
        var csv = FodsCsvExporter.ExportSheetToCsvString(sheet);
        Assert.Contains("Widget", csv);
        Assert.Contains("9.99", csv);
        Assert.Contains(",", csv);
    }
}
