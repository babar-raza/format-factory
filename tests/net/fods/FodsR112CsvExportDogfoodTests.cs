using Xunit;
using System;
using System.IO;
using FormatFactory.Fods;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R112 Dogfood: FODS edit -> CSV export -> verify roundtrip.
/// Uses FF library for both input and output — no external dependencies.
/// </summary>
public class FodsR112CsvExportDogfoodTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));
    private static string SamplePath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void CsvExport_AfterSetCell_ContainsValue()
    {
        var doc = FodsDocument.Load(SamplePath);
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellValue(sheet, 0, 0, "DogfoodTest");
        var csv = FodsDocument.ExportSheetToCsv(sheet);
        Assert.Contains("DogfoodTest", csv);
    }

    [Fact]
    public void CsvExport_AfterMergeCells_ProducesCsv()
    {
        var doc = FodsDocument.Load(Path.Combine(SamplesDir, "multi-sheet-basic.fods"));
        var sheetName = doc.Sheets[0].Name;
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 0, "Merged");
        doc.MergeCells(sheetName, 0, 0, 1, 2);
        var csv = doc.ExportSheetToCsv(sheetName);
        Assert.Contains("Merged", csv);
    }

    [Fact]
    public void CsvExport_AfterSetFormula_ContainsOriginalValue()
    {
        var doc = FodsDocument.Load(SamplePath);
        var sheetName = doc.Sheets[0].Name;
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 0, "100");
        doc.SetCellFormula(sheetName, 0, 0, "=SUM(B1:B3)");
        var csv = doc.ExportSheetToCsv(sheetName);
        Assert.Contains("100", csv);
    }

    [Fact]
    public void CsvExport_MultiSheet_FirstSheetDefault()
    {
        var doc = FodsDocument.Load(SamplePath);
        doc.AddSheet("ExtraSheet");
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 0, "FirstSheet");
        var csv = doc.ExportSheetToCsv();
        Assert.Contains("FirstSheet", csv);
    }

    [Fact]
    public void CsvExport_SaveReload_CsvStillValid()
    {
        var doc = FodsDocument.Load(SamplePath);
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 0, "SaveReloadCSV");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var csv = reloaded.ExportSheetToCsv();
            Assert.Contains("SaveReloadCSV", csv);
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
        }
    }

    [Fact]
    public void CsvExport_EmptySheet_DoesNotThrow()
    {
        var doc = FodsDocument.Load(SamplePath);
        doc.AddSheet("EmptyDogfood");
        var csv = doc.ExportSheetToCsv("EmptyDogfood");
        Assert.NotNull(csv);
    }

    [Fact]
    public void CsvExport_GetUsedRange_ThenExport_Consistent()
    {
        var doc = FodsDocument.Load(SamplePath);
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 0, "RangeTest");
        var range = doc.GetUsedRange();
        var csv = doc.ExportSheetToCsv();
        Assert.NotNull(range);
        Assert.Contains("RangeTest", csv);
    }

    [Fact]
    public void CsvExport_InsertRowWithValues_ThenExport()
    {
        var doc = FodsDocument.Load(SamplePath);
        var sheetName = doc.Sheets[0].Name;
        doc.InsertRowWithValues(sheetName, 0, new[] { "A", "B", "C" });
        var csv = doc.ExportSheetToCsv(sheetName);
        Assert.Contains("A", csv);
        Assert.Contains("B", csv);
        Assert.Contains("C", csv);
    }
}
