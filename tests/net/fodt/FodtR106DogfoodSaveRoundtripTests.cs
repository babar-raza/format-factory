// R106 Wave 4: FODT dogfood — RemoveAllParagraphs + rebuild + save roundtrip
// Ledger: R106-DOGFOOD-FODT-SAVE-ROUNDTRIP-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR106DogfoodSaveRoundtripTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void Dogfood_RemoveAllThenAppendThenSave()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("Rebuilt");
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var r = FodtDocument.Load(tmp);
            Assert.Equal(1, r.ParagraphCount);
            Assert.Equal("Rebuilt", r.GetParagraphText(0));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Dogfood_GetTextBetweenThenExportHtml()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        doc.AppendParagraph("Gamma");
        var text = doc.GetTextBetweenParagraphs(0, 2);
        Assert.Equal("Alpha\nBeta", text);
        var html = doc.ExportToHtml();
        Assert.Contains("Alpha", html);
        Assert.Contains("Gamma", html);
    }

    [Fact]
    public void Dogfood_RemoveRebuildSaveReloadStats()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        for (int i = 0; i < 10; i++)
            doc.AppendParagraph($"Line {i}");
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var r = FodtDocument.Load(tmp);
            Assert.Equal(10, r.ParagraphCount);
            var stats = r.GetDocumentStats();
            Assert.Equal(10, stats.ParagraphCount);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Dogfood_FullPipeline_ClearEditExportSave()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("Dogfood Pipeline");
        var html = doc.ExportToHtml();
        Assert.Contains("Dogfood Pipeline", html);
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var r = FodtDocument.Load(tmp);
            Assert.Equal("Dogfood Pipeline", r.GetParagraphText(0));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Dogfood_ExportToMarkdown_AfterRebuild()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("MarkdownTest");
        var md = doc.ExportToMarkdown();
        Assert.Contains("MarkdownTest", md);
    }

    [Fact]
    public void Dogfood_SearchAfterRebuild()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("Find me here");
        var results = doc.SearchText("Find");
        Assert.True(results.Count > 0);
    }
}
