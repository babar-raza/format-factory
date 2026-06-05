// R106 Wave 2: FODT RemoveAllParagraphs tests
// Ledger: R106-GOVERNED-DOTNET-FODT-REMOVEALLPARAGRAPHS-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR106RemoveAllParagraphsTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void RemoveAllParagraphs_ClearsDocument()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.True(doc.ParagraphCount > 0);
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveAllParagraphs_ThenAppend_Works()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("Fresh");
        Assert.Equal(1, doc.ParagraphCount);
        Assert.Equal("Fresh", doc.GetParagraphText(0));
    }

    [Fact]
    public void RemoveAllParagraphs_TwiceNoError()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveAllParagraphs_GetPlainText_Empty()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        var text = doc.GetPlainText();
        Assert.Equal(string.Empty, text);
    }

    [Fact]
    public void RemoveAllParagraphs_ExportHtml_EmptyBody()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        var html = doc.ExportToHtml();
        Assert.Contains("</html>", html);
        Assert.DoesNotContain("<p>", html);
    }

    [Fact]
    public void RemoveAllParagraphs_WordCountZero()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.WordCount);
    }

    [Fact]
    public void RemoveAllParagraphs_SaveAndReload()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("Survived");
        var tmpPath = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmpPath);
            var reloaded = FodtDocument.Load(tmpPath);
            Assert.Equal(1, reloaded.ParagraphCount);
            Assert.Equal("Survived", reloaded.GetParagraphText(0));
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }

    [Fact]
    public void RemoveAllParagraphs_DocumentStatsReset()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        var stats = doc.GetDocumentStats();
        Assert.Equal(0, stats.ParagraphCount);
        Assert.Equal(0, stats.WordCount);
    }
}
