// R111 Wave 7: FODS save roundtrip dogfood pipeline tests
// Pipeline: load → edit formula → save → reload → verify

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR111DogfoodSaveRoundtripTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void Dogfood_SetFormula_SaveReload_FormulaPreserved()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        doc.SetCellFormula(name, 0, 0, "of:=1+2");

        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal("of:=1+2", reloaded.GetCellFormula(name, 0, 0));
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
        }
    }

    [Fact]
    public void Dogfood_MergeCells_SaveReload_MergePreserved()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        int rows = doc.GetRowCount(name);
        int cols = doc.GetColumnCount(name);
        if (rows < 2 || cols < 2) return;

        doc.MergeCells(name, 0, 0, 2, 2);
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            // Cell (0,1) should be covered after reload
            Assert.Null(FodsDocument.GetCellValue(reloaded.Sheets[0], 0, 1));
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
        }
    }

    [Fact]
    public void Dogfood_EditCell_SetFormula_SaveReload()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 0, "edited");
        doc.SetCellFormula(name, 0, 0, "of:=SUM([.B1:.B5])");

        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal("edited", FodsDocument.GetCellValue(reloaded.Sheets[0], 0, 0));
            Assert.Equal("of:=SUM([.B1:.B5])", reloaded.GetCellFormula(name, 0, 0));
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
        }
    }

    [Fact]
    public void Dogfood_CsvExport_AfterFormula()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 0, "csv_test");
        doc.SetCellFormula(name, 0, 0, "of:=1");
        var csv = doc.ExportSheetToCsv(name);
        Assert.Contains("csv_test", csv);
    }
}
