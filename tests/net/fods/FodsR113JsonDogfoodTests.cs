using Xunit;
using System;
using System.IO;
using FormatFactory.Fods;

namespace FormatFactory.Fods.Tests;

public class FodsR113JsonDogfoodTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));
    private static string SamplePath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void JsonExport_AfterSetCell_ContainsValue()
    {
        var doc = FodsDocument.Load(SamplePath);
        var sheet = doc.AddSheet("JsonTest");
        doc.InsertRowWithValues("JsonTest", 0, new[] { "Header" });
        doc.InsertRowWithValues("JsonTest", 1, new[] { "JsonVal" });
        var json = FodsDocument.ExportSheetToJson(sheet);
        Assert.Contains("JsonVal", json);
    }

    [Fact]
    public void JsonExport_AfterInsertRow_ContainsRow()
    {
        var doc = FodsDocument.Load(SamplePath);
        doc.AddSheet("JsonTest2");
        doc.InsertRowWithValues("JsonTest2", 0, new[] { "Col1" });
        doc.InsertRowWithValues("JsonTest2", 1, new[] { "Data1" });
        var json = doc.ExportSheetToJson("JsonTest2");
        Assert.Contains("Data1", json);
    }

    [Fact]
    public void JsonExport_SaveReload_StillExports()
    {
        var doc = FodsDocument.Load(SamplePath);
        doc.AddSheet("JsonSave");
        doc.InsertRowWithValues("JsonSave", 0, new[] { "Hdr" });
        doc.InsertRowWithValues("JsonSave", 1, new[] { "SavedJson" });
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var json = reloaded.ExportSheetToJson("JsonSave");
            Assert.Contains("SavedJson", json);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void JsonExport_ContainsBothValues()
    {
        var doc = FodsDocument.Load(SamplePath);
        doc.AddSheet("JsonBoth");
        doc.InsertRowWithValues("JsonBoth", 0, new[] { "Name" });
        doc.InsertRowWithValues("JsonBoth", 1, new[] { "Apple" });
        doc.InsertRowWithValues("JsonBoth", 2, new[] { "Banana" });
        var json = doc.ExportSheetToJson("JsonBoth");
        Assert.Contains("Apple", json);
        Assert.Contains("Banana", json);
    }

    [Fact]
    public void MarkdownExport_AfterSetCell_ContainsValue()
    {
        var doc = FodsDocument.Load(SamplePath);
        doc.AddSheet("MdTest");
        doc.InsertRowWithValues("MdTest", 0, new[] { "MdVal" });
        var md = doc.ExportSheetToMarkdown("MdTest");
        Assert.Contains("MdVal", md);
    }

    [Fact]
    public void HtmlExport_AfterSetCell_ContainsValue()
    {
        var doc = FodsDocument.Load(SamplePath);
        doc.AddSheet("HtmlTest");
        doc.InsertRowWithValues("HtmlTest", 0, new[] { "HtmlVal" });
        var html = doc.ExportSheetToHtml("HtmlTest");
        Assert.Contains("HtmlVal", html);
    }
}
