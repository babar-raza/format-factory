// FormatFactory.Fodt Tests -- FodtHtmlExporter G11-E Expanded Prototype Tests
// Sprint: FORMAT-FACTORY-R23-MEGA-TRAIN-001
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// commercial_product_ready: false

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// Tests for the G11-E FODT → HTML export prototype.
/// Tests cover: basic export, HTML structure, escaping, null guards.
/// All tests use local fixture files only — no network.
/// </summary>
public class FodtHtmlExporterTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fodt/Fixtures"));

    private static readonly string MinimalFodt =
        Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");

    private readonly string _tempDir;

    public FodtHtmlExporterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fodt-html-export-tests-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // -------------------------------------------------------------------------
    // Null guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_NullFodtPath_Throws()
    {
        Assert.Throws<FodtHtmlExportException>(() =>
            FodtHtmlExporter.ExportToHtml(null!, Path.Combine(_tempDir, "out.html")));
    }

    [Fact]
    public void ExportToHtml_EmptyFodtPath_Throws()
    {
        Assert.Throws<FodtHtmlExportException>(() =>
            FodtHtmlExporter.ExportToHtml("", Path.Combine(_tempDir, "out.html")));
    }

    [Fact]
    public void ExportToHtml_NullHtmlPath_Throws()
    {
        Assert.Throws<FodtHtmlExportException>(() =>
            FodtHtmlExporter.ExportToHtml(MinimalFodt, null!));
    }

    [Fact]
    public void ExportToHtml_NonExistentFodtPath_Throws()
    {
        Assert.Throws<FodtHtmlExportException>(() =>
            FodtHtmlExporter.ExportToHtml(
                Path.Combine(_tempDir, "nonexistent.fodt"),
                Path.Combine(_tempDir, "out.html")));
    }

    // -------------------------------------------------------------------------
    // HtmlEscape unit tests
    // -------------------------------------------------------------------------

    [Fact]
    public void HtmlEscape_Null_ReturnsEmpty()
    {
        Assert.Equal(string.Empty, FodtHtmlExporter.HtmlEscape(null));
    }

    [Fact]
    public void HtmlEscape_Empty_ReturnsEmpty()
    {
        Assert.Equal(string.Empty, FodtHtmlExporter.HtmlEscape(""));
    }

    [Fact]
    public void HtmlEscape_LtGt_EscapedCorrectly()
    {
        var result = FodtHtmlExporter.HtmlEscape("<b>text</b>");
        Assert.Contains("&lt;", result);
        Assert.Contains("&gt;", result);
        Assert.DoesNotContain("<b>", result);
    }

    [Fact]
    public void HtmlEscape_Ampersand_EscapedCorrectly()
    {
        var result = FodtHtmlExporter.HtmlEscape("A & B");
        Assert.Contains("&amp;", result);
    }

    // -------------------------------------------------------------------------
    // Integration tests (using fixture)
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_MinimalFodt_CreatesHtmlFile()
    {
        var outHtml = Path.Combine(_tempDir, "minimal.html");
        var result = FodtHtmlExporter.ExportToHtml(MinimalFodt, outHtml);

        Assert.True(File.Exists(outHtml), "HTML output file must be created");
        Assert.Equal(outHtml, result.OutputPath);
    }

    [Fact]
    public void ExportToHtml_MinimalFodt_ContainsDoctype()
    {
        var outHtml = Path.Combine(_tempDir, "out.html");
        FodtHtmlExporter.ExportToHtml(MinimalFodt, outHtml);

        var text = File.ReadAllText(outHtml);
        Assert.Contains("<!DOCTYPE html>", text);
    }

    [Fact]
    public void ExportToHtml_MinimalFodt_ContainsCharsetUtf8()
    {
        var outHtml = Path.Combine(_tempDir, "out.html");
        FodtHtmlExporter.ExportToHtml(MinimalFodt, outHtml);

        var text = File.ReadAllText(outHtml);
        Assert.Contains("UTF-8", text);
    }

    [Fact]
    public void ExportToHtml_MinimalFodt_HasBodyTag()
    {
        var outHtml = Path.Combine(_tempDir, "out.html");
        FodtHtmlExporter.ExportToHtml(MinimalFodt, outHtml);

        var text = File.ReadAllText(outHtml);
        Assert.Contains("<body>", text);
        Assert.Contains("</body>", text);
    }

    [Fact]
    public void ExportToHtml_MinimalFodt_OutputNonEmpty()
    {
        var outHtml = Path.Combine(_tempDir, "out.html");
        FodtHtmlExporter.ExportToHtml(MinimalFodt, outHtml);

        var info = new FileInfo(outHtml);
        Assert.True(info.Length > 0, "HTML output file must be non-empty");
    }

    [Fact]
    public void ExportToHtml_MinimalFodt_StatusIsExportedOrEmpty()
    {
        var outHtml = Path.Combine(_tempDir, "out.html");
        var result = FodtHtmlExporter.ExportToHtml(MinimalFodt, outHtml);

        Assert.True(
            result.Status == "exported" ||
            result.Status == "exported_empty_no_paragraphs",
            $"Status must be exported or empty, got: {result.Status}");
    }

    // -------------------------------------------------------------------------
    // Governance tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_Prototype_CommentInOutput()
    {
        var outHtml = Path.Combine(_tempDir, "out.html");
        FodtHtmlExporter.ExportToHtml(MinimalFodt, outHtml);

        var text = File.ReadAllText(outHtml);
        Assert.Contains("commercial_product_ready=false", text);
    }

    [Fact]
    public void ExportToHtml_MinimalFodt_NonNegativeCounts()
    {
        var outHtml = Path.Combine(_tempDir, "out.html");
        var result = FodtHtmlExporter.ExportToHtml(MinimalFodt, outHtml);

        Assert.True(result.HeadingsExported >= 0);
        Assert.True(result.ParagraphsExported >= 0);
    }
}
