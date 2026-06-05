// R107 Wave 4: FODT plain text export dogfood pipeline
// Ledger: R107-DOGFOOD-FODT-PLAINTEXT

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR107DogfoodPlainTextExportTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void Dogfood_EditExportPlainText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("Dogfood plain text test");
        var tmp = Path.GetTempFileName() + ".txt";
        try
        {
            doc.ExportToPlainTextFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.Contains("Dogfood plain text test", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Dogfood_ClearRebuildExportPlainText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        var tmp = Path.GetTempFileName() + ".txt";
        try
        {
            doc.ExportToPlainTextFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.Equal("First\nSecond", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Dogfood_HeadingsInPlainText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var headings = doc.GetHeadingTexts();
        var text = doc.GetPlainText();
        foreach (var h in headings)
            Assert.Contains(h, text);
    }

    [Fact]
    public void Dogfood_SaveReloadExportPlainText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("PERSISTENT_TEXT");
        var tmpFodt = Path.GetTempFileName() + ".fodt";
        var tmpTxt = Path.GetTempFileName() + ".txt";
        try
        {
            doc.Save(tmpFodt);
            var reloaded = FodtDocument.Load(tmpFodt);
            reloaded.ExportToPlainTextFile(tmpTxt);
            var content = File.ReadAllText(tmpTxt);
            Assert.Contains("PERSISTENT_TEXT", content);
        }
        finally
        {
            if (File.Exists(tmpFodt)) File.Delete(tmpFodt);
            if (File.Exists(tmpTxt)) File.Delete(tmpTxt);
        }
    }

    [Fact]
    public void Dogfood_GetHeadingTexts_WithExport()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var headings = doc.GetHeadingTexts();
        var html = doc.ExportToHtml();
        foreach (var h in headings)
            Assert.Contains(h, html);
    }

    [Fact]
    public void Dogfood_FullPipeline_EditSearchExportSave()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        doc.AppendParagraph("Gamma");
        var range = doc.GetTextBetweenParagraphs(0, 2);
        Assert.Equal("Alpha\nBeta", range);
        var tmp = Path.GetTempFileName() + ".txt";
        try
        {
            doc.ExportToPlainTextFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.Equal("Alpha\nBeta\nGamma", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
