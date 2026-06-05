// R99 Train B: FODS .NET Export Quality Edge Case Tests
// Governed skill: /add-roundtrip-test
// Ledger: R99-GOVERNED-DOTNET-FODS-EXPORT-QUALITY-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR99ExportQualityTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void CsvExport_CommaInValue_IsQuoted()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.SetCellValue(0, 0, "hello, world");
        var tmp = Path.GetTempFileName() + ".fods";
        var csv = Path.GetTempFileName() + ".csv";
        try
        {
            doc.Save(tmp);
            FodsCsvExporter.ExportFirstSheetToCsv(tmp, csv);
            var content = File.ReadAllText(csv);
            Assert.Contains("\"hello, world\"", content);
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
            if (File.Exists(csv)) File.Delete(csv);
        }
    }

    [Fact]
    public void CsvExport_QuoteInValue_IsDoubled()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.SetCellValue(0, 0, "say \"hi\"");
        var tmp = Path.GetTempFileName() + ".fods";
        var csv = Path.GetTempFileName() + ".csv";
        try
        {
            doc.Save(tmp);
            FodsCsvExporter.ExportFirstSheetToCsv(tmp, csv);
            var content = File.ReadAllText(csv);
            Assert.Contains("\"\"hi\"\"", content);
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
            if (File.Exists(csv)) File.Delete(csv);
        }
    }

    [Fact]
    public void HtmlExport_ContainsTableStructure()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var html = doc.ExportSheetToHtml();
        Assert.Contains("<table", html);
        Assert.Contains("</table>", html);
        Assert.Contains("<tr", html);
        Assert.Contains("<td", html);
    }

    [Fact]
    public void HtmlExport_AfterEdit_ReflectsChange()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.SetCellValue(0, 0, "HTML-QUALITY-R99");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var html = reloaded.ExportSheetToHtml();
            Assert.Contains("HTML-QUALITY-R99", html);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void JsonExport_IsValidJsonArray()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var json = doc.ExportSheetToJson();
        Assert.True(json.Trim().StartsWith("["), "JSON should start with [");
        Assert.True(json.Trim().EndsWith("]"), "JSON should end with ]");
    }

    [Fact]
    public void CsvInMemory_MatchesFileExport()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        var inMemory = FodsCsvExporter.ExportSheetToCsvString(sheet);
        var tmpCsv = Path.GetTempFileName() + ".csv";
        try
        {
            FodsCsvExporter.ExportFirstSheetToCsv(MinimalPath, tmpCsv);
            var fromFile = File.ReadAllText(tmpCsv);
            Assert.Equal(inMemory.TrimEnd(), fromFile.TrimEnd());
        }
        finally { if (File.Exists(tmpCsv)) File.Delete(tmpCsv); }
    }

    [Fact]
    public void ExportSheetToHtml_ByName_MatchesFirstSheet()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var htmlDefault = doc.ExportSheetToHtml();
        var sheetName = doc.GetSheetNames()[0];
        var htmlByName = doc.ExportSheetToHtml(sheetName);
        Assert.Equal(htmlDefault, htmlByName);
    }

    [Fact]
    public void ExportSheetToJson_ByName_MatchesFirstSheet()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var jsonDefault = doc.ExportSheetToJson();
        var sheetName = doc.GetSheetNames()[0];
        var jsonByName = doc.ExportSheetToJson(sheetName);
        Assert.Equal(jsonDefault, jsonByName);
    }
}
