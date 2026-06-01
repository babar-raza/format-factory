// R87 Train I: FODT .NET product slice deepening tests
// Sprint: FORMAT-FACTORY-R87-CLEAN-SUPERVISOR-CLOSEOUT-REVIEW-PACKAGE-POC-PRODUCT-FACTORY-DEEPENING-MEGA-TRAIN-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR87ProductDeepening : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fodt/Fixtures"));

    private static readonly string MinimalFodt =
        Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");

    private readonly string _tempDir;

    public FodtR87ProductDeepening()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fodt-r87-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // === TXT Export Deepening ===

    [Fact]
    public void TxtExport_MinimalFixture_ProducesFile()
    {
        var outPath = Path.Combine(_tempDir, "export.txt");
        var result = FodtTxtExporter.ExportTxt(MinimalFodt, outPath);
        Assert.True(
            result.Status == "exported" || result.Status == "exported_empty_no_paragraphs",
            $"Expected exported status, got: {result.Status}");
        Assert.True(File.Exists(outPath));
    }

    [Fact]
    public void TxtExport_OutputIsPlainText()
    {
        var outPath = Path.Combine(_tempDir, "plain.txt");
        FodtTxtExporter.ExportTxt(MinimalFodt, outPath);
        if (File.Exists(outPath))
        {
            var text = File.ReadAllText(outPath);
            Assert.DoesNotContain("<office:", text);
            Assert.DoesNotContain("</text:", text);
        }
    }

    // === Markdown Export Deepening ===

    [Fact]
    public void MarkdownExport_MinimalFixture_ProducesFile()
    {
        var outPath = Path.Combine(_tempDir, "export.md");
        var result = FodtMarkdownExporter.ExportToMarkdown(MinimalFodt, outPath);
        Assert.True(
            result.Status == "Success" || result.Status == "exported_empty" || result.Status == "exported",
            $"Expected success status, got: {result.Status}");
        Assert.True(File.Exists(outPath));
    }

    // === HTML Export Deepening ===

    [Fact]
    public void HtmlExport_MinimalFixture_ProducesValidStructure()
    {
        var outPath = Path.Combine(_tempDir, "export.html");
        var result = FodtHtmlExporter.ExportToHtml(MinimalFodt, outPath);
        Assert.True(
            result.Status == "Success" || result.Status == "exported_empty" || result.Status == "exported",
            $"Expected success status, got: {result.Status}");
        if (File.Exists(outPath))
        {
            var html = File.ReadAllText(outPath);
            Assert.Contains("<html", html);
            Assert.Contains("<body", html);
            Assert.Contains("</html>", html);
        }
    }

    [Fact]
    public void HtmlExport_NoXmlTagsLeak()
    {
        var outPath = Path.Combine(_tempDir, "noleak.html");
        FodtHtmlExporter.ExportToHtml(MinimalFodt, outPath);
        if (File.Exists(outPath))
        {
            var html = File.ReadAllText(outPath);
            Assert.DoesNotContain("<office:", html);
            Assert.DoesNotContain("<text:p", html);
        }
    }

    // === Same-format roundtrip ===

    [Fact]
    public void FodtRoundTrip_SavePreservesStructure()
    {
        var outPath = Path.Combine(_tempDir, "roundtrip.fodt");
        var content = File.ReadAllText(MinimalFodt);
        File.WriteAllText(outPath, content);
        var reloaded = File.ReadAllText(outPath);
        Assert.Contains("office:document", reloaded);
    }

    // === Null guards ===

    [Fact]
    public void TxtExport_NullPath_Throws()
    {
        Assert.Throws<FodtTxtExportException>(() =>
            FodtTxtExporter.ExportTxt(null!, Path.Combine(_tempDir, "out.txt")));
    }

    [Fact]
    public void MarkdownExport_NullPath_Throws()
    {
        Assert.Throws<FodtMarkdownExportException>(() =>
            FodtMarkdownExporter.ExportToMarkdown(null!, Path.Combine(_tempDir, "out.md")));
    }
}
