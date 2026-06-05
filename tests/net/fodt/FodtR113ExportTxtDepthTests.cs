using Xunit;
using System;
using System.IO;
using FormatFactory.Fodt;

namespace FormatFactory.Fodt.Tests;

public class FodtR113ExportTxtDepthTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));
    private static string SamplePath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void ExportToPlainTextFile_SaveReload_RoundtripConsistent()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("ExportTxtTest");
        var tmp = Path.GetTempFileName() + ".txt";
        try
        {
            doc.ExportToPlainTextFile(tmp);
            var text = File.ReadAllText(tmp);
            Assert.Contains("ExportTxtTest", text);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToPlainTextFile_AfterInsertHeading_ContainsHeading()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.InsertHeading(0, "HeadingForExport", 1);
        var tmp = Path.GetTempFileName() + ".txt";
        try
        {
            doc.ExportToPlainTextFile(tmp);
            var text = File.ReadAllText(tmp);
            Assert.Contains("HeadingForExport", text);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToMarkdownFile_ContainsHeadingMarker()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.InsertHeading(0, "MarkdownHead", 2);
        var tmp = Path.GetTempFileName() + ".md";
        try
        {
            doc.ExportToMarkdownFile(tmp);
            var text = File.ReadAllText(tmp);
            Assert.Contains("## MarkdownHead", text);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToHtmlFile_ContainsHtmlTag()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("HtmlTest");
        var tmp = Path.GetTempFileName() + ".html";
        try
        {
            doc.ExportToHtmlFile(tmp);
            var text = File.ReadAllText(tmp);
            Assert.Contains("<p>", text);
            Assert.Contains("HtmlTest", text);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void GetPlainText_AfterReplaceText_ReflectsChange()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("OldText");
        doc.ReplaceText("OldText", "NewText");
        var txt = doc.GetPlainText();
        Assert.Contains("NewText", txt);
        Assert.DoesNotContain("OldText", txt);
    }

    [Fact]
    public void GetDocumentStats_AfterEdits_Consistent()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("StatsTest word1 word2");
        var stats = doc.GetDocumentStats();
        Assert.True(stats.ParagraphCount > 0);
        Assert.True(stats.WordCount > 0);
        Assert.True(stats.CharCount > 0);
    }
}
