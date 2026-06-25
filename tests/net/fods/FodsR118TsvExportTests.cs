// Tests for FodsDocumentExporter.ExportSheetToTsv
// Sprint: FORMAT-FACTORY-FODS-TSV-EXPORT-20260625
// Ledger: R118-GOVERNED-DOTNET-FODS-TSV-EXPORT-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR118TsvExportTests
{
    // Fixtures: minimal-spreadsheet.fods  → Sheet1, 1 row × 1 col = "Hello"
    //           multi-sheet-basic.fods    → Data (2 rows × 2 cols), Summary (1 row × 1 col)
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory, "../../../../../../samples/by-format/fods"));

    private static string MinimalPath => Path.Combine(SamplesDir, "minimal-spreadsheet.fods");
    private static string MultiPath   => Path.Combine(SamplesDir, "multi-sheet-basic.fods");

    // ---- Basic structure ----

    [Fact]
    public void ExportSheetToTsv_EmptySheet_ReturnsEmptyString()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Empty");
        var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
        Assert.Equal(string.Empty, tsv);
    }

    [Fact]
    public void ExportSheetToTsv_SingleCell_ReturnsValueWithNewline()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetByIndex(0)!;
        var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
        Assert.Contains("Hello", tsv);
        Assert.EndsWith(Environment.NewLine, tsv);
    }

    [Fact]
    public void ExportSheetToTsv_TwoColumns_SeparatedByTab()
    {
        // Data row 0: Name\tValue
        var doc = FodsDocument.Load(MultiPath);
        var sheet = doc.GetSheetByName("Data")!;
        var lines = FodsDocumentExporter.ExportSheetToTsv(sheet)
            .Split(new[] { "\r\n", "\n" }, StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal("Name\tValue", lines[0]);
    }

    [Fact]
    public void ExportSheetToTsv_TwoRows_EachOnSeparateLine()
    {
        var doc = FodsDocument.Load(MultiPath);
        var sheet = doc.GetSheetByName("Data")!;
        var lines = FodsDocumentExporter.ExportSheetToTsv(sheet)
            .Split(new[] { "\r\n", "\n" }, StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(2, lines.Length);
    }

    [Fact]
    public void ExportSheetToTsv_DataValues_AllPresent()
    {
        var doc = FodsDocument.Load(MultiPath);
        var sheet = doc.GetSheetByName("Data")!;
        var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
        Assert.Contains("Alpha", tsv);
        Assert.Contains("Beta", tsv);
    }

    // ---- Tab/newline sanitization ----

    [Fact]
    public void ExportSheetToTsv_TabInCellValue_ReplacedWithSpace()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetByIndex(0)!;
        FodsDocument.SetCellValue(sheet, 0, 0, "A\tB");
        var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
        Assert.Contains("A B", tsv);
        // Verify no literal tab from the cell content (only separator tabs)
        var lines = tsv.Split(new[] { "\r\n", "\n" }, StringSplitOptions.RemoveEmptyEntries);
        Assert.DoesNotContain('\t', lines[0]); // single cell row → no tab separator
    }

    [Fact]
    public void ExportSheetToTsv_NewlineInCellValue_ReplacedWithSpace()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetByIndex(0)!;
        FodsDocument.SetCellValue(sheet, 0, 0, "line1\nline2");
        var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
        Assert.Contains("line1 line2", tsv);
    }

    // ---- Null guard ----

    [Fact]
    public void ExportSheetToTsv_NullSheetThrows()
    {
        Assert.Throws<ArgumentNullException>(() => FodsDocumentExporter.ExportSheetToTsv(null!));
    }

    // ---- Round-trip check ----

    [Fact]
    public void ExportSheetToTsv_ParseableAsTsv()
    {
        var doc = FodsDocument.Load(MultiPath);
        var sheet = doc.GetSheetByName("Data")!;
        var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
        var lines = tsv.Split(new[] { "\r\n", "\n" }, StringSplitOptions.RemoveEmptyEntries);
        foreach (var line in lines)
        {
            var cells = line.Split('\t');
            Assert.Equal(2, cells.Length); // Data sheet has 2 columns
        }
    }
}
