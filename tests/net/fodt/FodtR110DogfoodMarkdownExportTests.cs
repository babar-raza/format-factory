// R110 Wave 6: FODT Markdown Export Dogfood Pipeline Tests
// Dogfood: load→edit→ExportToMarkdown pipeline

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR110DogfoodMarkdownExportTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void Dogfood_LoadEditExportMarkdown_Pipeline()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("Dogfood paragraph R110");
        var md = doc.ExportToMarkdown();
        Assert.Contains("Dogfood paragraph R110", md);
    }

    [Fact]
    public void Dogfood_InsertHeadingThenExportMarkdown()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertHeading(0, "R110 Dogfood Heading", 2);
        var md = doc.ExportToMarkdown();
        Assert.Contains("## R110 Dogfood Heading", md);
    }

    [Fact]
    public void Dogfood_ExportMarkdownToFile_Pipeline()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("File export test R110");
        var tmpPath = Path.GetTempFileName() + ".md";
        try
        {
            doc.ExportToMarkdownFile(tmpPath);
            Assert.True(File.Exists(tmpPath));
            var content = File.ReadAllText(tmpPath);
            Assert.Contains("File export test R110", content);
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }

    [Fact]
    public void Dogfood_GetStyleThenExport_Pipeline()
    {
        var doc = FodtDocument.Load(MinimalPath);
        if (doc.GetParagraphCount() > 0)
        {
            _ = doc.GetParagraphStyleName(0);
        }
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
    }
}
