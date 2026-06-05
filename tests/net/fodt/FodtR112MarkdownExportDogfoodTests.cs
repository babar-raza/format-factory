using Xunit;
using System;
using System.IO;
using FormatFactory.Fodt;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R112 Dogfood: FODT edit -> Markdown export -> verify.
/// Uses FF library for both input and output.
/// </summary>
public class FodtR112MarkdownExportDogfoodTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));
    private static string SamplePath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void MarkdownExport_ContainsHeadings()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.InsertHeading(0, "Chapter One", 1);
        doc.InsertHeading(1, "Section A", 2);
        var md = doc.ExportToMarkdown();
        Assert.Contains("# Chapter One", md);
        Assert.Contains("## Section A", md);
    }

    [Fact]
    public void MarkdownExport_ContainsParagraphs()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("Body text for dogfood test");
        var md = doc.ExportToMarkdown();
        Assert.Contains("Body text for dogfood test", md);
    }

    [Fact]
    public void MarkdownExport_AfterReplace_ReflectsChange()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("old content");
        doc.ReplaceText("old content", "new content");
        var md = doc.ExportToMarkdown();
        Assert.Contains("new content", md);
        Assert.DoesNotContain("old content", md);
    }

    [Fact]
    public void MarkdownExport_SaveReload_ThenExport()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.InsertHeading(0, "Saved Heading", 1);
        doc.AppendParagraph("Saved body");
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var md = reloaded.ExportToMarkdown();
            Assert.Contains("# Saved Heading", md);
            Assert.Contains("Saved body", md);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void MarkdownExportToFile_CreatesFile()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.InsertHeading(0, "File Export", 1);
        var tmp = Path.GetTempFileName() + ".md";
        try
        {
            doc.ExportToMarkdownFile(tmp);
            Assert.True(File.Exists(tmp));
            var content = File.ReadAllText(tmp);
            Assert.Contains("# File Export", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void HtmlExport_AfterEdit_ContainsH1()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.InsertHeading(0, "HTML Dogfood", 1);
        var html = doc.ExportToHtml();
        Assert.Contains("<h1>HTML Dogfood</h1>", html);
    }

    [Fact]
    public void PlainTextExport_AfterEdit_ContainsText()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("plain text dogfood");
        var txt = doc.GetPlainText();
        Assert.Contains("plain text dogfood", txt);
    }

    [Fact]
    public void ExportToPlainTextFile_CreatesFile()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("file text export");
        var tmp = Path.GetTempFileName() + ".txt";
        try
        {
            doc.ExportToPlainTextFile(tmp);
            Assert.True(File.Exists(tmp));
            var content = File.ReadAllText(tmp);
            Assert.Contains("file text export", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
