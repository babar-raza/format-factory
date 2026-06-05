// R98 Train L: FODS .NET Same-Format Save After SetCellValue
// Governed skill: /add-same-format-writer-feature
// Ledger: R98-GOVERNED-DOTNET-FODS-SAVE-AFTER-EDIT-001
// Priority: 2 (same-format save after edits — core product value)

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR98SaveAfterEditTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    private static string MultiSheetPath =>
        Path.Combine(SamplesDir, "multi-sheet-basic.fods");

    [Fact]
    public void SetCellValue_Save_Reload_PreservesEditedValue()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.SetCellValue(0, 0, "R98-EDIT-A1");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal("R98-EDIT-A1", reloaded.GetCellValue(0, 0));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SetCellValue_Save_Reload_PreservesUneditedCells()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var originalB1 = doc.GetCellValue(0, 1);
        doc.SetCellValue(0, 0, "CHANGED");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal(originalB1, reloaded.GetCellValue(0, 1));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SetCellValue_Save_Reload_SheetCountPreserved()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var originalCount = doc.SheetCount;
        doc.SetCellValue(0, 0, "EDIT");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal(originalCount, reloaded.SheetCount);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SetCellValue_Save_CsvExport_ContainsEditedValue()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.SetCellValue(0, 0, "CSV-TEST-VALUE");
        var tmpFods = Path.GetTempFileName() + ".fods";
        var tmpCsv = Path.GetTempFileName() + ".csv";
        try
        {
            doc.Save(tmpFods);
            var result = FodsCsvExporter.ExportFirstSheetToCsv(tmpFods, tmpCsv);
            Assert.Equal("exported", result.Status);
            var csv = File.ReadAllText(tmpCsv);
            Assert.Contains("CSV-TEST-VALUE", csv);
        }
        finally
        {
            if (File.Exists(tmpFods)) File.Delete(tmpFods);
            if (File.Exists(tmpCsv)) File.Delete(tmpCsv);
        }
    }

    [Fact]
    public void SetCellValue_Save_HtmlExport_ContainsEditedValue()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.SetCellValue(0, 0, "HTML-TEST-R98");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var html = reloaded.ExportSheetToHtml();
            Assert.Contains("HTML-TEST-R98", html);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SetCellValue_Save_JsonExport_ReflectsEditedHeader()
    {
        var doc = FodsDocument.Load(MinimalPath);
        // Row 0 is header for JSON export; edit it and verify it appears as a key
        // if the sheet has >1 row. If only 1 row, JSON returns "[]" — verify that.
        doc.SetCellValue(0, 0, "JSON-HEADER-R98");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var json = reloaded.ExportSheetToJson();
            if (reloaded.GetRowCount() > 1)
                Assert.Contains("JSON-HEADER-R98", json);
            else
                Assert.Equal("[]", json.Trim());
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SetCellValue_Save_MimeTypePreserved()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var origMime = doc.MimeType;
        doc.SetCellValue(0, 0, "MIME-CHECK");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal(origMime, reloaded.MimeType);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void MultiSheet_SetCellValue_Save_Reload()
    {
        if (!File.Exists(MultiSheetPath)) return; // skip if sample missing
        var doc = FodsDocument.Load(MultiSheetPath);
        if (doc.SheetCount < 2) return;
        var sheet2 = doc.Sheets[1];
        if (sheet2.Rows.Count == 0 || sheet2.Rows[0].Cells.Count == 0) return;
        FodsDocument.SetCellValue(sheet2, 0, 0, "SHEET2-R98");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal("SHEET2-R98",
                FodsDocument.GetCellValue(reloaded.Sheets[1], 0, 0));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
