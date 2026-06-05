// R111 Wave 7: FODT outline extraction + markdown export dogfood pipeline tests
// Pipeline: load → insert headings → get outline → export markdown → verify

using System;
using System.IO;
using System.Linq;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR111DogfoodOutlineExportTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void Dogfood_InsertHeadings_GetOutline_ExportMarkdown()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertHeading(0, "Chapter 1", 1);
        doc.InsertHeading(1, "Section 1.1", 2);
        doc.AppendParagraph("Some body text.");

        var outline = doc.GetDocumentOutline();
        Assert.True(outline.Count >= 2);

        var md = doc.ExportToMarkdown();
        Assert.Contains("Chapter 1", md);
        Assert.Contains("Section 1.1", md);
    }

    [Fact]
    public void Dogfood_RemoveHeading_OutlineUpdates()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertHeading(0, "Keep", 1);
        doc.InsertHeading(1, "Remove", 2);

        doc.RemoveHeading(1);
        var outline = doc.GetDocumentOutline();
        Assert.DoesNotContain(outline, o => o.Text == "Remove");
        Assert.Contains(outline, o => o.Text == "Keep");
    }

    [Fact]
    public void Dogfood_Outline_SaveReload_Preserved()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertHeading(0, "Persistent H1", 1);

        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var outline = reloaded.GetDocumentOutline();
            Assert.Contains(outline, o => o.Text == "Persistent H1" && o.Level == 1);
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
        }
    }

    [Fact]
    public void Dogfood_MarkdownExport_HeadingLevels()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.InsertHeading(0, "H1", 1);
        doc.InsertHeading(1, "H2", 2);
        doc.InsertHeading(2, "H3", 3);

        var md = doc.ExportToMarkdown();
        Assert.Contains("# H1", md);
        Assert.Contains("## H2", md);
        Assert.Contains("### H3", md);
    }
}
