// R104 Wave 3: FODT .NET dogfood — plaintext/markdown export from edited document
// Ledger: R104-DOGFOOD-FODT-EXPORT-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR104DogfoodExportTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void Dogfood_LoadEditExportPlainText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.SetParagraphText(0, "Dogfood plaintext test");
        var text = doc.GetPlainText();
        Assert.Contains("Dogfood plaintext test", text);
    }

    [Fact]
    public void Dogfood_AppendThenExportMarkdown()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("New paragraph for export");
        var md = doc.ExportToMarkdown();
        Assert.Contains("New paragraph for export", md);
    }

    [Fact]
    public void Dogfood_SetParagraphThenStats()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.SetParagraphText(0, "one two three four five");
        var stats = doc.GetDocumentStats();
        Assert.True(stats.WordCount >= 5);
        Assert.True(stats.ParagraphCount >= 1);
    }

    [Fact]
    public void Dogfood_EditSaveReloadVerify()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.SetParagraphText(0, "Saved content");
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Equal("Saved content", reloaded.Paragraphs[0].Text);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Dogfood_StatsAfterMultipleEdits()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("extra one");
        doc.AppendParagraph("extra two");
        var stats = doc.GetDocumentStats();
        Assert.True(stats.ParagraphCount >= 3);
        Assert.True(stats.WordCount >= 4);
    }

    [Fact]
    public void Dogfood_FullPipeline_EditExportSaveReload()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.SetParagraphText(0, "pipeline test");
        doc.AppendParagraph("second paragraph");
        var plainBefore = doc.GetPlainText();
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var plainAfter = reloaded.GetPlainText();
            Assert.Contains("pipeline test", plainAfter);
            Assert.Contains("second paragraph", plainAfter);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
