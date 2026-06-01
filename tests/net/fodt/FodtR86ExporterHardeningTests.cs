// R86 Train H: FODT .NET exporter edge-case hardening tests
// Sprint: FORMAT-FACTORY-R86-SUPERVISOR-TRUTH-POC-PRODUCT-FACTORY-DEEPENING

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR86ExporterHardeningTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fodt/Fixtures"));

    private static readonly string MinimalFodt =
        Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");

    private readonly string _tempDir;

    public FodtR86ExporterHardeningTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fodt-r86-hardening-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // === TXT Export Integration ===

    [Fact]
    public void TxtExport_MinimalFixture_ProducesFile()
    {
        var outPath = Path.Combine(_tempDir, "minimal.txt");
        var result = FodtTxtExporter.ExportTxt(MinimalFodt, outPath);
        Assert.True(
            result.Status == "exported" || result.Status == "exported_empty_no_paragraphs",
            $"Expected exported status, got: {result.Status}");
        Assert.True(File.Exists(outPath));
    }

    // === Markdown Export Integration ===

    [Fact]
    public void MarkdownExport_MinimalFixture_ProducesFile()
    {
        var outPath = Path.Combine(_tempDir, "minimal.md");
        var result = FodtMarkdownExporter.ExportToMarkdown(MinimalFodt, outPath);
        Assert.True(
            result.Status == "Success" || result.Status == "exported_empty" || result.Status == "exported",
            $"Expected success status, got: {result.Status}");
        Assert.True(File.Exists(outPath));
    }

    // === HTML Export Integration ===

    [Fact]
    public void HtmlExport_MinimalFixture_ProducesValidHtml()
    {
        var outPath = Path.Combine(_tempDir, "minimal.html");
        var result = FodtHtmlExporter.ExportToHtml(MinimalFodt, outPath);
        Assert.True(
            result.Status == "Success" || result.Status == "exported_empty" || result.Status == "exported",
            $"Expected success status, got: {result.Status}");
        var html = File.ReadAllText(outPath);
        Assert.Contains("<html", html);
        Assert.Contains("</html>", html);
    }

    [Fact]
    public void HtmlExport_MinimalFixture_ContainsBodyTag()
    {
        var outPath = Path.Combine(_tempDir, "body.html");
        var result = FodtHtmlExporter.ExportToHtml(MinimalFodt, outPath);
        Assert.True(
            result.Status == "Success" || result.Status == "exported_empty" || result.Status == "exported",
            $"Expected success status, got: {result.Status}");
        var html = File.ReadAllText(outPath);
        Assert.Contains("<body", html);
    }

    // === Null Guard Tests (all exporters) ===

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

    [Fact]
    public void HtmlExport_NullPath_Throws()
    {
        Assert.Throws<FodtHtmlExportException>(() =>
            FodtHtmlExporter.ExportToHtml(null!, Path.Combine(_tempDir, "out.html")));
    }
}
