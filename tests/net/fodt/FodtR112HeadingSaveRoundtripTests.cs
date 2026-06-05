using Xunit;
using System;
using System.IO;
using FormatFactory.Fodt;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R112 depth: FODT InsertHeading save-reload roundtrip.
/// Proves heading insertion survives Save→Load with level and text preserved.
/// </summary>
public class FodtR112HeadingSaveRoundtripTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));
    private static string SamplePath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void InsertHeading_SurvivesSaveReload()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.InsertHeading(0, "R112 Heading Test", 1);
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var outline = reloaded.GetDocumentOutline();
            Assert.Contains(outline, h => h.Text == "R112 Heading Test" && h.Level == 1);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void InsertHeading_Level2_PreservesLevel()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.InsertHeading(0, "Subheading", 2);
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var outline = reloaded.GetDocumentOutline();
            Assert.Contains(outline, h => h.Text == "Subheading" && h.Level == 2);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void InsertMultipleHeadings_AllSurvive()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.InsertHeading(0, "H1 Title", 1);
        doc.InsertHeading(1, "H2 Section", 2);
        doc.InsertHeading(2, "H3 Sub", 3);
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var outline = reloaded.GetDocumentOutline();
            Assert.True(outline.Count >= 3);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void RemoveHeading_ThenSave_HeadingGone()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.InsertHeading(0, "ToRemove", 1);
        int headingIdx = 0;
        doc.RemoveHeading(headingIdx);
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var outline = reloaded.GetDocumentOutline();
            Assert.DoesNotContain(outline, h => h.Text == "ToRemove");
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void GetDocumentOutline_SurvivesSaveReload()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.InsertHeading(0, "OutlineTest", 1);
        var outlineBefore = doc.GetDocumentOutline();
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var outlineAfter = reloaded.GetDocumentOutline();
            Assert.Equal(outlineBefore.Count, outlineAfter.Count);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Heading_ParagraphCount_ConsistentAfterReload()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.InsertHeading(0, "CountTest", 1);
        int countBefore = doc.ParagraphCount;
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Equal(countBefore, reloaded.ParagraphCount);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Heading_ExportToMarkdown_ContainsHeading()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.InsertHeading(0, "MD Heading", 1);
        var md = doc.ExportToMarkdown();
        Assert.Contains("# MD Heading", md);
    }

    [Fact]
    public void Heading_ExportToHtml_ContainsH1()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.InsertHeading(0, "HTML Heading", 1);
        var html = doc.ExportToHtml();
        Assert.Contains("<h1>HTML Heading</h1>", html);
    }
}
