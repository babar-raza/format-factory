// R108 Lane G: FODS save-after-edit dogfood roundtrip
// Proves: Load -> Edit -> Save -> Reload -> Verify cycle works end-to-end

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR108DogfoodSaveEditRoundtripTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void Dogfood_EditCellSaveReloadVerify()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.SetCellValue(0, 0, "R108_ROUNDTRIP");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal("R108_ROUNDTRIP", reloaded.GetCellValue(0, 0));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Dogfood_ClearInsertSaveCsvExport()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        doc.InsertRowWithValues(sheet, 0, new[] { "A", "B" });
        doc.InsertRowWithValues(sheet, 1, new[] { "1", "2" });
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var csv = reloaded.ExportSheetToCsv(sheet);
            Assert.Contains("A,B", csv);
            Assert.Contains("1,2", csv);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Dogfood_ColumnCountPreservedAfterSave()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        doc.InsertRowWithValues(sheet, 0, new[] { "x", "y", "z" });
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal(3, reloaded.GetColumnCount(sheet));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Dogfood_FullPipeline_InsertExportSaveReload()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        for (int i = 0; i < 5; i++)
            doc.InsertRowWithValues(sheet, i, new[] { $"r{i}", $"c{i}" });
        var csvBefore = doc.ExportSheetToCsv(sheet);
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var csvAfter = reloaded.ExportSheetToCsv(sheet);
            Assert.Equal(csvBefore, csvAfter);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
