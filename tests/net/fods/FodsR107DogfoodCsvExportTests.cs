// R107 Wave 4: FODS CSV export dogfood pipeline
// Ledger: R107-DOGFOOD-FODS-CSV

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR107DogfoodCsvExportTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void Dogfood_LoadEditExportCsv()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.SetCellValue(0, 0, "CsvTest");
        var csv = doc.ExportSheetToCsv(sheet);
        Assert.Contains("CsvTest", csv);
    }

    [Fact]
    public void Dogfood_ClearInsertExportCsv()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        doc.InsertRowWithValues(sheet, 0, new[] { "A", "B", "C" });
        doc.InsertRowWithValues(sheet, 1, new[] { "1", "2", "3" });
        var csv = doc.ExportSheetToCsv(sheet);
        Assert.Contains("A,B,C", csv);
        Assert.Contains("1,2,3", csv);
    }

    [Fact]
    public void Dogfood_SaveReloadExportCsv()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        doc.InsertRowWithValues(sheet, 0, new[] { "saved", "data" });
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var csv = reloaded.ExportSheetToCsv(sheet);
            Assert.Contains("saved,data", csv);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Dogfood_CsvRfc4180_QuotedValues()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.SetCellValue(0, 0, "has,comma");
        var csv = doc.ExportSheetToCsv(sheet);
        Assert.Contains("\"has,comma\"", csv);
    }

    [Fact]
    public void Dogfood_FullPipeline_InsertMultiRowExportCsv()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        for (int i = 0; i < 5; i++)
            doc.InsertRowWithValues(sheet, i, new[] { $"r{i}c0", $"r{i}c1" });
        var csv = doc.ExportSheetToCsv(sheet);
        var lines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        int nonEmpty = 0;
        foreach (var l in lines) if (l.Trim().Length > 0) nonEmpty++;
        Assert.Equal(5, nonEmpty);
    }

    [Fact]
    public void Dogfood_CsvExportMatchesColumnValues()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        doc.InsertRowWithValues(sheet, 0, new[] { "X", "Y" });
        var csv = doc.ExportSheetToCsv(sheet);
        var col0 = doc.GetColumnValues(sheet, 0);
        Assert.Equal("X", col0[0]);
        Assert.Contains("X,Y", csv);
    }
}
