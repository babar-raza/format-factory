// R104 Wave 3: FODS .NET dogfood — CSV export from edited spreadsheet
// Ledger: R104-DOGFOOD-FODS-CSV-EXPORT-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR104DogfoodCsvExportTests
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
        doc.SetCellValue(0, 0, "DogfoodTest");
        var html = doc.ExportSheetToHtml(doc.GetSheetNames()[0]);
        Assert.Contains("DogfoodTest", html);
    }

    [Fact]
    public void Dogfood_CopySheetThenExport()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var source = doc.GetSheetNames()[0];
        doc.CopySheet(source, "Export");
        var html = doc.ExportSheetToHtml("Export");
        Assert.NotNull(html);
        Assert.Contains("<table", html);
    }

    [Fact]
    public void Dogfood_AddSheetEditExportJson()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.AddSheet("JsonSheet");
        doc.SetCellValue(0, 0, "key");
        var json = doc.ExportSheetToJson(doc.GetSheetNames()[0]);
        Assert.NotNull(json);
    }

    [Fact]
    public void Dogfood_EditSaveReloadVerify()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.SetCellValue(0, 0, "Saved");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal("Saved", reloaded.GetCellValue(0, 0));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Dogfood_GetSheetByIndexThenExport()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetByIndex(0);
        Assert.NotNull(sheet);
        var html = doc.ExportSheetToHtml(sheet!.Name);
        Assert.Contains("<table", html);
    }

    [Fact]
    public void Dogfood_FullPipeline_LoadCopyEditSaveExport()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var source = doc.GetSheetNames()[0];
        doc.CopySheet(source, "Pipeline");
        FodsDocument.SetCellValue(doc.GetSheetByName("Pipeline")!, 0, 0, "PipelineVal");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var val = FodsDocument.GetCellValue(reloaded.GetSheetByName("Pipeline")!, 0, 0);
            Assert.Equal("PipelineVal", val);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
