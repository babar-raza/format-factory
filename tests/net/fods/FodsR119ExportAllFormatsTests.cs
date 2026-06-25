// Tests for multi-format export pipeline consistency across ExportSheetTo* methods.
// Sprint: FORMAT-FACTORY-FODS-EXPORT-ALL-20260626
// Ledger: R119-GOVERNED-DOTNET-FODS-EXPORT-ALL-001

using System;
using System.IO;
using System.Linq;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R119: Verifies that all five FodsDocumentExporter export formats (HTML, JSON, Markdown, CSV, TSV, XML)
/// produce consistent non-empty output for the same sheet, and that shared invariants hold
/// across all formats (e.g., all contain expected cell values).
/// </summary>
public class FodsR119ExportAllFormatsTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory, "../../../../../../samples/by-format/fods"));

    private static string MinimalPath => Path.Combine(SamplesDir, "minimal-spreadsheet.fods");
    private static string MultiPath   => Path.Combine(SamplesDir, "multi-sheet-basic.fods");

    // ---- Each format non-empty for non-empty sheet ----

    [Fact]
    public void Html_NonEmpty_ForMinimalSheet()
    {
        var sheet = FodsDocument.Load(MinimalPath).GetSheetByIndex(0)!;
        Assert.NotEmpty(FodsDocumentExporter.ExportSheetToHtml(sheet));
    }

    [Fact]
    public void Json_NonEmpty_ForDataSheet()
    {
        var sheet = FodsDocument.Load(MultiPath).GetSheetByName("Data")!;
        Assert.NotEmpty(FodsDocumentExporter.ExportSheetToJson(sheet));
    }

    [Fact]
    public void Markdown_NonEmpty_ForDataSheet()
    {
        var sheet = FodsDocument.Load(MultiPath).GetSheetByName("Data")!;
        Assert.NotEmpty(FodsDocumentExporter.ExportSheetToMarkdown(sheet));
    }

    [Fact]
    public void Csv_NonEmpty_ForDataSheet()
    {
        var sheet = FodsDocument.Load(MultiPath).GetSheetByName("Data")!;
        Assert.NotEmpty(FodsDocumentExporter.ExportSheetToCsv(sheet));
    }

    [Fact]
    public void Tsv_NonEmpty_ForDataSheet()
    {
        var sheet = FodsDocument.Load(MultiPath).GetSheetByName("Data")!;
        Assert.NotEmpty(FodsDocumentExporter.ExportSheetToTsv(sheet));
    }

    [Fact]
    public void Xml_NonEmpty_ForDataSheet()
    {
        var sheet = FodsDocument.Load(MultiPath).GetSheetByName("Data")!;
        Assert.NotEmpty(FodsDocumentExporter.ExportSheetToXml(sheet));
    }

    // ---- All formats contain the same cell values ----

    [Fact]
    public void AllFormats_ContainName_FromDataSheet()
    {
        var sheet = FodsDocument.Load(MultiPath).GetSheetByName("Data")!;
        var html = FodsDocumentExporter.ExportSheetToHtml(sheet);
        var markdown = FodsDocumentExporter.ExportSheetToMarkdown(sheet);
        var csv = FodsDocumentExporter.ExportSheetToCsv(sheet);
        var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);

        Assert.Contains("Name", html);
        Assert.Contains("Name", markdown);
        Assert.Contains("Name", csv);
        Assert.Contains("Name", tsv);
        Assert.Contains("Name", xml);
    }

    [Fact]
    public void AllFormats_ContainAlpha_FromDataSheet()
    {
        var sheet = FodsDocument.Load(MultiPath).GetSheetByName("Data")!;
        var html = FodsDocumentExporter.ExportSheetToHtml(sheet);
        var markdown = FodsDocumentExporter.ExportSheetToMarkdown(sheet);
        var csv = FodsDocumentExporter.ExportSheetToCsv(sheet);
        var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);

        Assert.Contains("Alpha", html);
        Assert.Contains("Alpha", markdown);
        Assert.Contains("Alpha", csv);
        Assert.Contains("Alpha", tsv);
        Assert.Contains("Alpha", xml);
    }

    // ---- Empty sheet produces empty/trivial output ----

    [Fact]
    public void AllFormats_EmptySheet_ProduceMinimalOutput()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Empty");

        Assert.Equal(string.Empty, FodsDocumentExporter.ExportSheetToTsv(sheet));
        Assert.Equal(string.Empty, FodsDocumentExporter.ExportSheetToMarkdown(sheet));
        Assert.Equal("[]", FodsDocumentExporter.ExportSheetToJson(sheet));
    }

    // ---- Dogfood pipeline: build → export all → verify counts ----

    [Fact]
    public void DogfoodPipeline_BuildAndExportToAllFormats()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Products");
        FodsDocument.SetCellValue(sheet, 0, 0, "Product");
        FodsDocument.SetCellValue(sheet, 0, 1, "Price");
        FodsDocument.InsertRow(sheet, 1, new[] { "Widget", "9.99" });
        FodsDocument.InsertRow(sheet, 2, new[] { "Gadget", "24.99" });

        var csv   = FodsDocumentExporter.ExportSheetToCsv(sheet);
        var tsv   = FodsDocumentExporter.ExportSheetToTsv(sheet);
        var xml   = FodsDocumentExporter.ExportSheetToXml(sheet);
        var json  = FodsDocumentExporter.ExportSheetToJson(sheet);
        var md    = FodsDocumentExporter.ExportSheetToMarkdown(sheet);
        var html  = FodsDocumentExporter.ExportSheetToHtml(sheet);

        // All formats contain both product names
        foreach (var output in new[] { csv, tsv, xml, json, md, html })
        {
            Assert.Contains("Widget", output);
            Assert.Contains("Gadget", output);
        }

        // CSV: 3 lines (header + 2 data rows)
        var csvLines = csv.Split(new[] { "\r\n", "\n" }, StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(3, csvLines.Length);

        // TSV: same row count
        var tsvLines = tsv.Split(new[] { "\r\n", "\n" }, StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(3, tsvLines.Length);

        // XML: 3 <row> elements
        int rowCount = CountOccurrences(xml, "<row>");
        Assert.Equal(3, rowCount);

        // Markdown: header + separator + 2 data rows = 4 lines
        var mdLines = md.Split(new[] { "\r\n", "\n" }, StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(4, mdLines.Length);
    }

    // ---- Null guards for all export methods ----

    [Fact]
    public void AllExportMethods_ThrowOnNullSheet()
    {
        Assert.Throws<ArgumentNullException>(() => FodsDocumentExporter.ExportSheetToHtml(null!));
        Assert.Throws<ArgumentNullException>(() => FodsDocumentExporter.ExportSheetToJson(null!));
        Assert.Throws<ArgumentNullException>(() => FodsDocumentExporter.ExportSheetToMarkdown(null!));
        Assert.Throws<ArgumentNullException>(() => FodsDocumentExporter.ExportSheetToCsv(null!));
        Assert.Throws<ArgumentNullException>(() => FodsDocumentExporter.ExportSheetToTsv(null!));
        Assert.Throws<ArgumentNullException>(() => FodsDocumentExporter.ExportSheetToXml(null!));
    }

    private static int CountOccurrences(string source, string pattern)
    {
        int count = 0, idx = 0;
        while ((idx = source.IndexOf(pattern, idx, StringComparison.Ordinal)) >= 0)
        {
            count++;
            idx += pattern.Length;
        }
        return count;
    }
}
