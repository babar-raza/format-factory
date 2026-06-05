// R106 Wave 4: FODS dogfood — ClearSheet + edit + save roundtrip
// Ledger: R106-DOGFOOD-FODS-SAVE-ROUNDTRIP-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR106DogfoodSaveRoundtripTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void Dogfood_ClearThenInsertThenSave()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        doc.InsertRow(sheet, 0);
        doc.InsertRow(sheet, 1);
        Assert.Equal(2, doc.GetRowCount(sheet));
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal(2, reloaded.GetRowCount(sheet));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Dogfood_EditCellThenExportColumn()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.SetCellValue(0, 0, "DogfoodCol");
        var vals = doc.GetColumnValues(sheet, 0);
        Assert.Equal("DogfoodCol", vals[0]);
    }

    [Fact]
    public void Dogfood_ClearAndRebuildSheet()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        for (int i = 0; i < 5; i++)
            doc.InsertRow(sheet, i);
        Assert.Equal(5, doc.GetRowCount(sheet));
        var html = doc.ExportSheetToHtml(sheet);
        Assert.Contains("<table", html);
    }

    [Fact]
    public void Dogfood_SaveReloadGetColumnValues()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.SetCellValue(0, 0, "SavedVal");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var vals = reloaded.GetColumnValues(sheet, 0);
            Assert.Equal("SavedVal", vals[0]);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Dogfood_ClearExportJson_EmptyArray()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        var json = doc.ExportSheetToJson(sheet);
        Assert.Contains("[]", json);
    }

    [Fact]
    public void Dogfood_FullPipeline_ClearInsertSaveReloadVerifyRows()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        doc.InsertRow(sheet, 0);
        doc.InsertRow(sheet, 1);
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var r = FodsDocument.Load(tmp);
            Assert.Equal(2, r.GetRowCount(sheet));
            var html = r.ExportSheetToHtml(sheet);
            Assert.Contains("<tr", html);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
