using Xunit;
using System;
using System.IO;
using FormatFactory.Fodt;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R112 depth: FODT ReplaceText save-reload roundtrip.
/// Proves text replacement survives Save→Load with content preserved.
/// </summary>
public class FodtR112ReplaceTextSaveRoundtripTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));
    private static string SamplePath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void ReplaceText_SurvivesSaveReload()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("OriginalText here");
        doc.ReplaceText("OriginalText", "ReplacedText");
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var text = reloaded.GetPlainText();
            Assert.Contains("ReplacedText", text);
            Assert.DoesNotContain("OriginalText", text);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ReplaceText_MultipleOccurrences_AllSurvive()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("foo bar foo baz foo");
        int count = doc.ReplaceText("foo", "qux");
        Assert.Equal(3, count);
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var text = reloaded.GetPlainText();
            Assert.DoesNotContain("foo", text);
            Assert.Contains("qux", text);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void AppendParagraph_SurvivesSaveReload()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("R112 appended paragraph");
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var text = reloaded.GetPlainText();
            Assert.Contains("R112 appended paragraph", text);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SetParagraphText_SurvivesSaveReload()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("before");
        int lastIdx = doc.ParagraphCount - 1;
        doc.SetParagraphText(lastIdx, "after");
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Equal("after", reloaded.GetParagraphText(reloaded.ParagraphCount - 1));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void DocumentStats_ConsistentAfterReload()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("stats test paragraph");
        var statsBefore = doc.GetDocumentStats();
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var statsAfter = reloaded.GetDocumentStats();
            Assert.Equal(statsBefore.ParagraphCount, statsAfter.ParagraphCount);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToMarkdownFile_AfterReplace_ContainsNewText()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("markdown_target");
        doc.ReplaceText("markdown_target", "markdown_replaced");
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var md = reloaded.ExportToMarkdown();
            Assert.Contains("markdown_replaced", md);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void WordCount_ChangesAfterReplace()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("one two three");
        doc.ReplaceText("one two three", "replaced");
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Contains("replaced", reloaded.GetPlainText());
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void RemoveParagraph_SurvivesSaveReload()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("to_remove");
        doc.AppendParagraph("to_keep");
        int removeIdx = doc.ParagraphCount - 2;
        doc.RemoveParagraph(removeIdx);
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var text = reloaded.GetPlainText();
            Assert.DoesNotContain("to_remove", text);
            Assert.Contains("to_keep", text);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
