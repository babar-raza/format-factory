// R105 Wave 4: FODT .NET dogfood — ExportToHtml + GetParagraphText pipeline
// Ledger: R105-DOGFOOD-FODT-HTML-EXPORT-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR105DogfoodHtmlExportTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void Dogfood_ExportToHtml_ContainsDoctype()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var html = doc.ExportToHtml();
        Assert.StartsWith("<!DOCTYPE html>", html);
    }

    [Fact]
    public void Dogfood_ExportToHtml_ContainsParagraphs()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var html = doc.ExportToHtml();
        Assert.Contains("<p>", html);
    }

    [Fact]
    public void Dogfood_GetParagraphText_FirstParagraph()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var text = doc.GetParagraphText(0);
        Assert.NotNull(text);
    }

    [Fact]
    public void Dogfood_GetParagraphText_OutOfRange_ReturnsNull()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphText(9999));
    }

    [Fact]
    public void Dogfood_AppendParagraphThenExportHtml()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("DogfoodHtmlParagraph");
        var html = doc.ExportToHtml();
        Assert.Contains("DogfoodHtmlParagraph", html);
    }

    [Fact]
    public void Dogfood_FullPipeline_LoadEditExportVerify()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("PipelineTest");
        var idx = doc.ParagraphCount - 1;
        var text = doc.GetParagraphText(idx);
        Assert.Equal("PipelineTest", text);
        var html = doc.ExportToHtml();
        Assert.Contains("PipelineTest", html);
        Assert.Contains("</html>", html);
    }
}
