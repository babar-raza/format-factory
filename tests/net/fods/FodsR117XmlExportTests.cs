// Tests for FodsDocumentExporter.ExportSheetToXml
// Sprint: FORMAT-FACTORY-FODS-XML-EXPORT-20260625
// Ledger: R117-GOVERNED-DOTNET-FODS-XML-EXPORT-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR117XmlExportTests
{
    // Fixtures: minimal-spreadsheet.fods  → Sheet1, 1 row × 1 col = "Hello"
    //           multi-sheet-basic.fods    → Data (2 rows × 2 cols), Summary (1 row × 1 col)
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory, "../../../../../../samples/by-format/fods"));

    private static string MinimalPath => Path.Combine(SamplesDir, "minimal-spreadsheet.fods");
    private static string MultiPath   => Path.Combine(SamplesDir, "multi-sheet-basic.fods");

    // ---- Basic structure ----

    [Fact]
    public void ExportSheetToXml_EmptySheet_ReturnsTableElement()
    {
        // CreateNew + AddSheet gives a sheet with zero rows
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Empty");
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.StartsWith("<table", xml);
        Assert.Contains("</table>", xml);
    }

    [Fact]
    public void ExportSheetToXml_SheetNameInAttribute()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetByIndex(0)!;
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("name=\"Sheet1\"", xml);
    }

    [Fact]
    public void ExportSheetToXml_RowsProduceRowElements()
    {
        // Data sheet in multi-sheet fixture has 2 rows
        var doc = FodsDocument.Load(MultiPath);
        var sheet = doc.GetSheetByName("Data")!;
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Equal(2, CountOccurrences(xml, "<row>"));
    }

    [Fact]
    public void ExportSheetToXml_CellValuesPresent()
    {
        // Data sheet row 0: Name, Value
        var doc = FodsDocument.Load(MultiPath);
        var sheet = doc.GetSheetByName("Data")!;
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("<cell>Name</cell>", xml);
        Assert.Contains("<cell>Value</cell>", xml);
    }

    [Fact]
    public void ExportSheetToXml_EmptyCellProducesSelfClosingTag()
    {
        // Set the only cell to empty string → should produce <cell/>
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetByIndex(0)!;
        FodsDocument.SetCellValue(sheet, 0, 0, "");
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("<cell/>", xml);
    }

    // ---- XML escaping ----

    [Fact]
    public void ExportSheetToXml_AmpersandEscaped()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetByIndex(0)!;
        FodsDocument.SetCellValue(sheet, 0, 0, "A & B");
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("A &amp; B", xml);
        Assert.DoesNotContain("A & B", xml);
    }

    [Fact]
    public void ExportSheetToXml_LtGtEscaped()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetByIndex(0)!;
        FodsDocument.SetCellValue(sheet, 0, 0, "x<y>z");
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("x&lt;y&gt;z", xml);
    }

    [Fact]
    public void ExportSheetToXml_QuoteEscaped()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetByIndex(0)!;
        FodsDocument.SetCellValue(sheet, 0, 0, "say \"hi\"");
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("say &quot;hi&quot;", xml);
    }

    // ---- Null / edge cases ----

    [Fact]
    public void ExportSheetToXml_NullSheetThrows()
    {
        Assert.Throws<ArgumentNullException>(() => FodsDocumentExporter.ExportSheetToXml(null!));
    }

    [Fact]
    public void ExportSheetToXml_SingleRowSingleCell_ValidXml()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetByIndex(0)!;
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("<table", xml);
        Assert.Contains("<row>", xml);
        Assert.Contains("<cell>Hello</cell>", xml);
        Assert.Contains("</row>", xml);
        Assert.Contains("</table>", xml);
    }

    // ---- Multi-row data ----

    [Fact]
    public void ExportSheetToXml_MultiRow_AllValuesPresent()
    {
        var doc = FodsDocument.Load(MultiPath);
        var sheet = doc.GetSheetByName("Data")!;
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("<cell>Alpha</cell>", xml);
        Assert.Contains("<cell>Beta</cell>", xml);
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
