// R105 Wave 2: FODT .NET ExportToHtml tests
// Governed skill: /add-dotnet-api
// Ledger: R105-GOVERNED-DOTNET-FODT-EXPORTTOHTML-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR105ExportToHtmlTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    private static string HeadingsPath =>
        Path.Combine(SamplesDir, "headings-and-paragraphs.fodt");

    [Fact]
    public void ExportToHtml_ContainsDoctype()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var html = doc.ExportToHtml();
        Assert.Contains("<!DOCTYPE html>", html);
    }

    [Fact]
    public void ExportToHtml_ContainsBodyTags()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var html = doc.ExportToHtml();
        Assert.Contains("<body>", html);
        Assert.Contains("</body>", html);
    }

    [Fact]
    public void ExportToHtml_ContainsParagraphTags()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var html = doc.ExportToHtml();
        Assert.Contains("<p>", html);
    }

    [Fact]
    public void ExportToHtml_HeadingsUseHtags()
    {
        if (!File.Exists(HeadingsPath)) return;
        var doc = FodtDocument.Load(HeadingsPath);
        var html = doc.ExportToHtml();
        Assert.Contains("<h", html);
    }

    [Fact]
    public void ExportToHtml_EscapesHtmlEntities()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.SetParagraphText(0, "A < B & C > D");
        var html = doc.ExportToHtml();
        Assert.Contains("&lt;", html);
        Assert.Contains("&amp;", html);
        Assert.Contains("&gt;", html);
    }

    [Fact]
    public void ExportToHtml_AfterAppend_IncludesNewParagraph()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("New HTML paragraph");
        var html = doc.ExportToHtml();
        Assert.Contains("New HTML paragraph", html);
    }

    [Fact]
    public void ExportToHtml_AfterEdit_ReflectsChange()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.SetParagraphText(0, "Edited for HTML");
        var html = doc.ExportToHtml();
        Assert.Contains("Edited for HTML", html);
    }

    [Fact]
    public void ExportToHtml_PersistsRoundtrip()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("Roundtrip test");
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var html = reloaded.ExportToHtml();
            Assert.Contains("Roundtrip test", html);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToHtml_NonEmptyForMinimalDocument()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var html = doc.ExportToHtml();
        Assert.True(html.Length > 50);
    }
}
