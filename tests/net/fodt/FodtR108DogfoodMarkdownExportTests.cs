// R108 Lane G: FODT markdown export dogfood roundtrip
// Proves: Load -> Edit -> Save -> Reload -> ExportToMarkdownFile cycle works

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR108DogfoodMarkdownExportTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void Dogfood_EditSaveReloadMarkdownExport()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("R108_MARKDOWN_TEST");
        var tmpFodt = Path.GetTempFileName() + ".fodt";
        var tmpMd = Path.GetTempFileName() + ".md";
        try
        {
            doc.Save(tmpFodt);
            var reloaded = FodtDocument.Load(tmpFodt);
            reloaded.ExportToMarkdownFile(tmpMd);
            var content = File.ReadAllText(tmpMd);
            Assert.Contains("R108_MARKDOWN_TEST", content);
        }
        finally
        {
            if (File.Exists(tmpFodt)) File.Delete(tmpFodt);
            if (File.Exists(tmpMd)) File.Delete(tmpMd);
        }
    }

    [Fact]
    public void Dogfood_ClearRebuildMarkdownExport()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("Heading");
        doc.AppendParagraph("Body text");
        var tmpMd = Path.GetTempFileName() + ".md";
        try
        {
            doc.ExportToMarkdownFile(tmpMd);
            var content = File.ReadAllText(tmpMd);
            Assert.Contains("Heading", content);
            Assert.Contains("Body text", content);
        }
        finally { if (File.Exists(tmpMd)) File.Delete(tmpMd); }
    }

    [Fact]
    public void Dogfood_MarkdownAndPlainTextConsistent()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        var tmpMd = Path.GetTempFileName() + ".md";
        var tmpTxt = Path.GetTempFileName() + ".txt";
        try
        {
            doc.ExportToMarkdownFile(tmpMd);
            doc.ExportToPlainTextFile(tmpTxt);
            var md = File.ReadAllText(tmpMd);
            var txt = File.ReadAllText(tmpTxt);
            // Both should contain the paragraph text
            Assert.Contains("Alpha", md);
            Assert.Contains("Alpha", txt);
            Assert.Contains("Beta", md);
            Assert.Contains("Beta", txt);
        }
        finally
        {
            if (File.Exists(tmpMd)) File.Delete(tmpMd);
            if (File.Exists(tmpTxt)) File.Delete(tmpTxt);
        }
    }

    [Fact]
    public void Dogfood_FullPipeline_EditReplaceSaveMarkdown()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("Hello World");
        doc.ReplaceText("World", "R108");
        var tmpFodt = Path.GetTempFileName() + ".fodt";
        var tmpMd = Path.GetTempFileName() + ".md";
        try
        {
            doc.Save(tmpFodt);
            var reloaded = FodtDocument.Load(tmpFodt);
            reloaded.ExportToMarkdownFile(tmpMd);
            var content = File.ReadAllText(tmpMd);
            Assert.Contains("R108", content);
            Assert.DoesNotContain("World", content);
        }
        finally
        {
            if (File.Exists(tmpFodt)) File.Delete(tmpFodt);
            if (File.Exists(tmpMd)) File.Delete(tmpMd);
        }
    }
}
